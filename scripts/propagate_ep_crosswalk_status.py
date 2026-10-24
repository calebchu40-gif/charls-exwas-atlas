"""Propagate source-backed E/P crosswalk status into generated catalogues."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
DIST = ROOT / "site-prototype" / "dist"
CSV_PATH = AUDIT / "charls_atlas_candidate_fields_v0.csv"
JSON_PATH = AUDIT / "charls_atlas_candidate_fields_v0.json"
MASTER_PATH = DIST / "catalog.json"


def identity(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(row.get(field, "")) for field in (
        "Source.Wave", "Variable.Name", "epcf", "category", "subcategory", "Data.File.Name"
    ))


def is_ep(row: dict[str, Any]) -> bool:
    roles = {role.strip().lower() for role in str(row.get("epcf", "")).split(",")}
    return bool(roles & {"e", "p"})


def update_row(row: dict[str, Any]) -> bool:
    if not is_ep(row) or not str(row.get("Concept.Mapping.Source", "")).strip():
        return False
    changed = False
    status = str(row.get("Candidate.Status", "")).strip()
    if status.lower().startswith(("automated discovery", "automated keyword discovery")):
        row["Candidate.Status"] = f"concept-source crosswalk candidate; see {row['Concept.Mapping.Source']}"
        changed = True
    flag = str(row.get("Review.Flag", "")).strip()
    if "approved test variable" not in flag and "not analytic inclusion" not in flag:
        caution = "documented source mapping is a candidate only; not an approved test variable"
        row["Review.Flag"] = f"{flag}; {caution}" if flag else caution
        changed = True
    return changed


def update_json_list(path: Path, counts: dict[str, int]) -> list[dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    for row in rows:
        if update_row(row):
            counts["json_rows"] = counts.get("json_rows", 0) + 1
    path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return rows


def main() -> int:
    counts: dict[str, int] = {}
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    for row in rows:
        if update_row(row):
            counts["csv_rows"] = counts.get("csv_rows", 0) + 1
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    update_json_list(JSON_PATH, counts)
    update_json_list(MASTER_PATH, counts)
    print(json.dumps(counts, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
