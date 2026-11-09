"""Run one wave's core scan (all registered pairs, M0 + M1).

Usage: python run_wave.py 2015
"""
from __future__ import annotations

import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path

import polars as pl
import pyreadstat

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
sys.path.insert(0, str(BASE / "code" / "scripts"))

import exwas_engine as eng  # noqa: E402

TABLES = {
    "2011": BASE / "private/derived_wave_tables/CHARLS_wave2011_person_analytic.dta",
    "2013": BASE / "private/derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
    "2015": BASE / "private/derived_wave_tables/CHARLS_wave2015_person_analytic_with_official_blood.dta",
    "2018": BASE / "private/derived_wave_tables/CHARLS_wave2018_person_analytic.dta",
    "2020": BASE / "private/derived_wave_tables/CHARLS_wave2020_person_analytic.dta",
}


def main(wave: str) -> None:
    started = time.perf_counter()
    table = TABLES[wave]
    registry_path = BASE / "private" / "derived_wave_tables" / f"registry_{wave}_core.csv"
    design_path = BASE / "private" / f"design_{wave}.json"
    covariates_path = BASE / "private" / "derived_wave_tables" / f"covariates_wave{wave}.csv"
    out = BASE / "private" / "results" / f"scan_{wave}_core_v1.csv"

    with registry_path.open(newline="", encoding="utf-8-sig") as handle:
        raw_rows = list(csv.DictReader(handle))
    registry = eng.load_registry(registry_path)
    design = eng.load_design(design_path)

    raw_columns = {row["source_variable"] for row in raw_rows}
    raw_columns |= {row["variable"] for row in raw_rows if row["kind"] != "binary"}
    _, meta = pyreadstat.read_dta(table, metadataonly=True)
    usecols = ["ID", design.weight, design.psu] + [c for c in sorted(raw_columns) if c in meta.column_names]
    df, _ = pyreadstat.read_dta(table, usecols=usecols)
    frame = pl.from_pandas(df, include_index=False).with_columns(pl.col("ID").cast(pl.String).str.strip_chars())

    recodes = []
    for row in raw_rows:
        if row["kind"] != "binary":
            continue
        source = row["source_variable"]
        yes, no = float(row["yes_code"]), float(row["no_code"])
        recodes.append(
            pl.when(pl.col(source).cast(pl.Float64, strict=False) == yes).then(1.0)
            .when(pl.col(source).cast(pl.Float64, strict=False) == no).then(0.0)
            .otherwise(None).alias(row["variable"])
        )
    if recodes:
        frame = frame.with_columns(recodes)

    covariates = pl.read_csv(covariates_path, infer_schema_length=10000)
    covariates = covariates.with_columns(pl.col("ID").cast(pl.String).str.strip_chars())
    frame = frame.join(covariates, on="ID", how="left")

    rows = eng.scan(frame, registry, design, wave, ["M0", "M1"], family_prefix=f"scan{wave}")
    eng.write_rows(rows, out)
    elapsed = time.perf_counter() - started
    print(json.dumps({"wave": wave, "rows": len(rows),
                      "status": dict(Counter(row.get("fit_status") for row in rows)),
                      "seconds": round(elapsed, 1), "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
