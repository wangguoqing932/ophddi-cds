# OphDDI-CDS 修订终审报告：审稿人意见、修订差异、自查问题与参考文献核验

**审计日期：** 2026-11-13
**审计对象：** `outputs/paper/manuscript.en.md`（340 行）、`outputs/deliverables/frontiers/Supplementary_Material.md`（1,256 行）、`outputs/submission/response_to_reviewers_r1.md`（166 行）、`outputs/submission/response_to_reviewers_r2.md`（115 行）
**四路输入：** R1 审计（10 条）、R2 审计（7 条）、DIFF（30 项差异）、NEW（12 条自查问题）、REFS（45 条参考文献，分三组核验）

**本轮实际执行的检查（仅列真正运行过的）：**

1. `python -m pytest tests/test_assessment_status.py -q` → `4 passed in 0.30s`。
2. `python scripts/audit_manuscript.py` → `0 个 FAIL, 2 个 WARN`（WARN 为 3.1/3.6/3.7/3.9 未被交叉引用、摘要 346 词距上限 350 仅 4 词）。
3. `sha256sum -c MANIFEST.sha256` → 4 条 OK、7 条 FAILED、7 条列出的文件缺失（详见 §4.2）。
4. `git diff --stat HEAD -- outputs/paper/manuscript.en.md` → `1 file changed, 148 insertions(+), 104 deletions(-)`；`git show HEAD:... | wc -l` = 296，当前 = 340。
5. `grep -c '^\[[0-9]'` → 当前 45 条，HEAD 42 条。
6. `pdftotext -layout outputs/deliverables/manuscript.pdf - | grep '333'` → PDF 仍保留 `Found Trends Inf Retr. 3, 333–389`（详见 §4.2）。
7. 逐段读取手稿、补充材料、两封回复信、Table 3/4/5/6/7、`outputs/audits/response_addendum_proposed.md`、`outputs/audits/reference_verification_table.md`，并抽查 `kg_layer.py`、`safety_agent.py`、`schemas.py`、`streamlit_app.py`、`build_r2_tables.py`。

**未执行：** 完整 `pytest` 套件、LLM 基线重跑、Lexicomp 重新查询、45 个 DOI 的重新联网核验（参考文献结论依据 REFS 三组已完成的 Crossref/Europe PMC/doi.org/Zotero 核验）。

**Post-audit update (2026-11-13, after this report was generated).** The substantive gaps below were corrected and re-checked: (i) `assessment_status` now propagates through `SafetyAgent` into `RiskAssessment`, and the Streamlit interface shows an UNASSESSED warning and no longer displays Confidence/Time; (ii) the R1/R2 response wording on the five unsupported downgrades and the 161 default-path downgrades now matches the manuscript; (iii) the matrix-source wording in §2.2, Text S10 and R2 was changed to "rule set, class extrapolation, expert consensus or pharmacological inference"; (iv) `build_r2_tables.py` now regenerates the correct Table 7 Lexicomp note; (v) the Table 3 note was synced, the duplicate Sacchi author was removed, [37] was restored to 3:333–389 (Crossref's 4:1–174 is a collision with 10.1561/1500000013), and MANIFEST was rebuilt with 20 entries; (vi) 45/45 DOIs are present in Zotero and 44/44 non-arXiv DOIs are Crossref-verified, with the arXiv DOI via DataCite. Revised status: **15/17 complete, 2 partial (R1-5 independent adjudication not done; R2-6 Lexicomp 2018 edition), 0 missing**. The residual limitations remain disclosed in the manuscript.

**Post-audit update (2026-11-14).** R1-5 is complete: one non-author ophthalmologist reclassified the 30 blinded cases; agreement with the author classification was 14/30 (14/28 within the three author classes, kappa 0.271), with 14 author route-consistent cases reclassified as unsupported. R2-6 was closed by the author on 2026-11-13 with the 2018 UpToDate/OpenMed comparison. All 17 reviewer items are addressed; the remaining limitations are L1 (no development-free/independently adjudicated test set), L3 (non-blinded 12-case expert exercise) and L6 (no outcome data), all disclosed.

---

## 一、结论摘要

### 1.1 总体判断

本次修订是实质性重写，不是文字润色：手稿 296→340 行（`+148/−104`），参考文献 42→45，补充材料由 Texts S1–S7/S9 + Tables S1–S8 扩为 S1–S10 + S1–S19，并新增 §3.9、§4.3、Table 6/7、Figure 6。修订主线有四条：①对照标准从 `gold/accuracy/0.907` 降为 `author-derived reference set/exact agreement/0.856（冻结标签）`，校正标签 0.881 降为敏感性分析；②工程行为改变：新增 unassessed 状态、对 `nsaid_antihypertensive_antagonism` 实施吸收门控、13 处 tier 不一致全部解决（分层计数 15/17/61/9/7/4 → 12/20/59/11/7/4）；③新增路径归因、仅局部制剂复算、审计 30 例分歧的 21/5/4 分类、RA-DDInter 与 Lexicomp（2018 版）对照、gated vs ungated 敏感性；④披露扩张与主张收窄：伦理措辞由 "no human participants" 改为 "no patients" 并明确 "no formal determination was issued"，删除 PPV 6.7%、"0.992"、curation-file 敏感性 75.27%/75.69% 等旧表述。

但 17 条审稿意见中 **12 条完成、5 条部分完成、0 条未完成**。"完成"只表示修订稿对该意见给出了可核对的回应，不等于审稿人的核心科学要求全部满足。最重要的残余是：

1. **仍无独立裁决、无开发暴露的测试集**。R1-1 的核心要求无法在本次完成，稿件 `:102`、`:188` 已明确披露（"No independently adjudicated or development-free test set exists"），这是诚实的 residual gap，不应在回复信里被写成已解决。
2. **unassessed 状态没有进入生产路径**（R1-3）。`kg_layer.deterministic_level_v2()` 返回了 `assessment_status`（`src/ophthalmic_ddi_cds_agent/kg_layer.py:250-253`），但 `SafetyAgent.assess()` 用 `v2_level,_,_` 丢弃了 info（`src/ophthalmic_ddi_cds_agent/safety_agent.py:24`），`RiskAssessment` schema 无该字段（`src/ophthalmic_ddi_cds_agent/schemas.py:155-160`），Streamlit 只渲染 `report.risk_assessment.risk_level`（`app/streamlit_app.py:735`）。因此界面仍把这类对显示为 low；手稿 `:79` 的 "are returned as low with `assessment_status = unassessed`" 对 app 不成立，`:192` 也把 "expose the unassessed status in the interface" 列为 future work。
3. **回复信在若干处比当前稿件更旧、更强或更错**：R1 回复 `:86` 仍称五个 unsupported 是 "the clinically critical subset"（稿件 `:116` 明确说不是）；R2 回复 `:73` 仍称五个都是 "high-tier agents"（实为 3 个 DDInter-high + 2 个 DDInter-medium）；R2 回复 `:105` 称 "No new references were required"（但新增了 Lexicomp 对照）；R1 回复 `:32` 对 B-only 只给结论半句，未给证据链。
4. **R2-1 的 "83 cells were created when at least one source supported" 与 S14 不一致**：按 S14 逐行统计，83 个 actionable 格中 18 个是 rule、32 个是 class extrapolation、18 个是 consensus、15 个是 pharmacology；其中 33 个并非外部来源支持，回复信重复了夸大表述。
5. **R2-6 的 Lexicomp 对照不可由回复信点名的脚本复现**：`scripts/build_r2_tables.py:92-94` 重新生成的 Table 7 仍写 "Licensed route-aware databases (Lexicomp, Micromedex, Stockley's) were not available for systematic comparison"，与 §3.9 和提交版 Table 7 直接矛盾。

### 1.2 R1 / R2 完成情况

| 审稿人 | 条数 | 完成 | 部分完成 | 未完成 | 主要残余 |
|---|---:|---:|---:|---:|---|
| R1 | 10 | 8 | 2（R1-3、R1-5） | 0 | unassessed 未进生产界面；五个 unsupported 被误称为全部临床关键集；无独立裁决测试集（已披露） |
| R2 | 7 | 4 | 3（R2-1、R2-5、R2-6） | 0 | 矩阵来源支持表述夸大；77.7% 的归因与 default path 未区分；Lexicomp 对照的复现脚本与提交表矛盾 |
| **合计** | **17** | **12** | **5** | **0** | — |

### 1.3 新问题与参考文献

- **自查新问题：** NEW 列出 12 条；其中仅 2 条部分披露（B01–B20 非 development-free、80.3% 用 "involved" 表述），10 条未披露。另有本轮汇总另行核实的 3 条（Table 3 注与正文矛盾、[37] 卷页被改错、MANIFEST 14/18 不通过），均未披露。
- **参考文献：** 45/45 DOI 可解析（doi.org 302）、45/45 Zotero 命中；#17 的重复 Sacchi 作者已删除，#37 的源稿已回退为 `3, 333–389`，因此 45 条均可按最终源稿核对。另有 1 条元数据需注意：#35 BNF 年份 2026 无法独立核验；#37 的 Crossref `4(1–2):1–174` 是出版方元数据撞号（与 10.1561/1500000013 同卷同页），最终采用 `3, 333–389`。

---

## 二、审稿人逐条完成情况表（17 行）

状态定义：**已完成** = 修订稿对该条的主要要求有可核对落实；**部分完成** = 有实质回应但仍有未满足的核心要素或回复信与稿件不一致；**未完成** = 无对应修订。下表每条均给稿件/补充材料/代码证据。

| 编号 | 状态 | 稿件证据 | 剩余 gap / 备注 |
|---|---|---|---|
| **R1-1** 参考标准独立性 | 已完成 | `manuscript.en.md:96-102`（0.856/101、0.881/104、36/40、B 18/20→20/20、C 18/20→19/20、45/58、40/47、5/11、56/60）；`:61`（31 July 三处修正；B/C 均非 development-free）；Table 3；`Supplementary_Material.md:190-235`（S1 17 条）；`:188`（No independently adjudicated test set） | 核心要求"独立裁决、无开发暴露的测试集"仍不存在（`:102`、`:188` 已披露）；回复信在 20/20 corrected 处未重复手稿 `:61` 的 "partly tautological" 限定。 |
| **R1-2** 吸收层级证据 | 已完成 | `manuscript.en.md:51`（六档定义、13 measured/11 label/89 class-inferred、13 处已解决）；`Supplementary_Material.md:301-419`（S5 113 行）、`:421-450`（S5b 24+conbercept，含制剂/剂量/暴露/来源）、`:719-762`（S10 A 13 行、B 12 个复方、C certainty 13/11/89）；`data/curation/absorption_tier_evidence.csv` | 13 个 measured 行的暴露指标不统一（timolol 为相对 IV 的生物利用度、atropine/aceclidine 为 Cmax、dorzolamide/brinzolamide 为低于定量限、dexamethasone 为 <1 ng/mL），未换算到同一"相对口服暴露"尺度；S10 仅对 dexamethasone 明说 "conservative ordinal placement"，其余 measured 行未逐行标不确定。 |
| **R1-3** 低风险保障 | **部分完成** | `kg_layer.py:250-253`（default_low + assessment_status=unassessed + note）；`tests/test_assessment_status.py`（本轮运行 4 passed）；`manuscript.en.md:108`（176/1,933，504/507/746/176，1,341/1,757）；`Supplementary_Material.md:764-974`（S11 B/C，176 行全列）；`manuscript.en.md:162`、`:79`、`:178`；`Supplementary_Material.md:1248-1256`（S19）；`safety_agent.py:24`；`schemas.py:155-160`；`app/streamlit_app.py:735` | `assessment_status` 只存在于 `kg_layer` 返回 tuple；生产路径 `SafetyAgent.assess` 丢弃 info，`RiskAssessment` 无字段，app 只渲染 `risk_level`，界面仍把这类对显示为 low。回复信 "We implemented the distinction in the engine, not only in the text" 只对 kg_layer 成立，未说明 service/app 丢弃该字段。 |
| **R1-4** 给药途径限定 | 已完成 | `manuscript.en.md:110`（1,930 对，1,499/77.7%，350 from high）；`Supplementary_Material.md:975-982`（S12：1,930/1,499/0.777/350/1,203/0.803；9 个非局部药仅 3 对，均 aflibercept）；`:421-450`（S5b 6 个抗 VEGF 逐个列制剂/分子量/暴露）；`:739-752`（S10B 12 个复方按组分）；`manuscript.en.md:51` | 摘要 `:15` 与结论 `:196` 仍以 1,933 为主分母，1,930 只是 `:110` 的限定分析；回复信 "The principal analysis is now repeated on the 104 topical agents" 措辞略强于手稿的实际呈现（差异仅 3 对，结论不变，且已披露）。 |
| **R1-5** 外部审计与安全分析 | **部分完成** | `manuscript.en.md:114-116`（62/92 0.674、61/92 0.663、8/25、8/29；21/5/4 分类）；Table 5；`Supplementary_Material.md:237-272`（S2 30 行含 tier/path/rules/direction；`:272` note 12 例 default path = 10 route-consistent + 2 unsupported） | 回复信 `:86` 称 "The five unsupported undergradings are the clinically critical subset"，但手稿 `:116` 与 S2 note（`:272`）明确说这 5 例"不是全部临床关键集"：另有 12 例在 unassessed default path，其中 D3-026、D3-029、D3-033、D3-080 四例 DDInter-high 的低分级 "not evidence of safety"；回复信漏掉这 4 例。审稿人要求的独立复核未做（作者分类，手稿 `:116` 已披露）。 |
| **R1-6** LLM 比较设计 | 已完成 | `manuscript.en.md:67`（rule_context 说明、接收规则层、prompt 限制）、`:69`（两配置同时改变模型/预算/采样）、`:124-128`（config 2 结果、26/92=19/62+7/30）；Table 3 末段 note；`Supplementary_Material.md:984-1015`（S13 全方法 66 例对照）；`scripts/draw_figure2.py:56`（lightrag→Rule-context） | 回复信未提 `:67` 与 Table 3 note 已披露的 prompt 混杂：共享 system prompt 仍写 dexamethasone >50%（tier 已改 medium），且 config-1 只重跑 rule_context、pure_llm/naive_rag 未重跑；手稿明说 "not a clean test of retrieval augmentation"，回复信未重复该限定。 |
| **R1-7** 数值纠正 | 已完成 | `manuscript.en.md:124`（2.2%、10.9%、6.5%、27.2%、7/6/15 of 28）；Table 3（Configuration 2, audit 行：0.080/0.400/0.240 → 2/25、10/25、6/25）；`outputs/recomputed/revision_r1_stats.json` 的 `R1_6_7_adequate_budget`（blind_v3_ddinter 2.2/10.9/6.5；blind_l1 tp_majority 7/6/15；naive_rag tp_range_per_rep [4,9]） | ungated "115 对（47 medium, 68 high）"与"95 high"未在 `revision_r1_stats.json` 或 `rule_gating_experiment.json` 中直接复算到；95 本身是审稿人原话；其余数字已复核。 |
| **R1-8** 收窄临床含义 | 已完成 | `manuscript.en.md:106`（difference in classification）、`:156`（perspective comparison）、`:172`（difference in classification produced by the exposure model, not evidence that alerts were inappropriate）、`:186`（No outcome data ... predictive value ... cannot be estimated）；本轮 `grep -in 'prevalence\|PPV\|positive predictive\|would reach a prescriber'` 无命中 | 回复信把 "difference in classification" 定位为 Sections 3.3 and 4.3，实际在 §3.4:106 与 §4.3:172（定位笔误，非内容夸大）。 |
| **R1-9** 临床医生练习描述 | 已完成 | `manuscript.en.md:75`（purposive panel、非盲、病例围绕系统输出构造）、`:136-140`（kappa 0.840；8/12（displayed）/6/12（frozen）更低；不能分离 perspective gap 与 case-selection；只支持"未复现 assigned grades"）、`:156`、`:192`（blinded reviewers including clinical pharmacy expertise）；本轮 `grep -in 'rarity\|recall\|rare events'` 无命中 | 无。 |
| **R1-10** 规则来源与可复现性 | 已完成 | `manuscript.en.md:43`（2/5/23/10；severity 2/28/10）；`Supplementary_Material.md:625-717`（S9 40 行）；`:11-33`（Text S2 四处引用修正）；`configs/rules.yaml:62-88`（digoxin 移除 Schuman 2000）、`:559-583`（warfarin 改 DB00682）、`:805-840`（low_abs 两条改 absorption prior）；`manuscript.en.md:212-214`、`:226-228`；`python scripts/audit_manuscript.py` → 0 FAIL, 2 WARN | 伦理依据仍是 "authors determined ... no submission was required, and no formal determination was issued"（`:212`），不是机构出具的豁免/审批；Zenodo DOI 10.5281/zenodo.23439606 解析到 zenodo.org（302），但记录内容因网络超时未能核验。 |
| **R2-1** 规则与矩阵构建 | **部分完成** | `manuscript.en.md:43`（候选来源、固定赋值顺序、研究团队+两位临床作者共识、无 Delphi/盲审/独立委员会）；`:45`（21×34、104 格、83 actionable+21 none）；`Supplementary_Material.md:611-625`（S10 构建协议）；S9 的 route-support 2/5/23/10；S14 104 行 | L45/S10 称 83 个 actionable 格均 "at least one source supported"，但按 S14 逐行统计：rule 18、class extrapolation 32、consensus 18、pharmacology 15、none 21（合计 104）；83 个 actionable 中有 33 个是 consensus/pharmacology，并非外部来源。S14 表末注（`Supplementary_Material.md:1126`）明确把 expert consensus/pharmacological inference 列为证据类型。回复信 `:31` 重复了该夸大表述。 |
| **R2-2** 分级定义与临床意义 | 已完成 | `manuscript.en.md:49`（四级操作性定义、临床意义、预期管理、示例）；Table 6（`outputs/deliverables/tables/table6_grade_definitions.md:1-8`，逐级列 operational definition/clinical significance/expected management/illustrative pair，第 8 行声明 grades are screening categories, not probabilities of harm）；`:55` 与 `:47` 的工作流处理 | 无。 |
| **R2-3** 患者因素 | 已完成 | `manuscript.en.md:53`（pair-level，因素不修饰 grade；三个 contextual policies 仅 advisory）；`Supplementary_Material.md:1128-1141`（S15 逐因素列 representation/effect/gap，覆盖 age、renal、hepatic、QT、dose+duration、CYP、instillation）；`configs/rules.yaml:850-898`（三个 policy 由 narrow_therapeutic_index/medium absorption flags 触发，无 eGFR/age/genotype 数值输入）；`manuscript.en.md:184`、`:192` | 无。 |
| **R2-4** A–E 分级定性 | 已完成 | `manuscript.en.md:35`（A-E 为 source tier/provenance，不是 strength of evidence，且不进入 grade）；`Supplementary_Material.md:1142-1153`（S16 逐级列 can/cannot support）；S1 `:8` 给出 A=53/B=191/C=215/D=584/E=264；S9 的 2/28/10 是 severity support 的另一维度 | 术语残留：S1 `:8` 仍写 "Evidence levels"、S9 `:629` 表头 "Evidence grade"，与 A–E source tier 的重新定性不完全一致（已在 R2 总评指出，属轻微问题）。 |
| **R2-5** 暴露降低≠风险降低 | **部分完成** | `manuscript.en.md:170-172` 与 `Supplementary_Material.md:1154-1165`（S17 按 reversible PD、NTI PK、threshold/idiosyncratic、cumulative、local 五类机制展开）；`:172` 明确 77.7% 是 classification difference；`:116` 给出 30 例分歧的 21/5/4 分类，并列出 4 个 DDInter-high default-path pairs（D3-026、D3-029、D3-033、D3-080） | 回复信 `:73` 称 77.7% 是 "the exposure model" 产生的分类差异，但 `:108`/`:172` 显示 1,502 个 downgrades 中有 161 个来自 unassessed default path（S11：176 default pairs = 151 medium + 10 high + 15 low），并非 exposure model 的判定；回复信 `:73` 只提 "five unsupported downgrades"，未提 §3.5 `:116` 明确补充的 4 个 DDInter-high default-path pairs。§4.3 `:172` "the low-tier downgrades are plausible..." 对 21 个 route-consistent downgrades（含 medium/minimal 及 4 个 DDInter-high）作了过度概括。 |
| **R2-6** route-aware 对照 | **部分完成** | `manuscript.en.md:144-150`（RA-DDInter 42 例：17/42、21/42、32/42；sensitivity 5/3/9 of 13；specificity 17/28/29 of 29；Table 7）；Lexicomp（S18b `:1215-1246`：C15/B1/X1/no interaction 25；exact 17/42、18/42；high-risk sensitivity 0/13、8/13；binary 16/32、10/10、26/42、κ0.323）；1,933 对比较 JSON：n=1933、agree=1489（0.7703）、higher=148、lower=296 | Lexicomp 为 2018 版，经第三方 IP 接口 `http://167.99.184.127/d/di.htm`（S18b `:1244`）访问，正文仅称 "OpenMed-provided interface"；未在参考文献中引用 Lexicomp/UpToDate（R2 回复 `:105` 称 "No new references were required"）；§3.9 的方法只一句，未说明 systemic entry 的 route 选择/查询者/盲法；摘要 `:15` 与结论 `:196` 仍只列 "three" perspectives，未报告新的 route-aware 比较；Discussion §4.2 未综合 Lexicomp/RA-DDInter 结果。更严重的是，R2 回复 `:111` 点名的 `scripts/build_r2_tables.py:92-94` 重新生成的 `outputs/tables/table7_route_aware.md:7` 仍写 "Licensed route-aware databases (Lexicomp, Micromedex, Stockley's) were not available for systematic comparison"，与 §3.9 和提交版 Table 7（`outputs/deliverables/tables/table7_route_aware.md:7`）直接矛盾；该脚本不能复现提交的 Table 7。 |
| **R2-7** 预期临床工作流 | 已完成 | `manuscript.en.md:55` 逐步描述 second-reader check、unknown-agent error、返回 grade/path/rule IDs/source/management；高→prescriber/pharmacist review，中→review+monitoring，低→usual care，unassessed→manual review；Figure 6；Table 6:3-6；`:55`/`:184` 声明 workflow 未在临床环境评估 | 无。 |

---

## 三、修改稿与原稿的主要差别

### 3.1 主题级差异

| 主题 | 原稿（HEAD） | 修订稿 | 证据 |
|---|---|---|---|
| 对照标准与术语 | 全文以 `gold` 与 `accuracy` 描述 118 例参考集，摘要写 "0.907 exact accuracy (kappa 0.857)"；§3.3 标题 "Agreement with the literature-derived gold" | 统一改为 `author-derived reference set` 与 `exact agreement`，正文明确 "we use 'exact agreement' rather than 'accuracy' throughout"；118 例主分析改为冻结标签 0.856 (101/118)、κ 0.779，校正标签降为敏感性分析 | `git show HEAD:...` L15、L90、L94 ↔ `manuscript.en.md:15`、`:94`、`:96-98` |
| 背景命题 | 摘要 "general-purpose DDI databases grade severity as though every drug were swallowed"；引言称 "General-purpose DDI databases, including DDInter, publish pair-level severity ratings derived predominantly from systemic administration [17,18]" | 摘要改为 "the DDInter export used here carries one severity grade per pair and no absorption field; route awareness is partial (Drugs.com, Lexicomp), but no registry-wide absorption model is applied"；引言改为 "The DDInter 2.0 export used here provides one pair-level severity per drug pair and no route or absorption field"，保留"错配规模未被测量"的缺口 | `HEAD` L15、L21 ↔ `manuscript.en.md:15`、`:21` |
| LLM 比较的因果框架 | §3.6 标题 "Reasoning-model baselines under an adequate output budget"；正文 "we repeated the three baselines under conditions that remove that constraint"、"artefact of the decision rule adopted with more room" | 标题改为 "Second configuration (different model, token allowance and sampling)"；明确 "It differs from configuration 1 in model, token allowance and sampling simultaneously; comparisons between them therefore describe two configurations"，删除全部 budget/reasoning 因果措辞 | `HEAD` L110、L112、L114 ↔ `manuscript.en.md:69`、`:120`、`:122`；`response_to_reviewers_r1.md:96` |
| 比较器改名与披露 | 比较器名为 `lightrag`，仅称其为 knowledge-graph context block | 改名 `rule_context`，注明 "method id lightrag in the deposited code, retained for continuity"；披露该基线接受匹配规则与严重度、低吸收对必须判 low 的指令，因此与级联的差距低估了纯检索的劣势；并披露配置 2 `rule_context` 使用修正前提示、共享 system prompt 仍写 dexamethasone >50% | `HEAD` L63、L65 ↔ `manuscript.en.md:67`、`:69`；`response_to_reviewers_r1.md:98`、`:100` |
| A–E 定性 | §2.1 "graded by evidence level: A regulatory label, B meta-analysis..."，未区分来源类型与证据强度 | 改为 `source tier`，写 "The tiers describe provenance, not strength of evidence - a label statement (A) can be less direct than a systematic review (B)... and they are not weights in the engine"；新增 S16 说明每层能与不能支撑什么 | `HEAD` L35 ↔ `manuscript.en.md:35`、`:206`；`response_to_reviewers_r2.md:59-63` |
| unassessed 状态 | §2.2 "Pairs reaching neither a rule nor a defined cell fall through to the default-low path"；同节又称 "out-of-coverage pairs are never assigned a grade by default"，两句互相矛盾 | default 路径返回 low 但带 `assessment_status = unassessed`，"the grade is retained for continuity but is not evidence of safety"；量化 176/1,933（9.1%），其中 151 DDInter-medium、10 DDInter-high、15 DDInter-low | `HEAD` L45、L47 ↔ `manuscript.en.md:47`、`:108`、`:178`；`response_to_reviewers_r1.md:56` |
| 暴露≠风险 | 无对应章节，仅在 Limitations 零散提及 | 新增 §4.3 "Exposure is not risk"，按可逆 PD、PK（受害者药物暴露分数变化）、阈值/特异质反应、累积毒性分别讨论，并明确 77.7% "is a difference in classification produced by the exposure model, not evidence that the downgraded pairs are safe" | `manuscript.en.md:168-172`（HEAD 无对应节，HEAD L146-150 为旧 Limitations）；`response_to_reviewers_r2.md:65-75` |
| 章节结构与新增内容 | §2.3 "Validation data"；§3.3 "Agreement with the literature-derived gold (118 cases)"；无 §3.9；Discussion 为 4.1/4.2/4.3 Limitations/4.4 Future directions | §2.3 改 "Reference and audit data"；§3.3 改 "Agreement with the author-derived reference set (118 cases)"；新增 §3.9 "Comparison with route-aware resources"；Discussion 扩为 4.1-4.5（新增 4.3 Exposure is not risk，Limitations 顺延 4.4，Future 4.5） | `HEAD` L53、L90、L128、L144、L152 ↔ `manuscript.en.md:59`、`:94`、`:142`、`:168`、`:174`、`:190` |
| §2.2 方法小节 | 仅 L1 rule engine、Citation coverage、L2 class matrix、L3 hard constraint、Absorption tiers 数段；规则构建、分级定义、患者因素、工作流均无独立小节 | 新增 "Rule construction, adjudication and provenance"、"L3 hard constraint and unassessed pairs"、"Grade definitions and expected management"、"Patient-specific factors"、"Intended workflow" 五个粗体小节；原 "Citation coverage is narrower than 'citation-verified' implies" 整段被替换为三问式规则溯源审计结果 | `HEAD` L41、L43、L45、L47、L49 ↔ `manuscript.en.md:43`、`:47`、`:49`、`:53`、`:55` |
| Limitations / Future | §4.3 三小节（Absorption-tier assignment / Bounded clinical impact / Validation）；§4.4 "Four directions follow" | §4.4 七小节（新增 Unassessed pairs and unmodelled inputs、Registry-scale denominator、Rule and matrix construction、Patient-level factors）；§4.5 "Six directions follow"，新增独立裁定、route-aware 对照、patient-level 模型 | `HEAD` L146、L148、L150、L154 ↔ `manuscript.en.md:176`、`:178`、`:180`、`:182`、`:184`、`:186`、`:188`、`:192` |
| 新增表/图 | 只有 Table 1-5 与 Figure 1-5；无分级定义表、无 route-aware 对照表、无工作流图 | 新增 Table 6（high/medium/low/unassessed 的操作定义、临床意义、预期处置、示例对）、Table 7（DDInter vs RA-DDInter vs 全级联，42 例）、Figure 6（Intended workflow and output contract） | `manuscript.en.md:49`、`:146`、`:55`、`:184`；`outputs/deliverables/tables/table6_grade_definitions.md:1-5`；`outputs/deliverables/tables/table7_route_aware.md:1-5`；`outputs/paper/figure_legends.md:23` |
| 补充材料 | Texts S1–S7/S9、Tables S1–S8 | Texts S1–S10、Tables S1–S19（含 S5b、S18b），新增 S8、S10 及 S9-S19 各表 | `HEAD` L168 ↔ `manuscript.en.md:206`；`Supplementary_Material.md:3`、`:607`、`:611`、`:623` |
| 伦理与同意 | "It involved no human participants"；"so neither ethical review nor informed consent was required"；"no submission to it was required"；未说明是否取得正式裁定 | 改为 "no patients, no patient-level data, no human tissue..."；明确 "the authors determined that no submission to it was required, and no formal determination was issued"；新增同意过程："consent beyond agreeing to take part was not required; the completed questionnaires were returned anonymously" | `HEAD` L174、L176 ↔ `manuscript.en.md:212`、`:214`、`:220`；`response_to_reviewers_r1.md:148` |
| 删除的旧表述 | ① 1% 患病率下 PPV≈6.7%；② "earlier versions scored higher on the same cases (0.992)"；③ curation-file 分层敏感性 75.27%→75.69%；④ 最大可达 κ 0.294/0.314 的辩护段；⑤ "would reach a prescriber at a different grade" | 五项全部删除；改为 "No outcome data are available, so predictive value for adverse events cannot be estimated" 与 "The 77.7% divergence is a property of the stated absorption model, not evidence that alerts were inappropriate or that prescribing would improve" | `HEAD` L98、L148、L150、L122 ↔ `manuscript.en.md:172`、`:186`、`:188`；`response_to_reviewers_r1.md:120`、`:128` |
| 新增的限制条目 | 未披露：Unknown 分母规模；规则/矩阵裁决方式；患者因素逐项缺口；基线比较的提示词混淆；20/20 的同义反复风险 | 新增：2,613/4,546 registry-matched 对为 Unknown 并排除；规则与矩阵为 study-team 共识、无 Delphi/盲审/独立委员会；S15 逐项列患者因素；披露共享提示词仍写 dexamethasone >50%、配置 1 rule_context 重跑而 pure_llm/naive_rag 未重跑；声明 B02/B12 校正使 20/20 "partly tautological"、"No development-free subset remains" | `manuscript.en.md:67`、`:69`、`:61`、`:180`、`:182`、`:188` |
| 数据可用性 | "all gold files with per-case provenance (data/gold/)"；"a per-agent absorption-tier table with a source column for each agent"；MANIFEST "LF line endings, so sha256sum -c works directly"；"No dataset is restricted" | 改为逐例溯源文件（`data/datasets/*/cases.jsonl`、`outputs/recomputed/l1_gold_provenance.csv`）、`revision_r1_stats.json`、`rule_provenance_audit.csv`、`absorption_tier_evidence.csv`、path-attribution 审计；MANIFEST 说明改为 "LF line endings and LF-normalized hashes; convert CRLF to LF before sha256sum -c"；新增 Lexicomp 仅存聚合结果的限制；"No author-generated dataset is restricted" | `HEAD` L186 ↔ `manuscript.en.md:224` |
| 参考文献 | 42 条（[1]-[42]）；DDInter 2.0 标 2024；BM25 标 "Found Trends Inf Retr. 3, 333–389"；5 条缺卷期或标题；Jumbe 标 "3rd ed. Boca Raton: CRC Press" | 45 条（[1]-[45]）：新增 Urtti 2006、Gaudana 2010、Salminen 1990 三篇眼部药代/全身吸收综述；DDInter 2.0 改 2025；BM25 保持 "3, 333–389"（Crossref 的 4:1–174 为撞号，见 §5）；5 条补全卷期/标题；Jumbe 改 "2nd ed. London: Routledge"；Prasad 补 "D. J."；全表因新增 3 条整体位移 | `HEAD` L214-296（`grep -c '^\[[0-9]'` = 42）↔ `manuscript.en.md:252-341`（45 条）；`response_to_reviewers_r1.md:156`、`response_to_reviewers_r2.md:105` |

### 3.2 关键数字：旧值 → 新值

| 指标 | 原稿 | 修订稿 |
|---|---|---|
| 1,933 对中降级比例 | 75.3%（1,455） | 77.7%（1,502）；新增评估子集口径 76.3%（1,341/1,757） |
| 降级中低吸收占比 | 80.5%（1,171/1,455），旧稿称 "attributable to" | 80.3%（1,206/1,502），"involved" + "composition statistic, not a causal decomposition" |
| 升级对数 / 两侧不一致比例 | 136（7.0%）/ 82.3% | 65（3.4%）/ 81.1% |
| 从 high 降级拆分 | 37→medium / 315→low；medium→low 1,103 | 34→medium / 318→low；medium→low 1,150 |
| 118 例一致率 | 0.907（107/118） | 冻结 0.856（101/118）；校正 0.881（104/118） |
| 118 例 κ | 0.857 | 冻结 0.779；校正 0.818 |
| 118 例高风险敏感性 | 0.964（27/28） | 冻结 0.857（24/28）；校正 0.893 |
| 118 例特异性 | 0.989 | 冻结 0.978；校正 0.989 |
| 40 例冻结盲集 | 39/40（0.975） | 36/40（0.900）；校正 39/40 |
| 子集分解 | 指南 48/58；规则保真 43/47；T1+盲 59/60；T1 20/20；人工 5/11 | 指南 45/58；规则保真 40/47；T1+盲 56/60；T1 20/20；人工 5/11 |
| LLM 基线区间 | 0.415–0.737（pure_llm 0.475、naive_rag 0.415、lightrag 0.737） | 0.419–0.714（pure_llm 0.478、naive_rag 0.419、rule_context 0.714） |
| 与最佳基线差距 | 0.170 | 0.142 |
| 基线高风险敏感性 | rule_context 0.779；pure_llm 0.771；naive_rag 0.757 | rule_context 0.593；pure_llm 0.779；naive_rag 0.764 |
| McNemar 不一致对 | 54:2 / 60:4 / 20:1 | 48:2 / 54:4 / 19:3（均 p<0.001） |
| 审计集重导标签 | 60/92（0.652）；敏感性 8/29；未校正 DDInter 0.370（34/92） | 61/92（0.663）；敏感性 8/29；未校正 0.380（35/92） |
| 审计集特异性 | 0.955 | 0.970（重导 0.968） |
| 与 rule_context 的 McNemar | 8:1，p=0.039（显著） | 10:3，p=0.092（不再显著） |
| 配置 2 级联敏感性 | 0.964 | 0.893（校正标签） |
| 配置 2 多数投票识别高参考例 | 27（共 28） | 7/6/15，级联 25（共 28） |
| 配置 1 rule_context | 0.737（未重跑） | 0.719（校正提示重跑）；敏感性 0.621 |
| 温度波动 | lightrag 0.712–0.771（SD 0.020）；pure_llm SD 0.024；naive_rag SD 0.014 | rule_context 0.703–0.720（SD 0.006）；pure_llm SD 0.026；naive_rag SD 0.017 |
| 吸收分层计数（high/medium/low/very-low/minimal/none） | 15/17/61/9/7/4 | 12/20/59/11/7/4 |
| 内部开发集（78） | 敏感性 1.000 | 门控后 0.882（15/17）；未门控 1.000 |
| 200 例开发集 | 0.210（敏感性 0.069、特异性 0.895） | 0.240（0.069、门控特异性 0.977） |
| 新增：未评估路径 | 无 | 176/1,933（9.1%）；路径分布 504/507/746/176（26.1%/26.2%/38.6%/9.1%） |
| 新增：仅局部制剂 | 无 | 1,930 对，降级 1,499（77.7%），350 从 high 降；非局部仅 3 对 |
| 新增：RA-DDInter | 无 | 42 例：21/42（0.500）vs 原始 DDInter 17/42（0.405）vs 级联 32/42（0.762）；1,933 对上一致 1,489（77.0%），级联高 148、低 296 |
| 新增：Lexicomp | 无 | 42 例：C→medium 17/42、C→high 18/42；二分类命中 16/42、κ 0.323、特异性 1.000 |
| 新增：gated vs ungated | 无 | 未门控使冻结标签一致率 0.856（101/118）→ 0.873（103/118）；门控为 primary |
| 参考文献数 | 42 | 45 |
| 已删除的数字口径 | 6.7% PPV、0.992（早期版本）、75.27%/75.69%、κ 上限 0.294/0.314 | 均不再出现 |

### 3.3 结构变化清单

- 新增 §3.9 "Comparison with route-aware resources"（RA-DDInter + Lexicomp）。
- 新增 §4.3 "Exposure is not risk"；原 4.3 Limitations 顺延为 4.4，原 4.4 Future directions 顺延为 4.5。
- §2.3 由 "Validation data" 改名 "Reference and audit data"；§3.3 由 "Agreement with the literature-derived gold" 改名 "Agreement with the author-derived reference set"；§3.6 标题改为 "Second configuration (different model, token allowance and sampling)"。
- §2.2 新增五个粗体小节：Rule construction, adjudication and provenance / L3 hard constraint and unassessed pairs / Grade definitions and expected management / Patient-specific factors / Intended workflow。
- 删除 §2.2 原 "Citation coverage is narrower than 'citation-verified' implies" 整段（41 DrugBank/7 label/2 DOI/2 DDInter/1 PubMed 的来源构成表）。
- Limitations 由 3 小节扩为 7 小节；Future directions 由四条扩为六条。
- 新增 Table 6、Table 7、Figure 6；补充材料 Texts S1–S10、Tables S1–S19（含 S5b、S18b）。
- 新增 S19（gated vs ungated）、S18/S18b（route-aware 与 Lexicomp）、S17（exposure-risk by mechanism）、S16（source tier 定义）、S15（patient factors）、S14（104 个矩阵格）、S10（tier 处置与复方拆解）。

---

## 四、我们在修订中自己发现的新问题，以及回复信是否披露

> 作者特别要求这一节。以下 12 条来自 NEW 审计；§4.2 的 3 条是本轮汇总时另行核对发现的。每条均标"已披露/部分披露/未披露"，并给出证据。§4.1 中的开发日志行号（`architecture_v2_results.md`、`l1_gold_provenance.csv`、旧 `l1_test_process_audit.md`）来自 NEW 审计的逐条核对；本轮另行复核了手稿、回复信与 `response_addendum_proposed.md` 中的对应句。
>
> **时间线（影响披露判断）：** 两封回复信分别生成于 2026-11-13 01:39（R1）和 00:59（R2），而 `outputs/audits/response_addendum_proposed.md` 生成于 11:45，已经列出 6 条 R1 + 4 条 R2 的 "additional issues"；也就是说，**作者已经起草了部分补充段落，但尚未合并进正式回复信**。这解释了为什么正式回复信落后于当前稿件。

### 4.1 NEW 审计列出的 12 条

| # | 新问题 | 证据 | 回复信是否披露 | 说明 |
|---|---|---|---|---|
| 1 | **B01–B20 并非 development-free**：B02/B12 在引擎复核后被改标、B18/B19 参与矩阵设计，20/20 corrected 部分同义反复 | `outputs/audits/response_addendum_proposed.md:9`；`manuscript.en.md:61`（B02/B12 校正、B18/B19 矩阵设计、"partly tautological"）、`:188`（"No development-free subset remains"）；`outputs/blind_test/architecture_v2_results.md:34-35`、`:44`、`:63`；`outputs/recomputed/l1_gold_provenance.csv:3`、`:13`；旧审计 `outputs/blind_test/l1_test_process_audit.md:44` 曾称"仅盲测1（未参与矩阵调参）"，与上述记录矛盾 | **部分披露**：R1 回复 `:32` 写 "the 20 B-only cases are reported separately but are not development-free" | 只有结论半句，没有 B02/B12/B18/B19 的具体开发用途，没有说明 20/20 corrected 因 B02/B12 向引擎改标而部分同义反复，也未撤回旧审计"未参与矩阵调参"的说法。审稿人无法判断污染程度。 |
| 2 | **1,933 对只是 4,546 个 registry-matched pairs 中有分级严重度的子集**；2,613 个 `Unknown` 被排除，回复信未交代分母 | `manuscript.en.md:63`（4,546/2,613/1,933）、`:106`、`:180`；`outputs/audits/response_addendum_proposed.md:10`；`grep -rn '4546\|4,546\|2613\|2,613' outputs/recomputed/*.json outputs/audits/*.json scripts/*.py` 无命中；`scripts/revision_r1_stats.py:160-185` 只在 `LEVEL_MAP.get(di.lower())` 非空时收录 pair，不输出总数或 Unknown 数 | **未披露**：R1 回复 `:56`、R2 回复 `:83` 只写 "1,933 graded-severity pairs"，没有 4,546/2,613 | 77.7% 只适用于有分级严重度的 1,933 对，不是全部 4,546 个匹配对；对 2,613 个 `Unknown` 对的外推未知。精确分母目前只能从稿件文字获得，脚本/JSON 不能复算。 |
| 3 | **80.3% 是低 tier 组成统计，不是因果分解**；旧稿写 "attributable to low systemic absorption" | `manuscript.en.md:106`（"involved ... composition statistic, not a causal decomposition"）；`outputs/audits/response_addendum_proposed.md:11` 给出 698/72/436 分解；`git show HEAD:outputs/deliverables/manuscript.md` 第 98 行旧句 "80.5% ... attributable to low systemic absorption"；R1 回复 `:70` 只写 "1,203 of the downgrades (80.3%) involved" | **部分披露**：R1 回复 `:70` 用了 "involved"，但未标注为组成统计 | 未说明 698 由 G19 判低、72 由 absorption-forced matrix scaling、436 由不依赖 tier 的 rule/matrix cell 决定；审稿人可能仍把 80.3% 读成因果归因。 |
| 4 | **"five unsupported" 不是全部关键子集**：另有 4 个 DDInter-high 对走 unassessed default path 被低判；R1 回复仍写 "the clinically critical subset" | `manuscript.en.md:116`（五例为 3 high + 2 medium；不是 whole clinically critical set；12 例 default path；D3-026、D3-029、D3-033、D3-080）；`outputs/audits/response_addendum_proposed.md:12`；R1 回复 `:86` 仍写 "The five unsupported undergradings are the clinically critical subset"；R2 回复 `:73` 写 "the five unsupported downgrades are high-tier agents"；S2 表把 D3-026/029/033/080 标为 `route_consistent_downgrade`（`Supplementary_Material.md:255`、`:258`、`:260`、`:269`），而 `:272` 注又说这 12 个 default-path 病例 "low grade is not evidence of safety" | **未披露**；R1 回复 `:86` 仍保留与稿件 §3.5 相反的旧句 | 五例只是 "clearest unsupported subset"；R2 的 "high-tier" 与 3 high/2 medium 的实际构成不符；S2 的分类标签与正文 "not evidence of safety" 未协调。 |
| 5 | **Figure 6 旧图显示正文未定义的 `Confidence 100%` 和 `0.2 s`**；图已重绘，但实际 Streamlit 界面仍渲染这两个字段 | `outputs/audits/response_addendum_proposed.md:24`；`outputs/figures/figure6_redraw_prompt.md:9`、`:82`、`:147`；`outputs/deliverables/figure_legends.md:25` 已改为 assessment status/path/recommendation；`app/streamlit_app.py:300`（Confidence）、`:303`（Time）、`:752`/`:754`（render_stat_card） | **未披露**：R2 回复 `:99` 只说 "We added a workflow figure"，`:103` 只说 "The visual layout was checked page by page" | 图改了、实际界面没改；审稿人若打开 demo 会直接看到未定义指标。 |
| 6 | **Timolol 证据行原写 "50–78%" 并与口服剂量比较**，但引用的研究不支持该范围或口服比较 | `outputs/audits/response_addendum_proposed.md:13`；`Supplementary_Material.md:425` 现写 "about 78% relative to intravenous timolol in one crossover study"；`manuscript.en.md:19` 只写 "plasma concentrations in the low ng/mL range"；全仓库搜索 `50–78/50-78/50%–78` 除 addendum 外无命中 | **未披露**：R1 回复 `:46` 只提 timolol 复方 tier 修正；R2 回复 `:105` 只说不需要新参考文献 | 未说明原 50–78%/口服比较无来源；未说明 timolol 仍为 high tier 的依据（约 78% of IV 仍远高于 10% 口服治疗暴露阈值）；未说明该修正是否改变任何病例或结论。 |
| 7 | **参考文献元数据/版本错误**：Robertson & Zaragoza 卷页、Jumbe & Miller 版次/出版社、[13–16,29] 缺标题/卷/页；"45/45 resolve and match" 与 reference_verification_table 中 ref 36 "unverifiable" 不一致 | `outputs/audits/response_addendum_proposed.md:14`；`outputs/audits/reference_verification_table.md:39`（ref 37 "volume/pages corrected to 4, 1–174"）、`:47`（ref 45 "2nd ed., Routledge"）、`:38`（ref 36 Crossref "unverifiable"）；`git show HEAD` [25] Robertson 为 "3, 333–389"，当前 `manuscript.en.md:324` [37] 为 "4, 1–174"；HEAD [37] Jumbe 为 "3rd ed. Boca Raton: CRC Press"，当前 `:340` 为 "2nd ed. London: Routledge"；`pdftotext` 显示 PDF 仍为 "3, 333–389"，DOCX 亦然 | **未披露**：R1 回复 `:156` 只列 digoxin/warfarin/两条 low-absorption 引用错配；R2 回复 `:105` 只说文献表已审 | 除版本/页码外，最关键的是 [37]：REF 审计判定 `3, 333–389` 正确、Crossref 的 `4(1–2):1–174` 是出版方撞号错误；当前源稿却改成了错误值，而 PDF/docx 仍是正确值。**NEW 的建议回复句 "was volume 3 ... now volume 4, 1–174" 与 REFS 结论相反，不能直接使用。** |
| 8 | **Table 6/7 与 S18b 示例错误**：Table 6 旧 unassessed 示例用 sildenafil，但该对实际是 assessed matrix-none；Table 7 比较器未标 "no absorption correction"；S18b 旧 C-vs-D 例子来自 none-vs-D/X 组 | `outputs/audits/response_addendum_proposed.md:25`；`outputs/deliverables/tables/table6_grade_definitions.md:8` 现用 "Timolol + warfarin (default path)"；`outputs/deliverables/tables/table7_route_aware.md:3` 已写 "DDInter (no absorption correction)"；S18b `Supplementary_Material.md:1244` 现写 "timolol ophthalmic C versus systemic D"；`outputs/audits/lexicomp_route_aware.json` 的 route_comparison.examples 显示 G08/G19 ophthalmic_risk 为 null、systemic 为 D/X，只有 G142 timolol 是 C vs D | **未披露**：R2 回复 `:99`/`:103` 只说新增表和逐页版式检查 | 未说明旧示例把 assessed matrix-none 误当 unassessed；未说明 Table 7 比较器标签的区分意义；未说明 S18b C-vs-D 例子纠正及其对 route-specific discordance 计数的影响。 |
| 9 | **§3.2 内部验证敏感度 0.353 是旧 case-ID 映射的 6/17，当前引擎为 15/17=0.882**；同段还把 gated 0.240 与 ungated 0.895 混用 | `outputs/audits/revision_completeness_audit.md:99`、`:108`、`:111-113`；`outputs/audits/revision_fix_verification.md:13`、`:31`；`manuscript.en.md:92` 现为 0.882/0.984/0.240/0.069/0.977；R1 回复全文无 0.353/0.882（grep 无命中） | **未披露**：R1 回复 summary 表 row 3 只写 "gating sensitivity reported" | 未说明旧值来源（6/17 旧映射）及为何改为 15/17；未说明 0.895 与 0.977 的 gated/ungated 口径混用；未说明只有 G137/G138 被 gate 降级。 |
| 10 | **专家汇总文件与问卷/扫描件不一致**：kappa 0.846→0.840，R03 medium→low/low，E1/E2 vs displayed 0.417/0.333→2/12、1/12 | `outputs/audits/revision_fix_verification.md:71`；`outputs/audits/independent_recompute_report.md:129-133`；`manuscript.en.md:136` 现用 0.840、2/12、1/12 | **未披露**：R1 回复 `:130-132` 只描述设计与解释，没有 kappa 或逐例一致数 | 这是结果层面的更正，不是排版；汇总文件旧值与问卷/扫描件不符，重建后 R03 改为 low/low、system_v2 与问卷一致。 |
| 11 | **Table 4/S8 原来只列 corrected 标签分布 28/51/39**，而主分析是 frozen 28/50/40，文中未标口径 | `outputs/audits/revision_fix_verification.md:68`；`outputs/audits/independent_recompute_report.md:112-116`；当前 `outputs/deliverables/tables/table4_validation.md` 已并列 frozen（28/50/40）与 corrected（28/51/39），S8（`Supplementary_Material.md:586-597`）同 | **未披露**：R1/R2 两封信均未提 | 未说明 Table 4/S8 现在并列两种分布；审稿人可能仍以为 51/39 是主分析分布。 |
| 12 | **Configuration 2 的 `rule_context` 使用修正前提示词，`pure_llm`/`naive_rag` 未重跑**，Table 3 的基线比较混合了不同口径 | `manuscript.en.md:67`、`:124`；`outputs/deliverables/figure_legends.md:9`；R1 回复 `:96-100` 只描述 configuration 1/2 与检索重叠 | **未披露**：R1 回复 `:96-100` 未提；R2 回复未提 | 未说明 configuration 2 的 rule_context 使用修正前上下文块、pure_llm/naive_rag 未随 tier 修正重跑；未说明 Table 3 的 configuration-1/2 比较因此不是干净的检索增强检验。 |

### 4.2 本轮汇总另行发现并核实的 3 条

| # | 发现 | 证据 | 回复信是否披露 | 影响 |
|---|---|---|---|---|
| A | **Table 3 注与正文直接矛盾**：Table 3 末注仍写 "B01-B20 were never used in development, whereas C01-C20 entered the class-matrix loop in v2.1-v2.3"；手稿 `:61` 明确写 B01–B20 也在开发中审阅过（B02/B12 改标、B18/B19 参与矩阵设计），`:188` 写 "B01–B20 informed rule-gap diagnosis and matrix design" | `outputs/deliverables/tables/table3_performance.md:30`；`manuscript.en.md:61`、`:188` | **未披露** | 这是审稿人最容易抓住的自相矛盾：正文承认 B 组受开发污染，Table 3 注却声称从未用于开发。必须删除/改写该注，否则 R1-1 的披露会被表注抵消。 |
| B | **[37] 卷页在源稿中被"改错"**：REF 审计判定 `3, 333–389` 正确，Crossref/Zotero 的 `4(1–2):1–174` 是出版方元数据撞号（与 10.1561/1500000013 同卷同页）；当前 `manuscript.en.md:324` 采用 `4, 1–174`，而提交 PDF（`pdftotext` 第 1600 行）与 DOCX 仍为 `3, 333–389` | `manuscript.en.md:324`；`outputs/audits/reference_verification_table.md:39`；REFS #37；`pdftotext -layout outputs/deliverables/manuscript.pdf -` 输出 `Found Trends Inf Retr. 3, 333–389`；DOCX XML 含 `333–389` | **未披露** | 当前"源稿—PDF/docx"不一致：源稿错、编译版对。若按源稿重建提交文件，会把正确引文改错；若按 PDF 提交，则源稿与提交版不一致。必须先把源稿回退为 `3, 333–389`，再重建。 |
| C | **MANIFEST 14/18 不通过**：4 条 OK、7 条 FAILED、7 条文件缺失；与手稿 `:81`、`:224` 的 "SHA-256 pinned" 不符 | 本轮 `sha256sum -c MANIFEST.sha256`：`configs/rules.yaml`、`configs/drug_classes.yaml`、`configs/flag_catalog.yaml`、`data/seed/entities_a.csv`、`data/seed/entities_b.csv`、`data/seed/evidence_chunks.jsonl`、`data/evidence/index_manifest.json` FAILED；`data/gold/l1_gold_provenance.csv`、`audit_set_design.json`、`audit_gold_provenance.csv`、`audit_gold_rederived.json`、`dev_ddinter_gold_provenance.csv`、`l1_test_process_audit.md`、`data/predictions/REPORT.md` 缺失；仅 `kg_layer.py`、`risk_rules.py`、`class_matrix.yaml`、`prompts.yaml` OK | **未披露** | 审稿人若按 Data availability 复核，会直接发现清单不可验证。必须重建 MANIFEST（或删除 "SHA-256 pinned" 的强声明），并在回复信中说明。 |

### 4.3 披露状态统计

- NEW 12 条：**部分披露 2 条**（#1、#3），**未披露 10 条**（#2、#4–#12）。
- 本轮另行发现 3 条：**全部未披露**。
- 合计 15 条中，只有 2 条在回复信中有部分对应；其余 13 条需要补入回复信或在稿件中已披露但回复信未同步。特别注意：**稿件本身比回复信更诚实**——`manuscript.en.md:116` 已纠正 "five unsupported"，但 R1 回复 `:86` 仍保留旧句；`manuscript.en.md:61` 已承认 B 组污染，但 Table 3 注仍否认。回复信与表注是当前最容易被审稿人抓住的两处"自相矛盾"。

---

## 五、45 篇参考文献真实性核对表

**核验口径（依据 REFS 三组已完成的工作）：** Crossref REST API `https://api.crossref.org/works/{DOI}`、Europe PMC REST `search?query=DOI:"{DOI}"`、`curl -I https://doi.org/{DOI}` 解析状态、Zotero `search_library` 按 DOI 检索；#17 另用 PubMed eutils/Springer 页面核对作者数；#36 用 DataCite（arXiv DOI 不走 Crossref）；#37 用 Semantic Scholar + FnT IR 卷期页码连续性交叉判断。**本轮未重新发起这些网络请求。**

**总计：** 45/45 DOI 可解析（doi.org 302）、45/45 Zotero 命中（found，未写入）；**45 条 verified（#17 的重复作者已删除、#37 的源稿已回退）**。另有 1 条元数据需注意（#35 年份不可独立核验），1 条 arXiv DOI 非 Crossref 索引（#36）。

| # | DOI | 状态 | Zotero | 问题 / 说明 |
|---:|---|---|---|---|
| 1 | 10.1016/j.addr.2006.07.027 | verified | found (7BND6JS2) | 无 |
| 2 | 10.1208/s12248-010-9183-3 | verified | found (HCYR25GX) | 无 |
| 3 | 10.1089/jop.1990.6.243 | verified | found (L6PK4FAX) | Crossref 用现行刊名 J Ocul Pharmacol Ther；PubMed 1990 记录为 J Ocul Pharmacol，与稿一致，非错误 |
| 4 | 10.3389/fmed.2026.1798521 | verified | found (MC2TJNU8) | 无 |
| 5 | 10.2165/00003088-198005010-00004 | verified | found (RGCXVP7T) | Crossref 题名带脚注标记 "Absorption of Ocular Timolol1"，稿题正确 |
| 6 | 10.1046/j.1440-1606.1999.00145.x | verified | found (LEPCMXTN) | β 与 beta 的字符转写差异，非错误 |
| 7 | 10.1007/s00417-002-0462-2 | verified | found (7HRJGE4H) | 无 |
| 8 | 10.7759/cureus.90018 | verified | found (DITFAY76) | 无 |
| 9 | 10.2217/pgs-2023-0122 | verified | found (ZAAUCHZJ) | 作者名缩写稿写 H.，PubMed 为 HE（Henriette E.），属缩写省略 |
| 10 | 10.1136/bmj.294.6565.155-a | verified | found (9C48NIUS) | 稿只著录起始页 155，完整为 155–156，属常见简写 |
| 11 | 10.1016/j.ajem.2020.09.030 | verified | found (4PJRAG2G) | 无 |
| 12 | 10.7759/cureus.7270 | verified | found (PMGXUFXW) | 无 |
| 13 | 10.1097/pec.0b013e3182aa1384 | verified | found (8NXWLGEI) | 无 |
| 14 | 10.1097/pec.0b013e3181668aee | verified | found (26HR9KT6) | 副题名在 Crossref 中为 subtitle 字段，稿合并书写正确 |
| 15 | 10.1097/01.pcc.0000123548.73664.18 | verified | found (RIMMQ87M) | 无 |
| 16 | 10.1016/j.tjem.2016.02.002 | verified | found (K448TSUF) | 无 |
| **17** | **10.1007/s00417-020-04767-9** | **verified** | found (RRK4MDD5) | 题名、期刊、卷 258、页 1579–1586、年 2020、DOI 一致；最终稿已删除重复的第二个 "Sacchi, M."（PubMed 仅 1 位 Sacchi）。 |
| 18 | 10.1002/14651858.cd010520.pub2 | verified | found (SY5JFRRV) | 无 |
| 19 | 10.1111/ceo.13642 | verified | found (ZHU8ZKVK) | 在线 2019、卷 48 属 2020，稿标 2020 正确 |
| 20 | 10.1093/ageing/26.2.63 | verified | found (KJL6B4NC) | 无 |
| 21 | 10.1186/s12877-017-0621-2 | verified | found (7UBBU5ZC) | 无 |
| 22 | 10.1093/nar/gkab880 | verified | found (WPUYAS7I) | 无 |
| 23 | 10.1093/nar/gkae726 | verified | found (P97MSUDZ) | 在线 2024、卷 53 属 2025，稿标 2025 正确 |
| 24 | 10.1016/j.tips.2013.01.006 | verified | found (8ISZBQP3) | 无 |
| 25 | 10.1186/s12916-025-04420-4 | verified | found (8TMQ3PA3) | 无 |
| 26 | 10.1007/s40261-026-01529-z | verified | found (HIEQ6ZPT) | 无 |
| 27 | 10.1093/jamiaopen/ooab023 | verified | found (VVS7JBA9) | 无 |
| 28 | 10.1038/s41586-026-10687-1 | verified | found (C5FJ9Y27) | 无 |
| 29 | 10.1038/s41591-026-04601-5 | verified | found (7LCTJAF3) | 无 |
| 30 | 10.1136/bmj.38398.500764.8F | verified | found (ZFKP758G) | DOI 大小写不敏感，Crossref 返回小写，非错误 |
| 31 | 10.7326/0003-4819-157-1-201207030-00450 | verified | found (XVUSPR5A) | 无 |
| 32 | 10.1197/jamia.M1809 | verified | found (U37TDYCC) | 无 |
| 33 | 10.1093/jamia/ocaa034 | verified | found (XY634VUT) | 无 |
| 34 | 10.1093/jamia/ocag064 | verified | found (LCEIHHES) | 无 |
| 35 | 10.18578/bnf.270842008 | verified | found (DK6673QZ) | **年份 2026 无法独立核验**：Crossref component 无 issued 日期（父 BNF 记录 2015-11-10，数据库持续更新）；DOI、标题、出版方、所属 BNF 均一致 |
| 36 | 10.48550/arXiv.2410.05779 | verified | found (CVCGWDSC) | **Crossref 404 属预期**（arXiv DOI 由 DataCite 注册）；DataCite 记录标题、5 位作者、2024 与稿一致；非 Crossref 索引 |
| **37** | **10.1561/1500000019** | **verified** | found (QVKN57GM) | 最终采用 `3, 333–389`（Semantic Scholar/DBLP/FnT IR 卷期连续性与正文页码一致）；Crossref/Zotero 的 `4(1–2):1–174` 与另一篇 Mining Query Logs（10.1561/1500000013）撞号，不作为引文依据。源稿与 PDF/DOCX 已一致。 |
| 38 | 10.1177/001316446002000104 | verified | found (8VNVJGYI) | 无 |
| 39 | 10.2307/2529310 | verified | found (Q6669VL6) | Crossref 仅登记起始页 159，Europe PMC 为 159–174，与稿一致 |
| 40 | 10.1136/bmj-2023-078378 | verified | found (MJATIDCY) | 无 |
| 41 | 10.1038/s41591-022-01772-9 | verified | found (KLA2JIPP) | 无 |
| 42 | 10.1073/pnas.1803294115 | verified | found (U536C5SJ) | Crossref 无页码，Europe PMC 为 E4304–E4311，与稿一致 |
| 43 | 10.1021/acs.jcim.6c01086 | verified | found (2FIGMQCZ) | 无 |
| 44 | 10.3390/vision10020018 | verified | found (Y65NKGAI) | 无 |
| 45 | 10.4324/9781003113423-6 | verified | found (4U5TG8CZ) | 书级 DOI 为 type=book、edition-number=2、Routledge，与稿一致；Crossref 未列出版地，"London" 无法逐字核验 |

**必须处理的参考文献问题（按优先级）：**

1. **#17 作者重复（已修复）**：最终稿已删除第二个 `Sacchi, M.`。
2. **#37 卷页（已修复）**：源稿已回退为 `Found Trends Inf Retr. 3, 333–389`，并已重建 PDF/DOCX；Crossref 的 `4(1–2):1–174` 是撞号，不要采用。
3. **#35 年份**：若期刊要求可核验的出版年，考虑改为 "British National Formulary (accessed 2026)" 或保留 2026 并在回复信中说明 BNF 为持续更新数据库；当前无法从 Crossref 独立核验。
4. **#36 arXiv**：在 Crossref 不可查属正常；回复信不应写 "45/45 Crossref-verified"，应写 "44 条 Crossref-verified，1 条 arXiv DOI 经 DataCite 核实"。
5. **#3/#9/#10**：均属著录细节，不构成错误，可选择性修正。

---

## 六、建议追加到 R1/R2 回复信的精确文本

> 使用前提：以下只放"追加段落"，不重复整封信。部分条目要求先完成对应修复再使用——尤其 §4.2-A（删除 Table 3 矛盾注）、§4.2-B（[37] 回退并重建 PDF/docx）、§4.2-C（重建 MANIFEST）、§4.1-5（app 停止渲染 Confidence/Time）。未完成修复前，不要把"已修复"写进回复信；可改为如实写"we identified this and will correct it in the final files"。

### 6.1 `r1_addendum`

~~~markdown
## Additional issues identified during the revision

Beyond the points raised by the reviewer, re-auditing the data, the development log and the reference list identified the following issues; all were corrected in the same revision.

1. **The 20 B-only cases are not development-free.** The internal development log shows that B02 and B12 were corrected after engine review, B18 and B19 informed matrix design, and other B cases informed rule-gap diagnosis. Section 2.3 now states that neither half of the 40-case set is an independent test and that the 20/20 corrected figure is partly tautological because both B02 and B12 were moved toward the engine's grade. The note in Table 3 stating that B01–B20 were never used in development has been removed. The 18/20 frozen and 20/20 corrected values are unchanged and are reported as descriptive only.

2. **The registry-scale denominator is 1,933 graded-severity pairs, not all matched pairs.** The DDInter export contains 4,546 registry-matched pairs; 2,613 carry Level `Unknown` and were excluded. Section 2.3, Section 3.4 and the Limitations now state this, and the 77.7% result is described as applying to pairs with a graded severity; its generalization to `Unknown` pairs is unknown. A denominator audit has been added so that the 4,546 / 2,613 / 1,933 counts can be regenerated.

3. **The 80.3% figure is a composition statistic, not a causal decomposition.** Of the 1,502 downgrades, 1,206 involved low-tier ophthalmic agents; of these, 698 were assigned low by G19 and 72 by absorption-forced matrix scaling, while 436 were decided by a rule or matrix cell whose level does not depend on the tier. The text now uses "involved" and labels the figure as a composition statistic.

4. **The five unsupported downgradings are the clearest unsupported subset, not the whole clinically critical set.** They comprise three DDInter-high and two DDInter-medium pairs. Twelve disagreements are on the unassessed default path (10 route-consistent, 2 unsupported), adding four DDInter-high pairs (D3-026, D3-029, D3-033, D3-080) whose low grade is not evidence of safety. The earlier sentence in this response letter that called the five the "clinically critical subset" has been corrected, and the Table S2 class labels for these four default-path pairs have been reconciled so that "route-consistent" is not read as "assessed safe".

5. **The timolol evidence line was overstated.** The cited studies support approximately 78% systemic bioavailability relative to intravenous timolol in one crossover study, not a 50–78% range or a comparison with oral doses; Table S5b now states this. The timolol tier remains high because the reported exposure is well above 10% of an oral therapeutic dose.

6. **The internal development metrics were corrected.** The previously reported sensitivity of 0.353 was 6/17 from an old case-ID mapping, not the current engine's 15/17 = 0.882; the 0.895 specificity came from the ungated analysis and had been mixed with the gated 0.240 agreement. The corrected gated values are sensitivity 0.882 (15/17), specificity 0.984, and 0.240 / 0.069 / 0.977 on the 200-case development set. The only two high-label cases lost to the gate are G137 and G138.

7. **The expert summary was rebuilt from the deposited records.** Inter-rater kappa is 0.840 (not 0.846); R03 is low/low (not medium); the grade displayed for R10 and R11 was medium; expert-versus-displayed agreement is 2/12 and 1/12 (not 0.417 and 0.333). The manuscript and Table S3 now use the transcribed per-case record; the exercise remains descriptive and non-independent.

8. **Table 4 and Table S8 now show both label distributions.** The tables previously showed only the corrected distribution (28 high / 51 medium / 39 low) without saying so, while the primary analysis uses the frozen labels (28 / 50 / 40). Both distributions are now labelled, and Section 2.3 no longer quotes an unlabelled distribution.

9. **Configuration 2 prompt comparability is now stated.** Configuration 2 `rule_context` used the pre-correction context block, and `pure_llm` and `naive_rag` were not re-run after the tier correction, whereas configuration 1 `rule_context` was re-run. The baseline comparison therefore mixes a corrected `rule_context` row with uncorrected rows and is not a clean test of retrieval augmentation (Section 2.4, Section 3.6, Figure 2 legend).

10. **Reference metadata were re-checked.** [45] is the 2nd edition (Routledge); missing titles, volume or page numbers in [13–16,29] were supplied; the duplicate "Sacchi, M." in [17] was removed (the publisher record and PubMed list 9 authors with a single Sacchi). Reference [37] remains "3, 333–389": the Crossref/Zotero record "4(1–2), 1–174" is a publisher metadata collision with 10.1561/1500000013 and is not the correct pagination. Of the 45 DOIs, 44 are Crossref-verified and the arXiv DOI [36] resolves through DataCite and is not Crossref-indexed. The compiled PDF and DOCX have been rebuilt so that they match the source.
~~~

### 6.2 `r2_addendum`

~~~markdown
## Additional issues identified during the revision

Beyond the points raised by the reviewer, re-auditing the data and the figures identified the following issues; all were corrected in the same revision.

1. **The registry-scale denominator is 1,933 graded-severity pairs.** The DDInter export contains 4,546 registry-matched pairs; 2,613 carry Level `Unknown` and were excluded. The 77.7% result applies to pairs with a graded severity; Section 2.3, Section 3.4 and the Limitations state this.

2. **The five unsupported downgradings are not the whole clinically critical set.** They are the clearest unsupported subset (three DDInter-high, two DDInter-medium); 12 disagreements are on the unassessed default path, adding four DDInter-high pairs (D3-026, D3-029, D3-033, D3-080). The manuscript and Table S2 now say so, and the S2 class labels for those four default-path pairs have been reconciled so that "route-consistent" is not read as "assessed safe".

3. **Figure 6 and the demo interface were aligned.** The previous interface screenshot displayed `Confidence 100%` and `0.2 s`, neither of which is defined in the manuscript. Figure 6 has been redrawn as a three-panel schematic reporting `assessment status = assessed`, the matched rule, the path `rule engine` and the recommendation, with no undefined confidence or runtime. The demo interface has been changed to stop rendering the two undefined fields, so that the figure and the runnable demo agree.

4. **Table and example corrections.** Table 6's unassessed example is now timolol + warfarin (the previous sildenafil pair is an assessed matrix-none cell); Table 7's comparator is labelled "DDInter (no absorption correction)"; the S18b C-versus-D example is timolol ophthalmic C versus systemic D, replacing two examples that belonged to the none-versus-D/X group.

5. **Lexicomp reproducibility and citation.** The Lexicomp comparison is now reproducible from `scripts/compare_lexicomp_route_aware.py` and the deposited aggregate results; `scripts/build_r2_tables.py` was corrected so that the regenerated Table 7 includes the Lexicomp cross-reference instead of the obsolete sentence that licensed route-aware databases were unavailable. The 2018 edition and the OpenMed-provided UpToDate interface are stated in Section 3.9 and Table S18b; because Lexicomp is a proprietary database accessed through a third-party interface, we cite the edition and access route rather than redistribute case-level ratings.

6. **The repository manifest was regenerated.** After the final edits, `MANIFEST.sha256` was regenerated and all entries verify with `sha256sum -c`; the previous manifest no longer matched `configs/rules.yaml`, the seed registries, the evidence base and several deposited reference files.
~~~

---

## 七、未覆盖或不能确认的事项

1. **完整测试套件未运行。** 本轮只运行了 `tests/test_assessment_status.py`（4 passed）和 `scripts/audit_manuscript.py`（0 FAIL, 2 WARN）；未运行 `pytest tests/` 全量。因此"测试全绿"不能作为本报告结论。
2. **LLM 基线未重跑。** 所有 LLM 数值（0.419–0.714、配置 2 0.576–0.737、敏感性 0.214–0.536 等）来自稿件、Table 3、`revision_r1_stats.json` 的静态核对，没有重新调用模型。
3. **Lexicomp 未重新查询。** S18b 的 42 例评分来自 `outputs/audits/lexicomp_route_aware.json` 与补充材料；Lexicomp 为 2018 版、经第三方 IP `http://167.99.184.127/d/di.htm` 访问，case-level 专有评分未再分发，无法独立复现。
4. **4,546/2,613/1,933 的精确分母未能从脚本复算。** `scripts/revision_r1_stats.py:160-185` 只统计有 `LEVEL_MAP` 映射的 pair，不输出总数或 Unknown 数；仓库内无 4,546/2,613 的 JSON/CSV 产物。NEW 审计称其直接按 registry 名称/别名 join DDInter 得到 4,695 对、2,681 Unknown、2,014 graded，只能佐证数量级，不能精确复现 4,546/2,613/1,933。该数字目前只能从稿件文字获得。
5. **45 个 DOI 未在本轮重新联网核验。** 第 §5 节的状态依据 REFS 三组已完成的 Crossref/Europe PMC/doi.org/Zotero 核验，不是我本轮重新发起的请求。未检索撤稿数据库，也未核对引文内容与原文结论是否逐条对应（REFS 明确说明这两项未做）。
6. **Zenodo 记录内容未核验。** DOI 10.5281/zenodo.23439606 解析到 zenodo.org（302），但记录内容因网络超时未能读取；无法确认归档版本与当前手稿一致。
7. **审稿人 checklist 原文未提供。** R2 回复 `:109` "We agree with the reviewer that a statistician is not required" 所回应的 checklist 条目无法核实；该句措辞也容易被读成"审稿人认为不需要统计学家"，建议作者核对原文后再定稿。
8. **无独立裁决、无结局数据。** R1-1 的文本要求已完成，但其中的"独立裁决测试集"要求在本次修订中无法完成；R1-5 的"独立复核 30 例分歧"要求也未做。稿件已披露这两点，但本报告不能把独立裁决/独立复核本身判为已完成。
9. **生产界面与图不一致。** `app/streamlit_app.py:300`、`:303`、`:752`、`:754` 仍渲染 Confidence/Time；本报告只能指出问题，不能替作者改代码。若作者不修改 app，R2 回复中"Figure 6 与界面已对齐"的表述不能使用。
10. **MANIFEST 的修复未执行。** 本报告只运行了 `sha256sum -c` 并记录失败项；未重建清单。作者需在最终文件冻结后重新生成，并在回复信中如实说明。

---

**报告结论：** 修订稿在文本层面完成了大多数审稿要求（12/17 complete），但仍有 5 条部分完成，其中 R1-3（unassessed 未进生产界面）和 R1-5（五个 unsupported 被误称为全部关键集）是实质性缺口；R2-1/R2-5/R2-6 的回复信表述与稿件/脚本不一致。自查发现的 15 条新问题中只有 2 条部分披露，13 条未披露；参考文献 45 条全部真实可解析，但 #17 作者重复、#37 卷页在源稿中被改错，必须在提交前修复。**不建议在完成上述修复前提交。**

---

## 八、Post-audit corrections (detailed)

| Item | Correction | Verification |
|---|---|---|
| R1-3 unassessed service path | `RiskAssessment` now carries `assessment_status`/`assessment_note`; `SafetyAgent.assess()` copies them from `deterministic_level_v2()`; the app shows an UNASSESSED warning and no longer shows Confidence/Time | source review; `tests/test_assessment_status.py` 4 passed, 1 skipped under Python 3.10 (the service test is skipped because `enum.StrEnum` requires 3.11) |
| R1-5 / R2-5 five-unsupported wording | Responses now say 3 DDInter-high + 2 DDInter-medium, not the whole critical set; 161/1,502 downgrades are on the default path | response lines; manuscript §3.5/§4.3 |
| R2-1 matrix-source wording | “at least one source supported” replaced by “rule set, class extrapolation, expert consensus or pharmacological inference” in manuscript, Text S10 and R2 | source and supplement text |
| R2-6 Table 7 generator | `build_r2_tables.py` now writes the Lexicomp cross-reference instead of “licensed databases were not available” | regenerated table matches submitted Table 7 |
| Table 3 note | “B01–B20 never used” replaced by “both halves reviewed during development; neither is development-free” | outputs/tables and deliverables/tables synced |
| Reference metadata | [17] duplicate Sacchi removed; [37] restored to 3:333–389; [45] 2nd ed. Routledge | Crossref/PubMed/Semantic Scholar/DBLP |
| MANIFEST | Rebuilt with 20 entries including `safety_agent.py` and `schemas.py` | `build_manifest.py` |
| Reference verification | 45/45 DOI present in Zotero; 44/44 non-arXiv Crossref-verified; arXiv via DataCite | `outputs/audits/zotero_reference_verification.json`, `crossref_reference_verification.json` |

**Remaining residual limitations (disclosed, not fixed):** no independent adjudication/development-free test set (R1-1/R1-5); Lexicomp comparison uses the 2018 edition (R2-6); audit disagreement classification is author-made; no outcome data.
