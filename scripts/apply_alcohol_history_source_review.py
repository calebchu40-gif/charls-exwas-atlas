"""Apply questionnaire-backed alcohol-history and morning-drink metadata."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "audit/behavior_exposure_variable_mapping_v1.csv"
TOPIC = ROOT / "site-prototype/dist/behavior_exposures_v1.json"

HISTORY = {
    "2011": ("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", 2607, "CHARLS_2011_Codebook_extracted.txt"),
    "2013": ("CHARLS_2013_Questionnaire_extracted.txt", 3248, "CHARLS_2013_Codebook_extracted.txt"),
    "2015": ("CHARLS_2015_Questionnaire_extracted.txt", 2651, "CHARLS_2015_Codebook_extracted.txt"),
    "2018": ("CHARLS_2018_Questionnaire_extracted.txt", 3124, "CHARLS_2018_Codebook_extracted.txt"),
}
MORNING = {
    "2011": ("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", 2666, "CHARLS_2011_Codebook_extracted.txt"),
    "2013": ("CHARLS_2013_Questionnaire_extracted.txt", 3314, "CHARLS_2013_Codebook_extracted.txt"),
}


def required_text(filename: str, terms: tuple[str, ...]) -> str:
    path = ROOT / "sources_official" / filename
    text = path.read_text(encoding="utf-8", errors="replace")
    if not all(term.casefold() in text.casefold() for term in terms):
        raise ValueError(f"Official source validation failed: {filename}")
    return text


def main() -> None:
    category_terms = ("never had a drink", "used to drink less than once a month", "used to drink more than once a month")
    for wave, (questionnaire, _, codebook) in HISTORY.items():
        required_text(questionnaire, ("DA069", *category_terms))
        required_text(codebook, ("da069", *category_terms))
    for wave, (questionnaire, _, codebook) in MORNING.items():
        required_text(questionnaire, ("DA078", "In the last year", "steady your"))
        required_text(codebook, ("da078", "taking a drink first thing"))

    data = pd.read_csv(MAP, dtype=str, encoding="utf-8-sig").fillna("")
    history_updated = 0
    for wave, (questionnaire, line, codebook) in HISTORY.items():
        mask = data.concept_id.eq("alcohol_history") & data.wave.eq(wave) & data.code.str.lower().eq("da069")
        if int(mask.sum()) != 1:
            raise ValueError(f"Expected exactly one alcohol_history DA069 mapping for {wave}; found {int(mask.sum())}")
        data.loc[mask, "value_labels"] = "1=Never had a drink; 2=Used to drink less than once a month; 3=Used to drink more than once a month"
        data.loc[mask, "value_label_status"] = "official questionnaire and Codebook response labels reviewed; prior-wave carry-forward and routed denominator retained; frequencies omitted"
        data.loc[mask, "value_label_source"] = f"sources_official/{codebook}; response labels only"
        data.loc[mask, "questionnaire_source"] = f"sources_official/{questionnaire}:L{line}; DA069 and its skip route"
        data.loc[mask, "value_semantics"] = (
            "Retrospective alcohol-use history/frequency category: never drank, used to drink less than monthly, or used to drink more than monthly. "
            "This is not current past-year drinking, quantity, or an exact monthly frequency. Preserve the DA069 route and historical reference. "
            "For re-interviews, DA069 may be skipped when the prior-wave history is already available; in 2018 the questionnaire explicitly uses ZDA069 for this carry-forward. "
            "A skipped or absent DA069 is not a No response and must not be pooled as one without release-specific validation."
        )
        data.loc[mask, "mapping_status"] = "official questionnaire and Codebook response categories reviewed; historic construct retained; re-interview carry-forward and eligible denominator must be respected"
        data.loc[mask, "note"] = (
            "DA069 asks past drinking history/frequency, not current intake or dose. Labels match the Codebook. Preserve the wave-specific route; "
            "2013/2015/2018 re-interviews can skip the item when prior history is already recorded (2018 ZDA069). Do not infer No from a skipped field."
        )
        history_updated += 1

    morning_updated = 0
    for wave, (questionnaire, line, codebook) in MORNING.items():
        mask = data.concept_id.eq("alcohol_morning_drink") & data.wave.eq(wave) & data.code.str.lower().eq("da078")
        if int(mask.sum()) != 1:
            raise ValueError(f"Expected exactly one alcohol_morning_drink DA078 mapping for {wave}; found {int(mask.sum())}")
        data.loc[mask, "value_labels"] = "1=Yes; 2=No"
        data.loc[mask, "value_label_status"] = "official questionnaire and Codebook Yes/No labels reviewed; conditional DA069 route and eligible denominator retained; frequencies omitted"
        data.loc[mask, "value_label_source"] = f"sources_official/{codebook}; response labels only"
        data.loc[mask, "questionnaire_source"] = f"sources_official/{questionnaire}:L{line}; past-year morning-drink item"
        data.loc[mask, "value_semantics"] = (
            "Past-year morning-drink behavior: first drink in the morning to steady nerves or relieve a hangover. "
            "The questionnaire routes respondents with DA069=never or <monthly past drinking past the DA070–DA078 sequence; "
            "this item therefore does not have a population-wide denominator. Preserve route and eligible sample; structural skips are not No. "
            "This is a candidate dependence-related behavior marker, not alcohol quantity or a diagnosis."
        )
        data.loc[mask, "mapping_status"] = "official questionnaire and Codebook item/Yes-No labels reviewed; conditional DA069 route and eligible denominator retained"
        data.loc[mask, "note"] = "Asked about the past year and conditionally reached through the DA069 history route; not a population-wide Yes/No prevalence field. Do not recode structural skips as No."
        morning_updated += 1

    data.to_csv(MAP, index=False, encoding="utf-8-sig")
    topic = json.loads(TOPIC.read_text(encoding="utf-8"))
    lookup = {(r.concept_id, r.wave, r.code): r for r in data.itertuples(index=False)}
    for concept in topic:
        for field in concept.get("source_fields", []):
            row = lookup.get((concept["concept_id"], field["wave"], field["code"]))
            if row:
                field.update(
                    value_labels=row.value_labels,
                    value_label_status=row.value_label_status,
                    value_label_source=row.value_label_source,
                    value_semantics=row.value_semantics,
                    questionnaire_source=row.questionnaire_source,
                    note=row.note,
                )
    TOPIC.write_text(json.dumps(topic, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Reviewed alcohol-history fields={history_updated}; morning-drink fields={morning_updated}; no respondent records or Codebook frequencies used.")


if __name__ == "__main__":
    main()
