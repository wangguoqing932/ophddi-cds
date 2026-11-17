#!/usr/bin/env python3
"""vision_lookup.py — 用智谱 GLM-4.6V-Flash 视觉模型查看图片/PDF（弥补 agent 视觉能力）。

用法:
  python scripts/vision_lookup.py <image_or_pdf_path> ["提示词，默认描述内容"]
输出: 模型对图片的文字描述（stdout）
"""
from __future__ import annotations

import base64
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

KEY = os.getenv("ZHIPU_API_KEY", "")
BASE = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
MODEL = os.getenv("ZHIPU_VISION_MODEL", "glm-4.6v-flash")


def image_to_b64(path: Path, max_side: int = 1400) -> str:
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side))
    import io
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def pdf_to_images(path: Path, max_side: int = 1400) -> list[bytes]:
    """用系统 python 的 pymupdf 渲染 PDF 页为 JPEG bytes。"""
    import subprocess
    code = f"""
import base64, io, sys
import pymupdf
doc = pymupdf.open(r"{path}")
out = []
for page in doc:
    pix = page.get_pixmap(dpi=110)
    im = pix.tobytes("png")
    sys.stdout.buffer.write(len(im).to_bytes(4, "big"))
    sys.stdout.buffer.write(im)
"""
    res = subprocess.run(
        [r"C:\Users\Administrator\AppData\Local\hermes\hermes-agent\.venv\Scripts\python.exe", "-c", code],
        capture_output=True)
    imgs = []
    buf = res.stdout
    off = 0
    while off + 4 <= len(buf):
        n = int.from_bytes(buf[off:off + 4], "big")
        off += 4
        imgs.append(buf[off:off + n])
        off += n
    return imgs


def call(text: str, img_b64: str, max_tokens: int = 600, retries: int = 8) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=KEY, base_url=BASE)
    last = None
    for a in range(retries):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}]}],
                max_tokens=max_tokens)
            return r.choices[0].message.content or "(空输出)"
        except Exception as e:
            last = e
            wait = min(30, 5 * (a + 1))
            print(f"[retry {a + 1}/{retries}] {type(e).__name__}: {str(e)[:80]} — 等 {wait}s", file=sys.stderr)
            time.sleep(wait)
    return f"FAILED: {last}"


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = Path(sys.argv[1])
    prompt = sys.argv[2] if len(sys.argv) > 2 else "请详细描述这张图片的内容：标题、结构、数据、文字。"
    if path.suffix.lower() == ".pdf":
        pages = pdf_to_images(path)
        print(f"[PDF {len(pages)} 页]", file=sys.stderr)
        for i, img in enumerate(pages, 1):
            b64 = base64.b64encode(img).decode()
            print(f"===== 第 {i} 页 =====")
            print(call(prompt, b64))
    else:
        b64 = image_to_b64(path)
        print(call(prompt, b64))


if __name__ == "__main__":
    main()
