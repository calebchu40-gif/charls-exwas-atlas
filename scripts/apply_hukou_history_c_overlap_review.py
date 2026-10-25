"""Link source-reviewed historical hukou/location E fields to exact C rows."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CROSSWALK = AUDIT / "social_context_remainder_crosswalk_v1.csv"
OUTPUT = AUDIT / "hukou_history_c_overlap_review_v1.csv"
EXPECTED = {
    ("2011", "bc011", "demographic_background"), ("2013", "bc011", "demographic_background"),
    ("2011", "bc013", "demographic_background"), ("2013", "bc013", "demographic_background"),
    ("2011", "bc014", "demographic_background"),
    ("2015", "bc001_w3_2", "demographic_background"), ("2018", "bc001_w3_2", "demographic_background"),
}


def load_items() -> list[dict[str, str]]:
    crosswalk = pd.read_csv(CROSSWALK, dtype=str, encoding="utf-8-sig").fillna("")
    candidates = pd.read_csv(AUDIT / "charls_atlas_candidate_fields_v0.csv", dtype=str, encoding="utf-8-sig").fillna("")
    role_keys = {
        (str(r["Source.Wave"]), str(r["Variable.Name"]).lower(), str(r["Data.File.Name"]).lower(), str(r["epcf"]).lower())
        for _, r in candidates.iterrows()
    }
    items = []
    for row in crosswalk.to_dict("records"):
        key = (str(row["wave"]), str(row["code"]).lower(), str(row["module"]).lower())
        if key + ("c",) not in role_keys or key + ("e",) not in role_keys:
            continue
        source_text = str(row.get("value_label_source", ""))
        sources = [p.strip() for p in source_text.split(";") if p.strip().startswith("sources_official/")]
        if len(sources) < 2 or any(not (ROOT / p).is_file() for p in sources):
            raise SystemExit(f"Missing official questionnaire/Codebook evidence for {key}: {sources}")
        status, caveat = str(row.get("mapping_status", "")), str(row.get("caveat", ""))
        if "reviewed" not in status.lower() or not any(token in caveat.lower() for token in ("asked only", "only asked", "route only when")):
            raise SystemExit(f"Hukou-history overlap lacks reviewed route details for {key}")
        items.append({
            "wave": key[0], "code": str(row["code"]), "module": str(row["module"]),
            "concept_id": str(row["concept_id"]), "concept_label": str(row["concept_label"]),
            "unit": str(row.get("unit", "")), "value_labels": str(row.get("value_labels", "")),
            "value_semantics": str(row.get("value_semantics", "")), "mapping_status": status,
            "caveat": caveat, "official_sources": "; ".join(sources),
        })
    found = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in items}
    if found != EXPECTED:
        raise SystemExit(f"Hukou-history C/E overlap mismatch: missing={EXPECTED-found}; extra={found-EXPECTED}")
    return items


def update(row: dict[str, object], item: dict[str, str]) -> None:
    note = f"{item['value_semantics']}. {item['caveat']}".strip(". ")
    row.update({
        "category": "source-mapped candidate context",
        "subcategory": "historical hukou/location context exposure overlap",
        "Candidate.Status": f"C metadata; exact source field is linked to a wave-specific historical hukou/location candidate; preserve question route and categories; not an adjustment recommendation; concept={item['concept_id']}",
        "Harmonization.Status": note,
        "Review.Flag": "Historical hukou/residential context with a route-specific denominator; do not interpret as current hukou or measured ambient pollution. The same field is an E candidate and must not adjust for itself. Preserve wave-specific reference categories and unresolved cross-wave differences.",
        "Unit": item["unit"], "Value.Labels": item["value_labels"], "Value.Label.Source": item["official_sources"],
        "Value.Label.Review": item["mapping_status"], "Concept.ID.Candidates": item["concept_id"],
        "Concept.Mapping.Source": "audit/social_context_remainder_crosswalk_v1.csv",
        "Concept.Mapping.Status": item["mapping_status"], "Concept.Mapping.Caveat": item["caveat"],
        "value_labels": item["value_labels"], "value_label_source": item["official_sources"],
        "value_label_review": item["mapping_status"], "harmonization_status": note,
        "candidate_concept_ids": item["concept_id"],
        "concept_mapping_sources": "audit/social_context_remainder_crosswalk_v1.csv",
        "concept_mapping_statuses": item["mapping_status"], "concept_mapping_caveats": item["caveat"],
    })


def propagate() -> None:
    items = load_items()
    targets = {(r["wave"], r["code"].lower(), r["module"].lower()): r for r in items}
    for rel in (
        "audit/charls_atlas_candidate_fields_v0.csv", "audit/charls_atlas_candidate_fields_v0.json",
        "site-prototype/dist/catalog.json", "site-prototype/dist/catalog_c.json",
    ):
        path = ROOT / rel
        if not path.exists():
            continue
        count = 0
        if path.suffix == ".csv":
            frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            for key, item in targets.items():
                mask = (frame["Source.Wave"].eq(key[0]) & frame["Variable.Name"].str.lower().eq(key[1]) &
                        frame["Data.File.Name"].str.lower().eq(key[2]) & frame["epcf"].str.lower().eq("c"))
                for idx in frame.index[mask]:
                    data = frame.loc[idx].to_dict()
                    update(data, item)
                    for field, value in data.items():
                        if field in frame.columns:
                            frame.at[idx, field] = value
                count += int(mask.sum())
            if count != 7:
                raise SystemExit(f"Expected 7 C overlap rows in {rel}; updated {count}")
            frame.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")).lower())
                if key in targets and str(row.get("epcf", "")).lower() == "c":
                    update(row, targets[key])
                    count += 1
            if count != 7:
                raise SystemExit(f"Expected 7 C overlap rows in {rel}; updated {count}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(items[0]))
        writer.writeheader()
        writer.writerows(items)
    print("Reviewed seven exact-wave historical hukou/location C/E overlaps; conditional routes and wave differences retained.")


if __name__ == "__main__":
    propagate()
