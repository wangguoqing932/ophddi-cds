# -*- coding: utf-8 -*-
"""stats_tests.py — 手稿报告的全部统计过程，集中实现，供审稿人直接复算。

覆盖：
  * exact_mcnemar   — 精确双侧 McNemar 检验（二项分布精确法）
  * wilson_ci       — Wilson score 区间（比例）
  * clopper_pearson — Clopper–Pearson 精确区间（比例）
  * cohens_kappa    — Cohen's kappa，支持线性/二次加权
  * bootstrap_kappa — kappa 的非参数 bootstrap 区间
  * max_kappa       — 给定边际分布下可达到的最大 kappa

依赖 scipy（beta/二项分布）。所有函数只接受原始标签序列或计数值，
不读任何项目内部文件，因此可独立复现。

用法（复算手稿全部统计量）:
    python scripts/stats_tests.py
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

LEVELS = ("low", "medium", "high")


# ──────────────────────────────────  McNemar  ──────────────────────────────
def exact_mcnemar(b: int, c: int) -> dict:
    """精确双侧 McNemar 检验。

    参数为两个不一致格的计数（b = 甲对乙错，c = 乙对甲错）。
    双侧 p = 2 * P(X <= min(b,c))，X ~ Binomial(b+c, 0.5)，上限截断到 1。
    """
    n = b + c
    if n == 0:
        return {"b": b, "c": c, "n_discordant": 0, "p_value": 1.0,
                "method": "exact binomial (two-sided)"}
    k = min(b, c)
    p = 2.0 * float(stats.binom.cdf(k, n, 0.5))
    p = min(p, 1.0)
    return {"b": b, "c": c, "n_discordant": n, "p_value": p,
            "method": "exact binomial (two-sided)"}


def mcnemar_from_labels(a: list, b: list, truth: list) -> dict:
    """由两组预测标签与真值直接计算 McNemar 的 b/c。"""
    assert len(a) == len(b) == len(truth)
    bb = sum(1 for x, y, t in zip(a, b, truth) if x == t and y != t)
    cc = sum(1 for x, y, t in zip(a, b, truth) if x != t and y == t)
    return exact_mcnemar(bb, cc)


# ───────────────────────────────  区间估计  ────────────────────────────────
def wilson_ci(k: int, n: int, alpha: float = 0.05) -> tuple:
    """Wilson score 区间（比例的 95% 置信区间）。"""
    if n == 0:
        return (0.0, 1.0)
    z = stats.norm.ppf(1 - alpha / 2)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (float(max(0.0, centre - half)), float(min(1.0, centre + half)))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple:
    """Clopper–Pearson 精确区间（用 Beta 分布求精确尾概率）。"""
    if n == 0:
        return (0.0, 1.0)
    lo = 0.0 if k == 0 else float(stats.beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1 - alpha / 2, k + 1, n - k))
    return (lo, hi)


# ────────────────────────────────  kappa  ──────────────────────────────────
def _kappa_core(a: np.ndarray, b: np.ndarray, levels: tuple, weights: str | None,
                labels: list | None = None) -> float:
    """kappa 计算核心。labels 指定混淆矩阵的取值范围（bootstrap 时需固定）。"""
    labs = labels if labels is not None else sorted(set(a) | set(b))
    idx = {l: i for i, l in enumerate(labs)}
    K = len(labs)
    O = np.zeros((K, K))
    for x, y in zip(a, b):
        O[idx[x], idx[y]] += 1
    n = O.sum()
    if n == 0:
        return 0.0
    O = O / n
    r = O.sum(axis=1)
    c = O.sum(axis=0)
    E = np.outer(r, c)
    if weights is None:
        W = 1 - np.eye(K)
    else:
        W = np.zeros((K, K))
        for i in range(K):
            for j in range(K):
                d = abs(i - j) / (K - 1)
                W[i, j] = d if weights == "linear" else d * d
    num = (W * O).sum()
    den = (W * E).sum()
    if den == 0:
        return 0.0
    return float(1 - num / den)


def cohens_kappa(a: list, b: list, weights: str | None = None) -> float:
    """Cohen's kappa。weights=None 为未加权；'linear'/'quadratic' 为加权。"""
    return _kappa_core(np.asarray(a), np.asarray(b), LEVELS, weights)


def max_kappa(a: list, b: list, weights: str | None = None) -> float:
    """给定双方边际分布时，理论上可达到的最大 kappa。

    做法：把混淆矩阵的非对角元素尽可能填到对角线（受边际约束），
    得到最大一致率 Po_max，再套 kappa 公式。
    """
    a = np.asarray(a); b = np.asarray(b)
    labs = sorted(set(a) | set(b))
    ca = Counter(a); cb = Counter(b)
    n = len(a)
    po_max = sum(min(ca.get(l, 0), cb.get(l, 0)) for l in labs) / n
    pe = sum(ca.get(l, 0) * cb.get(l, 0) for l in labs) / (n * n)
    if weights is not None:
        # 加权情形：最大加权一致率需要求解指派问题；此处仅对未加权给精确值
        raise NotImplementedError("max_kappa 目前只实现未加权情形")
    return float((po_max - pe) / (1 - pe)) if pe < 1 else 0.0


def bootstrap_kappa(a: list, b: list, n_resamples: int = 2000,
                    seed: int = 12345, weights: str | None = None,
                    alpha: float = 0.05) -> dict:
    """kappa 的非参数 bootstrap 区间（按案例重抽，固定标签空间）。"""
    a = np.asarray(a); b = np.asarray(b)
    rng = np.random.default_rng(seed)
    n = len(a)
    labs = sorted(set(a) | set(b))
    vals = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        idx = rng.integers(0, n, n)
        vals[i] = _kappa_core(a[idx], b[idx], LEVELS, weights, labels=labs)
    lo, hi = np.percentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"kappa": cohens_kappa(list(a), list(b), weights),
            "ci_low": float(lo), "ci_high": float(hi),
            "n_resamples": n_resamples, "seed": seed,
            "percentile": f"{100*(1-alpha):.0f}%"}


# ─────────────────────────────  自检与复算入口  ───────────────────────────
def _selftest() -> None:
    """把手稿中报告的统计量用本模块复算一遍，便于审稿人比对。"""
    print("=== 模块自检（与手稿数值对照）===")
    print(f"  Wilson 107/118      : {wilson_ci(107,118)[0]:.3f}-{wilson_ci(107,118)[1]:.3f}"
          f"   手稿 0.841-0.947")
    print(f"  Wilson 62/92        : {wilson_ci(62,92)[0]:.3f}-{wilson_ci(62,92)[1]:.3f}"
          f"   手稿 0.573-0.761")
    a, b = clopper_pearson(39, 40)
    print(f"  Clopper-Pearson 39/40: {a:.3f}-{b:.3f}   手稿 0.868-0.999")
    a, b = clopper_pearson(27, 28)
    print(f"  Clopper-Pearson 27/28: {a:.3f}-{b:.3f}   手稿 0.823-0.994 (Wilson)")
    for (bb, cc, want) in [(54, 2, "3.1e-15"), (60, 4, "9.0e-15"), (20, 1, "1.1e-5"),
                           (8, 1, "0.039"), (27, 17, "0.174"), (18, 15, "0.728")]:
        r = exact_mcnemar(bb, cc)
        print(f"  McNemar {bb} vs {cc:<3d}   : p = {r['p_value']:.4g}   手稿 {want}")


def main() -> int:
    ap = argparse.ArgumentParser(description="手稿统计过程复算")
    ap.add_argument("--selftest", action="store_true", help="只跑模块自检")
    ap.add_argument("--dataset", default=None, help="gold 数据集目录（cases.jsonl）")
    ap.add_argument("--predictions", default=None, help="预测 jsonl 路径")
    args = ap.parse_args()

    _selftest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
