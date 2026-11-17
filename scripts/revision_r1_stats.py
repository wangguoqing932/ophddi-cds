# -*- coding: utf-8 -*-
"""revision_r1_stats.py — Reviewer 1 修订所需的全部统计量。

输出 outputs/recomputed/revision_r1_stats.json，供正文、补充材料与回复稿引用。
只读取仓库中已冻结的数据与预测文件，不修改任何分级或标签。

覆盖：
  R1-1  118 例参考集：冻结标签为主分析；40 例无开发暴露子集；kappa/Wilson CI
  R1-3  1,933 对路径归因；default-low（未评估）与 G19/矩阵/规则分流；低吸收越级
  R1-4  104 个局部滴眼剂复算；9 个非局部制剂单列；复方制剂清单
  R1-5  审计集 applied / re-derived 双标签完整指标；62 例保留子集；26 例检索泄漏
  R1-7  足额预算基线的 high 预测计数与多数票区间
"""
from __future__ import annotations

import csv
import json
import math
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG  # noqa: E402

LEVELS = ["low", "medium", "high"]
LEVEL_MAP = {"major": "high", "moderate": "medium", "minor": "low", "unknown": None}
SEV = {"high": 3, "medium": 2, "low": 1}


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [None, None]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(c - h, 3), round(c + h, 3)]


def kappa(a: list[str], b: list[str], weighted: bool = False) -> float:
    n = len(a)
    obs = sum(x == y for x, y in zip(a, b)) / n
    if weighted:
        wmax = 2
        exp_w = obs_w = 0.0
        for i, x in enumerate(LEVELS):
            for j, y in enumerate(LEVELS):
                wij = 1 - (abs(i - j) / wmax) ** 2
                pa, pb = a.count(x) / n, b.count(y) / n
                exp_w += pa * pb * wij
                obs_w += sum(1 for u, v in zip(a, b) if u == x and v == y) / n * wij
        return (obs_w - exp_w) / (1 - exp_w) if exp_w != 1 else 0.0
    exp = sum((a.count(lv) / n) * (b.count(lv) / n) for lv in LEVELS)
    return (obs - exp) / (1 - exp) if exp != 1 else 0.0


def binary_metrics(y: list[str], p: list[str]) -> dict:
    n = len(y)
    correct = sum(a == b for a, b in zip(y, p))
    hi = [i for i, g in enumerate(y) if g == "high"]
    tp = sum(p[i] == "high" for i in hi)
    non = [i for i, g in enumerate(y) if g != "high"]
    tn = sum(p[i] != "high" for i in non)
    return {
        "n": n,
        "correct": correct,
        "agreement": round(correct / n, 4),
        "agreement_ci": wilson(correct, n),
        "high_n": len(hi),
        "high_tp": tp,
        "sensitivity": round(tp / len(hi), 4) if hi else None,
        "nonhigh_n": len(non),
        "specificity": round(tn / len(non), 4) if non else None,
        "kappa": round(kappa(y, p), 4),
        "quadratic_weighted_kappa": round(kappa(y, p, weighted=True), 4),
    }


def temperature_mean_fields(rows: list[tuple[str, list[str]]]) -> dict:
    """Mean over the five temperature conditions, matching Table 3."""
    per = []
    for i in range(5):
        per.append(binary_metrics([g for g, _ in rows],
                                  [vs[i] for _, vs in rows]))
    return {
        "temperature_mean_agreement": round(st.mean(x["agreement"] for x in per), 4),
        "temperature_mean_sensitivity": round(st.mean(x["sensitivity"] for x in per), 4),
        "temperature_mean_specificity": round(st.mean(x["specificity"] for x in per), 4),
        "temperature_mean_kappa": round(st.mean(x["kappa"] for x in per), 4),
    }


def load_preds(dataset: str, methods: list[str]) -> dict:
    """method -> case_id -> list of predicted labels across the five temperature files."""
    out: dict[str, dict[str, list[str]]] = {m: defaultdict(list) for m in methods}
    for seed in range(5):
        path = ROOT / "outputs" / "multiseed_per_dataset" / f"{dataset}__seed{seed}.jsonl"
        for line in path.open(encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            if r["method"] in out:
                out[r["method"]][r["case_id"]].append(r["predicted"])
    return out


def seed0_rows(dataset: str, method: str) -> list[dict]:
    path = ROOT / "outputs" / "multiseed_per_dataset" / f"{dataset}__seed0.jsonl"
    return [r for r in (json.loads(l) for l in path.open(encoding="utf-8") if l.strip())
            if r["method"] == method]


def main() -> int:
    out: dict = {}
    kg = PreciseKG()

    # ── L1: frozen vs corrected labels ──
    prov = {r["case_id"]: r for r in csv.DictReader(
        (ROOT / "outputs/recomputed/l1_gold_provenance.csv").open(encoding="utf-8"))}
    l1 = load_preds("blind_l1", ["full_system", "pure_llm", "naive_rag", "lightrag"])
    l1_seed0 = seed0_rows("blind_l1", "full_system")
    subset_of = {r["case_id"]: r["subset"] for r in l1_seed0}
    errata = [{"case_id": k, "current": v["gold_current"], "frozen": v["gold_pre_errata"]}
              for k, v in prov.items() if v["gold_pre_errata"]]

    def l1_metrics(method: str, label: str, subset: str | None = None) -> dict:
        rows = []
        for cid, votes in l1[method].items():
            if subset and subset_of.get(cid) != subset:
                continue
            if label == "frozen":
                g = prov[cid]["gold_pre_errata"] or prov[cid]["gold_current"]
            else:
                g = prov[cid]["gold_current"]
            # deterministic system; baselines are averaged over the five temperature files
            scores = [int(v == g) for v in votes]
            rows.append((g, votes))
        y = [g for g, _ in rows]
        # mean agreement across temperatures, and majority-vote agreement
        mean_acc = sum(sum(int(v == g) for v in vs) / len(vs) for g, vs in rows) / len(rows)
        maj = [Counter(vs).most_common(1)[0][0] for _, vs in rows]
        m = binary_metrics(y, maj)
        m["temperature_mean_agreement"] = round(mean_acc, 4)
        m.update(temperature_mean_fields(rows))
        return m

    out["R1_1_l1"] = {
        "errata": errata,
        "corrected": {m: l1_metrics(m, "current") for m in l1},
        "frozen": {m: l1_metrics(m, "frozen") for m in l1},
        "frozen_blind40": l1_metrics("full_system", "frozen", "blind_frozen"),
        "frozen_guideline58": l1_metrics("full_system", "frozen", "guideline_sourced"),
        "frozen_T1_20": l1_metrics("full_system", "frozen", "T1_literature_consensus"),
        "corrected_blind40": l1_metrics("full_system", "current", "blind_frozen"),
    }

    # ── DDInter 1,933: path attribution, route restriction, unassessed ──
    ddinter = {}
    for code in ["A", "B", "C", "N", "S"]:
        with (ROOT / f"data/raw/ddinter/ddinter_code_{code}.csv").open(encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                a, b = row["Drug_A"].strip().lower(), row["Drug_B"].strip().lower()
                ddinter[(a, b)] = row["Level"]
                ddinter[(b, a)] = row["Level"]
    route = {r["primary_name"].lower(): r["ophthalmic_administration"] for r in csv.DictReader(
        (ROOT / "data/seed/entities_a.csv").open(encoding="utf-8-sig"))}
    combo = {r["primary_name"].lower(): (r.get("components") or "")
             for r in csv.DictReader((ROOT / "data/seed/entities_a.csv").open(encoding="utf-8-sig"))
             if "/" in r["primary_name"] or "+" in r["primary_name"]}

    pairs = []
    for an in kg.a_registry:
        for bn in kg.b_registry:
            di = ddinter.get((an.lower(), bn.lower()))
            dl = LEVEL_MAP.get(di.lower()) if di else None
            if dl is None:
                continue
            lvl, rules, info = kg.deterministic_level_v2(an, bn)
            pairs.append({"a": an, "b": bn, "ddinter": dl, "system": lvl,
                          "path": info.get("path"), "rules": rules,
                          "route": route.get(an.lower()), "tier": next(
                              (f for f in kg.a_registry[an]["flags"] if "absorption" in f), None)})

    def pair_summary(rows: list[dict]) -> dict:
        n = len(rows)
        if n == 0:
            return {"n": 0, "agree": 0, "downgrade": 0, "upgrade": 0,
                    "downgrade_share": None, "low_absorption_downgrades": 0,
                    "share_of_downgrades": None, "from_high": 0}
        down = sum(SEV[r["system"]] < SEV[r["ddinter"]] for r in rows)
        up = sum(SEV[r["system"]] > SEV[r["ddinter"]] for r in rows)
        agree = n - down - up
        low_abs = {"systemic_absorption_low", "systemic_absorption_very_low",
                   "minimal_systemic_absorption", "systemic_absorption_none"}
        low_down = sum(1 for r in rows if SEV[r["system"]] < SEV[r["ddinter"]]
                       and r["tier"] in low_abs)
        from_high = sum(1 for r in rows if r["ddinter"] == "high"
                        and SEV[r["system"]] < 3)
        return {
            "n": n, "agree": agree, "downgrade": down, "upgrade": up,
            "downgrade_share": round(down / n, 4),
            "low_absorption_downgrades": low_down,
            "share_of_downgrades": round(low_down / down, 4) if down else None,
            "from_high": from_high,
        }

    out["R1_3_paths_1933"] = {
        "all": pair_summary(pairs),
        "by_path": dict(Counter(r["path"] for r in pairs)),
        "by_path_level": {f"{p}|{l}": c for (p, l), c in
                          Counter((r["path"], r["system"]) for r in pairs).items()},
        "default_low_pairs": [{"a": r["a"], "b": r["b"], "ddinter": r["ddinter"]}
                              for r in pairs if r["path"] == "default_low"],
        "assessed_only": pair_summary([r for r in pairs if r["path"] != "default_low"]),
    }
    low_tier_nonlow = [r for r in pairs if r["tier"] in
                       {"systemic_absorption_low", "systemic_absorption_very_low",
                        "minimal_systemic_absorption", "systemic_absorption_none"}
                       and r["system"] in ("medium", "high")]
    out["R1_3_low_tier_overrides"] = {
        "n": len(low_tier_nonlow),
        "by_level": dict(Counter(r["system"] for r in low_tier_nonlow)),
        "by_rule": dict(Counter(rule for r in low_tier_nonlow for rule in r["rules"]).most_common()),
    }

    topical = [r for r in pairs if r["route"] == "topical"]
    out["R1_4_route"] = {
        "topical": pair_summary(topical),
        "non_topical": pair_summary([r for r in pairs if r["route"] != "topical"]),
        "non_topical_agents": sorted({r["a"] for r in pairs if r["route"] != "topical"}),
        "combination_products_in_pairs": sorted({r["a"] for r in pairs if r["a"] in combo}),
        "combination_products_registry": combo,
    }

    # ── Audit 92: applied vs re-derived ──
    audit = {c["case_id"]: c for c in json.load(
        (ROOT / "outputs/blind_test/blind_set_v3_ddinter.json").open(encoding="utf-8"))}
    rederived = {c["case_id"]: c["gold_rederived"] for c in json.load(
        (ROOT / "outputs/recomputed/audit_gold_rederived.json").open(encoding="utf-8"))["changed_cases"]}
    leak = json.load((ROOT / "outputs/recomputed/naive_rag_leakage.json").open(encoding="utf-8"))
    leak26 = set(leak["subsets"][2]["cases"])
    kept62 = {cid for cid, c in audit.items() if c["proposed_gold"] == c["ddinter_level"]}

    a_preds = load_preds("blind_v3_ddinter", ["full_system", "pure_llm", "naive_rag", "lightrag"])

    def audit_metrics(method: str, label: str, ids: set[str] | None = None) -> dict:
        rows = []
        for cid, votes in a_preds[method].items():
            if ids is not None and cid not in ids:
                continue
            g = audit[cid]["proposed_gold"] if label == "applied" else rederived.get(
                cid, audit[cid]["proposed_gold"])
            rows.append((g, votes))
        y = [g for g, _ in rows]
        p = [Counter(votes).most_common(1)[0][0] for _, votes in rows]
        m = binary_metrics(y, p)
        m.update(temperature_mean_fields(rows))
        return m

    out["R1_5_audit"] = {
        "applied": {m: audit_metrics(m, "applied") for m in a_preds},
        "rederived": {m: audit_metrics(m, "rederived") for m in a_preds},
        "kept62_applied": {m: audit_metrics(m, "applied", kept62) for m in a_preds},
        "kept62_rederived": {m: audit_metrics(m, "rederived", kept62) for m in a_preds},
        "excl26_applied": {m: audit_metrics(m, "applied", set(audit) - leak26) for m in a_preds},
        "excl26_rederived": {m: audit_metrics(m, "rederived", set(audit) - leak26) for m in a_preds},
        "leakage": leak,
        "n_kept62": len(kept62),
    }

    # Per-case disagreement classification for the applied gold
    dis = []
    for r in seed0_rows("blind_v3_ddinter", "full_system"):
        if r["predicted"] == r["gold_risk"]:
            continue
        c = audit[r["case_id"]]
        lvl, rules, info = kg.deterministic_level_v2(r["a_name"], r["b_name"])
        tier = next((f for f in kg.get_ophthalmic(r["a_name"])["flags"] if "absorption" in f), None)
        direction = ("upgrade" if SEV[r["predicted"]] > SEV[r["gold_risk"]] else "downgrade")
        # classification rule stated in the manuscript: a downgrade of a high-tier
        # agent through a matrix/default path is "unsupported undergrading"; every
        # other downgrade is route-consistent by construction of the tier.
        cls = ("unsupported_undergrading"
               if direction == "downgrade" and tier == "systemic_absorption_high"
               else "route_consistent_downgrade" if direction == "downgrade"
               else "system_overgrading")
        dis.append({"case_id": r["case_id"], "a": r["a_name"], "b": r["b_name"],
                    "ddinter": c["ddinter_level"], "gold": r["gold_risk"],
                    "system": r["predicted"], "tier": tier, "path": info.get("path"),
                    "rules": rules, "direction": direction, "class": cls})
    out["R1_5_disagreements"] = {
        "n": len(dis),
        "by_class": dict(Counter(d["class"] for d in dis)),
        "cases": dis,
    }

    # ── Adequate-budget baselines (R1-6, R1-7) ──
    glm = [json.loads(l) for l in (ROOT / "outputs/glm53_baselines/predictions.jsonl").open(encoding="utf-8") if l.strip()]
    ab: dict = {}
    for ds in ["blind_l1", "blind_v3_ddinter"]:
        ab[ds] = {}
        for m in ["pure_llm", "naive_rag", "lightrag"]:
            rows = [r for r in glm if r["dataset"] == ds and r["method"] == m]
            by_case: dict[str, list[str]] = defaultdict(list)
            for r in rows:
                by_case[r["case_id"]].append(r["pred"])
            high_cases = sorted({r["case_id"] for r in rows if r["gold"] == "high"})
            maj = {cid: Counter(v).most_common(1)[0][0] for cid, v in by_case.items()}
            high_pred = sum(1 for v in maj.values() if v == "high")
            tp = sum(1 for cid in high_cases if maj.get(cid) == "high")
            ab[ds][m] = {
                "n_cases": len(by_case),
                "high_gold": len(high_cases),
                "high_predicted_majority": high_pred,
                "high_predicted_pct": round(high_pred / len(by_case) * 100, 1),
                "tp_majority": tp,
                "sensitivity_majority": round(tp / len(high_cases), 3),
                "tp_range_per_rep": [min(sum(1 for c in high_cases if next(
                    (r["pred"] for r in rows if r["case_id"] == c and r["rep"] == rep), None) == "high")
                    for rep in sorted({r["rep"] for r in rows})),
                    max(sum(1 for c in high_cases if next(
                        (r["pred"] for r in rows if r["case_id"] == c and r["rep"] == rep), None) == "high")
                        for rep in sorted({r["rep"] for r in rows}))],
            }
    out["R1_6_7_adequate_budget"] = ab

    dst = ROOT / "outputs/recomputed/revision_r1_stats.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
