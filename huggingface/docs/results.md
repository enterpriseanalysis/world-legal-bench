# Reporting results

The included [reference selection profile](../provenance/reference_selection.json) is a retrospective development artifact. It is not a fresh evaluation or an unbiased estimate of the selection model's general legal competence.

A new model result should include the dataset version and manifest digest, exact model identifier, legal-evaluation condition, input messages, reasoning settings, token budget, temperature, parser version, coverage, invalid count, and inference-error count. Report the country-macro accuracy and each country score together.

When discussing consistency, also show the lowest country score and the country gap. Small differences on fixed country subsets should be interpreted cautiously. Country and language vary with content, so this benchmark alone does not establish which factor caused a performance difference.

Different prompts, tool access, parsers, answer keys, or best-of-run policies are different protocols. Label those changes. Do not combine scores from different conditions into one ranking without explaining the aggregation.

No public multi-model leaderboard, public/private correlation study, or version-comparison plot is included in this local preparation. Those artifacts require separately collected and documented results.
