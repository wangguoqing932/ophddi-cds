# -*- coding: utf-8 -*-
"""build_demo_guide.py — annotate the real Streamlit screenshots and build a PDF guide.

The screenshots are captured from the running application with the light,
manuscript-matched palette and English labels. Numbered callouts correspond to
the notes on each page.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"
OUT = ROOT / "outputs" / "deliverables" / "Interactive_Demo_Guide.pdf"

BLUE = HexColor("#1F4E79")
MID = HexColor("#4A7FA5")
LIGHT = HexColor("#F2F5F9")
GREY = HexColor("#555555")
DARK = HexColor("#222222")
AMBER = HexColor("#E8A33D")

FONT_DIR = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", str(FONT_DIR / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONT_DIR / "arialbd.ttf")))

# ── screenshot crops ────────────────────────────────────────────────────────
CROPS = {
    "step1": (0, 300, 1440, 792),
    "step2": (0, 140, 1440, 682),
    "step3": (315, 420, 1310, 690),
}
# (number, bounding box in original pixel coordinates, badge centre)
MARKS = {
    "step1": [
        (1, (382, 354, 1350, 391), (360, 372)),
        (2, (382, 516, 853, 547), (360, 532)),
        (3, (872, 516, 1352, 607), (1370, 562)),
        (4, (382, 625, 1350, 656), (360, 640)),
        (5, (382, 680, 1350, 715), (360, 698)),
    ],
    "step2": [
        (1, (366, 154, 1294, 294), (348, 224)),
        (2, (365, 319, 1294, 386), (348, 352)),
        (3, (365, 443, 830, 468), (348, 455)),
        (4, (365, 484, 1294, 560), (348, 522)),
        (5, (365, 612, 760, 662), (348, 628)),
    ],
    "step3": [
        (1, (365, 443, 558, 468), (340, 455)),
        (2, (368, 487, 650, 515), (340, 501)),
        (3, (370, 523, 610, 541), (340, 532)),
        (4, (370, 548, 1265, 592), (340, 568)),
        (5, (370, 601, 1170, 622), (340, 611)),
        (6, (370, 641, 1288, 668), (340, 655)),
    ],
}


SRC = {"step1": "step1_select", "step2": "step2_result", "step3": "step3_rule"}


def annotate(key: str) -> Path:
    im = Image.open(FIG / f"demo_ui_{SRC[key]}.png").convert("RGB")
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(str(FONT_DIR / "arialbd.ttf"), 17)
    for num, (x0, y0, x1, y1), (bx, by) in MARKS[key]:
        if key != "step3":
            d.rounded_rectangle([x0, y0, x1, y1], radius=6, outline=(31, 78, 121), width=3)
        d.ellipse([bx - 15, by - 15, bx + 15, by + 15], fill=(255, 255, 255))
        d.ellipse([bx - 13, by - 13, bx + 13, by + 13], fill=(31, 78, 121))
        tw = d.textlength(str(num), font=font)
        d.text((bx - tw / 2, by - 10), str(num), font=font, fill=(255, 255, 255))
    im = im.crop(CROPS[key])
    out = FIG / f"demo_ui_{key}_annotated.png"
    im.save(out, dpi=(220, 220))
    return out


def wrap(text: str, font: str, size: float, width: float) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if pdfmetrics.stringWidth(trial, font, size) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def note(c: canvas.Canvas, x: float, y: float, width: float, num: int,
         lead: str, body: str, size: float = 8.6) -> float:
    """Draw one numbered note; return the new y."""
    badge_r = 7.4
    c.setFillColor(BLUE)
    c.circle(x + badge_r, y - 2.4, badge_r, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Arial-Bold", 7.4)
    c.drawCentredString(x + badge_r, y - 5.0, str(num))
    tx = x + 2 * badge_r + 6
    avail = width - (tx - x)

    c.setFont("Arial-Bold", size)
    lead_w = pdfmetrics.stringWidth(lead + " ", "Arial-Bold", size)
    c.setFillColor(DARK)
    c.drawString(tx, y - size + 0.6, lead)

    first_room = avail - lead_w
    body_lines: list[str] = []
    words = body.split()
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if pdfmetrics.stringWidth(trial, "Arial", size) <= first_room:
            cur = trial
        else:
            body_lines.append(cur)
            first_room = avail
            cur = w
            # recompute with the wider line width
            while pdfmetrics.stringWidth(cur, "Arial", size) > avail and " " in cur:
                cut = cur.rsplit(" ", 1)
                body_lines.append(cut[0])
                cur = cut[1]
    if cur:
        body_lines.append(cur)

    c.setFont("Arial", size)
    c.setFillColor(GREY)
    if body_lines:
        c.drawString(tx + lead_w, y - size + 0.6, body_lines[0])
    line_h = size * 1.28
    yy = y - size + 0.6 - line_h
    for line in body_lines[1:]:
        c.drawString(tx, yy, line)
        yy -= line_h
    return yy + line_h - 7


def header(c: canvas.Canvas, step: str, title: str, subtitle: str) -> None:
    w, h = landscape(A4)
    c.setFillColor(BLUE)
    c.rect(0, h - 5, w, 5, stroke=0, fill=1)
    c.setFillColor(BLUE)
    c.setFont("Arial-Bold", 17)
    c.drawString(36, h - 40, "Interactive demonstration of OphDDI-CDS")
    c.setFillColor(GREY)
    c.setFont("Arial", 8.2)
    c.drawString(36, h - 54,
                 "Screenshots from the running Streamlit application. Interface labels are English and the palette matches the manuscript figures.")
    c.setFillColor(BLUE)
    c.setFont("Arial-Bold", 11.5)
    c.drawString(36, h - 78, f"{step}  —  {title}")
    c.setStrokeColor(HexColor("#C9D6E3"))
    c.setLineWidth(0.7)
    c.line(36, h - 86, w - 36, h - 86)
    c.setFillColor(GREY)
    c.setFont("Arial", 8.0)
    c.drawString(36, h - 99, subtitle)


def footer(c: canvas.Canvas, page: int, total: int) -> None:
    w, _ = landscape(A4)
    c.setStrokeColor(HexColor("#C9D6E3"))
    c.setLineWidth(0.6)
    c.line(36, 30, w - 36, 30)
    c.setFillColor(AMBER)
    c.setFont("Arial-Bold", 7.4)
    lead = "Research decision support only."
    c.drawString(36, 19, lead)
    lead_w = pdfmetrics.stringWidth(lead, "Arial-Bold", 7.4)
    c.setFillColor(GREY)
    c.setFont("Arial", 7.4)
    c.drawString(36 + lead_w + 8, 19,
                 "A screening flag, not a probability of harm; final judgement rests with the clinician.")
    c.drawRightString(w - 36, 19, f"{page} / {total}")


def info_box(c: canvas.Canvas, y: float, title: str, text: str, text2: str = "") -> None:
    w, _ = landscape(A4)
    height = 42 if not text2 else 50
    c.setFillColor(LIGHT)
    c.roundRect(36, y, w - 72, height, 5, stroke=0, fill=1)
    c.setFillColor(BLUE)
    c.setFont("Arial-Bold", 7.8)
    c.drawString(46, y + height - 14, title)
    tw = pdfmetrics.stringWidth(title, "Arial-Bold", 7.8)
    c.setFillColor(GREY)
    c.setFont("Arial", 7.8)
    c.drawString(46 + tw + 10, y + height - 14, text)
    if text2:
        c.setFillColor(MID)
        c.setFont("Arial", 7.4)
        c.drawString(46, y + 10, text2)


def page1(c: canvas.Canvas, img: Path) -> None:
    w, h = landscape(A4)
    header(c, "Step 1", "Select an ophthalmic–systemic pair",
           "The left sidebar reports registry coverage (113 ophthalmic agents, 232 systemic drugs) and the run configuration. No LLM call is needed for the deterministic path.")
    iw = 780.0
    ih = iw * 492 / 1440
    c.drawImage(str(img), 36, h - 105 - ih, width=iw, height=ih,
                preserveAspectRatio=True, anchor="nw")

    y = h - 105 - ih - 22
    col_w = 370
    notes = [
        ("Demo cases.", "Expand to load one of four preset pairs; both selectors fill automatically."),
        ("Ophthalmic agent (113).", "Every topical agent carries its absorption tier and flags from the registry."),
        ("Systemic medication (232).", "Search by name; the registry identifier (e.g. sys_med_0013) confirms the match."),
        ("Patient factors (optional).", "Age, renal or hepatic impairment and other modifiers can change which rules are eligible."),
        ("Run assessment.", "Executes L1 → L2 → L3 deterministically; the result appears below in about 0.2 s."),
    ]
    left = notes[:3]
    right = notes[3:]
    yy = y
    for i, (lead, body) in enumerate(left, 1):
        yy = note(c, 42, yy, col_w, i, lead, body)
    yy = y
    for i, (lead, body) in enumerate(right, 4):
        yy = note(c, 36 + iw / 2 + 4, yy, col_w, i, lead, body)
    info_box(c, 46, "Deterministic by design",
             "L1 40 mechanism rules → L2 21 × 40 class matrix (104 cells) → L3 G19 hard constraint; final grade = max of the three layers.",
             'Launch locally: pip install -e ".[streamlit]"   ·   streamlit run app/streamlit_app.py')
    footer(c, 1, 3)
    c.showPage()


def page2(c: canvas.Canvas, img: Path) -> None:
    w, h = landscape(A4)
    header(c, "Step 2", "Read the result at a glance",
           "The same object returns the final grade, the decision path and the evidence that produced it. Colour encodes severity, not probability.")
    iw = 780.0
    ih = iw * 542 / 1440
    c.drawImage(str(img), 36, h - 105 - ih, width=iw, height=ih,
                preserveAspectRatio=True, anchor="nw")

    y = h - 105 - ih - 22
    col_w = 370
    notes = [
        ("Grade and metadata.", "Final grade = max(L1, L2, L3); this pair is HIGH from one L1 rule. A 100% score marks a deterministic rule match, not a probability of harm."),
        ("Metric cards.", "Triggered rules, evidence passages, confidence and runtime for this run."),
        ("Four levels of detail.", "Summary, Rule details, Evidence chain and Technical details."),
        ("Full report.", "Lists every triggered signal by severity."),
        ("Signal tags.", "Each tag is the rule ID that produced the signal, linking back to the rule record."),
    ]
    yy = y
    for i, (lead, body) in enumerate(notes[:3], 1):
        yy = note(c, 42, yy, col_w, i, lead, body)
    yy = y
    for i, (lead, body) in enumerate(notes[3:], 4):
        yy = note(c, 36 + iw / 2 + 4, yy, col_w, i, lead, body)
    info_box(c, 46, "Reading the grade",
             "HIGH — avoid or monitor; MEDIUM — review and monitor; LOW — usual care; UNASSESSED — manual review, not evidence of safety.",
             "A grade is a screening flag. It does not quantify the probability of an adverse event.")
    footer(c, 2, 3)
    c.showPage()


def page3(c: canvas.Canvas, img: Path) -> None:
    w, h = landscape(A4)
    header(c, "Step 3", "Inspect the rule and its evidence",
           "Rule details expose the exact record behind the grade: identifier, severity, mechanism, citations and the action attached to the rule.")
    iw = 780.0
    ih = iw * 270 / 995
    c.drawImage(str(img), 36, h - 105 - ih, width=iw, height=ih,
                preserveAspectRatio=True, anchor="nw")

    y = h - 105 - ih - 22
    col_w = 370
    notes = [
        ("Rule details tab.", "Switches from the summary to the rule-level record for this pair."),
        ("Rule ID.", "beta_blocker_ccb_additive is the audit handle that links the output to configs/rules.yaml."),
        ("Severity and mechanism class.", "[HIGH] and pharmacodynamic_cardiovascular; the grade is rule-derived, not model-generated."),
        ("Rationale.", "Mechanism plus the case-report and label citations behind the rule (BMJ 1987; Med J Aust 1983; DDInter 2.0)."),
        ("Recommendation.", "Rule-specific action: avoid or monitor HR/ECG when high-absorption beta-blockers are combined with verapamil or diltiazem."),
        ("Matched tags.", "Agent tags and patient factors used in matching, so the trigger can be reproduced."),
    ]
    yy = y
    for i, (lead, body) in enumerate(notes[:3], 1):
        yy = note(c, 42, yy, col_w, i, lead, body)
    yy = y
    for i, (lead, body) in enumerate(notes[3:], 4):
        yy = note(c, 36 + iw / 2 + 4, yy, col_w, i, lead, body)

    c.setFillColor(HexColor("#EAF0F6"))
    c.roundRect(36, 104, w - 72, 30, 4, stroke=0, fill=1)
    c.setFillColor(BLUE)
    c.setFont("Arial-Bold", 7.6)
    c.drawString(46, 114, "Traceability")
    c.setFillColor(GREY)
    c.setFont("Arial", 7.6)
    c.drawString(108, 114,
                 "UI label  →  rule ID  →  configs/rules.yaml  →  source tier (A–E)  →  citation  →  recommended action")
    info_box(c, 46, "Output contract",
             "every result returns grade · decision path · matched rule IDs · source record · recommended action",
             "The production path is deterministic and reproducible; retrieval and LLM components are optional and never required to obtain the grade.")
    footer(c, 3, 3)
    c.showPage()


def main() -> None:
    imgs = {k: annotate(k) for k in CROPS}
    c = canvas.Canvas(str(OUT), pagesize=landscape(A4))
    c.setTitle("Interactive demonstration of OphDDI-CDS")
    c.setAuthor("OphDDI-CDS authors")
    page1(c, imgs["step1"])
    page2(c, imgs["step2"])
    page3(c, imgs["step3"])
    c.save()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
