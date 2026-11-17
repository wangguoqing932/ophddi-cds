# -*- coding: utf-8 -*-
"""nature-polishing Part 1: Abstract + Introduction + Methods."""
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "outputs" / "paper" / "manuscript.en.md"

PART1 = '''## Abstract

**Background.** Ophthalmic topical medications can reach clinically meaningful systemic exposure, yet existing drug–drug interaction (DDI) screening tools lack ophthalmic-specific pharmacokinetic modeling. Outside a few well-known classes, such as non-selective beta-blockers, ophthalmic–systemic interactions are easily overlooked in clinical practice.

**Methods.** We developed a deterministic, fully explainable three-layer cascade consisting of 40 citation-verified rules, an absorption-scaled 20 × 37 drug-class matrix, and a hard-constraint layer that encodes ophthalmic systemic-absorption pharmacology. The system is grounded in 1,307 verified evidence chunks covering 113 ophthalmic agents and 232 systemic drugs. We evaluated four methods, the deterministic system and three LLM baselines (pure LLM, BM25 retrieval-augmented, LightRAG graph-augmented), over five seeds on an L1 literature-consensus set (118 cases) and a DDInter-derived audit set (92 cases). Two independent ophthalmologists reviewed 12 cases.

**Results.** On the L1 set, the deterministic system achieved 0.915 four-level accuracy (sensitivity 1.000; Cohen's kappa 0.870; zero seed variance), outperforming lightrag (0.741), pure_llm (0.475), and naive_rag (0.415). On the audit set it reached 0.707 (kappa 0.489). The two experts agreed closely (kappa 0.846) but rated most cases one tier lower than the system, a systematic perspective gap attributable to the low base rate of serious ophthalmic–systemic events and to clinical emphasis on beta-blockers.

**Conclusions.** An absorption-first deterministic cascade outperforms LLM baselines for ophthalmic DDI screening with full output traceability, complementing rather than overriding clinical judgment. Its clinical impact is bounded by the rarity of serious events, and prospective outcome-linked calibration is warranted.

## Introduction

Ophthalmic topical medications are among the most widely prescribed drugs worldwide, yet their systemic absorption is frequently underestimated in routine DDI screening. Although eye drops are assumed to act locally, several agents achieve clinically meaningful systemic exposure. Non-selective beta-blockers such as timolol reach plasma concentrations comparable to low oral doses through nasolacrimal drainage and mucosal absorption [1]. Severe systemic events are documented: topical timolol combined with verapamil can cause bradycardia and cardiogenic shock [2], and alpha-2 agonists can produce CNS depression. In elderly patients with polypharmacy, the accumulation of such additive effects is a recognized source of preventable harm [3].

General-purpose DDI databases, including DDInter, provide comprehensive pair-level severity ratings derived predominantly from systemic administration [3]. These resources are of limited direct utility for ophthalmic prescribing because they do not encode the decisive ophthalmic pharmacokinetic modifier, namely the magnitude of systemic absorption from topical administration. They also omit dose-route corrections derived from ophthalmic pharmacology. As a result, the same drug pair can be rated high-risk for oral administration while being clinically negligible for topical use, and clinicians lack a mechanism-level ophthalmic-specific screening tool.

Recent LLM approaches to clinical DDI screening offer flexibility but raise reliability concerns. Context-free models hallucinate interactions, and retrieval-augmented variants inherit the biases of their retrieval corpora. In our own evaluations, naive keyword retrieval (BM25) degraded accuracy below the context-free LLM baseline in this domain [4], while graph-based retrieval (LightRAG) provided measurable but incomplete gains [5]. Moreover, LLM outputs are non-deterministic, non-reproducible, and difficult to audit in a clinical context.

We present an ophthalmic DDI clinical decision-support system built on a deterministic, fully explainable three-layer cascade: an L1 rule engine of 40 citation-verified mechanism rules, an L2 drug-class matrix with absorption-scaled upgrades, and an L3 hard constraint that encodes ophthalmic systemic-absorption pharmacology. The system is grounded in a curated knowledge base of 1,307 verified evidence chunks (113 ophthalmic agents, 232 systemic agents). It produces traceable risk grades (high, medium, or low) with matched rule IDs and evidence chains, requires zero LLM calls in the production path, shows zero variance across seeds, and completes inference in milliseconds.

Our contributions are fourfold. First, we provide a reproducible, citation-verified rule engine for ophthalmic DDIs, including class-matrix cells and absorption scaling absent from general-purpose databases. Second, we report a four-phase evaluation protocol (rule consistency, internal validation, external DDInter audit, and independent validation) comparing the system against three LLM baselines over five seeds. Third, we disclose the validation limits transparently: the literature-derived gold labels share sources with the rules, only the procedurally frozen blind subset is independent in a procedural sense, and a two-expert clinical review reveals a systematic one-tier perspective gap between clinical prior and evidence-based grading. Fourth, we provide a downloadable, zero-configuration web interface for clinical and educational use.

## Methods

### Study design

We developed and evaluated a clinical decision-support system for DDIs between ophthalmic topical medications and systemic drugs. The system combines a deterministic, fully explainable rule cascade with a curated ophthalmic DDI knowledge base. Evaluation followed a four-phase protocol (rule consistency, internal validation, external audit, and independent validation), comparing the system against three LLM baselines across five random seeds.

### Data sources

Evidence and gold labels were derived from multiple sources: (i) DDInter 2.0, a curated database of 302,516 DDI records, for severity levels and drug-pair evidence [3]; (ii) FDA prescribing labels for ophthalmic products (for example, Timoptic, Alphagan, Trusopt, Acular, and Betoptic); (iii) Stockley's Drug Interactions and the British National Formulary for mechanism-level annotations; (iv) peer-reviewed literature retrieved from PubMed; and (v) clinical guidelines. All 1,307 evidence chunks were filtered to approved-release status and graded by evidence level (A, regulatory; B, meta-analysis; C, original study; D, in vitro or animal; E, mechanism inference).

### System architecture

The production system (full_system) is a three-layer deterministic cascade with zero LLM calls.

**L1 rule engine.** Forty mechanism rules define DDI risk, including additive beta-blockade, beta-blocker–calcium-channel-blocker additive effects, additive alpha-2 CNS depression, CYP3A4 induction or inhibition, and QT prolongation risk with low-absorption fluoroquinolones. Each rule is defined by entity-flag predicates with match-all or match-any semantics, and the highest-severity hit is retained (MAX-MATCH). Every rule carries at least one citation verified through a three-source cross-check (Crossref, OpenAlex, PubMed) with mandatory retraction screening. Rules are additionally scoped by drug class where class-matrix cells provide finer granularity, for example weak versus full-potency corticosteroids.

**L2 class matrix.** A 20 (ophthalmic) × 37 (systemic) drug-class matrix defines 82 cell-level risks. Four upgrade rules require both a class match and specific absorption or selectivity flags, for example a non-selective beta-blocker with high systemic absorption. An absorption-scaling step forces agents with low or very-low systemic absorption to low risk unless an upgrade condition applies; high or medium absorption preserves the cell level.

**L3 G19 hard constraint.** Low or very-low absorption with no rule hit and no matrix signal yields low risk. Otherwise the default is low with a documented decision path.

Drug-class mapping (113 ophthalmic agents, 232 systemic agents) was built from ATC codes, DrugBank records, and manual pharmacologic review. Ophthalmic systemic-absorption tiers (high, medium, low, or very-low) were assigned from pharmacokinetic sources, including nasolacrimal-drainage bioavailability for timolol, atropine, and dexamethasone.

### Knowledge base and retrieval

The evidence base (1,307 chunks) was embedded with a 2048-dimensional Doubao embedding model and indexed with LightRAG [5] (working directory data/processed/lightrag_index; 1,307 documents, 1,627 entities, 1,836 relations). Index freshness was verified against rule and evidence fingerprints. Retrieval baselines used BM25 (Best Matching 25) [4] over the same evidence chunks.

### Validation datasets

**L1 literature-consensus validation set (118 cases).** Gold labels were constructed independently of system outputs: 20 mechanism annotations from FDA labels, Stockley's, or the BNF; 40 procedurally frozen blind cases (SHA-256 locked before evaluation); and 58 guideline-sourced cases. Gold labels share literature sources with the rules (homogeneous construction); this is disclosed and interpreted accordingly.

**DDInter audit set (92 cases).** The set was a stratified random sample by absorption tier and DDInter severity, with absorption-based gold correction (42 of 92 cases downgraded to low). DDInter severity levels provide the only third-party component of the gold.

**Development set.** A development set (200 cases, DDInter-derived) and an internal validation set (78 cases) were used for rule-consistency and development-phase gates only.

### Baselines and evaluation protocol

Four methods were compared: pure_llm (single LLM call, no context), naive_rag (BM25 retrieval plus LLM), lightrag (LightRAG knowledge-graph context plus LLM), and full_system (deterministic cascade). LLM baselines used DeepSeek-chat through the OpenAI-compatible API (temperature 0 for seed 0; 0.3, 0.6, 0.9, and 1.2 for seeds 1 through 4; maximum 10 tokens). Five seeds × four methods × four datasets produced 9,600 prediction rows with zero API failures; full_system is deterministic and therefore identical across seeds. Metrics were four-level exact accuracy (Acc4), high-risk sensitivity and specificity, high-risk F1, and Cohen's kappa, reported as mean ± SD over five seeds.

### Statistical analysis

Cohen's kappa [6] was computed as (observed agreement − expected agreement) / (1 − expected agreement) on the four-level confusion matrix. Kappa interpretation followed Landis and Koch [7]. No significance testing between methods is reported because the deterministic method has zero variance; effect sizes are given as absolute differences in Acc4 and kappa.

### Expert review

Two independent ophthalmologists, blinded to system outputs, reviewed 12 representative cases covering errata confirmations, upgrade disputes, downgrade confirmations, potency granularity, and a typical case. Each expert recorded a three-level risk judgment (high, medium, or low) per case. Inter-rater reliability and expert–system agreement were summarized with Cohen's kappa.

### Software and reproducibility

The system is implemented in Python 3.11 (package ophthalmic_ddi_cds_agent). Code, data, evaluation artifacts, and a downloadable release package, including a zero-configuration local web interface, are provided as supplementary material. All evaluation scripts, seed schedules, and gold files are version-controlled, with SHA-256 fingerprints recorded for the engine, rules, evidence, and index.

'''


def main() -> None:
    old = P.read_text(encoding="utf-8")
    idx_start = old.find("## Abstract")
    idx_end = old.find("## Results")
    assert idx_start > 0 and idx_end > idx_start
    P.write_text(old[:idx_start] + PART1 + old[idx_end:], encoding="utf-8")
    print("Part 1 (Abstract/Introduction/Methods) rewritten")


if __name__ == "__main__":
    main()
