# Results and reporting

## Retrospective selection profile

The saved `gpt-6-luna` (`max`) answers used for v2.0 selection contain 33 correct, 301 incorrect and 26 invalid final-answer outcomes. This gives 9.17% item-micro and 9.13% region-macro accuracy on the selected 360 items. The [reference profile](../provenance/v2.0/reference_selection.json) records the exact counts.

These are selection-conditioned statistics, not an independently rerun benchmark result or a public multi-model leaderboard. Raw model transcripts are not distributed. Do not treat the selected reference score as evidence of general model capability or calibration to another benchmark.

## Required result disclosure

Report dataset version and manifest digest; tested model/provider snapshot when available; Judge model and configuration; inference protocol, reasoning settings, token limits and sampling parameters; item-micro and region-macro accuracy; per-region and per-jurisdiction results; correct, incorrect and invalid-answer counts; missing items and execution failures; retry/repeat policy; and any tools or external context supplied to the tested model.

Only compare runs using compatible data and grading. Version 2.0 is not directly comparable to v1.4.1-release. Regional results summarize included jurisdictions rather than entire geographic populations. A four-item Brazil subset, for example, cannot support precise national capability estimates.
