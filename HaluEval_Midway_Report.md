# HaluEval: Measuring Hallucination Rates in Open-Source LLMs
## Midway Report (July 5–8, 2026)

**Team:** Sushmita Hari, Connor Fahs, William McDonald, Sriram Rella

---

### Executive Summary

We evaluated three open-source language models — Qwen3 1.7B, Llama 3.2 1B, and Gemma 3 1B — on their ability to discriminate between grounded and hallucinated answers across three HaluEval tasks (QA, Dialogue, Summarization), using a corrected paired-sampling protocol that scores both directions of each sample (9,000 total judgements). **None of the three models reliably beat chance-level accuracy.** Qualitative error analysis shows this is largely because two of the three models collapse to a fixed response bias — one always predicting "hallucinated," the other almost always predicting "grounded" — rather than genuinely evaluating content, while the third model shows partial, genuine (if weak) discriminative signal.

### Methods

- **Models:** Qwen3 1.7B, Llama 3.2 1B, Gemma 3 1B — all run locally via Ollama, temperature 0.0. (Note: the original plan specified "Gemma 2 1B," but Ollama's Gemma 2 line has no 1B tag; Gemma 3 1B was substituted as the closest available match.)
- **Tasks:** QA (500 sampled items), Dialogue (500), Summarization (500) — HaluEval discrimination benchmark, seed=42.
- **Evaluation protocol:** each sampled item is judged twice — once with its `right_answer` (expected judgement "No") and once with its `hallucinated_answer` (expected judgement "Yes") — producing 1,000 scored judgements per model-task pair and 9,000 total. This paired design was a deliberate fix to the original draft pipeline, which only tested hallucinated answers and left precision/recall undefined.
- **Metrics:** Accuracy, Precision, Recall, F1, computed from pooled TP/FP/TN/FN per model-task pair.
- **Prompting:** two silent small-model failure modes were found and fixed during smoke testing before scaling up — Llama echoing the few-shot prompt instead of answering, and Qwen3's "thinking" mode consuming the output budget with no final answer. After both fixes, parsing was 100% clean (0 ambiguous responses across all 9,000 judgements).

### Results

| Model | QA Acc | QA F1 | Dialogue Acc | Dialogue F1 | Summ. Acc | Summ. F1 | **Avg Acc** | **Avg F1** |
|---|---|---|---|---|---|---|---|---|
| Qwen3 1.7B | 0.509 | 0.246 | 0.563 | 0.642 | 0.444 | 0.514 | **0.505** | **0.467** |
| Llama 3.2 1B | 0.498 | 0.664 | 0.503 | 0.629 | 0.500 | 0.667 | **0.500** | **0.653** |
| Gemma 3 1B | 0.512 | 0.173 | 0.488 | 0.126 | 0.514 | 0.100 | **0.505** | **0.133** |

Full 9-row accuracy/precision/recall/F1 table and confusion matrices (TP/FP/TN/FN per cell) are in `HaluEval_Findings_and_Analysis.md` §4.1–4.2. Visualizations (accuracy heatmap, precision/recall scatter) are in the same document, §4.3.

### Key Findings

1. **No model "wins" in any meaningful sense — and the obvious metric to rank them by is actively misleading.** All nine accuracy values sit within ±6 percentage points of the 0.50 chance baseline. Average F1 superficially favors Llama (0.653 vs. Qwen's 0.467 and Gemma's 0.133), but this is an artifact of Llama's near-constant "Yes" bias inflating recall (0.84–1.00) while precision sits at chance (~0.50) — not genuine hallucination-detection skill. **This is worth calling out explicitly in the report: F1 alone would rank Llama "best" here, and that ranking would be wrong.**

2. **Task difficulty is model-dependent, not universal.** Dialogue is the easiest task for both Qwen and Llama, but Qwen's Summarization accuracy (0.444) is the only value in the entire 9-cell grid that falls *below* chance — a genuine anomaly (not just noise, since the task is class-balanced by construction) and a strong candidate for follow-up analysis (e.g., checking whether long summarization documents are being silently truncated).

3. **Only Qwen3 shows non-degenerate behavior.** Llama collapses to an almost-always-"Yes" strategy and Gemma collapses to an almost-always-"No" strategy. Qualitative review of 90 sampled errors confirms these are not content-driven judgements: 100% of sampled false positives for all three models reflect fixed response bias rather than a graded content error, and Llama's rare "No" predictions still miss comically obvious fabrications (e.g., "the Green Bay Packers are actually coached by Joe Biden"), indicating its occasional "No" is noise around a fixed bias, not a moment of real reasoning.

### Error Analysis

Blended across all 9,000 judgements:

- **False positives: 25.2%** of all judgements (2,266/9,000) — grounded answers wrongly flagged as hallucinated. Driven overwhelmingly by Llama's and Qwen's over-flagging tendency.
- **False negatives: 24.5%** of all judgements (2,203/9,000) — real hallucinations missed. Driven overwhelmingly by Gemma's under-flagging tendency.
- **Ambiguous: 0.0%** (0/9,000) — no unparseable model responses after the prompt fixes described in Methods.

Qualitative categorization (90-sample manual review using the five-category schema: minor error, unsupported claim, fabricated answer, confidently wrong, model confusion/ambiguous):

- **Every sampled false positive across all three models** falls into "model confusion" — because these are all correct answers with no real hallucination present, so the false-positive rate for Llama and Gemma is a direct readout of fixed response bias, not content sensitivity.
- **False negatives show real spread for Qwen and Gemma** (all five categories represented), concentrated on the hardest cases — near-neighbor entity substitutions and evasive non-answers — while **Llama's false negatives skew toward blatant fabrications** it still fails to catch.
- A secondary finding: ~4.4% of the 90 sampled examples contained dataset-label content that a careful human reader would judge as arguably true despite being labeled "hallucinated" (e.g., a true claim about DiCaprio in *The Aviator*) — a small but nonzero dataset-noise ceiling worth a caveat in the final report, independent of model performance.

Full categorized sample (all 90 examples with rationale) is in `HaluEval_Error_Analysis.md`.

### Next Steps

- Expand task-specific discussion for the final report: why Dialogue is easier than Summarization across models, and whether hallucination type clusters by domain.
- Prompt-variation study: test whether Llama's and Gemma's degenerate strategies are artifacts of this specific prompt framing or robust across phrasings (direct "is this a hallucination?" vs. "is this supported by the knowledge?").
- Secondary dataset (e.g., TruthfulQA) to test whether these findings generalize beyond HaluEval.
- Small synthetic ground-truth test set to independently validate the pipeline.
- Two required final-report visualizations (accuracy heatmap, precision/recall scatter) are already complete — see `HaluEval_Findings_and_Analysis.md` §4.3 — ahead of the Jul 23 deadline.

---

**Supporting materials** (all in this repository, `willmcd` branch):
- `HaluEval_Findings_and_Analysis.md` / `.docx` — full quantitative methodology, results, and visualizations
- `HaluEval_Error_Analysis.md` / `.docx` — full 90-sample qualitative error categorization
- `scripts/` — reproducible evaluation pipeline (`evaluate_local_models.py`, `compute_metrics.py`, `generate_visualizations.py`)
- `results/full/` — raw per-instance judgements (9 JSONL files, 1,000 lines each) and `summary.json`
