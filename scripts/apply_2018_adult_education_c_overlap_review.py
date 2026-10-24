"""Review Wave-4 adult-education duration overlaps using official routing."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUTPUT = AUDIT / "adult_education_c_overlap_review_2018_v1.csv"
MAP = AUDIT / "adult_education_training_exposure_crosswalk_v1.csv"
BASE = (
    "C metadata; exact field also mapped as an adult-education duration exposure candidate; "
    "adjustment use depends on the estimand and the field must not adjust for itself when focal"
)


def targets() -> list[dict[str, str]]:
    frame = pd.read_csv(MAP, dtype=str, encoding="utf-8-sig").fillna("")
    catalog = json.loads((ROOT / "site-prototype/dist/catalog.json").read_text(encoding="utf-8"))
    ckeys = {(str(r.get("Source.Wave", "")), str(r.get("Variable.Name", "")).lower(), str(r.get("Data.File.Name", ""))) for r in catalog if str(r.get("epcf", "")).lower() == "c" and r.get("Value.Label.Review") == "not yet reviewed"}
    ekeys = {(str(r.get("Source.Wave", "")), str(r.get("Variable.Name", "")).lower(), str(r.get("Data.File.Name", ""))) for r in catalog if str(r.get("epcf", "")).lower() == "e"}
    result = []
    for r in frame.to_dict("records"):
        key = (r["wave"], r["code"].lower(), r["module"])
        if r["wave"] != "2018" or r["code"].lower() not in {"bd008_w2_1", "bd008_w4_1"} or key not in ckeys or key not in ekeys:
            continue
        sources = [p.strip() for p in r["source_archive"].split(";") if p.strip().startswith("sources_official/")]
        if len(sources) < 2 or any(not (ROOT / p).is_file() for p in sources):
            raise SystemExit(f"Missing official questionnaire/Codebook citation for {key}")
        r["official_sources"] = "; ".join(sources)
        result.append(r)
    if {(r["wave"], r["code"].lower(), r["module"]) for r in result} != {
        ("2018", "bd008_w2_1", "Demographic_Background"),
        ("2018", "bd008_w4_1", "Demographic_Background"),
    }:
        raise SystemExit("Expected two exact Wave-4 E/C adult-education duration overlaps")
    return result


def update(row: dict[str, object], item: dict[str, str]) -> None:
    note = (
        f"{item['value_semantics']}. Unit: years. The preceding BD007 route has a None option that skips this duration item; "
        "structural skips are not zero. In 2018 W2_1 is the total-duration item and W4_1 explicitly refers to years since ZIWTime. "
        "Keep the route/time window and do not treat this field as a universal adjustment variable. " + item["caveat"]
    )
    row.update({
        "category": "automated covariate search hit",
        "subcategory": "adult-education duration exposure overlap; route-specific context candidate",
        "Candidate.Status": BASE,
        "Harmonization.Status": note,
        "Review.Flag": note,
        "Value.Labels": "",
        "Value.Label.Source": item["official_sources"],
        "Value.Label.Review": "2018 official questionnaire and Codebook item/route reviewed; continuous duration in years; no discrete labels or frequencies copied",
        "Unit": "years",
        "Concept.Unit.Candidates": f"{item['concept_id']}=years",
        "Concept.ID.Candidates": item["concept_id"],
        "Concept.Mapping.Source": "audit/adult_education_training_exposure_crosswalk_v1.csv",
        "Concept.Mapping.Status": item["mapping_status"],
        "Concept.Mapping.Caveat": item["caveat"],
        "value_labels": "", "value_label_source": item["official_sources"],
        "value_label_review": "2018 official questionnaire and Codebook item/route reviewed; continuous duration in years; no discrete labels or frequencies copied",
        "harmonization_status": note,
        "candidate_concept_ids": item["concept_id"],
        "concept_mapping_sources": "audit/adult_education_training_exposure_crosswalk_v1.csv",
        "concept_mapping_statuses": item["mapping_status"],
        "concept_mapping_caveats": item["caveat"],
        "candidate_concept_units": f"{item['concept_id']}=years",
    })


def propagate() -> None:
    rows = targets()
    dest = {(r["wave"], r["code"].lower(), r["module"]): r for r in rows}
    for rel in ("audit/charls_atlas_candidate_fields_v0.csv", "site-prototype/dist/catalog.json"):
        path = ROOT / rel
        if not path.exists(): continue
        count = 0
        if path.suffix == ".csv":
            df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            for key, item in dest.items():
                mask = df["Source.Wave"].eq(key[0]) & df["Variable.Name"].str.lower().eq(key[1]) & df["Data.File.Name"].eq(key[2]) & df["epcf"].str.lower().eq("c")
                if mask.any():
                    for i in df.index[mask]:
                        values = df.loc[i].to_dict(); update(values, item)
                        for col, value in values.items():
                            if col in df.columns: df.at[i, col] = value
                    count += int(mask.sum())
            if count != 2: raise SystemExit(f"Expected two C rows in {rel}; updated {count}")
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")))
                if key in dest and str(row.get("epcf", "")).lower() == "c": update(row, dest[key]); count += 1
            if count != 2: raise SystemExit(f"Expected two C rows in {rel}; updated {count}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("Reviewed two Wave-4 adult-education E/C overlaps; years, None-route skips, and W2/W4 time windows retained.")


if __name__ == "__main__": propagate()
