"""Validate respondent community IDs against a protected CHARLS PSU-map candidate.

Reads respondent-level files locally but writes only wave-level aggregate QA.
This establishes key coverage only; it does not authenticate the source release
or verify a complete survey variance design.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path

import pandas as pd
import pyreadstat
from project_paths import QA_OUTPUT_DIR, require_private_path

PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = require_private_path(Path(os.environ.get("LOCALAPPDATA", ".")) / "CHARLS_ExWAS_Atlas" / "derived_wave_tables")
DEFAULT_PSU_FILE = require_private_path(
    Path(os.environ.get("LOCALAPPDATA", ".")) / "CHARLS_ExWAS_Atlas" / "raw_extract_2011_community" / "psu.dta"
)
WAVES = (2011, 2013, 2015, 2018, 2020)


def normalize_codes(values: pd.Series) -> pd.Series:
    return (values.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
            .replace({"": pd.NA, "<NA>": pd.NA, "nan": pd.NA}))


def read_psu_map_candidate(path: Path) -> pd.DataFrame:
    path = require_private_path(path)
    mapping, _ = pyreadstat.read_dta(str(path), usecols=["communityID", "province", "city", "urban_nbs", "areatype"])
    required = {"communityID", "province", "city", "urban_nbs", "areatype"}
    if not required.issubset(mapping.columns):
        raise ValueError(f"PSU-map candidate lacks expected fields: {required - set(mapping.columns)}")
    mapping["community_key"] = normalize_codes(mapping["communityID"])
    if mapping["community_key"].isna().any() or mapping["community_key"].duplicated().any():
        raise ValueError("PSU-map candidate must have one nonmissing row per communityID")
    # Check whether each community identifier maps to one geography tuple.
    return mapping


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--psu-file", type=Path, default=DEFAULT_PSU_FILE,
                    help="Protected local PSU.dta candidate; exact official archive identity must be verified separately")
    ap.add_argument("--out", type=Path, default=QA_OUTPUT_DIR / "charls_psu_mapping_aggregate_v1.csv")
    args = ap.parse_args()
    args.data_dir = require_private_path(args.data_dir)
    args.psu_file = require_private_path(args.psu_file)
    args.out = require_private_path(args.out)
    psu = read_psu_map_candidate(args.psu_file)
    psu_keys = set(psu["community_key"].dropna())
    rows = []
    for wave in WAVES:
        path = args.data_dir / f"CHARLS_wave{wave}_person_analytic.dta"
        people, _ = pyreadstat.read_dta(str(path), usecols=["communityID"])
        community = normalize_codes(people["communityID"])
        seen = set(community.dropna())
        rows.append({
            "wave": wave,
            "respondent_rows": len(people),
            "community_id_nonmissing_n": int(community.notna().sum()),
            "unique_community_ids_n": len(seen),
            "unique_ids_in_official_psu_map_n": len(seen & psu_keys),
            "unmatched_unique_community_ids_n": len(seen - psu_keys),
            "respondents_with_mapped_community_n": int(community.isin(psu_keys).sum()),
            "respondents_with_unmapped_community_n": int((community.notna() & ~community.isin(psu_keys)).sum()),
            "official_psu_map_rows": len(psu),
            "psu_map_source_identity": "not_independently_verified_against_original_release_archive",
            "status": "aggregate_key_coverage_only_not_variance_design_validation",
        })
    result = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
