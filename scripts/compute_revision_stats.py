# -*- coding: utf-8 -*-
"""compute_revision_stats.py — R1/R2 修改补充统计量 v2:
1) 专家 vs gold / 系统 vs gold Cohen's kappa（12 例，含 quadratic weighted kappa、最大可达 kappa、high 层一致率）
2) L1/audit 集 McNemar（full_system vs 各 LLM 基线，seed0）
3) DDInter 审计集：未校正 gold 对比（ddinter_level vs predicted）、校正/保留分层
4) blind1-only (B01-B20) 终版引擎 acc4（调参暴露最小子集）
5) 置信区间：Wilson (acc), Clopper-Pearson (n=40/20), kappa bootstrap CI
运行: .venv\\Scripts\\python.exe scripts\\compute_revision_stats.py
"""
import csv
import json
import random
from math import comb, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ["low", "medium", "high"]


def cohen_kappa(a, b, weighted=False):
    n = len(a)
    obs = sum(1 for x, y in zip(a, b) if x == y) / n
    if weighted:
        w = [[abs(LEVELS.index(x) - LEVELS.index(y)) for y in LEVELS] for x in LEVELS]
        wmax = 2
        exp_w = 0.0
        obs_w = 0.0
        for i, x in enumerate(LEVELS):
            for j, y in enumerate(LEVELS):
                pa, pb = a.count(x) / n, b.count(y) / n
                wij = 1 - (w[i][j] / wmax) ** 2
                exp_w += pa * pb * wij
                obs_w += (sum(1 for u, v in zip(a, b) if u == x and v == y) / n) * wij
        return (obs_w - exp_w) / (1 - exp_w) if exp_w != 1 else 0.0
    exp = sum((a.count(lv) / n) * (b.count(lv) / n) for lv in LEVELS)
    return (obs - exp) / (1 - exp) if exp != 1 else 0.0


def max_achievable_kappa(a, b):
    """给定边际分布的最大可达未加权 kappa（最优对角排列）。"""
    n = len(a)
    best = 0
    perms = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
    for p in perms:
        agree = sum(min(a.count(LEVELS[i]), b.count(LEVELS[p[i]])) for i in range(3))
        best = max(best, agree)
    obs = best / n
    exp = sum((a.count(lv) / n) * (b.count(lv) / n) for lv in LEVELS)
    return (obs - exp) / (1 - exp) if exp != 1 else 0.0, best


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return round(c - h, 3), round(c + h, 3)


def clopper_pearson(k, n, alpha=0.05):
    from scipy.stats import beta
    lo = beta.ppf(alpha / 2, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(1 - alpha / 2, k + 1, n - k) if k < n else 1.0
    return round(lo, 3), round(hi, 3)


def mcnemar_exact(b01, b10):
    n = b01 + b10
    if n == 0:
        return 1.0
    p = sum(comb(n, k) * (0.5 ** n) for k in range(0, min(b01, b10) + 1))
    return 2 * p if p <= 0.5 else 2 * (1 - p)


def kappa_bootstrap(a, b, n_iter=2000, seed=42):
    rng = random.Random(seed)
    vals = []
    n = len(a)
    for _ in range(n_iter):
        idx = [rng.randrange(n) for _ in range(n)]
        aa = [a[i] for i in idx]
        bb = [b[i] for i in idx]
        vals.append(cohen_kappa(aa, bb))
    vals.sort()
    return round(vals[int(0.025 * n_iter)], 3), round(vals[int(0.975 * n_iter)], 3)


def load_preds(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    out = {}
    # ── 1) 专家 vs gold ──
    er = json.loads((ROOT / "outputs/expert_review/expert_review_results.json").read_text(encoding="utf-8"))
    e1, e2, sysv = er["expert_1"], er["expert_2"], er["system_v2"]
    gold = []
    with open(ROOT / "outputs/expert_review/blind_gold_review_CN.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            gold.append(row["gold(待确认)"].strip().lower())
    pairs = {
        "expert1_vs_gold": (e1, gold), "expert2_vs_gold": (e2, gold),
        "system_vs_gold": (sysv, gold), "expert1_vs_system": (e1, sysv),
        "expert2_vs_system": (e2, sysv), "expert1_vs_expert2": (e1, e2),
    }
    out["expert_kappas"] = {
        k: {"kappa": round(cohen_kappa(a, b), 3),
            "kw": round(cohen_kappa(a, b, weighted=True), 3),
            "agreement": round(sum(1 for x, y in zip(a, b) if x == y) / len(a), 3)}
        for k, (a, b) in pairs.items()
    }
    out["expert_max_kappa_sys"] = max_achievable_kappa(sysv, e1)
    out["high_tier_agreement"] = {
        "system_high_n": sysv.count("high"),
        "experts_high_on_system_high": sum(1 for i, s in enumerate(sysv) if s == "high" and e1[i] == "high" and e2[i] == "high"),
        "expert1_high_on_system_high": sum(1 for i, s in enumerate(sysv) if s == "high" and e1[i] == "high"),
        "expert2_high_on_system_high": sum(1 for i, s in enumerate(sysv) if s == "high" and e2[i] == "high"),
    }

    # ── 2) McNemar ──
    l1 = load_preds(ROOT / "outputs/multiseed_per_dataset/blind_l1__seed0.jsonl")
    v3 = load_preds(ROOT / "outputs/multiseed_per_dataset/blind_v3_ddinter__seed0.jsonl")
    for ds_name, rows in (("l1", l1), ("audit", v3)):
        by = {}
        for r in rows:
            by.setdefault(r["method"], []).append(r)
        fs = {(r["case_id"]): (r["predicted"] == r["gold_risk"]) for r in by["full_system"]}
        out[f"mcnemar_{ds_name}"] = {}
        for m in ("pure_llm", "naive_rag", "lightrag"):
            base = {(r["case_id"]): (r["predicted"] == r["gold_risk"]) for r in by[m]}
            b01 = sum(1 for k in fs if fs[k] and not base[k])
            b10 = sum(1 for k in fs if fs[k] is False and base[k])
            out[f"mcnemar_{ds_name}"][m] = {"sys_ok_base_err": b01, "sys_err_base_ok": b10,
                                            "p_exact": mcnemar_exact(b01, b10)}

    # ── 3) 审计集：未校正 gold 分层 ──
    bv3 = json.loads((ROOT / "outputs/blind_test/blind_set_v3_ddinter.json").read_text(encoding="utf-8"))
    v3fs = [r for r in v3 if r["method"] == "full_system"]
    v3map = {c["case_id"]: c for c in bv3}
    corr = {"agree": 0, "n": 0, "to_low": 0}
    kept = {"agree": 0, "n": 0}
    unc = {"agree": 0, "n": 0}
    for r in v3fs:
        c = v3map[r["case_id"]]
        is_corr = c["proposed_gold"] != c["ddinter_level"]
        if is_corr:
            corr["n"] += 1
            corr["agree"] += 1 if r["predicted"] == r["gold_risk"] else 0
            corr["to_low"] += 1 if c["proposed_gold"] == "low" else 0
        else:
            kept["n"] += 1
            kept["agree"] += 1 if r["predicted"] == r["gold_risk"] else 0
        unc["n"] += 1
        unc["agree"] += 1 if r["predicted"] == c["ddinter_level"] else 0
    out["audit_strata"] = {
        "corrected": corr, "kept": kept,
        "system_vs_uncorrected_ddinter": {
            "agree_n": unc["agree"], "n": unc["n"],
            "acc4": round(unc["agree"] / unc["n"], 3)},
        "system_vs_corrected_gold": {
            "agree_n": corr["agree"] + kept["agree"], "n": 92,
            "acc4": round((corr["agree"] + kept["agree"]) / 92, 3)},
    }

    # ── 4) blind1-only（B01-B20）终版 acc4 ──
    l1ind = json.loads((ROOT / "outputs/blind_test/l1_independent.json").read_text(encoding="utf-8"))
    b_ids = {c["case_id"] for c in l1ind if c["source"] == "blind_frozen" and c["case_id"].startswith("B")}
    c_ids = {c["case_id"] for c in l1ind if c["source"] == "blind_frozen" and c["case_id"].startswith("C")}
    l1_by = {}
    for r in l1:
        l1_by.setdefault(r["method"], []).append(r)
    fs1 = {(r["case_id"]): (r["predicted"] == r["gold_risk"]) for r in l1_by["full_system"]}
    b_ok = sum(1 for k in b_ids if fs1.get(k) is True)
    c_ok = sum(1 for k in c_ids if fs1.get(k) is True)
    out["blind_split"] = {
        "blind1_B_20": {"correct": b_ok, "acc4": b_ok / 20},
        "blind2_C_20": {"correct": c_ok, "acc4": c_ok / 20},
    }

    # ── 5) 置信区间 ──
    out["cis"] = {
        "l1_full_system_acc4_108_118_wilson": wilson(108, 118),
        "l1_full_system_sens_28_28_wilson": wilson(28, 28),
        "audit_full_system_acc4_65_92_wilson": wilson(65, 92),
        "audit_sens_11_25_wilson": wilson(11, 25),
        "blind_frozen_40_40_cp": clopper_pearson(40, 40),
        "blind1_20_20_cp": clopper_pearson(20, 20),
    }
    # kappa bootstrap over real L1 case pairs (full_system vs gold, 118 cases)
    l1gold = [r["gold_risk"] for r in l1_by["full_system"]]
    l1pred = [r["predicted"] for r in l1_by["full_system"]]
    out["cis"]["l1_kappa_boot95"] = kappa_bootstrap(l1pred, l1gold)
    out["cis"]["l1_kappa_point"] = round(cohen_kappa(l1pred, l1gold), 4)

    print(json.dumps(out, indent=2, ensure_ascii=False))
    (ROOT / "outputs/revision_r1_stats.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nsaved: outputs/revision_r1_stats.json")


if __name__ == "__main__":
    main()
