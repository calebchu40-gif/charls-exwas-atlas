"""Create a protected, provisional Wave 1 age-interval candidate table.

This is a data-preparation aid, not a model-ready age approval. It reads only
the source-bound Wave 1 birth/calendar/conditional-age fields and official
interview year/month. It never writes DOBs, IDs, or person-level output to the
repository. Because CHARLS records interview month but not interview day and
does not record a separate leap-month flag, age is retained as an interval.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from calendar import monthrange
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path


LUNARDATE_014_SHA256 = "3b2eb1b90ec8107a7bd8a852a4efacd54ca4d3f5ce862145cfd5500e52ffed52"
EXPECTED_COLUMNS = (
    "ID", "birth_year", "birth_month", "birth_day", "calendar_type",
    "reported_age_conditional", "iyear", "imonth",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def private_path(path: Path, root: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"CHARLS inputs and derived files must remain under {root}")
    return resolved


def set_private_mode(path: Path, *, directory: bool = False) -> None:
    if os.name == "posix":
        os.chmod(path, 0o700 if directory else 0o600)


def number(value: Any) -> int | None:
    if pd.isna(value):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not parsed.is_integer():
        return None
    return int(parsed)


def age_on(birth: date, interview: date) -> int:
    return interview.year - birth.year - ((interview.month, interview.day) < (birth.month, birth.day))


def load_lunardate(source: Path):
    actual = sha256(source)
    if actual != LUNARDATE_014_SHA256:
        raise ValueError("Pinned lunardate 0.1.4 source SHA-256 mismatch")
    spec = importlib.util.spec_from_file_location("charls_pinned_lunardate_014", source)
    if spec is None or spec.loader is None:
        raise ValueError("Could not load the pinned lunar converter source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, actual


def validate_source_provenance(root: Path, intake: Path, rebuilt: Path) -> dict[str, Any]:
    intake_manifest_path = private_path(intake / "intake_manifest.json", root)
    prepared_manifest_path = private_path(rebuilt / "prepared_data_manifest.json", root)
    intake_manifest = json.loads(intake_manifest_path.read_text(encoding="utf-8"))
    if intake_manifest.get("status") != "source_identity_reviewed_metadata_only":
        raise ValueError("Official Wave 1 source identity review is not recorded")
    roles = {item.get("role"): item for item in intake_manifest.get("required_files", [])}
    required_roles = {"wave1_all_data", "psu", "weight", "blood"}
    if set(roles) != required_roles or any(
        roles[role].get("identity_review_status") != "verified_official_source"
        for role in required_roles
    ):
        raise ValueError("All four official Wave 1 source identities must be verified")
    prepared_manifest = json.loads(prepared_manifest_path.read_text(encoding="utf-8"))
    prepared_sources = prepared_manifest.get("source_inputs_by_wave", {}).get("2011", {})
    wave_entry = next(
        (item for item in prepared_manifest.get("waves", []) if item.get("wave") == "2011"),
        None,
    )
    if wave_entry is None or wave_entry.get("source_review", {}).get("source_manifest_id") != intake_manifest.get("source_manifest_id"):
        raise ValueError("Prepared respondent frame is not bound to the reviewed intake manifest")
    mapping = {
        "wave1_all_data": "all_data_archive",
        "psu": "psu",
        "weight": "weight",
        "blood": "blood",
    }
    for role, manifest_key in mapping.items():
        item = roles[role]
        prepared_item = prepared_sources.get(manifest_key, {})
        expected = item.get("reviewed_local_sha256")
        if not expected or expected != prepared_item.get("sha256"):
            raise ValueError(f"Source/prepared manifests disagree for {role}")
        source_path = private_path(intake / item.get("original_filename", ""), root)
        if not source_path.is_file() or sha256(source_path) != expected:
            raise ValueError(f"Current official source fingerprint mismatch for {role}")
    return {
        "source_manifest_id": intake_manifest.get("source_manifest_id"),
        "verified_roles": sorted(required_roles),
        "person_table_sha256": wave_entry.get("prepared_output", {}).get("sha256"),
        "weight_sha256": prepared_sources["weight"].get("sha256"),
    }


def derive() -> dict[str, Any]:
    root = private_path(PRIVATE_ROOT, PRIVATE_ROOT)
    intake = private_path(Path(os.environ.get("CHARLS_WAVE1_INTAKE_DIR", str(root / "incoming_2011_official"))), root)
    rebuilt = private_path(Path(os.environ.get(
        "CHARLS_WAVE1_REBUILT_DIR", str(root / "derived_wave_tables_2011_official_rebuild_20261029")
    )), root)
    age_dir = private_path(root / "age_inputs_2011", root)
    qa_dir = private_path(root / "qa_outputs", root)
    age_input = private_path(age_dir / "wave1_official_age_inputs.dta", root)
    age_input_qa = private_path(qa_dir / "wave1_official_age_inputs_qa.json", root)
    person_path = private_path(rebuilt / "CHARLS_wave2011_person_analytic.dta", root)
    weight_path = private_path(intake / "weight.dta", root)
    source_review = validate_source_provenance(root, intake, rebuilt)
    if not person_path.is_file() or sha256(person_path) != source_review["person_table_sha256"]:
        raise ValueError("Current protected respondent frame does not match its preparation manifest")
    if not weight_path.is_file() or sha256(weight_path) != source_review["weight_sha256"]:
        raise ValueError("Current official Weight.dta does not match its preparation manifest")
    input_qa = json.loads(age_input_qa.read_text(encoding="utf-8"))
    if input_qa.get("person_source_sha256") != source_review["person_table_sha256"]:
        raise ValueError("Age-input preparation QA does not match the current person table")
    if input_qa.get("weight_source_sha256") != source_review["weight_sha256"]:
        raise ValueError("Age-input preparation QA does not match the current Weight source")
    if input_qa.get("source_manifest_id") != source_review["source_manifest_id"]:
        raise ValueError("Age-input preparation QA is not bound to the current source review")
    if input_qa.get("age_input_sha256") != sha256(age_input):
        raise ValueError("Protected age-input file does not match its preparation QA fingerprint")
    _, age_meta = pyreadstat.read_dta(str(age_input), metadataonly=True)
    if set(EXPECTED_COLUMNS) - set(age_meta.column_names):
        raise ValueError("Protected age-input table is missing required source fields")
    if len(age_meta.column_names) != len(EXPECTED_COLUMNS) + 1:
        raise ValueError("Protected age-input table has unexpected columns")
    age_input_hash = sha256(age_input)

    reference_root = private_path(root / "references", root)
    converter_path = private_path(
        reference_root / "lunardate_0.1.4" / "lunardate-0.1.4" / "lunardate.py", root
    )
    lunar_module, lunar_source_hash = load_lunardate(converter_path)
    fields = list(EXPECTED_COLUMNS)
    frame, _ = pyreadstat.read_dta(str(age_input), usecols=fields)
    respondent_ids = frame["ID"].astype("string").str.strip()
    if respondent_ids.isna().any() or respondent_ids.eq("").any() or respondent_ids.duplicated().any():
        raise ValueError("Protected age-input respondent keys must be present and unique")
    output: list[dict[str, Any]] = []
    routes: Counter[str] = Counter()
    age45_status: Counter[str] = Counter()
    invalid: Counter[str] = Counter()
    invalid_detail: Counter[str] = Counter()

    for row in frame.itertuples(index=False, name=None):
        (respondent_id, raw_year, raw_month, raw_day, raw_calendar,
         raw_reported_age, raw_iyear, raw_imonth) = row
        year, month, day = number(raw_year), number(raw_month), number(raw_day)
        calendar_code = number(raw_calendar)
        reported_age = number(raw_reported_age)
        interview_year, interview_month = number(raw_iyear), number(raw_imonth)
        lower = upper = None
        route = "unresolved_input"
        leap_ambiguity = False

        if interview_year is None or interview_month is None or not 1 <= interview_month <= 12:
            route = "missing_interview_month"
        elif year is not None and 1900 <= year <= interview_year and calendar_code in (1, 2):
            complete = month is not None and day is not None and 1 <= month <= 12 and 1 <= day <= 31
            if calendar_code == 1 and complete:
                try:
                    birth = date(year, month, day)
                    route = "solar_full_date_interview_day_unknown"
                except ValueError:
                    birth = None
                    invalid["invalid_solar_date"] += 1
                    invalid_detail["solar_day_exceeds_calendar_month"] += 1
                    route = "invalid_solar_date"
                if birth is not None:
                    interview_first = date(interview_year, interview_month, 1)
                    interview_last = date(interview_year, interview_month, monthrange(interview_year, interview_month)[1])
                    lower, upper = sorted((age_on(birth, interview_first), age_on(birth, interview_last)))
            elif calendar_code == 2 and complete:
                outside_lunar_domain = False
                try:
                    lunar_key = year * 10000 + month * 100 + day
                    if lunar_key < 19000101 or lunar_key > 20401128:
                        outside_lunar_domain = True
                        raise ValueError("outside official lunar converter domain")
                    year_info = lunar_module.yearInfos[year - 1900]
                    leap_month = year_info % 16
                    leap_ambiguity = leap_month == month
                    if leap_ambiguity:
                        # No leap-month answer exists in the questionnaire. Validate the
                        # date against either route but retain only a year-based age interval.
                        try:
                            lunar_module.LunarDate(year, month, day, False).toSolarDate()
                        except ValueError:
                            lunar_module.LunarDate(year, month, day, True).toSolarDate()
                        lower, upper = max(0, interview_year - year - 1), interview_year - year
                        route = "lunar_leap_month_ambiguous_year_interval"
                    else:
                        birth = lunar_module.LunarDate(year, month, day, False).toSolarDate()
                        interview_first = date(interview_year, interview_month, 1)
                        interview_last = date(interview_year, interview_month, monthrange(interview_year, interview_month)[1])
                        lower, upper = sorted((age_on(birth, interview_first), age_on(birth, interview_last)))
                        route = "lunar_full_date_official_default_interview_day_unknown"
                except (ValueError, IndexError, OverflowError):
                    if outside_lunar_domain:
                        invalid["lunar_date_outside_official_domain"] += 1
                        route = "lunar_date_outside_official_domain"
                    else:
                        invalid["invalid_lunar_calendar_date"] += 1
                        detail = "lunar_day_31" if day == 31 else "lunar_month_day_not_in_calendar_table"
                        invalid_detail[detail] += 1
                        route = "invalid_lunar_calendar_date"
            elif year is not None:
                base = interview_year - year
                if calendar_code == 1 and month is not None and 1 <= month <= 12:
                    if month < interview_month:
                        lower = upper = base
                        route = "solar_month_known_day_missing"
                    elif month > interview_month:
                        lower = upper = base - 1
                        route = "solar_month_known_day_missing"
                    else:
                        lower, upper = max(0, base - 1), base
                        route = "solar_same_month_day_missing_interval"
                else:
                    lower, upper = max(0, base - 1), base
                    route = "partial_or_lunar_date_year_interval"
        elif year is not None and 1900 <= year <= interview_year:
            lower, upper = max(0, interview_year - year - 1), interview_year - year
            route = "calendar_or_date_route_unresolved_year_interval"
        elif (
            reported_age is not None
            and 1 <= reported_age <= 120
            and year is None
            and month is None
            and day is None
            and calendar_code is None
        ):
            lower = upper = reported_age
            route = "conditional_self_reported_age_all_ba002_components_missing"
        else:
            route = "no_valid_birth_year_or_conditional_age"

        if lower is not None and upper is not None and (lower < 0 or upper > 120 or lower > upper):
            lower = upper = None
            route = "age_interval_out_of_range"
            invalid["age_interval_out_of_range"] += 1
        if lower is None:
            domain = "age_unresolved"
        elif lower >= 45:
            domain = "45plus_definite"
        elif upper >= 45:
            domain = "45plus_ambiguous"
        else:
            domain = "below45_definite"
        routes[route] += 1
        age45_status[domain] += 1
        output.append({
            "ID": str(respondent_id).strip(),
            "age_at_interview_lower": lower,
            "age_at_interview_upper": upper,
            "age_route": route,
            "leap_month_ambiguity": int(leap_ambiguity),
            "age45_domain_status_candidate": domain,
        })

    result = pd.DataFrame(output)
    age_dir.mkdir(parents=True, exist_ok=True)
    qa_dir.mkdir(parents=True, exist_ok=True)
    set_private_mode(age_dir, directory=True)
    set_private_mode(qa_dir, directory=True)
    output_path = private_path(age_dir / "wave1_age_interval_candidate.dta", root)
    qa_path = private_path(qa_dir / "wave1_age_interval_candidate_qa.json", root)
    pyreadstat.write_dta(
        result, str(output_path), version=14,
        column_labels=[
            "Protected CHARLS respondent ID; never publish",
            "Candidate lower completed age at interview, not method approved",
            "Candidate upper completed age at interview, not method approved",
            "Source/date route used; candidate only",
            "1 if lunar month could be an unflagged leap month",
            "Candidate 45+ interval classification; not analysis eligibility",
        ],
    )
    set_private_mode(output_path)
    output_sha256 = sha256(output_path)
    report = {
        "scope": "provisional protected age-interval preparation only",
        "source_manifest_id": source_review["source_manifest_id"],
        "age_input_sha256": age_input_hash,
        "person_level_output_sha256": output_sha256,
        "lunardate_014_source_sha256": lunar_source_hash,
        "row_count": int(len(result)),
        "route_counts_private": dict(sorted(routes.items())),
        "age45_interval_status_counts_private": dict(sorted(age45_status.items())),
        "invalid_route_counts_private": dict(sorted(invalid.items())),
        "invalid_detail_counts_private": dict(sorted(invalid_detail.items())),
        "read_only_fields": list(EXPECTED_COLUMNS),
        "interview_day_available": False,
        "separate_leap_month_response_available": False,
        "leap_ambiguous_dates_use_year_interval": True,
        "age_domain_is_not_used_to_filter_rows": True,
        "age_derivation_method_reviewed": False,
        "survey_design_approved": False,
        "association_models_fitted": False,
        "person_level_output_path": output_path.name,
    }
    qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    set_private_mode(qa_path)
    print(json.dumps({
        "scope": report["scope"],
        "row_count": report["row_count"],
        "route_categories": len(routes),
        "age_domain_categories": len(age45_status),
        "age_derivation_method_reviewed": False,
        "survey_design_approved": False,
        "association_models_fitted": False,
        "private_outputs_written": True,
    }, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    derive()
