"""Run the 2011 core-set pilot on the server and report timing, blocks and hits.

Inputs (private):
    registry_2011_core_continuous.csv
    covariates_wave2011.csv
    CHARLS_wave2011_person_analytic.dta
    design_2011_blood.json
Output:
    private/results/pilot_2011_core_continuous_v1.csv
"""
from __future__ import annotations

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

WAVE = "2011"
TABLE = BASE / "private" / "derived_wave_tables" / "CHARLS_wave2011_person_analytic.dta"
REGISTRY = BASE / "private" / "derived_wave_tables" / "registry_2011_core_continuous_v2.csv"
COVARIATES = BASE / "private" / "derived_wave_tables" / "covariates_wave2011.csv"
DESIGN = BASE / "private" / "design_2011_blood.json"
OUT = BASE / "private" / "results" / "pilot_2011_core_continuous_v2.csv"


def main() -> None:
    started = time.perf_counter()
    registry = eng.load_registry(REGISTRY)
    design = eng.load_design(DESIGN)
    variables = sorted({spec.variable for spec in registry})
    usecols = ["ID", design.weight, design.psu] + variables

    _, meta = pyreadstat.read_dta(TABLE, metadataonly=True)
    usecols = [c for c in usecols if c in meta.column_names]
    missing = [spec.variable for spec in registry if spec.variable not in usecols]
    if missing:
        print("WARNING missing columns:", missing[:10], "count", len(missing))

    df, _ = pyreadstat.read_dta(TABLE, usecols=usecols)
    frame = pl.from_pandas(df, include_index=False)
    frame = frame.with_columns(pl.col("ID").cast(pl.String).str.strip_chars())

    covariates = pl.read_csv(COVARIATES, infer_schema_length=10000)
    covariates = covariates.with_columns(pl.col("ID").cast(pl.String).str.strip_chars())
    frame = frame.join(covariates, on="ID", how="left")
    print("frame", frame.height, "columns", frame.width)

    models = ["M0", "M1"]
    rows = eng.scan(frame, registry, design, WAVE, models, family_prefix="pilot2011")
    eng.write_rows(rows, OUT)

    elapsed = time.perf_counter() - started
    status = Counter(row.get("fit_status") for row in rows)
    blocked_reason = Counter(row.get("blocked_reason") for row in rows if row.get("blocked_reason"))
    by_model = Counter(row.get("model_id") for row in rows)
    estimable = sum(1 for row in rows if row.get("fit_status") == "success")
    print(json.dumps({
        "rows": len(rows),
        "estimable": estimable,
        "by_model": dict(by_model),
        "status": dict(status),
        "top_blocked": blocked_reason.most_common(5),
        "seconds": round(elapsed, 1),
        "output": str(OUT),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
