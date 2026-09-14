import csv
from pathlib import Path


def test_candidate_counts_and_no_duplicate_systemic_name() -> None:
    import yaml
    root = Path(__file__).resolve().parents[1]
    a = yaml.safe_load((root / "data/curation/entity_a_candidates.yaml").read_text(encoding="utf-8"))["entities"]
    b = yaml.safe_load((root / "data/curation/entity_b_candidates.yaml").read_text(encoding="utf-8"))["entities"]
    assert len(a) >= 100
    assert len(b) >= 200
    names = [item["generic_name"].casefold() for item in b]
    assert len(names) == len(set(names))
