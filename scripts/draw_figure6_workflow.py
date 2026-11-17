# -*- coding: utf-8 -*-
"""draw_figure6_workflow.py — install the author-supplied Figure 6 design.

The journal figure is the supplied 1024 x 1536 design in
outputs/figures/source_images/figure6_workflow_design_2026-11-13.png.
This script trims the white margin, upsamples to 300 dpi at the print width
(147 mm), and writes PNG, TIFF (RGB/LZW), PDF and an SVG wrapper. It replaces
the earlier Matplotlib mock-up so a rebuild cannot silently restore the old
browser-screenshot design.
"""
from __future__ import annotations

import base64
import io
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"
SRC = FIG / "source_images" / "figure6_workflow_design_2026-11-13.png"
TARGET_WIDTH_PX = 1740          # 300 dpi at 147.3 mm
CROP = (0, 74, 1024, 1455)      # remove white page margin, keep breathing room


def main() -> None:
    im = Image.open(SRC).convert("RGB").crop(CROP)
    height = round(im.height * TARGET_WIDTH_PX / im.width)
    im = im.resize((TARGET_WIDTH_PX, height), Image.LANCZOS)

    im.save(FIG / "figure6_workflow.png", dpi=(300, 300))
    im.save(FIG / "figure6_workflow.tiff", compression="tiff_lzw", dpi=(300, 300))

    width_mm = TARGET_WIDTH_PX / 300 * 25.4
    height_mm = height / 300 * 25.4
    doc = fitz.open()
    page = doc.new_page(width=width_mm * 72 / 25.4, height=height_mm * 72 / 25.4)
    page.insert_image(fitz.Rect(0, 0, width_mm * 72 / 25.4, height_mm * 72 / 25.4),
                      filename=str(FIG / "figure6_workflow.png"))
    doc.save(FIG / "figure6_workflow.pdf", deflate=True, garbage=4)
    doc.close()

    buf = io.BytesIO()
    im.save(buf, format="PNG", dpi=(300, 300))
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_mm:.1f}mm" '
        f'height="{height_mm:.1f}mm" viewBox="0 0 {TARGET_WIDTH_PX} {height}">\n'
        f'<image width="{TARGET_WIDTH_PX}" height="{height}" '
        f'href="data:image/png;base64,{b64}"/>\n</svg>\n'
    )
    (FIG / "figure6_workflow.svg").write_text(svg, encoding="utf-8")
    print(f"figure6_workflow installed: {TARGET_WIDTH_PX}x{height} px, "
          f"{width_mm:.1f}x{height_mm:.1f} mm at 300 dpi")


if __name__ == "__main__":
    main()
