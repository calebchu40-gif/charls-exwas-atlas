"""Run metadata-only CHARLS intake checks for official files already present.

This convenience entry point never downloads, bulk-extracts, merges, or reads
respondent values. It stages only required DTA members in protected temporary
storage for header inspection. Missing inputs are reported as skipped; present
inputs must pass the release-hash and header checks before aggregate QA is saved.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_2013_weights_intake import (
    DEFAULT_ARCHIVE as WEIGHTS_ARCHIVE,
    audit_weights_header,
    audit_weights_archive_header,
)
from audit_2015_blood_intake import (
    DEFAULT_ARTIFACT as BLOOD_ARTIFACT,
    DEFAULT_STATA as BLOOD_STATA,
    audit_intake as audit_blood_intake,
    audit_archive_header as audit_blood_archive_header,
)
from project_paths import QA_OUTPUT_DIR, require_private_path


def run_available_gates(
    weights_source: Path = WEIGHTS_ARCHIVE,
    blood_artifact: Path = BLOOD_ARTIFACT,
    blood_stata: Path | None = None,
) -> dict[str, object]:
    """Check official ZIPs directly, with an optional legacy extracted-DTA pair."""
    weights_source = require_private_path(weights_source)
    blood_artifact = require_private_path(blood_artifact)
    if blood_stata is not None:
        blood_stata = require_private_path(blood_stata)
    result: dict[str, object] = {
        "metadata_only": True,
        "respondent_values_read": False,
        "wave_2013_weights": {"status": "skipped_missing_input"},
        "wave_2015_blood": {"status": "skipped_missing_input"},
    }

    if weights_source.is_file():
        audit = (
            audit_weights_archive_header(weights_source)
            if weights_source.suffix.casefold() == ".zip"
            else audit_weights_header(weights_source)
        )
        result["wave_2013_weights"] = {"status": "passed", **audit}

    if blood_artifact.is_file() and blood_stata is not None and blood_stata.is_file():
        result["wave_2015_blood"] = {
            "status": "passed",
            **audit_blood_intake(blood_artifact, blood_stata),
        }
    elif blood_artifact.is_file() and blood_stata is not None:
        result["wave_2015_blood"] = {
            "status": "skipped_incomplete_input_set",
            "download_artifact_present": True,
            "stata_file_present": False,
        }
    elif blood_artifact.is_file():
        result["wave_2015_blood"] = {"status": "passed", **audit_blood_archive_header(blood_artifact)}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        default=QA_OUTPUT_DIR / "charls_available_intake_gates.json",
        help="Aggregate-only report path in protected local storage",
    )
    args = parser.parse_args()
    output = require_private_path(args.output)
    report = run_available_gates()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for wave, details in (("2013 weights", report["wave_2013_weights"]), ("2015 blood", report["wave_2015_blood"])):
        print(f"{wave}: {details['status']}")
    print(f"Aggregate metadata report saved outside the repository: {output}")


if __name__ == "__main__":
    main()
