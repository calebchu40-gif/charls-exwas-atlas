#!/usr/bin/env python3
"""2015 replication of the cooking-fuel gradient across the fifteen blood markers.

The 2011 gradient test ranked fuels from electric through gas/LPG and marsh gas
to coal, wood and other. This repeats it in the 2015 wave with the same rank,
the 2015 biomarker weight, age from the recorded birth year, sex from the
interview record, and urbanicity and education merged from the 2011 baseline.
Fifteen outcomes form one family, BY correction over K=15.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))

import svy  # noqa: E402
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path  # noqa: E402

TABLE = PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2015_person_analytic_with_official_blood.dta"
BASE2011 = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
OUTPUTS = {
    "blood_wbc": "bl_wbc", "blood_hemoglobin": "bl_hgb", "blood_hematocrit": "bl_hct",
    "blood_mcv": "bl_mcv", "blood_platelets": "bl_plt", "blood_crp": "bl_crp",
    "blood_hba1c": "bl_hbalc", "blood_total_cholesterol": "bl_cho", "blood_hdl": "bl_hdl",
    "blood_ldl": "bl_ldl", "blood_triglycerides": "bl_tg", "blood_bun": "bl_bun",
    "blood_creatinine": "bl_crea", "blood_glucose": "bl_glu", "blood_uric_acid": "bl_ua",
}
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave2015_fuel_gradient_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "wave2015_fuel_gradient_v1.json"


def bh(values: list[float]) -> list[float]:
    order = np.argsort(values)
    n = len(values)
    adjusted = np.empty(n)
    running = 1.0
    for rank in range(n - 1, -1, -1):
        index = order[rank]
        running = min(running, values[index] * n / (rank + 1))
        adjusted[index] = running
    return adjusted.tolist()


def main(argv: list[str] | None = None) -> int:
    import pyreadstat
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected wave tables")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected wave tables")

    columns = ["ID", "i022", "Biomarker_weight", "ba000_w2_3", "ba002_1", "communityID"] + list(OUTPUTS.values())
    table, _ = pyreadstat.read_dta(str(TABLE), usecols=columns, output_format="polars")
    base, _ = pyreadstat.read_dta(str(BASE2011), usecols=["ID", "urban_nbs", "bd001"],
                                  output_format="polars")
    base = base.rename({"ID": "id11"})
    num = lambda name: pl.col(name).cast(pl.Float64, strict=False)  # noqa: E731
    table = table.with_columns(pl.col("ID").cast(pl.String).alias("id_str"))
    table = table.with_columns(
        (pl.col("id_str").str.slice(0, 10) + pl.col("id_str").str.slice(11)).alias("id11"))
    table = table.join(base, on="id11", how="left")
    table = table.with_columns([
        pl.when(num("i022") == 5.0).then(0.0)
          .when(num("i022").is_in([2.0, 4.0])).then(1.0)
          .when(num("i022") == 3.0).then(2.0)
          .when(num("i022").is_in([1.0, 6.0, 7.0])).then(3.0)
          .otherwise(None).alias("rank"),
        pl.when(num("ba002_1").is_between(1900, 2000)).then(2015.0 - num("ba002_1"))
          .otherwise(None).alias("age"),
        pl.when(num("ba000_w2_3") == 2.0).then(1.0)
          .when(num("ba000_w2_3") == 1.0).then(0.0).otherwise(None).alias("female"),
        pl.when(num("urban_nbs") == 1.0).then(1.0)
          .when(num("urban_nbs") == 0.0).then(0.0).otherwise(None).alias("urban"),
        num("bd001").alias("edu"),
        num("Biomarker_weight").alias("wgt"),
    ]).with_columns([
        (pl.col("age") - 60).alias("age_c"),
        ((pl.col("age") - 60) ** 2).alias("age_c2"),
        pl.when(pl.col("edu").is_in([1.0, 2.0, 3.0])).then(0.0)
          .when(pl.col("edu").is_in([4.0, 5.0])).then(1.0)
          .when(pl.col("edu").is_in([6.0, 7.0, 8.0])).then(2.0)
          .when(pl.col("edu").is_in([9.0, 10.0, 11.0])).then(3.0)
          .otherwise(None).alias("edu_group"),
    ]).with_columns([
        (pl.col("edu_group") == 1).cast(pl.Float64).alias("edu_2"),
        (pl.col("edu_group") == 2).cast(pl.Float64).alias("edu_3"),
        (pl.col("edu_group") == 3).cast(pl.Float64).alias("edu_4"),
    ])
    table = table.filter((pl.col("age") >= 45) & (pl.col("wgt") > 0))

    covariates = ["age_c", "age_c2", "female", "urban", "edu_2", "edu_3", "edu_4"]
    rows = []
    for concept, field in OUTPUTS.items():
        data = table.select(["rank", field, "wgt", "communityID", *covariates]).drop_nulls()
        data = data.filter(pl.col(field) > 0).rename({"communityID": "psu", "wgt": "_w"})
        if data.height < 500:
            continue
        weights = data["_w"].to_numpy().astype(float)
        values = data[field].to_numpy().astype(float)
        mean = np.average(values, weights=weights)
        sd = math.sqrt(np.average((values - mean) ** 2, weights=weights))
        if not sd > 0:
            continue
        data = data.with_columns(((pl.col(field) - mean) / sd).alias("y_std"))
        try:
            result = svy.Sample(data=data, design=svy.Design(psu="psu", wgt="_w", wr=True)) \
                .glm.fit(y="y_std", x=["rank"] + covariates, family="gaussian",
                         drop_nulls=True, alpha=0.05).to_polars()
        except Exception as error:
            rows.append({"phenotype_concept_id": concept, "fit_status": f"error: {error}"[:120]})
            continue
        cell = {row["term"]: row for row in result.to_dicts()}.get("rank")
        if not cell:
            continue
        rows.append({
            "phenotype_concept_id": concept,
            "estimate": float(cell["estimate"]),
            "standard_error": float(cell["std_err"]),
            "ci_lower": float(cell["conf_low"]),
            "ci_upper": float(cell["conf_high"]),
            "p_value": float(cell["p_value"]),
            "n_model": data.height,
            "fit_status": "success",
        })
    ok = [row for row in rows if row.get("fit_status") == "success"]
    adjusted = bh([row["p_value"] for row in ok])
    for row, q in zip(ok, adjusted):
        row["q_value_by"] = float(q)

    import csv
    out = require_private_path(PRIVATE_OUT)
    fields = ["phenotype_concept_id", "estimate", "standard_error", "ci_lower", "ci_upper",
              "p_value", "q_value_by", "n_model", "fit_status"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})
    payload = {
        "schema_version": 1,
        "wave": "2015",
        "exposure": "cooking fuel rank 0 electric, 1 gas/LPG, 2 marsh gas, 3 coal/wood/other",
        "results": sorted(ok, key=lambda item: item["p_value"]),
        "summary": {"outcomes": len(ok), "q_lt_05": sum(1 for row in ok if row["q_value_by"] < 0.05)},
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave2015_fuel_gradient_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
