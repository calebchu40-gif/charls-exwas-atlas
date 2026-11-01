#!/usr/bin/env python3
"""Compare county-stage primary estimates with historical community-cluster runs.

This is a method-sensitivity audit, not a second discovery family. Exact
coefficients and matching diagnostics are written only under PRIVATE_ROOT.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from project_paths import PRIVATE_ROOT, require_private_path

PRIVATE = PRIVATE_ROOT.resolve()
PRIMARY = PRIVATE / "results" / "charls_waves1_5_primary_county_stage_BY_global_K845_private_v1.csv"
HISTORICAL = {
    "2011": PRIVATE / "results" / "wave1_household_environment_K240_schema_v3_20261031_final.csv",
    "2013": PRIVATE / "results" / "wave2013_household_environment_anthropometry_K75_schema_v3_v2_private.csv",
    "2015": PRIVATE / "results" / "2015_household_environment_blood_K225_schema_v3.csv",
}
OUTPUT = PRIVATE / "qa_outputs" / "county_vs_community_primary_sensitivity_private_v1.json"
PRIMARY_FAMILY_SIZES = {"2011": 240, "2013": 75, "2015": 225}


def private_path(path: Path) -> Path:
    result = require_private_path(path)
    if not result.is_relative_to(PRIVATE):
        raise ValueError(f"Path escaped protected storage: {result}")
    return result


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with private_path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _key(row: dict[str, str]) -> tuple[str, str, str, str]:
    # Some waves register multiple source items under one exposure concept;
    # include the source field so same-labelled contrasts remain distinct.
    return (row.get("exposure_concept_id", ""), row.get("exposure_variable", ""),
            row.get("phenotype_concept_id", ""), row.get("contrast", ""))


def _number(value: str | None) -> float | None:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def compare() -> dict:
    primary_rows = read_csv(PRIMARY)
    primary_hash = digest(PRIMARY)
    waves = {}
    for wave, historical_path in HISTORICAL.items():
        new = [r for r in primary_rows if r["wave"] == wave]
        old = read_csv(historical_path)
        if len(new) != PRIMARY_FAMILY_SIZES[wave] or len(old) != PRIMARY_FAMILY_SIZES[wave]:
            raise ValueError(f"Wave {wave}: primary or sensitivity family is incomplete")
        if any("county" not in (r.get("variance_design", "") + r.get("psu_id", "")).casefold() for r in new):
            raise ValueError(f"Wave {wave}: current result is not county-stage clustered")
        if any("communityid" not in (r.get("variance_design", "") + r.get("psu_id", "")).casefold() for r in old):
            raise ValueError(f"Wave {wave}: historical comparator is not community-clustered")
        new_map = {_key(r): r for r in new}
        old_map = {_key(r): r for r in old}
        if len(new_map) != len(new) or len(old_map) != len(old) or set(new_map) != set(old_map):
            raise ValueError(f"Wave {wave}: hypothesis identity mismatch across variance runs")
        paired = [(new_map[k], old_map[k]) for k in sorted(new_map)]
        valid = [(a, b) for a, b in paired if a.get("fit_status") == "success" and b.get("fit_status") == "success"]
        new_beta = np.array([_number(a.get("estimate")) for a, _ in valid], dtype=float)
        old_beta = np.array([_number(b.get("estimate")) for _, b in valid], dtype=float)
        new_se = np.array([_number(a.get("standard_error")) for a, _ in valid], dtype=float)
        old_se = np.array([_number(b.get("standard_error")) for _, b in valid], dtype=float)
        if any(np.isnan(x).any() for x in (new_beta, old_beta, new_se, old_se)):
            raise ValueError(f"Wave {wave}: a successful matched row has nonnumeric estimate/SE")
        nonzero = (new_beta != 0) & (old_beta != 0)
        waves[wave] = {
            "registered_K_private": len(paired),
            "both_estimable_private": len(valid),
            "status_disagreement_private": sum(a.get("fit_status") != b.get("fit_status") for a, b in paired),
            "coefficient_sign_concordance_private": float(np.mean(np.sign(new_beta[nonzero]) == np.sign(old_beta[nonzero]))) if nonzero.any() else None,
            "coefficient_pearson_r_private": float(np.corrcoef(new_beta, old_beta)[0, 1]) if len(valid) > 2 else None,
            "median_absolute_coefficient_change_private": float(np.median(np.abs(new_beta - old_beta))) if len(valid) else None,
            "median_county_to_community_se_ratio_private": float(np.median(new_se / old_se)) if len(valid) and np.all(old_se > 0) else None,
            "new_county_result_sha256_private": primary_hash,
            "historical_community_result_sha256_private": digest(historical_path),
            "comparison_note": "coefficient comparison only where both fitted; this is a variance-cluster sensitivity, not a pooled analysis",
        }
    report = {
        "status": "passed_identity_and_numeric_sensitivity_reconciliation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "primary_global_result_sha256_private": primary_hash,
        "waves": waves,
        "scope": "Wave 1-3 county-stage primary vs historical community-cluster same-hypothesis comparison",
        "limitation": "Does not recover unavailable implicit strata, county PPS/FPC, or split-community design; coefficients may also reflect plan-version differences and must be interpreted alongside the frozen plan hashes.",
        "release": "private only; no exact sensitivity metrics copied to Pages",
    }
    out = private_path(OUTPUT)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600); os.replace(tmp, out)
    return report


if __name__ == "__main__":
    result = compare()
    print(json.dumps({"status": result["status"], "waves_compared": list(result["waves"]),
                      "report_sha256_private": digest(OUTPUT)}, ensure_ascii=False))
