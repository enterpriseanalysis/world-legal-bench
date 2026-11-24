# Evaluation protocol

World Legal Bench 2.0 uses closed-book, single-turn questions and an explicit LLM Judge. The tested model receives the question and four choices. Reference answers, source annotations and selection metadata remain outside its input. Preserve the legal-source version and assumptions stated in each question.

## Inference and judging

`wlb run` writes immutable prediction records. Configure the tested model endpoint, model identifier, reasoning settings, output budget, sampling parameters and retries explicitly. No model requests occur when importing or validating the dataset.

`wlb judge` separately grades saved predictions against the reference option and its meaning. It accepts multilingual final-choice declarations and unambiguous semantic equivalents, strips reasoning before the last `</think>`, and records `correct`, `incorrect` or `invalid_output`. The Judge must not re-solve the question or repair the candidate's answer. A quoted candidate excerpt, chosen option and brief explanation accompany each grade.

Judge JSON is validated for its field schema, evidence origin and consistency between choice and outcome. Malformed or inconsistent replies can be retried; exhausted Judge requests become `judge_error`, not substantive wrong answers. This validation does not guarantee semantic correctness. Preserve the exact Judge model and version in published runs.

`wlb score` aggregates saved, validated judgements without making model calls. Version 2.0 does not silently fall back to regular-expression answer matching. Earlier deterministic parser code is retained for archived protocols and diagnostics.

## Scores and coverage

Report item-level accuracy and region-macro accuracy together. Pool items within each geographic region, then give the five regions equal weight in the macro average. Retain country-level results for analysis. See [methodology](methodology.md#scoring-and-aggregation) for the formulas and interpretation limits.

Incomplete prediction sets must be labeled partial; the scorer withholds full-release macro scores. Invalid answers, inference failures and Judge failures are reported separately. Runtime failures remain visible and must not be reclassified as legal reasoning mistakes. A retry policy must be declared rather than selecting whichever answer happened to score best.

## Platform protocol

The BM platform identifiers are `world-legal-bench-v2-0-{country}`, suite `world-legal-bench-v2-0`, and protocol `world-legal-bench-mcq-v2.0`. Both V1 OpenCompass and V2 adapter integrations use full LLM judging. Geographic grouping does not alter questions, options, reference keys or governing law.
