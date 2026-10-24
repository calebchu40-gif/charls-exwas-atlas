"""Review C-side records that overlap with audited marriage-history exposures."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUTPUT = AUDIT / "marital_history_c_overlap_review_v1.csv"
CROSSWALK = AUDIT / "marital_history_exposure_crosswalk_v1.csv"
CATALOG = ROOT / "site-prototype/dist/catalog.json"
BASE = (
    "C metadata; source-reviewed field also appears in the life-course marriage exposure catalog; "
    "adjustment use is estimand-specific and the field must not adjust for itself when it is the focal exposure"
)


def load_items() -> list[dict[str, str]]:
    frame = pd.read_csv(CROSSWALK, dtype=str, encoding="utf-8-sig").fillna("")
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    ckeys = {(str(r.get("Source.Wave", "")), str(r.get("Variable.Name", "")).lower(), str(r.get("Data.File.Name", ""))) for r in catalog if str(r.get("epcf", "")).lower() == "c" and str(r.get("Value.Label.Review", "")) == "not yet reviewed"}
    ekeys = {(str(r.get("Source.Wave", "")), str(r.get("Variable.Name", "")).lower(), str(r.get("Data.File.Name", ""))) for r in catalog if str(r.get("epcf", "")).lower() == "e"}
    items = []
    for row in frame.to_dict("records"):
        key = (row["wave"], row["code"].lower(), row["module"])
        if key in ckeys and key in ekeys:
            paths = [x.strip() for x in row["value_label_source"].split(";") if x.strip()]
            if not paths or any(not (ROOT / path).is_file() for path in paths):
                raise SystemExit(f"Missing official source for {key}")
            items.append({**row, "official_sources": "; ".join(paths)})
    expected = {("2011", "be007", "demographic_background"), ("2011", "be008", "demographic_background"), ("2013", "be009_1", "Demographic_Background"), ("2013", "be009_2", "Demographic_Background")}
    found = {(x["wave"], x["code"].lower(), x["module"]) for x in items}
    if found != expected:
        raise SystemExit(f"Marriage E/C overlap target mismatch: missing={expected-found}; extra={found-expected}")
    return items


def update(row: dict[str, object], item: dict[str, str]) -> None:
    caveat = item["caveat"]
    note = f"{item['mapping_status']}. {item['value_semantics']} {caveat}"
    row.update({
        "category": "automated covariate search hit",
        "subcategory": "marital-history exposure overlap; estimand-specific context candidate",
        "Candidate.Status": BASE,
        "Harmonization.Status": note,
        "Review.Flag": note,
        "Value.Labels": item["value_labels"],
        "Value.Label.Source": item["official_sources"],
        "Value.Label.Review": item["value_label_status"],
        "Concept.ID.Candidates": item["concept_id"],
        "Concept.Mapping.Source": "audit/marital_history_exposure_crosswalk_v1.csv",
        "Concept.Mapping.Status": item["mapping_status"],
        "Concept.Mapping.Caveat": caveat,
        "value_labels": item["value_labels"], "value_label_source": item["official_sources"],
        "value_label_review": item["value_label_status"], "harmonization_status": note,
        "candidate_concept_ids": item["concept_id"],
        "concept_mapping_sources": "audit/marital_history_exposure_crosswalk_v1.csv",
        "concept_mapping_statuses": item["mapping_status"], "concept_mapping_caveats": caveat,
    })


def propagate() -> None:
    items = load_items()
    targets = {(x["wave"], x["code"].lower(), x["module"]): x for x in items}
    for rel in ("audit/charls_atlas_candidate_fields_v0.csv", "site-prototype/dist/catalog.json"):
        path = ROOT / rel
        if not path.exists(): continue
        count = 0
        if path.suffix == ".csv":
            df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            for key, item in targets.items():
                mask = df["Source.Wave"].eq(key[0]) & df["Variable.Name"].str.lower().eq(key[1]) & df["Data.File.Name"].eq(key[2]) & df["epcf"].str.lower().eq("c")
                if mask.any():
                    for idx in df.index[mask]:
                        data = df.loc[idx].to_dict(); update(data, item)
                        for field, value in data.items():
                            if field in df.columns: df.at[idx, field] = value
                    count += int(mask.sum())
            if count != 4: raise SystemExit(f"Expected four C overlap rows in {rel}; updated {count}")
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")))
                if key in targets and str(row.get("epcf", "")).lower() == "c": update(row, targets[key]); count += 1
            if count != 4: raise SystemExit(f"Expected four C overlap rows in {rel}; updated {count}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(items[0])); writer.writeheader(); writer.writerows(items)
    print("Reviewed four module-qualified marriage-history E/C overlaps; retained conditional routes and estimand-specific adjustment cautions.")


if __name__ == "__main__": propagate()
