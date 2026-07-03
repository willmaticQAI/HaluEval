# HaluEval Project: Goals, Metrics & Success Criteria

---

## 🎯 **Primary Goal**

```
QUESTION:
How often do small open-source LLMs (1B parameters) hallucinate, 
and does hallucination behavior differ across model families?

ANSWER THROUGH:
Reproducible evaluation of Qwen, Llama, and Gemma across QA, 
dialogue, and summarization tasks using the 35K-sample HaluEval 
benchmark.
```

---

## 📊 **Success Criteria (What "Done" Looks Like)**

### ✅ **By Midway Report (July 5-8)**

- [ ] **Evaluated all 3 models on all 3 tasks**
  - Qwen + QA, Dialogue, Summarization
  - Llama + QA, Dialogue, Summarization
  - Gemma + QA, Dialogue, Summarization
  - = 9 evaluation runs, ~4,500 total inferences

- [ ] **Computed 4 metrics per model-task pair:**
  - Accuracy (% of correct Yes/No predictions)
  - Precision (% of "Yes" predictions that were correct hallucinations)
  - Recall (% of actual hallucinations that were detected)
  - F1 (harmonic mean of precision & recall)

- [ ] **Created comparison table:**
  ```
  Model  | Task           | Accuracy | Precision | Recall | F1
  -------|----------------|----------|-----------|--------|-----
  Qwen   | QA             | 0.78     | 0.82      | 0.72   | 0.77
  Qwen   | Dialogue       | 0.75     | 0.79      | 0.69   | 0.74
  Qwen   | Summarization  | 0.81     | 0.85      | 0.75   | 0.80
  Llama  | QA             | 0.76     | 0.80      | 0.70   | 0.75
  ... (9 rows total)
  ```

- [ ] **Error analysis:**
  - 20-30 false positives categorized (why marked as hallucination when they weren't?)
  - 20-30 false negatives categorized (why hallucinations went undetected?)
  - Identified ambiguous cases (model said "maybe"?)

- [ ] **Methods section written:**
  - Which models tested and why
  - How samples were selected (random, full dataset, or stratified?)
  - Prompting strategy (exact prompt used for evaluation)
  - Metric definitions (how you calculated precision/recall/F1)

---

### ✅ **By Final Report (July 23)**

Everything above, plus:

- [ ] **Visualization 1: Accuracy Heatmap**
  ```
                QA    Dialogue  Summarization
  Qwen        [0.78]   [0.75]      [0.81]
  Llama       [0.76]   [0.72]      [0.79]
  Gemma       [0.74]   [0.70]      [0.77]
  ```

- [ ] **Visualization 2: Precision vs. Recall Trade-off**
  - 3 dots per task (one per model)
  - Shows which model balances catching hallucinations vs. avoiding false alarms

- [ ] **Qualitative Analysis:**
  - Example of a hallucination the model caught (true positive)
  - Example of a hallucination the model missed (false negative)
  - Example of a correct answer marked as hallucinated (false positive)
  - Why each occurred (ambiguous phrasing? model confusion? prompt issue?)

- [ ] **Task-Specific Insights:**
  - Which task is hardest? (QA: requires world knowledge; Dialogue: requires context; Summarization: requires faithful reproduction)
  - Do models hallucinate more in certain domains?
  - Is there a model that excels at one task but struggles at another?

- [ ] **Reproducible Code:**
  - GitHub repo (or shared code) with:
    - Data loading scripts
    - Evaluation pipeline (infer from all 3 models)
    - Result aggregation (compute metrics)
    - Visualization generation
  - Clear README with exact steps to reproduce

---

## 📈 **Key Metrics Explained**

### **Accuracy**
```
= (Correct predictions) / (Total predictions)
= (TP + TN) / (TP + TN + FP + FN)

Example: If model correctly identified 390 of 500 hallucinations:
Accuracy = 390 / 500 = 78%
```
**Interpretation:** Rough overall performance, but not sufficient alone (skewed by class distribution).

### **Precision**
```
= (True Positives) / (Predicted Positives)
= TP / (TP + FP)

"Of all the times the model said 'Yes, hallucination detected',
how often was it correct?"
```
**Interpretation:** If precision is low, the model is overly cautious (flags too many false hallucinations).

### **Recall**
```
= (True Positives) / (Actual Positives)
= TP / (TP + FN)

"Of all the actual hallucinations in the dataset,
how many did the model catch?"
```
**Interpretation:** If recall is low, the model misses real hallucinations.

### **F1 Score**
```
= 2 × (Precision × Recall) / (Precision + Recall)

Balances precision and recall (punishes models that are good at
one but bad at the other).
```

---

## 🗂️ **Data Structure: What You're Evaluating**

### **Example: QA Task**

```json
{
  "knowledge": "Python is a programming language created by Guido van Rossum. 
                It was first released in 1991.",
  "question": "Who created Python and when?",
  "right_answer": "Python was created by Guido van Rossum in 1991.",
  "hallucinated_answer": "Python was created by Linus Torvalds in 1985."
}
```

**Evaluation:**
- Show model the knowledge + question + **hallucinated answer**
- Model should respond: **"Yes, hallucination detected"** (they said Linus Torvalds, wrong!)
- If model says "No", that's a **false negative** (missed the hallucination)

---

### **Example: Dialogue Task**

```json
{
  "knowledge": "Alice is a doctor. Bob is an engineer.",
  "dialogue_history": "Q: What is Alice's profession?\nA: ",
  "right_response": "Alice is a doctor.",
  "hallucinated_response": "Alice works as a lawyer."
}
```

**Evaluation:**
- Model reads knowledge + dialogue
- Should answer **"Yes"** (hallucination detected—she's a doctor, not a lawyer)

---

### **Example: Summarization Task**

```json
{
  "document": "The new climate policy requires companies to reduce 
              emissions by 50% by 2030. The deadline is mandatory.",
  "right_summary": "A climate policy mandates 50% emission reduction by 2030.",
  "hallucinated_summary": "The climate policy was rejected by Congress and 
                          will not be implemented."
}
```

**Evaluation:**
- Model reads document + summary
- Should answer **"Yes"** (hallucination—the document says policy IS mandatory, not rejected)

---

## 💾 **Output Structures**

### **Individual Result File** (per model-task pair)
```json
{
  "model": "qwen",
  "task": "qa",
  "num_samples": 500,
  "accuracy": 0.78,
  "precision": 0.82,
  "recall": 0.72,
  "f1": 0.77,
  "elapsed_seconds": 1245.3,
  "results": [
    {
      "sample_id": 0,
      "question": "Who created Python?",
      "answer": "Python was created by Linus Torvalds in 1985.",
      "is_hallucinated": true,
      "model_response": "Yes, the answer contains hallucination.",
      "prediction": "Yes",
      "correct": true,
      "error_type": null
    },
    {
      "sample_id": 1,
      "question": "What is the capital of France?",
      "answer": "Paris is the capital of France.",
      "is_hallucinated": false,
      "model_response": "No, the answer is correct.",
      "prediction": "No",
      "correct": true,
      "error_type": null
    },
    {
      "sample_id": 2,
      "question": "What color is the sky?",
      "answer": "The sky is green.",
      "is_hallucinated": true,
      "model_response": "Actually, that's... probably not right. No.",
      "prediction": "No",
      "correct": false,
      "error_type": "false_negative"  # Missed hallucination
    }
  ]
}
```

### **Comparative Summary** (for report)
```
| Model | QA Acc | QA F1 | Dial Acc | Dial F1 | Sum Acc | Sum F1 | Avg Acc |
|-------|--------|-------|----------|---------|---------|--------|---------|
| Qwen  | 0.78   | 0.77  | 0.75     | 0.74    | 0.81    | 0.80   | 0.78    |
| Llama | 0.76   | 0.75  | 0.72     | 0.71    | 0.79    | 0.78   | 0.76    |
| Gemma | 0.74   | 0.73  | 0.70     | 0.69    | 0.77    | 0.76   | 0.74    |
```

---

## 🔍 **Error Categorization (Qualitative Analysis)**

For each false positive and false negative, categorize:

| Category | Definition | Example |
|----------|-----------|---------|
| **Minor Error** | Detail wrong, core answer correct | Q: "What year was Python released?" A: "1990" (actually 1991, off by 1 year) |
| **Unsupported Claim** | Answer reasonable but not in knowledge base | Q: "How many languages are spoken in Europe?" A: "54 languages" (reasonable guess, but not grounded) |
| **Fabricated Answer** | Completely made-up content | Q: "Who is the CEO of Apple?" A: "Bob Johnson" (doesn't exist) |
| **Confidently Wrong** | Nonsensical or self-contradictory | Q: "What color is red?" A: "Red is blue." |
| **Model Confusion** | Ambiguous phrasing in prompt | Response is borderline—could go either way |

---

## 📅 **Timeline with Metric Milestones**

| Week | Task | Deliverable |
|------|------|-------------|
| Jun 1-5 | Setup | ✓ Ollama/HF running, data verified |
| Jun 6-10 | Implement | ✓ evaluate_local_models.py working on 50-sample test |
| Jun 11-20 | **Evaluate** | ✓ **All 9 results complete (9 JSON files)** |
| Jun 21-25 | Validate | ✓ Error analysis (30 samples per model) |
| Jun 26-Jul 5 | Aggregate | ✓ **Metrics computed, visualizations drafted** |
| **Jul 5-8** | **MIDWAY REPORT** | ✓ **Accuracy table + error analysis + methods** |
| Jul 8-15 | Analysis | ✓ Task-specific insights, prompt variations |
| Jul 16-22 | **FINAL REPORT** | ✓ **All visualizations, qualitative analysis, discussion** |
| Jul 23+ | Presentation | ✓ Slides with key findings |

---

## 🎲 **Potential Findings (What You Might Discover)**

### **Scenario 1: Consistent Performance**
```
All models perform similarly (~75-80% accuracy across tasks)
→ Hallucination detection is task-hard, not model-dependent
→ Need better prompts or evaluation methods
```

### **Scenario 2: Model-Dependent**
```
Qwen > Llama > Gemma across all tasks
→ Suggest Qwen is better at recognizing hallucinations
→ Could correlate with: training data, architecture, size
```

### **Scenario 3: Task-Dependent**
```
All models perform well on QA (0.80), 
struggle on Dialogue (0.65), moderate on Summarization (0.75)
→ Dialogue is inherently harder (requires context)
→ QA has clearer factual grounding
```

### **Scenario 4: Mixed Results**
```
Qwen excels at QA (0.85) but struggles at Dialogue (0.68)
Llama has balanced performance across tasks
→ Different models have different strengths
→ Useful for selecting models for specific tasks
```

---

## ✨ **Bonus Analyses** (If Time Permits)

### **Prompt Variation Study**
Run same samples with different prompts:
1. Direct: "Is this hallucination?" 
2. Reframing: "Is this claim supported by the knowledge?"
3. Chain-of-thought: "Let me think step by step..."

→ See which prompt elicits better detection

### **Sample Difficulty**
Categorize HaluEval samples by "difficulty":
- **Easy hallucinations:** Obviously false (e.g., "Paris is in Germany")
- **Hard hallucinations:** Plausible but false (e.g., "Python released in 1990" vs 1991)

→ See if models struggle more with subtle hallucinations

### **Explanation Generation**
Ask models to explain their Yes/No decision:
- "Yes, hallucination detected because..."
- "No, this is correct because..."

→ Evaluate quality of explanations (bonus signal)

---

## 📝 **Midway Report Template**

```markdown
# HaluEval: Measuring Hallucination Rates in Open-Source LLMs
## Midway Report (July 5-8)

### Executive Summary
We evaluated three open-source language models (Qwen, Llama, Gemma) 
on their ability to detect hallucinations across three tasks using 
the HaluEval benchmark.

### Methods
- **Models:** Qwen 1.5B, Llama 3.2 1B, Gemma 2 1B
- **Tasks:** QA (500 samples), Dialogue (500), Summarization (500)
- **Evaluation:** Did model correctly identify hallucinated answers?
- **Metrics:** Accuracy, Precision, Recall, F1

### Results
[INSERT ACCURACY TABLE HERE]

### Key Findings
1. [Which model performs best overall?]
2. [Which task is hardest?]
3. [Any surprising differences?]

### Error Analysis
- False positives: X% (model overly cautious)
- False negatives: Y% (model misses hallucinations)
- Ambiguous: Z% (model unsure)

### Next Steps
- Extended analysis on harder subset of samples
- Prompt variation experiments
- Task-specific deep dive
```

---

## ✅ **Definition of Done**

**Minimum (Midway):**
- 9 evaluation runs completed
- Metrics table with all 4 metrics per model-task
- Error analysis with categorization
- Methods section for report

**Full (Final Report):**
- All above + 2 visualizations
- Task-specific discussion (why dialogue harder than QA?)
- Reproducible code repository
- Clear narrative explaining findings

---

**The goal isn't perfect accuracy—it's to understand where and why these models hallucinate, and to create a pipeline that future researchers can use to evaluate other models.**
