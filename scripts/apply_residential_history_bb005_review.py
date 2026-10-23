"""Review the routed BB005 residential-history year field in the public C catalogue."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WAVES = ("2011", "2013", "2015", "2018")
DOCS = {
    "2011": ("sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt", "sources_official/CHARLS_2011_Codebook_extracted.txt"),
    "2013": ("sources_official/CHARLS_2013_Questionnaire_extracted.txt", "sources_official/CHARLS_2013_Codebook_extracted.txt"),
    "2015": ("sources_official/CHARLS_2015_Questionnaire_extracted.txt", "sources_official/CHARLS_2015_Codebook_extracted.txt"),
    "2018": ("sources_official/CHARLS_2018_Questionnaire_extracted.txt", "sources_official/CHARLS_2018_Codebook_extracted.txt"),
}
ARCHIVES = {"2011": "household_and_community_questionnaire_data.rar", "2013": "CHARLS2013_Dataset.zip", "2015": "CHARLS2015r.zip", "2018": "CHARLS2018r.zip"}
DESCRIPTIONS = {
    "2011": "Year",
    "2013": "In Which Year Did You First Live In this Village/Community",
    "2015": "In Which Year Did You First Live In this Village/Community",
    "2018": "Year of First Live",
}
NOTES = {
    "2011": "2011 BB005 is a four-digit calendar year for first living in the permanent address's village/community (questionnaire range 1900–2013). It is routed after BB004=No; BB004=Yes skips to BB006. The 2011 Codebook heading is only 'Year'; do not infer a more detailed label from later waves. Preserve routing and validate release-specific special values before analysis.",
    "2013": "2013 BB005 is the four-digit calendar year for first living in the permanent address's village/community (questionnaire range 1900–2013). It is routed after BB004=No; BB004=Yes skips to BB006. Preserve routed missingness and validate release-specific special values; this is residential-history context, not duration of environmental exposure by itself.",
    "2015": "2015 BB005 is the four-digit calendar year for first living in the permanent address's village/community (questionnaire range 1900–2015). It is routed after BB004=No; BB004=Yes skips to BB005_W3_1. Preserve routed missingness and validate release-specific special values; this is residential-history context, not duration of environmental exposure by itself.",
    "2018": "2018 BB005 is the four-digit calendar year for first living in the current address BB001_W3's village/community (questionnaire range 1900–2018). BB001–BB005 are asked on the new-interview route (XRType=2); returners skip this block. Keep distinct from the permanent-address wording in 2011–2015 and preserve route-specific missingness.",
}


def make_row(template: dict, wave: str) -> dict:
    row = dict(template)
    row["Variable.Name"] = "bb005"
    row["Variable.Description"] = DESCRIPTIONS[wave]
    row["Begin.Year"] = row["EndYear"] = row["Source.Wave"] = row["waves"] = wave
    row["Source.Archive"] = ARCHIVES[wave]
    row["wave_count"] = "1"
    row["Value.Labels"] = row["value_labels"] = ""
    row["Value.Label.Source"] = row["value_label_source"] = "; ".join(DOCS[wave])
    row["Value.Label.Review"] = row["value_label_review"] = "official questionnaire and Codebook reviewed; continuous calendar-year field; descriptive frequencies and statistics omitted; special-value storage pending release-specific validation"
    row["Candidate.Status"] = "C metadata candidate; source question reviewed; not an approved adjustment variable"
    row["Review.Flag"] = "C residential-history metadata; routed calendar year; not a direct environmental dose or selected adjustment covariate"
    row["Harmonization.Status"] = row["harmonization_status"] = NOTES[wave]
    return row


def main() -> None:
    # Verify official question wording and wave-specific year bounds before updating metadata.
    for wave, (qpath, cpath) in DOCS.items():
        q = (ROOT / qpath).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
        c = (ROOT / cpath).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
        if "BB005" not in q or "bb005" not in c.casefold():
            raise ValueError(f"Official BB005 questionnaire/Codebook evidence missing for {wave}")
        if wave != "2011" and "In Which Year" not in c and "Year of First Live" not in c:
            raise ValueError(f"Expected wave-specific BB005 Codebook heading missing for {wave}")
        if wave == "2018" and "XRType = 2" not in q:
            raise ValueError("2018 BB001–BB005 new-interview route not confirmed")

    field_csv = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
    fields = pd.read_csv(field_csv, dtype=str, encoding="utf-8-sig").fillna("")
    # This source CSV intentionally stores only the canonical field schema; the
    # lowercase aliases belong to generated JSON records, not extra CSV columns.
    aliases = ("variable", "waves", "wave_count", "value_labels", "value_label_source", "value_label_review", "harmonization_status")
    fields = fields.drop(columns=[c for c in aliases if c in fields.columns])
    for wave in WAVES:
        mask = fields["Variable.Name"].str.casefold().eq("bb005") & fields["Source.Wave"].eq(wave) & fields["epcf"].str.casefold().eq("c")
        if not mask.any():
            # 2011 and 2018 source fields exist in the official release inventory but
            # were absent from the candidate seed; clone a same-wave C record so the
            # browser exposes the documented wave-specific field without inventing E/P status.
            template_mask = fields["Variable.Name"].str.casefold().eq("bb004") & fields["Source.Wave"].eq(wave) & fields["epcf"].str.casefold().eq("c")
            if not template_mask.any():
                raise ValueError(f"No same-wave C metadata template for BB005 {wave}")
            row = {k: v for k, v in make_row(fields.loc[template_mask].iloc[0].to_dict(), wave).items() if k in fields.columns}
            fields = pd.concat([fields, pd.DataFrame([row])], ignore_index=True)
            mask = fields["Variable.Name"].str.casefold().eq("bb005") & fields["Source.Wave"].eq(wave) & fields["epcf"].str.casefold().eq("c")
        if int(mask.sum()) != 1:
            raise ValueError(f"Expected one BB005 C row for {wave}, found {int(mask.sum())}")
        idx = fields.index[mask][0]
        row = make_row(fields.loc[idx].to_dict(), wave)
        for key in fields.columns:
            fields.at[idx, key] = row.get(key, fields.at[idx, key])
    fields.to_csv(field_csv, index=False, encoding="utf-8-sig")

    for path in (ROOT / "audit/charls_atlas_candidate_fields_v0.json", ROOT / "site-prototype/dist/catalog.json", ROOT / "site-prototype/dist/catalog_c.json"):
        rows = json.loads(path.read_text(encoding="utf-8"))
        for wave in WAVES:
            selected = [i for i, r in enumerate(rows) if str(r.get("Variable.Name", "")).casefold() == "bb005" and str(r.get("Source.Wave", "")) == wave and str(r.get("epcf", "")).casefold() == "c"]
            if not selected:
                template = next((r for r in rows if str(r.get("Variable.Name", "")).casefold() == "bb004" and str(r.get("Source.Wave", "")) == wave and str(r.get("epcf", "")).casefold() == "c"), None)
                if template is None:
                    raise ValueError(f"No C JSON template for {path.name} BB005 {wave}")
                rows.append(make_row(template, wave))
                selected = [len(rows) - 1]
            if len(selected) != 1:
                raise ValueError(f"{path.name}: duplicate BB005 C rows for {wave}")
            rows[selected[0]] = make_row(rows[selected[0]], wave)
        path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # Rebuild the grouped series entry to include the four reviewed waves.
    series_csv = ROOT / "audit/charls_atlas_candidate_series_v0.csv"
    series = pd.read_csv(series_csv, dtype=str, encoding="utf-8-sig").fillna("")
    mask = series["Variable.Name"].str.casefold().eq("bb005") & series["epcf"].str.casefold().eq("c")
    if int(mask.sum()) != 1:
        raise ValueError(f"Expected one BB005 C series row, found {int(mask.sum())}")
    series.loc[mask, "waves"] = ",".join(WAVES)
    series.loc[mask, "wave_count"] = str(len(WAVES))
    series.loc[mask, "value_labels"] = ""
    series.loc[mask, "value_label_source"] = "; ".join(sorted({p for pair in DOCS.values() for p in pair}))
    series.loc[mask, "value_label_review"] = "official wave questionnaires and Codebooks reviewed for 2011–2018; continuous calendar-year field; frequencies omitted; release-specific special values pending validation"
    series.loc[mask, "harmonization_status"] = "Four wave-specific BB005 calendar-year records; 2011–2015 permanent-address wording differs from 2018 current-address BB001_W3 wording. Routed after BB004=No; 2018 block limited to XRType=2 new interviews. Do not combine years or infer exposure duration without release-specific routing, address-reference and estimand validation."
    series.to_csv(series_csv, index=False, encoding="utf-8-sig")
    (ROOT / "audit/charls_atlas_candidate_series_v0.json").write_text(json.dumps(series.to_dict(orient="records"), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    audit = ROOT / "audit/residential_history_bb005_source_review_2011_2018_2026-10-24.md"
    lines = ["# BB005 residential-history year source review, 2011–2018", "", "Official wave questionnaires and Codebooks were reviewed. No respondent records, Codebook descriptive statistics, or frequencies were used.", "", "| Wave | Official question scope | Route and treatment |", "|---|---|---|"]
    lines.extend([
        "| 2011 | Year first lived in permanent address's village/community; questionnaire range 1900–2013 | BB004=Yes skips to BB006; BB004=No receives year question. Codebook calls it only ‘Year’; retain the less specific source identity. |",
        "| 2013 | Year first lived in permanent address's village/community; questionnaire range 1900–2013 | BB004=Yes skips to BB006; BB004=No receives year question. |",
        "| 2015 | Year first lived in permanent address's village/community; questionnaire range 1900–2015 | BB004=Yes skips to BB005_W3_1; BB004=No receives year question. |",
        "| 2018 | Year first lived in current address BB001_W3's village/community; questionnaire range 1900–2018 | BB001–BB005 asked only for new interviews (XRType=2); BB004=No routes to BB005. Keep distinct from the earlier permanent-address wording. |",
        "", "BB005 is a continuous calendar-year residential-history field, not an exposure-duration measure by itself. Conditional nonresponse is structural, not a substantive value. Preserve the year as recorded, validate special codes and respondent eligibility against the authorized release, and do not use Codebook means, ranges, or OBS counts as sample-size or analysis evidence. No direct environmental concentration, current neighborhood quality, or approved covariate role is implied.", "",
        "Sources: " + "; ".join(f"`{p}`" for pair in DOCS.values() for p in pair), ""
    ])
    audit.write_text("\n".join(lines), encoding="utf-8")
    print("Reviewed and catalogued BB005 for four waves; routed year metadata only, no frequencies or respondent data.")


if __name__ == "__main__":
    main()
