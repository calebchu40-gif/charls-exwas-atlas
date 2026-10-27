#!/usr/bin/env python3
"""CLI driver for the generic CHARLS exposure-phenotype scan engine.

Two modes
---------
1. ``--synthetic``: builds a fake person-level frame with *known* exposure
   effects and runs the full engine on it. No CHARLS data is read. This is the
   smoke test that must pass on every machine (and on the analysis server)
   before any real scan is attempted.
2. Real mode: ``--frame`` points to a protected prepared wave table (``.dta``,
   ``.parquet`` or ``.csv``), ``--registry`` lists the variables to scan and
   ``--design`` fixes the weight / PSU / domain / covariate sets.

Both modes write only under the protected private workspace; the CLI refuses
to write anywhere else.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))

import exwas_engine as engine  # noqa: E402
from project_paths import PRIVATE_ROOT, require_private_path  # noqa: E402


# --------------------------------------------------------------------------
# synthetic fixtures (no CHARLS data)
# --------------------------------------------------------------------------
def synthetic_frame(n: int = 3000, seed: int = 7) -> pl.DataFrame:
    """Build a person-level frame with a known, recoverable exposure effect."""
    rng = np.random.default_rng(seed)
    age = rng.integers(45, 86, n)
    female = rng.integers(0, 2, n)
    education = rng.integers(1, 5, n)
    urban = rng.integers(0, 2, n)
    area = rng.integers(1, 4, n)
    exposure_cont = rng.normal(0, 1, n)
    exposure_bin = rng.binomial(1, 0.45, n)
    noise = rng.normal(0, 1, n)
    # known structure: 0.60 per SD of continuous exposure, +1.20 for binary
    phenotype_cont = 0.60 * exposure_cont + 1.20 * exposure_bin + 0.02 * (age - 60) + 0.25 * female + noise
    linear = -1.2 + 0.70 * exposure_cont + 0.50 * exposure_bin
    phenotype_bin = rng.binomial(1, 1.0 / (1.0 + np.exp(-linear)))
    weight = rng.uniform(0.4, 2.5, n)
    return pl.DataFrame({
        "ID": [f"SYN{i:06d}" for i in range(n)],
        "psu": [f"P{i % 60:03d}" for i in range(n)],
        "stratum": [f"S{(i % 60) // 15:02d}" for i in range(n)],
        "ind_weight": weight,
        "age": age.astype(float),
        "female": female.astype(float),
        "education": education.astype(float),
        "urban": urban.astype(float),
        "area": area.astype(float),
        "exposure_cont": exposure_cont,
        "exposure_bin": exposure_bin.astype(float),
        "pheno_cont": phenotype_cont,
        "pheno_bin": phenotype_bin.astype(float),
    })


def synthetic_registry() -> list[engine.VariableSpec]:
    specs = [
        engine.VariableSpec("synth_cont", "E", "Synthetic continuous exposure", "SYNTH",
                            "exposure_cont", "continuous"),
        engine.VariableSpec("synth_bin", "E", "Synthetic binary exposure", "SYNTH",
                            "exposure_bin", "binary"),
        engine.VariableSpec("synth_site", "E", "Synthetic 3-level exposure", "SYNTH",
                            "area", "categorical", levels=("1", "2", "3"), reference="1"),
        engine.VariableSpec("synth_pheno_cont", "P", "Synthetic continuous phenotype", "SYNTH",
                            "pheno_cont", "continuous", family="gaussian", unit="synthetic"),
        engine.VariableSpec("synth_pheno_bin", "P", "Synthetic binary phenotype", "SYNTH",
                            "pheno_bin", "binary", family="binomial"),
    ]
    return specs


def synthetic_design() -> engine.DesignSpec:
    return engine.DesignSpec(
        weight="ind_weight", psu="psu", strata="stratum",
        age_field="age", age_min=45,
        covariate_sets={
            "M0": [],
            "M1": ["age", "female"],
            "M2": ["age", "female", "education", "urban"],
        },
        scale_outcome=False,
    )


# --------------------------------------------------------------------------
def read_frame(path: Path, columns: list[str]) -> pl.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".dta":
        import pyreadstat
        frame, _ = pyreadstat.read_dta(str(path), usecols=columns, output_format="polars")
        return frame
    if suffix == ".parquet":
        return pl.read_parquet(path, columns=columns)
    if suffix == ".csv":
        return pl.read_csv(path, columns=columns)
    raise SystemExit(f"unsupported frame type: {suffix}")


def required_columns(registry: list[engine.VariableSpec], design: engine.DesignSpec) -> list[str]:
    names = {design.weight, design.psu}
    if design.strata:
        names.add(design.strata)
    if design.age_field:
        names.add(design.age_field)
    names.update(spec.variable for spec in registry)
    for columns in design.covariate_sets.values():
        names.update(columns)
    return sorted(names)


def summarise(rows: list[dict[str, object]], pairs: int) -> dict[str, object]:
    success = [row for row in rows if row.get("fit_status") == "success"]
    by_family: dict[str, int] = {}
    for row in rows:
        family = str(row.get("multiple_testing_family", "")).split(";")[0]
        by_family[family] = by_family.get(family, 0) + 1
    return {
        "pairs": pairs,
        "rows": len(rows),
        "success": len(success),
        "blocked": len(rows) - len(success),
        "families": by_family,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--synthetic", action="store_true", help="run on a fake frame with known effects")
    parser.add_argument("--frame", type=Path, help="protected prepared wave table")
    parser.add_argument("--registry", type=Path, help="variable registry CSV")
    parser.add_argument("--design", type=Path, help="design specification JSON")
    parser.add_argument("--wave", default="SYNTH", help="wave label used to select registry rows")
    parser.add_argument("--models", default="M0,M1", help="comma-separated model ids")
    parser.add_argument("--out", type=Path, required=True, help="result CSV (must be inside the private workspace)")
    parser.add_argument("--family-prefix", default="charls_exwas")
    args = parser.parse_args(argv)

    out = require_private_path(args.out)
    if not out.is_relative_to(PRIVATE_ROOT.resolve()):
        parser.error(f"--out must stay under the protected workspace {PRIVATE_ROOT}")

    if args.synthetic:
        frame = synthetic_frame()
        registry = synthetic_registry()
        design = synthetic_design()
        wave = "SYNTH"
    else:
        if not (args.frame and args.registry and args.design):
            parser.error("real mode requires --frame, --registry and --design")
        registry = engine.load_registry(args.registry)
        design = engine.load_design(args.design)
        wave = args.wave
        columns = required_columns(registry, design)
        if args.frame.suffix.lower() == ".dta":
            import pyreadstat
            _, meta = pyreadstat.read_dta(str(args.frame), metadataonly=True)
            missing = [c for c in columns if c not in meta.column_names]
        else:
            missing = []
        if missing:
            parser.error("frame is missing registry/design columns: " + ", ".join(missing))
        frame = read_frame(args.frame, columns)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    rows = engine.scan(frame, registry, design, wave=wave, models=models,
                       family_prefix=args.family_prefix)
    engine.write_rows(rows, out)
    pairs = len(engine.enumerate_pairs(registry, wave))
    summary = summarise(rows, pairs)
    summary["design_note"] = design.note()
    summary["output"] = str(out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
