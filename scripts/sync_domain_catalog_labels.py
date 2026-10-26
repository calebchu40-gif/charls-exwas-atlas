#!/usr/bin/env python3
"""Copy uniquely reviewed value-label metadata into duplicated domain views.

The canonical E/P catalogue remains the source of truth. This only fills blank
label fields in domain-specific JSON after matching the exact CHARLS wave and
variable name; it never changes concept or analysis eligibility metadata.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site-prototype" / "dist"
AUDIT = ROOT / "audit"
DOMAIN_FILES = ("food_environment_v1.json", "social_exposures_v1.json")


def normalize_code(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sync(catalog: list[dict[str, Any]], domain_data: list[dict[str, Any]]) -> dict[str, int]:
    index: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in catalog:
        key = (str(row.get("Source.Wave") or ""), normalize_code(row.get("Variable.Name")))
        if key[0] and key[1] and str(row.get("Value.Labels") or "").strip():
            index[key].append(row)

    stats = {"fields": 0, "filled": 0, "existing": 0, "no_match": 0, "ambiguous": 0}
    for concept in domain_data:
        for field in concept.get("source_fields", []):
            stats["fields"] += 1
            if str(field.get("value_labels") or "").strip():
                stats["existing"] += 1
                continue
            key = (str(field.get("wave") or ""), normalize_code(field.get("code")))
            candidates = index.get(key, [])
            # Require all matching canonical entries to agree on the full
            # provenance tuple. Multiple identical catalogue records are safe;
            # disagreement must remain a human review item.
            tuples = {
                (str(row.get("Value.Labels") or "").strip(),
                 str(row.get("Value.Label.Source") or "").strip(),
                 str(row.get("Value.Label.Review") or "").strip())
                for row in candidates
            }
            if not tuples:
                stats["no_match"] += 1
                continue
            if len(tuples) != 1:
                stats["ambiguous"] += 1
                continue
            labels, source, review = next(iter(tuples))
            if not labels:
                stats["no_match"] += 1
                continue
            field["value_labels"] = labels
            if source and not str(field.get("value_label_source") or "").strip():
                field["value_label_source"] = source
            if review and not str(field.get("value_label_status") or "").strip():
                field["value_label_status"] = review
            stats["filled"] += 1
    return stats


def main() -> int:
    catalog = load_json(SITE / "catalog.json")
    summary: dict[str, dict[str, int]] = {}
    for filename in DOMAIN_FILES:
        path = SITE / filename
        domain_data = load_json(path)
        summary[filename] = sync(catalog, domain_data)
        path.write_text(json.dumps(domain_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{filename}: {summary[filename]}", flush=True)
    report = {"source": "catalog.json Value.Labels / Value.Label.Source / Value.Label.Review",
              "matching": "exact wave + normalized CHARLS variable code; unique provenance tuple only",
              "files": summary}
    (AUDIT / "domain_catalog_label_sync_report_v1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote audit/domain_catalog_label_sync_report_v1.json: {summary}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
