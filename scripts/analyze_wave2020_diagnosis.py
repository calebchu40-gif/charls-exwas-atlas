#!/usr/bin/env python3
"""Household exposures and doctor-diagnosed conditions in the 2020 wave.

Wave 5 carries the household items and the route-derived diagnosis file but no
sex, urbanicity or education. Those are time-invariant, so they are merged back
from the 2011 baseline after mapping the 12-digit 2020 identifier to the 11-digit
2011 one (drop character 11; 85% overlap verified earlier).

Model per outcome: age, age squared, sex, education groups and urbanicity, with
the household exposures entered one at a time. Conservative, exploratory.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

import svy  # noqa: E402
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path  # noqa: E402

W2020 = PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2020_person_analytic.dta"
DIAG = PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2020_doctor_diagnosis_outcomes_route_derived.dta"
AGE2020 = PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2020_age_candidate_private.dta"
W2011 = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
AGE2011 = PRIVATE_ROOT / "age_inputs_2011" / "wave1_age_interval_candidate.dta"

EXPOSURES = {
    "water": ("i017", {1.0: 1.0, 2.0: 0.0}),
    "heating": ("i020", {1.0: 1.0, 2.0: 0.0}),
    "gas_supply": ("i019", {1.0: 1.0, 2.0: 0.0}),
}
OUTCOMES = [
    "hypertension_diagnosis_ever_doctor_diagnosed",
    "dyslipidemia_diagnosis_ever_doctor_diagnosed",
    "diabetes_high_blood_sugar_diagnosis_ever_doctor_diagnosed",
    "heart_disease_diagnosis_ever_doctor_diagnosed",
    "stroke_diagnosis_ever_doctor_diagnosed",
    "chronic_lung_disease_diagnosis_ever_doctor_diagnosed",
    "liver_disease_diagnosis_ever_doctor_diagnosed",
    "cancer_diagnosis_ever_doctor_diagnosed",
]
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave2020_household_diagnosis_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "wave2020_diagnosis_v1.json"


def main(argv: list[str] | None = None) -> int:
    import pyreadstat
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected wave tables")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected wave tables")

    frame, _ = pyreadstat.read_dta(str(W2020), usecols=["ID", "i017", "i019", "i020", "i022",
                                                       "INDV_weight", "communityID"])
    frame["ID"] = frame["ID"].astype(str)
    frame["id11"] = frame["ID"].str.slice(0, 10) + frame["ID"].str.slice(11)

    ages, _ = pyreadstat.read_dta(str(AGE2020), usecols=["ID", "official_xrage"])
    ages["ID"] = ages["ID"].astype(str)
    ages["age"] = pd.to_numeric(ages["official_xrage"], errors="coerce")
    ages = ages[["ID", "age"]]

    diag, _ = pyreadstat.read_dta(str(DIAG), usecols=["ID"] + OUTCOMES)
    diag["ID"] = diag["ID"].astype(str)

    base, _ = pyreadstat.read_dta(str(W2011), usecols=["ID", "rgender", "urban_nbs", "bd001"])
    base["ID"] = base["ID"].astype(str)
    base["female"] = np.where(base["rgender"] == 2, 1.0, np.where(base["rgender"] == 1, 0.0, np.nan))
    base["urban"] = np.where(base["urban_nbs"] == 1, 1.0, np.where(base["urban_nbs"] == 0, 0.0, np.nan))
    base = base.rename(columns={"ID": "id11"})[["id11", "female", "urban", "bd001"]]

    merged = frame.merge(ages, on="ID", how="left").merge(diag, on="ID", how="left") \
        .merge(base, on="id11", how="left")
    merged["bd001_num"] = pd.to_numeric(merged["bd001"], errors="coerce")
    merged["edu_group"] = pd.cut(merged["bd001_num"], bins=[0, 3, 5, 7, 11], labels=False, right=True)
    merged["age_c"] = merged["age"] - 60
    merged["age_c2"] = merged["age_c"] ** 2
    for name, (field, mapping) in EXPOSURES.items():
        values = pd.to_numeric(merged[field], errors="coerce")
        merged[name] = values.map(mapping)
    fuel = pd.to_numeric(merged["i022"], errors="coerce")
    merged["solid_fuel"] = np.where(fuel.isin([1, 6, 7]), 1.0,
                                    np.where(fuel.isin([2, 3, 4, 5]), 0.0, np.nan))
    merged = merged.rename(columns={"INDV_weight": "_w", "communityID": "psu"})
    merged = merged[merged["age"] >= 45]

    covariates = ["age_c", "age_c2", "female", "urban", "edu_group"]
    rows = []
    for exposure in ["water", "heating", "gas_supply", "solid_fuel"]:
        for outcome in OUTCOMES:
            data = merged[[exposure, outcome, "_w", "psu", *covariates]].dropna()
            data = data[data["_w"] > 0]
            if data.shape[0] < 300 or data[outcome].nunique() < 2:
                continue
            try:
                result = svy.Sample(data=data, design=svy.Design(psu="psu", wgt="_w", wr=True)) \
                    .glm.fit(y=outcome, x=[exposure] + covariates, family="binomial",
                             drop_nulls=True, alpha=0.05).to_polars()
            except Exception as error:
                rows.append({"exposure": exposure, "outcome": outcome,
                             "fit_status": f"error: {error}"[:120]})
                continue
            cell = {row["term"]: row for row in result.to_dicts()}.get(exposure)
            if not cell:
                continue
            rows.append({
                "exposure": exposure,
                "outcome": outcome.replace("_diagnosis_ever_doctor_diagnosed", ""),
                "log_or": float(cell["estimate"]),
                "odds_ratio": float(np.exp(cell["estimate"])),
                "ci_lower": float(np.exp(cell["conf_low"])),
                "ci_upper": float(np.exp(cell["conf_high"])),
                "p_value": float(cell["p_value"]),
                "n_model": data.shape[0],
                "fit_status": "success",
            })

    import csv
    out = require_private_path(PRIVATE_OUT)
    fields = ["exposure", "outcome", "log_or", "odds_ratio", "ci_lower", "ci_upper",
              "p_value", "n_model", "fit_status"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})
    ok = [row for row in rows if row.get("fit_status") == "success"]
    payload = {
        "schema_version": 1,
        "wave": "2020",
        "design": "age, sex, education and urbanicity from the 2011 baseline; household exposures one at a time",
        "results": ok,
        "summary": {"models": len(ok), "p_lt_05": sum(1 for row in ok if row["p_value"] < 0.05)},
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave2020_household_diagnosis_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
