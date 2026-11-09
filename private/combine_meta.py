"""Combine per-wave estimates into one pair-level result (inverse-variance, DL)."""
from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/results")
WAVES = ("2011", "2013", "2015", "2018", "2020")

frames = []
for wave in WAVES:
    path = BASE / f"scan_{wave}_full_v1.csv"
    if not path.exists():
        continue
    df = pd.read_csv(path, low_memory=False)
    df = df[(df["fit_status"] == "success") & (df["model_id"] == "M1")].copy()
    for col in ("estimate", "standard_error", "p_value", "q_value_by", "n_model"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df["standard_error"] > 0]
    frames.append(df)
    print(wave, "usable per-wave rows", len(df))

allw = pd.concat(frames, ignore_index=True)
print("total per-wave rows:", len(allw))

group_cols = ["exposure_concept_id", "phenotype_concept_id", "exposure_term"]
rows = []
for (exp, phe, term), grp in allw.groupby(group_cols, sort=False):
    est = grp["estimate"].to_numpy()
    se = grp["standard_error"].to_numpy()
    w = 1.0 / se**2
    fixed = float(np.sum(est * w) / np.sum(w))
    se_fixed = float(np.sqrt(1.0 / np.sum(w)))
    q = float(np.sum(w * (est - fixed) ** 2))
    dfree = len(est) - 1
    tau2 = 0.0
    if dfree > 0 and q > dfree:
        c = float(np.sum(w) - np.sum(w**2) / np.sum(w))
        tau2 = max(0.0, (q - dfree) / c) if c > 0 else 0.0
    w2 = 1.0 / (se**2 + tau2)
    est_dl = float(np.sum(est * w2) / np.sum(w2))
    se_dl = float(np.sqrt(1.0 / np.sum(w2)))
    i2 = 0.0 if len(est) < 2 or q <= 0 else max(0.0, (q - dfree) / q)
    z = est_dl / se_dl if se_dl > 0 else np.nan
    p = float(2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))) if np.isfinite(z) else np.nan
    rows.append({
        "exposure_concept_id": exp, "phenotype_concept_id": phe, "exposure_term": term,
        "waves": int(grp["wave"].nunique()),
        "estimate": est_dl, "standard_error": se_dl,
        "ci_lower": est_dl - 1.959964 * se_dl, "ci_upper": est_dl + 1.959964 * se_dl,
        "p_value": p, "i2": i2, "tau2": tau2,
        "estimate_fixed": fixed, "se_fixed": se_fixed,
        "n_model_min": int(grp["n_model"].min()), "n_model_max": int(grp["n_model"].max()),
        "n_estimable_rows": int(len(grp)),
        "any_q_family_lt_05": bool((grp["q_value_by"] < 0.05).any()) if "q_value_by" in grp else False,
    })

pairs = pd.DataFrame(rows)
pairs["q_value"] = np.nan
ok = pairs["p_value"].notna()
p = pairs.loc[ok, "p_value"].to_numpy()
order = np.argsort(p)
ranked = np.empty(len(p))
prev = 1.0
for rank, idx in enumerate(order[::-1], start=1):
    k = len(p) - rank + 1
    value = min(prev, p[idx] * len(p) / k)
    ranked[idx] = value
    prev = value
pairs.loc[ok, "q_value"] = ranked
pairs.to_csv(BASE / "pair_term_results_v1.csv", index=False)

print("pair-level results:", len(pairs))
print("pairs with >=2 waves:", int((pairs["waves"] >= 2).sum()))
print("p<0.05:", int((pairs["p_value"] < 0.05).sum()), "| q<0.05:", int((pairs["q_value"] < 0.05).sum()))
print("median n_model:", int(pairs["n_model_min"].median()))
