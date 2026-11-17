# 修复后复核（A–H）

**日期**：2026-11-11
**范围**：`outputs/paper/manuscript.en.md`、补充材料、两封回复稿、Table 2/3/5/6/7、S13/S17/S19、Frontiers 包、标红版
**结论**：A–H 已全部修复并重建；最终自动门禁 **92/92 PASS**，`audit_manuscript.py` **0 FAIL / 2 WARN**；修复过程中新出现的表格分页问题也已修好并通过视觉复核。

---

## 1. 逐项修复

| 项 | 修复前 | 修复后 | 位置/验证 |
|---|---|---|---|
| **A. §3.2 内部验证指标** | gated sens 0.353、spec 1.000；dev spec 0.895 与 gated agreement 0.240 混用 | gated **0.882（15/17）**、spec **0.984**；ungated 1.000/0.984；dev 200 例 **0.240 / 0.069 / 0.977**；明确仅 G137/G138 被 gate 降级 | 正文 §3.2；`scripts/recompute_development_metrics.py`；`outputs/recomputed/development_gate_metrics.json` |
| **B. S17 旧数** | “76.1% divergence” | **77.7%** | `outputs/tables/table_s17_exposure_risk.md`、补充材料 S17 |
| **C. 词数/页数元数据** | 正文 6,279、摘要 334、补充 51 页 | 正文 **6,775**、摘要 **336**、补充 **38 页**、主稿 47 页 | `SUBMISSION_STATUS.md`、`outputs/deliverables/frontiers/README.md`、`_form_fields.json`、`_abstract_plain.txt` |
| **D. 回复稿编号** | R1 回复写 Tables S1–S18 | **S1–S19** | `outputs/submission/response_to_reviewers_r1.md/.docx/.pdf` 及 frontiers 副本 |
| **E. 层级表述** | 两处“two layers / rule and matrix layers” | 统一为 **three layers**（L1/L2/L3） | 正文 §2.2、§4.2；补充 S4 Figure 1 图注；`outputs/paper/figure_legends.md` |
| **F. 摘要配置 2** | “model and sampling” | “model, **token allowance** and sampling” | 摘要；346 词（上限 350） |
| **G. `numbers.json` 口径** | `audit.*` 只有 seed0，与 Table 3 的五条件均值不一致 | 新增 `audit.multi.*` 五条件均值 + `_metric_conventions`；Table 3 对应值 0.630/0.535/0.602 | `outputs/recomputed/numbers.json` |
| **H. S13 方法名** | 行名仍为 `lightrag` | 行名 **`rule_context`**，脚注保留 method id | 补充材料 S13；`scripts/build_revision_tables.py` |

### A 的复算依据

用当前引擎逐例重跑 `data/datasets/internal_validation/cases.jsonl`（78 例，17 例 high）：

- gated：TP 15/17 = **0.882**，TN 60/61 = **0.984**
- ungated：17/17 = **1.000**，TN 60/61 = **0.984**
- dev 200 例 gated：**0.240** exact agreement，sens **0.069**，spec **0.977**
- 外部 70 例：0.443，0.077，0.935

旧值 0.353 恰好等于 6/17，与早期只计入 G01–G06 的口径吻合；当前引擎按 entity ID 映射后为 15/17。

---

## 2. 修复过程中新发现并已修掉的问题

| 问题 | 修复 |
|---|---|
| 补充表 S13 在页末只显示 3 个方法，`rule_context` 落到下一页，看起来像缺行 | 表头/标题与首行绑定，表格可跨页但行不拆；S13 现在完整落在 1 页 |
| 补充表 S18 页末出现终止线，看起来只到 23 例 | 改为“终止线只画在最后一行”，跨页时不再像结束；S18 现在 42 例完整落在 1 页 |
| 回复稿 Summary 表第 8 行在页末被切断 | 行不可拆分；第 8 行整行移到第 2 页并重复表头 |
| 主稿 Table 2a 页末出现终止线、Table 2b 无标题 | 终止线只画最后一行；补回 Table 2b 子标题 |
| Table 5 的三个面板在续页无标题 | 增加 “Table 5 (continued).” 子标题；Table 5/6 视觉复核通过 |

视觉复核：S13、S18、回复稿第 1/2 页、主稿 Table 5/6 页面均 **pass**。

---

## 3. 最终自动门禁

`scripts/final_consistency_check.py`：**92 项全部通过**，包括：

- 主稿 49 页（标红 49 页）、补充 42 页；摘要 346 词；正文 7,527 词；45 条参考文献
- 正文含 0.882/0.984/0.977，无 0.353/76.1%；补充含 77.7%、无 76.1%
- S1–S19、Text S1–S10 各仅 1 个标题；S2=30 行、S5=113 行、S14=104 行、S18=42 行、S18b 已入表
- R1 回复 S1–S19；frontiers README/STATUS 的 346/7,527/42 页均同步
- `numbers.json` 的 `audit.multi.*` 与 Table 3 一致；dev/gating JSON 与正文一致
- 标红版 42 全红 / 46 部分红 / 98 全黑；frontiers 副本与源文件 SHA-256 一致

`scripts/audit_manuscript.py`：**0 FAIL / 2 WARN**（WARN 为 2.1/3.1/3.6/3.7/3.9 小节未被交叉引用，属既有提示，不影响投稿）。

---

## 3b. 从原始数据重跑后追加修复（第三轮）

| 问题 | 原状 | 修复 |
|---|---|---|
| Table 4 / S8 / §2.3 标签分布口径 | 表中 L1 行是 **corrected** 分布（28/51/39），但主分析是 frozen（28/50/40），文中未标明，读者会误以为 51/39 是主分析 | Table 4 与 S8 同时列出 frozen（28 high / 50 medium / 40 low）与 corrected（28 / 51 / 39）；§2.3 不再单写一个无口径的数字 |
| §3.7 温度敏感性区间 | 写的是 corrected-label 区间（0.712–0.771、0.432、SD 0.024/0.014），但主分析是 frozen | 改为 frozen 区间：rule_context **0.703–0.720（SD 0.006）**、pure_llm **0.449–0.517（SD 0.026）**、naive_rag **0.390–0.441（SD 0.017）** |
| §3.1 “all four datasets” | Table 3 并不包含 dev200/external70，句子里却说四个数据集都在表内 | 改为“primary reference set、no-development subset、DDInter audit、configuration 2 在 Table 3；两个 development-phase sets 在 §3.2” |
| 专家原始汇总文件 | `expert_review_results.json`/`.md` 是旧版：R03 记为 medium、system_v2 与问卷不符、kappa 0.846 | 从 S3 逐例转录重生成：R03 low/low、system_v2 用问卷实际展示值（R10/R11 medium）、kappa **0.840**、E1/E2 vs displayed **2/12、1/12** |
| `MANIFEST.sha256` | 27 个文件的哈希全部过期，且引用不存在的 `data/gold/audit_set_design.json`；`sha256sum -c` 15 项失败 | 以当前文件重生成 27 条 manifest，`sha256sum -c` **27/27 OK** |
| Figure 1 图内公式 | 仍是 `max(L1, L2)`；source CSV 写 105 matrix cells | 改为 `max(L1, L2, L3)`；source CSV 改为 104 cells；Figure 1 四种格式重新生成并嵌入主稿 |
| Table 2 缺 3 条 patient-factor policies | Table 2 标题说 43 policy entries，但表内只有 40 条 rule | 增加 **Table 2c**（elderly / renal impairment / polypharmacy），S6 同步；Table 2 现在确实覆盖 40 + 3 |
| Figure 6 只有示意图/契约卡片 | 没有展示实际网页 | 重做为三面板：**(a) workflow、(b) 实际网页 HIGH 结果截图、(c) 同一界面的 rule-details 内容以矢量重绘（保证印刷清晰）**；图注同步，Figure 6 与 caption 同页 |
| README 数据路径 | 写 `data/gold/`，目录不存在 | 改为 `data/datasets/` |
| `numbers.json` 主分析口径 | 只有 corrected 指标；frozen 主分析（101/118、0.856、kappa 0.779、36/40）不在机器可读文件里 | 新增 `l1.frozen.*`、`l1.frozen.subset.blind_frozen`、`l1.frozen.acc3_wilson/sens_wilson/kappa` |

独立重跑的核心数字与稿件一致：L1 frozen 101/118、0.856、24/28、0.978、kappa 0.779；audit applied 62/92、0.674、8/25、0.970、kappa 0.428；registry 1,933 / 1,502 / 65 / 352 / 1,206；paths 504/507/746/176；topical 1,930/1,499/350/1,203；RA 1,489/148/296；config2 0.576/0.585/0.737。详见 `outputs/audits/independent_recompute.json`。

---

## 4. 残留限制

1. **独立临床/临床药师裁定或盲法评审**（R1 #1/#5/#9）：没有新数据集，也没有独立评审；稿中明确写成 limitation / future work。
2. **商业 route-aware 数据库对照**（R2 #6）：已完成 Lexicomp 2018（UpToDate/OpenMed 实例）对照，使用 35 例 ophthalmic-specific entry，7 例 generic entry 已标注；结果见 `outputs/audits/lexicomp_route_aware_report.md` 与 Supplementary Table S18b。该实例为 2018 版，不是当前授权版本，稿中已如实披露；当前版本对照仍列为 future work。

这两项不是本轮“修 bug”能解决的，属于研究设计层面的残留；当前稿的表述是诚实的。

---

## 5. 当前文件

| 文件 | 页数/说明 |
|---|---|
| `outputs/deliverables/manuscript.pdf` | 48 页，clean |
| `outputs/deliverables/manuscript_marked_changes.pdf` | 48 页，逐词标红 |
| `outputs/deliverables/supplementary_files/Supplementary_Material.pdf` | 42 页，S1–S19（含 S18b） |
| `outputs/deliverables/supplementary_files/Supplementary_Material_marked_changes.pdf` | 42 页，表格按行标红 |
| `outputs/submission/response_to_reviewers_r1.pdf` | 14 页 |
| `outputs/submission/response_to_reviewers_r2.pdf` | 8 页 |
| `outputs/deliverables/frontiers/` | 上述文件已同步 |

> 未提交。等您明确说“投”之后才执行投稿。
