# HaluEval Qualitative Error Analysis

**Date:** 2026-07-03
**Follows:** `HaluEval_Findings_and_Analysis.md` (quantitative results)
**Scope:** five-category error schema applied to false positives and false negatives across all three models

---

## 1. Method

For each model, up to 15 false positives (grounded right-answer wrongly judged "Yes"/hallucinated) and 15 false negatives (hallucinated answer wrongly judged "No"/grounded) were sampled, pooled across all three tasks (QA, Dialogue, Summarization), using a fixed random seed (`seed=7`) for reproducibility. Sample pools per model (before sampling down to 15+15):

| model | FP pool | FN pool |
|---|---|---|
| qwen | 749 | 735 |
| llama | 1,416 | 83 |
| llama caveat | — | Llama's FN pool is small because it almost always predicts "Yes" (see §5.2 of the main findings doc) — there are simply few "No" predictions to sample from |
| gemma | 101 | 1,385 |
| gemma caveat | — | Gemma's FP pool is small for the mirror-image reason — it almost always predicts "No" |

**Category schema** (applied per the project's original five-category taxonomy):

| Code | Category | Meaning |
|---|---|---|
| MIN | Minor error | Detail wrong, core claim right |
| UNSUP | Unsupported claim | Plausible but ungrounded / not verifiable from context |
| FAB | Fabricated answer | Invented entity, fact, or attribution |
| CONF | Confidently wrong | Self-contradictory, nonsensical, or comically impossible |
| AMBIG | Model confusion / ambiguous | Borderline phrasing, or — for false positives specifically — the answer has no real error at all and the category reflects *why the model likely misjudged it*, not a defect in the content |

**Important framing note:** for **false positives**, the sampled answer is the *correct* (`right_answer`) response — by definition there is no hallucination in the content. The category therefore does not describe a content defect; it describes the most likely surface-level trigger for the model's incorrect "Yes" judgement (e.g., brevity, a dataset typo, dense statistics). For **false negatives**, the sampled answer is the actual `hallucinated_answer`, so the category genuinely characterizes the type of hallucination the model failed to catch.

---

## 2. Category Distribution

### 2.1 False Positives (grounded answers wrongly flagged)

| model | MIN | UNSUP | FAB | CONF | AMBIG |
|---|---|---|---|---|---|
| qwen | 0 | 0 | 0 | 0 | **15/15** |
| llama | 0 | 0 | 0 | 0 | **15/15** |
| gemma | 0 | 0 | 0 | 0 | **15/15** |

**Every single sampled false positive across all three models falls into the "model confusion" bucket** — because by construction these are correct answers with no hallucination present, so there is no content-level error to categorize. This is itself a finding: **none of the false-positive errors reflect a graded judgement about answer quality.** They reflect either (a) a global response bias (Llama/Gemma, see §3) or (b) narrower surface-level triggers (Qwen, see §3.1).

### 2.2 False Negatives (hallucinations missed)

| model | MIN | UNSUP | FAB | CONF | AMBIG |
|---|---|---|---|---|---|
| qwen | 1 | 3 | 6 | 3 | 2 |
| llama | 0 | 0 | 8 | 5 | 2 |
| gemma | 1 | 2 | 7 | 2 | 3 |

False negatives show real spread — this is where the interesting qualitative differences between models live.

---

## 3. Qualitative Patterns

### 3.1 Qwen's false positives cluster around brevity and dataset typos, not genuine ambiguity

Across Qwen's 15 sampled FPs, two concrete surface triggers recur:

- **Terse/fragment-style correct answers get flagged disproportionately** — e.g., `"It is a documentary film."`, `"Hasbro"`, `"It originated in Renaissance Italy. Verona"`. These are all fully correct but very short, and Qwen appears to associate brevity with under-elaboration/suspicion.
- **Dataset-level typos in the ground-truth `right_answer` text itself get misread as fabricated entities.** Two examples recurred independently across models: `"Tryod Taylor"` (should be Tyrod Taylor) and `"Rupert Gaves"` (should be Rupert Graves) — both are typos present in HaluEval's own source data, not model errors, yet they visually resemble a garbled/invented name and appear to trigger false "Yes" judgements in both Qwen and Gemma. **This is worth flagging in your report as a dataset noise source that likely affects any model evaluated on this benchmark, not something specific to the models tested.**

### 3.2 Llama and Gemma's false positives are pure bias, not content-sensitive at all

For both models, the sampled FP content spans everything from single-word factoids to multi-sentence summaries to grounded dialogue corrections — with no discernible pattern connecting content type to the (mis)judgement. This is consistent with the quantitative finding that both models collapsed to a near-constant output (Llama → "Yes", Gemma → "No"): **the false-positive rate for these two models is not telling you anything about what confuses them content-wise — it is a direct readout of their fixed response bias.** A qualitative pass on FPs for these two models adds little beyond confirming the degenerate-strategy finding already visible in the confusion matrices.

### 3.3 Llama's rare "No" predictions (its false negatives) still miss blatant fabrications

Because Llama predicts "Yes" ~99% of the time, its 83 false negatives (across the full 1,000-instance-per-task grid) represent the rare cases where it broke pattern. Notably, **these rare "No" predictions are not correlated with subtlety** — the missed hallucinations in this sample include comically obvious fabrications: *"the Green Bay Packers are actually coached by Joe Biden"*, *"He's from Antarctica"* (about Roger Federer), *"A Christmas Carol is actually a comic book adaptation of Oliver Twist... a little like a superhero genre"*. A model with genuine discrimination ability would be expected to at least catch absurd, low-plausibility fabrications even if it missed subtle ones — Llama's failure to do so on even these obvious cases reinforces that its "No" predictions are essentially noise around a fixed "Yes" bias rather than moments of actual reasoning.

### 3.4 Qwen shows the broadest and most content-engaged false-negative distribution

Qwen is the only model whose FN sample spans all five categories, including genuine "Minor error" and "Unsupported claim" cases that require real world-knowledge comparison to catch (e.g., correctly distinguishing "Camp Rock is a Disney Channel property" from a fabricated "Nickelodeon" attribution, or catching that a Golden Girls castmate reunion cites a plausible-but-wrong actor name). This is consistent with Qwen being the only model in the quantitative results with a non-degenerate precision/recall profile — its errors reflect genuine (if imperfect) engagement with content, concentrated on the hardest sub-cases: near-neighbor entity substitutions and evasive non-answers, which are exactly the categories one would expect a small model to struggle with most.

### 3.5 Gemma's false negatives span the full category range too — it simply doesn't act on what it (arguably) can process

Interestingly, Gemma's 15 sampled FNs also span all five categories, similar to Qwen's spread — including catching some clearly fabricated claims in principle. But because Gemma's recall is only 0.05–0.10 overall, this diversity in the *sample* doesn't reflect diversity in *behavior*: it is simply saying "No" to almost everything regardless of category, so a diverse-looking sample of misses is expected under a near-constant-negative strategy, not evidence of nuanced judgement.

### 3.6 Dataset-label ambiguity: a ceiling on achievable accuracy

At least 4 of the 90 sampled examples (~4.4%) contain `hallucinated_answer` content that a careful human reader would judge as **factually defensible or arguably true**, despite being labeled as the hallucinated variant in the dataset:

- *"He also starred in The Aviator, directed by Martin Scorsese"* (Leonardo DiCaprio) — this is true.
- *"The melody... comes from the song 'Good Morning to All'"* — this is the widely-cited real origin of the "Happy Birthday" melody.
- *"Rupert Murdoch's 21st Century Fox"* re: the network that aired Glee — Fox's parent company ownership at the time is broadly defensible.
- *"[It] is actually a completely different book from Hamlet"* — arguably true in a narrow bibliographic sense (distinct early printed text).

This suggests a small but nonzero rate of noisy/debatable labels in the underlying HaluEval dataset itself, which sets a soft ceiling on the accuracy any model — however capable — could achieve on this exact sample. **Worth a caveat sentence in your report's limitations section**, distinct from the model-behavior findings.

---

## 4. Summary Takeaway for the Report

The quantitative results (main findings doc) show Llama and Gemma collapsing to near-constant "Yes"/"No" strategies respectively, with only Qwen showing real signal. This qualitative pass **confirms and sharpens that story**: Llama and Gemma's false positives are 100% attributable to fixed response bias with no content-level pattern, and even Llama's rare deviations from that bias fail to catch obvious fabrications — evidence against these being examples of genuine (if imperfect) reasoning. Qwen alone shows a false-negative distribution that engages with real content-difficulty gradients (missing the hard near-neighbor-substitution cases while presumably catching easier ones), which is the qualitative signature of a model that is actually trying to discriminate, just not well enough to reliably succeed. Separately, a small dataset-label-noise rate (~4%) should be flagged as a scope caveat rather than attributed to model weakness.

---

## Appendix: Full Categorized Sample (90 examples)

### Qwen — False Positives (all AMBIG / model confusion — content is correct in every case)

| task | answer excerpt | likely trigger |
|---|---|---|
| dialogue | "Tryod Taylor is also from there" | Dataset typo resembles fabricated name |
| summarization | "71% of voters say they don't need to know..." | Dense statistical content |
| dialogue | "One of the more recent versions stars Edward Norton" | No clear trigger |
| summarization | "Khloe Kardashian posted a photo..." | No clear trigger |
| qa | "Hasbro" | Brevity bias |
| dialogue | "Rupert Gaves also starred in The Waiting room" | Dataset typo resembles fabricated name |
| summarization | "2015 Sydney Royal Easter show opened..." | No clear trigger |
| dialogue | "It originated in Renaissance Italy. Verona" | Brevity / fragment style |
| dialogue | "It was released 2012, is in English" | Brevity / fragment style |
| dialogue | "Verne Troyer was in it..." | No clear trigger |
| summarization | "John Axford has been placed on the family medical..." | No clear trigger |
| dialogue | "It is a documentary film." | Brevity bias |
| summarization | "Dornoch in Scotland is pointing tourists..." | No clear trigger |
| summarization | "Mark Lippert was attacked in early March..." | No clear trigger |
| summarization | "Raheem Sterling says he is not yet ready..." | No clear trigger |

### Qwen — False Negatives

| task | answer excerpt | category |
|---|---|---|
| qa | "Both have 'Wainscott' in common." | AMBIG — tautological non-answer |
| dialogue | "Matt Damon played the lead role in True Grit" | FAB — misattributed lead role |
| qa | "associated with Nickelodeon" | FAB — wrong studio |
| qa | "Cancun, Mexico was a site..." | FAB — substituted location |
| qa | "transmitter is located on Sebago Mountain" | FAB — substituted entity |
| qa | "Raphael Elkan Samuel was an outstanding intellectual..." | UNSUP — evasive restatement |
| qa | "considered printed publications" | CONF — conflates entity types |
| qa | "originates from the late 1970s" | FAB — fabricated date |
| summarization | "...confined to her home and in const[ant]..." | MIN — embellished detail |
| dialogue | "spokesperson for Spirit Soda company" | FAB — invented entity |
| dialogue | "Kill Bill and The Hateful Eight" | AMBIG — plausible, genuinely hard case |
| summarization | "has completed a career grand slam after winning" | CONF — future event asserted as fact |
| dialogue | "Any of the Alien movies... I would also recommend Jaws" | UNSUP — not grounded in filmography |
| qa | "reunite with Estelle Getty in Ladies Man" | UNSUP — plausible same-show substitution |
| dialogue | "signed by Portugal national football team" | CONF — self-contradictory |

### Llama — False Positives (all AMBIG / model confusion — content is correct in every case)

15/15 samples span single-word factoids, multi-sentence summaries, and grounded dialogue corrections with no discernible content pattern — consistent with a fixed "always Yes" response bias rather than content-driven misjudgement (see §3.2).

### Llama — False Negatives

| task | answer excerpt | category |
|---|---|---|
| dialogue | "Green Bay Packers are actually coached by Joe Biden" | CONF — comically obvious fabrication |
| dialogue | "One that comes to mind is Funny People" | FAB — wrong filmography |
| dialogue | "drafted Baltimore's Rudy Gay... great quarterback" | CONF — nonsensical cross-sport claim |
| dialogue | "also starred in the movie Time Traveler's Wife" | FAB — wrong filmography |
| dialogue | "He's from Antarctica" | CONF — obviously absurd |
| dialogue | "big fan of underwater basket weaving" | AMBIG — non-sequitur deflection |
| dialogue | "romance novels about a group of Spanish prostitutes" | FAB — mischaracterized work |
| dialogue | "also starred in The Aviator, directed by Martin Scorsese" | AMBIG — arguably true; dataset-label ambiguity |
| dialogue | "Pink is actually color-blind..." | FAB — fabricated personal fact |
| dialogue | "I'm a Little Teapot" | FAB — fabricated song attribution |
| dialogue | "It was written in French" | FAB — fabricated origin-language claim |
| dialogue | "33 years to the day of Theismann's hair cutting" | CONF — nonsensical |
| dialogue | "Yanina Wickmayer also plays football" | FAB — fabricated cross-sport claim |
| dialogue | "stars Vivica A. Fox, who also starred in Independence Day" | FAB — fabricated cast claim |
| dialogue | "A Christmas Carol is actually a comic book adaptation..." | CONF — nonsensical |

### Gemma — False Positives (all AMBIG / model confusion — content is correct in every case)

| task | answer excerpt | likely trigger |
|---|---|---|
| qa | "atomic and quantum physics" | Brevity bias |
| qa | "1987" | Brevity bias |
| qa | "35" | Brevity bias |
| dialogue | "I can create a playlist for you..." | No clear trigger |
| dialogue | "Shark Night is another as is State of the Union" | No clear trigger |
| qa | "Sojourners" | Brevity bias |
| qa | "2007" | Brevity bias |
| dialogue | "Rupert Gaves also starred in The Waiting room" | Dataset typo resembles fabricated name |
| dialogue | "Zombieland starred both Emma Stone and Bill Murray" | No clear trigger |
| dialogue | "Castle Roogna, Children of the Mind..." | No clear trigger |
| qa | "Lady Mary Crawley" | Brevity bias |
| summarization | "19-year-old singer was a finalist..." | No clear trigger |
| dialogue | "so is the movie The Golden Compass" | No clear trigger |
| dialogue | "He directed The Passion of the Christ and also Braveheart" | No clear trigger |
| qa | "Maurice Pialat" | Brevity bias |

### Gemma — False Negatives

| task | answer excerpt | category |
|---|---|---|
| summarization | "upcoming rugby season is going to be filled with excitement" | MIN — plausible embellishment |
| dialogue | "The Legend of Bagger Vance. Very funny" | UNSUP — fabricated association |
| dialogue | "played quarterback for the Dallas Cowboys before coaching" | FAB — wrong team affiliation |
| dialogue | "It was actually written in German, but later translated" | FAB — fabricated origin-language claim |
| qa | "comes from the song 'Good Morning to All'" | AMBIG — arguably accurate; dataset-label ambiguity |
| qa | "is Robert Rose" | FAB — substituted entity |
| dialogue | "American Beauty was written by William Shakespeare" | CONF — comically impossible |
| dialogue | "Tom Brady was also a fantastic linebacker" | CONF — nonsensical claim |
| dialogue | "won the Academy Award for Best Picture and Best Director" | UNSUP — vague, ungrounded |
| dialogue | "Adam Sandler acted in the movies Cars, The Incredibles..." | FAB — fabricated voice-cast claims |
| qa | "Rupert Murdoch's 21st Century Fox" | AMBIG — arguably reasonable; dataset-label ambiguity |
| qa | "200 Press is an EP by James Blake" | FAB — substituted artist |
| dialogue | "Michael Bay starred in Armageddon, co-written by Tony Gilroy" | FAB — multiple stacked fabrications |
| dialogue | "completely different book from Hamlet" | AMBIG — arguably defensible; dataset-label ambiguity |
| dialogue | "Tyga's Record Label is: Interscope Records" | FAB — substituted label |

---

## Reproduction

```bash
cd HaluEval
python3 -c "
import json, random
rng = random.Random(7)
for model in ['qwen','llama','gemma']:
    fps, fns = [], []
    for task in ['qa','dialogue','summarization']:
        records = [json.loads(l) for l in open(f'results/full/{model}_{task}_results.jsonl')]
        for r in records: r['task'] = task
        fps += [r for r in records if r['ground_truth']=='No' and r['judgement']=='Yes']
        fns += [r for r in records if r['ground_truth']=='Yes' and r['judgement']=='No']
    rng.shuffle(fps); rng.shuffle(fns)
    sample = fps[:15] + fns[:15]
    with open(f'results/error_analysis/{model}_error_sample.jsonl', 'w') as f:
        for r in sample: f.write(json.dumps(r, ensure_ascii=False) + '\n')
"
```
