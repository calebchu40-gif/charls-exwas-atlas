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
        "concept_id": "life_history_residential_episode_timing",
        "label": "Residential episode entry/exit timing and duration context",
        "role": "e",
        "domain": "life-course residential mobility and environmental context",
        "patterns": [r"t001a_\d+_", r"t001a_[1-4]_\d+_", r"t001b_\d+_", r"t001b_[1-4]_\d+_"],
        "question": "T001a/T001b",
        "unit": "episode-specific timing relation, year, month, season, or half-year fields (up to 25 residences)",
        "values": "T001a records whether entry coincided with birth/previous residence exit or gives a nonmatching date; T001b records whether/when the respondent first left that residence, including a still-resident option. Date components may be year, month, season, or half-year.",
        "status": "official questionnaire loop and Codebook field families reviewed; actual date coding, episode ordering, and missing values require authorized-release QA",
        "caveat": "Retrospective timeline metadata for residential mobility, not an environmental dose or geocoded exposure. Entry and exit dates are interdependent across episodes; the first entry may anchor to birth and later entries to the prior exit. Do not count the 250 fields as separate exposures, derive duration from incomplete dates, or publish participant dates. Geographic linkage is excluded; official release notes warn that t002_psu fields are not comparable to PSU.dta.",
    },
    {
        "concept_id": "life_history_between_residence_migration_reasons",
        "label": "Reasons for stopping cross-county mobility during residence-history gaps",
        "role": "e",
        "domain": "life-course migration and social context",
        "patterns": [r"t003e_\d+_s\d+"],
        "question": "T002e/T003e",
        "unit": "conditional option slots for up to 13 between-residence mobility-gap episodes",
        "values": "T003e uses the questionnaire's migration-stop reason categories; options parallel T003c, while other write-in response text is excluded.",
        "status": "official questionnaire gap eligibility and Codebook option fields reviewed; checkbox storage and episode alignment require authorized-release QA",
        "caveat": "Asked for gaps exceeding six months between listed residences, before the first residence, or after the final residence according to the questionnaire's T002e procedure. These are reasons for a period of cross-county mobility, not T003c reasons for leaving a listed residence; keep concepts separate. Do not treat blank options as No or use T002e region/location fields as environmental linkage.",
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
        "concept_id": "life_history_parental_loss",
        "label": "Biological-parent death and loss context",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "early-life family adversity",
        "patterns": [r"a1[ab]", r"a2[ab]_[12]"],
        "question": "A1/A2",
        "unit": "parent-specific alive status and conditional death year or age",
        "values": "A1 reports whether each biological parent is alive. If deceased, A2 records death year or age at death; preserve the year and age fields as alternative measures.",
        "status": "official parent-specific skip route reviewed; event timing and release coding require QA",
        "caveat": "Parent death is family adversity, not respondent mortality. Death fields are conditional on the parent being reported deceased; age at respondent event and temporal ordering require approved linkage to respondent birth year. Do not interpret skipped death fields as missing death or No.",
    },
    {
        "concept_id": "life_history_parental_remarriage_stepfamily",
        "label": "Parental remarriage and stepfamily transitions",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "early-life family structure and psychosocial context",
        "patterns": [r"a11[ab](?:_1|_2|_3|_4_[12])?", r"a12[ab](?:_1|_2|_3|_4_[12])?"],
        "question": "A11a/A11b/A12a/A12b",
        "unit": "parent-specific remarriage report, respondent age, step-parent status and conditional death timing",
        "values": "A11 covers remarriage after parental divorce; A12 covers remarriage after a biological parent's death. Exact age and age band are alternatives; step-parent alive status gates death timing.",
        "status": "official divorce/death branches, conditional age ranges and step-parent routes reviewed; release coding requires QA",
        "caveat": "Keep remarriage after divorce distinct from remarriage after bereavement and preserve maternal/paternal branches. Exact age and age band are not separate events. Step-parent death year/age are conditional. The questionnaire treats long-term cohabitation as marriage; no skipped field is recoded as No.",
    },
    {
        "concept_id": "life_history_nonbiological_parent_education",
        "label": "Adoptive and step-parent education",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family-of-origin socioeconomic context",
        "patterns": [r"a6[c-f]"],
        "question": "A6c-A6f",
        "unit": "highest completed education category for adoptive/step parents",
        "values": "Separate adoptive mother, stepmother, adoptive father and stepfather fields; do not combine these with biological-parent education.",
        "status": "official source identities and questionnaire categories reviewed; relationship-specific routes require release QA",
        "caveat": "These are adult caregiver/parent background measures, not the respondent's education. A4 identifies who raised the respondent before age 17; do not assume every listed adoptive/step parent was the primary caregiver or impute skipped categories.",
    },
    {
        "concept_id": "life_history_sibling_death_before_age6",
        "label": "Sibling deaths before age six and family relationship context",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "early-life family adversity",
        "patterns": [r"b1", r"b2_1_\d+_", r"b2_2_\d+_", r"b2_3_\d+_", r"b2_5_\d+_"],
        "question": "B1/B2_1-B2_3/B2_5",
        "unit": "count plus repeated sibling relationship, age-at-death, age-gap and parentage fields",
        "values": "B1 counts siblings who died before age six. Repeated B2 fields identify the sibling relationship, age at death, age gap, and same/different parentage; free-text cause of death is not included.",
        "status": "official questionnaire loops, fields and B1=0 route reviewed; authorized-release slot storage requires QA",
        "caveat": "B2 loops over deaths before age six and is conditional on B1>0; B1/B2 describe sibling/family adversity, not respondent death or a sibling mortality rate. Do not use open-text cause-of-death responses, infer No from absent loop slots, or treat repeated sibling slots as independent exposures.",
    },
    {
        "concept_id": "life_history_sibling_family_structure",
        "label": "Sibling composition and half-sibling family structure",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family-of-origin social context",
        "patterns": [r"b3", r"b4_2_\d+_", r"b4_3_\d+_", r"b5s\d+", r"b6_\d+_"],
        "question": "B3/B4_2-B4_3/B5/B6",
        "unit": "sibling count and repeated sibling gender, birth-year, parentage-selector and conditional relationship fields",
        "values": "B3 counts siblings who survived to age six. B4 records sibling gender and birth year. B5 selects siblings with a different parent; B6 records the corresponding parentage relationship. B5 includes a none option.",
        "status": "official questionnaire loop alignment and conditional B5-to-B6 route reviewed; identifier-free catalog only",
        "caveat": "B4_1 sibling names are excluded. B5 selectors align to siblings in B4, and B6 is asked only for selected siblings; do not treat selector slots as separate exposure indicators or blank as No. Sibling birth year and composition are family context, not measured respondent dose; no sibling records are published.",
    },
    {
        "concept_id": "life_history_sibling_party_membership",
        "label": "Sibling party-membership context",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family sociohistorical context",
        "patterns": [r"b7s\d+"],
        "question": "B7",
        "unit": "sibling-index selector fields plus a none option",
        "values": "B7 asks which sibling(s) are party members; fields represent sibling-list selections, not 26 independent yes/no exposures. Exact release storage remains unverified.",
        "status": "official sibling-list routing reviewed; checkbox/selector encoding requires authorized-release QA",
        "caveat": "Family-reported context about siblings. Align selector positions to the B4 sibling roster only after release-file verification; do not treat blank slots as No or infer the respondent's own political membership.",
    },
    {
        "concept_id": "life_history_sibling_ethnic_context",
        "label": "Sibling ethnic-composition context",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family sociohistorical context",
        "patterns": [r"b8s\d+", r"b9_\d+_"],
        "question": "B8/B9",
        "unit": "sibling-index selectors and conditional ethnicity categories",
        "values": "B8 selects minority siblings; B9 records an ethnicity category for selected siblings. Keep list-selector and sibling-specific category fields distinct.",
        "status": "official B8-to-B9 sibling route and category definitions reviewed; storage/linkage require authorized-release QA",
        "caveat": "This is sibling/family composition, not the respondent's ethnicity. B9 applies to siblings selected in B8; selector positions must be reconciled to the B4 roster, and no unselected sibling is coded as a non-minority individual without verified storage.",
    },
    {
        "concept_id": "life_history_parental_party_membership_context",
        "label": "Parent and caregiver party-membership context",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family sociohistorical context",
        "patterns": [r"c1_g1s\d+"],
        "question": "C1_g1",
        "unit": "parent/caregiver-index selector fields plus a none option",
        "values": "C1_g1 asks which biological, adoptive, step-parent or listed caregiver was a Communist Party member. The nine fields are response slots/options, not nine independent exposures.",
        "status": "official questionnaire and Codebook field family reviewed; response-slot storage and parent-roster alignment require authorized-release QA",
        "caveat": "Historical family context during childhood, not the respondent's own party membership. Preserve the none option and parent/caregiver selector meaning; do not infer a negative response from blanks or collapse relatives without release-file verification.",
    },
    {
        "concept_id": "life_history_parental_minority_ethnicity_context",
        "label": "Parent and caregiver minority-ethnicity status",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family sociohistorical context",
        "patterns": [r"c1_g2s\d+"],
        "question": "C1_g2",
        "unit": "parent/caregiver-index selector fields plus a none option",
        "values": "C1_g2 selects which biological, adoptive, step-parent or listed caregiver belongs to an ethnic minority; the nine fields are response slots/options, not independent people.",
        "status": "official questionnaire and Codebook route reviewed; selector storage and parent-roster alignment require authorized-release QA",
        "caveat": "This is family-of-origin ethnicity context, not the respondent's own ethnicity. Keep it separate from C1_g2_1 ethnicity-group fields; do not infer No from blank selectors or assume every relative slot represents an observed person.",
    },
    {
        "concept_id": "life_history_parental_minority_group_context",
        "label": "Ethnic groups of selected parents and caregivers",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family sociohistorical context",
        "patterns": [r"c1_g2_1_\d+_"],
        "question": "C1_g2_1",
        "unit": "conditional repeated ethnicity-category fields",
        "values": "C1_g2_1 records an ethnic-group category for each parent/caregiver selected in C1_g2; the questionnaire lists Hui, Zhuang, Uyghur, Manchu, Yi, Tibetan, Miao, Mongol, Dai, Tujia and Other.",
        "status": "official questionnaire loop and Codebook family reviewed; exact response-slot-to-relative linkage requires authorized-release QA",
        "caveat": "Asked only for relatives selected in C1_g2. Do not assign categories to unselected relatives, impute missing group fields, or treat repeated slots as independent observations; this is family context, not respondent ethnicity.",
    },
    {
        "concept_id": "life_history_parental_religious_context",
        "label": "Parent and caregiver religious-belief context",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family sociohistorical context",
        "patterns": [r"c1_g3s\d+"],
        "question": "C1_g3",
        "unit": "parent/caregiver-index selector fields plus a none option",
        "values": "C1_g3 asks which biological, adoptive, step-parent or listed caregiver had a religious belief; nine fields correspond to selector options, not nine independent exposures.",
        "status": "official questionnaire and Codebook family reviewed; Chinese questionnaire repeats A4a for option 8 where English says male caregiver; retain wording discrepancy and verify release coding",
        "caveat": "Historical family religious context, not the respondent's own belief. The English source identifies option 8 as the male-caregiver slot while Chinese repeats A4a; do not resolve this discrepancy by assumption. Preserve the none option and verify selector coding before analysis.",
    },
    {
        "concept_id": "life_history_sibling_sent_down_experience",
        "label": "Sibling sent-down movement experience",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family sociohistorical and migration context",
        "patterns": [r"b10s\d+"],
        "question": "B10",
        "unit": "sibling-index selector fields plus a none option",
        "values": "B10 asks which sibling(s) experienced the sent-down-to-countryside movement; fields are sibling-list selections, not independent exposure indicators.",
        "status": "official sibling-list route reviewed; selector storage and sibling roster alignment require authorized-release QA",
        "caveat": "This records a sibling's historical experience, not necessarily the respondent's own exposure or residence. Preserve family-level context and do not infer No from blank selector slots.",
    },
    {
        "concept_id": "life_history_sibling_death_after_age6",
        "label": "Death years of siblings who survived to age six",
        "role": "p",
        "modules": ["FAMILYINFORMATION"],
        "domain": "family-level historical mortality outcome",
        "patterns": [r"b11_\d+_"],
        "question": "B11/B4_4",
        "unit": "conditional sibling death-year fields",
        "values": "B11 asks the death year for siblings identified as deceased in B4_4; cause-of-death free text is not part of this catalog.",
        "status": "official B4_4-to-B11 route reviewed; authorized-release field order and coding require QA",
        "caveat": "Family-level sibling mortality history, not respondent mortality. Timing relative to the respondent's age requires approved linkage to respondent birth year and validation of the sibling loop order; do not treat these as individual events or derive a mortality rate.",
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
        "concept_id": "life_history_historical_family_class_background",
        "label": "Family class background in the 1950s-1970s",
        "role": "e",
        "modules": ["WEALTHHISTORY"],
        "domain": "historical family socioeconomic and political context",
        "patterns": [r"c5(?:[a-f])?s\d+"],
        "question": "C5/C5a-C5f",
        "unit": "27 option-specific fields for respondent, parents, grandparents and foster parents",
        "values": "The questionnaire lists historical family-background categories and a none option. Each field is an option slot within a multi-select question; preserve respondent/relative forms separately and do not treat option slots as separate exposures.",
        "status": "official questionnaire age and relative-specific routes reviewed; multi-select storage and authorized-release codes require QA",
        "caveat": "Only respondents aged 80 and over (born before December 1934 according to the questionnaire) are asked the respondent C5 item. Parent/grandparent and foster-parent follow-ups have conditional routes. These are historical family social/political classifications, not current household wealth, individual income, or a measured environmental dose. Questionnaire-only write-in text is not ingested; blanks are not interpreted as No.",
    },
    {
        "concept_id": "life_history_inheritance_history",
        "label": "Inheritance receipt, source, asset/debt type, timing and reported value",
        "role": "e",
        "modules": ["WEALTHHISTORY"],
        "domain": "life-course socioeconomic and wealth context",
        "patterns": [r"fs012", r"fs013", r"fs013_2_\d+_", r"fs013_3_\d+_s\d+", r"fs013_4_\d+_s\d+", r"fs013_5_\d+_"],
        "question": "FS012/FS013",
        "unit": "ever-inherited status plus up to five event year, source, asset/debt-type and nominal-value records",
        "values": "Inheritance may include housing, land, financial assets, financial debt, durable assets and other categories. FS013_3 and FS013_4 are multiple-response source/type slots; FS013_5 records reported value at the time, with inherited debt treated as negative in the questionnaire.",
        "status": "official questionnaire definitions and second-respondent route reviewed; release slot storage, amounts, missing codes and event alignment require authorized-release QA",
        "caveat": "Sensitive personal financial-history metadata. A household second respondent may be asked only about pre-marriage inheritance depending on the first respondent's FS012s status; FS012s is route metadata and excluded from this concept. Do not publish participant values, inheritances, or Codebook frequencies; no inflation adjustment or net-wealth score is derived. Blank repeated slots are not No.",
    },
    {
        "concept_id": "life_history_family_political_death_context",
        "label": "Relatives reported to have died for political reasons, 1950s–1970s",
        "role": "e",
        "modules": ["WEALTHHISTORY"],
        "domain": "historical family adversity and political context",
        "patterns": [r"c6s\d+"],
        "question": "C6",
        "unit": "relative-specific selection slots plus a none option",
        "values": "C6 is a multi-response relative list covering biological/foster parents, grandparents, siblings and children; the questionnaire describes deaths during 1950s–1970s political campaigns, based on the respondent's subjective judgement.",
        "status": "official interviewer note, questionnaire relative list and Codebook fields reviewed; selector coding requires authorized-release QA",
        "caveat": "Highly sensitive retrospective family political adversity. Preserve respondent-subjective attribution; do not imply independently verified cause of death. No relative identities, participant data or frequencies are published; blanks are not No and selections are not independent participant records.",
    },
    {
        "concept_id": "life_history_family_rightist_label_context",
        "label": "Family member or respondent labelled a rightist in the 1950s",
        "role": "e",
        "modules": ["WEALTHHISTORY"],
        "domain": "historical political and family adversity",
        "patterns": [r"c7s\d+"],
        "question": "C7",
        "unit": "relative-specific selection slots including respondent and a none option",
        "values": "C7 asks which listed family members, including the respondent, were labelled a 'rightist' during the 1950s Anti-rightist movement.",
        "status": "official questionnaire categories and Codebook selector family reviewed; multi-select storage requires authorized-release QA",
        "caveat": "Sensitive historical political-label information, not a verified legal finding or current political status. Metadata only; no participant-level answers, relative identities or Codebook frequencies are published. Blank selectors are not No.",
    },
    {
        "concept_id": "life_history_red_guard_participation",
        "label": "Respondent-reported Red Guard participation during the Cultural Revolution",
        "role": "e",
        "modules": ["WEALTHHISTORY"],
        "domain": "historical political and social context",
        "patterns": [r"c8"],
        "question": "C8 (Wealth History module)",
        "unit": "binary retrospective report",
        "values": "The questionnaire asks whether the respondent was a Red Guard during the Cultural Revolution; preserve the official response categories and verify release coding.",
        "status": "official questionnaire and Codebook field identity reviewed; authorized-release values and eligibility require QA",
        "caveat": "Sensitive retrospective political/social-history metadata. This is the WEALTHHISTORY:c8 field and is distinct from similarly named codes in other modules; catalog identity is determined by module plus code. No participant responses or frequencies are published.",
    },
    {
        "concept_id": "life_history_land_expropriation_history",
        "label": "Household land expropriation, timing, area and compensation since 1978",
        "role": "e",
        "modules": ["WEALTHHISTORY"],
        "domain": "household property and policy-related socioeconomic context",
        "patterns": [r"hf00[12]", r"hf003_[12]_\d+_", r"hf004_\d+_s\d+", r"hf004_[1-4]_\d+_"],
        "question": "HF001–HF004",
        "unit": "ever/number of land expropriations; repeated year, mu area and compensation-category/amount fields",
        "values": "HF001 gates land acquisition history; HF002 counts events; repeated HF003 records year and mu area; HF004 records compensation types and conditional amounts/areas, including money, land, work, pension insurance, urban hukou, other, or none.",
        "status": "official questionnaire, Codebook event loops and units reviewed; proxy response, route, release special values and monetary fields require QA",
        "caveat": "The questionnaire says this is the respondent's current-household history since that house was established, answered by the person who knows household information best. Not necessarily respondent-owned land or a personal exposure. Preserve HF001 No/not-applicable skips and HF002 loop structure; do not infer skipped events as No, sum compensation, or inflation-adjust values without a defined estimand and validation.",
    },
    {
        "concept_id": "life_history_home_demolition_history",
        "label": "Household home demolition, timing, area and compensation since 1978",
        "role": "e",
        "modules": ["WEALTHHISTORY"],
        "domain": "household housing disruption and property context",
        "patterns": [r"hf005", r"hf006", r"hf007_\d+_", r"hf008_[12]_\d+_", r"hf009_\d+_s\d+", r"hf009_[1-5]_\d+_"],
        "question": "HF005–HF009",
        "unit": "ever/count of demolitions; repeated year, house/patio area and compensation-category/amount fields",
        "values": "HF005/HF006 gate and count demolitions; repeated HF007 records year, HF008 house and patio area, and HF009 compensation type and conditional amounts/areas, including money, replacement house, homestead, urban hukou, other or none.",
        "status": "official questionnaire, Codebook loop structure and units reviewed; proxy response, route, special values and compensation coding require QA",
        "caveat": "Current-household property history since the current house was established, answered by a knowledgeable household respondent; not necessarily the participant's individually owned home. Keep distinct from land expropriation and T003c relocation reason. No participant amounts, years, areas or frequencies are published; do not impute No from blank loops or aggregate compensation without an explicit estimand.",
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
        "concept_id": "life_history_guardian_depressive_symptoms",
        "label": "Childhood female/male guardian anxiety and depressive symptoms",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "childhood family psychosocial environment",
        "patterns": [r"h[12]_[ab]", r"h3_[ab]", r"h4_[ab]", r"h5_[ab]", r"h8_[ab]"],
        "question": "H1-H5/H8 (female and male guardian forms)",
        "unit": "item-specific frequency, duration, symptom and interference responses",
        "values": "Keep nervousness/anxiety, upset/panic, prolonged sadness/depression, childhood duration, associated symptoms and interference as distinct items; do not create a diagnostic scale.",
        "status": "official questionnaire wording, guardian identity and depression skip route reviewed; authorized-release storage requires QA",
        "caveat": "Female/male guardian refers to the caregiver selected in A4a/A4b, not necessarily the biological mother/father. The item family is skipped when the corresponding guardian is absent; H4/H5/H8 are conditional after H3. Missing/skip is not No, and these are respondent-reported family-context exposures rather than the guardian's clinical diagnosis.",
    },
    {
        "concept_id": "life_history_guardian_substance_behaviors",
        "label": "Childhood female/male guardian substance-use behaviors",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "childhood family psychosocial environment",
        "patterns": [r"h9_[ab]s[1-5]", r"h10_[ab]", r"h11_[ab]", r"h14_[ab]"],
        "question": "H9-H11/H14 (female and male guardian forms)",
        "unit": "option-specific behavior fields and conditional follow-up items",
        "values": "H9 covers alcohol misuse, smoking, drug use, gambling and none; H10 follows the alcohol option, while H11/H14 follow the drug option. Preserve item identity and routes.",
        "status": "official questionnaire options and branch instructions reviewed; checkbox storage requires authorized-release QA",
        "caveat": "Reported for the childhood caregiver defined in A4a/A4b, not necessarily a biological parent. H10 is conditional on the alcohol option; H11/H14 are conditional on the drug option. An unselected option or skipped follow-up is not No; do not infer a substance-use diagnosis or severity score.",
    },
    {
        "concept_id": "life_history_guardian_behavioral_adversity",
        "label": "Childhood female/male guardian behavioral and justice-system history",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "childhood family and social adversity",
        "patterns": [r"h15_[ab]s[1-6]", r"h16_[ab]"],
        "question": "H15/H16 (female and male guardian forms)",
        "unit": "option-specific behavior fields and conditional charge category",
        "values": "H15 lists difficulty keeping a job, frequent lying, physical fights, criminal activity, arrest/imprisonment and none. H16 asks the charge when the arrest/imprisonment option applies; questionnaire option sets differ between female and male guardian forms.",
        "status": "official questionnaire options, guardian routing and H16 option-set difference reviewed; response storage requires release QA",
        "caveat": "Retrospective reports about a childhood caregiver, not the respondent's own behavior. H16 is conditional on the relevant H15 response and its female/male categories are not interchangeable. The catalog contains metadata only, not respondent reports or counts; no unselected option is recoded as No.",
    },
    {
        "concept_id": "life_history_guardian_physical_mental_health",
        "label": "Childhood female/male guardian prolonged illness and disability",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "childhood family health environment",
        "patterns": [r"h1[789]_[ab]"],
        "question": "H17-H19 (female and male guardian forms)",
        "unit": "three item-specific yes/no historical reports",
        "values": "Separate prolonged bed illness, serious physical deformity and mental abnormality; do not combine them into a clinical score.",
        "status": "official questionnaire items and guardian identity reviewed; authorized-release coding requires QA",
        "caveat": "Family-context reports refer to the female/male guardian defined in A4a/A4b, not necessarily a biological parent. These are not the respondent's conditions, and absent guardians or skipped items must not be coded as No.",
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
        "unit": "separate female/male caregiver work status and conditional unemployment experience/frequency",
        "values": "C1 work duration: 1=all childhood; 2=part; 3=none. C2: 1=yes, 2=no; frequency: 1=not very often, 2=a few times, 3=many times.",
        "status": "official questionnaire and Codebook fields reviewed; authorized-release special values and conditional routes require QA",
        "caveat": "Questions refer to the A4a/A4b female/male caregiver before age 17, not necessarily biological parents. C2 frequency fields follow Yes only and occupation-dependent skips; blank is not No. Keep caregiver-specific routes, do not convert childhood categories to years, and verify release values before analysis.",
    },
    {
        "concept_id": "life_history_childhood_guardian_occupation",
        "label": "Childhood female/male guardian occupation type",
        "role": "e",
        "domain": "childhood socioeconomic context",
        "patterns": [r"c1_[ab]2(?:_\d+)?"],
        "question": "C1a2/C1b2",
        "unit": "categorical agricultural/non-agricultural usual occupation; questionnaire also requests free-text detail",
        "values": "Structured category: 1=farming; 2=non-agricultural. Questionnaire requests department, position and job-content text, which is excluded from the public atlas.",
        "status": "official questionnaire and Codebook structured categories reviewed; open-text responses are not ingested",
        "caveat": "Caregiver occupation context, not respondent occupation or household income. Do not expose personal occupation strings; preserve A4a/A4b caregiver routes, do not infer skipped fields, and verify release values before analysis.",
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
        "concept_id": "life_history_childhood_romantic_relationship",
        "label": "Romantic relationship experience before age 17 and perceived influence",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "childhood psychosocial context",
        "patterns": [r"e7", r"e8"],
        "question": "E7/E8",
        "unit": "binary relationship-history item and conditional three-category influence item",
        "values": "E7 asks whether the respondent had a romantic partner before age 17; E8 records mostly positive, mostly negative or neutral perceived influence for the most important relationship.",
        "status": "official questionnaire route and Codebook item identities reviewed; E8 eligibility and release special values require QA",
        "caveat": "Sensitive retrospective relationship history. E8 follows E7=Yes; blank E8 is not No. Metadata only: no participant-level relationship details or response frequencies are published, and this is not a validated psychosocial scale.",
    },
    {
        "concept_id": "life_history_childhood_police_custody_and_charge",
        "label": "Police arrest/custody before age 17 and reported charge category",
        "role": "e",
        "modules": ["FAMILYINFORMATION"],
        "domain": "childhood adversity and justice-system contact",
        "patterns": [r"g1", r"g2"],
        "question": "G1/G2",
        "unit": "binary police arrest/custody history and conditional charge-category item",
        "values": "G1 asks about being arrested or taken into police custody before age 17; G2 records the charge category for an affirmative case, asking about the last event if there were multiple events.",
        "status": "official questionnaire route and Codebook field identities reviewed; exact authorized-release coding and privacy review required before any analysis",
        "caveat": "Highly sensitive retrospective justice-system information. An arrest/custody report is not proof of conviction or guilt. G2 follows G1=Yes and is conditional; blank is not No. This public catalog exposes metadata only, never participant values or counts; use in analysis requires a separate ethical, privacy, and disclosure review.",
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
    {
        "concept_id": "life_history_menarche_timing",
        "label": "Age at first menstrual period",
        "role": "p",
        "modules": ["HEALTHHISTORY"],
        "domain": "reproductive development history",
        "patterns": [r"hs048"],
        "question": "HS048",
        "unit": "five-category recalled age band",
        "values": "1=<11 years; 2=11–12; 3=13–15; 4=16–18; 5=>18. Asked only of female respondents per the questionnaire procedure.",
        "status": "official age eligibility and response bands reviewed; authorized-release coding requires QA",
        "caveat": "Retrospective, female-only reproductive-development phenotype candidate; not a direct environmental exposure or exact age. Preserve the questionnaire's broad bands and sex-specific route; do not infer age from band midpoints.",
    },
    {
        "concept_id": "life_history_adult_injury_disability",
        "label": "Adult physical injury with lasting disability or activity limitation",
        "role": "p",
        "modules": ["HEALTHHISTORY"],
        "domain": "adult injury and disability history",
        "patterns": [r"hs051", r"hs052a", r"hs053", r"hs053a", r"hs053a_1"],
        "question": "HS051–HS053a_1",
        "unit": "injury-history gate, work-related status, first injury year, disability certificate and conditional disability category",
        "values": "HS051 asks about physical injury resulting in permanent handicap/disability or daily-life limitation. HS052a asks whether the most serious injury was work related; HS053 records first injury year if multiple events; HS053a asks about a disability certificate and HS053a_1 records level/type.",
        "status": "official route and item referents reviewed; authorized-release category coding and special values require QA",
        "caveat": "Phenotype history, not an exposure dose. HS052 narrative injury type/body part is questionnaire free text and is not ingested. HS052a/HS053/HS053a follow HS051=Yes; HS053a_1 is conditional on certification. Do not interpret blank follow-ups as No or imply causation from work-related status.",
    },
    {
        "concept_id": "life_history_ill_health_work_consequences",
        "label": "Workplace consequences attributed to ill health after age 16",
        "role": "p",
        "modules": ["HEALTHHISTORY"],
        "domain": "health-related occupational functioning",
        "patterns": [r"hs060s[1-6]", r"hs060s96"],
        "question": "HS060",
        "unit": "seven multi-select outcome slots, including a none option",
        "values": "Questionnaire options: denied promotion; reduced work responsibilities; work below qualifications; harassment by boss/colleagues; pay cut; dismissal; none of these. Respondent attributes the experience to ill health after age 16.",
        "status": "official multi-select menu and age/attribution scope reviewed; checkbox storage requires authorized-release QA",
        "caveat": "Retrospective self-attributed occupational consequence, not an objective employment record or disease diagnosis. Treat options as components of one reported outcome family; none is mutually exclusive in meaning and unselected slots are not automatically No. Do not expose response counts.",
    },
    {
        "concept_id": "life_history_adult_health_burden",
        "label": "Adult illness-related confinement, hospitalization and work absence",
        "role": "p",
        "modules": ["HEALTHHISTORY"],
        "domain": "adult health and functional limitation history",
        "patterns": [r"hs06[1-4]"],
        "question": "HS061–HS064",
        "unit": "four binary retrospective indicators after age 16",
        "values": "One-month-or-longer bed/home confinement; one-month-or-longer hospitalization; more than three hospitalizations within a 12-month period; and leaving a job for at least one month because of a health condition.",
        "status": "official age thresholds and item wording reviewed; authorized-release special values require QA",
        "caveat": "Separate retrospective health/function outcomes, not current clinical measurements. Preserve the distinct thresholds and work-absence referent; do not collapse into an unvalidated severity score or infer No from skipped responses.",
    },
    {
        "concept_id": "life_history_childhood_vaccination",
        "label": "Any vaccination before age 16",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "early-life preventive healthcare access",
        "patterns": [r"hc001"],
        "question": "HC001",
        "unit": "binary retrospective report",
        "values": "Any vaccination before age 15 inclusive; questionnaire examples include smallpox vaccination and oral polio-prevention pills.",
        "status": "official age boundary and examples reviewed; authorized-release coding requires QA",
        "caveat": "Candidate early-life preventive-care marker, not a vaccine-specific exposure or complete immunization record. The questionnaire examples are not exhaustive; do not infer type, timing, dose or disease protection.",
    },
    {
        "concept_id": "life_history_usual_source_of_care",
        "label": "Usual source of care and periods without convenient care",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "life-course healthcare access",
        "patterns": [r"hc002", r"hc004a", r"hc004s[1-7]"],
        "question": "HC002/HC004/HC004a",
        "unit": "usual-source status, first-doctor type, and age-band-specific years without a usual source",
        "values": "HC002 defines usual source as a particular person/place for illness or advice within two hours. If No, HC004 records age periods and approximate years without such a source; HC004a asks the type of doctor seen the first time the respondent remembers seeing a doctor, with a separate never-seen option.",
        "status": "official routing, two-hour definition and age-band labels reviewed; duration slots and doctor categories require authorized-release QA",
        "caveat": "Retrospective access context. HC004 fields follow HC002=No; their durations are approximate and age bands differ in width. HC004a is a separate first-doctor referent, not automatically the usual source. The English questionnaire labels HC004a as first remembered doctor; check the Chinese instrument and authorized release before comparing categories. Do not sum durations across unequal age bands without a prespecified denominator.",
    },
    {
        "concept_id": "life_history_adult_blood_pressure_screening",
        "label": "Blood pressure screening after age 16",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "adult preventive healthcare utilization",
        "patterns": [r"hc005", r"hc005_1"],
        "question": "HC005/HC005_1",
        "unit": "ever-screened status and first screening year",
        "values": "Questionnaire asks whether blood pressure was checked after age 16 and, if yes, the first calendar year.",
        "status": "official route and date referent reviewed; authorized-release year coding requires QA",
        "caveat": "Screening/utilization history, not measured blood pressure or hypertension status. HC005_1 follows Yes; preserve the first-year referent and do not treat the year as screening frequency or quality.",
    },
    {
        "concept_id": "life_history_adult_blood_test",
        "label": "Blood testing after age 16",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "adult preventive healthcare utilization",
        "patterns": [r"hc008", r"hc008_1"],
        "question": "HC008/HC008_1",
        "unit": "ever-tested status and first blood-test year",
        "values": "Questionnaire asks about blood testing after age 16 (e.g., cholesterol or blood sugar), excluding blood tests performed in previous CHARLS visits; HC008_1 records the first year after age 16.",
        "status": "official wording and exclusion of prior CHARLS visits reviewed; authorized-release coding requires QA",
        "caveat": "Healthcare utilization history, not a cholesterol/glucose result or diagnosis. Preserve the exclusion of previous CHARLS study visits and conditional year route; do not infer which analyte was tested from a Yes response.",
    },
    {
        "concept_id": "life_history_breast_screening",
        "label": "Breast examination after age 16",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "sex-specific preventive healthcare utilization",
        "patterns": [r"hc011a", r"hc011a_1"],
        "question": "HC011a/HC011a_1",
        "unit": "ever-examined status and first examination year",
        "values": "Questionnaire routes to this item for female respondents and records whether breast examination occurred after age 16 and the first year if Yes.",
        "status": "official sex-specific skip and year route reviewed; authorized-release coding requires QA",
        "caveat": "Sex-specific healthcare utilization, not a cancer diagnosis or proof of guideline-concordant screening. Keep separate from prostate testing; year follows Yes and must not be imputed from a skipped male route.",
    },
    {
        "concept_id": "life_history_prostate_screening",
        "label": "Prostate cancer testing after age 16",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "sex-specific preventive healthcare utilization",
        "patterns": [r"hc014", r"hc014_1"],
        "question": "HC014/HC014_1",
        "unit": "ever-tested status and first test year",
        "values": "Questionnaire defines testing examples including digital rectal exam, PSA and transrectal ultrasound-guided biopsy; the male/female route is specified in the questionnaire.",
        "status": "official screening definition, sex-specific route and year condition reviewed; authorized-release coding requires QA",
        "caveat": "Sex-specific healthcare utilization, not prostate cancer diagnosis; the question combines heterogeneous test types and does not establish indication or screening quality. Keep test year conditional and separate from breast examination.",
    },
    {
        "concept_id": "life_history_vision_screening",
        "label": "Vision testing after age 16",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "adult preventive healthcare utilization",
        "patterns": [r"hc017", r"hc017_1"],
        "question": "HC017/HC017_1",
        "unit": "ever-tested status and first test year",
        "values": "Questionnaire asks whether the respondent had a vision test after age 16 and, if Yes, the first calendar year.",
        "status": "official question and conditional date route reviewed; authorized-release coding requires QA",
        "caveat": "Healthcare utilization history, not visual acuity or an eye-disease phenotype. Preserve first-year and conditional response semantics.",
    },
    {
        "concept_id": "life_history_dental_screening",
        "label": "Dental examination after age 16",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "adult preventive healthcare utilization",
        "patterns": [r"hc017a", r"hc017a_1"],
        "question": "HC017a/HC017a_1",
        "unit": "ever-examined status and first examination year",
        "values": "Questionnaire asks whether the respondent had dental examinations after age 16 and, if Yes, the first calendar year.",
        "status": "official question and conditional date route reviewed; authorized-release coding requires QA",
        "caveat": "Healthcare utilization history, not oral-health status or examination quality. Preserve conditional year route; do not interpret no reported examination as a dental diagnosis.",
    },
    {
        "concept_id": "life_history_physical_activity_increase_periods",
        "label": "Life periods when physical activity was increased for at least a year",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "life-course health behavior change",
        "patterns": [r"hc023s1", r"hc024_1_s[1-7]"],
        "question": "HC023/HC024 physical activity option",
        "unit": "ever-change selector and seven age-period selectors",
        "values": "HC023 qualifies changes maintained for at least one year; HC024 age periods are 0–15, 16–25, 26–40, 41–55, 56–65, 66–75 and >75 years.",
        "status": "official duration threshold, behavior referent and age-band labels reviewed; multi-select release coding requires QA",
        "caveat": "Reports periods of increased activity, not activity level, type, intensity or duration beyond the one-year eligibility threshold. HC024 is routed for selected HC023 behaviors; period slots are not independent exposures and an unselected band is not No.",
    },
    {
        "concept_id": "life_history_diet_change_periods",
        "label": "Life periods when diet was changed for at least a year",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "life-course health behavior change",
        "patterns": [r"hc023s2", r"hc024_2_s[1-7]"],
        "question": "HC023/HC024 diet-change option",
        "unit": "ever-change selector and seven age-period selectors",
        "values": "HC023 qualifies changes maintained for at least one year; HC024 age periods are 0–15, 16–25, 26–40, 41–55, 56–65, 66–75 and >75 years.",
        "status": "official duration threshold, behavior referent and age-band labels reviewed; multi-select release coding requires QA",
        "caveat": "The questionnaire says 'changed your diet'; it does not establish improvement, diet quality or a particular dietary pattern. Period selectors are conditional and not independent exposures; blank/unchecked slots are not No.",
    },
    {
        "concept_id": "life_history_smoking_cessation_periods",
        "label": "Life periods when smoking was stopped for at least a year",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "life-course health behavior change",
        "patterns": [r"hc023s3", r"hc024_3_s[1-7]"],
        "question": "HC023/HC024 smoking-cessation option",
        "unit": "ever-cessation selector and seven age-period selectors",
        "values": "HC023 qualifies changes maintained for at least one year; HC024 age periods are 0–15, 16–25, 26–40, 41–55, 56–65, 66–75 and >75 years.",
        "status": "official duration threshold, behavior referent and age-band labels reviewed; multi-select release coding requires QA",
        "caveat": "Captures reported smoking cessation, not smoking initiation, cumulative smoking, duration or relapse. Period selectors are conditional and not independent exposures; blank/unchecked slots are not No.",
    },
    {
        "concept_id": "life_history_alcohol_reduction_periods",
        "label": "Life periods when alcohol consumption was reduced for at least a year",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "life-course health behavior change",
        "patterns": [r"hc023s4", r"hc024_4_s[1-7]"],
        "question": "HC023/HC024 alcohol-reduction option",
        "unit": "ever-reduction selector and seven age-period selectors",
        "values": "HC023 qualifies changes maintained for at least one year; HC024 age periods are 0–15, 16–25, 26–40, 41–55, 56–65, 66–75 and >75 years.",
        "status": "official duration threshold, behavior referent and age-band labels reviewed; multi-select release coding requires QA",
        "caveat": "Captures reported reduction, not alcohol exposure level, baseline use, amount or abstinence. Period selectors are conditional and not independent exposures; blank/unchecked slots are not No.",
    },
    {
        "concept_id": "life_history_medical_insurance_history",
        "label": "Medical insurance status and first coverage year after age 16",
        "role": "e",
        "modules": ["HEALTHHISTORY"],
        "domain": "life-course healthcare access and socioeconomic context",
        "patterns": [r"hc025", r"hc025_1"],
        "question": "HC025/HC025_1",
        "unit": "insurance status and first post-16 coverage year",
        "values": "Questionnaire examples include urban employee/resident basic insurance, new rural cooperative medical insurance, free medical care and commercial insurance; HC025_1 asks first year after age 16 if insured.",
        "status": "official insurance examples and conditional year route reviewed; current-versus-ever wording and release coding require QA",
        "caveat": "The English stem asks 'Do you have' insurance while its negative response says never had insurance; preserve that wording inconsistency and do not infer continuous coverage or insurance type. HC025_1 follows Yes; year is not duration.",
    },
    {
        "concept_id": "life_history_sample_vital_status",
        "label": "Life History sample vital status (alive/deceased indicator)",
        "role": "p",
        "modules": ["SAMPLEINFORMATION"],
        "domain": "sample follow-up and mortality status",
        "patterns": [r"died"],
        "question": "Sample_Infor.dta: died",
        "unit": "binary release vital-status indicator",
        "values": "The official release note states that responded Life History samples are released and deceased persons can be identified in Sample_Infor.dta. No death date or cause is provided by this field.",
        "status": "official Life History release note and Codebook identity reviewed; authorized-release coding and observation window require QA",
        "caveat": "Metadata-only mortality endpoint candidate. This field also defines selection/survival status in the special survey and must not be interpreted as a population mortality rate, event time, cause of death, or a nationally representative outcome; no Life History sampling weight is provided. Do not publish participant vital status or Codebook distributions.",
    },
    {
        "concept_id": "life_history_education_level_history",
        "label": "Educational stages ever attended",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "early-life socioeconomic and educational context",
        "patterns": [r"e000s(?:[1-9]|1[0-2])"],
        "question": "E000",
        "unit": "12 multi-select education-stage indicators including a none option",
        "values": "Questionnaire options span home school, kindergarten, preschool, primary, middle, high, vocational, three-year college, four-year college, master's, PhD and none. Treat the stage checklist as one educational-history family; option 12 is a none-of-these marker, not an attainment level.",
        "status": "official questionnaire categories reviewed; multi-select authorized-release coding requires QA",
        "caveat": "Retrospective education history; does not by itself establish credential completion, duration, quality or age at attendance. Preserve the ErrorE000 consistency check and authorized-release routes; do not treat each selector slot as an independent exposure.",
    },
    {
        "concept_id": "life_history_literacy",
        "label": "Self-reported ability to read or write",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational and socioeconomic context",
        "patterns": [r"e001"],
        "question": "E001",
        "unit": "binary self-report",
        "values": "Questionnaire asks whether the respondent can read or write.",
        "status": "official question and eligibility route reviewed; authorized-release coding requires QA",
        "caveat": "Literacy is educational/social context, not a validated cognitive phenotype. The item is routed by E000 education selections, including the none category; retain the official denominator and missingness.",
    },
    {
        "concept_id": "life_history_cultural_revolution_school_disruption",
        "label": "School attendance and interruption during the Cultural Revolution",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "historical educational and political context",
        "patterns": [r"e002", r"e003(?:_[1-4])?", r"e003a"],
        "question": "E002–E003a",
        "unit": "cohort-restricted school attendance, closure longer than one month, conditional dates and reason for not attending",
        "values": "E002–E003a apply to respondents born 1946–1961 inclusive. E002 asks whether in school when the Cultural Revolution started in fall 1966; E003 records school closure lasting over one month and start/end year/month; E003a asks why the respondent was not in school at that time.",
        "status": "official birth-cohort eligibility and conditional routes reviewed; date/reason release coding requires QA",
        "caveat": "Cohort- and period-specific recalled school disruption, not a general political exposure. E003 date fields are conditional; E003a is skipped when E002=Yes. Preserve birth-cohort eligibility and do not interpret skipped fields as No.",
    },
    {
        "concept_id": "life_history_schooling_interruption",
        "label": "Interruption and return during a school stage",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational continuity and life-course context",
        "patterns": [r"e004", r"e005s(?:[1-8])"],
        "question": "E004/E005",
        "unit": "interruption gate and eight stage-specific multi-select indicators",
        "values": "E004 defines interruption as leaving school for at least one semester and later returning; ordinary gaps between school stages are explicitly excluded. E005 records stages affected: primary, middle, high, vocational, three-year college, four-year college, master's or PhD.",
        "status": "official interruption definition and follow-up route reviewed; checkbox storage requires QA",
        "caveat": "Retrospective education-continuity context; E005 follows E004=Yes. Do not conflate stage-transition gaps with interruptions or count stage slots as independent events; blank slots are not No.",
    },
    {
        "concept_id": "life_history_school_dormitory_experience",
        "label": "School-dormitory residence during primary through high school",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "childhood residential and schooling context",
        "patterns": [r"e010", r"e011s[1-3]"],
        "question": "E010/E011",
        "unit": "ever-lived-in-dormitory gate and three school-stage selectors",
        "values": "E010 asks whether the respondent lived in a school dormitory from primary through high school; the questionnaire includes residence with nearby relatives/friends in its description. E011 selects primary, middle and/or high school stages.",
        "status": "official housing definition and follow-up route reviewed; multi-select release coding requires QA",
        "caveat": "Retrospective schooling/residential-context proxy, not measured crowding, indoor air or a geographic exposure. E011 follows E010=Yes; retain the broad questionnaire definition and do not infer duration or living conditions.",
    },
    {
        "concept_id": "life_history_primary_school_attainment",
        "label": "Primary-school duration, completion and peer progression context",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational attainment and historical schooling context",
        "patterns": [r"e013(?:_1)?", r"e020", r"e021", r"e022"],
        "question": "E013/E020–E022",
        "unit": "last primary school's nominal duration, graduation, highest completed grade and recalled peer transition category",
        "values": "E013 distinguishes five-year, six-year and incomplete primary school (with E013_1 grade); E020 asks graduation; E021 highest grade completed; E022 asks the approximate share of classmates who entered middle school.",
        "status": "official questionnaire routes and Codebook identities reviewed; anomalous grade values and authorized-release coding require QA",
        "caveat": "E013 is the last primary school attended, not a standardized years-of-schooling measure. E021 is asked on the non-graduate route; E022 is a recalled peer-context category, not an individual transition or school-quality measure. Keep routed denominators and do not infer missing answers.",
    },
    {
        "concept_id": "life_history_primary_school_interruption_detail",
        "label": "Primary-school interruption duration and reported reasons",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational continuity and childhood socioeconomic context",
        "patterns": [r"e018", r"e019s(?:[1-9]|1[0-3])"],
        "question": "E018–E019",
        "unit": "interrupted semester count and 13 reason selectors",
        "values": "Reasons include health, tuition affordability, need for labor, family care, interest/family preference, school closure, moving, political reasons, military service, incarceration, famine and other.",
        "status": "official questionnaire says follow-up is routed by E005 primary-stage interruption; Codebook identities reviewed; checkbox storage requires QA",
        "caveat": "These are retrospective reasons for a primary-school interruption, not independent causal effects. E019 is multi-select; blank or unobserved option slots are not No. Avoid publishing free-text details or Codebook frequencies.",
    },
    {
        "concept_id": "life_history_middle_school_attainment",
        "label": "Middle-school completion, grade, peer progression and examination context",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational attainment and historical schooling context",
        "patterns": [r"e024a", r"e024", r"e031", r"e032", r"e033", r"e034[abc]"],
        "question": "E024/E024a/E031–E034c",
        "unit": "middle-school attendance count, graduation, E024 grade/school-length item with bilingual wording discrepancy, peer progression category and high-school entrance examination pathway",
        "values": "The Codebook labels E024 as TheHighestGrade and the English questionnaire asks the highest grade; its Chinese wording asks how many years the last middle school was structured for. E024a counts middle schools attended; E031–E032 capture graduation and completed grade; E033 is the recalled share entering high/vocational school; E034a–c ask whether an exam was required, taken and passed the cutoff.",
        "status": "official routes and Codebook identities reviewed; E024 bilingual wording discrepancy, conditional examination path and response coding require QA",
        "caveat": "Do not interpret E024 as a harmonized grade or school-duration measure until the bilingual wording and authorized-release coding are reconciled. The entrance-exam questions describe historical schooling context, not a standardized academic-performance test. Preserve E031–E032 skip logic and E034a/b conditional routing; E033 is recalled peer context, not individual attainment.",
    },
    {
        "concept_id": "life_history_middle_school_interruption_detail",
        "label": "Middle-school interruption duration and reported reasons",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational continuity and childhood socioeconomic context",
        "patterns": [r"e029", r"e030s(?:[1-9]|1[0-3])"],
        "question": "E029–E030",
        "unit": "interrupted semester count and 13 reason selectors",
        "values": "Reasons parallel the primary-school list and include health, tuition affordability, labor, family care, school closure, moving, political reasons, military service, incarceration, famine and other.",
        "status": "official questionnaire says follow-up is routed by E005 middle-stage interruption; Codebook identities reviewed; checkbox storage requires QA",
        "caveat": "Retrospective reasons for middle-school interruption, not independent causal effects. E030 is multi-select; blank or unobserved option slots are not No. Do not publish free-text details or Codebook frequencies.",
    },
    {
        "concept_id": "life_history_high_school_attendance_intensity",
        "label": "High-school attendance count, study mode and nominal duration",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational attainment and historical schooling context",
        "patterns": [r"e035a", r"e035e", r"e035"],
        "question": "E035a/E035e/E035",
        "unit": "number of high schools attended, full-time/part-time status in last school, and nominal program duration",
        "values": "E035a counts high schools; E035e asks whether the last high school was full-time or part-time; E035 asks the duration of that school's program.",
        "status": "official questionnaire scope and field identities reviewed; response coding and unusual duration values require QA",
        "caveat": "Retrospective report, not verified attendance records. E035a–E035 apply to respondents reporting high-school attendance. Do not equate nominal school duration with years completed or assume full-time status across all schools.",
    },
    {
        "concept_id": "life_history_high_school_interruption_detail",
        "label": "High-school interruption duration and reported reasons",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational continuity and childhood socioeconomic context",
        "patterns": [r"e040", r"e041s(?:[1-9]|1[0-3])"],
        "question": "E040–E041",
        "unit": "interrupted semester count and 13 reason selectors",
        "values": "Reason options cover health, tuition affordability, labor, family care or preference, school closure, moving, political reasons, military service, incarceration, famine and other.",
        "status": "official E005 high-school stage route and Codebook field identities reviewed; checkbox storage requires QA",
        "caveat": "Multi-select retrospective reasons, not independent causal estimates. Asked only when E005 marks a high-school interruption; unchecked/blank is not No. Do not expose free-text responses or Codebook frequencies.",
    },
    {
        "concept_id": "life_history_high_school_completion_and_exam_pathway",
        "label": "High-school graduation and college-entrance examination pathway",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational attainment and historical schooling context",
        "patterns": [r"e04[2-8]", r"e046a"],
        "question": "E042–E048",
        "unit": "graduation, completed grade, entrance-exam participation and count/year/track/cutoff, and recalled peer progression",
        "values": "E042/E043 record graduation and highest grade; E044–E047 describe college entrance examination history and cutoff category; E048 is the recalled share of high-school classmates entering three-/four-year college.",
        "status": "official conditional skip paths and Codebook field identities reviewed; category coding and historical comparability require QA",
        "caveat": "Examination pathway is historical context, not a standardized academic score. E043 follows non-graduation; E045–E047 follow E044=Yes. E048 is peer context, not the respondent's educational transition. Preserve each route and denominator.",
    },
    {
        "concept_id": "life_history_vocational_education_pathway",
        "label": "Vocational education mode, field and completion history",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational attainment and historical training context",
        "patterns": [r"e050a", r"e050b_type_[1-3]_", r"e050e_[1-3]_", r"e050f_[1-3]_", r"e050_[1-3]_", r"e051_[1-3]_", r"e054_[1-3]_", r"e055_[1-3]_", r"e056b_[2-5]_[1-3]_"],
        "question": "E050a/E050b type/E050e–E051/E054–E056b_5",
        "unit": "up to three listed vocational-school pathways, study mode, type/major, part-time status, program duration, graduation and diploma outcomes",
        "values": "The questionnaire distinguishes evening classes, self-study examination, correspondence, radio/TV university, formal school and other routes. Institution type and part-time status follow formal schooling; alternative routes have a separate major/duration/diploma sequence. Up to three vocational schools are represented in the structured fields.",
        "status": "official route logic and Codebook field identities reviewed; repeated-school sequence and authorized-release coding require QA",
        "caveat": "Do not collapse distinct study modes or treat a diploma as equivalent across routes without review. Fields are repeated by school slot; E050e/E050f/E051/E054/E055 follow formal-school route, while E056b fields follow specified nonformal routes. Free-text majors, school names and addresses are excluded.",
    },
    {
        "concept_id": "life_history_vocational_school_interruption_detail",
        "label": "Vocational-school interruption duration and reported reasons",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational continuity and socioeconomic context",
        "patterns": [r"e052", r"e053s(?:[1-9]|1[0-3])"],
        "question": "E052–E053",
        "unit": "interrupted semester count and 13 reason selectors",
        "values": "Reason options include health, tuition affordability, labor, care, interest/family preference, school closure, moving, political reasons, military service, incarceration, famine and other.",
        "status": "official E005 vocational-stage route and Codebook identities reviewed; multi-select storage requires QA",
        "caveat": "Asked only when E005 identifies a vocational-school interruption. Retrospective multi-select reasons are not causal estimates; blank options are not No. Do not publish free-text details or Codebook frequencies.",
    },
    {
        "concept_id": "life_history_three_year_college_pathway",
        "label": "Three-year college attendance, study route and completion history",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational attainment and historical training context",
        "patterns": [r"e057a", r"e057b_type_[1-2]_", r"e057e_[1-2]_", r"e057f_[1-2]_", r"e057g_[1-2]_", r"e058_[1-2]_", r"e059_[1-2]_", r"e062_[1-3]_", r"e063_[1-2]_", r"e064b_[2-5]_[1-2]_"],
        "question": "E057a/E057b route/E057e–E059/E062–E064b_5",
        "unit": "attendance count, up to two school route/type/major/duration records, historical worker-peasant-soldier status, graduation and diploma outcomes",
        "values": "Questionnaire differentiates formal school education from evening/self-study/correspondence/radio-TV/other routes. The worker-peasant-soldier question applies to attendance years 1971–1977. Formal-route type, part-time, major and nominal duration differ from the nonformal-route diploma sequence.",
        "status": "official questionnaire routes and Codebook field identities reviewed; repeated episode and authorized-release coding require QA",
        "caveat": "Keep study route distinct; do not equate diploma type or years across modes. E057e is cohort/time-specific. E062/E063 follow formal-route schooling; E064b fields follow the listed alternative routes. The E064b_1 open-text major is excluded.",
    },
    {
        "concept_id": "life_history_three_year_college_interruption_detail",
        "label": "Three-year college interruption duration and reported reasons",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational continuity and socioeconomic context",
        "patterns": [r"e060", r"e061s(?:[1-9]|1[0-3])"],
        "question": "E060–E061",
        "unit": "interrupted semester count and 13 reason selectors",
        "values": "Reason options parallel earlier schooling interruption items: health, tuition affordability, labor, family care or preference, school closure, moving, political reasons, military service, incarceration, famine and other.",
        "status": "official E005 three-year-college stage route and Codebook identities reviewed; checkbox storage requires QA",
        "caveat": "Asked only when E005 marks a three-year-college interruption. Reasons are retrospective multi-select context, not independent causal effects; blank options are not No.",
    },
    {
        "concept_id": "life_history_four_year_college_pathway",
        "label": "Four-year college attendance, study route and completion history",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational attainment and historical training context",
        "patterns": [r"e065a", r"e065b_type_[1-3]_", r"e065e_[1-3]_", r"e065f_[1-3]_", r"e065g_[1-3]_", r"e066_[1-3]_", r"e067_[1-3]_", r"e070_[1-3]_", r"e071_[1-3]_", r"e073b_[2-5]_[1-3]_"],
        "question": "E065a/E065b route/E065e–E067/E070–E073b_5",
        "unit": "attendance count, up to three degree records, admission-era marker, school type/major/duration, graduation and diploma outcomes",
        "values": "Questionnaire records study mode, institution type, major category and nominal program length by degree episode; for degrees attended 1971–1977 it asks whether the respondent was a worker-peasant-soldier student. Formal and alternative routes have distinct diploma follow-ups.",
        "status": "official questionnaire routes and Codebook identities reviewed; double/multiple degree instructions and authorized-release coding require QA",
        "caveat": "Respondents with double/multiple degrees were instructed to record two and answer separately; preserve degree-slot structure. E065e is restricted to the 1971–1977 period. E070/E071 and E073b are conditional by route; do not collapse credentials or treat school type as quality.",
    },
    {
        "concept_id": "life_history_four_year_college_interruption_detail",
        "label": "Four-year college interruption duration and reported reasons",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational continuity and socioeconomic context",
        "patterns": [r"e068", r"e069s(?:[1-9]|1[0-3])"],
        "question": "E068–E069",
        "unit": "interrupted semester count and 13 reason selectors",
        "values": "Reason options parallel earlier schooling interruption items and include health, affordability, labor, family care, school closure, moving, political reasons, military service, incarceration and famine.",
        "status": "official E005 four-year-college stage route and Codebook identities reviewed; checkbox storage requires QA",
        "caveat": "Asked only when E005 marks a four-year-college interruption. Retrospective multi-select reasons are not causal estimates; blank options are not No.",
    },
    {
        "concept_id": "life_history_masters_education_pathway",
        "label": "Master's program type, study route and diploma history",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational attainment and historical training context",
        "patterns": [r"e074a", r"e074b_[1-8]_1_", r"e074b_type_1_", r"e074b_type1_1_", r"e074_1_", r"e075_1_", r"e076_1_", r"e079_1_", r"e080_1_", r"e082b_[2-5]_1_"],
        "question": "E074a/E074b/E074–E080/E082b_2–E082b_5",
        "unit": "program count, start/end timing components, study mode, master's type/major, part-time status and conditional diploma outcomes",
        "values": "Questionnaire separates academic, professional and MBA/EMBA master's types; formal education has a major/program-length/part-time/diploma path while alternative study modes have a separate duration and diploma path.",
        "status": "official route and Codebook identities reviewed; single listed structured episode and authorized-release coding require QA",
        "caveat": "Do not combine master's type with study mode or diploma as equivalent credential measures. E074/E075/E076/E079/E080 follow formal-school route; E082b follows specified nonformal routes. E074b school names, free-text alternatives and addresses remain excluded.",
    },
    {
        "concept_id": "life_history_masters_education_interruption_detail",
        "label": "Master's program interruption duration and reported reasons",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational continuity and socioeconomic context",
        "patterns": [r"e077", r"e078s(?:[1-9]|1[0-3])"],
        "question": "E077–E078",
        "unit": "interrupted semester count and 13 reason selectors",
        "values": "Reason options cover health, tuition affordability, labor, family care/preferences, school closure, moving, political reasons, military service, incarceration, famine and other.",
        "status": "official E005 master's-stage route and Codebook identities reviewed; multi-select storage requires QA",
        "caveat": "Asked only when E005 marks a master's interruption. Retrospective multi-select reasons are not causal estimates; blank options are not No.",
    },
    {
        "concept_id": "life_history_phd_education_pathway",
        "label": "PhD program study route, major and diploma history",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational attainment and historical training context",
        "patterns": [r"e092a", r"e092b_[1-8]_1_", r"e092b_type_1_", r"e092_1_", r"e093_1_", r"e096_1_", r"e097_1_", r"e099b_[2-5]_1_"],
        "question": "E092a/E092b/E092–E093/E096–E097/E099b_2–E099b_5",
        "unit": "program count, start/end timing components, study mode, major, part-time status and conditional diploma outcomes",
        "values": "Questionnaire distinguishes formal education from evening classes, self-study, correspondence, radio/TV university and other routes; diploma duration/type details are route-specific.",
        "status": "official questionnaire routes and Codebook field identities reviewed; repeated-program structure and authorized-release coding require QA",
        "caveat": "Preserve the E092a program count and E092b episode structure. E092/E093/E096/E097 apply to the formal route; E099b follows specified alternative routes. Do not equate program count, diploma or duration with verified attainment. School names, locations and open text are excluded.",
    },
    {
        "concept_id": "life_history_phd_education_interruption_detail",
        "label": "PhD program interruption duration and reported reasons",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational continuity and socioeconomic context",
        "patterns": [r"e094", r"e095s(?:[1-9]|1[0-3])"],
        "question": "E094–E095",
        "unit": "interrupted semester count and 13 reason selectors",
        "values": "Reason options parallel other education-stage interruptions: health, affordability, labor, family care, school closure, moving, political reasons, military service, incarceration, famine and other.",
        "status": "official E005 PhD-stage route and Codebook field identities reviewed; multi-select storage requires QA",
        "caveat": "Asked only when E005 marks a PhD interruption. Retrospective multi-select reasons are not causal estimates; blank options are not No.",
    },
    {
        "concept_id": "life_history_primary_education_continuation_barriers",
        "label": "Reported reasons for not continuing education after primary school",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational opportunity and socioeconomic context",
        "patterns": [r"e100as(?:[1-9]|1[0-3])"],
        "question": "E100a",
        "unit": "13 multi-select reasons conditional on primary school being highest education",
        "values": "Questionnaire options include not entering middle school, expected barriers to later schooling, distance, tuition, family labor/care, political or health reasons, lack of interest, Cultural Revolution school closure/sent-down experience, famine and other.",
        "status": "official highest-education route and category identities reviewed; checkbox storage requires QA",
        "caveat": "Asked only when primary school is the highest reported education. Reasons are retrospective self-reported barriers, not causal effects or current exposures; blank options are not No. Do not publish free-text details or Codebook frequencies.",
    },
    {
        "concept_id": "life_history_middle_education_continuation_barriers",
        "label": "Reported reasons for not continuing education after middle school",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational opportunity and socioeconomic context",
        "patterns": [r"e100bs(?:[1-9]|1[0-3])"],
        "question": "E100b",
        "unit": "13 multi-select reasons conditional on middle school being highest education",
        "values": "Options cover not entering high/vocational school or later college, distance, tuition, family labor/care, political or health reasons, disinterest, Cultural Revolution disruption, famine and other.",
        "status": "official highest-education route and category identities reviewed; checkbox storage requires QA",
        "caveat": "Asked only when middle school is the highest reported education. These are recalled barriers, not causal effects; blank options are not No. Preserve the stage-specific denominator and do not release free text or Codebook frequencies.",
    },
    {
        "concept_id": "life_history_high_education_continuation_barriers",
        "label": "Reported reasons for not continuing education after high school",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational opportunity and socioeconomic context",
        "patterns": [r"e100cs(?:[1-9]|1[0-3])"],
        "question": "E100c",
        "unit": "13 multi-select reasons conditional on high school being highest education",
        "values": "Options include not entering further education, perceived utility, distance, tuition, family labor/care, political or health reasons, disinterest, Cultural Revolution disruption, famine and other.",
        "status": "official highest-education route and category identities reviewed; checkbox storage requires QA",
        "caveat": "Asked only when high school is the highest reported education. These are recalled barriers, not causal effects; blank options are not No. Preserve the stage-specific denominator and do not release free text or Codebook frequencies.",
    },
    {
        "concept_id": "life_history_adult_education_types",
        "label": "Adult education types ever attended",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "adult education and life-course training",
        "patterns": [r"e102s[1-9]"],
        "question": "E102",
        "unit": "nine multi-select indicators, including a none option",
        "values": "Types include literacy class, evening class, career training of at least 10 days (apprenticeships excluded), accelerated course, radio/TV university, correspondence, self-study examination, other and none.",
        "status": "official item wording and type definitions reviewed; multi-select authorized-release coding requires QA",
        "caveat": "E102 is an ever-attendance checklist, not duration, credential or quality. The none option is not an educational activity and must not be combined with attended types; unchecked is not No without release-specific validation.",
    },
    {
        "concept_id": "life_history_adult_literacy_class",
        "label": "Adult literacy-class timing and duration",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "adult education and life-course training",
        "patterns": [r"e103", r"e104_[1-3]"],
        "question": "E103–E104",
        "unit": "start year and attended duration in years/months/days",
        "values": "Questionnaire asks start year and total time attending a literacy class.",
        "status": "official E102 literacy-class route and Codebook fields reviewed; duration component ranges require QA",
        "caveat": "Only asked of literacy-class attendees. Preserve the separate time units; do not combine components or infer literacy gains, current skill or credential.",
    },
    {
        "concept_id": "life_history_adult_evening_class",
        "label": "Adult evening-class attendance and diploma history",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "adult education and life-course training",
        "patterns": [r"e105", r"e106a_[1-3]_", r"e106c_[1-3]_", r"e106d_[1-3]_", r"e106e_[1-3]_", r"e106f_[1-3]_"],
        "question": "E105/E106a/E106c–E106f",
        "unit": "number of evening classes and up to three episodes with start year, duration, diploma indicator/year/type",
        "values": "Follow-up records up to three evening-class episodes. Diploma details are conditional on receiving a diploma; the questionnaire's open-text major is not included.",
        "status": "official E102 route, repeated episode count and diploma skip path reviewed; coding requires QA",
        "caveat": "Episode slots are repeated records, not separate independent concepts. E106d gates diploma year/type; missing follow-ups must not be interpreted as no diploma. Free-text major and institution identifiers are excluded.",
    },
    {
        "concept_id": "life_history_career_training_history",
        "label": "Adult career-training timing, duration and payer",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "adult education and occupational training context",
        "patterns": [r"e107", r"e107a_(?:[1-9]|1[0-9]|2[0-4])_", r"e107b_[1-3]_(?:[1-9]|1[0-9]|2[0-4])_", r"e107c_(?:[1-9]|1[0-9]|2[0-4])_"],
        "question": "E107/E107a–E107c",
        "unit": "count and up to 24 repeated training records with year, duration components and payer",
        "values": "The preceding E102 item defines career training as lasting at least 10 days and excludes apprenticeships. E107 records the count; each record includes year, duration in years/months/days and payer (work unit, self or other).",
        "status": "official E102 threshold, 24-slot Codebook structure and item definitions reviewed; slot identity and authorized-release coding require QA",
        "caveat": "Repeated slots are not independent exposures and a 10-day threshold comes from E102 wording. Preserve duration units and payer categories; no participant-level amounts, free text or Codebook frequencies are published.",
    },
    {
        "concept_id": "life_history_accelerated_education_course",
        "label": "Accelerated-education course count and average duration",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "adult education and life-course training",
        "patterns": [r"e108", r"e109_[1-3]"],
        "question": "E108–E109",
        "unit": "course count and average duration in years/months/days",
        "values": "Questionnaire records number of accelerated courses and average duration per course in separate units.",
        "status": "official E102 route and Codebook fields reviewed; duration component ranges require QA",
        "caveat": "Only asked of attendees. Preserve years/months/days separately; do not infer educational attainment, skill gains or credential from course attendance.",
    },
    {
        "concept_id": "life_history_radio_television_university",
        "label": "Radio/television university attendance and diploma history",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "adult education and life-course training",
        "patterns": [r"e110a", r"e110_[1-2]_", r"e112_[1-2]_", r"e113_[1-2]_", r"e114_[1-2]_", r"e115_[1-2]_"],
        "question": "E110a/E110/E112–E115",
        "unit": "count and up to two episodes with start year, duration and conditional diploma year/type",
        "values": "Separate episode slots record start year, study duration, diploma receipt and conditional diploma year/type. Major is open text and not mapped.",
        "status": "official E102 route, two-slot structure and diploma skip path reviewed; coding requires QA",
        "caveat": "Repeated slots are not independent exposures. E113 gates diploma year/type; do not interpret missing follow-ups as no credential or compare diploma categories as equivalent attainment without validation.",
    },
    {
        "concept_id": "life_history_correspondence_education",
        "label": "Correspondence-education attendance and diploma history",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "adult education and life-course training",
        "patterns": [r"e116a", r"e116_[1-3]_", r"e118_[1-3]_", r"e119_[1-3]_", r"e120_[1-3]_", r"e121_[1-3]_"],
        "question": "E116a/E116/E118–E121",
        "unit": "count and up to three episodes with start year, duration and conditional diploma year/type",
        "values": "Questionnaire records start year, years of study, diploma status and conditional diploma year/type for each correspondence-education episode. Major is open text and not mapped.",
        "status": "official E102 route, three-slot structure and diploma skip path reviewed; coding requires QA",
        "caveat": "Keep correspondence education distinct from other adult-education modes. Episode slots are repeated records, not independent exposures; E119 gates E120/E121.",
    },
    {
        "concept_id": "life_history_self_study_examination",
        "label": "Self-study examination attendance and diploma history",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "adult education and life-course training",
        "patterns": [r"e122a", r"e122_[1-3]_", r"e124_[1-3]_", r"e125_[1-3]_", r"e126_[1-3]_", r"e127_[1-3]_"],
        "question": "E122a/E122/E124–E127",
        "unit": "count and up to three episodes with start year, duration and conditional diploma year/type",
        "values": "Questionnaire records start year, years spent in self-study examination, diploma receipt and conditional diploma year/type. Major is open text and not mapped.",
        "status": "official E102 route, three-slot structure and diploma skip path reviewed; coding requires QA",
        "caveat": "Keep self-study examination distinct from formal schooling and other adult-education modes. Repeated episodes are not independent; E125 gates diploma year/type.",
    },
    {
        "concept_id": "life_history_other_adult_education",
        "label": "Other adult-education attendance, duration and diploma history",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "adult education and life-course training",
        "patterns": [r"e128a", r"e129_[1-4]_", r"e130_[1-3]_[1-4]_", r"e131_[1-4]_", r"e132_[1-4]_"],
        "question": "E128a–E132",
        "unit": "count and up to four episodes with start year, duration and conditional diploma status/type",
        "values": "The questionnaire calls these other education and records start year, duration in years/months/days and diploma receipt/type. The education names are open text and are not mapped.",
        "status": "official E102 route, four-slot Codebook structure and diploma skip path reviewed; episode correspondence requires QA",
        "caveat": "Because course identity is open text, do not pool these episodes into one standardized course type or infer credential level without a validated linkage. E131 gates E132. Names and free text remain excluded.",
    },
    {
        "concept_id": "life_history_skill_certificate_indicator",
        "label": "Ever received a vocational skill certificate",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "occupational training and qualification context",
        "patterns": [r"e133"],
        "question": "E133",
        "unit": "binary ever-received indicator",
        "values": "Question asks whether the respondent has ever received any skill certificate.",
        "status": "official item and yes/no skip route reviewed; certificate identity/year linkage requires separate QA",
        "caveat": "This is a self-reported ever indicator, not a particular certificate, standardized competence or current license. Certificate names are open text; E134 year slots are not mapped until certificate-to-year identity can be validated.",
    },
    {
        "concept_id": "life_history_education_gap_activity_context",
        "label": "Activities reported during gaps between repeated education episodes",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational continuity and life-course context",
        "patterns": [r"e011d_[1-3]_s(?:[1-9]|1[01])", r"e011h_[1-2]_s(?:[1-9]|1[01])", r"e011l_[1-2]_s(?:[1-9]|1[01])", r"e012d_[1-5]_s(?:[1-9]|1[01])", r"e024d_[1-3]_s(?:[1-9]|1[01])", r"e035d_[1-2]_s(?:[1-9]|1[01])", r"e050d_[1-2]_s(?:[1-9]|1[01])", r"e057d_1_s(?:[1-9]|1[01])", r"e065d_[1-2]_s(?:[1-9]|1[01])"],
        "question": "E011d/E011h/E011l/E012d/E024d/E035d/E050d/E057d/E065d",
        "unit": "242 repeated multi-select activity slots across preschool, primary, middle, high, vocational and college episode gaps",
        "values": "Questionnaire activity options cover work, inactivity, illness, childbirth, family care, leisure/travel, training, incarceration and other. The gap questions are routed when the interval between repeated same-stage education episodes exceeds seven months.",
        "status": "official questionnaire gap definitions and Codebook repeated-slot identities reviewed; category storage and route-specific missingness require QA",
        "caveat": "These describe activities during recalled gaps between same-stage education episodes, not general life history or independent causal exposures. Repeated episode slots are nested and not independent; preserve stage and route. Other is not interpreted; open-text details and Codebook frequencies are excluded.",
    },
    {
        "concept_id": "life_history_education_gap_without_other_schooling",
        "label": "Reported absence of other education during long gaps between same-stage episodes",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational continuity and life-course context",
        "patterns": [r"e011[ck]_[1-3]_", r"e012c_[1-5]_", r"e024c_[1-3]_", r"e035c_[1-2]_", r"e050c_[1-2]_", r"e057c_1_", r"e065c_[1-2]_"],
        "question": "E011c/E011k/E012c/E024c/E035c/E050c/E057c/E065c",
        "unit": "20 routed yes/no gap questions across education stages",
        "values": "Question asks whether the respondent left education during an unreported gap between the former episode's end and the next episode's start. Asked only for intervals meeting the questionnaire's greater-than-seven-month rule.",
        "status": "official gap routing and Codebook field identities reviewed; yes/no storage and stage-specific routes require QA",
        "caveat": "This is a retrospective gap-status indicator, not school dropout as defined by E004/E005 and not proof of no informal learning. Preserve episode/stage context; do not treat skipped gap checks as No.",
    },
    {
        "concept_id": "life_history_early_education_episode_counts",
        "label": "Counts of private traditional schooling, kindergarten, preschool and primary-school episodes",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "early-life educational context",
        "patterns": [r"e011a", r"e011e", r"e011i", r"e012a"],
        "question": "E011a/E011e/E011i/E012a",
        "unit": "reported counts of private traditional-school, kindergarten, preschool and primary-school episodes",
        "values": "The questionnaire identifies E011a as 私塾 (private traditional schooling), E011e as kindergarten, E011i as preschool and E012a as primary school; each asks the number attended before looping through the episode history.",
        "status": "official questionnaire labels and Codebook field identities reviewed; count coding requires authorized-release QA",
        "caveat": "Do not interpret E011a as modern home-schooling; its Chinese questionnaire label is 私塾. Counts do not measure duration, quality, enrollment continuity or geographic setting. Keep the four institution types distinct.",
    },
    {
        "concept_id": "life_history_education_episode_timing",
        "label": "Reported start and end periods across repeated education episodes",
        "role": "e",
        "modules": ["EDUCATIONHISTORY"],
        "domain": "educational life-course chronology",
        "patterns": [r"e011b_[1-8]_[1-4]_", r"e011f_[1-8]_[1-3]_", r"e011j_[1-8]_[1-2]_", r"e012b_[1-8]_[1-6]_", r"e024b_[1-8]_[1-4]_", r"e035b_[1-8]_[1-3]_", r"e050b_[1-8]_[1-3]_", r"e057b_[1-8]_[1-2]_", r"e065b_[1-8]_[1-3]_"],
        "question": "E011b/E011f/E011j/E012b/E024b/E035b/E050b/E057b/E065b",
        "unit": "240 start/end period components across 30 repeated episode slots and nine schooling stages",
        "values": "Each school record asks start and end time using year and one of month, season or half-year. Interviewers are instructed to ask for a range when exact year is not recalled and enter a midpoint.",
        "status": "official episode structure, approximate-recall instruction and Codebook timing identities reviewed; alternative precision and episode linkage require QA",
        "caveat": "This is recalled schooling chronology, not exact dates, education duration or environmental dose. Month/season/half-year fields represent alternative precision rather than additive components; repeated records are nested. Do not derive total years or age at exposure without validated date reconciliation. School names and addresses remain excluded.",
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
            expected.setdefault(module, set()).add(code)

    codes = [(x["module"], x["code"]) for x in rows]
    if len(codes) != len(set(codes)):
        raise ValueError("A source field was assigned to multiple Life History concepts")
    if any("OBS:" in " ".join(row.values()) or re.search(r"\b\d[,.]?\d*%", row["value_labels"]) for row in rows):
        raise ValueError("Codebook frequencies/statistics must not be copied into atlas metadata")
    return rows, summary


def build_sibling_module_coverage(rows: list[dict]) -> list[dict]:
    """Give every Codebook B-family field a mapped or explicit non-E/P disposition."""
    mapped = {row["code"]: row for row in rows if row["module"] == "FAMILYINFORMATION"}
    fields = read_codebook_fields()
    ledger: list[dict] = []
    for (module, code), label in sorted(fields.items()):
        if module != "FAMILYINFORMATION" or not re.fullmatch(r"b\d+.*", code, re.I):
            continue
        row = mapped.get(code)
        if row:
            disposition = "mapped_candidate"
            concept_id = row["concept_id"]
            rationale = row["caveat"]
        elif re.fullmatch(r"b4_4_\d+_", code, re.I):
            disposition = "deferred_relative_status"
            concept_id = ""
            rationale = "Roster status for a sibling; questionnaire provides no event date in this field. Keep out of E/P pending a defined family-context estimand."
        elif re.fullmatch(r"b4_5_\d+_", code, re.I):
            disposition = "deferred_relative_attainment"
            concept_id = ""
            rationale = "Sibling's highest completed education has no timing relative to respondent childhood and is not the respondent's phenotype; assess only under a justified family-context estimand."
        else:
            raise ValueError(f"Unmapped sibling Codebook field has no disposition: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": disposition, "concept_id": concept_id,
                       "rationale": rationale,
                       "questionnaire_source": "sources_official/CHARLS_Life_History_Questionnaire.pdf",
                       "codebook_source": "sources_official/CHARLS_Life_History_codebook.pdf"})
    return ledger


def build_parent_module_coverage(rows: list[dict]) -> list[dict]:
    """Disposition every structured A-section parent/family-background Codebook field."""
    mapped = {row["code"]: row for row in rows if row["module"] == "FAMILYINFORMATION"}
    fields = read_codebook_fields()
    ledger: list[dict] = []
    for (module, code), label in sorted(fields.items()):
        if module != "FAMILYINFORMATION" or not re.match(r"a\d", code, re.I):
            continue
        row = mapped.get(code)
        if row:
            disposition, concept_id, rationale = "mapped_candidate", row["concept_id"], row["caveat"]
        elif code in {"a4a", "a4b"}:
            disposition, concept_id = "deferred_caregiver_identity", ""
            rationale = "Caregiver identity is a route-defining relationship category, not an E/P measure; retain only as metadata until a target estimand needs it."
        elif re.fullmatch(r"a5[abcdef]", code, re.I):
            disposition, concept_id = "deferred_parent_birth_year", ""
            rationale = "Parent birth year is background/timing metadata, not a stand-alone exposure; event-age derivation requires approved linkage and validation."
        else:
            raise ValueError(f"Unmapped parent/family-background Codebook field has no disposition: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": disposition, "concept_id": concept_id,
                       "rationale": rationale,
                       "questionnaire_source": "sources_official/CHARLS_Life_History_Questionnaire.pdf",
                       "codebook_source": "sources_official/CHARLS_Life_History_codebook.pdf"})
    return ledger


def build_historical_family_class_coverage(rows: list[dict]) -> list[dict]:
    """Confirm every structured 2014 C5 family-class option field maps exactly once."""
    pattern = re.compile(r"c5(?:[a-f])?s\d+", re.I)
    mapped = {row["code"]: row for row in rows if row["module"] == "WEALTHHISTORY"}
    fields = read_codebook_fields()
    ledger: list[dict] = []
    for (module, code), label in sorted(fields.items()):
        if module != "WEALTHHISTORY" or not pattern.fullmatch(code):
            continue
        row = mapped.get(code)
        if not row or row["concept_id"] != "life_history_historical_family_class_background":
            raise ValueError(f"Historical family-class Codebook field is not mapped: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": "mapped_candidate", "concept_id": row["concept_id"],
                       "questionnaire_item": row["questionnaire_item"],
                       "questionnaire_source": row["questionnaire_source"],
                       "codebook_source": row["codebook_source"]})
    return ledger


def build_parent_social_context_coverage(rows: list[dict]) -> list[dict]:
    """Track all parent/caregiver selector and ethnicity-category slots in C1_g1-g3."""
    pattern = re.compile(r"c1_g[13]s\d+|c1_g2s\d+|c1_g2_1_\d+_", re.I)
    target_ids = {
        "life_history_parental_party_membership_context",
        "life_history_parental_minority_ethnicity_context",
        "life_history_parental_minority_group_context",
        "life_history_parental_religious_context",
    }
    mapped = {row["code"]: row for row in rows
              if row["module"] == "FAMILYINFORMATION" and row["concept_id"] in target_ids}
    fields = read_codebook_fields()
    ledger: list[dict] = []
    for (module, code), label in sorted(fields.items()):
        if module != "FAMILYINFORMATION" or not pattern.fullmatch(code):
            continue
        row = mapped.get(code)
        if row is None:
            raise ValueError(f"C1 parent/caregiver social-context field lacks disposition: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": "mapped_candidate", "concept_id": row["concept_id"],
                       "questionnaire_item": row["questionnaire_item"], "rationale": row["caveat"],
                       "questionnaire_source": row["questionnaire_source"],
                       "codebook_source": row["codebook_source"]})
    if len(ledger) != 36:
        raise ValueError(f"Expected 36 C1 parent/caregiver social-context fields; found {len(ledger)}")
    return ledger


def build_parent_employment_coverage(rows: list[dict]) -> list[dict]:
    """Check all structured C1/C2 caregiver work fields and exclude write-in occupation text."""
    patterns = [re.compile(x, re.I) for x in (r"c1_[ab][12]", r"c2_[ab](?:_1)?")]
    concept_ids = {
        "life_history_guardian_employment_context",
        "life_history_childhood_guardian_occupation",
    }
    mapped = {row["code"]: row for row in rows
              if row["module"] == "FAMILYINFORMATION" and row["concept_id"] in concept_ids}
    fields = read_codebook_fields()
    ledger = []
    for (module, code), label in sorted(fields.items()):
        if module != "FAMILYINFORMATION" or not any(p.fullmatch(code) for p in patterns):
            continue
        row = mapped.get(code)
        if row is None:
            raise ValueError(f"C1/C2 structured caregiver work field lacks disposition: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": "mapped_candidate", "concept_id": row["concept_id"],
                       "questionnaire_item": row["questionnaire_item"], "rationale": row["caveat"],
                       "questionnaire_source": row["questionnaire_source"],
                       "codebook_source": row["codebook_source"]})
    if len(ledger) != 8:
        raise ValueError(f"Expected 8 structured C1/C2 caregiver work fields; found {len(ledger)}")
    if any(re.match(r"c1_[ab]2_\d", row["code"], re.I) for row in ledger):
        raise ValueError("Occupation free-text detail fields must not enter the structured catalog")
    return ledger


def build_sensitive_history_coverage(rows: list[dict]) -> list[dict]:
    """Track E7/E8 and G1/G2 without ever importing Codebook frequencies or participant values."""
    ids = {"life_history_childhood_romantic_relationship",
           "life_history_childhood_police_custody_and_charge"}
    mapped = {row["code"]: row for row in rows
              if row["module"] == "FAMILYINFORMATION" and row["concept_id"] in ids}
    fields = read_codebook_fields()
    ledger = []
    for code in ("e7", "e8", "g1", "g2"):
        label = fields.get(("FAMILYINFORMATION", code))
        row = mapped.get(code)
        if not label or row is None:
            raise ValueError(f"Sensitive childhood-history Codebook field lacks disposition: {code}")
        ledger.append({"module": "FAMILYINFORMATION", "code": code, "codebook_label": label,
                       "disposition": "mapped_metadata_only", "concept_id": row["concept_id"],
                       "questionnaire_item": row["questionnaire_item"], "rationale": row["caveat"],
                       "questionnaire_source": row["questionnaire_source"],
                       "codebook_source": row["codebook_source"]})
    return ledger


def build_family_information_module_coverage(rows: list[dict]) -> list[dict]:
    """Require one explicit catalog or non-E/P disposition for every Family Information Codebook field."""
    mapped = {row["code"]: row for row in rows if row["module"] == "FAMILYINFORMATION"}
    fields = read_codebook_fields()
    ledger = []
    for (module, code), label in sorted(fields.items()):
        if module != "FAMILYINFORMATION":
            continue
        row = mapped.get(code)
        if row:
            disposition, concept_id, rationale = "mapped_candidate", row["concept_id"], row["caveat"]
        elif code in {"id", "householdid", "communityid"}:
            disposition, concept_id = "excluded_linkage_key", ""
            rationale = "Person, household, or community linkage key. Never publish key values; retain only in controlled analysis joins when authorized and required."
        elif code == "versionid":
            disposition, concept_id = "excluded_release_metadata", ""
            rationale = "Release/version bookkeeping metadata, not a respondent exposure or phenotype."
        elif code in {"a4a", "a4b"}:
            disposition, concept_id = "deferred_caregiver_identity", ""
            rationale = "Caregiver identity is a route-defining relationship category, not a stand-alone E/P measure."
        elif re.fullmatch(r"a5[abcdef]", code, re.I):
            disposition, concept_id = "deferred_parent_birth_year", ""
            rationale = "Parent birth year is timing/background metadata; event-age derivation requires an explicit estimand and authorized linkage."
        elif re.fullmatch(r"b4_4_\d+_", code, re.I):
            disposition, concept_id = "deferred_relative_status", ""
            rationale = "Sibling roster status; no timing/event definition in the item. Keep out of E/P pending a justified family-context estimand."
        elif re.fullmatch(r"b4_5_\d+_", code, re.I):
            disposition, concept_id = "deferred_relative_attainment", ""
            rationale = "Sibling educational attainment has no timing relative to respondent childhood and is not respondent phenotype; retain only if a family-context estimand justifies it."
        else:
            raise ValueError(f"FAMILYINFORMATION Codebook field has no explicit disposition: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": disposition, "concept_id": concept_id, "rationale": rationale,
                       "questionnaire_source": "sources_official/CHARLS_Life_History_Questionnaire.pdf",
                       "codebook_source": "sources_official/CHARLS_Life_History_codebook.pdf"})
    codes = [row["code"] for row in ledger]
    if len(ledger) != 473 or len(codes) != len(set(codes)):
        raise ValueError(f"FAMILYINFORMATION coverage not exhaustive/unique: rows={len(ledger)}, unique={len(set(codes))}")
    return ledger


def build_residence_transition_coverage(rows: list[dict]) -> list[dict]:
    """Audit T001 entry/exit timing slots for up to 25 linked residence episodes."""
    patterns = [re.compile(x, re.I) for x in
                (r"t001a_\d+_", r"t001a_[1-4]_\d+_", r"t001b_\d+_", r"t001b_[1-4]_\d+_")]
    mapped = {row["code"]: row for row in rows if row["module"] == "RESIDENCE"
              and row["concept_id"] == "life_history_residential_episode_timing"}
    fields = read_codebook_fields()
    ledger = []
    for (module, code), label in sorted(fields.items()):
        if module != "RESIDENCE" or not any(p.fullmatch(code) for p in patterns):
            continue
        row = mapped.get(code)
        if row is None:
            raise ValueError(f"T001 residence timing Codebook field lacks mapping: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": "mapped_candidate", "concept_id": row["concept_id"],
                       "questionnaire_item": row["questionnaire_item"], "rationale": row["caveat"],
                       "questionnaire_source": row["questionnaire_source"],
                       "codebook_source": row["codebook_source"]})
    if len(ledger) != 250:
        raise ValueError(f"Expected 250 T001 timing fields; found {len(ledger)}")
    return ledger


def build_gap_migration_reason_coverage(rows: list[dict]) -> list[dict]:
    """Audit all T003e reason-option fields separately from T003c residence-exit reasons."""
    mapped = {row["code"]: row for row in rows if row["module"] == "RESIDENCE"
              and row["concept_id"] == "life_history_between_residence_migration_reasons"}
    fields = read_codebook_fields()
    ledger = []
    for (module, code), label in sorted(fields.items()):
        if module != "RESIDENCE" or not re.fullmatch(r"t003e_\d+_s\d+", code, re.I):
            continue
        row = mapped.get(code)
        if row is None:
            raise ValueError(f"T003e gap migration reason Codebook field lacks mapping: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": "mapped_candidate", "concept_id": row["concept_id"],
                       "questionnaire_item": row["questionnaire_item"], "rationale": row["caveat"],
                       "questionnaire_source": row["questionnaire_source"],
                       "codebook_source": row["codebook_source"]})
    if len(ledger) != 169:
        raise ValueError(f"Expected 169 T003e reason fields; found {len(ledger)}")
    return ledger


def build_residence_module_coverage(rows: list[dict]) -> list[dict]:
    """Give all 935 Residence Codebook fields exactly one mapped, deferred, or excluded disposition."""
    mapped = {row["code"]: row for row in rows if row["module"] == "RESIDENCE"}
    fields = read_codebook_fields()
    ledger = []
    demographic = {"rbirthyear", "rbirthmonth", "rbirthid", "rbirthid_1", "rbirthid_2", "rgender"}
    linkage = {"id", "householdid", "communityid"}
    proxy = {"ac040", "ac041", "ac042"}
    for (module, code), label in sorted(fields.items()):
        if module != "RESIDENCE":
            continue
        row = mapped.get(code)
        if row:
            disposition, concept_id, rationale = "mapped_candidate", row["concept_id"], row["caveat"]
        elif code in linkage:
            disposition, concept_id = "excluded_linkage_key", ""
            rationale = "Person/household/community linkage key. Never publish key values; use only in controlled authorized joins when required."
        elif code == "versionid":
            disposition, concept_id = "excluded_release_metadata", ""
            rationale = "Release/version bookkeeping metadata, not an E/P measure."
        elif code in demographic:
            disposition, concept_id = "deferred_respondent_demographic", ""
            rationale = "Respondent birth/gender or ID-card verification data are demographic/linkage metadata, not standalone E/P measures; protect values and use only for a justified estimand."
        elif code in proxy:
            disposition, concept_id = "excluded_interview_proxy_metadata", ""
            rationale = "Module respondent/proxy identity and relationship metadata, not an E/P measure."
        elif re.fullmatch(r"t002_\d+_|t002_psu_\d+_|t002e(?:_\d+){1,2}_", code, re.I):
            disposition, concept_id = "excluded_geographic_location_metadata", ""
            rationale = "Residence county/location or between-county region code. Location values are excluded from the public site; the official release note warns t002_psu codes cannot be compared directly with PSU.dta. No geographic linkage is performed."
        else:
            raise ValueError(f"RESIDENCE Codebook field has no explicit disposition: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": disposition, "concept_id": concept_id, "rationale": rationale,
                       "questionnaire_source": "sources_official/CHARLS_Life_History_Questionnaire.pdf",
                       "codebook_source": "sources_official/CHARLS_Life_History_codebook.pdf"})
    codes = [row["code"] for row in ledger]
    if len(ledger) != 935 or len(codes) != len(set(codes)):
        raise ValueError(f"RESIDENCE coverage not exhaustive/unique: rows={len(ledger)}, unique={len(set(codes))}")
    return ledger


def build_wealth_history_module_coverage(rows: list[dict]) -> list[dict]:
    """Give all 440 Wealth History Codebook fields exactly one mapped or metadata-only disposition."""
    mapped = {row["code"]: row for row in rows if row["module"] == "WEALTHHISTORY"}
    fields = read_codebook_fields()
    ledger = []
    linkage = {"id", "householdid", "communityid"}
    interview = {"hs001", "hs002", "hs003"}
    for (module, code), label in sorted(fields.items()):
        if module != "WEALTHHISTORY":
            continue
        row = mapped.get(code)
        if row:
            disposition, concept_id, rationale = "mapped_candidate", row["concept_id"], row["caveat"]
        elif code in linkage:
            disposition, concept_id = "excluded_linkage_key", ""
            rationale = "Person/household/community linkage key. Never publish values; use only in authorized controlled joins when required."
        elif code in interview:
            disposition, concept_id = "excluded_interview_proxy_metadata", ""
            rationale = "Module respondent/facilitator/proxy identity and relationship metadata, not an E/P measure."
        elif code == "fs012s":
            disposition, concept_id = "excluded_household_route_metadata", ""
            rationale = "First household respondent's inheritance status controls the second respondent's pre-marriage route; it is routing metadata, not the second respondent's own inheritance outcome."
        elif code == "versionid":
            disposition, concept_id = "excluded_release_metadata", ""
            rationale = "Release/version bookkeeping metadata, not an E/P measure."
        else:
            raise ValueError(f"WEALTHHISTORY Codebook field has no explicit disposition: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": disposition, "concept_id": concept_id, "rationale": rationale,
                       "questionnaire_source": "sources_official/CHARLS_Life_History_Questionnaire.pdf",
                       "codebook_source": "sources_official/CHARLS_Life_History_codebook.pdf"})
    codes = [row["code"] for row in ledger]
    if len(ledger) != 440 or len(codes) != len(set(codes)):
        raise ValueError(f"WEALTHHISTORY coverage not exhaustive/unique: rows={len(ledger)}, unique={len(set(codes))}")
    return ledger


def build_health_history_module_coverage(rows: list[dict]) -> list[dict]:
    """Disposition all 86 Codebook health-history fields, including existing childhood outcomes."""
    mapped = {row["code"]: row for row in rows if row["module"] == "HEALTHHISTORY"}
    fields = read_codebook_fields()
    ledger = []
    linkage = {"id", "householdid", "communityid"}
    interview = {"hc061", "hc062", "hc063"}
    for (module, code), label in sorted(fields.items()):
        if module != "HEALTHHISTORY":
            continue
        row = mapped.get(code)
        if row:
            disposition, concept_id, rationale = "mapped_candidate", row["concept_id"], row["caveat"]
        elif code in linkage:
            disposition, concept_id = "excluded_linkage_key", ""
            rationale = "Person/household/community linkage key. Never publish values; use only in authorized controlled joins when required."
        elif code in interview:
            disposition, concept_id = "excluded_interview_proxy_metadata", ""
            rationale = "Section respondent/proxy identity or relationship metadata, not an E/P measure."
        elif code == "versionid":
            disposition, concept_id = "excluded_release_metadata", ""
            rationale = "Release/version bookkeeping metadata, not an E/P measure."
        elif code == "hc023s96":
            disposition, concept_id = "excluded_none_option_metadata", ""
            rationale = "Shared 'none of the above' option for the HC023 health-behavior-change checklist; it is not an independent exposure. The four specific HC023 behavior selectors remain mapped with their HC024 age-period fields."
        else:
            raise ValueError(f"HEALTHHISTORY Codebook field has no explicit disposition: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": disposition, "concept_id": concept_id, "rationale": rationale,
                       "questionnaire_source": "sources_official/CHARLS_Life_History_Questionnaire.pdf",
                       "codebook_source": "sources_official/CHARLS_Life_History_codebook.pdf"})
    codes = [row["code"] for row in ledger]
    if len(ledger) != 86 or len(codes) != len(set(codes)):
        raise ValueError(f"HEALTHHISTORY coverage not exhaustive/unique: rows={len(ledger)}, unique={len(set(codes))}")
    return ledger


def build_sample_information_coverage(rows: list[dict]) -> list[dict]:
    """Disposition the eight Sample_Infor fields without leaking Codebook distributions."""
    mapped = {row["code"]: row for row in rows if row["module"] == "SAMPLEINFORMATION"}
    fields = read_codebook_fields()
    ledger = []
    linkage = {"id", "householdid", "communityid"}
    for (module, code), label in sorted(fields.items()):
        if module != "SAMPLEINFORMATION":
            continue
        row = mapped.get(code)
        if row:
            disposition, concept_id, rationale = "mapped_candidate", row["concept_id"], row["caveat"]
        elif code in linkage:
            disposition, concept_id = "excluded_linkage_key", ""
            rationale = "Person/household/community linkage key. Never publish values; ID adjustment for Wave 1 must follow the official release note."
        elif code == "longitudinal":
            disposition, concept_id = "excluded_sample_design_metadata", ""
            rationale = "Longitudinal-sample membership is a design/selection field, not an exposure or phenotype; preserve only in controlled analytic design metadata."
        elif code in {"iyear", "imonth"}:
            disposition, concept_id = "excluded_interview_timing_metadata", ""
            rationale = "Interview year/month describes data collection timing, not a phenotype or environmental exposure."
        elif code == "versionid":
            disposition, concept_id = "excluded_release_metadata", ""
            rationale = "Release/version bookkeeping metadata, not an E/P measure."
        else:
            raise ValueError(f"SAMPLEINFORMATION Codebook field has no explicit disposition: {code}")
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": disposition, "concept_id": concept_id, "rationale": rationale,
                       "release_note_source": "sources_official/CHARLS_Life_History_Release_note.pdf",
                       "codebook_source": "sources_official/CHARLS_Life_History_codebook.pdf"})
    codes = [row["code"] for row in ledger]
    if len(ledger) != 8 or len(codes) != len(set(codes)):
        raise ValueError(f"SAMPLEINFORMATION coverage not exhaustive/unique: rows={len(ledger)}, unique={len(set(codes))}")
    return ledger


def build_education_history_coverage(rows: list[dict]) -> list[dict]:
    """Map reviewed early Education History fields and explicitly defer the unreviewed remainder."""
    mapped = {row["code"]: row for row in rows if row["module"] == "EDUCATIONHISTORY"}
    fields = read_codebook_fields()
    ledger = []
    linkage = {"id", "householdid", "communityid"}
    for (module, code), label in sorted(fields.items()):
        if module != "EDUCATIONHISTORY":
            continue
        row = mapped.get(code)
        if row:
            disposition, concept_id, rationale = "mapped_candidate", row["concept_id"], row["caveat"]
        elif code in linkage:
            disposition, concept_id = "excluded_linkage_key", ""
            rationale = "Person/household/community linkage key. Never publish values; use only authorized controlled joins when required."
        elif code == "versionid":
            disposition, concept_id = "excluded_release_metadata", ""
            rationale = "Release/version bookkeeping metadata, not an E/P measure."
        elif re.search(r"address", label, re.I):
            disposition, concept_id = "excluded_sensitive_geography", ""
            rationale = "School address is sensitive location information and is not needed for an E/P catalogue; no school-level geographic linkage is performed."
        elif code == "errore000":
            disposition, concept_id = "excluded_data_quality_flag", ""
            rationale = "Internal interview/data-quality flag, not a respondent exposure or phenotype."
        elif re.search(r"noobservations", label, re.I):
            disposition, concept_id = "excluded_no_observations", ""
            rationale = "Release bookkeeping field indicating no observations, not a measured exposure or phenotype."
        elif re.fullmatch(r"e134_2_[1-5]_", code, re.I):
            disposition, concept_id = "deferred_certificate_identity_linkage", ""
            rationale = "Certificate-year slot cannot be interpreted as a specific certificate without validated linkage to the corresponding open-text certificate identity; retain for source review."
        else:
            disposition, concept_id = "deferred_source_review", ""
            rationale = "Education History questionnaire/codebook family not yet reviewed field-by-field for routing, referent, free text, address/privacy, repeated episode structure and authorized-release storage. Do not publish as a candidate or use in analysis until reviewed."
        ledger.append({"module": module, "code": code, "codebook_label": label,
                       "disposition": disposition, "concept_id": concept_id, "rationale": rationale,
                       "questionnaire_source": "sources_official/CHARLS_Life_History_Questionnaire.pdf",
                       "codebook_source": "sources_official/CHARLS_Life_History_codebook.pdf"})
    codes = [row["code"] for row in ledger]
    if len(ledger) != 1105 or len(codes) != len(set(codes)):
        raise ValueError(f"EDUCATIONHISTORY coverage not exhaustive/unique: rows={len(ledger)}, unique={len(set(codes))}")
    return ledger


def main() -> None:
    rows, concepts = build()
    sibling_coverage = build_sibling_module_coverage(rows)
    parent_coverage = build_parent_module_coverage(rows)
    family_class_coverage = build_historical_family_class_coverage(rows)
    parent_social_coverage = build_parent_social_context_coverage(rows)
    parent_employment_coverage = build_parent_employment_coverage(rows)
    sensitive_history_coverage = build_sensitive_history_coverage(rows)
    family_information_coverage = build_family_information_module_coverage(rows)
    residence_transition_coverage = build_residence_transition_coverage(rows)
    gap_migration_coverage = build_gap_migration_reason_coverage(rows)
    residence_module_coverage = build_residence_module_coverage(rows)
    wealth_history_coverage = build_wealth_history_module_coverage(rows)
    health_history_coverage = build_health_history_module_coverage(rows)
    sample_information_coverage = build_sample_information_coverage(rows)
    education_history_coverage = build_education_history_coverage(rows)
    AUDIT.mkdir(parents=True, exist_ok=True)
    DIST.mkdir(parents=True, exist_ok=True)
    csv_path = AUDIT / "life_history_exposure_crosswalk_v1.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    json_path = DIST / "life_history_exposures_v1.json"
    json_path.write_text(json.dumps(concepts, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    coverage_path = AUDIT / "life_history_sibling_module_coverage_2014_v1.csv"
    with coverage_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(sibling_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sibling_coverage)
    parent_coverage_path = AUDIT / "life_history_parent_module_coverage_2014_v1.csv"
    with parent_coverage_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(parent_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(parent_coverage)
    family_class_coverage_path = AUDIT / "life_history_historical_family_class_coverage_2014_v1.csv"
    with family_class_coverage_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(family_class_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(family_class_coverage)
    parent_social_coverage_path = AUDIT / "life_history_parent_social_context_coverage_2014_v1.csv"
    with parent_social_coverage_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(parent_social_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(parent_social_coverage)
    parent_employment_coverage_path = AUDIT / "life_history_parent_employment_coverage_2014_v1.csv"
    with parent_employment_coverage_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(parent_employment_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(parent_employment_coverage)
    sensitive_history_coverage_path = AUDIT / "life_history_sensitive_history_coverage_2014_v1.csv"
    with sensitive_history_coverage_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(sensitive_history_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sensitive_history_coverage)
    family_information_coverage_path = AUDIT / "life_history_family_information_full_coverage_2014_v1.csv"
    with family_information_coverage_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(family_information_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(family_information_coverage)
    residence_transition_path = AUDIT / "life_history_residential_timing_coverage_2014_v1.csv"
    with residence_transition_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(residence_transition_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(residence_transition_coverage)
    gap_migration_path = AUDIT / "life_history_gap_migration_reason_coverage_2014_v1.csv"
    with gap_migration_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(gap_migration_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(gap_migration_coverage)
    residence_module_path = AUDIT / "life_history_residence_full_coverage_2014_v1.csv"
    with residence_module_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(residence_module_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(residence_module_coverage)
    wealth_history_path = AUDIT / "life_history_wealth_history_full_coverage_2014_v1.csv"
    with wealth_history_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(wealth_history_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(wealth_history_coverage)
    health_history_path = AUDIT / "life_history_health_history_full_coverage_2014_v1.csv"
    with health_history_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(health_history_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(health_history_coverage)
    sample_information_path = AUDIT / "life_history_sample_information_coverage_2014_v1.csv"
    with sample_information_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(sample_information_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sample_information_coverage)
    education_history_path = AUDIT / "life_history_education_history_coverage_2014_v1.csv"
    with education_history_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(education_history_coverage[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(education_history_coverage)
    print(json.dumps({"concepts": len(concepts), "field_rows": len(rows),
                      "by_role": {role: sum(x["role"] == role for x in rows) for role in ("e", "p")},
                      "by_module": {module: sum(x["module"] == module for x in rows)
                                    for module in sorted({x["module"] for x in rows})},
                      "sibling_module_fields_dispositioned": len(sibling_coverage),
                      "parent_module_fields_dispositioned": len(parent_coverage),
                      "historical_family_class_fields_mapped": len(family_class_coverage),
                      "parent_social_context_fields_mapped": len(parent_social_coverage),
                      "parent_employment_fields_mapped": len(parent_employment_coverage),
                      "sensitive_history_metadata_fields": len(sensitive_history_coverage),
                      "family_information_fields_dispositioned": len(family_information_coverage),
                      "residence_timing_fields_mapped": len(residence_transition_coverage),
                      "between_residence_migration_fields_mapped": len(gap_migration_coverage),
                      "residence_module_fields_dispositioned": len(residence_module_coverage),
                      "wealth_history_fields_dispositioned": len(wealth_history_coverage),
                      "health_history_fields_dispositioned": len(health_history_coverage),
                      "sample_information_fields_dispositioned": len(sample_information_coverage),
                      "education_history_fields_dispositioned": len(education_history_coverage),
                      "csv": str(csv_path), "json": str(json_path),
                      "sibling_coverage": str(coverage_path),
                      "parent_coverage": str(parent_coverage_path),
                      "family_class_coverage": str(family_class_coverage_path),
                      "parent_social_context_coverage": str(parent_social_coverage_path),
                      "parent_employment_coverage": str(parent_employment_coverage_path),
                      "sensitive_history_coverage": str(sensitive_history_coverage_path),
                      "family_information_coverage": str(family_information_coverage_path),
                      "residence_timing_coverage": str(residence_transition_path),
                      "gap_migration_coverage": str(gap_migration_path),
                      "residence_module_coverage": str(residence_module_path),
                      "wealth_history_coverage": str(wealth_history_path),
                      "health_history_coverage": str(health_history_path),
                      "sample_information_coverage": str(sample_information_path),
                      "education_history_coverage": str(education_history_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
