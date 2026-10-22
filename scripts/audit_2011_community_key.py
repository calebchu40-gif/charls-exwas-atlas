"""Aggregate-only audit of the 2011 community module's merge keys."""
from __future__ import annotations
import argparse
import os
from pathlib import Path

import pandas as pd
import pyreadstat

PROJECT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = Path(os.environ.get("LOCALAPPDATA", ".")) / "CHARLS_ExWAS_Atlas"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--community-data", type=Path, default=PRIVATE_ROOT / "raw_extract_2011_community" / "community.dta")
    ap.add_argument("--person-data", type=Path, default=PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2011_person_analytic.dta")
    ap.add_argument("--out", type=Path, default=PROJECT / "audit" / "community_2011_key_aggregate_qa_v1.csv")
    args = ap.parse_args()

    comm, _ = pyreadstat.read_dta(str(args.community_data), usecols=["communityID", "sub_commuID"])
    persons, _ = pyreadstat.read_dta(str(args.person_data), usecols=["communityID"])
    comm_id = comm["communityID"].astype("string").str.strip()
    sub_id = comm["sub_commuID"].astype("string").str.strip()
    person_id = persons["communityID"].astype("string").str.strip()
    by_community = comm.assign(_community=comm_id).groupby("_community", dropna=True).size()
    respondent_by_community = person_id.value_counts(dropna=True)
    multi = by_community[by_community > 1]
    community_set = set(comm_id.dropna())
    person_set = set(person_id.dropna())
    extra_rows = int(sum((count - 1) * respondent_by_community.get(cid, 0)
                         for cid, count in multi.items()))

    metrics = [
        ("community_module_rows", len(comm)),
        ("unique_community_ids_n", int(comm_id.nunique(dropna=True))),
        ("unique_community_subcommunity_keys_n", int(pd.DataFrame({"community": comm_id, "subcommunity": sub_id}).drop_duplicates().shape[0])),
        ("rows_missing_community_id_n", int(comm_id.isna().sum())),
        ("rows_missing_subcommunity_id_n", int(sub_id.isna().sum())),
        ("community_ids_with_multiple_module_rows_n", int(len(multi))),
        ("max_module_rows_per_community", int(by_community.max()) if len(by_community) else 0),
        ("respondent_rows", len(persons)),
        ("unique_person_community_ids_n", int(person_id.nunique(dropna=True))),
        ("person_community_ids_found_in_community_module_n", len(person_set & community_set)),
        ("respondent_rows_on_multirow_community_ids_n", int(person_id.isin(set(multi.index)).sum())),
        ("extra_person_rows_if_joined_on_community_id", extra_rows),
        ("person_file_has_sub_commuID", 0),
    ]
    out = pd.DataFrame([{"wave": 2011, "metric": name, "count": value,
                         "status": "aggregate_key_audit_no_person_rows_written"} for name, value in metrics])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(out[["metric", "count"]].to_string(index=False))


if __name__ == "__main__":
    main()
