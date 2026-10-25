"""Apply field-specific, source-backed mortality metadata to catalog rows."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
SOURCE = AUDIT / "mortality_endpoint_crosswalk_v1.csv"
TARGETS = [
    AUDIT / "charls_atlas_candidate_fields_v0.csv",
    AUDIT / "charls_atlas_candidate_fields_v0.json",
    ROOT / "site-prototype/dist/catalog.json",
]


def read_source() -> list[dict[str, str]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 11 or len({(r["wave"], r["code"], r["role"]) for r in rows}) != 11:
        raise ValueError("Mortality crosswalk must contain exactly 11 unique wave-field-role rows")
    return rows


def apply(row: dict, by_key: dict[tuple[str, str, str], dict[str, str]]) -> bool:
    key = (
        str(row.get("Source.Wave", "")),
        str(row.get("Variable.Name", "")).lower(),
        str(row.get("epcf", "")).lower(),
    )
    item = by_key.get(key)
    if item is None:
        return False
    row["Value.Labels"] = item["value_labels"]
    row["Value.Label.Source"] = item["source_document"]
    row["Value.Label.Review"] = item["value_label_status"]
    row["Harmonization.Status"] = item["value_semantics"]
    row["Concept.Mapping.Caveat"] = item["caveat"]
    row["subcategory"] = item["subcategory"]
    return True


def main() -> None:
    source_rows = read_source()
    by_key = {(r["wave"], r["code"].lower(), r["role"].lower()): r for r in source_rows}
    for path in TARGETS:
        if path.suffix == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                fields = list(reader.fieldnames or [])
                rows = list(reader)
            matched = sum(apply(row, by_key) for row in rows)
            if matched != len(source_rows):
                raise ValueError(f"{path}: expected {len(source_rows)} mortality rows; matched {matched}")
            with path.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
        else:
            rows = json.loads(path.read_text(encoding="utf-8"))
            matched = sum(apply(row, by_key) for row in rows)
            if matched != len(source_rows):
                raise ValueError(f"{path}: expected {len(source_rows)} mortality rows; matched {matched}")
            path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"Applied mortality source review to {matched} rows in {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
