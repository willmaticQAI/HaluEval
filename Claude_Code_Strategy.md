# Claude Code for HaluEval: Acceleration Strategy

## Why Claude Code Fits This Project

You're building an **AI automation workflow evaluation pipeline**—exactly the use case where Claude Code excels.

<cite index="2-1">Claude Code is an agentic coding tool that reads your codebase, edits files, runs commands, and integrates with your development tools. Available in your terminal, IDE, desktop app, and browser.</cite>

For your specific work:

| Task | Why Claude Code Helps |
|------|----------------------|
| **Model loading** | Write code to load Qwen/Llama/Gemma, run it instantly, see errors immediately |
| **Inference testing** | Test inference on 5 samples, debug parsing issues, iterate without context switching |
| **Batch evaluation** | Run all 9 model-task combinations, monitor progress, handle failures dynamically |
| **Analysis automation** | Generate metrics, create visualizations, aggregate results in one workflow |
| **Debugging** | See full stack traces, propose fixes, verify they work before saving |

---

## How to Use Claude Code for HaluEval

### Setup (10 minutes)

<cite index="2-1">Claude Code is available in your terminal, IDE, desktop app, and browser.</cite>

**Option 1: Terminal (Best for this project)**
```bash
# Install Claude Code (macOS/Linux)
curl https://install.claude.ai | sh

# Or via Homebrew
brew install claude-code

# Start in your project directory
cd ~/HaluEval-willmcd
claude
```

**Option 2: VS Code Extension**
<cite index="2-1">Install for VS Code via Extensions view (Cmd+Shift+X on Mac, Ctrl+Shift+X on Windows/Linux)</cite>

Then you can write prompts directly in your editor with inline diffs.

---

### Phase 1: Build & Test (June 6-10)

#### Step 1: Ask Claude Code to analyze your HaluEval structure
```bash
claude> Analyze the HaluEval-willmcd directory and explain what data formats 
         are in each JSON file (qa_data.json, dialogue_data.json, etc). 
         Show me one example from each.
```

Claude Code will:
- Read all files in `data/`
- Parse JSON structure
- Print examples
- Explain what you're evaluating

#### Step 2: Load models and test inference

```bash
claude> I want to evaluate hallucination detection. Set up Ollama 
        to run locally. Write a Python script that:
        1. Loads the Qwen 1.5B model via Ollama
        2. Sends a test hallucination detection prompt
        3. Parses the response for "Yes" or "No"
        4. Shows elapsed time
```

Claude Code will:
- Check if Ollama is installed (ask you to install if not)
- Write the inference script
- Run it
- Show you the output and timing

#### Step 3: Adapt the existing evaluate.py

```bash
claude> We have evaluation/evaluate.py that uses OpenAI API. 
        Rewrite it to use local models via Ollama instead. 
        Keep the same structure but swap API calls for local inference.
```

Claude Code will:
- Read the old OpenAI-based code
- Rewrite it for Ollama
- Test it on a small sample
- Show diffs so you can review

---

### Phase 2: Scale Evaluation (June 11-20)

#### Run all 9 evaluations with error handling

```bash
claude> Build a batch evaluation script that:
        1. Defines models = ["qwen", "llama", "gemma"]
        2. Defines tasks = ["qa", "dialogue", "summarization"]
        3. For each model-task pair:
           - Load data
           - Run 500 inferences
           - Compute accuracy, precision, recall, F1
           - Save results to results/{model}_{task}_results.json
        4. Print a summary table when done
        5. Handle model loading errors gracefully
```

Claude Code will:
- Write the full batch pipeline
- Run it (this takes 2-3 hours for all 9 combinations)
- Monitor progress in real-time
- If inference fails on model #2, it will catch it and keep going
- Save structured JSON results

---

### Phase 3: Analysis & Visualization (June 21-July 5)

#### Generate metrics and charts

```bash
claude> Load all results JSON files from results/ directory.
        Create:
        1. A comparison table (model x task x accuracy/precision/recall/F1)
        2. A bar chart comparing accuracy across models
        3. An error analysis breakdown
        Export as markdown, PNG, and CSV
```

Claude Code will:
- Load all results
- Compute aggregate statistics
- Generate visualizations using matplotlib
- Save outputs
- Show you the chart preview

#### Error analysis automation

```bash
claude> For each results file, categorize false negatives and false 
        positives. Group them by:
        - minor_error
        - unsupported_claim
        - fabricated_answer
        - confident_wrong
        
        Show me the top 5 categories and example errors.
```

Claude Code will:
- Parse each result
- Categorize errors (using heuristics or manual review)
- Generate a categorization report
- Show examples

---

## Key Claude Code Advantages for Your Workflow

### 1. **Iterative Development Loop**
```
You:      "Write code to load Qwen model"
Claude:   (Writes script, runs it, shows output)
You:      "That's too slow. Use quantized version and add batching"
Claude:   (Edits code, runs again, shows 5x speedup)
```

No context switching. No copy-paste. Just natural iteration.

### 2. **Real-Time Debugging**
If inference crashes on sample #247:
```
You:      "Why did it fail?"
Claude:   (Shows stack trace, pinpoints issue)
You:      "Fix it"
Claude:   (Edits code, reruns with sample #247)
```

### 3. **Reproducibility**
<cite index="8-1">Claude Code uses a CLAUDE.md memory file (Official). This file is the agent's constitution for your repository. Claude reads it every session to anchor conventions and commands.</cite>

You can create a `CLAUDE.md` in your project:
```markdown
# HaluEval Evaluation Pipeline

## Context
- Evaluating 3 models (Qwen, Llama, Gemma) on hallucination detection
- 3 tasks: QA, Dialogue, Summarization
- Data in HaluEval-willmcd/data/
- Results saved to results/{model}_{task}_results.json

## Standard Commands
- `eval all` → Run all 9 evaluations
- `analyze` → Generate metrics and visualizations
- `error-review` → Categorize false positives/negatives

## Conventions
- All model names lowercase
- Results always include: accuracy, precision, recall, f1, elapsed_time
```

Every session, Claude Code remembers the context and conventions.

### 4. **Multi-File Coordination**
<cite index="4-1">Claude Code makes powerful, multi-file edits with understanding of your codebase and dependencies.</cite>

If you need to:
- Update data loader
- Modify prompt templates
- Change result aggregation
- Fix metrics computation

Claude Code edits all files cohesively and tests the full pipeline.

### 5. **Skill Modules**
<cite index="8-1">Skills (Official). A skill is a SKILL.md file with frontmatter under .claude/skills/<name>/. It supports /name invocation and autonomous invocation by Claude.</cite>

Create reusable skills:
```bash
# Create a skill for model loading
.claude/skills/load_model/SKILL.md

# Create a skill for metric computation
.claude/skills/compute_metrics/SKILL.md

# Then invoke
claude> /load_model qwen
claude> /compute_metrics results/
```

---

## Recommended Workflow

### Week 1: Build & Test
```
Mon-Tue:  claude> Load HaluEval data, explain structure
Wed-Thu:  claude> Set up Ollama, test single inference
Fri:      claude> Adapt evaluate.py to local models
```

### Week 2-3: Scale & Evaluate
```
Mon-Wed:  claude> Run batch evaluation on all 9 combinations
          (Claude Code monitors progress, saves results)
Thu-Fri:  claude> Error analysis, spot-check results
```

### Week 4: Analysis & Reports
```
Mon-Tue:  claude> Generate metrics table and visualizations
Wed-Thu:  claude> Categorize errors, write error analysis section
Fri:      claude> Compile midway report (markdown)
```

---

## Example: Full Conversation Flow

```
YOU: I need to evaluate 3 models on hallucination detection. 
     Here's my plan [paste the Implementation Roadmap]. 
     Can you build this step by step?

CLAUDE CODE: I'll set up the evaluation pipeline. Let me start by 
             analyzing your data structure and setting up Ollama.
             (reads HaluEval data, checks Ollama)
             
             ✓ HaluEval has 35K samples across 4 categories
             ✓ Ollama installed and running
             
             Now I'll write evaluate_local_models.py...

YOU: Run it on 5 QA samples to test

CLAUDE CODE: Running test evaluation on 5 QA samples...
             ✓ Qwen loaded successfully
             ✓ 5 inferences completed in 8.3 seconds
             ✓ 4/5 correct (80% accuracy on test set)
             ✓ Parse success: 5/5 responses parsed correctly
             
             Sample output: Yes (hallucination detected) ✓

YOU: Good. Now scale to 500 samples per task and run all 3 models

CLAUDE CODE: Running full evaluation (3 models × 3 tasks × 500 samples)
             [Progress bar showing completion]
             
             Qwen:
             ✓ QA: 390/500 (78%) - 12m 45s
             ✓ Dialogue: 375/500 (75%) - 13m 22s
             ✓ Summarization: 405/500 (81%) - 14m 05s
             
             Llama: ... [similar]
             Gemma: ... [similar]
             
             All results saved to results/ directory

YOU: Analyze the results and create a comparison table

CLAUDE CODE: Generating analysis...
             [Comparison table with all metrics]
             [Bar chart visualization]
             [Accuracy heatmap]
             
             Key findings:
             - Qwen performs best overall (78% avg)
             - Summarization is easiest task (79% avg)
             - Dialogue is hardest task (72% avg)
             - Clear model ranking: Qwen > Llama > Gemma

YOU: Now categorize the errors in the failed cases

CLAUDE CODE: Analyzing 315 failed cases across all evaluations...
             [Breakdown by error type]
             
             Most common errors:
             1. Unsupported claims (45%) - Model confused by context
             2. Fabricated answers (30%) - Clearly false content
             3. Minor errors (15%) - Borderline hallucinations
             4. Model confusion (10%) - Ambiguous response
             
             [Examples of each type shown]

YOU: Perfect. Can you write the Methods section for our midway report?

CLAUDE CODE: Writing Methods section based on your evaluation...
             [Generated markdown with proper notation and metrics]
```

---

## For Your AI Automation Focus

Since you care about **AI automation workflows**, Claude Code also helps you build the next layer:

### Orchestration Layer
```bash
claude> Build an evaluation orchestration system that:
        1. Queues hallucination detection jobs
        2. Routes inferences to cheapest model per task
        3. Tracks confidence scores
        4. Triggers fallback to higher-quality model if accuracy < threshold
```

This is exactly what you'll need to integrate these models into production automation workflows.

---

## Next Steps

1. **Install Claude Code** (5 min)
   ```bash
   curl https://install.claude.ai | sh
   ```

2. **Navigate to your project** (1 min)
   ```bash
   cd ~/HaluEval-willmcd
   claude
   ```

3. **Start building** (30 min for first iteration)
   ```bash
   claude> Analyze the HaluEval data structure and show me examples 
           from each file
   ```

4. **Let it compound** - Each task takes 15-30 minutes instead of hours because:
   - No manual copy-paste
   - Errors caught immediately
   - Code runs and shows results in real-time
   - Iterations are frictionless

---

## Official Resources

- <cite index="2-1">Claude Code Documentation: https://code.claude.com/docs/en/overview</cite>
- Installation guide (terminal, VS Code, JetBrains, desktop): https://code.claude.com/docs
- Getting started for researchers: https://paulgp.substack.com/p/getting-started-with-claude-code

**Estimated time to productivity: 30 minutes setup + 2-3 hours building evaluation pipeline with Claude Code.**

Compare that to ~20+ hours doing it manually. That's the power of agentic coding for ML pipelines.
