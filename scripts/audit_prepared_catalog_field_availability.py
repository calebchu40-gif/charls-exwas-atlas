"""Compare public catalog source field names with private prepared-wave headers only.

This audit never reads respondent values. It reports only field/module counts and
the availability of design/weight column names, into the protected local QA path.
Exact code-name presence is a screening check, not proof of module identity,
eligibility, non-missingness, or analytic readiness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

try:  # Support both `python scripts/file.py` and package-style test imports.
    from .project_paths import QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path
except ImportError:
    from project_paths import QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path


WAVES = ("2011", "2013", "2015", "2018", "2020")
ROLES = ("e", "p", "c")
KEY_COLUMNS = ["Source.Wave", "Data.File.Name", "Variable.Name", "epcf"]
WEIGHT_NAMES = (
    "crosssection", "cross_section", "longitudinal", "hh_weight", "hh_weight_ad1",
    "indv_weight", "indv_weight_ad1", "indv_weight_ad2", "biomarker_weight",
    "bloodweight", "bio_weight1", "bio_weight2",
)


def missing_reason(wave: str, module: str) -> str:
    """Classify known structural absences without inferring record eligibility."""
    mod = module.casefold()
    if wave == "2011" and mod == "community":
        return "community module kept separate because communityID is not a safe unique join key"
    if mod in {"child", "parent", "sibling", "spousal_sibling"}:
        return "relationship roster remains separate; not a one-row-per-respondent module"
    if wave == "2015" and "blood_data_2015_independent_release" in mod:
        return "independent 2015 Blood Data release is absent from the prepared table"
    return "no exact source-code column name; inspect module merge, rename, and source release"


def inspect_catalog(catalog_path: Path, data_dir: Path) -> tuple[list[dict], list[dict], dict]:
    catalog = pd.read_csv(catalog_path, dtype=str, encoding="utf-8-sig").fillna("")
    missing_columns = [name for name in KEY_COLUMNS if name not in catalog.columns]
    if missing_columns:
        raise ValueError(f"Catalog is missing required columns: {missing_columns}")

    summaries: list[dict] = []
    missing_rows: list[dict] = []
    design: dict[str, dict] = {}
    for wave in WAVES:
        path = data_dir / f"CHARLS_wave{wave}_person_analytic.dta"
        if not path.is_file():
            design[wave] = {"prepared_table": path.name, "status": "missing"}
            for role in ROLES:
                summaries.append({"wave": wave, "role": role.upper(), "distinct_module_field_keys": 0,
                                  "distinct_source_codes": 0, "source_codes_present_by_name": 0,
                                  "source_codes_absent_by_name": 0, "status": "prepared table missing"})
            continue

        # pandas StataReader exposes file metadata without iterating over rows.
        with pd.read_stata(path, iterator=True, convert_categoricals=False) as reader:
            columns = {str(name).casefold() for name in reader.variable_labels().keys()}
        wave_rows = catalog[catalog["Source.Wave"].eq(wave)].copy()
        wave_rows["_role"] = wave_rows["epcf"].str.casefold()
        wave_rows = wave_rows[wave_rows["_role"].isin(ROLES)]
        wave_rows["_code"] = wave_rows["Variable.Name"].str.casefold()
        wave_rows["_module"] = wave_rows["Data.File.Name"].str.strip()
        keys = wave_rows.drop_duplicates(["_role", "_module", "_code"])

        for role in ROLES:
            role_rows = keys[keys["_role"].eq(role)]
            codes = set(role_rows["_code"])
            present = codes & columns
            absent = codes - columns
            summaries.append({
                "wave": wave, "role": role.upper(),
                "distinct_module_field_keys": int(len(role_rows)),
                "distinct_source_codes": int(len(codes)),
                "source_codes_present_by_name": int(len(present)),
                "source_codes_absent_by_name": int(len(absent)),
                "status": "name-only metadata comparison; no values or row counts read",
            })
            for _, row in role_rows[role_rows["_code"].isin(absent)].iterrows():
                module = str(row["_module"])
                code = str(row["_code"])
                missing_rows.append({
                    "wave": wave, "role": role.upper(), "module": module, "source_code": code,
                    "reason": missing_reason(wave, module),
                })

        available_weights = [name for name in WEIGHT_NAMES if name in columns]
        design[wave] = {
            "prepared_table": path.name,
            "header_column_count": len(columns),
            "available_weight_or_sample_flag_columns": available_weights,
            "required_2013_sample_flags_missing": [name for name in ("crosssection", "longitudinal")
                                                    if wave == "2013" and name not in columns],
            "status": "header-only; no respondent values read",
        }

    report = {
        "catalog_source": catalog_path.name,
        "waves": design,
        "interpretation": (
            "Exact code-name presence is a metadata screening check only. It does not establish source-module identity, "
            "within-wave eligibility, non-missingness, sample size, design validity, or analysis readiness. "
            "All output is aggregate/catalog metadata and is written to protected local QA storage."
        ),
    }
    return summaries, missing_rows, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path,
                        default=Path(__file__).resolve().parents[1] / "audit" / "charls_atlas_candidate_fields_v0.csv")
    parser.add_argument("--data-dir", type=Path, default=WAVE_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=QA_OUTPUT_DIR)
    args = parser.parse_args()
    data_dir = require_private_path(args.data_dir)
    output_dir = require_private_path(args.output_dir)
    summaries, missing_rows, report = inspect_catalog(args.catalog, data_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summaries).to_csv(output_dir / "prepared_catalog_field_availability_v1.csv",
                                   index=False, encoding="utf-8-sig")
    pd.DataFrame(missing_rows, columns=["wave", "role", "module", "source_code", "reason"]).to_csv(
        output_dir / "prepared_catalog_fields_missing_by_name_v1.csv", index=False, encoding="utf-8-sig")
    (output_dir / "prepared_catalog_field_availability_v1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote header-only catalogue availability summary for {len(WAVES)} waves to protected QA output.")
    print("No respondent values, IDs, non-missing counts, pairwise Ns, or associations were read or generated.")


if __name__ == "__main__":
    main()
