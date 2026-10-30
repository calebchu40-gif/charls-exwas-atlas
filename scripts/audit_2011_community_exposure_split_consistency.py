"""Protected, aggregate-only audit of community-exposure consistency at split PSUs.

Reads only the Wave 1 community module and public candidate-field catalog.
Writes field-code summaries only to the access-controlled local QA directory.
No respondent spine, blood outcomes, person IDs, community IDs, or source values
are written to the report or printed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path


ROOT = Path(__file__).resolve().parents[1]
COMMUNITY = PRIVATE_ROOT / "raw_extract_2011_community" / "community.dta"
CATALOG = ROOT / "audit" / "charls_atlas_candidate_fields_v0.csv"
PRIOR_KEY_AUDIT = QA_OUTPUT_DIR / "community_2011_linkage_audit.json"
OUTPUT = QA_OUTPUT_DIR / "community_exposure_split_consistency_v1.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exposure_codes() -> list[str]:
    catalog = pd.read_csv(CATALOG, dtype=str, encoding="utf-8-sig").fillna("")
    mask = (
        catalog["Source.Wave"].eq("2011")
        & catalog["Data.File.Name"].str.casefold().eq("community")
        & catalog["epcf"].apply(
            lambda value: "e" in {part.strip().casefold() for part in value.split(",")}
        )
    )
    return sorted(set(catalog.loc[mask, "Variable.Name"].str.strip().dropna()))


def normalized_values(series: pd.Series) -> set[str]:
    values = series.astype("string").str.strip()
    return {"<MISSING>" if pd.isna(value) or value == "" else str(value) for value in values}


def main() -> None:
    community_path = require_private_path(COMMUNITY)
    output_path = require_private_path(OUTPUT)
    if not community_path.is_file() or not CATALOG.is_file() or not PRIOR_KEY_AUDIT.is_file():
        raise FileNotFoundError("community source, public catalog, or prior private key audit is missing")

    prior = json.loads(PRIOR_KEY_AUDIT.read_text(encoding="utf-8"))
    source_hash = sha256(community_path)
    if source_hash != prior.get("community_source_sha256"):
        raise ValueError("community source differs from the previously source-bound key audit")

    codes = exposure_codes()
    _, metadata = pyreadstat.read_dta(str(community_path), metadataonly=True)
    columns = {name.casefold(): name for name in metadata.column_names}
    if not {"communityid", "sub_commuid"}.issubset(columns):
        raise ValueError("community source lacks expected parent/sub-community keys")
    available = [code for code in codes if code.casefold() in columns]
    if len(available) != len(codes):
        raise ValueError("one or more catalogued community exposure fields are absent from source")

    selected = [columns["communityid"], columns["sub_commuid"]]
    selected.extend(columns[code.casefold()] for code in available)
    data, _ = pyreadstat.read_dta(str(community_path), usecols=list(dict.fromkeys(selected)))
    parent = data[columns["communityid"]].astype("string").str.strip()
    sub = data[columns["sub_commuid"]].astype("string").str.strip()
    parent = parent.mask(parent.eq(""))
    sub = sub.mask(sub.eq(""))
    rows_per_parent = parent.dropna().value_counts()
    split_parents = set(rows_per_parent[rows_per_parent.gt(1)].index)
    if not split_parents:
        raise ValueError("expected split-parent records were not found; review source assumptions")

    split_rows = data.loc[parent.isin(split_parents)].copy()
    split_rows["__parent"] = parent.loc[split_rows.index]
    per_field: list[dict[str, object]] = []
    for code in available:
        column = columns[code.casefold()]
        statuses: list[str] = []
        for _, group in split_rows.groupby("__parent", sort=False, dropna=True):
            values = normalized_values(group[column])
            if len(values) > 1:
                statuses.append("conflicting_values_or_missingness")
            elif values == {"<MISSING>"}:
                statuses.append("uniformly_missing")
            else:
                statuses.append("uniform_nonmissing_value")
        per_field.append(
            {
                "field_code": code,
                "split_parent_groups_conflicting": statuses.count("conflicting_values_or_missingness"),
                "split_parent_groups_uniform_nonmissing": statuses.count("uniform_nonmissing_value"),
                "split_parent_groups_uniformly_missing": statuses.count("uniformly_missing"),
                "parent_aggregation_candidate": (
                    "not_ambiguous_by_value_consistency_only"
                    if "conflicting_values_or_missingness" not in statuses
                    and "uniform_nonmissing_value" in statuses
                    else "not_supported"
                ),
            }
        )

    output = {
        "audit_type": "protected_aggregate_community_exposure_split_consistency",
        "source_role": "official CHARLS Wave 1 Community module",
        "source_sha256_matches_prior_key_audit": True,
        "respondent_or_blood_data_read": False,
        "identifiers_or_source_values_written": False,
        "candidate_exposure_field_count": len(available),
        "split_parent_group_count": len(split_parents),
        "split_parent_row_count": int(len(split_rows)),
        "subcommunity_key_nonmissing_split_rows": int(sub.loc[split_rows.index].notna().sum()),
        "field_results": per_field,
        "interpretation": (
            "Uniform values only identify fields that are not ambiguous by observed value consistency; "
            "this does not establish measurement validity, sub-PSU respondent membership, survey weights, "
            "variance validity, or permission to fit/release an association."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    counts: dict[str, int] = {}
    for row in per_field:
        label = str(row["parent_aggregation_candidate"])
        counts[label] = counts.get(label, 0) + 1
    print(
        "status=aggregate_only_completed "
        f"candidate_fields={len(available)} "
        f"split_parent_groups={len(split_parents)} "
        f"field_status_counts={counts} "
        f"report={output_path}"
    )


if __name__ == "__main__":
    main()
