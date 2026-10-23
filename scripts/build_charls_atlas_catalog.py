"""Create a broad, metadata-only CHARLS Atlas catalog for manual review.

The output mirrors NHANES PE Atlas catalog fields (source code, category,
description, role, wave availability), but uses CHARLS-specific categories.
Automated labels are discovery candidates, never a finalized analysis set.
No respondent-level values are read or written.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


WAVES = {"2011", "2013", "2015", "2018", "2020"}
ID_VARS = {"id", "householdid", "communityid", "sub_commuid", "household_id", "individual_id"}
ADMIN_LABEL = re.compile(
    r"\b(weight|psu|sample id|sample information|interview type|respondent type|"
    r"why didn.?t complete|measure or not|understand (the )?directions|"
    r"measure time|minute|\bhour\b|other \(specify\))\b",
    re.I,
)

RULES: list[tuple[str, str, str, re.Pattern[str], re.Pattern[str]]] = [
    # (role, category, subcategory, module regex, label/variable regex)
    ("e", "behavior", "smoking and tobacco", re.compile(r"health_status|health status", re.I), re.compile(r"smok|cigarette|tobacco|second.?hand", re.I)),
    ("e", "behavior", "alcohol use", re.compile(r"health_status|health status", re.I), re.compile(r"alcohol|drink|drinking", re.I)),
    ("e", "behavior", "physical activity", re.compile(r"health_status|health status|biomarker", re.I), re.compile(r"physical activ|exercise|vigorous|moderate activ|walking|walk for", re.I)),
    ("e", "behavior", "sleep", re.compile(r"health_status|health status|cognition", re.I), re.compile(r"sleep|nap|restless", re.I)),
    ("e", "behavior", "diet and food", re.compile(r"health_status|health status|household_income|household income", re.I), re.compile(r"diet|food|meal|\beat(?:ing)?\b|nutrition|food security|vegetable|fruit|meat|grain", re.I)),
    ("e", "built environment", "housing and dwelling", re.compile(r"housing_characteristics", re.I), re.compile(r"residen|house|building|room|bedroom|kitchen|toilet|water|electric|fuel|heat|floor|roof|ventilat|sewage|sanitation|cooking|stove|crowd", re.I)),
    ("e", "community context", "environment, infrastructure, and services", re.compile(r"community", re.I), re.compile(r"pollut|environment|water|waste|garbage|road|traffic|noise|clinic|hospital|health care|healthcare|school|transport|distance|market|facility|sanitation|toilet|electric|fuel|heating|disaster|industry|factory|green|park", re.I)),
    ("e", "social determinants", "education and social position", re.compile(r"demographic|family_information|family information|parent|sibling", re.I), re.compile(r"education|school|literacy|degree|hukou|urban|rural|residen|marital|married|ethnic|social class", re.I)),
    ("e", "social determinants", "income, wealth, and material resources", re.compile(r"income|asset|family_transfer|family transfer", re.I), re.compile(r"income|wealth|asset|debt|expenditure|consumption|spend|transfer|pension|wage|salary|value of|financial", re.I)),
    ("e", "social determinants", "employment, occupation, and work organization", re.compile(r"work|retirement|pension", re.I), re.compile(r"work|job|occupation|employ|labor|labour|hours worked|physical demand", re.I)),
    ("e", "social determinants", "social relations and care", re.compile(r"family|transfer|health_status|health status|health_care", re.I), re.compile(r"social particip|volunteer|caregiv|care for|receive help|give help|contact with|meet with|living arrangement|social activity|lonely|isolation|support", re.I)),
    ("e,p", "internal biomarker", "blood and biomarker measures; dual role requires review", re.compile(r"biomarker|blood_assays", re.I), re.compile(r"blood|serum|plasma|urine|urinary|hemoglobin|glucose|cholesterol|triglycer|hdl|ldl|creatin|cystatin|crp|bun|uric acid|pressure|systolic|diastolic|pulse|height|weight|waist|grip|peak flow|lung|balance|walk|chair stand|vitamin|biomarker", re.I)),
    # Phenome screening domains.
    ("p", "anthropometric", "body size and anthropometry", re.compile(r"biomarker", re.I), re.compile(r"height|body weight|weight measure|waist|circumference|body mass|bmi|hip|arm circumference|knee height", re.I)),
    ("p", "blood pressure", "blood pressure and pulse", re.compile(r"biomarker", re.I), re.compile(r"systolic|diastolic|blood pressure|pulse", re.I)),
    ("p", "biochemistry", "blood and urine laboratory measures", re.compile(r"blood_assays|blood assays", re.I), re.compile(r"blood|serum|plasma|urine|hemoglobin|glucose|cholesterol|triglycer|hdl|ldl|creatin|cystatin|crp|bun|uric acid|vitamin|assay", re.I)),
    ("p", "physical function", "strength, mobility, lung function, and performance", re.compile(r"biomarker|health_status|health status", re.I), re.compile(r"grip|peak flow|lung function|pulmonary|balance|chair stand|walk speed|walking speed|mobility|adl|iadl|difficulty|disabilit|physical function|activities of daily", re.I)),
    ("p", "cognition", "memory and cognitive performance", re.compile(r"cognition|health_status|health status", re.I), re.compile(r"cognit|memory|remember|recall|word|orientation|calculation|serial 7|mental status", re.I)),
    ("p", "mental health", "depressive symptoms and emotional wellbeing", re.compile(r"cognition|health_status|health status", re.I), re.compile(r"depress|anx|sad|lonely|loneliness|happiness|hopeful|fear|restless|mental health|psycholog", re.I)),
    ("p", "chronic disease", "self-reported physician diagnosis", re.compile(r"health_status|health status", re.I), re.compile(r"diagnos|hypertension|blood pressure|diabetes|high blood sugar|dyslipid|cancer|tumou?r|lung disease|heart disease|stroke|arthritis|kidney disease|liver disease|asthma|disease|health problem", re.I)),
    ("p", "health and symptoms", "self-rated health, pain, and symptoms", re.compile(r"health_status|health status", re.I), re.compile(r"self.?rated health|self comment of your health|pain|chest|symptom|vision|hearing|sleep quality|health condition|discomfort|incontinent", re.I)),
]

CONFOUNDERS = re.compile(r"age|gender|sex|education|marital|hukou|urban|rural|province|city|region|ethnic|race", re.I)
# Exclude slot-specific household/family grids until respondent-level derivations are reviewed.
ROSTER_NOISE = re.compile(r"household ?member|hhmember|household roster|member of (the )?household|sibling|this child|child.?s (?:education|school|marital)|other household member|other_hhmember|other chair|why didn.?t .*complete", re.I)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] / "audit/raw_variable_catalog_v1.csv")
    ap.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parents[1] / "audit")
    ap.add_argument("--site-catalog", type=Path, default=Path(__file__).resolve().parents[1] / "site-prototype/dist/catalog.json")
    args = ap.parse_args()

    source = pd.read_csv(args.catalog, dtype=str, encoding="utf-8-sig").fillna("")
    source = source[source.wave.isin(WAVES)].copy()
    # Crosswalk enrichment resolves the module for thousands of source-field
    # rows. Pre-index the small lookup once instead of repeatedly scanning the
    # full pandas table for every field (which dominated catalog-build time).
    modules_by_wave_variable: dict[tuple[str, str], list[str]] = {}
    archive_by_wave_variable: dict[tuple[str, str], str] = {}
    for wave, variable, source_module, source_archive in source[["wave", "variable", "module", "source"]].itertuples(index=False, name=None):
        key = (str(wave), str(variable).lower())
        modules = modules_by_wave_variable.setdefault(key, [])
        source_module = str(source_module)
        if source_module not in modules:
            modules.append(source_module)
        archive_by_wave_variable.setdefault(key, str(source_archive))

    def canonical_module(wave: str, code: str, module: str) -> str | None:
        modules = modules_by_wave_variable.get((str(wave), str(code).lower()), [])
        if len(modules) == 1:
            return modules[0]
        exact = [name for name in modules if name.strip().lower() == str(module).strip().lower()]
        if exact:
            return exact[0]
        if len(modules) > 1:
            return None
        return module
    outputs: list[dict[str, str]] = []
    for row in source.itertuples(index=False):
        var = row.variable.strip()
        label = row.variable_label.strip()
        module = row.module.strip()
        if (str(row.wave), var.lower()) in {
            ("2011", "qh006"), ("2013", "qh006"),
            ("2015", "qh006"), ("2015", "qh006_1"),
        }:
            # QH006 is chair/setup information for repeated chair stands,
            # despite legacy 2011/2013 codebook labels that say only Height.
            # The 2015 questionnaire explicitly records chair height; the
            # personal standing-height outcome is QI002.
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "c", "category": "measurement metadata",
                "subcategory": "chair setup for repeated chair-stand test",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "official codebook field; 2015 biomarker questionnaire identifies QH006 as chair-height/setup information",
                "Harmonization.Status": "2011/2013 codebook reports continuous values around 42 cm; 2015 records standard-chair versus other-chair and QH006_1 height. Individual height is QI002.",
                "Review.Flag": "protocol/setup metadata, not a respondent phenotype or environmental exposure; retain only for measurement-quality or sensitivity review",
            })
            continue
        if (not var or var.lower() in ID_VARS or label.lower().endswith(" id") or ADMIN_LABEL.search(label) or ROSTER_NOISE.search(f"{label} {var}") or re.search(r"family_information|family_transfer", module, re.I)):
            continue
        lower_var = var.lower()
        if row.wave in {"2011", "2013", "2015"} and lower_var == "ha064":
            # In these waves HA064 selects a currency/applicability response
            # for the conditional HA064_1 amount; it is not the later-wave
            # yes/no rental-income status. It is reintroduced below as C-only
            # measurement metadata from the reviewed crosswalk.
            continue
        is_asset_module = re.search(r"household.?income", module, re.I)
        is_asset_choice = bool(re.fullmatch(r"ha065s(?:[1-9]|1[0-8])|ha065_s(?:[1-9]|1[0-9])", lower_var))
        is_asset_value_legacy = bool(re.fullmatch(r"ha065_1_(?:[1-9]|1[0-7])_", lower_var))
        is_asset_value_wave4 = bool(row.wave == "2018" and re.fullmatch(r"ha065_(?:[1-9]|1[0-8])", lower_var))
        if is_asset_module and (is_asset_choice or is_asset_value_legacy or is_asset_value_wave4):
            value_item = bool(is_asset_value_legacy or is_asset_value_wave4)
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "e", "category": "social determinants",
                "subcategory": "income, wealth, and material resources",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "household durable asset field identified; official asset list / current value mapping available",
                "Harmonization.Status": ("Household ownership response; 2011–2015 selected-option coding differs from 2018 item-specific 0=No / item-code=Yes. Preserve wave-specific coding."
                                         if is_asset_choice else "Household-level current value in Yuan; preserve item-specific routing, special missingness, and zero values. Not respondent-owned wealth."),
                "Review.Flag": "candidate only; do not infer No from unselected/missing fields or equate household ownership/value with respondent/spouse ownership",
            })
            continue
        fixed_ownership = bool(re.fullmatch(r"ha066s[1-6]", lower_var)) or bool(row.wave == "2018" and re.fullmatch(r"ha066_w4_s[1-8]", lower_var))
        fixed_value_legacy = bool(row.wave in {"2011", "2013", "2015"} and re.fullmatch(r"ha066_1_[1-5]_", lower_var))
        fixed_value_wave4 = bool(row.wave == "2018" and re.fullmatch(r"ha066_w4_[1-7]", lower_var))
        fixed_capital_other = lower_var in {"ha067", "ha067_w4", "ha068", "ha068_1"}
        inactive_fixed_metadata = row.wave == "2015" and lower_var in {"ha066_1", "ha066_1_6_"}
        if is_asset_module and inactive_fixed_metadata:
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "c", "category": "measurement metadata",
                "subcategory": "inactive fixed-capital legacy/format fields",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "2015 Codebook explicitly reports No Observations for this parent/format field",
                "Harmonization.Status": "Inactive technical parent or face-value field; specific asset ownership/value fields are catalogued separately.",
                "Review.Flag": "C-only metadata; do not treat as exposure or infer values from a parent/format field",
            })
            continue
        if is_asset_module and (fixed_ownership or fixed_value_legacy or fixed_value_wave4 or fixed_capital_other):
            is_value = fixed_value_legacy or fixed_value_wave4 or lower_var in {"ha067", "ha067_w4", "ha068_1"}
            description = label
            if lower_var in {"ha067", "ha067_w4"}:
                harmonization = "Other production/self-employment fixed-capital value; preserve its wave-specific household/respondent-spouse scope and do not add to listed-asset values as net wealth."
            elif lower_var == "ha068":
                harmonization = "Other durable/fixed asset status for the 500-Yuan threshold item; preserve wave-specific scope, response categories, and conditional value route."
            elif is_value:
                harmonization = "Current-value field; preserve asset-specific routing, scope, unit, special missingness, and zero values; do not infer non-ownership from missing value."
            else:
                harmonization = "Asset ownership/none-of-list field; preserve wave-specific codes and ownership scope; an unselected or missing legacy multi-select option is not automatically No."
            outputs.append({
                "Variable.Name": var, "Variable.Description": description,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "e", "category": "social determinants",
                "subcategory": "income, wealth, and material resources",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "official fixed-capital/other-asset field identified; see audited wave-specific concept mapping",
                "Harmonization.Status": harmonization,
                "Review.Flag": "candidate only; retain official scope, response route and codebook missingness; no composite wealth measure implied",
            })
            continue
        lending_debt_item = lower_var in {"ha069", "ha070", "ha071", "ha072"}
        debt_bracket_item = bool(re.fullmatch(r"ha073_[1-6]", lower_var)) or lower_var in {"ha073_bracket_min", "ha073_bracket_max"}
        household_finance_module = re.search(r"household.?income", module, re.I)
        if household_finance_module and lending_debt_item and row.wave == "2015":
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "c", "category": "measurement metadata",
                "subcategory": "inactive household lending and debt legacy fields",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "2015 Codebook explicitly reports No Observations for this field",
                "Harmonization.Status": "Inactive legacy field; no observed response category or amount is supplied in the official Codebook.",
                "Review.Flag": "C-only metadata; do not interpret absence as zero or No and do not enter an analysis set",
            })
            continue
        if household_finance_module and lending_debt_item and row.wave in {"2011", "2013"}:
            meaning = {
                "ha069": "Household indicator for loans lent to other families/individuals that remain unpaid; preserve Yes/No coding and do not infer a No from an unselected or missing value.",
                "ha070": "Household total of lent amounts still unpaid; asked after HA069=Yes. Preserve conditional missingness and keep household receivable principal distinct from income.",
                "ha071": "Household interest income from lending during the past year; HA069=No routes to this item, so do not restrict it to positive current receivables.",
                "ha072": "Household outstanding debt owed to other families, individuals or the work unit, explicitly excluding mortgage loans; if the exact answer is not provided, the questionnaire routes to HA073 unfolding brackets.",
            }[lower_var]
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "e", "category": "social determinants",
                "subcategory": "income, wealth, and material resources",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "official household lending/debt item identified; see audited concept mapping",
                "Harmonization.Status": meaning,
                "Review.Flag": "candidate only; retain household level, item route, exact amount semantics, and wave-specific nonresponse; no individual debt or net-wealth measure implied",
            })
            continue
        if household_finance_module and debt_bracket_item and row.wave in {"2011", "2013"}:
            no_observations = row.wave == "2011" and lower_var == "ha073_6"
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "c", "category": "measurement metadata",
                "subcategory": "household debt unfolding-bracket response metadata",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "2011 Codebook reports No Observations for this bracket field" if no_observations else "official questionnaire debt nonresponse fallback field identified",
                "Harmonization.Status": "Conditional HA073 unfolding-bracket component when the exact HA072 debt amount is not supplied; not an exact debt value or independent exposure.",
                "Review.Flag": "C-only response-protocol metadata; preserve bracket route, do not midpoint-impute, and do not count threshold components as separate exposures",
            })
            continue
        if row.wave in {"2013", "2015", "2018"} and var.lower() == "da019_w2_2":
            # DA019_W2_2 only records whether the most-recent-stroke timing
            # response is a year or an age. It is a format selector, not a
            # stroke outcome; the numeric date/age components are separate.
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "c", "category": "measurement metadata",
                "subcategory": "stroke recurrence timing response format",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "official questionnaire/codebook response-format field",
                "Harmonization.Status": "1=Year; 2=Age; applies to DA019_W2_2_1/_2; not a standalone phenotype",
                "Review.Flag": "conditional on the prior-stroke recurrence route; retain as timing metadata only",
                "Value.Labels": "1=Year; 2=Age",
                "Value.Label.Source": f"sources_official/CHARLS_{row.wave}_Codebook_extracted.txt",
                "Value.Label.Review": "officially reviewed",
            })
            continue
        # ZF* fields are prior-interview preloads/verification states, not
        # current-wave work exposures; keep them in the source catalog, but
        # out of this current exposure screen until a longitudinal construct
        # is explicitly defined.
        if var.lower().startswith("zf") and re.search(r"work|retirement", module, re.I):
            continue
        # In 2020 DA009–DA012 are COVID-period delayed-care items, not the
        # legacy disease-management DA010 fields used in earlier waves.
        if row.wave == "2020" and re.fullmatch(r"da009|da0(10|11|12)_s\d+", var.lower()):
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "p", "category": "healthcare access",
                "subcategory": "COVID-period delayed or unmet medical care",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "2020 questionnaire-grounded conditional healthcare-access phenotype candidate",
                "Harmonization.Status": "COVID-period-specific; DA010–DA012 are conditional on DA009 and/or outpatient-service selection; no cross-wave equivalent assumed",
                "Review.Flag": "preserve item-specific response code, conditional denominator, and 2020-only scope",
            })
            continue
        if var.lower().startswith("da010_") and re.search(r"health_status", module, re.I):
            # DA010 medication/treatment items are disease-management
            # constructs, not disease-prevalence outcomes or diet exposures.
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "p", "category": "chronic disease ancillary",
                "subcategory": "reported disease treatment / wave-specific treatment response",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "official disease-treatment crosswalk; disease-specific routing and response options require review",
                "Harmonization.Status": "Treatment is not a disease diagnosis; preserve disease item, wave, response slot, and skip route",
                "Review.Flag": "do not interpret medication/treatment fields as current prevalence or as dietary exposures",
            })
            continue
        if row.wave == "2020" and var.lower().startswith("da002_"):
            # Wave 5 DA002 is a retrospective change item. Keep it out of the
            # current-prevalence category; the concept crosswalk supplies its
            # disease-specific meaning and official response labels.
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "p", "category": "chronic disease ancillary",
                "subcategory": "reported disease change since prior interview / self-rated interval change",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "official 2020 disease-index crosswalk; longitudinal comparison item, not current prevalence",
                "Harmonization.Status": "Compare to prior interview; value 99 means absent at prior interview and is not current disease status",
                "Review.Flag": "retain as a separate longitudinal outcome; do not merge with same-wave diagnosis prevalence",
            })
            continue
        matched = False
        work_prefix = var.lower()[:2]
        if work_prefix == "fn" and re.search(r"work|retirement|pension", module, re.I):
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "e", "category": "social protection",
                "subcategory": "pension participation, receipt, and benefit details",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "automated discovery; pension field family identified from official module and code prefix",
                "Harmonization.Status": "plan-specific and wave-specific pension questions; verify response object, routing, and category before deriving coverage or benefit indicators",
                "Review.Flag": "plan/benefit subfields are not separate harmonized pension concepts; do not treat bracket bounds or preloads as observed benefit amounts",
            })
            matched = True
        elif work_prefix == "fm" and re.search(r"work|retirement|pension", module, re.I):
            outputs.append({
                "Variable.Name": var, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave, "EndYear": row.wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "e", "category": "social determinants",
                "subcategory": "retirement and employment-transition history",
                "Source.Wave": row.wave, "Source.Archive": row.source,
                "Candidate.Status": "automated discovery; retirement-module field family identified from official module and code prefix",
                "Harmonization.Status": "retirement/receding-status records are route- and history-dependent; verify current versus prior event and respondent eligibility",
                "Review.Flag": "do not count preload/verification fields as additional current-wave exposures",
            })
            matched = True
        if work_prefix in {"fn", "fm"}:
            continue
        for role, category, subcategory, mod_re, value_re in RULES:
            if mod_re.search(module) and value_re.search(f"{label} {var}"):
                # GE005/GF005 asks a household respondent how many meals the
                # household provided to guests. It is a household social-
                # reciprocity measure, not personal diet/food exposure; the
                # reviewed concept crosswalk below supplies its E catalog row.
                if role == "e" and category == "behavior" and subcategory == "diet and food" and var.lower() in {"ge005", "gf005"}:
                    continue
                # The DA044 disease-history fields belong in the physician-
                # reported disease family only; avoid duplicate P-catalog rows
                # under the generic symptom keyword rule.
                if role == "p" and category == "health and symptoms" and re.fullmatch(r"da044s(?:[1-9]|1[0-4])", var.lower()):
                    continue
                # The 2011/2013 DA003–DA004 fields are non-proxy chest-pain
                # symptoms. “Walking quickly” in DA004 describes the trigger
                # for pain; it is not a physical-activity exposure.
                if role == "e" and re.search(r"chest pain", f"{label} {var}", re.I):
                    continue
                outputs.append({
                    "Variable.Name": var,
                    "Variable.Description": label,
                    "Data.File.Name": module,
                    "Data.File.Description": module.replace("_", " "),
                    "Begin.Year": row.wave,
                    "EndYear": row.wave,
                    "Component": module,
                    "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                    "epcf": role,
                    "category": category,
                    "subcategory": subcategory,
                    "Source.Wave": row.wave,
                    "Source.Archive": row.source,
                    "Candidate.Status": "automated discovery; questionnaire/codebook review required",
                    "Harmonization.Status": "wave-specific source field; cross-wave concept mapping not yet approved",
                    "Review.Flag": "role/category is a search aid, not analytic inclusion",
                })
                matched = True
        if CONFOUNDERS.search(f"{label} {var}") and re.search(r"demographic|health_status|health status|family|housing", module, re.I):
            outputs.append({
                "Variable.Name": var,
                "Variable.Description": label,
                "Data.File.Name": module,
                "Data.File.Description": module.replace("_", " "),
                "Begin.Year": row.wave,
                "EndYear": row.wave,
                "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": "c",
                "category": "covariate candidate",
                "subcategory": "demographic / design / socioeconomic adjustment candidate",
                "Source.Wave": row.wave,
                "Source.Archive": row.source,
                "Candidate.Status": "automated discovery; questionnaire/codebook review required",
                "Harmonization.Status": "wave-specific source field; cross-wave concept mapping not yet approved",
                "Review.Flag": "do not automatically adjust; select by estimand and causal structure",
            })
            matched = True
        if not matched:
            continue

    # Fold existing audited domain crosswalks into the searchable E/P catalog
    # when keyword discovery missed a field (e.g. social participation grids).
    # These remain candidate rows and retain each domain audit's caveats.
    existing_keys = {
        (str(x.get("Source.Wave", "")), str(x.get("Variable.Name", "")).lower(),
         str(x.get("Data.File.Name", "")).strip().lower(), str(x.get("epcf", "")),
         str(x.get("category", "")), str(x.get("subcategory", "")))
        for x in outputs
    }
    existing_wave_role_category = set()
    for x in outputs:
        for role in str(x.get("epcf", "")).split(","):
            existing_wave_role_category.add((str(x.get("Source.Wave", "")),
                str(x.get("Variable.Name", "")).lower(), str(x.get("Data.File.Name", "")).strip().lower(),
                role.strip(), str(x.get("category", ""))))

    def append_audited_crosswalk(file: str, wave_col: str, code_col: str, module_col: str,
                                 label_col: str, category: str, subcategory: str,
                                 note_col: str | None = None, role: str = "e", role_col: str | None = None) -> None:
        path = Path(__file__).resolve().parents[1] / "audit" / file
        if not path.exists():
            return
        tab = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
        for item in tab.to_dict(orient="records"):
            wave, code = str(item.get(wave_col, "")).strip(), str(item.get(code_col, "")).strip()
            if not wave or not code or wave not in WAVES:
                continue
            if file == "healthcare_access_crosswalk_v1.csv" and wave == "2020" and re.fullmatch(r"da009|da0(10|11|12)_s\d+", code.lower()):
                # These pandemic-only phenotype rows were added explicitly
                # above with their conditional-route caveat and P role.
                continue
            module = canonical_module(wave, code, str(item.get(module_col, "")).strip() or "official crosswalk")
            if module is None:
                continue
            key = (wave, code.lower(), module.lower(), role, category, subcategory)
            broad_key = (wave, code.lower(), module.lower(), role, category)
            if key in existing_keys or broad_key in existing_wave_role_category:
                continue
            description = str(item.get(label_col, "")).strip() or code
            note = str(item.get(note_col, "")).strip() if note_col else ""
            raw = source[(source.wave == wave) & (source.variable.str.lower() == code.lower())]
            archive = raw.iloc[0].source if not raw.empty else "official audit crosswalk"
            outputs.append({
                "Variable.Name": code, "Variable.Description": description,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": wave, "EndYear": wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": (str(item.get(role_col, "")).strip() or role) if role_col else role,
                "category": category, "subcategory": subcategory,
                "Source.Wave": wave, "Source.Archive": archive,
                "Candidate.Status": f"audited domain crosswalk candidate; see audit/{file}",
                "Harmonization.Status": note or "wave-specific source field; cross-wave harmonization remains under review",
                "Review.Flag": "candidate role is estimand-dependent; do not treat as automatic analytic inclusion",
            })
            existing_keys.add(key)
            existing_wave_role_category.add(broad_key)

    append_audited_crosswalk("social_exposure_crosswalk_v1.csv", "wave", "code", "module", "source_label",
                             "social determinants", "social relations and care", "caveat")
    append_audited_crosswalk("formal_schooling_lifecourse_crosswalk_v1.csv", "wave", "code", "module", "source_label",
                             "social determinants", "formal schooling history and timing", "caveat")
    append_audited_crosswalk("partner_context_crosswalk_v1.csv", "wave", "code", "module", "source_label",
                             "social determinants", "marital status and partner context", "caveat")
    append_audited_crosswalk("healthcare_access_crosswalk_v1.csv", "wave", "code", "module", "source_label",
                             "healthcare access", "insurance, outpatient and inpatient utilization", "caveat", "e,p", "catalog_role")
    append_audited_crosswalk("food_environment_crosswalk_v1.csv", "wave", "code", "module", "source_label",
                             "food and household environment", "diet, food security, housing and utilities", "caveat")

    def append_concept_crosswalk(file: str, wave_col: str, code_col: str, concept_col: str,
                                 label_col: str, module_col: str, category: str, subcategory,
                                 role: str, status_col: str, detail_cols: tuple[str, ...]) -> None:
        path = Path(__file__).resolve().parents[1] / "audit" / file
        if not path.exists():
            return
        tab = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
        for item in tab.to_dict(orient="records"):
            wave = str(item.get(wave_col, "")).strip()
            code = str(item.get(code_col, "")).strip()
            concept = str(item.get(concept_col, "")).strip()
            if not wave or not code or wave not in WAVES or not concept:
                continue
            cat = category(concept, item) if callable(category) else category
            sub = subcategory(concept, item) if callable(subcategory) else subcategory
            module = canonical_module(wave, code, str(item.get(module_col, "")).strip() or "official crosswalk")
            if module is None:
                continue
            broad_key = (wave, code.lower(), module.lower(), role, cat)
            if broad_key in existing_wave_role_category:
                continue
            label = str(item.get(label_col, "")).strip() or code
            archive = archive_by_wave_variable.get((wave, code.lower()), f"audit/{file}")
            detail = "; ".join(str(item.get(col, "")).strip() for col in detail_cols if str(item.get(col, "")).strip())
            outputs.append({
                "Variable.Name": code, "Variable.Description": label,
                "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                "Begin.Year": wave, "EndYear": wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": role, "category": cat, "subcategory": sub,
                "Source.Wave": wave, "Source.Archive": archive,
                "Candidate.Status": f"concept-source crosswalk candidate; see audit/{file}",
                "Harmonization.Status": detail or f"candidate mapping to {concept}; confirm source routing and wave compatibility",
                "Review.Flag": "preserve source item and mapping status; candidate concept is not yet an approved test variable",
            })
            existing_wave_role_category.add(broad_key)

    def behavior_subcategory(concept: str, _item: dict) -> str:
        key = concept.lower()
        if "smok" in key or "tobacco" in key:
            return "smoking and tobacco"
        if "alcohol" in key or "drink" in key:
            return "alcohol use"
        if "activity" in key or "exercise" in key:
            return "physical activity"
        if "sleep" in key:
            return "sleep"
        if "diet" in key or "food" in key:
            return "diet and food"
        return "other behavior"

    append_concept_crosswalk("behavior_exposure_variable_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "behavior", behavior_subcategory, "e", "mapping_status", ("note", "value_semantics"))
    append_concept_crosswalk("assistive_device_phenotype_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "physical function", "assistive-device use in ADL/IADL support", "p", "mapping_status", ("value_semantics", "caveat"))
    append_concept_crosswalk("functional_concept_variable_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "physical function", "strength, mobility, lung function, and performance", "p", "mapping_status", ("harmonization_note", "note"))
    append_concept_crosswalk("health_work_limitation_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "physical function", "work and housework capacity limitations", "p", "mapping_status", ("note", "value_semantics"))
    append_concept_crosswalk("health_work_absence_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "health and symptoms", "health-related work absence", "p", "mapping_status", ("caveat", "value_semantics", "unit"))
    append_concept_crosswalk("health_symptom_variable_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "health and symptoms", "self-rated health, pain, symptoms, and test eligibility", "p", "mapping_status", ("note", "value_labels", "value_label_status", "value_label_source"))
    append_concept_crosswalk("biomarker_measurement_gate_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "measurement metadata", "biomarker assessment agreement and completion", "c", "mapping_status", ("caveat", "value_semantics", "value_labels", "source_document"))
    append_concept_crosswalk("mood_item_variable_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "mental health", "depressive symptoms and emotional wellbeing", "p", "mapping_status", ("note",))
    append_concept_crosswalk("loneliness_exposure_role_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "social relations and care", "e", "mapping_status", ("caveat", "value_semantics"))
    append_concept_crosswalk("cognition_item_variable_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "cognition", "memory and cognitive performance", "p", "mapping_status", ("note",))
    append_concept_crosswalk("chronic_disease_concept_variable_mapping_v2.csv", "Source.Wave", "Source.Variable", "Concept.ID", "Source.Label", "Source.Module",
                             "chronic disease", "self-reported physician diagnosis", "p", "Mapping.Status", ("Caveat",))
    append_concept_crosswalk("chronic_disease_ancillary_variable_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "chronic disease ancillary", lambda concept, item: f"{item.get('construct', 'ancillary')} / {item.get('subtype', '')}",
                             "p", "mapping_status", ("caveat",))
    append_concept_crosswalk("psych_treatment_2011_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "chronic disease ancillary", "emotional/psychiatric treatment options",
                             "p", "mapping_status", ("source_item", "construct", "unit", "value_semantics", "caveat"))
    append_concept_crosswalk("chronic_disease_management_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "chronic disease ancillary", lambda concept, item: f"conditional management / {item.get('construct', '')} / {item.get('subtype', '')}",
                             "p", "mapping_status", ("caveat", "value_labels", "unit"))
    append_concept_crosswalk("cancer_site_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "chronic disease ancillary", lambda concept, item: f"reported cancer site / {item.get('subtype', '')}",
                             "p", "mapping_status", ("caveat", "value_labels"))
    append_concept_crosswalk("disability_history_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "physical function", lambda concept, item: f"reported disability history / {item.get('subtype', '')}",
                             "p", "mapping_status", ("field_role", "value_semantics", "caveat"))
    append_concept_crosswalk("community_exposure_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "community context", "environment, infrastructure, and services", "e", "mapping_status", ("source_evidence", "caveat"))
    append_concept_crosswalk("social_exposure_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "social relations and care", "e", "mapping_status", ("value_semantics", "caveat"))
    append_concept_crosswalk("work_exposure_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "employment, occupation, and work organization", "e", "questionnaire_review", ("caveat",))
    append_concept_crosswalk("interwave_other_job_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "employment, occupation, and work organization", "e", "mapping_status", ("questionnaire_review", "caveat", "unit"))
    append_concept_crosswalk("pension_exposure_variable_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social protection", lambda concept, item: item.get("construct", "pension construct"),
                             "e", "mapping_status", ("caveat",))
    append_concept_crosswalk("life_insurance_exposure_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social protection", "life insurance coverage, type, premiums and benefits", "e", "mapping_status", ("mapping_status", "construct", "unit", "caveat"))
    append_concept_crosswalk("pension_subsidy_delivery_2015_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social protection", "old-age subsidy delivery and card/voucher use", "e", "mapping_status", ("caveat", "unit"))
    append_concept_crosswalk("personal_income_exposure_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "individual income and wage resources",
                             "e", "mapping_status", ("construct", "unit", "value_labels", "caveat"))
    append_concept_crosswalk("individual_transfer_income_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social protection", "individual transfer income source and amount",
                             "e", "mapping_status", ("source_item", "construct", "unit", "value_semantics", "caveat"))
    append_concept_crosswalk("household_economic_exposure_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "household expenditure and material resources",
                             "e", "mapping_status", ("construct", "reference_period", "caveat"))
    append_concept_crosswalk("household_renovation_expenditure_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "income, wealth, and material resources", "e", "mapping_status", ("unit", "caveat"))
    append_concept_crosswalk("health_anchoring_vignette_metadata_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "measurement metadata", "hypothetical health anchoring vignettes", "c", "mapping_status", ("value_semantics", "value_labels", "caveat"))
    append_concept_crosswalk("household_transfer_compensation_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "income, wealth, and material resources", "e", "mapping_status", ("unit", "caveat"))
    append_concept_crosswalk("household_dibao_amount_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social protection", "household social assistance and transfers", "e", "mapping_status", ("unit", "caveat"))
    append_concept_crosswalk("household_transfer_receipt_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "income, wealth, and material resources", "e", "mapping_status", ("construct", "unit", "caveat"))
    append_concept_crosswalk("household_transfer_none_option_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "measurement metadata", "checklist none-option coding", "c", "mapping_status", ("unit", "caveat"))
    append_concept_crosswalk("household_additional_income_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "income, wealth, and material resources",
                             "e", "mapping_status", ("unit", "caveat"))
    append_concept_crosswalk("residential_rental_income_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "income, wealth, and material resources",
                             "e", "mapping_status", ("unit", "value_semantics", "caveat"))
    append_concept_crosswalk("land_rental_income_crosswalk_v1.csv", "wave", "code", "concept_id", "concept_label", "module",
                             "social determinants", "income, wealth, and material resources",
                             "e", "mapping_status", ("unit", "value_semantics", "caveat"))
    append_concept_crosswalk("household_other_asset_rental_income_amount_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "income, wealth, and material resources",
                             "e", "mapping_status", ("unit", "caveat"))
    append_concept_crosswalk("household_other_asset_rental_income_status_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "income, wealth, and material resources",
                             "e", "mapping_status", ("unit", "value_labels", "caveat"))
    append_concept_crosswalk("household_other_asset_rental_income_selector_metadata_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "measurement metadata", "household income response-format selectors",
                             "c", "mapping_status", ("unit", "caveat"))
    append_concept_crosswalk("household_covid_economic_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "household income, financial strain, and COVID-period coping",
                             "e", "mapping_status", ("unit", "value_labels", "caveat"))
    append_concept_crosswalk("personal_wage_deductions_2020_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "personal income, wage, and deductions",
                             "e", "mapping_status", ("unit", "value_labels", "caveat"))
    append_concept_crosswalk("personal_wage_deduction_2020_selector_metadata_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "measurement metadata", "personal wage-deduction format selector",
                             "c", "mapping_status", ("caveat",))
    append_concept_crosswalk("household_agricultural_production_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "income, wealth, and material resources",
                             "e", "mapping_status", ("unit", "caveat"))
    append_concept_crosswalk("housing_exposure_variable_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "housing and built environment", "dwelling conditions and household property",
                             "e", "mapping_status", ("construct", "caveat"))
    append_concept_crosswalk("demographic_social_exposure_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", lambda concept, item: item.get("domain", "education and social position"),
                             "e", "mapping_status", ("construct", "caveat"))
    append_concept_crosswalk("parent_education_exposure_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "early-life family socioeconomic context",
                             "e", "mapping_status", ("construct", "value_semantics", "value_labels", "caveat"))
    append_concept_crosswalk("parent_roster_education_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "early-life and family socioeconomic context",
                             "e", "mapping_status", ("construct", "value_semantics", "value_labels", "caveat"))
    append_concept_crosswalk("sibling_record_context_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             lambda concept, item: item.get("domain", "family and intergenerational context"),
                             lambda concept, item: item.get("subcategory", "sibling record context"),
                             "e", "mapping_status", ("construct", "value_semantics", "value_labels", "caveat"))
    append_concept_crosswalk("parent_roster_context_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             lambda concept, item: item.get("domain", "social determinants"),
                             lambda concept, item: item.get("subcategory", "family context"),
                             "e", "mapping_status", ("construct", "value_semantics", "value_labels", "caveat"))
    append_concept_crosswalk("parent_marital_ethnicity_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             lambda concept, item: item.get("domain", "family context"),
                             lambda concept, item: item.get("subcategory", "parent marital and ethnic context"),
                             "e", "mapping_status", ("construct", "value_semantics", "value_labels", "caveat"))
    append_concept_crosswalk("social_context_remainder_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             lambda concept, item: item.get("domain", "social determinants"),
                             lambda concept, item: item.get("subcategory", "historical and residential context"),
                             "e", "mapping_status", ("construct", "unit", "value_semantics", "value_labels", "caveat"))
    append_concept_crosswalk("hukou_lifecourse_exposure_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "hukou history and transitions",
                             "e", "mapping_status", ("construct", "unit", "value_semantics", "value_labels", "caveat"))
    append_concept_crosswalk("hukou_recent_change_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "hukou history and transitions",
                             "e", "mapping_status", ("construct", "unit", "value_semantics", "value_labels", "caveat"))
    append_concept_crosswalk("residential_settlement_exposure_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "residential settlement context",
                             "e", "mapping_status", ("construct", "value_semantics", "value_labels", "caveat"))
    append_concept_crosswalk("marital_history_exposure_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", "marital history and marriage transfers",
                             "e", "mapping_status", ("construct", "value_semantics", "value_labels", "caveat"))
    append_concept_crosswalk("adult_education_training_exposure_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants",
                             lambda concept, item: "adult education and lifelong learning" if concept.startswith("adult_education_") else "vocational and technical training",
                             "e", "mapping_status", ("construct", "value_semantics", "caveat"))
    append_concept_crosswalk("residual_behavior_exposure_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             lambda concept, item: "behavior" if concept == "previous_day_sleep_schedule" else "social determinants",
                             lambda concept, item: "sleep" if concept == "previous_day_sleep_schedule" else "social relations and care",
                             "e", "mapping_status", ("construct", "value_semantics", "caveat"))
    append_concept_crosswalk("household_member_income_mapping_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "social determinants", lambda concept, item: item.get("construct", "household-member income slot"),
                             "e", "mapping_status", ("construct", "caveat"))
    append_concept_crosswalk("measurement_protocol_crosswalk_v1.csv", "wave", "code", "concept_id", "source_label", "module",
                             "measurement metadata", "personal wage deduction scope and response-unit selectors",
                             "c", "mapping_status", ("value_semantics", "value_labels", "caveat"))

    # Laboratory assays are released separately from the wave-level interview
    # module inventory. In particular, 2015 bl_* fields are absent from the
    # raw module catalog but confirmed by CHARLS's official blood release note.
    blood_path = Path(__file__).resolve().parents[1] / "audit" / "blood_biomarker_crosswalk_v1.csv"
    if blood_path.exists():
        blood = pd.read_csv(blood_path, dtype=str, encoding="utf-8-sig").fillna("")
        for item in blood.to_dict(orient="records"):
            wave = str(item.get("wave", "")).strip()
            code = str(item.get("variable", "")).strip()
            concept = str(item.get("concept_id", "")).strip()
            if not wave or not code or wave not in WAVES or concept == "blood_collection_metadata":
                continue
            category, subcategory, role = "biochemistry", "blood and urine laboratory measures", "p"
            key = (wave, code.lower(), role, category, subcategory)
            if key in existing_keys:
                continue
            unit = str(item.get("unit", "")).strip()
            description = str(item.get("concept_label", code)).strip()
            if unit:
                description += f" (continuous laboratory measure; unit: {unit})"
            module = str(item.get("module", "Blood Data")).strip()
            detail = "; ".join(filter(None, [
                str(item.get("value_semantics", "")).strip(),
                str(item.get("collection_scope", "")).strip(),
                f"blood weight field: {item.get('weight_field', '').strip()}" if str(item.get("weight_field", "")).strip() else "",
                f"official source: {item.get('source_document', '').strip()}" if str(item.get("source_document", "")).strip() else "",
                str(item.get("source_status", "")).strip(),
            ]))
            outputs.append({
                "Variable.Name": code, "Variable.Description": description,
                "Data.File.Name": module, "Data.File.Description": module,
                "Begin.Year": wave, "EndYear": wave, "Component": module,
                "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                "epcf": role,
                "category": category, "subcategory": subcategory,
                "Source.Wave": wave,
                "Source.Archive": str(item.get("source_document", "official blood biomarker crosswalk")),
                "Candidate.Status": "officially audited blood biomarker crosswalk candidate",
                "Harmonization.Status": detail or "continuous laboratory measure; verify wave-specific comparability",
                "Review.Flag": "laboratory sub-sample; use the wave-specific blood weight and preserve assay/release-note caveats",
            })
            existing_keys.add(key)

    # Preserve the audited objective-measurement component fields (repeat
    # readings, timed trials, and anthropometry) in the broad searchable
    # catalog. The concept crosswalk remains the place to fold these into
    # analysis-ready measures; component fields are not separate outcomes.
    objective_path = Path(__file__).resolve().parents[1] / "audit" / "objective_measurement_crosswalk_v1.csv"
    if objective_path.exists():
        objective = pd.read_csv(objective_path, dtype=str, encoding="utf-8-sig").fillna("")
        domains = {
            "systolic_bp": ("blood pressure", "blood pressure and pulse"),
            "diastolic_bp": ("blood pressure", "blood pressure and pulse"),
            "pulse_rate": ("blood pressure", "blood pressure and pulse"),
            "peak_flow": ("physical function", "strength, mobility, lung function, and performance"),
            "grip_strength": ("physical function", "strength, mobility, lung function, and performance"),
            "balance_semi_tandem": ("physical function", "strength, mobility, lung function, and performance"),
            "balance_full_tandem": ("physical function", "strength, mobility, lung function, and performance"),
            "balance_side_by_side": ("physical function", "strength, mobility, lung function, and performance"),
            "walking_speed": ("physical function", "strength, mobility, lung function, and performance"),
            "repeated_chair_stand": ("physical function", "strength, mobility, lung function, and performance"),
            "standing_height": ("anthropometric", "body size and anthropometry"),
            "arm_length": ("anthropometric", "body size and anthropometry"),
            "knee_height": ("anthropometric", "body size and anthropometry"),
            "body_weight": ("anthropometric", "body size and anthropometry"),
            "waist_circumference": ("anthropometric", "body size and anthropometry"),
        }
        for item in objective.to_dict(orient="records"):
            wave = str(item.get("wave", "")).strip()
            concept = str(item.get("concept_id", "")).strip()
            if wave not in WAVES or concept not in domains:
                continue
            category, subcategory = domains[concept]
            module = str(item.get("module", "Biomarker")).strip()
            for code in str(item.get("variables", "")).split(";"):
                code = code.strip()
                if not code:
                    continue
                key = (wave, code.lower(), "p", category, subcategory)
                if key in existing_keys:
                    continue
                raw = source[(source.wave == wave) & (source.variable.str.lower() == code.lower())]
                description = raw.iloc[0].variable_label if not raw.empty else f"{item.get('concept_label', concept)}: {code}"
                archive = raw.iloc[0].source if not raw.empty else str(item.get("source_document", "official objective measurement crosswalk"))
                detail = "; ".join(filter(None, [
                    str(item.get("value_semantics", "")).strip(),
                    str(item.get("source_status", "")).strip(),
                    f"official source: {item.get('source_document', '').strip()}" if str(item.get("source_document", "")).strip() else "",
                ]))
                outputs.append({
                    "Variable.Name": code, "Variable.Description": description,
                    "Data.File.Name": module, "Data.File.Description": module.replace("_", " "),
                    "Begin.Year": wave, "EndYear": wave, "Component": module,
                    "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
                    "epcf": "p", "category": category, "subcategory": subcategory,
                    "Source.Wave": wave, "Source.Archive": archive,
                    "Candidate.Status": "officially audited objective measurement crosswalk candidate",
                    "Harmonization.Status": detail or "component field of an objective measurement; derive concept using the audited crosswalk",
                    "Review.Flag": "repeated readings/trials or protocol component; do not count each source field as a distinct phenotype",
                })
                existing_keys.add(key)

    # Curated single-wave item found in the 2018 questionnaire. Keep it out of
    # automated cognition matching: this is a subjective environmental
    # perception item, not an objective exposure measurement or phenotype.
    air_quality = source[(source.wave == "2018") & (source.variable.str.lower() == "dc046_w4")]
    if not air_quality.empty:
        row = air_quality.iloc[0]
        outputs.append({
            "Variable.Name": row.variable,
            "Variable.Description": row.variable_label,
            "Data.File.Name": row.module,
            "Data.File.Description": "2018 individual questionnaire; satisfaction with air quality",
            "Begin.Year": "2018",
            "EndYear": "2018",
            "Component": row.module,
            "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
            "epcf": "e",
            "category": "environmental perception",
            "subcategory": "self-reported air-quality satisfaction",
            "Source.Wave": "2018",
            "Source.Archive": row.source,
            "Candidate.Status": "manually curated from official 2018 questionnaire and codebook",
            "Harmonization.Status": "single-wave ordinal satisfaction item; subjective perception, not ambient concentration; no cross-wave comparable series identified",
            "Review.Flag": "retain the five original response categories; do not interpret as measured pollution or combine with objective exposure estimates",
            "Value.Labels": "1=Completely satisfied; 2=Very satisfied; 3=Somewhat satisfied; 4=Not very satisfied; 5=Not at all satisfied",
            "Value.Label.Source": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; audit/charls_catalog_count_interpretation_v0.md",
        })

    # 2011 BA005 is a binary weekly-return item. Its official questionnaire
    # and CodeBook agree; keep it separate from the three-level 2013 item.
    return_home_2011 = source[(source.wave == "2011") & (source.variable.str.lower() == "ba005")]
    if not return_home_2011.empty:
        row = return_home_2011.iloc[0]
        outputs.append({
            "Variable.Name": row.variable,
            "Variable.Description": row.variable_label,
            "Data.File.Name": row.module,
            "Data.File.Description": "2011 individual questionnaire; return-home frequency while attending school/work away",
            "Begin.Year": "2011",
            "EndYear": "2011",
            "Component": row.module,
            "Use.Constraints": "CHARLS applicant data; access and publication governed by official agreement",
            "epcf": "e",
            "category": "social determinants",
            "subcategory": "residential and mobility context",
            "Source.Wave": "2011",
            "Source.Archive": row.source,
            "Candidate.Status": "official questionnaire/CodeBook item identity reviewed; single-wave candidate; denominator and eligibility require review",
            "Harmonization.Status": "Binary weekly-return status; not an ordinal return-frequency scale and not harmonized with 2013",
            "Review.Flag": "candidate only; preserve binary coding, wave-specific wording, and applicable respondent denominator",
        })

    # Reuse only field-level value labels already reviewed against official
    # CHARLS codebooks/questionnaires in the domain audits. Candidate labels
    # without an explicit reviewed status stay blank in the E/P directory.
    root = Path(__file__).resolve().parents[1]
    label_map: dict[tuple[str, str], set[tuple[str, str]]] = {}

    def add_reviewed_labels(file: str, wave_col: str, code_col: str, label_col: str,
                            status_col: str | None = None, source_col: str | None = None,
                            accepted_status: re.Pattern[str] | None = None) -> None:
        path = root / "audit" / file
        if not path.exists():
            return
        tab = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
        for item in tab.to_dict(orient="records"):
            label = str(item.get(label_col, "")).strip()
            status = str(item.get(status_col, "")).strip() if status_col else ""
            if not label or (accepted_status and not accepted_status.search(status)):
                continue
            wave = str(item.get(wave_col, "")).strip()
            code = str(item.get(code_col, "")).strip().lower()
            if not wave or not code:
                continue
            ref = str(item.get(source_col, "")).strip() if source_col else f"audit/{file}"
            label_map.setdefault((wave, code), set()).add((label, ref or f"audit/{file}"))

    official_review = re.compile(r"official codebook (?:item )?response labels reviewed", re.I)
    add_reviewed_labels("behavior_exposure_variable_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official codebook response labels reviewed|official selector code reviewed;", re.I))
    add_reviewed_labels("personal_income_exposure_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire/codebook response labels reviewed|official questionnaire response categories transcribed|official questionnaire response categories; frequencies omitted|official Codebook response labels reviewed; frequencies omitted", re.I))
    add_reviewed_labels("health_symptom_variable_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official codebook response labels reviewed|official questionnaire response scale verified", re.I))
    add_reviewed_labels("functional_concept_variable_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official codebook response labels reviewed", re.I))
    add_reviewed_labels("health_work_limitation_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"matched to wave-specific official codebook", re.I))
    add_reviewed_labels("mood_item_variable_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official codebook item response labels reviewed", re.I))
    add_reviewed_labels("loneliness_exposure_role_mapping_v1.csv", "wave", "code", "value_labels", "mapping_status", "value_label_source", re.compile(r"officially reviewed item-level response labels", re.I))
    add_reviewed_labels("cognition_item_variable_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"(?:official (?:\d{4} )?codebook|20\d{2} (?:official )?codebook)", re.I))
    add_reviewed_labels("chronic_disease_ancillary_variable_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official codebook response labels reviewed; option index only|official 2011 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|official 2013 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|official 2015 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE", re.I))
    # These labels were also transcribed from wave-specific official Codebooks.
    # Keep route/conditional-option caveats in the mapping and analysis locks;
    # importing a display label does not make these fields analysis-ready.
    add_reviewed_labels("chronic_disease_ancillary_variable_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official (?:2011|2020) Codebook response categories transcribed; frequencies omitted; self-awareness route retained; release coding and eligible denominator require validation|official 2020 questionnaire/Codebook response labels reviewed; prior-wave route retained; frequencies excluded|official codebook response labels; prior-wave self-awareness/preload route retained; frequencies excluded|official wave codebook category verified; selected option only; frequencies excluded|official 2018 Codebook response categories transcribed; frequencies omitted|official (?:2013|2015|2018) Codebook response categories transcribed; frequencies omitted; (?:disease-specific|prior-interview recall) route retained; release coding and eligible denominator require validation|official 2011 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|official 2013 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|official 2015 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE", re.I))
    add_reviewed_labels("pension_value_label_review_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", official_review)
    add_reviewed_labels("pension_codebook_value_labels_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official answer labels transcribed; frequencies omitted", re.I))
    add_reviewed_labels("pension_participation_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "official_source", re.compile(r"official 2011 questionnaire and codebook reviewed; candidate mapping", re.I))
    add_reviewed_labels("pension_eligibility_2015_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "official_source", re.compile(r"2015 questionnaire and CodeBook labels/routes reviewed; candidate mapping", re.I))
    add_reviewed_labels("life_insurance_exposure_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire/codebook response categories; frequencies omitted", re.I))
    add_reviewed_labels("pension_subsidy_delivery_2015_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "source_document", re.compile(r"official questionnaire and CodeBook option label matched|option 3 conflict marked DO NOT ANALYZE", re.I))
    add_reviewed_labels("work_exposure_value_labels_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official .*response labels|official questionnaire response categories; codebook frequencies omitted|official selected-option label; checkbox slot, absence is not a negative response|official questionnaire checkbox menu and codebook slot coding; frequencies omitted; absence is not a negative response outside the routed checklist|official questionnaire categories; frequencies omitted; FC020 multiple-job main-work route or FC021 single nonfarm-job route|full questionnaire menu transcribed without frequencies; 2011 codebook omits FL014 and later codebook menus may omit unobserved categories; not-currently-working prior-job route|official questionnaire categories; frequencies omitted; 2011 question wording controls its scope|full official questionnaire response menu transcribed without frequencies; current employer firm route|official questionnaire response categories transcribed without frequencies; continuity of the specific prior-wave work activity|official 2020 questionnaire response categories; frequencies omitted; conditional work-history transition route|official questionnaire categories transcribed without frequencies; preserve three-category employment/family-business status|official questionnaire/codebook categories; frequencies omitted; current employer benefit route|wave-specific official questionnaire categories transcribed without frequencies; retrospective first-workplace location|official questionnaire categories; frequencies omitted; conditional agricultural-wage/other-job temporary-absence route|DO NOT ANALYZE; official 2011 baseline questionnaire option label", re.I))
    add_reviewed_labels("housing_value_label_review_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", official_review)
    add_reviewed_labels("household_asset_exposure_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire/codebook response labels reviewed|official questionnaire response categories transcribed", re.I))
    add_reviewed_labels("household_covid_economic_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "source_document", re.compile(r"candidate; questionnaire and Codebook labels reviewed; validate routes and eligible denominator in approved data", re.I))
    add_reviewed_labels("household_lending_debt_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire response labels reviewed; frequencies omitted; wave-specific", re.I))
    add_reviewed_labels("pension_2011_nrsp_detail_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "official_source", re.compile(r"2011 questionnaire/CodeBook item reviewed; candidate mapping", re.I))
    add_reviewed_labels("old_age_support_expectation_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "official_source", re.compile(r"2011 questionnaire and CodeBook response labels reviewed; candidate mapping", re.I))
    # This hand-audited mapping cites the official codebook/questionnaire by
    # repository-relative path; accept those explicit source paths as reviewed
    # evidence too, so DA009's 1=Year/2=Age coding is searchable in the catalog.
    add_reviewed_labels("chronic_disease_concept_variable_mapping_v2.csv", "Source.Wave", "Source.Variable", "Value.Labels", "Official.Source", "Official.Source", re.compile(r"CHARLS official|sources_official|CHARLS_\d{4}_Codebook", re.I))
    add_reviewed_labels("chronic_disease_ancillary_variable_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official response labels reviewed", re.I))
    add_reviewed_labels("chronic_disease_management_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official wave codebook/questionnaire response semantics reviewed", re.I))
    add_reviewed_labels("healthcare_access_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source")
    add_reviewed_labels("community_exposure_value_labels_v1.csv", "wave", "code", "value_labels",
                        "value_label_status", "value_label_source",
                        re.compile(r"official (?:codebook response labels|questionnaire seven-point ordinal scale anchors reviewed; codebook numeric categories only|questionnaire semantics reconciled with codebook response categories); frequencies omitted", re.I))
    add_reviewed_labels("housing_value_label_review_v1.csv", "wave", "code", "value_labels",
                        "value_label_status", "value_label_source",
                        re.compile(r"official codebook response categories reviewed; frequencies and percentages omitted; preserve wave-specific coding", re.I))
    add_reviewed_labels("social_exposure_crosswalk_v1.csv", "wave", "code", "value_semantics", "mapping_status", None, re.compile(r"Official codebook response labels reviewed", re.I))
    add_reviewed_labels("social_exposure_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "value_label_source", re.compile(r"Official questionnaire/codebook yes-no response categories reviewed", re.I))
    add_reviewed_labels("measurement_protocol_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "source_document", re.compile(r"official questionnaire and codebook mapping|2018 questionnaire/codebook verified; C metadata only|2018 questionnaire date-component protocol verified; C metadata", re.I))
    add_reviewed_labels("demographic_social_exposure_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire and codebook response labels reviewed", re.I))
    add_reviewed_labels("parent_education_exposure_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official wave questionnaire and codebook response categories reviewed", re.I))
    add_reviewed_labels("parent_roster_education_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official wave questionnaire and Codebook response categories reviewed; frequency counts omitted", re.I))
    add_reviewed_labels("sibling_record_context_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire/codebook categories reviewed; codebook frequencies omitted", re.I))
    add_reviewed_labels("parent_roster_context_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire and codebook categories reviewed; frequencies omitted", re.I))
    add_reviewed_labels("parent_marital_ethnicity_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire and Codebook categories reviewed; frequency counts omitted", re.I))
    add_reviewed_labels("household_transfer_receipt_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire/Codebook option label reviewed; frequencies omitted", re.I))
    add_reviewed_labels("household_transfer_none_option_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire/Codebook option label reviewed; frequencies omitted", re.I))
    add_reviewed_labels("social_context_remainder_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire and codebook categories reviewed; frequency counts omitted", re.I))
    add_reviewed_labels("stroke_timing_metadata_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "source_document", re.compile(r"official codebook/questionnaire response-format field", re.I))
    add_reviewed_labels("cancer_site_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official codebook (?:category verified|reports no observed categories|shows 0=No)", re.I))
    add_reviewed_labels("disability_history_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official codebook|official (?:2018 )?codebook", re.I))
    add_reviewed_labels("chronic_disease_ancillary_variable_mapping_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire confirms response options", re.I))
    add_reviewed_labels("assistive_device_phenotype_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "value_label_source", re.compile(r"official questionnaire and codebook response option labels verified", re.I))
    add_reviewed_labels("adult_education_training_exposure_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "source_archive", re.compile(r"official questionnaire/codebook field identified", re.I))
    add_reviewed_labels("formal_schooling_lifecourse_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "source_archive", re.compile(r"official questionnaire and codebook field reviewed", re.I))
    add_reviewed_labels("psych_treatment_2011_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "official_source", re.compile(r"2011 questionnaire and CodeBook response label reviewed", re.I))
    add_reviewed_labels("partner_context_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "source_archive", re.compile(r"official questionnaire and codebook reviewed", re.I))
    add_reviewed_labels("hukou_lifecourse_exposure_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official wave codebook response labels reviewed", re.I))
    add_reviewed_labels("hukou_recent_change_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official wave questionnaire/codebook labels reviewed; frequencies omitted", re.I))
    add_reviewed_labels("residential_settlement_exposure_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official wave questionnaire and codebook categories reviewed", re.I))
    add_reviewed_labels("home_return_frequency_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official questionnaire/codebook response labels reviewed; frequencies omitted", re.I))
    add_reviewed_labels("home_return_frequency_value_label_review_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official (?:codebook labels|questionnaire categories|questionnaire and codebook labels) reviewed|official questionnaire and codebook agree", re.I))
    add_reviewed_labels("housing_owner_relation_value_label_review_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official Codebook response labels complete", re.I))
    add_reviewed_labels("marital_history_exposure_crosswalk_v1.csv", "wave", "code", "value_labels", "value_label_status", "value_label_source", re.compile(r"official wave questionnaire/codebook item definition reviewed", re.I))
    add_reviewed_labels("residual_behavior_exposure_crosswalk_v1.csv", "wave", "code", "value_labels", "mapping_status", "source_archive", re.compile(r"official questionnaire/codebook field identified", re.I))
    # Keep this confirmed questionnaire/Codebook conflict searchable while
    # retaining its explicit DO NOT ANALYZE status; it is not a harmonized label.
    work_labels = root / "audit" / "work_exposure_value_labels_v1.csv"
    if work_labels.exists():
        work = pd.read_csv(work_labels, dtype=str, encoding="utf-8-sig").fillna("")
        for item in work.to_dict(orient="records"):
            if item.get("wave") == "2011" and item.get("code", "").lower() == "fb010" and item.get("value_labels"):
                label_map.setdefault(("2011", "fb010"), set()).add((item["value_labels"], item.get("value_label_source", "audit/work_exposure_value_labels_v1.csv")))
    # Fuel response categories are an explicit wave-specific codebook table;
    # aggregate by the actual field, never by the numeric category alone.
    fuel_path = root / "audit" / "cooking_fuel_crosswalk_v1.csv"
    if fuel_path.exists():
        fuel = pd.read_csv(fuel_path, dtype=str, encoding="utf-8-sig").fillna("")
        for (wave, code), group in fuel.groupby(["wave", "raw_variable"]):
            labels = sorted({f"{r.raw_code}={r.codebook_label}" for r in group.itertuples(index=False) if r.raw_code and r.codebook_label})
            if labels:
                label_map.setdefault((str(wave), str(code).lower()), set()).add(("; ".join(labels), "audit/cooking_fuel_crosswalk_v1.csv; official wave codebooks"))

    # Disease-specific examinations/advice have dedicated conditional
    # management concepts. Remove their broad keyword-only disease rows to
    # avoid presenting one source code as both a diagnosis and management.
    management_path = root / "audit" / "chronic_disease_management_crosswalk_v1.csv"
    if management_path.exists():
        management = pd.read_csv(management_path, dtype=str, encoding="utf-8-sig").fillna("")
        management_keys = {(str(r.wave), str(r.code).lower()) for r in management.itertuples(index=False)}
        outputs = [item for item in outputs if not (
            (str(item.get("Source.Wave", "")), str(item.get("Variable.Name", "")).lower()) in management_keys
            and not (item.get("epcf") == "p" and item.get("category") == "chronic disease ancillary")
        )]

    # These fields describe the instrument rather than a respondent-level
    # phenotype, or are preloaded prior-wave states. Keep them in the raw
    # source catalog, but do not expose them as same-wave P candidates.
    excluded_chronic = re.compile(r"^(xchrodistype|zdiagnosed|zdisease|zselfdisease)_", re.I)
    outputs = [item for item in outputs if not (
        item.get("category") == "chronic disease"
        and excluded_chronic.search(str(item.get("Variable.Name", "")))
    )]
    # DA008_W2_1_i records how a respondent knew about the disease indexed
    # by DA007; the explicit ancillary concept should replace the generic
    # keyword-only diagnosis-category row for the same wave and field.
    awareness_path = root / "audit" / "chronic_disease_ancillary_variable_mapping_v1.csv"
    if awareness_path.exists():
        awareness = pd.read_csv(awareness_path, dtype=str, encoding="utf-8-sig").fillna("")
        awareness_keys = {(str(r.wave), str(r.code).lower()) for r in awareness.itertuples(index=False)
                          if str(r.code).lower().startswith("da008_w2_1_")}
        outputs = [item for item in outputs if not (
            (str(item.get("Source.Wave", "")), str(item.get("Variable.Name", "")).lower()) in awareness_keys
            and item.get("category") == "chronic disease"
        )]
    # DA044s15 is the questionnaire's “None of these” response option, not a
    # disease phenotype. Keep it documented in the item audit, but do not show
    # it as a P-catalog endpoint.
    outputs = [item for item in outputs if str(item.get("Variable.Name", "")).lower() != "da044s15"]
    # A broad disease keyword also matches the generic health/symptoms rule;
    # present infectious-history fields once in the disease-history category.
    outputs = [item for item in outputs if not (
        str(item.get("Variable.Name", "")).lower().startswith("da044s")
        and item.get("category") == "health and symptoms"
    )]

    hukou_frames = [pd.read_csv(root / "audit" / name, dtype=str, encoding="utf-8-sig") for name in ("hukou_lifecourse_exposure_crosswalk_v1.csv", "hukou_recent_change_crosswalk_v1.csv")]
    hukou_keys = {(str(r.wave), str(r.code).lower()) for frame in hukou_frames for r in frame.itertuples(index=False)}
    settlement_keys = {(str(r.wave), str(r.code).lower()) for r in pd.read_csv(root / "audit" / "residential_settlement_exposure_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").itertuples(index=False)}
    marital_keys = {(str(r.wave), str(r.code).lower()) for r in pd.read_csv(root / "audit" / "marital_history_exposure_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").itertuples(index=False)}
    schooling_keys = {(str(r.wave), str(r.code).lower()) for r in pd.read_csv(root / "audit" / "formal_schooling_lifecourse_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").itertuples(index=False)}
    partner_keys = {(str(r.wave), str(r.code).lower()) for r in pd.read_csv(root / "audit" / "partner_context_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").itertuples(index=False)}
    for item in outputs:
        key = (str(item.get("Begin.Year", "")), str(item.get("Variable.Name", "")).lower())
        if item.get("epcf") == "e" and key in hukou_keys:
            item["subcategory"] = "hukou history and transitions"
        if item.get("epcf") == "e" and key in settlement_keys:
            item["subcategory"] = "residential settlement context"
        if item.get("epcf") == "e" and key in marital_keys:
            item["subcategory"] = "marital history and marriage transfers"
        if item.get("epcf") == "e" and key in schooling_keys:
            item["subcategory"] = "formal schooling history and timing"
        if item.get("epcf") == "e" and key in partner_keys:
            item["subcategory"] = "marital status and partner context"

    # Once a wave/module/role has an audited concept mapping, a broad
    # keyword-generated row for that same field is redundant and can expose a
    # conflicting generic category. Keep the audited mapping as the catalog
    # representation; other independently reviewed roles remain eligible.
    audited_field_roles = {
        (str(item.get("Source.Wave", "")), str(item.get("Variable.Name", "")).lower(),
         str(item.get("Data.File.Name", "")).lower(), str(item.get("epcf", "")))
        for item in outputs
        if item.get("epcf") in {"e", "p"}
        and re.search(r"audited|concept-source crosswalk", str(item.get("Candidate.Status", "")), re.I)
    }
    outputs = [item for item in outputs if not (
        str(item.get("Candidate.Status", "")).startswith("automated discovery")
        and (str(item.get("Source.Wave", "")), str(item.get("Variable.Name", "")).lower(),
             str(item.get("Data.File.Name", "")).lower(), str(item.get("epcf", ""))) in audited_field_roles
    )]

    # CHARLS 2018 DC031 checkbox fields record test-administration conditions
    # (verbal administration, interruption, reading difficulty, or none), not
    # respondent cognition. Keep them discoverable as metadata, but out of E/P.
    for item in outputs:
        cognition_code = str(item.get("Variable.Name", "")).lower()
        cognition_wave = str(item.get("Source.Wave", ""))
        cognition_metadata = (
            cognition_code in {"dc028_w4_1", *(f"dc031_w4_s{i}" for i in range(1, 5))}
            or re.fullmatch(r"dc014_w4_[1-5]", cognition_code)
            or (cognition_code == "dc024" and cognition_wave in {"2011", "2013", "2015", "2018"})
            or (cognition_code == "dc008" and cognition_wave == "2020")
        )
        if cognition_wave in {"2011", "2013", "2015", "2018", "2020"} and cognition_metadata:
            item["epcf"] = "c"
            item["category"] = "measurement metadata"
            if cognition_code == "dc024" or (cognition_wave == "2020" and cognition_code == "dc008"):
                item["subcategory"] = "cognitive-test instrument-use metadata"
                item["Candidate.Status"] = f"official {cognition_wave} cognition instrument-use metadata"
                item["Harmonization.Status"] = "records whether paper or other instruments were used for the math task; not cognitive performance"
                item["Review.Flag"] = "exclude from E/P association matrix; use only to describe or adjust for measurement conditions under a defined estimand"
            else:
                item["subcategory"] = "cognitive-test administration and nonresponse metadata"
                item["Candidate.Status"] = f"official {cognition_wave} cognition instrument administration/nonresponse metadata"
                item["Harmonization.Status"] = "records refusal/nonresponse reason or test administration conditions; not a cognitive performance phenotype"
                item["Review.Flag"] = "exclude from E/P association matrix; may be used to describe missingness and measurement conditions"

    # DA020 is a current-treatment multi-select, not an exposure. The broad
    # keyword rule can misclassify the sleeping-pill option as an exposure;
    # the reviewed item audit establishes the P role for all four options.
    psych_treatment_codes = {f"da020s{i}" for i in range(1, 5)}
    outputs = [item for item in outputs if not (
        str(item.get("Source.Wave", "")) == "2011"
        and str(item.get("Variable.Name", "")).lower() in psych_treatment_codes
        and item.get("epcf") == "e"
    )]
    outputs = [item for item in outputs if not (
        str(item.get("Source.Wave", "")) == "2011"
        and str(item.get("Variable.Name", "")).lower() in psych_treatment_codes
        and str(item.get("Candidate.Status", "")).startswith("automated discovery")
    )]
    subsidy_delivery_codes = {"ga004_w3s1", "ga004_w3s2", "ga004_w3s3"} | {
        f"ga004_w3_1s{i}" for i in range(1, 8)
    }
    outputs = [item for item in outputs if not (
        str(item.get("Source.Wave", "")) == "2015"
        and str(item.get("Variable.Name", "")).lower() in subsidy_delivery_codes
        and str(item.get("Candidate.Status", "")).startswith("automated discovery")
    )]

    fields = ["Variable.Name", "Variable.Description", "Data.File.Name", "Data.File.Description", "Begin.Year", "EndYear", "Component", "Use.Constraints", "epcf", "category", "subcategory", "Source.Wave", "Source.Archive", "Candidate.Status", "Harmonization.Status", "Review.Flag", "Value.Labels", "Value.Label.Source", "Value.Label.Review"]
    out = pd.DataFrame(outputs, columns=fields).drop_duplicates()
    # Automated discovery and an audited domain crosswalk can point to the
    # same source field and classification. Keep the audited row so the site
    # shows its route/measurement caveat once instead of duplicate entries.
    source_identity = ["Source.Wave", "Variable.Name", "Data.File.Name", "epcf", "category", "subcategory"]
    out["_audit_priority"] = ~out["Candidate.Status"].str.contains(
        r"audited|concept-source crosswalk", case=False, regex=True, na=False
    )
    out = (out.sort_values("_audit_priority")
           .drop_duplicates(source_identity, keep="first")
           .drop(columns=["_audit_priority"]))
    # xfgsample selects respondents routed to the 2020 FG pandemic work
    # module. Keep it searchable as routing metadata, never as an exposure;
    # FF005 belongs to the FF path and is not assigned this selector.
    selection = out["Variable.Name"].str.lower().eq("xfgsample") & out["Source.Wave"].astype(str).eq("2020")
    out.loc[selection, "epcf"] = "c"
    out.loc[selection, "category"] = "measurement metadata"
    out.loc[selection, "subcategory"] = "2020 pandemic work-module selection flag"
    out.loc[selection, "Candidate.Status"] = "official codebook selection flag; associated with the FG pandemic work module"
    out.loc[selection, "Harmonization.Status"] = "binary respondent-selection metadata; does not measure work exposure"
    out.loc[selection, "Review.Flag"] = "use to preserve the 2020 FG module universe for FG001–FG009; not an exposure and not presumed to govern FF005"
    reviewed_labels: list[str] = []
    reviewed_sources: list[str] = []
    label_conflicts: list[str] = []
    declared_conflicts: set[tuple[str, str]] = set()
    home_return_review = root / "audit" / "home_return_frequency_value_label_review_v1.csv"
    if home_return_review.exists():
        review = pd.read_csv(home_return_review, dtype=str, encoding="utf-8-sig").fillna("")
        declared_conflicts = {
            (str(r.wave), str(r.code).lower())
            for r in review.itertuples(index=False)
            if "conflict" in str(r.value_label_status).lower()
        }
    # Exact wave/code adjudications for documented pension label conflicts.
    # Prefer the reviewed CodeBook wording for semantic/translation variants;
    # leave genuine questionnaire-versus-CodeBook category conflicts locked.
    pension_adjudication = root / "audit" / "pension_label_conflict_adjudication_v1.csv"
    if pension_adjudication.exists():
        decisions = pd.read_csv(pension_adjudication, dtype=str, encoding="utf-8-sig").fillna("")
        for decision in decisions.itertuples(index=False):
            key = (str(decision.wave), str(decision.code).lower())
            if str(decision.decision_status) in {"resolved_official_codebook_precedence", "resolved_questionnaire_authority_codebook_category_table_partial"} and decision.value_labels:
                label_map[key] = {(str(decision.value_labels), str(decision.value_label_source))}
            elif str(decision.decision_status) == "unresolved_source_conflict":
                declared_conflicts.add(key)
    for _, row in out.iterrows():
        key = (str(row["Source.Wave"]), str(row["Variable.Name"]).lower())
        entries = label_map.get(key, set())
        labels = sorted({label for label, _ in entries})
        refs = sorted({ref for _, ref in entries})
        reviewed_labels.append(" | ".join(labels) if len(labels) == 1 else "")
        reviewed_sources.append("; ".join(refs) if len(labels) == 1 else "")
        label_conflicts.append("conflicting reviewed labels; manual review required" if len(labels) > 1 or key in declared_conflicts else "")
    out["Value.Labels"] = [existing or reviewed for existing, reviewed in zip(out["Value.Labels"].fillna(""), reviewed_labels)]
    out["Value.Label.Source"] = [existing or reviewed for existing, reviewed in zip(out["Value.Label.Source"].fillna(""), reviewed_sources)]
    out["Value.Label.Review"] = ["conflict" if conflict else ("officially reviewed" if reviewed or source else "not yet reviewed") for conflict, reviewed, source in zip(label_conflicts, reviewed_labels, out["Value.Label.Source"])]
    awareness_review_path = root / "audit" / "chronic_disease_ancillary_variable_mapping_v1.csv"
    if awareness_review_path.exists():
        awareness_review = pd.read_csv(awareness_review_path, dtype=str, encoding="utf-8-sig").fillna("")
        awareness_review = awareness_review[
            awareness_review["value_label_status"].str.startswith("official questionnaire confirms response options")
        ]
        for item in awareness_review.to_dict(orient="records"):
            selected = (
                out["Source.Wave"].astype(str).eq(str(item.get("wave", "")))
                & out["Variable.Name"].str.lower().eq(str(item.get("code", "")).lower())
            )
            out.loc[selected, "Value.Label.Review"] = str(item["value_label_status"])
    # Bring the domain audit's field-level review state into the main E/P
    # catalogue even when a continuous measure has no discrete value labels.
    # This prevents reviewed counts, units, and conditional routes from being
    # presented as generic unreviewed categorical labels.
    healthcare_review_path = root / "audit" / "healthcare_access_crosswalk_v1.csv"
    if healthcare_review_path.exists():
        healthcare_review = pd.read_csv(healthcare_review_path, dtype=str, encoding="utf-8-sig").fillna("")
        for item in healthcare_review.to_dict(orient="records"):
            wave = str(item.get("wave", "")).strip()
            code = str(item.get("code", "")).strip().lower()
            status = str(item.get("value_label_status", "")).strip()
            source = str(item.get("value_label_source", "")).strip()
            if not wave or not code or not status:
                continue
            selected = (
                out["Source.Wave"].astype(str).eq(wave)
                & out["Variable.Name"].str.lower().eq(code)
                & out["category"].eq("healthcare access")
            )
            unlocked = selected & ~out["Value.Label.Review"].astype(str).str.contains("conflict", case=False, na=False)
            out.loc[unlocked, "Value.Label.Review"] = status
            if source:
                missing_source = unlocked & out["Value.Label.Source"].fillna("").eq("")
                out.loc[missing_source, "Value.Label.Source"] = source
    # Preserve the explicit wave-specific audit wording for housing labels;
    # the generic label merge above establishes provenance and conflicts.
    housing_label_path = root / "audit" / "housing_value_label_review_v1.csv"
    if housing_label_path.exists():
        housing_labels = pd.read_csv(housing_label_path, dtype=str, encoding="utf-8-sig").fillna("")
        for item in housing_labels.to_dict(orient="records"):
            labels = str(item.get("value_labels", "")).strip()
            if not labels:
                continue
            selected = (
                out["Source.Wave"].astype(str).eq(str(item.get("wave", "")))
                & out["Variable.Name"].str.lower().eq(str(item.get("code", "")).lower())
            )
            conflict = selected & out["Value.Labels"].ne("") & out["Value.Labels"].ne(labels)
            out.loc[conflict, "Value.Label.Review"] = "conflict"
            blank = selected & out["Value.Labels"].eq("")
            out.loc[blank, "Value.Labels"] = labels
            out.loc[blank, "Value.Label.Source"] = str(item.get("value_label_source", ""))
            out.loc[blank, "Value.Label.Review"] = str(item.get("value_label_status", "Official Codebook response categories reviewed"))
    # Preserve user-facing interpretation warnings for checkbox/route labels.
    # A label being correct does not imply that an unselected slot is a No.
    for filename, status_pattern in (
        ("work_exposure_value_labels_v1.csv", re.compile(r"official selected-option label; checkbox slot, absence is not a negative response|official questionnaire checkbox menu and codebook slot coding; frequencies omitted; absence is not a negative response outside the routed checklist|official questionnaire categories; frequencies omitted; FC020 multiple-job main-work route or FC021 single nonfarm-job route|full questionnaire menu transcribed without frequencies; 2011 codebook omits FL014 and later codebook menus may omit unobserved categories; not-currently-working prior-job route|official questionnaire categories; frequencies omitted; 2011 question wording controls its scope|full official questionnaire response menu transcribed without frequencies; current employer firm route|official questionnaire response categories transcribed without frequencies; continuity of the specific prior-wave work activity|official 2020 questionnaire response categories; frequencies omitted; conditional work-history transition route|official questionnaire categories transcribed without frequencies; preserve three-category employment/family-business status|official questionnaire/codebook categories; frequencies omitted; current employer benefit route|wave-specific official questionnaire categories transcribed without frequencies; retrospective first-workplace location|official questionnaire categories; frequencies omitted; conditional agricultural-wage/other-job temporary-absence route|DO NOT ANALYZE; official 2011 baseline questionnaire option label", re.I)),
        ("behavior_exposure_variable_mapping_v1.csv", re.compile(r"official selector code reviewed;", re.I)),
        ("chronic_disease_ancillary_variable_mapping_v1.csv", re.compile(r"official (?:2011|2020) Codebook response categories transcribed; frequencies omitted; self-awareness route retained; release coding and eligible denominator require validation|official 2020 questionnaire/Codebook response labels reviewed; prior-wave route retained; frequencies excluded|official codebook response labels; prior-wave self-awareness/preload route retained; frequencies excluded|official wave codebook category verified; selected option only; frequencies excluded|official 2018 Codebook response categories transcribed; frequencies omitted|official (?:2013|2015|2018) Codebook response categories transcribed; frequencies omitted; (?:disease-specific|prior-interview recall) route retained; release coding and eligible denominator require validation|official 2011 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|official 2013 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE|official 2015 Codebook selected-option category transcribed; frequencies omitted; unselected storage and routed denominator unverified; DO NOT ANALYZE", re.I)),
        ("housing_value_label_review_v1.csv", re.compile(r"official codebook response categories reviewed; frequencies and percentages omitted; preserve wave-specific coding", re.I)),
    ):
        status_path = root / "audit" / filename
        if not status_path.exists():
            continue
        status_rows = pd.read_csv(status_path, dtype=str, encoding="utf-8-sig").fillna("")
        for item in status_rows.to_dict(orient="records"):
            status = str(item.get("value_label_status", "")).strip()
            labels = str(item.get("value_labels", "")).strip()
            if not labels or not status_pattern.search(status):
                continue
            selected = (
                out["Source.Wave"].astype(str).eq(str(item.get("wave", "")))
                & out["Variable.Name"].str.lower().eq(str(item.get("code", "")).lower())
                & out["Value.Labels"].eq(labels)
                & out["Value.Label.Review"].ne("conflict")
            )
            out.loc[selected, "Value.Label.Review"] = status
    # The codebook categories remain searchable, but their provenance conflict
    # must survive the aggregate catalog's generic review-status reduction.
    fb010_status_path = root / "audit" / "work_exposure_value_labels_v1.csv"
    if fb010_status_path.exists():
        work_labels = pd.read_csv(fb010_status_path, dtype=str, encoding="utf-8-sig").fillna("")
        for item in work_labels.to_dict(orient="records"):
            if item.get("wave") != "2011" or item.get("code", "").lower() != "fb010":
                continue
            selected = out["Source.Wave"].astype(str).eq("2011") & out["Variable.Name"].str.lower().eq("fb010")
            out.loc[selected, "Value.Label.Review"] = item.get("value_label_status", "DO NOT ANALYZE; questionnaire/Codebook coding unresolved")
            out.loc[selected, "Value.Label.Source"] = item.get("value_label_source", "")

    fl020_status_path = root / "audit" / "work_exposure_value_labels_v1.csv"
    if fl020_status_path.exists():
        work_labels = pd.read_csv(fl020_status_path, dtype=str, encoding="utf-8-sig").fillna("")
        for item in work_labels.to_dict(orient="records"):
            if item.get("wave") != "2011" or not re.fullmatch(r"fl020s(?:[1-9]|1[0-6])", item.get("code", "").lower()):
                continue
            selected = out["Source.Wave"].astype(str).eq("2011") & out["Variable.Name"].str.lower().eq(item["code"].lower())
            out.loc[selected, "Value.Label.Review"] = item.get("value_label_status", "DO NOT ANALYZE; checkbox coding unresolved")
            out.loc[selected, "Value.Label.Source"] = item.get("value_label_source", "")
    covid_status_path = root / "audit" / "household_covid_economic_crosswalk_v1.csv"
    if covid_status_path.exists():
        covid_status = pd.read_csv(covid_status_path, dtype=str, encoding="utf-8-sig").fillna("")
        for item in covid_status.itertuples(index=False):
            status = str(item.mapping_status).strip()
            labels = str(item.value_labels).strip()
            if not labels or not status.startswith("candidate; questionnaire and Codebook labels reviewed; validate routes and eligible denominator in approved data"):
                continue
            selected = (
                out["Source.Wave"].astype(str).eq(str(item.wave))
                & out["Variable.Name"].str.lower().eq(str(item.code).lower())
                & out["Value.Labels"].eq(labels)
                & out["Value.Label.Review"].ne("conflict")
            )
            out.loc[selected, "Value.Label.Review"] = status
    # Continuous behavior measures do not need discrete value-label menus.
    # Preserve their already-audited units/semantics in the main catalogue,
    # but only replace the generic pending state and never overwrite labels,
    # conflicts, or an explicit analysis lock.
    behavior_path = root / "audit" / "behavior_exposure_variable_mapping_v1.csv"
    if behavior_path.exists():
        behavior_values = pd.read_csv(behavior_path, dtype=str, encoding="utf-8-sig").fillna("")
        continuous_prefixes = (
            "continuous count, not a categorical code;",
            "continuous monetary amount, not a categorical code;",
            "continuous component, not a categorical code;",
            "continuous beverage quantity, not a categorical code;",
            "continuous measure, not a categorical code;",
        )
        for item in behavior_values.to_dict(orient="records"):
            status = str(item.get("value_label_status", "")).strip()
            if not status.startswith(continuous_prefixes):
                continue
            selected = (
                out["Source.Wave"].astype(str).eq(str(item.get("wave", "")))
                & out["Variable.Name"].str.lower().eq(str(item.get("code", "")).lower())
                & out["Value.Labels"].eq("")
                & out["Value.Label.Review"].isin(["", "not yet reviewed"])
            )
            out.loc[selected, "Value.Label.Review"] = status
            source = str(item.get("value_label_source", "")).strip()
            if source:
                out.loc[selected, "Value.Label.Source"] = source
    # Pension Codebook matches with no extracted response categories should
    # not be presented as if the field itself has never been located. This is
    # a source-location status only; it does not settle amount units, routes,
    # special values, or analysis eligibility.
    pension_codebook_path = root / "audit" / "pension_codebook_value_labels_v1.csv"
    if pension_codebook_path.exists():
        pension_values = pd.read_csv(pension_codebook_path, dtype=str, encoding="utf-8-sig").fillna("")
        pending_codebook_status = "official codebook field located; continuous/count or no categorical labels"
        for item in pension_values.to_dict(orient="records"):
            if item.get("value_label_status", "").strip() != pending_codebook_status or item.get("value_labels", "").strip():
                continue
            selected = (
                out["Source.Wave"].astype(str).eq(str(item.get("wave", "")))
                & out["Variable.Name"].str.lower().eq(str(item.get("code", "")).lower())
                & out["Value.Labels"].eq("")
                & out["Value.Label.Review"].isin(["", "not yet reviewed"])
            )
            out.loc[selected, "Value.Label.Review"] = pending_codebook_status
            source = str(item.get("value_label_source", "")).strip()
            if source:
                out.loc[selected, "Value.Label.Source"] = source
    # Exact Codebook entries for household-income candidates with numeric
    # summary tables and no categorical menu. This is deliberately narrower
    # than all numeric-looking expenditure/income fields: unknown routes,
    # units, special codes, and release coding remain unresolved.
    income_numeric_path = root / "audit" / "household_income_numeric_status_v1.csv"
    if income_numeric_path.exists():
        income_numeric = pd.read_csv(income_numeric_path, dtype=str, encoding="utf-8-sig").fillna("")
        income_numeric_status = "official Codebook lists numeric summary; no categorical response menu in this entry"
        for item in income_numeric.to_dict(orient="records"):
            if item.get("value_label_status", "").strip() != income_numeric_status:
                continue
            selected = (
                out["Source.Wave"].astype(str).eq(str(item.get("wave", "")))
                & out["Variable.Name"].str.lower().eq(str(item.get("code", "")).lower())
                & out["category"].eq("social determinants")
                & out["subcategory"].isin(["income, wealth, and material resources", "household expenditure and material resources"])
                & out["Value.Labels"].eq("")
                & out["Value.Label.Review"].isin(["", "not yet reviewed"])
            )
            out.loc[selected, "Value.Label.Review"] = income_numeric_status
            source = str(item.get("value_label_source", "")).strip()
            if source:
                out.loc[selected, "Value.Label.Source"] = source
    wage_receipt_path = root / "audit" / "personal_wage_receipt_value_labels_v1.csv"
    if wage_receipt_path.exists():
        wage_receipts = pd.read_csv(wage_receipt_path, dtype=str, encoding="utf-8-sig").fillna("")
        receipt_status = "official Codebook response categories transcribed; frequencies omitted; cross-wave question scope and release coding pending"
        for item in wage_receipts.to_dict(orient="records"):
            if item.get("value_label_status", "").strip() != receipt_status or not item.get("value_labels", "").strip():
                continue
            selected = (
                out["Source.Wave"].astype(str).eq(str(item.get("wave", "")))
                & out["Variable.Name"].str.lower().eq(str(item.get("code", "")).lower())
                & out["Value.Labels"].eq("")
                & out["Value.Label.Review"].isin(["", "not yet reviewed"])
            )
            out.loc[selected, "Value.Labels"] = item["value_labels"].strip()
            out.loc[selected, "Value.Label.Review"] = receipt_status
            source = str(item.get("value_label_source", "")).strip()
            if source:
                out.loc[selected, "Value.Label.Source"] = source
    cognition_value_path = root / "audit" / "cognition_item_variable_mapping_v1.csv"
    if cognition_value_path.exists():
        cognition_values = pd.read_csv(cognition_value_path, dtype=str, encoding="utf-8-sig").fillna("")
        # The cognition crosswalk is the reviewed, wave-specific source for
        # explicit Codebook labels. Import its non-empty labels into both E/P
        # items and C-class administration metadata; do not infer unlisted
        # response codes or use Codebook frequencies as respondent counts.
        for item in cognition_values.itertuples(index=False):
            labels = str(item.value_labels).strip()
            if not labels:
                continue
            selected = (
                out["Source.Wave"].astype(str).eq(str(item.wave))
                & out["Variable.Name"].str.lower().eq(str(item.code).lower())
                & out["category"].eq("cognition")
            )
            different = selected & out["Value.Labels"].ne("") & out["Value.Labels"].ne(labels)
            out.loc[different, "Value.Label.Review"] = "conflict"
            out.loc[different, "Review.Flag"] = "Codebook label differs from cognition crosswalk; adjudication required"
            blank = selected & out["Value.Labels"].eq("")
            out.loc[blank, "Value.Labels"] = labels
            out.loc[blank, "Value.Label.Source"] = str(item.value_label_source)
            out.loc[blank, "Value.Label.Review"] = str(item.value_label_status or "officially reviewed")
        cognition_partial = cognition_values[cognition_values["value_label_status"].str.startswith(
            "official Codebook extraction exposes only a partial response-code set"
        )]
        for item in cognition_partial.itertuples(index=False):
            selected = out["Source.Wave"].astype(str).eq(str(item.wave)) & out["Variable.Name"].str.lower().eq(str(item.code).lower())
            out.loc[selected, "Value.Label.Review"] = str(item.value_label_status)
            out.loc[selected, "Value.Label.Source"] = str(item.value_label_source)
    owner_relation_review = root / "audit" / "housing_owner_relation_value_label_review_v1.csv"
    if owner_relation_review.exists():
        partial = pd.read_csv(owner_relation_review, dtype=str, encoding="utf-8-sig").fillna("")
        partial = partial[partial["value_label_status"].str.contains("partial response-code set", case=False, regex=False)]
        for item in partial.itertuples(index=False):
            selected = out["Source.Wave"].astype(str).eq(str(item.wave)) & out["Variable.Name"].str.lower().eq(str(item.code).lower())
            out.loc[selected, "Value.Label.Review"] = str(item.value_label_status)
            out.loc[selected, "Value.Label.Source"] = str(item.value_label_source)
    # 2011 FM019 fields are source-option slots, not self-describing response
    # values. Keep the menu searchable while blocking analysis until the
    # respondent-level checkbox storage and routed denominator are verified.
    pension_source_slots = {
        "fm019s1": "Government", "fm019s2": "Previous work unit",
        "fm019s3": "Social insurance agency", "fm019s4": "Commercial insurance company",
        "fm019s5": "Other",
    }
    for code, meaning in pension_source_slots.items():
        selected = out["Source.Wave"].astype(str).eq("2011") & out["Variable.Name"].str.lower().eq(code)
        out.loc[selected, "Value.Labels"] = f"questionnaire option slot={meaning} (not an answer-value label)"
        out.loc[selected, "Value.Label.Source"] = "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        out.loc[selected, "Value.Label.Review"] = "selected option-code storage confirmed in authorized local table; route/denominator unresolved"
        out.loc[selected, "Candidate.Status"] = "official questionnaire option-slot mapping; local selected-code storage verified; route discrepancy remains"
        out.loc[selected, "Harmonization.Status"] = "2011 FM019 pension-source checkbox; empty strings conflate unselected/not-asked; selections outside apparent routes; see field audit"
        out.loc[selected, "Review.Flag"] = "DO NOT ANALYZE; option-code storage confirmed, but route discrepancy and eligible denominator remain unresolved; do not infer unselected options as No"
    internal_retirement_gate = out["Source.Wave"].astype(str).eq("2011") & out["Variable.Name"].str.lower().isin({"fm031", "fm032_a", "fm032_b", "fm035_a", "fm035_b"})
    out.loc[internal_retirement_gate, "Review.Flag"] = "DO NOT ANALYZE until Codebook observations, response-category menu, bracket endpoints and special-value storage are reconciled for the FM011=3 route"
    out.loc[internal_retirement_gate, "Value.Label.Review"] = "questionnaire route reviewed; Codebook/storage conflict or no-observations gate"
    out.loc[internal_retirement_gate, "Harmonization.Status"] = "2011 FM011=3 internal-then-formal retirement route; see field-level audit for source-specific restriction"
    fm032 = out["Source.Wave"].astype(str).eq("2011") & out["Variable.Name"].str.lower().isin({"fm032_a", "fm032_b"})
    out.loc[fm032, "Candidate.Status"] = "conditional bracket-component candidate; local paired string storage and route checked; special-value meaning unresolved"
    out.loc[fm032, "Review.Flag"] = "DO NOT ANALYZE: FM032 paired bracket endpoints and extreme special-value meaning remain unresolved"
    out.loc[fm032, "Value.Label.Review"] = "local paired endpoint storage and FM011=3 route checked; Codebook extreme upper value retained; do not derive amount"
    fm035 = out["Source.Wave"].astype(str).eq("2011") & out["Variable.Name"].str.lower().isin({"fm035_a", "fm035_b"})
    out.loc[fm035, "Candidate.Status"] = "conditional bracket-component candidate; local paired string storage and route checked; special-value meaning unresolved"
    out.loc[fm035, "Review.Flag"] = "DO NOT ANALYZE: FM035 paired bracket endpoints and extreme special-value meaning remain unresolved"
    out.loc[fm035, "Value.Label.Review"] = "local paired endpoint storage and FM011=3 route checked; Codebook extreme upper value retained; do not derive amount"
    fm033 = out["Source.Wave"].astype(str).eq("2011") & out["Variable.Name"].str.lower().eq("fm033")
    out.loc[fm033, "Candidate.Status"] = "official questionnaire route and all observed response codes verified; route-specific categorical candidate"
    out.loc[fm033, "Harmonization.Status"] = "2011 FM011=3 route only; retain documented codes 6/7/8/10; do not infer code for questionnaire option with no Codebook observations"
    out.loc[fm033, "Review.Flag"] = "conditional route-specific E candidate; one questionnaire option has no Codebook observations; preserve blank as missing"
    out.loc[fm033, "Value.Label.Review"] = "all observed codes verified against official Codebook; unobserved commercial-insurance option left unmapped"
    fm034 = out["Source.Wave"].astype(str).eq("2011") & out["Variable.Name"].str.lower().eq("fm034")
    out.loc[fm034, "Candidate.Status"] = "official questionnaire item and yuan/month unit reviewed; conditional FM011=3 route"
    out.loc[fm034, "Review.Flag"] = "preserve FM011=3 denominator; verify whether zero and extreme/special values are valid before analysis"
    out.loc[fm034, "Value.Label.Review"] = "continuous amount; Codebook range available; inspect zero and special values"
    out.loc[fm034, "Value.Label.Source"] = "sources_official/CHARLS_2011_Codebook_extracted.txt"
    fm039 = out["Source.Wave"].astype(str).eq("2011") & out["Variable.Name"].str.lower().isin({"fm039_a", "fm039_b"})
    out.loc[fm039, "Candidate.Status"] = "conditional bracket-component candidate; local bound storage checked; unit branch unresolved"
    out.loc[fm039, "Harmonization.Status"] = "FM011=4 route; FM038 unit selector absent on bracket rows; interval endpoints are not point estimates; upper special code unresolved"
    out.loc[fm039, "Review.Flag"] = "DO NOT ANALYZE; endpoints/extreme code observed, but FM038 unit branch and special-value meaning remain unresolved"
    out.loc[fm039, "Value.Label.Review"] = "local string endpoint pairs checked; Codebook extreme upper value present; route/unit and sentinel semantics unresolved"
    fm010 = out["Source.Wave"].astype(str).eq("2011") & out["Variable.Name"].str.lower().eq("fm010")
    out.loc[fm010, "Harmonization.Status"] = "current pension receipt after retirement/receding; questionnaire route FB011=1 or FB012=1; 1=Yes/2=No; not general pension enrollment"
    out.loc[fm010, "Review.Flag"] = "conditional route-specific E candidate; establish the eligible retired/receded denominator before analysis"
    da079_2011 = out["Source.Wave"].astype(str).eq("2011") & out["Variable.Name"].str.lower().eq("da079")
    out.loc[da079_2011, "Candidate.Status"] = "official questionnaire item and response scale verified; Codebook variable-title conflict retained for review"
    out.loc[da079_2011, "Harmonization.Status"] = "candidate for self-rated overall health; confirm released data dictionary and wave equivalence before analysis"
    out.loc[da079_2011, "Review.Flag"] = "retain as candidate; verify questionnaire/Codebook title conflict against approved release dictionary"
    out.loc[da079_2011, "Value.Label.Review"] = "questionnaire response scale verified; Codebook title conflict retained"
    # 2018 FN012's CodeBook frequency table and questionnaire both confirm
    # 1=Yes/2=No; the exact-wave pension adjudication supplies those labels.
    # These are continuous counts with official units/ranges, not categorical
    # items. Mark the value-label review state accurately and preserve the
    # wave-specific codebook source without fabricating response labels.
    continuous_measure_sources = {
        ("2011", "gd001_c"): "sources_official/CHARLS_2011_Codebook_extracted.txt",
        ("2013", "gd001"): "sources_official/CHARLS_2013_Codebook_extracted.txt",
        ("2015", "gd001"): "sources_official/CHARLS_2015_Codebook_extracted.txt",
        ("2018", "fn105_w4_1"): "sources_official/CHARLS_2018_Codebook_extracted.txt",
        ("2018", "fn105_w4_2"): "sources_official/CHARLS_2018_Codebook_extracted.txt",
        ("2018", "fh009_w4"): "sources_official/CHARLS_2018_Codebook_extracted.txt",
        ("2020", "fd004"): "sources_official/CHARLS_2020_Codebook_extracted.txt",
        ("2018", "fc024_w4"): "sources_official/CHARLS_2018_Codebook_extracted.txt",
        ("2018", "fj001_w4"): "sources_official/CHARLS_2018_Codebook_extracted.txt",
        ("2018", "fj002_w4"): "sources_official/CHARLS_2018_Codebook_extracted.txt",
        ("2018", "fj003_w4"): "sources_official/CHARLS_2018_Codebook_extracted.txt",
        ("2018", "fl012_w4"): "sources_official/CHARLS_2018_Codebook_extracted.txt",
        ("2020", "ff001"): "sources_official/CHARLS_2020_Codebook_extracted.txt",
        ("2020", "fc025"): "sources_official/CHARLS_2020_Codebook_extracted.txt",
        ("2020", "ff004_1"): "sources_official/CHARLS_2020_Codebook_extracted.txt",
        ("2020", "ff004_2"): "sources_official/CHARLS_2020_Codebook_extracted.txt",
    }
    # 2018 HA&I owner-share fields are continuous percent responses. The
    # official questionnaire defines these as each rostered member's share
    # of a particular house; they are not categorical response codes.
    housing_mapping_path = root / "audit" / "housing_exposure_variable_mapping_v1.csv"
    if housing_mapping_path.exists():
        housing_mapping = pd.read_csv(housing_mapping_path, dtype=str, encoding="utf-8-sig").fillna("")
        owner_share_codes = housing_mapping.loc[
            housing_mapping["concept_id"].eq("household_property_owner_share_slots")
            & housing_mapping["wave"].eq("2018"), "code"
        ].drop_duplicates()
        for code in owner_share_codes:
            continuous_measure_sources[("2018", str(code).lower())] = "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"
    for (wave, code), source in continuous_measure_sources.items():
        selected = out["Source.Wave"].astype(str).eq(wave) & out["Variable.Name"].str.lower().eq(code)
        out.loc[selected, "Value.Label.Review"] = "continuous measure metadata available"
        out.loc[selected, "Value.Label.Source"] = source
    # DA009's numbered value fields are numeric time measures, not categorical
    # responses. The official wave Codebooks distinguish calendar year from
    # age in years; keep those units separate and do not infer valid ranges
    # from the descriptive summary extrema.
    diagnosis_time = (
        out["Source.Wave"].astype(str).isin({"2011", "2013", "2015", "2018"})
        & out["Variable.Name"].str.lower().str.fullmatch(r"da009_[12]_\d+_?")
    )
    diagnosis_index = out["Variable.Name"].str.lower().str.extract(r"da009_[12]_(\d+)_?")[0]
    diagnosis_time &= diagnosis_index.isin({str(i) for i in range(1, 15)})
    for idx in out.index[diagnosis_time]:
        wave = str(out.at[idx, "Source.Wave"])
        code = str(out.at[idx, "Variable.Name"]).lower()
        unit = "calendar year" if code.startswith("da009_1_") else "age in years"
        out.at[idx, "Concept.Unit.Candidates"] = unit
        out.at[idx, "Value.Label.Review"] = "numeric/time unit metadata available; no discrete labels assigned"
        out.at[idx, "Value.Label.Source"] = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        out.at[idx, "Harmonization.Status"] = (
            f"reported first diagnosis/awareness time; Codebook unit={unit}; not biological disease onset. "
            "Keep year and age fields separate; preserve route and special values; Codebook extrema do not define a valid range."
        )
    # Disability-onset year components are continuous time measures. Surface
    # their unit and route review state even though they have no categorical
    # value labels; the crosswalk distinguishes current-wave and prior-wave
    # verification branches and records the corresponding official sources.
    disability_path = root / "audit" / "disability_history_crosswalk_v1.csv"
    if disability_path.exists():
        disability_rows = pd.read_csv(disability_path, dtype=str, encoding="utf-8-sig").fillna("")
        onset_rows = disability_rows[
            disability_rows["field_role"].str.contains("onset year", case=False, na=False)
        ]
        for item in onset_rows.to_dict(orient="records"):
            wave = str(item.get("wave", ""))
            code = str(item.get("code", "")).lower()
            selected = (
                out["Source.Wave"].astype(str).eq(wave)
                & out["Variable.Name"].str.lower().eq(code)
                & out["Value.Labels"].eq("")
            )
            if not selected.any():
                continue
            out.loc[selected, "Concept.Unit.Candidates"] = "calendar year"
            out.loc[selected, "Value.Label.Review"] = "numeric/time unit metadata available; no discrete labels assigned"
            out.loc[selected, "Value.Label.Source"] = str(item.get("value_label_source", ""))
            out.loc[selected, "Harmonization.Status"] = (
                out.loc[selected, "Harmonization.Status"].astype(str)
                + "; reported onset year in calendar years; conditional disability/verification route; preserve special values; not biological disease onset"
            ).str.strip("; ")
    # DA030_1/DA030_2 are the corresponding prostate-illness timing
    # components. The official Codebooks label these as calendar year and
    # age in years. They are not categorical disease outcomes, and their
    # conditional male-only route and valid ranges remain unverified.
    prostate_diagnosis_time = (
        out["Source.Wave"].astype(str).isin({"2011", "2013", "2015", "2018"})
        & out["Variable.Name"].str.lower().isin({"da030_1", "da030_2"})
    )
    for idx in out.index[prostate_diagnosis_time]:
        wave = str(out.at[idx, "Source.Wave"])
        code = str(out.at[idx, "Variable.Name"]).lower()
        unit = "calendar year" if code == "da030_1" else "age in years"
        out.at[idx, "Concept.Unit.Candidates"] = unit
        out.at[idx, "Value.Label.Review"] = "numeric/time unit metadata available; no discrete labels assigned"
        out.at[idx, "Value.Label.Source"] = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        out.at[idx, "Harmonization.Status"] = (
            f"male-only, wave-routed prostate illness first-diagnosis time; Codebook unit={unit}; "
            "not prostate cancer and not biological disease onset. Keep year and age separate; "
            "preserve route and special values; Codebook extrema do not define a valid range."
        )
    stroke_timing = (
        out["Source.Wave"].astype(str).isin({"2013", "2015", "2018"})
        & out["Variable.Name"].str.lower().str.fullmatch(r"da019_w2_2_[12]")
    )
    for idx in out.index[stroke_timing]:
        wave = str(out.at[idx, "Source.Wave"])
        code = str(out.at[idx, "Variable.Name"]).lower()
        if code.endswith("_1"):
            unit = "calendar year"
        elif wave == "2013":
            unit = "month"
        else:
            unit = "age in years"
        out.at[idx, "Concept.Unit.Candidates"] = unit
        out.at[idx, "Value.Label.Review"] = "numeric/time unit metadata available; no discrete labels assigned"
        out.at[idx, "Value.Label.Source"] = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        out.at[idx, "Harmonization.Status"] = (
            f"conditional most-recent-stroke timing after prior stroke; Codebook unit={unit}. "
            "2013 second component is month; 2015/2018 second component is age in years. "
            "Not first-ever diagnosis time; preserve prior-stroke eligibility route and special values."
        )
    animal_fluency = (
        out["Source.Wave"].astype(str).eq("2018")
        & out["category"].eq("cognition")
        & out["Variable.Name"].str.lower().str.fullmatch(r"dc03[2-9]_w4")
    )
    out.loc[animal_fluency, "Value.Label.Review"] = "continuous count measure; Codebook identifies 15-second animal-fluency intervals; summary statistics are not valid-range evidence"
    out.loc[animal_fluency, "Value.Label.Source"] = "sources_official/CHARLS_2018_Codebook_extracted.txt; audit/cognition_item_variable_mapping_v1.csv"
    out.loc[animal_fluency, "Harmonization.Status"] = "continuous count per source-defined 15-second interval; preserve total versus correct counts and interval; Codebook extrema require raw-data QA and do not define a valid range"
    specific_math = out["Source.Wave"].astype(str).eq("2018") & out["Variable.Name"].str.lower().str.fullmatch(r"dc014_w4_[1-5]_1")
    earlier_math = out["Source.Wave"].astype(str).isin({"2011", "2013", "2015"}) & out["category"].eq("cognition") & out["Variable.Name"].str.lower().str.fullmatch(r"dc0(19|20|21|22|23)")
    wave5_math = out["Source.Wave"].astype(str).eq("2020") & out["category"].eq("cognition") & out["Variable.Name"].str.lower().str.fullmatch(r"dc007_[1-5]_1")
    math_answers = specific_math | earlier_math | wave5_math
    out.loc[math_answers, "Value.Label.Review"] = "continuous raw subtraction response; Codebook extreme maxima occur; valid range and scoring require authorized raw-data QA"
    out.loc[math_answers, "Value.Label.Source"] = "wave-specific official CHARLS Codebook; audit/cognition_item_variable_mapping_v1.csv"
    out.loc[math_answers, "Harmonization.Status"] = "raw recorded subtraction response; do not score or define valid range from Codebook summaries; inspect authorized release before analysis"
    # Objective biomarkers, blood assays and physical measurements are
    # continuous internal clinical measures, not environmental exposure
    # analytes. Keep their dual-role discovery tag but make this distinction
    # explicit and cite the wave-specific official instrument/document.
    internal_measure = out["category"].eq("internal biomarker") & out["Value.Label.Review"].eq("not yet reviewed")
    for idx in out.index[internal_measure]:
        wave = str(out.at[idx, "Source.Wave"])
        module = str(out.at[idx, "Data.File.Name"]).lower()
        if "blood_assays" in module:
            refs = "sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2011_Blood_User_Guide_extracted.txt"
        elif wave == "2011":
            refs = "sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt"
        else:
            refs = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt; sources_official/CHARLS_{wave}_Biomarker_Questionnaire_extracted.txt"
        out.at[idx, "Value.Label.Review"] = "continuous measure metadata available"
        out.at[idx, "Value.Label.Source"] = refs
        out.at[idx, "Harmonization.Status"] = "continuous internal biomarker/clinical or physical measure; not an exogenous environmental exposure. Candidate phenotype; role as exposure is estimand-dependent. Preserve wave-specific protocol and units; cross-wave harmonization not approved."
        out.at[idx, "subcategory"] = "internal clinical/physiological measure; phenotype candidate, not exogenous environmental exposure"
    community_value_path = root / "audit" / "community_exposure_value_labels_v1.csv"
    if community_value_path.exists():
        community_values = pd.read_csv(community_value_path, dtype=str, encoding="utf-8-sig").fillna("")
        numeric_community = community_values.loc[
            community_values["value_label_status"].str.contains("continuous/count response, no category labels", case=False, regex=False)
        ]
        for item in numeric_community.itertuples(index=False):
            selected = (
                out["Source.Wave"].astype(str).eq(str(item.wave))
                & out["Variable.Name"].str.lower().eq(str(item.code).lower())
                & out["category"].eq("community context")
            )
            out.loc[selected, "Value.Label.Review"] = "official Codebook numeric/count response located; no discrete answer labels"
            out.loc[selected, "Value.Label.Source"] = str(item.value_label_source)
    no_labels = out["Value.Labels"].fillna("").str.strip().eq("")
    continuous = out["category"].isin(["biochemistry", "blood pressure", "anthropometric"])
    objective_component = out["Candidate.Status"].eq("officially audited objective measurement crosswalk candidate")
    out.loc[no_labels & continuous, "Value.Label.Review"] = "continuous measure metadata available; see description/crosswalk"
    out.loc[no_labels & objective_component, "Value.Label.Review"] = "audited measurement component; derive concept per crosswalk"
    # Apply onset-year units after generic review-status propagation so these
    # continuous fields retain their unit even when an earlier audit supplied
    # a more detailed route/semantic review string.
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = out.drop_duplicates(source_identity, keep="first")
    if disability_path.exists():
        for item in onset_rows.to_dict(orient="records"):
            selected = (
                out["Source.Wave"].astype(str).eq(str(item.get("wave", "")))
                & out["Variable.Name"].str.lower().eq(str(item.get("code", "")).lower())
                & out["Value.Labels"].fillna("").eq("")
            )
            out.loc[selected, "Concept.Unit.Candidates"] = "calendar year"
    out.to_csv(args.out_dir / "charls_atlas_candidate_fields_v0.csv", index=False, encoding="utf-8-sig")

    def summarize_label_review(values: pd.Series) -> str:
        reviews = [str(value) for value in values if pd.notna(value) and str(value).strip()]
        blocked = next((value for value in reviews if any(
            marker in value.lower() for marker in ("do not analyze", "unresolved", "conflict")
        )), "")
        if blocked:
            return blocked
        partial = next((value for value in reviews if value.startswith("official Codebook extraction exposes only a partial response-code set")), "")
        if partial:
            return partial
        if "officially reviewed" in reviews:
            return "officially reviewed"
        if any("audited measurement component" in value for value in reviews):
            return "audited measurement component"
        if any("continuous measure metadata available" in value for value in reviews):
            return "continuous measure metadata available"
        return "not yet reviewed"

    out["_code_key"] = out["Variable.Name"].str.lower()
    series = (out.groupby(["epcf", "category", "subcategory", "_code_key"], dropna=False)
              .agg(**{"Variable.Name": ("Variable.Name", "first"),
                   "Variable.Description": ("Variable.Description", lambda s: " | ".join(sorted(set(s))[:3])),
                   "waves": ("Source.Wave", lambda s: ",".join(sorted(set(s)))),
                   "wave_count": ("Source.Wave", "nunique"),
                   "source_modules": ("Data.File.Name", lambda s: ",".join(sorted(set(s)))),
                   "value_labels": ("Value.Labels", lambda s: " | ".join(sorted({str(v) for v in s if pd.notna(v) and str(v).strip()}))),
                   "value_label_source": ("Value.Label.Source", lambda s: " | ".join(sorted({str(v) for v in s if pd.notna(v) and str(v).strip()}))),
                   "value_label_review": ("Value.Label.Review", summarize_label_review),
                   "harmonization_status": ("Harmonization.Status", lambda s: next((str(v) for v in s if str(v).startswith("continuous internal biomarker/clinical or physical measure")), ""))})
              .reset_index().drop(columns=["_code_key"]))
    # Explicitly preserve special review states in the public series view.
    # These are critical caveats that a generic "not yet reviewed" would hide.
    if "harmonization_status" not in series.columns:
        series["harmonization_status"] = ""
    for idx, item in series.iterrows():
        selected = (
            out["epcf"].eq(item["epcf"]) & out["category"].eq(item["category"])
            & out["subcategory"].eq(item["subcategory"])
            & out["Variable.Name"].str.lower().eq(str(item["Variable.Name"]).lower())
        )
        reviews = out.loc[selected, "Value.Label.Review"].astype(str)
        partial = next((v for v in reviews if v.startswith("official Codebook extraction exposes only a partial response-code set")), "")
        if partial:
            series.at[idx, "value_label_review"] = partial
        note = next((str(v) for v in out.loc[selected, "Harmonization.Status"] if str(v).startswith("continuous internal biomarker/clinical or physical measure")), "")
        if note:
            series.at[idx, "harmonization_status"] = note
    series.to_csv(args.out_dir / "charls_atlas_candidate_series_v0.csv", index=False, encoding="utf-8-sig")
    (args.out_dir / "charls_atlas_candidate_series_v0.json").write_text(
        json.dumps(series.to_dict(orient="records"), ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    args.site_catalog.parent.mkdir(parents=True, exist_ok=True)
    args.site_catalog.write_text(
        json.dumps(series.to_dict(orient="records"), ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    summary = (out.groupby(["epcf", "category", "subcategory"], dropna=False)
               .agg(source_field_wave_rows=("Variable.Name", "size"), distinct_source_codes=("Variable.Name", "nunique"),
                    wave_count=("Source.Wave", "nunique"))
               .reset_index().sort_values(["epcf", "category", "subcategory"]))
    summary.to_csv(args.out_dir / "charls_atlas_candidate_domain_counts_v0.csv", index=False, encoding="utf-8-sig")
    label_summary = (out.assign(_has_label=out["Value.Labels"].fillna("").str.strip().ne(""),
                                _wave_code=out["Source.Wave"].astype(str) + "::" + out["Variable.Name"].astype(str).str.lower())
                     .groupby(["epcf", "category", "subcategory"], dropna=False)
                     .agg(field_category_rows=("Variable.Name", "size"),
                          distinct_wave_fields=("_wave_code", "nunique"),
                          rows_with_reviewed_labels=("_has_label", "sum"))
                     .reset_index().sort_values(["epcf", "category", "subcategory"]))
    label_summary.to_csv(args.out_dir / "charls_ep_catalog_value_label_coverage_v1.csv", index=False, encoding="utf-8-sig")
    print(f"candidate_field_wave_rows={len(out)}")
    print(f"candidate_source_series={len(series)}")
    print(summary.to_string(index=False))
    # Correct exact-wave exposure-role false positives documented in the audit.
    import subprocess, sys
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "apply_catalog_role_overrides.py")], cwd=root, check=True)


if __name__ == "__main__":
    main()
