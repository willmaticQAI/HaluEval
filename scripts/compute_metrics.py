"""Aggregate per-instance JSONL results into accuracy/precision/recall/F1
per model-task pair, plus an ambiguous-response rate (parse failures are a
finding in their own right, not just noise to discard)."""

import argparse
import glob
import json
import os

MODELS = ["qwen", "llama", "gemma"]
TASKS = ["qa", "dialogue", "summarization"]


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def compute(records):
    tp = fp = tn = fn = ambiguous = 0
    for r in records:
        gt = r["ground_truth"]
        j = r["judgement"]
        if j not in ("Yes", "No"):
            ambiguous += 1
            continue
        if gt == "Yes" and j == "Yes":
            tp += 1
        elif gt == "Yes" and j == "No":
            fn += 1
        elif gt == "No" and j == "No":
            tn += 1
        elif gt == "No" and j == "Yes":
            fp += 1

    n_scored = tp + fp + tn + fn
    accuracy = (tp + tn) / n_scored if n_scored else float("nan")
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = (2 * precision * recall / (precision + recall)
          if precision and recall and (precision + recall) else float("nan"))
    return {
        "n_total": len(records),
        "n_scored": n_scored,
        "ambiguous": ambiguous,
        "ambiguous_rate": ambiguous / len(records) if records else float("nan"),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def main():
    parser = argparse.ArgumentParser(description="Compute HaluEval metrics from results/*.jsonl")
    parser.add_argument("--results_dir", default=None,
                         help="Defaults to <repo_root>/results")
    parser.add_argument("--out", default=None,
                         help="Write summary JSON here; defaults to <results_dir>/summary.json")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = args.results_dir or os.path.join(repo_root, "results")
    out_path = args.out or os.path.join(results_dir, "summary.json")

    summary = {}
    rows = []
    for model in MODELS:
        for task in TASKS:
            path = os.path.join(results_dir, f"{model}_{task}_results.jsonl")
            if not os.path.exists(path):
                continue
            records = load_jsonl(path)
            metrics = compute(records)
            summary[f"{model}_{task}"] = metrics
            rows.append((model, task, metrics))

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    if not rows:
        print(f"No result files found in {results_dir}")
        return

    header = f"{'model':8} | {'task':14} | {'n':>5} | {'amb%':>6} | {'acc':>6} | {'prec':>6} | {'rec':>6} | {'f1':>6}"
    print(header)
    print("-" * len(header))
    for model, task, m in rows:
        print(f"{model:8} | {task:14} | {m['n_scored']:5d} | "
              f"{m['ambiguous_rate']*100:5.1f}% | {m['accuracy']:.4f} | "
              f"{m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f}")

    print(f"\nSummary written to {out_path}")


if __name__ == "__main__":
    main()
