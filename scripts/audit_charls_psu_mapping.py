"""Validate respondent community IDs against the official CHARLS PSU map.

Reads respondent-level files locally but writes only wave-level aggregate QA.
"""
from __future__ import annotations
import argparse
import io
import os
from pathlib import Path
import zipfile

import pandas as pd
import pyreadstat
from project_paths import QA_OUTPUT_DIR, require_private_path

PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = require_private_path(Path(os.environ.get("LOCALAPPDATA", ".")) / "CHARLS_ExWAS_Atlas" / "derived_wave_tables")
DEFAULT_RAW = PROJECT.parent / "charls2011~2020清洗好+原版数据" / "原始数据+问卷2011~2020"
WAVES = (2011, 2013, 2015, 2018, 2020)


def normalize_codes(values: pd.Series) -> pd.Series:
    return (values.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
            .replace({"": pd.NA, "<NA>": pd.NA, "nan": pd.NA}))


def read_official_psu_map(raw_root: Path) -> pd.DataFrame:
    archive = raw_root / "2013" / "CHARLS2013_Dataset.zip"
    with zipfile.ZipFile(archive) as zf:
        payload = io.BytesIO(zf.read("PSU.dta"))
        mapping, _ = pyreadstat.read_dta(payload)
    required = {"communityID", "province", "city", "urban_nbs", "areatype"}
    if not required.issubset(mapping.columns):
        raise ValueError(f"Official PSU map lacks expected fields: {required - set(mapping.columns)}")
    mapping["community_key"] = normalize_codes(mapping["communityID"])
    if mapping["community_key"].isna().any() or mapping["community_key"].duplicated().any():
        raise ValueError("Official PSU mapping must have one nonmissing row per communityID")
    # Check whether each public community identifier maps to one geography tuple.
    return mapping


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--raw-root", type=Path, default=DEFAULT_RAW)
    ap.add_argument("--out", type=Path, default=QA_OUTPUT_DIR / "charls_psu_mapping_aggregate_v1.csv")
    args = ap.parse_args()
    args.data_dir = require_private_path(args.data_dir)
    args.out = require_private_path(args.out)
    psu = read_official_psu_map(args.raw_root)
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
            "status": "aggregate_key_coverage_only_not_variance_design_validation",
        })
    result = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
