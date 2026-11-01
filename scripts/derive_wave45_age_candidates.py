#!/usr/bin/env python3
"""Derive protected Wave 4/5 age-at-interview candidates from documented sources.

Wave 4 follows the questionnaire's BA005/BA004_W3/BA002 actual-date routing;
Wave 5 retains official XRAge and records an independent source-formula check.
All row-level outputs and exact diagnostics are restricted to private storage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path

PRIVATE = PRIVATE_ROOT.resolve()
BASE = ("ID", "crosssection", "INDV_weight_ad2", "communityID")


def private_path(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE):
        raise ValueError(f"Path escaped protected storage: {resolved}")
    return resolved


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _num(v: Any) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _year(v: Any, low: int, high: int) -> int | None:
    x = _num(v)
    if x is None or not x.is_integer() or not low <= x <= high:
        return None
    return int(x)


def _field(cols: list[str], wanted: str, required: bool = True) -> str | None:
    m = [c for c in cols if c.casefold() == wanted.casefold()]
    if len(m) > 1 or (required and len(m) != 1):
        raise ValueError(f"Required source field missing or ambiguous: {wanted}")
    return m[0] if m else None


def _manifest_record(wave: str, manifest_path: Path, data_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = [x for x in manifest.get("waves", []) if str(x.get("wave")) == wave]
    if len(records) != 1 or records[0].get("prepared_output", {}).get("sha256") != sha256(data_path):
        raise ValueError("Prepared input does not match protected manifest")
    return {"prepared_manifest_sha256_private": sha256(manifest_path),
            "prepared_table_sha256_private": sha256(data_path),
            "source_archive_record": records[0].get("source_archive"),
            "source_inputs_record": records[0].get("source_inputs")}


def derive(wave: str, code_commit: str) -> dict[str, Any]:
    if wave not in ("2018", "2020"):
        raise ValueError("Wave must be 2018 or 2020")
    if len(code_commit) not in range(7, 41) or any(c not in "0123456789abcdef" for c in code_commit):
        raise ValueError("Pass the public analysis-code commit SHA")
    table_dir = private_path(PRIVATE / "derived_wave_tables")
    data_path = private_path(table_dir / f"CHARLS_wave{wave}_person_analytic.dta")
    manifest_path = private_path(table_dir / "prepared_data_manifest.json")
    if not data_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("Protected prepared wave table or manifest is absent")
    binding = _manifest_record(wave, manifest_path, data_path)
    _, meta = pyreadstat.read_dta(str(data_path), metadataonly=True)
    cols = list(meta.column_names)
    id_f, frame_f, weight_f, psu_f = [_field(cols, c) for c in BASE]
    use = [id_f, frame_f, weight_f, psu_f]

    if wave == "2018":
        required = ("ba004_w3", "ba004_w3_1", "ba002_1", "ba005_w4", "iyear")
        fs = {x: _field(cols, x) for x in required}
        optional = ("ba004_w3_2", "ba004_w3_3", "ba002_2", "ba002_3", "imonth")
        fs.update({x: _field(cols, x, required=False) for x in optional})
        use.extend(x for x in fs.values() if x)
    else:
        fs = {"xrage": _field(cols, "xrage"), "iyear": _field(cols, "iyear"),
              "ba003_1": _field(cols, "ba003_1", required=False),
              "zrbirthyear": _field(cols, "zrbirthyear", required=False),
              "xrtype": _field(cols, "xrtype", required=False)}
        use.extend(x for x in fs.values() if x)
    raw, _ = pyreadstat.read_dta(str(data_path), usecols=list(dict.fromkeys(use)))
    if raw[id_f].isna().any() or raw[id_f].duplicated().any():
        raise ValueError("Prepared person table ID integrity failed")
    if raw[frame_f].isna().any() or not set(pd.to_numeric(raw[frame_f], errors="coerce").dropna().unique()).issubset({0, 1}):
        raise ValueError("Unexpected crosssection frame coding")

    ages, sources, states, formula_matches = [], [], [], []
    for row in raw.to_dict(orient="records"):
        interview_year = _year(row.get(fs["iyear"]), 2000, 2030)
        if wave == "2018":
            same_as_id = _num(row.get(fs["ba005_w4"]))
            id_route = _num(row.get(fs["ba004_w3"]))
            if same_as_id == 1:
                birth_year = _year(row.get(fs["ba004_w3_1"]), 1900, 2018)
                source, state = "BA004_W3_documented_same_as_actual", "official_route_same_as_id"
            elif same_as_id == 2 or id_route in (2, 3):
                birth_year = _year(row.get(fs["ba002_1"]), 1900, 2018)
                source, state = "BA002_actual_birth_year", "official_route_actual_date"
            else:
                birth_year, source, state = None, "unresolved", "route_missing_or_inconsistent"
            age = interview_year - birth_year if interview_year is not None and birth_year is not None else math.nan
            ages.append(age)
            sources.append(source)
            states.append(state if math.isfinite(age) else "age_unavailable_or_invalid_year")
            formula_matches.append(None)
        else:
            age = _num(row.get(fs["xrage"]))
            xrtype = _num(row.get(fs["xrtype"])) if fs.get("xrtype") else None
            if xrtype == 2 or _num(row.get(fs["zrbirthyear"])) is None:
                birth_year = _year(row.get(fs["ba003_1"]), 1900, 2020) if fs.get("ba003_1") else None
            else:
                birth_year = _year(row.get(fs["zrbirthyear"]), 1900, 2020)
            # The official Wave 5 questionnaire's generated XRAge uses the
            # fixed survey-year constant 2020, so validate that exact formula.
            expected_age = 2020 - birth_year if birth_year is not None else None
            match = (age is not None and expected_age is not None and age == expected_age)
            ages.append(age if age is not None else math.nan)
            sources.append("official_XRAge")
            states.append("official_age_present" if age is not None else "official_age_missing")
            formula_matches.append(match if expected_age is not None else None)

    age_field = "age_at_interview_year_candidate" if wave == "2018" else "official_xrage"
    out = raw[[id_f, frame_f, weight_f, psu_f]].copy()
    out[age_field] = ages
    out["age_source_route"] = sources
    out["age_candidate_status"] = states
    if wave == "2020":
        out["xrage_source_formula_match_private"] = formula_matches
    result_path = private_path(table_dir / f"CHARLS_wave{wave}_age_candidate_private.dta")
    qa_path = private_path(PRIVATE / "qa_outputs" / f"wave{wave}_age_candidate_private.json")
    if result_path.exists() or qa_path.exists():
        raise FileExistsError("Protected age candidate exists; refusing overwrite")
    pyreadstat.write_dta(out, str(result_path), version=15)
    if os.name == "posix":
        os.chmod(result_path, 0o600)
    age_numeric = pd.to_numeric(out[age_field], errors="coerce")
    status_counts = out["age_candidate_status"].value_counts(dropna=False).astype(int).to_dict()
    report = {"scope": "protected Wave 4/5 age-at-interview candidate derivation; no domain exclusion",
              "created_utc": datetime.now(timezone.utc).isoformat(), "wave": wave,
              "age_definition": ("interview year minus source-routed actual birth year, following the 2018 questionnaire actual-date routing" if wave == "2018" else "official XRAge as released; questionnaire code defines 2020 minus BA003_1 or ZRBirthYear"),
              "row_count_private": len(out), "age_status_counts_private": status_counts,
              "valid_age_min_private": float(age_numeric.min()) if age_numeric.notna().any() else None,
              "valid_age_max_private": float(age_numeric.max()) if age_numeric.notna().any() else None,
              "2020_xrage_formula_match_counts_private": {str(k): int(v) for k, v in pd.Series(formula_matches, dtype="object").value_counts(dropna=False).items()} if wave == "2020" else None,
              "input_bindings_private": binding, "result_file_private": result_path.name,
              "result_sha256_private": sha256(result_path), "code_commit": code_commit,
              "interpretation": "candidate age covariate only; no 45+ domain, pairwise eligibility, or association is implied",
              "publication": "private preparation and exact QA only"}
    qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    if os.name == "posix":
        os.chmod(qa_path, 0o600)
    return {"status": "private_age_candidate_complete", "wave": wave}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", choices=("2018", "2020"), required=True)
    parser.add_argument("--code-commit", required=True)
    args = parser.parse_args()
    print(json.dumps(derive(args.wave, args.code_commit)))


if __name__ == "__main__":
    main()
