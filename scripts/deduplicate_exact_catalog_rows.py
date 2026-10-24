"""Remove only byte-equivalent duplicate rows from generated field catalogs."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
JSON_PATHS = (
    ROOT / "audit/charls_atlas_candidate_fields_v0.json",
    ROOT / "site-prototype/dist/catalog.json",
)


def unique_rows(rows: list[dict]) -> tuple[list[dict], int]:
    seen: set[str] = set()
    kept = []
    for row in rows:
        signature = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if signature in seen:
            continue
        seen.add(signature)
        kept.append(row)
    return kept, len(rows) - len(kept)


def main() -> int:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    rows, removed = unique_rows(rows)
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{CSV_PATH.relative_to(ROOT)}: removed {removed} exact duplicate rows")

    for path in JSON_PATHS:
        rows = json.loads(path.read_text(encoding="utf-8"))
        rows, removed = unique_rows(rows)
        path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{path.relative_to(ROOT)}: removed {removed} exact duplicate rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
