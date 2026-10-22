#!/usr/bin/env python3
"""Validate CHARLS ExWAS result-table structure and release-state invariants.

This utility reads only the supplied result CSV and the public project schema.
It does not read respondent data or fit statistical models.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "audit" / "EXWAS_result_schema_v2.csv"
FIT_STATUSES = {
    "planned",
    "blocked_design_verification",
    "blocked_data_access",
    "success",
    "nonconvergence",
    "inestimable",
    "code_error",
}
WEIGHT_STATUSES = {
    "verified_used",
    "verified_unweighted",
    "not_applicable",
    "unavailable_pending_authorized_file",
    "unresolved",
}
DESIGN_STATUSES = {
    "verified_used",
    "not_released",
    "unavailable_pending_authorized_file",
    "not_applicable",
    "unresolved",
}
ESTIMATE_FIELDS = (
    "estimate",
    "standard_error",
    "ci_lower",
    "ci_upper",
    "p_value",
    "q_value_by",
    "p_bonferroni",
)
COUNT_FIELDS = (
    "n_interview",
    "n_eligible",
    "n_exposure_valid",
    "n_phenotype_valid",
    "n_pair_complete",
    "n_model",
)


def read_schema(path: Path = SCHEMA_PATH) -> tuple[list[str], dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"schema is empty: {path}")
    names = [row["field"].strip() for row in rows]
    if len(names) != len(set(names)):
        raise ValueError("schema has duplicate field names")
    return names, {row["field"].strip(): row["required"].strip() for row in rows}


def _number(value: str, field: str, errors: list[str], row_no: int) -> float | None:
    if value == "":
        return None
    try:
        parsed = float(value)
    except ValueError:
        errors.append(f"row {row_no}: {field} is not numeric")
        return None
    if not math.isfinite(parsed):
        errors.append(f"row {row_no}: {field} must be finite")
        return None
    return parsed


def validate_rows(rows: list[dict[str, str]], schema_fields: list[str], required: dict[str, str]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for row_no, row in enumerate(rows, start=2):
        for field in schema_fields:
            value = row.get(field, "").strip()
            if required[field] == "yes" and not value:
                errors.append(f"row {row_no}: required field {field} is blank")

        analysis_id = row.get("analysis_id", "").strip()
        if analysis_id:
            if analysis_id in seen_ids:
                errors.append(f"row {row_no}: duplicate analysis_id {analysis_id}")
            seen_ids.add(analysis_id)

        fit_status = row.get("fit_status", "").strip()
        if fit_status and fit_status not in FIT_STATUSES:
            errors.append(f"row {row_no}: unsupported fit_status {fit_status}")

        for field, allowed in (
            ("weight_status", WEIGHT_STATUSES),
            ("psu_status", DESIGN_STATUSES),
            ("stratum_status", DESIGN_STATUSES),
        ):
            value = row.get(field, "").strip()
            if value and value not in allowed:
                errors.append(f"row {row_no}: unsupported {field} {value}")

        for field in ("weight_id", "psu_id", "stratum_id"):
            status_field = {
                "weight_id": "weight_status",
                "psu_id": "psu_status",
                "stratum_id": "stratum_status",
            }[field]
            status = row.get(status_field, "").strip()
            has_id = bool(row.get(field, "").strip())
            if status == "verified_used" and not has_id:
                errors.append(f"row {row_no}: {status_field}=verified_used requires {field}")
            if status and status != "verified_used" and has_id:
                errors.append(f"row {row_no}: {field} must be blank unless {status_field}=verified_used")

        numeric_values: dict[str, float | None] = {}
        for field in (*ESTIMATE_FIELDS, *COUNT_FIELDS):
            if field in row:
                numeric_values[field] = _number(row.get(field, "").strip(), field, errors, row_no)

        for field in ("p_value", "q_value_by", "p_bonferroni"):
            value = numeric_values.get(field)
            if value is not None and not 0 <= value <= 1:
                errors.append(f"row {row_no}: {field} must be between 0 and 1")
        if numeric_values.get("standard_error") is not None and numeric_values["standard_error"] < 0:
            errors.append(f"row {row_no}: standard_error cannot be negative")

        counts: dict[str, int] = {}
        for field in COUNT_FIELDS:
            value = numeric_values.get(field)
            if value is None:
                continue
            if value < 0 or not value.is_integer():
                errors.append(f"row {row_no}: {field} must be a non-negative integer")
            else:
                counts[field] = int(value)
        for smaller, larger in (
            ("n_eligible", "n_interview"),
            ("n_exposure_valid", "n_eligible"),
            ("n_phenotype_valid", "n_eligible"),
            ("n_pair_complete", "n_exposure_valid"),
            ("n_pair_complete", "n_phenotype_valid"),
            ("n_model", "n_pair_complete"),
        ):
            if smaller in counts and larger in counts and counts[smaller] > counts[larger]:
                errors.append(f"row {row_no}: {smaller} cannot exceed {larger}")

        lo, hi = numeric_values.get("ci_lower"), numeric_values.get("ci_upper")
        if lo is not None and hi is not None and lo > hi:
            errors.append(f"row {row_no}: ci_lower cannot exceed ci_upper")

        has_estimate = any(row.get(field, "").strip() for field in ESTIMATE_FIELDS)
        if fit_status == "success":
            for field in ("estimate", "standard_error", "ci_lower", "ci_upper", "p_value", "n_model"):
                if not row.get(field, "").strip():
                    errors.append(f"row {row_no}: success requires {field}")
            if row.get("weight_status", "").strip() in {"unresolved", "unavailable_pending_authorized_file"}:
                errors.append(f"row {row_no}: successful fit has unresolved/unavailable weight status")
            if row.get("psu_status", "").strip() in {"unresolved", "unavailable_pending_authorized_file"}:
                errors.append(f"row {row_no}: successful fit has unresolved/unavailable PSU status")
            if row.get("stratum_status", "").strip() in {"unresolved", "unavailable_pending_authorized_file"}:
                errors.append(f"row {row_no}: successful fit has unresolved/unavailable stratum status")
            variance = row.get("variance_design", "").strip().lower()
            if "not fit-ready" in variance or "unresolved" in variance or "not verified" in variance:
                errors.append(f"row {row_no}: successful fit cannot claim an unverified variance design")
        elif has_estimate:
            errors.append(f"row {row_no}: estimate fields must be blank unless fit_status=success")

    return errors


def validate_csv(path: Path, schema_path: Path = SCHEMA_PATH) -> list[str]:
    schema_fields, required = read_schema(schema_path)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        missing = [field for field in schema_fields if field not in headers]
        if missing:
            return ["CSV is missing schema fields: " + ", ".join(missing)]
        rows = list(reader)
    return validate_rows(rows, schema_fields, required)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="Result CSV using EXWAS_result_schema_v2.csv")
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH, help="Schema CSV path")
    args = parser.parse_args()
    try:
        errors = validate_csv(args.csv_path, args.schema)
    except (OSError, ValueError, KeyError) as exc:
        print(f"FAIL: {exc}")
        return 2
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print(f"PASS: {args.csv_path} conforms to schema and release-state checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
