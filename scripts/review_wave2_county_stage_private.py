#!/usr/bin/env python3
"""Bind internal Wave 2 county-stage QA to the exact private rerun artifacts."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from project_paths import PRIVATE_ROOT, require_private_path

PRIVATE = PRIVATE_ROOT.resolve()
RESULT = PRIVATE / "results" / "2013_household_environment_anthropometry_K75_county_stage_v2_midpoint_primary_raw_private.csv"
QA = PRIVATE / "qa_outputs" / "2013_household_environment_anthropometry_K75_county_stage_v2_midpoint_primary_private.json"
CONFIG = PRIVATE / "analysis_review" / "wave2013_anthropometry_midpoint_county_stage_v2_config_private.json"
SUPPORT = PRIVATE / "qa_outputs" / "wave2013_registered_contrast_support_reconciliation_county_stage_v2_private.json"
AGE = PRIVATE / "qa_outputs" / "2013_anthropometry_age_bound_reconciliation_county_stage_v2_private.json"
OUTPUT = PRIVATE / "analysis_review" / "wave2013_anthropometry_county_stage_v2_technical_review_private.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def private(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE):
        raise ValueError("Wave 2 QA artifact escaped the protected root")
    if not resolved.is_file():
        raise FileNotFoundError(resolved.name)
    return resolved


def main() -> None:
    paths = [private(p) for p in (RESULT, QA, CONFIG, SUPPORT, AGE)]
    result, qa_path, config_path, support_path, age_path = paths
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    support = json.loads(support_path.read_text(encoding="utf-8"))
    age = json.loads(age_path.read_text(encoding="utf-8"))
    with result.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 75 or len({r.get("analysis_id") for r in rows}) != 75:
        raise ValueError("County-stage Wave 2 result does not contain the complete unique family")
    finite = True
    for row in rows:
        if row.get("fit_status") != "success":
            finite = False
            break
        vals = [float(row[k]) for k in ("estimate", "standard_error", "ci_lower", "ci_upper", "p_value")]
        if not all(map(__import__("math").isfinite, vals)) or vals[1] <= 0 or vals[2] > vals[3]:
            finite = False
            break
    bindings = {
        "result_sha256": sha(result), "qa_sha256": sha(qa_path),
        "config_sha256": sha(config_path), "support_sha256": sha(support_path),
        "age_reconciliation_sha256": sha(age_path),
    }
    checks = {
        "registered_family_complete": len(rows) == 75,
        "all_fits_successful": all(r.get("fit_status") == "success" for r in rows),
        "finite_estimates_and_intervals": finite,
        "pair_n_and_county_psu_support": support.get("status") == "support_reconciliation_complete" and all(support.get("checks", {}).values()),
        "official_wave_weight_and_frame": config.get("weight") == "Biomarker_weight from the official Wave 2 Weights module" and config.get("target_frame", "").startswith("crosssection=1"),
        "documented_county_key": config.get("psu", "").startswith("documented county segment of householdID") and "county" in config.get("variance", "").casefold(),
        "age_bound_family_reconciled": age.get("complete_family_pair_match") is True and age.get("all_registered_fits_successful") is True and age.get("estimate_sign_discordant_pairs") == 0,
    }
    if not all(checks.values()):
        raise ValueError("County-stage Wave 2 technical checks need follow-up: " + ", ".join(k for k,v in checks.items() if not v))
    report = {
        "scope": "internal technical QA for the Wave 2 county-stage primary family; not an independent scientific review",
        "status": "internal_technical_QA_pass", "created_utc": datetime.now(timezone.utc).isoformat(),
        "registered_K": 75, "checks": checks, "primary_age_specification": "midpoint",
        "sensitivity_age_specifications": ["lower", "upper"],
        "age_bound_reconciliation_sha256": bindings["age_reconciliation_sha256"],
        "private_bindings": {"midpoint": {"result_sha256": bindings["result_sha256"], "qa_sha256": bindings["qa_sha256"], "config_sha256": bindings["config_sha256"]}},
        "support_sha256": bindings["support_sha256"], "public_release_status": "not_approved",
        "review_kind": "automated_internal_consistency_and_support_reconciliation",
        "design_summary": "Official Wave 2 cross-sectional Biomarker_weight; householdID county-stage WR Taylor approximation; no released implicit strata/FPC; community-only analysis retained as sensitivity.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True); os.chmod(OUTPUT.parent, 0o700)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); os.chmod(OUTPUT, 0o600)
    print("PASS: county-stage Wave 2 internal QA is hash-bound; exact diagnostics remain private")


if __name__ == "__main__":
    main()
