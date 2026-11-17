# -*- coding: utf-8 -*-
"""fix_figure1_labels.py — 修正 Figure 1 图内两处与正文不符的文字。

背景（两处都会被审稿人直接看到）：
  1. L1 说明原为 "40 citation-verified rules"。审稿人意见 2 指出 "citation-verified"
     与证据不符，正文已删除该措辞、回复信写明"该短语已在全文移除"；图内若保留原文，
     回复与图就会互相矛盾。改为 "40 mechanism rules"。
  2. L2 说明原为 "20 x 37 drug classes"。configs/class_matrix.yaml 与
     configs/drug_classes.yaml 实为 21 个眼科行键 × 40 个全身列键（使用 34 列，
     104 个显式单元格），正文与表注均已按 21/40/34/104 叙述，图内数字属于旧版本残留。

做法：不引入外部字体，所有字形都从同一张图内的同字号文本中提取（'m' 取自底部说明行，
'h' 取自 "chain"，'4' 取自同图的 "40"，'1' 取自 "(113 agents)"，其余取自目标行自身）。
按基线对齐后以 alpha 合成，字面、笔画粗细与抗锯齿观感与图内其他标签一致。

用法:
    python scripts/fix_figure1_labels.py <原始png> <输出png>
输入必须是未修改过的 figure1_architecture.png；本仓库中可从 git 历史取回：
    git show <首次提交>:outputs/figures/figure1_architecture.png > fig1_pristine.png
脚本可重复运行（始终从原始图开始），不会叠字。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

# ── 字形来源：(x0, x1, y0, y1, 源基线) ───────────────────────────────
# 字形与目标同字号（x-height 28 / 数字高 38-39），无需缩放。
G = {
    # 取自 L1 行自身
    "e2": (1095, 1118, 520, 548, 548),
    "c2": (888, 911, 520, 548, 548),
    "a2": (944, 966, 520, 548, 548),
    "n2": (1029, 1051, 520, 548, 548),
    "i2": (916, 922, 510, 548, 548),
    "s2": (1331, 1353, 520, 548, 548),
    "r2": (1248, 1261, 520, 548, 548),
    "u2": (1265, 1286, 520, 548, 548),
    "l2": (1293, 1298, 509, 548, 548),
    # 取自底部 "Deterministic" / "chain"
    "m2": (961, 1000, 1605, 1633, 1633),
    "h2": (1549, 1571, 1464, 1503, 1503),
    # 数字
    "4": (818, 845, 511, 548, 548),      # L1 的 "40"
    "1": (740, 755, 212, 251, 251),      # "(113 agents)"
    "2b": (819, 844, 796, 834, 834),     # L2 的 "20"
    "0b": (848, 872, 796, 834, 834),
    "xb": (888, 910, 806, 834, 834),     # L2 的 "x"
}

# ── 编辑一：L1 副标题 "40 citation-verified rules" -> "40 mechanism rules" ──
L1_ERASE = (876, 1362, 500, 557)
L1_TEXT = "mechanism rules"
L1_X = 888
L1_BASE = 548
L1_GAP, L1_SPACE = 4, 16
L1_GLYPHS = {c: c + "2" for c in "mechanismrules"}

# ── 编辑二：L2 副标题 "20 x 37" -> "21 x 40" ──
L2_ERASE = (815, 983, 790, 840)
L2_BASE = 834
L2_SEQ = [("2b", 4), ("1", 19), ("xb", 20), ("4", 4), ("0b", 0)]
L2_X = 819


def erase(arr: np.ndarray, x0: int, x1: int, y0: int, y1: int) -> None:
    """逐列抹掉文字带，用最近的干净背景像素插值填充。

    不能简单地取"文字带上下各几行"作插值源：标题的 g/y 等字母的下伸部分会落到
    文字带上方，被采样后会在擦除区里拖出一条竖直暗带。这里改为逐列向上/向下
    搜索最近的亮像素（背景），只用真正干净的行作端点。
    """
    lum = arr.mean(axis=2)
    h = y1 - y0
    for x in range(x0, x1):
        col = lum[:, x]
        # 向上找最近背景像素
        uy = None
        for y in range(y0 - 1, max(y0 - 40, 0), -1):
            if col[y] > 215.0 and col[y - 1] > 215.0 and col[y - 2] > 215.0:
                uy = y
                break
        # 向下找最近背景像素
        dy = None
        for y in range(y1, min(y1 + 40, col.size - 3)):
            if col[y] > 215.0 and col[y + 1] > 215.0 and col[y + 2] > 215.0:
                dy = y
                break
        if uy is None or dy is None:      # 兜底：整列取中位背景色
            arr[y0:y1, x] = np.median(arr[y0 - 30:y1 + 30, x], axis=0)
            continue
        top = arr[uy, x].astype(float)
        bot = arr[dy, x].astype(float)
        for i in range(h):
            w = (y0 + i - uy) / float(dy - uy)
            arr[y0 + i, x] = top * (1 - w) + bot * w


def glyph_alpha(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """由字形小图求 (笔画覆盖率 alpha, 墨色)。

    用分位数估计背景与最暗值：若用中位数，窄字母（'i'）会因墨占多数而把中位数
    误当背景，导致 alpha 失真。
    """
    g = rgb.mean(axis=2)
    bg = float(np.percentile(g, 95))
    ink_level = float(np.percentile(g, 1))
    if bg - ink_level < 1e-6:
        return np.zeros(g.shape), np.zeros(3)
    a = np.clip((bg - g) / (bg - ink_level), 0.0, 1.0)
    thr = np.percentile(g, 2)
    ink_rgb = rgb[g <= thr].reshape(-1, 3).mean(axis=0)
    return a, ink_rgb


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    src, dst = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    arr = np.asarray(Image.open(src).convert("RGB")).astype(float)

    cores = {}
    for ch, (x0, x1, y0, y1, bl) in G.items():
        cores[ch] = (*glyph_alpha(arr[y0:y1, x0:x1]), bl)

    out = arr.copy()

    # ── 编辑一 ──
    erase(out, *L1_ERASE)
    x = L1_X
    for i, ch in enumerate(L1_TEXT):
        if ch == " ":
            x += L1_SPACE
            continue
        if i and L1_TEXT[i - 1] != " ":
            x += L1_GAP
        key = L1_GLYPHS[ch]
        a, ink, bl = cores[key]
        _, _, gy0, _, _ = G[key]
        ty = gy0 + (L1_BASE - bl)
        a3 = a[..., None]
        out[ty:ty + a.shape[0], x:x + a.shape[1]] = (
            out[ty:ty + a.shape[0], x:x + a.shape[1]] * (1 - a3) + ink * a3)
        x += a.shape[1]

    # ── 编辑二 ──
    erase(out, *L2_ERASE)
    x = L2_X
    for ch, gap_after in L2_SEQ:
        a, ink, bl = cores[ch]
        _, _, gy0, _, _ = G[ch]
        ty = gy0 + (L2_BASE - bl)
        a3 = a[..., None]
        out[ty:ty + a.shape[0], x:x + a.shape[1]] = (
            out[ty:ty + a.shape[0], x:x + a.shape[1]] * (1 - a3) + ink * a3)
        x += a.shape[1] + gap_after

    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
    print(f"已写出 {dst}")
    print(f"  L1: '40 {L1_TEXT}'")
    print(f"  L2: '21 x 40'  结束 x={x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
