# -*- coding: utf-8 -*-
"""docx_to_pdf.py — 用本机 Word（COM）把 docx 导出为 PDF。

用法: python scripts/docx_to_pdf.py <input.docx> [output.pdf]
"""
import sys
from pathlib import Path

WD_FORMAT_PDF = 17


def main():
    src = Path(sys.argv[1]).resolve()
    dst = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.with_suffix(".pdf")
    if not src.exists():
        raise SystemExit(f"missing: {src}")

    import win32com.client as win32

    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(str(src), ReadOnly=True, AddToRecentFiles=False)
        doc.SaveAs(str(dst), FileFormat=WD_FORMAT_PDF)
        print(f"pdf -> {dst} ({dst.stat().st_size/1024/1024:.2f} MB)")
    finally:
        if doc is not None:
            try:
                doc.Close(SaveChanges=0)
            except Exception:
                pass
        try:
            word.Quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
