# -*- coding: utf-8 -*-
"""rule_gating_experiment.py — compatibility wrapper.

The gated-versus-ungated experiment is implemented in
``scripts/build_gating_tables.py``. That script writes both the machine-readable
``outputs/recomputed/rule_gating_experiment.json`` (keys: gated, ungated) and
Supplementary Table S19.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_gating_tables import main  # noqa: E402

if __name__ == "__main__":
    main()
