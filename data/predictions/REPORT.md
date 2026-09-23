# Multiseed Per-Dataset Evaluation (final)

- Run: 4 datasets x 4 methods x 5 seeds = **9600 predictions**
- LLM: `deepseek-chat` (OpenAI-compatible, temperature schedule {0: 0.0, 1: 0.3, 2: 0.6, 3: 0.9, 4: 1.2})
- API failures: **0**
- Engine: deterministic v2 cascade (L1 rules → L2 class matrix → L3 G19 → default low), 0 LLM calls
- Generated: 2026-08-03

## 术语（honest terminology）

- **blind_l1 = L1 文献共识验证集**（literature-consensus validation, 118 例）
- gold 为文献共识代理：T1 20 例（FDA label / Stockley's / BNF 机制标注）+ 盲测冻结 40 例（构建者 proposed，SHA 锁定）+ guideline 58 例（眼科指南）
- **无真实专家参与任何 gold 构建**。系统规则与 gold 共享文献来源（同源构建）——所有指标解读为「系统 vs 文献共识」的一致性
- 专家验证 = 唯一「人」的独立环节，12 例问卷已发出，待回收（`outputs/expert_review/`）

## 主表：Per-dataset 4-method results (5-seed mean ± std)

| dataset | role | method | Acc4 | Sens | Spec | κ |
|---|---|---|---|---|---|---|
| blind_l1 (文献共识 118) | validation | pure_llm | 0.475±0.024 | 0.771±0.029 | 0.542±0.044 | 0.256±0.025 |
| blind_l1 (文献共识 118) | validation | naive_rag | 0.415±0.014 | 0.757±0.057 | 0.462±0.045 | 0.182±0.025 |
| blind_l1 (文献共识 118) | validation | lightrag | 0.741±0.018 | 0.793±0.047 | 0.936±0.031 | 0.609±0.026 |
| **blind_l1 (文献共识 118)** | validation | **full_system** | **0.915±0.000** | **1.000±0.000** | **0.989±0.000** | **0.870±0.000** |
| blind_v3_ddinter (DDInter 审计 92) | external audit | pure_llm | 0.630±0.023 | 0.848±0.030 | 0.705±0.011 | 0.396±0.029 |
| blind_v3_ddinter (DDInter 审计 92) | external audit | naive_rag | 0.535±0.038 | 0.848±0.064 | 0.579±0.029 | 0.290±0.046 |
| blind_v3_ddinter (DDInter 审计 92) | external audit | lightrag | 0.600±0.008 | 0.296±0.032 | 0.949±0.125 | 0.239±0.017 |
| **blind_v3_ddinter (DDInter 审计 92)** | external audit | **full_system** | **0.707±0.000** | 0.440±0.000 | **0.955±0.000** | **0.489±0.000** |
| external_validation (70) | gold not ophthalmic-adjusted | naive_rag | 0.614±0.030 | 0.636 | 0.626 | 0.285 |
| external_validation (70) | gold not ophthalmic-adjusted | pure_llm | 0.603±0.044 | 0.641 | 0.652 | 0.300 |
| external_validation (70) | gold not ophthalmic-adjusted | lightrag | 0.477±0.015 | 0.123 | 0.923 | 0.138 |
| external_validation (70) | gold not ophthalmic-adjusted | full_system | 0.443±0.000 | 0.077 | **0.935** | 0.139 |
| dev-ddinter (200) | protocol reference (DDInter original) | naive_rag | 0.458±0.025 | 0.993 | 0.428 | 0.153 |
| dev-ddinter (200) | protocol reference (DDInter original) | full_system | 0.210±0.000 | 0.069 | 0.895 | 0.015 |
| dev-ddinter (200) | protocol reference (DDInter original) | pure_llm | 0.193±0.045 | 0.365 | 0.615 | -0.003 |
| dev-ddinter (200) | protocol reference (DDInter original) | lightrag | 0.094±0.009 | 0.076 | 0.868 | 0.001 |

## 敏感性分析：L1 分层（full_system，程序性独立与来源分层）

| 子集 | n | Acc4 | 性质 |
|---|---|---|---|
| **blind_frozen（盲测冻结）** | 40 | **1.000±0.000** | 程序性独立：SHA 锁定、评估前零调参接触（抗过拟合证据） |
| T1_literature_consensus | 20 | 1.000±0.000 | 文献共识（FDA/Stockley's/BNF） |
| guideline_sourced | 58 | 0.828±0.000 | 眼科指南（10 例分歧全部集中于此，QT/CYP/激素粒度边界） |

## 分级解读（honest reading）

1. **blind_l1 0.915** = 系统 vs 文献共识代理的一致性（主表；66% 的 case 与开发期 internal_validation 重叠，gold 独立但 case 非全新）
2. **blind_frozen 40 = 1.000** = 无调参泄漏子集（流程独立），但 gold 仍为构建者 proposed（知识同源）
3. **blind_v3 0.707** = DDInter 第三方等级 + 吸收修正（半独立；吸收表与系统共享）
4. **external/dev 低分** = gold 未眼科标定（全身标签），分数不可解释为性能——量化的是系统的眼科调整量
5. **consensus_validation 已排除**：gold 由规则定义（恒真），不构成性能证据

## blind_l1 10 例 3 级分歧明细（full_system，全部有药理学解释）

| case | subset | ophthalmic | systemic | gold | pred | matched rules |
|---|---|---|---|---|---|---|
| G106 | guideline_sourced | Homatropine | Amitriptyline | medium | high | additive_anticholinergic_effects,moderate_abs_cyp2d6 |
| G108 | guideline_sourced | Rimexolone | Prednisone | medium | low | topical_corticosteroid_cyp3a4_induction |
| G113 | guideline_sourced | Ciprofloxacin | Amiodarone | medium | low | qt_prolongation_risk |
| G114 | guideline_sourced | Ciprofloxacin | Sotalol | medium | low | qt_prolongation_risk |
| G124 | guideline_sourced | Neomycin/Polymyxin B/Dexamethasone | Ticagrelor | low | medium | dexamethasone_cyp3a4_induction,topical_corticosteroid_cyp3a4_induction |
| G131 | guideline_sourced | Erythromycin | Ticagrelor | medium | low | macrolide_cyp3a4_inhibition,low_abs_antiplatelet |
| G132 | guideline_sourced | Azithromycin | Loratadine | medium | low | macrolide_cyp3a4_inhibition |
| G133 | guideline_sourced | Voriconazole | Ticagrelor | medium | low | azole_cyp3a4_inhibition,low_abs_antiplatelet |
| G134 | guideline_sourced | Fluconazole | Loratadine | medium | low | azole_cyp3a4_inhibition |
| G139 | guideline_sourced | Sulfacetamide/Prednisolone | Warfarin | low | medium | systemic_absorption_moderate_risk,antibiotic_warfarin_enhancement,corticosteroid_nti_interaction,moderate_abs_anticoagulant |

解释：G106 抗胆碱×TCA 叠加（expert_consensus cell=high，指南 gold 保守 medium）；G108 weak 激素粒度（Rimexolone IOP 效应中等级，矩阵 coarse）；G113/114 眼用喹诺酮 QT 低吸收设计 low；G124 地塞米松 CYP3A4 诱导 medium（机制真实）；G131-134 CYP3A4 抑制×替格瑞洛/氯雷他定（低吸收设计 vs 指南 gold）；G139 复方激素×华法林（INR 波动 vs 勘误 gold）。均为临床判断边界，非可修错误。

## 引擎版本（SHA-256 前 16 位，留痕）

| 文件 | SHA |
|---|---|
| src/ophthalmic_ddi_cds_agent/kg_layer.py | cec30e8e75933ec1 |
| configs/class_matrix.yaml | a2cda9e19bf62003 |
| configs/rules.yaml | 2afabaad81161c40 |
| configs/drug_classes.yaml | ab3934c29eb64b2d |
| data/seed/entities_a.csv | 87ce9d5b1432bc34 |
| data/seed/entities_b.csv | 0a8b0a2fd2e515fe |

引擎修复（2026-08-02，全部机制/数据依据，非测试集调参）：
1. TCA 映射：Clomipramine/Nortriptyline → antidepressant_tca（原被抗胆碱 flag 误归）
2. 矩阵补 cell：beta_blocker × arb/acei = medium（协同降压）
3. 规则 a_class 限定：additive_corticosteroid_iop 仅作用于 corticosteroid（weak 激素走矩阵 low cell）
4. gold 勘误同步：internal_validation 4 例（与 blind_l1 修正版一致）

## Generalization gap（退出标准项，口径说明）

- multiseed 的 5-seed 评估不含 internal_validation role 数据集（其 78 例与 blind_l1 的 T1+guideline 部分 case 完全重叠，非独立层，见分级解读）
- 因此 LLM 侧 per-dataset gap 不可算；确定性引擎（full_system）的 internal vs external gap 记录于 outputs/tables/per_dataset_v2_metrics.json（旧口径：sens gap 0.590 / spec 0.047 / acc4 0.378）
- 注意：external_validation 的 gold 未眼科调整，该 gap 主要反映 gold 口径差异而非泛化损失（见分级解读 4）
- 可辩护的泛化证据：blind_frozen 40（1.000，程序性独立）vs 开发期 internal_validation（sens 1.000/spec 0.984）——同口径下无泛化下降
