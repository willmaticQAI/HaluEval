"""HaluEval discrimination-task pipeline for local Ollama models.

For each sampled dataset item, generates TWO evaluation instances — one with
the right_answer (expected judgement "No") and one with the hallucinated_answer
(expected judgement "Yes") — so every run produces a balanced pool of positives
and negatives and precision/recall/F1 are well-defined. This mirrors the
original HaluEval discriminate-task design (each sample judged in both
directions) rather than randomly picking a single direction per item.

Results are appended to a JSONL file keyed by a stable instance_id, so an
interrupted run can be resumed by re-invoking with the same --model/--task/
--sample_size/--seed: already-completed instances are skipped.
"""

import argparse
import json
import os
import random
import re
import sys
import time

from ollama_client import OllamaClient

TASK_CONFIG = {
    "qa": {
        "data_file": "qa_data.json",
        "instruction_file": "evaluation/qa/qa_evaluation_instruction.txt",
        "system": (
            "You are a hallucination detector. You MUST determine if the provided "
            "answer contains hallucination or not for the question based on the "
            "world knowledge. Respond with exactly one word: Yes or No. Do not "
            "repeat the question or answer, do not explain, do not generate "
            "additional examples."
        ),
        "fields": ["question"],
        "answer_field_right": "right_answer",
        "answer_field_hallucinated": "hallucinated_answer",
    },
    "dialogue": {
        "data_file": "dialogue_data.json",
        "instruction_file": "evaluation/dialogue/dialogue_evaluation_instruction.txt",
        "system": (
            "You are a response judge. You MUST determine if the provided response "
            "contains non-factual or hallucinated information. Respond with exactly "
            "one word: Yes or No. Do not repeat the dialogue or response, do not "
            "explain, do not generate additional examples."
        ),
        "fields": ["dialogue_history"],
        "answer_field_right": "right_response",
        "answer_field_hallucinated": "hallucinated_response",
    },
    "summarization": {
        "data_file": "summarization_data.json",
        "instruction_file": "evaluation/summarization/summarization_evaluation_instruction.txt",
        "system": (
            "You are a summary judge. You MUST determine if the provided summary "
            "contains non-factual or hallucinated information. Respond with exactly "
            "one word: Yes or No. Do not repeat the document or summary, do not "
            "explain, do not generate additional examples."
        ),
        "fields": ["document"],
        "answer_field_right": "right_summary",
        "answer_field_hallucinated": "hallucinated_summary",
    },
}

PROMPT_LABELS = {
    "question": "#Question#",
    "dialogue_history": "#Dialogue History#",
    "document": "#Document#",
}

ANSWER_LABELS = {
    "qa": "#Answer#",
    "dialogue": "#Response#",
    "summarization": "#Summary#",
}


def load_jsonl(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def load_repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_prompt(task, instruction, item):
    cfg = TASK_CONFIG[task]
    context_field = cfg["fields"][0]
    context_label = PROMPT_LABELS[context_field]
    answer_label = ANSWER_LABELS[task]
    context_value = item["context_value"]
    answer_value = item["answer_value"]
    return (
        f"{instruction}\n\nNow judge ONLY the following pair. Respond with "
        f"exactly one word, Yes or No.\n{context_label}: {context_value}\n"
        f"{answer_label}: {answer_value}\n#Your Judgement#:"
    )


def parse_judgement(response):
    """Robustly extract Yes/No from a model response. Returns 'AMBIGUOUS' if
    both or neither appear, rather than silently discarding the sample."""
    text = response.strip()
    exact = text.strip(" .\"'*").lower()
    if exact == "yes":
        return "Yes"
    if exact == "no":
        return "No"

    first_line = text.splitlines()[0] if text else ""
    yes_first = re.search(r"\byes\b", first_line, re.IGNORECASE)
    no_first = re.search(r"\bno\b", first_line, re.IGNORECASE)
    if yes_first and not no_first:
        return "Yes"
    if no_first and not yes_first:
        return "No"

    yes_any = re.search(r"\byes\b", text, re.IGNORECASE)
    no_any = re.search(r"\bno\b", text, re.IGNORECASE)
    if yes_any and no_any:
        return "Yes" if yes_any.start() < no_any.start() else "No"
    if yes_any:
        return "Yes"
    if no_any:
        return "No"
    return "AMBIGUOUS"


def make_instances(task, data, sample_size, seed):
    cfg = TASK_CONFIG[task]
    context_field = cfg["fields"][0]
    rng = random.Random(seed)
    indices = rng.sample(range(len(data)), min(sample_size, len(data)))
    instances = []
    for idx in indices:
        item = data[idx]
        context_value = item[context_field]
        for direction, answer_field, ground_truth in [
            ("right", cfg["answer_field_right"], "No"),
            ("hallucinated", cfg["answer_field_hallucinated"], "Yes"),
        ]:
            instances.append(
                {
                    "instance_id": f"{task}-{idx}-{direction}",
                    "sample_index": idx,
                    "direction": direction,
                    "ground_truth": ground_truth,
                    "context_value": context_value,
                    "answer_value": item[answer_field],
                }
            )
    return instances


def load_done_ids(output_path):
    if not os.path.exists(output_path):
        return set()
    done = set()
    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                done.add(json.loads(line)["instance_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    return done


def run(model, task, sample_size, seed, output_dir, repo_root):
    cfg = TASK_CONFIG[task]
    data = load_jsonl(os.path.join(repo_root, "data", cfg["data_file"]))
    with open(os.path.join(repo_root, cfg["instruction_file"]), "r", encoding="utf-8") as f:
        instruction = f.read()

    instances = make_instances(task, data, sample_size, seed)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{model}_{task}_results.jsonl")
    done_ids = load_done_ids(output_path)

    client = OllamaClient(model)

    n_total = len(instances)
    n_skip = sum(1 for i in instances if i["instance_id"] in done_ids)
    print(f"[{model}/{task}] {n_total} instances ({n_total // 2} samples x2), "
          f"{n_skip} already done, {n_total - n_skip} to run", file=sys.stderr)

    correct = incorrect = ambiguous = 0
    t0 = time.time()
    for i, inst in enumerate(instances):
        if inst["instance_id"] in done_ids:
            continue
        prompt = build_prompt(task, instruction, inst)
        try:
            raw_response = client.generate(prompt, system=cfg["system"])
        except RuntimeError as e:
            raw_response = ""
            judgement = "ERROR"
            print(f"  [{i+1}/{n_total}] {inst['instance_id']}: ERROR {e}", file=sys.stderr)
        else:
            judgement = parse_judgement(raw_response)

        is_correct = judgement == inst["ground_truth"] if judgement in ("Yes", "No") else None
        if judgement == "AMBIGUOUS" or judgement == "ERROR":
            ambiguous += 1
        elif is_correct:
            correct += 1
        else:
            incorrect += 1

        record = {
            "instance_id": inst["instance_id"],
            "model": model,
            "task": task,
            "sample_index": inst["sample_index"],
            "direction": inst["direction"],
            "ground_truth": inst["ground_truth"],
            "context_value": inst["context_value"],
            "answer_value": inst["answer_value"],
            "model_response_raw": raw_response,
            "judgement": judgement,
            "correct": is_correct,
        }
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        if (i + 1) % 10 == 0 or (i + 1) == n_total:
            elapsed = time.time() - t0
            print(f"  [{i+1}/{n_total}] correct={correct} incorrect={incorrect} "
                  f"ambiguous={ambiguous} ({elapsed:.0f}s elapsed)", file=sys.stderr)

    print(f"[{model}/{task}] done -> {output_path}", file=sys.stderr)
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HaluEval local-model discrimination pipeline")
    parser.add_argument("--model", choices=["qwen", "llama", "gemma"], required=True)
    parser.add_argument("--task", choices=["qa", "dialogue", "summarization"], required=True)
    parser.add_argument("--sample_size", type=int, default=500,
                         help="Number of dataset items to sample; each yields 2 instances (right + hallucinated)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output_dir", default="results")
    args = parser.parse_args()

    repo_root = load_repo_root()
    output_dir = args.output_dir if os.path.isabs(args.output_dir) else os.path.join(repo_root, args.output_dir)
    run(args.model, args.task, args.sample_size, args.seed, output_dir, repo_root)
