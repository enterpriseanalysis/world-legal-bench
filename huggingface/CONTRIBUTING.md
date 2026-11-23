# Contributing

## Item corrections

A useful item report identifies the question ID, the disputed wording or answer, the official source URL and provision locator, and the legal edition being used. Explain whether the problem is an incorrect key, multiple defensible options, a missing assumption, an ambiguous translation, or an inaccessible specified source.

Reviewers should compare the question against its stated legal version. A later legal amendment can justify a new item revision without making the original version's answer incorrect. Include enough source context to distinguish those cases.

The release is frozen. Do not overwrite its data files to make a local score improve. A maintained correction should preserve the old item, assign a revised dataset version, record the exact change and evidence, and update the manifest and tests.

## Evaluator changes

Parser changes need positive and negative behavioral tests. A correct explicit answer should be recognized while reasoning letters, Portuguese articles, quoted option discussion, multiple choices, and conflicting conclusions remain distinguishable. Do not add question-ID-specific parsing rules or consult gold labels during extraction.

Scoring changes should preserve explicit coverage and failure accounting. Missing or invalid predictions must not disappear from a reported denominator. Inference tests should use local fixtures; they must not require real credentials or paid model requests.

```bash
python evaluate.py --help
```

## New model results

Follow the [reporting template](docs/results.md). Include exact configuration and saved final responses where redistribution is permitted. Do not submit API keys, private endpoints, personal data, provider reasoning transcripts, or confidential operational logs.

New runs must be labeled as new observations. The bundled reference selection profile must not be relabeled as an independently reproduced test result.
