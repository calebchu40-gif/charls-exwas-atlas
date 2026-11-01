"""Construct source-documented CHARLS county-stage cluster keys.

CHARLS 2011 documentation describes the county and community segments in
household identifiers. The helper validates that relationship against the
released community identifier before exposing a county cluster key. It does
not infer or construct variance strata.
"""
from __future__ import annotations

import polars as pl


def add_documented_county_cluster(
    frame: pl.DataFrame,
    *,
    household_id: str = "householdID",
    community_id: str = "communityID",
    output: str = "__county_psu",
) -> pl.DataFrame:
    missing = {household_id, community_id} - set(frame.columns)
    if missing:
        raise ValueError(f"Cannot construct documented county cluster; fields missing: {sorted(missing)}")
    keyed = frame.with_columns(
        pl.col(household_id).cast(pl.String).str.replace(r"\.0+$", "").alias("__hhid_digits"),
        pl.col(community_id).cast(pl.String).str.replace(r"\.0+$", "").alias("__community_digits"),
    )
    invalid = keyed.filter(
        pl.col("__hhid_digits").is_null()
        | ~pl.col("__hhid_digits").str.contains(r"^\d{7,}$")
        | pl.col("__community_digits").is_null()
        | ~pl.col("__community_digits").str.contains(r"^\d{7}$")
        | (pl.col("__hhid_digits").str.slice(0, 7) != pl.col("__community_digits"))
    )
    if invalid.height:
        raise ValueError(
            "Released household/community IDs do not satisfy the officially documented "
            "county/community segment relationship; refusing county-stage analysis"
        )
    return keyed.with_columns(
        pl.col("__hhid_digits").str.slice(0, 6).alias(output)
    ).drop("__hhid_digits", "__community_digits")
