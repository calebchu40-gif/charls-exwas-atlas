#!/usr/bin/env python3
"""Run a protected, exploratory CHARLS Wave 1 survey-weighted pilot.

Reads only selected fields from the locally prepared 2011 respondent table and
the protected provisional age file. All participant-level inputs and outputs
stay under LOCALAPPDATA/CHARLS_ExWAS_Atlas. No files are written to the repo.

The local PSU key mapping is checked against the protected Wave 1 psu.dta
file, but exact release provenance, blood-weight source identity, and
variance-stratum/split-community interpretation are not authenticated.
Estimates remain exploratory and use an unstratified with-replacement PSU
Taylor approximation. They are not public or release-ready results.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import polars as pl
import pyreadstat
import svy

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CHARLS_ExWAS_Atlas"
DATA = PRIVATE / "derived_wave_tables" / "CHARLS_wave2011_person_analytic.dta"
AGE = PRIVATE / "age_candidates" / "age_candidate_2011.dta"
PSU_MAP = PRIVATE / "raw_extract_2011_community" / "psu.dta"
OUT = PRIVATE / "pilot_2011_water_blood"
CROSSWALK = ROOT / "audit" / "blood_biomarker_crosswalk_v1.csv"
EXPECTED_SVY = "0.35.0"
EXPOSURE = "running_water_at_residence"
EXPOSURE_FIELD = "i017"
COOKING_FIELD = "i022"
WEIGHT_FIELD = "bloodweight"
PSU_FIELD = "communityID"
SEX_FIELD = "rgender"
EDUCATION_FIELD = "bd001"
URBAN_FIELD = "urban_nbs"
AGE_FIELD = "age_years_candidate"
AGE_SOURCE = "Harmonized CHARLS D-derived candidate; provisional covariate"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def private_path(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(PRIVATE.resolve()):
        raise ValueError(f"Refusing to write outside protected local path: {resolved}")
    if any(part.casefold() in {"onedrive", "dropbox", "googledrive", "icloud"} for part in resolved.parts):
        raise ValueError("Refusing synchronized storage for CHARLS data or analysis outputs")
    return resolved


def read_analytes() -> list[dict[str, str]]:
    with CROSSWALK.open(newline="", encoding="utf-8-sig") as stream:
        rows = [r for r in csv.DictReader(stream) if r["wave"] == "2011"]
    # Cystatin C has an age-stratified assay subsample whose selection
    # probability/weight is not established in the available release notes.
    rows = [
        r for r in rows
        if r["concept_id"] not in {"blood_cystatin_c", "blood_collection_metadata"}
    ]
    if len(rows) != 15:
        raise RuntimeError(f"Expected 15 non-cystatin 2011 analytes, found {len(rows)}")
    return rows


def read_input(analytes: list[dict[str, str]]) -> pl.DataFrame:
    if not DATA.is_file() or not AGE.is_file() or not PSU_MAP.is_file():
        raise FileNotFoundError("Protected 2011 prepared table, age candidate, or PSU map is missing")
    fields = ["ID", EXPOSURE_FIELD, COOKING_FIELD, WEIGHT_FIELD, PSU_FIELD, SEX_FIELD,
              EDUCATION_FIELD, URBAN_FIELD]
    fields.extend(r["variable"] for r in analytes)
    fields = list(dict.fromkeys(fields))
    person, meta = pyreadstat.read_dta(str(DATA), usecols=fields, output_format="polars")
    if person.height == 0 or person["ID"].null_count() or person["ID"].n_unique() != person.height:
        raise ValueError("Prepared Wave 1 table must be nonempty with unique, nonmissing respondent IDs")
    psu_map, _ = pyreadstat.read_dta(
        str(PSU_MAP), usecols=[PSU_FIELD], output_format="polars"
    )
    if (psu_map.height == 0 or psu_map[PSU_FIELD].null_count()
            or psu_map[PSU_FIELD].n_unique() != psu_map.height):
        raise ValueError("Protected Wave 1 PSU map must have unique, nonmissing community keys")
    if person.join(
        psu_map.select(PSU_FIELD).unique(), on=PSU_FIELD, how="anti"
    ).height:
        raise ValueError("Prepared respondent table has a community key absent from the PSU map")
    age, _ = pyreadstat.read_dta(
        str(AGE), usecols=["ID", AGE_FIELD], output_format="polars"
    )
    if age["ID"].null_count() or age["ID"].n_unique() != age.height:
        raise ValueError("Protected age candidate ID integrity check failed")
    joined = person.join(age, on="ID", how="left", validate="1:1")
    if joined.height != person.height:
        raise ValueError("Age join changed the respondent row count")

    def numeric(name: str) -> pl.Expr:
        value = pl.col(name).cast(pl.Float64, strict=False)
        return pl.when(value.is_finite()).then(value).otherwise(None).alias(name)

    joined = joined.with_columns(
        numeric(EXPOSURE_FIELD), numeric(COOKING_FIELD), numeric(WEIGHT_FIELD), numeric(SEX_FIELD),
        numeric(EDUCATION_FIELD), numeric(URBAN_FIELD),
        numeric(AGE_FIELD), *(numeric(r["variable"]) for r in analytes),
    )
    water = pl.col(EXPOSURE_FIELD)
    joined = joined.with_columns(
        pl.when(water == 1).then(1.0)
        .when(water == 2).then(0.0)
        .otherwise(None).alias("water_yes"),
        pl.when(pl.col(COOKING_FIELD).is_between(1, 7, closed="both"))
        .then(pl.col(COOKING_FIELD).cast(pl.Int8)).otherwise(None)
        .alias("cooking_fuel_code"),
        pl.when(pl.col(WEIGHT_FIELD).is_not_null() & (pl.col(WEIGHT_FIELD) > 0))
        .then(pl.col(WEIGHT_FIELD)).otherwise(0.0).alias("analysis_weight"),
        pl.when(pl.col(SEX_FIELD) == 2).then(1.0)
        .when(pl.col(SEX_FIELD) == 1).then(0.0)
        .otherwise(None).alias("female"),
        pl.when(pl.col(EDUCATION_FIELD) == 1).then(1)
        .when(pl.col(EDUCATION_FIELD).is_between(2, 4, closed="both")).then(2)
        .when(pl.col(EDUCATION_FIELD) == 5).then(3)
        .when(pl.col(EDUCATION_FIELD).is_between(6, 11, closed="both")).then(4)
        .otherwise(None).cast(pl.Int8).alias("education_group"),
        pl.when(pl.col(URBAN_FIELD).is_in([0.0, 1.0]))
        .then(pl.col(URBAN_FIELD)).otherwise(None).alias("urban"),
    ).with_columns(
        (pl.col(AGE_FIELD) - 60.0).alias("age_c"),
        ((pl.col(AGE_FIELD) - 60.0) ** 2).alias("age_c2"),
        pl.col(PSU_FIELD).cast(pl.String).alias("psu"),
    )
    # Drop the participant key before handing the analysis frame to the engine.
    return joined.drop(["ID", EXPOSURE_FIELD, WEIGHT_FIELD, SEX_FIELD,
                        EDUCATION_FIELD, URBAN_FIELD, PSU_FIELD, COOKING_FIELD])


def as_num(value: object) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if np.isfinite(number) else None


def model_rows(data: pl.DataFrame, analyte: dict[str, str], model_id: str) -> tuple[dict[str, object], dict[str, object]]:
    outcome = analyte["variable"]
    domain = (
        (pl.col(AGE_FIELD) >= 45)
        & (pl.col("analysis_weight") > 0)
        & pl.col("water_yes").is_not_null()
    )
    if model_id == "M0":
        xvars = ["water_yes"]
    elif model_id == "M1":
        xvars = ["water_yes", "age_c", "age_c2", "female"]
    else:
        xvars = ["water_yes", "age_c", "age_c2", "female",
                 "education_2", "education_3", "education_4", "urban"]
    pair_domain = data.filter(domain & pl.col(outcome).is_not_null())
    if model_id in {"M1", "M2"}:
        pair_domain = pair_domain.filter(pl.col("age_c").is_not_null() & pl.col("female").is_not_null())
    if model_id == "M2":
        pair_domain = pair_domain.filter(pl.col("education_group").is_not_null() & pl.col("urban").is_not_null())
        pair_domain = pair_domain.with_columns(
            (pl.col("education_group") == 2).cast(pl.Float64).alias("education_2"),
            (pl.col("education_group") == 3).cast(pl.Float64).alias("education_3"),
            (pl.col("education_group") == 4).cast(pl.Float64).alias("education_4"),
        )
        # Restore the complete design frame after creating factor indicators.
        # The model data are formed from the full design below; category
        # indicators are generated there from the same verified grouping.
        data = data.with_columns(
            (pl.col("education_group") == 2).cast(pl.Float64).alias("education_2"),
            (pl.col("education_group") == 3).cast(pl.Float64).alias("education_3"),
            (pl.col("education_group") == 4).cast(pl.Float64).alias("education_4"),
        )
    model_complete = domain
    if model_id in {"M1", "M2"}:
        model_complete = model_complete & pl.col("age_c").is_not_null() & pl.col("female").is_not_null()
    if model_id == "M2":
        model_complete = model_complete & pl.col("education_group").is_not_null() & pl.col("urban").is_not_null()
    pair_domain = data.filter(model_complete & pl.col(outcome).is_not_null())
    w_for_sd = np.asarray(pair_domain["analysis_weight"].to_list(), dtype=float)
    y_for_sd = np.asarray(pair_domain[outcome].to_list(), dtype=float)
    if not len(y_for_sd) or w_for_sd.sum() <= 0:
        raise RuntimeError(f"No eligible complete cases for {outcome}/{model_id}")
    weighted_mean = float(np.average(y_for_sd, weights=w_for_sd))
    weighted_sd = float(np.sqrt(np.average(np.square(y_for_sd - weighted_mean), weights=w_for_sd)))
    if not np.isfinite(weighted_sd) or weighted_sd <= 0:
        raise RuntimeError(f"Outcome has no positive weighted SD for {outcome}/{model_id}")
    data = data.with_columns(((pl.col(outcome) - weighted_mean) / weighted_sd).alias("outcome_z"))
    fit = svy.Sample(
        data=data,
        design=svy.Design(psu="psu", wgt="analysis_weight", wr=True),
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = fit.glm.fit(
            y="outcome_z", x=xvars, family="gaussian", where=domain,
            drop_nulls=True, alpha=0.05,
        ).to_polars()
    record = next((r for r in result.to_dicts() if r.get("term") == "water_yes"), None)
    if record is None:
        raise RuntimeError(f"Engine omitted exposure term for {outcome}/{model_id}")

    # Private pair-level diagnostics; no respondent identifiers or values.
    group_support = (
        pair_domain.group_by("water_yes")
        .agg(pl.len().alias("n"), pl.col("psu").n_unique().alias("psus"))
        .sort("water_yes").to_dicts()
    )
    weight = np.asarray(pair_domain["analysis_weight"].to_list(), dtype=float)
    ess = float(weight.sum() ** 2 / np.square(weight).sum()) if np.square(weight).sum() > 0 else None
    estimate = as_num(record.get("estimate"))
    se = as_num(record.get("std_err"))
    low = as_num(record.get("conf_low"))
    high = as_num(record.get("conf_high"))
    pvalue = as_num(record.get("p_value"))
    df = as_num(record.get("df"))
    if all(v is not None for v in (estimate, se, low, high, pvalue, df)) and se and se > 0 and df and df > 0:
        raw = [v * weighted_sd if v is not None else None for v in (estimate, se, low, high)]
    else:
        raw = [None, None, None, None]
    rows = {
        "wave": "2011", "exposure_concept_id": EXPOSURE,
        "exposure_variable": EXPOSURE_FIELD,
        "phenotype_concept_id": analyte["concept_id"],
        "phenotype_label": analyte["concept_label"],
        "phenotype_variable": outcome, "unit": analyte["unit"],
        "model_id": model_id,
        "contrast": "Residence has running water: Yes (1) vs No (0)",
        "estimate": estimate, "standard_error": se,
        "ci_lower": low, "ci_upper": high,
        "estimate_unit_scale": raw[0], "standard_error_unit_scale": raw[1],
        "ci_lower_unit_scale": raw[2], "ci_upper_unit_scale": raw[3],
        "weighted_outcome_sd": weighted_sd,
        "p_value": pvalue, "design_df": df,
        "n_model": pair_domain.height,
        "n_psu": pair_domain["psu"].n_unique(),
        "kish_effective_n": ess,
        "exposure_group_support_private": json.dumps(group_support, separators=(",", ":")),
        "engine_warnings_private": " | ".join(str(w.message) for w in caught),
        "fit_status": "provisional_exploratory" if pvalue is not None else "numerically_unavailable",
        "design_note": "bloodweight + candidate communityID PSU; with-replacement unstratified Taylor approximation; not full design variance",
    }
    return rows, {"n_eligible": data.filter(domain).height}


def main() -> None:
    if getattr(svy, "__version__", None) != EXPECTED_SVY:
        raise RuntimeError(f"Expected svy {EXPECTED_SVY}, found {getattr(svy, '__version__', 'unknown')}")
    if not PRIVATE.is_dir():
        raise FileNotFoundError("Protected local CHARLS workspace not found")
    OUT.mkdir(parents=True, exist_ok=True)
    analytes = read_analytes()
    data = read_input(analytes)

    results: list[dict[str, object]] = []
    private_qa: list[dict[str, object]] = []
    for analyte in analytes:
        outcome = analyte["variable"]
        # Impossible negative lab values are excluded; no distribution-based
        # trimming or outlier winsorization is performed.
        data = data.with_columns(
            pl.when(pl.col(outcome) >= 0).then(pl.col(outcome)).otherwise(None).alias(outcome)
        )
        for model_id in ("M0", "M1", "M2"):
            row, qa = model_rows(data, analyte, model_id)
            results.append(row)
            private_qa.append({"phenotype_variable": outcome, "model_id": model_id, **qa,
                               "exposure_group_support_private": row["exposure_group_support_private"],
                               "engine_warnings_private": row["engine_warnings_private"]})

    adjust = __import__("adjust_exwas_pvalues").adjust_pvalues
    for model_id in ("M1", "M2"):
        family = [r for r in results if r["model_id"] == model_id]
        adj = adjust([as_num(r["p_value"]) for r in family])
        family_id = f"pilot_2011_water_biomarkers_{model_id};K=15"
        for row, q, bonf in zip(family, adj["q_value_by"], adj["p_bonferroni"], strict=True):
            row["multiple_testing_family"] = family_id
            row["q_value_by"] = q
            row["p_bonferroni"] = bonf
    primary = [r for r in results if r["model_id"] == "M1"]

    input_hash = sha256(DATA)
    age_hash = sha256(AGE)
    psu_hash = sha256(PSU_MAP)
    stamp = datetime.now(timezone.utc).isoformat()
    manifest = {
        "run_utc": stamp,
        "analysis": "Exploratory 2011 cross-sectional water-access proxy × 15 blood analytes",
        "prepared_frame_rows": int(data.height),
        "prepared_frame_unique_psu_keys": int(data["psu"].n_unique()),
        "official_frame_denominator_reconciled": False,
        "provisional_analysis_domain": "age >=45 subpopulation within the full 2011 main-respondent/spouse blood-target frame, with valid water response and positive bloodweight; not a validated national estimand until exact source fields and design are verified",
        "age_domain_method": "official-guide-based direction: create the survey design on the complete blood-target frame, then apply age >=45 through the estimator domain/where condition; do not prefilter younger spouses before design creation",
        "target_population_gate": "Open for source validation: official guides support a 45+ domain within the main-respondent/spouse blood frame, but exact age/relationship eligibility, released bloodweight coverage, and final PSU/variance design must be verified against the authorized release.",
        "exposure": "i017, 1=Yes, 2=No; official household questionnaire wording; contrast Yes vs No",
        "phenotypes": [r["concept_id"] for r in analytes],
        "excluded_phenotype": "blood_cystatin_c: age-stratified assay subsample and selection-weight applicability unresolved",
        "weight": "bloodweight; baseline blood-response weight candidate, pending independent source-archive identity/hash confirmation",
        "psu": "communityID validated as a unique key in the local 450-row psu.dta mapping and all prepared Wave 1 respondent keys map to it; source archive identity/checksum and split-community interpretation remain unauthenticated",
        "variance": "unstratified with-replacement PSU Taylor approximation; exploratory only; official implicit stratification not represented",
        "outcome_scale": "Primary estimates use each pair/model's bloodweight-weighted outcome SD; raw-unit estimates are retained alongside them.",
        "education": "2011 official bd001 grouped for sensitivity: 1=no formal education; 2-4=below/mid-primary and sishu; 5=middle school; 6-11=high school/vocational/tertiary.",
        "urban_covariate": "2011 PSU-map urban_nbs: 0=rural, 1=urban; used as a contextual covariate only, never as a variance stratum.",
        "models": {
            "M0": "water exposure only",
            "M1": "water exposure + centered age + centered age squared + sex (primary)",
            "M2": "M1 + NBS urban/rural context + grouped official baseline education (sensitivity)",
        },
        "missingness": "Only i017 codes 1/2 treated as valid; nonpositive lab values excluded as physically invalid; remaining missing values handled as complete-case in the model while retaining the full design frame.",
        "age_covariate_source": AGE_SOURCE,
        "multiplicity": "M1 family fixed before fitting at K=15; report BY-FDR and Bonferroni; M0 is descriptive only.",
        "data_sha256": input_hash,
        "age_candidate_sha256": age_hash,
        "psu_map_sha256": psu_hash,
        "code_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip(),
        "runtime": sys.version,
        "svy_version": getattr(svy, "__version__", "unknown"),
        "public_release": False,
        "disclosure": "Outputs are stored only in the protected local workspace and are not copied to repository/GitHub/Pages.",
        "status": "pilot estimates are not release-ready; per-pair estimability/source-design review remains required",
    }
    private_path(OUT)
    with (OUT / "pilot_results_private.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        fields = sorted({key for row in results for key in row})
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(results)
    with (OUT / "pilot_pair_qa_private.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        fields = sorted({key for row in private_qa for key in row})
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(private_qa)
    (OUT / "pilot_run_manifest_private.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "run": "complete",
        "rows": len(results),
        "primary_hypotheses": len(primary),
        "fit_pvalues": sum(r["p_value"] is not None for r in primary),
        "models": ["M0", "M1", "M2"],
        "results_path": str(OUT / "pilot_results_private.csv"),
        "public_release": False,
        "design_status": manifest["status"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
