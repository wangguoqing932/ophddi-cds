# 从原始数据重跑：稿件数字与前后一致性复核

**日期**：2026-11-11
**方法**：不引用任何既有审计报告；直接从 `data/`、`outputs/multiseed_per_dataset/`、`outputs/blind_test/`、`outputs/glm53_baselines/`、`outputs/expert_review/` 和当前引擎重算，使用独立实现的 metrics / kappa 函数。结果写入 `outputs/audits/independent_recompute.json`。

---

## 1. 重算结果与稿件对照

### 1.1 L1 参考集（118 例）

| 指标 | 稿件 | 重算 | 判定 |
|---|---:|---:|---|
| frozen full_system | 101/118（0.856）；sens 0.857（24/28）；spec 0.978；κ 0.779 | 101/118（0.8559）；0.8571；0.9778；0.7790 | 一致 |
| corrected full_system | 104/118（0.881）；sens 0.893（25/28）；spec 0.989；κ 0.818 | 104/118（0.8814）；0.8929；0.9889；0.8181 | 一致 |
| no-dev frozen | 36/40（0.900）；0.818（9/11）；0.966 | 36/40（0.9000）；0.8182；0.9655 | 一致 |
| frozen baselines | 0.478 / 0.419 / 0.714 | 0.4780 / 0.4186 / 0.7136 | 一致 |
| corrected baselines | 0.475 / 0.415 / 0.719 | 0.4746 / 0.4153 / 0.7186 | 一致 |
| frozen CI | 0.781–0.908；0.685–0.943 | 0.781–0.908；0.685–0.943 | 一致 |

### 1.2 DDInter 审计（92 例）

| 指标 | 稿件 | 重算 | 判定 |
|---|---:|---:|---|
| applied | 62/92（0.674）；sens 8/25（0.320）；spec 0.970；κ 0.428 | 62/92（0.6739）；0.3200；0.9701；0.4285 | 一致 |
| rederived | 61/92（0.663）；sens 8/29（0.276）；spec 0.968；κ 0.434 | 61/92（0.6630）；0.2759；0.9683；0.4342 | 一致 |
| kept at DDInter | 34/62（0.548） | 34/62（0.5484） | 一致 |
| corrected cases | 28/30 | 28/30 | 一致 |
| uncorrected DDInter | 35/92（0.380） | 35/92 | 一致 |
| applied baselines | 0.630 / 0.535 / 0.602 | 0.6304 / 0.5348 / 0.6022 | 一致 |
| 26 excluded full | 47/66（0.712） | 47/66（0.7121） | 一致 |

### 1.3 Registry-scale（1,933 对）

| 指标 | 稿件 | 重算 | 判定 |
|---|---:|---:|---|
| matched pairs | 1,933 | 1,933 | 一致 |
| downgraded | 1,502（77.7%） | 1,502（77.70%） | 一致 |
| upgraded | 65（3.4%） | 65 | 一致 |
| high → lower | 352（34 medium / 318 low） | 352（34 / 318） | 一致 |
| medium → low | 1,150 | 1,150 | 一致 |
| low-absorption share of downgrades | 1,206（80.3%） | 1,206（80.29%） | 一致 |
| paths rule/matrix/g19/default | 504 / 507 / 746 / 176 | 504 / 507 / 746 / 176 | 一致 |
| assessed downgrades | 1,341/1,757（76.3%） | 1,341/1,757（76.32%） | 一致 |
| topical subset | 1,930；1,499 down；350 high；1,203 low-abs | 1,930；1,499；350；1,203 | 一致 |

### 1.4 Gating 敏感性（S19）

| 指标 | 稿件 | 重算 | 判定 |
|---|---:|---:|---|
| gated L1 frozen | 101/118（0.856） | 101/118 | 一致 |
| ungated L1 frozen | 103/118（0.873） | 103/118 | 一致 |
| gated corrected | 104/118（0.881） | 104/118 | 一致 |
| ungated corrected | 106/118（0.898） | 106/118 | 一致 |
| ungated downgrade / low-abs / upgrades | 1,470 / 1,174 / 133 | 1,470 / 1,174 / 133 | 一致 |

### 1.5 Development-phase

| 指标 | 稿件 | 重算 | 判定 |
|---|---:|---:|---|
| internal 78 gated | sens 0.882（15/17）；spec 0.984 | 0.8824；0.9836 | 一致 |
| internal 78 ungated | 1.000 / 0.984 | 1.0000 / 0.9836 | 一致 |
| dev 200 gated | 0.240；0.069；0.977 | 0.2400；0.0690；0.9766 | 一致 |
| external 70 | 0.443；0.077；0.935 | 0.4429；0.0769；0.9355 | 一致 |

### 1.6 Expert review

| 指标 | 稿件 | 重算 | 判定 |
|---|---:|---:|---|
| inter-rater | 11/12；κ 0.840 | 11/12；0.8400 | 一致 |
| E1 vs displayed | 2/12 | 2/12 | 一致 |
| E2 vs displayed | 1/12 | 1/12 | 一致 |
| E1 vs reference | 4/12 | 4/12 | 一致 |
| E2 vs reference | 3/12 | 3/12 | 一致 |
| lower than reference | 8/8 与 8/9 | 8/8 与 8/9 | 一致 |
| high cases rated high | 0/4；0/4 | 0/4；0/4 | 一致 |

### 1.7 RA-DDInter

| 指标 | 稿件 | 重算 | 判定 |
|---|---:|---:|---|
| 42 L1 cases: raw / RA / cascade | 17 / 21 / 32 | 17 / 21 / 32 | 一致 |
| sensitivity | 5/13；3/13；9/13 | 5/13；3/13；9/13 | 一致 |
| specificity | 17/29；28/29；29/29 | 17/29；28/29；29/29 | 一致 |
| 1,933 agree / higher / lower | 1,489 / 148 / 296 | 1,489 / 148 / 296 | 一致 |

### 1.8 Configuration 2

| 指标 | 稿件 | 重算 | 判定 |
|---|---:|---:|---|
| L1 agreement | 0.576 / 0.585 / 0.737 | 0.5763 / 0.5847 / 0.7373 | 一致 |
| L1 sensitivity | 0.250 / 0.214 / 0.536 | 0.2500 / 0.2143 / 0.5357 | 一致 |
| audit agreement | 0.609 / 0.728 / 0.674 | 0.6087 / 0.7283 / 0.6739 | 一致 |
| audit high-risk predictions | 2/92；10/92；6/92 | 2/92；10/92；6/92 | 一致 |
| no26 naive_rag | 43/66（0.652） | 43/66（0.6515） | 一致 |

### 1.9 Structure and tiers

| 指标 | 稿件 | 重算 | 判定 |
|---|---:|---:|---|
| tiers high/medium/low/very-low/minimal/none | 12/20/59/11/7/4 | 12/20/59/11/7/4 | 一致 |
| certainty measured/label/class | 13/11/89 | 13/11/89 | 一致 |
| rules / policies | 40 / 3 | 40 / 3 | 一致 |
| gated rules | nsaid_antihypertensive_antagonism | 同 | 一致 |
| matrix rows/cols/defined | 21 / 34 used（40 declared）/ 104 | 21 / 34 / 104 | 一致 |
| matrix actionable/none | 83 / 21 | 83 / 21 | 一致 |

---

## 2. 重跑中发现并已修正的前后不一致

### 2.1 Table 4 / S8 / §2.3：主分析标签分布写成了 corrected 口径

- Table 4 与 S8 的 L1 行原为 **28 high / 51 medium / 39 low**，这是 **corrected** 分布；主分析 frozen 的分布是 **28 / 50 / 40**。
- §2.3 又在一个讲 frozen-label disagreements 的句子里写“distribution: 28 high, 51 medium, 39 low”，没有说明口径。
- **修复**：Table 4 与 S8 同时列出 frozen（28/50/40）和 corrected（28/51/39）；§2.3 改为引用表，不再单写一个无口径的数字。

### 2.2 §3.7：温度敏感性区间用了 corrected 值

- 原文 0.712–0.771（SD 0.020）、0.449–0.517（SD 0.024）、0.390–0.432（SD 0.014）是 **corrected-label** 区间。
- frozen 主分析对应值为 **0.703–0.720（SD 0.006）、0.449–0.517（SD 0.026）、0.390–0.441（SD 0.017）**。
- **修复**：改为 frozen 值，并明确写“under the frozen labels”。

### 2.3 §3.1：Table 3 并不包含 “all four datasets”

- 原文说“Method performance on all four datasets is tabulated in Table 3”，但 Table 3 没有 dev200 和 external70。
- **修复**：改为“primary reference set、no-development subset、DDInter audit、configuration 2 在 Table 3；两个 development-phase sets 在 §3.2”。

### 2.4 专家原始汇总文件与 S3/扫描件矛盾

- `outputs/expert_review/expert_review_results.json` / `.md` 是旧版：R03 记为 medium、`system_v2` 与问卷不符、κ 0.846、E1/E2 vs displayed 0.417/0.333。
- 扫描件显示 R03 为 low/low；问卷实际展示 R10/R11 为 medium。
- **修复**：从 S3 逐例转录重建 JSON/MD：κ 0.840、E1/E2 vs displayed 2/12、1/12、R03 low/low、system_v2 用实际展示值。

### 2.5 MANIFEST 失效

- 原 `MANIFEST.sha256` 的 27 条哈希全部过期，并引用不存在的 `data/gold/audit_set_design.json`；`sha256sum -c` 15 项失败。
- **修复**：按当前文件重生成 27 条 manifest，`sha256sum -c` **27/27 OK**。

### 2.6 `numbers.json` 缺少 frozen 主分析

- 原文件只有 corrected 指标；frozen 101/118、0.856、κ 0.779、36/40 不在机器可读文件里。
- **修复**：新增 `l1.frozen.*`、`l1.frozen.subset.blind_frozen`、`l1.frozen.acc3_wilson/sens_wilson/kappa`，并加入口径说明。

### 2.7 Table 2 标题承诺 43 条 policy，表内只有 40 条 rule

- Table 2 caption 写“40 mechanism rules plus 3 patient-factor policies (43 policy entries)”，但 Table 2a/2b 只列 40 条 rules；3 条 patient-factor policies 缺失。
- **修复**：新增 **Table 2c**（elderly、renal impairment、polypharmacy），补充材料 S6 同步；Table 2 现在与 43 policy entries 一致。

### 2.8 Figure 1 仍写 max(L1, L2)

- 图内底部仍是旧式 **max(L1, L2)**，与正文/Figure 6 的 max(L1, L2, L3) 不一致；`figure1_architecture.csv` 还写 105 matrix cells。
- **修复**：`scripts/draw_figure1.py` 改为 max(L1, L2, L3)，source CSV 改为 104 cells；Figure 1 的 PNG/PDF/SVG/TIFF 已重新生成并嵌入主稿。

### 2.9 README 数据路径

- `data/gold/` 不存在；实际验证集在 `data/datasets/`。已修正 README。

---

## 3. 复核过程的一个审计脚本 bug（不是稿件错误）

RA-DDInter 1,933 对初次重算为 1,486/148/299，差 3 对。追查为审计脚本的 tier 选择只匹配 `systemic_absorption_*`，漏掉了 `minimal_systemic_absorption`；修正后为 **1,489/148/296**，与 Table 7 一致。稿件本身没有问题。

---

## 4. 最终状态

- `scripts/final_consistency_check.py`：**92/92 PASS**
- `scripts/audit_manuscript.py`：**0 FAIL / 2 WARN**（部分小节未被交叉引用；摘要距上限 5 词）
- `sha256sum -c MANIFEST.sha256`：**27/27 OK**
- 主稿 49 页，标红版 49 页；补充 42 页，标红版 42 页
- 摘要 346 词；正文 7,527 词；45 条参考文献
- 关键表格页面（Table 2a/2b、4、5、6，S13、S18/S18b）与回复稿分页均已视觉复核

## 5. 残留限制

1. 独立临床/临床药师裁定或盲法评审（R1 #1/#5/#9）仍未完成；稿中明确写成 limitation / future work。
2. 商业 route-aware 数据库对照（R2 #6）已完成 Lexicomp 2018（UpToDate/OpenMed 实例）对照，35 例使用 ophthalmic-specific entry，7 例 generic entry 已标注；结果见 `outputs/audits/lexicomp_route_aware_report.md` 与 Supplementary Table S18b。该实例为 2018 版，不是当前授权版本，稿中已如实披露；当前版本对照仍列为 future work。

这些属于研究设计层面的残留，不是本轮数据重跑能解决的。
