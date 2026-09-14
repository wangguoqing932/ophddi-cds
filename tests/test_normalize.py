from ophthalmic_ddi_cds_agent.normalize import normalize_medication
from ophthalmic_ddi_cds_agent.schemas import EntityA, EntityB


def test_normalizes_salt_and_case_with_route() -> None:
    item = EntityA(entity_a_id="a1", primary_name="Timolol", canonical_name="Timolol", aliases=["timolol maleate"], category="x", flags=["beta_blocker"], active_mechanisms=[], evidence_sources=[])
    result = normalize_medication(" TIMOLOL-MALEATE ", [item], route="ophthalmic")
    assert result.canonical_name == "Timolol"


def test_route_prevents_cross_registry_resolution() -> None:
    topical = EntityA(entity_a_id="a1", primary_name="Dexamethasone", canonical_name="Dexamethasone", category="x", flags=[], active_mechanisms=[], evidence_sources=[])
    systemic = EntityB(entity_b_id="b1", generic_name="Dexamethasone systemic", canonical_name="Dexamethasone", aliases=["dexamethasone"], drug_class="x", flags=[])
    result = normalize_medication("dexamethasone", [topical, systemic])
    assert result.ambiguous
    assert normalize_medication("dexamethasone", [topical, systemic], route="ophthalmic").canonical_name == "Dexamethasone"
