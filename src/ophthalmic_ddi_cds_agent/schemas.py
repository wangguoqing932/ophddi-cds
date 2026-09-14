from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, model_validator


class RiskLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class TherapeuticIndexTier(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


RISK_ORDER: dict[RiskLevel, int] = {
    RiskLevel.UNKNOWN: 0, RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3,
}


class SourceRecord(BaseModel):
    """A cached, auditable source record used to build a registry field."""
    provider: str
    source_id: str
    url: str
    retrieved_at: str
    response_sha256: str
    cache_path: str
    parser_version: str
    purpose: str
    verification_status: str = "verified"


class EntityA(BaseModel):
    """Canonical ophthalmic product or active-moiety registry record."""
    entity_a_id: str
    primary_name: str
    aliases: list[str] = Field(default_factory=list)
    category: str
    active_mechanisms: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    evidence_sources: list[str] = Field(default_factory=list)
    canonical_name: str = ""
    rxcui: str = ""
    pubchem_cid: str = ""
    route: str = "ophthalmic"
    dosage_form: str = ""
    ophthalmic_administration: str = "topical"
    components: list[str] = Field(default_factory=list)
    provenance: list[SourceRecord] = Field(default_factory=list)
    curation_status: str = "needs_review"
    extra: dict[str, Any] = Field(default_factory=dict)


class EntityB(BaseModel):
    """Canonical systemic medication registry record."""
    entity_b_id: str
    generic_name: str
    aliases: list[str] = Field(default_factory=list)
    drug_class: str
    flags: list[str] = Field(default_factory=list)
    metabolic_pathways: list[str] = Field(default_factory=list)
    transporter_substrates: list[str] = Field(default_factory=list)
    therapeutic_index_tier: TherapeuticIndexTier = TherapeuticIndexTier.UNKNOWN
    narrow_therapeutic_index: bool = False
    label_source: str = ""
    canonical_name: str = ""
    rxcui: str = ""
    pubchem_cid: str = ""
    route: str = "systemic"
    dosage_form: str = ""
    provenance: list[SourceRecord] = Field(default_factory=list)
    curation_status: str = "needs_review"

    @model_validator(mode="after")
    def set_narrow_therapeutic_index(self) -> "EntityB":
        if "narrow_therapeutic_index" in self.flags:
            self.narrow_therapeutic_index = True
        return self


class PatientFactors(BaseModel):
    factors: list[str] = Field(default_factory=list)


class InteractionCase(BaseModel):
    case_id: str
    entity_a: str
    entity_b: str
    patient_factors: list[str] = Field(default_factory=list)
    gold_risk_level: RiskLevel | None = None
    risk_type: list[str] = Field(default_factory=list)
    notes: str = ""


class EvidenceChunk(BaseModel):
    """A source-located evidence excerpt or attributed abstract summary.

    `approved_release` is assigned only after source/cache/locator validation;
    it is a data-release status, not a clinical-expert endorsement.
    """
    evidence_id: str
    title: str
    source: str
    source_type: str
    evidence_level: str = ""
    evidence_relation: str = ""
    source_id: str = ""
    source_version: str = ""
    source_locator: str = ""
    citation_hint: str = ""
    pmid: str = ""
    doi: str = ""
    verification_status: str = "candidate"
    source_quality_rank: str = ""
    retrieved_at: str = ""
    cache_path: str = ""
    content_sha256: str = ""
    parser_version: str = ""
    authorized_source: bool = False
    rule_ids: list[str] = Field(default_factory=list)
    entities_a: list[str] = Field(default_factory=list)
    entities_b: list[str] = Field(default_factory=list)
    risk_types: list[str] = Field(default_factory=list)
    claim_text: str = ""
    text: str
    url: str = ""
    weight: int = 1


class RiskSignal(BaseModel):
    rule_id: str
    risk_level: RiskLevel
    risk_type: str
    rationale: str
    recommendation: str
    matched_terms: dict[str, list[str]] = Field(default_factory=dict)
    evidence_ids: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    rules_yaml_sha256: str = ""
    output_class: str = "insufficient_evidence"
    support_tier: str = "none"
    action_behavior: str = "no_ddi_conclusion"
    claim_scope: str = ""
    verified_citation_ids: list[str] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    risk_level: RiskLevel
    risk_types: list[str] = Field(default_factory=list)
    signals: list[RiskSignal] = Field(default_factory=list)
    confidence: str = "low"
    confidence_score: float = 0.0


class SafetyReport(BaseModel):
    case_id: str
    entity_a: str
    entity_b: str
    patient_factors: list[str] = Field(default_factory=list)
    risk_assessment: RiskAssessment
    evidence: list[EvidenceChunk] = Field(default_factory=list)
    report_text: str
    context_char_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
