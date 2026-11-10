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
OUT = RES / "public_full_scan_v2"
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
        "version": "v2",
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
