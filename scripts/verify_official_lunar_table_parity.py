"""Compare pinned python-lunardate mappings with CHARLS's official Mata table.

This source-only validator reads the public CHARLS .mmat lookup and a pinned
python-lunardate source file. It never reads CHARLS participant records.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
from datetime import date
from pathlib import Path


OFFICIAL_MMAT_SHA256 = "ebec9fe5109295a347894ec6173aa3750adbb270329f0ba357d2778636d20aa2"
LUNARDATE_014_SHA256 = "3b2eb1b90ec8107a7bd8a852a4efacd54ca4d3f5ce862145cfd5500e52ffed52"
EXPECTED_ROWS = (49_949, 1_521)
FOOTER = b"TAM\x00JBO\x00POTOM\x00"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_mata_tables(path: Path) -> list[list[tuple[str, str]]]:
    """Read the two string matrices in the pinned CHARLS mmat serialization."""
    data = path.read_bytes()
    tables: list[list[tuple[str, str]]] = []
    cursor = 0
    while True:
        object_start = data.find(b"MOTOP", cursor)
        if object_start < 0:
            break
        marker = data.find(b"MAT\x00S", object_start)
        if marker < 0:
            raise ValueError("Mata object is missing its string-matrix marker")
        rows, columns = struct.unpack_from("<II", data, marker + 5)
        if columns != 2 or rows not in EXPECTED_ROWS:
            raise ValueError(f"Unexpected Mata matrix dimensions: {rows} x {columns}")
        position = marker + 13
        pairs: list[tuple[str, str]] = []
        for _ in range(rows):
            row: list[str] = []
            for _ in range(columns):
                length = struct.unpack_from("<I", data, position)[0]
                position += 4
                if length != 8 or position + length > len(data):
                    raise ValueError("Unexpected CHARLS date-string encoding")
                value = data[position:position + length].decode("ascii")
                position += length
                if not value.isdigit():
                    raise ValueError("Lookup contains a nonnumeric date key")
                row.append(value)
            solar, lunar = row
            date(int(solar[:4]), int(solar[4:6]), int(solar[6:8]))
            lunar_year, lunar_month, lunar_day = int(lunar[:4]), int(lunar[4:6]), int(lunar[6:8])
            if not 1 <= lunar_month <= 12 or not 1 <= lunar_day <= 30:
                raise ValueError("Lookup contains a lunar date outside month/day bounds")
            pairs.append((solar, lunar))
        if data[position:position + len(FOOTER)] != FOOTER:
            raise ValueError("Unexpected Mata matrix footer")
        tables.append(pairs)
        cursor = position + len(FOOTER)
    if tuple(map(len, tables)) != EXPECTED_ROWS:
        raise ValueError(f"Expected ordinary/leap tables {EXPECTED_ROWS}; found {tuple(map(len, tables))}")
    if len(tables) != 2:
        raise ValueError(f"Expected two Mata matrices; found {len(tables)}")
    return tables


def load_lunardate(path: Path):
    spec = importlib.util.spec_from_file_location("pinned_lunardate_014", path)
    if spec is None or spec.loader is None:
        raise ValueError("Could not load pinned python-lunardate source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(official_mmat: Path, lunardate_source: Path) -> dict:
    official_hash = sha256(official_mmat)
    python_hash = sha256(lunardate_source)
    if official_hash != OFFICIAL_MMAT_SHA256:
        raise ValueError("Official CHARLS .mmat SHA-256 does not match pinned source")
    if python_hash != LUNARDATE_014_SHA256:
        raise ValueError("python-lunardate source SHA-256 does not match pinned v0.1.4")
    module = load_lunardate(lunardate_source)
    tables = read_mata_tables(official_mmat)
    summaries = []
    for name, pairs, leap in zip(("ordinary", "leap"), tables, (False, True)):
        seen: set[str] = set()
        mismatches = invalid = 0
        solar_min, solar_max = "99999999", "00000000"
        lunar_min, lunar_max = "99999999", "00000000"
        for solar, lunar in pairs:
            if lunar in seen:
                raise ValueError(f"Duplicate {name} lunar key in official lookup")
            seen.add(lunar)
            y, m, d = int(lunar[:4]), int(lunar[4:6]), int(lunar[6:8])
            try:
                converted = module.LunarDate(y, m, d, leap).toSolarDate().strftime("%Y%m%d")
            except (ValueError, IndexError, OverflowError):
                invalid += 1
                continue
            mismatches += converted != solar
            solar_min, solar_max = min(solar_min, solar), max(solar_max, solar)
            lunar_min, lunar_max = min(lunar_min, lunar), max(lunar_max, lunar)
        summaries.append({
            "table": name,
            "official_rows": len(pairs),
            "unique_lunar_keys": len(seen),
            "invalid_in_python": invalid,
            "mapping_mismatches": mismatches,
            "solar_key_range": [solar_min, solar_max],
            "lunar_key_range": [lunar_min, lunar_max],
        })
    return {
        "official_repository": "https://github.com/charls-data/lunar2solar",
        "official_repository_commit": "2284ccffdd74f057c234a446585ec32034b2d50d",
        "official_mmat_sha256": official_hash,
        "python_lunardate_version": "0.1.4",
        "python_source_sha256": python_hash,
        "tables": summaries,
        "participant_records_read": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-mmat", type=Path, required=True)
    parser.add_argument("--lunardate-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args.official_mmat, args.lunardate_source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
