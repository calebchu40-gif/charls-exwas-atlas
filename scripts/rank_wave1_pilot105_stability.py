#!/usr/bin/env python3
"""Rank the pilot-105 hypotheses by cross-variant stability.

A single p-value can hide a signal that only appears under one design choice, or
promote one that disappears under the next. This script scores every
coefficient by how many of the five sensitivity variants (county PSU, no urban,
age/sex only, drop small groups, fasting adjust) keep the sign **and** hold
p < 0.05, then ranks them.

Output is private: it contains coefficients.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))

from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path  # noqa: E402

RESULT_DIR = PRIVATE_ROOT / "results"
MAIN = "wave1_pilot105_main_v1.csv"
VARIANTS = {
    "county_psu": "wave1_pilot105_county_psu_v1.csv",
    "no_urban": "wave1_pilot105_no_urban_v1.csv",
    "age_sex": "wave1_pilot105_age_sex_v1.csv",
    "drop_small": "wave1_pilot105_drop_small_v1.csv",
    "fasting_adjust": "wave1_pilot105_fasting_adjust_v1.csv",
}
FLOAT = ("estimate", "p_value", "q_value_by")


def read(path: Path) -> pl.DataFrame:
    frame = pl.read_csv(path, infer_schema_length=10000)
    return frame.with_columns([pl.col(c).cast(pl.Float64, strict=False) for c in FLOAT])


def score(main: pl.DataFrame, variants: dict[str, pl.DataFrame]) -> pl.DataFrame:
    columns = ["exposure_concept_id", "phenotype_concept_id", "main_estimate", "main_p", "main_q"]
    base = main.select([
        "exposure_concept_id", "phenotype_concept_id",
        pl.col("estimate").alias("main_estimate"),
        pl.col("p_value").alias("main_p"),
        pl.col("q_value_by").alias("main_q"),
    ])
    for name, frame in variants.items():
        base = base.join(
            frame.select(["exposure_concept_id", "phenotype_concept_id",
                          pl.col("estimate").alias(f"{name}_estimate"),
                          pl.col("p_value").alias(f"{name}_p")]),
            on=["exposure_concept_id", "phenotype_concept_id"], how="left")
    rows = []
    for row in base.to_dicts():
        kept = 0
        available = 0
        for name in variants:
            estimate = row.get(f"{name}_estimate")
            p_value = row.get(f"{name}_p")
            if estimate is None or p_value is None:
                continue
            available += 1
            same_sign = (estimate > 0) == (row["main_estimate"] > 0)
            if same_sign and p_value < 0.05:
                kept += 1
        rows.append({
            "exposure_concept_id": row["exposure_concept_id"],
            "phenotype_concept_id": row["phenotype_concept_id"],
            "main_estimate": row["main_estimate"],
            "main_p": row["main_p"],
            "main_q": row["main_q"],
            "variants_available": available,
            "variants_supporting": kept,
            "support_fraction": round(kept / available, 3) if available else 0.0,
        })
    scored = pl.DataFrame(rows).sort(
        ["variants_supporting", "main_p"], descending=[True, False])
    return scored


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected result tables")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected result tables")

    main_table = read(RESULT_DIR / MAIN)
    variants = {}
    for name, filename in VARIANTS.items():
        path = RESULT_DIR / filename
        if path.is_file():
            variants[name] = read(path)
    scored = score(main_table, variants)
    out = require_private_path(RESULT_DIR / "wave1_pilot105_stability_v1.csv")
    if not out.is_relative_to(PRIVATE_ROOT.resolve()):
        parser.error(f"output must stay under {PRIVATE_ROOT}")
    scored.write_csv(out)

    report = {
        "rows": scored.height,
        "variants": list(variants),
        "all_variants_support": scored.filter(
            pl.col("variants_supporting") == pl.col("variants_available")).height,
        "at_least_three": scored.filter(pl.col("variants_supporting") >= 3).height,
        "main_q_below_05": scored.filter(pl.col("main_q") < 0.05).height,
        "top": scored.head(12).to_dicts(),
        "output": str(out),
    }
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_pilot105_stability_v1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("rows", "all_variants_support", "at_least_three",
                                             "main_q_below_05")}, ensure_ascii=False))
    for row in report["top"]:
        print(f'{row["exposure_concept_id"]:<30} {row["phenotype_concept_id"]:<22} '
              f'support={row["variants_supporting"]}/{row["variants_available"]} '
              f'main_p={row["main_p"]:.2e} q={row["main_q"]:.3f}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
