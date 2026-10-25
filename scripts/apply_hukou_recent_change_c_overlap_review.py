"""Link source-reviewed recent hukou-change E fields to exact C catalogue rows."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CROSSWALK = AUDIT / "hukou_recent_change_crosswalk_v1.csv"
OUTPUT = AUDIT / "hukou_recent_change_c_overlap_review_v1.csv"
EXPECTED = {
    ("2013", "bc001_w2_1", "demographic_background"),
    ("2013", "bc001_w2_2", "demographic_background"),
    ("2013", "bc001_w2_3", "demographic_background"),
    ("2013", "bc005_w2_1", "demographic_background"),
    ("2013", "bc005_w2_2", "demographic_background"),
    ("2015", "bc002_w3", "demographic_background"),
    ("2018", "bc002_w3", "demographic_background"),
    ("2015", "bc002_w3_2", "demographic_background"),
    ("2018", "bc002_w3_2", "demographic_background"),
    ("2015", "bc002_w3_5", "demographic_background"),
    ("2018", "bc002_w3_5", "demographic_background"),
}
SUBCATEGORY = "recent hukou change exposure overlap; conditional context candidate"


def load_items() -> list[dict[str, str]]:
    crosswalk = pd.read_csv(CROSSWALK, dtype=str, encoding="utf-8-sig").fillna("")
    fields = pd.read_csv(AUDIT / "charls_atlas_candidate_fields_v0.csv", dtype=str, encoding="utf-8-sig").fillna("")
    roles = {
        (str(r["Source.Wave"]), str(r["Variable.Name"]).lower(), str(r["Data.File.Name"]).lower(), str(r["epcf"]).lower())
        for _, r in fields.iterrows()
    }
    items: list[dict[str, str]] = []
    for row in crosswalk.to_dict("records"):
        key = (str(row["wave"]), str(row["code"]).lower(), str(row["module"]).lower())
        if key not in EXPECTED:
            continue
        if key + ("c",) not in roles or key + ("e",) not in roles:
            raise SystemExit(f"Exact C/E roles missing for {key}")
        raw_sources = [s.strip() for s in str(row.get("value_label_source", "")).split(";") if s.strip()]
        q_sources = [s.strip() for s in (str(row.get("questionnaire_source", "")) + ";" + str(row.get("value_label_source", ""))).split(";") if s.strip().startswith("sources_official/") and "Questionnaire" in s]
        cb_sources = [s for s in raw_sources if s.startswith("sources_official/") and "Codebook" in s]
        sources = list(dict.fromkeys(q_sources + cb_sources))
        if len(q_sources) != 1 or len(cb_sources) != 1 or any(not (ROOT / s).is_file() for s in sources):
            raise SystemExit(f"Expected existing official Questionnaire/Codebook for {key}: {sources}")
        for source in sources:
            text = (ROOT / source).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
            if not re.search(rf"(?<![A-Za-z0-9_]){re.escape(str(row['code']))}(?![A-Za-z0-9_])", text, re.IGNORECASE):
                raise SystemExit(f"Exact field code not found in {source}: {key}")
        status = str(row.get("mapping_status", "")); semantics = str(row.get("value_semantics", "")); caveat = str(row.get("caveat", ""))
        labels = str(row.get("value_labels", ""))
        if not status or not semantics or not caveat or not labels:
            raise SystemExit(f"Crosswalk lacks reviewed labels/semantics/caveat for {key}")
        if not any(t in (semantics + " " + caveat).lower() for t in ("conditional", "reinterview", "only on", "asked in", "asked on")):
            raise SystemExit(f"Recent-change route detail missing for {key}")
        items.append({
            "wave": key[0], "code": str(row["code"]), "module": str(row["module"]),
            "concept_id": str(row["concept_id"]), "concept_label": str(row["concept_label"]),
            "value_labels": labels, "mapping_status": status, "value_semantics": semantics,
            "caveat": caveat, "official_sources": "; ".join(sources),
        })
    found = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in items}
    if found != EXPECTED:
        raise SystemExit(f"Recent hukou-change C/E mismatch: missing={EXPECTED-found}; extra={found-EXPECTED}")
    return items


def update(row: dict[str, object], item: dict[str, str]) -> None:
    note = f"{item['mapping_status']}. {item['value_semantics']} {item['caveat']}"
    restriction = "This is wave-specific historical C/E metadata, not a current residence or pollution measure. The exact field is itself the focal E candidate and must not adjust for itself; other adjustment use is estimand-specific."
    row.update({
        "category": "automated covariate search hit", "subcategory": SUBCATEGORY,
        "Candidate.Status": "C metadata linked to an exact wave-specific hukou-change E candidate; conditional route and analysis eligibility remain estimand-specific; no default adjustment recommendation",
        "Harmonization.Status": f"{note} {restriction}", "Review.Flag": f"{note} {restriction}",
        "Value.Labels": item["value_labels"], "Value.Label.Source": item["official_sources"],
        "Value.Label.Review": item["mapping_status"], "Concept.ID.Candidates": item["concept_id"],
        "Concept.Mapping.Source": "audit/hukou_recent_change_crosswalk_v1.csv",
        "Concept.Mapping.Status": item["mapping_status"], "Concept.Mapping.Caveat": item["caveat"],
        "value_labels": item["value_labels"], "value_label_source": item["official_sources"],
        "value_label_review": item["mapping_status"], "harmonization_status": f"{note} {restriction}",
        "candidate_concept_ids": item["concept_id"],
        "concept_mapping_sources": "audit/hukou_recent_change_crosswalk_v1.csv",
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
        if not path.exists(): continue
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
            if count != len(EXPECTED): raise SystemExit(f"Expected {len(EXPECTED)} C rows in {rel}; updated {count}")
            frame.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")).lower())
                if key in targets and str(row.get("epcf", "")).lower() == "c": update(row, targets[key]); count += 1
            if count != len(EXPECTED): raise SystemExit(f"Expected {len(EXPECTED)} C rows in {rel}; updated {count}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(items[0])); writer.writeheader(); writer.writerows(items)
    print("Reviewed 11 exact 2013/2015/2018 hukou-change C/E links; wave-specific codes, route categories, and conditional reasons retained.")


if __name__ == "__main__":
    propagate()
