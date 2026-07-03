# HaluEval Local-Model Hallucination Discrimination: Findings & Analysis

**Date:** 2026-07-03
**Models evaluated:** Qwen3 1.7B, Llama 3.2 1B, Gemma 3 1B (all run locally via Ollama)
**Tasks evaluated:** QA, Dialogue, Summarization (HaluEval discrimination benchmark)
**Scale:** 500 sampled items × 2 directions (right/hallucinated) × 3 tasks × 3 models = **9,000 total judgements**

---

## 1. What This Evaluation Measures

HaluEval's QA/Dialogue/Summarization tasks are **binary discrimination tasks, not generation-quality tests**. For each sampled item, the model is shown a context (a question, a dialogue history, or a document) plus one candidate answer/response/summary, and must output "Yes" (the candidate is hallucinated) or "No" (the candidate is grounded/correct). Each dataset item ships with two candidates:

- `right_answer` / `right_response` / `right_summary` — correct, expected model judgement: **"No"**
- `hallucinated_answer` / `hallucinated_response` / `hallucinated_summary` — a GPT-generated, plausible-but-wrong distractor, filtered by the original HaluEval authors to be non-trivial, expected model judgement: **"Yes"**

**Scope statement:** this evaluation measures whether a ~1–1.7B parameter model can *tell a correct answer from a plausible-sounding wrong one when both are handed to it directly*. It does **not** measure whether these models hallucinate when generating their own answers — that is a materially different (and unaddressed) question. This distinction should be stated explicitly in any report derived from this data so the scope isn't overclaimed.

---

## 2. Methodology

### 2.1 Models

| Model | Ollama tag | Params | Lab | Notes |
|---|---|---|---|---|
| Qwen3 | `qwen3:1.7b` | 1.7B | Alibaba | Ships with a "thinking" reasoning mode — see §2.4 |
| Llama 3.2 | `llama3.2:1b` | 1B | Meta | — |
| Gemma 3 | `gemma3:1b` | 1B | Google | Substituted for "Gemma 2 1B" — see below |

**Deviation from original plan:** the project's planning docs specified "Gemma 2 1B," but Ollama's Gemma 2 line has no 1B tag (its smallest is 2B). Gemma 3 is the only Gemma line that ships a 1B size, so `gemma3:1b` was used instead. This keeps the "one model per lab, matched ~1–1.7B parameter band" comparison design intact but should be noted as a substitution in the methods section, since Gemma 3 is architecturally a generation newer than Gemma 2.

### 2.2 Discrimination Protocol — Paired Sampling Design

The original project draft (`Implementation_Roadmap.md`) only tested the `hallucinated_answer` field and hardcoded `is_hallucinated: True` as ground truth for every instance. That design has no negative class, so **precision and recall are undefined** — you can only compute a hit rate on positives.

This was corrected before any full-scale run: for every sampled dataset item, the pipeline generates **two evaluation instances** — one with the right answer (expected judgement "No") and one with the hallucinated answer (expected judgement "Yes") — and pools both directions into a single confusion matrix per model-task pair. This mirrors the original HaluEval paper's discrimination protocol. Concretely: 500 sampled items × 2 directions = 1,000 scored judgements per model-task cell, 9,000 total across the 3×3 grid.

### 2.3 Sampling

- Random seed: `42` (fixed, reproducible)
- Sample size: 500 dataset items per task (out of 10,000 available in each of `qa_data.json`, `dialogue_data.json`, `summarization_data.json`)
- Same 500-item sample (by index) is reused across all three models for a given task, so model comparisons are on identical items

### 2.4 Prompting — Issues Found and Fixed

Two silent-failure modes were discovered during a 5-sample smoke test, before scaling up. Both produced plausible-looking but wrong output that only became visible by inspecting raw model responses, not aggregate stats:

1. **Llama 3.2 1B echoed the few-shot prompt instead of answering.** Given the original HaluEval instruction file verbatim (which contains several `#Question#/#Answer#/#Your Judgement#` worked examples), Llama continued the pattern by generating more fake examples rather than judging the new pair. Raw accuracy on the first unfixed smoke test was 1/10 — worse than chance.
   **Fix:** appended an explicit instruction after the few-shot block — *"Now judge ONLY the following pair. Respond with exactly one word, Yes or No."* — plus a stricter system prompt forbidding repetition/explanation.

2. **Qwen3 has "thinking" mode on by default.** Through Ollama's `/api/generate` endpoint, Qwen3 spends its entire output token budget on internal `<think>...</think>` reasoning and returns an **empty** final `response` field — invisible unless you inspect the raw JSON's separate `thinking` field. This produced a 100% ambiguous/empty-response rate on the first unfixed smoke test.
   **Fix:** passed `"think": false` in the Ollama API request payload.

After both fixes, all three models produced clean, parseable Yes/No output with **0% ambiguous responses across all 9,000 full-scale judgements** (see §4).

### 2.5 Parsing

Model responses are parsed with a layered heuristic (exact match → first-line regex → whole-response regex with first-occurrence tiebreak) rather than requiring an exact "Yes"/"No" string. Responses that are genuinely both or neither are logged as `AMBIGUOUS` rather than silently dropped or coerced — a spike in ambiguous responses is itself a finding, not just noise. In this run, ambiguous count was 0/9,000.

### 2.6 Infrastructure

- Local inference via Ollama 0.31.1 on Apple Silicon (arm64 macOS)
- Temperature = 0.0 (deterministic decoding) for all runs
- `num_predict` capped at 20 tokens (sufficient for a one-word answer; also limits runaway-echo failure cost)
- Pipeline is resumable: each judgement is written as a JSONL record keyed by a stable `instance_id`; re-invoking the same command skips already-completed instances. This mattered in practice — see §6.

---

## 3. Pilot Validation (N=25 per task, before committing to full scale)

Before running the full 500-sample grid (9,000 inferences, ~2–2.5 hour estimated cost), a small pilot (25 samples × 2 directions = 50 instances per model-task, 450 total) was run to validate the pipeline and get an early read on model behavior.

| model | task | n | acc | prec | recall | f1 |
|---|---|---|---|---|---|---|
| qwen | qa | 50 | 0.500 | 0.500 | 0.120 | 0.194 |
| qwen | dialogue | 50 | 0.540 | 0.526 | 0.800 | 0.635 |
| qwen | summarization | 50 | 0.500 | 0.500 | 0.640 | 0.561 |
| llama | qa | 50 | 0.500 | 0.500 | 1.000 | 0.667 |
| llama | dialogue | 50 | 0.560 | 0.538 | 0.840 | 0.656 |
| llama | summarization | 50 | 0.500 | 0.500 | 1.000 | 0.667 |
| gemma | qa | 50 | 0.580 | 0.833 | 0.200 | 0.323 |
| gemma | dialogue | 50 | 0.540 | 0.625 | 0.200 | 0.303 |
| gemma | summarization | 50 | 0.540 | 0.750 | 0.120 | 0.207 |

Pilot result: 0% ambiguous parses, all three models already showing distinct behavioral signatures (Llama trending toward always-"Yes", Gemma toward high-precision/low-recall). This was judged sufficient to proceed to the full run.

---

## 4. Full-Scale Results (N=500 per task → 1,000 scored judgements per model-task)

### 4.1 Summary Metrics

| model | task | n | ambiguous% | accuracy | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| **qwen3:1.7b** | qa | 1000 | 0.0% | 0.509 | 0.530 | 0.160 | 0.246 |
| **qwen3:1.7b** | dialogue | 1000 | 0.0% | 0.563 | 0.544 | 0.782 | 0.642 |
| **qwen3:1.7b** | summarization | 1000 | 0.0% | 0.444 | 0.457 | 0.588 | 0.514 |
| **llama3.2:1b** | qa | 1000 | 0.0% | 0.498 | 0.499 | 0.992 | 0.664 |
| **llama3.2:1b** | dialogue | 1000 | 0.0% | 0.503 | 0.502 | 0.842 | 0.629 |
| **llama3.2:1b** | summarization | 1000 | 0.0% | 0.500 | 0.500 | 1.000 | 0.667 |
| **gemma3:1b** | qa | 1000 | 0.0% | 0.512 | 0.567 | 0.102 | 0.173 |
| **gemma3:1b** | dialogue | 1000 | 0.0% | 0.488 | 0.430 | 0.074 | 0.126 |
| **gemma3:1b** | summarization | 1000 | 0.0% | 0.514 | 0.675 | 0.054 | 0.100 |

### 4.2 Raw Confusion Matrices

(TP = correctly flagged hallucination, FP = grounded answer wrongly flagged, TN = grounded answer correctly passed, FN = hallucination missed)

| model | task | TP | FP | TN | FN |
|---|---|---|---|---|---|
| qwen3:1.7b | qa | 80 | 71 | 429 | 420 |
| qwen3:1.7b | dialogue | 391 | 328 | 172 | 109 |
| qwen3:1.7b | summarization | 294 | 350 | 150 | 206 |
| llama3.2:1b | qa | 496 | 498 | 2 | 4 |
| llama3.2:1b | dialogue | 421 | 418 | 82 | 79 |
| llama3.2:1b | summarization | 500 | 500 | 0 | 0 |
| gemma3:1b | qa | 51 | 39 | 461 | 449 |
| gemma3:1b | dialogue | 37 | 49 | 451 | 463 |
| gemma3:1b | summarization | 27 | 13 | 487 | 473 |

Note the extremes: **Llama on summarization predicted "Yes" on all 1,000 instances** (TN=FN=0) — a complete class collapse. **Llama on QA** is nearly as degenerate (only 6/1000 "No" predictions total). **Gemma** shows the opposite collapse pattern but less extreme (it does predict "No" the vast majority of the time across all three tasks).

---

## 5. Key Findings

### 5.1 No model beats chance-level accuracy on any task

All nine accuracy values fall in a narrow band around 0.44–0.56 — statistically indistinguishable from random guessing at n=1000 (50% is the baseline for a balanced binary task, which this is by construction). **Accuracy alone is not a useful metric here** — every model's F1/precision/recall profile tells a very different story about *how* it's failing, even though raw accuracy looks similarly mediocre across the board.

### 5.2 Llama 3.2 1B: degenerate always-"Yes" strategy

Llama's recall is 0.84–1.00 and precision sits almost exactly at 0.50 on every task — the signature of a classifier that (almost) always predicts the positive class regardless of input. This is not "good hallucination detection dressed up as high recall" — it is functionally equivalent to flipping a coin weighted 99% toward "Yes." The summarization case is total collapse: literally every single one of 1,000 instances was judged "Yes," including 500 grounded right-summaries. This model is not discriminating at all on this task; it is not reading the answer/summary in any way that changes its output.

### 5.3 Gemma 3 1B: mirror-image degenerate always-"No" strategy

Gemma shows the opposite pathology: recall collapses to 0.05–0.10 while precision is inflated (0.43–0.68) purely because it says "Yes" so rarely that on the few occasions it does, it's more often right than wrong by chance. This model is systematically under-flagging hallucinations — it would be nearly useless as an actual hallucination detector in production despite its higher headline precision numbers, since it misses ~90-95% of true hallucinations.

### 5.4 Qwen3 1.7B: the only model showing real discriminative signal — with an anomaly

Qwen is the only model whose precision/recall pair isn't pinned near a degenerate extreme. Dialogue performance (F1=0.642, recall=0.782, precision=0.544) suggests it is doing some genuine reasoning about entity/fact consistency in dialogue responses. Summarization (F1=0.514) shows a real but weaker signal.

**Anomaly worth flagging:** Qwen's summarization *accuracy* (0.444) is the only accuracy value in the entire grid that falls **below** the 0.50 chance baseline — despite the task being perfectly class-balanced by construction. This means Qwen is systematically *worse than random* at this specific task, not merely noisy. This is the most interesting single result in the dataset and is a strong candidate for the qualitative error-analysis pass (§7): is it consistently mislabeling a particular hallucination subtype in summaries, or something more mechanical like document truncation (summarization documents are the longest inputs in the dataset, and the pipeline does not currently truncate to fit the model's context window)?

### 5.5 Cross-task pattern

Dialogue is the "easiest" task for both Qwen and Llama (highest accuracy and F1 of their three tasks), while summarization is the hardest for Qwen specifically. This is plausible given task structure: dialogue hallucinations in the HaluEval design are often entity-substitution errors (e.g., "Steven Spielberg" instead of "Christopher Nolan") which may be more lexically salient to a small model than the more diffuse, inference-based errors typical of summarization hallucinations (see the few-shot examples in `evaluation/summarization/summarization_evaluation_instruction.txt`).

### 5.6 Pilot vs. full-scale stability — a caution about small-N piloting

Comparing §3 (N=25) to §4.1 (N=500) shows most metrics were directionally stable, but some moved substantially — most notably **Gemma/dialogue precision fell from 0.625 (pilot) to 0.430 (full run)**, a 20-point swing. At N=25 per class-half (effectively ~12-13 positive predictions), single-digit count changes produce large percentage swings. This is a useful data point for the report: a 25-sample pilot is enough to validate pipeline mechanics (parsing, prompt behavior, non-degenerate output) but **not** enough to trust specific precision/recall values — those should always be read off the full N=500 run.

---

## 6. Operational Notes

- Total wall-clock time for the full 9,000-instance run: **~2 hours 55 minutes** (08:22–11:18 local time), across two background invocations.
- The run was interrupted once, mid-flight, after completing 5 of 9 model-task combinations plus 260/1000 instances of a sixth (`llama/summarization`) — killed by a session/host boundary, not a script error or crash. It was resumed by re-invoking the identical command; the pipeline's `instance_id`-based dedup against already-written output skipped all completed instances and continued exactly where it left off. Final per-file line counts confirmed exactly 1,000 instances in every one of the 9 output files — no data loss or duplication from the interruption.
- Per-instance latency varied substantially by task: QA and Dialogue instances averaged ~0.6s each; Summarization instances (much longer document contexts) averaged ~1.2–1.3s each, roughly 2x slower.

---

## 7. Limitations & Scope

- **This is a discrimination task, not a generation-quality test** (see §1) — results should not be characterized as "Model X hallucinates Y% of the time" in open-ended use; they characterize forced-choice judgement ability only.
- **Single deterministic sample per instance** (temperature=0, no repeated sampling) — no variance/confidence interval is reported per model-task cell. Given how close several models are to exact 50/50 degenerate behavior, repeated sampling at nonzero temperature could reveal whether the "always Yes"/"always No" pattern is a hard deterministic artifact of the prompt or a strong-but-not-total bias.
- **One frozen prompt per task** — no prompt-sensitivity study was run. Small models are known to be more sensitive to instruction phrasing than large ones; the specific "always Yes"/"always No" collapses observed for Llama/Gemma could in principle be partially an artifact of this exact prompt framing rather than a pure model-capability finding. This is explicitly flagged as future/bonus work, not scoped into this evaluation.
- **No context-length truncation for long documents** — summarization documents are not truncated to fit each model's context window before being sent to Ollama; extremely long documents could be silently truncated by Ollama's own context handling rather than the pipeline's. This is a candidate explanation for the Qwen summarization anomaly (§5.4) and should be checked during error analysis.
- **Qualitative error categorization not yet performed** — this document reports only quantitative discrimination metrics. The planned next step (five-category error schema applied to 20–30 false positives/negatives per model) will add interpretive depth to *why* each model fails, not just how often.

---

## 8. Recommended Next Step (in progress)

Apply the five-category error schema — minor error, unsupported claim, fabricated answer, confidently wrong, model confusion/ambiguous — to a sample of false positives and false negatives per model, drawn from `results/full/*_results.jsonl`. Given the degenerate-strategy findings above, the qualitative pass is likely to surface *why* Llama/Gemma collapsed to a single class (e.g., a fixed lexical trigger, an inability to use the context field at all) rather than a distribution of varied error types — that in itself would be a notable finding to report.

---

## Appendix A: File Manifest

```
HaluEval/
├── scripts/
│   ├── ollama_client.py          # Ollama HTTP client (think:false, retries, num_predict cap)
│   ├── evaluate_local_models.py  # Paired-sampling discrimination pipeline, resumable
│   └── compute_metrics.py        # Aggregates JSONL -> accuracy/precision/recall/F1 summary
├── results/
│   ├── pilot/
│   │   ├── {model}_{task}_results.jsonl   # 9 files, 50 instances each
│   │   └── summary.json
│   └── full/
│       ├── {model}_{task}_results.jsonl   # 9 files, 1000 instances each
│       └── summary.json
```

## Appendix B: Reproduction Command

```bash
cd HaluEval
for model in qwen llama gemma; do
  for task in qa dialogue summarization; do
    python3 scripts/evaluate_local_models.py --model $model --task $task \
      --sample_size 500 --seed 42 --output_dir results/full
  done
done
python3 scripts/compute_metrics.py --results_dir results/full --out results/full/summary.json
```
