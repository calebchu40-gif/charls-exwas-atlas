"""Audit whether 2011 community candidates can be linked by communityID.

The audit reads only community-level source fields and the communityID key from
the protected respondent table. It writes aggregate QA to a private local path;
it never writes or prints IDs, source values, or row-level records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, WAVE_DATA_DIR, require_private_path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMMUNITY_FILE = PRIVATE_ROOT / "raw_extract_2011_community" / "community.dta"
DEFAULT_PERSON_FILE = WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"
DEFAULT_OUTPUT = PRIVATE_ROOT / "qa_outputs" / "community_2011_linkage_audit.json"
CATALOG = ROOT / "audit" / "charls_atlas_candidate_fields_v0.csv"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _norm_key(values: pd.Series) -> pd.Series:
    result = values.astype("string").str.strip()
    return result.mask(result.eq(""))


def summarize_linkage(
    community: pd.DataFrame,
    persons: pd.DataFrame,
    candidate_codes: list[str],
) -> dict[str, object]:
    """Return disclosure-safe key and source-field counts for a synthetic or private QA."""
    required = {"communityID", "sub_commuID"}
    missing_required = sorted(required - set(community.columns))
    if "communityID" not in persons.columns:
        raise ValueError("respondent table must contain communityID")
    if missing_required:
        raise ValueError(f"community table is missing required key columns: {missing_required}")

    comm_key = _norm_key(community["communityID"])
    person_key = _norm_key(persons["communityID"])
    key_counts = comm_key.dropna().value_counts()
    repeated_keys = set(key_counts[key_counts.gt(1)].index)
    repeated_rows = int(comm_key.isin(repeated_keys).sum())
    community_keys = set(comm_key.dropna())
    person_keys = set(person_key.dropna())
    matched_person_keys = person_keys & community_keys

    available_codes = {str(column).casefold(): str(column) for column in community.columns}
    matched_codes = [code for code in candidate_codes if code.casefold() in available_codes]
    mismatched_fields: list[str] = []
    if repeated_keys:
        repeated = community.loc[comm_key.isin(repeated_keys)].copy()
        repeated["__normalized_key"] = comm_key.loc[repeated.index]
        for code in matched_codes:
            actual_column = available_codes[code.casefold()]
            differs = False
            for _, group in repeated.groupby("__normalized_key", dropna=False, sort=False):
                values = group[actual_column].astype("string").fillna("<MISSING>")
                if values.nunique(dropna=False) > 1:
                    differs = True
                    break
            if differs:
                mismatched_fields.append(code)

    repeated_subcommunity_ids = 0
    if repeated_keys:
        repeated = community.loc[comm_key.isin(repeated_keys)].copy()
        repeated["__normalized_key"] = comm_key.loc[repeated.index]
        for _, group in repeated.groupby("__normalized_key", dropna=False, sort=False):
            subkeys = _norm_key(group["sub_commuID"])
            if subkeys.notna().any():
                repeated_subcommunity_ids += int(subkeys.nunique(dropna=True))

    status = "blocked_duplicate_community_key" if repeated_keys else "key_structure_pass_needs_source_review"
    return {
        "audit_type": "metadata_and_aggregate_key_coverage_only",
        "community_rows": int(len(community)),
        "community_key_missing_rows": int(comm_key.isna().sum()),
        "community_unique_key_count": int(comm_key.nunique(dropna=True)),
        "community_duplicate_key_groups": int(len(repeated_keys)),
        "community_rows_in_duplicate_key_groups": repeated_rows,
        "distinct_subcommunity_keys_within_duplicate_groups": repeated_subcommunity_ids,
        "respondent_rows": int(len(persons)),
        "respondent_community_key_missing_rows": int(person_key.isna().sum()),
        "respondent_unique_community_key_count": int(len(person_keys)),
        "respondent_community_key_match_rate": (
            len(matched_person_keys) / len(person_keys) if person_keys else None
        ),
        "respondent_table_has_sub_commuID": any(
            str(column).casefold() == "sub_commuid" for column in persons.columns
        ),
        "candidate_code_count": int(len(candidate_codes)),
        "candidate_codes_found_in_community_file": int(len(matched_codes)),
        "candidate_codes_missing_from_community_file": int(len(candidate_codes) - len(matched_codes)),
        "candidate_fields_varying_within_duplicate_community_keys": int(len(mismatched_fields)),
        "candidate_field_names_varying_within_duplicate_keys": sorted(mismatched_fields),
        "linkage_status": status,
        "merge_authorized_by_this_audit": False,
        "interpretation": (
            "communityID alone is not a safe many-to-one key while duplicate community records exist; "
            "do not deduplicate or merge until the release-specific respondent-to-subcommunity mapping "
            "and source archive identity are verified"
            if repeated_keys else
            "unique communityID structure is only a key check; source identity, target population, "
            "eligibility, weights, and variance design still require separate review"
        ),
        "privacy": "aggregate-only private QA; no participant/community IDs or source values are emitted",
    }


def candidate_2011_community_exposure_codes(path: Path = CATALOG) -> list[str]:
    catalog = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    mask = (
        catalog["Source.Wave"].eq("2011")
        & catalog["Data.File.Name"].str.casefold().eq("community")
        & catalog["epcf"].apply(lambda value: "e" in {part.strip().casefold() for part in value.split(",")})
    )
    return sorted(set(catalog.loc[mask, "Variable.Name"].str.strip()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--community-file", type=Path, default=DEFAULT_COMMUNITY_FILE)
    parser.add_argument("--person-file", type=Path, default=DEFAULT_PERSON_FILE)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    community_path = require_private_path(args.community_file)
    person_path = require_private_path(args.person_file)
    output_path = require_private_path(args.output)
    if not community_path.is_file() or not person_path.is_file():
        raise FileNotFoundError("required private community or respondent file is missing")

    codes = candidate_2011_community_exposure_codes(args.catalog)
    _, community_meta = pyreadstat.read_dta(str(community_path), metadataonly=True)
    _, person_meta = pyreadstat.read_dta(str(person_path), metadataonly=True)
    community_fields = {field.casefold(): field for field in community_meta.column_names}
    source_columns = [community_fields[key] for key in ("communityid", "sub_commuid") if key in community_fields]
    source_columns += [community_fields[code.casefold()] for code in codes if code.casefold() in community_fields]
    community, _ = pyreadstat.read_dta(str(community_path), usecols=list(dict.fromkeys(source_columns)))
    person_fields = {field.casefold(): field for field in person_meta.column_names}
    if "communityid" not in person_fields:
        raise ValueError("respondent file metadata has no communityID field")
    persons, _ = pyreadstat.read_dta(str(person_path), usecols=[person_fields["communityid"]])

    summary = summarize_linkage(community, persons, codes)
    summary["community_source_sha256"] = sha256_file(community_path)
    summary["respondent_source_sha256"] = sha256_file(person_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"status={summary['linkage_status']} "
        f"community_keys={summary['community_unique_key_count']} "
        f"duplicate_key_groups={summary['community_duplicate_key_groups']} "
        f"candidate_fields_present={summary['candidate_codes_found_in_community_file']}/"
        f"{summary['candidate_code_count']} "
        f"differing_fields_in_duplicate_groups={summary['candidate_fields_varying_within_duplicate_community_keys']} "
        f"report={output_path}"
    )


if __name__ == "__main__":
    main()
