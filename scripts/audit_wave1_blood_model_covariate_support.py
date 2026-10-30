#!/usr/bin/env python3
"""Private aggregate-only support audit for the Wave 1 blood-model covariates.

Reads only the protected person key, bloodweight, age interval, sex, education,
community key and NBS urban/rural context. It does not read biomarker outcomes,
estimate associations, or write respondent-level rows. Exact category counts
are restricted to the protected server QA directory.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, WAVE_DATA_DIR, require_private_path
from prepare_charls_wave_tables import sha256_file
from require_verified_wave1_frame import require_verified_wave1_frame


ROOT = Path(__file__).resolve().parents[1]
PERSON = WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"
PRIVATE = PRIVATE_ROOT
BLOOD = PRIVATE / "incoming_2011_official" / "Blood_20140429.dta"
PSU = PRIVATE / "incoming_2011_official" / "PSU.dta"
AGE = PRIVATE / "age_inputs_2011" / "wave1_age_interval_candidate.dta"
AGE_QA = PRIVATE / "qa_outputs" / "wave1_age_interval_candidate_qa.json"
DEFAULT_OUTPUT = PRIVATE / "qa_outputs" / "wave1_blood_model_covariate_support_private.json"
PERSON_FIELDS = ("rgender", "bd001")
COMMUNITY_FIELD = "urban_nbs"


def private(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("All participant-derived inputs and QA must remain under the private root")
    return resolved


def normalized_key(values: pd.Series) -> pd.Series:
    result = values.astype("string").str.strip()
    result = result.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return result.str.replace(r"\.0+$", "", regex=True)


def _read(path: Path, fields: list[str]) -> tuple[pd.DataFrame, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required private input is missing: {path.name}")
    frame, metadata = pyreadstat.read_dta(str(path), usecols=fields)
    return frame, metadata


def _category_counts(frame: pd.DataFrame, field: str) -> dict[str, int]:
    values = pd.to_numeric(frame[field], errors="coerce")
    counts = values.value_counts(dropna=False, sort=False)
    result: dict[str, int] = {}
    for value, count in counts.items():
        key = "missing_or_non_numeric" if pd.isna(value) else format(float(value), ".15g")
        result[key] = int(count)
    return dict(sorted(result.items()))


def _field_label_metadata(meta: Any, field: str) -> dict[str, Any]:
    label_name = getattr(meta, "variable_to_label", {}).get(field, "")
    labels = getattr(meta, "value_labels", {}).get(label_name, {}) if label_name else {}
    return {
        "variable_label": getattr(meta, "column_names_to_labels", {}).get(field, ""),
        "value_label_set_attached": bool(label_name),
        "value_label_name": label_name or None,
        "label_map": {str(key): str(value) for key, value in labels.items()},
    }


def run(output_path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    output_path = private(output_path)
    for path in (PERSON, BLOOD, PSU, AGE, AGE_QA):
        private(path)

    provenance = require_verified_wave1_frame(data_path=PERSON)
    age_qa = json.loads(AGE_QA.read_text(encoding="utf-8"))
    if age_qa.get("source_manifest_id") != provenance["source_manifest_id"]:
        raise ValueError("Age interval candidate is not bound to the verified source manifest")
    if age_qa.get("person_level_output_sha256") != sha256_file(AGE):
        raise ValueError("Age interval output hash does not match its private QA record")
    if age_qa.get("age_derivation_method_reviewed") is not False:
        raise ValueError("This preflight accepts only an explicitly provisional age candidate")

    person, person_meta = _read(PERSON, ["ID", "communityID", *PERSON_FIELDS])
    blood, _ = _read(BLOOD, ["ID", "bloodweight"])
    psu, psu_meta = _read(PSU, ["communityID", COMMUNITY_FIELD])
    age, _ = _read(AGE, ["ID", "age_at_interview_lower", "age_at_interview_upper"])

    for frame, name in ((person, "prepared person table"), (blood, "Blood release"), (age, "age candidate")):
        frame["_key"] = normalized_key(frame["ID"])
        if frame["_key"].isna().any() or frame["_key"].duplicated().any():
            raise ValueError(f"{name} key must be complete and unique")
    person["_community_key"] = normalized_key(person["communityID"])
    psu["_community_key"] = normalized_key(psu["communityID"])
    if psu["_community_key"].isna().any() or psu["_community_key"].duplicated().any():
        raise ValueError("PSU community key must be complete and unique")

    joined = blood[["_key", "bloodweight"]].merge(
        person[["_key", "_community_key", *PERSON_FIELDS]],
        on="_key", how="left", validate="1:1", indicator="_person_link",
    )
    if not joined["_person_link"].eq("both").all():
        raise ValueError("Blood respondents do not all map to the protected person table")
    joined = joined.drop(columns="_person_link").merge(
        psu[["_community_key", COMMUNITY_FIELD]],
        on="_community_key", how="left", validate="m:1", indicator="_psu_link",
    )
    if not joined["_psu_link"].eq("both").all():
        raise ValueError("Blood respondents do not all map to the official PSU/community file")
    joined = joined.drop(columns="_psu_link").merge(
        age[["_key", "age_at_interview_lower", "age_at_interview_upper"]],
        on="_key", how="left", validate="1:1", indicator="_age_link",
    )
    if not joined["_age_link"].eq("both").all():
        raise ValueError("Blood respondents do not all map to the provisional age interval file")

    weight = pd.to_numeric(joined["bloodweight"], errors="coerce")
    positive = weight.notna() & weight.map(lambda value: math.isfinite(float(value)) if pd.notna(value) else False) & weight.gt(0)
    if not positive.any():
        raise ValueError("No finite positive-bloodweight Blood respondents were found")
    joined = joined.loc[positive].copy()
    lower = pd.to_numeric(joined["age_at_interview_lower"], errors="coerce")
    domains = {
        "observed_positive_bloodweight_blood_sample": joined,
        "primary_candidate_lower_age_bound_45plus": joined.loc[lower.ge(45)],
    }

    result: dict[str, Any] = {
        "audit_type": "private aggregate-only Wave 1 model-covariate support preflight",
        "audit_utc": datetime.now(timezone.utc).isoformat(),
        "source_manifest_id": provenance["source_manifest_id"],
        "prepared_person_sha256": sha256_file(PERSON),
        "blood_source_sha256": sha256_file(BLOOD),
        "psu_source_sha256": sha256_file(PSU),
        "age_candidate_sha256": sha256_file(AGE),
        "target_population_count_is_not_model_n": True,
        "respondent_level_rows_written": False,
        "biomarker_outcomes_read": False,
        "associations_estimated": False,
        "domains_are_support_diagnostics_not_approved_model_n": True,
        "fields": {
            "sex_candidate": {"field": "rgender", **_field_label_metadata(person_meta, "rgender")},
            "education_candidate": {"field": "bd001", **_field_label_metadata(person_meta, "bd001")},
            "community_context_candidate": {"field": "urban_nbs", **_field_label_metadata(psu_meta, "urban_nbs")},
        },
        "domain_support": {},
    }
    for domain_name, frame in domains.items():
        result["domain_support"][domain_name] = {
            "support_records_private": int(len(frame)),
            "community_clusters_private": int(frame["_community_key"].nunique(dropna=True)),
            "covariate_categories_private": {
                field: _category_counts(frame, field) for field in (*PERSON_FIELDS, COMMUNITY_FIELD)
            },
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(output_path, 0o600)
    return {"status": "completed_private_aggregate_only", "output": str(output_path.name)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Wave 1 blood-model covariate support without fitting associations.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
