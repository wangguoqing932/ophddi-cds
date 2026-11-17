# -*- coding: utf-8 -*-
"""fix_figure1_count.py — 修正图1标签 "Systemic drug B (229 agents)" -> "(232 agents)"。

背景：Figure 1 为 AI 生成光栅示意图，图内 agent 数量与实体注册表(113/232)及正文
不一致。本脚本从图内既有字形取 '2'（229 首位）与 '3'（"113" 第三位），以 alpha 蒙版
合成到目标数字格，保留原始字体与背景渐变；随后按 300 dpi 导出 png/pdf/tiff。

用法:
    python scripts/fix_figure1_count.py <pristine_original.png> [outdir]

必须显式给出未修正的原始 600 dpi 图（本仓库早期版本 outputs/figures/figure1_architecture.png，
可从 git 历史取回）。脚本对已修正图重复运行会破坏字形，因此不提供默认输入。
默认 outdir = outputs/figures；会覆盖其中的 figure1_architecture.{png,pdf,tiff}。
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "outputs" / "figures"

# 目标数字格（原图 5056x3392 坐标）: "229" 的三格
D1 = (3117, 3167)   # '2'（保留，并作为 '2' 字源）
D2 = (3178, 3228)   # '2' -> '3'
D3 = (3239, 3286)   # '9' -> '2'
Y0, Y1 = 354, 431   # 229 数字行带
SRC3 = (1599, 1646)  # "113" 的 '3'
SY0, SY1 = 423, 501


def fix(src: Path) -> Image.Image:
    im = Image.open(src).convert("RGB")
    arr = np.asarray(im).astype(np.float64)
    lum = np.asarray(im.convert("L")).astype(np.float64)
    out = arr.copy()

    def matte(x0, x1, y0, y1):
        l = lum[y0:y1 + 1, x0:x1 + 1]
        rgb = arr[y0:y1 + 1, x0:x1 + 1, :]
        bg, fg = np.percentile(l, 92), np.percentile(l, 3)
        alpha = np.clip((bg - l) / max(bg - fg, 1.0), 0, 1)
        k = alpha.ravel().argsort()[-max(1, alpha.size // 8):]
        return alpha, np.median(rgb.reshape(-1, 3)[k], axis=0)

    def erase(x0, x1, y0, y1):
        for y in range(y0 - 2, y1 + 3):
            l = out[y, x0 - 10:x0 - 4].mean(axis=0)
            r = out[y, x1 + 5:x1 + 11].mean(axis=0)
            n = x1 - x0 + 3
            for i in range(n):
                out[y, x0 - 1 + i] = l + (r - l) * (i / max(n - 1, 1))

    def paste(alpha, fg_rgb, cx, y_top, h):
        a = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).resize(
            (alpha.shape[1], h), Image.LANCZOS)).astype(np.float64) / 255.0
        x0 = cx - a.shape[1] // 2
        out[y_top:y_top + h, x0:x0 + a.shape[1]] = (
            out[y_top:y_top + h, x0:x0 + a.shape[1]] * (1 - a[..., None])
            + fg_rgb[None, None, :] * a[..., None])

    m2 = matte(*D1, Y0, Y1)
    m3 = matte(*SRC3, SY0, SY1)
    H = Y1 - Y0 + 1
    erase(*D2, Y0, Y1)
    erase(*D3, Y0, Y1)
    paste(m3[0], m3[1], (D2[0] + D2[1]) // 2, Y0, H)
    paste(m2[0], m2[1], (D3[0] + D3[1]) // 2, Y0, H)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def main():
    if len(sys.argv) < 2:
        sys.exit("需要未修正的原始图路径作为参数（避免对已修正图重复应用）")
    src = Path(sys.argv[1])
    outdir = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTDIR
    outdir.mkdir(parents=True, exist_ok=True)

    fixed = fix(src)
    # 统一到 300 dpi（与 Figure 2-5 一致）；原图 600 dpi 无必要，徒增体积
    w = 2528
    fixed = fixed.resize((w, round(fixed.height * w / fixed.width)), Image.LANCZOS)

    png = outdir / "figure1_architecture.png"
    fixed.save(png, optimize=True)
    fixed.save(outdir / "figure1_architecture.pdf", "PDF", resolution=300.0)
    fixed.save(outdir / "figure1_architecture.tiff", "TIFF", compression="tiff_lzw", dpi=(300, 300))
    print(f"fixed -> {png}  ({png.stat().st_size/1024/1024:.2f} MB, {fixed.size[0]}x{fixed.size[1]} @300dpi)")


if __name__ == "__main__":
    main()
