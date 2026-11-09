"""Build the all-results public aggregate (M1 primary, both directions).

Every estimable pair is kept regardless of significance.  The only drops are
failed fits, models with fewer than 500 complete cases, and pairs whose
exposure or phenotype has no label.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
RES = BASE / "private/results"
OUT = BASE / "private/results/full_scan_public"
MIN_N = 500

FIELDS = ["pair_id", "exposure_concept_id", "exposure_label", "exposure_kind",
          "phenotype_concept_id", "phenotype_label", "phenotype_kind",
          "estimate_type", "estimate", "standard_error", "ci_lower", "ci_upper",
          "p_value", "q_family", "n_model", "n_psu", "exposure_contrast", "model_id"]

summary = {}
for wave in ("2011", "2013", "2015", "2018", "2020"):
    scan = pd.read_csv(RES / f"scan_{wave}_core_fdr.csv", low_memory=False)
    reg = pd.read_csv(BASE / "private/derived_wave_tables" / f"registry_{wave}_core.csv")
    labels = dict(zip(reg["concept_id"], reg["label"]))
    kinds = dict(zip(reg["concept_id"], reg["kind"]))

    df = scan[(scan["fit_status"] == "success") & (scan["model_id"] == "M1")].copy()
    df = df[pd.to_numeric(df["n_model"], errors="coerce") >= MIN_N]
    df["exposure_label"] = df["exposure_concept_id"].map(labels)
    df["phenotype_label"] = df["phenotype_concept_id"].map(labels)
    df["exposure_kind"] = df["exposure_concept_id"].map(kinds)
    df["phenotype_kind"] = df["phenotype_concept_id"].map(kinds)
    df = df.dropna(subset=["exposure_label", "phenotype_label"])
    df["pair_id"] = (df["wave"].astype(str) + ":" + df["exposure_concept_id"].astype(str)
                     + ":" + df["phenotype_concept_id"].astype(str))

    payload = {"wave": wave, "fields": FIELDS, "rows": df[FIELDS].round(6).to_dict(orient="records")}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"full_scan_{wave}_v1.json").write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    by_exposure = df.groupby("exposure_concept_id").size().sort_values(ascending=False)
    by_phenotype = df.groupby("phenotype_concept_id").size().sort_values(ascending=False)
    summary[wave] = {
        "rows": int(len(df)),
        "exposures": int(df["exposure_concept_id"].nunique()),
        "phenotypes": int(df["phenotype_concept_id"].nunique()),
        "significant_q": int((df["q_family"] < 0.05).sum()),
        "significant_p": int((df["p_value"] < 0.05).sum()),
        "top_exposure": by_exposure.head(3).to_dict(),
        "bytes": (OUT / f"full_scan_{wave}_v1.json").stat().st_size,
    }

print(json.dumps(summary, ensure_ascii=False, indent=1))
total = sum(item["rows"] for item in summary.values())
print("total rows", total, "| files in", str(OUT))
