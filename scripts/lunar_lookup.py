#!/usr/bin/env python3
"""Lunar-to-solar conversion from CHARLS's own published lookup table.

Why this module exists
----------------------
CHARLS's official ``lunar2solar`` Stata package (MIT licensed, vendored under
``references/charls_lunar2solar/``) ships a pre-computed lookup table
``lunar2solar.mmat``. The package's `.ado` file only re-serves that table; it
does not compute anything. Deriving Wave 1 age therefore needs nothing more
than this table.

The alternative implementation, the PyPI package ``python-lunardate``, is
**GPLv3** (it derives from a GPLv2 project). It is a useful *external* cross
check — and the parity check against the official table has already been run
with zero mismatches — but its code must not be vendored into this repository
or redistributed with it.

This module therefore depends only on the MIT-licensed official table:

    python scripts/lunar_lookup.py --self-test

Design rules
------------
* The matrix file is pinned by SHA-256; a different file is rejected.
* Unknown lunar keys return ``None`` rather than an exception, because
  "this date is not in the official table" is a data condition the caller
  must handle explicitly (CHARLS's table covers 1900-01-31 .. 2040-12-31
  solar, with a separate 1,521-row leap-month table).
* No participant data is read. Only the public lookup table.
"""
from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path

OFFICIAL_MMAT_SHA256 = "ebec9fe5109295a347894ec6173aa3750adbb270329f0ba357d2778636d20aa2"
EXPECTED_ROWS = (49_949, 1_521)
FOOTER = b"TAM\x00JBO\x00POTOM\x00"
DEFAULT_MMAT = (Path(__file__).resolve().parents[1]
                / "references" / "charls_lunar2solar" / "src" / "lunar2solar.mmat")


class LunarLookupError(ValueError):
    """The lookup table is missing, altered, or internally inconsistent."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_mata_tables(path: Path) -> list[list[tuple[str, str]]]:
    """Read the two string matrices in the pinned CHARLS ``.mmat`` file.

    Returns ``[(solar, lunar), ...]`` for the ordinary table and then for the
    leap-month table, in file order. Raises :class:`LunarLookupError` on any
    structural surprise; the caller must not guess.
    """
    data = Path(path).read_bytes()
    tables: list[list[tuple[str, str]]] = []
    cursor = 0
    while True:
        object_start = data.find(b"MOTOP", cursor)
        if object_start < 0:
            break
        marker = data.find(b"MAT\x00S", object_start)
        if marker < 0:
            raise LunarLookupError("Mata object is missing its string-matrix marker")
        rows, columns = struct.unpack_from("<II", data, marker + 5)
        if columns != 2 or rows not in EXPECTED_ROWS:
            raise LunarLookupError(f"Unexpected Mata matrix dimensions: {rows} x {columns}")
        position = marker + 13
        pairs: list[tuple[str, str]] = []
        for _ in range(rows):
            row: list[str] = []
            for _ in range(columns):
                length = struct.unpack_from("<I", data, position)[0]
                position += 4
                if length != 8 or position + length > len(data):
                    raise LunarLookupError("Unexpected date-string encoding")
                value = data[position:position + length].decode("ascii")
                position += length
                if not value.isdigit():
                    raise LunarLookupError("Lookup contains a nonnumeric date key")
                row.append(value)
            solar, lunar = row
            pairs.append((solar, lunar))
        if data[position:position + len(FOOTER)] != FOOTER:
            raise LunarLookupError("Unexpected Mata matrix footer")
        tables.append(pairs)
        cursor = position + len(FOOTER)
    if tuple(map(len, tables)) != EXPECTED_ROWS:
        raise LunarLookupError(
            f"Expected ordinary/leap tables {EXPECTED_ROWS}; found {tuple(map(len, tables))}")
    if len(tables) != 2:
        raise LunarLookupError(f"Expected two Mata matrices; found {len(tables)}")
    return tables


@dataclass(frozen=True)
class SolarDate:
    solar: str      # YYYYMMDD
    lunar: str      # YYYYMMDD
    leap: bool

    @property
    def year(self) -> int:
        return int(self.solar[:4])

    @property
    def month(self) -> int:
        return int(self.solar[4:6])

    @property
    def day(self) -> int:
        return int(self.solar[6:8])


class OfficialLunarLookup:
    """Bidirectional lookup over CHARLS's official lunar/solar table."""

    def __init__(self, path: Path | None = None, expected_sha256: str = OFFICIAL_MMAT_SHA256):
        self.path = Path(path or DEFAULT_MMAT)
        if not self.path.is_file():
            raise LunarLookupError(f"official lookup table not found: {self.path}")
        observed = sha256_file(self.path)
        if expected_sha256 and observed != expected_sha256:
            raise LunarLookupError(
                f"official lookup SHA-256 mismatch: expected {expected_sha256}, observed {observed}")
        self.sha256 = observed
        ordinary, leap = read_mata_tables(self.path)
        self._lunar_to_solar: dict[tuple[str, bool], str] = {}
        self._solar_to_lunar: dict[str, SolarDate] = {}
        for pairs, is_leap in ((ordinary, False), (leap, True)):
            for solar, lunar in pairs:
                key = (lunar, is_leap)
                if key in self._lunar_to_solar:
                    raise LunarLookupError(f"duplicate lunar key {key} in official table")
                if solar in self._solar_to_lunar:
                    raise LunarLookupError(f"duplicate solar key {solar} in official table")
                self._lunar_to_solar[key] = solar
                self._solar_to_lunar[solar] = SolarDate(solar=solar, lunar=lunar, leap=is_leap)

    # -- introspection ----------------------------------------------------
    @property
    def counts(self) -> dict[str, int]:
        leap = sum(1 for value in self._solar_to_lunar.values() if value.leap)
        return {"total": len(self._solar_to_lunar),
                "ordinary": len(self._solar_to_lunar) - leap,
                "leap": leap}

    # -- conversion -------------------------------------------------------
    @staticmethod
    def _key(year: int, month: int, day: int) -> str:
        return f"{year:04d}{month:02d}{day:02d}"

    def to_solar(self, year: int, month: int, day: int, leap: bool = False) -> str | None:
        """Lunar Y/M/D -> solar ``YYYYMMDD``, or ``None`` if not in the table."""
        if not (1 <= month <= 12 and 1 <= day <= 30):
            return None
        return self._lunar_to_solar.get((self._key(year, month, day), leap))

    def from_solar(self, year: int, month: int, day: int) -> SolarDate | None:
        """Solar Y/M/D -> :class:`SolarDate`, or ``None`` if outside the table."""
        return self._solar_to_lunar.get(self._key(year, month, day))

    def iter_solar(self):
        for value in self._solar_to_lunar.values():
            yield value


def _self_test() -> int:
    lookup = OfficialLunarLookup()
    print(f"table: {lookup.path}")
    print(f"sha256: {lookup.sha256}")
    print(f"counts: {lookup.counts}")
    checks = [
        ("lunar 1900-01-01 -> solar 1900-01-31", lookup.to_solar(1900, 1, 1), "19000131"),
        ("lunar 1900-08-01 (leap) -> solar 1900-09-24", lookup.to_solar(1900, 8, 1, True), "19000924"),
        ("lunar 1976-08-08 (leap) -> solar 1976-10-01", lookup.to_solar(1976, 8, 8, True), "19761001"),
        ("solar 1976-10-01 -> lunar 1976-08-08 leap", getattr(lookup.from_solar(1976, 10, 1), "lunar", None), "19760808"),
        ("unknown lunar 1899-12-01 -> None", lookup.to_solar(1899, 12, 1), None),
    ]
    failures = 0
    for label, observed, expected in checks:
        status = "ok" if observed == expected else "FAIL"
        failures += observed != expected
        print(f"  [{status}] {label}: {observed!r} (expected {expected!r})")
    return 1 if failures else 0


def main() -> int:
    import sys
    if "--self-test" in sys.argv:
        return _self_test()
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
