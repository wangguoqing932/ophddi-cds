# -*- coding: utf-8 -*-
"""export_deliverables.py — 由 outputs/paper/manuscript.en.md 生成交付用 manuscript.md。

补齐 docx 构建时才注入的两处内容：作者块（finalize_docx2.AUTHORS）与资助信息
（finalize_docx2.FUNDING），使 md 交付件与 docx 完全一致。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from finalize_docx2 import AUTHORS, FUNDING  # noqa: E402

SRC = ROOT / "outputs" / "paper" / "manuscript.en.md"
DST = ROOT / "outputs" / "deliverables" / "manuscript.md"
FUND_PLACEHOLDER = "[To be completed. If none, state: This research received no specific grant from any funding agency.]"


def main():
    text = SRC.read_text(encoding="utf-8")

    author_block = "\n\n".join(AUTHORS)
    if "## Authors\n\n## Abstract" in text:
        text = text.replace("## Authors\n\n## Abstract",
                            f"## Authors\n\n{author_block}\n\n## Abstract", 1)
    elif "## Authors" in text:
        raise SystemExit("unsupported Authors section layout — check source md")

    # 源手稿应已含真实基金声明（干净源文件是目标状态）；旧版曾留模板占位符，
    # 这里两种都接受，只要最终文本里确有正确内容即可。
    if FUND_PLACEHOLDER in text:
        text = text.replace(FUND_PLACEHOLDER, FUNDING, 1)
    elif FUNDING[:40] not in text:
        raise SystemExit("funding statement missing from source manuscript")

    for marker in ("Wang Guoqing", FUNDING[:40]):
        if marker not in text:
            raise SystemExit(f"post-check failed: {marker!r} missing")

    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(text, encoding="utf-8")
    print(f"wrote {DST}  ({len(text)} chars, {text.count(chr(10)) + 1} lines)")


if __name__ == "__main__":
    main()
