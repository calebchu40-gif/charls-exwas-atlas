#!/usr/bin/env python3
"""Exploratory Wave 1 pilot-105 scan with pre-declared sensitivity variants.

What this is
------------
The frozen K=150 register defines the pilot batch as one running-water contrast
plus six cooking-fuel-versus-electricity contrasts crossed with the fifteen
predeclared blood phenotypes. This driver runs that 7 x 15 grid through
:mod:`exwas_engine` on the official-rebuild Wave 1 table, plus a fixed set of
sensitivity variants:

``main``
    bloodweight, communityID PSUs, no strata, with-replacement Taylor
    approximation; age/age^2, sex, urban/rural, education groups; glucose and
    triglycerides restricted to the fasting subsample.
``county_psu``
    identical to ``main`` but PSUs are the six-digit county prefix of
    communityID (150 clusters instead of 450), so within-county correlation is
    partly absorbed.
``no_urban``
    ``main`` minus the urban/rural covariate (cooking fuel and urbanicity are
    closely related, so this checks whether the fuel contrasts are driven by
    that adjustment).
``age_sex``
    age/age^2 and sex only.
``drop_small``
    ``main`` without the marsh-gas and other-fuel contrasts (176 and 90 exposed
    respondents respectively).
``fasting_adjust``
    glucose and triglycerides on the full sample with the fasting indicator as
    a covariate instead of restricting to fasting.

What this is **not**
-------------------
It is not the gated scale-up executor. That path requires an independently
reviewed readiness record for the same batch and remains the route to any
release-grade number. Results written here are *exploratory, PI-delegated, and
not independently reviewed*; they may not be published or described as formal
findings.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))

import exwas_engine as engine  # noqa: E402
from project_paths import PRIVATE_ROOT, WAVE_DATA_DIR, QA_OUTPUT_DIR, require_private_path  # noqa: E402

WAVE = "2011"
MODEL_ID = "M1"
PREPARED = WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"
AGE_CANDIDATE = PRIVATE_ROOT / "age_inputs_2011" / "wave1_age_interval_candidate.dta"
RESULT_DIR = PRIVATE_ROOT / "results"
SUMMARY = QA_OUTPUT_DIR / "wave1_pilot105_variants_summary_v1.json"

WATER_FIELD = "i017"
FUEL_FIELD = "i022"
FASTING_FIELD = "qc1_va003"
FUEL_LEVELS = {1: "coal", 2: "natural_gas", 3: "marsh_gas", 4: "LPG",
               6: "crop_residue_or_wood", 7: "other"}
FUEL_REFERENCE = 5  # electricity
SMALL_GROUPS = ("marsh_gas", "other")

OUTCOMES = {
    "blood_wbc": ("qc1_vb002", "1000 cells/\u00b5L"),
    "blood_hemoglobin": ("qc1_vb004", "g/dL"),
    "blood_hematocrit": ("qc1_vb005", "%"),
    "blood_mcv": ("qc1_vb006", "fL"),
    "blood_platelets": ("qc1_vb009", "10^9/L"),
    "blood_crp": ("newcrp", "mg/L"),
    "blood_hba1c": ("newhba1c", "%"),
    "blood_total_cholesterol": ("newcho", "mg/dL"),
    "blood_hdl": ("newhdl", "mg/dL"),
    "blood_ldl": ("newldl", "mg/dL"),
    "blood_triglycerides": ("newtg", "mg/dL"),
    "blood_bun": ("newbun", "mg/dL"),
    "blood_creatinine": ("newcrea", "mg/dL"),
    "blood_glucose": ("newglu", "mg/dL"),
    "blood_uric_acid": ("newua", "mg/dL"),
}
FASTING_SENSITIVE = ("blood_glucose", "blood_triglycerides")

M1 = ["age_c", "age_c2", "female", "urban", "edu_2", "edu_3", "edu_4", "edu_5"]
M1_NO_URBAN = ["age_c", "age_c2", "female", "edu_2", "edu_3", "edu_4", "edu_5"]
M0 = ["age_c", "age_c2", "female"]
M1F = M1 + ["fasting_code"]

VARIANTS = {
    "main": {"psu": "communityID", "covariates": M1, "drop_small": False, "fasting": "restrict"},
    "county_psu": {"psu": "psu_county", "covariates": M1, "drop_small": False, "fasting": "restrict"},
    "no_urban": {"psu": "communityID", "covariates": M1_NO_URBAN, "drop_small": False, "fasting": "restrict"},
    "age_sex": {"psu": "communityID", "covariates": M0, "drop_small": False, "fasting": "restrict"},
    "drop_small": {"psu": "communityID", "covariates": M1, "drop_small": True, "fasting": "restrict"},
    "fasting_adjust": {"psu": "communityID", "covariates": M1F, "drop_small": False, "fasting": "adjust"},
}


class DriverError(RuntimeError):
    """The scan cannot proceed without inventing a rule."""


def derive_frame(raw: pl.DataFrame) -> pl.DataFrame:
    """Recode exposures and covariates; enforce finite-positive outcomes."""
    num = lambda name: pl.col(name).cast(pl.Float64, strict=False)  # noqa: E731
    frame = raw.with_columns([
        pl.when(num(WATER_FIELD) == 1).then(1.0)
          .when(num(WATER_FIELD) == 2).then(0.0)
          .otherwise(None).alias("water_yes"),
        pl.when(num("rgender") == 2).then(1.0)
          .when(num("rgender") == 1).then(0.0)
          .otherwise(None).alias("female"),
        pl.when(num("urban_nbs") == 1).then(1.0)
          .when(num("urban_nbs") == 0).then(0.0)
          .otherwise(None).alias("urban"),
        num(FASTING_FIELD).alias("fasting_code"),
    ])
    valid_fuel = [float(code) for code in (1, 2, 3, 4, 5, 6, 7)]
    for level in FUEL_LEVELS:
        name = f"fuel_{FUEL_LEVELS[level]}"
        frame = frame.with_columns(
            pl.when(num(FUEL_FIELD) == level).then(1.0)
              .when(num(FUEL_FIELD).is_in(valid_fuel)).then(0.0)
              .otherwise(None).alias(name))
    edu = num("bd001")
    groups = {"edu_2": [4], "edu_3": [5], "edu_4": [6, 7], "edu_5": [8, 9, 10, 11]}
    valid_edu = [float(code) for code in range(1, 12)]
    for name, codes in groups.items():
        frame = frame.with_columns(
            pl.when(edu.is_in([float(c) for c in codes])).then(1.0)
              .when(edu.is_in(valid_edu)).then(0.0)
              .otherwise(None).alias(name))
    for concept, (field, _unit) in OUTCOMES.items():
        value = num(field)
        frame = frame.with_columns(
            pl.when(value.is_not_null() & (value > 0)).then(value).otherwise(None).alias(f"out_{concept}"))
    return frame


def age_frame(raw: pl.DataFrame) -> pl.DataFrame:
    num = lambda name: pl.col(name).cast(pl.Float64, strict=False)  # noqa: E731
    return raw.with_columns([
        num("age_at_interview_lower").alias("age_lower"),
        ((num("age_at_interview_lower") + num("age_at_interview_upper")) / 2.0).alias("age_mid"),
    ]).select(["ID", "age_lower", "age_mid"])


def with_covariates(frame: pl.DataFrame) -> pl.DataFrame:
    mid = pl.col("age_mid").cast(pl.Float64, strict=False)
    county = pl.col("communityID").cast(pl.String).str.slice(0, 6)
    return frame.with_columns([
        (mid - 60).alias("age_c"),
        ((mid - 60) ** 2).alias("age_c2"),
        county.alias("psu_county"),
    ])


def registry(fasting_only: bool, drop_small: bool) -> list[engine.VariableSpec]:
    exposures = [engine.VariableSpec("running_water_at_residence", "E", "Running water: Yes vs No",
                                     WAVE, "water_yes", "binary")]
    for level, label in FUEL_LEVELS.items():
        if drop_small and label in SMALL_GROUPS:
            continue
        exposures.append(engine.VariableSpec(f"cooking_fuel_{label}", "E", f"{label} vs electricity",
                                             WAVE, f"fuel_{label}", "binary"))
    concepts = FASTING_SENSITIVE if fasting_only else tuple(
        c for c in OUTCOMES if c not in FASTING_SENSITIVE)
    phenotypes = [engine.VariableSpec(c, "P", c, WAVE, f"out_{c}", "continuous",
                                      unit=OUTCOMES[c][1]) for c in concepts]
    return exposures + phenotypes


def design(variant: str) -> engine.DesignSpec:
    spec = VARIANTS[variant]
    return engine.DesignSpec(
        weight="bloodweight", psu=spec["psu"], strata=None,
        age_field="age_lower", age_min=45,
        covariate_sets={MODEL_ID: list(spec["covariates"])},
        scale_outcome=True,
        variance_limitations=("released communityID clustering only; no official CHARLS strata or "
                              "replicate weights; with-replacement Taylor approximation"))


def load_private_frame() -> pl.DataFrame:
    import pyreadstat
    if not PREPARED.is_file():
        raise DriverError(f"prepared Wave 1 table missing: {PREPARED.name}")
    if not AGE_CANDIDATE.is_file():
        raise DriverError(f"age candidate missing: {AGE_CANDIDATE.name}")
    columns = ["ID", "bloodweight", "communityID", "rgender", "urban_nbs", "bd001",
               WATER_FIELD, FUEL_FIELD, FASTING_FIELD, *[f for f, _ in OUTCOMES.values()]]
    table, _ = pyreadstat.read_dta(str(PREPARED), usecols=columns, output_format="polars")
    ages, _ = pyreadstat.read_dta(str(AGE_CANDIDATE), usecols=["ID", "age_at_interview_lower",
                                                               "age_at_interview_upper"],
                                  output_format="polars")
    return with_covariates(derive_frame(table.join(age_frame(ages), on="ID", how="left")))


def run(frame: pl.DataFrame, variant: str) -> tuple[list[dict], dict]:
    spec = VARIANTS[variant]
    design_spec = design(variant)
    prefix = f"wave1_pilot105_{variant}"
    if spec["fasting"] == "adjust":
        rows = engine.scan(frame, registry(True, False), design_spec, wave=WAVE,
                           models=[MODEL_ID], family_prefix=prefix)
    elif spec["drop_small"]:
        full = engine.scan(frame, registry(False, True), design_spec, wave=WAVE,
                           models=[MODEL_ID], family_prefix=prefix)
        fasting = frame.filter(pl.col("fasting_code") == 1.0)
        fast = engine.scan(fasting, registry(True, True), design_spec, wave=WAVE,
                           models=[MODEL_ID], family_prefix=prefix)
        rows = full + fast
        engine.assign_families(rows, prefix)
    else:
        full = engine.scan(frame, registry(False, False), design_spec, wave=WAVE,
                           models=[MODEL_ID], family_prefix=prefix)
        fasting = frame.filter(pl.col("fasting_code") == 1.0)
        fast = engine.scan(fasting, registry(True, False), design_spec, wave=WAVE,
                           models=[MODEL_ID], family_prefix=prefix)
        rows = full + fast
        engine.assign_families(rows, prefix)
    summary = {
        "variant": variant,
        "rows": len(rows),
        "success": sum(1 for row in rows if row["fit_status"] == "success"),
        "blocked": sum(1 for row in rows if row["fit_status"] != "success"),
        "family": rows[0]["multiple_testing_family"] if rows else "",
        "status": "exploratory_pi_delegated_not_independently_reviewed",
    }
    return rows, summary


def synthetic_frame(n: int = 1500, seed: int = 11) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    water = rng.choice([1.0, 2.0], n, p=[0.55, 0.45]).astype(float)
    water[rng.random(n) < 0.05] = np.nan
    fasting = rng.choice([1.0, 2.0], n, p=[0.89, 0.11]).astype(float)
    fasting[rng.random(n) < 0.03] = np.nan
    data: dict[str, object] = {
        "ID": [f"SYN{i:06d}" for i in range(n)],
        "bloodweight": rng.uniform(0.4, 2.5, n),
        "communityID": [f"{110000 + i % 150:06d}{i % 3}" for i in range(n)],
        "rgender": rng.integers(1, 3, n).astype(float),
        "urban_nbs": rng.integers(0, 2, n).astype(float),
        "bd001": rng.integers(1, 12, n).astype(float),
        "age_lower": rng.integers(45, 90, n).astype(float),
        "age_mid": rng.integers(45, 90, n).astype(float),
        WATER_FIELD: water,
        FUEL_FIELD: rng.choice([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0], n).astype(float),
        FASTING_FIELD: fasting,
    }
    for field, _unit in OUTCOMES.values():
        data[field] = rng.normal(50, 10, n)
    return pl.DataFrame(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="run on the protected Wave 1 table")
    parser.add_argument("--synthetic", action="store_true", help="run the main variant on synthetic data")
    parser.add_argument("--variant", default="all",
                        help="variant name, 'all', or a comma-separated list")
    args = parser.parse_args(argv)

    names = list(VARIANTS) if args.variant == "all" else [v.strip() for v in args.variant.split(",")]
    unknown = [v for v in names if v not in VARIANTS]
    if unknown:
        parser.error(f"unknown variant(s): {', '.join(unknown)}")

    if args.synthetic:
        frame = with_covariates(derive_frame(synthetic_frame()))
        rows, summary = run(frame, "main")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0 if summary["rows"] == 105 else 1
    if not args.run:
        parser.error("--run is required to read the protected Wave 1 table")

    frame = load_private_frame()
    summaries = []
    for name in names:
        rows, summary = run(frame, name)
        out = require_private_path(RESULT_DIR / f"wave1_pilot105_{name}_v1.csv")
        if not out.is_relative_to(PRIVATE_ROOT.resolve()):
            parser.error(f"output must stay under {PRIVATE_ROOT}")
        engine.write_rows(rows, out)
        summary["output"] = str(out)
        summaries.append(summary)
        print(json.dumps(summary, ensure_ascii=False))

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summaries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
