# -*- coding: utf-8 -*-
"""build_supplementary.py — 重建补充材料，修正编号体系并补齐缺失项。

回应审稿人意见 9：原先所有补充内容共用一个 S1-S6 序列，导致 S3 内部又出现
Table S1-S6，稿件引用因此系统性错位。改为两级独立编号：

    Supplementary Text S1..S7    叙述性章节
    Supplementary Table S1..S8   表格

同时补齐审稿人指出缺失的四项：
    - 逐药吸收分级表（原被引用但不存在）
    - 评估 prompts（原被当作 Text S4，实为图注）
    - TRIPOD-AI 检查表（原被当作 Text S6，实为缩略语）
    - L1 十例分歧的药理理由表（原被当作 Table S1，实为注册表摘要）
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPP = ROOT / "outputs" / "deliverables" / "supplementary_files" / "Supplementary_Material.md"
FIGLEGENDS = ROOT / "outputs" / "deliverables" / "supplementary_files" / "figure_legends.md"

L1_RATIONALE = {
    "C04": "NSAID-anticoagulant bleeding risk graded medium after the flurbiprofen tier was corrected to low (0.03% formulation); the frozen gold retains the systemic-route high (additive_nsaid_bleeding, low_abs_anticoagulant)",
    "G106": "Anticholinergic burden with tricyclic antidepressant (expert-consensus matrix cell = high; guideline gold conservative at medium)",
    "G108": "Weak-corticosteroid potency granularity (rimexolone intermediate IOP effect; class-matrix cell coarse)",
    "G113": "Ophthalmic fluoroquinolone QT risk: low-absorption design decision vs guideline gold medium",
    "G114": "Ophthalmic fluoroquinolone QT risk: low-absorption design decision vs guideline gold medium",
    "G124": "Dexamethasone CYP3A4 induction to medium (mechanism genuine; guideline gold low)",
    "G131": "Macrolide CYP3A4 inhibition with low-absorption ophthalmic erythromycin vs guideline gold medium",
    "G132": "Macrolide CYP3A4 inhibition with low-absorption azithromycin vs guideline gold medium",
    "G133": "Azole CYP3A4 inhibition with low-absorption voriconazole vs guideline gold medium",
    "G134": "Azole CYP3A4 inhibition with low-absorption fluconazole vs guideline gold medium",
    "G139": "Combination corticosteroid x warfarin (INR fluctuation risk vs errata-corrected gold)",
}


def l1_disagreements() -> list[dict]:
    f = ROOT / "outputs" / "multiseed_per_dataset" / "blind_l1__seed0.jsonl"
    rows = []
    for line in f.open(encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["method"] == "full_system" and r["predicted"] != r["gold_risk"]:
            rows.append(r)
    return rows


def tier_rows() -> list[tuple]:
    src = ROOT / "data" / "seed" / "entities_a.csv"
    out = []
    for r in csv.DictReader(src.open(encoding="utf-8-sig")):
        flags = [x.strip() for x in (r.get("flags") or "").split("|") if x.strip()]
        tier = next((x for x in flags if x.startswith("systemic_absorption_")
                     or x == "minimal_systemic_absorption"), "")
        out.append((r.get("topical_ophthalmic_medications_id", ""), r.get("primary_name", ""),
                    r.get("category", ""), tier or "(no tier)", r.get("evidence_sources", "")))
    return out


def main() -> int:
    # 优先从 .bak（保持原始编号 ## S1. … ## S6. 的副本）读取，保证脚本可重复运行；
    # .bak 缺失时回退到当前已重编号的 SUPP（## Supplementary Text S1.…），按新编号取块，
    # 表格块以下一个 "**Supplementary Table" 为界。两种输入都只读，不改写。
    src = SUPP.with_suffix(".md.bak")
    if src.exists():
        old = src.read_text(encoding="utf-8")

        def block(start: str, end: str | None) -> str:
            i = old.find(start)
            if i < 0:
                return ""
            j = old.find(end, i) if end else len(old)
            return old[i:j if j > 0 else len(old)]

        s1 = block("## S1. Evidence base summary", "## S2.")
        s2 = block("## S2. Rule citation verification", "## S3.")
        s5 = block("## S5. Evaluation reproducibility", "## S6.")
        s6 = block("## S6. Abbreviations", "## Supplementary Tables")
        t_registry = block("| entity_type | count | with_flags | with_drugbank_ids |", "**Table S2.**")
        t_rules = block("| rule_id | severity | risk_type |", "**Table S3.**")
        t_perf = block("| dataset_id | method | n | sensitivity_high |", "**Table S4.**")
        t_dist = block("| dataset_id | gold_level | count | percentage |", "**Table S5.**")
    else:
        cur = SUPP.read_text(encoding="utf-8")

        def block2(start: str, end: str | None) -> str:
            i = cur.find(start)
            if i < 0:
                return ""
            j = cur.find(end, i) if end else len(cur)
            return cur[i:j if j > 0 else len(cur)]

        s1 = block2("## Supplementary Text S1. Evidence base summary",
                    "## Supplementary Text S2.")
        s2 = block2("## Supplementary Text S2. Rule citation verification",
                    "## Supplementary Text S3.")
        s5 = block2("## Supplementary Text S5. Evaluation reproducibility",
                    "## Supplementary Text S6.")
        s6 = block2("## Supplementary Text S7. Abbreviations", "## Supplementary Tables")
        def clean(s: str) -> str:
            # 上一轮输出的尾部可能残留孤立的 "## Supplementary Tables" 标题，剥掉
            return "\n".join(l for l in s.splitlines()
                             if l.strip() != "## Supplementary Tables").rstrip() + "\n"

        t_registry = clean(block2("| entity_type | count | with_flags | with_drugbank_ids |",
                                  "**Supplementary Table"))
        t_rules = clean(block2("| rule_id | severity | risk_type |", "**Supplementary Table"))
        t_perf = clean(block2("| dataset_id | method | n | sensitivity_high |",
                              "**Supplementary Table"))
        t_dist = clean(block2("| dataset_id | gold_level | count | percentage |",
                              "**Supplementary Table"))

    figleg = FIGLEGENDS.read_text(encoding="utf-8") if FIGLEGENDS.exists() else ""
    # Table S3 改为读取单一来源文件（含 engine grade / system shown / L1 case 列），
    # 不再从 .bak 旧表拼接——旧表缺列且 R03 曾记错。
    s3_src = ROOT / "outputs" / "paper" / "supplementary" / "S3_expert_cases.md"
    if s3_src.exists():
        t_expert = "\n".join(l for l in s3_src.read_text(encoding="utf-8").splitlines()
                             if not l.startswith("# "))
    else:
        t_expert = ""

    dis = l1_disagreements()
    tiers = tier_rows()

    parts = ["# Supplementary Material", "",
             "Two independent numbering series are used. Prose sections are **Supplementary Text S1–S7**; "
             "tables are **Supplementary Table S1–S8**. Earlier versions shared a single sequence, which "
             "made cross-references from the manuscript ambiguous; the numbering below is self-consistent.",
             ""]

    # ── Text S1 ──
    parts += ["## Supplementary Text S1. Evidence base summary", "",
              "- Total verified evidence chunks: 1,307 (all approved release)",
              "- Evidence levels: A (regulatory) 53, B (meta-analysis) 191, C (original study) 215, "
              "D (in vitro or animal) 584, E (mechanism inference) 264",
              "- Ophthalmic agents: 113; systemic medications: 232", ""]

    # ── Text S2（修正表述）──
    parts += ["## Supplementary Text S2. Rule citation verification", "",
              "The verification report covers **8 manifest items spanning 7 distinct DOIs**; of these, "
              "**three rules resolve to a verified literature citation**: `additive_beta_blockade`, "
              "`beta_blocker_ccb_additive` and `beta_blocker_digoxin_additive`.", "",
              "The 40 rules carry 53 source records in total, of which 41 are DrugBank entries, "
              "7 regulatory label records, 2 DOIs, 2 DDInter pair annotations and 1 a PubMed citation. "
              "DrugBank and label records were **not** independently re-verified against external "
              "sources, so the earlier description of all 40 rules as \"citation-verified\" was "
              "overstated and has been corrected in the manuscript.", "",
              "Other properties of the gate: 43 policy entries (40 rules + 3 patient-factor policies); "
              "0 policy errors; retraction screening identified no retracted references. The report is "
              "bound to a SHA-256 of `configs/rules.yaml`, so any later edit to the rules invalidates it. "
              "The report itself is deposited as `data/evidence/citation_verification_report.json`.", "",
              "**Known provenance gap.** `beta_blocker_digoxin_additive` cites a study of additive "
              "topical-plus-systemic beta-blockade (Schuman 2000, PMID 10857839) rather than a "
              "digoxin-specific source, and it grades as high a pair whose DDInter annotation records "
              "as moderate. The conservative high grade is retained, and the gap is recorded here.", ""]

    # ── Text S3（新增：prompts）──
    parts += ["## Supplementary Text S3. Evaluation prompts", "",
              "Transcribed from `scripts/run_multiseed_per_dataset.py`, which is authoritative. "
              "The same file is deposited as `configs/prompts.yaml`.", "",
              "**Model and decoding.** `deepseek-chat`; `max_tokens = 10`; five temperature conditions "
              "(0.0, 0.3, 0.6, 0.9, 1.2). The 10-token cap forces a one-word answer and precludes any "
              "reasoning or justification; this bound on the comparison is stated in the manuscript "
              "(Section 2.4) and in the deposit README.", "",
              "**System prompt (all three LLM methods).**", "",
              "```",
              "You are a clinical pharmacologist assessing ophthalmic drug-drug interaction risk.",
              "",
              "Classify the interaction risk as: low, medium, or high.",
              "Definitions:",
              "- low: negligible clinical significance at ophthalmic doses",
              "- medium: potential interaction requiring monitoring or dose adjustment",
              "- high: clinically significant interaction; may require avoidance or strict monitoring",
              "",
              "Consider ophthalmic pharmacokinetics (systemic absorption from eye drops is often <10% of oral dose,",
              "but some drugs like timolol, atropine, dexamethasone reach >50%).",
              "",
              "Reply with EXACTLY ONE WORD: low, medium, or high. No explanation.",
              "```", "",
              "**User prompt — `pure_llm`** (no retrieved evidence):", "",
              "```",
              "Drug pair: ophthalmic {oph} (eye drops) + systemic {sysd} (oral/IV)",
              "Risk level:",
              "```", "",
              "**User prompt — `naive_rag`** (BM25 retrieval over the same 1,307 evidence chunks: "
              "`BM25Okapi`, k1 = 1.5, b = 0.75, top-k = 3, each passage truncated to 400 characters):", "",
              "```",
              "Evidence:",
              "{retrieved_passages}",
              "",
              "Drug pair: ophthalmic {oph} (eye drops) + systemic {sysd} (oral/IV)",
              "Risk level:",
              "```", "",
              "**User prompt — `lightrag`**: identical structure, with the context block generated by "
              "`PreciseKG.full_kg_context()` rather than by a query to the LightRAG vector index. The "
              "baseline is named `lightrag` for continuity with earlier protocol versions; the manuscript "
              "states this limitation explicitly (Section 2.4).", "",
              "**Parsing.** Lowercase the response; `high` if it contains \"high\"; else `medium` if it "
              "contains \"medium\" or \"moderate\"; else `low` if it contains \"low\"; otherwise `unknown`. "
              "No non-conforming output occurred on the L1 or audit sets.", "",
              "**Reasoning-model re-run (reported in Section 3.6 and Table 3 of the manuscript).** "
              "The three LLM baselines were re-run under an adequate output budget with a reasoning "
              "model. All parameters, as requested:", "",
              "| item | value |",
              "|---|---|",
              "| provider / endpoint | Zhipu coding-plan endpoint `https://open.bigmodel.cn/api/coding/paas/v4` |",
              "| model identifier | `glm-5.3-flash` |",
              "| temperature | 0.0 (fixed; five repeated samples per case) |",
              "| max_tokens | 3000 |",
              "| reasoning effort | not set — the request carries only `max_tokens` and `temperature`, so the endpoint default applied |",
              "| reasoning tokens | count against the 3000-token budget (`reasoning_content` is emitted before `content`) |",
              "| truncated responses | 0 of 3,150 (completion_tokens never reached max_tokens) |",
              "| vote resolution | majority over the five samples; every case had at least three concordant samples, so no tie arose |",
              "| per-sample parsing | exact match first, then substring `high` > `medium`/`moderate` > `low`, else `unknown`; no sample returned `unknown` |",
              "| run dates | 23-24 September 2026 |",
              "| raw responses | deposited in full: `data/predictions/glm53_baselines/predictions.jsonl` (3,150 rows with token usage) |",
              "| run script | `scripts/rerun_glm53_baselines.py` |", "",
              "Single-model caveat: this is one commercial reasoning model at one endpoint, and the "
              "endpoint exposes no checkpoint revision. The finding that reasoning models adopt a "
              "conservative rarely-high-risk policy is therefore a property of this model at this "
              "budget, not a claim about reasoning models in general. The deterministic cascade "
              "makes no model call and is identical under both settings.", ""]

    # ── Text S4 图注 ──
    fl = figleg.strip()
    fl = re.sub(r"^#+\s*Figure Legends[^\n]*\n", "", fl, count=1)
    fl = "## Supplementary Text S4. Figure legends\n\n" + fl.lstrip()
    # 修正 Fig 1 图注中的矩阵计数
    fl = fl.replace("the L2 class-matrix layer (20 ophthalmic × 37 systemic drug classes, 82 cells with "
                    "absorption-scaled upgrades, `configs/class_matrix.yaml`)",
                    "the L2 class-matrix layer (21 ophthalmic row keys and 40 systemic column keys, "
                    "34 columns in use, 104 cells with explicit levels and absorption-scaled upgrades, "
                    "`configs/class_matrix.yaml`)")
    fl = fl.replace("(40 citation-verified mechanism rules plus 3 patient-factor policies",
                    "(40 mechanism rules plus 3 patient-factor policies, each carrying at least one "
                    "source record")
    parts += [fl, ""]

    # ── Text S5 可复现性 ──
    s5b = s5.replace("## S5. Evaluation reproducibility",
                     "## Supplementary Text S5. Evaluation reproducibility")
    s5b = s5b.replace("- Engine/rules/evidence/index SHA-256 fingerprints recorded in the project log",
                      "- SHA-256 fingerprints are defined over **LF-normalised content**; convert CRLF to LF "
                      "before hashing or Windows and Linux checkouts will differ. Evaluated rules version: "
                      "`2afabaad81161c40` (CRLF as deposited)")
    parts += [s5b.strip(), ""]

    # ── Text S6（新增：TRIPOD-AI）──
    parts += ["## Supplementary Text S6. TRIPOD-AI checklist", "",
              "The manuscript is a system-development report for a rule-based decision-support tool, not "
              "a statistical prediction model. TRIPOD+AI items are answered where applicable; items that "
              "concern model fitting, tuning or updating are marked not applicable and the reason is given.", "",
              "| Item | Status | Where addressed |",
              "|---|---|---|",
              "| Title and abstract: identify the study as developing/evaluating a model | Addressed | Title; Abstract |",
              "| Background: rationale and intended use | Addressed | Section 1; Section 2.6 |",
              "| Data sources and selection | Addressed | Section 2.1; Section 2.3 |",
              "| Outcome / target definition | Addressed | Section 2.3 (gold construction, three-level risk) |",
              "| Predictors | Addressed | Section 2.2 (entity-flag predicates, matrix cells) |",
              "| Sample size | Addressed | Section 2.3; 118 + 92 + 200 + 70 cases |",
              "| Missing data handling | Not applicable | Rule engine requires complete registry entries; out-of-coverage pairs are rejected, not imputed (Section 2.2) |",
              "| Model development | Addressed | Section 2.2; rules and matrix are author-curated, not fitted |",
              "| Model fitting / hyperparameter tuning | Not applicable | No parameters are estimated from data |",
              "| Model updating | Not applicable | No updating procedure exists; flagged in Section 4.5 as future work |",
              "| Performance measures | Addressed | Section 2.4 (Acc3, sensitivity, specificity, F1, kappa) |",
              "| Internal validation | Addressed | Section 3.3; with explicit disclosure of gold homogeneity |",
              "| External validation | Partially addressed | Section 3.5 (semi-independent DDInter audit; third-party-only subset reported) |",
              "| Calibration | Not applicable | The output is a three-level grade, not a probability |",
              "| Clinical utility / decision-curve analysis | Not addressed | Prospective, outcome-linked evaluation is identified as required future work (Sections 4.4, 4.5) |",
              "| Fairness / subgroup analysis | Not addressed | No patient-level data; flagged as a limitation |",
              "| Limitations | Addressed | Sections 3.8 and 4.4 |",
              "| Data and code availability | Addressed | Availability of data and materials; public repository |",
              "| Registration / protocol | Not applicable | No prospective protocol; no trial registration |", ""]

    # ── Text S7 缩略语 ──
    s7 = s6.replace("## S6. Abbreviations", "## Supplementary Text S7. Abbreviations")
    parts += [s7.strip(), ""]

    # ── Supplementary Tables ──
    parts += ["## Supplementary Tables", ""]

    # Table S1：L1 分歧（11 例：guideline 10 例 + 冻结子集 C04）
    parts += ["**Supplementary Table S1. L1 literature-derived gold: the eleven exact-scale disagreements, "
              "with the pharmacological rationale for each.**", "",
              "| case | ophthalmic | systemic | gold | system | direction | documented rationale |",
              "|---|---|---|---|---|---|---|"]
    order = {"low": 1, "medium": 2, "high": 3}
    for r in dis:
        g, p = r["gold_risk"], r["predicted"]
        d = "upgrade" if order.get(p, 0) > order.get(g, 0) else "downgrade"
        parts.append(f"| {r['case_id']} | {r['a_name']} | {r['b_name']} | {g} | {p} | {d} | "
                     f"{L1_RATIONALE.get(r['case_id'], '')} |")
    parts += ["", "Ten disagreements occur in the guideline-sourced subset (n = 58). The eleventh "
              "(C04, flurbiprofen × warfarin) is the single miss in the procedurally frozen blind "
              "subset (n = 40, 39 of 40 correct; 36 of 40 under the pre-correction labels, Section 3.8) "
              "and follows the flurbiprofen tier correction. The FDA/Stockley's/BNF mechanism subset "
              "(n = 20) was classified with perfect exact accuracy.", ""]

    # Table S2：审计分歧方向（当前引擎实测 30 处）
    parts += ["**Supplementary Table S2. Audit-set disagreements between the system and the "
              "absorption-corrected gold, by direction (n = 92).**", "",
              "| disagreement direction | n |", "|---|---|",
              "| high -> low | 8 |", "| high -> medium | 9 |", "| medium -> low | 9 |",
              "| medium -> high | 2 |", "| low -> medium | 1 |", "| low -> high | 1 |",
              "| **total disagreements** | **30** |", "",
              "The four over-alerts (system grade higher than gold) are apraclonidine x midazolam, "
              "apraclonidine x loperamide, tacrolimus x ibuprofen and bromfenac x enalapril.", ""]

    # Table S3：专家逐例
    parts += ["**Supplementary Table S3. Expert case-level ratings (12 cases, two ophthalmologists).**", "",
              t_expert.strip(), "",
              "The instrument displayed the proposed gold grade and a system grade to the reviewers, "
              "so this is a grade review rather than a blinded assessment (Sections 2.5 and 3.8); for "
              "R10 and R11 the displayed grade was a class-level hint, not the engine's output.", ""]

    # Table S4：注册表摘要
    parts += ["**Supplementary Table S4. Registry summary.**", "", t_registry.strip(), ""]

    # Table S5：逐药分级（新增）
    parts += ["**Supplementary Table S5. Per-agent systemic-absorption tier, with the source record "
              "for each agent (n = 113).**", "",
              "Tiers are a study-team assignment from the sources listed in the final column, not a "
              "measured quantity. Six tier values appear in the registry "
              "(`systemic_absorption_high`, `_medium`, `_low`, `_very_low`, "
              "`minimal_systemic_absorption`, `systemic_absorption_none`); the L3 hard constraint "
              "fires on two of them, `systemic_absorption_low` and `systemic_absorption_very_low` "
              "(`kg_layer.py`); the remaining four values preserve the assigned level, and the other "
              "low-exposure values are already mapped to low risk within the matrix layer, so final "
              "grades are unaffected.", "",
              "| ophthalmic_id | primary_name | category | absorption_tier | evidence_sources |",
              "|---|---|---|---|---|"]
    for oid, name, cat, tier, src in tiers:
        parts.append(f"| {oid} | {name} | {cat} | {tier} | {src} |")
    parts += [""]

    # Table S6：规则清单
    parts += ["**Supplementary Table S6. Rule inventory (40 mechanism rules).**", "", t_rules.strip(), ""]

    # Table S7：性能
    parts += ["**Supplementary Table S7. Four-method performance by dataset.**", "", t_perf.strip(), ""]

    # Table S8：分布
    parts += ["**Supplementary Table S8. Gold-level distribution by dataset.**", "", t_dist.strip(), ""]

    SUPP.write_text("\n".join(parts) + "\n", encoding="utf-8")

    print(f"补充材料已重建 -> {SUPP}")
    print(f"  文件行数: {len(parts)}")
    print(f"  新增表: S1 分歧理由({len(dis)} 例), S5 逐药分级({len(tiers)} 例)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
