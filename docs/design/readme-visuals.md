# README visuals

The current v2.0 README uses `assets/regional-coverage-v20.svg`, a deterministic diagram
of the five region counts in `provenance/v2.0/reference_selection.json`. It makes no geographic
boundary or model-performance claim. The previous assets below are retained as historical
v1.4.1-release artwork and are not embedded in the v2.0 homepage.

# README visual assets

The README uses a white research-publication treatment, aligned with the structure of a Hugging Face dataset card. The artwork provides identity; the coverage and protocol figures carry inspectable claims about the release.

| Asset | Purpose | Evidence or method |
|---|---|---|
| `assets/hero-research-v2.png` | Editorial title artwork | Built-in image generation; prompt below. Decorative geography is illustrative and does not encode coverage. |
| `assets/coverage-matrix-v2.png` | Jurisdiction and selected-language coverage | Country counts and language fields in the frozen questions and jurisdiction metadata. |
| `assets/evaluation-flow-v2.png` | Closed-book scoring contract | Question messages, single-turn inference, final-choice parser, and country-macro scorer. |
| `assets/selection-profile-v2.png` | Retrospective selection composition | `provenance/reference_selection.json`; not a new model run. |

Each generated plotting asset is also available as SVG. Read the cover and figures at the 720px content width used by a dataset card; titles, labels, and metric qualifiers must remain visible. Run `python scripts/build_readme_visuals.py` with Matplotlib installed to regenerate the figures. Matching copies are placed under `huggingface/assets/` for the self-contained dataset folder.

## Cover prompt

The cover was generated with the built-in image-generation tool, not an API/CLI fallback. The exact generation prompt was:

```text
Create a polished wide horizontal editorial cover image for a serious research benchmark dataset card, approximately 3:1 aspect ratio. White / near-white background, elegant restrained typography, sophisticated scientific publication design inspired by clean Hugging Face research dataset cards. Do NOT draw a browser, website screenshot, charts, leaderboard, badges, or a fake interface. On the left, clear large exact title 'World Legal Bench' in a refined dark ink serif, with exact small subtitle 'Legal reasoning across jurisdictions' in a neat sans serif. Below, exact small metadata line '720 questions  /  12 jurisdictions  /  9 languages'. On the right, a restrained original conceptual illustration: a thin-line abstract globe, precisely arranged legal-document sheets, elegant column-like geometric forms, connected source-reference nodes; small flat geometric teal, indigo and muted amber accents. It should feel like a credible law-and-AI research publication rather than a technology sales banner. Flat editorial illustration, beautifully balanced asymmetry, precise fine lines and ample but purposeful whitespace, no gradients across the entire background, no heavy shadows, no 3D rendering, no gavel, no scales of justice cliché, no flags, no institution logos, no watermarks. Keep all text comfortably inside the frame and very legible at 720px display width. The illustration should be secondary to the title. New original artwork. Save the generated asset as an available local image file so it can be incorporated into the project's README.
```

The generated cover's title and metadata were visually checked. The cover is not a jurisdiction map or a model-performance figure. No leaderboard or model-comparison image is included without independent run data.
