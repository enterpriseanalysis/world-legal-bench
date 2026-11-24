# Reproducibility

Run `wlb validate` or `python scripts/check_release.py` to verify the current data manifest, quota map, unique item identities and source/gold alignment. These checks do not call models or constitute a legal expert audit.

Preserve immutable prediction and Judge-output files with run configuration. `wlb score` reproduces aggregate arithmetic from those saved grades without contacting a provider. Report both item-micro and region-macro accuracy and use the same grouping and retry policy across compared models.

The current data manifest and `provenance/v2.0/release.json` identify the parent pool. The release-selection builder accepts explicit private platform snapshots and a pinned parent bundle, verifies identities, and emits public selection metadata. Private provider transcripts are not included, so public users can reproduce the released selection arithmetic but cannot independently reconstruct the original Judge's semantic decisions from those metadata alone.

The archived `data/v1.4.1-release/` files and their original provenance remain unchanged. Use the corresponding historical code version to reproduce the archived grading protocol.
