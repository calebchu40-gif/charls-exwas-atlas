#!/usr/bin/env python3
"""Normalize the registered Wave 2 anthropometry family for private review.

This adapter consumes only protected K=75 run artifacts and hash-bound QA.
It marks estimability reviewed only when the technical review, age-bound
reconciliation and contrast-support report all pass. Exact outputs remain
under CHARLS_EXWAS_PRIVATE_ROOT; this command never publishes site data.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adjust_exwas_pvalues import adjust_pvalues
from project_paths import PRIVATE_ROOT, require_private_path
from validate_exwas_result_table import read_schema, validate_csv


PRIVATE = PRIVATE_ROOT.resolve()
RESULTS = PRIVATE / "results"
QA = PRIVATE / "qa_outputs"
REVIEW = PRIVATE / "analysis_review"
RAW_NAME = "2013_household_environment_anthropometry_K75_midpoint_primary_raw_private.csv"
RAW_QA_NAME = "2013_household_environment_anthropometry_K75_midpoint_primary_private.json"
CONFIG_NAME = "wave2013_anthropometry_midpoint_config_private.json"
TECH_REVIEW_NAME = "wave2013_anthropometry_technical_review_20261101_private.json"
SUPPORT_NAME = "wave2013_registered_contrast_support_reconciliation_v2_private.json"
AGE_RECON_NAME = "2013_anthropometry_age_bound_reconciliation_private.json"
REVIEW_ID = "w2013-anthro-estimability-20261101-v1"
ATLAS_FAMILY = "wave2013_household_environment_anthropometry"


def private_path(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE):
        raise ValueError(f"Private result path escaped protected storage: {resolved}")
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path.name}")
    return payload


def normalize(output: Path) -> dict[str, Any]:
    raw = private_path(RESULTS / RAW_NAME)
    raw_qa_path = private_path(QA / RAW_QA_NAME)
    config_path = private_path(REVIEW / CONFIG_NAME)
    technical_path = private_path(REVIEW / TECH_REVIEW_NAME)
    support_path = private_path(QA / SUPPORT_NAME)
    age_recon_path = private_path(QA / AGE_RECON_NAME)
    output = private_path(output)
    record_path = output.with_suffix(output.suffix + ".normalization.json")
    if output.exists() or record_path.exists():
        raise FileExistsError("Refusing to overwrite a prior private normalized result")

    raw_qa = _read_json(raw_qa_path)
    config = _read_json(config_path)
    technical = _read_json(technical_path)
    support = _read_json(support_path)
    age_recon = _read_json(age_recon_path)
    expected_bindings = technical.get("private_bindings", {}).get("midpoint", {})
    if (technical.get("status") != "internal_technical_QA_pass"
            or not technical.get("checks")
            or not all(technical["checks"].values())
            or expected_bindings.get("result_sha256") != sha256(raw)
            or expected_bindings.get("qa_sha256") != sha256(raw_qa_path)
            or expected_bindings.get("config_sha256") != sha256(config_path)):
        raise ValueError("Wave 2 technical review is missing or does not bind the raw family")
    if (support.get("status") != "support_reconciliation_complete"
            or not support.get("checks")
            or not all(support["checks"].values())
            or support.get("input_bindings_private", {}).get("midpoint_result_sha256") != sha256(raw)):
        raise ValueError("Wave 2 contrast-support reconciliation is missing or unresolved")
    if (not age_recon.get("complete_family_pair_match")
            or not age_recon.get("all_registered_fits_successful")
            or age_recon.get("estimate_sign_discordant_pairs") != 0
            or technical.get("age_bound_reconciliation_sha256") != sha256(age_recon_path)):
        raise ValueError("Wave 2 age-bound family reconciliation is missing or unresolved")
    if (config.get("status") != "user_authorized_internal_analysis"
            or config.get("registered_K") != 75
            or config.get("age_field") != "midpoint of protected age interval bounds (midpoint)"):
        raise ValueError("The protected midpoint configuration is not the registered K=75 primary")

    with raw.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 75 or len({row.get("analysis_id", "") for row in rows}) != 75:
        raise ValueError("Raw midpoint results do not contain the complete unique K=75 family")
    if any(row.get("fit_status") != "success" for row in rows):
        raise ValueError("A non-success hypothesis needs its own reviewed final status before normalization")

    schema_fields, _ = read_schema()
    output_fields = schema_fields + (["contrast"] if "contrast" not in schema_fields else [])
    p_values = [float(row["p_value"]) for row in rows]
    adjusted = adjust_pvalues(p_values)
    normalized: list[dict[str, str]] = []
    for index, source in enumerate(rows):
        row = {field: source.get(field, "") for field in schema_fields}
        if "contrast" not in schema_fields:
            row["contrast"] = source.get("contrast", "")
        row["multiple_testing_family"] = f"{ATLAS_FAMILY};K=75"
        row["estimability_review_status"] = "reviewed_pass"
        row["estimability_review_id"] = REVIEW_ID
        row["q_value_by"] = format(adjusted["q_value_by"][index], ".17g")
        row["p_bonferroni"] = format(adjusted["p_bonferroni"][index], ".17g")
        normalized.append(row)

    output.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(output.parent, 0o700)
    record = {
        "scope": "private Wave 2 K=75 schema-v3 normalization",
        "status": "normalized_for_private_disclosure_review",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "registered_K": 75,
        "estimability_review_id": REVIEW_ID,
        "review_basis": "internal technical review, hash-bound age-bound reconciliation, and complete contrast-level support reconciliation; no p-value-based pair selection",
        "multiplicity": "BY and Bonferroni recomputed across the complete registered wave-specific K=75 primary family",
        "public_release": "not performed; separate disclosure review is required",
        "input_bindings_private": {
            "raw_results_sha256": sha256(raw),
            "raw_qa_sha256": sha256(raw_qa_path),
            "configuration_sha256": sha256(config_path),
            "technical_review_sha256": sha256(technical_path),
            "contrast_support_report_sha256": sha256(support_path),
            "age_bound_reconciliation_sha256": sha256(age_recon_path),
            "code_commit": "commit: " + __import__("subprocess").check_output(
                ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1], text=True
            ).strip(),
        },
    }
    temp_csv: Path | None = None
    temp_record: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", newline="", encoding="utf-8", delete=False,
                                         dir=output.parent, prefix=f".{output.name}.", suffix=".tmp") as stream:
            writer = csv.DictWriter(stream, fieldnames=output_fields, extrasaction="raise")
            writer.writeheader()
            writer.writerows(normalized)
            stream.flush()
            os.fsync(stream.fileno())
            temp_csv = Path(stream.name)
        errors = validate_csv(temp_csv)
        if errors:
            raise ValueError("Normalized Wave 2 table failed schema validation: " + "; ".join(errors[:8]))
        record["output_sha256_private"] = sha256(temp_csv)
        record["output_filename_private"] = output.name
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False,
                                         dir=record_path.parent, prefix=f".{record_path.name}.", suffix=".tmp") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
            temp_record = Path(stream.name)
        os.chmod(temp_csv, 0o600)
        os.chmod(temp_record, 0o600)
        os.replace(temp_csv, output)
        temp_csv = None
        os.replace(temp_record, record_path)
        temp_record = None
    finally:
        if temp_csv is not None:
            temp_csv.unlink(missing_ok=True)
        if temp_record is not None:
            temp_record.unlink(missing_ok=True)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=RESULTS / "wave2013_household_environment_anthropometry_K75_schema_v3_private.csv")
    args = parser.parse_args()
    try:
        record = normalize(args.output)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(2, f"FAIL: {exc}\n")
    print(json.dumps({"status": record["status"], "registered_K": record["registered_K"],
                      "output": record["output_filename_private"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
