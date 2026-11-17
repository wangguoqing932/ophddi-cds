# -*- coding: utf-8 -*-
"""normalize_tiff.py — make every figure TIFF print-ready (RGB, LZW, 300 dpi).

Matplotlib writes RGBA TIFFs, and the Figure 6 export is an uncompressed
600-dpi RGB TIFF. Journals ask for RGB, LZW-compressed, >=300-dpi files, so
this pass flattens alpha onto white, converts to RGB, sets 300 dpi and
rewrites the file in place. Run after the figure scripts and before export.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"


def normalize(path: Path) -> tuple[str, int, int]:
    im = Image.open(path)
    before = im.mode
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    im.save(path, format="TIFF", compression="tiff_lzw", dpi=(300, 300))
    return before, im.size[0], im.size[1]


def main() -> None:
    for path in sorted(FIG.glob("figure*.tiff")):
        before, w, h = normalize(path)
        print(f"{path.name}: {before} -> RGB, LZW, 300 dpi, {w}x{h}, "
              f"{path.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
