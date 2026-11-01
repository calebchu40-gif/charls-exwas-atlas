#!/usr/bin/env python3
"""Audit protected Wave 4/5 binary pair support for aggregate disclosure.

Reads only the user's protected prepared tables and route-derived outcomes.
Writes exact cell counts, county-PSU support, hash bindings and row decisions
only beneath CHARLS_EXWAS_PRIVATE_ROOT. Thresholds are an internal review
screen, not an official CHARLS numerical disclosure rule.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path
from run_wave45_environment_disease import (
    BASE, DISEASES, EXPOSURES, MIN_MODEL_N, MIN_MODEL_PSU, MODELS,
    _read_selected, _recode_binary, _source_binding, private_path,
    sha256, TABLES, QA, PRIVATE,
)

OUT = private_path(PRIVATE / "qa_outputs" / "wave45_county_pair_cell_disclosure_private_v1.json")
CSV_OUT = private_path(PRIVATE / "analysis_review" / "wave45_county_pair_cell_disclosure_private_v1.csv")
RAW_CELL_MIN = 10
CELL_PSU_MIN = 10


def _pair_values(df: pd.DataFrame, exposure: dict, concept: str) -> tuple[pd.Series, pd.Series]:
    x = pd.to_numeric(df[exposure["field"]], errors="coerce")
    if exposure["type"] == "binary":
        x = x.map({1: 1.0, 2: 0.0})
    else:
        x = x.map({exposure["case"]: 1.0, exposure["reference"]: 0.0})
    y = pd.to_numeric(df[f"{concept}_ever_doctor_diagnosed"], errors="coerce")
    return x, y


def _model_complete(df: pd.DataFrame, x: pd.Series, y: pd.Series, model: str,
                    age_col: str, location_col: str) -> pd.Series:
    keep = pd.to_numeric(df["INDV_weight_ad2"], errors="coerce").gt(0)
    keep &= x.isin([0.0, 1.0]) & y.isin([0.0, 1.0])
    if model == "M1_age_sex_residence":
        age = pd.to_numeric(df[age_col], errors="coerce")
        gender = pd.to_numeric(df["xrgender"], errors="coerce").isin([1, 2])
        residence = pd.to_numeric(df[location_col], errors="coerce").isin([1, 2, 3, 4])
        keep &= age.notna() & np.isfinite(age) & gender & residence
    return keep.fillna(False)


def audit(waves: list[str], code_commit: str) -> dict:
    manifest_path = private_path(TABLES / "prepared_data_manifest.json")
    manifest_sha = sha256(manifest_path)
    rows: list[dict[str, str]] = []
    bindings = {}
    summary = {}
    for wave in waves:
        binding = _source_binding(wave)
        bindings[wave] = binding
        source = private_path(TABLES / f"CHARLS_wave{wave}_person_analytic.dta")
        age_path = private_path(TABLES / f"CHARLS_wave{wave}_age_candidate_private.dta")
        outcome_path = private_path(TABLES / f"CHARLS_wave{wave}_doctor_diagnosis_outcomes_route_derived.dta")
        source_fields = sorted({e["field"] for e in EXPOSURES[wave]})
        location_field = "i000_w4_2" if wave == "2018" else "ba008"
        raw = _read_selected(source, list(dict.fromkeys([*BASE, "xrgender", location_field, *source_fields])))
        age_col = "age_at_interview_year_candidate" if wave == "2018" else "official_xrage"
        age = _read_selected(age_path, ["ID", age_col])
        concepts = [d[0] for d in DISEASES[wave]]
        outcome = _read_selected(outcome_path, ["ID", *[f"{c}_ever_doctor_diagnosed" for c in concepts]])
        if any(frame.ID.isna().any() or frame.ID.duplicated().any() for frame in (raw, age, outcome)):
            raise ValueError(f"Wave {wave}: duplicate/missing source IDs")
        if not raw.ID.reset_index(drop=True).equals(age.ID.reset_index(drop=True)) or not raw.ID.reset_index(drop=True).equals(outcome.ID.reset_index(drop=True)):
            raise ValueError(f"Wave {wave}: source, age, outcome rows do not align")
        df = raw.copy()
        df[age_col] = age[age_col]
        df = df.merge(outcome, on="ID", how="left", validate="one_to_one", sort=False)
        frame = pd.to_numeric(df.crosssection, errors="coerce")
        if frame.isna().any() or not set(frame.unique()).issubset({0, 1}):
            raise ValueError(f"Wave {wave}: unsupported crosssection codes")
        df = df.loc[frame.eq(1) & pd.to_numeric(df.INDV_weight_ad2, errors="coerce").gt(0)].copy()
        # county PSU is the documented six-character householdID segment.
        household = df.householdID.astype("string").str.strip()
        county = household.str.slice(0, 6)
        community = df.communityID.astype("string").str.strip()
        if county.isna().any() or community.isna().any() or ((county.str.slice(0, 6) != community.str.slice(0, 6))).any():
            raise ValueError(f"Wave {wave}: household county/community key audit failed")
        df["__county"] = county
        for exposure in EXPOSURES[wave]:
            for concept, _, _ in DISEASES[wave]:
                x, y = _pair_values(df, exposure, concept)
                complete = x.isin([0.0, 1.0]) & y.isin([0.0, 1.0])
                cells = []
                cell_psu = []
                for xv in (0.0, 1.0):
                    for yv in (0.0, 1.0):
                        mask = complete & x.eq(xv) & y.eq(yv)
                        cells.append(int(mask.sum()))
                        cell_psu.append(int(df.loc[mask, "__county"].nunique()))
                for model in MODELS:
                    cc = _model_complete(df, x, y, model, age_col, location_field)
                    n_model = int(cc.sum())
                    n_psu = int(df.loc[cc, "__county"].nunique())
                    reasons = []
                    if min(cells) < RAW_CELL_MIN:
                        reasons.append("raw_2x2_cell_below_internal_minimum")
                    if min(cell_psu) < CELL_PSU_MIN:
                        reasons.append("cell_county_psu_below_internal_minimum")
                    if n_model < MIN_MODEL_N:
                        reasons.append("model_complete_case_n_below_frozen_minimum")
                    if n_psu < MIN_MODEL_PSU:
                        reasons.append("model_county_psu_below_frozen_minimum")
                    rows.append({
                        "analysis_id": f"{wave}:{exposure['id']}:{concept}:{model}",
                        "wave": wave, "model_id": model,
                        "decision": "withheld" if reasons else "approved_public_aggregate",
                        "reason_codes_private": ";".join(reasons) if reasons else "no_internal_support_flag",
                        "raw_cell_n_00_private": str(cells[0]), "raw_cell_n_01_private": str(cells[1]),
                        "raw_cell_n_10_private": str(cells[2]), "raw_cell_n_11_private": str(cells[3]),
                        "raw_cell_county_psu_min_private": str(min(cell_psu)),
                        "n_model_private": str(n_model), "n_county_psu_private": str(n_psu),
                    })
        summary[wave] = {"hypotheses_private": sum(r["wave"] == wave for r in rows),
                         "crosssection_positive_weight_rows_private": len(df),
                         "source_binding_private": binding}
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    os.chmod(CSV_OUT, 0o600)
    report = {
        "status": "passed_internal_support_disclosure_screen",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "code_commit": code_commit,
        "input_manifest_sha256_private": manifest_sha,
        "result_files_reviewed": {w: sha256(private_path(PRIVATE / "results" / f"wave{w}_environment_disease_M0_M1_v3_county_stage_private.csv")) for w in waves},
        "thresholds": {"raw_2x2_cell_n_min_internal": RAW_CELL_MIN, "distinct_county_psu_per_cell_min_internal": CELL_PSU_MIN,
                       "model_complete_case_n_min_frozen": MIN_MODEL_N, "model_distinct_county_psu_min_frozen": MIN_MODEL_PSU,
                       "note": "Internal conservative review screen, not a numerical rule issued by CHARLS."},
        "input_bindings_private": bindings,
        "row_review_file_sha256_private": sha256(CSV_OUT),
        "rows_reviewed_private": len(rows),
        "decisions_private": {"approved_public_aggregate": sum(r["decision"] == "approved_public_aggregate" for r in rows),
                              "withheld": sum(r["decision"] == "withheld" for r in rows)},
        "wave_summaries_private": summary,
        "public_release": "not authorized by this technical screen; aggregate review remains necessary",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600); os.replace(tmp, OUT)
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--waves", nargs="+", choices=("2018", "2020"), default=["2018", "2020"])
    p.add_argument("--code-commit", required=True)
    a = p.parse_args()
    result = audit(a.waves, a.code_commit)
    print(json.dumps({"status": result["status"], "rows_reviewed_private": result["rows_reviewed_private"],
                      "decisions_private": result["decisions_private"],
                      "report_sha256_private": sha256(OUT), "row_file_sha256_private": sha256(CSV_OUT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
