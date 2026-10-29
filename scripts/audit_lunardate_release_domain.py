"""Compare two external python-lunardate source releases on CHARLS's stated date domain.

This synthetic-only provenance audit imports source files supplied by the caller;
it does not vendor, install, or redistribute the GPL-licensed library. It prints
aggregate coverage and mismatch counts only, never the generated date mapping.
It cannot establish cell-by-cell parity with CHARLS's Stata Mata lookup table.
"""
from __future__ import annotations

import argparse
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


def audit(first: Path, second: Path) -> dict[str, Any]:
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
    return {
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first_source", type=Path)
    parser.add_argument("second_source", type=Path)
    parser.add_argument("--output", type=Path, help="Optional aggregate JSON report path")
    args = parser.parse_args()
    report = audit(args.first_source, args.second_source)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if not report["mapping_key_coverage_equal"] or report["shared_key_mapping_mismatches"]:
        raise SystemExit("Source releases differ over shared valid lunar-date keys")
    if not report["matches_official_matrix_dimensions"]:
        raise SystemExit("Enumerated mapping dimensions do not match the CHARLS lookup sizes")


if __name__ == "__main__":
    main()
