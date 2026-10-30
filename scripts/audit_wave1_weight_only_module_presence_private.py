"""Reconcile positive official Wave 1 weight IDs against All Data person modules.

This audit reads only respondent IDs and the weight eligibility field needed to
identify positive-weight records, then compares those IDs with ID columns in
the verified All Data archive. Exact IDs and detailed counts stay in protected
local QA. It does not inspect exposures/outcomes or estimate associations.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import pandas as pd
import pyreadstat

from prepare_charls_wave_tables import (
    EXCLUDE_MODULES,
    normalize_key,
    sha256_file,
    validate_wave1_source_review,
)
from audit_2011_pilot_intake_metadata import _rar_member_names
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path


DEFAULT_INTAKE = PRIVATE_ROOT / "incoming_2011_official"
DEFAULT_DATA = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
DEFAULT_OUTPUT = QA_OUTPUT_DIR / "wave1_weight_only_person_module_presence_private.json"
SKIP_MODULES = EXCLUDE_MODULES | {"psu", "weight", "weights", "blood", "blood_assays"}


def private(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Wave 1 module-presence audit inputs/output must remain under protected local storage")
    return resolved


def columns(path: Path) -> dict[str, str]:
    _, metadata = pyreadstat.read_dta(str(path), metadataonly=True)
    return {name.casefold(): name for name in metadata.column_names}


def id_set(path: Path, field: str) -> set[str]:
    frame, _ = pyreadstat.read_dta(str(path), usecols=[field])
    ids = normalize_key(frame[field])
    if ids.isna().any() or ids.duplicated().any():
        raise ValueError(f"Expected unique nonmissing ID key in {path.name}")
    return set(ids.astype(str))


def protected_rar_modules(archive: Path):
    """Extract verified RAR members into a temporary protected directory."""
    scratch = private(PRIVATE_ROOT / "tmp")
    scratch.mkdir(parents=True, exist_ok=True)
    listing = _rar_member_names(archive)
    members = [name for name in listing if name.casefold().endswith(".dta")]
    if not members:
        raise ValueError("Verified Wave 1 RAR contains no Stata modules")
    for name in members:
        member_path = PurePosixPath(name.replace("\\", "/"))
        if member_path.is_absolute() or ".." in member_path.parts:
            raise ValueError("Wave 1 RAR contains an unsafe member path")
    extractor = (
        os.environ.get("UNRAR_FREE_PATH", "")
        or shutil.which("unrar-free")
        or str(PRIVATE_ROOT / "tools" / "unrar-free" / "extracted" / "usr" / "bin" / "unrar-free")
    )
    extractor_path = Path(extractor)
    if not extractor_path.is_file():
        resolved_extractor = shutil.which(extractor)
        if resolved_extractor:
            extractor_path = Path(resolved_extractor)
    if not extractor_path.is_file():
        raise FileNotFoundError("A protected RAR extractor is required for the Wave 1 module-ID audit")
    with tempfile.TemporaryDirectory(prefix="wave1_module_ids_", dir=scratch) as directory:
        root = Path(directory).resolve()
        for member in members:
            subprocess.run(
                [str(extractor_path), "-x", str(archive), member, str(root)],
                capture_output=True, timeout=600, check=True,
            )
        extracted = sorted(root.rglob("*.dta"))
        if len(extracted) != len(members) or any(not path.resolve().is_relative_to(root) for path in extracted):
            raise ValueError("Wave 1 RAR module extraction did not match the verified member list")
        yield from extracted


def audit(intake: Path, prepared_data: Path, output: Path) -> dict[str, object]:
    intake, prepared_data, output = map(private, (intake, prepared_data, output))
    archive = intake / "household_and_community_questionnaire_data.rar"
    psu = intake / "PSU.dta"
    weight = intake / "weight.dta"
    blood = intake / "Blood_20140429.dta"
    if not all(path.is_file() for path in (archive, psu, weight, blood, prepared_data)):
        raise FileNotFoundError("One or more reviewed Wave 1 source files or the prepared frame are missing")

    source_inputs = {
        "all_data_archive": {"filename": archive.name, "sha256": sha256_file(archive)},
        "psu": {"filename": psu.name, "sha256": sha256_file(psu)},
        "weight": {"filename": weight.name, "sha256": sha256_file(weight)},
        "blood": {"filename": blood.name, "sha256": sha256_file(blood)},
    }
    source_review = validate_wave1_source_review(source_inputs, intake / "intake_manifest.json")
    prepared_cols = columns(prepared_data)
    if "id" not in prepared_cols:
        raise ValueError("Prepared Wave 1 frame has no respondent ID")
    frame_ids = id_set(prepared_data, prepared_cols["id"])

    weight_cols = columns(weight)
    if "id" not in weight_cols or "ind_weight_ad2" not in weight_cols:
        raise ValueError("Official Weight file lacks ID or ind_weight_ad2")
    wt, _ = pyreadstat.read_dta(str(weight), usecols=[weight_cols["id"], weight_cols["ind_weight_ad2"]])
    wt_ids = normalize_key(wt[weight_cols["id"]])
    wt_values = pd.to_numeric(wt[weight_cols["ind_weight_ad2"]], errors="coerce")
    positive_ids = set(wt_ids[wt_values.gt(0)].dropna().astype(str))
    weight_only_ids = positive_ids - frame_ids
    if not weight_only_ids:
        raise ValueError("This reconciliation expected positive-weight IDs outside the prepared frame")

    module_reports = []
    weight_only_ids_found_in_other_modules: set[str] = set()
    for module_path in protected_rar_modules(archive):
        module = module_path.stem
        if module.casefold() in SKIP_MODULES:
            continue
        module_cols = columns(module_path)
        if "id" not in module_cols:
            continue
        ids = id_set(module_path, module_cols["id"])
        if module.casefold() != "demographic_background":
            weight_only_ids_found_in_other_modules.update(weight_only_ids & ids)
        module_reports.append({
            "module": module,
            "unique_id_rows": len(ids),
            "positive_weight_only_ids_present": len(weight_only_ids & ids),
        })

    other_module_matches = sum(
        row["positive_weight_only_ids_present"] > 0
        for row in module_reports
        if row["module"].casefold() != "demographic_background"
    )
    report: dict[str, object] = {
        "audit_type": "wave1_positive_weight_only_person_module_presence",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_manifest_id": source_review.get("source_manifest_id"),
        "source_identity_status": source_review.get("source_identity_status"),
        "archive_sha256": source_inputs["all_data_archive"]["sha256"],
        "prepared_data_sha256": sha256_file(prepared_data),
        "person_spine_module": "demographic_background",
        "positive_weight_only_id_count": len(weight_only_ids),
        "weight_only_id_values_emitted": False,
        "participant_fields_read": ["ID", "ind_weight_ad2"],
        "exposure_or_outcome_fields_read": False,
        "module_reports_private_only": True,
        "person_module_summaries": module_reports,
        "non_demographic_modules_with_any_weight_only_id": other_module_matches,
        "positive_weight_only_ids_found_in_any_other_person_module": len(weight_only_ids_found_in_other_modules),
        "association_models_estimated": 0,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        temp.chmod(0o600)
    os.replace(temp, output)
    if os.name == "posix":
        output.chmod(0o600)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    parser.add_argument("--prepared-data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = audit(args.intake, args.prepared_data, args.output)
    print(json.dumps({
        "message": "Protected Wave 1 weight-only module reconciliation completed",
        "source_identity_status": report["source_identity_status"],
        "non_demographic_modules_with_any_weight_only_id": report["non_demographic_modules_with_any_weight_only_id"],
        "positive_weight_only_ids_found_in_any_other_person_module": report[
            "positive_weight_only_ids_found_in_any_other_person_module"
        ],
        "detailed_counts_and_module_names_private": True,
        "IDs_emitted": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
