"""OphDDI-CDS — ophthalmic drug interaction knowledge base and clinical decision support (Streamlit UI, v2.4, 3-tab).

Three tabs (forced by Executor Phase 6 since skill v2.4):
  1. 📊 Overview — agent profile + LightRAG build status + rule/citation status
  2. 💬 RAG Q&A — free-form Q&A: LightRAG retrieval -> DeepSeek answers
  3. 🔍 Risk assessment — A x B selection -> risk report (4 sub-tabs)

The Overview and Chat tabs read everything from project files at runtime
(.planner.config.json, PLAN.md, .executor/progress.json, configs/rules.yaml),
so this template is project-agnostic — no per-project hardcoding.

Usage:
    streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import streamlit as st

# Python 3.10 compatibility for the 3.11 StrEnum used by the package schemas.
import enum as _enum
if not hasattr(_enum, "StrEnum"):
    class _StrEnum(str, _enum.Enum):
        def __str__(self) -> str:
            return str(self.value)
    _enum.StrEnum = _StrEnum

PROJECT_ROOT = Path(__file__).resolve().parents[1]

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

from ophthalmic_ddi_cds_agent.evidence_store import EvidenceStore
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG
from ophthalmic_ddi_cds_agent.lightrag_adapter import LightRAGAdapter
from ophthalmic_ddi_cds_agent.llm_client import LLMClient
from ophthalmic_ddi_cds_agent.safety_agent import SafetyAgent, SafetyAgentConfig


# ─────────────────────────────────────────────────────────────────────────────
# Registry helpers (read the curated CSVs directly)
# ─────────────────────────────────────────────────────────────────────────────
def load_a_registry() -> dict[str, dict]:
    """id -> {name, category} for ophthalmic drugs."""
    out = {}
    import csv
    with (PROJECT_ROOT / "data" / "seed" / "entities_a.csv").open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            out[row["topical_ophthalmic_medications_id"]] = {
                "name": row["primary_name"], "category": row.get("category", "")}
    return out


def load_b_registry() -> dict[str, dict]:
    """id -> {name, drug_class} for systemic drugs."""
    out = {}
    import csv
    with (PROJECT_ROOT / "data" / "seed" / "entities_b.csv").open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            out[row["entity_b_id"]] = {
                "name": row["generic_name"], "drug_class": row.get("drug_class", "")}
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Design tokens — aligned with manuscript Figure 1-5 (NMI pastel palette)
# ─────────────────────────────────────────────────────────────────────────────
RISK_COLORS = {
    "high":    {"bg": "#1F4E79", "fg": "#ffffff", "soft": "#EAF0F5", "border": "#1F4E79"},
    "medium":  {"bg": "#4A7FA5", "fg": "#ffffff", "soft": "#EEF3F7", "border": "#3E6C8E"},
    "low":     {"bg": "#6C8DA8", "fg": "#ffffff", "soft": "#F4F7FA", "border": "#6C8DA8"},
    "unknown": {"bg": "#E8A33D", "fg": "#ffffff", "soft": "#FFF8EC", "border": "#C58A2A"},
}

EVIDENCE_LEVEL_COLORS = {
    "A": "#1F4E79",  # regulatory label
    "B": "#4A7FA5",  # meta-analysis
    "C": "#7FA3BE",  # original study
    "D": "#E8A33D",  # in vitro / animal
    "E": "#8D6E63",  # mechanism inference
}

MECHANISM_COLORS = {
    "endocrine": "#5B8FF9",
    "genetic": "#722ED1",
    "physicochemical": "#F6BD16",
    "toxicity": "#F4664A",
    "patient_factor": "#5AD8A6",
    "regulatory": "#B8B8B8",
}


# ─────────────────────────────────────────────────────────────────────────────
# Page config + global CSS
# ─────────────────────────────────────────────────────────────────────────────
def set_page_config() -> None:
    st.set_page_config(
        page_title="OphDDI-CDS | Ophthalmic Drug Interaction Decision Support",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
    <style>
        /* Typography */
        .stApp { font-family: 'Arial', 'Helvetica Neue', sans-serif; }
        h1, h2, h3 { letter-spacing: -0.02em; }

        /* Main container tighter */
        .block-container { padding-top: 1.5rem; padding-bottom: 1rem; max-width: 1400px; }

        /* Risk hero card */
        .risk-hero {
            border-radius: 12px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            border-left: 6px solid;
        }
        .risk-hero-title { font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.8; }
        .risk-hero-level {
            font-size: 3rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 0.5rem;
        }
        .risk-hero-meta {
            font-size: 0.875rem;
            opacity: 0.85;
        }

        /* Stat cards */
        .stat-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }
        .stat-card .label { font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }
        .stat-card .value { font-size: 1.5rem; font-weight: 700; color: #111827; }

        /* Evidence card */
        .evidence-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-left: 4px solid;
            border-radius: 6px;
            padding: 0.875rem 1rem;
            margin-bottom: 0.75rem;
        }
        .evidence-card .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        .evidence-card .level-badge {
            display: inline-block;
            color: white;
            font-weight: 700;
            font-size: 0.75rem;
            padding: 2px 8px;
            border-radius: 4px;
        }
        .evidence-card .source { font-size: 0.75rem; color: #6b7280; }
        .evidence-card .body { font-size: 0.875rem; color: #374151; line-height: 1.5; }

        /* Rule chip */
        .rule-chip {
            display: inline-block;
            background: #f3f4f6;
            color: #374151;
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 12px;
            margin-right: 6px;
            margin-bottom: 4px;
            border: 1px solid #e5e7eb;
        }

        /* Status pill (Overview tab) */
        .status-pill {
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 12px;
            color: white;
        }

        /* Footer */
        .app-footer {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #e5e7eb;
            font-size: 0.75rem;
            color: #6b7280;
            text-align: center;
        }

        /* Hide Streamlit branding and deploy button */
        #MainMenu { visibility: hidden; }
        [data-testid="stAppDeployButton"] { display: none; }
        footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Project file readers (Overview tab) — all defensive, never crash
# ─────────────────────────────────────────────────────────────────────────────
def _load_json(path: Path) -> dict | None:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def read_project_config() -> dict:
    return _load_json(PROJECT_ROOT / ".planner.config.json") or {}


def read_progress() -> dict:
    data = _load_json(PROJECT_ROOT / ".executor" / "progress.json") or {}
    # progress.json stores phases at top level; older layouts wrapped them under "phases"
    return data.get("phases", data)


def read_plan_title() -> str:
    plan = PROJECT_ROOT / "PLAN.md"
    if not plan.exists():
        return ""
    try:
        first = plan.read_text(encoding="utf-8").lstrip().splitlines()[0]
        return first.lstrip("# ").strip()
    except Exception:
        return ""


def read_rules_yaml_sha() -> str:
    rules = PROJECT_ROOT / "configs" / "rules.yaml"
    if not rules.exists():
        return ""
    return hashlib.sha256(rules.read_bytes()).hexdigest()


def index_freshness() -> tuple[str, str]:
    """Return (status_label, detail).

    status_label ∈ {"fresh", "stale_rules_changed", "stale_not_built", "unknown"}.
    Compares: phase3.rules_yaml_sha256 vs phase4.index_built_against_rules_sha256
    vs current configs/rules.yaml sha.
    """
    progress = read_progress()
    p3 = progress.get("phase3", {}) or {}
    p4 = progress.get("phase4", {}) or {}
    verified_sha = p3.get("rules_yaml_sha256")
    index_sha = p4.get("index_built_against_rules_sha256")
    current_sha = read_rules_yaml_sha()
    index_dir = PROJECT_ROOT / "data" / "processed" / "lightrag_index"
    if not index_sha or not index_dir.exists():
        return ("stale_not_built", "LightRAG index not built or not bound to a rules SHA (run Phase 4)")
    if verified_sha and current_sha and verified_sha != current_sha:
        return ("stale_rules_changed", "rules.yaml changed since the last verification; rerun Phase 3 + Phase 4")
    if index_sha != verified_sha:
        return ("stale_rules_changed", "Index built against a different rules.yaml; rebuild it")
    return ("fresh", "Index matches the current rules.yaml")


# ─────────────────────────────────────────────────────────────────────────────
# Components
# ─────────────────────────────────────────────────────────────────────────────
def render_risk_hero(risk_level: str, confidence: float, n_signals: int,
                     n_evidence: int, elapsed: float, llm_label: str) -> None:
    colors = RISK_COLORS.get(risk_level, RISK_COLORS["unknown"])
    icon = {"high": "⚠️", "medium": "⚡", "low": "✅", "unknown": "❓"}.get(risk_level, "❓")

    recommendation = {
         "high": "Avoid this exposure; clinical follow-up and biological monitoring",
         "medium": "Reduce exposure; further assessment if needed",
         "low": "Current evidence does not indicate a significant risk",
         "unknown": "Insufficient evidence; continue monitoring the literature",
    }.get(risk_level, "")

    st.markdown(f"""
    <div class="risk-hero" style="background:{colors['soft']}; border-left-color:{colors['bg']};">
        <div class="risk-hero-title" style="color:{colors['bg']};">RISK LEVEL</div>
        <div class="risk-hero-level" style="color:{colors['bg']};">{icon} {risk_level.upper()}</div>
        <div class="risk-hero-meta" style="color:{colors['border']};">
            <strong>Triggered rules:</strong> {n_signals} &nbsp;·&nbsp;
            <strong>Evidence passages:</strong> {n_evidence} &nbsp;·&nbsp;
            <strong>LLM:</strong> {llm_label}
        </div>
        <div style="margin-top:0.75rem; padding:0.5rem 0.75rem; background:white; border-radius:6px; font-size:0.875rem; color:#374151;">
            <strong>Recommendation:</strong> {recommendation}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(label: str, value: str, accent: str = "#1F4E79") -> None:
    st.markdown(f"""
    <div class="stat-card">
        <div class="label">{label}</div>
        <div class="value" style="color:{accent};">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_evidence_card(level: str, title: str, source: str, text: str) -> None:
    color = EVIDENCE_LEVEL_COLORS.get(level, "#6b7280")
    # Truncate text to keep cards compact
    display_text = text[:400] + ("..." if len(text) > 400 else "")
    st.markdown(f"""
    <div class="evidence-card" style="border-left-color:{color};">
        <div class="header">
            <span class="level-badge" style="background:{color};">Level {level}</span>
            <span class="source">{source}</span>
        </div>
        <div style="font-weight:600; font-size:0.875rem; margin-bottom:0.25rem; color:#111827;">{title}</div>
        <div class="body">{display_text}</div>
    </div>
    """, unsafe_allow_html=True)


def render_rule_chip(rule_id: str, severity: str, mechanism: str) -> None:
    color = RISK_COLORS.get(severity, RISK_COLORS["unknown"])["bg"]
    st.markdown(f"""
    <span class="rule-chip" style="border-color:{color}; color:{color};">
        <strong>[{severity.upper()}]</strong> {rule_id} <span style="opacity:0.6;">· {mechanism}</span>
    </span>
    """, unsafe_allow_html=True)


def render_status_pill(status: str) -> None:
    colors = {"fresh": "#1F4E79", "stale_rules_changed": "#E8A33D",
              "stale_not_built": "#B54A4A", "unknown": "#767676"}
    labels = {"fresh": "✅ Fresh", "stale_rules_changed": "⚠️ Rules changed — rebuild",
              "stale_not_built": "❌ Not built", "unknown": "❓ Unknown"}
    c = colors.get(status, "#6b7280")
    l = labels.get(status, status)
    st.markdown(f'<span class="status-pill" style="background:{c};">{l}</span>',
                unsafe_allow_html=True)


def render_footer(report_metadata: dict) -> None:
    st.markdown(f"""
    <div class="app-footer">
        <div>OphDDI-CDS · deterministic rule engine + class matrix + hard constraint</div>
        <div style="margin-top:0.5rem;">
            case_id: <code>{report_metadata.get('case_id', '-')}</code> ·
            LLM: <code>{report_metadata.get('llm_label', '-')}</code> ·
            context: <code>{report_metadata.get('context_chars', 0)}</code> chars
        </div>
        <div style="margin-top:0.5rem; opacity:0.7;">
            ⚠️ Research decision support only. Final judgment rests with the clinician. Not for automated diagnosis.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Cached agent (Screening tab)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading registries and rule engine…")
def get_agent(use_real_llm: bool, use_lightrag: bool, top_k: int) -> SafetyAgent:
    """Cascade agent: deterministic rule layer (40 rules + G19 hard constraint)
    covers the decision; evidence store provides the citation chain."""
    return SafetyAgent(config=SafetyAgentConfig(project_root=PROJECT_ROOT))


@st.cache_resource(show_spinner="Loading LightRAG index…")
def get_lightrag_adapter():
    """Cached LightRAG adapter for the Chat tab (RAG-augmented Q&A)."""
    try:
        return LightRAGAdapter()
    except Exception as e:
        st.warning(f"LightRAG initialization failed: {e}")
        return None


@st.cache_resource(show_spinner="Loading DeepSeek client…")
def get_chat_llm():
    """DeepSeek chat client for the Chat tab. Reads key from .env via llm_client."""
    try:
        return LLMClient(provider="deepseek", temperature=0.2, max_tokens=1024)
    except Exception as e:
        st.warning(f"DeepSeek client initialization failed: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Overview
# ─────────────────────────────────────────────────────────────────────────────
def overview_tab() -> None:
    st.header("📊 Overview & build status")

    cfg = read_project_config()
    progress = read_progress()
    plan_title = read_plan_title()

    # --- Agent intro ---
    st.subheader("🧬 Agent profile")
    project = cfg.get("project", {}) or {}
    intro_cols = st.columns([2, 1])
    with intro_cols[0]:
        st.write(f"**Code**: `ophthalmic-ddi-cds` / OphDDI-CDS")
        st.write(f"**Created**: {project.get('created_date', '-')}")
        st.write("**One-line description**: Absorption-first deterministic cascade for ophthalmic drug-drug interaction screening.")
        domain = cfg.get("domain", {}) or {}
        st.write("**Research direction**: Ophthalmic drug-drug interactions and clinical decision support.")
    with intro_cols[1]:
        st.write("**Target journal**")
        tj = cfg.get("target_journal", {})
        if isinstance(tj, dict):
            st.write(f"· First choice: {tj.get('first', '-')}")
            backups = tj.get('backup') or []
            for b in backups[:3]:
                st.write(f"· Alternative: {b}")
        else:
            st.write(str(tj or '-'))

    # --- Architecture ---
    st.subheader("🏗️ Three-layer cascade")
    entities = cfg.get("entities", {}) or {}
    ea = entities.get("a", {}) or {}
    eb = entities.get("b", {}) or {}
    interaction = cfg.get("interaction", {}) or {}
    st.markdown(f"""
```
User input (ophthalmic agent + systemic drug + patient factors)
   │
   ├─ ① Rule engine (risk_rules.py + rules.yaml)
   │     ├─ flag matching + patient-factor escalation
   │     └─ triggered mechanisms: {', '.join(interaction.get('mechanisms', []) or [])}
   │
   ├─ ② LightRAG evidence retrieval (lightrag_adapter.py)
   │     └─ DeepSeek entity extraction + Volcengine Ark embeddings
   │
   └─ ③ LLM arbitration (safety_agent.py)
         └─ DeepSeek generates a structured report from rule signals + evidence
   │
   ▼
Traceable, explainable risk report
```
""")

    st.divider()

    # --- LightRAG build status ---
    st.subheader("📚 LightRAG build status")
    p4 = progress.get("phase4", {}) or {}
    p2 = progress.get("phase2", {}) or {}
    p1 = progress.get("phase1", {}) or {}

    fresh_status, fresh_detail = index_freshness()
    fresh_cols = st.columns([1, 3])
    with fresh_cols[0]:
        render_status_pill(fresh_status)
    with fresh_cols[1]:
        st.caption(fresh_detail)

    stat_cols = st.columns(5)
    with stat_cols[0]:
        render_stat_card("Entity A (ophthalmic)", str(p1.get("entity_a_count", "-")))
    with stat_cols[1]:
        render_stat_card("Entity B (systemic)", str(p1.get("entity_b_count", "-")))
    with stat_cols[2]:
        render_stat_card("Evidence chunks", str(p2.get("evidence_chunks", "-")))
    with stat_cols[3]:
        render_stat_card("Graph entities", str(p4.get("entities_extracted", "-")))
    with stat_cols[4]:
        render_stat_card("Graph relations", str(p4.get("relations_extracted", "-")))

    meta_cols = st.columns(3)
    with meta_cols[0]:
        st.metric("Index size", f"{(p4.get('index_disk_kb', 0) or 0) / 1024:.1f} MB")
        st.metric("Build time", f"{(p4.get('build_time_sec', 0) or 0) / 60:.1f} min")
    with meta_cols[1]:
        st.caption("Chat LLM")
        st.code(p4.get("llm_provider", "-"))
        st.caption("Embedding")
        st.code(p4.get("embedding_provider", "-"))
    with meta_cols[2]:
        st.caption("Evidence-level distribution (A/B/C/D/E)")
        lv = p2
        st.write(f"A(regulatory) **{lv.get('level_a', 0)}** · B(meta-analysis) **{lv.get('level_b', 0)}** · "
                 f"C(original study) **{lv.get('level_c', 0)}** · D(in vitro/animal) **{lv.get('level_d', 0)}** · "
                 f"E(mechanism) **{lv.get('level_e', 0)}**")

    st.divider()

    # --- Rule engine + citation verification status ---
    st.subheader("⚙️ Rule engine & citation verification")
    p3 = progress.get("phase3", {}) or {}
    cite_cols = st.columns(4)
    with cite_cols[0]:
        render_stat_card("Rules", str(p3.get("rule_count", "-")))
    with cite_cols[1]:
        render_stat_card("Patient-factor policies", str(p3.get("patient_factor_rules", "-")))
    with cite_cols[2]:
        verified = p3.get("citations_verified")
        if verified is True:
            render_stat_card("Citation check", "✅ Passed", "#1F4E79")
        elif verified is False:
            render_stat_card("Citation check", "❌ Failed", "#B54A4A")
        else:
            render_stat_card("Citation check", "— Not run", "#767676")
    with cite_cols[3]:
        render_stat_card("Verified references", str(p3.get("verified_count", "-")))

    cv_cols = st.columns(3)
    with cv_cols[0]:
        st.metric("verified (DOI/PMID)", p3.get("verified_count", 0))
    with cv_cols[1]:
        st.metric("report_ok (authoritative report)", p3.get("report_ok_count", 0))
    with cv_cols[2]:
        st.metric("db_ok (database accession)", p3.get("db_ok_count", 0))

    if p3.get("rules_yaml_sha256"):
        st.caption(f"rules.yaml SHA256: `{p3['rules_yaml_sha256'][:32]}...`")
        st.caption(f"Current file SHA256: `{read_rules_yaml_sha()[:32]}...`")

    if p3.get("citations_report"):
        st.caption(f"Verification report: `{p3['citations_report']}`")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — RAG Q&A
# ─────────────────────────────────────────────────────────────────────────────
def chat_tab() -> None:
    st.header("💬 RAG-enhanced Q&A")
    st.caption("Each question first queries the LightRAG knowledge base; the model then answers from the retrieved evidence and states when evidence is insufficient.")

    # guard: index must exist
    index_dir = PROJECT_ROOT / "data" / "processed" / "lightrag_index"
    if not index_dir.exists():
        st.error("🚫 LightRAG index not built. Run Executor Phase 4 first:")
        st.code("python <skill>/scripts/phase4_build_index.py --project-root .", language="bash")
        return

    fresh_status, _ = index_freshness()
    if fresh_status == "stale_rules_changed":
        st.warning("⚠️ The index is stale relative to the current rules.yaml; answers may reflect older rules. Rebuild Phase 4.")

    # sidebar-ish controls inline (chat tab keeps its own controls)
    ctrl_cols = st.columns([1, 1, 2])
    with ctrl_cols[0]:
        show_evidence = st.toggle("Show retrieved evidence", value=True, key="chat_show_ev")
    with ctrl_cols[1]:
        if st.button("🧹 Clear conversation", use_container_width=True):
            st.session_state["chat_messages"] = []
            st.rerun()

    adapter = get_lightrag_adapter()
    llm = get_chat_llm()
    if adapter is None or llm is None:
        st.error("LightRAG or DeepSeek client failed to initialize. Check .env (DEEPSEEK_API_KEY / ARK_DOUBAO_API_KEY).")
        return

    if getattr(llm, "degraded", False):
        st.warning("⚠️ No DeepSeek API key; running in stub mode (template replies only). Configure .env.")

    # init history
    st.session_state.setdefault("chat_messages", [])

    # render history
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and show_evidence and msg.get("evidence"):
                with st.expander(f"📚 Retrieved evidence ({len(msg['evidence'])} passages)"):
                    for i, ev in enumerate(msg["evidence"], 1):
                        st.caption(f"Passage {i}")
                        st.write(ev[:600] + ("..." if len(ev) > 600 else ""))

    # input
    question = st.chat_input("Ask the agent… (e.g., which mechanisms drive the interaction between topical timolol and verapamil?)")
    if not question:
        return

    st.session_state["chat_messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # 1) retrieve
    with st.chat_message("assistant"):
        with st.spinner("Retrieving from the LightRAG knowledge base…"):
            try:
                import asyncio
                retrieved_text = asyncio.run(adapter.query(question, mode="hybrid"))
            except Exception as e:
                st.error(f"LightRAG retrieval failed: {e}")
                return
        retrieved_text = retrieved_text or ""
        # split into pseudo-chunks for display (LightRAG returns concatenated text)
        evidence_chunks = [c.strip() for c in retrieved_text.split("\n\n") if c.strip()][:8]

        if not retrieved_text.strip():
            answer = "No relevant evidence was retrieved from the knowledge base. Try more specific keywords."
        elif getattr(llm, "degraded", False):
            # Offline mode (no API key): show retrieved evidence directly
            answer = (
                "(Offline demo mode: no DeepSeek API key configured. The relevant evidence retrieved "
                "from the knowledge base is shown below. Configure DEEPSEEK_API_KEY in .env for the full AI answer.)\n\n"
                + "\n\n".join(evidence_chunks[:4])
            )
        else:
            # 2) DeepSeek answer grounded in evidence
            with st.spinner("Generating an evidence-grounded answer…"):
                system = (
                    "You are a medical question-answering assistant grounded in a curated knowledge base. "
                    "Answer **only** from the evidence passages below. If the evidence is insufficient, say so explicitly and do not invent. "
                    "Use concise bullet points and cite [Evidence N] after each claim."
                )
                prompt = f"[Evidence passages]\n{retrieved_text[:6000]}\n\n[User question]\n{question}"
                try:
                    resp = llm.complete(prompt=prompt, system=system)
                    answer = resp.text
                except Exception as e:
                    answer = f"DeepSeek call failed: {e}"

        st.write(answer)
        if show_evidence and evidence_chunks:
            with st.expander(f"📚 Retrieved evidence ({len(evidence_chunks)} passages)"):
                for i, ev in enumerate(evidence_chunks, 1):
                    st.caption(f"Passage {i}")
                    st.write(ev[:600] + ("..." if len(ev) > 600 else ""))

    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": answer, "evidence": evidence_chunks}
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Risk assessment
# ─────────────────────────────────────────────────────────────────────────────
def screening_tab(use_real_llm: bool, use_lightrag: bool, top_k: int) -> None:
    st.header("🔍 Risk assessment")

    # ─── Demo-case shortcut ───
    try:
        _demo_cases = json.loads((PROJECT_ROOT / "outputs" / "demo" / "demo_cases_curated.json").read_text(encoding="utf-8"))
        _a_reg = load_a_registry()
        _b_reg = load_b_registry()
        _a_opts = {f"{aid}: {v['name']}": aid for aid, v in _a_reg.items()}
        _b_opts = {f"{bid}: {v['name']}": bid for bid, v in _b_reg.items()}
        with st.expander("🎯 Load a demo case (auto-fills the selectors below)", expanded=False):
            _demo_names = [f"{c['ophthalmic']} × {c['systemic']} ({c['risk']})" for c in _demo_cases]
            _pick = st.selectbox("Select a demo case", ["— Select manually —"] + _demo_names, key="screen_demo_pick")
            if _pick != "— Select manually —":
                _idx = _demo_names.index(_pick)
                _a_name = _demo_cases[_idx]["ophthalmic"]
                _b_name = _demo_cases[_idx]["systemic"]
                _la = next((k for k, v in _a_opts.items() if v["name"] == _a_name), None)
                _lb = next((k for k, v in _b_opts.items() if v["name"] == _b_name), None)
                if _la:
                    st.session_state["screen_a"] = _la
                if _lb:
                    st.session_state["screen_b"] = _lb
                    st.session_state["screen_b_search"] = ""
                st.caption(f"✅ Loaded: {_a_name} × {_b_name}. Click “🚀 Run assessment”.")
    except Exception as _e:
        st.caption(f"(Demo cases failed to load: {_e})")

    # ─── Input selection ───
    st.subheader("Select a drug pair")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Ophthalmic agent**")
        try:
            a_reg = load_a_registry()
            a_options = {f"{aid}: {v['name']}": aid for aid, v in a_reg.items()}
            a_label = st.selectbox("Select ophthalmic agent", options=list(a_options.keys()),
                                   label_visibility="collapsed",
                                   key="screen_a")
            a_id = a_options[a_label]
        except Exception as e:
            st.error(f"Load failed: {e}")
            return

    with col_b:
        st.markdown("**Systemic medication**")
        try:
            b_reg = load_b_registry()
            b_options = {f"{bid}: {v['name']}": bid for bid, v in b_reg.items()}
            search = st.text_input("Search", "", help="Filter by keyword", label_visibility="collapsed",
                                    placeholder="🔍 Filter by keyword...", key="screen_b_search")
            filtered = [k for k in b_options if search.lower() in k.lower()] if search else list(b_options)
            if not filtered:
                st.warning("No match; showing all options")
                filtered = list(b_options)
            b_label = st.selectbox("Select systemic medication", options=filtered,
                                   label_visibility="collapsed", key="screen_b")
            b_id = b_options[b_label]
        except Exception as e:
            st.error(f"Load failed: {e}")
            return

    # Patient factors
    with st.expander("🏥 Patient factors (optional; affects rule triggering)", expanded=False):
        pf_options = ["elderly", "renal_impairment", "polypharmacy"]
        patient_factors = st.multiselect("Applicable patient factors", pf_options, default=[], key="screen_pf")

    # Run button
    if not st.button("🚀 Run assessment", type="primary", use_container_width=True, key="screen_run"):
        return

    with st.spinner("Running the deterministic cascade…"):
        try:
            t0 = time.time()
            agent = get_agent(use_real_llm, use_lightrag, top_k)
            a_name = a_reg[a_id]["name"]
            b_name = b_reg[b_id]["name"]
            report = agent.assess(a_name, b_name, patient_factors)
            elapsed = time.time() - t0
        except Exception as e:
            err_type = type(e).__name__
            err_msg = str(e)
            st.error(f"Assessment failed: {err_type}: {err_msg}")
            return

    risk = report.risk_assessment.risk_level.value
    confidence = float(report.risk_assessment.confidence_score or 0)
    n_signals = len(report.risk_assessment.signals)
    n_evidence = len(report.evidence)
    llm_label = report.metadata.get("llm_label", "rule-engine")
    assessment_status = report.risk_assessment.assessment_status

    # ─── Hero ───
    st.divider()
    if assessment_status == "unassessed":
        # Never present a default-path pair as an assessed low-risk result.
        st.markdown(f"""
        <div class="risk-hero" style="background:#FFF4E1; border-left-color:#B7791F;">
            <div class="risk-hero-title" style="color:#8A5A12;">ASSESSMENT STATUS</div>
            <div class="risk-hero-level" style="color:#8A5A12;">⚠️ UNASSESSED</div>
            <div class="risk-hero-meta" style="color:#6B4A12;">
                <strong>Default output grade:</strong> low (not assessed) &nbsp;·&nbsp;
                <strong>Triggered rules:</strong> {n_signals} &nbsp;·&nbsp;
                <strong>Evidence passages:</strong> {n_evidence}
            </div>
            <div style="margin-top:0.75rem; padding:0.5rem 0.75rem; background:white; border-radius:6px; font-size:0.875rem; color:#6B4A12;">
                <strong>No rule or defined matrix cell covers this pair.</strong>
                This is a coverage gap, not evidence of safety. Refer for manual medication review.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        render_risk_hero(risk, confidence, n_signals, n_evidence, elapsed, llm_label)

    # ─── Quick stats row ───
    col1, col2, col3 = st.columns(3)
    with col1:
        render_stat_card("Triggered rules", str(n_signals), RISK_COLORS.get(risk, RISK_COLORS["unknown"])["bg"])
    with col2:
        render_stat_card("Evidence passages", str(n_evidence), "#4A7FA5")
    with col3:
        render_stat_card("Assessment status", assessment_status, "#1F4E79")

    st.divider()

    # ─── Sub-tabs ───
    tab_summary, tab_rules, tab_evidence, tab_technical = st.tabs([
        "📋 Summary", "⚙️ Rule details", "📚 Evidence chain", "🔧 Technical details"
    ])

    with tab_summary:
        st.subheader("📄 Full report")
        st.code(report.report_text, language="markdown")

        if report.risk_assessment.signals:
            st.subheader("🎯 Main risk signals (by severity)")
            sorted_signals = sorted(
                report.risk_assessment.signals,
                key=lambda s: {"high": 0, "medium": 1, "low": 2, "unknown": 3}.get(s.risk_level.value, 4)
            )
            for sig in sorted_signals[:3]:  # top 3 only in summary
                sev = sig.risk_level.value
                render_rule_chip(sig.rule_id, sev, sig.risk_type.split("_")[-1] if sig.risk_type else "")

    with tab_rules:
        if not report.risk_assessment.signals:
            st.info("✅ No rule triggered")
        else:
            sorted_signals = sorted(
                report.risk_assessment.signals,
                key=lambda s: {"high": 0, "medium": 1, "low": 2, "unknown": 3}.get(s.risk_level.value, 4)
            )
            for sig in sorted_signals:
                sev = sig.risk_level.value
                sev_icon = {"high": "🔴", "medium": "🟠", "low": "🟢", "unknown": "⚪"}.get(sev, "⚪")
                sev_color = RISK_COLORS.get(sev, RISK_COLORS["unknown"])["bg"]
                st.markdown(f"### {sev_icon} {sig.rule_id}")
                st.markdown(f"<span style='color:{sev_color}; font-weight:600;'>[{sev.upper()}]</span> · <code>{sig.risk_type}</code>", unsafe_allow_html=True)
                st.write(f"**Rationale**: {sig.rationale}")
                if sig.recommendation:
                    st.write(f"**Recommendation**: {sig.recommendation}")
                if sig.matched_terms:
                    with st.expander("Matched tags"):
                        for k, v in sig.matched_terms.items():
                            if v:
                                st.write(f"- **{k}**: {', '.join(v)}")
                st.divider()

    with tab_evidence:
        if not report.evidence:
            st.info("📚 No evidence retrieved")
        else:
            # Filter by level
            levels_present = sorted({ev.evidence_level for ev in report.evidence})
            selected_levels = st.multiselect(
                "Filter evidence level",
                options=["A", "B", "C", "D", "E"],
                default=levels_present,
                help="A=regulatory label, B=meta-analysis, C=original study, D=in vitro/animal, E=mechanism inference",
                key="screen_ev_filter",
            )
            for ev in report.evidence:
                if ev.evidence_level not in selected_levels:
                    continue
                render_evidence_card(ev.evidence_level, ev.title[:80], ev.source, ev.text)

    with tab_technical:
        st.subheader("🔧 Metadata")
        meta_cols = st.columns(3)
        with meta_cols[0]:
            st.metric("case_id", report.case_id)
            st.metric("entity_a_id", report.metadata.get("entity_a_id"))
            st.metric("entity_b_id", report.metadata.get("entity_b_id"))
        with meta_cols[1]:
            st.metric("LLM role", report.metadata.get("llm_role"))
            st.metric("LLM model", report.metadata.get("llm_label"))
            st.metric("Context characters", report.context_char_count)
        with meta_cols[2]:
            st.metric("Rule signals", report.metadata.get("n_signals"))
            st.metric("Evidence passages", report.metadata.get("n_evidence"))
            st.metric("Assessment status", assessment_status)

        with st.expander("Full metadata JSON"):
            st.json(report.metadata)

    # ─── Footer ───
    render_footer({
        "case_id": report.case_id,
        "llm_label": llm_label,
        "context_chars": report.context_char_count,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Main — 3 top-level tabs
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    set_page_config()

    # Header
    st.title("🧬 OphDDI-CDS — Ophthalmic Drug Interaction Knowledge Base and Clinical Decision Support")
    st.caption("Topical ophthalmic drugs × systemic medications · deterministic three-layer cascade (rules + class matrix + hard constraint)")

    # ─── Sidebar (applies to Screening tab; Chat has its own inline controls) ───
    with st.sidebar:
        st.header("⚙️ Configuration (Risk assessment tab)")
        use_real_llm = st.toggle("Use real LLM (DeepSeek)", value=True,
                                  help="Off: deterministic rule engine only (stub LLM)")
        use_lightrag = st.toggle("Use LightRAG retrieval", value=True,
                                  help="Off: keyword evidence retrieval")
        top_k = st.slider("Top-K evidence passages", min_value=1, max_value=15, value=5)

        st.divider()
        st.subheader("📊 Registry status")
        try:
            a_reg = load_a_registry()
            b_reg = load_b_registry()
            st.metric("Ophthalmic agents", len(a_reg))
            st.metric("Systemic agents", len(b_reg))
        except Exception as e:
            st.error(f"Registry load failed: {e}")

        if st.button("🔄 Clear cache", use_container_width=True):
            st.cache_resource.clear()
            st.success("Cache cleared")

    # ─── 3 top-level tabs ───
    tab_overview, tab_chat, tab_screening = st.tabs([
        "📊 Overview", "💬 RAG Q&A", "🔍 Risk assessment"
    ])

    with tab_overview:
        overview_tab()

    with tab_chat:
        chat_tab()

    with tab_screening:
        screening_tab(use_real_llm, use_lightrag, top_k)


if __name__ == "__main__":
    main()
