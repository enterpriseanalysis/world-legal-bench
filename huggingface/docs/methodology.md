# Methodology

## Evaluation scope

World Legal Bench 2.0 is a difficulty-selected, source-linked assessment of native-language legal reasoning across twelve jurisdictions. The legal unit is a question tied to a particular jurisdiction, legal-source version and set of stated assumptions. Geographic grouping does not change the governing law, merge answer keys, or treat distinct legal systems as interchangeable.

The 360 selected items retain the question, options, reference answer and source annotations of the v1.4.2 closed-book parent pool. The parent service-bundle SHA-256 is `6963b17c7124f034b2c614140eb193927c0dcd4b2b8516a6d5e59fa4a38c7282`. Schema conversion for this public repository does not rewrite question or option text.

## Geographic reporting framework

The five reporting groups reference the United Nations Statistics Division's **Standard Country or Area Codes for Statistical Use (M49)**: Americas (019), Asia (142), Europe (150), Africa (002) and Oceania (009). The mapping was consulted on 2026-11-24. The benchmark retains country-level identities and uses these broader groups for reporting. [Official UNSD M49 methodology](https://unstats.un.org/unsd/methodology/m49/)

M49 assignments serve statistical presentation; they do not establish political affiliation or imply a position on sovereignty, legal status or boundaries. Referencing the classification does not imply United Nations participation, approval or endorsement of this benchmark.

| Region | Country codes | Items | Reference successes | Reference nonpasses | Retrospective accuracy |
|---|---|---:|---:|---:|---:|
| Americas | US, CA, BR, MX | 84 | 7 | 77 | 8.33% |
| Asia | KR, CN, JP, IN, ID | 157 | 15 | 142 | 9.55% |
| Europe | FR | 45 | 4 | 41 | 8.89% |
| Africa | ZA | 38 | 4 | 34 | 10.53% |
| Oceania | AU | 36 | 3 | 33 | 8.33% |
| **Total** | **12 jurisdictions** | **360** | **33** | **327** | **9.17%** |

These groups describe the included jurisdictions. Europe, Africa and Oceania each contain one sampled jurisdiction in this release; their scores must not be interpreted as estimates for all countries in those regions. Antarctica is outside the jurisdiction sample. Coverage of five reporting regions does not establish comprehensive global legal coverage.

## Reference-guided selection

Selection is based on saved responses from `gpt-6-luna` at `max` reasoning effort, not on newly generated answers. This reported identifier does not certify a provider-side model snapshot. The platform aggregate snapshot inspected on 2026-11-24 contained 9,782 successes, 327 scored nonpasses, nine execution failures and fourteen unscored cases in the 10,132-item parent pool. Execution failures and unscored cases are not model answer errors and were excluded.

All 327 scored nonpasses were retained. They consist of 301 `incorrect` outcomes and 26 `invalid_output` outcomes assigned by the v1.4.2 LLM Judge. None of the retained responses was empty. Invalid final answers remain a separate category: they are not evidence of 26 additional substantive legal reasoning errors.

Thirty-three recorded successes were added. Country quotas were allocated proportionally to observed nonpass counts using largest remainders. Within each country, successful candidates were sampled at spaced positions in the saved success list; coverage fill prioritized new legal-knowledge families, reasoning-task families and source identities relative to already retained items, with a deterministic item-ID hash tie-break. This is an operational coverage heuristic, not a proof of optimal diversity or a stratified random sample.

Unequal country and regional quotas are deliberate. Enforcing equal quotas would discard observed nonpasses in some jurisdictions and require more success fill in others. The objective is to preserve the observed challenge set while making the effect of unequal sampling explicit through dual score aggregation.

The machine-readable authorities are [selection.jsonl](../provenance/v2.0/selection.jsonl), [reference_selection.json](../provenance/v2.0/reference_selection.json), and [release.json](../provenance/v2.0/release.json). Raw provider transcripts and platform credentials are not distributed in this repository.

## Scoring and aggregation

Every response is graded by an explicitly configured LLM Judge. The Judge compares the final answer with the reference option and its meaning; it must not answer the legal question on the candidate's behalf. Choice declarations in the question's language and unambiguous semantic equivalents are eligible. Recorded outcomes distinguish correct answers, incorrect answers, invalid final answers and execution errors. The Judge model and configuration must accompany a result.

Two overall measures must be reported:

1. **Item-level overall accuracy (micro):** the number of correct answers divided by the number of evaluated items. In a complete release run the denominator is 360. Nonpassing final answers and recorded execution failures remain visible in the denominator; missing items make the run incomplete.
2. **Equal-region macro accuracy:** first pool correct answers and item counts within each reporting region, then take the arithmetic mean of the five regional accuracies. Each region receives 20% of this macro score, regardless of item count.

Do not average country percentages equally within a region: country quotas differ. Weight country accuracies by their selected item counts, or compute regional accuracy directly from item outcomes. Country-macro accuracy may be retained as a diagnostic, but it must not be substituted for region-macro accuracy without changing its label.

The selected historical record yields 9.17% item-micro and 9.13% region-macro accuracy. These values are conditional on selecting the same model's nonpasses. They are not a fresh evaluation, an estimate on an independent holdout, or a guarantee that a rerun will remain below 10%. A different model may answer the retained items correctly. The public offline scorer withholds full-release macro scores when prediction coverage is incomplete.

## Quality and interpretation limits

This release performs mechanical identity, quota, duplicate and source-binding checks. It inherits the parent questions' authored keys and annotations; it does not add a new independent expert audit, manually certify every retained item, or prove that every Judge decision is correct. Official-source-backed corrections should produce a new version with documented item changes.

Selecting against one model introduces reference-model selection bias. No items were selected to enforce an Artificial Analysis ranking or any other external model ordering. A low retrospective reference score is evidence of the selection policy, not of broad legal capability, future benchmark durability or ranking validity. Evaluate independent models and report their per-region and per-jurisdiction outcomes before claiming discriminative performance.

Version 2.0 differs from the archived v1.4.1-release in item selection, country quotas, grading and aggregation. Their scores are not directly comparable. The earlier data and provenance remain preserved under their original version paths.
