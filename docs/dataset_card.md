# Dataset card

World Legal Bench 2.0 contains 360 source-linked closed-book legal multiple-choice questions in nine selected test languages, covering twelve jurisdictions in five UN M49-referenced reporting regions. The [methodology](methodology.md) defines selection and grouping.

The release retains 327 recorded nonpasses from a saved gpt-6-luna run and supplements them with 33 recorded successes. Nonpasses include 301 incorrect and 26 invalid final answers. This reference-guided process creates explicit selection bias; the set is not a representative sample of legal questions or an independent holdout for that model.

Question text, options, keys and source bindings are inherited unchanged from the v1.4.2 parent pool. No new expert audit is claimed. Questions concern constitutional and public law, including statutory procedure, public accountability, institutional powers and related source-bound legal application. Topic coverage varies by jurisdiction.

Use the set for controlled model comparisons and error analysis. Do not use its results to certify professional legal competence, infer the capability of every jurisdiction in a region, or establish a causal effect of language. Authored data uses CC BY 4.0; underlying source documents retain their own terms.
