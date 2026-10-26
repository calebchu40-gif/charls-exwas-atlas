"""Merge the separately released 2015 Blood Data into a verified Wave 3 table.

This is a protected local preparation step, not an analysis. It requires exact
CHARLS SHA-1 matches for both the Wave 3 all-data archive and separate Blood
artifact, plus an output/source hash manifest created by the current wave-table
builder. It preserves the full prepared frame and retains the cross-sectional
flag; official Blood_weight must not be interpreted as a panel weight.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyreadstat

from audit_2015_blood_intake import audit_intake
from prepare_charls_wave_tables import normalize_key
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path

EXPECTED_WAVE3_ARCHIVE_SHA1 = "47aab04178a6895ce687beb2f74286215e8f6b33"
EXPECTED_WAVE3_BLOOD_SHA1 = "de5b1d80e9b72d61b690dff19b191f50f21ee8c5"
EXPECTED_WAVE3_BLOOD_ROWS = 13_420
OFFICIAL_SOURCE_PAGE = "https://charls.charlsdata.com/pages/Data/2015-charls-wave4/en.html"
OFFICIAL_BLOOD_RELEASE_NOTE = "https://charls.pku.edu.cn/en/data/Blood2015.pdf"
MANIFEST = WAVE_DATA_DIR / "prepared_data_manifest.json"
DEFAULT_PREPARED = WAVE_DATA_DIR / "CHARLS_wave2015_person_analytic.dta"
DEFAULT_BLOOD_ARTIFACT = PRIVATE_ROOT / "incoming_2015_blood" / "Blood_Data_2015_download"
DEFAULT_BLOOD_STATA = PRIVATE_ROOT / "incoming_2015_blood" / "Blood_Data_2015.dta"
DEFAULT_OUTPUT = WAVE_DATA_DIR / "CHARLS_wave2015_person_analytic_with_official_blood.dta"
DEFAULT_QA = QA_OUTPUT_DIR / "charls_2015_official_blood_merge_qa.json"

BLOOD_FIELDS = (
    "blood_weight", "bl_fasting", "bl_wbc", "bl_hgb", "bl_hct", "bl_mcv",
    "bl_plt", "bl_tg", "bl_crea", "bl_bun", "bl_hdl", "bl_ldl", "bl_cho",
    "bl_glu", "bl_ua", "bl_cysc", "bl_crp", "bl_hbalc", "bl_top_coding_tg",
)


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


def verify_sha1(path: Path, expected: str, label: str) -> str:
    observed = sha1_file(path).lower()
    if observed != expected.lower():
        raise ValueError(f"{label} SHA-1 does not match the official CHARLS listing; no merge performed")
    return observed


def validate_prepared_provenance(record: dict, prepared: Path, archive: Path) -> None:
    """Bind the prepared Wave 3 table to the exact, checksum-verified archive."""
    source = record.get("source_archive")
    output = record.get("prepared_output")
    if not isinstance(source, dict) or not isinstance(output, dict):
        raise ValueError("prepared Wave 3 table lacks source/output hashes; rebuild it from the official archive first")
    archive_sha256 = sha256_file(archive)
    prepared_sha256 = sha256_file(prepared)
    if (int(source.get("bytes", 0)) != archive.stat().st_size
            or str(source.get("sha256", "")).lower() != archive_sha256):
        raise ValueError("prepared Wave 3 source archive does not match the verified official archive")
    if (output.get("filename") != prepared.name
            or int(output.get("bytes", 0)) != prepared.stat().st_size
            or str(output.get("sha256", "")).lower() != prepared_sha256):
        raise ValueError("prepared Wave 3 table does not match its recorded output hash")


def _column_map(frame: pd.DataFrame) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in frame.columns:
        folded = str(name).casefold()
        if folded in result:
            raise ValueError(f"case-insensitive column-name collision in protected input: {folded}")
        result[folded] = str(name)
    return result


def merge_blood_tables(prepared: pd.DataFrame, blood: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    """Left-merge blood responders by unique CHARLS ID without row expansion."""
    prepared_cols = _column_map(prepared)
    blood_cols = _column_map(blood)
    for name in ("id", "crosssection"):
        if name not in prepared_cols:
            raise ValueError(f"prepared Wave 3 table must retain the official {name} field")
    required = ("id", *BLOOD_FIELDS)
    missing = [name for name in required if name not in blood_cols]
    if missing:
        raise ValueError(f"official Blood Data file is missing required fields: {missing}")

    collision = sorted(set(BLOOD_FIELDS) & set(prepared_cols))
    if collision:
        raise ValueError(f"Blood Data fields already exist in prepared table; rebuild from clean archive: {collision}")

    prepared_key = normalize_key(prepared[prepared_cols["id"]])
    blood_key = normalize_key(blood[blood_cols["id"]])
    if prepared_key.isna().any() or prepared_key.duplicated().any():
        raise ValueError("prepared Wave 3 respondent ID key must be complete and unique")
    if blood_key.isna().any() or blood_key.duplicated().any():
        raise ValueError("official Blood Data respondent ID key must be complete and unique")
    prepared_ids = set(prepared_key.tolist())
    blood_ids = set(blood_key.tolist())
    if not blood_ids.issubset(prepared_ids):
        raise ValueError("official Blood Data contains IDs absent from the prepared Wave 3 respondent frame")

    left = prepared.copy()
    left["_exwas_join_id"] = prepared_key.to_numpy()
    right = blood[[blood_cols["id"], *[blood_cols[name] for name in BLOOD_FIELDS]]].copy()
    right.columns = ["_blood_join_id", *BLOOD_FIELDS]
    right["_blood_join_id"] = blood_key.to_numpy()
    merged = left.merge(
        right, left_on="_exwas_join_id", right_on="_blood_join_id", how="left",
        validate="one_to_one", sort=False, indicator="_blood_merge_status",
    )
    matched = int(merged["_blood_merge_status"].eq("both").sum())
    if len(merged) != len(prepared) or merged[prepared_cols["id"]].tolist() != prepared[prepared_cols["id"]].tolist():
        raise ValueError("Blood merge changed prepared respondent row count or order")
    merged = merged.drop(columns=["_exwas_join_id", "_blood_join_id", "_blood_merge_status"])
    qa = {
        "wave": "2015",
        "merge_key": "respondent ID; one-to-one left merge",
        "prepared_rows": int(len(prepared)),
        "blood_release_rows": int(len(blood)),
        "blood_ids_matched_to_prepared_frame": matched,
        "prepared_rows_with_blood_record": matched,
        "prepared_rows_without_blood_record": int(len(prepared) - matched),
        "row_expansion": False,
        "crosssection_flag_retained": True,
        "blood_weight_scope": "cross-sectional only; not a released panel blood weight",
        "analysis_eligibility": "not assessed by merge; confirm cross-sectional codes, PSU/variance design, and estimand before modeling",
    }
    return merged, qa


def _atomic_json(path: Path, payload: dict[str, object]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def merge_official_blood(
    archive: Path, blood_artifact: Path, blood_stata: Path, prepared: Path,
    manifest_path: Path = MANIFEST, output: Path = DEFAULT_OUTPUT, qa_output: Path = DEFAULT_QA,
) -> dict[str, object]:
    paths = {"archive": archive, "blood_artifact": blood_artifact, "blood_stata": blood_stata,
             "prepared": prepared, "manifest": manifest_path, "output": output, "qa_output": qa_output}
    paths = {key: require_private_path(value) for key, value in paths.items()}
    for key in ("archive", "blood_artifact", "blood_stata", "prepared", "manifest"):
        if not paths[key].is_file():
            raise FileNotFoundError(f"required protected Wave 3 input is missing: {key}")
    if not paths["output"].is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Wave 3 merged output must remain under protected local storage")
    if not paths["qa_output"].is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Wave 3 merge QA must remain under protected local storage")
    if paths["output"].exists():
        raise FileExistsError("refusing to overwrite an existing merged Wave 3 table")

    archive_sha1 = verify_sha1(paths["archive"], EXPECTED_WAVE3_ARCHIVE_SHA1, "Wave 3 All Data archive")
    blood_audit = audit_intake(paths["blood_artifact"], paths["blood_stata"], EXPECTED_WAVE3_BLOOD_ROWS)
    blood_sha1 = verify_sha1(paths["blood_artifact"], EXPECTED_WAVE3_BLOOD_SHA1, "Wave 3 Blood Data artifact")
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    entries = [item for item in manifest.get("waves", []) if str(item.get("wave")) == "2015"]
    if len(entries) != 1:
        raise ValueError("prepared-data manifest must contain exactly one 2015 wave entry")
    validate_prepared_provenance(entries[0], paths["prepared"], paths["archive"])

    prepared_data, prepared_meta = pyreadstat.read_dta(str(paths["prepared"]))
    blood_data, blood_meta = pyreadstat.read_dta(str(paths["blood_stata"]))
    merged, qa = merge_blood_tables(prepared_data, blood_data)
    labels = {name: label for name, label in zip(prepared_meta.column_names, prepared_meta.column_labels or []) if label}
    blood_labels = {name.casefold(): label for name, label in
                    zip(blood_meta.column_names, blood_meta.column_labels or []) if label}
    labels.update({name: blood_labels[name] for name in BLOOD_FIELDS if name in blood_labels})

    paths["output"].parent.mkdir(parents=True, exist_ok=True)
    temporary = paths["output"].with_name(paths["output"].stem + ".tmp.dta")
    try:
        pyreadstat.write_dta(merged, str(temporary), column_labels={key: val for key, val in labels.items() if key in merged},
                             version=15, file_label="CHARLS 2015 respondent table with official Blood Data")
        _, output_meta = pyreadstat.read_dta(str(temporary), metadataonly=True)
        if output_meta.number_rows != len(prepared_data) or output_meta.number_columns != len(merged.columns):
            raise RuntimeError("Wave 3 blood merge output failed metadata readback")
        os.replace(temporary, paths["output"])
    finally:
        temporary.unlink(missing_ok=True)

    output_record = {
        "artifact_type": "2015_official_blood_merged_person_table",
        "filename": paths["output"].name,
        "bytes": paths["output"].stat().st_size,
        "sha256": sha256_file(paths["output"]),
        "source_archive_sha1": archive_sha1,
        "blood_artifact_sha1": blood_sha1,
        "blood_stata_sha256": blood_audit["stata_file_sha256"],
        "prepared_table_sha256": sha256_file(paths["prepared"]),
        "official_source_page": OFFICIAL_SOURCE_PAGE,
        "official_blood_release_note": OFFICIAL_BLOOD_RELEASE_NOTE,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "pandas_version": pd.__version__,
        "pyreadstat_version": getattr(pyreadstat, "__version__", "unknown"),
        "builder_script_sha256": sha256_file(Path(__file__).resolve()),
    }
    wave_entry = entries[0]
    derived = [item for item in wave_entry.get("derived_artifacts", [])
               if item.get("artifact_type") != output_record["artifact_type"]]
    wave_entry["derived_artifacts"] = [*derived, output_record]
    qa.update({
        "official_all_data_archive_sha1": archive_sha1,
        "official_blood_artifact_sha1": blood_sha1,
        "blood_stata_sha256": blood_audit["stata_file_sha256"],
        "merged_output_file": paths["output"].name,
        "merged_output_sha256": output_record["sha256"],
        "participant_level_data_written": True,
        "qa_contains_participant_values_or_ids": False,
    })
    paths["qa_output"].parent.mkdir(parents=True, exist_ok=True)
    _atomic_json(paths["qa_output"], qa)
    _atomic_json(paths["manifest"], manifest)
    return qa


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--merge", action="store_true", required=True,
                        help="explicitly authorize local merging of the two checksum-verified 2015 releases")
    parser.add_argument("--archive", type=Path, required=True,
                        help="official CHARLS2015r.zip used to build the prepared table")
    parser.add_argument("--blood-artifact", type=Path, default=DEFAULT_BLOOD_ARTIFACT)
    parser.add_argument("--blood-stata", type=Path, default=DEFAULT_BLOOD_STATA)
    parser.add_argument("--prepared", type=Path, default=DEFAULT_PREPARED)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--qa-output", type=Path, default=DEFAULT_QA)
    args = parser.parse_args()
    qa = merge_official_blood(args.archive, args.blood_artifact, args.blood_stata,
                              args.prepared, args.manifest, args.output, args.qa_output)
    print(json.dumps({key: value for key, value in qa.items()
                      if key not in {"blood_ids_matched_to_prepared_frame", "prepared_rows_with_blood_record",
                                     "prepared_rows_without_blood_record"}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
