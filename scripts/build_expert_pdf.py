#!/usr/bin/env python3
"""build_expert_pdf.py — Generate two clinician-oriented PDFs for ophthalmologist review.

1. phase4_expert_review.pdf    — 12-case system evaluation questionnaire (table, 2 pages, evidence-rich)
2. blind_gold_review.pdf       — 12-case gold labelling review (1-page table, route-annotated)

Clinical framing: cases presented as patient scenarios; evidence sources cited per case
(FDA labels / Stockley's / DDInter) so ophthalmologists can judge with full context.
"""
import csv
import sys
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ophthalmic_ddi_cds_agent.kg_layer import PreciseKG

SONG = Path("C:/Windows/Fonts/simsun.ttc")
HEI = Path("C:/Windows/Fonts/simhei.ttf")


class ExpertPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("hei", "", 8)
            self.set_text_color(150, 150, 150)
            self.cell(190, 6, "眼科药物相互作用临床决策支持系统 — 专家评审材料", align="R")
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("song", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"第 {self.page_no()} 页", align="C")


def build_questionnaire():
    """Two-page table: 12 cases x 6 per page, evidence-rich rows."""
    pdf = ExpertPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_font("song", "", SONG)
    pdf.add_font("hei", "", HEI)
    pdf.add_font("song", "B", SONG)

    cases = [
        ("1", "噻吗洛尔（滴眼液）× 阿替洛尔（口服）",
         "65 岁男性，开角型青光眼，0.5% 噻吗洛尔滴眼液每日 2 次；因高血压口服阿替洛尔 25mg/日。复诊诉偶有头晕乏力，静息心率 52 次/分。",
         "高　机制：噻吗洛尔滴眼液全身吸收可达 50-80%（经鼻泪管入血、绕过首过代谢），与全身 β 受体阻滞剂叠加负性变时效应 → 明显心动过缓。\n"
         "建议：监测心率/血压，必要时换用前列腺素类似物等全身影响小的降眼压药。\n"
         "证据：FDA Timoptic 标签明确警示“additive effects of beta blockade”；Stockley's Drug Interactions"),
        ("2", "溴莫尼定（滴眼液）× 芬太尼（静脉/透皮）",
         "72 岁女性，青光眼，滴用溴莫尼定；因膝关节置换术后疼痛使用芬太尼镇痛。家属诉患者白天嗜睡明显，血压偏低。",
         "高　机制：溴莫尼定（α2 激动剂）全身吸收约 10-50%，本身可引起中枢抑制（嗜睡、低血压、儿童呼吸抑制）；与阿片类中枢抑制叠加，老年患者风险更高。\n"
         "建议：监测意识状态与血压，避免夜间加用镇静药。\n"
         "证据：FDA Alphagan P 标签 CNS depression 警示；α2 激动剂类效应"),
        ("3", "阿托品（滴眼液）× 阿米替林（口服）",
         "58 岁男性，虹膜睫状体炎，1% 阿托品滴眼液；因抑郁症口服阿米替林 75mg/日。用药 1 周后出现排尿困难、口干、轻度意识模糊。",
         "高　机制：阿托品滴眼液全身吸收高（>50%），与三环类抗抑郁药（强抗胆碱）叠加 → 外周（尿潴留、便秘）与中枢（谵妄）抗胆碱综合征。\n"
         "建议：避免合用或密切监测；必要时换用无抗胆碱活性的抗抑郁药。\n"
         "证据：FDA 阿托品标签抗胆碱警示；Stockley's 抗胆碱药叠加章节"),
        ("4", "多佐胺（滴眼液）× 氢氯噻嗪（口服）",
         "60 岁女性，青光眼，2% 多佐胺滴眼液；因高血压口服氢氯噻嗪 12.5mg/日。化验示血钾 3.3mmol/L，碳酸氢根轻度下降。",
         "中　机制：多佐胺（碳酸酐酶抑制剂）与噻嗪类利尿剂均可致代谢性酸中毒与低钾，合用风险叠加（尤其肾功能不全者）。\n"
         "建议：监测电解质/酸碱平衡，必要时补钾。\n"
         "证据：FDA Trusopt 标签“additive effects with oral carbonic anhydrase inhibitors”；DDInter Moderate"),
        ("5", "酮咯酸（滴眼液）× 华法林（口服）",
         "68 岁男性，白内障术后炎症，酮咯酸滴眼液；因房颤长期口服华法林（INR 2.2）。",
         "中　机制：酮咯酸（NSAID）滴眼液有少量全身吸收（<10%），抑制血小板 + 华法林抗凝 → 出血风险增加（胃肠道、眼内）。\n"
         "建议：监测 INR 与出血征象，避免长期使用；与抗凝患者沟通。\n"
         "证据：FDA Acular 标签“caution with anticoagulants”；DDInter Major（全身途径评级，眼科剂量修正为中）"),
        ("6", "倍他洛尔（滴眼液）× 美托洛尔（口服）",
         "70 岁女性，青光眼，0.25% 倍他洛尔滴眼液；因冠心病口服美托洛尔 47.5mg/日。静息心率 55 次/分，无不适。",
         "中　机制：倍他洛尔（β1 选择性，全身吸收中等 10-50%）与全身 β 阻滞剂存在叠加负性变时效应，但程度较轻。\n"
         "建议：监测心率即可，一般无需停药。\n"
         "证据：FDA Betoptic 标签 additive beta-blockade 警示；DDInter Moderate"),
        ("7", "拉坦前列素（滴眼液）× 阿替洛尔（口服）",
         "63 岁男性，开角型青光眼，拉坦前列素滴眼液；因高血压口服阿替洛尔。无特殊不适。",
         "低　机制：前列腺素类似物全身吸收极低（<1%），与 β 阻滞剂无已知药理学相互作用。\n"
         "建议：无需特殊处理。\n"
         "证据：FDA Xalatan 标签无系统相互作用记录"),
        ("8", "拉坦前列素（滴眼液）× 美托洛尔（口服）",
         "66 岁女性，青光眼，拉坦前列素；因心衰口服美托洛尔。病情平稳。",
         "低　机制：前列腺素类似物全身暴露极低，无已知与 β 阻滞剂相互作用。\n"
         "建议：无需特殊处理。\n"
         "证据：FDA Xalatan 标签；DDInter 无眼科相关记录"),
        ("9", "拉坦前列素（滴眼液）× 普萘洛尔（口服）",
         "55 岁男性，青光眼，拉坦前列素；因偏头痛预防口服普萘洛尔。无不适。",
         "低　机制：无已知相互作用机制（前列腺素类不干扰 β 通路）。\n"
         "建议：无需特殊处理。\n"
         "证据：FDA Xalatan 标签"),
        ("10", "噻吗洛尔（滴眼液）× 美托洛尔（口服）",
         "71 岁男性，青光眼，0.5% 噻吗洛尔滴眼液；因心衰口服美托洛尔 95mg/日。诉活动后气短乏力，静息心率 48 次/分。",
         "高　机制：噻吗洛尔高全身吸收 + 全身 β 阻滞剂叠加 → 显著心动过缓、心衰代偿受损（本例心率 48 已有表现）。\n"
         "建议：监测心率/心功能，考虑换用前列腺素类似物或溴莫尼定替代。\n"
         "证据：FDA Timoptic 标签；DDInter（timolol 全身评级高，眼科高吸收适用）"),
        ("11", "溴莫尼定（滴眼液）× 吗啡（口服）",
         "74 岁女性，青光眼，溴莫尼定滴眼液；因带状疱疹后神经痛口服吗啡缓释片。家属诉白天嗜睡明显。",
         "高　机制：溴莫尼定中枢抑制与阿片类叠加（老年患者尤其明显），可致明显嗜睡、低血压，跌倒风险增加。\n"
         "建议：监测意识状态，谨慎合用；告知家属观察。\n"
         "证据：FDA Alphagan P 标签 CNS 警示；阿片类中枢抑制类效应"),
        ("12", "阿托品（滴眼液）× 苯海拉明（口服）",
         "45 岁女性，葡萄膜炎，1% 阿托品滴眼液；因过敏性鼻炎口服苯海拉明。诉口干、视物模糊加重、便秘。",
         "中　机制：阿托品（高全身吸收）与苯海拉明（抗组胺，具抗胆碱活性）抗胆碱作用叠加 → 口干、便秘、尿潴留、谵妄风险。\n"
         "建议：关注抗胆碱症状，可换用无抗胆碱活性的抗组胺药（如氯雷他定）。\n"
         "证据：FDA 阿托品标签；抗胆碱类效应"),
    ]


    HINTS = {
        "1": "患者提示：老年患者心率储备低，β 叠加效应更明显，应主动问诊头晕/乏力。",
        "2": "患者提示：老年 + 术后状态，嗜睡增加跌倒风险，应嘱家属观察。",
        "3": "患者提示：老年男性合并前列腺增生者，尿潴留风险显著升高。",
        "4": "患者提示：肾功能不全、低钾饮食者电解质风险更高。",
        "5": "患者提示：INR 目标 2-3，合用期间可适当增加监测频率。",
        "6": "患者提示：心率 <50 次/分或出现症状时应重新评估。",
        "7": "患者提示：无特殊。",
        "8": "患者提示：无特殊。",
        "9": "患者提示：无特殊。",
        "10": "患者提示：心衰患者代偿储备低，心率下降可能诱发失代偿。",
        "11": "患者提示：老年患者跌倒风险高，应嘱家属观察意识状态。",
        "12": "患者提示：老年患者抗胆碱效应更敏感，警惕谵妄。",
    }

    def render_page(start_i):
        pdf.add_page()
        pdf.set_font("hei", "", 13)
        pdf.set_text_color(0, 60, 120)
        pdf.cell(190, 8, f"眼科药物相互作用系统评估 — 专家评审问卷（第 {start_i // 6 + 1} 页 / 共 2 页）",
                 align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        pdf.set_font("song", "", 8.5)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(190, 4.4,
                       "说明：每行一例 —— 眼科局部用药（滴眼液）× 全身用药（口服/注射）。"
                       "【风险判断】= 您对该组合临床风险的个人判断；【认可度】= 对系统评估的认可程度（5=完全认可）。"
                       "证据来源已注明（FDA 标签 / Stockley's / DDInter），供参考。")
        pdf.ln(1.5)
        pdf.set_font("song", "", 8)
        with pdf.table(col_widths=(8, 32, 40, 68, 26, 16), line_height=3.9,
                       text_align=("CENTER", "LEFT", "LEFT", "LEFT", "LEFT", "LEFT"),
                       padding=0.6) as table:
            head = table.row()
            for h in ("编号", "药物组合", "临床情境", "系统评估与依据", "风险判断", "认可度"):
                head.cell(h)
            for num, pair, scen, sys_ in cases[start_i:start_i + 6]:
                # split combo into two lines: ophthalmic / systemic
                a_part, _, b_part = pair.partition("×")
                pair2 = a_part.strip() + chr(10) + chr(215) + chr(32) + b_part.strip()
                sys_full = sys_ + chr(10) + HINTS.get(num, "")
                row = table.row()
                row.cell(num)
                row.cell(pair2)
                row.cell(scen)
                row.cell(sys_full)
                row.cell("□高 □中 □低")
                row.cell("1□ 2□ 3□ 4□ 5□")
        pdf.ln(1)
        pdf.set_font("song", "", 8.5)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(190, 4.4,
                       "标注含义：高=建议规避或严格监测；中=需监测或调整；低=眼科剂量下风险可忽略。意见请写在表格空白处。")

    render_page(0)
    render_page(6)
    out = ROOT / "outputs" / "expert_review" / "phase4_expert_review.pdf"
    pdf.output(str(out))
    print(f"PDF saved -> {out} ({pdf.page_no()} pages)")


def build_gold_review():
    """Gold-labelling review in plain clinical language: 12 combos, expert picks 高/中/低 directly.
    No meta-judgement (agree/upgrade/downgrade) — same format as the questionnaire."""
    pdf = ExpertPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_font("song", "", SONG)
    pdf.add_font("hei", "", HEI)
    pdf.add_font("song", "B", SONG)

    # system rationale per case
    SYS = {
        "R01": "系统判定：中风险（酮咯酸眼用吸收低，NSAID×抗凝出血相加需监测）",
        "R02": "系统判定：高风险（α2 激动×阿片 CNS 抑制相加，与 G03 专家共识一致）",
        "R03": "系统判定：中风险（利福平强 CYP3A4 诱导降低激素暴露，疗效损失有临床意义）",
        "R04": "系统判定：高风险（阿托品高吸收×阿片，中枢抗胆碱综合征）",
        "R05": "系统判定：高风险（东莨菪碱高吸收×TCA 强抗胆碱）",
        "R06": "系统判定：高风险（阿托品高吸收×阿片，同 R04 机制）",
        "R07": "系统判定：低风险（喹诺酮 QT 机制存在但眼用吸收<5%，无临床 QT 意义）",
        "R08": "系统判定：中风险（倍他洛尔中吸收 β1 选择性×CCB，暴露受限）",
        "R09": "系统判定：中风险（同 R01，NSAID×NOAC 出血相加）",
        "R10": "系统判定：中风险（弱效激素类级保守提示，IOP/全身效应弱）",
        "R11": "系统判定：中风险（弱效激素×磺脲，类级保守提示）",
        "R12": "系统判定：中风险（同 R01/R09，NSAID×华法林监测 INR）",
    }
    # (num, oph, sys, scenario, current) — scenario in clinical language
    cases = [
        ("R01", "酮咯酸（滴眼液）", "依诺肝素（皮下注射）",
         "白内障术后滴用酮咯酸；因静脉血栓预防皮下注射依诺肝素。",
         "当前标注：中风险（需监测）"),
        ("R02", "溴莫尼定（滴眼液）", "曲马多（口服）",
         "青光眼滴用溴莫尼定；因慢性疼痛口服曲马多。白天嗜睡。",
         "当前标注：高风险（建议监测）"),
        ("R03", "地塞米松（滴眼液）", "利福平（口服）",
         "术后炎症滴用地塞米松；因结核病口服利福平。",
         "当前标注：中风险（需监测）"),
        ("R04", "阿托品（滴眼液）", "曲马多（口服）",
         "虹膜睫状体炎滴用阿托品；因疼痛口服曲马多。",
         "当前标注：高风险"),
        ("R05", "东莨菪碱（滴眼液）", "阿米替林（口服）",
         "睫状肌麻痹滴用东莨菪碱；因抑郁症口服阿米替林。",
         "当前标注：高风险"),
        ("R06", "阿托品（滴眼液）", "羟考酮（口服）",
         "葡萄膜炎滴用阿托品；因癌痛口服羟考酮。",
         "当前标注：高风险"),
        ("R07", "左氧氟沙星（滴眼液）", "索他洛尔（口服）",
         "角膜炎滴用左氧氟沙星；因心律失常口服索他洛尔。",
         "当前标注：低风险（无需特殊处理）"),
        ("R08", "倍他洛尔（滴眼液）", "维拉帕米（口服）",
         "青光眼滴用倍他洛尔；因高血压口服维拉帕米。",
         "当前标注：中风险"),
        ("R09", "酮咯酸（滴眼液）", "利伐沙班（口服）",
         "白内障术后滴用酮咯酸；因房颤口服利伐沙班。",
         "当前标注：中风险"),
        ("R10", "氟米龙（滴眼液）", "泼尼松（口服）",
         "结膜炎滴用氟米龙；因类风湿口服泼尼松。",
         "当前标注：低风险；系统提示中风险（弱效激素争议）"),
        ("R11", "氟米龙（滴眼液）", "格列美脲（口服）",
         "结膜炎滴用氟米龙；因糖尿病口服格列美脲。",
         "当前标注：低风险；系统提示中风险（同上）"),
        ("R12", "酮咯酸（滴眼液）", "华法林（口服）",
         "白内障术后滴用酮咯酸；因房颤口服华法林（INR 2.2）。",
         "当前标注：中风险"),
    ]

    def render_page(start_i):
        pdf.add_page()
        pdf.set_font("hei", "", 13)
        pdf.set_text_color(0, 60, 120)
        pdf.cell(190, 8, f"药物组合临床风险复核（第 {start_i // 6 + 1} 页 / 共 2 页）",
                 align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        pdf.set_font("song", "", 8.5)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(190, 4.4,
                       "说明：以下 12 个组合用于系统病例标注的复核。请直接给出您对该组合临床风险的判断（高/中/低），"
                       "与当前标注是否一致均可 —— 您的独立判断即金标准。")
        pdf.ln(1.5)
        with pdf.table(col_widths=(9, 34, 34, 55, 28, 30), line_height=4.6,
                       text_align=("CENTER", "LEFT", "LEFT", "LEFT", "LEFT", "LEFT"),
                       padding=0.9) as table:
            head = table.row()
            for h in ("编号", "眼科局部用药", "全身用药", "临床情境", "当前标注", "您的判断"):
                head.cell(h)
            for num, oph, sysd, scen, cur in cases[start_i:start_i + 6]:
                row = table.row()
                row.cell(num)
                row.cell(oph)
                row.cell(sysd)
                row.cell(scen)
                row.cell(cur + chr(10) + SYS.get(num, ""))
                row.cell("□高 □中 □低")
        pdf.ln(1)
        pdf.set_font("song", "", 8.5)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(190, 4.4,
                       "标注含义：高=建议规避或严格监测；中=需监测或调整；低=眼科剂量下风险可忽略。"
                       "意见可写在表格空白处。")

    render_page(0)
    render_page(6)
    out = ROOT / "outputs" / "expert_review" / "blind_gold_review.pdf"
    pdf.output(str(out))
    print(f"PDF saved -> {out} ({pdf.page_no()} pages)")


if __name__ == "__main__":
    build_questionnaire()
    build_gold_review()
