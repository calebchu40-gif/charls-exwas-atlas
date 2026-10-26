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
import re
import uuid
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
ROLE_DOCUMENTS = {"wave1_all_data": 123, "psu": 117, "weight": 118, "blood": 201}
SOURCE_MANIFEST_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{2,63}$")
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


def evaluate_source_manifest(manifest: dict[str, Any] | None,
                             role_results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Validate a private, human-reviewed source manifest against received files.

    This validates recorded evidence and byte identity; it cannot independently
    prove how a user authenticated to CHARLS or where a file was downloaded.
    """
    if not isinstance(manifest, dict):
        return {
            "source_manifest_id": "",
            "source_identity_status": "unresolved",
            "source_hash_status": "unavailable_pending_authorized_file",
            "source_identity_review_errors": ["intake_manifest.json is absent or invalid"],
        }

    manifest_id = str(manifest.get("source_manifest_id", "")).strip()
    safe_id = manifest_id if SOURCE_MANIFEST_ID_RE.fullmatch(manifest_id) else ""
    errors: list[str] = []
    if not safe_id:
        errors.append("source_manifest_id is missing or is not an opaque identifier")

    required_files = manifest.get("required_files")
    if not isinstance(required_files, list):
        required_files = []
        errors.append("required_files is missing or invalid")
    entries: dict[str, dict[str, Any]] = {}
    for entry in required_files:
        if not isinstance(entry, dict):
            continue
        role = entry.get("role")
        if role in entries:
            errors.append(f"duplicate manifest entry for role {role}")
        elif role in ROLE_URLS:
            entries[role] = entry
    present_roles = [role for role in ROLE_URLS if role_results.get(role, {}).get("status") == "metadata_read"]
    all_files_present = len(present_roles) == len(ROLE_URLS)
    if not all_files_present:
        return {
            "source_manifest_id": safe_id,
            "source_identity_status": "unavailable_pending_authorized_file",
            "source_hash_status": "unavailable_pending_authorized_file",
            "source_identity_review_errors": errors + [
                f"required source files absent or ambiguous: {', '.join(role for role in ROLE_URLS if role not in present_roles)}"
            ],
        }

    review = manifest.get("source_identity_review")
    if not isinstance(review, dict):
        review = {}
    if review.get("status") != "verified_official_source":
        errors.append("source_identity_review.status is not verified_official_source")
    if not str(review.get("reviewed_at", "")).strip():
        errors.append("source_identity_review.reviewed_at is missing")
    if not str(review.get("reviewer_note", "")).strip():
        errors.append("source_identity_review.reviewer_note is missing")

    for role in ROLE_URLS:
        entry = entries.get(role)
        observed = role_results[role]
        if entry is None:
            errors.append(f"manifest entry missing for role {role}")
            continue
        if str(entry.get("source_page", "")).strip() != ROLE_URLS[role]:
            errors.append(f"official source page mismatch for role {role}")
        if entry.get("official_document") != ROLE_DOCUMENTS[role]:
            errors.append(f"official document id mismatch for role {role}")
        if str(entry.get("original_filename", "")).strip() != observed.get("file_name"):
            errors.append(f"original filename mismatch or missing for role {role}")
        if str(entry.get("downloaded_at", "")).strip() == "":
            errors.append(f"downloaded_at missing for role {role}")
        if entry.get("identity_review_status") != "verified_official_source":
            errors.append(f"identity review is not verified for role {role}")
        if str(entry.get("reviewed_local_sha256", "")).lower() != str(observed.get("local_sha256", "")).lower():
            errors.append(f"reviewed local SHA-256 does not match received file for role {role}")
        if not str(entry.get("official_title", "")).strip():
            errors.append(f"official_title missing for role {role}")

    return {
        "source_manifest_id": safe_id,
        "source_identity_status": "verified_official_source" if safe_id and not errors else "unresolved",
        "source_hash_status": "private_local_sha256_recorded",
        "source_identity_review_errors": errors,
    }


def refresh_manifest_after_file_change(manifest: dict[str, Any],
                                       role_results: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], bool]:
    """Pin current input hashes; rotate the manifest ID and reopen review on change."""
    current = {
        role: str(result.get("local_sha256", "")).lower()
        for role, result in role_results.items()
        if result.get("status") == "metadata_read" and result.get("local_sha256")
    }
    if len(current) != len(ROLE_URLS):
        return manifest, False

    previous = manifest.get("last_preflight_local_sha256")
    changed = isinstance(previous, dict) and bool(previous) and previous != current
    if changed:
        manifest["source_manifest_id"] = "charls2011-" + uuid.uuid4().hex
        manifest["source_identity_review"] = {
            "status": "unresolved",
            "reviewed_at": None,
            "reviewer_note": None,
        }
        for item in manifest.get("required_files", []):
            if isinstance(item, dict):
                item["identity_review_status"] = "unresolved"
                item["reviewed_local_sha256"] = None
    manifest["last_preflight_local_sha256"] = current
    return manifest, changed


def run_preflight(intake: Path, explicit: dict[str, Path | None]) -> dict[str, Any]:
    intake = private_input(intake)
    manifest_path = intake / "intake_manifest.json"
    try:
        private_input(manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        manifest = None
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
    manifest_changed = False
    if manifest is not None and not missing:
        manifest, manifest_changed = refresh_manifest_after_file_change(manifest, report["roles"])
        if manifest_changed or not manifest.get("last_preflight_local_sha256"):
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report.update(evaluate_source_manifest(manifest, report["roles"]))
    report["source_manifest_rotated_after_file_change"] = manifest_changed
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
