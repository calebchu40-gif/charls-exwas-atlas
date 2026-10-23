"""Review alternate-branch residential mobility and duration fields BB007–BB010."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WAVES = ("2011", "2013")
DOCS = {
    "2011": ("sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt", "sources_official/CHARLS_2011_Codebook_extracted.txt"),
    "2013": ("sources_official/CHARLS_2013_Questionnaire_extracted.txt", "sources_official/CHARLS_2013_Codebook_extracted.txt"),
}
ARCHIVES = {"2011": "household_and_community_questionnaire_data.rar", "2013": "CHARLS2013_Dataset.zip"}
ITEMS = {
    ("2011", "bb007"): ("Did You Ever Live Outside Your Present County/City for More Than 6 Months", "1=Yes; 2=No", "Since first coming to the permanent county/city/district, ever lived outside it for more than six months. BB001=1 or 2 routes to BB009 instead of BB007. A No response skips to BC001; Yes routes to BB008. The 2011 Codebook says ‘present county/city’ while the questionnaire says ‘permanent county/city/district’; retain this wording difference and do not merge with BB009."),
    ("2013", "bb007"): ("Ever Since You First Come to Your Permanent City/County/District, Have You Ever Lived Outside for More Than 6 Months", "1=Yes; 2=No", "Since first coming to the permanent county/city/district, ever lived outside it for more than six months. BB001=1 or 2 routes to BB009 instead of BB007. A No response skips to BC001; Yes routes to BB008. This is a distinct branch from BB009/BB010."),
    ("2011", "bb008_1"): ("Years lived outside permanent county/city/district (BB008)", "", "BB008_1 records cumulative years lived outside the permanent county/city/district after a Yes response to BB007; BB001=1 or 2 routes to BB009 instead. Preserve the paired BB008_2 month component and do not treat routed absence as zero."),
    ("2013", "bb008_1"): ("Years lived outside permanent county/city/district (BB008)", "", "BB008_1 records cumulative years lived outside the permanent county/city/district after a Yes response to BB007; BB001=1 or 2 routes to BB009 instead. Preserve the paired BB008_2 month component and do not treat routed absence as zero."),
    ("2011", "bb008_2"): ("Months lived outside permanent county/city/district (BB008)", "", "BB008_2 records the month component of cumulative time outside the permanent county/city/district after a Yes response to BB007; BB001=1 or 2 routes to BB009 instead. Preserve the paired BB008_1 year component and do not treat routed absence as zero."),
    ("2013", "bb008_2"): ("Months lived outside permanent county/city/district (BB008)", "", "BB008_2 records the month component of cumulative time outside the permanent county/city/district after a Yes response to BB007; BB001=1 or 2 routes to BB009 instead. Preserve the paired BB008_1 year component and do not treat routed absence as zero."),
    ("2011", "bb009"): ("Did You Ever Lived Outside this County/City for More than 6 Months", "1=Yes; 2=No", "Alternate residential-history branch: the questionnaire routes to BB009 when BB001=1 or 2. A No response skips to BC001; Yes routes to BB010. Keep distinct from BB007/BB008, which follow the other BB001 branch; the 2011 Codebook heading is less specific than the questionnaire reference."),
    ("2013", "bb009"): ("Did You Ever Live Outside Your Permanent City/County/District More Than 6 Months", "1=Yes; 2=No", "Alternate residential-history branch: the questionnaire routes to BB009 when BB001=1 or 2. A No response skips to BC001; Yes routes to BB010. Keep distinct from BB007/BB008, which follow the other BB001 branch."),
    ("2011", "bb010_1"): ("Years lived outside permanent county/city/district (BB010)", "", "BB010_1 records cumulative years outside the permanent county/city/district after a Yes response to BB009; BB009 is the BB001=1 or 2 branch. The 2011 questionnaire includes a year ceiling based on 2013-BB003. Preserve BB010_2 months separately; do not treat routed absence as zero."),
    ("2013", "bb010_1"): ("Years lived outside permanent county/city/district (BB010)", "", "BB010_1 records cumulative years outside the permanent county/city/district after a Yes response to BB009; BB009 is the BB001=1 or 2 branch. Preserve BB010_2 months separately and do not treat routed absence as zero."),
    ("2011", "bb010_2"): ("Months lived outside permanent county/city/district (BB010)", "", "BB010_2 records the month component of cumulative time outside the permanent county/city/district after a Yes response to BB009; BB009 is the BB001=1 or 2 branch. Preserve BB010_1 years separately and do not treat routed absence as zero."),
    ("2013", "bb010_2"): ("Months lived outside permanent county/city/district (BB010)", "", "BB010_2 records the month component of cumulative time outside the permanent county/city/district after a Yes response to BB009; BB009 is the BB001=1 or 2 branch. Preserve BB010_1 years separately and do not treat routed absence as zero."),
}


def update(row: dict, wave: str, var: str) -> dict:
    description, labels, note = ITEMS[(wave, var)]
    row["Variable.Name"] = var
    row["Variable.Description"] = description
    row["Begin.Year"] = row["EndYear"] = row["Source.Wave"] = wave
    row["Source.Archive"] = ARCHIVES[wave]
    row["Value.Labels"] = labels
    row["Value.Label.Source"] = "; ".join(DOCS[wave])
    row["Value.Label.Review"] = "official questionnaire and Codebook reviewed; response categories shown only for the yes/no gate items; Codebook frequencies and descriptive statistics omitted; numeric duration components require release-specific special-value validation"
    row["Candidate.Status"] = "C metadata candidate; questionnaire route and field meaning reviewed; not an approved adjustment variable"
    row["Review.Flag"] = "C residential-history metadata; route-specific migration history; not a direct environmental dose or selected adjustment covariate"
    row["Harmonization.Status"] = note
    for k, v in (("waves", wave), ("wave_count", "1"), ("value_labels", labels), ("value_label_source", row["Value.Label.Source"]), ("value_label_review", row["Value.Label.Review"]), ("harmonization_status", note)):
        if k in row: row[k] = v
    return row


def verify_sources() -> None:
    for wave, (qpath, cpath) in DOCS.items():
        q = (ROOT / qpath).read_text(encoding="utf-8", errors="replace").replace("\x00", "").casefold()
        c = (ROOT / cpath).read_text(encoding="utf-8", errors="replace").replace("\x00", "").casefold()
        for base in ("bb007", "bb008", "bb009", "bb010"):
            if base not in q:
                raise ValueError(f"Questionnaire missing {base} in {wave}")
            # Codebook extraction sometimes renders underscore separators as spaces.
            normalized = re.sub(r"[ _]", "", c)
            if base not in normalized:
                raise ValueError(f"Codebook missing {base} in {wave}")
        if not re.search(r"bb001\s*=\s*1\s+or\s*bb001\s*=\s*2\s+go\s*to\s*bb009", q):
            raise ValueError(f"Alternate BB007/BB009 branch not confirmed in {wave}")
        if "1. yes" not in q or "2. no" not in q:
            raise ValueError(f"Expected yes/no gate labels missing in {wave}")


def main() -> None:
    verify_sources()
    field_csv = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
    fields = pd.read_csv(field_csv, dtype=str, encoding="utf-8-sig").fillna("")
    alias_cols = ("variable", "waves", "wave_count", "value_labels", "value_label_source", "value_label_review", "harmonization_status")
    fields = fields.drop(columns=[c for c in alias_cols if c in fields.columns])
    for (wave, var), (description, _, _) in ITEMS.items():
        mask = fields["Variable.Name"].str.casefold().eq(var) & fields["Source.Wave"].eq(wave) & fields["epcf"].str.casefold().eq("c")
        if not mask.any():
            template_mask = fields["Variable.Name"].str.casefold().eq("bb007") & fields["Source.Wave"].eq(wave) & fields["epcf"].str.casefold().eq("c")
            if not template_mask.any():
                raise ValueError(f"No same-wave C template for {var} {wave}")
            new = update(fields.loc[template_mask].iloc[0].to_dict(), wave, var)
            fields = pd.concat([fields, pd.DataFrame([{k: v for k, v in new.items() if k in fields.columns}])], ignore_index=True)
            mask = fields["Variable.Name"].str.casefold().eq(var) & fields["Source.Wave"].eq(wave) & fields["epcf"].str.casefold().eq("c")
        if int(mask.sum()) != 1:
            raise ValueError(f"Expected one C row for {var} {wave}, found {int(mask.sum())}")
        idx = fields.index[mask][0]
        new = update(fields.loc[idx].to_dict(), wave, var)
        for col in fields.columns: fields.at[idx, col] = new.get(col, fields.at[idx, col])
    fields.to_csv(field_csv, index=False, encoding="utf-8-sig")

    for path in (ROOT / "audit/charls_atlas_candidate_fields_v0.json", ROOT / "site-prototype/dist/catalog.json", ROOT / "site-prototype/dist/catalog_c.json"):
        rows = json.loads(path.read_text(encoding="utf-8"))
        for (wave, var) in ITEMS:
            idxs = [i for i, r in enumerate(rows) if str(r.get("Variable.Name", "")).casefold() == var and str(r.get("Source.Wave", "")) == wave and str(r.get("epcf", "")).casefold() == "c"]
            if not idxs:
                template = next((r for r in rows if str(r.get("Variable.Name", "")).casefold() == "bb007" and str(r.get("Source.Wave", "")) == wave and str(r.get("epcf", "")).casefold() == "c"), None)
                if template is None: raise ValueError(f"No C template in {path.name} for {var} {wave}")
                rows.append(update(dict(template), wave, var)); idxs = [len(rows)-1]
            if len(idxs) != 1: raise ValueError(f"Duplicate C rows in {path.name} for {var} {wave}")
            rows[idxs[0]] = update(rows[idxs[0]], wave, var)
        path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    series_csv = ROOT / "audit/charls_atlas_candidate_series_v0.csv"
    series = pd.read_csv(series_csv, dtype=str, encoding="utf-8-sig").fillna("")
    for var in sorted({var for _, var in ITEMS}):
        mask = series["Variable.Name"].str.casefold().eq(var) & series["epcf"].str.casefold().eq("c")
        if int(mask.sum()) != 1: raise ValueError(f"Expected one C series row for {var}")
        waves = sorted(w for w in WAVES if (w, var) in ITEMS)
        series.loc[mask, "waves"] = ",".join(waves)
        series.loc[mask, "wave_count"] = str(len(waves))
        series.loc[mask, "value_labels"] = ITEMS[(waves[0], var)][1] if all(ITEMS[(w, var)][1] == ITEMS[(waves[0], var)][1] for w in waves) else ""
        series.loc[mask, "value_label_source"] = "; ".join(sorted({p for w in waves for p in DOCS[w]}))
        series.loc[mask, "value_label_review"] = "wave-specific questionnaires and Codebooks reviewed; frequencies omitted; numeric components have no response categories assigned"
        series.loc[mask, "harmonization_status"] = "Route-specific residential mobility history. BB007/BB008 and BB009/BB010 are alternate questionnaire branches selected by BB001; do not combine as repeated measurements. Preserve yes/no gate routing and year/month components. No address location, exposure duration, or covariate eligibility is inferred."
    series.to_csv(series_csv, index=False, encoding="utf-8-sig")
    (ROOT / "audit/charls_atlas_candidate_series_v0.json").write_text(json.dumps(series.to_dict(orient="records"), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    audit = ROOT / "audit/residential_history_mobility_duration_review_2011_2013_2026-10-24.md"
    lines = ["# Residential mobility branch and duration review, 2011 and 2013", "", "Official questionnaires and Codebooks were reviewed. No respondent values or Codebook frequencies/statistics were copied.", "", "| Wave | BB001 route | Gate and duration fields |", "|---|---|---|"]
    lines.extend([
        "| 2011 | BB001=1 or 2 routes to BB009/BB010; other eligible path asks BB007/BB008 | BB007 Yes/No gates BB008_1 years and BB008_2 months; BB009 Yes/No gates BB010_1 years and BB010_2 months. The 2011 BB007 Codebook says ‘present county/city’ while its question says ‘permanent county/city/district’; BB009 wording is also less specific in the Codebook. |",
        "| 2013 | BB001=1 or 2 routes to BB009/BB010; other eligible path asks BB007/BB008 | BB007 and BB009 have separate Yes/No gates for their alternate paths; each gates its own years/months pair. |",
        "", "BB007/BB008 and BB009/BB010 are alternate branches, not two repeated exposure measures. BB008 and BB010 record cumulative time outside the permanent county/city/district in years and months; conditional blanks must not be recoded as zero. The 2011 questionnaire includes a consistency check tying BB010 years to 2013-BB003. Because the yes/no gate wording varies and 2011 Codebook labels are less specific, preserve item and wave identity; do not pool, derive environmental exposure duration, or assign adjustment status without checking released routing and a prespecified estimand.", "",
        "Sources: " + "; ".join(f"`{p}`" for pair in DOCS.values() for p in pair), ""
    ])
    audit.write_text("\n".join(lines), encoding="utf-8")
    print(f"Reviewed {len(ITEMS)} wave-field mobility records; branch-specific durations retained without response values.")


if __name__ == "__main__":
    main()
