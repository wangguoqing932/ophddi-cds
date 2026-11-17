#!/usr/bin/env python3
"""build_release_package.py — 生成"下载即用"的发布包（论文 supplementary / 审稿人试用）。

打包内容：
  src/ configs/ app/           代码
  data/seed|datasets|manifest  数据 + 证据
  data/processed/lightrag_index  LightRAG 索引（Chat 检索必需，246M）
  outputs/demo/                演示案例（Screening 一键填充）
  requirements.txt 启动脚本    README（中文步骤）
排除：.git .venv outputs 其余 .executor __pycache__ .env（密钥不进包）
"""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "dist" / "ophthalmic_ddi_cds_release"

INCLUDE_DIRS = ["src", "configs", "app"]
INCLUDE_DATA = ["seed", "datasets", "manifest", "processed/lightrag_index"]
INCLUDE_FILES = ["pyproject.toml", ".env.example"]
INCLUDE_OUTPUT = ["demo"]

EXCLUDE_PATTERNS = {"__pycache__", ".venv", ".git", ".pytest_cache", "*.pyc"}


def should_exclude(rel: Path) -> bool:
    return any(part in EXCLUDE_PATTERNS or str(part).endswith(".pyc") for part in rel.parts)


def main() -> None:
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.mkdir(parents=True)

    # 代码目录
    for d in INCLUDE_DIRS:
        src = ROOT / d
        if src.exists():
            shutil.copytree(src, RELEASE / d, ignore=shutil.ignore_patterns(*EXCLUDE_PATTERNS))

    # 数据
    for d in INCLUDE_DATA:
        src = ROOT / "data" / d
        if src.exists():
            shutil.copytree(src, RELEASE / "data" / d)

    # 演示输出
    for d in INCLUDE_OUTPUT:
        src = ROOT / "outputs" / d
        if src.exists():
            shutil.copytree(src, RELEASE / "outputs" / d)

    # 单文件
    for f in INCLUDE_FILES:
        src = ROOT / f
        if src.exists():
            shutil.copy2(src, RELEASE / f)

    # requirements.txt（pyproject dependencies + 运行所需）
    import tomllib
    with open(ROOT / "pyproject.toml", "rb") as f:
        deps = tomllib.load(f)["project"]["dependencies"]
    extra = ["streamlit>=1.36", "rank-bm25>=0.2.2"]
    req = "\n".join(deps + extra) + "\n"
    (RELEASE / "requirements.txt").write_text(req, encoding="utf-8")

    # 启动脚本
    (RELEASE / "start.bat").write_text(
        '@echo off\r\ncd /d %~dp0\r\nwhere python >nul 2>nul || (echo [错误] 未找到 Python，请先安装 Python 3.11 并勾选 Add to PATH & pause & exit /b 1)\r\n'
        'if not exist .venv (python -m venv .venv)\r\ncall .venv\\Scripts\\activate.bat\r\n'
        'python -m pip install -r requirements.txt -q\r\n'
        'python -m streamlit run app/streamlit_app.py\r\n',
        encoding="utf-8")
    (RELEASE / "start.sh").write_text(
        '#!/usr/bin/env bash\ncd "$(dirname "$0")"\n'
        'if [ ! -d .venv ]; then python3 -m venv .venv; fi\n'
        'source .venv/bin/activate\npip install -r requirements.txt -q\n'
        'streamlit run app/streamlit_app.py\n',
        encoding="utf-8")
    (RELEASE / "README.md").write_text(
        """# 眼科药物相互作用临床决策支持系统 — 试用包

## 快速开始（3 步）

1. **安装 Python 3.11**（https://www.python.org/downloads/ ，安装时勾选 "Add to PATH"）
2. **双击 `start.bat`**（Windows）或运行 `./start.sh`（Mac/Linux）——首次运行自动安装依赖（约 2-5 分钟）
3. 浏览器自动打开 **http://localhost:8501** 即可试用

## 试用内容

| 模块 | 功能 | 是否需要 API key |
|---|---|---|
| 📊 项目介绍 | 系统架构 + 知识库/规则引擎状态 | 否 |
| 🔍 风险评估 | 选择眼科药 × 全身药 → 风险等级 + 依据（40 条规则 + 类矩阵 + 吸收分级）| **否（完全离线）** |
| 💬 RAG 问答 | 知识库检索 → AI 回答 | 可选（无 key 时展示检索证据）|

## 可选：启用完整 AI 问答

将项目根目录的 `.env.example` 复制为 `.env`，填入：
- `DEEPSEEK_API_KEY`（DeepSeek API 密钥）→ 重启应用即可

## 提示

- 风险评估页有「🎯 演示案例一键填充」：Timolol×Verapamil（高危）、Ketorolac×Warfarin（中危）、Cyclosporine×Itraconazole（低危）等 8 个案例
- 数据：113 种眼科局部用药 × 229 种全身用药；1307 条已核验证据；40 条带引文规则

## 问题反馈

欢迎将使用中发现的问题发送至项目作者。
""",
        encoding="utf-8")

    # 打包 zip
    zip_path = ROOT / "dist" / "ophthalmic_ddi_cds_release.zip"
    if zip_path.exists():
        zip_path.unlink()
    total = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for f in sorted(RELEASE.rglob("*")):
            if f.is_file():
                total += f.stat().st_size
                zf.write(f, f.relative_to(RELEASE))
    print(f"release dir : {RELEASE}")
    print(f"release zip : {zip_path}  ({zip_path.stat().st_size/1024/1024:.1f} MB, 源 {total/1024/1024:.1f} MB)")


if __name__ == "__main__":
    main()
