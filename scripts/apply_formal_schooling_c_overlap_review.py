"""Keep reviewed formal-schooling C/E overlaps source-linked and role-specific."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CROSSWALK = AUDIT / "formal_schooling_lifecourse_crosswalk_v1.csv"
OUTPUT = AUDIT / "formal_schooling_c_overlap_review_v1.csv"
BASE_STATUS = (
    "C metadata; exact source field is mapped to a wave-specific formal-schooling candidate; "
    "preserve its question route and response definition; not an adjustment recommendation"
)


def load_items() -> list[dict[str, str]]:
    frame = pd.read_csv(CROSSWALK, dtype=str, encoding="utf-8-sig").fillna("")
    candidate = pd.read_csv(AUDIT / "charls_atlas_candidate_fields_v0.csv", dtype=str, encoding="utf-8-sig").fillna("")
    c_keys = {
        (str(r["Source.Wave"]), str(r["Variable.Name"]).lower(), str(r["Data.File.Name"]).lower())
        for _, r in candidate.iterrows() if str(r["epcf"]).lower() == "c"
    }
    e_keys = {
        (str(r["Source.Wave"]), str(r["Variable.Name"]).lower(), str(r["Data.File.Name"]).lower())
        for _, r in candidate.iterrows() if str(r["epcf"]).lower() == "e"
    }
    items: list[dict[str, str]] = []
    for row in frame.to_dict("records"):
        key = (str(row["wave"]), str(row["code"]).lower(), str(row["module"]).lower())
        if key not in c_keys or key not in e_keys:
            continue
        sources = [p.strip() for p in str(row.get("source_archive", "")).split(";") if p.strip().startswith("sources_official/")]
        if len(sources) < 2 or any(not (ROOT / source).is_file() for source in sources):
            raise SystemExit(f"Missing questionnaire/Codebook source evidence for {key}: {sources}")
        items.append({
            "wave": str(row["wave"]), "code": str(row["code"]), "module": str(row["module"]),
            "concept_id": str(row["concept_id"]), "concept_label": str(row["concept_label"]),
            "unit": str(row.get("unit", "")), "value_labels": str(row.get("value_labels", "")),
            "value_semantics": str(row.get("value_semantics", "")),
            "mapping_status": str(row.get("mapping_status", "")), "caveat": str(row.get("caveat", "")),
            "official_sources": "; ".join(sources),
        })
    expected = {
        ("2011", "bd005", "demographic_background"), ("2013", "bd005", "demographic_background"),
        ("2011", "bd006", "demographic_background"), ("2013", "bd006", "demographic_background"),
        ("2015", "bd006", "demographic_background"), ("2018", "bd006", "demographic_background"),
        ("2018", "bd002_w3", "demographic_background"),
        ("2018", "bg005_w4", "demographic_background"), ("2018", "bg006_w4", "demographic_background"),
    }
    found = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in items}
    if found != expected:
        raise SystemExit(f"Formal-schooling C/E overlap mismatch: missing={expected-found}; extra={found-expected}")
    return items


def update(row: dict[str, object], item: dict[str, str]) -> None:
    note = f"{item['value_semantics']}. {item['caveat']}"
    row.update({
        "category": "source-mapped candidate context",
        "subcategory": "formal-schooling history exposure overlap",
        "Candidate.Status": f"{BASE_STATUS}; concept={item['concept_id']}",
        "Harmonization.Status": note,
        "Review.Flag": "C role is retained for source/context lookup; the same field is an E candidate and must not adjust for itself. Preserve wave-specific route, denominator, and estimand.",
        "Value.Labels": item["value_labels"], "Value.Label.Source": item["official_sources"],
        "Value.Label.Review": item["mapping_status"], "Unit": item["unit"],
        "Concept.ID.Candidates": item["concept_id"],
        "Concept.Mapping.Source": "audit/formal_schooling_lifecourse_crosswalk_v1.csv",
        "Concept.Mapping.Status": item["mapping_status"], "Concept.Mapping.Caveat": item["caveat"],
        "value_labels": item["value_labels"], "value_label_source": item["official_sources"],
        "value_label_review": item["mapping_status"], "harmonization_status": note,
        "candidate_concept_ids": item["concept_id"],
        "concept_mapping_sources": "audit/formal_schooling_lifecourse_crosswalk_v1.csv",
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
                    data = frame.loc[idx].to_dict(); update(data, item)
                    for field, value in data.items():
                        if field in frame.columns: frame.at[idx, field] = value
                count += int(mask.sum())
            if count != 9:
                raise SystemExit(f"Expected 9 C overlap rows in {rel}; updated {count}")
            frame.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")).lower())
                if key in targets and str(row.get("epcf", "")).lower() == "c":
                    update(row, targets[key]); count += 1
            if count != 9:
                raise SystemExit(f"Expected 9 C overlap rows in {rel}; updated {count}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(items[0])); writer.writeheader(); writer.writerows(items)
    print("Reviewed 9 exact-wave formal-schooling C/E overlaps; C role retained, source route caveats preserved, no adjustment recommendation implied.")


if __name__ == "__main__":
    propagate()
