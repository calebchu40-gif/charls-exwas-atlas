"""Apply source-reviewed Wave 4 housing-roster context metadata to C fields."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WAVE = "2018"
ROSTER_CODES = {f"ha025_w4_{i}_" for i in range(1, 12)}
MORTGAGE_CODE = "ha057_w3"
RESIDENCE_CODE = "i000_w4_2"
SOURCE = (
    "sources_official/CHARLS_2018_Questionnaire_extracted.txt; "
    "sources_official/CHARLS_2018_Codebook_extracted.txt"
)
ROSTER_LABELS = (
    "1=City or town central areas; 2=Town or semi-rural areas; "
    "3=Rural areas; 4=Special regions"
)
ROSTER_REVIEW = (
    "official 2018 questionnaire response menu reviewed; roster-slot response labels; "
    "Codebook summary frequencies omitted; confirm release-specific special values"
)
ROSTER_NOTE = (
    "2018 HA025_W4[i] records whether each separately listed house property is in a "
    "city/town central area, town/semi-rural area, rural area, or special region. The [i] "
    "suffix is the property roster position, not respondent identity or survey wave. This is "
    "property-level context, not automatically the respondent's current residence or a "
    "community urbanicity measure. Preserve the house-property linkage and do not treat the "
    "roster slots as independent observations. The questionnaire defines the four labels; "
    "Codebook frequencies are not copied. Verify released coding, special/missing values, "
    "eligible roster slots, and any household-to-person linkage before analysis. This C entry "
    "is discovery metadata, not an approved adjustment variable."
)
MORTGAGE_REVIEW = (
    "official 2018 questionnaire identifies continuous household mortgage payment in "
    "10,000 Yuan/month; no discrete labels; route and release-specific special values require QA"
)
MORTGAGE_NOTE = (
    "2018 HA057_W3 asks the monthly mortgage payment after the mortgage route for the "
    "respondent's and spouse's houses; the interviewer instruction covers owned properties "
    "with an active mortgage and excludes properties whose mortgage is paid off. Unit: "
    "10,000 Yuan/month. This is a household/property payment measure, not an individual "
    "income or routine adjustment variable. Keep it separate from outstanding principal and "
    "unpaid interest; validate route, multiple-property aggregation, special values, and "
    "release storage before analysis. No Codebook summary statistics are copied."
)
RESIDENCE_LABELS = (
    "1=City/Town central area; 2=Rural-urban fringe; 3=Rural; 4=Special zone"
)
RESIDENCE_REVIEW = (
    "official 2018 questionnaire and Codebook response categories reviewed; preserve Codebook labels; "
    "questionnaire wording differs slightly; confirm route and special values in release"
)
RESIDENCE_NOTE = (
    "2018 I000_W4_2 describes the rural/urban context of the main respondent's currently occupied "
    "house, selected at I000_W4 from the preloaded property list (or 99=None of the above). It is "
    "distinct from HA025_W4[i], which describes each separately listed property. The questionnaire "
    "and Codebook use slightly different English renderings of the same four categories; the displayed "
    "labels follow the Codebook. This is a single-wave residence-context candidate, not a direct "
    "pollutant measurement, community classification, or automatically selected adjustment variable. "
    "Preserve the residence-selection route and verify released missing/special codes and eligible "
    "denominator; cross-wave equivalence is not approved."
)


def update(row: dict) -> None:
    code = str(row.get("Variable.Name", "")).lower()
    role = str(row.get("epcf", "")).lower()
    if code == RESIDENCE_CODE:
        row["Value.Labels"] = RESIDENCE_LABELS
        row["value_labels"] = RESIDENCE_LABELS
        row["Value.Label.Source"] = SOURCE
        row["value_label_source"] = SOURCE
        row["Value.Label.Review"] = RESIDENCE_REVIEW
        row["value_label_review"] = RESIDENCE_REVIEW
        row["Harmonization.Status"] = RESIDENCE_NOTE
        row["harmonization_status"] = RESIDENCE_NOTE
        row["Review.Flag"] = (
            "C search metadata for an existing E candidate; current-residence context only; "
            "not an adjustment recommendation"
            if role == "c" else
            "preserve source item and mapping status; context candidate, not an approved test variable"
        )
        if role == "e":
            row["Concept.Mapping.Status"] = (
                "official 2018 questionnaire and Codebook reviewed; main respondent's current residence "
                "context; response labels documented; cross-wave equivalence and analysis eligibility pending"
            )
            row["Concept.Mapping.Caveat"] = RESIDENCE_NOTE
            row["concept_mapping_statuses"] = row["Concept.Mapping.Status"]
            row["concept_mapping_caveats"] = RESIDENCE_NOTE
        return
    row["Value.Label.Source"] = SOURCE
    row["value_label_source"] = SOURCE
    if code in ROSTER_CODES:
        row["Value.Labels"] = ROSTER_LABELS
        row["value_labels"] = ROSTER_LABELS
        row["Value.Label.Review"] = ROSTER_REVIEW
        row["value_label_review"] = ROSTER_REVIEW
        row["Concept.Unit.Candidates"] = "— (categorical property-context response)"
        row["candidate_concept_units"] = "— (categorical property-context response)"
        row["Harmonization.Status"] = ROSTER_NOTE
        row["harmonization_status"] = ROSTER_NOTE
        row["Review.Flag"] = "C metadata; property-roster context only; not a respondent residence measure or selected model covariate"
    elif code == MORTGAGE_CODE:
        row["Value.Labels"] = ""
        row["value_labels"] = ""
        row["Value.Label.Review"] = MORTGAGE_REVIEW
        row["value_label_review"] = MORTGAGE_REVIEW
        row["Concept.Unit.Candidates"] = "10,000 Yuan/month"
        row["candidate_concept_units"] = "10,000 Yuan/month"
        row["Harmonization.Status"] = MORTGAGE_NOTE
        row["harmonization_status"] = MORTGAGE_NOTE
        row["Review.Flag"] = "C metadata; continuous household mortgage payment; not a selected model covariate"
    else:
        raise ValueError(f"Unexpected field: {code}")


def main() -> None:
    questionnaire_path = ROOT / "sources_official/CHARLS_2018_Questionnaire_extracted.txt"
    codebook_path = ROOT / "sources_official/CHARLS_2018_Codebook_extracted.txt"
    questionnaire = questionnaire_path.read_text(encoding="utf-8", errors="replace").casefold()
    codebook_lines = codebook_path.read_text(encoding="utf-8", errors="replace").splitlines()
    for code in ROSTER_CODES | {MORTGAGE_CODE}:
        if not any(line.casefold().startswith(code.casefold() + ":") for line in codebook_lines):
            raise ValueError(f"Codebook field heading not found: {code}")
    # The questionnaire presents HA025_W4 as a loop over [i]; individual
    # flattened release names (ha025_w4_1_, etc.) appear in the Codebook.
    if "ha025_w4[𝑖]" not in questionnaire and "ha025_w4[i]" not in questionnaire:
        raise ValueError("Questionnaire does not contain the HA025_W4 property loop")
    for phrase in ("City or town central areas", "Town or semi-rural areas", "Rural areas", "Special regions"):
        if phrase.casefold() not in questionnaire:
            raise ValueError(f"Questionnaire response label not found: {phrase}")
    mortgage_at = questionnaire.find("ha057_w3")
    if mortgage_at < 0 or "10,000 yuan" not in questionnaire[mortgage_at:mortgage_at + 1200]:
        raise ValueError("Mortgage-payment unit not found near HA057_W3")
    for phrase in ("I000_W4_2", "currently living in", "City or town central areas", "Town or semi-rural areas", "Rural areas", "Special regions"):
        if phrase.casefold() not in questionnaire:
            raise ValueError(f"Current-residence questionnaire wording not found: {phrase}")
    if not any(line.casefold().startswith("i000_w4_2:") for line in codebook_lines):
        raise ValueError("Codebook field heading not found: i000_w4_2")

    codes = {code.casefold() for code in ROSTER_CODES | {MORTGAGE_CODE}}
    csv_path = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
    table = pd.read_csv(csv_path, dtype=str, encoding="utf-8-sig").fillna("")
    mask = table["Source.Wave"].eq(WAVE) & table["Variable.Name"].str.lower().isin(codes) & table["epcf"].str.lower().eq("c")
    found = set(table.loc[mask, "Variable.Name"].str.lower())
    if found != codes:
        raise ValueError(f"Expected all 12 Wave 4 C fields, found {sorted(found)}")
    for idx in table.index[mask]:
        row = table.loc[idx].to_dict()
        update(row)
        for key in ("Value.Labels", "Value.Label.Review", "Value.Label.Source", "Concept.Unit.Candidates", "Harmonization.Status", "Review.Flag"):
            table.at[idx, key] = row[key]
    table.to_csv(csv_path, index=False, encoding="utf-8-sig")

    residence_csv = table[table["Source.Wave"].eq(WAVE) & table["Variable.Name"].str.lower().eq(RESIDENCE_CODE)]
    if set(residence_csv["epcf"].str.lower()) != {"e", "c"}:
        raise ValueError("Expected both E and C candidate rows for 2018 i000_w4_2")
    for idx in residence_csv.index:
        row = table.loc[idx].to_dict()
        update(row)
        for key in ("Value.Labels", "Value.Label.Review", "Value.Label.Source", "Harmonization.Status", "Review.Flag", "Concept.Mapping.Status", "Concept.Mapping.Caveat"):
            if key in table.columns:
                table.at[idx, key] = row.get(key, "")
    table.to_csv(csv_path, index=False, encoding="utf-8-sig")

    for path in (ROOT / "audit/charls_atlas_candidate_fields_v0.json", ROOT / "site-prototype/dist/catalog.json", ROOT / "site-prototype/dist/catalog_c.json", ROOT / "site-prototype/dist/catalog_e.json"):
        rows = json.loads(path.read_text(encoding="utf-8"))
        if path.name == "catalog_e.json":
            selected = [r for r in rows if str(r.get("Source.Wave", "")) == WAVE and str(r.get("Variable.Name", "")).lower() == RESIDENCE_CODE and str(r.get("epcf", "")).lower() == "e"]
        else:
            selected = [r for r in rows if str(r.get("Source.Wave", "")) == WAVE and str(r.get("Variable.Name", "")).lower() in codes and str(r.get("epcf", "")).lower() == "c"]
            selected.extend(r for r in rows if str(r.get("Source.Wave", "")) == WAVE and str(r.get("Variable.Name", "")).lower() == RESIDENCE_CODE and str(r.get("epcf", "")).lower() == "c")
            if path.name in {"catalog.json", "charls_atlas_candidate_fields_v0.json"}:
                selected.extend(r for r in rows if str(r.get("Source.Wave", "")) == WAVE and str(r.get("Variable.Name", "")).lower() == RESIDENCE_CODE and str(r.get("epcf", "")).lower() == "e")
        if path.name != "catalog_e.json" and {str(r["Variable.Name"]).lower() for r in selected if str(r.get("Variable.Name", "")).lower() in codes} != codes:
            raise ValueError(f"{path}: expected all 12 Wave 4 C fields")
        if path.name == "catalog_e.json" and len(selected) != 1:
            raise ValueError(f"{path}: expected the Wave 4 urban/rural E candidate")
        for row in selected:
            update(row)
        path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"Updated {len(selected)} audited fields in {path.relative_to(ROOT)}")

    housing_map_path = ROOT / "audit/housing_exposure_variable_mapping_v1.csv"
    housing_map = pd.read_csv(housing_map_path, dtype=str, encoding="utf-8-sig").fillna("")
    housing_mask = housing_map["wave"].eq(WAVE) & housing_map["code"].str.lower().eq(RESIDENCE_CODE)
    if int(housing_mask.sum()) != 1:
        raise ValueError("Expected one 2018 current-residence mapping row")
    housing_map.loc[housing_mask, "mapping_status"] = "official 2018 questionnaire and Codebook reviewed; response labels documented; cross-wave equivalence and analysis eligibility pending"
    housing_map.loc[housing_mask, "construct"] = "main respondent's currently occupied residence context"
    housing_map.loc[housing_mask, "caveat"] = RESIDENCE_NOTE
    housing_map.to_csv(housing_map_path, index=False, encoding="utf-8-sig")

    concept_map_path = ROOT / "audit/ep_concept_source_crosswalk_v1.csv"
    concept_map = pd.read_csv(concept_map_path, dtype=str, encoding="utf-8-sig").fillna("")
    concept_mask = concept_map["Wave"].eq(WAVE) & concept_map["Source.Code"].str.lower().eq(RESIDENCE_CODE) & concept_map["Role"].str.lower().eq("e")
    if int(concept_mask.sum()) != 1:
        raise ValueError("Expected one E concept-source mapping for the current residence field")
    concept_map.loc[concept_mask, "Value.Labels"] = RESIDENCE_LABELS
    concept_map.loc[concept_mask, "Mapping.Status"] = housing_map.loc[housing_mask, "mapping_status"].iloc[0]
    concept_map.loc[concept_mask, "Caveat"] = RESIDENCE_NOTE
    concept_map.to_csv(concept_map_path, index=False, encoding="utf-8-sig")

    series_path = ROOT / "audit/charls_atlas_candidate_series_v0.csv"
    series = pd.read_csv(series_path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = series["Variable.Name"].str.lower().isin(codes) & series["waves"].eq(WAVE) & series["epcf"].str.lower().eq("c")
    if set(series.loc[selected, "Variable.Name"].str.lower()) != codes:
        raise ValueError("Candidate series does not contain the same 12 Wave 4 C fields")
    for idx in series.index[selected]:
        row = series.loc[idx].to_dict()
        update(row)
        series.at[idx, "value_labels"] = row["Value.Labels"]
        series.at[idx, "value_label_source"] = row["Value.Label.Source"]
        series.at[idx, "value_label_review"] = row["Value.Label.Review"]
        series.at[idx, "candidate_concept_units"] = row["Concept.Unit.Candidates"]
        series.at[idx, "harmonization_status"] = row["Harmonization.Status"]
    residence_series = series[series["Variable.Name"].str.lower().eq(RESIDENCE_CODE) & series["waves"].eq(WAVE)]
    if set(residence_series["epcf"].str.lower()) != {"e", "c"}:
        raise ValueError("Candidate series must contain both E and C residence-context rows")
    for idx in residence_series.index:
        row = series.loc[idx].to_dict()
        update(row)
        for key, value_key in (("value_labels", "Value.Labels"), ("value_label_source", "Value.Label.Source"), ("value_label_review", "Value.Label.Review"), ("harmonization_status", "Harmonization.Status"), ("concept_mapping_statuses", "Concept.Mapping.Status"), ("concept_mapping_caveats", "Concept.Mapping.Caveat")):
            if key in series.columns:
                series.at[idx, key] = row.get(value_key, "")
    series.to_csv(series_path, index=False, encoding="utf-8-sig")
    (ROOT / "audit/charls_atlas_candidate_series_v0.json").write_text(
        json.dumps(series.to_dict(orient="records"), ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    print(f"Updated {int(selected.sum())} audited fields in {series_path.relative_to(ROOT)}")

    audit_path = ROOT / "audit/housing_roster_context_review_2018_2026-10-24.md"
    audit_path.write_text(
        "# 2018 housing roster context review\n\n"
        "Reviewed the Wave 4 questionnaire and Codebook for HA025_W4[i] property-location fields (i=1–11) and HA057_W3 monthly mortgage payment. "
        "The 11 location rows use the questionnaire's four response labels; Codebook frequencies were not transcribed because they are descriptive release summaries, not category definitions. "
        "These are C metadata entries and do not recommend covariate adjustment.\n\n"
        f"HA025 labels: {ROSTER_LABELS}. Each suffix denotes a listed house-property slot. It must not be interpreted as respondent current residence, a community measure, or 11 independent exposures. "
        "Keep property-to-household/person linkage and eligible roster denominators explicit.\n\n"
        "HA057_W3 is a continuous 10,000 Yuan/month household mortgage payment on the active-mortgage route. The 2018 questionnaire asks about mortgages for the respondent's/spouse's houses and excludes properties with a paid-off mortgage. "
        "Do not merge it with outstanding principal or unpaid interest. Multiple-property aggregation, special values, and release storage need authorized-data QA.\n\n"
        f"Sources: `{SOURCE}`. No respondent data, Codebook frequencies, minima, maxima, or other descriptive statistics were used.\n\n"
        "## Current residence urban/rural item\n\n"
        f"I000_W4_2 describes the main respondent's currently occupied house selected from the preloaded property list. It is distinct from HA025_W4[i], which records location for each listed property. The questionnaire and Codebook use slightly different English renderings; the catalog keeps the Codebook labels `{RESIDENCE_LABELS}` and cites both documents. This is a single-wave context candidate; cross-wave equivalence and analysis eligibility remain open. It is not a pollutant measurement or an automatically selected adjustment variable.\n",
        encoding="utf-8",
    )
    print("Reviewed 11 property-roster fields, one continuous mortgage-payment field, and reconciled the current-residence E/C source row.")


if __name__ == "__main__":
    main()
