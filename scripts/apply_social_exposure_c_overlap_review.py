"""Link carefully source-reviewed social-exposure fields to exact C catalogue rows."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CROSSWALK = AUDIT / "social_exposure_crosswalk_v1.csv"
OUTPUT = AUDIT / "social_exposure_c_overlap_review_v1.csv"
QUESTIONNAIRES = {
    "2011": "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
    "2013": "CHARLS_2013_Questionnaire_extracted.txt",
    "2020": "CHARLS_2020_Questionnaire_English_extracted.txt",
}
EXPECTED = {
    ("2011", "da056s8", "health_status_and_functioning"),
    ("2013", "db022_w2_9_1_s64", "health_status_and_functioning"),
    ("2013", "db022_w2_9_2_s64", "health_status_and_functioning"),
    ("2020", "xsoctype_7_", "health_status_and_functioning"),
}


def load_items() -> list[dict[str, str]]:
    crosswalk = pd.read_csv(CROSSWALK, dtype=str, encoding="utf-8-sig").fillna("")
    candidates = pd.read_csv(AUDIT / "charls_atlas_candidate_fields_v0.csv", dtype=str, encoding="utf-8-sig").fillna("")
    roles = {
        (str(r["Source.Wave"]), str(r["Variable.Name"]).lower(), str(r["Data.File.Name"]).lower(), str(r["epcf"]).lower())
        for _, r in candidates.iterrows()
    }
    items: list[dict[str, str]] = []
    for row in crosswalk.to_dict("records"):
        key = (str(row["wave"]), str(row["code"]).lower(), str(row["module"]).lower())
        if key not in EXPECTED:
            continue
        if key + ("c",) not in roles or key + ("e",) not in roles:
            raise SystemExit(f"Social C/E role mismatch for {key}")
        label_sources = [p.strip() for p in str(row.get("value_label_source", "")).split(";") if p.strip()]
        questionnaire = str(row.get("questionnaire_source", "")).strip() or next(
            (p for p in label_sources if "Questionnaire" in p), f"sources_official/{QUESTIONNAIRES[key[0]]}"
        )
        codebook = next(
            (p for p in label_sources if "Codebook" in p), f"sources_official/CHARLS_{key[0]}_Codebook_extracted.txt"
        )
        official_sources = [questionnaire, codebook]
        if len(official_sources) != 2 or any(not (ROOT / p).is_file() for p in official_sources):
            raise SystemExit(f"Missing official questionnaire/Codebook evidence for {key}: {official_sources}")
        status, caveat = str(row.get("mapping_status", "")), str(row.get("caveat", ""))
        semantics = str(row.get("value_semantics", ""))
        if not status or not caveat or not semantics:
            raise SystemExit(f"Social crosswalk lacks a reviewed status, semantics, or caveat for {key}")
        if key[1] in {"da056s8", "db022_w2_9_1_s64", "db022_w2_9_2_s64"} and not any(
            token in (status + " " + caveat + " " + semantics).lower()
            for token in ("unresolved", "no observations", "do not infer")
        ):
            raise SystemExit(f"Social field with unresolved storage/denominator lost its limitation for {key}")
        if key[1].startswith("db022_w2_9_"):
            codebook_lines = (ROOT / codebook).read_text(encoding="utf-8", errors="replace").splitlines()
            exact = [i for i, line in enumerate(codebook_lines) if re.search(rf"•\s*{re.escape(key[1])}\s*:", line, re.IGNORECASE)]
            if len(exact) != 1 or not any("No Observations" in line for line in codebook_lines[exact[0]:exact[0] + 5]):
                raise SystemExit(f"Expected exact Codebook 'No Observations' note for {key}")
            questionnaire_text = (ROOT / questionnaire).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
            if "15. volunteer or employee of facility" not in re.sub(r"\s+", " ", questionnaire_text).lower():
                raise SystemExit(f"Questionnaire caregiver category was not located for {key}")
            caveat += (
                " The official 2013 questionnaire lists volunteer/employee of facility as helper category 15, "
                "while the Codebook field suffix is s64; the suffix is a field identifier, not a verified response value. "
                "The exact Codebook field reports No Observations. Do not equate category codes or infer a respondent-level "
                "negative, frequency, or structural skip; reconcile against the authorized release first."
            )
        items.append({
            "wave": key[0], "code": str(row["code"]), "module": str(row["module"]),
            "concept_id": str(row["concept_id"]), "concept_label": str(row["concept_label"]),
            "value_labels": str(row.get("value_labels", "")), "mapping_status": status,
            "value_semantics": semantics, "caveat": caveat,
            "official_sources": "; ".join(official_sources),
        })
    found = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in items}
    if found != EXPECTED:
        raise SystemExit(f"Social C/E overlap mismatch: missing={EXPECTED-found}; extra={found-EXPECTED}")
    return items


def update(row: dict[str, object], item: dict[str, str]) -> None:
    caveat = item["caveat"]
    status = item["mapping_status"]
    note = f"{status}. {item['value_semantics']} {caveat}"
    row.update({
        "category": "source-mapped candidate context",
        "subcategory": "social participation/care exposure overlap",
        "Candidate.Status": f"C metadata; exact wave and source field link to the social-exposure candidate {item['concept_id']}; retain item and route; not an adjustment recommendation or analysis-ready indicator",
        "Harmonization.Status": note,
        "Review.Flag": f"Social activity/care candidate; the same field is an E candidate and must not adjust for itself. Preserve source wave, response storage, task/activity slot, and eligible route. {item['value_semantics']} {caveat}",
        "Value.Labels": item["value_labels"], "Value.Label.Source": item["official_sources"],
        "Value.Label.Review": status,
        "Concept.ID.Candidates": item["concept_id"],
        "Concept.Mapping.Source": "audit/social_exposure_crosswalk_v1.csv",
        "Concept.Mapping.Status": status, "Concept.Mapping.Caveat": caveat,
        "value_labels": item["value_labels"], "value_label_source": item["official_sources"],
        "value_label_review": status, "harmonization_status": note,
        "candidate_concept_ids": item["concept_id"],
        "concept_mapping_sources": "audit/social_exposure_crosswalk_v1.csv",
        "concept_mapping_statuses": status, "concept_mapping_caveats": caveat,
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
            if count != len(EXPECTED):
                raise SystemExit(f"Expected {len(EXPECTED)} social C overlap rows in {rel}; updated {count}")
            frame.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")).lower())
                if key in targets and str(row.get("epcf", "")).lower() == "c":
                    update(row, targets[key])
                    count += 1
            if count != len(EXPECTED):
                raise SystemExit(f"Expected {len(EXPECTED)} social C overlap rows in {rel}; updated {count}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(items[0]))
        writer.writeheader()
        writer.writerows(items)
    print("Reviewed four exact-wave social participation/care C/E links; unresolved storage, routing, and analysis limits remain explicit.")


if __name__ == "__main__":
    propagate()
