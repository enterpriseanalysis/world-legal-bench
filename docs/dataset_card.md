# Dataset card

## Identity and intended use

World Legal Bench v1.4.1-release is a difficulty-selected, closed-book multiple-choice dataset for evaluating constitutional and public-law reasoning in jurisdiction-specific languages. Its machine-readable identity is in [manifest.json](../data/v1.4.1-release/manifest.json).

The evaluation unit is one question with four options and one reference answer. Each jurisdiction contributes the same number of items. The [coverage table](../README.md#coverage) specifies the selected languages and counts. The dataset is a single evaluation split; no training split, validation split, or matched translation split is provided.

Intended uses include comparing models under a shared protocol, examining jurisdiction-level differences, and analyzing errors involving authority, legal scope, procedural thresholds, and exceptions. The dataset does not establish whether a model can deliver reliable professional legal services.

## Content and construction

Items apply stated legal texts and assumptions to concrete scenarios. They can involve multiple provisions, institutional distinctions, changes in material facts, and procedural sequencing. The scope includes constitutional rules and related public-law statutes; it is not limited to the text of national constitutions. Some retained questions refer to judicial decisions.

The parent candidate release contained 10,132 items. This release contains a selected subset, with wording, options, and reference answers preserved. A public export separates model-visible questions from answers and converts embedded legal source material into source-reference records. [release.json](../provenance/release.json) records the transformation and upstream content digest.

Selection used existing `qwen3.8-flash` responses. The intended ratio was 55 reference errors to 5 reference successes per jurisdiction. Where fewer eligible mistakes remained, reference successes filled the quota. All selected items received an AI-assisted source quick check. Ten initially selected items were excluded for identified problems or insufficient source evidence; replacements were also checked. See [methodology](methodology.md) for the final composition.

## Labels and review

Each answer record contains a single option label, the matching answer text, and a rationale for each option. The answer label and text must agree exactly with the question's options. Released question IDs preserve both retained older IDs and newer authoring IDs; the ID prefix alone does not identify this release's membership.

Authorship and selected-question checking were AI-assisted. The checks covered consistency with the supplied legal source, unique answer selection, conspicuous ambiguity, missing assumptions, and duplicate options. [reviews.jsonl](../provenance/reviews.jsonl) provides item-level notes in Chinese. This is not an independent legal-expert certification, and additional errors may remain.

An answer key is public for reproducibility. It must be kept separate from model input and must not be used to tune a model while claiming an uncontaminated evaluation.

## Source grounding and legal scope

Source records contain official URLs, provision locators, edition labels, and available content digests. They do not redistribute the bulk legal source texts. Some labels refer to an authoring snapshot rather than a publisher-issued edition. Source availability and URL revision stability differ between jurisdictions.

A question's stated legal version and assumptions define the intended task. The dataset does not assert that its answer describes the law currently in force on the evaluation date. A jurisdiction's legal reforms can therefore require a new dataset revision rather than a silent edit.

## Limitations

Selection is conditioned on one reference model's mistakes. The resulting performance distribution is not representative of a random sample of legal questions, and models may benefit unequally from the selection process. Questions about the same provisions can also be correlated.

Country and language are not independently controlled. Different jurisdictions have different legal topics and questions, and only one selected test language is used for each jurisdiction. Differences between country scores cannot be attributed solely to language competence, training-data coverage, legal-system familiarity, or fairness.

Each jurisdiction has a small fixed evaluation set. Small score differences should be interpreted cautiously. Neither a high total score nor a low score in one jurisdiction establishes professional competence or a complete profile of that jurisdiction's legal knowledge.

The original response transcripts are not included. Public selection labels can be inspected, but the original extraction process cannot be independently replayed from this repository alone. No new live model evaluation was performed when creating the standalone export.

## Distribution and maintenance

The code and original authored dataset have separate licenses, as specified in [NOTICE](../NOTICE). Official sources and third-party quotations retain their original rights status. Internal deployment artifacts, private service addresses, authentication material, and evaluation task identifiers are excluded from this export.

Reports of errors should include the item ID, disputed answer or assumption, and an official source with a provision locator. Correction policy and versioning rules are in [CONTRIBUTING.md](../CONTRIBUTING.md).
