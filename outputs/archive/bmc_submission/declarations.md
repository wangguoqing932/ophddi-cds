# Declarations

### Ethics approval and consent to participate

This study used only publicly available secondary data: the DDInter severity tables, published drug labels, DrugBank records and the peer-reviewed literature. No human participants, patient-level data, human tissue, biological specimens or clinical interventions were involved, and no identifiable information was collected. Under the Declaration of Helsinki and the Chinese Measures for Ethical Review of Life Science and Medical Research Involving Humans, secondary analysis of published data does not constitute human-subjects research requiring ethics committee review, and the study was therefore exempt from ethics approval for the retrospective data-analysis and software-development components.

The only human involvement was a professional-opinion exercise: two ophthalmologists, both clinicians from the Department of Ophthalmology of the First Affiliated Hospital of Xinjiang Medical University, independently rated 12 hypothetical drug-pair vignettes constructed by the study team. The vignettes contained no patient data and no identifiable information; the experts provided their ratings as professional opinion and consented to their anonymised ratings being used in research and publication. One of the experts was a member of the research team of a separately approved study at the same department (ethics approval K202509-29, "Preliminary study of a mobile-device-based method for refractive error detection"), which is the source of the institutional link between that approval and the present work; K202509-29 does not itself cover this study. The document is included in the supplementary material only to evidence that relationship, and we ask the editor to treat this study as exempt rather than as covered by that approval.

The system is a research decision-support tool and is not intended to replace clinical judgment (Section 2.6).

### Consent for publication

Not applicable. This study did not involve data from any individual person.

### Availability of data and materials

All datasets supporting the conclusions of this article are deposited in a public repository and are also included as additional files.

**Repository.** https://github.com/wangguoqing932/ophddi-cds (release tag `v1.1-revision3`, archived at DOI {DOI}; accessible without an account). The deposit contains the entity registries (113 ophthalmic, 232 systemic agents) and the 1,307-chunk evidence base; all gold files with case-level provenance (L1 118 cases, DDInter audit 92 cases, development 200 cases, external 70 cases, plus the two development-gate sets); the 12-case expert ratings together with the review instrument and scanned questionnaires; the complete prediction files (9,600 rows, covering 4 methods x 5 temperature conditions x 4 datasets) and the evaluation and statistics scripts; the exact prompt templates; the DDInter severity tables used for the registry-scale audit; a per-agent absorption tier table with a source column for each agent; the path-attribution audit reporting which layer produced each grade; and SHA-256 fingerprints for the engine, rules and gold versions. The deterministic cascade requires no API key or network access, so the pipeline can be run end to end from the deposit; re-running the LLM baselines requires credentials for the model API.

**Software.** Project name: OphDDI-CDS (Python package ophthalmic_ddi_cds_agent). Project home page: https://github.com/wangguoqing932/ophddi-cds. Archived version: the release corresponding to this manuscript is tagged `v1.1-revision3` and is archived at DOI {DOI} (Zenodo). The archive contains the full source, configurations, gold sets, 9,600 prediction rows, the 3,150 reasoning-model responses, the statistics module and every audit output, so the reported figures can be regenerated without network access. Operating system(s): platform independent. Programming language: Python 3.11. Other requirements: Python 3.10 or later, with dependencies pinned in `pyproject.toml`. Licence: Apache-2.0 (code) and CC BY 4.0 (original data). The bundled DDInter severity tables are third-party data and remain under DDInter's CC BY-NC-SA 4.0 terms; they are included for research reproducibility only, and reuse is subject to those terms (see the component-licensing section of the repository LICENSE).

The repository contains the production screening engine, the curated knowledge base, the rule-citation verification tooling and the evaluation scripts, together with a synthetic demonstration dataset. The deterministic cascade described in this paper makes no LLM calls and requires no credential or network access, so the pipeline can be executed end to end with a single command (`python scripts/demo_pipeline.py`), which reproduces the expected risk level for 25 bundled mock pairs covering all three decision paths and the unknown-drug fail-safe behaviour. A test suite (`pytest tests/`, 34 passing, 1 skipped) verifies the registry, rules and citation-verification layers.

### Competing interests

The authors declare that the research was conducted in the absence of any commercial or financial relationships that could be construed as a potential conflict of interest.

### Funding

This study was supported by the Natural Science Foundation of Xinjiang Uygur Autonomous Region, China (Key Project No. 2022D01D68).

### Authors' contributions

Wang G: Conceptualization, Methodology, Software, Formal analysis, Data curation, Visualization, Writing - original draft. Hu L: Clinical input, Data interpretation, Writing - review & editing. Wang S: Clinical input, Data interpretation, Writing - review & editing. Yi X: Conceptualization, Supervision, Project administration, Funding acquisition, Resources, Writing - review & editing. All authors contributed to the article and approved the submitted version.

### Acknowledgements

Not applicable.

### Generative AI

Generative AI tools were used during this research and manuscript preparation, with full author review and responsibility. DeepSeek-chat (deepseek.ai) was used for LLM-baseline evaluations, for literature-assisted drafting, and as an assistive tool in knowledge-engineering tasks, including registry curation, evidence grading, and gold-label annotation; Zhipu GLM-4.6V was used for visual verification of scanned expert questionnaires and figures. Figure 1 (system architecture schematic) was created with an AI image-generation tool from a prompt defined by the authors (prompt archived in the supplementary material, figure_prompts.md); all quantitative figures (Figures 2–5) were generated directly from system outputs with Matplotlib. All AI-assisted content was reviewed and validated by the authors, who take full responsibility for the content of this manuscript. The authors disclose that no human expert participated in gold-label construction; the 12-case expert assessment is the sole human validation channel. For clarity about the "T1 expert" referred to in the deposited design files: that label denotes the clinical opinion recorded in an earlier, separately conducted exercise by a member of the research team of the approved study cited in the Ethics statement, used only to phrase the questionnaire vignettes and to cross-check mechanism plausibility for R02 and R12. No human expert assigned any gold label in this study; every gold label is the study team's own annotation from published sources, and the T1 comparison is reported in the deposit as provenance for how the vignettes were written, not as a source of gold.
