# 修改稿 vs 原稿差异与审稿意见完成度审计

> **状态更新（2026-11-11）：** 本报告 A–H 已全部修复并重建；修复后复核见 [revision_fix_verification.md](revision_fix_verification.md)。以下保留修复前审计记录。
>
> **后续引擎修正（2026-11-12）：** unassessed 定义修正后，1,933 对路径为 504/507/746/176，unassessed 176（9.1%），assessed downgrade 1,341/1,757（76.3%）；本表 43/1,220 为修正前记录。

**基线**：`HEAD 0f129ca`（Frontiers 已投稿冻结版，2026-10-17）
**当前稿**：`outputs/paper/manuscript.en.md` / `outputs/deliverables/manuscript.pdf`
**审计日期**：2026-11-11
**范围**：正文、补充材料、两封回复稿、表 3/5/6/7、S1–S19、引擎与复算文件

---

## 一、改了多少

### 1. 规模变化

| 指标 | 原稿 | 修改稿 | 变化 |
|---|---:|---:|---:|
| 全文词数（含摘要/声明/参考文献） | 8,450 | 9,801 | **+1,351（+16.0%）** |
| 正文词数（Introduction–Conclusions，包口径） | 5,551 | 6,742 | **+1,191（+21.5%）** |
| 摘要 | 332 | 334 | +2 |
| 参考文献 | 42 | 45 | +3 |
| 主稿页数 | 43 | 47 | +4 |
| 补充材料页数 | 40 | 51 | +11 |
| 主文表 | 5 | 7 | +2（Table 6、7） |
| 主文图 | 5 | 6 | +1（Figure 6） |
| 补充表 | S1–S8 | S1–S19 | +11 |
| 补充文本 | S1–S7、S9 | S1–S10 | 补齐 S8、新增 S10 |

> 注：Frontiers 表单与 `outputs/deliverables/frontiers/README.md` 仍写 **6,279 词**，是 R2 新增方法学内容之前的旧数；当前 docx 正文实测 **6,742 词**。离 12,000 词上限仍很远，但元数据需同步。

### 2. 改动深度

- 正文段落：**67 → 82 段**。
- 原稿 67 段中：**仅 12 段原样保留**（17.9%）；**34 段重写**（50.7%）；**21 段删除**（31.3%）。
- 新增段落 **36 段**，主要是 §2.2 规则/矩阵构建、等级定义、患者因素、工作流，§3.9 RA-DDInter，§4.3 暴露≠风险，以及 Declarations 细化。
- 词级 diff：**新增 3,509 词、删除 2,209 词**，合计 5,718 个词位被触碰，相当于原正文词数的 75.8%。
- 标红 docx：主稿 **5,068 个红字 / 319 个红色 run**；补充材料 **2,442 个红字 / 130 个红色 run**。

### 3. 各节词数变化

| 章节 | 原稿 | 修改稿 | 变化 |
|---|---:|---:|---:|
| 1. Introduction | 439 | 413 | −26 |
| 2. Materials and methods | 1,798 | 2,340 | **+542（+30.1%）** |
| 3. Results | 2,013 | 2,434 | **+421（+20.9%）** |
| 4. Discussion | 1,115 | 1,405 | **+290（+26.0%）** |
| 5. Conclusions | 198 | 162 | −36 |

（小节合计 5,563→6,754；与上表 5,551→6,742 的 12 词差异来自节间分隔符。）

结论：**不是文字润色，而是方法、结果、讨论三块都重写了**；增幅集中在 Methods（+30.1%）和 Results（+20.9%），与两位审稿人要求的方法学补充、外部审计拆分、RA-DDInter 对照一致。

---

## 二、Reviewer 1（10 条）

| # | 意见要点 | 状态 | 当前稿证据 | 残留 |
|---|---|---|---|---|
| 1 | 不能把 90.7% 叫 accuracy/gold；frozen 为主分析；单独报无开发暴露病例 | **已解决** | §3.3：frozen 101/118（0.856）、corrected 104/118（0.881）、no-dev 36/40（0.900）；全文改用 exact agreement；S1 列 17 例分歧 | 仍无独立裁定测试集，已在 §4.4/§4.5 明说 |
| 2 | 吸收分级要有药械证据；13 处 registry/curation 不一致必须解决 | **已解决** | §2.2；S5 全 113 行（13 measured / 11 label / 89 class-inferred）；S5b 24 例细节；S10 列 13 处逐条解决 | 89/113 仍是 class inference，已标 uncertain |
| 3 | 低风险要有 safeguard；default low 不能等于安全；量化路径；处理 gating | **已解决（引擎改动）** | `assessment_status=unassessed`；43/1,933（2.2%）；路径 504/1,220/166/43；S11 列 43 例；S19 gated vs ungated；测试 `test_assessment_status.py` | 无 |
| 4 | 按 route 拆分；104 topical 主分析；抗 VEGF 逐个论证；复方拆组分 | **已解决** | §3.4：104 topical → 1,930 对，1,499 降级，350 从 high 降；9 非 topical → 3 对，S12；S5 逐个抗 VEGF；S10 12 个复方 | 无 |
| 5 | 外部审计两套标签都要报；30 例分歧要独立复核并区分 route-consistent / unsupported | **部分解决（已披露）** | §3.5 两套标签全报；S2 列 30 例，21 route-consistent / 5 unsupported / 4 over-grade；明确“未独立裁定” | **“independently reviewed”未做到**，仅作者分类并披露 |
| 6 | 不能把第二配置归因于 output budget；LightRAG 应改名；检索重叠要前瞻测量 | **已解决** | §2.4/§3.6 改为 configuration 1/2，明确同时变模型、token、采样；`rule_context`；26/92 重叠前瞻测量，S13 全方法 with/without | 补充表 S13 行名仍用 `lightrag`（有脚注说明） |
| 7 | 2%/10.9%/6.5% 与 7–15 的数字错误 | **已解决** | §3.6：2.2%、10.9%、6.5%；majority vote 7/6/15；范围 6–15 | 无 |
| 8 | 临床意义不能外推；删 1% PPV；不能把分歧说成 alert correction | **已解决** | PPV 段已删；§4.1/§4.4 明确无 outcome data、不能估计 predictive value；77.7% 只是分类差异 | 无 |
| 9 | 专家练习只能描述；删推测性解释；不能把两医生一致性当临床共识 | **已解决** | §2.5/§3.8 改为 perspective comparison；删 rarity/recall/expectation 解释；§4.5 提 blinded independent panel + clinical pharmacy | 仍未实际做盲法独立评审 |
| 10 | 40 条规则逐条核 provenance；修 citation；统一 archive；补交叉引用；ethics 说清楚 | **已解决** | §2.2 + S9：2 direct / 5 contextual / 23 class / 10 mechanism；severity 2 direct / 28 inferred / 10 provisional；digoxin/warfarin/两条 low-abs citation 已修；archive 改为“现有 record + 修订版新版本”；ethics 明说无患者、两医生匿名练习、无正式伦理裁定 | 回复稿仍写 “Tables S1–S18”，应为 S1–S19 |

**R1 小结：10/10 都有对应修改；其中 #5 的“独立复核”未真正完成，#1/#9 的“独立测试集/盲法评审”也只能作为 future work。这三处是审稿人可能继续追问的点。**

---

## 三、Reviewer 2（7 条）

| # | 意见要点 | 状态 | 当前稿证据 | 残留 |
|---|---|---|---|---|
| 1 | 规则/矩阵怎么构建、严重度怎么定、怎么裁定 | **已解决** | §2.2 四段；Text S10；S9 40 条逐条；S14 104 个 cell 全表；明确无 Delphi/独立委员会 | 无 |
| 2 | low/medium/high 要连到临床意义和处理 | **已解决** | §2.2 + Table 6：定义、临床意义、预期处理、示例四列，含 unassessed | 无 |
| 3 | 年龄、肾/肝、QT、剂量、疗程、CYP、滴眼技术怎么处理 | **已解决（明确未建模）** | §2.2 患者因素段；S15 七行覆盖八类因素（剂量与疗程合并一行）；§4.4/§4.5 | 仍是 pair-level，未做患者级模型 |
| 4 | A–E 不能混同来源与证据强度 | **已解决** | §2.1 改为 source tier；S16 说明每级能/不能支持什么；明确不进 grade | 无 |
| 5 | 暴露降低 ≠ 临床风险降低，要按机制/治疗指数说明 | **已解决（正文）/ 补充表有旧数** | §4.3 分 PD/PK/threshold/cumulative 四类；S17 机制表 | **S17 末尾仍写 76.1%，应为 77.7%** |
| 6 | 至少和一个 route-aware 临床资源比较 | **部分解决（替代方案+披露）** | §3.9 + Table 7：42 例 DDInter 17/42、RA-DDInter 21/42、cascade 32/42；1,933 对一致 1,489（77.0%）；明说 Lexicomp/Micromedex/Stockley’s 不可得 | **RA-DDInter 是作者构造的过滤器，不是商业 route-aware 数据库**；审稿人可能不接受为“clinical interaction resource” |
| 7 | 工作流要更清楚，low/medium/high 如何影响管理 | **已解决** | §2.2 工作流段；Figure 6 两面板；Table 6 管理列；明确 proposed, not evaluated | 无 |

**R2 小结：7/7 都有对应修改；#5 有一个补充表旧数必须修；#6 是“用可获得的替代方案做了量化，并诚实披露没有商业库”，属于部分满足。**

---

## 四、本次复核新发现的硬问题（建议提交前修）

### A. §3.2 内部验证集指标与当前引擎不符（最严重）

**位置**：`outputs/paper/manuscript.en.md:92`

现文：
> On the internal validation set (78 cases) sensitivity was **0.353** and specificity **1.000** under the gated primary analysis; under the ungated sensitivity analysis **1.000 and 0.984**. … the drop under the gate is expected because **many of its high labels were derived from the gated rule**.

用当前引擎逐例重跑 `data/datasets/internal_validation/cases.jsonl`（78 例，17 例 high）：

| 口径 | 敏感度 | 特异度 | 说明 |
|---|---:|---:|---|
| gated（当前引擎） | **15/17 = 0.882** | **60/61 = 0.984** | 只有 G137、G138（bromfenac 两例）被 gate 降级 |
| ungated | 17/17 = 1.000 | 60/61 = 0.984 | 与现文 ungated 一致 |

0.353 恰好等于 **6/17**，与“只计入了 G01–G06 这 6 个 high 例”的旧口径吻合；当前引擎按 entity ID 映射后是 15/17。更重要的是，“many of its high labels were derived from the gated rule”不成立：17 个 high 里只有 2 个与 gate 有关。

同一段还有一处混用：
- 现文说 development set 200 例 **0.240 exact agreement（sensitivity 0.069, specificity 0.895）**。
- 当前 gated 口径：0.240 / 0.069 / **0.977**；ungated 口径：0.200 / 0.069 / 0.895。
- 也就是说，0.240 是 gated，0.895 是 ungated，两个口径被拼在一句里。

**建议改成**：
> On the internal validation set (78 cases) sensitivity was 0.882 (15 of 17) and specificity 0.984 under the gated primary analysis; under the ungated sensitivity analysis it was 1.000 and 0.984. The only two high-label cases lost to the gate are the bromfenac pairs G137 and G138. Against the unadjusted systemic-route labels of the development set (200 cases) the system achieved 0.240 exact agreement (sensitivity 0.069, specificity 0.977), and against the external co-mention labels (70 cases) 0.443 (0.077, 0.935).

### B. S17 仍写 76.1%

**位置**：`outputs/deliverables/supplementary_files/Supplementary_Material.md:1017` 与 `outputs/tables/table_s17_exposure_risk.md:9`

> This is why the **76.1%** divergence is reported as a difference in classification…

应为 **77.7%**。这是 R2 #5 专门新增的机制表，旧数残留很显眼。

### C. 正文词数元数据过期

`outputs/deliverables/frontiers/README.md:12`、`SUBMISSION_STATUS.md:44` 仍写 **6,279 词**；当前 docx 正文实测 **6,742 词**（+463）。不影响 12,000 上限，但 Frontiers 表单/包说明应同步。

### D. R1 回复稿补充表编号过期

`outputs/submission/response_to_reviewers_r1.md:146` 写 **Tables S1–S18**；当前补充材料是 **S1–S19**（新增 gating 表）。应改。

### E. 层级表述前后不一致

- `manuscript.en.md:41`：“the only cross-layer composition is the final maximum of the **two layers**”
- `manuscript.en.md:160`：“the final grade is the maximum of the **rule and matrix layers**”
- `Supplementary_Material.md:103` 与 `outputs/paper/figure_legends.md:5`（Figure 1 图注）也写 “maximum of the rule and matrix layers”

全文其他地方和 Figure 6 都是 **max(L1, L2, L3)**。建议统一为“three layers”，或明确 L3 只在 L1/L2 都无信号时提供 low 地板。

### F. 摘要漏掉 token allowance

`manuscript.en.md:15`：“A second configuration that also changed **model and sampling** raised baseline agreement…”；正文 §2.4/§3.6 都写 **model, token allowance and sampling**。R1 #6 正是要求不能把差异归因于单一因素，摘要应补上 token allowance。

### G. `numbers.json` 的审计基线仍是旧值

`outputs/recomputed/numbers.json` 中 audit 基线为 pure_llm 0.641 / naive_rag 0.565 / rule_context 0.598；Table 3 与正文是 **0.630 / 0.535 / 0.591**。不影响正文内部一致性，但“每个数字都可由脚本复算”的声明需要一个统一的输出文件。

### H. 补充表 S13 行名仍为 `lightrag`

S13/S18 的部分行仍用 `lightrag`，虽有脚注说明“method stored as lightrag”，但与正文已改名 `rule_context` 不一致。建议行名改为 `rule_context (lightrag)`，脚注保留。

---

## 五、总体结论

1. **改动量**：正文 +1,191 词（+21.5%），全文 +1,351 词（+16.0%），43→47 页；67 段中只有 12 段原样保留，34 段重写、36 段新增、21 段删除。属于实质性大修，不是润色。
2. **审稿意见**：R1 10/10、R2 7/7 都已在稿中有对应修改和回复；没有“提了但没改”的条目。
3. **没有真正完成、只能披露的 2 项**：
   - 独立临床/临床药师裁定或盲法评审（R1 #1/#5/#9）；
   - 商业 route-aware 数据库对照（R2 #6）。
   这两项在 Limitations/Future directions 中都写明了，属于“诚实披露的残留”，不是隐瞒。
4. **必须在提交前修的硬问题**：A（§3.2 内部验证指标）、B（S17 76.1%）；建议同时修 C–H。A 是最可能被二审抓住的：它同时存在“数值不可复现”和“解释与数据相反”两个问题。

> 本报告只做审计，未改稿。若要按 A–H 直接修并重建主稿/补充/标红/回复稿，我可以一次完成后再给对照清单。
