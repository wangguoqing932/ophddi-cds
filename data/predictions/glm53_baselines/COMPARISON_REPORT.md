# 基线重跑对比分析报告

**日期**：2026-09-24
**目的**：回应 Reviewer 1 意见 5（"与 LLM 基线的比较不能支撑其结论"）
**状态**：数据已完成，**尚未并入论文**，等待决策

---

## 1. 审稿人的原始批评

> The Methods cap baseline output at 10 tokens, use a single non-reasoning model, parse by
> substring, and describe a baseline named lightrag that does not query the LightRAG index.
> A 10-token cap removes any possibility of reasoning or justification and turns the task into
> a forced one-word answer; two of the three baselines then perform at or near a constant-response
> classifier. **Nothing in the paper's comparison therefore licenses a statement about LLM
> capability in this domain.**

**他们提出的四项改进**：① 用当前推理模型；② 充足输出预算；③ 固定温度下重复采样（而非每个条件调一次温度）；④ 预先规定解析规则。

---

## 2. 本次执行

| 项目 | 原设置（论文中） | 本次设置 |
|---|---|---|
| 模型 | `deepseek-chat`（非推理） | **`glm-5.3-flash`（推理模型）** |
| 输出上限 | **10 tokens** | **3000 tokens** |
| 采样 | 每个温度条件跑 1 次，温度递增 0→1.2 | **固定温度 0.0，每例重复 5 次，取多数票** |
| 解析 | 子串匹配 | **预先规定的规则**（整体匹配 → high > medium > low 子串 → unknown） |
| 数据集 | 4 个 | **L1 118 例 + 审计集 92 例**（两个核心验证集） |
| 调用量 | — | **3,150 次**（210 例 × 3 方法 × 5 次） |
| 质量 | — | **0 错误、0 unknown**；推理 token 中位 262、最大 1855；单次中位 7.2 秒 |

prompt 与原始评估**逐字一致**（system prompt、BM25 参数、三种 user prompt 模板），保证可比性。

**聚合方式**：主表使用**5 次采样的多数票**（预先规定）。逐次指标另附，用于评估稳定性。

### 2.1 逐次稳定性（Acc3）

| 数据集 | 方法 | rep0 | rep1 | rep2 | rep3 | rep4 | 均值 | SD |
|---|---|---|---|---|---|---|---|---|
| L1 118例 | pure_llm | 0.525 | 0.585 | 0.508 | 0.559 | 0.576 | 0.551 | 0.029 |
| | naive_rag | 0.551 | 0.585 | 0.602 | 0.593 | 0.551 | 0.576 | 0.021 |
| | lightrag | 0.737 | 0.746 | 0.737 | 0.720 | 0.703 | 0.729 | 0.015 |
| 审计集 92例 | pure_llm | 0.609 | 0.641 | 0.641 | 0.620 | 0.620 | 0.626 | 0.013 |
| | naive_rag | 0.674 | 0.717 | 0.696 | 0.652 | 0.750 | 0.698 | 0.034 |
| | lightrag | 0.652 | 0.696 | 0.641 | 0.663 | 0.674 | 0.665 | 0.019 |

**要点**：即使在温度 0.0 下，逐次 Acc3 仍有 0.013–0.034 的波动（推理模型固有的路径随机性），**因此单次调用不可靠，重复采样是必要的**——这印证了审稿人第③条的合理性。系统本身 SD = 0。

---

## 3. 结果对比

### 3.1 L1 118 例

| 方法 | Acc3（原） | Acc3（新） | 敏感性（原） | 敏感性（新） | 特异性（原） | 特异性（新） | kappa（新） |
|---|---|---|---|---|---|---|---|
| pure_llm | 0.475 | **0.576** | 0.771 | **0.250** | 0.542 | **1.000** | 0.333 |
| naive_rag | 0.415 | **0.585** | 0.757 | **0.214** | 0.462 | **0.989** | 0.341 |
| lightrag | 0.737 | 0.737 | 0.779 | **0.536** | 0.936 | **1.000** | 0.587 |
| **full_system** | **0.907** | — | **0.964** | — | 0.989 | — | **0.857** |

### 3.2 审计集 92 例

| 方法 | Acc3（原） | Acc3（新） | 敏感性（原） | 敏感性（新） | 特异性（原） | 特异性（新） | kappa（新） |
|---|---|---|---|---|---|---|---|
| pure_llm | 0.630 | 0.609 | 0.848 | **0.080** | 0.704 | **1.000** | 0.317 |
| naive_rag | 0.535 | **0.728** | 0.848 | **0.400** | 0.579 | **1.000** | 0.553 |
| lightrag | 0.591 | 0.674 | 0.264 | 0.240 | 0.949 | **1.000** | 0.428 |
| **full_system** | 0.674 | — | 0.320 | — | 0.955 | — | 0.428 |

---

## 4. 三个必须理解的机制

### 4.1 敏感性暴跌、特异性接近 1.000：基线变成了"极少报警"的分类器

这是本次最重要的发现。预测分布对比：

| 数据集 | 方法 | 判 high | 判 medium | 判 low |
|---|---|---|---|---|
| L1（gold：24% high） | pure_llm | **6%** | 39% | **55%** |
| | naive_rag | **6%** | 44% | 50% |
| | lightrag | 13% | 44% | 43% |
| 审计集（gold：27% high） | pure_llm | **2%** | 28% | **70%** |
| | naive_rag | 11% | 33% | 57% |
| | lightrag | **7%** | 24% | **70%** |

**判高风险的绝对数**：

| | L1（gold 高风险 28 例） | 审计集（gold 高风险 25 例） |
|---|---|---|
| pure_llm | 判 7 例 | 判 **2** 例 |
| naive_rag | 判 7 例 | 判 10 例 |
| lightrag | 判 15 例 | 判 6 例 |
| **full_system** | 判 **28 例** | 判 8 例 |

**机制**：放开采 token 预算后，推理模型的推理链倾向于得出"证据不足→风险较低"的结论，系统性压低分级。因为 L1 的 gold 有 76% 是 low/medium，**把大多数案例判为低风险反而提高了 Acc3**——但代价是几乎识别不出任何高风险案例。特异性随之升到 1.000（仅 L1 的 naive_rag 为 0.989）。

**临床含义**：Acc3 上升是**分布偏移的副产品**，不是判断能力提升。对筛查工具而言，敏感性才是关键指标，而基线在这个指标上**从 0.757–0.848 跌到 0.080–0.536**。

### 4.2 "BM25 检索引入噪声"的论断不成立

论文现有表述（§3.3 与 §4.2）：

> naive keyword retrieval (BM25) degraded accuracy below the plain-LLM baseline in this domain

| 数据集 | pure_llm | naive_rag | 差值 |
|---|---|---|---|
| L1（新） | 0.576 | 0.585 | **+0.009**（反超） |
| 审计集（新） | 0.609 | **0.728** | **+0.119**（大幅反超） |

**新设置下 naive_rag 在两个数据集上都不低于 pure_llm**，审计集上还大幅领先。原结论（0.475 > 0.415；0.630 > 0.535）是 **10-token 限制的产物**——预算受限时，检索注入的长 context 挤占了本就极少的输出空间。

**必须删除或改写这个论断。**

### 4.3 审计集上 naive_rag 在 Acc3 与敏感性上都高于系统

| 方法 | Acc3 | 敏感性 | TP/高风险 | kappa |
|---|---|---|---|---|
| **naive_rag** | **0.728** | **0.400** | 10/25 | 0.553 |
| lightrag | 0.674 | 0.240 | 6/25 | 0.428 |
| full_system | 0.674 | 0.320 | 8/25 | 0.428 |
| pure_llm | 0.609 | 0.080 | 2/25 | 0.317 |

这是**对论文最不利**的结果。无法用"分布偏移"解释，因为 naive_rag 在这个数据集上**两项指标都领先**。

**但敏感性不稳健**（逐次值）：

| | rep0 | rep1 | rep2 | rep3 | rep4 | 多数票 |
|---|---|---|---|---|---|---|
| naive_rag | 0.320 | 0.400 | 0.480 | **0.280** | 0.440 | 0.400 |
| full_system | 0.320 | 0.320 | 0.320 | 0.320 | 0.320 | 0.320 |

5 次中 3 次高于系统、1 次持平、1 次低于。**方向偏向 naive_rag，但不是压倒性的**——这与 Acc3 的差距（0.728 vs 0.674）相比更不稳定。

**诚实表述建议**：承认在审计集上 naive_rag 的 Acc3 更高，但指出（a）其敏感性在逐次间不稳定（0.280–0.480），(b) 该数据集的 gold 有 30/92 例由系统自身假设校正，因此这个比较本身不是独立的（论文已有此披露）。

---

## 5. 对论文的净影响

### 5.1 不利（必须改）

| # | 影响 | 涉及位置 |
|---|---|---|
| 1 | **"BM25 引入噪声"论断失效** | §3.3、§4.2、摘要（"naive_rag degraded accuracy"） |
| 2 | **审计集上系统不再是 Acc3 最优** | §3.5、§4.1、摘要、Table 3、Figure 2、Table S7 |
| 3 | 基线绝对值提高，系统相对优势（倍数）缩小 | 全文多处 |
| 4 | 审计集系统的 kappa（0.428）低于 naive_rag（0.553） | §3.5、§4.1 |

### 5.2 有利（可强化）

| # | 影响 | 说明 |
|---|---|---|
| 1 | **系统在 L1 上的高风险敏感性优势变为压倒性** | 0.964 vs 0.214–0.536（原为 0.964 vs 0.771–0.779） |
| 2 | **审稿人的批评被证实部分成立，但我们主动发现并报告** | 这是科学诚信的加分项 |
| 3 | **L1 上结论方向不变** | 系统 Acc3（0.907）与敏感性（0.964）均遥遥领先 |
| 4 | **"确定性"价值更突出** | 新基线 SD 0.013–0.034，系统 SD=0 |
| 5 | 推理模型的"保守偏好"本身是有价值的发现 | 说明通用 LLM 在缺乏机制证据时倾向低估，这正是论文所论证的"需要专门知识工程" |

**注意**：审计集上系统**不占优**（naive_rag 在 Acc3 与敏感性上都更高），因此第 1 条的"压倒性优势"**只适用于 L1**，不能推广到两个数据集。

### 5.3 关键判断

**审稿人的批评成立，但成立的后果与他们预期相反。** 他们担心 10-token 压制了基线、使比较不公平；实测发现**放开预算后基线在临床关键指标（敏感性）上更差**，因为它们退化为"从不报警"的保守分类器。

这**不意味着不需要改**——恰恰相反，我们需要：
- 保留两套设置（体现透明性与审稿人意见的采纳）
- 重新定位论述重心：从"Acc3 全面领先"转向"**高风险敏感性 + 确定性 + 可审计性**"
- 删除不成立的论断（BM25 噪声、审计集 Acc3 最优）

---

## 6. 建议的论文修改方案

### 6.1 新增一个结果小节（建议 §3.6 或 §3.5 后半）

如实报告本次重跑：

> **Reasoning-model baselines under an adequate output budget.** To address the concern that
> a 10-token cap may have suppressed baseline performance, we re-ran all three LLM baselines
> with a reasoning model (glm-5.3-flash), a 3000-token budget, and five repeated samples at
> fixed temperature, with a pre-specified parsing rule. Exact accuracy rose (pure_llm 0.475→0.576;
> naive_rag 0.415→0.585 on L1) but **high-risk sensitivity fell sharply** (0.771→0.250 and
> 0.757→0.214), and specificity reached 1.000: given a larger budget, the baselines converge on
> a conservative "rarely high-risk" policy that inflates exact accuracy on a gold set dominated
> by low and medium grades while failing to flag almost any of the 28 gold-high cases.
> The deterministic cascade retains 0.964 sensitivity. We report both settings rather than
> replacing one with the other.

### 6.2 需要删除/改写的现有表述

| 位置 | 现有表述 | 建议改为 |
|---|---|---|
| §3.3 | "Naive BM25 retrieval was consistently worse than the plain-LLM baseline, indicating that keyword retrieval injects noise" | "Under the 10-token setting BM25 retrieval scored below the plain-LLM baseline; **under an adequate output budget the ordering reverses** (0.585 vs 0.576 on L1), so we no longer attribute the earlier gap to retrieval noise." |
| §3.5 | "the system led all methods on exact accuracy (0.707 versus 0.535–0.630)" | 补充：在充分预算对照下 naive_rag 达到 0.728，**高于系统的 0.674**；系统的优势在敏感性与特异性，不在审计集的 Acc3 |
| §4.1 | "outperformed three LLM baselines (0.415–0.741 accuracy)" | 说明两套设置下的范围，并突出敏感性对比 |
| 摘要 | 相关表述 | 改为突出敏感性 + 确定性，弱化 Acc3 倍数 |

### 6.3 图表

- **Figure 2**：建议改为**两面板**（原设置 / 充分预算），或保留现图并新增一图。推荐前者，直观展示"预算放开后敏感性下降"。
- **Table 3 / Table S7**：增加"设置"列，并列两套数字。

### 6.4 回复信要点

1. **采纳批评**：承认 10-token 上限确实压制了基线（Acc3 印证：pure_llm 0.475→0.576，naive_rag 0.415→0.585）
2. **执行四项改进**：推理模型、3000 token、5 次重复采样、预定解析规则
3. **如实报告意外结果**：敏感性暴跌（0.771→0.250；0.757→0.214）、特异性接近 1.000、基线退化为"极少报警"的保守分类器；逐次波动 0.013–0.034 印证重复采样的必要性
4. **主动披露不利结果**：审计集上 naive_rag 的 Acc3（0.728）与敏感性（0.400）均高于系统（0.674/0.320）
5. **删除不成立的论断**：BM25 引入噪声（两套设置下顺序相反）
6. **结论**：L1 上系统的优势在提高输出预算后**更强**（敏感性 0.964 vs 0.214–0.536）；审计集上系统不占优，已在正文如实说明；系统价值定位应转向**敏感性 + 确定性 + 可审计性**，而非 Acc3 全面领先

---

## 7. 需要你决定的四件事

| # | 决策 | 选项 |
|---|---|---|
| 1 | **是否并入论文** | A. 并入为独立小节 + 两套并列（推荐）<br>B. 只更新回复信、不改论文<br>C. 并入但只报告新设置 |
| 2 | **"BM25 引入噪声"论断** | 必须删除。是否接受改为"两套设置下顺序相反"？ |
| 3 | **审计集 naive_rag 更高** | 如实写入正文，还是仅在补充材料披露？（建议正文，避免被审稿人二次发现） |
| 4 | **Figure 2 处理** | 两面板，还是新增一张图？ |

---

## 8. 附：数据文件位置

| 文件 | 内容 |
|---|---|
| `outputs/glm53_baselines/predictions.jsonl` | 3,150 次原始调用记录（含 usage、耗时、推理 token） |
| `outputs/glm53_baselines/metrics.json` | 逐次指标 + 多数票指标 |
| `scripts/rerun_glm53_baselines.py` | 重跑脚本（支持断点续跑、截断行容错、flush+fsync） |
| `scripts/probe_glm53.py` | 端点与参数探测脚本 |

**可复现性**：脚本按 `(dataset, method, case_id, rep)` 去重续跑，进程中断后重跑同一命令即可从中断处继续，已完成调用不重复、不丢失。
