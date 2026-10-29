"""Audit the Wave 1 county-unit prefix encoded in CHARLS identifiers.

The official 2011 Users' Guide says the first six digits of the household ID
distinguish county-level units and that the first seven digits identify the
community. This script validates that published coding rule against the
protected Wave 1 person, community, and PSU files. It writes aggregate-only QA
to private storage and never prints or exports identifiers or row-level data.

Passing this key audit does not recover implicit strata, exact first-stage
selection probabilities, or respondent-to-subcommunity PSU membership, and
does not itself approve a variance estimator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path


DEFAULT_PERSON = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
DEFAULT_PSU = PRIVATE_ROOT / "incoming_2011_official" / "PSU.dta"
DEFAULT_MANIFEST = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "prepared_data_manifest.json"
DEFAULT_INTAKE_MANIFEST = PRIVATE_ROOT / "incoming_2011_official" / "intake_manifest.json"
DEFAULT_OUTPUT = PRIVATE_ROOT / "qa_outputs" / "wave1_county_prefix_design_candidate.json"


def norm(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.replace(r"\.0$", "", regex=True).replace({"": pd.NA, "<NA>": pd.NA, "nan": pd.NA})


def id_shape(series: pd.Series, width: int) -> pd.Series:
    clean = norm(series)
    return clean.where(clean.str.fullmatch(rf"\d{{{width}}}", na=False))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--person", type=Path, default=DEFAULT_PERSON)
    parser.add_argument("--psu", type=Path, default=DEFAULT_PSU)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--intake-manifest", type=Path, default=DEFAULT_INTAKE_MANIFEST)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    for name in ("person", "psu", "manifest", "intake_manifest", "out"):
        setattr(args, name, require_private_path(getattr(args, name)))

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    intake = json.loads(args.intake_manifest.read_text(encoding="utf-8"))
    wave = next((item for item in manifest.get("waves", []) if str(item.get("wave")) == "2011"), None)
    if not wave or int(wave.get("rows", 0)) <= 0 or int(wave.get("columns", 0)) <= 0:
        raise ValueError("Prepared Wave 1 manifest is missing or invalid")
    if wave.get("source_review", {}).get("source_identity_status") != "verified_official_source":
        raise ValueError("Prepared Wave 1 source identity is not verified")
    person_hash = sha256_file(args.person)
    if person_hash != wave.get("prepared_output", {}).get("sha256"):
        raise ValueError("Prepared Wave 1 respondent table does not match its manifest hash")
    psu_hash = sha256_file(args.psu)
    psu_entry = next((item for item in intake.get("required_files", []) if item.get("role") == "psu"), None)
    if not psu_entry or psu_entry.get("identity_review_status") != "verified_official_source" or psu_hash != psu_entry.get("reviewed_local_sha256"):
        raise ValueError("PSU source does not match the reviewed official intake manifest")

    _, person_meta = pyreadstat.read_dta(str(args.person), metadataonly=True)
    people, _ = pyreadstat.read_dta(str(args.person), usecols=["ID", "householdID", "communityID"])
    psu, _ = pyreadstat.read_dta(str(args.psu), usecols=["communityID"])
    if len(people) != int(wave["rows"]) or person_meta.number_columns != int(wave["columns"]):
        raise ValueError("Prepared Wave 1 table does not match its manifest dimensions")

    people["person_key"] = id_shape(people["ID"], 11)
    people["household_key"] = id_shape(people["householdID"], 9)
    people["community_key"] = id_shape(people["communityID"], 7)
    psu["community_key"] = id_shape(psu["communityID"], 7)

    person_county = people["person_key"].str[:6]
    household_county = people["household_key"].str[:6]
    community_county = people["community_key"].str[:6]
    psu_county = psu["community_key"].str[:6]

    person_communities = set(people["community_key"].dropna())
    psu_communities = set(psu["community_key"].dropna())
    county_sizes = psu.dropna(subset=["community_key"]).groupby(psu_county.dropna()).community_key.nunique()

    report = {
        "audit_type": "protected_aggregate_identifier_prefix_consistency",
        "source": "CHARLS 2011 official release and Users Guide identifier rules",
        "source_identity_verified": True,
        "prepared_person_hash_matches_manifest": True,
        "official_psu_hash_matches_reviewed_intake": True,
        "person_rows": int(len(people)),
        "person_id_shape_valid_rows": int(people["person_key"].notna().sum()),
        "household_id_shape_valid_rows": int(people["household_key"].notna().sum()),
        "community_id_shape_valid_rows": int(people["community_key"].notna().sum()),
        "person_household_county_prefix_match": bool((person_county == household_county).fillna(False).all()),
        "person_community_county_prefix_match": bool((person_county == community_county).fillna(False).all()),
        "respondent_community_keys_match_official_psu_map": person_communities == psu_communities,
        "psu_community_key_shape_valid_rows": int(psu["community_key"].notna().sum()),
        "county_prefix_candidate_count_private": int(psu_county.nunique(dropna=True)),
        "communities_per_county_min_private": int(county_sizes.min()) if len(county_sizes) else None,
        "communities_per_county_max_private": int(county_sizes.max()) if len(county_sizes) else None,
        "psu_rows_with_valid_community_key": int(psu["community_key"].notna().sum()),
        "subcommunity_crosswalk_to_respondents_available": False,
        "implicit_strata_reconstructed": False,
        "variance_estimator_approved": False,
        "association_models_authorized": False,
    }
    report["candidate_key_audit_status"] = (
        "prefix_consistency_pass_needs_independent_design_review"
        if all((report["person_household_county_prefix_match"],
                report["person_community_county_prefix_match"],
                report["respondent_community_keys_match_official_psu_map"]))
        else "prefix_consistency_failed"
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"status={report['candidate_key_audit_status']}; output=protected aggregate QA; no identifiers emitted")


if __name__ == "__main__":
    main()
