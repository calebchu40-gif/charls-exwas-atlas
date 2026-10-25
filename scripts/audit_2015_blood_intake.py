"""Validate the provenance and schema of the official CHARLS 2015 Blood Data.

This is a fail-closed, metadata-only intake check. It verifies the official
download artifact SHA1, then inspects the Stata header without reading any
respondent values. It does not merge data, calculate sample counts from values,
or publish the file or its QA report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pyreadstat

from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path


EXPECTED_OFFICIAL_BLOOD_SHA1 = "de5b1d80e9b72d61b690dff19b191f50f21ee8c5"
EXPECTED_RELEASE_ROWS = 13_420
REQUIRED_FIELDS = (
    "id",
    "blood_weight",
    "bl_fasting",
    "bl_wbc",
    "bl_hgb",
    "bl_hct",
    "bl_mcv",
    "bl_plt",
    "bl_tg",
    "bl_crea",
    "bl_bun",
    "bl_hdl",
    "bl_ldl",
    "bl_cho",
    "bl_glu",
    "bl_ua",
    "bl_cysc",
    "bl_crp",
    "bl_hbalc",
    "bl_top_coding_tg",
)
DEFAULT_INTAKE = PRIVATE_ROOT / "incoming_2015_blood"
DEFAULT_ARTIFACT = DEFAULT_INTAKE / "Blood_Data_2015_download"
DEFAULT_STATA = DEFAULT_INTAKE / "Blood_Data_2015.dta"
DEFAULT_QA = QA_OUTPUT_DIR / "blood_2015_intake_metadata.json"


def sha1_file(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_official_artifact_sha1(
    path: Path, expected: str = EXPECTED_OFFICIAL_BLOOD_SHA1
) -> str:
    """Reject any artifact not matching CHARLS's posted 2015 Blood Data hash."""
    actual = sha1_file(path).lower()
    if actual != expected.lower():
        raise ValueError(
            "Blood Data SHA1 does not match the official CHARLS 2015 listing; "
            f"expected {expected.lower()}, got {actual}. No intake accepted."
        )
    return actual


def inspect_stata_metadata(
    path: Path, expected_rows: int | None = EXPECTED_RELEASE_ROWS
) -> dict[str, object]:
    """Inspect only the Stata header and confirm the release-note schema."""
    _, metadata = pyreadstat.read_dta(str(path), metadataonly=True)
    available = {str(name).casefold() for name in metadata.column_names}
    missing = [name for name in REQUIRED_FIELDS if name.casefold() not in available]
    if missing:
        raise ValueError(f"2015 Blood Data is missing required official fields: {missing}")
    if expected_rows is not None and metadata.number_rows != expected_rows:
        raise ValueError(
            "2015 Blood Data row count does not match the official release note; "
            f"expected {expected_rows}, got {metadata.number_rows}."
        )
    return {
        "release_version": "20190620",
        "metadata_only": True,
        "respondent_values_read": False,
        "row_count_from_stata_header": int(metadata.number_rows),
        "column_count": len(metadata.column_names),
        "required_field_count": len(REQUIRED_FIELDS),
        "required_fields_present": len(REQUIRED_FIELDS) - len(missing),
        "required_fields_missing": missing,
    }


def audit_intake(artifact: Path, stata_file: Path, expected_rows: int | None = EXPECTED_RELEASE_ROWS):
    artifact = require_private_path(artifact)
    stata_file = require_private_path(stata_file)
    if not artifact.is_file() or not stata_file.is_file():
        raise FileNotFoundError("official Blood Data download artifact or Stata file is missing")
    artifact_sha1 = verify_official_artifact_sha1(artifact)
    metadata = inspect_stata_metadata(stata_file, expected_rows=expected_rows)
    metadata.update(
        {
            "official_artifact_sha1": artifact_sha1,
            "stata_file_sha256": sha256_file(stata_file),
            "source_page": "https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html",
            "release_note_sha1": "f48c549a7f1253230d4c11cbae1687966a3d39d5",
            "interpretation": (
                "Provenance and header check only. No values, IDs, blood-weight counts, "
                "merges, analytic N, or association results were inspected."
            ),
        }
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT,
                        help="Exact CHARLS download artifact whose SHA1 is posted on the official page")
    parser.add_argument("--stata-file", type=Path, default=DEFAULT_STATA,
                        help="Extracted/received Stata Blood Data file to inspect by header only")
    parser.add_argument("--output", type=Path, default=DEFAULT_QA,
                        help="Aggregate-only JSON destination under protected local storage")
    args = parser.parse_args()

    qa = audit_intake(args.artifact, args.stata_file)
    output = require_private_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "2015 Blood Data metadata gate passed: "
        f"rows={qa['row_count_from_stata_header']} "
        f"fields={qa['required_fields_present']}/{qa['required_field_count']} "
        f"artifact_sha1={qa['official_artifact_sha1']}"
    )


if __name__ == "__main__":
    main()
