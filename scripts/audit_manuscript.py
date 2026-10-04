# -*- coding: utf-8 -*-
"""audit_manuscript.py — 手稿提交前的自动一致性审计。

背景：前两轮修订中，审稿人发现的问题（数字未同步、交叉引用断裂、图表未引用、
占位符残留、代码与文本描述不符）都是可以用脚本查出来的，但当时没有做。本脚本把
这些检查固化下来，作为提交前的最后一道闸门，也可由审稿人直接运行验证。

检查项：
  A. 交叉引用：Section X.Y / Table N / Figure N / Supplementary Table SN / Text SN
     是否都有定义，是否存在"定义了却从未被引用"
  B. 参考文献：编号连续性、悬空引用、定义未引用
  C. 占位符：TODO / TBD / {DOI} / XXX / FIXME 等
  D. 数字一致性：手稿中的关键数值是否能从 recomputed/numbers.json 复算得到
  E. 沉积文件：手稿/补充材料提到的仓库内路径是否真实存在
  F. 摘要长度：是否符合期刊限制
  G. 自洽性：同一指标在不同章节的取值是否一致

用法:
    python scripts/audit_manuscript.py               # 审计并打印报告
    python scripts/audit_manuscript.py --strict      # 有 FAIL 时以非零码退出
    python scripts/audit_manuscript.py --json out.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]

# 手稿在两种布局下的位置
MANUSCRIPT_CANDIDATES = [
    ROOT / "outputs" / "paper" / "manuscript.en.md",
    ROOT / "manuscript" / "manuscript.md",
]
SUPP_CANDIDATES = [
    ROOT / "outputs" / "deliverables" / "supplementary_files" / "Supplementary_Material.md",
    ROOT / "supplementary" / "Supplementary_Material.md",
]
LEGENDS_CANDIDATES = [
    ROOT / "outputs" / "paper" / "figure_legends.md",
    ROOT / "supplementary" / "figure_legends.md",
]
NUMBERS_CANDIDATES = [
    ROOT / "outputs" / "recomputed" / "numbers.json",
    ROOT / "audits" / "recomputed" / "numbers.json",
]

ABSTRACT_WORD_LIMIT = 350          # BMC Bioinformatics


def first_existing(paths) -> pathlib.Path | None:
    return next((p for p in paths if p.exists()), None)


class Audit:
    def __init__(self) -> None:
        self.findings: list[dict] = []

    def add(self, level: str, check: str, message: str, detail=None) -> None:
        self.findings.append({"level": level, "check": check,
                              "message": message, "detail": detail})

    def fail(self, check: str, msg: str, detail=None) -> None:
        self.add("FAIL", check, msg, detail)

    def warn(self, check: str, msg: str, detail=None) -> None:
        self.add("WARN", check, msg, detail)

    def ok(self, check: str, msg: str) -> None:
        self.add("OK", check, msg)

    @property
    def failures(self) -> list[dict]:
        return [f for f in self.findings if f["level"] == "FAIL"]

    @property
    def warnings(self) -> list[dict]:
        return [f for f in self.findings if f["level"] == "WARN"]


# ──────────────────────────────  A. 交叉引用  ──────────────────────────────
def check_crossrefs(text: str, supp: str, legends: str, a: Audit) -> None:
    check = "A.crossrefs"

    defined = set(re.findall(r"^#{2,4}\s+(\d+(?:\.\d+)?)[\.\s]", text, re.M))
    cited = set(re.findall(r"Section\s+(\d+(?:\.\d+)?)", text))
    dangling = sorted(cited - defined, key=lambda s: [int(x) for x in s.split(".")])
    if dangling:
        a.fail(check, f"正文引用了不存在的章节: {dangling}")
    else:
        a.ok(check, f"章节引用全部有效（{len(cited)} 个不同引用）")

    # 定义了但从未被引用的方法/结果小节（引言/结论类章节不引用属正常）
    never = sorted(defined - cited, key=lambda s: [int(x) for x in s.split(".")])
    substantive = [s for s in never if s.count(".") == 1 and s.split(".")[0] in ("2", "3")]
    if substantive:
        a.warn(check, f"方法/结果小节从未被交叉引用: {substantive}")

    # Table / Figure
    for label, pat in [("Table", r"Table\s+(\d)"), ("Figure", r"Figure\s+(\d)")]:
        found = sorted(set(re.findall(pat, text)))
        expected = [str(i) for i in range(1, (7 if label == "Table" else 6))]
        missing = [e for e in expected if e not in found]
        if missing:
            a.fail(check, f"{label} {missing} 在正文中从未被引用（图/表存在但正文不提）")
        else:
            a.ok(check, f"{label} 1-{expected[-1]} 均已在正文引用")

    # 补充材料：表必须都被引用；文本章节 S4（图注）/S7（缩略语）可不引用
    supp_tables = sorted(set(re.findall(r"Supplementary Table\s+S(\d)", supp)))
    cited_tables = sorted(set(re.findall(r"Supplementary Table\s+S(\d)", text)))
    uncited = [t for t in supp_tables if t not in cited_tables]
    if uncited:
        a.fail(check, f"补充表 S{', S'.join(uncited)} 已定义但正文从未引用")
    else:
        a.ok(check, f"补充表 S{supp_tables[0]}-S{supp_tables[-1]} 均已在正文引用")

    supp_texts = sorted(set(re.findall(r"Supplementary Text\s+S(\d)", supp)))
    cited_texts = sorted(set(re.findall(r"Supplementary Text\s+S(\d)", text)))
    # S4 是图注、S7 是缩略语，正文不引用属正常
    optional = {"4", "7"}
    unref = [t for t in supp_texts if t not in cited_texts and t not in optional]
    if unref:
        a.warn(check, f"补充文本 S{', S'.join(unref)} 已定义但正文未引用")
    else:
        a.ok(check, "补充文本引用正常")


# ──────────────────────────────  B. 参考文献  ──────────────────────────────
def check_references(text: str, a: Audit) -> None:
    check = "B.references"
    refs = re.findall(r"^\[(\d+)\]\s+\S", text, re.M)
    if not refs:
        a.fail(check, "未找到参考文献列表")
        return
    nums = sorted(int(x) for x in refs)
    expected = list(range(1, len(nums) + 1))
    if nums != expected:
        gaps = sorted(set(expected) - set(nums))
        dups = [n for n in set(nums) if nums.count(n) > 1]
        msg = []
        if gaps:
            msg.append(f"缺号 {gaps}")
        if dups:
            msg.append(f"重复 {dups}")
        a.fail(check, f"参考文献编号不连续: {'; '.join(msg)}")
    else:
        a.ok(check, f"参考文献编号连续 1-{len(nums)}")

    listed = set(str(n) for n in nums)
    body = text[:text.find("## References")] if "## References" in text else text
    cited = set(re.findall(r"\[(\d+(?:[,\-–]\s*\d+)*)\]", body))
    cited_flat = set()
    for grp in cited:
        for part in re.split(r",", grp):
            part = part.strip()
            if re.fullmatch(r"\d+", part):
                cited_flat.add(part)
            else:
                m = re.match(r"(\d+)\s*[-–]\s*(\d+)", part)
                if m:
                    cited_flat.update(str(i) for i in range(int(m.group(1)), int(m.group(2)) + 1))
    dangling = sorted(int(x) for x in cited_flat - listed)
    if dangling:
        a.fail(check, f"正文引用了不存在的文献编号: {dangling}")
    uncited = sorted(int(x) for x in listed - cited_flat)
    if uncited:
        a.warn(check, f"文献列表中有未被正文引用的条目: {uncited}")
    if not dangling and not uncited:
        a.ok(check, "所有引用与列表条目一一对应")


# ──────────────────────────────  C. 占位符  ──────────────────────────────
PLACEHOLDER_PATTERNS = [
    (r"\{DOI\}", "DOI 占位符（拿到 Zenodo DOI 后必须替换）"),
    (r"\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX\b", "待办标记"),
    (r"\[to be (?:inserted|completed|filled)[^\]]*\]", "待填占位"),
    (r"\[待[^\]]*\]", "中文待填占位"),
    (r"placeholder", "占位文本"),
    (r"⟨[^⟩]*⟩|<<[^>]*>>", "模板占位"),
]


def check_placeholders(text: str, supp: str, a: Audit, allow_doi: bool = True) -> None:
    check = "C.placeholders"
    hits = []
    for name, body in [("手稿", text), ("补充材料", supp)]:
        for pat, desc in PLACEHOLDER_PATTERNS:
            if allow_doi and pat == r"\{DOI\}":
                continue
            for m in re.finditer(pat, body, re.I):
                hits.append(f"{name}: {desc} -> {m.group()[:40]!r}")
    if hits:
        for h in hits:
            a.fail(check, h)
    else:
        a.ok(check, "未发现占位符残留")


def check_doi_present(text: str, a: Audit) -> None:
    """DOI 单独检查：允许占位，但要明确提示出来。"""
    check = "C.doi"
    if "{DOI}" in text:
        n = text.count("{DOI}")
        a.warn(check, f"手稿中仍有 {n} 处 DOI 占位符，提交前需替换为实际 DOI")
    else:
        dois = re.findall(r"10\.\d{4,9}/[^\s\)\]]+", text)
        a.ok(check, f"DOI 已填（发现 {len(dois)} 个 DOI 字串）")


# ───────────────────────────  D. 数字一致性  ───────────────────────────
# (正则, numbers.json 的键, 取值路径, 说明) —— 手稿中出现该数值即视为必须匹配
NUMBER_CHECKS = [
    (r"0\.907\b",            "l1.full_system",                  "acc3",  "L1 Acc3"),
    (r"0\.857\b",            "l1.kappa",                        None,    "L1 kappa"),
    (r"0\.964\b",            "l1.full_system",                  "sens",  "L1 sensitivity"),
    (r"0\.989\b",            "l1.full_system",                  "spec",  "L1 specificity"),
    (r"0\.674\b",            "audit.full_system",               "acc3",  "审计集 Acc3"),
    (r"0\.428\b",            "audit.kappa",                     None,    "审计集 kappa"),
    (r"0\.320\b",            "audit.full_system",               "sens",  "审计集 sensitivity"),
    (r"0\.955\b",            "audit.full_system",               "spec",  "审计集 specificity"),
    (r"0\.370\b",            "audit.agreement_uncorrected",     "rate",  "对未更正 DDInter 的一致率"),
    (r"0\.548\b",            "audit.stratum.kept(third-party)", "rate",  "第三方分级子集一致率"),
]

# 这些数值由专门脚本产出，单独核对（numbers.json 之外）
# 元组第三项是要从匹配文本中提取的数值位置：0=取第一个小数，1=取第二个小数
EXTRA_NUMBER_CHECKS = [
    (r"from 0\.907 to (0\.\d{3})", "rule_gating_experiment.json", "gate_single.accuracy",
     "门控单条 NSAID 规则后的 L1 一致率"),
    (r"lowers it to (0\.\d{3})",   "rule_gating_experiment.json", "gate_all_nsaid.accuracy",
     "门控全部 NSAID 规则后的 L1 一致率"),
]


def check_numbers(text: str, numbers: dict, a: Audit) -> None:
    check = "D.numbers"
    if not numbers:
        a.warn(check, "未找到 recomputed/numbers.json，跳过数字一致性检查")
        return
    bad = []
    for pat, key, field, desc in NUMBER_CHECKS:
        if not re.search(pat, text):
            continue                      # 手稿未使用该数值，跳过
        node = numbers.get(key)
        if node is None:
            bad.append(f"{desc}: numbers.json 缺少 {key}")
            continue
        want = node if field is None else node.get(field)
        if want is None:
            bad.append(f"{desc}: {key}.{field} 缺失")
            continue
        shown = float(re.search(pat, text).group())
        if abs(float(want) - shown) > 5e-4:
            bad.append(f"{desc}: 手稿 {shown} vs 复算 {float(want):.4f}")
    if bad:
        for b in bad:
            a.fail(check, b)
    else:
        a.ok(check, f"手稿中 {sum(1 for p, *_ in NUMBER_CHECKS if re.search(p, text))} "
                    f"个关键数值与复算结果一致")

    # 附加数值（由专门实验产出）
    recomputed = ROOT / "outputs" / "recomputed"
    if not recomputed.exists():
        recomputed = ROOT / "audits" / "recomputed"
    extra_bad = []
    for pat, fname, field, desc in EXTRA_NUMBER_CHECKS:
        m = re.search(pat, text)
        if not m:
            continue
        f = recomputed / fname
        if not f.exists():
            extra_bad.append(f"{desc}: 缺少 {fname}（实验未沉积，审稿人无法复算）")
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        node = data
        for key in field.split("."):
            node = node.get(key) if isinstance(node, dict) else None
        if node is None:
            extra_bad.append(f"{desc}: {fname} 中缺少 {field}")
            continue
        # 正则里的捕获组就是要比对的数值（可能是句子中的第二个小数）
        shown = float(m.group(1) if m.groups() else re.search(r"0\.\d{3}", m.group()).group())
        if abs(float(node) - shown) > 5e-4:
            extra_bad.append(f"{desc}: 手稿 {shown} vs 复算 {float(node):.4f}")
    for b in extra_bad:
        a.fail(check + ".extra", b)
    if not extra_bad and any(re.search(p, text) for p, *_ in EXTRA_NUMBER_CHECKS):
        a.ok(check + ".extra", "门控实验数值可由 rule_gating_experiment.py 复现")


# ───────────────────────────  E. 沉积文件存在性  ───────────────────────────
def check_deposited_paths(text: str, supp: str, a: Audit) -> None:
    check = "E.deposited"
    # 只检查看起来是仓库内相对路径的字符串
    pat = re.compile(r"`([a-zA-Z_][\w./-]*\.(?:py|yaml|yml|json|jsonl|csv|md|txt))`")
    mentioned = set()
    for body in (text, supp):
        for m in pat.finditer(body):
            p = m.group(1)
            if p.startswith(("http", "10.")):
                continue
            mentioned.add(p)

    # 查找根目录要覆盖两种发布布局：
    #   项目布局  : <root>/outputs/paper/...  <root>/data/...  <root>/scripts/...
    #   公开仓库  : <root>/manuscript/...     <root>/data/...  <root>/scripts/...
    # 另外手稿习惯用简写（如 kg_layer.py、prompts.yaml），需按文件名兜底搜索。
    roots = [ROOT]
    by_name: dict[str, list[pathlib.Path]] = {}
    for r in roots:
        for f in r.rglob("*"):
            if f.is_file() and ".git" not in f.parts:
                by_name.setdefault(f.name, []).append(f)

    missing = []
    for p in sorted(mentioned):
        if any((r / p).exists() for r in roots):
            continue
        # 兜底：按文件名在仓库中找同名文件
        if pathlib.Path(p).name in by_name:
            continue
        missing.append(p)
    if missing:
        for m in missing:
            a.warn(check, f"手稿/补充材料提到但仓库中找不到: {m}")
    else:
        a.ok(check, f"提到的 {len(mentioned)} 个文件路径均可定位")


# ──────────────────────────────  F. 摘要长度  ──────────────────────────────
def check_abstract(text: str, a: Audit, limit: int = ABSTRACT_WORD_LIMIT) -> None:
    check = "F.abstract"
    m = re.search(r"## Abstract\s*\n(.*?)(?=\n## )", text, re.S)
    if not m:
        a.fail(check, "未找到摘要区块")
        return
    n = len(m.group(1).split())
    if n > limit:
        a.fail(check, f"摘要 {n} 词，超过期刊上限 {limit}")
    elif n > limit - 10:
        a.warn(check, f"摘要 {n} 词，距上限 {limit} 仅 {limit - n} 词")
    else:
        a.ok(check, f"摘要 {n} 词（上限 {limit}）")


# ────────────────────────────  G. 内部自洽性  ────────────────────────────
def check_self_consistency(text: str, a: Audit) -> None:
    """同一数值若在正文多处出现，取值必须一致。"""
    check = "G.consistency"
    # 收集“同一指标不同写法”的候选：以指标关键词定位，检查数字
    rules = [
        ("L1 kappa 0.857 与 0.870 不应共存", [r"0\.857\b"], [r"kappa\s*0\.870\b"]),
        ("审计集 0.674 与 0.707 不应共存", [r"0\.674\b"], [r"0\.707\b"]),
        ("对 DDInter 0.370 与 0.402 不应共存", [r"0\.370\b"], [r"0\.402\b"]),
        ("层级 15 high 与 16 high 不应共存", [r"\b15 high\b"], [r"\b16 high\b"]),
        ("专家 kappa 0.840 与 0.846 不应共存", [r"0\.840\b"], [r"0\.846\b"]),
    ]
    bad = []
    for desc, keep_pats, stale_pats in rules:
        if all(re.search(p, text) for p in keep_pats) and any(re.search(p, text) for p in stale_pats):
            bad.append(desc)
    if bad:
        for b in bad:
            a.fail(check, f"新旧取值共存: {b}")
    else:
        a.ok(check, "未发现新旧数值共存")


def check_code_text_consistency(text: str, a: Audit) -> None:
    """核对"手稿描述的参数"与"代码里的实际取值"。

    审稿人上一轮正是从这类不一致里挑出问题的（L3 说四层实际两层、BM25 参数、
    推理模型预算）。把这些比较固化成断言，避免下次再靠人眼对。
    """
    check = "H.code_text"
    checks = []

    # 1) L3 硬约束实际测试的层级
    kg = ROOT / "src" / "ophthalmic_ddi_cds_agent" / "kg_layer.py"
    if kg.exists():
        src = kg.read_text(encoding="utf-8", errors="replace")
        low_tier_values = len(re.findall(r'"systemic_absorption_(?:low|very_low)"', src))
        m = re.search(r"tests two of these|tests four of these|(two|four) of which the (?:hard constraint|L3)", text)
        if m:
            claimed = m.group(0)
            want = 2
            if f"{'two' if want == 2 else 'four'}" not in claimed:
                checks.append(("L3 层级数", f"正文称 {claimed!r}，代码实际测试 {want} 层"))
        else:
            checks.append(("L3 层级数", "正文未明确说明 L3 测试的层级数（上一轮审稿人问过）"))

    # 2) BM25 参数
    rag = ROOT / "src" / "ophthalmic_ddi_cds_agent" / "naive_rag.py"
    if rag.exists():
        src = rag.read_text(encoding="utf-8", errors="replace")
        for name, pat_code, pat_text in [
            ("BM25 k1", r"K1\s*=\s*([\d.]+)", r"k1\s*=\s*([\d.]+)"),
            ("BM25 b", r"B\s*=\s*([\d.]+)", r"\bb\s*=\s*([\d.]+)"),
            ("BM25 top-k", r"TOP_K\s*=\s*(\d+)", r"top-?k\s*=?\s*(\d+)"),
            ("passage cap", r"PASSAGE_CHAR_CAP\s*=\s*(\d+)", r"truncated to (\d+) characters"),
        ]:
            mc = re.search(pat_code, src)
            mt = re.search(pat_text, text)
            if mc and mt and mc.group(1) != mt.group(1):
                checks.append((name, f"代码 {mc.group(1)} vs 正文 {mt.group(1)}"))
            elif mc and not mt:
                checks.append((name, f"代码为 {mc.group(1)}，正文未报告"))
        # query 是否含药名
        if "ophthalmic_drug} {systemic_drug}" in src.replace("\n", ""):
            if not re.search(r"drug name.{0,20}systemic drug name|includes the drug names", text):
                checks.append(("BM25 query", "代码用两药名拼查询串，正文未说明包含药名"))

    # 3) 推理模型重跑参数（若正文引用了该实验）
    if "glm-5.3-flash" in text:
        run = ROOT / "scripts" / "rerun_glm53_baselines.py"
        if run.exists():
            src = run.read_text(encoding="utf-8", errors="replace")
            pairs = [("max_tokens", r"MAX_TOKENS\s*=\s*(\d+)", r"`?max_tokens`?\s*(?:to\s*)?(\d{3,5})"),
                     # 正文写法多样（"majority vote over five repeated samples" / "the majority of
                     # five samples"），只接受数字或英文数词，不接受 "the" 等冠词，否则误报。
                     ("samples", r"REPS\s*=\s*(\d+)",
                      r"majority (?:vote )?(?:of|over) (\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b"),
                     ("temperature", r"TEMPERATURE\s*=\s*([\d.]+)", r"temperature\s*([\d.]+)")]
            wordnum = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
            for name, pc, pt in pairs:
                mc = re.search(pc, src); mt = re.search(pt, text)
                if mc and mt:
                    tv = mt.group(1)
                    tv = str(wordnum.get(tv.lower(), tv))
                    if mc.group(1).rstrip("0").rstrip(".") != tv.rstrip("0").rstrip("."):
                        checks.append((f"GLM {name}", f"代码 {mc.group(1)} vs 正文 {mt.group(1)}"))
        else:
            checks.append(("GLM 脚本", "正文报告了 glm-5.3-flash 重跑，但脚本不在仓库中"))

    # 4) 统计参数（bootstrap 次数）
    st = ROOT / "scripts" / "stats_tests.py"
    if st.exists() and re.search(r"bootstrap", text, re.I):
        mc = re.search(r"n_resamples:\s*int\s*=\s*(\d+)", st.read_text(encoding="utf-8", errors="replace"))
        mt = re.search(r"bootstrap intervals \((\d[\d,]*)\s*resamples?\)", text)
        if mc and mt and mc.group(1) != mt.group(1).replace(",", ""):
            checks.append(("bootstrap 次数", f"代码 {mc.group(1)} vs 正文 {mt.group(1)}"))

    if checks:
        for name, msg in checks:
            a.fail(check, f"{name}: {msg}")
    else:
        a.ok(check, "手稿报告的参数与代码实现一致")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="有 FAIL 时以非零码退出")
    ap.add_argument("--json", default=None, help="把报告写入 JSON")
    args = ap.parse_args()

    mpath = first_existing(MANUSCRIPT_CANDIDATES)
    spath = first_existing(SUPP_CANDIDATES)
    lpath = first_existing(LEGENDS_CANDIDATES)
    npath = first_existing(NUMBERS_CANDIDATES)
    if not mpath:
        print("错误：找不到手稿文件")
        return 1
    text = mpath.read_text(encoding="utf-8")
    supp = spath.read_text(encoding="utf-8") if spath else ""
    legends = lpath.read_text(encoding="utf-8") if lpath else ""
    numbers = json.loads(npath.read_text(encoding="utf-8")) if npath else {}

    a = Audit()
    check_crossrefs(text, supp, legends, a)
    check_references(text, a)
    check_placeholders(text, supp, a)
    check_doi_present(text, a)
    check_numbers(text, numbers, a)
    check_deposited_paths(text, supp, a)
    check_abstract(text, a)
    check_self_consistency(text, a)
    check_code_text_consistency(text, a)

    print(f"=== 手稿一致性审计 ===\n源文件: {mpath}\n")
    for f in a.findings:
        mark = {"FAIL": "✗", "WARN": "!", "OK": "✓"}[f["level"]]
        print(f"  {mark} [{f['check']}] {f['message']}")

    n_fail, n_warn = len(a.failures), len(a.warnings)
    print(f"\n合计: {n_fail} 个 FAIL, {n_warn} 个 WARN")
    if n_fail:
        print("\nFAIL 必须修复后才能提交。")

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps({"manuscript": str(mpath), "findings": a.findings,
                        "n_fail": n_fail, "n_warn": n_warn},
                       ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"报告已写出 -> {args.json}")

    return 1 if (args.strict and n_fail) else 0


if __name__ == "__main__":
    raise SystemExit(main())
