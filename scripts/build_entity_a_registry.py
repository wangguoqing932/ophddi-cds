"""Build the auditable Phase 1 Entity A registry."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ophthalmic_ddi_cds_agent.registry_builder import build


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-mode", choices=("online", "cache-only"), default="online")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    result = build(
        root,
        "A",
        args.source_mode,
        args.cache_dir or root / "data" / "raw",
        args.output_dir or root / "data" / "seed",
    )
    print(
        f"Entity A: {result['entity_count']} records; "
        f"{result['source_record_count']} source records; {result['warning_count']} warnings"
    )


if __name__ == "__main__":
    main()
