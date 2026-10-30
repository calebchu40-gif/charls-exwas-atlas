#!/usr/bin/env python3
"""Private aggregate-only cluster-support audit for the Wave 1 blood frame.

Reads only participant keys, released blood weights and the reviewed age
interval candidate. It writes no row-level data and estimates no associations.
All output must remain under CHARLS_EXWAS_PRIVATE_ROOT. The county-prefix
summary is a structural sensitivity only; it is not an approved first-stage
PSU mapping or a variance estimator.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path
from prepare_charls_wave_tables import sha256_file
from require_verified_wave1_frame import require_verified_wave1_frame


PRIVATE = PRIVATE_ROOT
PERSON = PRIVATE / "derived_wave_tables" / "CHARLS_wave2011_person_analytic.dta"
BLOOD = PRIVATE / "incoming_2011_official" / "Blood_20140429.dta"
PSU = PRIVATE / "incoming_2011_official" / "PSU.dta"
AGE = PRIVATE / "age_inputs_2011" / "wave1_age_interval_candidate.dta"
AGE_QA = PRIVATE / "qa_outputs" / "wave1_age_interval_candidate_qa.json"
DEFAULT_OUTPUT = PRIVATE / "qa_outputs" / "wave1_design_cluster_support_private.json"


def _private(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("All participant-derived inputs and QA must remain under the protected private root")
    return resolved


def _read(path: Path, fields: list[str]) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Required protected input is missing: {path.name}")
    frame, _ = pyreadstat.read_dta(str(path), usecols=fields)
    return frame


def _key(values: pd.Series) -> pd.Series:
    result = values.astype("string").str.strip()
    result = result.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return result.str.replace(r"\.0+$", "", regex=True)


def _cluster_summary(frame: pd.DataFrame, cluster: str, weight: pd.Series) -> dict[str, Any]:
    usable = frame[cluster].notna()
    work = frame.loc[usable, [cluster]].copy()
    w = pd.to_numeric(weight.loc[usable], errors="coerce").to_numpy(dtype=float)
    if len(work) == 0 or not np.isfinite(w).all() or (w <= 0).any():
        raise ValueError(f"Invalid positive-weight cluster support for {cluster}")
    sizes = work.groupby(cluster, dropna=False).size()
    total_weight = float(w.sum())
    weight_cv = float(w.std(ddof=1) / w.mean()) if len(w) > 1 else None
    kish = total_weight**2 / float(np.square(w).sum())
    return {
        "records": int(len(work)),
        "clusters": int(len(sizes)),
        "clusters_with_one_observed_record": int((sizes == 1).sum()),
        "clusters_with_two_or_more_observed_records": int((sizes >= 2).sum()),
        "minimum_records_per_cluster": int(sizes.min()),
        "maximum_records_per_cluster": int(sizes.max()),
        "wr_one_stage_reference_df_clusters_minus_one": max(int(len(sizes)) - 1, 0),
        "weight_sum_private": total_weight,
        "weight_cv_private": weight_cv,
        "kish_weight_effective_n_private": float(kish),
    }


def audit(output_path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    output_path = _private(output_path)
    for path in (PERSON, BLOOD, PSU, AGE, AGE_QA):
        _private(path)
    provenance = require_verified_wave1_frame(data_path=PERSON)
    age_qa = json.loads(AGE_QA.read_text(encoding="utf-8"))
    age_hash = sha256_file(AGE)
    if age_qa.get("source_manifest_id") != provenance["source_manifest_id"]:
        raise ValueError("Age interval candidate and prepared frame have different source manifests")
    if age_qa.get("person_level_output_sha256") != age_hash:
        raise ValueError("Age interval candidate hash does not match its protected QA manifest")

    person = _read(PERSON, ["ID", "communityID"])
    blood = _read(BLOOD, ["ID", "bloodweight"])
    age = _read(AGE, ["ID", "age_at_interview_lower", "age_at_interview_upper"])
    psu = _read(PSU, ["communityID"])
    for frame, label in ((person, "prepared person"), (blood, "Blood"), (age, "age candidate")):
        frame["_key"] = _key(frame["ID"])
        if frame["_key"].isna().any() or frame["_key"].duplicated().any():
            raise ValueError(f"{label} person key is missing or duplicated")
    psu["_community"] = _key(psu["communityID"])
    if psu["_community"].isna().any() or psu["_community"].duplicated().any():
        raise ValueError("Official PSU community key is missing or duplicated")

    merged = blood[["_key", "bloodweight"]].merge(
        person[["_key", "communityID"]], on="_key", how="left", validate="1:1", indicator="_person_link"
    )
    if not merged["_person_link"].eq("both").all():
        raise ValueError("A released Blood record does not map to the prepared person frame")
    merged = merged.drop(columns="_person_link").merge(
        age[["_key", "age_at_interview_lower", "age_at_interview_upper"]],
        on="_key", how="left", validate="1:1", indicator="_age_link",
    )
    if not merged["_age_link"].eq("both").all():
        raise ValueError("A released Blood record does not map to the age interval candidate")
    merged["_community"] = _key(merged["communityID"])
    official_communities = set(psu["_community"])
    unmatched = int((~merged["_community"].isin(official_communities)).sum())
    if unmatched:
        raise ValueError("Blood respondents include community keys absent from the official PSU file")

    merged["_weight"] = pd.to_numeric(merged["bloodweight"], errors="coerce")
    observed = merged.loc[np.isfinite(merged["_weight"]) & (merged["_weight"] > 0)].copy()
    lo = pd.to_numeric(observed["age_at_interview_lower"], errors="coerce")
    hi = pd.to_numeric(observed["age_at_interview_upper"], errors="coerce")
    observed["_county_prefix_candidate"] = observed["_key"].str.slice(0, 6)
    if observed["_county_prefix_candidate"].isna().any() or (observed["_county_prefix_candidate"].str.len() != 6).any():
        raise ValueError("Person keys do not support the documented six-character county-code grouping")

    domains = {
        "observed_positive_bloodweight_all": observed,
        "age_lower_bound_at_least_45": observed.loc[lo >= 45],
        "age_upper_bound_at_least_45": observed.loc[hi >= 45],
    }
    result: dict[str, Any] = {
        "audit_utc": datetime.now(timezone.utc).isoformat(),
        "audit_type": "private aggregate-only cluster support; no outcome data or associations",
        "source_identity_status": provenance["source_identity_status"],
        "source_manifest_id": provenance["source_manifest_id"],
        "input_sha256": {
            "prepared_person": sha256_file(PERSON),
            "blood": sha256_file(BLOOD),
            "psu": sha256_file(PSU),
            "age_interval_candidate": age_hash,
        },
        "blood_records_unlinked_to_prepared_person": 0,
        "blood_records_unlinked_to_official_psu_community": unmatched,
        "domains_are_diagnostics_not_approved_model_n": True,
        "county_prefix_is_confirmed_first_stage_psu": False,
        "cluster_support": {},
        "limitations": [
            "Counts describe released blood records with finite positive bloodweight and the supplied provisional age candidate; they are not approved model N.",
            "A one-record community in an analysis domain is reported as support information; it is not, by itself, a survey singleton-PSU variance rule.",
            "The county-prefix grouping is a structural sensitivity candidate only and does not recover the original sampling PSU, implicit strata, PPS size measures, or final split-community map.",
            "Weight CV and Kish effective N are descriptive diagnostics and do not replace design-based variance or a methods review.",
        ],
    }
    for domain_name, frame in domains.items():
        weights = frame["_weight"]
        result["cluster_support"][domain_name] = {
            "communityID_candidate": _cluster_summary(frame, "_community", weights),
            "county_prefix_sensitivity_candidate": _cluster_summary(frame, "_county_prefix_candidate", weights),
        }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_path.chmod(0o600)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit(args.output)
    print("Wave 1 cluster-support diagnostic completed; detailed aggregates remain private.")


if __name__ == "__main__":
    main()
