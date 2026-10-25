"""Link reviewed residential-settlement E candidates to exact C catalogue rows."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CROSSWALK = AUDIT / "residential_settlement_exposure_crosswalk_v1.csv"
OUTPUT = AUDIT / "residential_settlement_c_overlap_review_v1.csv"
QUESTIONNAIRES = {
    "2015": "CHARLS_2015_Questionnaire_extracted.txt",
    "2020": "CHARLS_2020_Questionnaire_English_extracted.txt",
}
EXPECTED = {
    ("2015", "bb001_w3_2", "demographic_background"),
    ("2020", "ba008", "demographic_background"),
}


def load_items() -> list[dict[str, str]]:
    crosswalk = pd.read_csv(CROSSWALK, dtype=str, encoding="utf-8-sig").fillna("")
    candidates = pd.read_csv(AUDIT / "charls_atlas_candidate_fields_v0.csv", dtype=str, encoding="utf-8-sig").fillna("")
    roles = {
        (str(r["Source.Wave"]), str(r["Variable.Name"]).lower(), str(r["Data.File.Name"]).lower(), str(r["epcf"]).lower())
        for _, r in candidates.iterrows()
    }
    items = []
    for row in crosswalk.to_dict("records"):
        if row["concept_id"] != "residential_settlement_type":
            continue
        key = (str(row["wave"]), str(row["code"]).lower(), str(row["module"]).lower())
        if key + ("c",) not in roles or key + ("e",) not in roles:
            continue
        wave = str(row["wave"])
        sources = [f"sources_official/{QUESTIONNAIRES[wave]}", f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"]
        if any(not (ROOT / p).is_file() for p in sources):
            raise SystemExit(f"Missing official questionnaire/Codebook source for {key}: {sources}")
        status, caveat = str(row.get("mapping_status", "")), str(row.get("caveat", ""))
        if "response categories reviewed" not in status.lower() or "not hukou" not in caveat.lower() or "not a measured environmental pollutant" not in caveat.lower():
            raise SystemExit(f"Residential-settlement mapping lacks source/scope caveats for {key}")
        items.append({
            "wave": wave, "code": str(row["code"]), "module": str(row["module"]),
            "concept_id": str(row["concept_id"]), "concept_label": str(row["concept_label"]),
            "value_labels": str(row.get("value_labels", "")), "mapping_status": status,
            "caveat": caveat, "official_sources": "; ".join(sources),
        })
    found = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in items}
    if found != EXPECTED:
        raise SystemExit(f"Residential-settlement C/E overlap mismatch: missing={EXPECTED-found}; extra={found-EXPECTED}")
    return items


def update(row: dict[str, object], item: dict[str, str]) -> None:
    caveat = item["caveat"]
    note = f"{item['mapping_status']}. {caveat}"
    row.update({
        "category": "source-mapped candidate context",
        "subcategory": "residential settlement context exposure overlap",
        "Candidate.Status": f"C metadata; exact source field is linked to a wave-specific residential settlement context candidate; preserve response categories; not an adjustment recommendation; concept={item['concept_id']}",
        "Harmonization.Status": caveat,
        "Review.Flag": "Residence context only; not hukou or measured pollutant. The same field is an E candidate and must not adjust for itself. Preserve wave-specific category counts and address/time frame; do not harmonize by numeric code.",
        "Value.Labels": item["value_labels"], "Value.Label.Source": item["official_sources"],
        "Value.Label.Review": item["mapping_status"],
        "Concept.ID.Candidates": item["concept_id"],
        "Concept.Mapping.Source": "audit/residential_settlement_exposure_crosswalk_v1.csv",
        "Concept.Mapping.Status": item["mapping_status"], "Concept.Mapping.Caveat": caveat,
        "value_labels": item["value_labels"], "value_label_source": item["official_sources"],
        "value_label_review": item["mapping_status"], "harmonization_status": note,
        "candidate_concept_ids": item["concept_id"],
        "concept_mapping_sources": "audit/residential_settlement_exposure_crosswalk_v1.csv",
        "concept_mapping_statuses": item["mapping_status"], "concept_mapping_caveats": caveat,
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
            if count != 2:
                raise SystemExit(f"Expected 2 C overlap rows in {rel}; updated {count}")
            frame.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")).lower())
                if key in targets and str(row.get("epcf", "")).lower() == "c":
                    update(row, targets[key])
                    count += 1
            if count != 2:
                raise SystemExit(f"Expected 2 C overlap rows in {rel}; updated {count}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(items[0]))
        writer.writeheader()
        writer.writerows(items)
    print("Reviewed two exact-wave residential-settlement C/E overlaps; category harmonization remains unapproved.")


if __name__ == "__main__":
    propagate()
