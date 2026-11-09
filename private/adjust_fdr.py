"""Add BH-FDR q values within wave x outcome domain to each scan file."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/results")


def domain_of(row: pd.Series) -> str:
    concept = str(row.get("phenotype_concept_id", ""))
    variable = str(row.get("phenotype_variable", ""))
    if concept == "cesd_score":
        return "cesd"
    if concept.startswith("blood_") or variable.startswith("qc1_") or variable.startswith("new"):
        return "blood"
    if str(row.get("phenotype_family", "")) == "binomial":
        return "diagnosis"
    return "other"


def bh(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = np.empty(n, dtype=float)
    prev = 1.0
    for rank, idx in enumerate(order[::-1], start=1):
        k = n - rank + 1
        value = min(prev, p[idx] * n / k)
        ranked[idx] = value
        prev = value
    return ranked


for wave in ("2011", "2013", "2015", "2018", "2020"):
    path = BASE / f"scan_{wave}_core_v1.csv"
    if not path.exists():
        continue
    df = pd.read_csv(path, low_memory=False)
    df["outcome_domain"] = df.apply(domain_of, axis=1)
    df["p_value"] = pd.to_numeric(df["p_value"], errors="coerce")
    ok = df["fit_status"] == "success"
    df["q_family"] = np.nan
    for (_, _), group in df[ok].groupby(["wave", "outcome_domain"]):
        q = bh(group["p_value"].fillna(1.0).to_numpy())
        df.loc[group.index, "q_family"] = q
    out = BASE / f"scan_{wave}_core_fdr.csv"
    df.to_csv(out, index=False)
    sig = df[(df["q_family"] < 0.05)]
    print(wave, "rows", len(df), "| q<0.05", len(sig), "| by domain",
          sig["outcome_domain"].value_counts().to_dict() if len(sig) else {})
