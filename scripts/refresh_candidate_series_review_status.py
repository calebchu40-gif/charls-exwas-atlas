"""Refresh series-level review summaries from the final wave-field catalog."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"


def summarize_review_status(values: list[str]) -> str:
    raw = [str(value or "").strip() for value in values]
    reviews = sorted({value for value in raw if value})
    blocked = next((value for value in reviews if any(
        marker in value.lower() for marker in ("do not analyze", "unresolved", "conflict")
    )), "")
    if blocked:
        return blocked
    partial = next((value for value in reviews if value.startswith(
        "official Codebook extraction exposes only a partial response-code set"
    )), "")
    if partial:
        return partial
    pending = any(not value or value.lower() == "not yet reviewed" for value in raw)
    reviewed = [value for value in reviews if value.lower() != "not yet reviewed"]
    if pending:
        if reviewed:
            return "not yet reviewed for at least one source wave; other wave states: " + " | ".join(reviewed)
        return "not yet reviewed"
    if len(reviews) == 1:
        return reviews[0]
    if reviews:
        return "wave-specific review states: " + " | ".join(reviews)
    return "not yet reviewed"


def main() -> None:
    fields_path = AUDIT / "charls_atlas_candidate_fields_v0.csv"
    series_csv = AUDIT / "charls_atlas_candidate_series_v0.csv"
    series_json = AUDIT / "charls_atlas_candidate_series_v0.json"
    with fields_path.open(encoding="utf-8-sig", newline="") as stream:
        fields = list(csv.DictReader(stream))
    with series_csv.open(encoding="utf-8-sig", newline="") as stream:
        series = list(csv.DictReader(stream))
    indexed: dict[tuple[str, str, str, str], list[dict[str, str]]] = {}
    for row in fields:
        key = (row.get("epcf", ""), row.get("category", ""), row.get("subcategory", ""),
               row.get("Variable.Name", "").lower())
        indexed.setdefault(key, []).append(row)
    changed = 0
    for row in series:
        key = (row.get("epcf", ""), row.get("category", ""), row.get("subcategory", ""),
               row.get("Variable.Name", "").lower())
        source_rows = indexed.get(key, [])
        if not source_rows:
            raise SystemExit(f"series row has no source fields: {key}")
        status = summarize_review_status([item.get("Value.Label.Review", "") for item in source_rows])
        if row.get("value_label_review", "") != status:
            row["value_label_review"] = status
            changed += 1
    with series_csv.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(series[0]))
        writer.writeheader()
        writer.writerows(series)
    series_json.write_text(json.dumps(series, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"refreshed wave-aware review status for {changed} of {len(series)} candidate series")


if __name__ == "__main__":
    main()
