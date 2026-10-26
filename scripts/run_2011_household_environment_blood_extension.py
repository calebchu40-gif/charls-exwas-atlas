#!/usr/bin/env python3
"""Protected exploratory extension: 2011 water/cooking-fuel × blood markers.

The fixed family contains 105 coefficients: running-water Yes vs No plus six
official cooking-fuel categories vs electricity, each paired with 15 blood
analytes. M1 and M2 are multiplicity-adjusted separately. Microdata and all
results stay under LOCALAPPDATA/CHARLS_ExWAS_Atlas.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import warnings
from datetime import datetime, timezone

import numpy as np
import polars as pl
import svy

from run_2011_water_blood_pilot import (
    AGE, DATA, OUT, PRIVATE, PSU_MAP, ROOT, WEIGHT_FIELD, AGE_FIELD,
    EDUCATION_FIELD, SEX_FIELD, URBAN_FIELD, as_num, private_path,
    read_analytes, read_input, sha256,
)

EXPECTED_SVY = "0.35.0"
FUEL_CATEGORIES = {
    1: "coal", 2: "natural_gas", 3: "marsh_gas", 4: "LPG",
    5: "electricity_reference", 6: "crop_residue_or_wood", 7: "other",
}
FUEL_REFERENCE = 5
FUEL_TERMS = [f"fuel_{code}" for code in FUEL_CATEGORIES if code != FUEL_REFERENCE]


def add_fuel_terms(data: pl.DataFrame) -> pl.DataFrame:
    expressions = [
        (pl.col("cooking_fuel_code") == code).cast(pl.Float64).alias(f"fuel_{code}")
        for code in FUEL_CATEGORIES if code != FUEL_REFERENCE
    ]
    expressions.extend(
        (pl.col("education_group") == code).cast(pl.Float64).alias(f"education_{code}")
        for code in (2, 3, 4)
    )
    return data.with_columns(expressions)


def model_rows(data: pl.DataFrame, analyte: dict[str, str], exposure: str,
               model_id: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    outcome = analyte["variable"]
    if exposure == "running_water":
        terms = ["water_yes"]
        exposure_domain = pl.col("water_yes").is_not_null()
        exposure_field = "i017"
        contrast_labels = {"water_yes": "running water yes vs no"}
        support_key = "water_yes"
    else:
        terms = FUEL_TERMS
        exposure_domain = pl.col("cooking_fuel_code").is_not_null()
        exposure_field = "i022"
        contrast_labels = {
            f"fuel_{code}": f"{FUEL_CATEGORIES[code]} vs electricity"
            for code in FUEL_CATEGORIES if code != FUEL_REFERENCE
        }
        support_key = "cooking_fuel_code"

    domain = ((pl.col(AGE_FIELD) >= 45) & (pl.col("analysis_weight") > 0)
              & exposure_domain)
    xvars = terms.copy()
    if model_id in {"M1", "M2"}:
        xvars += ["age_c", "age_c2", "female"]
        domain &= pl.col("age_c").is_not_null() & pl.col("female").is_not_null()
    if model_id == "M2":
        xvars += ["education_2", "education_3", "education_4", "urban"]
        domain &= pl.col("education_group").is_not_null() & pl.col("urban").is_not_null()

    pair_domain = data.filter(domain & pl.col(outcome).is_not_null())
    if pair_domain.height == 0:
        return [
            {"wave": "2011", "exposure_concept_id": exposure,
             "exposure_variable": exposure_field,
             "phenotype_concept_id": analyte["concept_id"],
             "phenotype_variable": outcome, "model_id": model_id,
             "term": term, "contrast": contrast_labels[term],
             "p_value": None, "fit_status": "not_estimable"}
            for term in terms
        ], {"n_complete": 0}

    weights = np.asarray(pair_domain["analysis_weight"].to_list(), dtype=float)
    values = np.asarray(pair_domain[outcome].to_list(), dtype=float)
    mean = float(np.average(values, weights=weights))
    sd = float(np.sqrt(np.average(np.square(values - mean), weights=weights)))
    if not np.isfinite(sd) or sd <= 0:
        raise RuntimeError(f"Outcome has no positive weighted SD: {outcome}/{exposure}/{model_id}")
    model_data = data.with_columns(((pl.col(outcome) - mean) / sd).alias("outcome_z"))
    fit = svy.Sample(
        data=model_data,
        design=svy.Design(psu="psu", wgt="analysis_weight", wr=True),
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = fit.glm.fit(
            y="outcome_z", x=xvars, family="gaussian", where=domain,
            drop_nulls=True, alpha=0.05,
        ).to_polars()
    by_term = {row.get("term"): row for row in result.to_dicts()}

    support = (pair_domain.group_by(support_key)
               .agg(pl.len().alias("n"), pl.col("psu").n_unique().alias("psus"))
               .sort(support_key).to_dicts())
    rows: list[dict[str, object]] = []
    for term in terms:
        rec = by_term.get(term)
        if rec is None:
            rows.append({
                "wave": "2011", "exposure_concept_id": exposure,
                "exposure_variable": exposure_field,
                "phenotype_concept_id": analyte["concept_id"],
                "phenotype_label": analyte["concept_label"],
                "phenotype_variable": outcome, "unit": analyte["unit"],
                "model_id": model_id, "term": term,
                "contrast": contrast_labels[term], "p_value": None,
                "fit_status": "term_not_returned",
            })
            continue
        estimate, se = as_num(rec.get("estimate")), as_num(rec.get("std_err"))
        low, high = as_num(rec.get("conf_low")), as_num(rec.get("conf_high"))
        pvalue = as_num(rec.get("p_value"))
        rows.append({
            "wave": "2011", "exposure_concept_id": exposure,
            "exposure_variable": exposure_field,
            "phenotype_concept_id": analyte["concept_id"],
            "phenotype_label": analyte["concept_label"],
            "phenotype_variable": outcome, "unit": analyte["unit"],
            "model_id": model_id, "term": term,
            "contrast": contrast_labels[term], "estimate": estimate,
            "standard_error": se, "ci_lower": low, "ci_upper": high,
            "estimate_unit_scale": estimate * sd if estimate is not None else None,
            "standard_error_unit_scale": se * sd if se is not None else None,
            "weighted_outcome_sd": sd, "p_value": pvalue,
            "design_df": as_num(rec.get("df")),
            "n_model": pair_domain.height,
            "n_psu": pair_domain["psu"].n_unique(),
            "kish_effective_n": float(weights.sum() ** 2 / np.square(weights).sum()),
            "support_private": json.dumps(support, separators=(",", ":")),
            "engine_warnings_private": " | ".join(str(w.message) for w in caught),
            "fit_status": "provisional_exploratory" if pvalue is not None else "numerically_unavailable",
            "design_note": "bloodweight + locally validated communityID PSU; unstratified with-replacement Taylor approximation; not full design variance",
        })
    return rows, {"n_complete": pair_domain.height}


def main() -> None:
    if getattr(svy, "__version__", None) != EXPECTED_SVY:
        raise RuntimeError(f"Expected svy {EXPECTED_SVY}, found {getattr(svy, '__version__', 'unknown')}")
    analytes = read_analytes()
    data = add_fuel_terms(read_input(analytes))
    # The exact 2011 Codebook categories are preserved; invalid/special codes
    # are not converted to a dose or silently collapsed into a fuel class.
    results: list[dict[str, object]] = []
    pair_qa: list[dict[str, object]] = []
    for analyte in analytes:
        outcome = analyte["variable"]
        data = data.with_columns(
            pl.when(pl.col(outcome) >= 0).then(pl.col(outcome)).otherwise(None).alias(outcome)
        )
        for exposure in ("running_water", "cooking_fuel_main"):
            for model_id in ("M0", "M1", "M2"):
                rows, qa = model_rows(data, analyte, exposure, model_id)
                results.extend(rows)
                pair_qa.append({
                    "phenotype_variable": outcome, "exposure": exposure,
                    "model_id": model_id, **qa,
                    "support_private": rows[0].get("support_private"),
                    "engine_warnings_private": rows[0].get("engine_warnings_private"),
                })

    adjust = __import__("adjust_exwas_pvalues").adjust_pvalues
    for model_id in ("M1", "M2"):
        family = [r for r in results if r["model_id"] == model_id]
        if len(family) != 105:
            raise RuntimeError(f"Predeclared family size changed: expected 105, observed {len(family)}")
        adjusted = adjust([as_num(r.get("p_value")) for r in family])
        for row, q, bonf in zip(family, adjusted["q_value_by"], adjusted["p_bonferroni"], strict=True):
            row["multiple_testing_family"] = f"pilot_2011_water_and_cooking_fuel_biomarkers_{model_id};K=105"
            row["q_value_by"] = q
            row["p_bonferroni"] = bonf

    stamp = datetime.now(timezone.utc).isoformat()
    manifest = {
        "run_utc": stamp,
        "analysis": "Exploratory 2011 running-water and cooking-fuel proxies × 15 blood analytes",
        "target": "CHARLS 2011 baseline household-resident age-45+ domain, valid exposure and positive bloodweight",
        "exposures": {
            "running_water": "i017 1=Yes vs 2=No",
            "cooking_fuel_main": "i022 valid 1-7; 6 indicators compared with electricity(code 5); categories retained exactly",
        },
        "outcomes": [r["concept_id"] for r in analytes],
        "fixed_primary_family": "15 water + (6 fuel-vs-electricity contrasts × 15 outcomes) = K 105; M1 BY-FDR and Bonferroni",
        "sensitivity_family": "Same K 105, separately adjusted in M2; exploratory sensitivity only",
        "model_definitions": {
            "M0": "Exposure-only weighted linear model; descriptive",
            "M1": "Exposure + centered age + age squared + sex; primary exploratory screen",
            "M2": "M1 + NBS urban/rural context + grouped baseline education; sensitivity only",
        },
        "weight": "2011 bloodweight; official guide describes household/individual/blood nonresponse correction based on inverse predicted participation, capped at 99th percentile; local source-file identity still pending",
        "psu": "communityID key verified against protected local psu.dta; source archive identity and split-community interpretation pending",
        "variance": "Unstratified with-replacement PSU Taylor approximation; exploratory only",
        "age_source": "Provisional Harmonized CHARLS D age candidate; domain classification and age derivation need official source verification",
        "sequential_screening": "Exploratory extension follows the first water pilot; multiplicity correction covers this declared 105-coefficient family but does not erase sequential screening",
        "participant_data_release": False,
        "source_sha256": {"prepared_person_table": sha256(DATA), "age_candidate": sha256(AGE), "psu_map": sha256(PSU_MAP)},
        "code_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip(),
        "python": sys.version,
        "svy_version": getattr(svy, "__version__", "unknown"),
        "status": "exploratory only; not approved for public/release-ready results",
    }
    private_path(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "environment_extension_results_private.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        fields = sorted({key for row in results for key in row})
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader(); writer.writerows(results)
    with (OUT / "environment_extension_pair_qa_private.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        fields = sorted({key for row in pair_qa for key in row})
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader(); writer.writerows(pair_qa)
    (OUT / "environment_extension_manifest_private.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "run": "complete", "rows": len(results), "primary_hypotheses": 105,
        "primary_finite_pvalues": sum(r.get("p_value") is not None for r in results if r["model_id"] == "M1"),
        "sensitivity_finite_pvalues": sum(r.get("p_value") is not None for r in results if r["model_id"] == "M2"),
        "models": ["M0", "M1", "M2"], "public_release": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
