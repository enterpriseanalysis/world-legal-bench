# Evaluation protocol

## Model input

The default condition is closed book, single turn, and one independent question per request. The harness sends the original question and four labeled choices. It supplies neither reference answers nor rationales, official source extracts, retrieval tools, browsing, or a prior conversational history.

The exact system instruction is defined in [messages_for](../src/world_legal_bench/dataset.py). It requests one uppercase letter and instructs the model to follow the item's legal version and assumptions. The instruction is English for all jurisdictions; the question and choices retain their authored test language. A different system instruction is a protocol variation that must be reported.

Export input messages with:

```bash
wlb export-prompts --output outputs/prompts.jsonl
wlb export-prompts --country KR --output outputs/kr-prompts.jsonl
```

Export files contain IDs, country/language metadata, and chat messages. Only the messages are passed to the model.

## Inference settings

Any inference implementation can be used if it preserves the input and records its settings. Identify the exact model/provider snapshot, reasoning or thinking configuration, temperature, sampling parameters, output-token limit, and any endpoint-specific settings. Repeated runs should have separate prediction files.

The optional built-in runner requires an explicitly configured Chat Completions base URL. It appends `/chat/completions`, reads the key from `OPENAI_API_KEY`, and stores final `message.content`. Separate provider reasoning fields are not included in scoring records. It does not automatically configure provider-specific thinking settings.

| Argument | Default | Purpose |
|---|---|---|
| `--model` | Required | Endpoint's model identifier |
| `--base-url` | `OPENAI_BASE_URL` | Base URL including any API prefix, such as `/v1` |
| `--output` | Required | Append-only prediction JSONL |
| `--workers` | 4 | Maximum active worker threads |
| `--qpm` | 60 | Shared request-start rate, including retry attempts |
| `--max-tokens` | 131072 | Requested output-token budget; provider must support it |
| `--temperature` | 0 | Requested sampling temperature |
| `--timeout` | 600 seconds | Per-attempt HTTP timeout |
| `--retries` | 2 | Additional attempts for transport errors, HTTP 429, or HTTP 5xx |
| `--extra-body` | `{}` | Additional non-credential provider parameters |
| `--resume` | Off | Require the same configuration and skip existing records |
| `--limit` | Unset | Debug subset; not a complete benchmark run |

Workers and QPM bound different parts of execution. QPM is not an estimate of completion throughput: output length, provider token limits, latency, and retries also affect wall time. Unsupported budgets or provider settings can produce an HTTP error. Supply compatible settings and report the change rather than silently altering a run.

A `.run.json` sidecar records non-secret configuration. Resume compares the saved configuration and question IDs; a changed configuration is rejected. Records with saved inference errors are also considered present during resume. A deliberate retry experiment should use a new output file, with its policy disclosed.

The runner records elapsed time per item including its rate wait and retries. Usage is the terminal response's usage object when available, not certified total retry billing. The toolkit does not calculate model prices or costs.

## Prediction format

Each record contains a unique release question ID and a string `prediction`:

```json
{"id":"WLB14-US-J0003-001","prediction":"D","status":"ok"}
```

`status` is optional and defaults to `ok`. Set it to `error` for a failed inference; such a record counts as invalid even if its text contains a correct option. Extra run metadata is allowed. Unknown IDs, duplicate IDs, non-string predictions, and unsupported status values are rejected. Prediction line order does not affect scoring.

## Final-answer extraction

The parser is frozen as `world-legal-final-choice-v1.3` in [parser.py](../src/world_legal_bench/parser.py). If a closing `</think>` marker is present, extraction uses the segment after its last occurrence. Otherwise it uses the supplied string as the final response. The parser cannot infer a missing channel boundary; submit the actual final response when an API separates reasoning and answer fields.

Supported answers include a bare option, common explicit multilingual answer declarations, and recognized concluding lines. Markdown emphasis and a surrounding text code fence can be removed. Examples include `Correct answer: A.`, `正确选项：A。`, `正解は C です。`, and `A alternativa correta é B`.

Multiple declared options or conflicting conclusions are invalid. A Portuguese article A and an English sentence such as `A court may decide ...` are not bare answers. Arbitrary letters inside legal discussion or quoted option text are not a fallback answer. A correct rationale without a recognized final choice remains invalid under this scoring protocol; semantic rejudging is a separate experiment.

## Scores and coverage

For each jurisdiction, accuracy is the number of correct predictions divided by the number of submitted predictions. Invalid, empty, and inference-error records remain in this denominator. Inference errors are a subset of invalid records, not an additional error count.

For a complete run, the primary overall score is the unweighted mean of the jurisdiction accuracies. Because this release uses equal country counts, it equals pooled micro accuracy. The report also includes minimum country accuracy and the maximum-minus-minimum country gap, in percentage points.

Complete runs require every release ID exactly once. With `--allow-partial`, the report gives submitted-only accuracy and explicit coverage, marks `complete: false`, and withholds country-macro, minimum-country, and country-gap metrics. A partial report must not be presented as a complete benchmark result.

```bash
wlb score --predictions outputs/predictions.jsonl --output outputs/report.json
wlb score --predictions examples/predictions.example.jsonl --allow-partial
```
