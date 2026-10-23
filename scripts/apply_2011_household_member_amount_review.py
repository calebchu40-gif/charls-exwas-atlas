"""Apply questionnaire-backed units to 2011 household-member income slots."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
MAPPING = AUDIT / "household_member_income_mapping_v1.csv"
def review_status(wave: str) -> str:
    return (
        f"official {wave} questionnaire identifies Yuan amount period and household-member roster slot; "
        "continuous amount with no discrete response categories; authorized-release storage scale and special values remain unverified"
    )


def sources(wave: str) -> str:
    questionnaire = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt"
    return f"sources_official/{questionnaire}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"


def semantics(wave: str, concept: str) -> tuple[str, str]:
    unit = "Yuan/year" if concept.endswith("_annual") else "Yuan/month"
    wording = "annual amount reported for the past year" if unit.endswith("year") else "monthly amount"
    return unit, (
        f"{wave} {wording} in {unit}; this is a household-member roster slot, not automatically the respondent's "
        "personal income or a complete household total. Preserve slot and household linkage; do not sum slots, "
        "annualize monthly entries, or assign the amount to an individual without the official roster relationship. "
        "Exact item wording and pre-/post-tax/social-insurance scope vary by wave; retain the source wave and wording. "
        "The questionnaire's soft checks are not analytic cutoffs. Confirm release-specific stored scale, special "
        "values, financial-respondent route, and eligible denominator in authorized-data QA."
    )


def main() -> None:
    frame = pd.read_csv(MAPPING, dtype=str, encoding="utf-8-sig").fillna("")
    for column in ("value_label_status", "value_label_source", "value_semantics", "unit"):
        if column not in frame:
            frame[column] = ""
    selected = frame[frame["wave"].isin({"2011", "2013", "2015"}) & frame["concept_id"].isin({
        "household_member_salary_annual", "household_member_salary_monthly",
        "household_member_pension_annual", "household_member_pension_monthly",
        "household_member_pension_subsidy_annual", "household_member_pension_subsidy_monthly",
        "household_member_other_income_annual", "household_member_other_income_monthly",
    })].copy()
    expected_by_wave = {"2011": 80, "2013": 24, "2015": 20}
    observed_by_wave = selected.groupby("wave").size().to_dict()
    if observed_by_wave != expected_by_wave:
        raise SystemExit(f"Expected household-member amounts by wave {expected_by_wave}; found {observed_by_wave}")
    for idx, row in selected.iterrows():
        wave, code, concept = row["wave"], row["code"].lower(), row["concept_id"]
        qfile = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt"
        questionnaire = (ROOT / "sources_official" / qfile).read_text(encoding="utf-8", errors="replace").lower()
        codebook = (ROOT / "sources_official" / f"CHARLS_{wave}_Codebook_extracted.txt").read_text(encoding="utf-8", errors="replace").lower()
        compact_codebook = re.sub(r"[^a-z0-9]", "", codebook)
        questionnaire_stem = "ga006" if concept.startswith("household_member_salary_") else "ga008"
        if questionnaire_stem not in questionnaire or re.sub(r"[^a-z0-9]", "", code) not in compact_codebook:
            raise SystemExit(f"Official questionnaire/Codebook field not found: {wave}/{code}")
        unit, note = semantics(wave, concept)
        status = review_status(wave)
        source = sources(wave)
        row["value_label_status"] = status
        row["value_label_source"] = source
        row["unit"] = unit
        row["value_semantics"] = note
        row["caveat"] = (row["caveat"].rstrip(".") + "; " + note)
        row["mapping_status"] = status
        frame.loc[idx, row.index] = row
        selected.loc[idx, row.index] = row
    frame.to_csv(MAPPING, index=False, encoding="utf-8-sig")

    catalog_csv = AUDIT / "charls_atlas_candidate_fields_v0.csv"
    if catalog_csv.exists():
        catalog = pd.read_csv(catalog_csv, dtype=str, encoding="utf-8-sig").fillna("")
        for row in selected.to_dict("records"):
            mask = catalog["Source.Wave"].eq(row["wave"]) & catalog["Variable.Name"].str.lower().eq(row["code"].lower())
            if not mask.any():
                raise SystemExit(f"Amount field missing from candidate catalogue: {row['code']}")
            catalog.loc[mask, "Unit"] = row["unit"]
            catalog.loc[mask, "Concept.Unit.Candidates"] = row["unit"]
            catalog.loc[mask, "Value.Labels"] = ""
            catalog.loc[mask, "Value.Label.Source"] = source
            catalog.loc[mask, "Value.Label.Review"] = status
            catalog.loc[mask, "Harmonization.Status"] = semantics(row["wave"], row["concept_id"])[1]
        catalog.to_csv(catalog_csv, index=False, encoding="utf-8-sig")

    master = ROOT / "site-prototype/dist/catalog.json"
    if master.exists():
        records = json.loads(master.read_text(encoding="utf-8"))
        # A completed site build stores concept-series rows here, not the
        # source-wave field rows. In that state the candidate field CSV/JSON
        # is authoritative and build_charls_atlas_catalog.py will regenerate
        # this derived series catalog later in the pipeline.
        if records and "Source.Wave" in records[0]:
            for row in selected.to_dict("records"):
                matches = [item for item in records if str(item.get("Source.Wave")) == row["wave"] and str(item.get("Variable.Name", "")).lower() == row["code"].lower()]
                if not matches:
                    raise SystemExit(f"Amount field missing from master site catalogue: {row['code']}")
                unit, note = semantics(row["wave"], row["concept_id"])
                status = review_status(row["wave"])
                source = sources(row["wave"])
                for item in matches:
                    item["Unit"] = item["Concept.Unit.Candidates"] = unit
                    item["Value.Labels"] = item["value_labels"] = ""
                    item["Value.Label.Source"] = item["value_label_source"] = source
                    item["Value.Label.Review"] = item["value_label_review"] = status
                    item["Harmonization.Status"] = item["harmonization_status"] = note
            master.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"2011–2015 household-member amount review applied to {len(selected)} fields; units carried; no response values or Codebook frequencies copied")


if __name__ == "__main__":
    main()
