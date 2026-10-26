#!/usr/bin/env python3
"""Reject respondent-level/tabular data and archives from the public Pages bundle.

This is a file-type release guard only. It does not certify disclosure safety of
JSON/HTML contents; association JSON must still pass the dedicated payload and
disclosure-review validators.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_DIR = ROOT / "site-prototype" / "dist"
# Pages may publish only these reviewed, browser-facing assets. Additions must
# be reviewed here explicitly; this prevents an unrecognized JSON/HTML artifact
# from being copied into the public bundle by accident.
ALLOWED_RELATIVE_PATHS = {
    ".nojekyll",
    "app.js",
    "behavior_exposures_v1.json",
    "blood_biomarkers_v1.json",
    "cancer_sites_v1.json",
    "candidate_pair_explorer_v1.json",
    "catalog_c.json",
    "catalog_e.json",
    "catalog_p.json",
    "catalog.json",
    "chronic_disease_concepts_v2.json",
    "cognition_items_v1.json",
    "community_exposures_v1.json",
    "disability_history_v1.json",
    "food_environment_v1.json",
    "functional_concepts_v1.json",
    "health_symptoms_v1.json",
    "health_work_limitations_v1.json",
    "healthcare_access_v1.json",
    "household_additional_income_v1.json",
    "household_agricultural_production_v1.json",
    "household_covid_economic_v1.json",
    "household_other_asset_rental_income_v1.json",
    "household_renovation_expenditure_v1.json",
    "household_transfer_compensation_v1.json",
    "housing_catalog_v1.json",
    "index.html",
    "individual_transfer_income_v1.json",
    "land_rental_income_v1.json",
    "life_history_exposures_v1.json",
    "mood_items_v1.json",
    "objective_measurements_v1.json",
    "residential_rental_income_v1.json",
    "social_exposures_v1.json",
    "verified_code_examples_v1.json",
    "work_exposures_v1.json",
}
OPTIONAL_RELATIVE_PATHS = {"association_results_v1.json"}
BLOCKED_SUFFIXES = {
    ".accdb",
    ".csv",
    ".dbf",
    ".dta",
    ".feather",
    ".mdb",
    ".parquet",
    ".por",
    ".rda",
    ".rdata",
    ".rar",
    ".rds",
    ".sav",
    ".sas7bdat",
    ".sqlite",
    ".sqlite3",
    ".tsv",
    ".xls",
    ".xlsx",
    ".xpt",
    ".zip",
    ".7z",
}


def main() -> int:
    requested_site_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SITE_DIR
    if requested_site_dir.is_symlink():
        print("Public site directory must not be a symbolic link.", file=sys.stderr)
        return 1
    site_dir = requested_site_dir.resolve()
    if not site_dir.is_dir():
        print(f"Public site directory does not exist: {site_dir}", file=sys.stderr)
        return 2

    blocked_count = 0
    symlink_count = 0
    file_count = 0
    blocked_suffixes: set[str] = set()
    unexpected_count = 0
    observed_paths: set[str] = set()
    for path in site_dir.rglob("*"):
        if path.is_symlink():
            symlink_count += 1
            continue
        if not path.is_file():
            continue
        file_count += 1
        relative_path = path.relative_to(site_dir).as_posix()
        observed_paths.add(relative_path)
        if relative_path not in ALLOWED_RELATIVE_PATHS | OPTIONAL_RELATIVE_PATHS:
            unexpected_count += 1
        suffix = path.suffix.lower()
        if suffix in BLOCKED_SUFFIXES:
            blocked_count += 1
            blocked_suffixes.add(suffix)

    missing_count = len(ALLOWED_RELATIVE_PATHS - observed_paths)
    if blocked_count or symlink_count or unexpected_count or missing_count:
        details = []
        if blocked_count:
            details.append(
                f"{blocked_count} blocked tabular/data/archive file(s) "
                f"with suffix(es): {', '.join(sorted(blocked_suffixes))}"
            )
        if symlink_count:
            details.append(f"{symlink_count} symbolic link(s)")
        if unexpected_count:
            details.append(f"{unexpected_count} unreviewed file(s)")
        if missing_count:
            details.append(f"{missing_count} required site asset(s) missing")
        print("Public site file-boundary check failed: " + "; ".join(details), file=sys.stderr)
        return 1

    print(f"Public site file-boundary check passed ({file_count} static files).")
    print("This check does not replace content-level disclosure review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
