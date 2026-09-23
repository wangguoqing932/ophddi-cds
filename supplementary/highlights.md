# Highlights

- A deterministic, zero-LLM three-layer cascade screens 113 ophthalmic against 232 systemic agents using 40 citation-verified mechanism rules, an absorption-scaled 20 x 37 class matrix, and a hard-constraint layer that encodes ophthalmic systemic-absorption pharmacology.
- On 118 literature-derived cases the system reached 0.915 exact accuracy (kappa 0.870), outperforming three LLM baselines across five temperature conditions while returning identical predictions at every temperature (SD = 0.000).
- A full audit of 1,933 registry-matched DDInter pairs showed 75.0% graded lower once ophthalmic absorption is modelled, with 77.0% of downgrades attributable to low systemic absorption, quantifying a gap that systemic-route databases leave unmodelled.
- High-risk sensitivity on the DDInter-derived audit set was 0.440 (11 of 25), the lowest of the four methods; the paper reports this false-negative profile as a primary limitation rather than a footnote.
- Two independent ophthalmologists agreed closely with each other (kappa 0.846) but graded most cases one tier below the system and its gold, a divergence reported as a clinical-prior versus evidence-graded-gold gap rather than masked.
