# Dataset-repository evaluation protocol

The default condition is closed book and single turn. Send the item question and the four labeled choices in A-D order. Do not send its answer, answer text, annotations, official source extracts, or reference selection metadata to the model.

The system instruction is printed in the [dataset card](../README.md#answering-and-scoring-approach). It is English for every jurisdiction; the item question and choices retain their authored language. Record any change to this instruction or to tool access.

## Saved predictions

Prediction records use `id` to match `question_id` in the dataset:

```json
{"id":"WLB14-US-J0003-001","prediction":"D","status":"ok"}
```

`prediction` is a string containing the model's final response. `status` is optional and defaults to `ok`; set it to `error` when inference failed. An error record is invalid even if its text contains a correct letter. Unknown IDs, repeated IDs, non-string predictions, and unsupported status values are rejected.

The evaluator consumes final responses only. If the inference API separates reasoning and final answer fields, save the final answer field. If a serialized response contains `</think>`, the parser considers only the portion after its last occurrence. A missing channel boundary cannot be inferred reliably.

## Parsing and scoring

The deterministic [parser](../evaluation/parser.py) is `world-legal-final-choice-v1.3`. It recognizes explicit multilingual answer declarations and common Markdown formatting. Several different declared options remain invalid. It does not extract an arbitrary A-D from discussion, and a Portuguese article A is not a bare answer choice.

The grader compares the unique extracted label with the gold label. Correct answers score one; wrong, empty, invalid, and failed-inference responses score zero. There is no partial-credit or abstention reward. Inference-error counts are a subset of invalid counts, not an additional outcome bucket.

A complete run requires every question ID exactly once. Each country score is its accuracy; the overall score is the unweighted country mean. Equal country counts make this identical to pooled accuracy. The report also gives the minimum country score and the maximum-minus-minimum country gap in percentage points.

```bash
python evaluate.py --predictions predictions.jsonl --output report.json
```

The evaluator verifies the bundled manifest's file digests before scoring. A digest check detects changed bytes; it does not establish legal correctness. Invalid output remains in the submitted denominator. Missing records cause the default scorer to fail rather than silently inflate accuracy.

With `--allow-partial`, the evaluator reports submitted-only accuracy and coverage, sets `complete` to false, and withholds macro, minimum-country, and country-gap metrics. Such reports are for debugging and must not be described as complete benchmark results.

## Run disclosure

Record the exact model/provider identifier, snapshot when known, temperature, reasoning settings, output-token budget, other sampling parameters, input template, parser version, and coverage. Preserve each run separately. Retry selection and repeated-run aggregation must be disclosed.

This local dataset bundle performs no inference by itself. `evaluate.py` uses only saved predictions and does not access model APIs.
