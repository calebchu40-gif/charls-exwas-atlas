#!/usr/bin/env python3
"""Map generic-engine scan output onto the frozen EXWAS result contract (v3).

The scan engine (:mod:`exwas_engine`) produces an analysis-oriented long table.
The release pipeline (:mod:`validate_exwas_result_table`,
:mod:`build_public_association_release`) expects the richer v3 schema, which
records *provenance* as well as estimates: source identity, weight/PSU/stratum
status, variance caveats, missingness rule, estimability review, software
versions.

Those provenance facts cannot be inferred from a scan. They must be supplied by
a frozen ``provenance.json`` that a human has reviewed. This module therefore
fails closed: a successful fit is only written when the provenance states a
verified source, a verified weight, a verified PSU, a documented stratum
status, a reviewed estimability decision, and a code commit in
``software_versions``.

Usage
-----
    python scripts/engine_to_schema_v3.py \
        --engine-results <private>/results/scan.csv \
        --provenance <private>/analysis_review/wave1_provenance.json \
        --output <private>/results/wave1_result_v3.csv

The output is validated with the production validator before the command
exits; a non-zero status means the table must not be used.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import validate_exwas_result_table as contract

#: Engine fit status -> contract fit status. Unmapped values are an error.
FIT_STATUS_MAP = {
    "success": "success",
    "no_eligible_records": "inestimable",
    "numerically_unavailable": "inestimable",
    "zero_outcome_variance": "inestimable",
    "zero_exposure_variance": "inestimable",
    "nonpositive_weight_total": "inestimable",
    "invalid_binary_outcome": "blocked_measurement_rule",
    "engine_omitted_term": "code_error",
}

#: Provenance keys every output row carries verbatim.
PROVENANCE_FIELDS = (
    "data_release", "source_identity_status", "source_hash_status", "source_manifest_id",
    "target_population", "eligibility_rule",
    "weight_id", "weight_status", "weight_source",
    "psu_id", "psu_status", "stratum_id", "stratum_status",
    "variance_design", "exposure_transform", "phenotype_transform", "missingness_rule",
    "comparability_grade", "estimability_review_status", "estimability_review_id",
    "software_versions",
)

REQUIRED_PROVENANCE = [name for name in PROVENANCE_FIELDS if name not in {"weight_id", "psu_id", "stratum_id"}]

#: Extra column kept for the public release builder (it reads ``contrast``).
EXTRA_FIELDS = ("contrast",)


class MappingError(ValueError):
    """The scan output or the provenance cannot be mapped without guessing."""


def load_provenance(path: Path) -> dict[str, str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MappingError("provenance must be a JSON object")
    provenance: dict[str, str] = {}
    for key in PROVENANCE_FIELDS:
        value = payload.get(key, "")
        provenance[key] = "" if value is None else str(value).strip()
    missing = [key for key in REQUIRED_PROVENANCE if not provenance[key]]
    if missing:
        raise MappingError("provenance is missing required fields: " + ", ".join(missing))
    checks = (
        ("source_identity_status", contract.SOURCE_IDENTITY_STATUSES),
        ("source_hash_status", contract.SOURCE_HASH_STATUSES),
        ("weight_status", contract.WEIGHT_STATUSES),
        ("psu_status", contract.DESIGN_STATUSES),
        ("stratum_status", contract.DESIGN_STATUSES),
        ("estimability_review_status", contract.ESTIMABILITY_STATUSES),
    )
    for field, allowed in checks:
        if provenance[field] not in allowed:
            raise MappingError(f"provenance {field} must be one of {sorted(allowed)}")
    if provenance["estimability_review_status"] == "reviewed_pass" and not provenance["estimability_review_id"]:
        raise MappingError("estimability_review_status=reviewed_pass requires estimability_review_id")
    if not contract.MANIFEST_ID_RE.fullmatch(provenance["source_manifest_id"]):
        raise MappingError("source_manifest_id must be an opaque identifier (no paths)")
    if not contract._has_git_commit(provenance["software_versions"]):
        raise MappingError("software_versions must contain a code commit (e.g. 'commit: 0e39927')")
    return provenance


def map_row(engine_row: dict[str, str], provenance: dict[str, str]) -> dict[str, str]:
    engine_status = (engine_row.get("fit_status") or "").strip()
    if engine_status not in FIT_STATUS_MAP:
        raise MappingError(f"unsupported engine fit_status {engine_status!r}")
    contract_status = FIT_STATUS_MAP[engine_status]

    row = {field: "" for field in contract_fields()}
    row.update(provenance)
    row["analysis_id"] = (engine_row.get("analysis_id") or "").strip()
    if not row["analysis_id"]:
        raise MappingError("engine row has no analysis_id")
    for field in ("wave", "model_id", "multiple_testing_family",
                  "exposure_concept_id", "exposure_variable",
                  "phenotype_concept_id", "phenotype_variable"):
        row[field] = (engine_row.get(field) or "").strip()
    row["estimate_type"] = (engine_row.get("estimate_type") or "").strip()
    row["fit_status"] = contract_status
    row["contrast"] = (engine_row.get("exposure_contrast") or "").strip()

    if contract_status == "success":
        for field in ("estimate", "standard_error", "ci_lower", "ci_upper",
                      "p_value", "q_value_by", "p_bonferroni", "n_model"):
            row[field] = (engine_row.get(field) or "").strip()
            if not row[field]:
                raise MappingError(f"{row['analysis_id']}: successful fit is missing {field}")
    else:
        # Fail closed: a non-success row must not smuggle an estimate through.
        for field in ("estimate", "standard_error", "ci_lower", "ci_upper",
                      "p_value", "q_value_by", "p_bonferroni", "n_model"):
            row[field] = ""
        row["estimability_review_id"] = ""
        if contract_status == "blocked_measurement_rule":
            row["estimability_review_status"] = "unresolved"
        elif row["estimability_review_status"] == "reviewed_pass":
            row["estimability_review_status"] = "pending"
    return row


def contract_fields() -> list[str]:
    fields, _ = contract.read_schema()
    return fields


def build(engine_rows: list[dict[str, str]], provenance: dict[str, str]) -> list[dict[str, str]]:
    rows = [map_row(row, provenance) for row in engine_rows]
    identifiers = [row["analysis_id"] for row in rows]
    if len(set(identifiers)) != len(identifiers):
        raise MappingError("engine output contains duplicate analysis_id values")
    return rows


def write_rows(rows: list[dict[str, str]], path: Path) -> None:
    fields = contract_fields() + [name for name in EXTRA_FIELDS if name not in contract_fields()]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--engine-results", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    with args.engine_results.open(newline="", encoding="utf-8") as handle:
        engine_rows = list(csv.DictReader(handle))
    if not engine_rows:
        raise SystemExit("engine result table is empty")

    provenance = load_provenance(args.provenance)
    rows = build(engine_rows, provenance)
    write_rows(rows, args.output)
    errors = contract.validate_csv(args.output)
    if errors:
        for error in errors[:20]:
            print("FAIL:", error)
        return 1
    print(json.dumps({
        "output": str(args.output),
        "rows": len(rows),
        "success": sum(1 for row in rows if row["fit_status"] == "success"),
        "families": sorted({row["multiple_testing_family"] for row in rows}),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
