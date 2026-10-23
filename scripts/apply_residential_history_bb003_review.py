"""Review wave-specific BB003 county/city/district move-in year metadata."""
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
    "2011": "When did you first live in permanent address’s county/city/district?",
    "2013": "When did you First Live in This County/City/District",
    "2015": "When Did You First Live in This County/City/District",
    "2018": "When did You First Live in This County/City/District",
}
NOTES = {
    "2011": "2011 BB003 is the four-digit calendar year for first living in the permanent address's county/city/district (questionnaire range 1900–2013). The demographic-background procedure varies by new-interview/reinterview path and the preceding BB001 response; use release routing to define eligibility rather than treating missingness as a value. This is distinct from BB005's village/community year.",
    "2013": "2013 BB003 is the four-digit calendar year for first living in the permanent address's county/city/district (questionnaire range 1900–2013). The demographic-background procedure varies by new-interview/reinterview path and the preceding BB001 response; use release routing to define eligibility rather than treating missingness as a value. This is distinct from BB005's village/community year.",
    "2015": "2015 BB003 is the four-digit calendar year for first living in the permanent address's county/city/district (questionnaire range 1900–2015). The questionnaire routes to BB003 when BB001_W3 is not 1 or XRType=NEWIW; otherwise it skips to BB005_W3_1. Preserve this route and distinguish the county/city year from BB005's village/community year.",
    "2018": "2018 BB003 is the four-digit calendar year for first moving to the county/city/district where the current address BB001_W3 is located (questionnaire range 1900–2018). BB001–BB005 are asked on the new-interview route (XRType=2); returners skip this block. Keep distinct from BB005's village/community year and from 2011–2015 permanent-address wording.",
}


def make_row(template: dict, wave: str) -> dict:
    row = dict(template)
    row["Variable.Name"] = "bb003"
    row["Variable.Description"] = DESCRIPTIONS[wave]
    row["Begin.Year"] = row["EndYear"] = row["Source.Wave"] = wave
    row["Source.Archive"] = ARCHIVES[wave]
    row["Value.Labels"] = ""
    row["Value.Label.Source"] = "; ".join(DOCS[wave])
    row["Value.Label.Review"] = "official questionnaire and Codebook reviewed; continuous calendar-year field; descriptive frequencies and statistics omitted; special-value storage pending release-specific validation"
    row["Candidate.Status"] = "C metadata candidate; source question reviewed; not an approved adjustment variable"
    row["Review.Flag"] = "C residential-history metadata; routed calendar year; not a direct environmental dose or selected adjustment covariate"
    row["Harmonization.Status"] = NOTES[wave]
    # Some source/series JSON files carry lowercase aliases in addition to the
    # canonical CSV schema. Keep those aliases synchronized only when present.
    for key in ("waves", "wave_count", "value_labels", "value_label_source", "value_label_review", "harmonization_status"):
        if key in row:
            if key == "waves": row[key] = wave
            elif key == "wave_count": row[key] = "1"
            elif key == "value_labels": row[key] = ""
            elif key == "value_label_source": row[key] = row["Value.Label.Source"]
            elif key == "value_label_review": row[key] = row["Value.Label.Review"]
            elif key == "harmonization_status": row[key] = NOTES[wave]
    return row


def verify_sources() -> None:
    for wave, (qpath, cpath) in DOCS.items():
        q = (ROOT / qpath).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
        c = (ROOT / cpath).read_text(encoding="utf-8", errors="replace").replace("\x00", "").casefold()
        if "bb003" not in q.casefold() or "bb003" not in c:
            raise ValueError(f"Official BB003 questionnaire/Codebook evidence missing for {wave}")
        if wave == "2015" and ("bb001_w3" not in q.casefold() or "xrtype = newiw" not in q.casefold()):
            raise ValueError("2015 BB001_W3/XRType route not confirmed")
        if wave == "2018" and "xrtype = 2" not in q.casefold():
            raise ValueError("2018 XRType=2 new-interview route not confirmed")


def main() -> None:
    verify_sources()
    field_csv = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
    fields = pd.read_csv(field_csv, dtype=str, encoding="utf-8-sig").fillna("")
    aliases = ("variable", "waves", "wave_count", "value_labels", "value_label_source", "value_label_review", "harmonization_status")
    fields = fields.drop(columns=[c for c in aliases if c in fields.columns])
    for wave in WAVES:
        mask = fields["Variable.Name"].str.casefold().eq("bb003") & fields["Source.Wave"].eq(wave) & fields["epcf"].str.casefold().eq("c")
        if not mask.any():
            template_mask = fields["Variable.Name"].str.casefold().eq("bb005") & fields["Source.Wave"].eq(wave) & fields["epcf"].str.casefold().eq("c")
            if not template_mask.any():
                raise ValueError(f"No same-wave C metadata template for BB003 {wave}")
            row = {k: v for k, v in make_row(fields.loc[template_mask].iloc[0].to_dict(), wave).items() if k in fields.columns}
            fields = pd.concat([fields, pd.DataFrame([row])], ignore_index=True)
            mask = fields["Variable.Name"].str.casefold().eq("bb003") & fields["Source.Wave"].eq(wave) & fields["epcf"].str.casefold().eq("c")
        if int(mask.sum()) != 1:
            raise ValueError(f"Expected one BB003 C row for {wave}, found {int(mask.sum())}")
        idx = fields.index[mask][0]
        row = make_row(fields.loc[idx].to_dict(), wave)
        for key in fields.columns:
            fields.at[idx, key] = row.get(key, fields.at[idx, key])
    fields.to_csv(field_csv, index=False, encoding="utf-8-sig")

    for path in (ROOT / "audit/charls_atlas_candidate_fields_v0.json", ROOT / "site-prototype/dist/catalog.json", ROOT / "site-prototype/dist/catalog_c.json"):
        rows = json.loads(path.read_text(encoding="utf-8"))
        for wave in WAVES:
            selected = [i for i, r in enumerate(rows) if str(r.get("Variable.Name", "")).casefold() == "bb003" and str(r.get("Source.Wave", "")) == wave and str(r.get("epcf", "")).casefold() == "c"]
            if not selected:
                template = next((r for r in rows if str(r.get("Variable.Name", "")).casefold() == "bb005" and str(r.get("Source.Wave", "")) == wave and str(r.get("epcf", "")).casefold() == "c"), None)
                if template is None:
                    raise ValueError(f"No C JSON template for {path.name} BB003 {wave}")
                rows.append(make_row(template, wave))
                selected = [len(rows) - 1]
            if len(selected) != 1:
                raise ValueError(f"{path.name}: duplicate BB003 C rows for {wave}")
            rows[selected[0]] = make_row(rows[selected[0]], wave)
        path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    series_csv = ROOT / "audit/charls_atlas_candidate_series_v0.csv"
    series = pd.read_csv(series_csv, dtype=str, encoding="utf-8-sig").fillna("")
    mask = series["Variable.Name"].str.casefold().eq("bb003") & series["epcf"].str.casefold().eq("c")
    if int(mask.sum()) != 1:
        raise ValueError(f"Expected one BB003 C series row, found {int(mask.sum())}")
    series.loc[mask, "waves"] = ",".join(WAVES)
    series.loc[mask, "wave_count"] = str(len(WAVES))
    series.loc[mask, "value_labels"] = ""
    series.loc[mask, "value_label_source"] = "; ".join(sorted({p for pair in DOCS.values() for p in pair}))
    series.loc[mask, "value_label_review"] = "official wave questionnaires and Codebooks reviewed for 2011–2018; continuous calendar-year field; descriptive statistics omitted; release-specific routing and special values must be validated"
    series.loc[mask, "harmonization_status"] = "Four wave-specific BB003 county/city/district move-in year records. References permanent address in 2011–2015 and current address BB001_W3 in 2018; routing differs by wave, especially the 2015 BB001_W3/XRType rule and 2018 new-interview restriction. Keep distinct from BB005 village/community year; do not derive exposure duration or combine without release-specific route and estimand validation."
    series.to_csv(series_csv, index=False, encoding="utf-8-sig")
    (ROOT / "audit/charls_atlas_candidate_series_v0.json").write_text(json.dumps(series.to_dict(orient="records"), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    audit = ROOT / "audit/residential_history_bb003_source_review_2011_2018_2026-10-24.md"
    lines = ["# BB003 residential-history county/city/district year review, 2011–2018", "", "Official wave questionnaires and Codebooks were reviewed. No respondent records, Codebook descriptive statistics, or frequencies were used.", "", "| Wave | Reference and questionnaire range | Routing caveat |", "|---|---|---|"]
    lines.extend([
        "| 2011 | First lived in permanent address's county/city/district; 1900–2013 | New-interview/reinterview and preceding BB001 procedures apply; use the release route to identify eligibility. |",
        "| 2013 | First lived in permanent address's county/city/district; 1900–2013 | New-interview/reinterview and preceding BB001 procedures apply; use the release route to identify eligibility. |",
        "| 2015 | First lived in permanent address's county/city/district; 1900–2015 | Ask BB003 if BB001_W3 is not 1 or XRType=NEWIW; otherwise skip to BB005_W3_1. |",
        "| 2018 | First moved to county/city/district of current address BB001_W3; 1900–2018 | BB001–BB005 block is asked for new interviews (XRType=2); returners skip it. |",
        "", "BB003 is a continuous calendar-year residential-history item. It records movement into a county/city/district and is distinct from BB005's village/community year. The 2018 current-address reference differs from the 2011–2015 permanent-address wording. Preserve the route, validate special codes against the authorized release, and do not interpret the year as duration of any environmental exposure without address-time linkage and a defined estimand. No Codebook means, ranges, or observation counts were copied.", "",
        "Sources: " + "; ".join(f"`{p}`" for pair in DOCS.values() for p in pair), ""
    ])
    audit.write_text("\n".join(lines), encoding="utf-8")
    print("Reviewed and catalogued BB003 for four waves; continuous-year metadata only, with wave-specific route notes.")


if __name__ == "__main__":
    main()
