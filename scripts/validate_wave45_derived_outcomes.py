#!/usr/bin/env python3
"""Validate protected Wave 4/5 routed disease outputs against prepared inputs.

Reads respondent-level files only from CHARLS_EXWAS_PRIVATE_ROOT and writes
the exact validation report only within that protected tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path
from derive_wave45_chronic_disease_outcomes import DISEASES

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


def _eq(a: pd.Series, b: pd.Series) -> bool:
    if len(a) != len(b):
        return False
    a = a.reset_index(drop=True)
    b = b.reset_index(drop=True)
    both_na = a.isna() & b.isna()
    try:
        same = a.eq(b)
    except (TypeError, ValueError):
        same = a.astype("string").eq(b.astype("string"))
    return bool((both_na | same.fillna(False)).all())


def validate(wave: str) -> dict[str, Any]:
    if wave not in DISEASES:
        raise ValueError("Wave must be 2018 or 2020")
    table_dir = private_path(PRIVATE / "derived_wave_tables")
    input_path = private_path(table_dir / f"CHARLS_wave{wave}_person_analytic.dta")
    derived_path = private_path(table_dir / f"CHARLS_wave{wave}_doctor_diagnosis_outcomes_route_derived.dta")
    manifest_path = private_path(table_dir / "prepared_data_manifest.json")
    route_path = private_path(PRIVATE / "qa_outputs" / f"wave{wave}_doctor_diagnosis_outcome_routes_private.json")
    if not all(p.is_file() for p in (input_path, derived_path, manifest_path, route_path)):
        raise FileNotFoundError("Required protected input, output, manifest, or derivation QA is absent")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = [x for x in manifest.get("waves", []) if str(x.get("wave")) == wave]
    if len(rows) != 1 or rows[0].get("prepared_output", {}).get("sha256") != sha256(input_path):
        raise ValueError("Prepared input does not match its protected manifest")
    derivation = json.loads(route_path.read_text(encoding="utf-8"))
    if derivation.get("result_sha256_private") != sha256(derived_path):
        raise ValueError("Derived output hash does not match derivation QA")

    src, _ = pyreadstat.read_dta(str(input_path), usecols=list(BASE))
    out, _ = pyreadstat.read_dta(str(derived_path))
    if len(src) != len(out) or src["ID"].isna().any() or src["ID"].duplicated().any():
        raise ValueError("Row count or source ID integrity check failed")
    if out["ID"].isna().any() or out["ID"].duplicated().any() or not _eq(src["ID"], out["ID"]):
        raise ValueError("Derived output does not preserve unique source IDs and row order")
    base_checks = {field: _eq(src[field], out[field]) for field in BASE[1:]}
    if not all(base_checks.values()):
        raise ValueError("Derived output changed frame, weight, or PSU fields")

    outcome_checks: dict[str, dict[str, int]] = {}
    for concept, _, _ in DISEASES[wave]:
        outcome_name = f"{concept}_ever_doctor_diagnosed"
        state_name = f"{concept}_source_route_state"
        if outcome_name not in out or state_name not in out:
            raise ValueError(f"Missing derived fields for {concept}")
        y = pd.to_numeric(out[outcome_name], errors="coerce")
        state = out[state_name].astype("string")
        positive = state.isin(["prior_positive", "current_yes"])
        negative = state.eq("current_no")
        unresolved = ~(positive | negative)
        if not y[positive].eq(1).all() or not y[negative].eq(0).all() or y[unresolved].notna().any():
            raise ValueError(f"Outcome/status consistency check failed for {concept}")
        if not set(y.dropna().unique()).issubset({0.0, 1.0}):
            raise ValueError(f"Unexpected outcome coding for {concept}")
        outcome_checks[concept] = {
            "valid_positive_private": int(positive.sum()),
            "valid_negative_private": int(negative.sum()),
            "unresolved_private": int(unresolved.sum()),
        }
    report = {
        "scope": "protected Wave 4/5 derived cumulative diagnosis outcome readback and alignment validation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "wave": wave,
        "status": "passed",
        "row_count_private": len(out),
        "unique_nonmissing_ids": True,
        "source_row_order_preserved": True,
        "frame_weight_psu_exact_alignment_private": base_checks,
        "outcome_route_consistency_private": outcome_checks,
        "input_sha256_private": sha256(input_path),
        "output_sha256_private": sha256(derived_path),
        "prepared_manifest_sha256_private": sha256(manifest_path),
        "derivation_qa_sha256_private": sha256(route_path),
        "association_models_fitted": 0,
        "publication": "private QA only; no participant-level output or exact counts approved for publication",
    }
    qa_path = private_path(PRIVATE / "qa_outputs" / f"wave{wave}_derived_outcome_validation_private.json")
    if qa_path.exists():
        raise FileExistsError("Refusing to overwrite protected validation report")
    qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        os.chmod(qa_path, 0o600)
    return {"status": "passed", "wave": wave, "concepts": len(outcome_checks)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", choices=("2018", "2020"), required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.wave)))


if __name__ == "__main__":
    main()
