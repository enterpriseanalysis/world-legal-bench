# Reporting results

## Reference selection profile

The bundled [reference_selection.json](../provenance/reference_selection.json) describes historical responses used in selection. It is not a fresh evaluation of the standalone release, not a held-out model result, and not a public leaderboard. The country breakdown and interpretation are in [methodology](methodology.md#final-composition).

The scorer can reproduce the selection profile from the released option labels without making model requests. This verifies aggregate arithmetic and scoring compatibility; it does not independently recover or verify the original response extraction.

## Report template

A model result should provide the following information alongside the generated score report:

| Field | Required disclosure |
|---|---|
| Dataset | `1.4.1-release`, preferably with the manifest digest |
| Model | Exact model/provider identifier and snapshot when known |
| Condition | Closed book, single turn; describe any variation |
| Inference | Temperature, token budget, reasoning settings, sampling parameters |
| Input | Exact message template or exported prompt file digest |
| Parser | Version and any extraction changes |
| Coverage | All expected items, missing records, invalid responses, inference errors |
| Aggregation | Country-macro score and each country's accuracy |
| Repeats | Number of independent runs and the run-selection policy |
| Tools | Any browsing, retrieval, or external material supplied |

Report the lowest country score and country gap when discussing jurisdictional consistency. A single macro score does not describe the full country profile.

## Comparability

Changing prompts, tool access, question wording, answer keys, parser rules, or run selection can change the measurement. Compare runs with the same protocol or label the differences. Do not select the best retry or best run without disclosing that policy.

Country differences are observational for this item set. The languages and questions differ between countries, and selection used one reference model. The dataset does not support a causal claim that one language or legal system alone caused a score difference.

## Synthetic scorer check

A gold-derived file can test the evaluator locally:

```bash
python examples/make_perfect_predictions.py --output outputs/synthetic-gold.jsonl
wlb score --predictions outputs/synthetic-gold.jsonl --output outputs/synthetic-report.json
```

The expected score is perfect by construction. This is a software smoke test, not a model evaluation, and must never be placed in a model leaderboard.
