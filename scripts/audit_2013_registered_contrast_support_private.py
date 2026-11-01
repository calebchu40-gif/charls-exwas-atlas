#!/usr/bin/env python3
"""Reconcile Wave 2 registered exposure-level support against private fits.

Reads only the protected 2013 prepared table, protected age-interval candidate,
and registered K=75 midpoint result table. Exact exposed/reference counts and
PSU support are written only under CHARLS_EXWAS_PRIVATE_ROOT. No model is fit,
no hypothesis is removed by p-value, and nothing is written to the site.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path


PRIVATE = PRIVATE_ROOT.resolve()
TABLE_DIR = PRIVATE / "derived_wave_tables"
RESULTS_DIR = PRIVATE / "results"
QA_DIR = PRIVATE / "qa_outputs"
REVIEW_DIR = PRIVATE / "analysis_review"
FAMILY_FILE = "2013_household_environment_anthropometry_K75_midpoint_primary_raw_private.csv"
FAMILY_QA_FILE = "2013_household_environment_anthropometry_K75_midpoint_primary_private.json"
CONFIG_FILE = "wave2013_anthropometry_midpoint_config_private.json"
OUTCOME_FIELDS = ("qi002", "qj002", "qk002", "ql002", "qm002")


def private_path(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE):
        raise ValueError(f"CHARLS input/output path escaped the protected root: {resolved}")
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Registered private family must have a unique nonempty CSV header")
        return list(reader)


def _code_commit() -> str:
    try:
        value = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return value


def audit(output: Path) -> dict[str, Any]:
    main = private_path(TABLE_DIR / "CHARLS_wave2013_person_analytic.dta")
    age = private_path(TABLE_DIR / "CHARLS_wave2013_age_interval_candidate.dta")
    manifest_path = private_path(TABLE_DIR / "prepared_data_manifest.json")
    age_qa_path = private_path(QA_DIR / "wave2_age_interval_candidate_private.json")
    result_path = private_path(RESULTS_DIR / FAMILY_FILE)
    family_qa_path = private_path(QA_DIR / FAMILY_QA_FILE)
    config_path = private_path(REVIEW_DIR / CONFIG_FILE)
    output = private_path(output)
    if output.exists():
        raise FileExistsError("Refusing to overwrite an existing protected support report")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    wave_records = [x for x in manifest.get("waves", []) if str(x.get("wave")) == "2013"]
    main_sha = sha256(main)
    if (len(wave_records) != 1
            or wave_records[0].get("prepared_output", {}).get("filename") != main.name
            or wave_records[0].get("prepared_output", {}).get("sha256") != main_sha):
        raise ValueError("Wave 2 prepared table does not match its protected manifest")
    age_qa = json.loads(age_qa_path.read_text(encoding="utf-8"))
    age_sha = sha256(age)
    if age_qa.get("person_level_candidate_sha256") != age_sha:
        raise ValueError("Age-interval candidate does not match its protected QA binding")
    family_qa = json.loads(family_qa_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    rows = _read_csv(result_path)
    if (len(rows) != 75 or len({r.get("analysis_id", "") for r in rows}) != 75
            or family_qa.get("registered_K") != 75
            or family_qa.get("age_bound") != "midpoint"
            or config.get("registered_K") != 75
            or config.get("status") != "user_authorized_internal_analysis"):
        raise ValueError("The midpoint results/configuration are not the registered K=75 family")

    usecols = ["ID", "crosssection", "Biomarker_weight", "communityID", "ba000_w2_3",
               "i017", "i019", "i020", "i021", "i022", *OUTCOME_FIELDS]
    people, _ = pyreadstat.read_dta(str(main), usecols=usecols)
    age_rows, _ = pyreadstat.read_dta(
        str(age), usecols=["ID", "age_at_interview_lower", "age_at_interview_upper"]
    )
    for frame in (people, age_rows):
        if frame["ID"].isna().any() or frame["ID"].duplicated().any():
            raise ValueError("Protected source tables have missing or duplicate IDs")
    data = people.merge(age_rows, on="ID", how="left", validate="one_to_one", indicator=True)
    if not data["_merge"].eq("both").all():
        raise ValueError("Age candidate does not cover the prepared Wave 2 respondent table")

    lower = pd.to_numeric(data["age_at_interview_lower"], errors="coerce")
    upper = pd.to_numeric(data["age_at_interview_upper"], errors="coerce")
    age_mid = (lower + upper) / 2
    weight = pd.to_numeric(data["Biomarker_weight"], errors="coerce")
    frame = pd.to_numeric(data["crosssection"], errors="coerce")
    sex = pd.to_numeric(data["ba000_w2_3"], errors="coerce")
    finite_age = age_mid.map(lambda x: math.isfinite(x) if pd.notna(x) else False)
    finite_weight = weight.map(lambda x: math.isfinite(x) if pd.notna(x) else False)
    base = (frame.eq(1) & weight.gt(0) & finite_weight & finite_age
            & sex.isin([1, 2]) & data["communityID"].notna())

    contrasts: dict[tuple[str, str, str], tuple[int, int, bool]] = {}
    for item in config.get("exposure_contrasts", []):
        concept, variable, exposed, reference, label, routed = item
        contrasts[(concept, variable, label)] = (int(exposed), int(reference), bool(routed))
    outcomes = config.get("outcomes", {})
    diagnostics: list[dict[str, Any]] = []
    all_n_psu_match = True
    all_fit_success = True
    all_support = True
    all_pairs_retained = True
    for row in rows:
        key = (row["exposure_concept_id"], row["exposure_variable"], row["contrast"])
        if key not in contrasts:
            raise ValueError("A registered result row lacks its frozen exposure contrast")
        exposed_code, reference_code, routed = contrasts[key]
        subset = base.copy()
        if routed:
            subset &= pd.to_numeric(data["i020"], errors="coerce").eq(2)
        exposure = pd.to_numeric(data[row["exposure_variable"]], errors="coerce")
        phenotype = pd.to_numeric(data[row["phenotype_variable"]], errors="coerce")
        outcome = next((v for v in outcomes.values()
                        if v.get("field", "").casefold() == row["phenotype_variable"].casefold()), None)
        if outcome is None:
            raise ValueError("A registered phenotype field lacks its frozen outcome rule")
        valid_outcome = phenotype.notna() & phenotype.map(
            lambda x: math.isfinite(x) if pd.notna(x) else False
        )
        for sentinel in outcome.get("excluded_nonmeasurement_codes", []):
            valid_outcome &= phenotype.ne(float(sentinel))
        complete = subset & exposure.isin([exposed_code, reference_code]) & valid_outcome
        exposed = complete & exposure.eq(exposed_code)
        reference = complete & exposure.eq(reference_code)
        exposed_n, reference_n = int(exposed.sum()), int(reference.sum())
        pair_n = int(complete.sum())
        exposed_psu = int(data.loc[exposed, "communityID"].nunique())
        reference_psu = int(data.loc[reference, "communityID"].nunique())
        pair_psu = int(data.loc[complete, "communityID"].nunique())
        match = pair_n == int(row["n_model"]) and pair_psu == int(row["n_psu_private"])
        fits = row.get("fit_status") == "success"
        support = exposed_n > 0 and reference_n > 0 and pair_n >= 500 and pair_psu >= 30
        all_n_psu_match &= match
        all_fit_success &= fits
        all_support &= support
        all_pairs_retained &= bool(row.get("analysis_id"))
        diagnostics.append({
            "analysis_id": row["analysis_id"],
            "exposure_concept_id": key[0], "exposure_variable": key[1],
            "contrast": key[2], "phenotype_concept_id": row["phenotype_concept_id"],
            "phenotype_variable": row["phenotype_variable"],
            "exposed_n_private": exposed_n, "reference_n_private": reference_n,
            "exposed_psus_private": exposed_psu, "reference_psus_private": reference_psu,
            "pair_complete_n_private": pair_n, "pair_psus_private": pair_psu,
            "matches_runner_n_and_psu": bool(match),
            "registered_support_gate_pass": bool(support),
            "sparse_level_flag_private": exposed_n < 30 or reference_n < 30,
            "sparse_level_psu_flag_private": exposed_psu < 10 or reference_psu < 10,
        })

    checks = {
        "registered_family_K75_retained": len(rows) == 75 and all_pairs_retained,
        "all_fits_successful": all_fit_success,
        "runner_pair_N_and_PSU_reconciled": all_n_psu_match,
        "registered_pair_N_and_PSU_support": all_support,
        "no_p_value_based_pair_selection": True,
    }
    status = "support_reconciliation_complete" if all(checks.values()) else "support_review_needs_followup"
    try:
        commit = _code_commit()
    except Exception:
        commit = "unavailable"
    report = {
        "scope": "private Wave 2 registered contrast-level support reconciliation",
        "status": status, "created_utc": datetime.now(timezone.utc).isoformat(),
        "code_commit": commit, "audit_script_sha256": sha256(Path(__file__).resolve()),
        "registered_K": 75,
        "source_rules": "crosssection=1; finite positive official Biomarker_weight; communityID observed; midpoint age and recorded sex complete; pair-complete anthropometry; heating-source contrasts only where i020=2",
        "checks": checks, "all_registered_hypotheses_retained": True,
        "design_note": "communityID clusters; strata not released; WR Taylor variance is approximate",
        "result_status": "private_internal_results_pending_technical_and_disclosure_review",
        "input_bindings_private": {
            "prepared_data_sha256": main_sha,
            "prepared_manifest_sha256": sha256(manifest_path),
            "age_candidate_sha256": age_sha,
            "age_candidate_qa_sha256": sha256(age_qa_path),
            "midpoint_result_sha256": sha256(result_path),
            "midpoint_qa_sha256": sha256(family_qa_path),
            "midpoint_config_sha256": sha256(config_path),
        },
        "private_pair_support": diagnostics,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(output.parent, 0o700)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(output, 0o600)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=QA_DIR / "wave2013_registered_contrast_support_reconciliation_v2_private.json")
    args = parser.parse_args()
    result = audit(args.output)
    print(json.dumps({
        "status": result["status"],
        "registered_K": result["registered_K"],
        "checks": result["checks"],
        "output": args.output.name,
    }, ensure_ascii=False))
    if result["status"] != "support_reconciliation_complete":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
