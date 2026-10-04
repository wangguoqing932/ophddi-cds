# -*- coding: utf-8 -*-
"""recompute_all_reported_numbers.py — 用沉积数据 + stats_tests.py 复算手稿全部数字。

回应审稿人意见 5："Please regenerate every number from the deposited data with
deposited code." 本脚本是唯一入口：所有数字都从 data/ 与 outputs/ 的归档文件
重新计算，不引用手稿中的任何现值。

输出：outputs/recomputed/numbers.json（机器可读）+ 屏幕对照表。
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402
from stats_tests import (bootstrap_kappa, clopper_pearson, cohens_kappa,  # noqa: E402
                         exact_mcnemar, max_kappa, wilson_ci)

OUT = ROOT / "outputs" / "recomputed"
OUT.mkdir(parents=True, exist_ok=True)
kg = PreciseKG()

# 数据集位置在两种布局下不同（项目内 / 公开仓库）
def gold_path(ds: str) -> pathlib.Path:
    for c in (ROOT / "data" / "datasets" / ds / "cases.jsonl",
              ROOT / "data" / "gold" / ds / "cases.jsonl"):
        if c.exists():
            return c
    raise FileNotFoundError(ds)


def pred_path(ds: str, seed: int = 0) -> pathlib.Path:
    for c in (ROOT / "outputs" / "multiseed_per_dataset" / f"{ds}__seed{seed}.jsonl",
              ROOT / "data" / "predictions" / f"{ds}__seed{seed}.jsonl"):
        if c.exists():
            return c
    raise FileNotFoundError(ds)


def load_gold(ds: str) -> dict:
    rows = [json.loads(l) for l in gold_path(ds).open(encoding="utf-8") if l.strip()]
    return {r["case_id"]: (r.get("gold_risk_level") or r.get("gold_risk")) for r in rows}


def load_pred(ds: str, method: str, seed: int = 0) -> dict:
    """返回 case_id -> 预测（单个温度条件）。full_system 一律用当前引擎重算。"""
    out = {}
    for line in pred_path(ds, seed).open(encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["method"] != method:
            continue
        if method == "full_system":
            out[r["case_id"]] = kg.deterministic_level_v2(r["a_name"], r["b_name"])[0]
        else:
            out[r["case_id"]] = r["predicted"]
    return out


def load_pred_multi(ds: str, method: str, seeds=range(5)) -> dict:
    """返回 (case_id, seed) -> 预测，供跨温度条件的均值与 SD 使用。

    注意：手稿 Table 3 报的是**五个温度条件的均值 ± 总体 SD**，不是温度 0 的
    单次值。full_system 是确定性的，各条件相同；LLM 基线则必须取均值。
    """
    out = {}
    for s in seeds:
        for cid, p in load_pred(ds, method, s).items():
            out[(cid, s)] = p
    return out


def metrics(gold: dict, pred: dict) -> dict:
    """分别给出三分类精确准确率与二分类（high vs 非 high）指标。

    注意：Acc3 是三级精确匹配数，与 high/非-high 的 (tp+tn) 不是一回事，
    两者不可混用（Wilson 区间必须用对应的计数）。
    """
    ids = [k for k in gold if k in pred]
    n = len(ids)
    exact = sum(1 for k in ids if gold[k] == pred[k])
    tp = sum(1 for k in ids if gold[k] == "high" and pred[k] == "high")
    fp = sum(1 for k in ids if gold[k] != "high" and pred[k] == "high")
    fn = sum(1 for k in ids if gold[k] == "high" and pred[k] != "high")
    tn = sum(1 for k in ids if gold[k] != "high" and pred[k] != "high")
    sens = tp / (tp + fn) if tp + fn else 0.0
    spec = tn / (tn + fp) if tn + fp else 0.0
    return {"n": n, "acc3": exact / n, "exact3": exact,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "binary_correct": tp + tn,
            "sens": sens, "spec": spec}


R: dict = {}

# ── 1. L1（118 例）四方法 ──────────────────────────────────────────────
print("=== 1. L1 数据集 ===")
g1 = load_gold("blind_l1")
preds1 = {m: load_pred("blind_l1", m) for m in
          ["full_system", "pure_llm", "naive_rag", "lightrag"]}
for m, p in preds1.items():
    mt = metrics(g1, p)
    R[f"l1.{m}"] = mt
    print(f"  {m:12s} n={mt['n']} acc={mt['acc3']:.4f} sens={mt['sens']:.4f} "
          f"spec={mt['spec']:.4f} exact3={mt['exact3']}")

# Wilson / Clopper-Pearson / bootstrap kappa（full_system）
# 五条件均值 ± 总体 SD（与 Table 3 口径一致）
print("  五条件均值 ± SD:")
for m in ["full_system", "pure_llm", "naive_rag", "lightrag"]:
    multi = load_pred_multi("blind_l1", m)
    accs, sens_, specs, ks = [], [], [], []
    for s in range(5):
        gs = {cid: g1[cid] for (cid, ss) in multi if ss == s and cid in g1}
        ps = {cid: multi[(cid, s)] for cid in gs}
        if not gs:
            continue
        mt = metrics(gs, ps)
        accs.append(mt["acc3"]); sens_.append(mt["sens"]); specs.append(mt["spec"])
        gl_ = [gs[k] for k in sorted(gs)]; pl_ = [ps[k] for k in sorted(gs)]
        ks.append(cohens_kappa(gl_, pl_))
    mean = lambda v: sum(v) / len(v) if v else 0.0
    sd = lambda v: (sum((x - mean(v)) ** 2 for x in v) / len(v)) ** 0.5 if v else 0.0
    R[f"l1.multi.{m}"] = {
        "acc3": {"mean": mean(accs), "sd": sd(accs), "values": accs},
        "sens": {"mean": mean(sens_), "sd": sd(sens_), "values": sens_},
        "spec": {"mean": mean(specs), "sd": sd(specs), "values": specs},
        "kappa": {"mean": mean(ks), "sd": sd(ks), "values": ks},
    }
    print(f"    {m:12s} acc3={mean(accs):.4f}±{sd(accs):.4f} "
          f"sens={mean(sens_):.4f}±{sd(sens_):.4f} kappa={mean(ks):.4f}±{sd(ks):.4f}")

fs1 = metrics(g1, preds1["full_system"])
gl = [g1[k] for k in g1 if k in preds1["full_system"]]
fs_pl = [preds1["full_system"][k] for k in g1 if k in preds1["full_system"]]
R["l1.acc3_wilson"] = wilson_ci(fs1["exact3"], fs1["n"])
R["l1.sens_wilson"] = wilson_ci(fs1["tp"], fs1["tp"] + fs1["fn"])
R["l1.kappa"] = cohens_kappa(gl, fs_pl)
R["l1.kappa_bootstrap"] = bootstrap_kappa(gl, fs_pl, n_resamples=2000, seed=12345)
print(f"  Acc3 Wilson      : {R['l1.acc3_wilson'][0]:.3f}-{R['l1.acc3_wilson'][1]:.3f}")
print(f"  Sens Wilson      : {R['l1.sens_wilson'][0]:.3f}-{R['l1.sens_wilson'][1]:.3f}")
print(f"  kappa            : {R['l1.kappa']:.4f}")
print(f"  kappa bootstrap  : {R['l1.kappa_bootstrap']['ci_low']:.3f}-"
      f"{R['l1.kappa_bootstrap']['ci_high']:.3f}")

# McNemar（condition 0），对三个基线
print("  McNemar (full_system vs 各基线):")
for base in ["pure_llm", "naive_rag", "lightrag"]:
    b = preds1[base]
    bb = sum(1 for k in g1 if k in b and preds1["full_system"][k] == g1[k] and b[k] != g1[k])
    cc = sum(1 for k in g1 if k in b and preds1["full_system"][k] != g1[k] and b[k] == g1[k])
    r = exact_mcnemar(bb, cc)
    R[f"l1.mcnemar_vs_{base}"] = r
    print(f"    vs {base:10s}: {bb} vs {cc}   p={r['p_value']:.4g}")

# 子集：frozen / mechanism / guideline
print("  L1 子集:")
sub_rows = [json.loads(l) for l in pred_path("blind_l1").open(encoding="utf-8")
            if l.strip() and json.loads(l)["method"] == "full_system"]
sub_of = {r["case_id"]: r.get("subset") for r in sub_rows}
for name in sorted({v for v in sub_of.values() if v}):
    ids = [k for k, v in sub_of.items() if v == name and k in preds1["full_system"]]
    ok = sum(1 for k in ids if g1[k] == preds1["full_system"][k])
    r = {"n": len(ids), "correct": ok, "acc3": ok / len(ids) if ids else 0}
    r["clopper_pearson"] = clopper_pearson(ok, len(ids))
    R[f"l1.subset.{name}"] = r
    print(f"    {name:26s} n={r['n']:3d} correct={ok:3d} acc={r['acc3']:.4f} "
          f"CP={r['clopper_pearson'][0]:.3f}-{r['clopper_pearson'][1]:.3f}")

# ── 2. 审计集（92 例）──────────────────────────────────────────────────
print("\n=== 2. 审计集（blind_v3_ddinter, 92 例）===")
g3 = load_gold("blind_v3_ddinter")
preds3 = {m: load_pred("blind_v3_ddinter", m) for m in
          ["full_system", "pure_llm", "naive_rag", "lightrag"]}
for m, p in preds3.items():
    mt = metrics(g3, p)
    R[f"audit.{m}"] = mt
    print(f"  {m:12s} acc={mt['acc3']:.4f} sens={mt['sens']:.4f} spec={mt['spec']:.4f}")
fs3 = metrics(g3, preds3["full_system"])
R["audit.acc3_wilson"] = wilson_ci(fs3["exact3"], fs3["n"])
R["audit.sens_wilson"] = wilson_ci(fs3["tp"], fs3["tp"] + fs3["fn"])
ga = [g3[k] for k in g3 if k in preds3["full_system"]]
pa = [preds3["full_system"][k] for k in g3 if k in preds3["full_system"]]
R["audit.kappa"] = cohens_kappa(ga, pa)
print(f"  Acc3 Wilson  : {R['audit.acc3_wilson'][0]:.3f}-{R['audit.acc3_wilson'][1]:.3f}")
print(f"  Sens Wilson  : {R['audit.sens_wilson'][0]:.3f}-{R['audit.sens_wilson'][1]:.3f}")
print(f"  kappa        : {R['audit.kappa']:.4f}")

# 与未更正 DDInter 严重度的同意率（设计文件保存了 ddinter_level）
design = json.loads((ROOT / "outputs" / "blind_test" /
                     "blind_set_v3_ddinter.json").read_text(encoding="utf-8"))
agree_ddinter = sum(1 for d in design
                    if preds3["full_system"].get(d["case_id"]) == d["ddinter_level"])
R["audit.agreement_uncorrected"] = {"n": len(design), "agree": agree_ddinter,
                                   "rate": agree_ddinter / len(design)}
print(f"  vs 未更正 DDInter: {agree_ddinter}/{len(design)} = "
      f"{agree_ddinter/len(design):.4f}")

# 分层：被更正的 30 例 / 保留的 62 例
# 判定依据用 ddinter_level（第三方原始）与 proposed_gold（更正后）是否相同。
# 设计文件里的 gold_rule 前缀计数（50/42）与这两个字段不一致，不能作为分层依据。
kept = [d["case_id"] for d in design if d["ddinter_level"] == d["proposed_gold"]]
corr = [d["case_id"] for d in design if d["ddinter_level"] != d["proposed_gold"]]
R["audit.strata_n"] = {"kept": len(kept), "corrected": len(corr)}
print(f"  分层: 更正 {len(corr)} 例, 保留 {len(kept)} 例")
for label, ids in [("kept(third-party)", kept), ("absorption-corrected", corr)]:
    ok = sum(1 for k in ids if g3[k] == preds3["full_system"][k])
    R[f"audit.stratum.{label}"] = {"n": len(ids), "correct": ok,
                                   "rate": ok / len(ids) if ids else 0,
                                   "wilson": wilson_ci(ok, len(ids))}
    print(f"  {label:22s} n={len(ids):3d} correct={ok:3d} "
          f"rate={ok/len(ids) if ids else 0:.4f}")

# 审计集 McNemar
print("  审计集 McNemar:")
for base in ["pure_llm", "naive_rag", "lightrag"]:
    b = preds3[base]
    bb = sum(1 for k in g3 if k in b and preds3["full_system"][k] == g3[k] and b[k] != g3[k])
    cc = sum(1 for k in g3 if k in b and preds3["full_system"][k] != g3[k] and b[k] == g3[k])
    r = exact_mcnemar(bb, cc)
    R[f"audit.mcnemar_vs_{base}"] = r
    print(f"    vs {base:10s}: {bb} vs {cc}   p={r['p_value']:.4g}")

# 阳性预测值（1% 患病率）
sens_a, spec_a, prev = fs3["sens"], fs3["spec"], 0.01
ppv = (sens_a * prev) / (sens_a * prev + (1 - spec_a) * (1 - prev))
R["audit.ppv_at_1pct"] = {"sens": sens_a, "spec": spec_a, "prevalence": prev, "ppv": ppv}
print(f"  PPV @1% 患病率: {ppv*100:.2f}%")

# ── 3. 吸收分级计数 ────────────────────────────────────────────────────
print("\n=== 3. 吸收分级计数 ===")
import csv
rows = list(csv.DictReader((ROOT / "data" / "seed" / "entities_a.csv").open(encoding="utf-8-sig")))
tiers = Counter()
for r in rows:
    for f in (r.get("flags") or "").split("|"):
        if f.startswith("systemic_absorption_") or f == "minimal_systemic_absorption":
            tiers[f] += 1
R["tiers"] = dict(tiers)
R["tiers.total_agents"] = len(rows)
for k, v in sorted(tiers.items()):
    print(f"  {k:32s} {v}")

# ── 4. expert 12 例（按表单实际记录）───────────────────────────────────
print("\n=== 4. 专家实验（按问卷/档案实际记录）===")
arch = json.loads((ROOT / "outputs" / "expert_review" /
                   "expert_responses_archive.json").read_text(encoding="utf-8"))
CN = {"低": "low", "中": "medium", "高": "high"}
e1 = [CN[r["expert_1"]] for r in arch["responses"]]
e2 = [CN[r["expert_2"]] for r in arch["responses"]]
# 问卷展示给专家的系统评级
shown = [r["system_v2"] for r in arch["responses"]]
gold_shown = [r["gold_proposed"] for r in arch["responses"]]
R["expert.agreement_e1_e2"] = cohens_kappa(e1, e2)
R["expert.agreement_e1_e2_raw"] = sum(1 for a, b in zip(e1, e2) if a == b)
R["expert.agreement_e1_system"] = cohens_kappa(e1, shown)
R["expert.agreement_e2_system"] = cohens_kappa(e2, shown)
R["expert.agreement_e1_gold"] = cohens_kappa(e1, gold_shown)
R["expert.agreement_e2_gold"] = cohens_kappa(e2, gold_shown)
R["expert.weighted_e1_system"] = cohens_kappa(e1, shown, weights="quadratic")
R["expert.weighted_e2_system"] = cohens_kappa(e2, shown, weights="quadratic")
R["expert.max_kappa_e1"] = max_kappa(e1, shown)
R["expert.max_kappa_e2"] = max_kappa(e2, shown)
R["expert.raw_agreement"] = {
    "e1_vs_system": sum(1 for a, b in zip(e1, shown) if a == b),
    "e2_vs_system": sum(1 for a, b in zip(e2, shown) if a == b),
    "e1_vs_gold": sum(1 for a, b in zip(e1, gold_shown) if a == b),
    "e2_vs_gold": sum(1 for a, b in zip(e2, gold_shown) if a == b),
}
R["expert.graded_lower_than_shown"] = {
    "e1": sum(1 for r in arch["responses"]
              if ["low", "medium", "high"].index(CN[r["expert_1"]])
              < ["low", "medium", "high"].index(r["system_v2"])),
    "e2": sum(1 for r in arch["responses"]
              if ["low", "medium", "high"].index(CN[r["expert_2"]])
              < ["low", "medium", "high"].index(r["system_v2"])),
}
print(f"  E1 vs E2        kappa={R['expert.agreement_e1_e2']:+.3f} "
      f"raw={R['expert.agreement_e1_e2_raw']}/12")
print(f"  E1 vs system    kappa={R['expert.agreement_e1_system']:+.3f} "
      f"raw={R['expert.raw_agreement']['e1_vs_system']}/12 "
      f"max={R['expert.max_kappa_e1']:.3f} w={R['expert.weighted_e1_system']:+.3f}")
print(f"  E2 vs system    kappa={R['expert.agreement_e2_system']:+.3f} "
      f"raw={R['expert.raw_agreement']['e2_vs_system']}/12 "
      f"max={R['expert.max_kappa_e2']:.3f} w={R['expert.weighted_e2_system']:+.3f}")
print(f"  E1 vs gold      kappa={R['expert.agreement_e1_gold']:+.3f}")
print(f"  E2 vs gold      kappa={R['expert.agreement_e2_gold']:+.3f}")
print(f"  判低于展示值: E1 {R['expert.graded_lower_than_shown']['e1']}/12, "
      f"E2 {R['expert.graded_lower_than_shown']['e2']}/12")

(OUT / "numbers.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str),
                                  encoding="utf-8")
print(f"\n已写出 -> {OUT / 'numbers.json'}")
