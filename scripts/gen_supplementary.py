# -*- coding: utf-8 -*-
"""gen_supplementary.py — 生成 R1 修改后的补充材料与新增表格：
S1: L1 10 例分歧（含判定层与解释，取自权威 REPORT）
S2: 审计集 27 例分歧（gold/pred/方向）
S3: 专家 12 例逐例评分（gold/system/E1/E2）
S5: 113 种眼科药吸收分级汇总
table5: 审计集分层与分歧构成
table6: 专家逐例评分表（与 S3 同源，精简）
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "paper" / "supplementary"
OUT.mkdir(parents=True, exist_ok=True)
TAB = ROOT / "outputs" / "tables"

# ── S1: L1 10 例分歧（数据来自 multiseed blind_l1 seed0 full_system）──
l1 = [json.loads(l) for l in open(ROOT / "outputs/multiseed_per_dataset/blind_l1__seed0.jsonl", encoding="utf-8")]
fs_l1 = [r for r in l1 if r["method"] == "full_system"]
disc_l1 = [r for r in fs_l1 if r["predicted"] != r["gold_risk"]]
assert len(disc_l1) == 10, len(disc_l1)
# 从 REPORT.md 取判定层/解释
report_txt = (ROOT / "outputs/multiseed_per_dataset/REPORT.md").read_text(encoding="utf-8")
expl = {}
for line in report_txt.splitlines():
    if line.strip().startswith("| G") and "|" in line:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 7 and cells[0].startswith("G"):
            expl[cells[0]] = {"oph": cells[2], "sys": cells[3], "gold": cells[4], "pred": cells[5],
                              "rules": cells[6], "note": ""}
# 解释段落逐例解析（中文 → 英文）
RAT_EN = {
    "G106": "Anticholinergic burden x TCA overlap (expert-consensus cell = high; guideline gold conservative at medium)",
    "G108": "Weak-corticosteroid potency granularity (Rimexolone intermediate IOP effect; class-matrix cell coarse)",
    "G113": "Ophthalmic fluoroquinolone QT risk: low absorption design decision vs guideline gold medium",
    "G114": "Ophthalmic fluoroquinolone QT risk: low absorption design decision vs guideline gold medium",
    "G124": "Dexamethasone CYP3A4 induction to medium (mechanism genuine; guideline gold low)",
    "G131": "Macrolide CYP3A4 inhibition with low-absorption ophthalmic erythromycin vs guideline gold medium",
    "G132": "Macrolide CYP3A4 inhibition with low-absorption azithromycin vs guideline gold medium",
    "G133": "Azole CYP3A4 inhibition with low-absorption voriconazole vs guideline gold medium",
    "G134": "Azole CYP3A4 inhibition with low-absorption fluconazole vs guideline gold medium",
    "G139": "Combination corticosteroid x warfarin (INR fluctuation risk vs errata-corrected gold)",
}
for para in report_txt.splitlines():
    if para.strip().startswith("解释："):
        for seg in para.strip()[3:].split("；"):
            seg = seg.strip()
            m = __import__("re").match(r"^([A-Z]+\d+)\s+(.*)$", seg)
            if m and m.group(1) in expl and m.group(1) not in RAT_EN:
                RAT_EN[m.group(1)] = m.group(2)
lines = ["# Supplementary Table S1. The ten L1 exact-scale disagreements (full_system, condition 0)",
         "", "| case | subset | ophthalmic | systemic | gold | predicted | matched rules | rationale |", "|---|---|---|---|---|---|---|---|"]
for r in sorted(disc_l1, key=lambda x: x["case_id"]):
    e = expl.get(r["case_id"], {})
    note = RAT_EN.get(r["case_id"], e.get("note", ""))
    if len(note) > 160:
        note = note[:160] + "..."
    lines.append(f"| {r['case_id']} | guideline_sourced | {r['a_name']} | {r['b_name']} | {r['gold_risk']} | {r['predicted']} | {e.get('rules','')} | {note} |")
lines += ["", "Note: all ten disagreements are clinical judgment boundaries at the low-absorption end of the risk scale; none reflects a correctable rule error."]
(OUT / "S1_l1_disagreements.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# ── S2: 审计集 27 例分歧 ──
v3 = [json.loads(l) for l in open(ROOT / "outputs/multiseed_per_dataset/blind_v3_ddinter__seed0.jsonl", encoding="utf-8")]
fs_v3 = [r for r in v3 if r["method"] == "full_system"]
disc_v3 = [r for r in fs_v3 if r["predicted"] != r["gold_risk"]]
assert len(disc_v3) == 27, len(disc_v3)
lines = ["# Supplementary Table S2. The 27 DDInter-audit disagreements (full_system, condition 0)",
         "", "| case | ophthalmic | systemic | gold (corrected) | predicted | direction |", "|---|---|---|---|---|---|"]
for r in sorted(disc_v3, key=lambda x: x["case_id"]):
    d = "downgrade" if ["low", "medium", "high"].index(r["predicted"]) < ["low", "medium", "high"].index(r["gold_risk"]) else "upgrade"
    lines.append(f"| {r['case_id']} | {r['a_name']} | {r['b_name']} | {r['gold_risk']} | {r['predicted']} | {d} |")
(OUT / "S2_audit_disagreements.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# ── S3 / table6: 专家 12 例逐例 ──
er = json.loads((ROOT / "outputs/expert_review/expert_review_results.json").read_text(encoding="utf-8"))
rows = []
with open(ROOT / "outputs/expert_review/blind_gold_review_CN.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        rows.append(row)
GOLD_SRC_EN = {
    "勘误后(原high)": "errata-corrected (originally high)",
    "勘误后(原medium)": "errata-corrected (originally medium)",
    "勘误后(原low)": "errata-corrected (originally low)",
    "药理标定": "pharmacology-labelled",
    "药理标定(陷阱例)": "pharmacology-labelled (trap case)",
    "T1专家": "T1 mechanism annotation",
}
lines = ["# Supplementary Table S3. Expert assessment, per-case ratings (R01–R12)",
         "", "| case | ophthalmic | systemic | gold | system | expert 1 | expert 2 | gold source |", "|---|---|---|---|---|---|---|---|"]
for i, row in enumerate(rows):
    src = row["gold来源"].strip()
    lines.append(f"| {row['编号']} | {row['眼科药']} | {row['全身药']} | {row['gold(待确认)']} | {er['system_v2'][i]} | {er['expert_1'][i]} | {er['expert_2'][i]} | {GOLD_SRC_EN.get(src, src)} |")
(OUT / "S3_expert_cases.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

t6 = ["# table6_expert_cases", "", "| case | ophthalmic | systemic | gold | system | expert1 | expert2 |", "|---|---|---|---|---|---|---|"]
for i, row in enumerate(rows):
    t6.append(f"| {row['编号']} | {row['眼科药']} | {row['全身药']} | {row['gold(待确认)']} | {er['system_v2'][i]} | {er['expert_1'][i]} | {er['expert_2'][i]} |")
(TAB / "table6_expert_cases.md").write_text("\n".join(t6) + "\n", encoding="utf-8")

# ── S5: 吸收分级汇总 ──
a_rows = list(csv.DictReader(open(ROOT / "data/seed/entities_a.csv", encoding="utf-8-sig")))
tier_cnt = {}
tier_list = {}
for r in a_rows:
    flags = r.get("flags", "").split("|")
    tier = next((f.replace("systemic_absorption_", "") for f in flags if f.startswith("systemic_absorption_")), "unknown")
    tier_cnt[tier] = tier_cnt.get(tier, 0) + 1
    tier_list.setdefault(tier, []).append(r.get("primary_name", r.get("generic_name", "?")))
lines = ["# Supplementary Table S5. Systemic-absorption tier distribution (113 ophthalmic agents)",
         "", "| tier | n |", "|---|---|"]
for t in ["high", "medium", "low", "very_low", "unknown", "none"]:
    lines.append(f"| {t} | {tier_cnt.get(t, 0)} |")
lines += ["", "Per-agent tiers with source flags are recorded in `data/seed/entities_a.csv` (column `flags`, prefix `systemic_absorption_`).",
          "Tiers: high/medium/low/very_low denote the estimated systemic absorption of the topically applied agent; `none` denotes agents carrying an explicit `systemic_absorption_none` flag (four tear substitutes and viscoelastics: hydroxypropyl cellulose, sodium hyaluronate, carboxymethylcellulose, hydroxypropyl methylcellulose); `unknown` denotes seven agents without an absorption flag in the registry (six intravitreal biologics and intraocular acetylcholine).",
          "", "**Agent lists per tier:**", ""]
for t in ["high", "medium", "low", "very_low", "unknown", "none"]:
    if tier_list.get(t):
        lines.append(f"- **{t}** ({len(tier_list[t])}): {', '.join(sorted(tier_list[t])[:60])}")
(OUT / "S5_absorption_tiers.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# ── table5: 审计分层 ──
stats = json.loads((ROOT / "outputs/revision_r1_stats.json").read_text(encoding="utf-8"))
st = stats["audit_strata"]
comp = {}
for r in fs_v3:
    k = f"{r['gold_risk']}->{r['predicted']}"
    comp[k] = comp.get(k, 0) + 1
t5 = ["# table5_audit_strata", "",
      "| stratum | n | system agreement |",
      "|---|---|---|",
      f"| All 92 (vs corrected gold) | 92 | 65 (0.707) |",
      f"| All 92 (vs uncorrected DDInter severity) | 92 | 37 (0.402) |",
      f"| Absorption-corrected cases | {st['corrected']['n']} | {st['corrected']['agree']} ({st['corrected']['agree']/st['corrected']['n']:.3f}) |",
      f"| Kept cases | {st['kept']['n']} | {st['kept']['agree']} ({st['kept']['agree']/st['kept']['n']:.3f}) |",
      "",
      "| disagreement direction | n |",
      "|---|---|",
      f"| high->low | {comp.get('high->low', 0)} |",
      f"| high->medium | {comp.get('high->medium', 0)} |",
      f"| medium->low | {comp.get('medium->low', 0)} |",
      f"| medium->high | {comp.get('medium->high', 0)} |",
      f"| low->medium | {comp.get('low->medium', 0)} |",
      f"| low->high | {comp.get('low->high', 0)} |",
      f"| **total disagreements** | **{len(disc_v3)}** |"]
(TAB / "table5_audit_strata.md").write_text("\n".join(t5) + "\n", encoding="utf-8")

print("S1:", len(disc_l1), "S2:", len(disc_v3), "S3: 12 rows; S5 tiers:", tier_cnt, "table5/6 written")
