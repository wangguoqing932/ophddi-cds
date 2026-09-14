"""眼科药物相互作用知识库与临床决策支持系统 (ophthalmic-ddi-cds) — modern Streamlit UI (v2.4, 3-tab).

Three tabs (forced by Executor Phase 6 since skill v2.4):
  1. 📊 项目介绍 (Overview)   — agent intro + LightRAG build status + rule/citation status
  2. 💬 RAG 问答 (Chat)        — free-form Q&A: LightRAG retrieval → DeepSeek answers
  3. 🔍 风险评估 (Screening)   — original A×B pick → risk report (4 sub-tabs)

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
    "high":    {"bg": "#dc2626", "fg": "#ffffff", "soft": "#fef2f2", "border": "#991b1b"},
    "medium":  {"bg": "#ea580c", "fg": "#ffffff", "soft": "#fff7ed", "border": "#9a3412"},
    "low":     {"bg": "#16a34a", "fg": "#ffffff", "soft": "#f0fdf4", "border": "#166534"},
    "unknown": {"bg": "#6b7280", "fg": "#ffffff", "soft": "#f9fafb", "border": "#374151"},
}

EVIDENCE_LEVEL_COLORS = {
    "A": "#003f5c",  # deep blue — regulatory
    "B": "#58508d",  # purple — meta-analysis
    "C": "#bc5090",  # pink — original study
    "D": "#ff6361",  # red-orange — in vitro
    "E": "#ffa600",  # amber — mechanism inference
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
        page_title="眼科药物相互作用知识库与临床决策支持系统",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
    <style>
        /* Typography */
        .stApp { font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif; }
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

        /* Hide Streamlit branding */
        #MainMenu { visibility: hidden; }
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
        return ("stale_not_built", "LightRAG 索引未构建或未绑定 rules sha（先跑 phase4）")
    if verified_sha and current_sha and verified_sha != current_sha:
        return ("stale_rules_changed", "rules.yaml 自上次核验后已改动，须重跑 phase3 + phase4")
    if index_sha != verified_sha:
        return ("stale_rules_changed", "索引构建于不同版本的 rules.yaml，须重建")
    return ("fresh", "索引与当前 rules.yaml 一致，可放心问答")


# ─────────────────────────────────────────────────────────────────────────────
# Components
# ─────────────────────────────────────────────────────────────────────────────
def render_risk_hero(risk_level: str, confidence: float, n_signals: int,
                     n_evidence: int, elapsed: float, llm_label: str) -> None:
    colors = RISK_COLORS.get(risk_level, RISK_COLORS["unknown"])
    icon = {"high": "⚠️", "medium": "⚡", "low": "✅", "unknown": "❓"}.get(risk_level, "❓")

    recommendation = {
        "high": "强烈建议规避该暴露；临床随访 + 生物监测",
        "medium": "建议减少暴露；必要时进一步评估",
        "low": "目前证据不足以提示显著风险",
        "unknown": "证据不足，建议持续关注研究进展",
    }.get(risk_level, "")

    st.markdown(f"""
    <div class="risk-hero" style="background:{colors['soft']}; border-left-color:{colors['bg']};">
        <div class="risk-hero-title" style="color:{colors['bg']};">风险分级 / Risk Level</div>
        <div class="risk-hero-level" style="color:{colors['bg']};">{icon} {risk_level.upper()}</div>
        <div class="risk-hero-meta" style="color:{colors['border']};">
            <strong>置信度:</strong> {confidence:.0%} &nbsp;·&nbsp;
            <strong>触发规则:</strong> {n_signals} 条 &nbsp;·&nbsp;
            <strong>证据片段:</strong> {n_evidence} 条 &nbsp;·&nbsp;
            <strong>耗时:</strong> {elapsed:.1f}s &nbsp;·&nbsp;
            <strong>LLM:</strong> {llm_label}
        </div>
        <div style="margin-top:0.75rem; padding:0.5rem 0.75rem; background:white; border-radius:6px; font-size:0.875rem; color:#374151;">
            <strong>建议:</strong> {recommendation}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(label: str, value: str, accent: str = "#111827") -> None:
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
    colors = {"fresh": "#16a34a", "stale_rules_changed": "#ea580c",
              "stale_not_built": "#dc2626", "unknown": "#6b7280"}
    labels = {"fresh": "✅ 新鲜", "stale_rules_changed": "⚠️ 规则已改须重建",
              "stale_not_built": "❌ 未构建", "unknown": "❓ 未知"}
    c = colors.get(status, "#6b7280")
    l = labels.get(status, status)
    st.markdown(f'<span class="status-pill" style="background:{c};">{l}</span>',
                unsafe_allow_html=True)


def render_footer(report_metadata: dict) -> None:
    st.markdown(f"""
    <div class="app-footer">
        <div>🧬 眼科药物相互作用知识库与临床决策支持系统 · 由规则引擎 + LightRAG + LLM 仲裁三层架构生成</div>
        <div style="margin-top:0.5rem;">
            case_id: <code>{report_metadata.get('case_id', '-')}</code> ·
            LLM: <code>{report_metadata.get('llm_label', '-')}</code> ·
            context: <code>{report_metadata.get('context_chars', 0)}</code> chars
        </div>
        <div style="margin-top:0.5rem; opacity:0.7;">
            ⚠️ 本输出仅供临床决策支持；最终判断由临床医生做出。请勿用于自动诊断。
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Cached agent (Screening tab)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="加载注册表 + 规则引擎中…")
def get_agent(use_real_llm: bool, use_lightrag: bool, top_k: int) -> SafetyAgent:
    """Cascade agent: deterministic rule layer (40 rules + G19 hard constraint)
    covers the decision; evidence store provides the citation chain."""
    return SafetyAgent(config=SafetyAgentConfig(project_root=PROJECT_ROOT))


@st.cache_resource(show_spinner="加载 LightRAG 索引…")
def get_lightrag_adapter():
    """Cached LightRAG adapter for the Chat tab (RAG-augmented Q&A)."""
    try:
        return LightRAGAdapter()
    except Exception as e:
        st.warning(f"LightRAG 初始化失败: {e}")
        return None


@st.cache_resource(show_spinner="加载 DeepSeek 客户端…")
def get_chat_llm():
    """DeepSeek chat client for the Chat tab. Reads key from .env via llm_client."""
    try:
        return LLMClient(provider="deepseek", temperature=0.2, max_tokens=1024)
    except Exception as e:
        st.warning(f"DeepSeek 客户端初始化失败: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — 项目介绍 / Overview
# ─────────────────────────────────────────────────────────────────────────────
def overview_tab() -> None:
    st.header("📊 项目介绍 & 构建状态")

    cfg = read_project_config()
    progress = read_progress()
    plan_title = read_plan_title()

    # --- Agent intro ---
    st.subheader("🧬 Agent 定位")
    project = cfg.get("project", {}) or {}
    intro_cols = st.columns([2, 1])
    with intro_cols[0]:
        st.write(f"**代号**：`{project.get('code_name', '-')}` / {project.get('chinese_name', '-')}")
        st.write(f"**创建日期**：{project.get('created_date', '-')}")
        st.write(f"**一句话定位**：{plan_title or '（PLAN.md 读取失败）'}")
        domain = cfg.get("domain", {}) or {}
        st.write(f"**研究方向**：{domain.get('research_direction', '-')}")
    with intro_cols[1]:
        st.write("**目标期刊**")
        tj = cfg.get("target_journal", {})
        if isinstance(tj, dict):
            st.write(f"· 一志愿：{tj.get('first', '-')}")
            backups = tj.get('backup') or []
            for b in backups[:3]:
                st.write(f"· 备选：{b}")
        else:
            st.write(str(tj or '-'))

    # --- Architecture ---
    st.subheader("🏗️ 三层混合架构")
    entities = cfg.get("entities", {}) or {}
    ea = entities.get("a", {}) or {}
    eb = entities.get("b", {}) or {}
    interaction = cfg.get("interaction", {}) or {}
    st.markdown(f"""
```
用户输入（{ea.get('chinese_name', 'Entity A')} + {eb.get('chinese_name', 'Entity B')} + 患者因素）
   │
   ├─ ① 规则引擎（risk_rules.py + rules.yaml）
   │     ├─ flag 匹配 + 患者因素升级
   │     └─ 触发条件：{', '.join(interaction.get('mechanisms', []) or [])}
   │
   ├─ ② LightRAG 图组织证据检索（lightrag_adapter.py）
   │     └─ DeepSeek 实体抽取 + Volcengine Ark 嵌入
   │
   └─ ③ LLM 仲裁（safety_agent.py）
         └─ DeepSeek 基于规则信号 + 证据生成结构化报告
   │
   ▼
可追溯、可解释的安全性/推荐性分级报告
```
""")

    st.divider()

    # --- LightRAG build status ---
    st.subheader("📚 LightRAG 构建情况")
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
        render_stat_card("COPD亚型 / 实体A", str(p1.get("entity_a_count", "-")))
    with stat_cols[1]:
        render_stat_card("暴露物 / 实体B", str(p1.get("entity_b_count", "-")))
    with stat_cols[2]:
        render_stat_card("证据 chunks", str(p2.get("evidence_chunks", "-")))
    with stat_cols[3]:
        render_stat_card("图实体数", str(p4.get("entities_extracted", "-")))
    with stat_cols[4]:
        render_stat_card("图关系数", str(p4.get("relations_extracted", "-")))

    meta_cols = st.columns(3)
    with meta_cols[0]:
        st.metric("索引磁盘占用", f"{(p4.get('index_disk_kb', 0) or 0) / 1024:.1f} MB")
        st.metric("构建耗时", f"{(p4.get('build_time_sec', 0) or 0) / 60:.1f} min")
    with meta_cols[1]:
        st.caption("Chat LLM")
        st.code(p4.get("llm_provider", "-"))
        st.caption("Embedding")
        st.code(p4.get("embedding_provider", "-"))
    with meta_cols[2]:
        st.caption("证据级别分布 (A/B/C/D/E)")
        lv = p2
        st.write(f"A(监管) **{lv.get('level_a', 0)}** · B(Meta) **{lv.get('level_b', 0)}** · "
                 f"C(原创) **{lv.get('level_c', 0)}** · D(体外) **{lv.get('level_d', 0)}** · "
                 f"E(机制) **{lv.get('level_e', 0)}**")

    st.divider()

    # --- Rule engine + citation verification status ---
    st.subheader("⚙️ 规则引擎 & 文献核验状态")
    p3 = progress.get("phase3", {}) or {}
    cite_cols = st.columns(4)
    with cite_cols[0]:
        render_stat_card("规则数", str(p3.get("rule_count", "-")))
    with cite_cols[1]:
        render_stat_card("患者因素规则", str(p3.get("patient_factor_rules", "-")))
    with cite_cols[2]:
        verified = p3.get("citations_verified")
        if verified is True:
            render_stat_card("文献核验", "✅ 通过", "#16a34a")
        elif verified is False:
            render_stat_card("文献核验", "❌ 失败", "#dc2626")
        else:
            render_stat_card("文献核验", "— 未跑", "#6b7280")
    with cite_cols[3]:
        render_stat_card("已核验文献", str(p3.get("verified_count", "-")))

    cv_cols = st.columns(3)
    with cv_cols[0]:
        st.metric("verified (DOI/PMID)", p3.get("verified_count", 0))
    with cv_cols[1]:
        st.metric("report_ok (权威报告)", p3.get("report_ok_count", 0))
    with cv_cols[2]:
        st.metric("db_ok (数据库 accession)", p3.get("db_ok_count", 0))

    if p3.get("rules_yaml_sha256"):
        st.caption(f"rules.yaml SHA256：`{p3['rules_yaml_sha256'][:32]}...`")
        st.caption(f"当前文件 SHA256：`{read_rules_yaml_sha()[:32]}...`")

    if p3.get("citations_report"):
        st.caption(f"核验报告：`{p3['citations_report']}`")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — RAG 问答 / Chat
# ─────────────────────────────────────────────────────────────────────────────
def chat_tab() -> None:
    st.header("💬 RAG 增强问答")
    st.caption("每条问题先查 LightRAG 知识库，再由 DeepSeek 基于检索证据回答（无证据时明说）。")

    # guard: index must exist
    index_dir = PROJECT_ROOT / "data" / "processed" / "lightrag_index"
    if not index_dir.exists():
        st.error("🚫 LightRAG 索引未构建。请先执行 Executor Phase 4：")
        st.code("python <skill>/scripts/phase4_build_index.py --project-root .", language="bash")
        return

    fresh_status, _ = index_freshness()
    if fresh_status == "stale_rules_changed":
        st.warning("⚠️ 索引相对当前 rules.yaml 已 stale，回答可能基于旧规则。建议重跑 phase4 重建。")

    # sidebar-ish controls inline (chat tab keeps its own controls)
    ctrl_cols = st.columns([1, 1, 2])
    with ctrl_cols[0]:
        show_evidence = st.toggle("显示检索证据原文", value=True, key="chat_show_ev")
    with ctrl_cols[1]:
        if st.button("🧹 清空对话", use_container_width=True):
            st.session_state["chat_messages"] = []
            st.rerun()

    adapter = get_lightrag_adapter()
    llm = get_chat_llm()
    if adapter is None or llm is None:
        st.error("LightRAG 或 DeepSeek 客户端初始化失败，请检查 .env（DEEPSEEK_API_KEY / ARK_DOUBAO_API_KEY）。")
        return

    if getattr(llm, "degraded", False):
        st.warning("⚠️ DeepSeek 无可用 API key，将使用 stub 模式（仅模板回复）。请配置 .env。")

    # init history
    st.session_state.setdefault("chat_messages", [])

    # render history
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and show_evidence and msg.get("evidence"):
                with st.expander(f"📚 检索证据（{len(msg['evidence'])} 段）"):
                    for i, ev in enumerate(msg["evidence"], 1):
                        st.caption(f"片段 {i}")
                        st.write(ev[:600] + ("..." if len(ev) > 600 else ""))

    # input
    question = st.chat_input("向 agent 提问…（例如：PM2.5 对 GOLD III 期 COPD 患者的主要危害机制是什么？）")
    if not question:
        return

    st.session_state["chat_messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # 1) retrieve
    with st.chat_message("assistant"):
        with st.spinner("检索 LightRAG 知识库…"):
            try:
                import asyncio
                retrieved_text = asyncio.run(adapter.query(question, mode="hybrid"))
            except Exception as e:
                st.error(f"LightRAG 检索失败: {e}")
                return
        retrieved_text = retrieved_text or ""
        # split into pseudo-chunks for display (LightRAG returns concatenated text)
        evidence_chunks = [c.strip() for c in retrieved_text.split("\n\n") if c.strip()][:8]

        if not retrieved_text.strip():
            answer = "知识库中未检索到与该问题相关的证据，无法回答。请尝试更具体的关键词。"
        elif getattr(llm, "degraded", False):
            # 离线模式（无 API key）：直接以检索到的证据作为回答，审稿人无需配置 key 即可体验
            answer = (
                "（离线演示模式：未配置 DeepSeek API key，以下为知识库检索到的相关证据。"
                "配置 .env 的 DEEPSEEK_API_KEY 后启用完整 AI 回答。）\n\n"
                + "\n\n".join(evidence_chunks[:4])
            )
        else:
            # 2) DeepSeek answer grounded in evidence
            with st.spinner("DeepSeek 基于证据生成回答…"):
                system = (
                    "你是基于知识库的医学问答助手。**只能**基于下面给出的证据片段回答用户问题。"
                    "如果证据不足以回答，明确说「证据不足」，不要编造。"
                    "回答用中文，分点陈述，并在每条结论后标注 [证据N]。"
                )
                prompt = f"【证据片段】\n{retrieved_text[:6000]}\n\n【用户问题】\n{question}"
                try:
                    resp = llm.complete(prompt=prompt, system=system)
                    answer = resp.text
                except Exception as e:
                    answer = f"DeepSeek 调用失败: {e}"

        st.write(answer)
        if show_evidence and evidence_chunks:
            with st.expander(f"📚 检索证据（{len(evidence_chunks)} 段）"):
                for i, ev in enumerate(evidence_chunks, 1):
                    st.caption(f"片段 {i}")
                    st.write(ev[:600] + ("..." if len(ev) > 600 else ""))

    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": answer, "evidence": evidence_chunks}
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — 风险评估 / Screening (original A×B pick → report)
# ─────────────────────────────────────────────────────────────────────────────
def screening_tab(use_real_llm: bool, use_lightrag: bool, top_k: int) -> None:
    st.header("🔍 风险评估")

    # ─── 演示案例快捷填充 ───
    try:
        _demo_cases = json.loads((PROJECT_ROOT / "outputs" / "demo" / "demo_cases_curated.json").read_text(encoding="utf-8"))
        _a_reg = load_a_registry()
        _b_reg = load_b_registry()
        _a_opts = {f"{aid}: {v['name']}": aid for aid, v in _a_reg.items()}
        _b_opts = {f"{bid}: {v['name']}": bid for bid, v in _b_reg.items()}
        with st.expander("🎯 演示案例一键填充（自动填入下方选择框）", expanded=False):
            _demo_names = [f"{c['ophthalmic']} × {c['systemic']}（{c['risk']}）" for c in _demo_cases]
            _pick = st.selectbox("选择演示案例", ["— 手动选择 —"] + _demo_names, key="screen_demo_pick")
            if _pick != "— 手动选择 —":
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
                st.caption(f"✅ 已填充：{_a_name} × {_b_name}，点击「🚀 开始评估」")
    except Exception as _e:
        st.caption(f"（演示案例加载失败：{_e}）")

    # ─── Input selection ───
    st.subheader("选择待评估的组合")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**👩 眼科局部用药**")
        try:
            a_reg = load_a_registry()
            a_options = {f"{aid}: {v['name']}": aid for aid, v in a_reg.items()}
            a_label = st.selectbox("选择 眼科局部用药", options=list(a_options.keys()),
                                   label_visibility="collapsed",
                                   key="screen_a")
            a_id = a_options[a_label]
        except Exception as e:
            st.error(f"加载失败: {e}")
            return

    with col_b:
        st.markdown("**🌍 全身系统用药**")
        try:
            b_reg = load_b_registry()
            b_options = {f"{bid}: {v['name']}": bid for bid, v in b_reg.items()}
            search = st.text_input("搜索", "", help="输入关键词筛选", label_visibility="collapsed",
                                    placeholder="🔍 输入关键词筛选...", key="screen_b_search")
            filtered = [k for k in b_options if search.lower() in k.lower()] if search else list(b_options)
            if not filtered:
                st.warning("无匹配，显示全部")
                filtered = list(b_options)
            b_label = st.selectbox("选择 全身系统用药", options=filtered,
                                   label_visibility="collapsed", key="screen_b")
            b_id = b_options[b_label]
        except Exception as e:
            st.error(f"加载失败: {e}")
            return

    # Patient factors
    with st.expander("🏥 患者因素（可选，影响规则触发）", expanded=False):
        pf_options = ["elderly", "renal_impairment", "polypharmacy"]
        patient_factors = st.multiselect("适用的患者因素", pf_options, default=[], key="screen_pf")

    # Run button
    if not st.button("🚀 开始评估", type="primary", use_container_width=True, key="screen_run"):
        return

    with st.spinner("运行规则引擎流水线中…"):
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
            st.error(f"评估失败: {err_type}: {err_msg}")
            return

    risk = report.risk_assessment.risk_level.value
    confidence = float(report.risk_assessment.confidence_score or 0)
    n_signals = len(report.risk_assessment.signals)
    n_evidence = len(report.evidence)
    llm_label = report.metadata.get("llm_label", "rule-engine")

    # ─── Hero ───
    st.divider()
    render_risk_hero(risk, confidence, n_signals, n_evidence, elapsed, llm_label)

    # ─── Quick stats row ───
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_stat_card("触发规则", str(n_signals), RISK_COLORS.get(risk, RISK_COLORS["unknown"])["bg"])
    with col2:
        render_stat_card("证据片段", str(n_evidence), "#5B8FF9")
    with col3:
        render_stat_card("置信度", f"{confidence:.0%}", "#5AD8A6")
    with col4:
        render_stat_card("耗时", f"{elapsed:.1f}s", "#6b7280")

    st.divider()

    # ─── Sub-tabs ───
    tab_summary, tab_rules, tab_evidence, tab_technical = st.tabs([
        "📋 摘要", "⚙️ 规则详情", "📚 证据链", "🔧 技术细节"
    ])

    with tab_summary:
        st.subheader("📄 完整报告")
        st.code(report.report_text, language="markdown")

        if report.risk_assessment.signals:
            st.subheader("🎯 主要风险信号（按严重度）")
            sorted_signals = sorted(
                report.risk_assessment.signals,
                key=lambda s: {"high": 0, "medium": 1, "low": 2, "unknown": 3}.get(s.risk_level.value, 4)
            )
            for sig in sorted_signals[:3]:  # top 3 only in summary
                sev = sig.risk_level.value
                render_rule_chip(sig.rule_id, sev, sig.risk_type.split("_")[-1] if sig.risk_type else "")

    with tab_rules:
        if not report.risk_assessment.signals:
            st.info("✅ 未触发任何规则")
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
                st.write(f"**依据**: {sig.rationale}")
                if sig.recommendation:
                    st.write(f"**建议**: {sig.recommendation}")
                if sig.matched_terms:
                    with st.expander("匹配的标签"):
                        for k, v in sig.matched_terms.items():
                            if v:
                                st.write(f"- **{k}**: {', '.join(v)}")
                st.divider()

    with tab_evidence:
        if not report.evidence:
            st.info("📚 未检索到证据")
        else:
            # Filter by level
            levels_present = sorted({ev.evidence_level for ev in report.evidence})
            selected_levels = st.multiselect(
                "筛选证据等级",
                options=["A", "B", "C", "D", "E"],
                default=levels_present,
                help="A=监管标签, B=Meta, C=原创研究, D=体外/动物, E=机制推断",
                key="screen_ev_filter",
            )
            for ev in report.evidence:
                if ev.evidence_level not in selected_levels:
                    continue
                render_evidence_card(ev.evidence_level, ev.title[:80], ev.source, ev.text)

    with tab_technical:
        st.subheader("🔧 元数据")
        meta_cols = st.columns(3)
        with meta_cols[0]:
            st.metric("case_id", report.case_id)
            st.metric("entity_a_id", report.metadata.get("entity_a_id"))
            st.metric("entity_b_id", report.metadata.get("entity_b_id"))
        with meta_cols[1]:
            st.metric("LLM 角色", report.metadata.get("llm_role"))
            st.metric("LLM 模型", report.metadata.get("llm_label"))
            st.metric("Context 字符数", report.context_char_count)
        with meta_cols[2]:
            st.metric("规则信号数", report.metadata.get("n_signals"))
            st.metric("证据片段数", report.metadata.get("n_evidence"))
            st.metric("耗时 (s)", f"{elapsed:.2f}")

        with st.expander("完整 metadata JSON"):
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
    st.title("🧬 眼科药物相互作用知识库与临床决策支持系统")
    st.caption("眼科局部用药 × 全身系统用药 · 三层混合架构（规则 + KG + LLM 仲裁）")

    # ─── Sidebar (applies to Screening tab; Chat has its own inline controls) ───
    with st.sidebar:
        st.header("⚙️ 配置（风险评估 tab）")
        use_real_llm = st.toggle("使用真实 LLM (DeepSeek + GPT-4)", value=True,
                                  help="关闭则用 stub LLM（仅规则引擎）")
        use_lightrag = st.toggle("使用 LightRAG 检索", value=True,
                                  help="关闭则用 EvidenceStore 关键词检索")
        top_k = st.slider("Top-K 证据片段", min_value=1, max_value=15, value=5)

        st.divider()
        st.subheader("📊 注册表状态")
        try:
            a_reg = load_a_registry()
            b_reg = load_b_registry()
            st.metric("眼科局部用药", len(a_reg))
            st.metric("全身系统用药", len(b_reg))
        except Exception as e:
            st.error(f"注册表加载失败: {e}")

        if st.button("🔄 清空缓存", use_container_width=True):
            st.cache_resource.clear()
            st.success("缓存已清空")

    # ─── 3 top-level tabs ───
    tab_overview, tab_chat, tab_screening = st.tabs([
        "📊 项目介绍", "💬 RAG 问答", "🔍 风险评估"
    ])

    with tab_overview:
        overview_tab()

    with tab_chat:
        chat_tab()

    with tab_screening:
        screening_tab(use_real_llm, use_lightrag, top_k)


if __name__ == "__main__":
    main()
