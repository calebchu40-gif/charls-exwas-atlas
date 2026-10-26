"""Build a metadata-only, special-wave crosswalk for CHARLS 2014 Life History.

Only codebook variable names/labels and questionnaire item wording are used.
The Life History Codebook's descriptive frequencies are deliberately ignored.
This special survey has no released weight and is excluded from the regular
2011/2013/2015/2018/2020 E/P pair-coavailability matrix.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources_official"
AUDIT = ROOT / "audit"
DIST = ROOT / "site-prototype" / "dist"
CODEBOOK = SOURCES / "CHARLS_Life_History_codebook_extracted.txt"
QUESTIONNAIRE = SOURCES / "CHARLS_Life_History_Questionnaire_extracted.txt"

COMMON = (
    "2014 special Life History survey; retrospective self-report. The official release note states that no weight is provided. "
    "Do not pool into regular-wave weighted pairwise analyses without a separately justified target population and linkage/design plan."
)

GROUPS = [
    {
        "concept_id": "life_history_residential_architecture",
        "label": "Residential building type over the life course",
        "role": "e",
        "domain": "retrospective housing and built environment",
        "patterns": [r"ac005a_\d+_", r"ac005b_\d+_", r"ac005b_1_\d+_"],
        "question": "AC005a/AC005b",
        "unit": "categorical building type; transition year components",
        "values": "AC005a: 1=concrete/brick-wood; 2=adobe; 3=wood/thatched; 4=cave; 5=yurt; 6=boat house; 7=other. AC005b: 1=changed; 2=not changed. AC005b_1: calendar year.",
        "status": "official questionnaire categories reviewed; repeated residence episodes and transition years are components, not independent exposures",
        "caveat": "Questionnaire loops through successive residence/building episodes. Do not infer duration from a category alone; event timing, episode order and recall must be checked in the licensed release. No residential address fields are included.",
    },
    {
        "concept_id": "life_history_residential_urbanicity",
        "label": "Urban/rural setting across residential episodes",
        "role": "e",
        "domain": "retrospective residential and built environment",
        "patterns": [r"t004_\d+_"],
        "question": "T004",
        "unit": "five-level rural/urban residence pattern for each episode",
        "values": "1=always rural; 2=always urban; 3=mainly rural; 4=mainly urban; 5=roughly equal time in rural and urban areas.",
        "status": "official questionnaire responses and Codebook field identities reviewed",
        "caveat": "Episode-specific retrospective context; residence loops are nested components, not 25 independent exposure concepts. Do not use `t002_psu_*` address codes or infer objective environmental conditions from rural/urban status.",
    },
    {
        "concept_id": "life_history_residential_transition_reasons",
        "label": "Reasons for leaving successive residences",
        "role": "e",
        "domain": "retrospective residential and life-course social context",
        "patterns": [r"t003c_\d+_s\d+"],
        "question": "T003c",
        "unit": "episode-specific reason option slots (up to 25 residence episodes)",
        "values": "Questionnaire options: schooling/graduation/drop-out; marriage/divorce/separation; work away; family care; famine/disaster flight; return to hometown; army/veteran service; moving with family; whole-village relocation/demolition; send-down/back to city; sent-down youth/back to city; house purchase; other (open response not ingested).",
        "status": "official questionnaire response options and Codebook labels reviewed; option storage/skip routing still requires licensed-release verification",
        "caveat": "Retrospective reasons reported for a residence transition, not a physical pollutant exposure. The Codebook exposes 13 option-specific fields per episode; do not count slots as separate exposures or infer No from an unselected/blank option. Excludes address and geographic identifiers.",
    },
    {
        "concept_id": "life_history_cooking_fuel",
        "label": "Household cooking fuel used since birth",
        "role": "e",
        "domain": "retrospective household energy exposure proxy",
        "patterns": [r"ac006(?:s[1-4]|_[12])"],
        "question": "AC006",
        "unit": "selected fuel source; adoption year",
        "values": "Selected options: coal; electricity/fuel gas; household cooked without these sources; household did not cook. AC006_1/_2: calendar year source began.",
        "status": "official questionnaire selected-option labels reviewed; checkbox storage and release coding require licensed-data QA",
        "caveat": "Household/lifetime recalled proxy, not an individual dose or measured pollutant. Unselected checkbox slots are not interpreted as No; onset year is not duration or cumulative dose.",
    },
    {
        "concept_id": "life_history_heating_energy",
        "label": "Household heating energy/service since birth",
        "role": "e",
        "domain": "retrospective household energy exposure proxy",
        "patterns": [r"ac008(?:s[1-5]|_[1-3])"],
        "question": "AC008",
        "unit": "selected heating source/service; adoption year",
        "values": "Selected options: coal; electricity/fuel gas/solar; central heating; heating without listed sources; no heating service. AC008_1/_2/_3: calendar year source began.",
        "status": "official questionnaire selected-option labels reviewed; checkbox storage and release coding require licensed-data QA",
        "caveat": "Household/lifetime recalled proxy, not an individual dose. Keep central heating distinct from household fuels; unselected checkbox slots are not interpreted as No; no cumulative dose is derived.",
    },
    {
        "concept_id": "life_history_basic_utility_adoption",
        "label": "Lifetime adoption of clean water, sanitation and electricity",
        "role": "e",
        "domain": "retrospective housing and built environment",
        "patterns": [r"ac029[abcd](?:_1)?"],
        "question": "AC029a-AC029d",
        "unit": "access/onset status; calendar year when adopted",
        "values": "Status: 1=from a specified year; 2=already available before respondent's birth; 3=not yet available. _1 fields: calendar year.",
        "status": "official questionnaire status categories reviewed; release coding and routes require licensed-data QA",
        "caveat": "Retrospective household/residence-level infrastructure proxy. Clean piped water, flush toilet, private toilet and electricity remain separate. Do not interpret onset year as duration or exposure intensity.",
    },
    {
        "concept_id": "life_history_parental_divorce",
        "label": "Biological-parent divorce/separation and respondent age at event",
        "role": "e",
        "domain": "early-life family and psychosocial context",
        "patterns": [r"a7", r"a10", r"a10_1"],
        "question": "A7/A10/A10_1",
        "unit": "parental divorce report; exact age in years or fallback age band",
        "values": "A7: 1=yes, 2=no. A10: respondent age when parents divorced. If exact age is unknown/refused, A10_1 asks 0-3, 4-11, 12-16, or 17+ years.",
        "status": "official questionnaire route and categories reviewed; keep exact-age and fallback-band responses as alternative representations",
        "caveat": "A10/A10_1 are conditional on A7=yes; A10_1 is asked when exact age is unknown/refused. Do not count the two age fields as independent exposures or treat skip/missing as no divorce. Questionnaire notes that long emotional separations may count, remarriage after divorce does not undo it, and bereavement is not classified as divorce.",
    },
    {
        "concept_id": "life_history_childhood_family_finances",
        "label": "Childhood family financial standing relative to community",
        "role": "e",
        "domain": "childhood socioeconomic context",
        "patterns": [r"c4_a"],
        "question": "C4_a",
        "unit": "five-level relative financial status",
        "values": "1=much better; 2=somewhat better; 3=same; 4=somewhat worse; 5=much worse than the community average.",
        "status": "official questionnaire response categories reviewed; retrospective ordinal proxy",
        "caveat": "Asked for the household in which the respondent lived the longest before age 17 when family circumstances differed. Not a numeric income or wealth measure.",
    },
    {
        "concept_id": "life_history_childhood_food_insecurity",
        "label": "Childhood household food insecurity",
        "role": "e",
        "domain": "childhood socioeconomic context",
        "patterns": [r"c3_a", r"c3_bs[1-3]"],
        "question": "C3_a/C3_b",
        "unit": "ever insufficient food; selected childhood age bands",
        "values": "C3_a: 1=yes, 2=no. C3_b selected age bands: 1=0-5; 2=6-12; 3=13-17 years.",
        "status": "official questionnaire categories reviewed; selected age bands require checkbox interpretation",
        "caveat": "Household-reported retrospective exposure. Age bands are components of a multi-response item; do not treat unselected bands as a separately observed No or assume severity/frequency.",
    },
    {
        "concept_id": "life_history_1958_1962_famine_exposure",
        "label": "Family famine/starvation exposure, 1958-1962",
        "role": "e",
        "domain": "historical and childhood socioeconomic context",
        "patterns": [r"c4"],
        "question": "C4",
        "unit": "binary family-history report",
        "values": "1=yes; 2=no.",
        "status": "official questionnaire item identified; retrospective family-level report",
        "caveat": "Question asks about respondent and extended family experience during 1958-1962. Age at exposure varies by birth cohort; not an individual famine-dose measure. Keep separate from C3_a childhood food insecurity.",
    },
    {
        "concept_id": "life_history_famine_displacement",
        "label": "Family displacement from famine-stricken area",
        "role": "e",
        "domain": "historical environmental and social context",
        "patterns": [r"c5"],
        "question": "C5 (1958-1962 famine sequence)",
        "unit": "family-level retrospective yes/no report",
        "values": "1=yes; 2=no, as printed in the official questionnaire.",
        "status": "official questionnaire and Codebook field identity reviewed; conditional routing and release coding require licensed-data QA",
        "caveat": "Asks whether the respondent or family moved away from a famine-stricken area during the 1958-1962 period. This is family-reported historical displacement, not a geocoded place or individual dose. Treat as conditional on the famine sequence; do not infer an unasked response as No.",
    },
    {
        "concept_id": "life_history_famine_flight_policy",
        "label": "Reported local-government permission to flee famine",
        "role": "e",
        "domain": "historical policy and social context",
        "patterns": [r"c6"],
        "question": "C6 (1958-1962 famine sequence)",
        "unit": "retrospective yes/no report of local policy",
        "values": "1=yes; 2=no, as printed in the official questionnaire.",
        "status": "official questionnaire and Codebook field identity reviewed; conditional route and release coding require licensed-data QA",
        "caveat": "A respondent-reported historical policy context, not an independently verified policy record or a location-specific linkage. Retain as a provisional broad E candidate and do not infer an unasked response as No.",
    },
    {
        "concept_id": "life_history_famine_family_mortality",
        "label": "Family deaths attributed to famine starvation",
        "role": "p",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family-level historical mortality outcome",
        "patterns": [r"c7", r"c7_1"],
        "question": "C7/C7_1 (1958-1962 famine sequence)",
        "unit": "family-level yes/no report and conditional count",
        "values": "C7: 1=yes; 2=no. C7_1: count of affected relatives when applicable; value range and special codes require licensed-release review.",
        "status": "official questionnaire and Codebook field identities reviewed; count scale, conditional routing and authorized-release coding require QA",
        "caveat": "This is reported mortality among relatives, not the respondent's own mortality or a validated household rate. C7_1 is conditional on C7 and must not be used as a population mortality count or rate without a defined family denominator.",
    },
    {
        "concept_id": "life_history_famine_family_reproductive_consequences",
        "label": "Family reproductive consequences attributed to famine food shortage",
        "role": "p",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family-level historical reproductive consequences",
        "patterns": [r"c8s[1-6]"],
        "question": "C8 (1958-1962 famine sequence)",
        "unit": "six option-specific response fields",
        "values": "Questionnaire options include delayed marriage, delayed or prevented childbirth, abortion, infant abandonment, and none. Option 5 is inconsistent across the official Chinese and English questionnaire text; preserve as unresolved pending authorized-release verification.",
        "status": "official questionnaire and Codebook fields identified; option 5 translation conflict and checkbox/none storage require review",
        "caveat": "Family-reported consequences, not necessarily the respondent's own reproductive history or clinical phenotype. Checkbox blanks do not establish No; the none-of-these option must be checked against release coding. The English questionnaire repeats 'artificial abortion' for option 5, while Chinese says 'abandoning an infant'.",
    },
    {
        "concept_id": "life_history_parental_guardian_education",
        "label": "Biological parents' education",
        "role": "e",
        "domain": "childhood socioeconomic context",
        "patterns": [r"a6[ab]"],
        "question": "A6a/A6b",
        "unit": "official education category",
        "values": "See wave-specific Life History Codebook value labels; category frequencies are intentionally omitted.",
        "status": "Codebook variable identity reviewed; exact category set displayed only after label-level comparison",
        "caveat": "Biological-parent education, not necessarily the guardian who raised the respondent. Do not substitute guardian or respondent education.",
    },
    {
        "concept_id": "life_history_guardian_employment_context",
        "label": "Childhood female/male guardian work and unemployment",
        "role": "e",
        "domain": "childhood socioeconomic context",
        "patterns": [r"c1_[ab]1", r"c2_[ab](?:_1)?"],
        "question": "C1a1/C1b1/C2a/C2b",
        "unit": "work participation and unemployment experience/frequency",
        "values": "C1 work duration: 1=all childhood; 2=part; 3=none. C2: 1=yes, 2=no; frequency: 1=not very often, 2=a few times, 3=many times.",
        "status": "official questionnaire categories and guardian-specific routes reviewed",
        "caveat": "Questions refer to female/male guardian before age 17 and have skip conditions. The Codebook labels these fields 'dependents'; retain questionnaire meaning and do not assume biological parents.",
    },
    {
        "concept_id": "life_history_childhood_guardian_occupation",
        "label": "Childhood female/male guardian occupation type",
        "role": "e",
        "domain": "childhood socioeconomic context",
        "patterns": [r"c1_[ab]2(?:_\d+)?"],
        "question": "C1a2/C1b2",
        "unit": "agricultural/non-agricultural occupation; open-text detail fields",
        "values": "1=farming; 2=non-agricultural; additional department, position and job-content fields are open text.",
        "status": "official questionnaire item and route reviewed; open-text response values are not ingested",
        "caveat": "Metadata only. Do not expose or publish personal occupation strings from respondent data. Guardian role and age-under-17 recall apply.",
    },
    {
        "concept_id": "life_history_childhood_neighborhood_quality",
        "label": "Childhood neighborhood safety, cohesion and cleanliness",
        "role": "e",
        "domain": "childhood social and built environment",
        "patterns": [r"d[1345]"],
        "question": "D1/D3/D4/D5",
        "unit": "four-level retrospective neighborhood perception items",
        "values": "D1 safety, D3 neighbor willingness to help, D4 neighbor cohesion, D5 cleanliness/attractiveness; each 1=most positive to 4=least positive per questionnaire wording.",
        "status": "official questionnaire categories reviewed; distinct items remain separate",
        "caveat": "Refers to the childhood place lived longest before age 17. Subjective retrospective neighborhood report, not an objective environmental measurement.",
    },
    {
        "concept_id": "life_history_childhood_peer_context",
        "label": "Childhood peer support, bullying and perceived safety",
        "role": "e",
        "domain": "childhood social environment",
        "patterns": [r"e[123]", r"f[1345]"],
        "question": "E1-E3/F1/F3-F5",
        "unit": "item-specific ordinal or binary retrospective reports",
        "values": "Use questionnaire item-specific categories; do not combine loneliness, friendship, bullying, happiness and safety into a single score.",
        "status": "official questionnaire items identified; per-item scales retained",
        "caveat": "Retrospective self-report about childhood. Questionnaire item wording and response scale differ; no composite score or validated cross-wave harmonization is implied.",
    },
    {
        "concept_id": "life_history_childhood_parent_relationships",
        "label": "Childhood parent/guardian relationships and family conflict",
        "role": "e",
        "domain": "childhood family and psychosocial context",
        "patterns": [r"j[1345678]_[ab]", r"j9", r"j10_[123]", r"k1_[abc]"],
        "question": "J1/J3-J10/K1",
        "unit": "item-specific relationship, conflict and violence reports",
        "values": "Preserve item-level categorical responses; do not aggregate relationship quality, parental conflict, favoritism and hitting into one index.",
        "status": "official questionnaire item identities and guardian routing reviewed",
        "caveat": "Sensitive retrospective family-history constructs. Route depends on availability of female/male guardians. Metadata only; no respondent narratives or small-cell results are published.",
    },
    {
        "concept_id": "life_history_young_adult_mentoring",
        "label": "Young-adult financial and non-financial mentoring",
        "role": "e",
        "domain": "life-course social support",
        "patterns": [r"l1_a(?:1s[12])?", r"l1_b(?:1s[12])?", r"l3(?:_as[12])?"],
        "question": "L1a/L1b/L3",
        "unit": "support presence and selected source type",
        "values": "Presence: 1=yes, 2=no. Source fields distinguish family member and non-family member; selected-option storage needs release-file verification.",
        "status": "official questionnaire item and route reviewed; selected-source fields remain checkbox candidates",
        "caveat": "Retrospective young-adult support for work/business or interpersonal relationships. Do not infer that an unselected source means no support.",
    },
    {
        "concept_id": "life_history_childhood_health",
        "label": "Childhood health and health-related school absence",
        "role": "p",
        "domain": "early-life health phenotype history",
        "patterns": [r"hs00[2-6]"],
        "question": "HS002-HS006",
        "unit": "retrospective self-rated health and health events before age 15",
        "values": "Includes childhood health status, school absence due to health, prolonged bed/home confinement, prolonged hospitalization and repeated hospitalization; preserve item-level scale and routes.",
        "status": "official questionnaire and Codebook field identity reviewed",
        "caveat": "These are retrospective early-life health history items, not current-wave clinical measures. They remain separate P candidates and are not automatically paired with 2014 exposures.",
    },
]


def read_codebook_fields() -> dict[tuple[str, str], str]:
    text = CODEBOOK.read_text(encoding="utf-8")
    out: dict[tuple[str, str], str] = {}
    for page in text.split("\f"):
        m = re.search(r"CHARLSCodeBook\s+\d+\s+([A-Z]+)", page)
        if not m:
            continue
        module = m.group(1)
        for code, label in re.findall(r"•\s*([A-Za-z][A-Za-z0-9_ ]*):\s*(.+)", page):
            key = (module, code.strip().lower())
            label = label.strip()
            if key in out and out[key] != label:
                raise ValueError(f"Conflicting official Codebook labels for {key}: {out[key]} vs {label}")
            out[key] = label
    return out


def build() -> tuple[list[dict], list[dict]]:
    fields = read_codebook_fields()
    rows: list[dict] = []
    summary: list[dict] = []
    expected = {"RESIDENCE": set(), "FAMILYINFORMATION": set(), "HEALTHHISTORY": set()}
    for group in GROUPS:
        role = group["role"]
        modules = set(group.get("modules", {"e": {"RESIDENCE", "FAMILYINFORMATION"}, "p": {"HEALTHHISTORY"}}[role]))
        patterns = [re.compile(pat, re.I) for pat in group["patterns"]]
        matches = [(module, code, label) for (module, code), label in fields.items()
                   if module in modules and any(p.fullmatch(code) for p in patterns)]
        if not matches:
            raise ValueError(f"No official Codebook variables found for {group['concept_id']}")
        summary.append({**{key: value for key, value in group.items() if key != "modules"}, "source_fields": []})
        for module, code, codebook_label in sorted(matches):
            row = {
                "concept_id": group["concept_id"],
                "concept_label": group["label"],
                "role": role,
                "domain": group["domain"],
                "wave": "2014",
                "wave_type": "special_life_history",
                "code": code,
                "module": module,
                "codebook_label": codebook_label,
                "questionnaire_item": group["question"],
                "unit": group["unit"],
                "value_labels": group["values"],
                "value_label_status": group["status"],
                "mapping_status": "candidate metadata mapped to official 2014 Life History Codebook; not analysis-ready",
                "caveat": group["caveat"] + " " + COMMON,
                "questionnaire_source": "sources_official/CHARLS_Life_History_Questionnaire.pdf",
                "codebook_source": "sources_official/CHARLS_Life_History_codebook.pdf",
                "release_note_source": "sources_official/CHARLS_Life_History_Release_note.pdf",
            }
            rows.append(row)
            summary[-1]["source_fields"].append(row)
            expected[module].add(code)

    codes = [(x["module"], x["code"]) for x in rows]
    if len(codes) != len(set(codes)):
        raise ValueError("A source field was assigned to multiple Life History concepts")
    if any("OBS:" in " ".join(row.values()) or re.search(r"\b\d[,.]?\d*%", row["value_labels"]) for row in rows):
        raise ValueError("Codebook frequencies/statistics must not be copied into atlas metadata")
    return rows, summary


def main() -> None:
    rows, concepts = build()
    AUDIT.mkdir(parents=True, exist_ok=True)
    DIST.mkdir(parents=True, exist_ok=True)
    csv_path = AUDIT / "life_history_exposure_crosswalk_v1.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    json_path = DIST / "life_history_exposures_v1.json"
    json_path.write_text(json.dumps(concepts, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"concepts": len(concepts), "field_rows": len(rows),
                      "by_role": {role: sum(x["role"] == role for x in rows) for role in ("e", "p")},
                      "by_module": {module: sum(x["module"] == module for x in rows)
                                    for module in sorted({x["module"] for x in rows})},
                      "csv": str(csv_path), "json": str(json_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
