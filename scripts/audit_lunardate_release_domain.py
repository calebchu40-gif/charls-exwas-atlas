"""Compare two external python-lunardate source releases on CHARLS's stated date domain.

This synthetic-only provenance audit imports source files supplied by the caller;
it does not vendor, install, or redistribute the GPL-licensed library. It prints
aggregate coverage and mismatch counts only, never the generated date mapping.
It cannot establish cell-by-cell parity with CHARLS's Stata Mata lookup table.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


DOMAIN_START = 19000101
DOMAIN_END = 20401128
EXPECTED_ORDINARY_ROWS = 49_949
EXPECTED_LEAP_ROWS = 1_521
EXPECTED_OFFICIAL_ADO_SHA256 = "14a3d7e28b3143e7f7276fecbd8f226e79ee77f395ccef1b0bcd35a453b932a1"
EXPECTED_OFFICIAL_MMAT_SHA256 = "ebec9fe5109295a347894ec6173aa3750adbb270329f0ba357d2778636d20aa2"
EXPECTED_GRID_ROWS = 141 * 12 * 31


def load_source(path: Path, name: str) -> tuple[ModuleType, str]:
    source = path.read_bytes()
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load source module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, hashlib.sha256(source).hexdigest()


def enumerate_domain(module: ModuleType) -> dict[tuple[int, int, int, bool], str]:
    converted: dict[tuple[int, int, int, bool], str] = {}
    converter = module.LunarDate
    for year in range(1900, 2041):
        for month in range(1, 13):
            for is_leap in (False, True):
                for day in range(1, 31):
                    numeric = year * 10_000 + month * 100 + day
                    if numeric < DOMAIN_START or numeric > DOMAIN_END:
                        continue
                    try:
                        solar = converter(year, month, day, is_leap).toSolarDate()
                    except (ValueError, OverflowError):
                        continue
                    converted[(year, month, day, is_leap)] = solar.isoformat()
    return converted


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_official_grid(path: Path) -> tuple[dict[tuple[int, int, int, bool], str], dict[str, Any]]:
    ordinary: dict[tuple[int, int, int, bool], str] = {}
    leap: dict[tuple[int, int, int, bool], str] = {}
    seen_dates: set[tuple[int, int, int]] = set()
    rows = 0
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["lunar_date", "solar_ordinary", "solar_leap"]:
            raise ValueError("Official Stata grid CSV must have the expected three synthetic-date columns")
        for row in reader:
            rows += 1
            lunar = str(row["lunar_date"]).strip()
            if len(lunar) != 8 or not lunar.isdigit():
                raise ValueError("Official grid contains an invalid synthetic date key")
            year, month, day = int(lunar[:4]), int(lunar[4:6]), int(lunar[6:])
            if not (1900 <= year <= 2040 and 1 <= month <= 12 and 1 <= day <= 31):
                raise ValueError("Official grid contains a key outside the synthetic YYYYMMDD grid")
            date_key = (year, month, day)
            if date_key in seen_dates:
                raise ValueError("Official grid contains a duplicate synthetic date key")
            seen_dates.add(date_key)
            numeric = year * 10_000 + month * 100 + day
            if not (19000101 <= numeric <= DOMAIN_END):
                continue
            for is_leap, column, destination in (
                (False, "solar_ordinary", ordinary),
                (True, "solar_leap", leap),
            ):
                converted = str(row[column]).strip()
                if not converted:
                    continue
                if len(converted) != 8 or not converted.isdigit():
                    raise ValueError("Official grid contains an invalid synthetic conversion")
                key = (year, month, day, is_leap)
                value = f"{converted[:4]}-{converted[4:6]}-{converted[6:]}"
                if key in destination:
                    raise ValueError("Official grid contains a duplicate mapping key")
                destination[key] = value
    if rows != EXPECTED_GRID_ROWS:
        raise ValueError(f"Official grid has {rows} rows; expected {EXPECTED_GRID_ROWS} synthetic keys")
    expected_dates = {
        (year, month, day)
        for year in range(1900, 2041)
        for month in range(1, 13)
        for day in range(1, 32)
    }
    if seen_dates != expected_dates:
        raise ValueError("Official grid does not cover the full synthetic YYYYMMDD key set")
    mappings = {**ordinary, **leap}
    return mappings, {
        "synthetic_grid_rows": rows,
        "official_ordinary_mapping_count": len(ordinary),
        "official_leap_mapping_count": len(leap),
        "official_mapped_keys_unique": True,
    }


def audit(
    first: Path,
    second: Path,
    official_grid: Path | None = None,
    official_ado: Path | None = None,
    official_mmat: Path | None = None,
) -> dict[str, Any]:
    module_a, sha_a = load_source(first, "lunardate_release_a")
    module_b, sha_b = load_source(second, "lunardate_release_b")
    map_a = enumerate_domain(module_a)
    map_b = enumerate_domain(module_b)
    keys_a, keys_b = set(map_a), set(map_b)
    shared = keys_a & keys_b
    ordinary_a = sum(not key[3] for key in keys_a)
    leap_a = sum(key[3] for key in keys_a)
    ordinary_b = sum(not key[3] for key in keys_b)
    leap_b = sum(key[3] for key in keys_b)
    mismatch_count = sum(map_a[key] != map_b[key] for key in shared)
    report: dict[str, Any] = {
        "scope": "synthetic exhaustive domain comparison; no respondent data",
        "documented_lunar_input_domain": [DOMAIN_START, DOMAIN_END],
        "source_sha256": {"first": sha_a, "second": sha_b},
        "first_release": {
            "ordinary_mapping_count": ordinary_a,
            "leap_mapping_count": leap_a,
            "total_mapping_count": len(keys_a),
        },
        "second_release": {
            "ordinary_mapping_count": ordinary_b,
            "leap_mapping_count": leap_b,
            "total_mapping_count": len(keys_b),
        },
        "mapping_key_coverage_equal": keys_a == keys_b,
        "shared_key_mapping_mismatches": mismatch_count,
        "matches_official_matrix_dimensions": (
            ordinary_a == ordinary_b == EXPECTED_ORDINARY_ROWS
            and leap_a == leap_b == EXPECTED_LEAP_ROWS
        ),
        "direct_cellwise_comparison_to_charls_mmat": False,
        "participant_data_accessed": False,
    }
    supplied = (official_grid is not None, official_ado is not None, official_mmat is not None)
    if any(supplied) and not all(supplied):
        raise ValueError("Direct comparison requires the Stata grid CSV plus the pinned official ado and mmat files")
    if official_grid is not None and official_ado is not None and official_mmat is not None:
        ado_sha = hash_file(official_ado)
        mmat_sha = hash_file(official_mmat)
        if ado_sha != EXPECTED_OFFICIAL_ADO_SHA256 or mmat_sha != EXPECTED_OFFICIAL_MMAT_SHA256:
            raise ValueError("Official CHARLS ado/mat source hash does not match the pinned repository snapshot")
        official_map, official_info = load_official_grid(official_grid)
        ordinary = {key: value for key, value in official_map.items() if not key[3]}
        leap = {key: value for key, value in official_map.items() if key[3]}
        dimensions_match = (
            len(ordinary) == EXPECTED_ORDINARY_ROWS and len(leap) == EXPECTED_LEAP_ROWS
        )
        if not dimensions_match:
            raise ValueError("Official grid mapping dimensions do not match the pinned CHARLS Mata tables")
        comparisons = {}
        for label, python_map in (("first", map_a), ("second", map_b)):
            differences = sum(
                python_map.get(key) != official_map.get(key)
                for key in set(python_map) | set(official_map)
            )
            comparisons[label] = {
                "mapping_key_coverage_equal": set(python_map) == set(official_map),
                "cellwise_mapping_mismatches": differences,
                "matches_official_grid": differences == 0 and set(python_map) == set(official_map),
            }
        report["direct_official_stata_grid_comparison"] = {
            **official_info,
            "official_source_commit": "2284ccffdd74f057c234a446585ec32034b2d50d",
            "official_ado_sha256": ado_sha,
            "official_mmat_sha256": mmat_sha,
            "official_dimensions_match_documented_tables": dimensions_match,
            "python_release_comparisons": comparisons,
            "participant_data_accessed": False,
        }
        report["direct_cellwise_comparison_to_charls_mmat"] = True
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first_source", type=Path)
    parser.add_argument("second_source", type=Path)
    parser.add_argument("--official-grid-csv", type=Path)
    parser.add_argument("--official-ado", type=Path)
    parser.add_argument("--official-mmat", type=Path)
    parser.add_argument("--output", type=Path, help="Optional aggregate JSON report path")
    args = parser.parse_args()
    report = audit(
        args.first_source,
        args.second_source,
        args.official_grid_csv,
        args.official_ado,
        args.official_mmat,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if not report["mapping_key_coverage_equal"] or report["shared_key_mapping_mismatches"]:
        raise SystemExit("Source releases differ over shared valid lunar-date keys")
    if not report["matches_official_matrix_dimensions"]:
        raise SystemExit("Enumerated mapping dimensions do not match the CHARLS lookup sizes")
    official = report.get("direct_official_stata_grid_comparison")
    if official and not all(item["matches_official_grid"] for item in official["python_release_comparisons"].values()):
        raise SystemExit("Python conversion differs from the official CHARLS Stata grid")


if __name__ == "__main__":
    main()
