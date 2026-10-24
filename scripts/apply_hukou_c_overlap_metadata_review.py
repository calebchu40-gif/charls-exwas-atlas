"""Propagate reviewed hukou exposure metadata to exact C-side overlaps.

These rows remain C metadata. Their possible adjustment role depends on the
estimand and is never an automatic model recommendation.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUTPUT = AUDIT / "hukou_c_overlap_review_v1.csv"
SOURCES = (
    "hukou_lifecourse_exposure_crosswalk_v1.csv",
    "hukou_recent_change_crosswalk_v1.csv",
)
CATALOG = ROOT / "site-prototype/dist/catalog.json"
BASE_STATUS = (
    "C metadata; exact source field also catalogued as a wave-specific hukou exposure candidate; "
    "adjustment use requires estimand-specific justification and is not approved by this catalogue"
)


def records() -> list[dict[str, str]]:
    crosswalk = pd.concat(
        [pd.read_csv(AUDIT / name, dtype=str, encoding="utf-8-sig").fillna("") for name in SOURCES],
        ignore_index=True,
    )
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    pending_c_keys = {
        (str(r.get("Source.Wave", "")), str(r.get("Variable.Name", "")).lower(), str(r.get("Data.File.Name", "")))
        for r in catalog
        if str(r.get("epcf", "")).lower() == "c" and r.get("Value.Label.Review") == "not yet reviewed"
    }
    e_keys = {
        (str(r.get("Source.Wave", "")), str(r.get("Variable.Name", "")).lower(), str(r.get("Data.File.Name", "")))
        for r in catalog if str(r.get("epcf", "")).lower() == "e"
    }
    result = []
    for _, row in crosswalk.iterrows():
        key = (str(row.wave), str(row.code).lower(), str(row.module))
        if key not in e_keys or key not in pending_c_keys:
            continue
        source_paths = [s.strip() for s in str(row.get("value_label_source", "")).split(";") if s.strip()]
        if not source_paths or any(not (ROOT / p).is_file() for p in source_paths):
            raise SystemExit(f"Missing official source(s) for {key}: {source_paths}")
        result.append({
            "wave": str(row.wave), "code": str(row.code), "module": str(row.module),
            "concept_id": str(row.concept_id), "unit": str(row.get("unit", "")),
            "source_label": str(row.get("source_label", "")),
            "value_labels": str(row.get("value_labels", "")),
            "value_label_status": str(row.get("value_label_status", "")),
            "official_sources": "; ".join(source_paths),
            "mapping_status": str(row.get("mapping_status", "")),
            "value_semantics": str(row.get("value_semantics", "")),
            "caveat": str(row.get("caveat", "")),
        })
    if len(result) != 20 or len({(r['wave'], r['code'], r['module']) for r in result}) != 20:
        raise SystemExit(f"Expected 20 unique exact E/C overlap keys; found {len(result)}")
    return result


def update(row: dict[str, object], item: dict[str, str]) -> None:
    note = (
        f"{item['mapping_status']}. {item['value_semantics']} "
        "This is a candidate exposure/context measure; use as an adjustment variable only when justified by the estimand and causal structure. "
        f"{item['caveat']}"
    )
    row["category"] = "automated covariate search hit"
    row["subcategory"] = "hukou life-course exposure overlap; estimand-specific context candidate"
    row["Candidate.Status"] = BASE_STATUS
    row["Harmonization.Status"] = note
    row["Review.Flag"] = note
    row["Value.Labels"] = item["value_labels"]
    row["Value.Label.Source"] = item["official_sources"]
    row["Value.Label.Review"] = item["value_label_status"]
    row["Concept.Unit.Candidates"] = f"{item['concept_id']}={item['unit']}" if item["unit"] else ""
    row["Concept.ID.Candidates"] = item["concept_id"]
    row["Concept.Mapping.Source"] = "audit/" + ("hukou_lifecourse_exposure_crosswalk_v1.csv; audit/hukou_recent_change_crosswalk_v1.csv")
    row["Concept.Mapping.Status"] = item["mapping_status"]
    row["Concept.Mapping.Caveat"] = item["caveat"]
    row["value_labels"] = item["value_labels"]
    row["value_label_source"] = item["official_sources"]
    row["value_label_review"] = item["value_label_status"]
    row["harmonization_status"] = note
    row["candidate_concept_ids"] = item["concept_id"]
    row["concept_mapping_sources"] = row["Concept.Mapping.Source"]
    row["concept_mapping_statuses"] = item["mapping_status"]
    row["concept_mapping_caveats"] = item["caveat"]
    row["candidate_concept_units"] = f"{item['concept_id']}={item['unit']}" if item["unit"] else ""


def propagate() -> None:
    items = records()
    targets = {(r["wave"], r["code"].lower(), r["module"]): r for r in items}
    for rel in ("audit/charls_atlas_candidate_fields_v0.csv", "site-prototype/dist/catalog.json"):
        path = ROOT / rel
        if not path.exists():
            continue
        count = 0
        if path.suffix == ".csv":
            df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            for key, item in targets.items():
                mask = (df["Source.Wave"].eq(key[0]) & df["Variable.Name"].str.lower().eq(key[1]) &
                        df["Data.File.Name"].eq(key[2]) & df["epcf"].str.lower().eq("c"))
                if mask.any():
                    for i in df.index[mask]:
                        data = df.loc[i].to_dict(); update(data, item)
                        for col, val in data.items():
                            if col in df.columns: df.at[i, col] = val
                    count += int(mask.sum())
            if count != 20: raise SystemExit(f"Expected 20 C overlap rows in {rel}; updated {count}")
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")))
                if key in targets and str(row.get("epcf", "")).lower() == "c":
                    update(row, targets[key]); count += 1
            if count != 20: raise SystemExit(f"Expected 20 C overlap rows in {rel}; updated {count}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(items[0])); w.writeheader(); w.writerows(items)
    print("Reviewed 20 exact module-qualified hukou E/C overlaps; retained C role and no automatic adjustment recommendation.")


if __name__ == "__main__":
    propagate()
