# Methodology

## Selection unit

The selected unit is an unchanged question from the parent candidate release, together with its options, answer, and source references. The standalone export changes the file schema, not the question wording or gold labels. Source questions are in their selected jurisdiction language and were not generated as a common translation template.

Existing reference-model responses were examined offline. Empty returns, execution errors, and answers whose final choice remained unresolved were excluded from the correct/error selection pools. Deterministic final-answer extraction and targeted reading distinguished substantive answer mismatches from formatting-related misclassification. No new tested-model requests were needed for this selection.

The reference model was `qwen3.8-flash`. This is a reported model identifier from the selection workflow; this repository does not certify its provider-side snapshot identity. The released metadata records selected choices and outcomes, not raw response transcripts.

## Final composition

The selection target was 55 reference errors and 5 reference successes in each jurisdiction. Correct cases filled the remaining slots when the available reviewed errors did not reach the target. Coverage and non-repetition were considered when choosing within the pools. Ten items were excluded during selected-question checking and replaced.

| Jurisdiction | Reference errors | Reference successes | Retrospective accuracy |
|---|---:|---:|---:|
| US | 43 | 17 | 28.33% |
| CA | 55 | 5 | 8.33% |
| AU | 55 | 5 | 8.33% |
| KR | 55 | 5 | 8.33% |
| FR | 55 | 5 | 8.33% |
| BR | 45 | 15 | 25.00% |
| MX | 51 | 9 | 15.00% |
| CN | 15 | 45 | 75.00% |
| JP | 55 | 5 | 8.33% |
| IN | 55 | 5 | 8.33% |
| ZA | 55 | 5 | 8.33% |
| ID | 53 | 7 | 11.67% |
| Total | 592 | 128 | 17.78% |

The machine-readable authority for this profile is [reference_selection.json](../provenance/reference_selection.json). Per-item decisions are in [selection.jsonl](../provenance/selection.jsonl). The profile is retrospective and conditional on item selection; it is not an independently measured result on an unseen benchmark.

## Selected-question check

Selected items and replacements received an AI-assisted quick check against the available official source material. A pass records that this check did not identify an answer/source inconsistency, conspicuous ambiguity, missing assumption, or duplicate option. The public [review records](../provenance/reviews.jsonl) preserve the item IDs and specific notes.

The check is narrower than an independent expert audit. It does not guarantee that every answer is unambiguous under all legal interpretations. Reports supported by official sources can lead to corrections in a subsequent version.

## Interpreting difficulty

The selected reference error profile is evidence about this selection process. It is not evidence that every future model will find the same items difficult. A different model may answer reference-error cases correctly, and the same model can change its answer on rerun.

A difficulty-selected legal benchmark can reveal model differences without matching a general-intelligence ordering. This release neither selects questions to enforce an external ranking nor treats disagreement with such a ranking as a dataset error. Jurisdiction-level outcomes remain part of the result.
