#!/usr/bin/env python3
"""Run the complete protected Wave 2 household-environment/anthropometry family.

The runner uses the official Wave 2 cross-section and Biomarker_weight, a
source-bound age-interval candidate, and community-clustered unstratified WR
Taylor variance. Results and exact QA are written only under PRIVATE_ROOT. The
full registered family is retained and adjusted together; estimates are not
filtered by statistical significance.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import polars as pl
import pyreadstat
import svy

CODE_SCRIPTS = Path.cwd() / "scripts"
if CODE_SCRIPTS.is_dir():
    sys.path.insert(0, str(CODE_SCRIPTS))
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from project_paths import PRIVATE_ROOT, WAVE_DATA_DIR, QA_OUTPUT_DIR, require_private_path


PRIVATE = PRIVATE_ROOT.resolve()
DATA = WAVE_DATA_DIR / "CHARLS_wave2013_person_analytic.dta"
AGE = WAVE_DATA_DIR / "CHARLS_wave2013_age_interval_candidate.dta"
PREPARED_MANIFEST = WAVE_DATA_DIR / "prepared_data_manifest.json"
AGE_QA = QA_OUTPUT_DIR / "wave2_age_interval_candidate_private.json"
WAVE2_AGE_INPUT_QA = QA_OUTPUT_DIR / "wave2_age_input_source_reconciliation_private.json"
OFFICIAL_WAVE2_BUNDLE = PRIVATE / "incoming_2013_official" / "2013_321_CHARLS2013_Dataset.zip"
ANALYSIS_REVIEW = PRIVATE / "analysis_review"
RESULTS = PRIVATE / "results"
QA = PRIVATE / "qa_outputs"

OUTCOMES = {
    "standing_height": "qi002",
    "arm_length": "qj002",
    "knee_height": "qk002",
    "body_weight": "ql002",
    "waist_circumference": "qm002",
}
EXPOSURES: list[tuple[str, str, int, int, str, bool]] = [
    ("running_water_at_residence", "i017", 1, 2, "Yes vs No", False),
    ("piped_gas_access", "i019", 1, 2, "Yes vs No", False),
    ("residential_heating", "i020", 1, 2, "Yes vs No", False),
]
for field, concept, labels in (
    ("i022", "cooking_fuel_main", {1: "Coal", 2: "Natural gas", 3: "Marsh gas",
                                    4: "LPG", 6: "Crop residue/Wood", 7: "Other"}),
    ("i021", "heating_energy", {1: "Solar", 2: "Coal", 3: "Natural gas",
                                 4: "LPG", 6: "Crop residue/Wood", 7: "Other"}),
):
    EXPOSURES.extend(
        (concept, field, code, 5, f"{label} vs Electric", field == "i021")
        for code, label in labels.items()
    )
REGISTERED_K = len(EXPOSURES) * len(OUTCOMES)
EXPECTED_SVY = "0.35.0"
FAMILY_STEM = "wave2013_household_environment_anthropometry"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def protected(path: Path) -> Path:
    result = require_private_path(path)
    if not result.is_relative_to(PRIVATE):
        raise ValueError(f"CHARLS input/output path must remain under the protected root: {result}")
    return result


def check_manifest_bindings() -> dict[str, object]:
    manifest = json.loads(PREPARED_MANIFEST.read_text(encoding="utf-8"))
    wave = {str(row.get("wave")): row for row in manifest.get("waves", [])}
    w2 = wave.get("2013", {})
    expected_data = w2.get("prepared_output", {}).get("sha256")
    if not expected_data or expected_data != sha256(DATA):
        raise ValueError("Wave 2 respondent frame does not match its protected source manifest")
    expected_archive = w2.get("source_archive", {}).get("sha256")
    if not expected_archive or expected_archive != sha256(OFFICIAL_WAVE2_BUNDLE):
        raise ValueError("Wave 2 official bundle does not match its protected preparation manifest")
    age_qa = json.loads(AGE_QA.read_text(encoding="utf-8"))
    if age_qa.get("person_level_candidate_sha256") != sha256(AGE):
        raise ValueError("Wave 2 age candidate does not match its protected QA manifest")
    age_input_qa = json.loads(WAVE2_AGE_INPUT_QA.read_text(encoding="utf-8"))
    if age_qa.get("source_age_input_sha256") != age_input_qa.get("output_sha256"):
        raise ValueError("Wave 2 age candidate is not bound to the source-resolved age input")
    if age_qa.get("age_method_reviewed") is not False or age_qa.get("association_models_fitted") is not False:
        raise ValueError("Unexpected Wave 2 age candidate state")
    return {
        "prepared_manifest_sha256": sha256(PREPARED_MANIFEST),
        "respondent_frame_sha256": sha256(DATA),
        "age_input_sha256": sha256(AGE),
        "age_qa_sha256": sha256(AGE_QA),
        "age_source_qa_sha256": sha256(WAVE2_AGE_INPUT_QA),
    }


def make_family_adjustments(rows: list[dict[str, object]]) -> None:
    p = np.asarray([
        float(row["p_value"]) if row["fit_status"] == "success" else 1.0
        for row in rows
    ])
    order = np.argsort(p)
    harmonic = float(np.sum(1.0 / np.arange(1, len(rows) + 1)))
    raw = p[order] * len(rows) * harmonic / np.arange(1, len(rows) + 1)
    q = np.clip(np.minimum.accumulate(raw[::-1])[::-1], 0.0, 1.0)
    for rank, index in enumerate(order):
        if rows[index]["fit_status"] == "success":
            rows[index]["q_value_by"] = float(q[rank])
            rows[index]["p_bonferroni"] = min(1.0, float(rows[index]["p_value"]) * len(rows))


def load_data(age_bound: str) -> tuple[pl.DataFrame, int]:
    data_cols = list(dict.fromkeys([
        "ID", "crosssection", "Biomarker_weight", "communityID", "ba000_w2_3",
        *[row[1] for row in EXPOSURES], *OUTCOMES.values(),
    ]))
    dta, _ = pyreadstat.read_dta(str(DATA), usecols=data_cols, output_format="polars")
    ages, _ = pyreadstat.read_dta(
        str(AGE), usecols=["ID", "age_at_interview_lower", "age_at_interview_upper"],
        output_format="polars",
    )
    if dta["ID"].n_unique() != dta.height or ages["ID"].n_unique() != ages.height:
        raise ValueError("Wave 2 frame or age-table IDs are not unique")
    if ages.height != dta.height:
        raise ValueError("Wave 2 age table and respondent frame have different row counts")
    data = dta.join(ages, on="ID", how="left", validate="1:1")
    numeric = [col for col in data.columns if col not in {"ID", "communityID"}]
    data = data.with_columns([pl.col(col).cast(pl.Float64, strict=False) for col in numeric])
    if age_bound == "midpoint":
        age_expr = (pl.col("age_at_interview_lower") + pl.col("age_at_interview_upper")) / 2.0
    elif age_bound == "lower":
        age_expr = pl.col("age_at_interview_lower")
    else:
        age_expr = pl.col("age_at_interview_upper")
    data = data.with_columns(
        age_expr.alias("__age"),
        pl.col("communityID").cast(pl.String).alias("__psu"),
        pl.col("Biomarker_weight").alias("__weight"),
        (pl.col("ba000_w2_3") == 2.0).cast(pl.Float64).alias("__female"),
    ).filter(
        (pl.col("crosssection") == 1.0)
        & pl.col("__weight").is_finite()
        & (pl.col("__weight") > 0.0)
        & pl.col("__psu").is_not_null()
    )
    return data, int(data.height)


def result_template(*, concept: str, field: str, code: int, ref: int, contrast: str,
                    outcome: str, outcome_field: str, age_bound: str,
                    pair_n: int, psu_n: int, code_commit: str) -> dict[str, object]:
    model = "M1_age_midpoint_sex" if age_bound == "midpoint" else f"M1_age_{age_bound}_sex_sensitivity"
    return {
        "analysis_id": f"{FAMILY_STEM}:{age_bound}:{concept}:{field}_{code}_vs_{ref}:{outcome}",
        "data_release": "CHARLS_2013", "source_identity_status": "verified_official_source",
        "source_hash_status": "private_local_sha256_recorded", "source_manifest_id": "charls2013_verified_release_20151118",
        "wave": "2013", "target_population": "Wave 2 cross-sectional Biomarker respondents with positive Biomarker_weight; model complete cases",
        "exposure_concept_id": concept, "exposure_variable": field,
        "phenotype_concept_id": outcome, "phenotype_variable": outcome_field,
        "eligibility_rule": "crosssection=1; positive Biomarker_weight; nonmissing communityID; complete exposure, outcome, age interval and interviewer-recorded gender; no age cutoff",
        "model_id": model,
        "estimate_type": "weighted_mean_difference_standardized",
        "contrast": contrast, "multiple_testing_family": f"{FAMILY_STEM}_{age_bound};K={REGISTERED_K}",
        "weight_status": "verified_used", "weight_id": "Biomarker_weight",
        "weight_source": "CHARLS 2013 official Weights.dta; cross-sectional biomarker-response weight",
        "psu_status": "verified_used", "psu_id": "communityID",
        "stratum_status": "not_released", "stratum_id": "",
        "variance_design": "Approximate method: WR Taylor linearization with communityID clusters and no released strata; limitation: official Wave 2 strata and split-community PSU mapping are not released.",
        "exposure_transform": f"{field}={code} vs {ref}; source-documented contrast; heating-energy contrasts restricted to i020=2 questionnaire route",
        "phenotype_transform": "identity; weighted SD standardization among positive-weight Wave 2 cross-sectional biomarker responses; only documented 993/999 nonmeasurement codes excluded",
        "missingness_rule": "pairwise complete case; no imputation; no assay or anthropometry range trimming",
        "comparability_grade": "wave-specific; not pooled",
        "estimability_review_status": "pending", "estimability_review_id": "",
        "fit_status": "inestimable", "fit_message": "", "n_interview": "", "n_eligible": "",
        "n_exposure_valid": "", "n_phenotype_valid": "", "n_pair_complete": pair_n,
        "n_model": "", "n_psu_private": psu_n,
        "standard_error": "", "estimate": "", "ci_lower": "", "ci_upper": "",
        "p_value": "", "q_value_by": "", "p_bonferroni": "",
        "software_versions": f"Python svy {svy.__version__}; commit: {code_commit}",
    }


def run(age_bound: str, code_commit: str) -> dict[str, object]:
    if svy.__version__ != EXPECTED_SVY:
        raise RuntimeError(f"Expected svy {EXPECTED_SVY}, got {svy.__version__}")
    if not re.fullmatch(r"[0-9a-f]{7,40}", code_commit):
        raise ValueError("Pass the full public analysis-code commit SHA")
    binding = check_manifest_bindings()
    config = {
        "status": "user_authorized_internal_analysis",
        "wave": "2013", "family_id": f"{FAMILY_STEM}_{age_bound}", "registered_K": REGISTERED_K,
        "target_frame": "crosssection=1 and positive official Biomarker_weight; no age cutoff",
        "weight": "Biomarker_weight from the official Wave 2 Weights module",
        "psu": "communityID",
        "strata": None,
        "variance": "Approximate method: WR Taylor linearization with communityID clusters and no released strata",
        "variance_limitation": "official Wave 2 strata and split-community PSU mapping are not released",
        "age_field": f"midpoint of protected age interval bounds ({age_bound})",
        "age_domain_filter": None,
        "covariates": ["age", "age squared", "ba000_w2_3 female indicator (2=female, 1=male)"],
        "outcomes": {name: {"field": field, "scale": "identity then weighted SD standardization",
                            "excluded_nonmeasurement_codes": [993, 999]}
                     for name, field in OUTCOMES.items()},
        "exposure_contrasts": [list(item) for item in EXPOSURES],
        "heating_energy_route": "2013 questionnaire: i020=1 skips i021; i020=2 routes to i021",
        "missingness": "pair-complete; no imputation; no range trimming",
        "multiplicity": f"BY and Bonferroni over full K={REGISTERED_K} family within this age specification",
        "code_commit": code_commit,
        "input_bindings_private": binding,
    }
    config_path = protected(ANALYSIS_REVIEW / f"wave2013_anthropometry_{age_bound}_config_private.json")
    config_text = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    if config_path.exists() and config_path.read_text(encoding="utf-8") != config_text:
        raise RuntimeError("A different private config already exists; refusing to overwrite it")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(config_text, encoding="utf-8")
    os.chmod(config_path, 0o600)
    config_sha256 = sha256(config_path)
    data, frame_n = load_data(age_bound)
    rows: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    for outcome, outcome_field in OUTCOMES.items():
        measure_valid = pl.col(outcome_field).is_finite() & ~pl.col(outcome_field).is_in([993.0, 999.0])
        eligible_outcome = data.filter(measure_valid)
        weights_for_sd = np.asarray(eligible_outcome["__weight"].to_list(), dtype=float)
        values_for_sd = np.asarray(eligible_outcome[outcome_field].to_list(), dtype=float)
        mean = float(np.average(values_for_sd, weights=weights_for_sd)) if len(values_for_sd) else math.nan
        sd = float(np.sqrt(np.average((values_for_sd - mean) ** 2, weights=weights_for_sd))) if len(values_for_sd) else math.nan
        for concept, field, code, ref, contrast, heating_route in EXPOSURES:
            exposure_levels = pl.col(field).is_in([float(code), float(ref)])
            route = (pl.col("i020") == 2.0) if heating_route else pl.lit(True)
            domain = (measure_valid & exposure_levels & route
                      & pl.col("__age").is_finite()
                      & pl.col("__female").is_in([0.0, 1.0]))
            prepared = data.with_columns(
                pl.when(measure_valid & math.isfinite(sd) & (sd > 0.0))
                .then((pl.col(outcome_field) - mean) / sd).otherwise(None).alias("__y"),
                domain.fill_null(False).alias("__domain"),
                pl.when(pl.col(field) == float(code)).then(1.0)
                .when(pl.col(field) == float(ref)).then(0.0).otherwise(None).alias("__x"),
                (pl.col("__age") - 60.0).alias("__age_c"),
            ).with_columns((pl.col("__age_c") ** 2).alias("__age_c2"))
            pair = prepared.filter(domain.fill_null(False))
            pair_n = int(pair.height)
            psu_n = int(pair["__psu"].n_unique()) if pair_n else 0
            row = result_template(concept=concept, field=field, code=code, ref=ref,
                                  contrast=contrast, outcome=outcome, outcome_field=outcome_field,
                                  age_bound=age_bound, pair_n=pair_n, psu_n=psu_n,
                                  code_commit=code_commit)
            warning_count = 0
            if pair_n >= 30 and psu_n > 8 and math.isfinite(sd) and sd > 0.0:
                fit_columns = ["__psu", "__weight", "__y", "__domain", "__x", "__age_c", "__age_c2", "__female"]
                sample = svy.Sample(data=prepared.select(fit_columns),
                                    design=svy.Design(psu="__psu", wgt="__weight", wr=True))
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    try:
                        fitted = sample.glm.fit(
                            y="__y", x=["__x", "__age_c", "__age_c2", "__female"],
                            family="gaussian", where=pl.col("__domain"), method="taylor",
                            drop_nulls=True, alpha=0.05,
                        ).to_polars()
                    except Exception as exc:
                        fitted = None
                        row["fit_message"] = str(exc).splitlines()[0][:220]
                    warning_count = len(caught)
                estimate = next((item for item in fitted.to_dicts() if item.get("term") == "__x"), None) if fitted is not None else None
                if estimate:
                    beta, se, low, high, p = [float(estimate[key]) for key in
                                               ("estimate", "std_err", "conf_low", "conf_high", "p_value")]
                    if all(map(math.isfinite, (beta, se, low, high, p))) and se > 0.0:
                        row.update(estimate=beta, standard_error=se, ci_lower=low, ci_upper=high,
                                   p_value=p, fit_status="success", n_model=pair_n,
                                   estimability_review_status="pending")
            rows.append(row)
            diagnostics.append({"analysis_id": row["analysis_id"], "n_pair_complete": pair_n,
                                "n_psu": psu_n, "fit_status": row["fit_status"],
                                "engine_warnings": warning_count})
    if len(rows) != REGISTERED_K or len({row["analysis_id"] for row in rows}) != REGISTERED_K:
        raise RuntimeError("Complete registered K family did not produce unique rows")
    make_family_adjustments(rows)
    RESULTS.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    os.chmod(RESULTS, 0o700); os.chmod(QA, 0o700); os.chmod(ANALYSIS_REVIEW, 0o700)
    suffix = "midpoint_primary" if age_bound == "midpoint" else f"{age_bound}_age_sensitivity"
    result_path = protected(RESULTS / f"2013_household_environment_anthropometry_K{REGISTERED_K}_{suffix}_raw_private.csv")
    qa_path = protected(QA / f"2013_household_environment_anthropometry_K{REGISTERED_K}_{suffix}_private.json")
    fields = list(rows[0])
    with result_path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    os.chmod(result_path, 0o600)
    summary = {
        "scope": "user-authorized protected Wave 2 association analysis",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "wave": "2013", "registered_K": REGISTERED_K,
        "success": sum(row["fit_status"] == "success" for row in rows),
        "inestimable_or_nonconverged": sum(row["fit_status"] != "success" for row in rows),
        "age_bound": age_bound, "age_bound_sensitivity_not_primary": age_bound != "midpoint",
        "frame_rows_after_crosssection_weight_and_psu": frame_n,
        "model": "crosssection=1; positive Biomarker_weight; age interval complete case; no age exclusion; age midpoint/lower/upper plus age squared and interviewer-recorded gender",
        "weight": "CHARLS 2013 official Biomarker_weight; cross-sectional biomarker response weight",
        "variance": "Approximate method: WR Taylor linearization with communityID clusters and no released strata; limitation: official Wave 2 strata and split-community PSU mapping are not released",
        "heating_route": "2013 questionnaire: i020=1 skips i021; i020=2 routes to i021",
        "measurement": "Identity scale; only official 993/999 nonmeasurement codes excluded; no range trimming",
        "multiplicity": f"BY and Bonferroni across the complete K={REGISTERED_K} family for this model specification",
        "code_commit": code_commit, "input_bindings_private": binding,
        "analysis_config_sha256_private": config_sha256,
        "result_sha256_private": sha256(result_path), "result_file_private": result_path.name,
        "diagnostics_private": diagnostics,
        "release_status": "private_internal_results_pending_technical_and_disclosure_review",
    }
    qa_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(qa_path, 0o600)
    return {k: v for k, v in summary.items() if k not in {"diagnostics_private", "input_bindings_private", "result_sha256_private"}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--age-bound", choices=("midpoint", "lower", "upper"), default="midpoint")
    parser.add_argument("--code-commit", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.age_bound, args.code_commit), ensure_ascii=False))
