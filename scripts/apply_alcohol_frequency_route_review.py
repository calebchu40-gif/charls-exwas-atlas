"""Propagate questionnaire-backed alcohol frequency and routing caveats."""
from pathlib import Path
import json
import csv
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "audit/behavior_exposure_variable_mapping_v1.csv"
TOPIC = ROOT / "site-prototype/dist/behavior_exposures_v1.json"

WAVES = {
    "2011": ("CHARLS_2011_Baseline_Questionnaire_official_extracted.txt", 3886),
    "2013": ("CHARLS_2013_Questionnaire_extracted.txt", 3233),
    "2015": ("CHARLS_2015_Questionnaire_extracted.txt", 2637),
    "2018": ("CHARLS_2018_Questionnaire_extracted.txt", 3102),
}
FREQ = {
    ("2011", "da072"): 3931, ("2011", "da074"): 3950, ("2011", "da076"): 3965,
    ("2013", "da072"): 3272, ("2013", "da074"): 3286, ("2013", "da076"): 3301,
    ("2015", "da072"): 2674, ("2015", "da074"): 2688, ("2015", "da076"): 2703,
    ("2018", "da072"): 3148, ("2018", "da074"): 3163, ("2018", "da076"): 3179,
}


def source(name: str) -> str:
    return (ROOT / "sources_official" / name).read_text(encoding="utf-8", errors="replace")


def require(name: str, terms: tuple[str, ...]) -> str:
    text = source(name)
    if not all(term.casefold() in text.casefold() for term in terms):
        raise ValueError(f"Official source assertion failed: {name}")
    return text


def set_rows(data: pd.DataFrame, concept: str, wave: str, code: str, **values: str) -> None:
    mask = data.concept_id.eq(concept) & data.wave.eq(wave) & data.code.str.lower().eq(code.lower())
    if int(mask.sum()) != 1:
        raise ValueError(f"Expected one row for {concept}/{wave}/{code}, got {int(mask.sum())}")
    for key, value in values.items():
        data.loc[mask, key] = value


def sync_c_metadata_statuses() -> int:
    """Propagate source-reviewed alcohol meaning to exact-wave C metadata rows."""
    rules = {
        (wave, "da067"): ("past-year alcohol threshold and route", "C metadata; questionnaire threshold and route source-reviewed; structural skips are not No/zero; not a dose or adjustment recommendation")
        for wave in ("2011", "2013", "2015", "2018")
    }
    rules[("2020", "da051")] = ("past-year alcohol threshold and route", "C metadata; Wave 5 threshold and flowchart route source-reviewed; DA052 is conditional; not a dose or adjustment recommendation")
    rules.update({
        (wave, "da069"): ("retrospective alcohol history and route", "C metadata; retrospective drinking-history categories and re-interview route source-reviewed; skipped/carry-forward is not No; not an adjustment recommendation")
        for wave in ("2011", "2013", "2015", "2018")
    })
    rules[("2018", "zda069")] = ("prior-wave alcohol history carry-forward metadata", "C metadata; prior-wave alcohol-history route/carry-forward field source-reviewed; not an independent exposure or adjustment recommendation")
    for wave in ("2011", "2013", "2015", "2018"):
        for code in ("da068s1", "da068s2", "da068s3", "da068_s1", "da068_s2", "da068_s3"):
            rules[(wave, code)] = ("alcohol beverage-type selector", "C metadata; beverage-type selection source-reviewed; selected beverage does not encode amount or population-wide eligibility")

    files = [
        ROOT / "audit/charls_atlas_candidate_fields_v0.csv",
        ROOT / "audit/charls_atlas_candidate_fields_v0.json",
        ROOT / "site-prototype/dist/catalog.json",
        ROOT / "site-prototype/dist/catalog_c.json",
    ]
    updated = 0
    for path in files:
        if not path.exists():
            continue
        if path.suffix == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
                fieldnames = list(rows[0]) if rows else []
            wave_key, code_key, role_key = "Source.Wave", "Variable.Name", "epcf"
            for row in rows:
                key = (str(row.get(wave_key, "")), str(row.get(code_key, "")).lower())
                if key in rules and str(row.get(role_key, "")).lower() == "c":
                    subcategory, status = rules[key]
                    row.update({"category": "source-reviewed context metadata", "subcategory": subcategory,
                                "Candidate.Status": status,
                                "Harmonization.Status": "source definition and route reviewed; not a default covariate; preserve wave-specific eligibility and structural missingness"})
                    updated += 1
            with path.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        else:
            records = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(records, list):
                continue
            for row in records:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower())
                if key in rules and str(row.get("epcf", "")).lower() == "c":
                    subcategory, status = rules[key]
                    row.update({"category": "source-reviewed context metadata", "subcategory": subcategory,
                                "Candidate.Status": status,
                                "Harmonization.Status": "source definition and route reviewed; not a default covariate; preserve wave-specific eligibility and structural missingness"})
                    updated += 1
            path.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return updated


def main() -> None:
    for wave, (name, _) in WAVES.items():
        route_text = "Skip to procedure before DA069" if wave == "2018" else "Skip to DA069"
        require(name, ("DA067", "Drink more than once a month", "Drink but less than once a month",
                       "None of these", route_text))
    require("CHARLS_2020_Questionnaire_Chinese_extracted.txt",
            ("DA051", "DA052", "喝酒，每月超过一次", "平均一个月喝几次酒"))
    require("CHARLS_2020_Flowchart_Chinese_extracted.txt", ("DA051.饮酒", "DA052.一个月喝"))
    for wave, (name, _) in WAVES.items():
        require(name, ("DA068", "Liquor", "Beer", "Wine or rice wine"))
    for (wave, code), _ in FREQ.items():
        require(WAVES[wave][0], (code.upper(), "per month"))

    data = pd.read_csv(MAP, dtype=str, encoding="utf-8-sig").fillna("")
    n_recent = 0
    for wave, (name, line) in WAVES.items():
        set_rows(data, "alcohol_recent", wave, "da067",
                 value_label_status="official questionnaire route and response categories reviewed; threshold categories retained; frequencies omitted",
                 questionnaire_source=f"sources_official/{name}:L{line}",
                 value_semantics=("Past-year frequency thresholds (>once/month, <once/month, or none), not an exact frequency or alcohol dose. "
                                  "Questionnaire routes DA067=2/3 to DA069, bypassing current-year beverage-detail items. "
                                  "A skipped or structural absence is not No/zero; preserve the eligible denominator and verify authorized-release storage."),
                 mapping_status="official questionnaire route and response categories reviewed; threshold measure retained; conditional denominator must be respected",
                 note="Past-year drinking threshold, not a numeric monthly dose. DA067=2/3 bypasses current-year beverage details and continues to past-history items; structural skips are not No.")
        n_recent += 1
    set_rows(data, "alcohol_recent", "2020", "da051",
             value_label_status="official Chinese questionnaire labels and flowchart route reviewed; threshold categories retained; frequencies omitted",
             questionnaire_source="sources_official/CHARLS_2020_Questionnaire_Chinese_extracted.txt:L1395; sources_official/CHARLS_2020_Flowchart_Chinese.pdf:PDF p.30 (printed p.24)",
             value_semantics="Past-year frequency thresholds (>once/month, <once/month, or none), not an exact frequency or alcohol dose. The Chinese flowchart routes DA051=1 to DA052 and DA051=2/3 to the end of the alcohol sequence. Structural absence is not No/zero; preserve the eligible denominator.",
             mapping_status="official Chinese questionnaire and flowchart reviewed; threshold measure and conditional route retained",
             note="2020 DA052 is reached only after DA051=1; do not infer zero from structural skip.")

    # DA072's Wave 1 instruction conditions on DA067=1 but does not explicitly
    # state a DA068 liquor-selection gate. Keep that denominator unresolved.
    for (wave, code), line in FREQ.items():
        beverage = {"da072": "liquor", "da074": "beer", "da076": "wine or rice wine"}[code]
        if wave == "2011" and code == "da072":
            route = ("Wave 1 text says ask DA072 when DA067=1 but does not explicitly require the DA068 liquor selection; "
                     "retain the liquor-specific item meaning and verify its exact released-file route before analysis.")
            status = "official questionnaire item and unit reviewed; DA067=1 route documented; beverage-selection denominator unresolved pending authorized-release QA"
        else:
            route = "The questionnaire routes this frequency item by the selected DA068 beverage type; preserve this beverage-specific denominator."
            status = "official questionnaire and Codebook response categories reviewed; selected-beverage route retained; frequencies omitted"
        set_rows(data, "alcohol_frequency", wave, code,
                 value_semantics=f"Past-year monthly frequency category for {beverage}, a beverage-specific component. {route} Not an overall alcohol-frequency measure or dose; do not sum across beverage types.",
                 value_label_status=status, mapping_status=status,
                 questionnaire_source=f"sources_official/{WAVES[wave][0]}:L{line}",
                 note=route + " 不应与其他酒类字段直接求和。Structural skips are not zero; keep wave and beverage scope separate.")

    set_rows(data, "alcohol_frequency", "2020", "da052",
             value_semantics=("Overall past-year monthly frequency of any alcoholic beverage. The Chinese Wave 5 flowchart routes DA051=1 to DA052 and DA051=2/3 to the end. "
                              "This is not beverage-specific and is not directly interchangeable with 2011-2018 DA072/DA074/DA076, even though response categories match. Structural skips are not zero."),
             value_label_status="official Chinese questionnaire response categories and flowchart route reviewed; overall measure and conditional denominator retained; frequencies omitted",
             mapping_status="official Chinese questionnaire and flowchart reviewed; overall any-beverage measure conditional on DA051=1; do not pool directly with earlier beverage-specific items",
             questionnaire_source="sources_official/CHARLS_2020_Questionnaire_Chinese_extracted.txt:L1401; sources_official/CHARLS_2020_Flowchart_Chinese.pdf:PDF p.30 (printed p.24)",
             note="2020 overall monthly frequency among DA051=1; it is not split by beverage type, unlike earlier beverage-specific fields. Do not infer zero from structural skip or pool without a prespecified harmonization rule.")

    topic = json.loads(TOPIC.read_text(encoding="utf-8"))
    lookup = {(r.concept_id, r.wave, r.code.lower()): r for r in data.itertuples(index=False)}
    for concept in topic:
        for field in concept.get("source_fields", []):
            row = lookup.get((concept["concept_id"], field["wave"], field["code"].lower()))
            if row:
                for key in ("value_label_status", "value_label_source", "value_semantics",
                            "questionnaire_source", "mapping_status", "note"):
                    field[key] = getattr(row, key)
    data.to_csv(MAP, index=False, encoding="utf-8-sig")
    TOPIC.write_text(json.dumps(topic, ensure_ascii=False, indent=2), encoding="utf-8")
    c_status_rows = sync_c_metadata_statuses()
    print(f"Updated five past-year threshold fields, eleven beverage-frequency fields, Wave 5 overall frequency, and {c_status_rows} alcohol C metadata rows. No respondent records or Codebook frequency summaries used.")


if __name__ == "__main__":
    main()
