#!/usr/bin/env python3
"""Bind row-wise aggregate disclosure decisions to the private K=845 table.

This performs a conservative, deterministic screen, not a claim that a numeric
cutoff was issued by CHARLS. Exact outputs are written only under PRIVATE_ROOT.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from project_paths import PRIVATE_ROOT, require_private_path

PRIVATE = PRIVATE_ROOT.resolve()
RESULT = PRIVATE / "results" / "charls_waves1_5_primary_county_stage_BY_global_K845_private_v1.csv"
W45_SUPPORT = PRIVATE / "analysis_review" / "wave45_county_pair_cell_disclosure_private_v1.csv"
OUT = PRIVATE / "analysis_review" / "charls_waves1_5_primary_K845_disclosure_review_private_v1.csv"
REPORT = PRIVATE / "qa_outputs" / "charls_waves1_5_primary_K845_disclosure_review_private_v1.json"
REVIEW_FIELDS = ["analysis_id", "decision", "review_record_id", "reviewer_reference", "reviewed_at", "reviewed_result_sha256"]


def private(path: Path) -> Path:
    value = require_private_path(path)
    if not value.is_relative_to(PRIVATE):
        raise ValueError(f"Path escaped protected storage: {value}")
    return value


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build(result_path: Path = RESULT, support_path: Path = W45_SUPPORT,
          review_path: Path = OUT, report_path: Path = REPORT) -> dict:
    result_path, support_path = private(result_path), private(support_path)
    review_path, report_path = private(review_path), private(report_path)
    with result_path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    with support_path.open(encoding="utf-8-sig", newline="") as f:
        support_rows = list(csv.DictReader(f))
    result_hash = sha256(result_path)
    support_map = {}
    for item in support_rows:
        # The support audit covers both M0 and M1; release family contains M1.
        parts = item["analysis_id"].split(":")
        if len(parts) != 4:
            raise ValueError("Unexpected Wave 4/5 support audit analysis ID")
        key = (item["wave"], parts[1], parts[2], item["model_id"])
        if key in support_map:
            raise ValueError("Duplicate Wave 4/5 support-audit key")
        support_map[key] = item
    now = datetime.now(timezone.utc).isoformat()
    review_record_id = "global-k845-disclosure-v1"
    reviewer_reference = "project-internal-technical-screen-v1"
    decisions = []
    reason_counts: dict[str, int] = {}
    for row in rows:
        wave = row["wave"]
        decision, reason = "withheld", "non_success_or_unresolved_support"
        if row["fit_status"] == "success":
            try:
                n = int(float(row["n_model"]))
            except (TypeError, ValueError):
                n = 0
            if wave in {"2018", "2020"}:
                key = (wave, row["exposure_concept_id"], row["phenotype_concept_id"], row["model_id"])
                audit = support_map.get(key)
                if not audit:
                    raise ValueError(f"Missing pair-cell audit for {row['analysis_id']}")
                decision = audit["decision"]
                reason = audit["reason_codes_private"] or "no_internal_support_flag"
            elif n >= 500:
                decision, reason = "approved_public_aggregate", "national_aggregate_and_model_n_at_least_500"
            else:
                decision, reason = "withheld", "model_n_below_internal_500_screen"
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
        decisions.append({
            "analysis_id": row["analysis_id"],
            "decision": decision,
            "review_record_id": review_record_id,
            "reviewer_reference": reviewer_reference,
            "reviewed_at": now,
            "reviewed_result_sha256": result_hash,
        })
    if len(rows) != 845 or len({r["analysis_id"] for r in rows}) != 845:
        raise ValueError("Input is not the complete unique K=845 family")
    if set(support_map) and sum(1 for r in support_rows if r["model_id"] == "M1_age_sex_residence") != sum(1 for r in rows if r["wave"] in {"2018", "2020"}):
        raise ValueError("Wave 4/5 M1 support audit does not cover the expected family rows")
    review_path.parent.mkdir(parents=True, exist_ok=True)
    with review_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REVIEW_FIELDS)
        writer.writeheader(); writer.writerows(decisions)
    os.chmod(review_path, 0o600)
    report = {
        "status": "complete_private_row_level_review_bound_to_exact_K845_csv",
        "reviewed_at": now,
        "result_sha256_private": result_hash,
        "wave45_support_sha256_private": sha256(support_path),
        "review_csv_sha256_private": sha256(review_path),
        "rows_reviewed_private": len(decisions),
        "decision_counts_private": {d: sum(x["decision"] == d for x in decisions) for d in ("approved_public_aggregate", "withheld")},
        "reason_counts_private": reason_counts,
        "policy": "internal conservative technical screen; not an official CHARLS numeric threshold; exact values/sample sizes for withheld rows must be suppressed; this review does not itself deploy the site",
        "multiplicity": "public builder recomputes BY and Bonferroni over complete K=845, treating withheld/inestimable rows as p=1 and publishing no adjusted p for withheld rows",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    temp = report_path.with_suffix(".tmp")
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(temp, 0o600); os.replace(temp, report_path)
    return report


if __name__ == "__main__":
    result = build()
    print(json.dumps({"status": result["status"], "rows_reviewed_private": result["rows_reviewed_private"],
                      "decision_counts_private": result["decision_counts_private"],
                      "review_csv_sha256_private": result["review_csv_sha256_private"]}, ensure_ascii=False))
