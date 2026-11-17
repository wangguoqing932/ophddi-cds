# -*- coding: utf-8 -*-
"""build_r1_5_review_form.py — build the offline 30-case review form.

Reads the blinded CSV (no author classes) and writes a single self-contained
HTML file. The reviewer can open it in any browser, fill the 30 cases, and
export a CSV that `analyze_independent_review.py` reads directly.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PACKET = ROOT / "outputs" / "audits" / "r1_5_independent_review"
SRC = PACKET / "cases_blinded.csv"
OUT = PACKET / "review_form.html"

TIER_ZH = {
    "systemic_absorption_high": "高",
    "systemic_absorption_medium": "中",
    "systemic_absorption_low": "低",
    "systemic_absorption_very_low": "很低",
    "minimal_systemic_absorption": "极低",
    "no_systemic_absorption": "无",
}
LEVEL_ZH = {"high": "高", "medium": "中", "low": "低"}
NAME_ZH = {
    "Aflibercept": "阿柏西普", "Apraclonidine": "安普乐定", "Betaxolol": "倍他洛尔",
    "Bromfenac": "溴芬酸", "Carteolol": "卡替洛尔", "Dexamethasone": "地塞米松",
    "Flurbiprofen": "氟比洛芬", "Homatropine": "后马托品", "Phenylephrine": "去氧肾上腺素",
    "Prednisolone": "泼尼松龙", "Scopolamine": "东莨菪碱", "Tacrolimus": "他克莫司",
    "Timolol": "噻吗洛尔", "Apixaban": "阿哌沙班", "Azathioprine": "硫唑嘌呤",
    "Captopril": "卡托普利", "Clonidine": "可乐定", "Desmopressin": "去氨加压素",
    "Diazepam": "地西泮", "Diltiazem": "地尔硫卓", "Doxazosin": "多沙唑嗪",
    "Enalapril": "依那普利", "Epinephrine": "肾上腺素", "Fluvoxamine": "氟伏沙明",
    "Ibuprofen": "布洛芬", "Leflunomide": "来氟米特", "Levothyroxine": "左甲状腺素",
    "Linezolid": "利奈唑胺", "Loperamide": "洛哌丁胺", "Methotrexate": "甲氨蝶呤",
    "Midazolam": "咪达唑仑", "Perindopril": "培哚普利", "Prasugrel": "普拉格雷",
    "Rivaroxaban": "利伐沙班", "Spironolactone": "螺内酯", "Telmisartan": "替米沙坦",
    "Theophylline": "茶碱", "Topiramate": "托吡酯", "Verapamil": "维拉帕米",
}


def main() -> None:
    with SRC.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    cases = []
    for i, r in enumerate(rows, 1):
        tier = TIER_ZH.get(r["absorption_tier"], r["absorption_tier"])
        cases.append({
            "n": i,
            "case_id": r["case_id"],
            "ophthalmic": r["ophthalmic"],
            "ophthalmic_zh": NAME_ZH.get(r["ophthalmic"], r["ophthalmic"]),
            "systemic": r["systemic"],
            "systemic_zh": NAME_ZH.get(r["systemic"], r["systemic"]),
            "reference": r["reference_label"],
            "reference_zh": LEVEL_ZH.get(r["reference_label"], r["reference_label"]),
            "system": r["system_grade"],
            "system_zh": LEVEL_ZH.get(r["system_grade"], r["system_grade"]),
            "tier": r["absorption_tier"],
            "tier_zh": tier,
            "direction": r["direction"],
        })
    data = json.dumps(cases, ensure_ascii=False, indent=1)
    html = TEMPLATE.replace("__CASES__", data)
    OUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({OUT.stat().st_size/1024:.0f} KB, {len(cases)} cases)")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>30 例独立复核表 · OphDDI-CDS</title>
<style>
  :root{
    --navy:#16324F; --blue:#2F6690; --ink:#1F2933;
    --muted:#5B6B7B; --line:#D8E1E9; --bg:#F5F7FA; --card:#FFFFFF;
    --green:#2E7D5B; --amber:#A66A12; --red:#A63A3A; --soft:#EEF3F8;
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{margin:0;background:var(--bg);color:var(--ink);
       font-family:"Microsoft YaHei","PingFang SC","Segoe UI",Arial,sans-serif;
       font-size:15px;line-height:1.65}
  h1,h2,h3{font-family:"Times New Roman","Songti SC","SimSun",serif;color:var(--navy);margin:0}
  header{background:var(--navy);color:#fff;padding:26px 20px 22px}
  .wrap{max-width:820px;margin:0 auto}
  .kicker{font-size:12px;letter-spacing:.08em;color:#BFD4E6}
  h1{color:#fff;font-size:28px;line-height:1.3;margin:6px 0 6px}
  header p{margin:0;color:#DCE8F2;font-size:14px;max-width:700px}
  main{max-width:820px;margin:0 auto;padding:18px 14px 48px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:10px;
        padding:16px 18px;margin:14px 0}
  .intro h2{font-size:20px;margin-bottom:6px}
  .intro p{margin:0 0 8px;color:#33475B;font-size:14px}
  .intro p.small{color:var(--muted);font-size:13px}
  .who{margin-top:8px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
  .who label{font-size:13px;color:var(--muted)}
  .who input{border:1px solid var(--line);border-radius:7px;padding:6px 9px;
             font:inherit;font-size:14px;min-width:180px}
  .sticky{position:sticky;top:0;z-index:20;background:rgba(245,247,250,.96);
          backdrop-filter:blur(6px);padding:8px 0 9px;border-bottom:1px solid var(--line)}
  .bar{height:8px;background:#DCE6EF;border-radius:20px;overflow:hidden}
  .bar i{display:block;height:100%;width:0;background:var(--blue);transition:width .2s ease}
  .bar-meta{display:flex;justify-content:space-between;font-size:12.5px;color:var(--muted);
            margin-top:4px}
  .case{background:var(--card);border:1px solid var(--line);border-radius:10px;
        padding:15px 17px;margin:10px 0}
  .case-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px;margin-bottom:7px}
  .idx{font-family:"Consolas",monospace;font-size:12px;color:#fff;background:var(--navy);
       padding:1px 6px;border-radius:4px}
  .case h3{font-size:18px;margin:0}
  .dir{font-size:12px;font-weight:700;padding:1px 8px;border-radius:999px;border:1px solid}
  .dir.downgrade{color:#7A4E0B;background:#FDF3DF;border-color:#E7C98B}
  .dir.upgrade{color:#1F5C44;background:#E4F3EC;border-color:#A9D3C1}
  .scene{background:#F7FAFD;border-left:3px solid var(--blue);padding:7px 10px;
         border-radius:0 6px 6px 0;font-size:13.5px;color:#33475B;margin:6px 0 9px}
  .scene b{color:var(--navy)}
  .facts{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin:7px 0 11px}
  @media(max-width:600px){.facts{grid-template-columns:1fr 1fr}}
  .fact{background:var(--soft);border-radius:7px;padding:6px 9px}
  .fact span{display:block;font-size:11.5px;color:var(--muted)}
  .fact b{font-size:15px;color:var(--navy)}
  .choices{display:grid;gap:6px;margin:6px 0}
  .choice{display:flex;gap:8px;align-items:flex-start;border:1px solid var(--line);
          border-radius:7px;padding:7px 9px;cursor:pointer;background:#fff}
  .choice:hover{border-color:#A9C1D6;background:#F8FBFD}
  .choice:has(input:checked){border-color:var(--blue);background:#EDF5FB}
  .choice input{margin-top:4px;width:16px;height:16px;accent-color:var(--blue)}
  .choice b{font-weight:600;color:var(--navy);font-size:14px}
  .row{display:flex;gap:8px;flex-wrap:wrap;margin-top:7px}
  .row textarea{flex:1 1 380px;min-height:42px;border:1px solid var(--line);border-radius:7px;
                padding:7px 9px;font:inherit;font-size:13.5px;resize:vertical;background:#fff}
  .row select{border:1px solid var(--line);border-radius:7px;padding:7px 9px;font:inherit;
              font-size:13.5px;background:#fff;color:var(--ink)}
  .submit{background:var(--card);border:1px solid var(--line);border-radius:10px;
          padding:16px 18px;margin-top:14px}
  .submit h2{font-size:20px;margin-bottom:4px}
  .submit p{margin:0 0 8px;font-size:13.5px;color:var(--muted)}
  .buttons{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}
  button{border:0;border-radius:7px;padding:9px 14px;font:inherit;font-size:14px;
         cursor:pointer;background:var(--navy);color:#fff}
  button.secondary{background:#fff;color:var(--navy);border:1px solid #B9CBD9}
  button.danger{background:#fff;color:var(--red);border:1px solid #E0B4B4}
  button:hover{filter:brightness(1.05)}
  #status{font-size:13px;color:var(--muted);min-height:1.3em;margin:4px 0 0}
  #status.err{color:var(--red);font-weight:600}
  footer{border-top:1px solid var(--line);color:var(--muted);font-size:12px;
         padding:14px;text-align:center}
  @media print{
    body{background:#fff;font-size:11pt}
    header{background:#fff;color:#000;border-bottom:2px solid #000}
    header h1{color:#000}.kicker,.sticky,.buttons,#status{display:none}
    .card,.case{break-inside:avoid}
  }
</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="kicker">OphDDI-CDS · 独立复核</div>
    <h1>眼科—全身药物相互作用分级复核</h1>
    <p>共 30 例。请判断系统给出的分级是否合理；判断不了就选“无法判断”。匿名复核，不涉及患者数据。</p>
  </div>
</header>

<main>
  <section class="card intro">
    <h2>怎么填</h2>
    <p>每例选一个分类，填完点“导出结果”，把 CSV 发回。网页不联网，填写只保存在本机。</p>
    <p class="small">每一例都设想同一位患者：一种药为眼科局部用药，另一种为全身用药。系统给出风险分级，DDInter 给出参考分级；请判断系统分级是否合理。</p>
    <p class="small">“参考分级”是 DDInter 的分级；“系统分级”是被评估系统的分级。两者不一致的病例才在表中。</p>
    <p class="small"><b>DDInter 分级：</b>严重（Major）= 高；中等（Moderate）= 中；轻微（Minor）= 低。DDInter 是外部公共数据库，其分级不是临床金标准。</p>
    <div class="who">
      <label for="reviewer">姓名缩写（可选）</label>
      <input id="reviewer" autocomplete="off" placeholder="例如：ZYH">
    </div>
  </section>

  <div class="sticky">
    <div class="bar"><i id="bar"></i></div>
    <div class="bar-meta"><span id="count">已填 0 / 30</span><span id="saved">未保存</span></div>
  </div>

  <section id="cases"></section>

  <section class="submit">
    <h2>提交</h2>
    <p>确认 30 例都选了分类，然后导出 CSV 发回。</p>
    <div class="buttons">
      <button id="export">导出结果（CSV）</button>
      <button id="print" class="secondary">打印 / 存 PDF</button>
      <button id="clear" class="danger">清空</button>
    </div>
    <p id="status"></p>
  </section>
</main>
<footer>OphDDI-CDS · 30 例独立复核 · 本页不上传任何内容</footer>

<script>
const CASES = __CASES__;
const KEY = "oddcds_r15_review_v2";
const LABEL = {
  route_consistent_downgrade: "与局部吸收有限一致",
  unsupported_undergrading: "缺乏依据的降级",
  system_overgrading: "缺乏依据的升级",
  supported_upgrade: "有依据的升级",
  uncertain: "无法判断"
};
const OPTIONS = {
  downgrade: ["route_consistent_downgrade", "unsupported_undergrading", "uncertain"],
  upgrade: ["system_overgrading", "supported_upgrade", "uncertain"]
};
const casesEl = document.getElementById("cases");
const bar = document.getElementById("bar");
const countEl = document.getElementById("count");
const savedEl = document.getElementById("saved");
const statusEl = document.getElementById("status");
const reviewerEl = document.getElementById("reviewer");
let state = {};

function esc(s){return String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}

function render(){
  casesEl.innerHTML = CASES.map(c => {
    const opts = OPTIONS[c.direction].map(v =>
      `<label class="choice"><input type="radio" name="cls-${c.case_id}" value="${v}">
        <span><b>${LABEL[v]}</b></span></label>`).join("");
    return `<article class="case" id="case-${c.case_id}">
      <div class="case-head"><span class="idx">${String(c.n).padStart(2,"0")}</span>
        <h3>${esc(c.ophthalmic_zh)} + ${esc(c.systemic_zh)}</h3>
        <span class="dir ${c.direction}">${c.direction === "downgrade" ? "降级" : "升级"}</span></div>
      <div class="scene"><b>场景：</b>患者同时使用「<b>${esc(c.ophthalmic_zh)}</b>」（眼科局部用药）与「<b>${esc(c.systemic_zh)}</b>」（全身用药），两者可能存在相互作用。</div>
      <div class="facts">
        <div class="fact"><span>参考分级</span><b>${esc(c.reference_zh)}</b></div>
        <div class="fact"><span>系统分级</span><b>${esc(c.system_zh)}</b></div>
        <div class="fact"><span>吸收等级</span><b>${esc(c.tier_zh)}</b></div>
      </div>
      <div class="choices">${opts}</div>
      <div class="row">
        <textarea data-reason="${c.case_id}" placeholder="理由（可选）"></textarea>
        <select data-confidence="${c.case_id}">
          <option value="">置信度（可选）</option>
          <option value="high">高</option>
          <option value="medium">中</option>
          <option value="low">低</option>
        </select>
      </div>
    </article>`;
  }).join("");
  bind();
  restore();
  updateProgress();
}

function bind(){
  document.querySelectorAll('input[type="radio"]').forEach(r => {
    r.addEventListener("change", () => {
      const id = r.name.replace("cls-","");
      state[id] = state[id] || {};
      state[id].cls = r.value;
      save(); updateProgress();
    });
  });
  document.querySelectorAll("textarea[data-reason]").forEach(t => {
    t.addEventListener("input", () => {
      const id = t.dataset.reason;
      state[id] = state[id] || {};
      state[id].reason = t.value;
      save();
    });
  });
  document.querySelectorAll("select[data-confidence]").forEach(s => {
    s.addEventListener("change", () => {
      const id = s.dataset.confidence;
      state[id] = state[id] || {};
      state[id].confidence = s.value;
      save();
    });
  });
  reviewerEl.addEventListener("input", save);
}

function save(){
  try{
    localStorage.setItem(KEY, JSON.stringify({reviewer: reviewerEl.value, answers: state}));
    savedEl.textContent = "已自动保存";
  }catch(e){ savedEl.textContent = "请及时导出"; }
}

function restore(){
  let data = null;
  try{ data = JSON.parse(localStorage.getItem(KEY) || "null"); }catch(e){}
  if(!data) return;
  if(data.reviewer) reviewerEl.value = data.reviewer;
  state = data.answers || {};
  Object.entries(state).forEach(([id,v]) => {
    if(v.cls){
      const r = document.querySelector(`input[name="cls-${id}"][value="${v.cls}"]`);
      if(r) r.checked = true;
    }
    const t = document.querySelector(`textarea[data-reason="${id}"]`);
    if(t && v.reason) t.value = v.reason;
    const s = document.querySelector(`select[data-confidence="${id}"]`);
    if(s && v.confidence) s.value = v.confidence;
  });
  savedEl.textContent = "已恢复上次填写";
}

function updateProgress(){
  const done = CASES.filter(c => state[c.case_id] && state[c.case_id].cls).length;
  bar.style.width = Math.round(done * 100 / CASES.length) + "%";
  countEl.textContent = `已填 ${done} / ${CASES.length}`;
}

function csvCell(v){
  const s = String(v == null ? "" : v);
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

function exportCsv(){
  const missing = CASES.filter(c => !(state[c.case_id] && state[c.case_id].cls));
  if(missing.length){
    statusEl.className = "err";
    statusEl.textContent = `还有 ${missing.length} 例未选：` + missing.map(c => c.case_id).join("、");
    document.getElementById(`case-${missing[0].case_id}`).scrollIntoView({behavior:"smooth", block:"center"});
    return;
  }
  const header = ["case_id","ophthalmic","systemic","reference_label","system_grade",
                  "absorption_tier","direction","your_class","your_reason","confidence","reviewer_code"];
  const lines = [header.join(",")];
  CASES.forEach(c => {
    const a = state[c.case_id] || {};
    lines.push([
      c.case_id, c.ophthalmic, c.systemic, c.reference, c.system, c.tier, c.direction,
      a.cls || "", a.reason || "", a.confidence || "", reviewerEl.value || ""
    ].map(csvCell).join(","));
  });
  const blob = new Blob(["\ufeff" + lines.join("\r\n") + "\r\n"], {type:"text/csv;charset=utf-8"});
  const a = document.createElement("a");
  const d = new Date();
  const stamp = `${d.getFullYear()}${String(d.getMonth()+1).padStart(2,"0")}${String(d.getDate()).padStart(2,"0")}`;
  a.href = URL.createObjectURL(blob);
  a.download = `R1-5_independent_review_${stamp}.csv`;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  statusEl.className = "";
  statusEl.textContent = "已导出，请把 CSV 发回。";
}

document.getElementById("export").addEventListener("click", exportCsv);
document.getElementById("print").addEventListener("click", () => window.print());
document.getElementById("clear").addEventListener("click", () => {
  if(!confirm("确定清空全部填写？")) return;
  state = {};
  try{ localStorage.removeItem(KEY); }catch(e){}
  render();
  statusEl.className = "";
  statusEl.textContent = "已清空。";
});
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
