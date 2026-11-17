# -*- coding: utf-8 -*-
"""Split remaining long sentences in manuscript.en.md (nature-polishing: <=30-35 words)."""
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "outputs" / "paper" / "manuscript.en.md"
t = P.read_text(encoding="utf-8")

REPL = [
    # Abstract
    ("Outside a few well-known classes, such as non-selective beta-blockers, ophthalmic\u2013systemic interactions are easily overlooked in clinical practice.",
     "Outside a few well-known classes, such as non-selective beta-blockers, these interactions are easily overlooked in clinical practice."),
    ("The two experts agreed closely (kappa 0.846) but rated most cases one tier lower than the system, a systematic perspective gap attributable to the low base rate of serious ophthalmic\u2013systemic events and to clinical emphasis on beta-blockers.",
     "The two experts agreed closely (kappa 0.846). They rated most cases one tier lower than the system. This systematic perspective gap reflects the low base rate of serious ophthalmic\u2013systemic events and the clinical emphasis on beta-blockers."),
    # Introduction
    ("We present an ophthalmic DDI clinical decision-support system built on a deterministic, fully explainable three-layer cascade: an L1 rule engine of 40 citation-verified mechanism rules, an L2 drug-class matrix with absorption-scaled upgrades, and an L3 hard constraint that encodes ophthalmic systemic-absorption pharmacology.",
     "We present an ophthalmic DDI clinical decision-support system built on a deterministic, fully explainable three-layer cascade. The L1 rule engine contains 40 citation-verified mechanism rules. The L2 drug-class matrix applies absorption-scaled upgrades. The L3 hard constraint encodes ophthalmic systemic-absorption pharmacology."),
    ("It produces traceable risk grades (high, medium, or low) with matched rule IDs and evidence chains, requires zero LLM calls in the production path, shows zero variance across seeds, and completes inference in milliseconds.",
     "It produces traceable risk grades (high, medium, or low) with matched rule IDs and evidence chains. The production path requires zero LLM calls, shows zero variance across seeds, and completes inference in milliseconds."),
    ("Third, we disclose the validation limits transparently: the literature-derived gold labels share sources with the rules, only the procedurally frozen blind subset is independent in a procedural sense, and a two-expert clinical review reveals a systematic one-tier perspective gap between clinical prior and evidence-based grading.",
     "Third, we disclose the validation limits transparently. The literature-derived gold labels share sources with the rules. Only the procedurally frozen blind subset is independent in a procedural sense. A two-expert clinical review reveals a systematic one-tier perspective gap between clinical prior and evidence-based grading."),
    # Methods
    ("Evidence and gold labels were derived from multiple sources: (i) DDInter 2.0, a curated database of 302,516 DDI records, for severity levels and drug-pair evidence [3]; (ii) FDA prescribing labels for ophthalmic products (for example, Timoptic, Alphagan, Trusopt, Acular, and Betoptic); (iii) Stockley's Drug Interactions and the British National Formulary for mechanism-level annotations; (iv) peer-reviewed literature retrieved from PubMed; and (v) clinical guidelines.",
     "Evidence and gold labels were derived from multiple sources. DDInter 2.0, a curated database of 302,516 DDI records, provided severity levels and drug-pair evidence [3]. FDA prescribing labels for ophthalmic products (Timoptic, Alphagan, Trusopt, Acular, Betoptic) provided product-specific warnings. Stockley's Drug Interactions and the British National Formulary provided mechanism-level annotations. Peer-reviewed literature was retrieved from PubMed, and clinical guidelines were consulted for ophthalmic practice."),
    ("Rules are additionally scoped by drug class where class-matrix cells provide finer granularity, for example weak versus full-potency corticosteroids.",
     "Rules are additionally scoped by drug class where class-matrix cells provide finer granularity, for example weak versus full-potency corticosteroids."),
    ("An absorption-scaling step forces agents with low or very-low systemic absorption to low risk unless an upgrade condition applies; high or medium absorption preserves the cell level.",
     "An absorption-scaling step forces agents with low or very-low systemic absorption to low risk unless an upgrade condition applies. High or medium absorption preserves the cell level."),
    ("Gold labels share literature sources with the rules (homogeneous construction); this is disclosed and interpreted accordingly.",
     "Gold labels share literature sources with the rules (homogeneous construction). This limitation is disclosed and interpreted accordingly."),
    # Results
    ("The ophthalmic DDI decision-support system was built on a curated knowledge base of 113 ophthalmic topical agents and 232 systemic medications (Table 1), with 1,307 evidence chunks (all approved release, evidence levels A through E) and a LightRAG index over 1,307 documents.",
     "The ophthalmic DDI decision-support system was built on a curated knowledge base of 113 ophthalmic topical agents and 232 systemic medications (Table 1). It included 1,307 evidence chunks (all approved release, evidence levels A through E) and a LightRAG index over 1,307 documents."),
    ("Table 3 and Figure 2 summarize the four-method comparison (five seeds each; mean \u00b1 SD) on the L1 literature-consensus set, whose gold labels were derived independently of the system outputs (20 FDA-label, Stockley's, or BNF mechanism annotations; 40 procedurally frozen blind cases; 58 guideline cases).",
     "Table 3 and Figure 2 summarize the four-method comparison (five seeds each; mean \u00b1 SD) on the L1 literature-consensus set. Gold labels were derived independently of the system outputs: 20 FDA-label, Stockley's, or BNF mechanism annotations; 40 procedurally frozen blind cases; and 58 guideline cases."),
    ("The deterministic three-layer cascade achieved 0.915 four-level accuracy and a kappa of 0.870 on the L1 literature-consensus validation set (118 cases), outperforming three LLM baselines by a wide margin (0.415 to 0.741 accuracy), with zero variance across seeds and millisecond inference.",
     "The deterministic three-layer cascade achieved 0.915 four-level accuracy and a kappa of 0.870 on the L1 set (118 cases). It outperformed three LLM baselines by a wide margin (0.415 to 0.741 accuracy), with zero variance across seeds and millisecond inference."),
    ("All ten three-level disagreements occurred in the guideline subset and concerned judgment boundaries, including QT risk with low-absorption fluoroquinolones, CYP3A4 inhibition with low-absorption macrolides or azoles, weak-corticosteroid potency granularity, and anticholinergic overlap with tricyclic antidepressants.",
     "All ten three-level disagreements occurred in the guideline subset. They concerned judgment boundaries, including QT risk with low-absorption fluoroquinolones, CYP3A4 inhibition with low-absorption macrolides or azoles, weak-corticosteroid potency granularity, and anticholinergic overlap with tricyclic antidepressants."),
    ("On the 92-case audit set (DDInter severity levels stratified by absorption tier, with absorption-based correction), full_system reached 0.707 accuracy (kappa 0.489, specificity 0.955), outperforming pure_llm (0.630), lightrag (0.600), and naive_rag (0.535).",
     "On the 92-case audit set, full_system reached 0.707 accuracy (kappa 0.489, specificity 0.955). It outperformed pure_llm (0.630), lightrag (0.600), and naive_rag (0.535). The set was stratified by absorption tier, with absorption-based gold correction."),
    ("The disagreement was systematic: experts rated most cases one tier lower, consistent with their stated clinical prior that ophthalmic drops have limited systemic impact and are not routinely screened for systemic DDI.",
     "The disagreement was systematic. Experts rated most cases one tier lower, consistent with their stated clinical prior that ophthalmic drops have limited systemic impact and are not routinely screened for systemic DDI."),
    # Discussion
    ("The gradient full_system > lightrag > pure_llm > naive_rag was stable across all five seeds, and the procedurally frozen blind subset (n = 40) was classified with perfect accuracy.",
     "The gradient full_system > lightrag > pure_llm > naive_rag was stable across all five seeds. The procedurally frozen blind subset (n = 40) was classified with perfect accuracy."),
    ("Our system makes this ophthalmic pharmacokinetic factor an explicit, first-class modeling component: a systemic-absorption tier (high, medium, low, or very-low) is assigned to every ophthalmic agent, an absorption-scaling step forces low-absorption pairs to low risk unless a mechanism-based upgrade applies, and a hard-constraint layer encodes the absorption-first pharmacology.",
     "Our system makes this ophthalmic pharmacokinetic factor an explicit, first-class modeling component. A systemic-absorption tier (high, medium, low, or very-low) is assigned to every ophthalmic agent. An absorption-scaling step forces low-absorption pairs to low risk unless a mechanism-based upgrade applies. A hard-constraint layer encodes the absorption-first pharmacology."),
    ("The 1,933-pair DDInter audit, in which 75% of original high-risk pairs were downgraded and 77% of downgrades were attributable to low systemic absorption, quantifies precisely what a general-purpose database would over-alert on in this setting.",
     "In the 1,933-pair DDInter audit, 75% of original high-risk pairs were downgraded and 77% of downgrades were attributable to low systemic absorption. This quantifies what a general-purpose database would over-alert on in this setting."),
    ("Our system is deterministic (zero variance across seeds), auditable (every decision returns matched rule IDs, decision path, and evidence citations), and fast (about 2 ms per pair), while retaining the full mechanism vocabulary of the knowledge base.",
     "Our system is deterministic (zero variance across seeds) and auditable (every decision returns matched rule IDs, decision path, and evidence citations). It is also fast, about 2 ms per pair, while retaining the full mechanism vocabulary of the knowledge base."),
    ("Our system screens all 113 ophthalmic agents against 232 systemic drugs exhaustively, surfacing mechanism-based signals that clinicians may not spontaneously consider, including anticholinergic accumulation with tricyclic antidepressants, additive carbonic-anhydrase inhibition, CYP3A4-mediated exposure changes, and weak-corticosteroid potency boundaries.",
     "Our system screens all 113 ophthalmic agents against 232 systemic drugs exhaustively. It surfaces mechanism-based signals that clinicians may not spontaneously consider, including anticholinergic accumulation with tricyclic antidepressants, additive carbonic-anhydrase inhibition, CYP3A4-mediated exposure changes, and weak-corticosteroid potency boundaries."),
    ("Beyond absolute performance, we contribute a four-phase validation protocol with a procedurally frozen blind subset (SHA-locked), a third-party audit component (DDInter severity levels), a five-seed protocol separating deterministic and stochastic methods, and transparent reporting of homogeneous-construction and overlap limitations.",
     "Beyond absolute performance, we contribute a four-phase validation protocol. It includes a procedurally frozen blind subset (SHA-locked), a third-party audit component (DDInter severity levels), and a five-seed protocol separating deterministic and stochastic methods. Homogeneous-construction and overlap limitations are reported transparently."),
    ("This prevailing perception constitutes our main adoption barrier: a screening tool whose outputs sit one tier above clinical intuition will be treated as noise unless its mechanism-based justifications are presented transparently, which our traceable decision paths are designed to do.",
     "This prevailing perception constitutes our main adoption barrier. A screening tool whose outputs sit one tier above clinical intuition will be treated as noise unless its mechanism-based justifications are presented transparently. Our traceable decision paths are designed to do exactly that."),
    ("A substantial part of the rule layer is mechanism-derived: PubMed yielded few dedicated ophthalmic\u2013systemic interaction studies or case series, and the evidence base is populated largely by pharmacokinetic first principles, class-level pharmacology, and extrapolation from systemic data (1,307 curated chunks, but few ophthalmic-specific outcome studies).",
     "A substantial part of the rule layer is mechanism-derived. PubMed yielded few dedicated ophthalmic\u2013systemic interaction studies or case series. The evidence base is populated largely by pharmacokinetic first principles, class-level pharmacology, and extrapolation from systemic data (1,307 curated chunks, but few ophthalmic-specific outcome studies)."),
    ("To the extent that the true risk gradient clusters at the low end for most ophthalmic agents, an evidence-graded system may systematically over-grade relative to what clinical practice observes, and the clinical impact of the system is correspondingly bounded.",
     "If the true risk gradient clusters at the low end for most ophthalmic agents, an evidence-graded system may systematically over-grade relative to clinical practice. The clinical impact of the system is correspondingly bounded."),
    ("In addition, 78 of 118 L1 cases overlap the development-phase internal validation set by case identity, and no real human expert participated in gold construction; the two-expert review is the only human channel and shows the systematic one-tier perspective gap discussed above.",
     "In addition, 78 of 118 L1 cases overlap the development-phase internal validation set by case identity. No real human expert participated in gold construction. The two-expert review is the only human channel and shows the systematic one-tier perspective gap discussed above."),
    # Conclusion
    ("We developed an ophthalmic DDI decision-support system built on a deterministic, fully explainable three-layer cascade, consisting of 40 citation-verified rules, an absorption-scaled class matrix, and a hard-constraint layer encoding ophthalmic systemic-absorption pharmacology, grounded in 1,307 verified evidence chunks.",
     "We developed an ophthalmic DDI decision-support system built on a deterministic, fully explainable three-layer cascade. It consists of 40 citation-verified rules, an absorption-scaled class matrix, and a hard-constraint layer encoding ophthalmic systemic-absorption pharmacology, grounded in 1,307 verified evidence chunks."),
    ("Across 118 literature-consensus validation cases and a 92-case DDInter audit, the system outperformed three LLM baselines (accuracy 0.915 versus 0.475 to 0.741; 0.707 versus 0.535 to 0.630) with zero seed variance and complete output traceability, adding ophthalmic absorption scaling and systematic coverage that general-purpose databases and current LLM approaches lack.",
     "Across 118 literature-consensus validation cases and a 92-case DDInter audit, the system outperformed three LLM baselines (accuracy 0.915 versus 0.475 to 0.741; 0.707 versus 0.535 to 0.630). It showed zero seed variance and complete output traceability, adding ophthalmic absorption scaling and systematic coverage that general-purpose databases and current LLM approaches lack."),
    ("A two-expert clinical review confirmed high inter-rater reliability (kappa 0.846) and revealed a systematic one-tier perspective gap that we attribute to the low base rate of serious ophthalmic\u2013systemic events, the clinical emphasis on beta-blockers to the exclusion of other classes, and the scarcity of direct evidence.",
     "A two-expert clinical review confirmed high inter-rater reliability (kappa 0.846). It revealed a systematic one-tier perspective gap. We attribute this gap to the low base rate of serious ophthalmic\u2013systemic events, the clinical emphasis on beta-blockers, and the scarcity of direct evidence."),
    ("The system is best understood as a systematic, mechanism-based second reader that prevents overlooked interactions in a low-frequency risk space; its clinical value, calibration, and generalizability warrant prospective outcome-linked evaluation.",
     "The system is best understood as a systematic, mechanism-based second reader. It prevents overlooked interactions in a low-frequency risk space. Its clinical value, calibration, and generalizability warrant prospective outcome-linked evaluation."),
]

n_hit = 0
for old, new in REPL:
    if old in t:
        t = t.replace(old, new, 1)
        n_hit += 1
    else:
        print(f"NOT FOUND: {old[:60]}...")
P.write_text(t, encoding="utf-8")
print(f"split {n_hit}/{len(REPL)} sentences")

import re
body = " ".join(l for l in t.split("\n") if not l.startswith("#") and not l.startswith("[") and not l.startswith("doi:"))
t2 = re.sub(r"\*\*[^*]+\*\*\.", ". ", body)
sents = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", t2)
longs = [s for s in sents if len(s.split()) > 32]
print(f"remaining >32-word sentences: {len(longs)}")
