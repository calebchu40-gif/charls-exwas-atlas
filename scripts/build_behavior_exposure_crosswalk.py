"""Build a questionnaire-aware candidate crosswalk for CHARLS behavioral exposures.

Uses variable names/labels only; never reads respondent-level values.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


SPECS = [
    ("smoking_status", "吸烟状态/吸烟经历题", "烟草使用", {
        "2011": [r"da059", r"da061"], "2013": [r"da059", r"da061"], "2015": [r"da059", r"da061", r"da061_w3"],
        "2018": [r"da059", r"da061", r"da061_w4"], "2020": [r"da046", r"da047"]},
     "保留原题标签。早期波次‘Smoke’/‘Smoke or Not’不能只凭标签统一解释为ever或current；2018/2020明确含ever-smoked题，需结合问卷跳转派生状态。"),
    ("smoking_product", "烟草产品类型", "烟草使用", {
        "2011": [r"da060"], "2015": [r"da060s\d+"], "2018": [r"da060"]},
     "产品类别及选项结构需逐波代码本核对；不是烟草剂量。"),
    ("smoking_quantity", "每日卷烟量/烟量题", "烟草使用", {
        "2011": [r"da063"], "2013": [r"da063"], "2015": [r"da063"], "2018": [r"da063"], "2020": [r"da050_[12]"]},
     "2020分别记录目前和戒烟前卷烟量；应按是否吸烟及题目路由解释，勿把戒烟前数值当当前剂量。"),
    ("cigarette_price_per_pack", "每20支卷烟价格", "烟草使用与经济环境", {
        "2011": [r"da064"], "2013": [r"da064"], "2015": [r"da064"]},
     "自报每包20支卷烟价格；问题按吸烟/戒烟前时间点路由，不是当前市场价格或地区烟价；只适用于被问到该题的人群。"),
    ("smoking_initiation_cessation", "吸烟起始/戒烟时间", "烟草使用", {
        "2011": [r"da062.*", r"da065.*"], "2013": [r"da062.*", r"da065.*"], "2015": [r"da062.*", r"da065.*"],
        "2018": [r"da062.*", r"da065.*"], "2020": [r"da049.*"]},
     "年龄、年份及回答时点字段分列；波次存在字段重排和历史信息复核字段。"),
    ("smoking_dependence", "醒后首次吸烟时间", "烟草使用", {
        "2011": [r"da066"], "2013": [r"da066"]},
     "当前仅在变量目录中匹配2011/2013；缺波不表示无此行为。"),
    ("alcohol_recent", "近期饮酒/饮酒频率", "饮酒", {
        "2011": [r"da067"], "2013": [r"da067"], "2015": [r"da067"], "2018": [r"da067"], "2020": [r"da051"]},
     "原题回答类别和参照期需逐波核对；2020代码重排。"),
    ("alcohol_history", "曾饮酒/过往饮酒频率题", "饮酒", {
        "2011": [r"da069"], "2013": [r"da069"], "2015": [r"da069"], "2018": [r"da069"]},
     "2018题目标签显示既往饮酒与频率信息合并，不能简单当作ever二分类；2020当前目录未检出同名的独立历史字段，不以空缺推断从未饮酒。"),
    ("alcohol_morning_drink", "清晨饮酒（过去一年）", "饮酒", {
        "2011": [r"da078"], "2013": [r"da078"]},
     "代码本将其标为过去一年内是否清晨第一件事饮酒；作为独立行为指标候选，不等同于饮酒频率或酒精摄入量。仅2011/2013目录明确出现该字段。"),
    ("alcohol_prior_wave_frequency", "上一轮访问时饮酒频率预载", "饮酒史（滞后/预载）", {
        "2018": [r"zda069"]},
     "2018代码本明确标为上一轮访问信息；保留为滞后历史暴露，不解释为2018当轮状态，且不与当轮da069直接合并。"),
    ("smoking_prior_wave_status", "上一轮访问吸烟状态预载", "烟草使用史（滞后/预载）", {
        "2013": [r"zda059"], "2015": [r"zda059"]},
     "代码本将其列为前次访谈预载吸烟状态；仅作为滞后历史暴露展示，不能替代当轮吸烟题。"),
    ("smoking_prior_wave_ever", "上一轮访问曾吸烟状态预载", "烟草使用史（滞后/预载）", {
        "2018": [r"zsmoke"]},
     "2018代码本标签为在上一轮访谈时曾吸烟；仅有阳性预载码，不把未预载解释为否，也不等同于2018当轮状态。"),
    ("smoking_last_interview_status", "最近一次访谈吸烟状态预载", "烟草使用史（滞后/预载）", {
        "2020": [r"zsmoke"]},
     "2020代码本标签为上一次访谈时吸烟；仅有阳性预载码，不把未预载解释为否，也不等同于2020当轮状态。"),
    ("alcohol_type", "饮酒类型", "饮酒", {
        "2011": [r"da068s[123]"], "2013": [r"da068s[123]"], "2015": [r"da068s[123]"], "2018": [r"da068_s[123]"]},
     "白酒/啤酒/葡萄酒等多选字段；各波类别编码与名称需由问卷/值标签复核。"),
    ("alcohol_frequency_amount", "酒类频率/饮用量", "饮酒", {
        "2011": [r"da072", r"da073", r"da074", r"da075(?:_[12])?", r"da076", r"da077"],
        "2013": [r"da072", r"da073", r"da074", r"da075(?:_[12])?", r"da076", r"da077"],
        "2015": [r"da072", r"da073", r"da074", r"da075(?:_[12])?", r"da076", r"da077"],
        "2018": [r"da072", r"da073", r"da074", r"da075(?:_[12])?", r"da076", r"da077"],
        "2020": [r"da052"]},
     "啤酒、白酒、葡萄酒的单位和回忆期会变化；不可直接相加为酒精克数，除非有单位/酒精度依据。"),
    ("alcohol_start_stop", "饮酒起始/停止时间", "饮酒", {
        "2011": [r"da070.*", r"da071.*"], "2013": [r"da070.*", r"da071.*"], "2015": [r"da070.*", r"da071.*"],
        "2018": [r"da070.*", r"da071.*"]},
     "历史年龄/年份字段和主问题分别保留，当前只作经历变量候选。"),
    ("sleep_duration", "夜间睡眠时长", "睡眠", {
        "2011": [r"da049"], "2013": [r"da049"], "2015": [r"da049"], "2018": [r"da049"], "2020": [r"da030"]},
     "2011/2018/2020标签含过去一个月；2013/2015字段标签较简略，需问卷核对回忆期和单位。"),
    ("daytime_nap", "午睡时长/午睡题", "睡眠", {
        "2011": [r"da050"], "2013": [r"da050"], "2015": [r"da050"], "2018": [r"da050"], "2020": [r"da031"]},
     "不同问卷波次可能以时长或午餐后午睡时间记录；先保留原始字段，不作分钟数跨波转换。"),
    ("physical_activity_occurrence", "体力活动：强度类别是否达到门槛", "体力活动", {
        "2011": [r"da051_[123]_"], "2013": [r"da051_[123]_"], "2015": [r"da051_[123]_"],
        "2018": [r"da051_[123]_"], "2020": [r"da032_[123]_" ]},
     "活动强度名称跨波变化（2011–2015含步行，2018–2020含轻体力活动）；2013/2015另有随机抽样/路由标记，须先确认子样本设计。"),
    ("physical_activity_days", "体力活动：每周天数", "体力活动", {
        "2011": [r"da052_[123]_"], "2013": [r"da052_[123]_"], "2015": [r"da052_[123]_"], "2018": [r"da052_[123]_"], "2020": [r"da033_[123]_" ]},
     "同上：强度类别与活动模块抽样规则需逐波解释；不将未询问编码为0天。"),
    ("physical_activity_duration", "体力活动：单次/每日时长字段", "体力活动", {
        "2011": [r"da053_[123]_", r"da054_[123]_", r"da055_[123]_"], "2013": [r"da053_[123]_", r"da054_[123]_", r"da055_[123]_"],
        "2015": [r"da053_[123]_", r"da054_[123]_", r"da055_[123]_"], "2018": [r"da053_[123]_", r"da054_[123]_", r"da055_[123]_"],
        "2020": [r"da034_[123]_", r"da035_[123]_", r"da036_[123]_"]},
     "变量标签中的时长分档/时间单位存在波次差异；应基于问卷完整选项与代码本先复核，不直接套用IPAQ派生公式。"),
    ("physical_activity_purpose", "体力活动：活动目的", "体力活动", {
        "2015": [r"da051_[123]_[123]_"], "2018": [r"da051_[123]_[123]_"], "2020": [r"da037_[123]_"]},
     "工作、交通或休闲等目的题可能存在类别变更；可作描述变量，不应混入活动剂量。"),
]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, default=root / "audit/raw_variable_catalog_v1.csv")
    ap.add_argument("--out-csv", type=Path, default=root / "audit/behavior_exposure_variable_mapping_v1.csv")
    ap.add_argument("--out-json", type=Path, default=root / "site-prototype/dist/behavior_exposures_v1.json")
    args = ap.parse_args()
    src = pd.read_csv(args.catalog, dtype=str, encoding="utf-8-sig").fillna("")
    src = src[src.module.str.contains(r"health_status_and_functioning|Health_Status_and_Functioning", case=False, regex=True)]
    concepts, rows = [], []
    for cid, label, domain, wave_patterns, caveat in SPECS:
        fields = []
        for wave, patterns in wave_patterns.items():
            part = src[src.wave.eq(wave)]
            matched = part[part.variable.apply(lambda code: any(re.fullmatch(pattern, code, flags=re.I) for pattern in patterns))]
            for _, rec in matched.sort_values(["variable", "module"]).iterrows():
                field = {"wave": wave, "code": rec.variable, "source_label": rec.variable_label,
                         "module": rec.module, "source_archive": rec.source,
                         "note": f"自动概念目录中的逐波字段候选；{caveat}"}
                fields.append(field)
                rows.append({"concept_id": cid, "concept_label": label, "domain": domain, **field,
                             "mapping_status": "变量标签/编码目录匹配；需回查问卷题干、值标签和路由"})
        concepts.append({"concept_id": cid, "label": label, "domain": domain, "source_fields": fields,
                         "status": "暴露概念候选，未进行跨波剂量统一", "caveat": caveat})
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.out_csv, index=False, encoding="utf-8-sig")
    args.out_json.write_text(json.dumps(concepts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Mapped {len(rows)} source fields across {sum(bool(c['source_fields']) for c in concepts)} behavioral exposure concepts; no respondent data read.")


if __name__ == "__main__":
    main()
