"""Aggregate-only integrity audit for protected CHARLS pilot result tables.

This checks the shape and numerical completeness of the two existing local
exploratory output tables and independently recomputes their declared BY and
Bonferroni adjustments. It never reads respondent microdata, never prints
pair-level estimates/support, and always labels formal design validity as
unverified. Its report is written only beneath the protected local root.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path


PILOT_DIR = PRIVATE_ROOT / "pilot_2011_water_blood"
DEFAULT_OUTPUT = QA_OUTPUT_DIR / "pilot_technical_integrity_aggregate.json"
NUMERIC_FIELDS = (
    "estimate", "standard_error", "ci_lower", "ci_upper", "p_value",
    "q_value_by", "p_bonferroni", "design_df",
)
ANALYSIS_KEY_FIELDS = (
    "wave", "exposure_concept_id", "phenotype_concept_id", "model_id",
)
REQUIRED_FIT_FIELDS = (
    "estimate", "standard_error", "ci_lower", "ci_upper", "p_value", "design_df",
)
FAMILY_RE = re.compile(r";K=([1-9][0-9]*)$")


def private_path(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError(f"Refusing path outside protected CHARLS storage: {resolved}")
    return resolved


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def by_adjust(p_values: list[float]) -> list[float]:
    """Benjamini–Yekutieli adjusted p-values in original row order."""
    size = len(p_values)
    harmonic = sum(1 / rank for rank in range(1, size + 1))
    order = sorted(range(size), key=p_values.__getitem__)
    adjusted = [0.0] * size
    running_min = 1.0
    for rank in range(size, 0, -1):
        index = order[rank - 1]
        running_min = min(running_min, p_values[index] * size * harmonic / rank, 1.0)
        adjusted[index] = running_min
    return adjusted


def audit_table(filename: str, expected_family_size: int) -> dict[str, Any]:
    path = private_path(PILOT_DIR / filename)
    rows = read_rows(path)
    required = {*ANALYSIS_KEY_FIELDS, "fit_status", *NUMERIC_FIELDS,
                "multiple_testing_family", "engine_warnings_private"}
    if rows and not required.issubset(rows[0]):
        raise ValueError(f"Required columns absent from protected output: {filename}")

    contrast_key = "term" if "term" in rows[0] else "contrast"
    if rows and contrast_key not in rows[0]:
        raise ValueError(f"No term/contrast key in protected output: {filename}")
    keys = [tuple(row.get(field, "").strip() for field in (*ANALYSIS_KEY_FIELDS, contrast_key))
            for row in rows]
    duplicate_keys = len(keys) - len(set(keys))
    model_rows = Counter(row.get("model_id", "") for row in rows)
    fit_statuses = Counter(row.get("fit_status", "") for row in rows)
    blank_fields = {
        field: sum(not row.get(field, "").strip() for row in rows)
        for field in NUMERIC_FIELDS
    }
    nonfinite_fields = {field: 0 for field in NUMERIC_FIELDS}
    invalid_ranges = {"p_value": 0, "q_value_by": 0, "p_bonferroni": 0,
                      "negative_standard_error": 0, "reversed_confidence_interval": 0}
    for row in rows:
        parsed: dict[str, float] = {}
        for field in NUMERIC_FIELDS:
            raw = row.get(field, "").strip()
            if not raw:
                continue
            try:
                value = float(raw)
            except ValueError:
                nonfinite_fields[field] += 1
                continue
            if not math.isfinite(value):
                nonfinite_fields[field] += 1
                continue
            parsed[field] = value
        for field in ("p_value", "q_value_by", "p_bonferroni"):
            if field in parsed and not 0 <= parsed[field] <= 1:
                invalid_ranges[field] += 1
        if parsed.get("standard_error", 0) < 0:
            invalid_ranges["negative_standard_error"] += 1
        if ("ci_lower" in parsed and "ci_upper" in parsed
                and parsed["ci_lower"] > parsed["ci_upper"]):
            invalid_ranges["reversed_confidence_interval"] += 1

    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        if row.get("model_id") in {"M1", "M2"}:
            groups.setdefault(row.get("multiple_testing_family", ""), []).append(row)
    families: list[dict[str, Any]] = []
    for name, family_rows in sorted(groups.items()):
        match = FAMILY_RE.search(name)
        declared_size = int(match.group(1)) if match else None
        complete = all(row.get(field, "").strip()
                       for row in family_rows
                       for field in ("p_value", "q_value_by", "p_bonferroni"))
        matches = False
        if complete and family_rows:
            p_values = [float(row["p_value"]) for row in family_rows]
            expected_by = by_adjust(p_values)
            matches = all(
                math.isclose(float(row["q_value_by"]), q_value,
                             rel_tol=1e-9, abs_tol=1e-11)
                and math.isclose(float(row["p_bonferroni"]),
                                 min(p_value * len(family_rows), 1.0),
                                 rel_tol=1e-9, abs_tol=1e-11)
                for row, p_value, q_value in zip(family_rows, p_values, expected_by)
            )
        families.append({
            "family": name,
            "rows": len(family_rows),
            "declared_size": declared_size,
            "all_adjusted_values_present": complete,
            "adjustments_match_independent_recalculation": matches,
        })

    return {
        "table": filename,
        "total_rows": len(rows),
        "model_rows": dict(sorted(model_rows.items())),
        "fit_status_counts": dict(sorted(fit_statuses.items())),
        "duplicate_analysis_keys": duplicate_keys,
        "blank_numeric_fields": blank_fields,
        "nonfinite_or_nonnumeric_fields": nonfinite_fields,
        "invalid_numeric_ranges": invalid_ranges,
        "rows_with_engine_warnings": sum(
            bool(row.get("engine_warnings_private", "").strip()) for row in rows
        ),
        "multiplicity_families": families,
        "integrity_pass": (
            bool(rows)
            and duplicate_keys == 0
            and all(blank_fields[field] == 0 for field in REQUIRED_FIT_FIELDS)
            and not any(nonfinite_fields.values())
            and not any(invalid_ranges.values())
            and all(item["rows"] == expected_family_size
                    and item["declared_size"] == expected_family_size
                    and item["all_adjusted_values_present"]
                    and item["adjustments_match_independent_recalculation"]
                    for item in families)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Aggregate report path under protected CHARLS storage")
    args = parser.parse_args()
    report = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "aggregate-only audit of existing private exploratory output tables; no microdata read",
        "formal_design_validity": "not assessed; official source and survey-design gates remain open",
        "pilot": audit_table("pilot_results_private.csv", expected_family_size=15),
        "extension": audit_table("environment_extension_results_private.csv",
                                  expected_family_size=105),
    }
    report["technical_integrity_checks_pass"] = (
        report["pilot"]["integrity_pass"] and report["extension"]["integrity_pass"]
    )
    output = private_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(f"technical integrity: {'pass' if report['technical_integrity_checks_pass'] else 'fail'}")
    print(f"formal design gate: {report['formal_design_validity']}")
    print(f"Aggregate report saved inside protected storage: {output}")


if __name__ == "__main__":
    main()
