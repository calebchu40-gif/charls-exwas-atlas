"""Replace generic C keyword status only for exact, source-verified E/P overlaps."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CATALOG = AUDIT / "charls_atlas_candidate_fields_v0.csv"
CROSSWALK = AUDIT / "ep_concept_source_crosswalk_v1.csv"
OUTPUT = AUDIT / "keyword_epc_overlap_review_v1.csv"
QUESTIONNAIRE = {
    "2011": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt",
    "2018": "sources_official/CHARLS_2018_Questionnaire_extracted.txt",
    "2020": "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt",
}
EXPECTED = {
    ("2020", "da030", "health_status_and_functioning"), ("2020", "da049_1", "health_status_and_functioning"),
    ("2020", "ba010", "demographic_background"), ("2020", "ba009", "demographic_background"),
    ("2013", "da030_2", "health_status_and_functioning"), ("2013", "da062_1", "health_status_and_functioning"),
    ("2013", "da065_1", "health_status_and_functioning"), ("2013", "da071_2", "health_status_and_functioning"),
    ("2013", "da070_2", "health_status_and_functioning"), ("2013", "bd001", "demographic_background"),
    ("2013", "bd001_w2_4", "demographic_background"), ("2013", "bd001_w2_3", "demographic_background"),
    ("2013", "bc005", "demographic_background"), ("2013", "bc001", "demographic_background"),
    ("2011", "da049", "health_status_and_functioning"), ("2011", "bc005", "demographic_background"),
    ("2011", "bc001", "demographic_background"), ("2011", "bd001", "demographic_background"),
    ("2018", "da049", "health_status_and_functioning"), ("2018", "da070_2", "health_status_and_functioning"),
    ("2018", "da065_2", "health_status_and_functioning"), ("2018", "da071_2", "health_status_and_functioning"),
    ("2018", "da030_2", "health_status_and_functioning"), ("2018", "da019_w2_2_2", "health_status_and_functioning"),
    ("2018", "bd001_w2_4", "demographic_background"), ("2018", "bc002_w3_4", "demographic_background"),
    ("2018", "bc002_w3_1", "demographic_background"), ("2015", "bd001_w2_4", "demographic_background"),
    ("2015", "bc002_w3_1", "demographic_background"), ("2015", "bc001_w3_3", "demographic_background"),
    ("2015", "da071_2", "health_status_and_functioning"), ("2015", "da070_2", "health_status_and_functioning"),
    ("2015", "da030_2", "health_status_and_functioning"), ("2015", "da065_1", "health_status_and_functioning"),
    ("2015", "da062_1", "health_status_and_functioning"),
}


def _contains_code(path: str, code: str) -> bool:
    text = (ROOT / path).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
    return bool(re.search(rf"(?<![A-Za-z0-9_]){re.escape(code)}(?![A-Za-z0-9_])", text, re.I))


def load_items() -> list[dict[str, str]]:
    candidates = pd.read_csv(CATALOG, dtype=str, encoding="utf-8-sig").fillna("")
    crosswalk = pd.read_csv(CROSSWALK, dtype=str, encoding="utf-8-sig").fillna("")
    items: list[dict[str, str]] = []
    for row in candidates.to_dict("records"):
        if row.get("epcf", "").lower() != "c":
            continue
        wave, code, module = row["Source.Wave"], row["Variable.Name"], row["Component"]
        key = (wave, code.lower(), module.lower())
        if key not in EXPECTED:
            continue
        matches = crosswalk[(crosswalk["Wave"].eq(wave)) & (crosswalk["Source.Code"].str.lower().eq(code.lower())) &
                            (crosswalk["_Module.Key"].str.lower().eq(module.lower())) &
                            (crosswalk["Role"].str.lower().isin(["e", "p"]))]
        if len(matches) != 1:
            raise SystemExit(f"Expected one exact E/P crosswalk for {key}, found {len(matches)}")
        ep = matches.iloc[0].to_dict()
        questionnaire = QUESTIONNAIRE[wave]
        codebook = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        for path in (questionnaire, codebook):
            if not (ROOT / path).is_file() or not _contains_code(path, code):
                raise SystemExit(f"Exact {code} field not confirmed in official Questionnaire + Codebook: {path}")
        roles = set(candidates[(candidates["Source.Wave"].eq(wave)) & (candidates["Variable.Name"].str.lower().eq(code.lower())) &
                               (candidates["Component"].str.lower().eq(module.lower()))]["epcf"].str.lower())
        if "c" not in roles or ep["Role"].lower() not in roles:
            raise SystemExit(f"Expected exact C/{ep['Role']} role pair absent for {key}: {roles}")
        items.append({
            "wave": wave, "code": code, "module": module, "role": ep["Role"].upper(),
            "concept_id": ep["Concept.ID"], "concept_label": ep["Concept.Label"],
            "mapping_status": ep["Mapping.Status"], "value_semantics": ep["Value.Semantics"],
            "mapping_caveat": ep["Caveat"], "official_questionnaire": questionnaire,
            "official_codebook": codebook,
        })
    found = {(r["wave"], r["code"].lower(), r["module"].lower()) for r in items}
    if found != EXPECTED:
        raise SystemExit(f"Exact source-reviewed generic C/E/P overlap mismatch: missing={EXPECTED-found}; extra={found-EXPECTED}")
    return items


def update(row: dict[str, object], item: dict[str, str]) -> None:
    concept_note = f"Exact same-wave field is also mapped as {item['role']} concept {item['concept_id']}; {item['mapping_status']}. {item['value_semantics']} {item['mapping_caveat']}"
    restriction = (f"This C row records a metadata overlap only; the field is itself the linked {item['role']} candidate. "
                   "Do not include it as a covariate for its own focal association. Any other adjustment use requires an explicitly defined estimand and source-specific justification; this catalogue is not a default adjustment set.")
    note = f"{concept_note} {restriction}".strip()
    sources = f"{item['official_questionnaire']}; {item['official_codebook']}; audit/ep_concept_source_crosswalk_v1.csv"
    def append_unique(field: str, value: str) -> str:
        existing = str(row.get(field, "") or "")
        parts = [part.strip() for part in existing.split("; ") if part.strip()]
        for part in (piece.strip() for piece in value.split("; ")):
            if part and part not in parts:
                parts.append(part)
        return "; ".join(parts)
    def append_sentence(field: str, value: str) -> str:
        existing = str(row.get(field, "") or "")
        return existing if value in existing else (f"{existing} {value}".strip())
    row.update({
        "category": "source-mapped candidate context", "subcategory": f"exact C/{item['role']} field overlap; metadata only",
        "Candidate.Status": f"C metadata linked to exact wave-specific {item['role']} concept {item['concept_id']}; covariate eligibility not inferred",
        "Harmonization.Status": append_sentence("Harmonization.Status", note),
        "Review.Flag": append_sentence("Review.Flag", restriction),
        "Value.Label.Source": append_unique("Value.Label.Source", sources),
        "Concept.ID.Candidates": append_unique("Concept.ID.Candidates", item["concept_id"]),
        "Concept.Mapping.Source": append_unique("Concept.Mapping.Source", "audit/ep_concept_source_crosswalk_v1.csv"),
        "Concept.Mapping.Status": append_sentence("Concept.Mapping.Status", item["mapping_status"]),
        "Concept.Mapping.Caveat": append_sentence("Concept.Mapping.Caveat", restriction),
        "value_label_source": append_unique("value_label_source", sources),
        "harmonization_status": append_sentence("harmonization_status", note),
        "candidate_concept_ids": append_unique("candidate_concept_ids", item["concept_id"]),
        "concept_mapping_sources": append_unique("concept_mapping_sources", "audit/ep_concept_source_crosswalk_v1.csv"),
        "concept_mapping_statuses": append_sentence("concept_mapping_statuses", item["mapping_status"]),
        "concept_mapping_caveats": append_sentence("concept_mapping_caveats", restriction),
    })


def propagate() -> None:
    items = load_items()
    targets = {(r["wave"], r["code"].lower(), r["module"].lower()): r for r in items}
    for rel in ("audit/charls_atlas_candidate_fields_v0.csv", "audit/charls_atlas_candidate_fields_v0.json",
                "site-prototype/dist/catalog.json", "site-prototype/dist/catalog_c.json"):
        path = ROOT / rel
        if not path.exists():
            continue
        count = 0
        if path.suffix == ".csv":
            frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            for key, item in targets.items():
                mask = (frame["Source.Wave"].eq(key[0]) & frame["Variable.Name"].str.lower().eq(key[1]) &
                        frame["Component"].str.lower().eq(key[2]) & frame["epcf"].str.lower().eq("c"))
                for idx in frame.index[mask]:
                    data = frame.loc[idx].to_dict(); update(data, item)
                    for field, value in data.items():
                        if field in frame.columns: frame.at[idx, field] = value
                count += int(mask.sum())
            if count != len(EXPECTED):
                raise SystemExit(f"Expected {len(EXPECTED)} exact C rows in {rel}; updated {count}")
            frame.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Component", "")).lower())
                if key in targets and str(row.get("epcf", "")).lower() == "c":
                    update(row, targets[key]); count += 1
            if count != len(EXPECTED):
                raise SystemExit(f"Expected {len(EXPECTED)} exact C rows in {rel}; updated {count}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(items[0])); writer.writeheader(); writer.writerows(items)
    print(f"Linked {len(items)} exact Questionnaire+Codebook-verified generic C rows to same-wave E/P metadata; no covariate eligibility or response recoding inferred.")


if __name__ == "__main__":
    propagate()
