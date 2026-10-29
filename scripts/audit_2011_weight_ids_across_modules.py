"""Check whether Wave 1 positive-weight IDs occur in any official All Data module.

The archive is extracted only to a temporary directory under the protected
CHARLS root. Analysis reads only `ID` from each module, `ID`/`ind_weight_ad2`/
`mainr` from Weight.dta, and `ID` from Blood.dta. The JSON report contains aggregate counts
only and must remain in protected storage. No IDs or questionnaire answers are
written, printed, or sent to GitHub/server/public storage.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path
from require_verified_wave1_frame import require_verified_wave1_frame


DEFAULT_INTAKE = PRIVATE_ROOT / "incoming_2011_official"
DEFAULT_FRAME = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
DEFAULT_UNRAR = Path(r"C:\Program Files\WinRAR\UnRAR.exe")


def private_path(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("All Wave 1 linkage inputs, scratch and outputs must stay under the protected root")
    return resolved


def normalize_id(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip()
    values = values.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return values.str.replace(r"\.0+$", "", regex=True)


def id_set(path: Path) -> tuple[pd.Index, int, int]:
    frame, _ = pyreadstat.read_dta(str(path), usecols=["ID"])
    values = normalize_id(frame["ID"])
    valid = values.dropna()
    return pd.Index(valid.unique()), len(frame), int(values.isna().sum())


def run(intake: Path, frame_path: Path, unrar: Path, output: Path) -> dict[str, object]:
    intake = private_path(intake)
    frame_path = private_path(frame_path)
    archive = private_path(intake / "household_and_community_questionnaire_data.rar")
    weight_path = private_path(intake / "weight.dta")
    blood_path = private_path(intake / "Blood_20140429.dta")
    output = private_path(output)
    unrar = unrar.resolve()
    if not archive.is_file() or not weight_path.is_file() or not blood_path.is_file() or not frame_path.is_file() or not unrar.is_file():
        raise FileNotFoundError("Required protected All Data/Weight/frame input or UnRAR executable is missing")

    source = require_verified_wave1_frame(data_path=frame_path)
    frame_ids, _, _ = id_set(frame_path)
    weight, _ = pyreadstat.read_dta(str(weight_path), usecols=["ID", "ind_weight_ad2", "mainr"])
    weight["_normalized_id"] = normalize_id(weight["ID"])
    positive = pd.to_numeric(weight["ind_weight_ad2"], errors="coerce").gt(0)
    target_ids = pd.Index(weight.loc[positive, "_normalized_id"].dropna().unique())
    unmatched = target_ids.difference(frame_ids)
    residual_roles = weight.loc[positive & weight["_normalized_id"].isin(unmatched), ["_normalized_id", "mainr"]]
    role_per_id: dict[str, str] = {}
    for identifier, group in residual_roles.groupby("_normalized_id", dropna=True):
        role_values = pd.to_numeric(group["mainr"], errors="coerce").dropna().astype(int).unique().tolist()
        if role_values == [0]:
            role_per_id[str(identifier)] = "spouse"
        elif role_values == [1]:
            role_per_id[str(identifier)] = "main_respondent"
        elif len(role_values) == 0:
            role_per_id[str(identifier)] = "missing_or_unlabeled"
        else:
            role_per_id[str(identifier)] = "conflicting_or_unexpected"
    residual_role_counts = {
        role: sum(value == role for value in role_per_id.values())
        for role in ("main_respondent", "spouse", "missing_or_unlabeled", "conflicting_or_unexpected")
    }
    blood, _ = pyreadstat.read_dta(str(blood_path), usecols=["ID"])
    blood_ids = pd.Index(normalize_id(blood["ID"]).dropna().unique())

    temp_root = private_path(PRIVATE_ROOT / "tmp")
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="w1_weight_module_ids_", dir=temp_root) as temp_name:
        extract_dir = Path(temp_name)
        listing = subprocess.run(
            [str(unrar), "lb", str(archive)], check=True, capture_output=True, text=True,
        ).stdout.splitlines()
        members = [line.strip() for line in listing if line.strip().casefold().endswith(".dta")]
        if not members or any(Path(member).name != member for member in members):
            raise ValueError("Unexpected All Data archive member paths; refusing extraction")
        subprocess.run(
            [str(unrar), "x", "-inul", "-o+", str(archive), str(extract_dir) + "\\"],
            check=True, capture_output=True, text=True,
        )
        module_results: dict[str, dict[str, int]] = {}
        any_module_ids: set[str] = set()
        for member in members:
            module_path = private_path(extract_dir / Path(member).name)
            if not module_path.is_file():
                raise FileNotFoundError(f"Expected official All Data module was not extracted: {Path(member).name}")
            _, metadata = pyreadstat.read_dta(str(module_path), metadataonly=True)
            if "ID" not in metadata.column_names:
                module_results[Path(member).stem] = {"id_column_present": 0}
                continue
            ids, rows, missing = id_set(module_path)
            normalized = set(ids.astype(str))
            any_module_ids.update(normalized)
            module_results[Path(member).stem] = {
                "id_column_present": 1,
                "rows": rows,
                "unique_nonmissing_ids": len(ids),
                "positive_weight_ids_found": len(unmatched.intersection(ids)),
                "missing_id_rows": missing,
            }
        found_any = unmatched.intersection(pd.Index(any_module_ids))

    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "audit_type": "protected aggregate-only Wave 1 ID module linkage",
        "source_identity_status": source["source_identity_status"],
        "source_manifest_id": source["source_manifest_id"],
        "individual_ids_processed_in_memory": True,
        "individual_ids_written_or_printed": False,
        "substantive_questionnaire_values_read": False,
        "respondent_role_metadata_values_read": True,
        "association_models_estimated": False,
        "positive_weight_ids_outside_demographic_frame": len(unmatched),
        "residual_positive_weight_ids_by_official_mainr_role": residual_role_counts,
        "those_ids_present_in_any_other_all_data_module": len(found_any),
        "those_ids_absent_from_all_module_id_columns": len(unmatched.difference(found_any)),
        "those_ids_present_in_official_blood_file": len(unmatched.intersection(blood_ids)),
        "module_aggregate_comparisons": module_results,
        "interpretation_limit": "Module ID presence only locates linkage candidates; it does not establish respondent eligibility, interview completion, or blood-weight applicability.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    parser.add_argument("--frame", type=Path, default=DEFAULT_FRAME)
    parser.add_argument("--unrar", type=Path, default=DEFAULT_UNRAR)
    parser.add_argument("--output", type=Path, default=PRIVATE_ROOT / "qa_outputs" / "wave1_weight_module_linkage_2026-10-29.json")
    args = parser.parse_args()
    output = private_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = run(args.intake, args.frame, args.unrar, output)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wave 1 ID-module linkage audit complete; aggregate report retained in protected storage")


if __name__ == "__main__":
    main()
