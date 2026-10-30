"""Audit Wave 3 birth-date route completeness using aggregate-only private QA.

Reads only the Wave 3 frame flag, interview year/month and official birth-date
route/date/calendar fields. It does not read or emit IDs, blood measurements,
exposures, or other outcomes. The report must remain under protected storage.
This is a source/eligibility preparation audit, not an age derivation or model.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path


DEFAULT_DATA = PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2015_person_analytic_with_official_blood.dta"
DEFAULT_MANIFEST = PRIVATE_ROOT / "derived_wave_tables" / "prepared_data_manifest.json"
DEFAULT_OUTPUT = QA_OUTPUT_DIR / "wave3_age_route_private_qa.json"
DEFAULT_ARCHIVE = PRIVATE_ROOT / "intake_raw" / "files" / "2015_1863_CHARLS2015r.zip"
DEFAULT_BLOOD = PRIVATE_ROOT / "intake_raw" / "files" / "2015_2088_Blood.zip"
REQUIRED = (
    "id", "crosssection", "iyear", "imonth", "ba002", "ba002_1", "ba002_2",
    "ba002_3", "ba003", "ba004_w3", "ba004_w3_1", "ba004_w3_2", "ba004_w3_3",
)


def in_private(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Wave 3 age-route inputs and QA must stay under protected private storage")
    return resolved


def sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def field_map(columns: list[str]) -> dict[str, str]:
    return {name.casefold(): name for name in columns}


def count(mask: pd.Series) -> int:
    return int(mask.fillna(False).sum())


def audit(data_path: Path, manifest_path: Path, output_path: Path,
          archive_path: Path, blood_path: Path) -> dict[str, object]:
    data_path, manifest_path, output_path, archive_path, blood_path = map(
        in_private, (data_path, manifest_path, output_path, archive_path, blood_path)
    )
    if not all(path.is_file() for path in (data_path, manifest_path, archive_path, blood_path)):
        raise FileNotFoundError("protected Wave 3 source archives, merged table, or manifest are missing")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    waves = [item for item in manifest.get("waves", []) if str(item.get("wave")) == "2015"]
    if len(waves) != 1 or waves[0].get("person_spine_module") != "sample_infor":
        raise ValueError("Wave 3 manifest must identify Sample_Infor as the person spine")
    artifacts = [item for item in waves[0].get("derived_artifacts", [])
                 if item.get("artifact_type") == "2015_official_blood_merged_person_table"]
    if len(artifacts) != 1:
        raise ValueError("manifest must bind exactly one official Wave 3 Blood merge")
    expected_hash = artifacts[0].get("sha256")
    if not expected_hash or sha256(data_path) != expected_hash:
        raise ValueError("merged Wave 3 table does not match its protected provenance manifest")
    from merge_2015_official_blood import EXPECTED_WAVE3_ARCHIVE_SHA1, EXPECTED_WAVE3_BLOOD_SHA1

    def sha1(path: Path) -> str:
        import hashlib

        digest = hashlib.sha1()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    archive_hash = sha1(archive_path)
    blood_hash = sha1(blood_path)
    if archive_hash != EXPECTED_WAVE3_ARCHIVE_SHA1 or blood_hash != EXPECTED_WAVE3_BLOOD_SHA1:
        raise ValueError("protected Wave 3 archives do not match the pinned official source hashes")
    if (artifacts[0].get("source_archive_sha1") != archive_hash
            or artifacts[0].get("blood_artifact_sha1") != blood_hash):
        raise ValueError("Wave 3 merge manifest does not bind the checked official source archives")

    _, metadata = pyreadstat.read_dta(str(data_path), metadataonly=True)
    columns = field_map(metadata.column_names)
    missing = [name for name in REQUIRED if name not in columns]
    if missing:
        raise ValueError(f"Wave 3 merged table is missing required route fields: {missing}")
    chosen = [columns[name] for name in REQUIRED if name != "id"]
    frame, _ = pyreadstat.read_dta(str(data_path), usecols=chosen)
    frame.columns = [column.casefold() for column in frame.columns]

    cross = pd.to_numeric(frame["crosssection"], errors="coerce")
    domain = cross.eq(1)
    route = pd.to_numeric(frame["ba002"], errors="coerce")
    actual_doc = route.eq(1)
    actual_report = route.eq(2)
    route_unknown = ~(actual_doc | actual_report)
    selected = {}
    for component in ("1", "2", "3"):
        selected[component] = frame[f"ba004_w3_{component}"].where(actual_doc, frame[f"ba002_{component}"].where(actual_report))
    year = pd.to_numeric(selected["1"], errors="coerce")
    month = pd.to_numeric(selected["2"], errors="coerce")
    day = pd.to_numeric(selected["3"], errors="coerce")
    calendar = pd.to_numeric(frame["ba003"], errors="coerce")
    interview_year = pd.to_numeric(frame["iyear"], errors="coerce")
    interview_month = pd.to_numeric(frame["imonth"], errors="coerce")

    # Separate absent Demographic_Background rows from BA002 item-level
    # missingness by joining only pseudonymous IDs and the route field. This
    # avoids treating Sample_Infor frame rows without a demographic-module row
    # as questionnaire refusals/DK responses.
    with zipfile.ZipFile(archive_path) as source_zip:
        demog_members = [name for name in source_zip.namelist()
                         if name.casefold() == "demographic_background.dta"]
        if len(demog_members) != 1:
            raise ValueError("official Wave 3 archive must contain one Demographic_Background.dta")
        demog_bytes = io.BytesIO(source_zip.read(demog_members[0]))
    _, demog_metadata = pyreadstat.read_dta(demog_bytes, metadataonly=True)
    demog_columns = field_map(demog_metadata.column_names)
    if "id" not in demog_columns or "ba002" not in demog_columns:
        raise ValueError("official Demographic_Background module lacks ID or BA002")
    demog_bytes.seek(0)
    demog_ids_routes, _ = pyreadstat.read_dta(
        demog_bytes, usecols=[demog_columns["id"], demog_columns["ba002"]], user_missing=True
    )
    _, prepared_metadata = pyreadstat.read_dta(str(data_path), metadataonly=True)
    prepared_columns = field_map(prepared_metadata.column_names)
    prepared_ids_routes, _ = pyreadstat.read_dta(
        str(data_path), usecols=[prepared_columns["id"], prepared_columns["ba002"]], user_missing=True
    )

    def norm_id(value: object) -> str:
        return "" if pd.isna(value) else str(value).strip()

    def norm_route(value: object) -> str:
        return "" if pd.isna(value) else str(value).strip()

    module_ids = demog_ids_routes.iloc[:, 0].map(norm_id)
    prepared_ids = prepared_ids_routes.iloc[:, 0].map(norm_id)
    module_route = demog_ids_routes.iloc[:, 1].map(norm_route)
    prepared_route = prepared_ids_routes.iloc[:, 1].map(norm_route)
    if module_ids.eq("").any() or prepared_ids.eq("").any():
        raise ValueError("Wave 3 source or prepared IDs contain missing values")
    if module_ids.duplicated().any() or prepared_ids.duplicated().any():
        raise ValueError("Wave 3 source or prepared IDs are not unique")
    module_id_set = set(module_ids)
    module_route_by_id = dict(zip(module_ids, module_route))
    frame_module_present = prepared_ids.isin(module_id_set)
    prepared_route_missing = prepared_route.eq("")
    module_route_missing = module_route.eq("")
    route_mismatch_n = sum(
        module_route_by_id.get(pid, "") != route
        for pid, route, present in zip(prepared_ids, prepared_route, frame_module_present)
        if present
    )
    module_ids_in_frame_n = int(module_ids.isin(set(prepared_ids)).sum())
    module_linkage = {
        "frame_rows": int(len(prepared_ids)),
        "demographic_module_rows": int(len(module_ids)),
        "unique_frame_ids": int(prepared_ids.nunique()),
        "unique_module_ids": int(module_ids.nunique()),
        "demographic_module_ids_found_in_frame": module_ids_in_frame_n,
        "frame_rows_with_demographic_module": int(frame_module_present.sum()),
        "frame_rows_without_demographic_module": int((~frame_module_present).sum()),
        "ba002_missing_on_module_present_frame_rows": int((frame_module_present & prepared_route_missing).sum()),
        "ba002_missing_on_module_absent_frame_rows": int(((~frame_module_present) & prepared_route_missing).sum()),
        "ba002_present_on_module_absent_frame_rows": int(((~frame_module_present) & ~prepared_route_missing).sum()),
        "prepared_vs_official_module_ba002_mismatches": int(route_mismatch_n),
        "IDs_emitted": False,
    }
    route_unknown_n = count(domain & route_unknown)
    # BA003 is observed for the separate actual-date route (BA002=2), not for
    # the much larger same-as-document route (BA002=1). Requiring BA003 on
    # BA002=1 incorrectly turns structurally unasked values into missingness.
    # The official 2015 Codebook frequency table lists BA003 observations at
    # roughly the size of the BA002=2 route, while BA002=1 is the dominant
    # response. Keep this route assumption explicit for methods review.
    calendar_required = domain & actual_report
    calendar_unknown_n = count(calendar_required & ~(calendar.eq(1) | calendar.eq(2)))
    route_calendar_cross_tab = {}
    for route_name, route_mask in (
        ("same_as_document_ba002_1", domain & actual_doc),
        ("separate_actual_date_ba002_2", domain & actual_report),
        ("unknown_or_missing_ba002", domain & route_unknown),
    ):
        route_calendar_cross_tab[route_name] = {
            "solar": count(route_mask & calendar.eq(1)),
            "lunar": count(route_mask & calendar.eq(2)),
            "missing_or_unrecognized": count(route_mask & ~(calendar.eq(1) | calendar.eq(2))),
            "route_rows": count(route_mask),
        }
    birth_year_missing_n = count(domain & year.isna())
    birth_year_invalid_n = count(domain & year.notna() & ~year.between(1900, 2015))
    birth_month_unknown_n = count(domain & (month.isna() | month.eq(0)))
    birth_day_unknown_n = count(domain & (day.isna() | day.eq(0)))
    birth_month_invalid_n = count(domain & month.notna() & ~(month.eq(0) | month.between(1, 12)))
    birth_day_invalid_n = count(domain & day.notna() & ~(day.eq(0) | day.between(1, 31)))
    interview_time_incomplete_n = count(domain & (interview_year.isna() | ~interview_month.between(1, 12)))

    report = {
        "wave": "2015",
        "source_frame": "official Sample_Infor; crosssection == 1 defines the described cross-sectional domain",
        "data_sha256": expected_hash,
        "official_archive_sha1_verified": True,
        "official_blood_artifact_sha1_verified": True,
        "manifest_spine": waves[0]["person_spine_module"],
        "field_route_source": "CHARLS 2015 Codebook and Questionnaire; BA002 1=same as civil document (use BA004_W3 date), 2=separate actual date (use BA002 date); BA003 1=solar, 2=lunar; questionnaire says .d/.r skip BA003",
        "calendar_applicability_assumption": "Provisional: require BA003 when BA002=2; BA002=1 uses the civil-document date. Private cross-tab also found BA003 values on some BA002=1 records, so the route interpretation and discordant cases require independent methods review.",
        "frame_module_linkage": module_linkage,
        "identifiers_processed_in_memory_for_private_join_only": True,
        "participant_level_values_or_ids_emitted": False,
        "aggregate_counts_emitted": True,
        "blood_or_exposure_outcomes_read": False,
        "counts_private_only": True,
        "domain": {
            "frame_rows": int(len(frame)),
            "crosssection_yes": count(domain),
            "crosssection_missing_or_other": count(~domain),
        },
        "birth_route": {
            "same_as_document": count(domain & actual_doc),
            "separate_actual_date": count(domain & actual_report),
            "unknown_missing_or_unrecognized": count(domain & route_unknown),
        },
        "selected_birth_date_components": {
            "year_present": count(domain & year.notna()),
            "year_in_questionnaire_range_1900_2015": count(domain & year.between(1900, 2015)),
            "month_zero_unknown": count(domain & month.eq(0)),
            "month_1_to_12": count(domain & month.between(1, 12)),
            "month_missing_or_out_of_range": count(domain & ~(month.eq(0) | month.between(1, 12))),
            "day_zero_unknown": count(domain & day.eq(0)),
            "day_1_to_31": count(domain & day.between(1, 31)),
            "day_missing_or_out_of_range": count(domain & ~(day.eq(0) | day.between(1, 31))),
        },
        "calendar_route": {
            "solar": count(domain & calendar.eq(1)),
            "lunar": count(domain & calendar.eq(2)),
            "missing_or_unrecognized": count(domain & ~(calendar.eq(1) | calendar.eq(2))),
            "ba003_present_on_same_as_document_route": count(domain & actual_doc & (calendar.eq(1) | calendar.eq(2))),
            "missing_or_unrecognized_on_separate_actual_date_route": calendar_unknown_n,
            "by_ba002_route": route_calendar_cross_tab,
        },
        "interview_timing": {
            "year_present": count(domain & interview_year.notna()),
            "month_1_to_12": count(domain & interview_month.between(1, 12)),
            "month_missing_or_out_of_range": count(domain & ~interview_month.between(1, 12)),
            "interview_day_available": False,
        },
        "gate_summary": {
            "unknown_birth_route_present": route_unknown_n > 0,
            "calendar_value_on_same_as_document_route_present": count(domain & actual_doc & (calendar.eq(1) | calendar.eq(2))) > 0,
            "unrecognized_or_missing_calendar_on_separate_actual_date_route_present": calendar_unknown_n > 0,
            "birth_year_outside_documented_range_present": birth_year_invalid_n > 0,
            "birth_year_missing_present": birth_year_missing_n > 0,
            "unknown_birth_month_or_day_present": birth_month_unknown_n > 0 or birth_day_unknown_n > 0,
            "invalid_birth_month_or_day_code_present": birth_month_invalid_n > 0 or birth_day_invalid_n > 0,
            "incomplete_interview_year_month_present": interview_time_incomplete_n > 0,
            "age_interval_ready": False,
            "reason_age_interval_not_ready": "route/date validity and calendar applicability require review; age interval and independent methods review are not complete",
        },
        "age_derived": False,
        "eligibility_gate": "not_passed; route/date validity and age interval still require review",
        "association_models_fitted": 0,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp = output_path.with_suffix(output_path.suffix + ".tmp")
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        temp.chmod(0o600)
    os.replace(temp, output_path)
    if os.name == "posix":
        output_path.chmod(0o600)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--blood-artifact", type=Path, default=DEFAULT_BLOOD)
    args = parser.parse_args()
    report = audit(args.data, args.manifest, args.output, args.archive, args.blood_artifact)
    print(json.dumps({
        "message": "Wave 3 aggregate-only age-route QA written to protected storage",
        "eligibility_gate": report["eligibility_gate"],
        "gate_summary": report["gate_summary"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
