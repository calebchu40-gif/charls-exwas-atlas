#!/usr/bin/env python3
"""Apply one BY/Bonferroni correction to all registered wave-specific primary tests.

This is a private-only finalization step. It does not pool effect estimates,
select hypotheses by significance, or approve public release. The input set
contains one declared primary model from each of Waves 1--5; secondary and
sensitivity models are intentionally excluded.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from adjust_exwas_pvalues import adjust_pvalues
from project_paths import PRIVATE_ROOT, require_private_path
from validate_exwas_result_table import read_schema, validate_csv

PRIVATE = PRIVATE_ROOT.resolve()
RESULTS = PRIVATE / "results"
OUTPUT = RESULTS / "charls_waves1_5_primary_county_stage_BY_global_K845_private_v1.csv"
AUDIT = OUTPUT.with_suffix(OUTPUT.suffix + ".finalization.json")
FAMILY_ID = "charls_waves1_5_primary_county_stage_global"

INPUTS = (
    ("2011", "wave1_household_environment_K240_county_stage_schema_v3_private_v2.csv", "M1_age_sex_urban_county_stage", 240),
    ("2013", "wave2013_household_environment_anthropometry_K75_county_stage_v2_schema_v3_private.csv", "M1_age_midpoint_sex", 75),
    ("2015", "2015_household_environment_blood_K225_county_stage_v2_primary.csv", "M1_2015_age_sex", 225),
    ("2018", "wave2018_environment_disease_M0_M1_v3_county_stage_schema_v3_private.csv", "M1_age_sex_residence", 140),
    ("2020", "wave2020_environment_disease_M0_M1_v3_county_stage_schema_v3_private.csv", "M1_age_sex_residence", 165),
)
ALLOWED = {"success", "nonconvergence", "inestimable", "blocked_measurement_rule"}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def private_file(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE) or not resolved.is_file():
        raise ValueError("All family inputs must exist inside the protected private root")
    return resolved


def finalize() -> dict[str, object]:
    if OUTPUT.exists() or AUDIT.exists():
        raise FileExistsError("Refusing to overwrite an existing global-family finalization")
    schema, _ = read_schema()
    selected: list[dict[str, str]] = []
    bindings: list[dict[str, str]] = []
    expected_k_total = sum(item[3] for item in INPUTS)
    for wave, name, primary_model, expected_k in INPUTS:
        path = private_file(RESULTS / name)
        errors = validate_csv(path)
        if errors:
            raise ValueError(f"{name} failed schema validation: {'; '.join(errors[:5])}")
        with path.open(newline="", encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
        primary = [row for row in rows if row.get("model_id", "").strip() == primary_model
                   and row.get("wave", "").strip() == wave]
        if len(primary) != expected_k:
            raise ValueError(f"Wave {wave}: expected {expected_k} registered primary rows; found {len(primary)}")
        ids = [row.get("analysis_id", "").strip() for row in primary]
        if any(not value for value in ids) or len(ids) != len(set(ids)):
            raise ValueError(f"Wave {wave}: blank or duplicate primary analysis IDs")
        bad = sorted({row.get("fit_status", "").strip() for row in primary} - ALLOWED)
        if bad:
            raise ValueError(f"Wave {wave}: unresolved statuses block family correction: {bad}")
        for row in primary:
            if row.get("fit_status") == "success":
                p = float(row.get("p_value", "nan"))
                if not 0 <= p <= 1:
                    raise ValueError(f"Wave {wave}: invalid p-value in successful row")
            elif row.get("p_value", "").strip():
                raise ValueError(f"Wave {wave}: non-estimable row must not carry a p-value")
            selected.append({field: row.get(field, "") for field in schema})
        bindings.append({"wave": wave, "file": name, "model_id": primary_model,
                         "expected_K": str(expected_k), "source_sha256": sha(path)})
    all_ids = [row["analysis_id"] for row in selected]
    if len(selected) != expected_k_total or len(all_ids) != len(set(all_ids)):
        raise ValueError("Global primary family is incomplete or has duplicate cross-wave analysis IDs")

    for row in selected:
        row["multiple_testing_family"] = f"{FAMILY_ID};K={expected_k_total}"
    raw_p = [float(row["p_value"]) if row["fit_status"] == "success" else None for row in selected]
    adjusted = adjust_pvalues(raw_p)
    for row, q, bonf in zip(selected, adjusted["q_value_by"], adjusted["p_bonferroni"], strict=True):
        row["q_value_by"] = "" if q is None else format(q, ".17g")
        row["p_bonferroni"] = "" if bonf is None else format(bonf, ".17g")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(OUTPUT.parent, 0o700)
    fd, temp_name = tempfile.mkstemp(prefix=".charls-global-family-", suffix=".csv", dir=OUTPUT.parent)
    os.chmod(temp_name, 0o600)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=schema)
            writer.writeheader(); writer.writerows(selected); stream.flush(); os.fsync(stream.fileno())
        errors = validate_csv(temp)
        if errors:
            raise ValueError("Global family failed schema checks: " + "; ".join(errors[:8]))
        record = {
            "status": "private_global_primary_family_finalized",
            "family_id": FAMILY_ID, "family_size_K": expected_k_total,
            "adjustment": "Benjamini-Yekutieli and Bonferroni across all predeclared wave-specific primary hypotheses; inestimable hypotheses remain in K and receive no adjusted value",
            "analysis_scope": "One primary model per wave; no effect estimates pooled; secondary and sensitivity fits excluded",
            "variance_design": "County-stage WR Taylor approximation by documented householdID county segment; no released implicit strata, county PPS/FPC, or full split-community mapping",
            "input_bindings": bindings,
            "output_sha256": sha(temp), "created_utc": datetime.now(timezone.utc).isoformat(),
            "public_release_status": "not_approved",
        }
        audit_temp = AUDIT.with_name("." + AUDIT.name + ".tmp")
        if audit_temp.exists(): audit_temp.unlink()
        audit_temp.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.chmod(audit_temp, 0o600)
        os.replace(temp, OUTPUT); os.chmod(OUTPUT, 0o600)
        os.replace(audit_temp, AUDIT); os.chmod(AUDIT, 0o600)
    finally:
        temp.unlink(missing_ok=True)
    return {"status": "private_global_primary_family_finalized", "K": expected_k_total,
            "wave_count": len(INPUTS), "output": OUTPUT.name, "public_release_status": "not_approved"}


if __name__ == "__main__":
    print(json.dumps(finalize(), ensure_ascii=False, indent=2))
