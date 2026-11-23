# Reproducibility

## Frozen evaluation artifacts

The released question text, option order, and answer labels define the test. The standalone file layout separates public questions from answer keys without changing those fields. [release.json](../provenance/release.json) identifies the original release digest and field mapping.

The [manifest](../data/v1.4.1-release/manifest.json) hashes all data and provenance files used to identify the frozen dataset. Validation checks those bytes before checking semantic relationships such as answer/choice alignment and complete per-country coverage. A checksum detects a change; it does not prove a legal answer is correct.

```bash
python scripts/check_release.py
python -m unittest discover -s tests -v
```

## Legal source recovery

Official URLs, provision locators, edition labels, and available source digests are bundled. Full legal source archives are not. Some edition labels name authoring snapshots; official URLs can later point to updated texts. Consequently, the exact source bytes cannot always be recovered from this distribution alone.

When independently checking an item, use its stated legal version and assumptions, locate the provision in an official archive, and record the source edition. A current consolidated text should not silently replace the item's specified version. If the specified version cannot be established, report that uncertainty with the question ID.

## Reference response recovery

Reference choices and outcomes are distributed in selection provenance. The original provider responses, operational task metadata, and reasoning transcripts are not. The retrospective profile can be recomputed from the choices; independent re-extraction from original transcripts is outside this distribution.

A new model run is a separate observation. Preserve its raw final responses and configuration, then score with the same parser. Do not overwrite historical results when evaluating a revised parser or answer key.

## Version boundaries

The package version is `1.4.1`; the exact dataset label is `1.4.1-release`. Record the dataset label with every result. Data files should be treated as immutable. A correction to wording, legal assumptions, source interpretation, or answer labels requires a new dataset revision and an explicit correction record.

Parser changes are also versioned. An alternative extractor can be useful for error analysis, but its results should be labeled with the new parser identity. Scores obtained with different extractors should not be silently mixed.
