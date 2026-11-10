"""Public aggregate v2: Chinese labels, gzip shards, disclosure screening CSV."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
RES = BASE / "private/results"
OUT = RES / "public_full_scan_v3"
CATALOG = BASE / "code/site-prototype/dist/catalog.json"
MIN_N = 100
SHARDS = 8
CJK = re.compile(r"[\u4e00-\u9fff]")

MANUAL = {
    "alcohol_frequency": "饮酒频率",
    "heating_energy": "取暖能源",
    "cooking_fuel_main": "炊事燃料",
    "current_employer_organization_type": "现工作单位类型",
    "building_structure": "住房结构",
    "marital_status_current": "婚姻状况",
    "first_job_work_unit_type": "第一份工作单位类型",
    "indoor_cleanliness": "室内整洁程度",
    "housing_construction_year": "住房建造年份",
    "sleep_restless": "睡眠不安",
    "entrance_steps": "入户台阶数",
    "indoor_temperature": "室内温度",
    "old_age_financial_support_source": "养老经济来源",
    "current_hukou_location": "当前户口所在地",
    "employed_hours_per_day": "每日工作小时",
    "dwelling_house_type": "住房类型",
    "smoking_status": "吸烟状态",
    "smoking_product": "吸烟类型",
    "individual_meal_frequency": "每日进食次数",
    "household_food_expenditure": "家庭食品支出",
    "dwelling_area": "住房面积",
    "running_water_at_residence": "自来水入户",
    "electricity_access": "是否通电",
    "piped_gas_access": "管道燃气",
    "toilet_access": "室内厕所",
    "bathing_facility": "洗浴设施",
    "home_accessibility": "无障碍设施",
    "building_stories": "楼层数",
    "drinking_water_source": "饮用水来源",
    "subjective_absolute_living_standard": "自评生活水平",
    "life_satisfaction": "生活满意度",
    "self_rated_health_very_good_very_poor": "自评健康",
    "pain_intensity": "疼痛程度",
    "vision_distance": "远视力",
    "vision_near": "近视力",
    "hearing_quality": "听力",
    "mobility_run": "跑动困难",
    "mobility_stairs": "爬楼困难",
    "mobility_bend": "弯腰困难",
    "mobility_lift": "提重物困难",
    "mobility_reach": "抬臂困难",
    "mobility_chair": "起身困难",
    "mobility_coin": "捡硬币困难",
    "adl_dressing": "穿衣困难",
    "adl_bathing": "洗澡困难",
    "adl_eating": "进食困难",
    "adl_bed": "上下床困难",
    "adl_toilet": "如厕困难",
    "adl_continence": "控制大小便困难",
    "iadl_chores": "做家务困难",
    "iadl_meals": "做饭困难",
    "iadl_shopping": "购物困难",
    "iadl_money": "管理钱财困难",
    "iadl_medication": "服药困难",
    "iadl_phone": "打电话困难",
    "mood_bothered": "情绪：烦恼",
    "mood_concentration": "情绪：注意力",
    "mood_depressed": "情绪：抑郁",
    "mood_effort": "情绪：费力",
    "mood_hopeful": "情绪：对未来抱有希望",
    "mood_fearful": "情绪：害怕",
    "mood_restless_sleep": "情绪：睡眠不安",
    "mood_happy": "情绪：愉快",
    "mood_lonely": "情绪：孤独",
    "mood_could_not_get_going": "情绪：提不起劲",
    "cog_subjective_memory": "自评记忆力",
    "cog_figure_copy": "画图复制",
    "cog_orientation_time": "时间定向",
    "cog_serial7": "连续减 7",
    "subjective_life_expectancy": "自评预期寿命",
    "cesd_score": "CES-D 抑郁得分",

    "healthcare_cost_outpatient_oop": "门诊自付费用",
    "respondent_health_at_retirement": "退休时自评健康",
    "spouse_health_at_respondent_retirement": "退休时配偶健康",
    "household_agricultural_work_satisfaction_2015_2018": "农业劳动满意度",
    "nonfarm_job_satisfaction_2015_2018": "非农工作满意度",
    "health_insurance_type_status": "医疗保险类型",
    "expected_time_current_workplace": "预计在当前单位工作多久",
    "wage_payer_source_2011_2020": "工资发放方",
    "spouse_work_at_respondent_retirement": "退休时配偶经济活动",
    "health_related_workdays_missed_current_job_2018": "因病缺勤天数",
    "reason_for_employer_change_since_last_interview_2018": "更换工作单位原因",
    "healthcare_cost_outpatient_medicine_oop": "门诊药费自付",
    "corrected_prior_nonwork_last_work_exit_reason_2020": "停止工作原因",
    "balance_test_preventing_health_problems_2013": "平衡测试受限原因",
    "subjective_relative_living_standard": "相对生活水平",
    "most_recent_job_employer_organization_type_2011_2018": "最近工作单位类型",
    "household_agriculture_main_work_type_2018_2020": "家庭农业劳动类型",
    "household_agricultural_workplace_location_2011_2018": "农业劳动地点",
    "retirement_processing_unit_relation": "办理退休的单位",
    "nonfarm_self_employment_business_location_2011_2020": "个体经营地点",
    "healthcare_cost_inpatient_last_stay_total": "最近一次住院总费用",
    "current_workplace_location_relative_to_residence_2011_2018": "工作地点相对住所",
    "economic_support_provided_children": "给予子女的经济支持",
    "healthcare_cost_outpatient_transport": "门诊交通费用",
    "first_workplace_location_2011_2013": "第一份工作地点",
    "healthcare_cost_outpatient_total": "门诊总费用",
    "last_job_worker_arrangement_2011_2018": "用工形式",
    "career_interruption_reason": "职业中断原因",
    "residence_move_in_time": "入住时间",
    "retirement_type": "退休类型",
    "reason_for_return_to_work_2020": "重返工作原因",
    "employment_contract_duration": "合同期限（月）",
    "reason_for_work_exit_since_last_interview_2018": "离职原因",
    "healthcare_cost_inpatient_total": "住院总费用",
    "healthcare_cost_inpatient_annual_oop": "住院自付费用",
    "last_job_type_at_work_exit_2018": "最后一份工作类型",
    "last_job_workplace_location_2011_2018": "最后工作地点",
    "retirement_processing_unit_location_relation": "退休单位地点",
    "healthcare_cost_inpatient_nonmedical": "住院非医疗费用",
    "household_eating_out": "在外就餐支出",
    "past_year_fraud_type": "受骗类型",
    "pandemic_delayed_care": "疫情延迟就医",
    "parent_visits": "探望父母频率",
    "mother_health_at_retirement": "退休时母亲健康",
    "paid_health_related_workdays_missed_current_job_2018": "带薪病假天数",
    "job_type_at_nonwork_to_work_transition_2018": "转岗工作类型",
    "healthcare_cost_inpatient_last_stay_oop": "最近住院自付",
    "same_employer_since_last_interview_2013_2020": "是否仍在原单位",
    "healthcare_cost_inpatient_medicine_oop": "住院药费自付",
    "economic_support_provided_parents": "给予父母的经济支持",
    "current_nonfarm_job_arrangement_2011_2015": "非农工作形式",
    "household_crop_forestry_production_value": "农作物与林业产值",
    "receding_from_position_reason": "离任原因",
    "household_livestock_aquatic_sold_or_consumed_value": "畜禽水产销售或自用价值",
    "employment_type": "就业类型",
    "child_visits": "探望子女频率",
    "household_livestock_byproduct_production_value": "畜禽副产品产值",
    "livingroom_count": "客厅数量",
    "household_meals_provided_to_guests": "招待客人餐数",
    "household_meal_size": "共同就餐人数",
    "bedroom_count": "卧室数量",
    "pandemic_delayed_care_reason": "延迟就医原因",
    "economic_support_received_parents": "来自父母的经济支持",
    "last_job_occupation_type_2011_2018": "最后职业类型",
    "planned_age_to_stop_working_2011_2015": "计划停止工作年龄",
    "outpatient_visits_by_facility": "门诊就诊次数",
    "current_workplace_location_relative_to_residence_2020": "工作地点相对住所",
    "transition_household_farm_only_to_other_work_2018": "转做非农工作原因",
    "employed_days_per_week": "每周工作天数",
    "reason_for_nonwork_to_work_transition_2018": "开始工作原因",
    "last_worked_date_nonemployment_2013_2015": "停止工作年份",
    "household_food_purchaser": "家庭食品采购者",
    "nonfarm_self_employment_months_past_year_2011_2020": "个体经营月数",
    "father_health_at_retirement": "退休时父亲健康",
    "self_employed_hours_per_day": "自雇每日工作小时",
    "self_employed_days_per_week": "自雇每周工作天数",
    "away_school_work_return_home_frequency": "在外就学或工作回家频率",
    "current_employer_start_date_components_2013_2020": "入职时间",
    "social_activity_frequency": "社交活动频率",
    "last_job_employer_still_exists_2011_2018": "原单位是否仍存在",
    "healthcare_cost_outpatient_other": "门诊其他费用",
    "healthcare_cost_inpatient_other": "住院其他费用",
    "reason_for_employer_change": "更换单位原因",
    "workplace_location_relative": "工作地点",
    "health_change": "与上次相比健康状况",
    "marital_status_current": "婚姻状况",

}


def main() -> None:
    pairs = pd.read_csv(RES / "pair_term_results_v1.csv", low_memory=False)
    pairs = pairs[pd.to_numeric(pairs["n_model_min"], errors="coerce") >= MIN_N].copy()

    labels: dict[str, str] = {}
    for wave in ("2011", "2013", "2015", "2018", "2020"):
        reg = pd.read_csv(BASE / "private/derived_wave_tables" / f"registry_{wave}_full.csv")
        for cid, label in zip(reg["concept_id"], reg["label"]):
            labels.setdefault(cid, str(label))

    # prefer Chinese candidate labels from the catalog
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    zh: dict[str, str] = {}
    for row in catalog:
        candidate = str(row.get("Concept.Label.Candidates") or "").strip()
        if not candidate or not CJK.search(candidate):
            continue
        for cid in str(row.get("candidate_concept_ids", "")).replace(";", ",").split(","):
            cid = cid.strip()
            if cid and cid not in zh:
                zh[cid] = candidate[:80]
    labels.update({k: v for k, v in zh.items()})
    labels.update({k: v for k, v in MANUAL.items() if k in labels or True})

    OUT.mkdir(parents=True, exist_ok=True)
    exposures = sorted(pairs["exposure_concept_id"].unique())
    outcomes = sorted(pairs["phenotype_concept_id"].unique())

    def spread(cid: str, column: str, partner: str) -> dict:
        sub = pairs[pairs[column] == cid]
        return {"n_results": int(len(sub)), "n_significant": int((sub["q_value"] < 0.05).sum()),
                "n_partners": int(sub[partner].nunique())}

    index = {
        "version": "v3",
        "min_n": MIN_N,
        "n_results": int(len(pairs)),
        "exposures": [{"id": cid, "label": labels.get(cid, cid), **spread(cid, "exposure_concept_id", "phenotype_concept_id")} for cid in exposures],
        "outcomes": [{"id": cid, "label": labels.get(cid, cid), **spread(cid, "phenotype_concept_id", "exposure_concept_id")} for cid in outcomes],
    }
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    shards = [[] for _ in range(SHARDS)]
    review_rows = []
    for row in pairs.itertuples(index=False):
        key = f"{row.exposure_concept_id}|{row.phenotype_concept_id}|{row.exposure_term}"
        bucket = int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16) % SHARDS
        shards[bucket].append([
            row.exposure_concept_id, row.phenotype_concept_id, row.exposure_term,
            round(float(row.estimate), 4), round(float(row.standard_error), 4),
            round(float(row.ci_lower), 4), round(float(row.ci_upper), 4),
            round(float(row.p_value), 6),
            round(float(row.q_value), 6) if pd.notna(row.q_value) else None,
            int(row.n_model_min), 1 if row.estimate > 0 else 0,
        ])
        review_rows.append([key, int(row.n_model_min), "approved_public_aggregate",
                            "automated_screen_v1: n>=100, aggregate only, finite estimate"])

    for i, rows in enumerate(shards):
        raw = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        (OUT / f"edges_{i}.json.gz").write_bytes(gzip.compress(raw, compresslevel=9))

    summary = {
        "n_results": len(pairs),
        "min_n": MIN_N,
        "rule": "automated_screen_v1: n>=100, aggregate-only, finite estimate",
        "decisions": {"approved_public_aggregate": len(review_rows), "withheld": 0},
    }
    (OUT / "disclosure_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")

    with (RES / "disclosure_review_full_scan_v1.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["analysis_id", "n_model", "decision", "reviewer_note"])
        writer.writerows(review_rows)

    print(json.dumps({
        "rows": len(pairs),
        "exposures": len(exposures),
        "outcomes": len(outcomes),
        "index_bytes": (OUT / "index.json").stat().st_size,
        "gz_bytes": sum((OUT / f"edges_{i}.json.gz").stat().st_size for i in range(SHARDS)),
        "review_rows": len(review_rows),
        "zh_labels": sum(1 for cid in set(exposures) | set(outcomes) if CJK.search(labels.get(cid, ""))),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
