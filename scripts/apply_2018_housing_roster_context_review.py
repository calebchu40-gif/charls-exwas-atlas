"""Apply source-reviewed Wave 4 housing-roster context metadata to C fields."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WAVE = "2018"
ROSTER_CODES = {f"ha025_w4_{i}_" for i in range(1, 12)}
MORTGAGE_CODE = "ha057_w3"
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


def update(row: dict) -> None:
    code = str(row.get("Variable.Name", "")).lower()
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

    for path in (ROOT / "audit/charls_atlas_candidate_fields_v0.json", ROOT / "site-prototype/dist/catalog.json", ROOT / "site-prototype/dist/catalog_c.json"):
        rows = json.loads(path.read_text(encoding="utf-8"))
        selected = [r for r in rows if str(r.get("Source.Wave", "")) == WAVE and str(r.get("Variable.Name", "")).lower() in codes and str(r.get("epcf", "")).lower() == "c"]
        if {str(r["Variable.Name"]).lower() for r in selected} != codes:
            raise ValueError(f"{path}: expected all 12 Wave 4 C fields")
        for row in selected:
            update(row)
        path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"Updated {len(selected)} audited fields in {path.relative_to(ROOT)}")

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
        f"Sources: `{SOURCE}`. No respondent data, Codebook frequencies, minima, maxima, or other descriptive statistics were used.\n",
        encoding="utf-8",
    )
    print("Reviewed 11 property roster fields and one continuous mortgage-payment field.")


if __name__ == "__main__":
    main()
