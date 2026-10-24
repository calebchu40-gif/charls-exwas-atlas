"""Publish a minimal Child-module field-presence manifest from the local metadata inventory."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-catalog", type=Path, default=ROOT / "audit/raw_variable_catalog_v1.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "audit/child_module_field_presence_v1.csv")
    args = parser.parse_args()

    requested = set()
    for filename in ("child_roster_context_crosswalk_v1.csv", "child_hukou_lifecourse_crosswalk_v1.csv"):
        for row in read_rows(ROOT / "audit" / filename):
            requested.add((row["wave"].strip(), row["code"].strip().lower()))
    requested.update((wave, code) for wave in ("2013", "2015") for code in ("id", "childid", "hhmemberid"))

    present = {
        (row["wave"].strip(), row["variable"].strip().lower(), row["module"].strip().lower())
        for row in read_rows(args.raw_catalog)
    }
    missing = sorted((wave, code) for wave, code in requested if (wave, code, "child") not in present)
    if missing:
        raise SystemExit(f"Requested fields are missing from the official Child-module inventory: {missing}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("wave", "variable", "module", "source_status"))
        writer.writerows((wave, code, "Child", "official raw variable inventory; field presence only")
                         for wave, code in sorted(requested))
    print(f"wrote {len(requested)} non-participant field-presence rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
