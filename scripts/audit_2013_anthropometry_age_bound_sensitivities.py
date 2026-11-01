#!/usr/bin/env python3
"""Privately reconcile the Wave 2 age-interval sensitivity result families.

The script compares the midpoint, lower-bound, and upper-bound model outputs
by registered exposure/phenotype pair. It writes exact diagnostics only below
CHARLS_EXWAS_PRIVATE_ROOT and does not create a publishable result payload.
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
from typing import Any

from project_paths import PRIVATE_ROOT, require_private_path


PRIVATE = PRIVATE_ROOT.resolve()
RESULTS = PRIVATE / "results"
QA = PRIVATE / "qa_outputs"
BOUNDS = ("midpoint", "lower", "upper")
FAMILY_STEM = "2013_household_environment_anthropometry_K75"
EXPECTED_K = 75
KEY_FIELDS = (
    "exposure_concept_id", "exposure_variable", "contrast",
    "phenotype_concept_id", "phenotype_variable",
)


def private_path(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE):
        raise ValueError(f"Private result/QA path escaped the protected root: {resolved}")
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _paths(bound: str) -> tuple[Path, Path]:
    suffix = "county_stage_v2_midpoint_primary" if bound == "midpoint" else f"county_stage_v2_{bound}_age_sensitivity"
    result = RESULTS / f"{FAMILY_STEM}_{suffix}_raw_private.csv"
    qa = QA / f"{FAMILY_STEM}_{suffix}_private.json"
    return private_path(result), private_path(qa)


def _read_family(bound: str) -> tuple[dict[tuple[str, ...], dict[str, Any]], dict[str, Any]]:
    result_path, qa_path = _paths(bound)
    missing = [str(path) for path in (result_path, qa_path) if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Required private {bound} family artifacts are missing")
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    if qa.get("wave") != "2013" or qa.get("registered_K") != EXPECTED_K:
        raise ValueError(f"Unexpected private QA family metadata for {bound}")
    if qa.get("age_bound") != bound:
        raise ValueError(f"Private QA age-bound label mismatch for {bound}")
    if qa.get("age_bound_sensitivity_not_primary") is not (bound != "midpoint"):
        raise ValueError(f"Private QA primary/sensitivity role mismatch for {bound}")
    if qa.get("result_sha256_private") != sha256(result_path):
        raise ValueError(f"Private result checksum mismatch for {bound}")
    config_path = private_path(
        PRIVATE / "analysis_review" / f"wave2013_anthropometry_{bound}_county_stage_v2_config_private.json"
    )
    if not config_path.is_file() or qa.get("analysis_config_sha256_private") != sha256(config_path):
        raise ValueError(f"Private analysis configuration checksum mismatch for {bound}")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if (config.get("status") != "user_authorized_internal_analysis"
            or config.get("registered_K") != EXPECTED_K
            or config.get("family_id") != f"wave2013_household_environment_anthropometry_{bound}"
            or config.get("age_field") != f"midpoint of protected age interval bounds ({bound})"):
        raise ValueError(f"Unexpected private analysis configuration for {bound}")
    if qa.get("release_status") != "private_internal_results_pending_technical_and_disclosure_review":
        raise ValueError(f"Unexpected release state for private {bound} family")

    rows: dict[tuple[str, ...], dict[str, Any]] = {}
    with result_path.open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            key = tuple(row.get(field, "") for field in KEY_FIELDS)
            if not all(key) or key in rows:
                raise ValueError(f"Invalid or duplicate registered pair in {bound} family")
            if row.get("fit_status") != "success":
                raise ValueError(f"Non-success registered row in {bound} family")
            for field in ("estimate", "standard_error", "ci_lower", "ci_upper", "p_value"):
                value = float(row[field])
                if not math.isfinite(value):
                    raise ValueError(f"Non-finite {field} in {bound} family")
            rows[key] = row
    if len(rows) != EXPECTED_K:
        raise ValueError(f"Incomplete registered family in {bound} output")
    if qa.get("success") != EXPECTED_K or qa.get("inestimable_or_nonconverged") != 0:
        raise ValueError(f"Private QA success totals do not match complete family for {bound}")
    return rows, {"result_path": result_path, "qa_path": qa_path,
                  "config_path": config_path, "config": config, "qa": qa}


def _float(row: dict[str, Any], field: str) -> float:
    return float(row[field])


def audit() -> dict[str, Any]:
    families = {bound: _read_family(bound) for bound in BOUNDS}
    key_sets = {bound: set(entry[0]) for bound, entry in families.items()}
    if not (key_sets["midpoint"] == key_sets["lower"] == key_sets["upper"]):
        raise ValueError("Registered exposure/phenotype pairs differ across age bounds")

    reference_bindings = families["midpoint"][1]["qa"].get("input_bindings_private")
    if not isinstance(reference_bindings, dict):
        raise ValueError("Private midpoint QA is missing its source hash bindings")
    for bound in BOUNDS[1:]:
        if families[bound][1]["qa"].get("input_bindings_private") != reference_bindings:
            raise ValueError("Age-bound families do not use the same hash-bound inputs")
    reference_config = families["midpoint"][1]["config"]
    config_fields = set(reference_config) - {"family_id", "age_field"}
    for bound in BOUNDS[1:]:
        config = families[bound][1]["config"]
        if {key: config.get(key) for key in config_fields} != {
            key: reference_config.get(key) for key in config_fields
        }:
            raise ValueError("Age-bound families differ in non-age model configuration")

    diagnostics: list[dict[str, Any]] = []
    sign_discordance = 0
    max_abs_estimate_shift = 0.0
    max_abs_se_shift = 0.0
    for key in sorted(key_sets["midpoint"]):
        paired = {bound: families[bound][0][key] for bound in BOUNDS}
        expected_models = {
            "midpoint": "M1_age_midpoint_sex",
            "lower": "M1_age_lower_sex_sensitivity",
            "upper": "M1_age_upper_sex_sensitivity",
        }
        if any(paired[bound].get("model_id") != expected_models[bound] for bound in BOUNDS):
            raise ValueError("Age-bound result model labels do not match their specification")
        estimates = {bound: _float(paired[bound], "estimate") for bound in BOUNDS}
        ses = {bound: _float(paired[bound], "standard_error") for bound in BOUNDS}
        signs = {bound: (estimates[bound] > 0) - (estimates[bound] < 0) for bound in BOUNDS}
        same_sign = len(set(signs.values())) == 1
        sign_discordance += int(not same_sign)
        estimate_shift = max(estimates.values()) - min(estimates.values())
        se_shift = max(ses.values()) - min(ses.values())
        max_abs_estimate_shift = max(max_abs_estimate_shift, abs(estimate_shift))
        max_abs_se_shift = max(max_abs_se_shift, abs(se_shift))
        diagnostics.append({
            "registered_pair": dict(zip(KEY_FIELDS, key)),
            "estimate_by_age_bound": estimates,
            "standard_error_by_age_bound": ses,
            "model_n_by_age_bound": {
                bound: int(paired[bound]["n_model"]) for bound in BOUNDS
            },
            "same_estimate_sign_across_bounds": same_sign,
            "absolute_estimate_range": abs(estimate_shift),
            "absolute_standard_error_range": abs(se_shift),
        })

    bindings = {}
    for bound, (_, artifacts) in families.items():
        bindings[bound] = {
            "result_file": Path(artifacts["result_path"]).name,
            "result_sha256_private": sha256(artifacts["result_path"]),
            "qa_file": Path(artifacts["qa_path"]).name,
            "qa_sha256_private": sha256(artifacts["qa_path"]),
            "config_file": Path(artifacts["config_path"]).name,
            "config_sha256_private": sha256(artifacts["config_path"]),
            "code_commit": artifacts["qa"].get("code_commit"),
            "analysis_config_sha256_private": artifacts["qa"].get("analysis_config_sha256_private"),
        }
    commits = {entry["code_commit"] for entry in bindings.values()}
    if len(commits) != 1:
        raise ValueError("Age-bound families were run from different code commits")

    return {
        "scope": "private Wave 2 anthropometry age-bound sensitivity reconciliation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "release_status": "private_internal_qa_not_for_publication",
        "registered_K": EXPECTED_K,
        "age_bounds": list(BOUNDS),
        "complete_family_pair_match": True,
        "all_registered_fits_successful": True,
        "estimate_sign_discordant_pairs": sign_discordance,
        "maximum_absolute_estimate_range": max_abs_estimate_shift,
        "maximum_absolute_standard_error_range": max_abs_se_shift,
        "code_commit": next(iter(commits)),
        "private_input_bindings": bindings,
        "private_pair_diagnostics": diagnostics,
        "interpretation": "Bound sensitivity evaluates age-interval uncertainty; it does not select models by p-value and is not a separate discovery family.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=QA / "2013_anthropometry_age_bound_reconciliation_county_stage_v2_private.json")
    args = parser.parse_args()
    output = private_path(args.output)
    summary = audit()
    output.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(output.parent, 0o700)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(output, 0o600)
    print(json.dumps({
        "status": "private_reconciliation_complete",
        "registered_K": summary["registered_K"],
        "age_bounds": summary["age_bounds"],
        "output": output.name,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
