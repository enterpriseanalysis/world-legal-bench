# Data format

The current release lives in `data/v2.0/`. JSONL files are UTF-8 with one object per line. Item IDs are inherited from the parent pool and are stable across schema exports; new dataset IDs distinguish the evaluation version.

| File | Record fields |
|---|---|
| `questions.jsonl` | `id`, `revision`, `country`, `region`, `language`, `question`, four-entry `choices`, `task_family`, `source_ids` |
| `answers.jsonl` | `id`, `answer`, `answer_text`, inherited `option_rationales` or `statement_reviews` |
| `sources.jsonl` | `id`, `country`, official `url`, `locator`, pinned `version`, available source `digests` |
| `jurisdictions.json` | Country identity, selected language, region and release-specific `cases` quota |
| `manifest.json` | Version, counts, protocol, quota map, provenance directory and file hashes |

Provenance is in `provenance/v2.0/`. Selection records include original sample position, reference outcome, reference choice when resolvable, and selection reason. Invalid final answers can have a null reference choice. No raw platform credentials or provider transcripts are included.

Inference predictions use `id`, textual `prediction`, and optional `status=ok|error`. Judged records add `judgement` with `outcome`, `choice`, `evidence` and `reason`, plus Judge identity/version. Exhausted Judge calls use `status=judge_error`. The aggregator requires judgements for v2.0; it does not guess missing grades.

The Hugging Face export joins question and gold columns for inspection. Its `answer` column is private evaluation material relative to the tested model and must never enter the tested model prompt.
