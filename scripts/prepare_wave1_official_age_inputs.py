"""Prepare a minimal, protected Wave 1 birth-age input table.

This joins only the official Wave 1 birth-date/calendar/conditional-age fields
to interview year/month from the official Weight release. It does not derive
age, inspect association exposures/outcomes, or write individual data into the
repository. The private intake and prepared-table manifests must agree with
current file hashes before any participant values are read.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path


def private_path(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError(f"Protected CHARLS data must remain under {PRIVATE_ROOT}")
    return resolved


def restrict(path: Path, *, directory: bool = False) -> None:
    if os.name == "posix":
        os.chmod(path, 0o700 if directory else 0o600)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def norm_id(value):
    if pd.isna(value):
        return pd.NA
    key = str(value).strip()
    if key.endswith(".0") and key[:-2].isdigit():
        key = key[:-2]
    return key or pd.NA


def require_columns(path: Path, columns: list[str]) -> None:
    _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
    missing = sorted(set(columns) - set(meta.column_names))
    if missing:
        raise ValueError(f"Required official fields absent from {path.name}: {missing}")


def main() -> None:
    root = private_path(PRIVATE_ROOT)
    intake = private_path(Path(os.environ.get(
        "CHARLS_WAVE1_INTAKE_DIR", str(root / "incoming_2011_official")
    )))
    rebuilt = private_path(Path(os.environ.get(
        "CHARLS_WAVE1_REBUILT_DIR",
        str(root / "derived_wave_tables_2011_official_rebuild_20261029"),
    )))
    output_dir = private_path(root / "age_inputs_2011")
    qa_dir = private_path(root / "qa_outputs")
    source_manifest_path = private_path(intake / "intake_manifest.json")
    prepared_manifest_path = private_path(rebuilt / "prepared_data_manifest.json")
    person_path = private_path(rebuilt / "CHARLS_wave2011_person_analytic.dta")
    weight_path = private_path(intake / "weight.dta")

    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if source_manifest.get("status") != "source_identity_reviewed_metadata_only":
        raise ValueError("Wave 1 source identity review is not recorded as complete")
    roles = {item.get("role"): item for item in source_manifest.get("required_files", [])}
    needed = {"wave1_all_data", "psu", "weight", "blood"}
    if set(roles) != needed or any(
        roles[role].get("identity_review_status") != "verified_official_source"
        for role in needed
    ):
        raise ValueError("The four official Wave 1 source identities are not all reviewed")

    prepared_manifest = json.loads(prepared_manifest_path.read_text(encoding="utf-8"))
    wave_sources = prepared_manifest.get("source_inputs_by_wave", {}).get("2011", {})
    for role, manifest_key in (("weight", "weight"), ("wave1_all_data", "all_data_archive"),
                               ("psu", "psu"), ("blood", "blood")):
        item = roles[role]
        prepared = wave_sources.get(manifest_key, {})
        if item.get("reviewed_local_sha256") != prepared.get("sha256"):
            raise ValueError(f"Source manifests disagree for {role}")
        candidate = intake / item.get("original_filename", "")
        if not candidate.is_file() or sha256(candidate) != item.get("reviewed_local_sha256"):
            raise ValueError(f"Reviewed source fingerprint does not match {role}")

    person_fields = ["ID", "ba002_1", "ba002_2", "ba002_3", "ba003", "ba004"]
    weight_fields = ["ID", "iyear", "imonth"]
    require_columns(person_path, person_fields)
    require_columns(weight_path, weight_fields)

    # Only these fields are loaded; unrelated questionnaire, exposure and
    # outcome values are never read by this preparation step.
    people, _ = pyreadstat.read_dta(str(person_path), usecols=person_fields)
    weights, _ = pyreadstat.read_dta(str(weight_path), usecols=weight_fields)
    people["_join_id"] = people["ID"].map(norm_id)
    weights["_join_id"] = weights["ID"].map(norm_id)
    if people["_join_id"].isna().any() or people["_join_id"].duplicated().any():
        raise ValueError("Person-spine IDs must be nonmissing and unique")
    if weights["_join_id"].isna().any() or weights["_join_id"].duplicated().any():
        raise ValueError("Official Weight IDs must be nonmissing and unique")

    joined = people.merge(
        weights[["_join_id", "iyear", "imonth"]],
        on="_join_id", how="left", validate="one_to_one", indicator=True,
    )
    joined["ID"] = joined["_join_id"].astype("string")
    joined["birth_year"] = joined["ba002_1"]
    joined["birth_month"] = joined["ba002_2"]
    joined["birth_day"] = joined["ba002_3"]
    joined["calendar_type"] = joined["ba003"]
    joined["reported_age_conditional"] = joined["ba004"]
    joined["age_input_source"] = "CHARLS 2011 official respondent fields + official Weight interview date"
    columns = ["ID", "birth_year", "birth_month", "birth_day", "calendar_type",
               "reported_age_conditional", "iyear", "imonth", "age_input_source"]
    age_inputs = joined[columns].copy()
    variable_labels = {
        "ID": "CHARLS respondent ID; protected join key",
        "birth_year": "Wave 1 official ba002_1: Birth Year",
        "birth_month": "Wave 1 official ba002_2: Birth Month",
        "birth_day": "Wave 1 official ba002_3: Birth Day",
        "calendar_type": "Wave 1 official ba003: Calendar Type",
        "reported_age_conditional": "Wave 1 official ba004: Age, conditional route",
        "iyear": "Wave 1 official Weight.dta: Interview Year",
        "imonth": "Wave 1 official Weight.dta: Interview Month",
        "age_input_source": "Source/route note; not a derived age",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    restrict(output_dir, directory=True)
    out_path = private_path(output_dir / "wave1_official_age_inputs.dta")
    pyreadstat.write_dta(
        age_inputs, str(out_path), version=14,
        column_labels=[variable_labels[name] for name in age_inputs.columns],
    )
    restrict(out_path)

    qa = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "protected preparation only; no age derivation or association analysis",
        "person_source_sha256": sha256(person_path),
        "weight_source_sha256": sha256(weight_path),
        "age_input_sha256": sha256(out_path),
        "source_manifest_id": source_manifest.get("source_manifest_id"),
        "prepared_source_weight_sha256": wave_sources["weight"].get("sha256"),
        "person_rows": int(len(people)),
        "weight_rows": int(len(weights)),
        "unique_person_id": int(people["_join_id"].nunique()),
        "unique_weight_id": int(weights["_join_id"].nunique()),
        "matched_interview_date_rows": int(joined["_merge"].eq("both").sum()),
        "unmatched_interview_date_rows": int(joined["_merge"].eq("left_only").sum()),
        "dob_or_calendar_values_processed": True,
        "age_values_derived": False,
        "association_models_fitted": False,
        "output": out_path.name,
    }
    qa_dir.mkdir(parents=True, exist_ok=True)
    restrict(qa_dir, directory=True)
    qa_path = private_path(qa_dir / "wave1_official_age_inputs_qa.json")
    qa_path.write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")
    restrict(qa_path)
    print(json.dumps({k: v for k, v in qa.items() if k not in {
        "person_source_sha256", "weight_source_sha256", "prepared_source_weight_sha256",
        "source_manifest_id", "output"
    }}, indent=2))
    print("Protected age-input file created; no ages or associations were derived.")


if __name__ == "__main__":
    main()
