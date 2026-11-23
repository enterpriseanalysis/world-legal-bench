# Hugging Face publication checklist

This is a local preparation. No repository has been created or uploaded. The dataset card is `README.md`; the default viewer configuration points only to `data/test.jsonl`.

## Ready locally

- English dataset card with Hub YAML metadata and a Chinese companion.
- Default configuration, one test split, and a joined question/answer table.
- Unchanged question IDs, wording, option order, and gold answers.
- Coverage table, data-derived language figure, column descriptions, and loading examples.
- Source references, option rationales, selected-item review notes, and selection provenance.
- Standalone deterministic evaluator and file digests.
- Citation metadata, scoped licenses, and contribution instructions.

## Information to confirm

| Item | Needed information | Effect |
|---|---|---|
| Hub namespace and dataset ID | Account or organization plus final repository name | Required to create the intended public URL later. |
| Author and institution attribution | Preferred public team/institution name and contributor attribution | Current citation uses the collective name World Legal Bench contributors. |
| Public contact | Issue tracker or public contact channel | Needed for direct correction reports on a published page. |
| License sign-off | Confirmation of the prepared MIT code / CC BY 4.0 authored-data scope | Complete before public distribution; third-party material is excluded from the grant. |

## Optional additions matching the reference page

| Artifact | Missing evidence or resource |
|---|---|
| Public code-repository link | A published repository URL; only a local Git repository exists. |
| Official benchmark website / leaderboard | A public URL that actually serves the intended release. |
| Paper, arXiv, or DOI link | A real manuscript or registered identifier. |
| Multi-model comparison plots | Independent complete model runs with exact inference and scoring settings. |
| Version-to-version comparison | The same models evaluated on both frozen versions under matched protocols. |
| Public/private agreement study | A defined independent holdout and paired model results. The parent candidate pool alone is not a validated holdout. |
| Independent expert-review claim | A completed and documented legal-expert review. Current records are AI-assisted quick checks. |

Download counts, likes, followers, linked papers, and “models trained on this dataset” are host-managed page elements. They cannot be populated with invented values in a README. Their actual appearance depends on a future hosted repository and Hub activity.

## Before any future upload

Recheck local hashes, dataset loading, column types, links, licenses, attribution, and evaluator behavior. Confirm that only this folder is intended for the dataset repository. An upload requires a new explicit user instruction; nothing in this checklist or the local build script authorizes publication.

## Local source-checkout commands

From the parent benchmark checkout, `python scripts/build_huggingface.py` rebuilds the joined data and standalone evaluator. `python scripts/build_huggingface_figure.py` regenerates the coverage figure; it requires Matplotlib. The optional dependencies are listed in `requirements-huggingface.txt`.

`python scripts/check_huggingface.py` parses the card and loads the configured split using the HF libraries with network access disabled. This verifies local compatibility, not an actual hosted Dataset Viewer. `python -m unittest discover -s tests -v` checks the canonical and bundled evaluator behavior.
