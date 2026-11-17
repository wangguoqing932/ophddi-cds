# -*- coding: utf-8 -*-
"""figure_palette.py — the single colour system for every figure in the paper.

Figure 3 fixes the reference palette. All other figures import from here so that
the manuscript reads as one design: three blues carrying ordered/quantitative
series, plus three accents reserved for categorical identities (proposed value,
first rater, second rater).

Do not hard-code hex values in a drawing script; add a named role here instead.
"""

# ── blue ramp: ordered and quantitative series ─────────────────────────────
BLUE_900 = "#1F4E79"      # primary series, strongest value
BLUE_700 = "#4A7FA5"      # second series
BLUE_400 = "#B9CDDC"      # third series / light fill
BLUE_200 = "#D7E3EC"      # fourth series (derived: same hue, lighter)
BLUE_100 = "#EAF0F5"      # backgrounds, empty cells

# ── accents: categorical identities only ──────────────────────────────────
AMBER = "#E8A33D"         # proposed / displayed value
GREEN = "#3C8C4E"         # first rater
BROWN = "#8D6E63"         # second rater

# ── neutrals ──────────────────────────────────────────────────────────────
INK = "#222222"           # text
GREY = "#767676"          # secondary text, inactive marks
RULE = "#D9D9D9"          # grid lines and hairlines


# ── semantic mappings shared across figures ───────────────────────────────
# Risk grades: darker means higher risk, so the scale reads in greyscale too.
RISK = {"high": BLUE_900, "medium": BLUE_700, "low": BLUE_400}

# Methods, ordered from the deterministic cascade down to the weakest baseline.
METHOD = {
    "full_system": BLUE_900,
    "lightrag": BLUE_700,
    "naive_rag": BLUE_400,
    "pure_llm": BLUE_200,
}

# Human and displayed values in the grade review.
RATER = {"gold": BLUE_900, "displayed": AMBER, "expert_1": GREEN, "expert_2": BROWN}
