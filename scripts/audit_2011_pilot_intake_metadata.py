"""Metadata-only provenance/header preflight for the CHARLS 2011 pilot.

The script does not extract the Wave 1 archive or read respondent-level values.
For standalone Stata files it reads the Stata header only. Hashing is performed
for local file identity and is not represented as an official CHARLS checksum.
All inputs and the report must remain in the private, non-synchronized root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

import pyreadstat

from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path


DEFAULT_INTAKE = PRIVATE_ROOT / "incoming_2011_official"
DEFAULT_REPORT = QA_OUTPUT_DIR / "charls_2011_pilot_intake_metadata.json"
ROLE_URLS = {
    "wave1_all_data": "https://charls.charlsdata.com/documents/123/download/en.html",
    "psu": "https://charls.charlsdata.com/documents/117/download/en.html",
    "weight": "https://charls.charlsdata.com/documents/118/download/en.html",
    "blood": "https://charls.charlsdata.com/documents/201/download/en.html",
}
STATA_SUFFIXES = {".dta"}


def private_input(path: Path) -> Path:
    resolved = require_private_path(path)
    root = PRIVATE_ROOT.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Input must remain inside the configured private root: {resolved}")
    return resolved


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def discover_file(directory: Path, role: str, explicit: Path | None) -> Path | None:
    if explicit is not None:
        return private_input(explicit)
    if not directory.is_dir():
        return None
    candidates = [p for p in directory.iterdir() if p.is_file()]
    if role == "wave1_all_data":
        matches = [p for p in candidates if p.suffix.casefold() == ".zip"]
    else:
        matches = [
            p for p in candidates
            if p.suffix.casefold() in STATA_SUFFIXES
            and role in p.stem.casefold()
        ]
    return private_input(matches[0]) if len(matches) == 1 else None


def audit_archive(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        stata_members = [
            item.filename for item in members
            if Path(item.filename).suffix.casefold() in STATA_SUFFIXES
        ]
    return {
        "file_name": path.name,
        "file_bytes": path.stat().st_size,
        "local_sha256": sha256_file(path),
        "official_checksum": "not listed for this download item on the checked Wave 1 page",
        "archive_member_count": len(members),
        "stata_member_count": len(stata_members),
        "stata_member_names": stata_members,
        "archive_contents_extracted": False,
        "respondent_values_read": False,
        "source_page": ROLE_URLS["wave1_all_data"],
    }


def audit_stata_header(path: Path, role: str) -> dict[str, Any]:
    _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
    return {
        "file_name": path.name,
        "file_bytes": path.stat().st_size,
        "local_sha256": sha256_file(path),
        "official_checksum": "not listed for this download item on the checked Wave 1 page",
        "stata_header_rows": int(meta.number_rows),
        "stata_header_columns": len(meta.column_names),
        "column_names": [str(value) for value in meta.column_names],
        "respondent_values_read": False,
        "source_page": ROLE_URLS[role],
    }


def run_preflight(intake: Path, explicit: dict[str, Path | None]) -> dict[str, Any]:
    intake = private_input(intake)
    report: dict[str, Any] = {
        "wave": "2011 baseline",
        "metadata_only": True,
        "respondent_values_read": False,
        "release_gate": "not_passed",
        "source_provenance_verified_by_script": False,
        "required_roles": list(ROLE_URLS),
        "roles": {},
        "limitations": [
            "Local SHA-256 identifies the received file; it is not an official CHARLS checksum.",
            "Header and archive-name checks do not establish survey-design eligibility or estimand validity.",
            "Inputs must be downloaded through an authorized CHARLS account and kept private.",
        ],
    }
    missing: list[str] = []
    for role in ROLE_URLS:
        path = discover_file(intake, role, explicit.get(role))
        if path is None or not path.is_file():
            report["roles"][role] = {"status": "missing_or_ambiguous"}
            missing.append(role)
            continue
        if path.stat().st_size == 0:
            report["roles"][role] = {"status": "empty_file", "file_name": path.name}
            missing.append(role)
            continue
        details = audit_archive(path) if role == "wave1_all_data" else audit_stata_header(path, role)
        report["roles"][role] = {"status": "metadata_read", **details}

    report["missing_or_ambiguous_roles"] = missing
    if not missing:
        report["release_gate"] = "input_set_complete_source_and_design_review_pending"
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intake", type=Path, default=DEFAULT_INTAKE,
                        help="Private folder containing the official Wave 1 source files")
    parser.add_argument("--all-data-zip", type=Path,
                        help="Explicit official Wave 1 all-data archive, if auto-discovery is ambiguous")
    parser.add_argument("--psu", type=Path, help="Explicit official PSU Stata file")
    parser.add_argument("--weight", type=Path, help="Explicit official Weight Stata file")
    parser.add_argument("--blood", type=Path, help="Explicit official Blood Stata file")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT,
                        help="Aggregate metadata report path under private storage")
    args = parser.parse_args()

    intake = private_input(args.intake)
    provided = {
        "wave1_all_data": args.all_data_zip,
        "psu": args.psu,
        "weight": args.weight,
        "blood": args.blood,
    }
    report = run_preflight(intake, provided)
    output = private_input(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for role, result in report["roles"].items():
        extra = ""
        if result.get("status") == "metadata_read":
            extra = f" file={result['file_name']} bytes={result['file_bytes']}"
        print(f"{role}: {result['status']}{extra}")
    print(f"2011 source gate: {report['release_gate']}")
    print(f"Metadata report saved outside the repository: {output}")
    if report["missing_or_ambiguous_roles"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
