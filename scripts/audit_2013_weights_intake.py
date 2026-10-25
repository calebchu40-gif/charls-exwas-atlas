"""Check official CHARLS Wave 2 Weights.dta provenance and header only.

This pre-merge gate accepts only the exact release artifact listed by CHARLS.
It reads the Stata header with ``metadataonly=True`` and does not inspect
respondent values, sample-flag counts, IDs, or merge the file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pyreadstat

from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path


EXPECTED_OFFICIAL_WEIGHTS_SHA1 = "22c4fc89df2e55fa8faf051e88830eebe0e035c0"
REQUIRED_FIELDS = ("id", "crosssection", "longitudinal")
DEFAULT_INTAKE = PRIVATE_ROOT / "incoming_2013_weights"
DEFAULT_SOURCE = DEFAULT_INTAKE / "Weights.dta"
DEFAULT_QA = QA_OUTPUT_DIR / "charls_2013_weights_intake_metadata.json"


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


def audit_weights_header(
    path: Path,
    expected_sha1: str = EXPECTED_OFFICIAL_WEIGHTS_SHA1,
) -> dict[str, object]:
    """Verify pinned CHARLS artifact hash and required header fields."""
    actual_sha1 = sha1_file(path).lower()
    if actual_sha1 != expected_sha1.lower():
        raise ValueError(
            "Weights.dta SHA1 does not match the official CHARLS Wave 2 listing; "
            f"expected {expected_sha1.lower()}, got {actual_sha1}. No intake accepted."
        )

    _, metadata = pyreadstat.read_dta(str(path), metadataonly=True)
    names = {str(name).casefold() for name in metadata.column_names}
    missing = [field for field in REQUIRED_FIELDS if field not in names]
    weight_fields = sorted(
        str(name) for name in metadata.column_names if "weight" in str(name).casefold()
    )
    if missing:
        raise ValueError(f"Official Weights.dta header is missing required fields: {missing}")
    if not weight_fields:
        raise ValueError("Official Weights.dta header contains no weight variables")

    return {
        "wave": "2013",
        "release_version": "20151118",
        "metadata_only": True,
        "respondent_values_read": False,
        "row_count_from_stata_header": int(metadata.number_rows),
        "column_count": len(metadata.column_names),
        "required_fields": list(REQUIRED_FIELDS),
        "required_fields_present": len(REQUIRED_FIELDS),
        "weight_field_count": len(weight_fields),
        "weight_field_names": weight_fields,
        "official_sha1": actual_sha1,
        "source_sha256": sha256_file(path),
        "source_page": "https://charls.charlsdata.com/pages/Data/2013-charls-wave2/en.html",
        "release_note": "https://charls.pku.edu.cn/en/data/Release2013.pdf",
        "interpretation": (
            "Provenance/header check only. Sample-flag values, IDs, weight values, "
            "matches, analytic Ns, and associations were not inspected."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, default=DEFAULT_SOURCE,
                        help="Official CHARLS Wave 2 Weights.dta in private local storage")
    parser.add_argument("--output", type=Path, default=DEFAULT_QA,
                        help="Aggregate metadata QA path under protected local storage")
    args = parser.parse_args()
    source = require_private_path(args.weights)
    output = require_private_path(args.output)
    if not source.is_file():
        raise FileNotFoundError(f"Official Wave 2 Weights.dta not found: {source}")
    result = audit_weights_header(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "2013 Weights.dta metadata gate passed: "
        f"rows={result['row_count_from_stata_header']} "
        f"columns={result['column_count']} "
        f"sample_flags={','.join(REQUIRED_FIELDS[1:])} "
        f"sha1={result['official_sha1']}"
    )


if __name__ == "__main__":
    main()
