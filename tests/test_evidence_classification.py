import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("build_evidence_base", Path(__file__).resolve().parents[1] / "scripts" / "build_evidence_base.py")
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_meta_analysis_takes_precedence() -> None:
    assert module.classify_publication(["Journal Article", "Meta-Analysis"], "plain abstract", "x") == ("B", "meta_or_systematic_review")


def test_case_report_is_not_misclassified_as_generic_article() -> None:
    assert module.classify_publication(["Journal Article", "Case Reports"], "plain abstract", "x") == ("E", "case_report")


def test_original_study_requires_explicit_publication_type() -> None:
    assert module.classify_publication(["Journal Article", "Randomized Controlled Trial"], "plain abstract", "x") == ("C", "original_study")
    assert module.classify_publication(["Journal Article"], "plain abstract", "x") == (None, "unclassified")


def test_mechanism_level_requires_topic_and_keyword() -> None:
    assert module.classify_publication(["Journal Article"], "Pharmacokinetic absorption was measured.", "mechanism_pk") == ("D", "mechanism_keyword")
    assert module.classify_publication(["Journal Article"], "plain abstract", "mechanism_pk") == (None, "unclassified")
