"""Run the 2011 core-set pilot v3 (continuous + binary + categorical).

Recodes binary exposures/outcomes to 0/1 using the yes/no codes recorded in the
registry, then fits M0 and M1 for every exposure-phenotype pair.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import polars as pl
import pyreadstat

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
sys.path.insert(0, str(BASE / "code" / "scripts"))

import exwas_engine as eng  # noqa: E402

WAVE = "2011"
TABLE = BASE / "private" / "derived_wave_tables" / "CHARLS_wave2011_person_analytic.dta"
REGISTRY = BASE / "private" / "derived_wave_tables" / "registry_2011_core_v3.csv"
COVARIATES = BASE / "private" / "derived_wave_tables" / "covariates_wave2011.csv"
DESIGN = BASE / "private" / "design_2011_blood.json"
OUT = BASE / "private" / "results" / "pilot_2011_core_v3.csv"


def main() -> None:
    started = time.perf_counter()
    with REGISTRY.open(newline="", encoding="utf-8-sig") as handle:
        raw_rows = list(csv.DictReader(handle))
    registry = eng.load_registry(REGISTRY)
    design = eng.load_design(DESIGN)

    raw_columns = set()
    for row in raw_rows:
        raw_columns.add(row["source_variable"])
        if row["kind"] != "binary":
            raw_columns.add(row["variable"])
    _, meta = pyreadstat.read_dta(TABLE, metadataonly=True)
    usecols = ["ID", design.weight, design.psu] + [c for c in sorted(raw_columns) if c in meta.column_names]
    df, _ = pyreadstat.read_dta(TABLE, usecols=usecols)
    frame = pl.from_pandas(df, include_index=False)
    frame = frame.with_columns(pl.col("ID").cast(pl.String).str.strip_chars())

    recodes = []
    for row in raw_rows:
        if row["kind"] != "binary":
            continue
        source = row["source_variable"]
        yes, no = row["yes_code"], row["no_code"]
        expr = (
            pl.when(pl.col(source).cast(pl.Float64, strict=False) == float(yes)).then(1.0)
            .when(pl.col(source).cast(pl.Float64, strict=False) == float(no)).then(0.0)
            .otherwise(None)
            .alias(row["variable"])
        )
        recodes.append(expr)
    if recodes:
        frame = frame.with_columns(recodes)

    covariates = pl.read_csv(COVARIATES, infer_schema_length=10000)
    covariates = covariates.with_columns(pl.col("ID").cast(pl.String).str.strip_chars())
    frame = frame.join(covariates, on="ID", how="left")
    print("frame", frame.height, "columns", frame.width, "registry", len(registry))

    models = ["M0", "M1"]
    rows = eng.scan(frame, registry, design, WAVE, models, family_prefix="pilot2011v3")
    eng.write_rows(rows, OUT)

    elapsed = time.perf_counter() - started
    status = Counter(row.get("fit_status") for row in rows)
    models_used = Counter(row.get("model_id") for row in rows)
    print(json.dumps({
        "rows": len(rows),
        "status": dict(status),
        "by_model": dict(models_used),
        "seconds": round(elapsed, 1),
        "output": str(OUT),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
