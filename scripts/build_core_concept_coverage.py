"""Build disclosure-safe CHARLS core concept coverage and pairwise N tables.

Only aggregate counts are written to the project directory. Participant-level
values and identifiers remain in the private local data directory.
"""
from pathlib import Path
import argparse
import json

import pandas as pd
import pyreadstat
from project_paths import QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path


WAVES = ["2011", "2013", "2015", "2018", "2020"]
DATA_DEFAULT = WAVE_DATA_DIR
PROJECT = Path(__file__).resolve().parents[1]

# Core v0 concepts. Variables are raw CHARLS fields; their meaning and
# cross-wave caveats are documented in the accompanying concept dictionary.
MAP = {
    "still_smoking_among_ever_smokers": {"2011": "da061", "2013": "da061", "2015": "da061", "2018": "da061", "2020": "da047"},
    "smoke_ever": {"2011": "da059", "2013": "da059", "2015": "da059", "2018": "da059", "2020": "da046"},
    "alcohol_past_year": {"2011": "da067", "2013": "da067", "2015": "da067", "2018": "da067", "2020": "da051"},
    "sleep_hours": {"2011": "da049", "2013": "da049", "2015": "da049", "2018": "da049", "2020": "da030"},
    "sleep_restless": {"2011": "dc015", "2013": "dc015", "2015": "dc015", "2018": "dc015", "2020": "dc022"},
    "vigorous_activity_10min": {"2011": "da051_1_", "2013": "da051_1_", "2015": "da051_1_", "2018": "da051_1_", "2020": "da032_1_"},
    "moderate_activity_10min": {"2011": "da051_2_", "2013": "da051_2_", "2015": "da051_2_", "2018": "da051_2_", "2020": "da032_2_"},
    "depressive_symptom_felt_depressed": {"2011": "dc011", "2013": "dc011", "2015": "dc011", "2018": "dc011", "2020": "dc018"},
    "cooking_fuel_main": {"2011": "i022", "2013": "i022", "2015": "i022", "2018": "i022_w4", "2020": "i021"},
    "running_water_at_residence": {"2011": "i017", "2013": "i017", "2015": "i017", "2018": "i017"},
    "waist_circumference": {"2011": "qm002", "2013": "qm002", "2015": "qm002"},
    "height": {"2011": "qi002", "2013": "qi002", "2015": "qi002", "2018": ""},
    "weight_measurement_eligibility": {"2011": "pl001", "2013": "pl001", "2015": "pl001"},
    "hypertension_diagnosis": {"2011": "da007_1_", "2013": "da007_1_", "2015": "da007_1_", "2018": "da007_1_", "2020": "da003_1_"},
    "diabetes_diagnosis": {"2011": "da007_3_", "2013": "da007_3_", "2015": "da007_3_", "2018": "da007_3_", "2020": "da003_3_"},
    "heart_disease_diagnosis": {"2011": "da007_7_", "2013": "da007_7_", "2015": "da007_7_", "2018": "da007_7_", "2020": "da003_7_"},
    "stroke_diagnosis": {"2011": "da007_8_", "2013": "da007_8_", "2015": "da007_8_", "2018": "da007_8_", "2020": "da003_8_"},
    "arthritis_diagnosis": {"2011": "da007_13_", "2013": "da007_13_", "2015": "da007_13_", "2018": "da007_13_", "2020": "da003_14_"},
    "chronic_lung_disease_diagnosis": {"2011": "da007_5_", "2013": "da007_5_", "2015": "da007_5_", "2018": "da007_5_", "2020": "da003_5_"},
    "dyslipidemia_diagnosis": {"2011": "da007_2_", "2013": "da007_2_", "2015": "da007_2_", "2018": "da007_2_", "2020": "da003_2_"},
    "kidney_disease_diagnosis": {"2011": "da007_9_", "2013": "da007_9_", "2015": "da007_9_", "2018": "da007_9_", "2020": "da003_9_"},
    "blood_glucose_lab": {"2011": "newglu"},
    "hba1c_lab": {"2011": "newhba1c"},
    "total_cholesterol_lab": {"2011": "newcho"},
    "hdl_lab": {"2011": "newhdl"},
    "ldl_lab": {"2011": "newldl"},
    "triglycerides_lab": {"2011": "newtg"},
    "creatinine_lab": {"2011": "newcrea"},
    "crp_lab": {"2011": "newcrp"},
    "bun_lab": {"2011": "newbun"},
    "uric_acid_lab": {"2011": "newua"},
}
ROLE = {k: ("exposure_proxy" if k in {
    "still_smoking_among_ever_smokers", "smoke_ever", "alcohol_past_year", "sleep_hours",
    "sleep_restless", "vigorous_activity_10min", "moderate_activity_10min",
    "cooking_fuel_main", "running_water_at_residence"
} else ("measurement_metadata" if k == "weight_measurement_eligibility" else "phenotype_or_measurement")) for k in MAP}

ZH = {
    "still_smoking_among_ever_smokers": ("既往吸烟者当前是否仍吸烟", "吸烟行为", "需按问卷跳题解释；非吸烟者结构性空缺"),
    "smoke_ever": ("是否曾吸烟", "吸烟行为", "类别编码需按各波代码本统一"),
    "alcohol_past_year": ("过去一年饮酒", "饮酒行为", "频率与是/否问法存在波次差异，分析前二分化并核对代码"),
    "sleep_hours": ("过去一个月夜间实际睡眠时长", "睡眠", "单位/异常值/特殊码复核后按小时统一"),
    "sleep_restless": ("睡眠不安单题", "心理/睡眠", "单题代理，不等于CES-D总分"),
    "vigorous_activity_10min": ("连续至少10分钟剧烈活动", "身体活动", "2013/2015活动模块仅随机抽中约一半家庭；缺失可能为设计性子样本"),
    "moderate_activity_10min": ("连续至少10分钟中等强度活动", "身体活动", "2013/2015活动模块仅随机抽中约一半家庭；缺失可能为设计性子样本"),
    "depressive_symptom_felt_depressed": ("感到抑郁单题", "心理健康", "波次/模块有变化；不得标作标准CES-D总分"),
    "cooking_fuel_main": ("家庭主要烹饪燃料", "家庭环境代理", "需按代码本映射燃料类别，不推断个体污染剂量"),
    "running_water_at_residence": ("住所是否有自来水", "家庭环境代理", "2020 i017含义变化为室内淋浴，故不映射"),
    "waist_circumference": ("腰围实测值", "体格测量", "仅确认2011—2015；统一单位并检查测量质控"),
    "height": ("身高实测值", "体格测量", "2011/2013/2015映射体检问卷QI002（cm）；按代码本排除993/999特殊结果码，2018/2020当前发布文件未见可比实测字段"),
    "weight_measurement_eligibility": ("体重测量资格/质控字段", "测量质控元数据", "不能作为表型结局；仅解释测量缺失"),
    "hypertension_diagnosis": ("医生诊断高血压", "慢病诊断", "2013/2015原da007仅新入样者；重复访谈需合并W2核实/新发分支；2020为da003"),
    "diabetes_diagnosis": ("医生诊断糖尿病/高血糖", "慢病诊断", "2013/2015原da007仅新入样者；重复访谈需合并W2核实/新发分支；2020为da003"),
    "heart_disease_diagnosis": ("医生诊断心脏病", "慢病诊断", "2013/2015需合并W2分支；2020为da003；病种措辞需核对"),
    "stroke_diagnosis": ("医生诊断中风", "慢病诊断", "2013/2015原da007仅新入样者；重复访谈需合并W2核实/新发分支；2020为da003"),
    "arthritis_diagnosis": ("医生诊断关节炎/风湿病", "慢病诊断", "2013/2015原da007仅新入样者；2018 DA007按既往诊断状态路由；2020为da003_14（清单含帕金森病后移一位）"),
    "chronic_lung_disease_diagnosis": ("医生诊断慢性肺病", "慢病诊断", "2013/2015原da007仅新入样者；重复访谈需合并W2核实/新发分支；2020为da003"),
    "dyslipidemia_diagnosis": ("医生诊断血脂异常", "慢病诊断", "2013/2015原da007仅新入样者；重复访谈需合并W2核实/新发分支；2020为da003"),
    "kidney_disease_diagnosis": ("医生诊断肾病", "慢病诊断", "2013/2015原da007仅新入样者；重复访谈需合并W2核实/新发分支；2020为da003"),
    "blood_glucose_lab": ("血糖实测", "血液生化", "当前本地可用血液化验仅2011波"),
    "hba1c_lab": ("糖化血红蛋白实测", "血液生化", "当前本地可用血液化验仅2011波"),
    "total_cholesterol_lab": ("总胆固醇实测", "血液生化", "当前本地可用血液化验仅2011波"),
    "hdl_lab": ("HDL胆固醇实测", "血液生化", "当前本地可用血液化验仅2011波"),
    "ldl_lab": ("LDL胆固醇实测", "血液生化", "当前本地可用血液化验仅2011波"),
    "triglycerides_lab": ("甘油三酯实测", "血液生化", "当前本地可用血液化验仅2011波"),
    "creatinine_lab": ("肌酐实测", "血液生化", "当前本地可用血液化验仅2011波"),
    "crp_lab": ("C反应蛋白实测", "血液生化", "当前本地可用血液化验仅2011波"),
    "bun_lab": ("尿素氮实测", "血液生化", "当前本地可用血液化验仅2011波"),
    "uric_acid_lab": ("尿酸实测", "血液生化", "当前本地可用血液化验仅2011波"),
}


def observed_mask(series):
    """Treat Stata string blanks as missing as well as Stata/numeric missings."""
    return series.notna() & series.astype(str).str.strip().ne("")


def available_mask(concept, wave, series):
    """Apply only explicitly documented special-code rules for core measures."""
    mask = observed_mask(series)
    if concept == "height" and wave in {"2011", "2013", "2015"}:
        # The CHARLS height instrument/codebook permits 0..210 cm and reserves
        # 993/999 for unable/refused; do not treat those codes as measurements.
        numeric = pd.to_numeric(series, errors="coerce")
        mask &= numeric.between(0, 210, inclusive="both")
    return mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, default=DATA_DEFAULT)
    ap.add_argument("--project-dir", type=Path, default=PROJECT)
    ap.add_argument("--output-dir", type=Path, default=QA_OUTPUT_DIR,
                    help="Private local directory for coverage and pair-count QA outputs")
    args = ap.parse_args()
    args.data_dir = require_private_path(args.data_dir)
    args.output_dir = require_private_path(args.output_dir)
    catalog = pd.read_csv(args.project_dir / "audit" / "raw_variable_catalog_v1.csv", low_memory=False)
    catalog["wave"] = catalog.wave.astype(str)
    rows, wave_data, statuses = [], {}, {}
    for wave in WAVES:
        path = args.data_dir / f"CHARLS_wave{wave}_person_analytic.dta"
        _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
        columns = set(meta.column_names)
        requested = sorted({v for concept, mapping in MAP.items() for w, v in mapping.items() if w == wave and v in columns})
        data, _ = pyreadstat.read_dta(str(path), usecols=["ID"] + requested)
        wave_data[wave] = data
        for concept, mapping in MAP.items():
            var = mapping.get(wave)
            status = "not_measured_in_wave" if not var else ("variable_not_in_prepared_table" if var not in columns else "measured")
            statuses[(wave, concept)] = status
            label_rows = catalog[(catalog.wave == wave) & (catalog.variable == var)] if var else catalog.iloc[0:0]
            label = " | ".join(label_rows.variable_label.dropna().astype(str).drop_duplicates().tolist())
            module = " | ".join(label_rows.module.dropna().astype(str).drop_duplicates().tolist())
            n_nonmissing = int(available_mask(concept, wave, data[var]).sum()) if status == "measured" else None
            rows.append({"concept_id": concept, "role": ROLE[concept], "wave": wave,
                         "raw_variable": var or "", "raw_label": label, "module": module,
                         "status": status, "respondent_rows": len(data),
                         "n_nonmissing": n_nonmissing,
                         "coverage_pct": round(100*n_nonmissing/len(data), 2) if n_nonmissing is not None else None})
    concept_df = pd.DataFrame(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    concept_df.to_csv(args.output_dir / "core_concept_coverage_v1.csv", index=False, encoding="utf-8-sig")
    dictionary = pd.DataFrame([{"concept_id": k, "role": ROLE[k], "concept_zh": ZH[k][0],
                                "domain": ZH[k][1], "harmonization_caveat": ZH[k][2]}
                               for k in MAP])
    dictionary.to_csv(args.output_dir / "core_concept_dictionary_v1.csv", index=False, encoding="utf-8-sig")

    exposure_ids = [k for k, role in ROLE.items() if role == "exposure_proxy"]
    outcome_ids = [k for k, role in ROLE.items() if role == "phenotype_or_measurement"]
    pair_rows = []
    for wave in WAVES:
        data = wave_data[wave]
        for exp in exposure_ids:
            ev = MAP[exp].get(wave)
            for out in outcome_ids:
                ov = MAP[out].get(wave)
                es = statuses[(wave, exp)]; os = statuses[(wave, out)]
                if es == "measured" and os == "measured":
                    n = int((available_mask(exp, wave, data[ev]) & available_mask(out, wave, data[ov])).sum())
                    status = "pair_observed"
                else:
                    n = None
                    status = "exposure_" + es if es != "measured" else "outcome_" + os
                pair_rows.append({"wave": wave, "exposure_concept": exp, "exposure_variable": ev or "",
                                  "outcome_concept": out, "outcome_variable": ov or "",
                                  "status": status, "n_complete_pair": n})
    pair_df = pd.DataFrame(pair_rows)
    pair_df.to_csv(args.output_dir / "core_pairwise_complete_n_v1.csv", index=False, encoding="utf-8-sig")
    wave_summary = []
    for wave in WAVES:
        cc = concept_df[concept_df.wave == wave]
        pp = pair_df[(pair_df.wave == wave) & (pair_df.status == "pair_observed")]
        ex_measured = cc[(cc.role == "exposure_proxy") & (cc.status == "measured")].concept_id.nunique()
        outcome_measured = cc[(cc.role == "phenotype_or_measurement") & (cc.status == "measured")].concept_id.nunique()
        wave_summary.append({"wave": wave, "respondent_rows": int(cc.respondent_rows.iloc[0]),
                             "measured_exposure_proxy_concepts": ex_measured,
                             "measured_phenotype_concepts": outcome_measured,
                             "observed_exposure_phenotype_pairs": len(pp),
                             "pair_n_min": int(pp.n_complete_pair.min()) if len(pp) else None,
                             "pair_n_median": float(pp.n_complete_pair.median()) if len(pp) else None,
                             "pair_n_max": int(pp.n_complete_pair.max()) if len(pp) else None})
    pd.DataFrame(wave_summary).to_csv(args.output_dir / "core_wave_pair_summary_v1.csv", index=False, encoding="utf-8-sig")
    summary = concept_df.groupby(["role", "wave", "status"], dropna=False).size().reset_index(name="concept_count")
    summary.to_csv(args.output_dir / "core_concept_status_summary_v1.csv", index=False, encoding="utf-8-sig")
    (args.output_dir / "core_coverage_build_metadata_v1.json").write_text(json.dumps({
        "waves": WAVES, "concepts": len(MAP), "exposure_proxy_concepts": len(exposure_ids),
        "phenotype_or_measurement_concepts": len(outcome_ids), "pair_rows": len(pair_rows),
        "privacy": "aggregate counts only; participant-level records remain outside synchronized project directory",
        "interpretation": "nonmissing counts and pairwise complete counts describe data availability, not analytic sample after eligibility, weights, QC, or model-specific exclusions"
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"concepts={len(MAP)} pair_rows={len(pair_rows)}")
    print(concept_df.groupby(["wave", "status"]).size().to_string())


if __name__ == "__main__":
    main()
