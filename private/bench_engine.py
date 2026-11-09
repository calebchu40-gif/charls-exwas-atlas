"""Micro-benchmark for the ExWAS engine: per-model wall time at realistic n.

Run on the server with the project venv:
    /storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/env/venv/bin/python bench_engine.py
"""
import sys
import time

sys.path.insert(0, "/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/code/scripts")

import numpy as np
import polars as pl

import exwas_engine as eng


def bench(n: int, reps: int = 25):
    rng = np.random.default_rng(7)
    frame = pl.DataFrame({
        "wgt": rng.uniform(200, 6000, n),
        "psu": rng.integers(0, 150, n),
        "age": rng.uniform(45, 90, n),
        "sex": rng.integers(0, 2, n),
        "edu": rng.integers(1, 5, n),
        "income": rng.integers(1, 6, n),
        "urban": rng.integers(0, 2, n),
        "expo": rng.normal(0, 1, n),
        "outc": rng.normal(0, 1, n),
        "binout": rng.integers(0, 2, n).astype(float),
    })
    design = eng.DesignSpec(
        weight="wgt", psu="psu", age_field="age", age_min=45,
        covariate_sets={"M1": ["age", "sex", "edu", "income", "urban"]},
        scale_outcome=True,
    )
    expo = eng.VariableSpec(concept_id="e1", role="e", label="expo", wave="2011",
                           variable="expo", kind="continuous", transform="z")
    out = eng.VariableSpec(concept_id="p1", role="p", label="outc", wave="2011",
                          variable="outc", kind="continuous", family="gaussian")
    bout = eng.VariableSpec(concept_id="p2", role="p", label="bin", wave="2011",
                           variable="binout", kind="binary", family="binomial")
    prepared = eng.prepare_frame(frame, design, [expo, out, bout])
    # warm-up: first calls compile lazy plans
    for _ in range(3):
        eng.fit_pair(prepared, expo, out, design, "M1")
        eng.fit_pair(prepared, expo, bout, design, "M1")

    start = time.perf_counter()
    for _ in range(reps):
        eng.fit_pair(prepared, expo, out, design, "M1")
    gaussian = (time.perf_counter() - start) / reps

    start = time.perf_counter()
    for _ in range(reps):
        eng.fit_pair(prepared, expo, bout, design, "M1")
    binomial = (time.perf_counter() - start) / reps
    return gaussian, binomial


if __name__ == "__main__":
    for n in (10000, 17000):
        gaussian, binomial = bench(n)
        print(f"n={n}: gaussian {gaussian*1000:.1f} ms/model; binomial {binomial*1000:.1f} ms/model")
