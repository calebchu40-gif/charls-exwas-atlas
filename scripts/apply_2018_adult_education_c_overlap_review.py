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
    ckeys = {(str(r.get("Source.Wave", "")), str(r.get("Variable.Name", "")).lower(), str(r.get("Data.File.Name", ""))) for r in catalog if str(r.get("epcf", "")).lower() == "c"}
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


def source_mapped_c_candidates() -> dict[tuple[str, str, str], dict[str, str]]:
    """Identify exact C rows already mapped to the adult-education E crosswalk."""
    crosswalk = pd.read_csv(MAP, dtype=str, encoding="utf-8-sig").fillna("")
    fields = pd.read_csv(AUDIT / "charls_atlas_candidate_fields_v0.csv", dtype=str, encoding="utf-8-sig").fillna("")
    ckeys = {
        (str(r["Source.Wave"]), str(r["Variable.Name"]).lower(), str(r["Data.File.Name"]).lower())
        for _, r in fields.iterrows()
        if str(r["epcf"]).lower() == "c" and (
            str(r["Candidate.Status"]).startswith("automated keyword discovery only") or
            str(r["Candidate.Status"]).startswith("C metadata; source-mapped to adult_education_")
        )
    }
    result = {}
    duration_overlap_keys = {
        ("2018", "bd008_w2_1", "demographic_background"),
        ("2018", "bd008_w4_1", "demographic_background"),
    }
    for item in crosswalk.to_dict("records"):
        key = (str(item["wave"]), str(item["code"]).lower(), str(item["module"]).lower())
        if key not in ckeys or key in duration_overlap_keys:
            continue
        sources = [p.strip() for p in item.get("source_archive", "").split(";") if p.strip().startswith("sources_official/")]
        if len(sources) < 2 or any(not (ROOT / source).is_file() for source in sources):
            raise SystemExit(f"Missing official source evidence for adult-education C row {key}")
        item["official_sources"] = "; ".join(sources)
        result[key] = item
    if len(result) != 33:
        raise SystemExit(f"Expected 33 source-mapped adult-education C rows; found {len(result)}")
    return result


def update_source_mapped_c(row: dict[str, object], item: dict[str, str]) -> None:
    concept = item["concept_id"]
    subcategory = {
        "adult_education_program_participation": "adult-education participation option slot",
        "adult_education_degree_received": "adult-education credential response metadata",
        "adult_education_highest_credential": "adult-education highest-credential response metadata",
    }.get(concept, "adult-education candidate metadata")
    row.update({
        "category": "source-mapped candidate context",
        "subcategory": subcategory,
        "Candidate.Status": f"C metadata; source-mapped to {concept}; official route, denominator and release coding review remain pending; not a default covariate",
        "Harmonization.Status": f"{item['value_semantics']}. {item['caveat']} Preserve source wave and exact question route; blank/structural skip is not a negative response.",
        "Review.Flag": "C metadata only; candidate exposure has a corresponding E role where mapped; route/value QA remains pending and no adjustment set is implied",
        "Value.Label.Source": item["official_sources"],
        "Value.Label.Review": "official questionnaire and Codebook source files identified; response coding and eligible-route QA pending; frequencies excluded",
        "Concept.ID.Candidates": concept,
        "Concept.Mapping.Source": "audit/adult_education_training_exposure_crosswalk_v1.csv",
        "Concept.Mapping.Status": item["mapping_status"],
        "Concept.Mapping.Caveat": item["caveat"],
    })


def propagate() -> None:
    rows = targets()
    dest = {(r["wave"], r["code"].lower(), r["module"]): r for r in rows}
    c_dest = source_mapped_c_candidates()
    for rel in ("audit/charls_atlas_candidate_fields_v0.csv", "audit/charls_atlas_candidate_fields_v0.json", "site-prototype/dist/catalog.json", "site-prototype/dist/catalog_c.json"):
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
            for key, item in c_dest.items():
                mask = df["Source.Wave"].eq(key[0]) & df["Variable.Name"].str.lower().eq(key[1]) & df["Data.File.Name"].str.lower().eq(key[2]) & df["epcf"].str.lower().eq("c")
                if mask.any():
                    for i in df.index[mask]:
                        values = df.loc[i].to_dict(); update_source_mapped_c(values, item)
                        for col, value in values.items():
                            if col in df.columns: df.at[i, col] = value
                    count += int(mask.sum())
            expected = 35
            if count != expected: raise SystemExit(f"Expected {expected} C rows in {rel}; updated {count}")
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")))
                if key in dest and str(row.get("epcf", "")).lower() == "c": update(row, dest[key]); count += 1
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")).lower())
                if key in c_dest and str(row.get("epcf", "")).lower() == "c": update_source_mapped_c(row, c_dest[key]); count += 1
            expected = 35
            if count != expected: raise SystemExit(f"Expected {expected} C rows in {rel}; updated {count}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("Reviewed two Wave-4 adult-education duration overlaps and source-mapped 33 additional C metadata rows; incomplete route/coding QA and wave-specific time windows remain explicit.")


if __name__ == "__main__": propagate()
