"""Check whether non-missing Wave 1 weight IDs occur in other All Data modules.

This is a protected, aggregate-only reconciliation aid. It reads only ID
columns from the official All Data archive and Weight file, never participant
exposure/outcome values, and writes a module-level count report only beneath
the configured private CHARLS root. Presence in a module is not treated as
respondent eligibility or as a resolved survey-weight denominator.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyreadstat

from prepare_charls_wave_tables import dta_members, sha256_file, validate_wave1_source_review
from project_paths import PRIVATE_ROOT, require_private_path


def private_file(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()) or not resolved.is_file():
        raise ValueError("All inputs and outputs must remain under the protected CHARLS root")
    return resolved


def normalize_ids(values: pd.Series) -> set[str]:
    normalized = values.astype("string").str.strip()
    normalized = normalized.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    normalized = normalized.str.replace(r"\.0+$", "", regex=True)
    return set(normalized.dropna().unique().tolist())


def run(
    archive: Path,
    psu_path: Path,
    weight_path: Path,
    blood_path: Path,
    manifest_path: Path,
    output: Path,
) -> dict[str, object]:
    archive = private_file(archive)
    psu_path = private_file(psu_path)
    weight_path = private_file(weight_path)
    blood_path = private_file(blood_path)
    manifest_path = private_file(manifest_path)
    output = require_private_path(output)
    if not output.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Output must remain under the protected CHARLS root")

    source_inputs = {
        "all_data_archive": {"filename": archive.name, "sha256": sha256_file(archive)},
        "psu": {"filename": psu_path.name, "sha256": sha256_file(psu_path)},
        "weight": {"filename": weight_path.name, "sha256": sha256_file(weight_path)},
        "blood": {"filename": blood_path.name, "sha256": sha256_file(blood_path)},
    }
    source_review = validate_wave1_source_review(source_inputs, manifest_path)

    weights, _ = pyreadstat.read_dta(str(weight_path), usecols=["ID", "ind_weight_ad2"])
    weight_values = pd.to_numeric(weights["ind_weight_ad2"], errors="coerce")
    weighted_ids = normalize_ids(weights.loc[weight_values.notna(), "ID"])

    # Keep this aligned with the current prepared respondent spine.
    spine_path = require_private_path(
        PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2011_person_analytic.dta"
    )
    spine, _ = pyreadstat.read_dta(str(spine_path), usecols=["ID"])
    spine_ids = normalize_ids(spine["ID"])
    unmatched_ids = weighted_ids - spine_ids

    module_presence: list[dict[str, object]] = []
    for member in dta_members(archive, "rar"):
        _, meta = pyreadstat.read_dta(str(member), metadataonly=True)
        columns = set(meta.column_names)
        if "ID" not in columns:
            continue
        frame, _ = pyreadstat.read_dta(str(member), usecols=["ID"])
        module_ids = normalize_ids(frame["ID"])
        module_presence.append({
            "module": member.stem,
            "id_rows": len(frame),
            "unique_id_count": len(module_ids),
            "nonmissing_weight_ids_present": len(unmatched_ids & module_ids),
        })

    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "audit_type": "protected Wave 1 weight-ID module-presence reconciliation",
        "source_identity_status": source_review["source_identity_status"],
        "metadata_only_except_ID_columns": True,
        "respondent_exposure_or_outcome_values_read": False,
        "individual_identifiers_processed_in_memory": True,
        "individual_identifiers_written": False,
        "module_presence_is_eligibility_evidence": False,
        "nonmissing_weight_ids": len(weighted_ids),
        "prepared_person_spine_ids": len(spine_ids),
        "weight_ids_outside_prepared_person_spine": len(unmatched_ids),
        "module_presence": module_presence,
        "interpretation": (
            "Module presence only locates where unmatched IDs may occur; it does not establish "
            "the official analytic frame, response eligibility, or weight denominator."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--psu", type=Path, required=True)
    parser.add_argument("--weight", type=Path, required=True)
    parser.add_argument("--blood", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=PRIVATE_ROOT / "qa_outputs" / "wave1_weight_unmatched_module_presence.json",
    )
    args = parser.parse_args()
    report = run(args.archive, args.psu, args.weight, args.blood, args.manifest, args.output)
    print(
        "Protected Wave 1 module-presence audit complete; "
        f"weighted IDs outside person spine={report['weight_ids_outside_prepared_person_spine']}; "
        "module-level aggregate report saved under protected storage."
    )


if __name__ == "__main__":
    main()
