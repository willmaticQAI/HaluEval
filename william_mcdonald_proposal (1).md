**Measuring Hallucination Rates in Open-Source Language Models Using HaluEval**  
***Team:** Sushmita Hari, Connor Fahs, William McDonald, Sriram Rella*

**Overview**

Large language models can produce answers that sound correct but are false, unsupported, or not grounded in the information they were given. These errors are commonly called hallucinations. This project will study how often selected open-source language models hallucinate and whether hallucination behavior changes across model family, model size, task type, and evaluation method. The main goal is to build a reproducible evaluation pipeline that compares several open-source models under the same conditions, rather than judging one model in isolation.

**Motivation & Background**

Hallucinations are currently evaluated through human review, benchmark datasets, automated judging, and repeated sampling. Each approach has significant limitations:

* Human review is useful for catching errors, but is slow, expensive, and subjective.   
* Benchmark datasets offer consistent comparisons but may not fully reflect real-world use.  
* Automated judges are faster, but can make mistakes or favor certain response styles.   
* Repeated sampling reveals inconsistency, but a model can still be consistently wrong. 

Because of these limits, a single hallucination score is not enough to explain how or why models fail. A multi-faceted, comparative pipeline is therefore needed.

**Approach & Models**

Our approach is to compare multiple open-source language model families using the same datasets, prompts, scoring rules, and analysis pipeline. We will evaluate models from families such as Qwen, Llama, Gemma, Phi, and Mistral. Smaller models that can run locally through Ollama or Hugging Face Transformers are prioritized, including: Qwen 2.5 0.5B, TinyLlama 1.1B, Llama 3.2 1B, Qwen 2.5 1.5B, Phi-3.5 Mini, and Gemma 3 1B. 

If hardware allows, we’ll test larger or quantized model variants to examine whether scale reduces hallucination. Our main baseline is direct evaluation on HaluEval, comparing model outputs against human-labeled ground truth. We’ll also test simple prompt variations, direct answering vs asking the model to first judge whether a response is supported or hallucinated.

**Datasets**

Our primary dataset is HaluEval, which contains human-annotated hallucination examples across question answering, dialogue, and summarization tasks. We’ll also use at least one secondary dataset(e.g. TruthfulQA or a public Kaggle benchmark) to test whether findings generalize beyond HaluEval. Finally, we’ll create a small synthetic test set of factual questions with known ground-truth answers to verify our evaluation pipeline.

**Evaluation Criteria**

| Quantitative Metrics Hallucination rate, accuracy, precision, recall, F1, and error rate by task type, compared across model family and size to assess whether larger models hallucinate less | Qualitative AnalysisIncorrect outputs will be categorized as: minor factual error, unsupported claim, fabricated answer, or confidently wrong, using consistent labeling rules and equal sample sizes to control for bias. |
| :---- | :---- |

**Risk & Mitigations**

| Risk | Mitigation |
| :---- | :---- |
| Benchmark performance may not reflect real-world model behavior | We will address this by clearly limiting our conclusions to the datasets and tasks tested. |
| Models may be too large or slow to run on available hardware | Use quantized versions, smaller parameter sizes, or a fixed subset of the benchmark. |
| Hallucination can be difficult to define consistently | Use HaluEval’s existing labels as ground truth and applying the same scoring process to every model |
| Automated evaluation misses subtle errors | Include a manual review step for error analysis. |

**Implementation**

The project will be implemented in Python. We will use Hugging Face Transformers and/or Ollama for model inference, pandas for organizing outputs, scikit-learn for evaluation metrics, and matplotlib or similar tools for visualizing results. All code will be placed in an open-source repository with scripts for loading datasets, running models, saving outputs, computing metrics, and generating result tables.

**Timeline**

| Dates | Milestone |
| :---- | :---- |
| Jun 1 \- 6 | Setup, dataset preparation, and baseline testing |
| Jun 7 \- 27 | Implement the main evaluation pipeline; begin running selected models |
| Jun 27 \- Jul 5 | Validate scoring process and perform initial analysis |
| Jul 5 \- Jul 8 | Midway Report |
| Jul 8 \- Jul 18 | Expand to additional models, datasets, or prompt settings if time allows |
| Jul 18 \- Jul 23 | Complete final analysis and results |
| After Jul 23 | Prepare the final report and spotlight presentation |

**Success Criteria**

We will determine success by whether we produce a working, reproducible pipeline and a clear empirical comparison of hallucination behavior across multiple open-source models. At minimum, we expect to report hallucination performance by model family, model size, and task type. A stronger outcome will include comparisons across multiple datasets, prompt formats, and hallucination severity categories. The final result should help future researchers understand which open-source models are more reliable, where they fail, and what evaluation practices are most useful for studying hallucination.

