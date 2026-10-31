#!/usr/bin/env python3
"""Run the registered cross-sectional 2015 household-environment/blood family.

Participant files and exact QA are read/written only under PRIVATE_ROOT. The
2015 heating route differs from 2011/2013/2018: i020=1 proceeds to i021.
"""
from __future__ import annotations

import csv
import argparse
import json
import math
import subprocess
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import polars as pl
import pyreadstat
import svy

from project_paths import PRIVATE_ROOT


PRIVATE = PRIVATE_ROOT
CODE_ROOT = Path(__file__).resolve().parents[1]
DATA = PRIVATE / "derived_wave_tables" / "CHARLS_wave2015_person_analytic_with_official_blood.dta"
RESULT = PRIVATE / "results" / "2015_household_environment_blood_K225_schema_v3.csv"
QA = PRIVATE / "qa_outputs" / "2015_household_environment_blood_K225_private.json"

PHENOTYPES = {
    "blood_wbc": "bl_wbc", "blood_hemoglobin": "bl_hgb",
    "blood_hematocrit": "bl_hct", "blood_mcv": "bl_mcv",
    "blood_platelets": "bl_plt", "blood_triglycerides": "bl_tg",
    "blood_creatinine": "bl_crea", "blood_bun": "bl_bun",
    "blood_hdl": "bl_hdl", "blood_ldl": "bl_ldl",
    "blood_total_cholesterol": "bl_cho", "blood_glucose": "bl_glu",
    "blood_uric_acid": "bl_ua", "blood_crp": "bl_crp",
    "blood_hba1c": "bl_hbalc",
}
EXPOSURES = [
    ("running_water_at_residence", "i017", 1, 2, "Yes vs No", False),
    ("piped_gas_access", "i019", 1, 2, "Yes vs No", False),
    ("residential_heating", "i020", 1, 2, "Yes vs No", False),
]
for field, concept in (("i022", "cooking_fuel_main"), ("i021", "heating_energy")):
    labels = {
        1: "Coal", 2: "Natural gas" if field == "i022" else "Coal",
        3: "Marsh gas" if field == "i022" else "Natural gas", 4: "LPG",
        6: "Crop residue/Wood", 7: "Other",
    }
    EXPOSURES.extend(
        (concept, field, code, 5, f"{label} vs Electric", field == "i021")
        for code, label in labels.items()
    )


def _read_frame() -> tuple[pl.DataFrame, int]:
    fields = list(dict.fromkeys([
        "crosssection", "blood_weight", "communityID", "iyear", "imonth",
        "ba004_w3_1", "ba004_w3_2", "ba000_w2_3", "i017", "i019", "i020",
        "i021", "i022", "bb001_w3_2", "bl_fasting", "bl_top_coding_tg", *PHENOTYPES.values(),
    ]))
    data, _ = pyreadstat.read_dta(str(DATA), usecols=fields, output_format="polars")
    numeric = [field for field in fields if field != "communityID"]
    data = data.with_columns([pl.col(field).cast(pl.Float64, strict=False) for field in numeric])
    data = data.filter(
        (pl.col("crosssection") == 1.0)
        & pl.col("blood_weight").is_finite()
        & (pl.col("blood_weight") > 0.0)
        & pl.col("communityID").is_not_null()
    )
    birth_valid = (
        pl.col("imonth").is_between(1.0, 12.0)
        & pl.col("iyear").is_not_null()
        & pl.col("ba004_w3_1").is_between(1900.0, 2015.0)
        & pl.col("ba004_w3_2").is_between(1.0, 12.0)
    )
    age = pl.col("iyear") - pl.col("ba004_w3_1") - (
        pl.col("imonth") <= pl.col("ba004_w3_2")
    ).cast(pl.Float64)
    data = data.with_columns(
        pl.when(birth_valid).then(age).otherwise(None).alias("__age"),
        pl.col("communityID").cast(pl.String).alias("__psu"),
        pl.col("blood_weight").alias("__weight"),
        (pl.col("ba000_w2_3") == 2.0).cast(pl.Float64).alias("__sex2"),
    ).filter(pl.col("__age").is_not_null())
    return data, data.height


def _result_row(concept: str, field: str, code: int, ref: int, contrast: str,
                outcome: str, outcome_field: str, n: int, code_commit: str,
                settlement_adjusted: bool) -> dict[str, object]:
    return {
        "analysis_id": f"2015_household_environment_K225:{concept}:{field}_{code}_vs_{ref}:{outcome}",
        "data_release": "CHARLS_2015", "source_identity_status": "verified_official_source",
        "source_hash_status": "private_local_sha256_recorded", "source_manifest_id": "charls2015blood_verified",
        "wave": "2015", "target_population": "2015 cross-sectional blood-response sample with positive Blood_weight; age 45+ domain",
        "exposure_concept_id": concept, "exposure_variable": field,
        "phenotype_concept_id": outcome, "phenotype_variable": outcome_field,
        "eligibility_rule": "crosssection=1; positive Blood_weight; age 45+ from ID/hukou date and interview year/month; pair-complete",
        "model_id": "M2_2015_age_sex_settlement_sensitivity" if settlement_adjusted else "M1_2015_age_sex",
        "estimate_type": "weighted_mean_difference_standardized",
        "contrast": contrast, "multiple_testing_family": "wave2015_household_environment_blood;K=225",
        "weight_status": "verified_used", "weight_id": "blood_weight",
        "weight_source": "CHARLS 2015 Blood release", "psu_status": "verified_used",
        "psu_id": "communityID", "stratum_status": "not_released", "stratum_id": "",
        "variance_design": "Approximate method: Taylor linearization WR with communityID clusters and no released strata. Limitation: final split-community PSU map and official strata are not released.",
        "exposure_transform": f"{field}={code} vs {ref}; official category contrast",
        "phenotype_transform": "identity; weighted SD standardization within valid age-domain blood responses",
        "missingness_rule": "pairwise complete case; no imputation; fasting restricted for glucose/triglycerides",
        "comparability_grade": "wave-specific; not pooled", "estimability_review_status": "reviewed_pass",
        "estimability_review_id": "charls_2015_internal_review_20261031", "fit_status": "inestimable",
        "fit_message": "", "n_interview": "", "n_eligible": "", "n_exposure_valid": "",
        "n_phenotype_valid": "", "n_pair_complete": n, "n_model": n,
        "standard_error": "", "estimate": "", "ci_lower": "", "ci_upper": "",
        "p_value": "", "q_value_by": "", "p_bonferroni": "",
        "software_versions": f"Python svy 0.35.0; git commit: {code_commit}",
    }


def run(settlement_adjusted: bool = False) -> dict[str, object]:
    if svy.__version__ != "0.35.0":
        raise RuntimeError(f"Expected svy 0.35.0, got {svy.__version__}")
    code_commit = subprocess.check_output(
        ["git", "-C", str(CODE_ROOT), "rev-parse", "--short", "HEAD"], text=True
    ).strip()
    data, frame_n = _read_frame()
    rows: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    for outcome, outcome_field in PHENOTYPES.items():
        valid = pl.col(outcome_field).is_finite() & (pl.col("__age") >= 45.0)
        fasting = outcome in {"blood_glucose", "blood_triglycerides"}
        if fasting:
            valid &= pl.col("bl_fasting") == 1.0
        reference = data.filter(valid)
        weights = np.asarray(reference["__weight"].to_list(), dtype=float)
        values = np.asarray(reference[outcome_field].to_list(), dtype=float)
        mean = float(np.average(values, weights=weights)) if len(values) else math.nan
        sd = float(np.sqrt(np.average((values - mean) ** 2, weights=weights))) if len(values) else math.nan
        for concept, field, code, ref, contrast, heating_route in EXPOSURES:
            domain = (pl.col("__age") >= 45.0) & pl.col(field).is_in([float(code), float(ref)]) & valid
            # Verified 2015 questionnaire route: Yes (1) proceeds to i021;
            # No (2) skips directly to i022. This differs from 2011/2013/2018.
            if heating_route:
                domain &= pl.col("i020") == 1.0
            prepared = data.with_columns(
                pl.when(valid & (sd > 0)).then((pl.col(outcome_field) - mean) / sd).otherwise(None).alias("__y"),
                domain.fill_null(False).alias("__domain"),
                pl.when(pl.col(field) == float(code)).then(1.0)
                .when(pl.col(field) == float(ref)).then(0.0).otherwise(None).alias("__x"),
                (pl.col("__age") - 60.0).alias("__age_c"),
            )
            pair_rule = domain & pl.col("__y").is_not_null() & pl.col("__sex2").is_not_null()
            model_terms = ["__x", "__age_c", "__age_c2", "__sex2"]
            if settlement_adjusted:
                pair_rule &= pl.col("bb001_w3_2").is_between(1.0, 7.0)
            pair = prepared.filter(pair_rule)
            if settlement_adjusted and pair.height:
                # Keep all supported nominal categories. For a pair where a
                # category is absent, omit only that empty level; use the
                # smallest observed category as the deterministic reference.
                # If exposure and settlement remain collinear, retain the row
                # as inestimable instead of collapsing categories post hoc.
                active_categories = sorted(int(value) for value in pair["bb001_w3_2"].unique().to_list())
                reference_category = active_categories[0] if active_categories else None
                terms = [category for category in active_categories if category != reference_category]
                prepared = prepared.with_columns([
                    pl.when(pl.col("bb001_w3_2").is_between(1.0, 7.0))
                    .then((pl.col("bb001_w3_2") == float(category)).cast(pl.Float64))
                    .otherwise(None).alias(f"__settlement_{category}")
                    for category in terms
                ])
                model_terms.extend(f"__settlement_{category}" for category in terms)
            row = _result_row(concept, field, code, ref, contrast, outcome, outcome_field, pair.height, code_commit, settlement_adjusted)
            warnings_count = 0
            if pair.height >= 30 and pair["__psu"].n_unique() > 8 and math.isfinite(sd) and sd > 0:
                fit_columns = ["__psu", "__weight", "__y", "__domain", *[term for term in model_terms if term != "__age_c2"]]
                fit_data = prepared.select(list(dict.fromkeys(fit_columns)))
                fit_data = fit_data.with_columns((pl.col("__age_c") ** 2).alias("__age_c2"))
                survey = svy.Sample(data=fit_data, design=svy.Design(psu="__psu", wgt="__weight", wr=True))
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    try:
                        fitted = survey.glm.fit(
                            y="__y", x=model_terms,
                            family="gaussian", where=pl.col("__domain"), method="taylor",
                            drop_nulls=True, alpha=0.05,
                        ).to_polars()
                    except svy.errors.model_errors.ModelError as error:
                        fitted = None
                        row["fit_message"] = str(error).splitlines()[0][:240]
                    warnings_count = len(caught)
                fit = next((item for item in fitted.to_dicts() if item.get("term") == "__x"), None) if fitted is not None else None
                if fit:
                    beta, se, low, high, p = [float(fit[key]) for key in ("estimate", "std_err", "conf_low", "conf_high", "p_value")]
                    if all(map(math.isfinite, (beta, se, low, high, p))) and se > 0:
                        row.update(estimate=beta, standard_error=se, ci_lower=low, ci_upper=high,
                                   p_value=p, fit_status="success")
            rows.append(row)
            diagnostics.append({"analysis_id": row["analysis_id"], "n": pair.height,
                                "psu_n": pair["__psu"].n_unique(), "status": row["fit_status"],
                                "warnings": warnings_count})
    pvalues = np.asarray([float(row["p_value"]) if row["fit_status"] == "success" else 1.0 for row in rows])
    order = np.argsort(pvalues)
    harmonic = sum(1 / j for j in range(1, len(rows) + 1))
    raw = pvalues[order] * len(rows) * harmonic / np.arange(1, len(rows) + 1)
    qvalues = np.clip(np.minimum.accumulate(raw[::-1])[::-1], 0, 1)
    for rank, index in enumerate(order):
        if rows[index]["fit_status"] == "success":
            rows[index]["q_value_by"] = float(qvalues[rank])
            rows[index]["p_bonferroni"] = min(1.0, float(rows[index]["p_value"]) * len(rows))
    result_path = RESULT.with_name("2015_household_environment_blood_K225_settlement_sensitivity_schema_v3.csv") if settlement_adjusted else RESULT
    qa_path = QA.with_name("2015_household_environment_blood_K225_settlement_sensitivity_private.json") if settlement_adjusted else QA
    result_path.parent.mkdir(parents=True, exist_ok=True)
    qa_path.parent.mkdir(parents=True, exist_ok=True)
    with result_path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    summary = {
        "created_utc": datetime.now(timezone.utc).isoformat(), "wave": "2015", "registered_K": 225,
        "success": sum(row["fit_status"] == "success" for row in rows),
        "non_success": sum(row["fit_status"] != "success" for row in rows),
        "frame_rows_after_weight_and_age_fields_private": frame_n,
        "model": "blood-weighted outcome SD; age 45+; age linear/quadratic and gender indicator; pair-complete" + ("; nominal bb001_w3_2 categories 2-7 vs category 1" if settlement_adjusted else ""),
        "fasting": "glucose and triglycerides restricted to bl_fasting=1",
        "heating_route": "2015-specific i020=1 Yes proceeds to i021",
        "code_commit": code_commit,
        "variance": "WR Taylor; communityID clusters; no released strata; approximate",
        "diagnostics_private": diagnostics,
    }
    qa_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result_path.chmod(0o600); qa_path.chmod(0o600)
    return {key: value for key, value in summary.items() if key != "diagnostics_private"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--settlement-sensitivity", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(settlement_adjusted=args.settlement_sensitivity), ensure_ascii=False))
