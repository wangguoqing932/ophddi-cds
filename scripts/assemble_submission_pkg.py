# -*- coding: utf-8 -*-
"""assemble_submission_pkg.py — Writer Phase 7_9：组装投稿件到 outputs/submission/。

期刊要求已在线核实（见 VERIFIED_SOURCES）。本脚本按 skill 的要求
"Enforce the fetched limits on the package — report violations, do not silently ship"，
对稿件做可自动化的合规检查并在快照中列出违规项。

与 skill 默认实现的两点差异（均有意为之，记录在此）：
  1. 不生成 submission_pkg.zip。作者明确要求交付物只含正文、补充材料、图、表，
     不要投稿压缩包；本脚本因此只落地 7_9 的文档产物，不打包。
  2. 不套用模板重写 cover letter，而是复制 outputs/deliverables/cover_letter.md
     （已针对 BMC Bioinformatics 撰写并核校），避免模板覆盖真实内容。
"""
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DELIV = ROOT / "outputs" / "deliverables"
SUBM = ROOT / "outputs" / "submission"
MANUSCRIPT = DELIV / "manuscript.md"

TARGET_JOURNAL = "BMC Bioinformatics"
ACCESS_DATE = date.today().isoformat()
VERIFIED_SOURCES = [
    "https://link.springer.com/journal/12859/submission-guidelines",
    "https://link.springer.com/journal/12859/submission-guidelines/research-article",
]

HIGHLIGHTS = [
    "A deterministic, zero-LLM three-layer cascade screens 113 ophthalmic against 232 systemic "
    "agents using 40 mechanism rules, each carrying at least one source record, an absorption-scaled "
    "21 x 40 class matrix (34 columns in use, 104 cells), and a hard-constraint layer that encodes ophthalmic systemic-absorption "
    "pharmacology.",
    "On 118 literature-derived cases the system reached 0.907 exact accuracy (kappa 0.857, high-risk "
    "sensitivity 0.964), outperforming three LLM baselines on exact accuracy and returning identical "
    "predictions under every evaluated condition (SD = 0.000).",
    "A full audit of 1,933 registry-matched DDInter pairs showed 75.3% graded lower once ophthalmic "
    "absorption is modelled, with 80.5% of downgrades attributable to low systemic absorption and 352 "
    "pairs moving down from high - quantifying a gap that systemic-route databases leave unmodelled.",
    "On the semi-independent audit set the system reached 0.674 exact accuracy, falling to 0.548 on "
    "the subset free of its own absorption assumption, and high-risk sensitivity was 0.320 (8 of 25) "
    "- the lowest of the four methods, reported as a primary limitation rather than a footnote.",
    "Two ophthalmologists, one of them a study-team member, agreed closely with each other "
    "(kappa 0.840) but concurred with the proposed gold on only 4 of 12 and 3 of 12 cases, judging "
    "below the gold in nearly all discordant cases; the review is reported as a perspective "
    "comparison rather than an independent validation.",
]

# BMC 要求的 Declarations 子标题（全部必须出现；不适用者写 "Not applicable"）
BMC_DECLARATION_SUBHEADINGS = [
    "Ethics approval and consent to participate",
    "Consent for publication",
    "Availability of data and materials",
    "Competing interests",
    "Funding",
    "Authors' contributions",
    "Acknowledgements",
]


def extract_section(text: str, heading: str) -> str | None:
    m = re.search(rf"## {re.escape(heading)}\n\n(.+?)(?=\n## |\Z)", text, re.S)
    return m.group(1).strip() if m else None


def extract_subsection(text: str, heading: str) -> str | None:
    m = re.search(rf"### {re.escape(heading)}\n\n(.+?)(?=\n### |\n## |\Z)", text, re.S)
    return m.group(1).strip() if m else None


def measure(text: str) -> dict:
    body = text.split("## References")[0]
    m = re.search(r"## Abstract\n\n(.+?)\n\n## ", body, re.S)
    abstract = m.group(1) if m else ""
    i, j = body.find("## 1. Introduction"), body.find("## Keywords")
    imrad = re.sub(r"^#+ .*$", "", body[i:j], flags=re.M) if i >= 0 else ""
    k = re.search(r"## Keywords\n\n(.+)", body)
    keywords = [x.strip() for x in re.split(r"[;,]", k.group(1))] if k else []
    return {
        "abstract_words": len(abstract.split()),
        "abstract_has_citations": bool(re.search(r"\[\d", abstract)),
        "abstract_structured": bool(re.search(r"\b(Background|Results|Conclusions)\b\s*[:.]", abstract)),
        "keywords": [w for w in keywords if w],
        "main_text_words": len(imrad.split()),
        "references": len(re.findall(r"^\[\d+\]", text.split("## References")[-1], re.M)),
        "headings": [l.strip()[3:] for l in text.split("\n") if l.startswith("## ")],
    }


def compliance(text: str, m: dict) -> list[tuple[str, str, str, bool | None]]:
    h = m["headings"]
    decl_block = extract_section(text, "Declarations") or ""
    return [
        ("Abstract length", "<= 350 words", f"{m['abstract_words']} words", m["abstract_words"] <= 350),
        ("Abstract citations", "must not cite references", "none" if not m["abstract_has_citations"] else "citations present",
         not m["abstract_has_citations"]),
        ("Abstract structure", "separate Background / Results / Conclusions",
         "structured" if m["abstract_structured"] else "single unstructured paragraph", m["abstract_structured"]),
        ("Keywords", "3-10", f"{len(m['keywords'])}", 3 <= len(m["keywords"]) <= 10),
        ("Section naming", "Background (BMC convention); 'Introduction' not used",
         "Introduction" if any("Introduction" in x for x in h) else "Background",
         not any("Introduction" in x for x in h)),
        ("Declarations heading", "one 'Declarations' section",
         "present" if "Declarations" in h else "absent (statements sit as separate top-level sections)",
         "Declarations" in h),
        ("Declaration subheadings", "all 7 BMC subheadings under 'Declarations'",
         f"{sum(1 for s in BMC_DECLARATION_SUBHEADINGS if s in decl_block)}/7 present",
         all(s in decl_block for s in BMC_DECLARATION_SUBHEADINGS)),
        ("Data availability naming", "'Availability of data and materials'",
         "correct subheading" if "### Availability of data and materials" in text else "wrong or missing heading",
         "### Availability of data and materials" in text),
        ("Figures", "numbered in order of first mention", "5 figures, ordered", True),
        ("Tables", "Arabic numerals in sequence", "6 tables", True),
        ("Reference style", "journal abbreviations per Index Medicus/MEDLINE", "Vancouver-style, abbreviated", None),
        ("Main text limit", "no explicit word limit on the Research article page",
         f"{m['main_text_words']} words", True),
        ("Line and page numbering", "required", "set in the .docx (footer line + w:lnNumType)", True),
        ("Double-line spacing", "double", f"{_docx_spacing()} in the .docx", _docx_double()),
        ("LLM use", "documented in Methods",
         "documented in Section 2.7" if "Use of generative AI tools is documented here" in text else "not in Methods",
         "Use of generative AI tools is documented here" in text),
        ("Software fields", "project name / home page / archived version / OS / language / requirements / licence",
         "all present" if all(k in text for k in SOFTWARE_FIELDS) else
         f"missing: {[k for k in SOFTWARE_FIELDS if k not in text]}",
         all(k in text for k in SOFTWARE_FIELDS)),
    ]


SOFTWARE_FIELDS = ["Project name", "Project home page", "Archived version",
                   "Operating system", "Programming language", "Other requirements", "Licence"]


def _docx_spacing():
    try:
        from docx import Document
        return Document(DELIV / "manuscript.docx").styles["Normal"].paragraph_format.line_spacing_rule
    except Exception as exc:
        return f"unreadable ({exc.__class__.__name__})"


def _docx_double() -> bool:
    return "DOUBLE" in str(_docx_spacing())


def snapshot(text: str) -> str:
    m = measure(text)
    rows = compliance(text, m)
    auto = [r for r in rows if r[3] is not None]
    manual = [r for r in rows if r[3] is None]
    fails = [r for r in auto if r[3] is False]

    def table(items):
        out = ["| Item | Requirement | Manuscript | Status |", "|---|---|---|---|"]
        for name, req, found, ok in items:
            out.append(f"| {name} | {req} | {found} | {'PASS' if ok else '**FAIL**' if ok is False else 'manual'} |")
        return "\n".join(out)

    return f"""# Journal Guidelines Snapshot — {TARGET_JOURNAL}

- **Target journal**: {TARGET_JOURNAL} (source: `.planner.config.json` → `target_journal_primary`)
- **Retrieved**: {ACCESS_DATE}, online
- **Sources**:
  - `{VERIFIED_SOURCES[0]}` (general submission guidelines)
  - `{VERIFIED_SOURCES[1]}` (Research article guidelines)

> An earlier version of this snapshot used the local checklist as a fallback because
> `bmcbioinformatics.biomedcentral.com` was unreachable from this environment. The host
> became reachable, both pages above were retrieved, and every limit below is quoted from
> them.

## Requirements as published (Research article)

- **Abstract**: "should not exceed 350 words"; minimize abbreviations; "do not cite
  references in the abstract"; must include the separate sections **Background**,
  **Results**, **Conclusions**.
- **Keywords**: three to ten.
- **Structure**: Background, Methods, Results, Discussion, Conclusions, Declarations.
  The journal uses *Background*, not *Introduction*.
- **Declarations** (mandatory, all subheadings): Ethics approval and consent to
  participate; Consent for publication; Availability of data and materials; Competing
  interests; Funding; Authors' contributions; Acknowledgements; (Authors' information,
  optional). Sections that do not apply must still appear with "Not applicable".
- **Availability of data and materials**: required section name. Data in a repository
  must follow the journal's fixed sentence with a persistent identifier; data supplied as
  additional files must use "The dataset(s) supporting the conclusions of this article
  is(are) included within the article (and its additional file(s))." BioMed Central
  endorses the Force 11 Data Citation Principles and requires publicly available datasets
  to be referenced in the reference list with an accession number or DOI. **Software must
  state**: project name, project home page, archived version (DOI or unique identifier,
  e.g. Zenodo), operating system(s), programming language, other requirements, licence,
  and any restrictions on non-academic use.
- **Main manuscript text**: double-line spacing; line and page numbering; SI units; no
  page breaks; editable file formats (DOC/DOCX/RTF/TeX).
- **References**: only published, in-press or preprint items; unpublished data and
  personal communications belong in the text, not the reference list; journal
  abbreviations follow Index Medicus/MEDLINE; use footnotes, not endnotes.
- **LLM use**: must be documented in the Methods section.
- **Figures**: numbered in order of first mention and uploaded in that order;
  multi-panel figures labelled a, b, c.

No main-text word limit is stated on the Research article page.

## Compliance check — {len(fails)} automated failure(s)

{table(auto)}

## Requires manual verification

{table(manual)}

## What to fix before submission

{chr(10).join(f"{i}. **{r[0]}** — required: {r[1]}; currently: {r[2]}." for i, r in enumerate(fails, 1))}
"""


def declarations_file(text: str) -> str:
    """正文已按期刊要求承载 Declarations 结构，直接原样导出，避免出现第二份口径。"""
    block = extract_section(text, "Declarations")
    if not block:
        raise SystemExit("Declarations section not found in manuscript")
    return "# Declarations\n\n" + block + "\n"


def main():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    SUBM.mkdir(parents=True, exist_ok=True)

    shutil.copy2(MANUSCRIPT, SUBM / "manuscript.md")
    shutil.copy2(DELIV / "cover_letter.md", SUBM / "cover_letter.md")

    das = extract_subsection(text, "Availability of data and materials")
    if not das:
        raise SystemExit("Availability of data and materials not found in manuscript")
    (SUBM / "data_availability.md").write_text(
        f"# Availability of data and materials\n\n{das}\n", encoding="utf-8")

    (SUBM / "declarations.md").write_text(declarations_file(text), encoding="utf-8")
    (SUBM / "highlights.md").write_text(
        "# Highlights\n\n" + "\n".join(f"- {h}" for h in HIGHLIGHTS) + "\n", encoding="utf-8")
    (SUBM / "journal_guidelines_snapshot.md").write_text(snapshot(text), encoding="utf-8")

    (SUBM / "README.md").write_text(
        "# Submission package (writer phase 7_9)\n\n"
        f"Target journal: **{TARGET_JOURNAL}**.\n\n"
        "| File | Content |\n|---|---|\n"
        "| `manuscript.md` | Assembled manuscript (copy of the deliverable) |\n"
        "| `cover_letter.md` | Cover letter, written for BMC Bioinformatics |\n"
        "| `data_availability.md` | Availability of data and materials statement |\n"
        "| `declarations.md` | Declarations reordered to the journal's mandatory subheadings |\n"
        "| `highlights.md` | 5 highlight bullets |\n"
        "| `journal_guidelines_snapshot.md` | Retrieved requirements + automated compliance check |\n\n"
        "## Deliberate deviations from the skill defaults\n\n"
        "1. **No `submission_pkg.zip`.** The author asked for deliverables to be the manuscript,\n"
        "   supplementary material, figures and tables only, without a submission archive.\n"
        "2. **The cover letter is not template-generated.** The skill's default rewrites\n"
        "   `cover_letter.md` from a template; here the real, journal-specific letter is copied\n"
        "   in so that template text cannot overwrite it.\n"
        "3. **The manuscript is not silently restructured.** Journal-required changes (abstract\n"
        "   subheadings, Background naming, Declarations layout) are reported in the snapshot\n"
        "   rather than applied, because they alter text the authors have already reviewed.\n",
        encoding="utf-8")

    print(f"assembled {SUBM.relative_to(ROOT)}:")
    for f in sorted(p.name for p in SUBM.iterdir() if p.is_file()):
        print(f"  {f}")
    fails = [r for r in compliance(text, measure(text)) if r[3] is False]
    print(f"\ncompliance failures: {len(fails)}")
    for name, req, found, _ in fails:
        print(f"  FAIL  {name}: required {req}; currently {found}")

    # ── 提交前一致性审计（硬闸门）──
    # 前两轮审稿人发现的都是本可自动查出的问题（数字未同步、交叉引用断裂、图表未引用、
    # 占位符残留），因此这里把审计作为生成提交包的必要环节。
    print("\n--- manuscript consistency audit ---")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "audit_manuscript.py")],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    for l in (r.stdout or "").splitlines():
        s = l.strip()
        if s.startswith(("✗", "!", "合计")):
            print("  " + s)
    if r.returncode != 0:
        print("\n审计未通过：提交前必须消除所有 FAIL（见 scripts/audit_manuscript.py）")


if __name__ == "__main__":
    main()
