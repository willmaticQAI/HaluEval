# HaluEval Project: Proposal Breakdown & Refocused Scope

**Project Team:** Sushmita Hari, Connor Fahs, William McDonald, Sriram Rella

---

## 🎯 **Primary Goal**

Build a **reproducible, comparative hallucination evaluation pipeline** that measures how often open-source LLMs hallucinate across different task types and model families.

Unlike single-model evaluation, the goal is to generate empirical data showing:
- Which models hallucinate more/less frequently
- How hallucination rates vary by task type (QA, dialogue, summarization)
- Whether larger models genuinely hallucinate less
- Which evaluation approaches catch hallucinations most effectively

---

## 📊 **Focused Scope: 3-Model Evaluation**

### Current Proposal (6+ models)
- Qwen 2.5 0.5B
- TinyLlama 1.1B
- Llama 3.2 1B
- Qwen 2.5 1.5B
- Phi-3.5 Mini
- Gemma 3 1B

### ✅ **Recommended Refocus (3 models)**
1. **Qwen 3** (1B-1.5B)
2. **Llama 3.2 1B** (strong baseline, widely used)
3. **Gemma 2 1B** (Google's efficient model, good comparison point)

**Rationale for refocus:**
- Reduces inference time (3 models × 3 tasks ≈ 12 evaluations vs. 18+)
- Allows deeper analysis per model (more prompt variations, error categorization)
- Covers three different model families (Alibaba, Meta, Google)
- All runnable locally via Ollama or HuggingFace Transformers
- Aligns with timeline (midway report in early July)

---

## 📋 **Project Structure Breakdown**

### **Phase 1: Setup & Data Preparation** (June 1-6)
**Current Status:** ✅ Mostly complete

The HaluEval codebase provides:
- **35K annotated hallucination examples** across 4 categories:
  - QA: 10K examples (from HotpotQA seed data)
  - Dialogue: 10K examples (from OpenDialKG seed data)
  - Summarization: 10K examples (from CNN/DailyMail seed data)
  - General: 5K examples (human-labeled ChatGPT responses)

**Your tasks:**
- [x] Download / verify HaluEval datasets
- [ ] Create sampling strategy for 3-model evaluation (e.g., 500-1000 samples per task to keep runtime manageable)
- [ ] Set up local environment (Ollama or HF Transformers for Qwen, Llama, Gemma)
- [ ] Verify model access and memory requirements

---

### **Phase 2: Pipeline Implementation** (June 7-27)
**Goal:** Adapt HaluEval's evaluation framework from OpenAI models → local open-source models

**Current Codebase:**
The `evaluation/evaluate.py` script is currently hardcoded for:
- OpenAI API (gpt-3.5-turbo, davinci)
- API-based inference with rate limiting

**What you need to build:**
1. **Inference adapter** for local models:
   - Load Qwen, Llama, Gemma from HuggingFace or Ollama
   - Batch inference with temperature=0.0 (deterministic evaluation)
   - Memory-efficient inference (use quantized versions if needed)

2. **Hallucination detection prompt** (adapted for local models):
   - Current: "Determine if the answer contains hallucination"
   - Output format: Strictly "Yes" or "No" (for metric calculation)
   - May need calibration—local models interpret instructions differently

3. **Evaluation loop** for all 3 tasks:
   - QA: (knowledge, question, answer) → detect hallucination
   - Dialogue: (dialogue_history, response) → detect hallucination
   - Summarization: (document, summary) → detect hallucination

**Deliverable:** `evaluate_local_models.py` with:
```python
def evaluate(model_name, task, dataset_path, sample_size=500):
    # Load model (Qwen, Llama, Gemma)
    # Load dataset (QA, dialogue, summarization)
    # For each sample:
    #   - Create prompt
    #   - Get model response
    #   - Parse "Yes"/"No"
    #   - Log result with timing
    # Return results.json
```

---

### **Phase 3: Validation & Analysis** (June 27 - July 5)
**Goal:** Ensure scoring is consistent and comparable

**Validation steps:**
1. **Consistency check:** Run same sample twice on same model → should get identical results
2. **Format validation:** Every response cleanly parses to "Yes"/"No"
3. **Baseline sanity check:** 
   - Accuracy on ground-truth examples should be high (>70%)
   - Accuracy on hallucinated examples should be lower
4. **Manual spot-check:** Review 20-30 borderline cases per task
   - Is the model detecting actual hallucinations or just disagreeing with phrasing?

**Output:** `validation_report.md` documenting:
- Consistency rates
- Format parse success rates
- Example errors and edge cases

---

### **Phase 4: Midway Report** (July 5-8)
**What to include:**
- Completed evaluations for 3 models × 3 tasks
- Hallucination rates by model and task type
- Comparison table (accuracy, precision, recall, F1)
- Error analysis: common hallucination types (unsupported claims, fabricated facts, etc.)
- Any implementation challenges encountered
- Updated timeline for final report

**Methods section template** (from your earlier work):
```
We evaluated three open-source LLMs:
- Qwen 3 1.5B
- Llama 3.2 1B
- Gemma 2 1B

Each model was evaluated on 500 samples per task (QA, dialogue, summarization)
using the HaluEval benchmark. Models were queried via [Ollama/HF Transformers]
with temperature=0 for deterministic responses.

Evaluation metric: Hallucination detection accuracy (correct "Yes"/"No" predictions)
```

---

### **Phase 5: Extended Analysis & Final Report** (July 8-23)

**Quantitative Metrics:**
| Metric | By Task Type | By Model | By Size |
|--------|--------------|----------|---------|
| Hallucination Rate | ✓ | ✓ | (3 different models) |
| Accuracy | ✓ | ✓ | Compare across |
| Precision (catching hallucinations) | ✓ | ✓ | |
| Recall (catching hallucinations) | ✓ | ✓ | |
| F1 Score | ✓ | ✓ | |

**Qualitative Analysis:**
Label false positives and false negatives:
- **Minor factual error** (small detail wrong, core answer correct)
- **Unsupported claim** (answer reasonable but not grounded in knowledge)
- **Fabricated answer** (completely made-up content)
- **Confidently wrong** (nonsensical or contradictory answer)

**Optional enhancements** (if time allows):
- Prompt variation test: Direct detection vs. "first judge if response is supported"
- Task-specific analysis: Do models hallucinate differently in QA vs. dialogue?
- Error correlation: Which model pair has most similar error patterns?

---

## 🛠️ **Technical Architecture**

### Current HaluEval Codebase
```
HaluEval/
├── data/                    # 35K benchmark samples
│   ├── qa_data.json        # (knowledge, question, right_answer, hallucinated_answer)
│   ├── dialogue_data.json   # (knowledge, dialogue_history, right_response, hallucinated_response)
│   ├── summarization_data.json # (document, right_summary, hallucinated_summary)
│   └── general_data.json    # (user_query, chatgpt_response, hallucination_label)
│
├── generation/              # Code for creating hallucinated samples (ChatGPT-based)
│   ├── generate.py
│   ├── filtering.py
│   └── [task-specific instructions]
│
├── evaluation/              # ⚠️ NEEDS MODIFICATION
│   ├── evaluate.py         # Currently OpenAI API only
│   └── [task instructions]
│
└── analysis/                # Post-evaluation analysis
    └── analyze.py          # LDA topic modeling
```

### Your Adaptations
```
New files to create:
├── models/
│   ├── qwen_loader.py       # Load Qwen 3 from HF/Ollama
│   ├── llama_loader.py      # Load Llama 3.2 1B
│   └── gemma_loader.py      # Load Gemma 2 1B
│
├── evaluation/
│   ├── evaluate_local.py    # ← Replace OpenAI evaluate.py
│   └── prompts.py           # Task-specific prompts for local models
│
├── results/
│   ├── qwen_qa_results.json
│   ├── qwen_dialogue_results.json
│   ├── llama_qa_results.json
│   └── [... 9 files total]
│
└── analysis/
    ├── comparative_analysis.py  # Compare 3 models
    └── error_analysis.py        # Categorize false positives/negatives
```

---

## 📈 **Evaluation Metrics**

For each model × task combination:

```
{
  "model": "qwen",
  "task": "qa",
  "samples_evaluated": 500,
  "accuracy": 0.78,
  "precision": 0.82,    # TP / (TP + FP) - how often "Yes" is correct
  "recall": 0.72,       # TP / (TP + FN) - how many hallucinations caught
  "f1": 0.77,
  "hallucination_rate": 0.45,  # % of samples detected as hallucinated
  "false_positive_rate": 0.18,  # % of ground-truth answers marked as hallucinated
  "results": [
    {
      "sample_id": 1,
      "knowledge": "...",
      "question": "...",
      "answer": "...",
      "is_hallucinated": true,
      "model_prediction": "Yes",
      "correct": true,
      "error_type": null
    },
    ...
  ]
}
```

---

## ⏱️ **Revised Timeline**

| Dates | Milestone | Owner(s) |
|-------|-----------|----------|
| Jun 1–5 | Verify data setup, test model loading (Ollama/HF) | William |
| Jun 6–10 | Implement local model inference adapter | William |
| Jun 11–20 | Run full evaluation pipeline (3 models × 3 tasks) | Team |
| Jun 21–25 | Validation & consistency checks | Sushmita/Connor |
| Jun 26–Jul 5 | Error analysis & manual review | Sriram/William |
| **Jul 5–8** | **Midway Report** | All |
| Jul 8–15 | Extended analysis (prompt variations, task comparisons) | Team |
| Jul 16–22 | Final visualizations, write-up | All |
| After Jul 23 | Presentation prep | All |

---

## 💡 **Key Implementation Challenges & Solutions**

| Challenge | Solution |
|-----------|----------|
| **Output parsing:** Local models may not strictly say "Yes"/"No"** | Use fuzzy matching: detect "yes/no" in any response, log ambiguous cases |
| **Hallucination prompt calibration:** Different models interpret instructions differently | Test prompt variations; track which phrasing works best per model |
| **Memory constraints:** 1B models still ~2-4GB VRAM | Use quantized versions (4-bit); run inference sequentially, not in parallel |
| **Slow inference:** 3 models × 500 samples/task = 4,500 inferences | Batch where possible; use GPU acceleration (CUDA if available) |
| **Ground-truth variability:** Some "hallucinations" in HaluEval are borderline | Manual review of 20-30 samples; document disagreements in error analysis |

---

## 📄 **Deliverables Summary**

### By Midway Report (July 5-8)
- ✅ Completed evaluation results (3 models × 3 tasks)
- ✅ Comparative accuracy/precision/recall table
- ✅ Methods section (detailed prompt, sampling strategy)
- ✅ Initial error analysis (categorization of hallucination types)

### By Final Report (July 23)
- ✅ All quantitative metrics by model, task, and error type
- ✅ Visualizations (bar charts: accuracy by task/model, confusion matrices)
- ✅ Qualitative analysis with example errors
- ✅ Discussion of findings (which model is most reliable? Which tasks hardest?)
- ✅ Code repository with fully reproducible pipeline

---

## 🎓 **Connection to Coursework**

**DATA-780 (ML):** This project applies supervised learning concepts:
- Classification task: detect hallucination (Yes/No)
- Evaluation metrics: precision, recall, F1 (covered in HW/lectures)
- Model comparison: understand why different architectures perform differently

**DATA-750 (Linear Algebra):** Understanding model architecture:
- Attention mechanisms in transformers rely on matrix operations
- Why smaller models (1B params) can still be competitive
- Condition numbers of weight matrices affect numerical stability

---

## 🚀 **Next Steps**

1. **This week:** Finalize model choices (confirm Qwen 3, Llama 3.2, Gemma 2 availability)
2. **By Jun 5:** Test local inference setup (Ollama or HF Transformers)
3. **By Jun 10:** First end-to-end evaluation on 50-sample pilot
4. **By Jun 20:** Full pipeline running on all 3 models × 3 tasks
5. **Jun 25–Jul 5:** Midway report prep and error analysis

---

**Questions to clarify:**
- Will you use **Ollama** (simpler, pre-optimized) or **HuggingFace Transformers** (more flexible)?
- Do you have GPU access for faster inference, or CPU only?
- Any specific model **quantization** preferences (4-bit vs. 8-bit vs. full precision)?
- Should evaluation be **deterministic** (temp=0) or sample multiple responses per prompt?
