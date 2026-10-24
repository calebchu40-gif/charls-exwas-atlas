"""Review source/derivation roles for Wave 1-4 respondent-gender metadata."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CATALOG = ROOT / "site-prototype/dist/catalog.json"
OUTPUT = AUDIT / "respondent_gender_source_derivation_crosswalk_2011_2018_v1.csv"

# Module is part of the identity: 2018 xrgender occurs in two released modules.
TARGETS = {
    ("2011", "rgender", "demographic_background"): "respondent gender field",
    ("2013", "ba000_w2_3", "Demographic_Background"): "interviewer-recorded gender input",
    ("2013", "xrgender", "Health_Status_and_Functioning"): "released respondent gender candidate",
    ("2015", "ba000_w2_3", "Demographic_Background"): "interviewer-recorded gender input",
    ("2015", "xrgender", "Health_Status_and_Functioning"): "released respondent gender candidate",
    ("2018", "ba000_w2_3", "Demographic_Background"): "interviewer-recorded gender input",
    ("2018", "xrgender", "Demographic_Background"): "released respondent gender candidate",
    ("2018", "xrgender", "Health_Status_and_Functioning"): "released respondent gender candidate",
    ("2018", "zfrgender", "Demographic_Background"): "prior-wave gender route flag",
}
WAVES = ("2011", "2013", "2015", "2018")
BASE_STATUS = (
    "C metadata; source reviewed as gender input/derived candidate only; adjustment use remains estimand-specific and unapproved"
)
SOURCES = {
    "2011": ("CHARLS_2011_Baseline_Questionnaire_official_extracted.txt", "CHARLS_2011_Codebook_extracted.txt"),
    "2013": ("CHARLS_2013_Questionnaire_extracted.txt", "CHARLS_2013_Codebook_extracted.txt"),
    "2015": ("CHARLS_2015_Questionnaire_extracted.txt", "CHARLS_2015_Codebook_extracted.txt"),
    "2018": ("CHARLS_2018_Questionnaire_extracted.txt", "CHARLS_2018_Codebook_extracted.txt"),
}


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def check_sources() -> dict[str, tuple[str, ...]]:
    texts: dict[str, tuple[str, ...]] = {}
    for wave, names in SOURCES.items():
        values = tuple((ROOT / "sources_official" / name).read_text(encoding="utf-8", errors="replace") for name in names)
        texts[wave] = values
        for name in names:
            if not (ROOT / "sources_official" / name).is_file():
                raise SystemExit(f"Missing official source: {name}")

    for wave in ("2013", "2015", "2018"):
        q, cb = (compact(value) for value in texts[wave])
        if "ba000w23" not in q or "1male" not in q or "2female" not in q:
            raise SystemExit(f"{wave} questionnaire does not support BA000_W2_3 gender categories")
        if "ba000w23" not in cb or "1male" not in cb or "2female" not in cb:
            raise SystemExit(f"{wave} Codebook does not support BA000_W2_3 gender categories")
        if "xrgender" not in cb or "1male" not in cb or "2female" not in cb:
            raise SystemExit(f"{wave} Codebook does not support XRGender category labels")
    baseline_q, baseline = (compact(value) for value in texts["2011"])
    if "ba000w23" not in baseline_q or "1male" not in baseline_q or "2female" not in baseline_q:
        raise SystemExit("2011 baseline questionnaire does not support interviewer gender input categories")
    if "rgender" not in baseline or "1male" not in baseline or "2female" not in baseline:
        raise SystemExit("2011 Codebook does not support RGender category labels")

    q18 = compact(texts["2018"][0])
    for cue in ("zfrgender", "xrtype", "xrgender", "ba000w23"):
        if cue not in q18:
            raise SystemExit(f"2018 questionnaire is missing the {cue} gender routing cue")
    for route in (
        "ifthisisareinterviewxrtype1andzfrgender1askba000w23thenrenewxrgenderba000w23",
        "ifthisisanewinterviewxrtype2askba000w23thenrenewxrgenderba000w23",
        "ifnotxrgenderzrgender",
    ):
        if route not in q18:
            raise SystemExit(f"2018 XRGender source derivation route not verified: {route}")
    # Do not infer zfrgender categories from the Codebook summary. The
    # questionnaire identifies it as a route input to refresh gender.
    if "zfrgender" not in compact(texts["2018"][1]):
        raise SystemExit("2018 Codebook does not list ZFRGender")
    return texts


def source_records() -> list[dict[str, str]]:
    check_sources()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    selected: dict[tuple[str, str, str], dict[str, object]] = {}
    for row in catalog:
        key = (
            str(row.get("Source.Wave", "")),
            str(row.get("Variable.Name", "")).lower(),
            str(row.get("Data.File.Name", "")),
        )
        if key in TARGETS and str(row.get("epcf", "")).lower() == "c":
            if key in selected:
                raise SystemExit(f"duplicate gender source record {key}")
            selected[key] = row
    if set(selected) != set(TARGETS):
        raise SystemExit(f"Gender target keys differ: missing={set(TARGETS)-set(selected)}, extra={set(selected)-set(TARGETS)}")

    result = []
    for key in sorted(TARGETS):
        wave, code, module = key
        item = selected[key]
        names = SOURCES[wave]
        sources = "; ".join(f"sources_official/{name}" for name in names)
        kind = TARGETS[key]
        if code == "zfrgender":
            subcategory = "prior-wave gender route flag"
            labels = ""
            review = "2018 questionnaire confirms a prior-wave routing input for gender refresh; Codebook summary is not treated as current gender categories; no values inferred"
            meaning = (
                "ZFRGender is a prior-wave route/reference input in the 2018 gender procedure, not an independent current-wave gender response. "
                "The questionnaire conditionally refreshes XRGender using interview type and prior-wave references. Preserve module and route; do not use this flag as a current gender covariate."
            )
        else:
            subcategory = "respondent gender source and derivation metadata"
            labels = "1=Male; 2=Female"
            if code == "ba000_w2_3":
                review = "official questionnaire and Codebook reviewed; interviewer-recorded/preloaded gender input; no frequencies copied"
                meaning = (
                    "Interviewer-recorded gender input, not automatically the released respondent-gender derivation. "
                    "2013/2015 questionnaires describe a preloaded value; 2018 routes updates by interview type and prior-wave flags. "
                    "Do not substitute this input for XRGender without wave-specific source and release QA."
                )
            elif wave == "2011":
                review = "2011 Codebook response labels reviewed; field retained as the baseline gender source"
                meaning = "Baseline released respondent gender field; use source module and authorized-release coding, and do not assume its construction is identical to later-wave XRGender."
            elif wave == "2018":
                review = "2018 questionnaire derivation and Codebook response labels reviewed; module-qualified duplicate retained"
                meaning = (
                    "Released XRGender candidate. The 2018 questionnaire renews gender from BA000_W2_3 under specified interview-type/prior-wave conditions and otherwise uses ZRGender. "
                    "This code is listed in both demographic and health modules; keep module identity and do not count the duplicate as a second measure."
                )
            else:
                review = "official Codebook response labels reviewed; derivation and cross-wave equivalence remain unresolved"
                meaning = (
                    "Released respondent-gender candidate with official 1/2 labels. The original wave Codebook does not establish a fully equivalent construction across waves; "
                    "retain module identity and verify authorized-release generation and cross-module conflicts before model use."
                )
        result.append({
            "wave": wave,
            "code": code,
            "module": module,
            "source_role": kind,
            "official_sources": sources,
            "value_labels": labels,
            "review_status": review,
            "catalog_note": meaning,
        })
    return result


def update_item(row: dict[str, object], item: dict[str, str]) -> None:
    row["category"] = "automated covariate search hit"
    row["subcategory"] = item["subcategory"] if "subcategory" in item else (
        "prior-wave gender route flag" if item["code"] == "zfrgender" else "respondent gender source and derivation metadata"
    )
    row["Candidate.Status"] = BASE_STATUS
    row["Harmonization.Status"] = item["catalog_note"]
    row["Review.Flag"] = item["catalog_note"]
    row["Value.Labels"] = item["value_labels"]
    row["Value.Label.Source"] = item["official_sources"]
    row["Value.Label.Review"] = item["review_status"]
    for alias, source in (("value_labels", "value_labels"), ("value_label_source", "official_sources"), ("value_label_review", "review_status"), ("harmonization_status", "catalog_note")):
        row[alias] = item[source]


def propagate(records: list[dict[str, str]]) -> None:
    targets = {(r["wave"], r["code"], r["module"]): r for r in records}
    for rel in (
        "audit/charls_atlas_candidate_fields_v0.csv",
        "audit/charls_atlas_candidate_fields_v0.json",
        "site-prototype/dist/catalog.json",
    ):
        path = ROOT / rel
        if not path.exists():
            continue
        updated = 0
        if path.suffix == ".csv":
            df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            for (wave, code, module), item in targets.items():
                mask = (
                    df["Source.Wave"].eq(wave)
                    & df["Variable.Name"].str.lower().eq(code)
                    & df["Data.File.Name"].eq(module)
                    & df["epcf"].str.lower().eq("c")
                )
                if mask.any():
                    for field, source in (
                        ("category", None), ("subcategory", None), ("Candidate.Status", None),
                        ("Harmonization.Status", "catalog_note"), ("Review.Flag", "catalog_note"),
                        ("Value.Labels", "value_labels"), ("Value.Label.Source", "official_sources"),
                        ("Value.Label.Review", "review_status"),
                    ):
                        value = item[source] if source else (
                            "prior-wave gender route flag" if code == "zfrgender" else "respondent gender source and derivation metadata"
                        ) if field == "subcategory" else "automated covariate search hit" if field == "category" else BASE_STATUS
                        df.loc[mask, field] = value
                    updated += int(mask.sum())
            if updated != len(targets):
                raise SystemExit(f"Expected {len(targets)} module-qualified C rows in {rel}; updated {updated}")
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")))
                if key in targets and str(row.get("epcf", "")).lower() == "c":
                    update_item(row, targets[key])
                    updated += 1
            if updated != len(targets):
                raise SystemExit(f"Expected {len(targets)} module-qualified C rows in {rel}; updated {updated}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(f"Reviewed {len(records)} module-qualified Wave 1-4 gender source/route rows; labels are wave-specific; no frequencies copied.")


if __name__ == "__main__":
    propagate(source_records())
