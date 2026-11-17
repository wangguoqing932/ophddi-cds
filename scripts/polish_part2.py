# -*- coding: utf-8 -*-
"""nature-polishing Part 2: Results + Discussion + Conclusion."""
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "outputs" / "paper" / "manuscript.en.md"

PART2 = '''## Results

### System construction

The ophthalmic DDI decision-support system was built on a curated knowledge base of 113 ophthalmic topical agents and 232 systemic medications (Table 1), with 1,307 evidence chunks (all approved release, evidence levels A through E) and a LightRAG index over 1,307 documents. The rule engine comprised 40 mechanism rules, each carrying at least one citation verified through a three-source cross-check (Crossref, OpenAlex, PubMed) with retraction screening (all verified, zero policy errors). The class-matrix layer defined 82 cells across 20 ophthalmic and 37 systemic drug classes with absorption-scaled upgrades.

### Rule consistency and development-phase validation

The deterministic engine achieved 100% rule consistency on the development dataset (Phase 1). On the development-phase internal validation set (78 cases, gold synced to the corrected blind labels), sensitivity was 1.000 and specificity 0.984. We note transparently that these 78 cases overlap the primary validation set by case identity (see Methods and the honest-limitations section); they are reported as a development gate, not as independent evidence.

### Primary evaluation: L1 literature-consensus validation set (118 cases)

Table 3 and Figure 2 summarize the four-method comparison (five seeds each; mean ± SD) on the L1 literature-consensus set, whose gold labels were derived independently of the system outputs (20 FDA-label, Stockley's, or BNF mechanism annotations; 40 procedurally frozen blind cases; 58 guideline cases).

The deterministic system (full_system) achieved 0.915 four-level accuracy, 1.000 high-risk sensitivity (28 of 28), 0.989 specificity, and a Cohen's kappa of 0.870, with zero variance across seeds. Lightrag (KG-context LLM) reached 0.741 accuracy, 0.793 sensitivity, and 0.936 specificity (kappa 0.609). Pure_llm (no context) reached 0.475 accuracy and 0.771 sensitivity (kappa 0.256). Naive_rag (BM25 plus LLM) reached 0.415 accuracy and 0.757 sensitivity (kappa 0.183).

The gradient full_system > lightrag > pure_llm > naive_rag was stable across all five seeds. Naive BM25 retrieval was consistently worse than the context-free LLM baseline, indicating that keyword retrieval injects noise in this domain.

In the per-subset analysis, the procedurally frozen blind subset (n = 40, SHA-locked before evaluation) reached 1.000 accuracy, and the FDA/Stockley's/BNF mechanism subset (n = 20) also reached 1.000. The guideline-sourced subset (n = 58) reached 0.828. All ten three-level disagreements occurred in the guideline subset and concerned judgment boundaries, including QT risk with low-absorption fluoroquinolones, CYP3A4 inhibition with low-absorption macrolides or azoles, weak-corticosteroid potency granularity, and anticholinergic overlap with tricyclic antidepressants. Each disagreement carried a documented pharmacological rationale (Figure 5; supplementary table).

### External audit: DDInter-derived set (92 cases)

On the 92-case audit set (DDInter severity levels stratified by absorption tier, with absorption-based correction), full_system reached 0.707 accuracy (kappa 0.489, specificity 0.955), outperforming pure_llm (0.630), lightrag (0.600), and naive_rag (0.535). The 29 disagreements with the audit gold showed a consistent direction: the system downgrades more aggressively on ophthalmic absorption grounds. This divergence is itself evidence of gold independence, since a tautological gold would score 1.000. It is consistent with the earlier 1,933-pair DDInter audit, in which 75% of original high-risk pairs were downgraded and 77% of downgrades were attributable to low systemic absorption.

### Robustness

Full_system is deterministic: all five seeds returned identical predictions (SD = 0.000 for every metric). LLM baselines showed seed variance of 0.014 to 0.038 in accuracy, reflecting sampling sensitivity.

### Expert review (two clinical ophthalmologists, 12 cases)

Two independent ophthalmology experts reviewed 12 cases (inter-rater agreement 91.7%, kappa 0.846; Figure 3). Expert–system agreement was limited: 41.7% for expert 1 (kappa 0.125) and 33.3% for expert 2 (kappa 0.010). The disagreement was systematic: experts rated most cases one tier lower, consistent with their stated clinical prior that ophthalmic drops have limited systemic impact and are not routinely screened for systemic DDI. Experts explicitly noted that they did not perform mechanism-level assessment. We therefore interpret this divergence as a perspective gap between clinical prior and evidence-based grading, and report it transparently rather than as evidence of system miscalibration.

### Honest limitations

First, gold labels share literature sources with the rules (homogeneous construction): the L1 set is a literature-consensus proxy, not an expert-adjudicated gold. Only the 40 procedurally frozen blind cases are independent in a procedural sense, and only the DDInter severity level provides a third-party component. Second, 78 of 118 L1 cases overlap the development-phase validation set by case identity (gold independent, cases not entirely novel). Third, no real human expert participated in gold construction; the 12-case expert review is the sole human-validation channel and shows a systematic one-tier perspective gap.

## Discussion

### Principal findings

The deterministic three-layer cascade achieved 0.915 four-level accuracy and a kappa of 0.870 on the L1 literature-consensus validation set (118 cases), outperforming three LLM baselines by a wide margin (0.415 to 0.741 accuracy), with zero variance across seeds and millisecond inference. On the DDInter-derived external audit set (92 cases), the system again led all methods (0.707 versus 0.535 to 0.630), with the highest specificity (0.955). The gradient full_system > lightrag > pure_llm > naive_rag was stable across all five seeds, and the procedurally frozen blind subset (n = 40) was classified with perfect accuracy.

### What we add relative to prior work

**Against general-purpose DDI databases.** Existing resources such as DDInter provide comprehensive pair-level severity ratings derived from systemic administration but do not encode the decisive ophthalmic modifier, the magnitude of systemic absorption from topical administration, nor dose-route corrections. Our system makes this ophthalmic pharmacokinetic factor an explicit, first-class modeling component: a systemic-absorption tier (high, medium, low, or very-low) is assigned to every ophthalmic agent, an absorption-scaling step forces low-absorption pairs to low risk unless a mechanism-based upgrade applies, and a hard-constraint layer encodes the absorption-first pharmacology. The 1,933-pair DDInter audit, in which 75% of original high-risk pairs were downgraded and 77% of downgrades were attributable to low systemic absorption, quantifies precisely what a general-purpose database would over-alert on in this setting.

**Against LLM and retrieval-augmented approaches.** Context-free LLMs hallucinate interactions and are non-reproducible. Naive keyword retrieval (BM25) measurably degraded accuracy below the context-free baseline in this domain, and graph-based retrieval (LightRAG) captured only part of the gain. Our system is deterministic (zero variance across seeds), auditable (every decision returns matched rule IDs, decision path, and evidence citations), and fast (about 2 ms per pair), while retaining the full mechanism vocabulary of the knowledge base.

**Systematic coverage of the overlooked space.** Clinical recall of ophthalmic–systemic DDI concentrates on a small set of well-known agents, most prominently non-selective beta-blockers. Beyond this class, interactions are rarely mentioned in routine practice and are easily overlooked. Our system screens all 113 ophthalmic agents against 232 systemic drugs exhaustively, surfacing mechanism-based signals that clinicians may not spontaneously consider, including anticholinergic accumulation with tricyclic antidepressants, additive carbonic-anhydrase inhibition, CYP3A4-mediated exposure changes, and weak-corticosteroid potency boundaries. Each signal is traceable to verified evidence.

**Validation discipline.** Beyond absolute performance, we contribute a four-phase validation protocol with a procedurally frozen blind subset (SHA-locked), a third-party audit component (DDInter severity levels), a five-seed protocol separating deterministic and stochastic methods, and transparent reporting of homogeneous-construction and overlap limitations. These elements are rarely reported together in clinical NLP or CDSS studies.

### The expert–system gap: a systematic perspective divergence

Two independent ophthalmologists agreed closely with each other (kappa 0.846) but rated most cases one tier lower than the system. We interpret this divergence through three observations. First, clinically serious events from ophthalmic–systemic DDI are rare, and expert judgments rationally gravitate toward lower risk tiers. Second, the few interactions clinicians do recall are dominated by non-selective beta-blockers, which are prominently discussed in prescribing guidance; the systematic coverage described above is therefore most valuable precisely where clinical recall is weakest. Third, consistent with the first two observations, reports of serious adverse events attributable to ophthalmic–systemic interactions are rare in the PubMed literature, and clinicians generally regard ophthalmic medications as having limited systemic influence. This prevailing perception constitutes our main adoption barrier: a screening tool whose outputs sit one tier above clinical intuition will be treated as noise unless its mechanism-based justifications are presented transparently, which our traceable decision paths are designed to do.

### Limitations

**Bounded clinical impact.** The scarcity of direct evidence plausibly reflects that ophthalmic absorption rarely alters systemic drug handling in a clinically detectable way. A substantial part of the rule layer is mechanism-derived: PubMed yielded few dedicated ophthalmic–systemic interaction studies or case series, and the evidence base is populated largely by pharmacokinetic first principles, class-level pharmacology, and extrapolation from systemic data (1,307 curated chunks, but few ophthalmic-specific outcome studies). To the extent that the true risk gradient clusters at the low end for most ophthalmic agents, an evidence-graded system may systematically over-grade relative to what clinical practice observes, and the clinical impact of the system is correspondingly bounded.

**Validation-related limitations.** The L1 gold labels were constructed from the same literature sources that informed the rules (homogeneous construction); the set is a literature-consensus proxy rather than an expert-adjudicated gold, and only the 40 procedurally frozen blind cases are independent in the procedural sense. In addition, 78 of 118 L1 cases overlap the development-phase internal validation set by case identity, and no real human expert participated in gold construction; the two-expert review is the only human channel and shows the systematic one-tier perspective gap discussed above. These constraints bound the strength of the accuracy claims and are reported to support a fair assessment.

### Future directions

Three directions follow directly. First, clinical calibration: a larger expert panel, or outcome-linked retrospective data, could establish whether a systematic one-tier offset should be applied to specific absorption tiers or drug classes, converting the perspective gap into a calibrated prior. Second, evidence enrichment: targeted pharmacovigilance mining (FAERS-style) and prospective monitoring of high-absorption agents would test the mechanism-derived rules against real-world outcomes and populate the sparse evidence base. Third, scope extension: the class-matrix architecture transfers naturally to other specialty–systemic interaction domains (dermatologic, inhaled, and intranasal routes) with the same absorption-first design.

## Conclusion

We developed an ophthalmic DDI decision-support system built on a deterministic, fully explainable three-layer cascade, consisting of 40 citation-verified rules, an absorption-scaled class matrix, and a hard-constraint layer encoding ophthalmic systemic-absorption pharmacology, grounded in 1,307 verified evidence chunks. Across 118 literature-consensus validation cases and a 92-case DDInter audit, the system outperformed three LLM baselines (accuracy 0.915 versus 0.475 to 0.741; 0.707 versus 0.535 to 0.630) with zero seed variance and complete output traceability, adding ophthalmic absorption scaling and systematic coverage that general-purpose databases and current LLM approaches lack. A two-expert clinical review confirmed high inter-rater reliability (kappa 0.846) and revealed a systematic one-tier perspective gap that we attribute to the low base rate of serious ophthalmic–systemic events, the clinical emphasis on beta-blockers to the exclusion of other classes, and the scarcity of direct evidence. The system is best understood as a systematic, mechanism-based second reader that prevents overlooked interactions in a low-frequency risk space; its clinical value, calibration, and generalizability warrant prospective outcome-linked evaluation.

'''

DECL = '''
## Keywords

ophthalmic drug-drug interaction; clinical decision support; deterministic rule engine; systemic absorption; explainable artificial intelligence; medication safety

## Data Availability Statement

The datasets and code supporting this study are available as supplementary material, including a downloadable release package with a zero-configuration web interface (requirements: Python 3.11). Engine, rules, evidence, and index files are version-controlled with SHA-256 fingerprints recorded in the project progress log.

## Ethics Statement

The expert review component involved two ophthalmologists assessing 12 hypothetical drug-pair cases; no patient data, biological samples, or clinical interventions were involved. Ethics approval was not required for this study design.

## Author Contributions

[To be completed by the corresponding author.]

## Funding

[To be completed. If none, state: This research received no specific grant from any funding agency.]

## Conflict of Interest

The authors declare that the research was conducted in the absence of any commercial or financial relationships that could be construed as a potential conflict of interest.

## Generative AI Statement

Generative AI tools were used during the research and manuscript preparation: DeepSeek-chat (deepseek.ai) for LLM-baseline evaluations and literature-assisted drafting, and Zhipu GLM-4.6V for visual verification of figures. Figure 1 (system architecture schematic) was created with an AI image-generation tool from a prompt defined by the authors (prompt archived in Supplementary Figure S1); all quantitative figures (Figures 2 through 5) were generated directly from system outputs with Matplotlib. All AI-generated content was reviewed and validated by the authors, who take full responsibility for the content of this manuscript.

'''


def main() -> None:
    old = P.read_text(encoding="utf-8")
    idx_results = old.find("## Results")
    idx_decl = old.find("## Keywords")
    assert idx_results > 0
    head = old[:idx_results]
    tail = old[idx_decl:] if idx_decl > 0 else ""
    P.write_text(head + PART2 + DECL + tail, encoding="utf-8")
    print("Part 2 (Results/Discussion/Conclusion/Declarations) rewritten")


if __name__ == "__main__":
    main()
