"""Fail-closed provenance check before any Wave 1 association model is run.

This verifies that the prepared respondent table was built from the same four
human-reviewed official release files currently staged in protected storage.
It does not certify survey-design or estimand validity.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from audit_2011_pilot_intake_metadata import (
    audit_archive,
    audit_stata_header,
    evaluate_source_manifest,
)
from project_paths import PRIVATE_ROOT, require_private_path
from prepare_charls_wave_tables import sha256_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]


ROLE_SOURCE_KEYS = {
    "wave1_all_data": "all_data_archive",
    "psu": "psu",
    "weight": "weight",
    "blood": "blood",
}
REQUIRED_ANALYSIS_GATES = (
    "official_source_identity",
    "sample_frame_and_denominators",
    "target_population_age_domain",
    "weight_and_nonresponse_eligibility",
    "final_psu_mapping",
    "variance_method_review",
    "frozen_analysis_plan",
)
ANALYSIS_PLANS = {
    "water_biomarker_pilot": {
        "filename": "wave1_water_biomarker_pilot.json",
        "plan_id": "pilot_2011_water_biomarker_plan_and_gates_2026-10-26",
        "plan_files": (
            "audit/pilot_2011_water_biomarker_plan_and_gates_2026-10-26.md",
            "audit/pilot_followup_execution_plan_2026-10-26.md",
            "audit/pilot_success_criteria_and_scale_up_2026-10-26.md",
            "audit/multiplicity_primary_family_reconciliation_2026-10-27.md",
            "audit/pilot_autonomous_execution_decision_2026-10-27.md",
        ),
        "additional_gates": (),
    },
    "household_environment_extension": {
        "filename": "wave1_household_environment_extension.json",
        "plan_id": "pilot_2011_water_biomarker_plan_and_gates_2026-10-26#household-environment-K105",
        "plan_files": (
            "audit/pilot_2011_water_biomarker_plan_and_gates_2026-10-26.md",
            "audit/pilot_followup_execution_plan_2026-10-26.md",
            "audit/pilot_success_criteria_and_scale_up_2026-10-26.md",
            "audit/multiplicity_primary_family_reconciliation_2026-10-27.md",
            "audit/pilot_autonomous_execution_decision_2026-10-27.md",
            "audit/wave1_household_environment_covariate_dag_review_2026-10-27.md",
        ),
        "additional_gates": ("pilot_success_and_reproducibility_review",),
    },
}


def analysis_plan_fingerprint(plan_key: str) -> str:
    """Hash the exact set and bytes of the tracked documents defining a plan."""
    plan = ANALYSIS_PLANS.get(plan_key)
    if plan is None:
        raise ValueError(f"Unknown Wave 1 analysis plan {plan_key!r}")
    entries = []
    for relative in plan["plan_files"]:
        path = PROJECT_ROOT / relative
        if not path.is_file():
            raise ValueError(f"Wave 1 analysis plan source is missing: {relative}")
        entries.append(f"{relative}\0{sha256_file(path)}")
    return hashlib.sha256("\n".join(entries).encode("utf-8")).hexdigest()


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"Wave 1 analysis gate: {label} is missing")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Wave 1 analysis gate: {label} is unreadable") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Wave 1 analysis gate: {label} must be a JSON object")
    return value


def require_verified_wave1_frame(
    private_root: Path = PRIVATE_ROOT,
    data_path: Path | None = None,
) -> dict[str, str]:
    """Check current source identity, prepared-table provenance, and output hash.

    All source and derived files must be in the configured private CHARLS root.
    The function reads only archive inventories, Stata headers, JSON manifests,
    and file hashes; it does not read respondent-level values.
    """
    root = require_private_path(private_root)
    if not root.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError(f"Wave 1 analysis gate: root is outside protected storage: {root}")
    intake_dir = root / "incoming_2011_official"
    intake_manifest = _load_json(intake_dir / "intake_manifest.json", "intake manifest")
    prepared_dir = root / "derived_wave_tables"
    prepared_manifest = _load_json(prepared_dir / "prepared_data_manifest.json", "prepared-data manifest")

    wave = next((item for item in prepared_manifest.get("waves", [])
                 if isinstance(item, dict) and str(item.get("wave")) == "2011"), None)
    if wave is None:
        raise ValueError("Wave 1 analysis gate: prepared-data manifest has no 2011 entry")
    source_review = wave.get("source_review")
    if not isinstance(source_review, dict):
        raise ValueError("Wave 1 analysis gate: prepared 2011 table predates source-review provenance")
    if source_review.get("source_identity_status") != "verified_official_source":
        raise ValueError("Wave 1 analysis gate: prepared 2011 table has no verified source identity")
    manifest_id = str(intake_manifest.get("source_manifest_id", ""))
    if not manifest_id or source_review.get("source_manifest_id") != manifest_id:
        raise ValueError("Wave 1 analysis gate: prepared table and current intake manifest IDs differ")

    prepared_sources = wave.get("source_inputs")
    if not isinstance(prepared_sources, dict):
        raise ValueError("Wave 1 analysis gate: prepared table source inputs are missing")
    role_results: dict[str, dict[str, Any]] = {}
    for role, source_key in ROLE_SOURCE_KEYS.items():
        stored = prepared_sources.get(source_key)
        if not isinstance(stored, dict):
            raise ValueError(f"Wave 1 analysis gate: prepared table is missing {role} provenance")
        filename = str(stored.get("filename", ""))
        digest = str(stored.get("sha256", "")).lower()
        if not filename or Path(filename).name != filename or len(digest) != 64:
            raise ValueError(f"Wave 1 analysis gate: invalid prepared {role} provenance")
        source_path = require_private_path(intake_dir / filename)
        if not source_path.is_relative_to(intake_dir):
            raise ValueError(f"Wave 1 analysis gate: unsafe staged {role} filename")
        if not source_path.is_file():
            raise ValueError(f"Wave 1 analysis gate: reviewed {role} file is no longer staged")
        if role == "wave1_all_data":
            observed = audit_archive(source_path)
        else:
            observed = audit_stata_header(source_path, role)
        if observed.get("local_sha256") != digest:
            raise ValueError(f"Wave 1 analysis gate: staged {role} bytes differ from prepared source")
        role_results[role] = {
            "status": "metadata_read",
            "file_name": observed.get("file_name"),
            "local_sha256": observed.get("local_sha256"),
        }

    current_review = evaluate_source_manifest(intake_manifest, role_results)
    if current_review.get("source_identity_status") != "verified_official_source":
        errors = "; ".join(current_review.get("source_identity_review_errors", []))
        raise ValueError(f"Wave 1 analysis gate: current source review is not valid: {errors}")
    if current_review.get("source_manifest_id") != source_review.get("source_manifest_id"):
        raise ValueError("Wave 1 analysis gate: current and prepared source-review IDs differ")

    output = wave.get("prepared_output")
    if not isinstance(output, dict):
        raise ValueError("Wave 1 analysis gate: prepared output hash is missing")
    output_filename = str(output.get("filename", ""))
    if not output_filename or Path(output_filename).name != output_filename:
        raise ValueError("Wave 1 analysis gate: unsafe prepared output filename")
    table = require_private_path(data_path or prepared_dir / output_filename)
    if not table.is_relative_to(root):
        raise ValueError("Wave 1 analysis gate: prepared respondent table is outside protected storage")
    if not table.is_file():
        raise ValueError("Wave 1 analysis gate: prepared respondent table is missing")
    if table.name != output.get("filename") or sha256_file(table) != output.get("sha256"):
        raise ValueError("Wave 1 analysis gate: prepared respondent table differs from manifest hash")

    return {
        "source_manifest_id": manifest_id,
        "source_identity_status": current_review["source_identity_status"],
        "prepared_output_sha256": str(output["sha256"]),
        "survey_design_status": "still_requires_independent_review",
    }


def require_wave1_analysis_readiness(
    private_root: Path,
    source_provenance: dict[str, str],
    analysis_plan: str,
) -> dict[str, str]:
    """Require a review record bound to the exact frame before pilot fitting.

    This gate approves only an internal exploratory pilot. Public release is
    always controlled by the separate disclosure-review workflow.
    """
    root = require_private_path(private_root)
    if not root.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Wave 1 readiness gate: root is outside protected storage")
    plan = ANALYSIS_PLANS.get(analysis_plan)
    if plan is None:
        raise ValueError(f"Wave 1 readiness gate: unknown analysis plan {analysis_plan!r}")
    path = root / "analysis_review" / plan["filename"]
    review = _load_json(path, "Wave 1 analysis readiness review")
    if review.get("status") != "approved_for_exploratory_pilot":
        raise ValueError("Wave 1 readiness gate: no approval for internal exploratory pilot")
    if review.get("source_manifest_id") != source_provenance.get("source_manifest_id"):
        raise ValueError("Wave 1 readiness gate: source manifest binding does not match current frame")
    if review.get("prepared_output_sha256") != source_provenance.get("prepared_output_sha256"):
        raise ValueError("Wave 1 readiness gate: prepared-frame hash binding does not match current frame")
    if review.get("analysis_plan_id") != plan["plan_id"]:
        raise ValueError("Wave 1 readiness gate: approval is not bound to the frozen pilot plan")
    expected_plan_hash = analysis_plan_fingerprint(analysis_plan)
    if str(review.get("analysis_plan_sha256", "")).lower() != expected_plan_hash:
        raise ValueError("Wave 1 readiness gate: approval is not bound to the exact frozen plan documents")
    if review.get("public_release_status") != "not_approved":
        raise ValueError("Wave 1 readiness gate: pilot approval cannot authorize public release")
    if not str(review.get("reviewer", "")).strip() or not str(review.get("reviewed_at", "")).strip():
        raise ValueError("Wave 1 readiness gate: reviewer and review date are required")
    gates = review.get("gates")
    if not isinstance(gates, dict):
        raise ValueError("Wave 1 readiness gate: required gate decisions are missing")
    for gate in (*REQUIRED_ANALYSIS_GATES, *plan["additional_gates"]):
        decision = gates.get(gate)
        if not isinstance(decision, dict) or decision.get("status") != "passed":
            raise ValueError(f"Wave 1 readiness gate: {gate} has not passed")
        if not str(decision.get("evidence", "")).strip():
            raise ValueError(f"Wave 1 readiness gate: {gate} has no evidence citation")
    variance = gates["variance_method_review"]
    if not str(variance.get("method", "")).strip() or not str(variance.get("limitations", "")).strip():
        raise ValueError("Wave 1 readiness gate: variance method and limitations must be explicit")
    return {
        "status": review["status"],
        "reviewer": review["reviewer"],
        "reviewed_at": review["reviewed_at"],
        "analysis_plan_id": review["analysis_plan_id"],
        "analysis_plan_sha256": expected_plan_hash,
        "public_release_status": "not_approved",
    }
