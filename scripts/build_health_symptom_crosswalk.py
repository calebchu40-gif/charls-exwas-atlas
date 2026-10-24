"""Create a source-field crosswalk for selected self-rated health and symptom outcomes."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


SPECS = [
    ("self_rated_health_very_good_very_poor", "自评总体健康（Very good至Very poor题型）", "自评健康", {
        "2011": [r"da002", r"da079"], "2013": [r"da002", r"da079"],
        "2015": [r"da002", r"da079"], "2018": [r"da002"], "2020": [r"da001"]},
     "按响应尺度映射：1=Very good、5=Very poor。2011–2015问卷在健康模块开头随机安排DA001/DA002顺序，并在末尾再次询问两种量表；DA002/DA079同属本响应尺度，但问卷位置/路由不同。2011 DA079问卷题干及选项与此尺度相符，Codebook标题含By Comparing With Others；保留冲突并待获批数据字典核实。不可把重复问答位置当作独立结局，也不能仅按概念名合并。"),
    ("self_rated_health_excellent_poor", "自评总体健康（Excellent至Poor题型）", "自评健康", {
        "2011": [r"da001", r"da080"], "2013": [r"da001", r"da080"], "2015": [r"da001", r"da080"]},
     "按响应尺度映射：1=Excellent、5=Poor。2011–2015问卷在健康模块开头随机安排DA001/DA002顺序，并在末尾再次询问两种量表；DA001/DA080同属本响应尺度，但问卷位置/路由不同。不得把两次问答当作独立结局，或将两套不同五级选项直接合并；字段路由及缺失机制须按发布数据字典核实。"),
    ("health_change", "与既往访谈相比的健康变化", "自评健康", {
        "2013": [r"da002_w2_1"], "2015": [r"da002_w2_1"], "2018": [r"da002_w2_1"]},
     "返访/既往访谈比较题；不是同一时点总体健康等级，不能与自评总体健康合并。"),
    ("chest_pain_symptoms", "胸痛症状（左侧胸痛与活动相关胸痛分项）", "症状", {
        "2011": [r"da003", r"da004"], "2013": [r"da003", r"da004"]},
     "包含左侧胸痛与爬楼/上坡/快走时胸痛两个分别提问的症状项；不等于心绞痛临床诊断，保留两个分项、波次和非代理路由，不合成一个分数。"),
    ("who_bodily_pain_severity", "过去一个月身体疼痛程度（WHO自报健康题）", "症状", {"2011": [r"de001"]},
     "2011年DE前6项本人健康题；仅随机抽中的一半家庭提问，且DE部分禁止代理回答。未问到是设计性缺失，不可编码为无症状；与疼痛部位/DA疼痛题分开，非跨波复测指标。"),
    ("who_sleep_difficulty_severity", "过去一个月睡眠困难程度（WHO自报健康题）", "睡眠/症状", {"2011": [r"de002"]},
     "2011年DE前6项本人健康题；仅随机抽中的一半家庭提问，且DE部分禁止代理回答。未问到是设计性缺失，不可编码为无症状；与睡眠时长/质量题分开，非跨波复测指标。"),
    ("who_mobility_problem_severity", "过去一个月活动/行走问题程度（WHO自报健康题）", "身体功能", {"2011": [r"de003"]},
     "2011年DE前6项本人健康题；仅随机抽中的一半家庭提问，且DE部分禁止代理回答。未问到是设计性缺失，不可编码为无症状；不与ADL/IADL功能限制题合成，非跨波复测指标。"),
    ("who_concentration_memory_difficulty", "过去一个月注意力/记忆困难程度（WHO自报健康题）", "认知症状", {"2011": [r"de004"]},
     "2011年DE前6项本人健康题；仅随机抽中的一半家庭提问，且DE部分禁止代理回答。未问到是设计性缺失，不可编码为无症状；自评主观困难，不等同客观认知测验，非跨波复测指标。"),
    ("who_breathlessness_severity", "过去一个月气短问题程度（WHO自报健康题）", "症状", {"2011": [r"de005"]},
     "2011年DE前6项本人健康题；仅随机抽中的一半家庭提问，且DE部分禁止代理回答。未问到是设计性缺失，不可编码为无症状；非跨波复测指标。"),
    ("who_low_mood_severity", "过去一个月低落/悲伤/抑郁感程度（WHO自报健康题）", "情绪症状", {"2011": [r"de006"]},
     "2011年DE前6项本人健康题；仅随机抽中的一半家庭提问，且DE部分禁止代理回答。未问到是设计性缺失，不可编码为无症状；与CES-D频率条目及量表分数分开，非跨波复测指标。"),
    ("affect_sad_yesterday", "昨日悲伤程度", "短期情绪状态", {"2013": [r"wb06"]},
     "2013年“昨天的感受”条目之一，单项1–5程度评定；回忆窗为昨日，与过去一周CES-D条目及2011 WHO过去一个月情绪题不同，单独保留、不合成抑郁量表。与昨天睡眠时点同日回忆，没有明确时间先后；授权数据核验前不推断目标分母或缺失类别。"),
    ("affect_lonely_yesterday", "昨日孤独程度", "短期情绪状态", {"2013": [r"wb08"]},
     "2013年“昨天的感受”条目之一，单项1–5程度评定；回忆窗为昨日，与过去一周CES-D孤独条目不同，单独保留、不合成抑郁量表。与昨天睡眠时点同日回忆，没有明确时间先后；授权数据核验前不推断目标分母或缺失类别。"),
    ("affect_frustrated_yesterday", "昨日挫败感程度", "短期情绪状态", {"2013": [r"wb05"]},
     "2013年“昨天的感受”条目之一，单项1–5程度评定；不是经验证的心理量表分数，不与其他项目合成。回忆窗与WB03/WB04同为昨天；关联没有明确时间先后。授权数据核验前不推断代理/本人路由、目标分母或缺失类别。"),
    ("affect_enthusiastic_yesterday", "昨日热情程度", "短期情绪状态", {"2013": [r"wb07"]},
     "2013年“昨天的感受”条目之一，单项1–5程度评定；不是经验证的心理量表分数，不与其他项目合成。回忆窗与WB03/WB04同为昨天；关联没有明确时间先后。授权数据核验前不推断代理/本人路由、目标分母或缺失类别。"),
    ("affect_content_yesterday", "昨日满足感程度", "短期情绪状态", {"2013": [r"wb09"]},
     "2013年“昨天的感受”条目之一，单项1–5程度评定；不是经验证的心理量表分数，不与其他项目合成。回忆窗与WB03/WB04同为昨天；关联没有明确时间先后。授权数据核验前不推断代理/本人路由、目标分母或缺失类别。"),
    ("affect_worried_yesterday", "昨日担忧程度", "短期情绪状态", {"2013": [r"wb10"]},
     "2013年“昨天的感受”条目之一，单项1–5程度评定；不是经验证的心理量表分数，不与其他项目合成。回忆窗与WB03/WB04同为昨天；关联没有明确时间先后。授权数据核验前不推断代理/本人路由、目标分母或缺失类别。"),
    ("affect_bored_yesterday", "昨日无聊程度", "短期情绪状态", {"2013": [r"wb11"]},
     "2013年“昨天的感受”条目之一，单项1–5程度评定；不是经验证的心理量表分数，不与其他项目合成。回忆窗与WB03/WB04同为昨天；关联没有明确时间先后。授权数据核验前不推断代理/本人路由、目标分母或缺失类别。"),
    ("affect_happy_yesterday", "昨日快乐程度", "短期情绪状态", {"2013": [r"wb12"]},
     "2013年“昨天的感受”条目之一，单项1–5程度评定；不是经验证的心理量表分数，不与其他项目合成。回忆窗与WB03/WB04同为昨天；关联没有明确时间先后。授权数据核验前不推断代理/本人路由、目标分母或缺失类别。"),
    ("affect_angry_yesterday", "昨日愤怒程度", "短期情绪状态", {"2013": [r"wb13"]},
     "2013年“昨天的感受”条目之一，单项1–5程度评定；不是经验证的心理量表分数，不与其他项目合成。回忆窗与WB03/WB04同为昨天；关联没有明确时间先后。授权数据核验前不推断代理/本人路由、目标分母或缺失类别。"),
    ("affect_tired_yesterday", "昨日疲惫程度", "短期情绪状态", {"2013": [r"wb14"]},
     "2013年“昨天的感受”条目之一，单项1–5程度评定；不是经验证的心理量表分数，不与其他项目合成。回忆窗与WB03/WB04同为昨天；关联没有明确时间先后。授权数据核验前不推断代理/本人路由、目标分母或缺失类别。"),
    ("affect_stressed_yesterday", "昨日压力感程度", "短期情绪状态", {"2013": [r"wb15"]},
     "2013年“昨天的感受”条目之一，单项1–5程度评定；不是经验证的心理量表分数，不与其他项目合成。回忆窗与WB03/WB04同为昨天；关联没有明确时间先后。授权数据核验前不推断代理/本人路由、目标分母或缺失类别。"),
    ("chewing_difficulty_solid_foods", "因牙齿导致的硬食咀嚼困难", "口腔/进食功能", {"2018": [r"da040_w4_2"]},
     "2018年波次特定题项；问卷依既往牙齿状态安排提问，佩戴假牙者按戴假牙时能力回答。代码3=Not Applicable（不适用）须与No（否）分开，跨波可比性未建立。"),
    ("pain_presence", "身体疼痛（存在/程度题）", "症状", {
        "2011": [r"da041"], "2015": [r"da041"], "2018": [r"da041_w4"], "2020": [r"da027"]},
     "2011问当前疼痛、2015问经常受身体疼痛困扰、2018/2020题目设置有变化；跨波可比性尚未确认。"),
    ("pain_yesterday", "昨日疼痛程度/有无", "症状", {"2013": [r"wb16"]},
     "2013问‘昨天是否疼痛’，回忆期明显不同于其他波的当前/经常疼痛题，单独保留。"),
    ("pain_location", "身体疼痛部位", "症状", {
        "2011": [r"da042s\d+"], "2013": [r"da042s\d+"], "2015": [r"da042s\d+"],
        "2018": [r"da042_s\d+"], "2020": [r"da028_s\d+"]},
     "身体部位为多选拆分字段；选项数量/具体部位和‘其他’的编码需逐波对照，不把每个部位字段当独立疾病。"),
    ("pain_management_measures", "疼痛缓解措施", "疼痛管理", {
        "2013": [r"da042_w2_1s[1-6]"], "2015": [r"da042_w2_1s[1-6]"], "2018": [r"da042_w2_1_s[1-6]"]},
     "疼痛缓解多选题，条件于问卷疼痛路由；含中/西药、针灸、按摩、其他及无措施等选项。选项各自拆栏，不能把未选择/缺失推断成No；2011及2020无直接对应的同组措施题，波次间措辞和底层存储仍须按原码本确认。"),
    ("other_important_medical_condition", "未列出的其他重要疾病或健康状况", "其他自报健康状况", {
        "2011": [r"da045"], "2013": [r"da045"], "2015": [r"da045"], "2018": [r"da045"]},
     "询问前述疾病之外、受访者认为对健康重要的其他疾病或状况；它是宽泛的自报补充项，不替代具名慢病诊断。仅映射是否有其他状况，不将后续开放文本作为公开网站内容；缺少2020直接等价字段。"),
    ("pain_intensity", "疼痛严重程度/等级题", "症状", {
        "2011": [r"da043"], "2013": [r"wb16"], "2018": [r"da041_w4"], "2020": [r"da027"]},
     "候选字段的题型和响应类别未证明等价；2013是昨日疼痛等级，其他波需检查选项与参照期后再决定能否建统一严重程度指标。"),
    ("subjective_life_expectancy", "主观预期寿命可能性", "主观健康预期", {"2020": [r"da029"]},
     "受访者对达到XFAgePossibility所示年龄的主观可能性判断；该阈值由年龄分组生成，必须与DA029一同解释。它不是实际生存结局或客观寿命预测；保留五级原始回答和年龄阈值，不建立跨波等价或衍生分数。"),
    ("vision_distance", "自评远视力", "感官功能", {"2011": [r"da033"], "2013": [r"da033"], "2015": [r"da033"], "2018": [r"da033"]},
     "问卷题目涉及戴眼镜/矫正镜时的自评远视力；目前目录未检出2020对应字段。"),
    ("vision_near", "自评近视力", "感官功能", {"2011": [r"da034"], "2013": [r"da034"], "2015": [r"da034"], "2018": [r"da034"]},
     "问卷题目涉及戴眼镜/矫正镜时的自评近视力；目前目录未检出2020对应字段。"),
    ("hearing_quality", "自评听力", "感官功能", {"2011": [r"da039"], "2013": [r"da039"], "2015": [r"da039"], "2018": [r"da039"]},
     "题干按是否通常佩戴助听器决定是否戴/不戴时回答；须保留助听器状态和代理应答路由。"),
    ("hearing_aid", "助听器使用", "感官功能", {
        "2011": [r"da038"], "2013": [r"da038", r"zda038"], "2015": [r"da038", r"zda038"], "2018": [r"da038_w4"]},
     "自报是否使用助听器；zda038是前次访谈记录/返访路由字段，不等同于本轮重新询问；当前目录未检出2020对应字段，不能将缺波填成未使用。"),
]

# 2011 DA044 is a single-select/multiple-response style disease-history card.
# The official codebook shows positive selected category codes only; it does
# not justify treating an unlisted storage value as a respondent-level No.
INFECTIOUS_HISTORY = [
    (1, "tuberculosis", "结核病史"), (2, "hepatitis_b", "乙型肝炎史"),
    (3, "malaria", "疟疾史"), (4, "influenza", "流感史"),
    (5, "rabies", "狂犬病史"), (6, "schistosomiasis", "血吸虫病史"),
    (7, "hiv_aids", "艾滋病/感染者病史"), (8, "encephalitis_b", "乙型脑炎史"),
    (9, "dysentery", "痢疾史"), (10, "measles", "麻疹史"),
    (11, "brucellosis", "布氏杆菌病史"), (12, "gonorrhea", "淋病史"),
    (13, "syphilis", "梅毒史"), (14, "other_infectious_disease", "其他传染病史（未具体指明）"),
]
SPECS.extend(
    (f"infectious_history_{cid}", f"曾被医生告知患有：{label}", "既往感染病史",
     {"2011": [rf"da044s{item}"]},
     "2011基线单波回顾性病史，不代表当前感染或现患状态。官方代码本仅显示被选中的类别代码；不得将未显示/未选存储值推断为No。单病种记录可能稀疏，分析前应核查发布数据的选择题编码、缺失及披露风险。")
    for item, cid, label in INFECTIOUS_HISTORY
)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, default=root / "audit/raw_variable_catalog_v1.csv")
    ap.add_argument("--out-csv", type=Path, default=root / "audit/health_symptom_variable_mapping_v1.csv")
    ap.add_argument("--out-json", type=Path, default=root / "site-prototype/dist/health_symptoms_v1.json")
    args = ap.parse_args()
    src = pd.read_csv(args.catalog, dtype=str, encoding="utf-8-sig").fillna("")
    src = src[src.module.str.contains(r"health_status_and_functioning|Health_Status_and_Functioning", case=False, regex=True)]
    concepts, rows = [], []
    for cid, label, domain, wave_patterns, caveat in SPECS:
        fields = []
        for wave, patterns in wave_patterns.items():
            part = src[src.wave.eq(wave)]
            selected = part[part.variable.apply(lambda code: any(re.fullmatch(pattern, code, flags=re.I) for pattern in patterns))]
            for _, rec in selected.sort_values(["variable", "module"]).iterrows():
                field_note = ("前次访谈/返访预加载的助听器使用状态；条件性显示，不是本轮重新询问。" if cid == "hearing_aid" and rec.variable.lower().startswith("zda") else f"结局概念候选；{caveat}")
                field = {"wave": wave, "code": rec.variable, "source_label": rec.variable_label,
                         "module": rec.module, "source_archive": rec.source,
                         "note": field_note}
                fields.append(field)
                rows.append({"concept_id": cid, "concept_label": label, "domain": domain, **field,
                             "mapping_status": "field identified in official questionnaire/codebook; see wave-specific caveat",
                             "value_labels": "",
                             "value_label_status": "",
                             "value_label_source": ""})
        concept_status = "表型概念候选；未创建跨波分数"
        concepts.append({"concept_id": cid, "label": label, "domain": domain, "source_fields": fields,
                         "status": concept_status, "caveat": caveat})
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.out_csv, index=False, encoding="utf-8-sig")
    args.out_json.write_text(json.dumps(concepts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Mapped {len(rows)} source fields across {sum(bool(c['source_fields']) for c in concepts)} health/symptom phenotype concepts; no respondent data read.")


if __name__ == "__main__":
    main()

