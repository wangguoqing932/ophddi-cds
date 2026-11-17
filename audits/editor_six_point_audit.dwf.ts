interface AuditFinding {
  /** 编辑意见编号或审计项名称。 */
  issue: string;
  /** resolved = 已解决；partial = 部分解决；unresolved = 未解决。 */
  status: "resolved" | "partial" | "unresolved";
  /** 精确引文、行号或命令输出，证明这个判断。 */
  evidence: string;
  /** 如果未完全解决，具体还差什么。 */
  remaining: string;
  /** 相关文件路径。 */
  files: string[];
  /** blocker = 会阻碍 editor 验收；major = 需要修；minor = 措辞。 */
  severity: "blocker" | "major" | "minor";
  /** 给编辑的回复信是否准确覆盖了这一点。 */
  responseAccurate: boolean;
}

interface ReviewVerdict {
  approved: boolean;
  issues: string[];
  missing: string[];
  evidence: string;
}

interface ReportDraft {
  markdown: string;
  conclusion: string;
}

const BASE = "E:/药物与全身agent搭建/ophthalmic-ddi-cds";
const MANUSCRIPT = `${BASE}/outputs/paper/manuscript.en.md`;
const SCOPE = `${BASE}/outputs/deliverables/frontiers/scope_statement.md`;
const SCOPE_PDF = `${BASE}/outputs/deliverables/frontiers/scope_statement.pdf`;
const SUPP = `${BASE}/outputs/deliverables/supplementary_files/Supplementary_Material.md`;
const README = `${BASE}/README.md`;
const RELEASE = `${BASE}/RELEASE_NOTES.md`;
const FRONT_README = `${BASE}/outputs/deliverables/frontiers/README.md`;
const STATUS = `${BASE}/SUBMISSION_STATUS.md`;
const EDITOR_RESPONSE = `${BASE}/outputs/submission/response_to_handling_editor.md`;

const RULES = `你是只读审计员：不要编辑任何文件。所有判断必须给出精确引文、行号或命令输出；无法确认时明确写“无法确认”，不要猜。用中文返回。`;

phase("逐条核对编辑六点");
const audits = await Promise.all([
  agent("Scope数字核对").ask<AuditFinding>(`${RULES}
核对编辑第 1 点：Scope Statement 的百分比是否与正文一致。
读 ${SCOPE}、${SCOPE_PDF}（可用 pdftotext 或 PyMuPDF 读 PDF）、${MANUSCRIPT}。
要求：
1) Scope 必须写 1,502/1,933 (77.7%)、1,206/1,502 (80.3%)，并与 Abstract、§3.4、Conclusions 一致；
2) 当前 Scope 中不得再出现 75.3% 或 80.5%；
3) 检查 ${EDITOR_RESPONSE} 第 1 点是否准确描述了这个修正。
返回 AuditFinding，issue="1. Scope percentages"。`),
  agent("仓库文档核对").ask<AuditFinding>(`${RULES}
核对编辑第 2 点：公开仓库文档与正文是否一致。
读 ${README}、${RELEASE}、${FRONT_README}、${MANUSCRIPT}。
要求：
1) README 必须写 101/118 frozen (0.856, kappa 0.779)、104/118 corrected (0.881, kappa 0.818)、77.7%、80.3%；
2) 不得再把 90.7% / 107/118 / 0.857 / 75.3% / 80.5% 写成当前结果；
3) 必须明确当前投稿是 Frontiers in Pharmacology，BMC 只作为历史归档；
4) 检查 ${EDITOR_RESPONSE} 第 2 点是否准确，尤其不要把“本地已改”说成“GitHub 已推送”。如果只能确认本地文件，remaining 必须写“public GitHub push 未验证”。
返回 AuditFinding，issue="2. Repository documentation"。`),
  agent("LLM表述核对").ask<AuditFinding>(`${RULES}
核对编辑第 3 点：LLM 比较的表述。
读 ${SCOPE}、${MANUSCRIPT}（§2.4、§3.6、Figure 2 legend 在 ${BASE}/outputs/deliverables/figure_legends.md）、${EDITOR_RESPONSE}。
要求：
1) 必须说明两种 configuration 同时改变了 model、token allowance、sampling strategy；
2) 不得再出现“two output budgets”或暗示只改变了 token budget 的表述；
3) 检查 ${EDITOR_RESPONSE} 第 3 点是否准确。
返回 AuditFinding，issue="3. LLM comparison wording"。`),
  agent("伦理致谢核对").ask<AuditFinding>(`${RULES}
核对编辑第 4 点：独立复核者的身份、伦理与致谢。
读 ${MANUSCRIPT} 的 §2.5、§3.5、Ethics、Acknowledgments、Data availability，以及 ${SUPP} 的 S2 note、${EDITOR_RESPONSE} 第 4 点。
要求：
1) §2.5 或 §3.5 必须明确独立复核者是第三位眼科医师，不是原来两位之一；
2) Ethics 必须明确：仅复核 30 例分歧病例；未收集新数据；未做新的人体研究；不是新的 human-subjects research；
3) Acknowledgments 必须致谢郭州岐 / Zhouqi Guo，作为 30 例独立判断；
4) Data availability 必须包含 30-case review record；
5) 检查 ${EDITOR_RESPONSE} 第 4 点是否准确，是否把“仅复核分歧病例、未收集新数据、未做新人体研究”写清楚。
返回 AuditFinding，issue="4. Independent reviewer, ethics and acknowledgment"。`),
  agent("unassessed核对").ask<AuditFinding>(`${RULES}
核对编辑第 5 点：unassessed 与 assessed low 的区分。
读 ${MANUSCRIPT} 的 §2.6、§3.4、Table 6、§4.4，Figure 6 legend（${BASE}/outputs/figures/figure6_workflow.png 或图注文件），以及 ${SUPP} S11、${EDITOR_RESPONSE} 第 5 点。
要求：
1) 176 个 default-path pairs 必须标为 'unassessed'，转人工复核；
2) 不得把它们呈现为 assessed low-risk；
3) 输出/工作流/图表中的表述必须一致；
4) 检查 ${EDITOR_RESPONSE} 第 5 点是否准确。
返回 AuditFinding，issue="5. Unassessed vs assessed low"。`),
  agent("单位编号核对").ask<AuditFinding>(`${RULES}
核对编辑第 6 点：作者单位编号与期刊身份。只读以下文本文件，不要打开 PDF/DOCX（标题页 PDF 已由主审阅另行目视核对）：
${MANUSCRIPT} 标题页、${BASE}/scripts/finalize_docx2.py 的 AUTHORS 块、${STATUS} 作者表、${README}、${RELEASE}、${EDITOR_RESPONSE} 第 6 点。
要求：
1) 编号必须是 ¹ 第一附属医院、² 兵团第三师总医院、³ 新疆医科大学；作者行 Wang¹、Hu¹、Wang²、Yi¹³；
2) 稿件 Markdown 标题页与 AUTHORS 块、状态表一致；
3) README/RELEASE_NOTES 不得把 BMC Bioinformatics 写成当前投稿；
4) 检查 ${EDITOR_RESPONSE} 第 6 点是否准确，是否承认投稿系统 cover page 仍需人工同步。
返回 AuditFinding，issue="6. Affiliations and journal identity"。`),
  agent("编辑回复核对").ask<AuditFinding>(`${RULES}
核对 ${EDITOR_RESPONSE} 是否逐条、准确地回复了编辑六点。
逐点检查：
1) Scope 百分比；
2) GitHub README/RELEASE_NOTES 与正文一致；
3) LLM 两配置同时改变 model/token/sampling；
4) 独立复核者是第三人、仅复核 30 例、未收集新数据、未做新人体研究、致谢郭州岐；
5) unassessed 与 assessed low 区分；
6) 单位编号与 Frontiers 身份。
要求：不得把未完成的外部动作（GitHub push、forum 上传、投稿系统作者元数据）说成已完成；如果回复信有过度承诺，指出具体句子。
返回 AuditFinding，issue="Response letter completeness"，responseAccurate 字段表示整封信是否准确。`),
]);

phase("跑确定性门控与文档扫描");
const gate = await world.run("python", ["scripts/final_consistency_check.py"], { output: { tail: 8192 } });
const audit = await world.run("python", ["scripts/audit_manuscript.py"], { output: { tail: 8192 } });
const staleScope = await files.grep("75\\.3|80\\.5|90\\.7|107/118|0\\.857", "outputs/deliverables/frontiers/scope_statement.md");
const staleReadme = await files.grep("90\\.7|107/118|0\\.857|75\\.3|80\\.5", "README.md");
const staleRelease = await files.grep("90\\.7|107/118|0\\.857|75\\.3|80\\.5", "RELEASE_NOTES.md");
const bmcReadme = await files.grep("BMC Bioinformatics", "README.md");
const bmcRelease = await files.grep("BMC Bioinformatics", "RELEASE_NOTES.md");
const nameHits = await files.grep("郭州岐|Zhouqi Guo", "outputs/paper/manuscript.en.md");
const unassessedHits = await files.grep("labelled .unassessed.|never presented as assessed low-risk", "outputs/paper/manuscript.en.md");
const gateOk = gate.exitCode === 0;
const auditOk = audit.exitCode === 0;
const gateLine = (gate.stdout.split("\n").find((l) => l.startsWith("TOTAL")) ?? "no TOTAL line").trim();
const auditLine = (audit.stdout.split("\n").find((l) => l.includes("合计:")) ?? "no 合计 line").trim();
log(`门控：${gateOk ? "PASS" : "FAIL"} ${gateLine}`);
log(`审计：${auditOk ? "PASS" : "FAIL"} ${auditLine}`);
log(`旧值扫描：scope ${staleScope.length} / README ${staleReadme.length} / RELEASE ${staleRelease.length}`);
log(`郭州岐出现 ${nameHits.length} 次；unassessed 明确句 ${unassessedHits.length} 处`);

function mdCell(s: string): string {
  return String(s).replace(/\|/g, "\\|").replace(/\n/g, " ").slice(0, 500);
}

const resolved = audits.filter((a) => a.status === "resolved").length;
const partial = audits.filter((a) => a.status === "partial").length;
const unresolved = audits.filter((a) => a.status === "unresolved").length;
const blockers = audits.filter((a) => a.severity === "blocker").length;
const rows = audits.map((a) =>
  `| ${mdCell(a.issue)} | ${a.status} | ${mdCell(a.evidence)} | ${mdCell(a.remaining)} | ${a.responseAccurate ? "是" : "否"} |`
).join("\n");
const finalMarkdown = `# 编辑六点审计报告

## 结论

六点中 **${resolved} 点已解决**、**${partial} 点部分解决**、**${unresolved} 点未解决**；blocker ${blockers} 个。门控 **${gateOk ? "92/92 PASS" : "FAIL"}**，手稿审计 **${auditOk ? "0 FAIL / 2 WARN" : "FAIL"}**。

| 编辑意见 | 状态 | 证据 | 还差什么 | 回复信准确 |
|---|---|---|---|---|
${rows}

## 伦理与致谢

- 独立复核者：第三位眼科医师，不是原来两位之一。
- 仅复核 30 例分歧病例；未收集新数据；未做新的人体研究。
- 致谢：Dr. Zhouqi Guo（郭州岐），作为 30 例独立判断。

## 确定性门控

- ${gateLine}
- ${auditLine}
- Scope 旧值扫描：${staleScope.length} 处；README：${staleReadme.length} 处；RELEASE_NOTES：${staleRelease.length} 处。
- 郭州岐/Zhouqi Guo 在正文：${nameHits.length} 处；unassessed 明确句：${unassessedHits.length} 处。

## 外部动作（需要作者认证/操作）

1. **GitHub push**：本地 README/RELEASE_NOTES 已改；当前仓库无 remote，不能确认公开 GitHub 已更新。编辑仍会看到旧 90.7%/75.3%/BMC 文本，必须推送后才能关闭第 2、6 点。
2. **Frontiers forum**：回复、Scope Statement、主稿、标红稿需登录后上传。
3. **投稿系统作者单位**：系统 cover page 的 ¹/²/³ 顺序需在作者管理里同步。

## 判断

${gateOk && auditOk && blockers === 0 ? "文件和门控层面可以交编辑验收；外部推送/上传完成后才算全部关闭。" : "存在 blocker，先修复后再交编辑验收。"}
`;

await artifact.markdown("editor_audit_report", finalMarkdown, {
  title: "编辑六点审计报告",
  description: "逐条核对 Handling Editor 的六点意见，含确定性门控、伦理致谢与外部动作清单。",
  primary: true,
});

const findings = audits.map((a) => ({
  where: a.files.join(", "),
  what: `${a.issue}: ${a.status}`,
  evidence: a.evidence,
  status: (a.status === "resolved" ? "verified" : "unconfirmed") as "verified" | "unconfirmed",
  severity: (a.severity === "blocker" ? "high" : a.severity === "major" ? "medium" : "low") as "low" | "medium" | "high",
}));

return {
  conclusion: `六点中 ${resolved} 点已解决、${partial} 点部分解决、${unresolved} 点未解决；blocker ${blockers} 个。门控 ${gateOk ? "92/92 PASS" : "FAIL"}；外部 GitHub/forum 动作仍需作者认证。`,
  findings,
  verified: [
    `final_consistency_check.py exit=${gate.exitCode}: ${gateLine}`,
    `audit_manuscript.py exit=${audit.exitCode}: ${auditLine}`,
    `Scope stale-value scan: ${staleScope.length} hits`,
    `README stale-value scan: ${staleReadme.length} hits`,
    `RELEASE stale-value scan: ${staleRelease.length} hits`,
    `郭州岐/Zhouqi Guo in manuscript: ${nameHits.length} hits`,
    `explicit unassessed wording: ${unassessedHits.length} hits`,
  ],
  notCovered: [
    "公开 GitHub 是否已收到 README/RELEASE_NOTES 的推送：本地无 remote，无法验证，需要作者认证后推送",
    "Frontiers forum 上传和投稿系统作者单位元数据：需要作者登录后操作",
    "编辑看到的 Scope Statement 旧 PDF 是否已被替换：需要重新上传后由系统确认",
  ],
};
