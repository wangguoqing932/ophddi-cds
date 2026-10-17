# 眼科药物相互作用知识库与临床决策支持系统（ophthalmic-ddi-cds）

**眼科药物相互作用知识库与临床决策支持系统** — A pharmacodynamic, pharmacokinetic, systemic_absorption rule-based decision support framework for screening **眼科局部用药与全身系统用药的药物相互作用（DDI）筛查与临床决策支持** in 合并心血管疾病, 合并糖尿病, 合并呼吸系统疾病, 合并精神神经系统疾病, 老年多药联用（≥65岁）, 肝肾功能不全, with a focus on 覆盖 113 种眼科局部用药与 232 种全身系统用药的全面的DDI知识图谱与CDSS系统，涵盖药效学、药代动力学与全身吸收后效应三类机制，附带全身吸收率分级与证据等级标注.

This project reuses the methodology skeleton of **TongYuan** (FDI screening, *Nutrients* submission) and applies it to a new domain: 眼科局部用药 × 全身系统用药 combinations.

## Project Status

✅ **Execution complete; writer stage in progress (last updated 2026-08-09).**

| Phase | Status | Key deliverables |
|---|---|---|
| Phase 0 | ✅ complete | Env + package skeleton + tests (34 passed / 1 skipped) |
| Phase 1 | ✅ complete | Registries: 113 ophthalmic agents × 232 systemic drugs, DrugBank/PubMed/RxNorm verified |
| Phase 2 | ✅ complete | Evidence base: 1,307 approved chunks (A=53, B=180, C=187, D=84, E=244) |
| Phase 3 | ✅ complete | 40 rules + 3 patient factors, citation verification pass (Crossref/OpenAlex/PubMed) |
| Phase 4 | ✅ complete | LightRAG index (1,307 docs), freshness verified |
| Phase 5 | ✅ complete | Validation: L1 (118) acc 0.907 (107/118) / κ 0.857; frozen blind-40 39/40 (36/40 under pre-errata labels); DDInter audit (92) 0.674 (34/62 on third-party-only subset); 5-condition × 4-method run (9,600 predictions); 2-expert review (12 cases, inter-rater κ 0.840 — see manuscript §3.8 for provenance caveats) |
| Phase 6 | ✅ complete | Streamlit app (3 tabs) + demo cases |
| Writer (7) | 🔄 in progress | Manuscript, 5 figures, 4 tables, references, cover letter, submission package → `outputs/paper/`, `outputs/submission/` |

Authoritative gate status lives in `.executor/progress.json` and `.medical-agent/state.json`.
Target journal: **Frontiers in Pharmacology** (submission package: `outputs/submission/frontiers_submission.zip`).

## Quick Navigation

| Document | Purpose |
|---|---|
| [PLAN.md](PLAN.md) | Master execution plan (8 phases, task list, subagent strategy, timeline) |
| `.planner.config.json` | Phase 1 investigation output (input to scaffold) |
| `src/ophthalmic_ddi_cds_agent/` | Core source code (to be migrated from TongYuan) |
| `configs/rules.yaml` | Rule engine configuration (to be authored) |
| `data/seed/` | Knowledge base: entities_a.csv, entities_b.csv, evidence_chunks.jsonl (to be built) |

## Differentiation from Reference Project

| Dimension | Reference (TongYuan) | This Project |
|---|---|---|
| Entity A | food | 眼科局部用药 |
| Entity B | drug | 全身系统用药 |
| Interaction type | FDI | pharmacodynamic, pharmacokinetic, systemic_absorption |
| Rules | 15 | 12 |
| Data sources | FDA + USDA + LiverTox | DrugBank, PubMed, FDA DailyMed, DDInter |
| Target journal | Nutrients | Digital Medicine |

## Methodology Pipeline

```text
User input (眼科局部用药 + 全身系统用药 + patient factors)
  → entity normalization
  → rule-based screening (12 rules)
  → graph-organized evidence retrieval (LightRAG)
  → evidence compression (top-k, char limit)
  → structured safety report
  → expert-review export / evaluation
```

## Setup (conda env per project, Chinese mirrors pre-configured)

The default flow creates a **conda env named after this project** (`ophthalmic-ddi-cds`) and installs all deps there.

```bash
python scripts/setup_environment.py --project-root . --mirror cn
conda activate ophthalmic-ddi-cds
```

This will:
- `conda create -n ophthalmic-ddi-cds python=3.11 -y` if the env doesn't exist (idempotent)
- Install `[dev, llm, lightrag, streamlit]` extras from `pyproject.toml`
- Configure Tsinghua PyPI / TUNA conda / hf-mirror.com mirrors
- Prompt for `DEEPSEEK_API_KEY` (chat) and `ARK_DOUBAO_API_KEY` (火山方舟 embedding) on first run

Alternatives:

```bash
# Different Python version
python scripts/setup_environment.py --project-root . --mirror cn --python 3.12

# Non-interactive (CI / scripted): pre-fill keys in .env first
python scripts/setup_environment.py --project-root . --mirror cn --non-interactive

# Fallback to local .venv if conda is unavailable
python scripts/setup_environment.py --project-root . --mirror cn --env-mode venv
```

Later sessions inside this project can re-discover the env via:

```bash
python C:/Users/heyb1/.claude/skills/medical-agent-planner/scripts/conda_helper.py discover --project-root .
```

## Execution Entry Point

The full development plan is in [PLAN.md](PLAN.md). To regenerate all artifacts from scratch:

```bash
# 1. Build knowledge base
python scripts/build_entity_a_registry.py
python scripts/build_entity_b_registry.py
python scripts/build_evidence_base.py

# 2. Fetch real evidence (needs NCBI + LLM keys in .env)
python scripts/fetch_pubmed.py --max-pairs 40
python scripts/build_real_evidence.py

# 3. Build validation sets + run baselines + evaluate
python scripts/generate_cases.py --target 400
python scripts/run_baselines.py
python scripts/run_multiseed.py --seeds 5
python scripts/evaluate.py

# 4. Generate figures/tables
python scripts/generate_paper_figures.py
python scripts/generate_paper_tables.py
```

## Interactive Demo (Streamlit)

```bash
pip install -e ".[streamlit]"
streamlit run app/streamlit_app.py
```

Then open http://localhost:8501.

> ⚠️ The demo is for clinical decision support only and does not replace clinician or pharmacist judgement.

## Target Output

- Reproducible Python package with ~80% code reuse from TongYuan
- Validated 眼科局部用药与全身系统用药的药物相互作用（DDI）筛查与临床决策支持 screening system (4-phase validation)
- Manuscript submitted to *Digital Medicine* (or fallback journal)

## License

For peer review and academic reproducibility. All data derived from publicly available sources.
