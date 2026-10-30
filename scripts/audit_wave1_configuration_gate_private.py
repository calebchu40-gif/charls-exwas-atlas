#!/usr/bin/env python3
"""Audit Wave 1 pilot configuration and readiness without reading respondent values.

The report is written only beneath the protected CHARLS private root. The
source gate checks provenance, hashes and metadata; this script never opens the
prepared respondent table for row-level analysis and never fits a model.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from project_paths import require_private_path
from require_verified_wave1_frame import (
    ANALYSIS_PLANS,
    analysis_plan_fingerprint,
    require_verified_wave1_frame,
    require_wave1_analysis_readiness,
)
from run_2011_household_environment_scaleup import AGE, DATA, PRIVATE, PILOT_PLAN_KEY
from prepare_charls_wave_tables import sha256_file


DRAFT_CONFIG = PRIVATE / "analysis_review" / "wave1_household_environment_pilot_model_config.draft_20261030.json"
RULE_KEYS = (
    "review_status", "reviewer", "reviewed_at", "source_anchor", "unit",
    "valid_domain_rule", "valid_min", "valid_max", "invalid_codes",
    "lod_censoring_rule", "topcode_rule", "fasting_rule",
)


def _write_private_report(report: dict[str, Any]) -> Path:
    root = require_private_path(PRIVATE)
    if root != PRIVATE.resolve():
        raise ValueError("private CHARLS root resolution changed unexpectedly")
    output_dir = require_private_path(root / "qa_outputs")
    if not output_dir.is_dir() or not output_dir.is_relative_to(root):
        raise ValueError("configuration gate report directory is outside protected storage")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = output_dir / f"wave1_configuration_gate_audit_{stamp}_private.json"
    if output.exists():
        raise FileExistsError("refusing to overwrite a prior configuration gate audit")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output.chmod(0o600)
    return output


def audit() -> dict[str, Any]:
    report: dict[str, Any] = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "configuration/provenance metadata only; no respondent values read; no models fitted",
        "formal_analysis_fitted": False,
    }
    provenance: dict[str, str] = {}
    try:
        provenance = require_verified_wave1_frame(PRIVATE, DATA, age_path=AGE)
        report.update({
            "source_gate": provenance.get("source_identity_status"),
            "source_manifest_bound": bool(provenance.get("source_manifest_id")),
            "prepared_table_hash_bound": bool(provenance.get("prepared_output_sha256")),
            "age_candidate_hash_bound": bool(provenance.get("age_candidate_sha256")),
        })
    except Exception as exc:  # record a closed gate without exposing local paths
        report["source_gate"] = "closed"
        report["source_gate_blocker"] = f"{type(exc).__name__}: {exc}"

    if DRAFT_CONFIG.is_file():
        config = json.loads(DRAFT_CONFIG.read_text(encoding="utf-8"))
        plan = ANALYSIS_PLANS[PILOT_PLAN_KEY]
        expected_plan_hash = analysis_plan_fingerprint(PILOT_PLAN_KEY)
        outcome_rules = config.get("outcome_validity_rules", {})
        missing_keys = {
            str(name): [key for key in RULE_KEYS if key not in rule]
            for name, rule in outcome_rules.items()
            if not isinstance(rule, dict) or any(key not in rule for key in RULE_KEYS)
        }
        status_counts = Counter(
            str(rule.get("review_status")) for rule in outcome_rules.values() if isinstance(rule, dict)
        )
        blank_review_fields = Counter(
            key for rule in outcome_rules.values() if isinstance(rule, dict)
            for key in ("reviewer", "reviewed_at") if not str(rule.get(key, "")).strip()
        )
        report.update({
            "draft_status": config.get("status"),
            "draft_config_sha256": sha256_file(DRAFT_CONFIG),
            "registered_plan_hash_matches": config.get("analysis_plan_sha256") == expected_plan_hash,
            "source_manifest_matches": bool(provenance) and config.get("source_manifest_id") == provenance.get("source_manifest_id"),
            "prepared_table_hash_matches": bool(provenance) and config.get("prepared_output_sha256") == provenance.get("prepared_output_sha256"),
            "age_candidate_hash_matches": bool(provenance) and config.get("age_candidate_sha256") == provenance.get("age_candidate_sha256"),
            "active_frozen_config_present": (PRIVATE / "analysis_review" / str(plan.get("config_filename", ""))).is_file(),
            "readiness_record_present": (PRIVATE / "analysis_review" / str(plan["filename"])).is_file(),
            "outcome_rule_count": len(outcome_rules),
            "missing_rule_keys_by_outcome": missing_keys,
            "outcome_rule_status_counts": dict(status_counts),
            "blank_reviewer_or_date_counts": dict(blank_review_fields),
            "null_numeric_bounds_allowed": True,
            "null_bound_count": sum(
                1 for rule in outcome_rules.values()
                if isinstance(rule, dict) and rule.get("valid_min") is None and rule.get("valid_max") is None
            ),
        })
    else:
        report["draft_config_present"] = False

    if provenance:
        try:
            readiness = require_wave1_analysis_readiness(PRIVATE, provenance, PILOT_PLAN_KEY)
            report["readiness_gate"] = "passed"
            report["readiness_status"] = readiness.get("status")
        except Exception as exc:
            report["readiness_gate"] = "closed"
            report["readiness_blocker"] = f"{type(exc).__name__}: {exc}"
    else:
        report["readiness_gate"] = "not_evaluated_source_gate_closed"

    path = _write_private_report(report)
    report["report_file_name"] = path.name
    report["report_mode"] = "0600"
    return report


def main() -> None:
    report = audit()
    # Keep stdout deliberately aggregate-only; complete hashes and blocker text
    # remain in the protected report for local review.
    summary = {
        key: report.get(key)
        for key in (
            "source_gate", "registered_plan_hash_matches", "draft_status",
            "active_frozen_config_present", "readiness_record_present",
            "outcome_rule_count", "outcome_rule_status_counts", "readiness_gate",
            "report_file_name", "report_mode",
        )
    }
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
