"""Review the remaining 2011–2015 housing/property money fields as amounts."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
FIELDS = {
    **{("2011", f"ha049_{i}_"): "Yuan" for i in range(1, 4)},
    **{("2011", f"ha047_{i}_"): "10,000 Yuan" for i in range(1, 3)},
    **{("2011", f"ha043_{i}_"): "10,000 Yuan" for i in range(1, 4)},
    ("2011", "ha023_1"): "10,000 Yuan", ("2011", "ha023_2"): "1,000 Yuan/square metre",
    ("2011", "ha022"): "10,000 Yuan", ("2011", "ha018"): "10,000 Yuan",
    **{("2013", f"ha043_{i}_"): "10,000 Yuan" for i in range(1, 5)},
    **{("2013", f"ha034_1_{i}_"): "10,000 Yuan" for i in range(1, 5)},
    **{("2013", f"ha034_2_{i}_"): "1,000 Yuan/square metre" for i in range(1, 5)},
    ("2013", "ha023_1"): "10,000 Yuan", ("2013", "ha023_2"): "1,000 Yuan/square metre",
    ("2013", "ha022"): "10,000 Yuan", ("2013", "ha018"): "10,000 Yuan",
    **{("2015", f"ha043_{i}_"): "10,000 Yuan" for i in range(1, 5)},
    **{("2015", f"ha034_1_{i}_"): "10,000 Yuan" for i in range(1, 5)},
    **{("2015", f"ha034_2_{i}_"): "1,000 Yuan/square metre" for i in range(1, 5)},
}
QUESTIONNAIRE = {
    "2011": ("CHARLS_2011_Baseline_Questionnaire_official_extracted.txt", "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"),
    "2013": ("CHARLS_2013_Questionnaire_extracted.txt",),
    "2015": ("CHARLS_2015_Questionnaire_extracted.txt",),
}
CODEBOOK = {w: f"CHARLS_{w}_Codebook_extracted.txt" for w in QUESTIONNAIRE}


def sources(wave: str) -> str:
    return "; ".join([*(f"sources_official/{p}" for p in QUESTIONNAIRE[wave]), f"sources_official/{CODEBOOK[wave]}"])


def unit_semantics(unit: str) -> str:
    return f"continuous monetary amount; questionnaire reporting unit {unit}"


def update_catalog_csv(path: Path) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: (str(r["Source.Wave"]), str(r["Variable.Name"]).lower()) in FIELDS, axis=1)
    found = set(zip(df.loc[selected, "Source.Wave"], df.loc[selected, "Variable.Name"].str.lower()))
    if found != set(FIELDS):
        raise ValueError(f"{path}: reviewed fields missing={sorted(set(FIELDS)-found)}")
    extra = "Official questionnaire soft checks are interviewer prompts, not analytic cutoffs. This review confirms the question's amount unit but not the authorized-release storage scale, special-value codes or complete unfolding-bracket linkage."
    for idx in df.index[selected]:
        wave, code = str(df.at[idx, "Source.Wave"]), str(df.at[idx, "Variable.Name"]).lower()
        unit = FIELDS[(wave, code)]
        df.at[idx, "Concept.Unit.Candidates"] = unit
        df.at[idx, "Unit"] = unit
        if "candidate_concept_units" in df.columns:
            df.at[idx, "candidate_concept_units"] = unit
        df.at[idx, "Value.Labels"] = ""
        df.at[idx, "Value.Label.Source"] = sources(wave)
        review = f"Official questionnaire identifies a numeric monetary amount; {unit_semantics(unit)}; no discrete category labels assigned; release storage and special codes remain unverified."
        df.at[idx, "Value.Label.Review"] = review
        if "value_labels" in df.columns: df.at[idx, "value_labels"] = ""
        if "value_label_source" in df.columns: df.at[idx, "value_label_source"] = sources(wave)
        if "value_label_review" in df.columns: df.at[idx, "value_label_review"] = review
        old = str(df.at[idx, "Harmonization.Status"])
        df.at[idx, "Harmonization.Status"] = old if extra in old else (old + " " + extra).strip()
        if "harmonization_status" in df.columns: df.at[idx, "harmonization_status"] = df.at[idx, "Harmonization.Status"]
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_crosswalk_csv(path: Path) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: (str(r["Wave"]), str(r["Source.Code"]).lower()) in FIELDS, axis=1)
    found = set(zip(df.loc[selected, "Wave"], df.loc[selected, "Source.Code"].str.lower()))
    if found != set(FIELDS):
        raise ValueError(f"{path}: reviewed fields missing={sorted(set(FIELDS)-found)}")
    for idx in df.index[selected]:
        wave, code = str(df.at[idx, "Wave"]), str(df.at[idx, "Source.Code"]).lower()
        unit = FIELDS[(wave, code)]
        df.at[idx, "Unit"] = unit
        df.at[idx, "Value.Semantics"] = unit_semantics(unit) + "; no discrete categories assigned"
        df.at[idx, "Mapping.Status"] = "official questionnaire amount unit verified; authorized-release storage/special codes pending"
        extra = "Official questionnaire soft checks are interviewer prompts, not analytic cutoffs; authorized-release storage scale, special values and bracket linkage still require verification."
        old = str(df.at[idx, "Caveat"])
        df.at[idx, "Caveat"] = old if extra in old else (old + " " + extra).strip()
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_catalog_json(path: Path) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    selected = [r for r in rows if (str(r.get("Source.Wave", "")), str(r.get("Variable.Name", "")).lower()) in FIELDS]
    found = {(str(r["Source.Wave"]), str(r["Variable.Name"]).lower()) for r in selected}
    if found != set(FIELDS):
        raise ValueError(f"{path}: reviewed fields missing={sorted(set(FIELDS)-found)}")
    for row in selected:
        wave, code = str(row["Source.Wave"]), str(row["Variable.Name"]).lower()
        unit = FIELDS[(wave, code)]
        review = f"Official questionnaire identifies a numeric monetary amount; {unit_semantics(unit)}; no discrete category labels assigned; release storage and special codes remain unverified."
        row.update({
            "Concept.Unit.Candidates": unit, "Unit": unit, "Concept.Unit": unit,
            "candidate_concept_units": unit, "unit": unit,
            "Value.Labels": "", "value_labels": "",
            "Value.Label.Source": sources(wave), "value_label_source": sources(wave),
            "Value.Label.Review": review, "value_label_review": review,
        })
        if "Value.Label.Review" in row:
            row["Value.Label.Review"] += ""
        if "Harmonization.Status" in row:
            extra = "Official questionnaire soft checks are interviewer prompts, not analytic cutoffs. Verify authorized-release storage scale, special values and bracket linkage before analysis."
            old = row.get("Harmonization.Status", "")
            row["Harmonization.Status"] = old if extra in old else old + " " + extra
            row["harmonization_status"] = row["Harmonization.Status"]
    path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(selected)


def main() -> None:
    mapping_path = AUDIT / "housing_exposure_variable_mapping_v1.csv"
    mapping = pd.read_csv(mapping_path, dtype=str, encoding="utf-8-sig").fillna("")
    lookup = {(str(r.wave), str(r.code).lower()): r for r in mapping.itertuples(index=False)}
    if not set(FIELDS).issubset(lookup):
        raise ValueError(f"housing mapping lacks reviewed keys: {sorted(set(FIELDS)-set(lookup))}")
    for wave, files in QUESTIONNAIRE.items():
        questionnaire_text = "\n".join((ROOT / "sources_official" / name).read_text(encoding="utf-8", errors="ignore") for name in files).casefold()
        codebook_text = (ROOT / "sources_official" / CODEBOOK[wave]).read_text(encoding="utf-8", errors="ignore").casefold()
        for w, code in FIELDS:
            if w != wave:
                continue
            question_prefix = code.split("_")[0]
            codebook_code = " ".join(code.rstrip("_").split("_")).casefold()
            if question_prefix not in questionnaire_text or not (code in codebook_text or codebook_code in codebook_text):
                raise ValueError(f"official source verification failed for {wave}/{code}")
    for (wave, code), unit in FIELDS.items():
        mask = mapping.wave.eq(wave) & mapping.code.str.lower().eq(code)
        mapping.loc[mask, "unit"] = unit
        mapping.loc[mask, "mapping_status"] = "official questionnaire amount unit verified; authorized-release storage/special codes pending"
        extra = "Official questionnaire soft checks are interviewer prompts, not analytic cutoffs; authorized-release storage scale, special values and bracket linkage still require verification."
        old = str(mapping.loc[mask, "caveat"].iloc[0])
        mapping.loc[mask, "caveat"] = old if extra in old else old + " " + extra
    mapping.to_csv(mapping_path, index=False, encoding="utf-8-sig")
    update_catalog_csv(AUDIT / "charls_atlas_candidate_fields_v0.csv")
    update_crosswalk_csv(AUDIT / "ep_concept_source_crosswalk_v1.csv")
    for path in (AUDIT / "charls_atlas_candidate_fields_v0.json", ROOT / "site-prototype/dist/catalog.json"):
        update_catalog_json(path)
    housing_path = ROOT / "site-prototype/dist/housing_catalog_v1.json"
    housing = json.loads(housing_path.read_text(encoding="utf-8"))
    selected = [r for r in housing if (str(r.get("wave", "")), str(r.get("code", "")).lower()) in FIELDS]
    found = {(str(r["wave"]), str(r["code"]).lower()) for r in selected}
    if found != set(FIELDS):
        raise ValueError(f"{housing_path}: reviewed fields missing={sorted(set(FIELDS)-found)}")
    for row in selected:
        wave, code = str(row["wave"]), str(row["code"]).lower()
        unit = FIELDS[(wave, code)]
        row["unit"] = unit
        row["value_label_source"] = sources(wave)
        row["value_label_status"] = f"Official questionnaire identifies numeric monetary amount; {unit_semantics(unit)}; no discrete categories assigned; release storage/special codes unverified."
        row["mapping_status"] = "official questionnaire amount unit reviewed; authorized-release numeric storage still requires verification"
        extra = "Official questionnaire soft checks are interviewer prompts, not analytic cutoffs; verify authorized-release storage scale, special values and bracket linkage before analysis."
        old = str(row.get("caveat", ""))
        row["caveat"] = old if extra in old else old + " " + extra
    housing_path.write_text(json.dumps(housing, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Reviewed {len(FIELDS)} 2011–2015 housing/property amount fields; units verified from official questionnaires; no respondent values or frequencies copied.")


if __name__ == "__main__":
    main()
