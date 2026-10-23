"""Restore the separately audited internet/digital behavior crosswalk after rebuilds."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
REVIEW = AUDIT / "internet_digital_exposure_crosswalk_v1.csv"
SOCIAL = AUDIT / "social_exposure_crosswalk_v1.csv"
RAW = AUDIT / "raw_variable_catalog_v1.csv"
JSON_PATH = ROOT / "site-prototype/dist/social_exposures_v1.json"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def main() -> None:
    columns, reviewed = read_csv(REVIEW)
    _, raw = read_csv(RAW)
    raw_keys = {(row["wave"], row["variable"].lower(), row["module"].lower()) for row in raw}
    keys = [(row["wave"], row["code"].lower(), row["concept_id"]) for row in reviewed]
    if len(keys) != len(set(keys)):
        raise SystemExit("duplicate wave/code/concept in reviewed internet/digital crosswalk")
    for row in reviewed:
        key = (row["wave"], row["code"].lower(), row["module"].lower())
        if key not in raw_keys:
            raise SystemExit(f"reviewed internet/digital field lacks official source catalog row: {key}")
    concept_ids = {row["concept_id"] for row in reviewed}
    social_columns, social_rows = read_csv(SOCIAL)
    kept = [row for row in social_rows if row.get("concept_id") not in concept_ids]
    kept.extend(reviewed)
    social_keys = [(row["wave"], row["code"].lower(), row["concept_id"]) for row in kept]
    if len(social_keys) != len(set(social_keys)):
        raise SystemExit("duplicate wave/code/concept after restoring internet/digital crosswalk")
    output_columns = list(social_columns)
    for name in columns:
        if name not in output_columns:
            output_columns.append(name)
    for row in kept:
        for name in output_columns:
            row.setdefault(name, "")
    with SOCIAL.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(kept)

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in reviewed:
        grouped[row["concept_id"]].append(row)
    concepts = []
    for concept_id, fields in grouped.items():
        concepts.append({
            "concept_id": concept_id,
            "label": fields[0]["concept_label"],
            "domain": fields[0]["domain"],
            "caveat": fields[0]["caveat"],
            "source_fields": [{
                "wave": row["wave"], "code": row["code"], "module": row["module"],
                "source_label": row["source_label"], "note": row["mapping_status"],
                "value_labels": row["value_labels"], "value_semantics": row["value_semantics"],
                "questionnaire_source": row["questionnaire_source"],
                "value_label_source": row["value_label_source"],
            } for row in fields],
        })
    existing = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    existing = [item for item in existing if item.get("concept_id") not in concept_ids]
    existing.extend(concepts)
    JSON_PATH.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"restored {len(reviewed)} reviewed internet/digital source rows across {len(concepts)} concepts")


if __name__ == "__main__":
    main()
