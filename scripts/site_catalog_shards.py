"""Build role-specific static catalog files from the audited master catalog."""

from __future__ import annotations

import json
import csv
from pathlib import Path
from typing import Any


ROLES = ("e", "p", "c")


def rows_for_role(records: list[dict[str, Any]], role: str) -> list[dict[str, Any]]:
    if role not in ROLES:
        raise ValueError(f"unsupported catalog role: {role}")
    return [
        record for record in records
        if role in {part.strip().lower() for part in str(record.get("epcf", "")).split(",")}
    ]


def write_role_catalogs(records: list[dict[str, Any]], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for role in ROLES:
        path = output_dir / f"catalog_{role}.json"
        path.write_text(
            json.dumps(rows_for_role(records, role), ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        paths[role] = path
    return paths


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    master_path = root / "site-prototype" / "dist" / "catalog.json"
    candidate_path = root / "audit" / "charls_atlas_candidate_fields_v0.csv"
    with candidate_path.open(encoding="utf-8-sig", newline="") as stream:
        audited = list(csv.DictReader(stream))
    audited_by_key = {
        (row.get("Source.Wave", ""), row.get("Variable.Name", "").lower(), row.get("epcf", ""),
         row.get("category", ""), row.get("subcategory", "")): row
        for row in audited
    }
    # Preserve the source-row layout used by review tools and add the browser's
    # lower-case search fields. Refresh review text from the audited wave-level
    # CSV so cross-wave aggregation cannot flatten distinct labels/caveats.
    records = json.loads(master_path.read_text(encoding="utf-8"))
    existing_keys = {
        (str(item.get("Source.Wave", "")), str(item.get("Variable.Name", "")).lower(),
         str(item.get("epcf", "")), str(item.get("category", "")), str(item.get("subcategory", "")))
        for item in records
    }
    # Some reviewed crosswalks add wave-specific candidate fields after the
    # aggregate master catalog was last generated. Carry those audited rows
    # into the public shards instead of silently dropping them.
    appended = 0
    for row in audited:
        roles = {part.strip().lower() for part in row.get("epcf", "").split(",")}
        if not roles.intersection({"e", "p"}):
            continue
        key = (row.get("Source.Wave", ""), row.get("Variable.Name", "").lower(),
               row.get("epcf", ""), row.get("category", ""), row.get("subcategory", ""))
        if key not in existing_keys:
            records.append(dict(row))
            existing_keys.add(key)
            appended += 1
    for item in records:
        key = (str(item.get("Source.Wave", "")), str(item.get("Variable.Name", "")).lower(),
               str(item.get("epcf", "")), str(item.get("category", "")), str(item.get("subcategory", "")))
        row = audited_by_key.get(key, {})
        item["waves"] = str(item.get("Source.Wave", ""))
        item["wave_count"] = 1
        item["source_modules"] = str(item.get("Data.File.Name", ""))
        for target, source in {
            "value_labels": "Value.Labels", "value_label_source": "Value.Label.Source",
            "value_label_review": "Value.Label.Review", "harmonization_status": "Harmonization.Status",
            "candidate_concept_ids": "Concept.ID.Candidates", "candidate_concept_alias_ids": "Concept.Alias.IDs",
            "candidate_concept_labels": "Concept.Label.Candidates", "candidate_concept_units": "Concept.Unit.Candidates",
            "concept_mapping_caveats": "Concept.Mapping.Caveat", "concept_mapping_collision": "Concept.Mapping.Collision",
            "concept_mapping_relationship": "Concept.Mapping.Relationship",
        }.items():
            item[target] = row.get(source, item.get(source, ""))
            if source in row and row[source] != "":
                item[source] = row[source]
    paths = write_role_catalogs(records, master_path.parent)
    if appended:
        master_path.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"audited source rows appended to master catalog: {appended}")
    for role, path in paths.items():
        print(f"catalog_{role}: rows={len(rows_for_role(records, role))}; bytes={path.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
