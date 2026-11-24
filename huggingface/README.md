---
pretty_name: World Legal Bench 2.0
license: cc-by-4.0
language:
- en
- fr
- ko
- pt
- es
- zh
- ja
- hi
- id
size_categories:
- n<1K
task_categories:
- question-answering
tags:
- legal-reasoning
- public-law
- multilingual
- multiple-choice
- benchmark
- closed-book
configs:
- config_name: default
  default: true
  data_files:
  - split: test
    path: data/test.jsonl
---

# World Legal Bench 2.0

**Source-linked legal reasoning across twelve jurisdictions and five geographic reporting regions.** This release contains 360 closed-book multiple-choice questions in nine selected test languages. Each question retains its original options, reference answer and official-source references from the v1.4.2 parent pool.

[Code repository](https://github.com/enterpriseanalysis/world-legal-bench) · [Methodology](docs/methodology.md) · [Evaluation protocol](docs/evaluation.md) · [Results and reporting](docs/results.md)

## Geographic coverage

Regional reporting references the United Nations Statistics Division's **M49 geographic classification**. Jurisdictions remain the legal unit of evaluation. The geographic grouping is a statistical presentation convention; it implies neither political affiliation nor United Nations endorsement of this benchmark. [Official UNSD M49 methodology](https://unstats.un.org/unsd/methodology/m49/)

| Reporting region | Included jurisdictions | Items | Share |
|---|---|---:|---:|
| Americas | United States, Canada, Brazil, Mexico | 84 | 23.33% |
| Asia | South Korea, China, Japan, India, Indonesia | 157 | 43.61% |
| Europe | France | 45 | 12.50% |
| Africa | South Africa | 38 | 10.56% |
| Oceania | Australia | 36 | 10.00% |
| **Total** | **12 jurisdictions** | **360** | **100%** |

![Regional question coverage](assets/regional-coverage-v20.svg)

Scores summarize included jurisdictions, not the full legal population of a region. Country quotas differ. Report both item-level overall accuracy and an equal-region macro average: pool items within each region, then give the five regional accuracies equal weight.

## Construction and reference profile

The set retains 327 scored nonpasses from saved `gpt-6-luna` (`max`) responses and adds 33 recorded successes to supplement legal-topic coverage. Nonpasses comprise 301 incorrect and 26 invalid final-answer outcomes. Execution failures, unscored cases and empty returns are excluded. Question text, options, keys and source bindings remain unchanged.

The selected historical responses yield **9.17% item-micro accuracy** and **9.13% region-macro accuracy**. These are retrospective selection statistics, not a fresh model run or an unbiased estimate on an independent holdout. The [per-item selection records](provenance/v2.0/selection.jsonl) and [reference profile](provenance/v2.0/reference_selection.json) disclose this bias. No new independent legal expert audit is claimed.

## Dataset viewer and columns

The `test` split contains all 360 items. There is no training split or undisclosed private holdout in this package.

| Column | Meaning |
|---|---|
| `country` | Source jurisdiction code |
| `region` | UN M49-referenced reporting group |
| `language` | Selected question language |
| `question_id` | Stable parent item identifier |
| `question` | Source-bound question and stated assumptions |
| `choices` | Four labeled alternatives, A through D |
| `answer` | Reference choice; evaluation material only |
| `answer_text` | Reference choice text |
| `task_family` | Inherited reasoning-task annotation |
| `source_urls` | Official-source references |

The viewer joins questions and keys for inspection. Never include `answer`, `answer_text`, annotations or selection metadata in the tested model's prompt. Nine language tags describe the selected questions, not every language used by each legal system; row tag `zh-Hans` is indexed under Hub language `zh`.

## Answering and scoring

The tested model answers one closed-book question at a time. Every saved response is then graded by an explicitly configured LLM Judge. The Judge accepts native-language final-choice declarations and unambiguous semantic equivalents, records candidate evidence and an explanation, and must not solve the question on the candidate's behalf.

Use the [code repository](https://github.com/enterpriseanalysis/world-legal-bench) for `wlb run` and `wlb judge`. This dataset package's `evaluate.py` aggregates already-judged prediction records offline:

```bash
python evaluate.py --predictions judged.jsonl --output report.json
```

Version 2.0 does not fall back to regular-expression matching when judgements are absent. Judge errors, inference errors and invalid final answers remain separate. Publish model and Judge identifiers, configurations, retry policy, complete coverage, and both overall scores. See [evaluation](docs/evaluation.md).

## Limitations, versioning and license

This reference-error-selected set supports controlled comparisons and error analysis. It does not certify professional legal competence, establish a causal effect of language, or represent every jurisdiction in its geographic groups. It was not selected to enforce an external general-intelligence ranking. Small country subsets have limited measurement precision.

Version 2.0 changes selection, quotas, grading and aggregation; its results are not directly comparable to v1.4.1-release. Underlying legal source materials retain their own terms. Authored data and documentation use [CC BY 4.0](LICENSE-DATA); code uses [MIT](LICENSE). Citation metadata is in [CITATION.cff](CITATION.cff).
