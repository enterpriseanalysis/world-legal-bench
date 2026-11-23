# Data format

## Questions

`data/v1.4.1-release/questions.jsonl` contains one JSON object per item. It contains no answer key. Labels and wording are preserved from the parent dataset.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable authored question identifier |
| `revision` | integer | Authored item revision |
| `country` | string | Two-letter benchmark jurisdiction code |
| `language` | string | Selected test language, including `zh-Hans` |
| `question` | string | Original scenario and question text |
| `choices` | object | Four distinct text values keyed by A, B, C, D |
| `task_family` | string | Authored reasoning/procedure category |
| `knowledge_family` | string or null | Authored topic grouping when supplied |
| `source_ids` | string array | References into `sources.jsonl` |

IDs can retain prefixes from earlier authoring releases. Membership in this dataset is determined by the release manifest and question file, not by the prefix.

## Answer keys

`answers.jsonl` contains `id`, `answer`, `answer_text`, and `option_rationales`. `answer` must be one of A-D. `answer_text` must exactly equal the corresponding choice in the question file. `option_rationales` maps all four labels to authored explanatory text.

Answer keys are intended for evaluation and error analysis. They must not be inserted into model prompts. The runner and prompt exporter use the question file, not the answer file, to construct model messages.

## Source references

`sources.jsonl` deduplicates reference metadata by a content-derived `SRC-...` ID. Each source contains `country`, `url`, `locator`, `version`, and `digests`. A version can be a string or a list of authored edition labels. Digest keys are preserved from the source records; they can describe an extract or a larger source text, depending on the original field name.

Source digests are provenance metadata. Without the exact original bytes, they are not a way to reconstruct missing source texts. URLs and locators are provided for inspection; bulk official source text is not redistributed.

## Provenance

`provenance/selection.jsonl` contains the reference model, extracted choice, gold label, outcome, and extraction protocol for every selected item. It contains no provider credentials, private task IDs, or response transcripts.

`provenance/reviews.jsonl` contains the selected-item quick-check verdict, review type, and a specific source-check note. Notes are in Chinese; legal questions retain their original test language.

`provenance/release.json` states the parent dataset version, parent size, original release content digest, and export mapping. `reference_selection.json` stores the aggregate retrospective selection profile. These are provenance artifacts, not a new model leaderboard.

## Manifest

`manifest.json` identifies the dataset, condition, count, scoring protocol, and parser version. Its `files` object maps repository-relative data/provenance paths to SHA-256 digests. The manifest is not included in its own digest list.

The validator rejects missing or changed files, duplicate JSON keys, misaligned IDs, invalid answer/choice mappings, incomplete review coverage, and incorrect country quotas. The reference [JSON schemas](../schemas/) describe the interoperable question, answer, and prediction records; release integrity checks are implemented in the Python validator.
