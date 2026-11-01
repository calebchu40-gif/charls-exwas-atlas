#!/usr/bin/env python3
"""Freeze and run private Wave 4/5 household-environment × disease families.

All participant-level reads, joined frames, exact QA, and estimates are confined
to CHARLS_EXWAS_PRIVATE_ROOT. `--freeze` writes a hash-bound complete register;
`--run` executes every registered row without significance-based filtering.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import polars as pl
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path
from derive_wave45_chronic_disease_outcomes import DISEASES
import exwas_engine as engine
from charls_design_keys import add_documented_county_cluster

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = PRIVATE_ROOT.resolve()
TABLES = PRIVATE / "derived_wave_tables"
REVIEW = PRIVATE / "analysis_review" / "wave45_environment_disease_v3_county_stage"
QA = PRIVATE / "qa_outputs"
BASE = ("ID", "crosssection", "INDV_weight_ad2", "householdID", "communityID")
MODELS = ("M0_unadjusted", "M1_age_sex_residence")
VARIANCE = (
    "Approximate with-replacement Taylor linearization clustered at the officially documented county stage; "
    "released data do not provide implicit strata or county FPC; community-cluster sensitivity retained."
)
COMMUNITY_SENSITIVITY_VARIANCE = (
    "Preplanned variance sensitivity: with-replacement Taylor linearization clustered at communityID; "
    "the official hierarchy documents county-level PPS before community PSUs, so this is a lower-stage "
    "cluster comparison rather than the primary variance specification."
)
MIN_MODEL_N = 500
MIN_MODEL_PSU = 30

EXPOSURES: dict[str, list[dict[str, Any]]] = {
    "2018": [
        {"id": "electricity", "field": "i016", "label": "Electricity access", "type": "binary", "codes": {"yes": 1, "no": 2}},
        {"id": "running_water", "field": "i017", "label": "Running water at residence", "type": "binary", "codes": {"yes": 1, "no": 2}},
        {"id": "gas_supply", "field": "i019", "label": "Coal or natural gas supply", "type": "binary", "codes": {"yes": 1, "no": 2}},
        {"id": "residential_heating", "field": "i020", "label": "Heating at residence", "type": "binary", "codes": {"yes": 1, "no": 2}},
        *[{"id": f"cooking_fuel_{name}", "field": "i022_w4", "label": f"Main cooking fuel: {name} vs electric", "type": "fuel", "case": code, "reference": 5}
          for name, code in (("coal", 1), ("natural_gas", 2), ("marsh_gas", 3), ("lpg", 4), ("crop_wood", 6), ("other", 7))],
    ],
    "2020": [
        {"id": "electricity", "field": "i015", "label": "Electricity access", "type": "binary", "codes": {"yes": 1, "no": 2}},
        {"id": "running_water", "field": "i016", "label": "Tap water at residence", "type": "binary", "codes": {"yes": 1, "no": 2}},
        {"id": "gas_supply", "field": "i018", "label": "Coal or natural gas supply", "type": "binary", "codes": {"yes": 1, "no": 2}},
        {"id": "residential_heating", "field": "i019", "label": "Centralized heating", "type": "binary", "codes": {"yes": 1, "no": 2}},
        *[{"id": f"cooking_fuel_{name}", "field": "i021", "label": f"Main cooking fuel: {name} vs electric", "type": "fuel", "case": code, "reference": 5}
          for name, code in (("coal", 1), ("natural_gas", 2), ("marsh_gas", 3), ("lpg", 4), ("crop_wood", 6), ("other", 8))],
        {"id": "cooking_fuel_solar", "field": "i021", "label": "Main cooking fuel: solar vs electric (Wave 5 only)", "type": "fuel", "case": 7, "reference": 5},
    ],
}

def private_path(path: Path) -> Path:
    result = require_private_path(path)
    if not result.is_relative_to(PRIVATE):
        raise ValueError(f"Path escaped protected storage: {result}")
    return result


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json_private(path: Path, obj: dict[str, Any]) -> None:
    path = private_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def _source_binding(wave: str) -> dict[str, str]:
    manifest_path = private_path(TABLES / "prepared_data_manifest.json")
    table_path = private_path(TABLES / f"CHARLS_wave{wave}_person_analytic.dta")
    age_path = private_path(TABLES / f"CHARLS_wave{wave}_age_candidate_private.dta")
    age_qa = private_path(QA / f"wave{wave}_age_candidate_private.json")
    outcome_path = private_path(TABLES / f"CHARLS_wave{wave}_doctor_diagnosis_outcomes_route_derived.dta")
    outcome_qa = private_path(QA / f"wave{wave}_doctor_diagnosis_outcome_routes_private.json")
    validation = private_path(QA / f"wave{wave}_derived_outcome_validation_private.json")
    age_report = json.loads(age_qa.read_text(encoding="utf-8"))
    outcome_report = json.loads(outcome_qa.read_text(encoding="utf-8"))
    outcome_validation = json.loads(validation.read_text(encoding="utf-8"))
    if age_report.get("result_sha256_private") != sha256(age_path):
        raise ValueError(f"Wave {wave}: age candidate hash binding failed")
    if outcome_report.get("result_sha256_private") != sha256(outcome_path):
        raise ValueError(f"Wave {wave}: outcome derivation hash binding failed")
    if outcome_validation.get("status") != "passed" or outcome_validation.get("output_sha256_private") != sha256(outcome_path):
        raise ValueError(f"Wave {wave}: outcome readback validation binding failed")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = [x for x in manifest.get("waves", []) if str(x.get("wave")) == wave]
    if len(records) != 1 or records[0].get("prepared_output", {}).get("sha256") != sha256(table_path):
        raise ValueError(f"Wave {wave}: prepared-table manifest binding failed")
    return {"prepared_manifest_sha256": sha256(manifest_path), "prepared_table_sha256": sha256(table_path),
            "age_candidate_sha256": sha256(age_path), "age_qa_sha256": sha256(age_qa),
            "outcome_table_sha256": sha256(outcome_path), "outcome_qa_sha256": sha256(outcome_qa),
            "outcome_validation_sha256": sha256(validation)}


def _hypothesis_rows(wave: str) -> list[dict[str, str]]:
    rows = []
    for exposure in EXPOSURES[wave]:
        for concept, label, _ in DISEASES[wave]:
            for model in MODELS:
                rows.append({"wave": wave, "family_id": f"wave{wave}_environment_disease_{model}",
                             "family_size": str(len(EXPOSURES[wave]) * len(DISEASES[wave])),
                             "analysis_id": f"{wave}:{exposure['id']}:{concept}:{model}",
                             "exposure_concept_id": exposure["id"], "exposure_source_field": exposure["field"],
                             "exposure_definition": exposure["label"], "phenotype_concept_id": concept,
                             "phenotype_label": label, "phenotype_definition": "cumulative doctor-diagnosed disease history; not incident disease",
                             "model_id": model, "analysis_status": "registered_not_yet_run",
                             "public_release_status": "not_approved"})
    return rows


def freeze(code_commit: str) -> dict[str, Any]:
    if len(code_commit) not in range(7, 41) or any(ch not in "0123456789abcdef" for ch in code_commit):
        raise ValueError("Pass the public analysis-code commit SHA")
    REVIEW.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        os.chmod(REVIEW, 0o700)
    register_path = private_path(REVIEW / "wave45_hypothesis_register_v1.csv")
    plan_path = private_path(REVIEW / "wave45_analysis_plan_v1.json")
    manifest_path = private_path(REVIEW / "wave45_freeze_manifest_v1.json")
    prior_freeze = None
    if any(path.exists() for path in (register_path, plan_path, manifest_path)):
        if not all(path.is_file() for path in (register_path, plan_path, manifest_path)):
            raise ValueError("Partial prior freeze detected; refusing to replace it")
        prior_freeze = json.loads(manifest_path.read_text(encoding="utf-8"))
        if prior_freeze.get("status") != "frozen_for_internal_execution":
            raise ValueError("Unrecognized prior freeze; refusing to replace it")
        for wave in ("2018", "2020"):
            if private_path(PRIVATE / "results" / f"wave{wave}_environment_disease_M0_M1_v3_county_stage_private.csv").exists():
                raise FileExistsError("Cannot refresh a freeze after any Wave 4/5 analysis output exists")
    all_rows = []
    bindings = {}
    for wave in ("2018", "2020"):
        bindings[wave] = _source_binding(wave)
        all_rows.extend(_hypothesis_rows(wave))
    with register_path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(all_rows[0]))
        writer.writeheader(); writer.writerows(all_rows)
    if os.name == "posix":
        os.chmod(register_path, 0o600)
    plan = {
        "plan_id": "wave45_environment_doctor_diagnosis_v3_county_stage",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "authorization_basis": "user-authorized internal analysis in the user's private server workspace",
        "waves": {"2018": {"exposure_contrasts": len(EXPOSURES["2018"]), "outcomes": len(DISEASES["2018"]), "registered_K": len(EXPOSURES["2018"]) * len(DISEASES["2018"])},
                  "2020": {"exposure_contrasts": len(EXPOSURES["2020"]), "outcomes": len(DISEASES["2020"]), "registered_K": len(EXPOSURES["2020"]) * len(DISEASES["2020"])}},
        "target": "official crosssection=1 respondent/spouse sample with positive INDV_weight_ad2; no automatic age cutoff; pairwise complete cases after model covariates",
        "exposure_rules": {w: EXPOSURES[w] for w in EXPOSURES},
        "outcome_rules": "official route-derived cumulative doctor-diagnosed positive or explicit routed current Yes/No; unresolved and contradictory routes missing; not incident disease",
        "primary_model": {"id": "M1_age_sex_residence", "family": "survey-weighted logistic regression", "covariates": ["age candidate, linear and quadratic", "female indicator from XRGender 1=male/2=female", "current residence categories 2/3/4 vs category 1"], "age_source": "Wave 4 actual-birth-year questionnaire route; Wave 5 official XRAge", "settlement_source": "2018 I000_W4_2; 2020 BA008; wave-specific source categories retain city-center reference"},
        "secondary_model": {"id": "M0_unadjusted", "family": "survey-weighted logistic regression", "covariates": []},
        "survey_design": {"weight": "INDV_weight_ad2", "frame": "crosssection=1", "psu": "documented county segment of householdID; validate against communityID", "strata": None, "variance": "with-replacement Taylor approximation at county stage; no fabricated strata; community-cluster sensitivity; label as approximate"},
        "multiplicity": "separate complete-family BY and Bonferroni correction for each wave and model; all registered rows retained including inestimable rows",
        "pair_support_gate": {"minimum_complete_case_n": MIN_MODEL_N, "minimum_distinct_psu": MIN_MODEL_PSU,
                              "below_threshold": "retain as inestimable hypothesis; do not lower threshold after viewing results"},
        "scale_up_rule": "No p-value or observed effect is used to omit a registered hypothesis.",
        "public_release": "not approved; requires complete family, independent QA, and aggregate disclosure review",
        "input_bindings_private": bindings,
        "code_commit": code_commit,
    }
    write_json_private(plan_path, plan)
    freeze_manifest = {"status": "frozen_for_internal_execution", "plan_sha256": sha256(plan_path),
                       "register_sha256": sha256(register_path), "code_commit": code_commit,
                       "created_utc": datetime.now(timezone.utc).isoformat(),
                       "hypothesis_rows_private": len(all_rows), "input_bindings_private": bindings,
                       "supersedes_plan_sha256_private": prior_freeze.get("plan_sha256") if prior_freeze else None}
    write_json_private(manifest_path, freeze_manifest)
    return {"status": "frozen", "registered_rows_private": len(all_rows), "plan_sha256": freeze_manifest["plan_sha256"]}


def _read_selected(path: Path, cols: list[str]) -> pd.DataFrame:
    frame, _ = pyreadstat.read_dta(str(path), usecols=cols)
    return frame


def _recode_binary(source: pd.Series, yes_code: int = 1, no_code: int = 2) -> pd.Series:
    x = pd.to_numeric(source, errors="coerce")
    return x.map({yes_code: 1.0, no_code: 0.0}).astype("float64")


def run(waves: list[str], community_sensitivity: bool = False,
        execution_commit: str | None = None) -> dict[str, Any]:
    manifest_path = private_path(REVIEW / "wave45_freeze_manifest_v1.json")
    plan_path = private_path(REVIEW / "wave45_analysis_plan_v1.json")
    register_path = private_path(REVIEW / "wave45_hypothesis_register_v1.csv")
    if not all(p.is_file() for p in (manifest_path, plan_path, register_path)):
        raise FileNotFoundError("Frozen Wave 4/5 plan/register is absent; run --freeze first")
    frozen = json.loads(manifest_path.read_text(encoding="utf-8"))
    if frozen.get("status") != "frozen_for_internal_execution" or frozen.get("plan_sha256") != sha256(plan_path) or frozen.get("register_sha256") != sha256(register_path):
        raise ValueError("Frozen plan/register hash binding failed")
    results = {}
    execution_commit = execution_commit or __import__("subprocess").check_output(
        ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], text=True
    ).strip()
    for wave in waves:
        binding = _source_binding(wave)
        if binding != frozen["input_bindings_private"][wave]:
            raise ValueError(f"Wave {wave}: inputs changed after freeze; do not run against stale registration")
        source = private_path(TABLES / f"CHARLS_wave{wave}_person_analytic.dta")
        age_path = private_path(TABLES / f"CHARLS_wave{wave}_age_candidate_private.dta")
        outcome_path = private_path(TABLES / f"CHARLS_wave{wave}_doctor_diagnosis_outcomes_route_derived.dta")
        source_fields = sorted({entry["field"] for entry in EXPOSURES[wave]})
        location_field = "i000_w4_2" if wave == "2018" else "ba008"
        base_cols = list(dict.fromkeys([*BASE, "xrgender", location_field, *source_fields]))
        raw = _read_selected(source, base_cols)
        age_col = "age_at_interview_year_candidate" if wave == "2018" else "official_xrage"
        age = _read_selected(age_path, ["ID", age_col])
        outcomes = [entry[0] for entry in DISEASES[wave]]
        outcome_cols = ["ID", *[f"{name}_ever_doctor_diagnosed" for name in outcomes]]
        disease = _read_selected(outcome_path, outcome_cols)
        for frame, label in ((raw, "source"), (age, "age"), (disease, "outcome")):
            if frame["ID"].isna().any() or frame["ID"].duplicated().any():
                raise ValueError(f"Wave {wave}: duplicate or missing {label} IDs")
        if not (raw["ID"].reset_index(drop=True).equals(age["ID"].reset_index(drop=True)) and raw["ID"].reset_index(drop=True).equals(disease["ID"].reset_index(drop=True))):
            raise ValueError(f"Wave {wave}: source, age, and outcome ID order differs")
        df = raw.copy()
        df["age"] = pd.to_numeric(age[age_col], errors="coerce")
        df["female"] = pd.to_numeric(df["xrgender"], errors="coerce").map({1: 0.0, 2: 1.0})
        df["age_centered"] = df["age"] - 60.0
        df["age_centered_sq"] = df["age_centered"] ** 2
        loc = pd.to_numeric(df[location_field], errors="coerce")
        valid_residence = loc.isin([1, 2, 3, 4])
        for level in (2, 3, 4):
            df[f"residence_{level}"] = np.where(valid_residence, loc.eq(level).astype(float), np.nan)
        df = df.merge(disease, on="ID", how="left", validate="one_to_one", sort=False)
        frame_flag = pd.to_numeric(df["crosssection"], errors="coerce")
        if frame_flag.isna().any() or not set(frame_flag.unique()).issubset({0, 1}):
            raise ValueError(f"Wave {wave}: unsupported official crosssection coding")
        df = df.loc[frame_flag.eq(1)].copy()
        df = df.loc[pd.to_numeric(df["INDV_weight_ad2"], errors="coerce").gt(0)].copy()
        e_specs = []
        for exposure in EXPOSURES[wave]:
            field = exposure["field"]
            new_var = f"e_{exposure['id']}"
            x = pd.to_numeric(df[field], errors="coerce")
            if exposure["type"] == "binary":
                df[new_var] = _recode_binary(x)
                contrast = "yes_vs_no"
            else:
                case, reference = exposure["case"], exposure["reference"]
                df[new_var] = x.map({case: 1.0, reference: 0.0}).astype("float64")
                contrast = f"code_{case}_vs_{reference}"
            e_specs.append(engine.VariableSpec(
                concept_id=exposure["id"], role="E", label=exposure["label"], wave=wave,
                variable=new_var, kind="binary", valid_min=0, valid_max=1,
            ))
        p_specs = []
        for concept, label, _ in DISEASES[wave]:
            variable = f"{concept}_ever_doctor_diagnosed"
            p_specs.append(engine.VariableSpec(
                concept_id=concept, role="P", label=label, wave=wave,
                variable=variable, kind="binary", valid_min=0, valid_max=1, family="binomial",
            ))
        # NaN values become nulls so the engine's complete-case logic is explicit.
        model_cols = list(dict.fromkeys([*BASE, "age_centered", "age_centered_sq", "female",
                                         "residence_2", "residence_3", "residence_4",
                                         *[s.variable for s in e_specs], *[s.variable for s in p_specs]]))
        model_frame = pl.from_pandas(df[model_cols], include_index=False, nan_to_null=True)
        model_frame = add_documented_county_cluster(model_frame, output="__county_psu")
        design = engine.DesignSpec(
            weight="INDV_weight_ad2", psu="communityID" if community_sensitivity else "__county_psu", strata=None,
            covariate_sets={"M0_unadjusted": [], "M1_age_sex_residence":
                            ["age_centered", "age_centered_sq", "female", "residence_2", "residence_3", "residence_4"]},
            scale_outcome=False, variance_limitations=COMMUNITY_SENSITIVITY_VARIANCE if community_sensitivity else VARIANCE,
        )
        expected_k = len(e_specs) * len(p_specs)
        registry = [*e_specs, *p_specs]
        prepared = engine.prepare_frame(model_frame, design, registry)
        rows = []
        for exposure in e_specs:
            for phenotype in p_specs:
                for model in MODELS:
                    complete = (pl.col("_analysis_weight") > 0)
                    complete &= engine._valid_expr(exposure) & engine._valid_expr(phenotype)
                    complete &= pl.col(exposure.variable).cast(pl.Float64, strict=False).is_finite()
                    complete &= pl.col(phenotype.variable).cast(pl.Float64, strict=False).is_finite()
                    for covariate in design.model_covariates(model):
                        value = pl.col(covariate).cast(pl.Float64, strict=False)
                        complete &= value.is_not_null() & value.is_finite()
                    support = prepared.filter(complete.fill_null(False))
                    support_n = support.height
                    support_psu = support["_psu"].n_unique()
                    if support_n < MIN_MODEL_N or support_psu < MIN_MODEL_PSU:
                        row = engine._blocked_row(
                            exposure, phenotype, design, model, [exposure.variable], {},
                            "inestimable",
                            f"prespecified pair support threshold not met: N={support_n}; PSU={support_psu}; minima={MIN_MODEL_N}/{MIN_MODEL_PSU}",
                        )
                        row["n_model"], row["n_psu"] = support_n, support_psu
                        rows.append(row)
                    else:
                        try:
                            rows.extend(engine.fit_pair(prepared, exposure, phenotype, design, model))
                        except Exception as exc:  # retain the registered pair and its exact failure in private QA
                            row = engine._blocked_row(
                                exposure, phenotype, design, model, [exposure.variable], {},
                                "numerically_unavailable",
                                f"prespecified model could not be estimated ({type(exc).__name__}); no post-hoc recoding",
                            )
                            row["n_model"], row["n_psu"] = support_n, support_psu
                            rows.append(row)
        engine.assign_families(rows, "charls_environment_disease")
        expected_rows = expected_k * len(MODELS)
        if len(rows) != expected_rows:
            raise ValueError(f"Wave {wave}: expected {expected_rows} coefficient rows, found {len(rows)}")
        suffix = "community_cluster_sensitivity" if community_sensitivity else "county_stage"
        output = private_path(PRIVATE / "results" / f"wave{wave}_environment_disease_M0_M1_v3_{suffix}_private.csv")
        qa_path = private_path(QA / f"wave{wave}_environment_disease_run_qa_v3_{suffix}_private.json")
        if output.exists() or qa_path.exists():
            raise FileExistsError(f"Wave {wave}: result artifacts already exist; refusing overwrite")
        engine.write_rows(rows, output)
        if os.name == "posix":
            os.chmod(output, 0o600)
        statuses = Counter(row["fit_status"] for row in rows)
        models = {}
        for model in MODELS:
            chosen = [r for r in rows if r["model_id"] == model]
            models[model] = {"registered_K_private": expected_k,
                             "row_count_private": len(chosen),
                             "fit_status_private": dict(Counter(r["fit_status"] for r in chosen)),
              "approximate_variance_note": design.note()}
        qa = {"scope": "private Wave 4/5 household-environment × cumulative doctor-diagnosed disease scan",
              "created_utc": datetime.now(timezone.utc).isoformat(), "wave": wave,
              "registered_K_per_model_private": expected_k,
              "total_model_rows_private": len(rows), "fit_status_all_private": dict(statuses),
              "model_summaries_private": models,
              "target_filter": "official crosssection=1 and positive INDV_weight_ad2; no automatic age cutoff",
              "primary_model": "M1_age_sex_residence", "secondary_model": "M0_unadjusted",
              "multiplicity": "complete-family BY and Bonferroni by wave and model; all non-estimable hypotheses remain in K",
              "pair_support_threshold_private": {"minimum_complete_case_n": MIN_MODEL_N, "minimum_distinct_psu": MIN_MODEL_PSU},
              "result_sha256_private": sha256(output), "frozen_plan_sha256": frozen["plan_sha256"],
              "hypothesis_register_sha256": frozen["register_sha256"], "input_bindings_private": binding,
              "primary_plan_code_commit": frozen["code_commit"],
              "execution_code_commit": execution_commit,
              "execution_script_sha256_private": sha256(Path(__file__).resolve()),
              "variance_sensitivity": "community_cluster_only" if community_sensitivity else "documented_county_stage_primary",
              "publication": "not approved; exact results and QA remain private"}
        write_json_private(qa_path, qa)
        results[wave] = {"registered_K_per_model": expected_k, "rows": len(rows), "status_counts": dict(statuses)}
    return {"status": "private_wave45_associations_complete", "waves": results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--run", action="store_true")
    parser.add_argument("--wave", choices=("2018", "2020", "both"), default="both")
    parser.add_argument("--code-commit", required=True)
    parser.add_argument("--community-cluster-sensitivity", action="store_true",
                        help="run the preplanned lower-stage PSU sensitivity into separate private outputs")
    args = parser.parse_args()
    if args.freeze:
        print(json.dumps(freeze(args.code_commit), ensure_ascii=False))
    else:
        waves = ["2018", "2020"] if args.wave == "both" else [args.wave]
        print(json.dumps(run(waves, community_sensitivity=args.community_cluster_sensitivity,
                             execution_commit=args.code_commit), ensure_ascii=False))


if __name__ == "__main__":
    main()
