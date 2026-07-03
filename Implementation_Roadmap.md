# HaluEval Implementation Roadmap

## Quick Overview: What You're Building

```
Input:  Model + Task + Sample
        ↓
[Your Pipeline]
        ↓
Output: Hallucination Detection Score (Yes/No)
        ↓
Aggregate: Accuracy, Precision, Recall, F1
```

**3 Models to evaluate:**
- Qwen 3 (1B or 1.5B)
- Llama 3.2 1B
- Gemma 2 1B

**3 Task types** (from HaluEval dataset):
- QA: Does the answer hallucinate facts?
- Dialogue: Is the response grounded in knowledge?
- Summarization: Does the summary stick to source material?

---

## Step 1: Environment Setup (June 1-5)

### Option A: Use Ollama (Easiest)
```bash
# Install Ollama (https://ollama.ai)
curl https://ollama.ai/install.sh | sh

# Pull models
ollama pull qwen:1.5b
ollama pull llama2:1b
ollama pull gemma:1b

# Start Ollama server
ollama serve
# (In another terminal, test:)
curl http://localhost:11434/api/generate -d '{"model":"qwen:1.5b","prompt":"Hello"}'
```

### Option B: Use HuggingFace Transformers (More Control)
```bash
pip install transformers torch ollama

# Models available:
# - Qwen: https://huggingface.co/Qwen/Qwen-1.5B
# - Llama: https://huggingface.co/meta-llama/Llama-2-1b
# - Gemma: https://huggingface.co/google/gemma-1b
```

**Recommendation:** Start with **Ollama** for simplicity, switch to HuggingFace if you need custom quantization.

---

## Step 2: Data Inspection (June 1-5)

```python
import json

# Load and inspect one sample from each task
tasks = ['qa', 'dialogue', 'summarization']

for task in tasks:
    with open(f'HaluEval-willmcd/data/{task}_data.json') as f:
        samples = json.load(f)
        print(f"\n=== {task.upper()} ===")
        print(f"Total samples: {len(samples)}")
        print(f"Fields: {samples[0].keys()}")
        print(f"Example:\n{json.dumps(samples[0], indent=2)[:500]}...")
```

**Expected structure:**

**QA:**
```json
{
  "knowledge": "Paris is the capital of France...",
  "question": "What is the capital of France?",
  "right_answer": "Paris",
  "hallucinated_answer": "London"
}
```

**Dialogue:**
```json
{
  "knowledge": "Alice is a doctor.",
  "dialogue_history": "Q: What does Alice do?\nA: ",
  "right_response": "Alice is a doctor.",
  "hallucinated_response": "Alice is a lawyer."
}
```

**Summarization:**
```json
{
  "document": "The new policy requires...",
  "right_summary": "A policy change was announced.",
  "hallucinated_summary": "The policy was rejected by Congress." (false)
}
```

---

## Step 3: Core Evaluation Module (June 6-10)

Create `evaluate_local_models.py`:

```python
import json
import time
import argparse
from typing import Dict, List, Tuple
import requests  # For Ollama API

class HaluEvalPipeline:
    def __init__(self, model_name: str, api_base: str = "http://localhost:11434"):
        """
        Args:
            model_name: "qwen", "llama", or "gemma"
            api_base: Ollama API endpoint
        """
        self.model_name = model_name
        self.api_base = api_base
        self.model_map = {
            "qwen": "qwen:1.5b",
            "llama": "llama2:1b",
            "gemma": "gemma:1b"
        }
        self.ollama_model = self.model_map.get(model_name)
        
    def get_model_response(self, prompt: str) -> str:
        """Query Ollama and get hallucination detection response."""
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "temperature": 0.0,  # Deterministic
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"].strip()
        except Exception as e:
            print(f"Error calling model: {e}")
            return "ERROR"
    
    def parse_yes_no(self, response: str) -> str:
        """Extract Yes/No from model response."""
        response_lower = response.lower()
        
        # Fuzzy matching
        if "yes" in response_lower:
            return "Yes"
        elif "no" in response_lower:
            return "No"
        else:
            return "AMBIGUOUS"  # Log for manual review
    
    def evaluate_qa(self, sample: Dict) -> Dict:
        """Evaluate a QA sample."""
        instruction = (
            "You are a hallucination detector. "
            "Determine if the answer contains hallucination for the question. "
            "Answer only 'Yes' (hallucination detected) or 'No' (no hallucination)."
        )
        
        prompt = (
            f"{instruction}\n\n"
            f"Knowledge: {sample['knowledge']}\n"
            f"Question: {sample['question']}\n"
            f"Answer: {sample['hallucinated_answer']}\n"
            f"Your judgment: "
        )
        
        response = self.get_model_response(prompt)
        prediction = self.parse_yes_no(response)
        
        return {
            "sample_id": sample.get("id"),
            "knowledge": sample["knowledge"][:100],  # Truncate for storage
            "question": sample["question"],
            "answer": sample["hallucinated_answer"],
            "is_hallucinated": True,  # This is a hallucinated sample
            "model_response": response,
            "prediction": prediction,
            "correct": prediction == "Yes"  # Correct if model said "Yes" (detected hallucination)
        }
    
    def evaluate_dialogue(self, sample: Dict) -> Dict:
        """Evaluate a dialogue sample."""
        instruction = (
            "You are a hallucination detector. "
            "Determine if the response is grounded in the knowledge. "
            "Answer only 'Yes' (hallucination detected) or 'No' (grounded)."
        )
        
        prompt = (
            f"{instruction}\n\n"
            f"Knowledge: {sample['knowledge']}\n"
            f"Dialogue: {sample['dialogue_history']}\n"
            f"Response: {sample['hallucinated_response']}\n"
            f"Your judgment: "
        )
        
        response = self.get_model_response(prompt)
        prediction = self.parse_yes_no(response)
        
        return {
            "sample_id": sample.get("id"),
            "dialogue": sample["dialogue_history"][:100],
            "response": sample["hallucinated_response"],
            "is_hallucinated": True,
            "model_response": response,
            "prediction": prediction,
            "correct": prediction == "Yes"
        }
    
    def evaluate_summarization(self, sample: Dict) -> Dict:
        """Evaluate a summarization sample."""
        instruction = (
            "You are a hallucination detector. "
            "Determine if the summary contains information not in the document. "
            "Answer only 'Yes' (hallucination detected) or 'No' (faithful)."
        )
        
        prompt = (
            f"{instruction}\n\n"
            f"Document: {sample['document'][:500]}\n"
            f"Summary: {sample['hallucinated_summary']}\n"
            f"Your judgment: "
        )
        
        response = self.get_model_response(prompt)
        prediction = self.parse_yes_no(response)
        
        return {
            "sample_id": sample.get("id"),
            "document": sample["document"][:100],
            "summary": sample["hallucinated_summary"],
            "is_hallucinated": True,
            "model_response": response,
            "prediction": prediction,
            "correct": prediction == "Yes"
        }
    
    def run_evaluation(self, task: str, data_path: str, sample_size: int = 100) -> Dict:
        """Run full evaluation on a task."""
        print(f"\nEvaluating {self.model_name} on {task} task...")
        
        with open(data_path) as f:
            samples = json.load(f)
        
        samples = samples[:sample_size]  # Limit for testing
        
        evaluator = {
            "qa": self.evaluate_qa,
            "dialogue": self.evaluate_dialogue,
            "summarization": self.evaluate_summarization
        }[task]
        
        results = []
        start_time = time.time()
        
        for i, sample in enumerate(samples):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(samples)}")
            
            result = evaluator(sample)
            results.append(result)
        
        elapsed = time.time() - start_time
        
        # Compute metrics
        correct = sum(1 for r in results if r["correct"])
        accuracy = correct / len(results) if results else 0
        
        return {
            "model": self.model_name,
            "task": task,
            "num_samples": len(results),
            "accuracy": round(accuracy, 3),
            "elapsed_seconds": round(elapsed, 1),
            "results": results
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["qwen", "llama", "gemma"], required=True)
    parser.add_argument("--task", choices=["qa", "dialogue", "summarization"], required=True)
    parser.add_argument("--sample_size", type=int, default=100)
    parser.add_argument("--data_dir", default="HaluEval-willmcd/data")
    parser.add_argument("--output_dir", default="results")
    
    args = parser.parse_args()
    
    # Create output directory
    import os
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run evaluation
    pipeline = HaluEvalPipeline(args.model)
    
    task_files = {
        "qa": f"{args.data_dir}/qa_data.json",
        "dialogue": f"{args.data_dir}/dialogue_data.json",
        "summarization": f"{args.data_dir}/summarization_data.json"
    }
    
    results = pipeline.run_evaluation(args.task, task_files[args.task], args.sample_size)
    
    # Save results
    output_file = f"{args.output_dir}/{args.model}_{args.task}_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    print(f"Accuracy: {results['accuracy']}")


if __name__ == "__main__":
    main()
```

**Run it:**
```bash
python evaluate_local_models.py --model qwen --task qa --sample_size 50
```

---

## Step 4: Batch Evaluation Script (June 11-20)

Create `run_all_evaluations.py`:

```python
import subprocess
import json
from itertools import product

models = ["qwen", "llama", "gemma"]
tasks = ["qa", "dialogue", "summarization"]
sample_size = 500  # Full evaluation

results_summary = {}

for model, task in product(models, tasks):
    print(f"\n{'='*50}")
    print(f"Evaluating {model} on {task}")
    print(f"{'='*50}")
    
    cmd = [
        "python", "evaluate_local_models.py",
        "--model", model,
        "--task", task,
        "--sample_size", str(sample_size)
    ]
    
    result = subprocess.run(cmd)
    
    # Load results
    with open(f"results/{model}_{task}_results.json") as f:
        data = json.load(f)
        results_summary[f"{model}_{task}"] = data["accuracy"]

# Print summary
print("\n" + "="*50)
print("SUMMARY")
print("="*50)
for key, acc in sorted(results_summary.items()):
    model, task = key.split("_")
    print(f"{model:8} | {task:15} | Accuracy: {acc:.3f}")
```

---

## Step 5: Analysis & Visualization (June 21-July 5)

Create `analyze_results.py`:

```python
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

results_dir = Path("results")

# Load all results
data = {}
for result_file in results_dir.glob("*_results.json"):
    with open(result_file) as f:
        result = json.load(f)
        key = f"{result['model']}_{result['task']}"
        data[key] = result

# Create comparison table
comparison = []
for key, result in data.items():
    model, task = key.split("_")
    comparison.append({
        "Model": model,
        "Task": task,
        "Accuracy": result["accuracy"],
        "Samples": result["num_samples"],
        "Time (s)": result["elapsed_seconds"]
    })

df = pd.DataFrame(comparison)
print("\n=== Accuracy Comparison ===")
print(df.pivot(index="Model", columns="Task", values="Accuracy"))

# Visualize
df_pivot = df.pivot(index="Model", columns="Task", values="Accuracy")
df_pivot.plot(kind="bar", figsize=(10, 6))
plt.ylabel("Accuracy")
plt.title("Hallucination Detection Accuracy by Model and Task")
plt.tight_layout()
plt.savefig("results/accuracy_comparison.png")
print("\nChart saved to results/accuracy_comparison.png")
```

---

## Step 6: Error Analysis (June 25-July 5)

Create `error_analysis.py`:

```python
import json
from collections import defaultdict

def categorize_error(sample_data):
    """Categorize the type of hallucination/error."""
    # Manual labeling schema
    categories = {
        "minor_error": "Small detail wrong, core answer correct",
        "unsupported": "Claim reasonable but not in knowledge base",
        "fabricated": "Completely made-up content",
        "confident_wrong": "Nonsensical or contradictory",
    }
    
    # This would be manual review of ~30 samples per model
    return None  # Placeholder

def analyze_errors(results_file):
    """Analyze false positives and false negatives."""
    with open(results_file) as f:
        results = json.load(f)
    
    false_positives = []  # Hallucinated sample, model said "No"
    false_negatives = []  # Real answer, model said "Yes"
    true_positives = []   # Hallucinated, model said "Yes"
    true_negatives = []   # Real answer, model said "No"
    ambiguous = []        # AMBIGUOUS response
    
    for result in results["results"]:
        if result["prediction"] == "AMBIGUOUS":
            ambiguous.append(result)
        elif result["correct"]:
            if result["is_hallucinated"]:
                true_positives.append(result)
            else:
                true_negatives.append(result)
        else:
            if result["is_hallucinated"]:
                false_negatives.append(result)
            else:
                false_positives.append(result)
    
    print(f"\nError Analysis for {results_file}")
    print(f"  True Positives:  {len(true_positives)}")
    print(f"  True Negatives:  {len(true_negatives)}")
    print(f"  False Positives: {len(false_positives)}")
    print(f"  False Negatives: {len(false_negatives)}")
    print(f"  Ambiguous:       {len(ambiguous)}")
    
    # Manual review examples
    print(f"\nFalse Negatives (hallucinations missed):")
    for ex in false_negatives[:5]:
        print(f"  - {ex.get('question', ex.get('response', ex.get('summary')))[:60]}...")

if __name__ == "__main__":
    import glob
    for result_file in glob.glob("results/*_results.json"):
        analyze_errors(result_file)
```

---

## Running Order (Timeline)

```
Week 1 (Jun 1-5):
  [ ] Verify Ollama/HF setup
  [ ] Inspect HaluEval data structure
  [ ] Test model loading with dummy prompt

Week 2 (Jun 6-10):
  [ ] Implement evaluate_local_models.py
  [ ] Test on 50 samples from each task
  [ ] Fix parsing issues (Yes/No extraction)

Week 3 (Jun 11-20):
  [ ] Run full pipeline on 3 models × 3 tasks
  [ ] Monitor for crashes, slow inference
  [ ] Aggregate results

Week 4 (Jun 21-Jul 5):
  [ ] Analyze results, generate metrics
  [ ] Manual error review (20-30 samples)
  [ ] Create visualizations

Week 5 (Jul 5-8):
  ✓ MIDWAY REPORT (use analyze_results.py output)

Week 6 (Jul 8-23):
  [ ] Extended analysis (prompts, subtasks)
  [ ] Final report writing
```

---

## Quick Debug Checklist

**Model not responding:**
- ✓ Is Ollama server running? (`ollama serve`)
- ✓ Is Ollama model pulled? (`ollama pull qwen:1.5b`)
- ✓ Can you curl the API? (`curl http://localhost:11434/api/generate ...`)

**Parse errors (Yes/No not detected):**
- ✓ Add logging: `print(f"Raw response: {response}")`
- ✓ Check for extra whitespace: `response.strip()`
- ✓ Use fuzzy matching (already in code)

**Slow evaluation:**
- ✓ Reduce sample size for testing
- ✓ Use smaller model variant (quantized)
- ✓ Enable GPU if available

**Memory issues:**
- ✓ Unload previous model before loading next
- ✓ Process samples sequentially (not batch)
- ✓ Use quantized versions (4-bit)

---

## Testing Workflow

```bash
# 1. Quick test (5 samples)
python evaluate_local_models.py --model qwen --task qa --sample_size 5

# 2. Medium test (50 samples per task)
python run_all_evaluations.py  # (modify to sample_size=50)

# 3. Error analysis
python error_analysis.py

# 4. Visualizations
python analyze_results.py

# 5. Full run (when confident)
# Modify run_all_evaluations.py to sample_size=500 and execute
```

---

**Next: Focus on getting one model × one task working end-to-end first (e.g., Qwen + QA). Once that's solid, scale to all 9 combinations.**
