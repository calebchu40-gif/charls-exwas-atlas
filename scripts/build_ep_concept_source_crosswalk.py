"""Assemble explicit concept-to-source-field mappings for the E/P atlas.

This is an evidence-preserving candidate layer: source mappings retain their
review state and do not imply that the concept is ready for statistical tests.
"""
from pathlib import Path
from datetime import date
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUT = AUDIT / "ep_concept_source_crosswalk_v1.csv"

rows: list[dict[str, str]] = []

def text(item: dict, *keys: str, default: str = "") -> str:
    for key in keys:
        value = str(item.get(key, "")).strip()
        if value:
            return value
    return default

def add(item: dict, *, role: str, file: str, wave_key: str, code_key: str,
        concept_key: str, label_keys: tuple[str, ...], domain_keys: tuple[str, ...],
        module_keys: tuple[str, ...], status_keys: tuple[str, ...],
        caveat_keys: tuple[str, ...] = (), semantics_keys: tuple[str, ...] = (),
        value_label_keys: tuple[str, ...] = (), unit_keys: tuple[str, ...] = (),
        archive_keys: tuple[str, ...] = (), document_keys: tuple[str, ...] = ()) -> None:
    wave = text(item, wave_key)
    code = text(item, code_key).lower()
    concept = text(item, concept_key)
    if not wave or not code or not concept:
        return
    rows.append({
        "Concept.ID": concept,
        "Concept.Label": text(item, *label_keys, default=concept),
        "Role": role,
        "Domain": text(item, *domain_keys),
        "Wave": wave,
        "Source.Code": code,
        "Source.Label": text(item, "source_label", "Source.Label", "Source.Label", default=code),
        "Module": text(item, *module_keys),
        "Source.Archive": text(item, *archive_keys),
        "Unit": text(item, *unit_keys),
        "Value.Labels": text(item, *value_label_keys),
        "Value.Semantics": text(item, *semantics_keys),
        "Mapping.Status": text(item, *status_keys, default="candidate concept-source mapping; review required"),
        "Caveat": (
            "2015 DA061_W3 is a retrospective question about smoking status at the last interview, not current 2015 status. Treat as prior-wave history only; do not label or analyze it as a contemporaneous 2015 exposure. It is asked only for eligible returning respondents with prior ever-smoking and missing prior DA061; preserve this routed denominator."
            if wave == "2015" and code == "da061_w3"
            else text(item, *caveat_keys)
        ),
        "Source.File": f"audit/{file}",
        "Source.Document": text(item, *document_keys),
    })

def load(file: str) -> pd.DataFrame:
    path = AUDIT / file
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")

def map_direct(file: str, role: str, *, wave="wave", code="code", concept="concept_id",
               labels=("concept_label",), domains=("domain",), modules=("module",),
               statuses=("mapping_status",), caveats=("caveat",), semantics=("value_semantics",),
               value_labels=("value_labels",), units=(), archives=("source_archive",), documents=(), include_codes=None) -> None:
    frame = load(file)
    if include_codes is not None:
        frame = frame[frame[code].str.lower().isin({x.lower() for x in include_codes})]
    for item in frame.to_dict("records"):
        add(item, role=role, file=file, wave_key=wave, code_key=code,
            concept_key=concept, label_keys=labels, domain_keys=domains,
            module_keys=modules, status_keys=statuses, caveat_keys=caveats,
            semantics_keys=semantics, value_label_keys=value_labels,
            unit_keys=units, archive_keys=archives, document_keys=documents)

# Wave-level, domain-audited mappings. Their original status/caveat is retained;
# several files intentionally describe candidates pending final harmonization.
behavior = load("behavior_exposure_variable_mapping_v1.csv")
behavior_selectors = behavior["value_label_status"].str.startswith(
    ("official selector code reviewed", "official component-type marker reviewed")
)
for item in behavior.loc[~behavior_selectors].to_dict("records"):
    add(item, role="e", file="behavior_exposure_variable_mapping_v1.csv",
        wave_key="wave", code_key="code", concept_key="concept_id",
        label_keys=("concept_label",), domain_keys=("domain",), module_keys=("module",),
        status_keys=("mapping_status",), caveat_keys=("note",), semantics_keys=("value_semantics",),
        value_label_keys=("value_labels",), archive_keys=("source_archive",),
        document_keys=("questionnaire_source", "value_label_source"))
for item in behavior.loc[behavior_selectors].to_dict("records"):
    add(item, role="c", file="behavior_exposure_variable_mapping_v1.csv",
        wave_key="wave", code_key="code", concept_key="concept_id",
        label_keys=("concept_label",), domain_keys=("domain",), module_keys=("module",),
        status_keys=("value_label_status", "mapping_status"),
        caveat_keys=("note",), semantics_keys=("value_semantics",),
        value_label_keys=("value_labels",), archive_keys=("source_archive",),
        document_keys=("value_label_source", "questionnaire_source"))
map_direct("functional_concept_variable_mapping_v1.csv", "p",
           statuses=("mapping_status",), caveats=("harmonization_note", "note"),
           archives=(), documents=("value_label_source",))
map_direct("health_work_limitation_crosswalk_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           value_labels=("value_labels",), modules=("module",), caveats=("note",),
           semantics=("value_semantics",), documents=("value_label_source",))
map_direct("health_symptom_variable_mapping_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("note",), value_labels=("value_labels",),
           documents=("value_label_source",), archives=("source_archive",))
map_direct("relationship_satisfaction_crosswalk_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), value_labels=("value_labels",),
           documents=("value_label_source",), archives=("source_archive",))
map_direct("other_satisfaction_phenotypes_crosswalk_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), value_labels=("value_labels",),
           documents=("value_label_source",), archives=("source_archive",))
map_direct("subjective_life_expectancy_2011_2018_crosswalk_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), value_labels=("value_labels",),
           documents=("value_label_source",), archives=("source_archive",))
map_direct("reproductive_history_exposure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("questionnaire_source", "value_label_source"))
map_direct("biomarker_measurement_gate_crosswalk_v1.csv", "c",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), documents=("source_document",), archives=("source_archive",))
map_direct("mood_item_variable_mapping_v1.csv", "p",
           statuses=("mapping_status",), caveats=("note",))
map_direct("loneliness_exposure_role_mapping_v1.csv", "e",
           statuses=("mapping_status",), caveats=("caveat",),
           semantics=("value_semantics",), value_labels=("value_labels",),
           documents=("value_label_source",), archives=("source_archive",))
cognition = load("cognition_item_variable_mapping_v1.csv")
for item in cognition.to_dict("records"):
    # Refusal/nonresponse reasons and interviewer-observed task conditions
    # describe measurement, not cognitive performance outcomes.
    code = text(item, "code").lower()
    cognition_metadata = (
        text(item, "concept_id") == "cog_word_recall_administration"
        or (text(item, "wave") in {"2011", "2013", "2015", "2018"} and code == "dc024")
        or (text(item, "wave") == "2020" and code == "dc008")
        or (text(item, "wave") == "2018" and re.fullmatch(r"dc014_w4_[1-5]", code))
    )
    role = "c" if cognition_metadata else "p"
    add(item, role=role, file="cognition_item_variable_mapping_v1.csv",
        wave_key="wave", code_key="code", concept_key="concept_id",
        label_keys=("concept_label",), domain_keys=("domain",), module_keys=("module",),
        status_keys=("mapping_status",), caveat_keys=("note",),
        value_label_keys=("value_labels",), document_keys=("value_label_source",))

# Chronic disease uses a title-cased, source-oriented schema.
map_direct("chronic_disease_concept_variable_mapping_v2.csv", "p",
           wave="Source.Wave", code="Source.Variable", concept="Concept.ID",
           labels=("Concept.Label.zh",), domains=(), modules=("Source.Module",),
           statuses=("Mapping.Status",), caveats=("Caveat",), value_labels=("Value.Labels",),
           archives=("Source.Archive",), documents=("Official.Source",))
map_direct("chronic_disease_ancillary_variable_mapping_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",), value_labels=("value_labels",),
           modules=("module",), caveats=("caveat",), semantics=("subtype",),
           archives=("source_archive",), documents=("source_archive",))
map_direct("chronic_disease_management_crosswalk_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct", "subtype"),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("pension_exposure_variable_mapping_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",), units=("unit",),
           value_labels=("value_labels",), archives=("source_archive",), documents=("value_label_source", "source_archive"))
map_direct("pension_subsidy_delivery_2015_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("source_document",))
map_direct("life_insurance_exposure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), value_labels=("value_labels",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("pension_participation_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           units=("unit",), value_labels=("value_labels",), archives=("source_archive",),
           documents=("official_source",))
map_direct("pension_eligibility_2015_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           units=("unit",), value_labels=("value_labels",), archives=("source_archive",),
           documents=("official_source",))
map_direct("pension_2011_nrsp_detail_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           units=("unit",), value_labels=("value_labels",), archives=("source_archive",),
           documents=("official_source",))
map_direct("old_age_support_expectation_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           units=("unit",), value_labels=("value_labels",), archives=("source_archive",),
           documents=("official_source",))
map_direct("psych_treatment_2011_crosswalk_v1.csv", "p", include_codes={"da020s3", "da020s4"},
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           units=("unit",), value_labels=("value_labels",), archives=("source_archive",),
           documents=("official_source",))
map_direct("personal_income_exposure_mapping_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), value_labels=("value_labels",), archives=("source_archive",), documents=("official_source",))
map_direct("individual_transfer_income_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("official_source",))
map_direct("household_asset_exposure_mapping_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("household_economic_exposure_mapping_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("reference_period", "construct"),
           archives=("source_archive",), documents=("source_archive",))
map_direct("household_lending_debt_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct", "value_semantics"),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
sale_proceeds = load("household_sale_proceeds_allocation_crosswalk_v1.csv")
sale_percent_codes = set(sale_proceeds.loc[
    sale_proceeds["concept_id"].eq("house_sale_proceeds_allocation_percent_2013_2015"), "code"
].str.lower())
map_direct("household_sale_proceeds_allocation_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("reference_period", "unit"),
           value_labels=("value_labels",), archives=("source_archive",), documents=("value_label_source",),
           include_codes=sale_percent_codes)
map_direct("health_anchoring_vignette_metadata_crosswalk_v1.csv", "c",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), documents=("source_document",), archives=("source_archive",))
map_direct("household_transfer_compensation_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), archives=("source_archive",), documents=("source_document",))
map_direct("household_dibao_amount_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), archives=("source_archive",), documents=("source_document",))
map_direct("household_transfer_receipt_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("source_document",))
map_direct("household_transfer_none_option_crosswalk_v1.csv", "c",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("unit",),
           value_labels=("value_labels",), archives=("source_archive",),
           documents=("source_document",))
map_direct("household_renovation_expenditure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), archives=("source_archive",), documents=("source_document",))
map_direct("household_additional_income_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), archives=("source_archive",), documents=("source_document",))
map_direct("residential_rental_income_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           units=("unit",), archives=("source_archive",), documents=("source_document",))
map_direct("household_other_asset_rental_income_amount_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), archives=("source_archive",), documents=("source_document",))
map_direct("household_other_asset_rental_income_status_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), value_labels=("value_labels",), archives=("source_archive",),
           documents=("source_document",))
map_direct("household_other_asset_rental_income_selector_metadata_v1.csv", "c",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), archives=("source_archive",), documents=("source_document",))
map_direct("household_covid_economic_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), value_labels=("value_labels",), archives=("source_archive",),
           documents=("source_document",))
map_direct("personal_wage_deductions_2020_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), value_labels=("value_labels",), archives=("source_archive",),
           documents=("source_document",))
map_direct("personal_wage_deduction_2020_selector_metadata_v1.csv", "c",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), value_labels=("value_labels",), archives=("source_archive",),
           documents=("source_document",))
map_direct("household_agricultural_production_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), archives=("source_archive",), documents=("source_document",))
map_direct("housing_exposure_variable_mapping_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           archives=("source_archive",), documents=("source_archive",))
map_direct("demographic_social_exposure_mapping_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct",),
           units=("unit",), archives=("source_archive",), documents=("value_label_source",))
map_direct("parent_education_exposure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("parent_roster_education_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("sibling_record_context_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("child_roster_context_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("child_hukou_lifecourse_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("child_education_context_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("child_phenotype_crosswalk_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("parent_roster_context_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("parent_marital_ethnicity_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("social_context_remainder_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("childhood_residential_context_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("hukou_lifecourse_exposure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("hukou_recent_change_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("residential_settlement_exposure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("home_return_frequency_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("marital_history_exposure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), archives=("source_archive",),
           documents=("value_label_source",))
map_direct("adult_education_training_exposure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("source_archive",))
map_direct("formal_schooling_lifecourse_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("source_archive",))
map_direct("partner_context_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("source_archive",))
map_direct("residual_behavior_exposure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), units=("unit",), archives=("source_archive",),
           documents=("source_archive",))
map_direct("household_member_income_mapping_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("construct", "value_semantics"),
           value_labels=("value_labels",), units=("unit",),
           archives=("source_archive",), documents=("value_label_source", "source_archive"))
map_direct("land_rental_income_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           units=("unit",), archives=("source_archive",), documents=("source_document",))

map_direct("community_exposure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), units=("unit",), caveats=("caveat",),
           documents=("source_evidence",))
map_direct("environmental_perception_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), value_labels=("value_labels",),
           documents=("questionnaire_reference",))
map_direct("food_environment_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), value_labels=("code_value_labels",), caveats=("caveat",))
for item in load("healthcare_access_crosswalk_v1.csv").to_dict("records"):
    # Routine access/utilization may be an exposure or a health outcome, but
    # pandemic-specific care disruption is a phenotype only.
    role = "p" if text(item, "concept_id").startswith(("pandemic_", "healthcare_cost_")) else "e,p"
    add(item, role=role, file="healthcare_access_crosswalk_v1.csv",
        wave_key="wave", code_key="code", concept_key="concept_id",
        label_keys=("concept_label",), domain_keys=("domain",), module_keys=("module",),
        status_keys=("mapping_status",), caveat_keys=("caveat",),
        semantics_keys=("value_semantics",), value_label_keys=("value_labels",),
        document_keys=("questionnaire_reference", "value_label_source"))
map_direct("assistive_device_phenotype_crosswalk_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           value_labels=("value_labels",), modules=("module",), caveats=("caveat",),
           semantics=("value_semantics",), documents=("questionnaire_source",))
map_direct("social_exposure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), documents=("questionnaire_source", "value_label_source"))
map_direct("work_exposure_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), caveats=("caveat",),
           units=("unit",), documents=("source_document",))
map_direct("interwave_other_job_crosswalk_v1.csv", "e",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           units=("unit",), archives=("source_archive",),
           documents=("questionnaire_review", "source_document"))
map_direct("pandemic_work_module_selection_metadata_v1.csv", "c",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           units=("unit",), documents=("source_document",))
map_direct("health_work_absence_crosswalk_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           units=("unit",), documents=("questionnaire_source",), archives=("source_archive",))
map_direct("measurement_protocol_crosswalk_v1.csv", "c",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), archives=("source_archive",), documents=("source_document",))
map_direct("stroke_timing_metadata_crosswalk_v1.csv", "c",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("value_semantics",),
           value_labels=("value_labels",), archives=("source_archive",), documents=("source_document",))
map_direct("cancer_site_crosswalk_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("subtype",),
           value_labels=("value_labels",), archives=("source_archive",), documents=("value_label_source",))
map_direct("disability_history_crosswalk_v1.csv", "p",
           statuses=("mapping_status",), labels=("concept_label",), domains=("domain",),
           modules=("module",), caveats=("caveat",), semantics=("field_role", "value_semantics"),
           value_labels=("value_labels",), archives=("source_archive",), documents=("value_label_source",))

# Concept-level crosswalks with multiple source fields are expanded at the
# field level, preserving repeated-measure components as the same concept ID.
for item in load("objective_measurement_crosswalk_v1.csv").to_dict("records"):
    for code in text(item, "variables").split(";"):
        expanded = dict(item, source_label=code.strip())
        add(expanded, role="p", file="objective_measurement_crosswalk_v1.csv",
            wave_key="wave", code_key="source_label", concept_key="concept_id",
            label_keys=("concept_label",), domain_keys=("domain",), module_keys=("module",),
            status_keys=("source_status",), caveat_keys=("source_caveat",),
            semantics_keys=("value_semantics",), unit_keys=("unit",), document_keys=("source_document",))

for item in load("blood_biomarker_crosswalk_v1.csv").to_dict("records"):
    if text(item, "concept_id") == "blood_collection_metadata":
        continue
    add(item, role="p", file="blood_biomarker_crosswalk_v1.csv",
        wave_key="wave", code_key="variable", concept_key="concept_id",
        label_keys=("concept_label",), domain_keys=("domain",), module_keys=("module",),
        status_keys=("source_status",), caveat_keys=("collection_scope",),
        semantics_keys=("value_semantics",), unit_keys=("unit",),
        document_keys=("source_document",))

# The 31-concept core coverage is a prepared-data audit layer; carry it as a
# separate source mapping and translate its explicit role without promoting it.
core_dict = load("core_concept_dictionary_v1.csv").set_index("concept_id").to_dict("index")
core_role = {"exposure_proxy": "e", "phenotype_or_measurement": "p", "measurement_metadata": "c"}
for item in load("core_concept_coverage_v1.csv").to_dict("records"):
    concept = text(item, "concept_id")
    if text(item, "role") not in core_role:
        continue
    d = core_dict.get(concept, {})
    rows.append({
        "Concept.ID": concept,
        "Concept.Label": text(d, "concept_zh", default=concept),
        "Role": core_role[text(item, "role")],
        "Domain": text(d, "domain"), "Wave": text(item, "wave"),
        "Source.Code": text(item, "raw_variable").lower(),
        "Source.Label": text(item, "raw_label"), "Module": text(item, "module"),
        "Source.Archive": "", "Unit": "", "Value.Labels": "",
        "Value.Semantics": text(d, "harmonization_caveat"),
        "Mapping.Status": text(item, "status", default="prepared core concept mapping; review evidence in core audit"),
        "Caveat": text(d, "harmonization_caveat"),
        "Source.File": "audit/core_concept_coverage_v1.csv",
        "Source.Document": "audit/core_concept_dictionary_v1.csv",
    })

master = pd.DataFrame(rows)
master = master[master["Wave"].isin(["2011", "2013", "2015", "2018", "2020"]) & master["Source.Code"].ne("")]
# The housing specialty review also covers a small set of housing fields
# represented in the food/environment crosswalk to prevent duplicate concept
# assignments. Attach those reviewed Codebook labels to the existing mappings.
housing_label_path = AUDIT / "housing_value_label_review_v1.csv"
if housing_label_path.exists():
    housing_labels = load("housing_value_label_review_v1.csv")
    for item in housing_labels.to_dict("records"):
        labels = text(item, "value_labels")
        if not labels:
            continue
        selected = (
            master["Wave"].astype(str).eq(text(item, "wave"))
            & master["Source.Code"].str.lower().eq(text(item, "code").lower())
            & master["Source.File"].eq("audit/food_environment_crosswalk_v1.csv")
        )
        blank = selected & master["Value.Labels"].eq("")
        master.loc[blank, "Value.Labels"] = labels
        master.loc[blank, "Source.Document"] = text(item, "value_label_source")
master["_Module.Key"] = master["Module"].astype(str).str.strip().str.lower()
master = master.drop_duplicates(["Concept.ID", "Role", "Wave", "Source.Code", "Module", "Source.File"])
source_provenance_duplicates_collapsed = len(master) - len(master.drop_duplicates(["Concept.ID", "Role", "Wave", "Source.Code", "Module"]))

# Consolidate only explicitly reviewed same-measurement/analyte aliases. Keep
# the input concept ID on each source row so the decision remains reversible
# and fully auditable.
alias_path = AUDIT / "concept_alias_canonicalization_v1.csv"
aliases = pd.read_csv(alias_path, dtype=str, encoding="utf-8-sig").fillna("")
alias_map = dict(zip(aliases["alias_concept_id"], aliases["canonical_concept_id"]))
master["Source.Concept.ID"] = master["Concept.ID"]
master["Concept.ID"] = master["Concept.ID"].map(lambda value: alias_map.get(value, value))

# The generic prepared-core table and a domain audit often point to the same
# concept/source field. Keep one mapping link while retaining every provenance
# document and distinct review note. Separate concept IDs are intentionally
# not collapsed here; they require explicit alias/parent/derivation review.
link_keys = ["Concept.ID", "Role", "Wave", "Source.Code", "Module"]
provenance_columns = ["Source.Concept.ID", "Source.File", "Source.Document", "Mapping.Status", "Value.Semantics", "Caveat"]
collapsed = []
for _, group in master.groupby(link_keys, sort=False, dropna=False):
    # Prefer the domain-specific mapping as the display row, then append the
    # generic-core evidence instead of letting it create another mapping.
    group = group.copy()
    group["_canonical_rank"] = group["Source.Concept.ID"].ne(group["Concept.ID"]).astype(int)
    group["_core_rank"] = group["Source.File"].eq("audit/core_concept_coverage_v1.csv").astype(int)
    base = group.sort_values(["_canonical_rank", "_core_rank"], kind="stable").iloc[0].drop(labels=["_canonical_rank", "_core_rank"]).copy()
    for column in provenance_columns:
        values = [str(value).strip() for value in group[column] if str(value).strip()]
        values = list(dict.fromkeys(values))
        # Do not let a generic discovery-stage status dilute a later, exact
        # source review for the same concept/field (for example, housing
        # mappings that also appear in the broader food/environment index).
        if column == "Mapping.Status" and len(values) > 1:
            values = [value for value in values if value != "catalog-label candidate; questionnaire review pending"] or values
        base[column] = " | ".join(values)
    collapsed.append(base)
master = pd.DataFrame(collapsed).reset_index(drop=True)

# Keep an explicit field-level review queue for cases where one CHARLS
# wave/code/role still points to multiple distinct concepts. These are not
# silently merged: they can be aliases, parent/child derivations, or mistakes.
collision_rows = []
for (wave, code, module, role), group in master.groupby(["Wave", "Source.Code", "_Module.Key", "Role"], sort=True, dropna=False):
    concepts = sorted(set(group["Concept.ID"].astype(str)))
    if len(concepts) < 2:
        continue
    collision_rows.append({
        "Wave": wave,
        "Source.Code": code,
        "Module": module,
        "Role": role,
        "Candidate.Concept.IDs": "; ".join(concepts),
        "Candidate.Concept.Labels": "; ".join(sorted(set(group["Concept.Label"].astype(str)))),
        "Source.Labels": "; ".join(sorted(set(group["Source.Label"].astype(str)))),
        "Source.Files": "; ".join(sorted({part.strip() for value in group["Source.File"] for part in str(value).split(" | ") if part.strip()})),
        "Review.Status": "unresolved; review alias, derived/parent construct, or mapping error before analysis",
    })
collision_path = AUDIT / "ep_concept_link_collision_review_v1.csv"
pd.DataFrame(collision_rows, columns=[
    "Wave", "Source.Code", "Module", "Role", "Candidate.Concept.IDs",
    "Candidate.Concept.Labels", "Source.Labels", "Source.Files", "Review.Status",
])

overlap_rules = [
    ("respondent_biological_father_ethnic_minority_status_2015",
     "respondent_biological_mother_ethnic_minority_status_2015",
     "relationship_stratified_parent_record_measure",
     "The same generic Parent-module source code applies to separate biological-parent records. Filter parentID=1 for father or parentID=2 for mother; do not merge the two records or treat the source row as two answers from one respondent."),
    ("respondent_biological_father_ethnic_group_2015",
     "respondent_biological_mother_ethnic_group_2015",
     "relationship_stratified_parent_record_measure",
     "The same generic Parent-module source code applies to separate biological-parent records, conditional on the parent-specific minority-status response being Yes. Filter parentID=1 for father or parentID=2 for mother; retain nominal categories and do not merge the records."),
    ("respondent_biological_fathers_education",
     "respondent_biological_mothers_education",
     "relationship_stratified_parent_record_measure",
     "The same generic Parent-module ca009 field is stored once per parent record. For 2013 filter parentID=1/2 and ca003=1 (biological parent); for 2015 filter parentID=1/2 (biological father/mother). Keep father and mother as separate respondent-level concepts; do not interpret the same generic source row as two answers."),
    ("physical_activity_occurrence", "vigorous_activity_10min", "umbrella_group_not_independent_measure", "CHARLS measures intensity-specific occurrence in separate items; `physical_activity_occurrence` is an umbrella grouping, not a separate overall activity response. If an any-activity indicator is needed, derive it from eligible intensity items under a prespecified rule. Do not count the umbrella alongside vigorous activity as an independent exposure."),
    ("moderate_activity_10min", "physical_activity_occurrence", "umbrella_group_not_independent_measure", "CHARLS measures intensity-specific occurrence in separate items; `physical_activity_occurrence` is an umbrella grouping, not a separate overall activity response. If an any-activity indicator is needed, derive it from eligible intensity items under a prespecified rule. Do not count the umbrella alongside moderate activity as an independent exposure."),
    ("smoke_ever", "smoking_status", "component_of_composite_status", "Ever-smoking and current/cessation status are related components. In follow-up waves a prior positive ever-smoking record can route respondents past DA059 to a current-status item; missing DA059 is therefore not equivalent to never smoking. DA061_W3 (2015) asks status at the last interview, while DA061_W4 (2018) asks current status; preserve the wave-specific reference time and route, and do not model composite and component indicators as independent exposures."),
    ("smoking_status", "still_smoking_among_ever_smokers", "component_of_composite_status", "Current smoking among ever-smokers contributes to smoking status; preserve the denominator and route. A prior-wave positive record may skip the ever-smoking item, so missing ever-smoking response is not No. 2015 DA061_W3 refers to the last interview (not current 2015 status); 2018 DA061_W4 asks current status. Do not double count a composite and its component."),
    ("alcohol_past_year", "alcohol_recent", "binary_derived_from_frequency_categories", "Official wave Codebooks define the shared DA067 (2020 DA051) response as: 1=drank more than once/month, 2=drank less than once/month, 3=none. If a binary past-year drinking indicator is prespecified, derive Yes from 1/2 and No from 3; it is a recode of the raw frequency item, not an independent exposure. Preserve the three-level response and routed/missing states."),
    ("pain_intensity", "pain_yesterday", "same_item_temporal_scope_alias", "Same 2013 ordinal response item; retain the yesterday reference period in the harmonized definition."),
    ("pain_intensity", "pain_presence", "binary_derived_from_ordinal_severity", "Pain presence is derivable from the ordinal no-pain-to-severe response; preserve raw categories and predefine the threshold."),
    ("last_job_business_workforce_size_2018", "last_self_employed_business_employee_count_2018", "same_measurement_alias", "Both concepts map to the same 2018 FL012_W4 employee-count question, asked on the prior self-employed business route (FL001=2). Canonicalize to one field-level concept; do not count it twice or confuse it with current-business workforce size."),
]
rule_map = {tuple(sorted((left, right))): (kind, note) for left, right, kind, note in overlap_rules}
digital_concepts = {
    "internet_use_social_activity", "internet_device_desktop", "internet_device_laptop",
    "internet_device_tablet", "internet_device_cellphone", "internet_device_other",
    "internet_activity_chat", "internet_activity_news", "internet_activity_video",
    "internet_activity_games", "internet_activity_financial_management",
    "internet_activity_other", "mobile_payment_use", "wechat_use",
    "wechat_moments_posting",
}
relationship_rows = []
for row in collision_rows:
    ids = row["Candidate.Concept.IDs"].split("; ")
    rule = rule_map.get(tuple(sorted(ids)))
    if rule is None and "social_participation" in ids and digital_concepts.intersection(ids):
        rule = (
            "specific_digital_option_within_social_participation_checklist",
            "The same wave-specific source field is represented as a specific internet/device/activity concept and as an option in the broader social-participation checklist. Preserve the source item, route, and option identity; do not count the duplicate concept links as independent exposures. For selected-option fields, absence is not No; verify released-data storage and the eligible denominator before analysis.",
        )
    if rule:
        kind, note = rule
        review_status = "relationship classified from official item wording/labels; verify analytic routing/denominator and any recode before analysis"
        row["Review.Status"] = "classified relationship; raw source retained; analytic denominator/recode still pending"
    else:
        kind = "unclassified_multiple_concept_link"
        note = "Requires wave-specific questionnaire/codebook review to distinguish alias, parent/child, derivation, or mapping error."
        review_status = "needs manual audit before analysis"
    relationship_rows.append({
        "Wave": row["Wave"], "Source.Code": row["Source.Code"], "Module": row["Module"], "Role": row["Role"],
        "Candidate.Concept.IDs": row["Candidate.Concept.IDs"], "Relationship.Type": kind,
        "Interpretation": note, "Review.Status": review_status,
    })
pd.DataFrame(collision_rows, columns=[
    "Wave", "Source.Code", "Module", "Role", "Candidate.Concept.IDs",
    "Candidate.Concept.Labels", "Source.Labels", "Source.Files", "Review.Status",
]).to_csv(collision_path, index=False, encoding="utf-8-sig")
relationship_path = AUDIT / "ep_concept_link_relationship_review_v1.csv"
pd.DataFrame(relationship_rows, columns=[
    "Wave", "Source.Code", "Module", "Role", "Candidate.Concept.IDs", "Relationship.Type",
    "Interpretation", "Review.Status",
]).to_csv(relationship_path, index=False, encoding="utf-8-sig")

fields = load("charls_atlas_candidate_fields_v0.csv")
ep_fields = fields[fields["epcf"].isin(["e", "p", "e,p", "p,e"])].copy()
catalog_keys = set()
for item in fields.to_dict("records"):
    role_text = str(item.get("epcf", "")).strip()
    roles = [role_text, *[part.strip() for part in role_text.split(",")]]
    for role in roles:
        catalog_keys.add((str(item.get("Source.Wave", "")), str(item.get("Variable.Name", "")).lower(), str(item.get("Data.File.Name", "")).strip().lower(), role))

# Some domain crosswalks were originally assembled as exposure candidates
# before an explicit catalog role audit reclassified their source fields as
# C-only measurement/response-format metadata. Apply those exact, reviewed
# E/P -> C decisions here as well, so the concept-source index and pair
# explorer cannot retain a selector as an exposure after the master catalog
# has removed that role.
role_override_path = AUDIT / "catalog_role_override_review_v1.csv"
if role_override_path.exists():
    role_overrides = load("catalog_role_override_review_v1.csv")
    c_catalog_keys = {key[:3] for key in catalog_keys if key[3] == "c"}
    for override in role_overrides.to_dict("records"):
        wave = str(override.get("wave", "")).strip()
        code = str(override.get("code", "")).strip().lower()
        old_role = str(override.get("remove_role", "")).strip().lower()
        keep_role = str(override.get("keep_role", "")).strip().lower()
        if keep_role != "c" or old_role not in {"e", "p", "e,p", "p,e"}:
            continue
        concept_ids = {x.strip() for x in str(override.get("concept_ids", "")).split(";") if x.strip()}
        selected = (
            master["Wave"].astype(str).eq(wave)
            & master["Source.Code"].astype(str).str.lower().eq(code)
            & master["Role"].astype(str).str.lower().eq(old_role)
        )
        if concept_ids:
            selected &= master["Concept.ID"].astype(str).isin(concept_ids) | master["Source.Concept.ID"].astype(str).isin(concept_ids)
        for idx in master.index[selected]:
            c_key = (str(master.at[idx, "Wave"]), str(master.at[idx, "Source.Code"]).lower(), str(master.at[idx, "Module"]).strip().lower())
            if c_key not in c_catalog_keys:
                continue
            master.at[idx, "Role"] = "c"
            status = str(master.at[idx, "Mapping.Status"]).strip()
            marker = "reclassified to C-only metadata by audit/catalog_role_override_review_v1.csv"
            if marker not in status:
                master.at[idx, "Mapping.Status"] = f"{status} | {marker}" if status else marker
            rationale = str(override.get("rationale", "")).strip()
            caveat = str(master.at[idx, "Caveat"]).strip()
            if rationale and rationale not in caveat:
                master.at[idx, "Caveat"] = f"{caveat} {rationale}".strip()
            source_document = str(master.at[idx, "Source.Document"]).strip()
            override_source = "audit/catalog_role_override_review_v1.csv"
            if override_source not in source_document:
                master.at[idx, "Source.Document"] = f"{source_document}; {override_source}".strip("; ")

master["Catalog.Match"] = [
    "matched" if (str(r.Wave), str(r["Source.Code"]).lower(), str(r["Module"]).strip().lower(), str(r.Role)) in catalog_keys else "not in E/P candidate catalog"
    for _, r in master.iterrows()
]
master = master.sort_values(["Role", "Concept.ID", "Wave", "Module", "Source.Code", "Source.File"], kind="stable")
master.to_csv(OUT, index=False, encoding="utf-8-sig")

master["_wave_code"] = master["Wave"].astype(str) + "::" + master["_Module.Key"] + "::" + master["Source.Code"].astype(str).str.lower()
master["_mapped_wave_code"] = master["_wave_code"].where(master["Catalog.Match"].eq("matched"), "")
def canonical_role(role_values: pd.Series) -> str:
    roles = {part.strip() for value in role_values for part in str(value).split(",")}
    if "e" in roles or "p" in roles:
        return ",".join(role for role in ("e", "p") if role in roles)
    return "c" if "c" in roles else ",".join(sorted(roles))

# A concept may have E source fields in one audited table and P source fields
# in another (for example, a loneliness item used in both roles). Keep the
# source rows' individual roles intact in the crosswalk, but report one
# canonical concept row with the union of its roles in the summary.
summary = (master.groupby("Concept.ID", dropna=False)
           .agg(**{
               "Role": ("Role", canonical_role),
               "Concept.Label": ("Concept.Label", "first"),
               "waves": ("Wave", lambda s: ",".join(sorted(set(s)))),
               "source_field_mappings": ("Source.Code", "size"),
               "unique_wave_module_fields": ("_wave_code", "nunique"),
               "mapped_wave_module_fields": ("_mapped_wave_code", lambda s: s[s.ne("")].nunique()),
               "source_files": ("Source.File", lambda s: ";".join(sorted(set(s)))),
               "source_alias_ids": ("Source.Concept.ID", lambda s: ";".join(sorted(set(s) - {str(master.loc[s.index[0], "Concept.ID"])}))),
               "mapping_statuses": ("Mapping.Status", lambda s: " | ".join(sorted(set(s)))),
               "wave_field_codes": ("_wave_code", lambda s: ";".join(sorted(set(s)))),
           }).reset_index())
summary["wave_count"] = summary["waves"].str.split(",").str.len()
summary["catalog_coverage_pct"] = (100 * summary["mapped_wave_module_fields"] / summary["unique_wave_module_fields"]).round(1)
summary.to_csv(AUDIT / "ep_concept_candidate_summary_v1.csv", index=False, encoding="utf-8-sig")

# Attach explicit candidate concept IDs to the field catalog and its series
# JSON so the website can search/display the code-to-concept mapping.
concept_keys: dict[tuple[str, str, str, str], set[tuple[str, str, str, str, str, str]]] = {}
objective_concept_keys: dict[tuple[str, str], set[tuple[str, str, str, str, str, str]]] = {}
for r in master[master["Catalog.Match"].eq("matched")].to_dict("records"):
    roles = [r["Role"]]
    if r["Role"] == "e,p":
        roles = ["e", "p", "e,p"]
    for role in roles:
        key = (str(r["Wave"]), str(r["Source.Code"]).lower(), str(r["Module"]).strip().lower(), role)
        concept_keys.setdefault(key, set()).add((str(r["Concept.ID"]), str(r["Concept.Label"]), str(r["Source.File"]), str(r["Mapping.Status"]), str(r["Unit"]), str(r["Source.Concept.ID"])))
    if str(r["Source.File"]).strip() == "audit/objective_measurement_crosswalk_v1.csv" and str(r["Role"]).lower() == "p":
        objective_concept_keys.setdefault((str(r["Wave"]), str(r["Source.Code"]).lower()), set()).add(
            (str(r["Concept.ID"]), str(r["Concept.Label"]), str(r["Source.File"]), str(r["Mapping.Status"]), str(r["Unit"]), str(r["Source.Concept.ID"]))
        )

def concepts_for(wave: str, code: str, module: str, role_text: str, category: str = "") -> list[tuple[str, str, str, str, str, str]]:
    found: set[tuple[str, str, str, str, str, str]] = set()
    for role in [role_text, *[x.strip() for x in role_text.split(",")]]:
        found.update(concept_keys.get((str(wave), str(code).lower(), str(module).strip().lower(), role), set()))
    # The objective-measurement audit maps exact wave/code/P fields from the
    # official instrument; the release catalogue may name its containing file
    # "biomarkers" instead. Bridge only those reviewed P fields (never E or C)
    # by exact wave and code, and only within the physical-function category.
    if not found and role_text.strip().lower() == "p" and category.strip().lower() in {
        "physical function", "blood pressure", "anthropometric"
    }:
        found.update(objective_concept_keys.get((str(wave), str(code).lower()), set()))
    return sorted(found)

field_path = AUDIT / "charls_atlas_candidate_fields_v0.csv"
field_catalog = pd.read_csv(field_path, dtype=str, encoding="utf-8-sig").fillna("")
field_identity = ["Source.Wave", "Variable.Name", "Data.File.Name", "epcf", "category", "subcategory"]
field_catalog = field_catalog.drop_duplicates(field_identity, keep="first").copy()
mapped_fields = [concepts_for(r["Source.Wave"], r["Variable.Name"], r["Data.File.Name"], r["epcf"], r.get("category", "")) for r in field_catalog.to_dict("records")]
field_catalog["Concept.ID.Candidates"] = ["; ".join(sorted({x[0] for x in xs})) for xs in mapped_fields]
field_catalog["Concept.Alias.IDs"] = ["; ".join(sorted({alias for x in xs for alias in x[5].split(" | ") if alias and alias != x[0]})) for xs in mapped_fields]
field_catalog["Concept.Label.Candidates"] = ["; ".join(sorted({x[1] for x in xs})) for xs in mapped_fields]
field_catalog["Concept.Mapping.Source"] = ["; ".join(sorted({x[2] for x in xs})) for xs in mapped_fields]
field_catalog["Concept.Mapping.Status"] = [" | ".join(sorted({x[3] for x in xs})) for xs in mapped_fields]
mapped_units = ["; ".join(sorted({f"{x[0]}={x[4]}" for x in xs if x[4]})) for xs in mapped_fields]
# A source crosswalk can legitimately omit a unit even when a separate
# questionnaire-based review has already established one in the field
# catalogue. Preserve those reviewed units on rebuild instead of erasing
# them merely because the concept link itself has no unit annotation.
field_catalog["Concept.Unit.Candidates"] = [
    mapped or str(existing).strip()
    for mapped, existing in zip(mapped_units, field_catalog["Concept.Unit.Candidates"].fillna(""))
]
# Re-apply exact, reviewed E/P -> C-only overrides after joining specialist
# concept maps. C-only selector/measurement fields may retain labels and
# units for interpretation, but must not regain an E/P candidate concept ID.
if role_override_path.exists():
    c_only_overrides = role_overrides[
        role_overrides["keep_role"].astype(str).str.strip().str.lower().eq("c")
        & role_overrides["remove_role"].astype(str).str.strip().str.lower().isin({"e", "p", "e,p", "p,e"})
    ]
    for override in c_only_overrides.to_dict("records"):
        selected = (
            field_catalog["Source.Wave"].astype(str).eq(str(override.get("wave", "")).strip())
            & field_catalog["Variable.Name"].astype(str).str.lower().eq(str(override.get("code", "")).strip().lower())
        )
        candidate_ids = {x.strip() for x in str(override.get("concept_ids", "")).split(";") if x.strip()}
        if candidate_ids:
            selected &= field_catalog["Concept.ID.Candidates"].map(
                lambda value: bool(candidate_ids.intersection({x.strip() for x in str(value).split(";") if x.strip()}))
            )
        for column in (
            "Concept.ID.Candidates", "Concept.Alias.IDs", "Concept.Label.Candidates",
            "Concept.Mapping.Source", "Concept.Mapping.Status", "Concept.Unit.Candidates",
        ):
            field_catalog.loc[selected, column] = ""
# Preserve the audited continuous calendar-year unit for disability-onset
# fields; the concept-source mapping layer otherwise replaces this metadata
# with an empty string because these timing fields have no mapped discrete unit.
disability_crosswalk_path = AUDIT / "disability_history_crosswalk_v1.csv"
if disability_crosswalk_path.exists():
    disability_crosswalk = pd.read_csv(disability_crosswalk_path, dtype=str, encoding="utf-8-sig").fillna("")
    onset_years = disability_crosswalk[
        disability_crosswalk["field_role"].str.contains("onset year", case=False, na=False)
    ]
    for item in onset_years.to_dict(orient="records"):
        selected = (
            field_catalog["Source.Wave"].astype(str).eq(str(item.get("wave", "")))
            & field_catalog["Variable.Name"].str.lower().eq(str(item.get("code", "")).lower())
            & field_catalog["Value.Labels"].fillna("").eq("")
        )
        field_catalog.loc[selected, "Concept.Unit.Candidates"] = "calendar year"
# DA009's numeric time fields have a verified wave-specific unit, but their
# concept mappings deliberately keep diagnosis year and age as separate
# concepts. Preserve that unit metadata in the catalog even when the source
# mapping's concept unit is otherwise blank.
diagnosis_time_unit = (
    field_catalog["Source.Wave"].astype(str).isin({"2011", "2013", "2015", "2018"})
    & field_catalog["Variable.Name"].str.lower().str.fullmatch(r"da009_[12]_\d+_?")
)
diagnosis_index = field_catalog["Variable.Name"].str.lower().str.extract(r"da009_[12]_(\d+)_?")[0]
diagnosis_time_unit &= diagnosis_index.isin({str(i) for i in range(1, 15)})
for idx in field_catalog.index[diagnosis_time_unit]:
    code = str(field_catalog.at[idx, "Variable.Name"]).lower()
    field_catalog.at[idx, "Concept.Unit.Candidates"] = "calendar year" if code.startswith("da009_1_") else "age in years"
if diagnosis_time_unit.any():
    print(f"verified diagnosis-time unit rows={int(diagnosis_time_unit.sum())}; unique wave fields={field_catalog.loc[diagnosis_time_unit, ['Source.Wave', 'Variable.Name']].drop_duplicates().shape[0]}; year and age kept separate")
prostate_diagnosis_time_unit = (
    field_catalog["Source.Wave"].astype(str).isin({"2011", "2013", "2015", "2018"})
    & field_catalog["Variable.Name"].str.lower().isin({"da030_1", "da030_2"})
)
for idx in field_catalog.index[prostate_diagnosis_time_unit]:
    code = str(field_catalog.at[idx, "Variable.Name"]).lower()
    field_catalog.at[idx, "Concept.Unit.Candidates"] = "calendar year" if code == "da030_1" else "age in years"
if prostate_diagnosis_time_unit.any():
    print(f"verified prostate-illness diagnosis-time unit rows={int(prostate_diagnosis_time_unit.sum())}; year and age kept separate")
stroke_timing_unit = (
    field_catalog["Source.Wave"].astype(str).isin({"2013", "2015", "2018"})
    & field_catalog["Variable.Name"].str.lower().str.fullmatch(r"da019_w2_2_[12]")
)
for idx in field_catalog.index[stroke_timing_unit]:
    wave = str(field_catalog.at[idx, "Source.Wave"])
    code = str(field_catalog.at[idx, "Variable.Name"]).lower()
    if code.endswith("_1"):
        unit = "calendar year"
    elif wave == "2013":
        unit = "month"
    else:
        unit = "age in years"
    field_catalog.at[idx, "Concept.Unit.Candidates"] = unit
if stroke_timing_unit.any():
    print(f"verified recurrent-stroke timing unit rows={int(stroke_timing_unit.sum())}; units are wave-specific")
# Distinguish numeric/time fields with reviewed mapped units from categorical
# fields whose value-label audit is still pending. Do not infer units from a
# variable name, and exclude selectors, categories, and unfolding bounds.
numeric_unit = re.compile(r"\b(yuan|cny|percent(?:age)?|years?|months?|days?|weeks?|hours?|minutes?|seconds?|cm|mmhg|kg|meters?|times|count|age|bpm|kg/m2|liters?|ml)\b", re.I)
excluded_unit_context = re.compile(r"categorical|interval bound|selector|response.?format|bracket", re.I)
mapped_numeric = (
    field_catalog["epcf"].isin({"e", "p", "e,p", "p,e"})
    & field_catalog["Value.Label.Review"].eq("not yet reviewed")
    & field_catalog["Value.Labels"].fillna("").str.strip().eq("")
    & field_catalog["Concept.Unit.Candidates"].fillna("").apply(lambda value: bool(numeric_unit.search(value)) and not excluded_unit_context.search(value))
)
field_catalog.loc[mapped_numeric, "Value.Label.Review"] = "numeric/time unit metadata available; no discrete labels assigned; see concept crosswalk"
mapped_sources = field_catalog.loc[mapped_numeric, "Concept.Mapping.Source"].fillna("").astype(str).str.strip()
existing_sources = field_catalog.loc[mapped_numeric, "Value.Label.Source"].fillna("").astype(str).str.strip()
field_catalog.loc[mapped_numeric, "Value.Label.Source"] = [old or new for old, new in zip(existing_sources, mapped_sources)]
caveat_keys: dict[tuple[str, str, str, str], set[str]] = {}
for r in master[master["Catalog.Match"].eq("matched")].to_dict("records"):
    roles = [r["Role"]]
    if r["Role"] == "e,p":
        roles = ["e", "p", "e,p"]
    for role in roles:
        caveat = str(r.get("Caveat", "")).strip()
        if caveat:
            caveat_keys.setdefault((str(r["Wave"]), str(r["Source.Code"]).lower(), str(r["Module"]).strip().lower(), role), set()).add(caveat)
field_catalog["Concept.Mapping.Caveat"] = [
    " | ".join(sorted(caveat_keys.get((str(r["Source.Wave"]), str(r["Variable.Name"]).lower(), str(r["Data.File.Name"]).strip().lower(), str(r["epcf"])), set())))
    for r in field_catalog.to_dict("records")
]
collision_table = pd.read_csv(collision_path, dtype=str, encoding="utf-8-sig").fillna("")
collision_keys = {(str(r["Wave"]), str(r["Source.Code"]).lower(), str(r["Module"]).strip().lower(), str(r["Role"]))
                  for _, r in collision_table.iterrows()}
relationship_table = pd.read_csv(relationship_path, dtype=str, encoding="utf-8-sig").fillna("")
relationship_notes = {(str(r["Wave"]), str(r["Source.Code"]).lower(), str(r["Module"]).strip().lower(), str(r["Role"])):
                      f"{r['Relationship.Type']}: {r['Interpretation']}"
                      for _, r in relationship_table.iterrows()}
def collision_note(wave: str, code: str, module: str, role_text: str) -> str:
    roles = [role_text, *[part.strip() for part in role_text.split(",")]]
    if any((str(wave), str(code).lower(), str(module).strip().lower(), role) in collision_keys for role in roles):
        return "multiple candidate concepts for this wave/module/code/role; inspect audit/ep_concept_link_collision_review_v1.csv; do not count each candidate as an independent test"
    return ""
def relationship_note(wave: str, code: str, module: str, role_text: str) -> str:
    roles = [role_text, *[part.strip() for part in role_text.split(",")]]
    notes = {relationship_notes[(str(wave), str(code).lower(), str(module).strip().lower(), role)]
             for role in roles if (str(wave), str(code).lower(), str(module).strip().lower(), role) in relationship_notes}
    return " | ".join(sorted(notes))
field_catalog["Concept.Mapping.Collision"] = [
    collision_note(r["Source.Wave"], r["Variable.Name"], r["Data.File.Name"], r["epcf"])
    for r in field_catalog.to_dict("records")
]
field_catalog["Concept.Mapping.Relationship"] = [
    relationship_note(r["Source.Wave"], r["Variable.Name"], r["Data.File.Name"], r["epcf"])
    for r in field_catalog.to_dict("records")
]
field_catalog.to_csv(field_path, index=False, encoding="utf-8-sig")
ep_fields = field_catalog[field_catalog["epcf"].isin(["e", "p", "e,p", "p,e"])].copy()

series_path = AUDIT / "charls_atlas_candidate_series_v0.csv"
series = pd.read_csv(series_path, dtype=str, encoding="utf-8-sig").fillna("")
series_mappings = []
for r in series.to_dict("records"):
    concepts: set[tuple[str, str, str, str, str]] = set()
    for wave in str(r.get("waves", "")).split(","):
        for module in str(r.get("source_modules", "")).split(","):
            concepts.update(concepts_for(wave, r.get("Variable.Name", ""), module, r.get("epcf", "")))
    series_mappings.append(sorted(concepts))
series["candidate_concept_ids"] = ["; ".join(sorted({x[0] for x in xs})) for xs in series_mappings]
series["candidate_concept_alias_ids"] = ["; ".join(sorted({alias for x in xs for alias in x[5].split(" | ") if alias and alias != x[0]})) for xs in series_mappings]
series["candidate_concept_labels"] = ["; ".join(sorted({x[1] for x in xs})) for xs in series_mappings]
series["concept_mapping_sources"] = ["; ".join(sorted({x[2] for x in xs})) for xs in series_mappings]
series["concept_mapping_statuses"] = [" | ".join(sorted({x[3] for x in xs})) for xs in series_mappings]
series["candidate_concept_units"] = ["; ".join(sorted({f"{x[0]}={x[4]}" for x in xs if x[4]})) for xs in series_mappings]
series["concept_mapping_caveats"] = [" | ".join(sorted({c for wave in str(r.get("waves", "")).split(",")
    for c in caveat_keys.get((wave, str(r.get("Variable.Name", "")).lower(), str(r.get("epcf", ""))), set())}))
    for r in series.to_dict("records")]
series["concept_mapping_collision"] = [
    "multiple candidate concepts in one or more waves; inspect audit/ep_concept_link_collision_review_v1.csv"
    if any(collision_note(wave, r.get("Variable.Name", ""), module, r.get("epcf", ""))
           for module in str(r.get("source_modules", "")).split(",")
           for wave in str(r.get("waves", "")).split(",")) else ""
    for r in series.to_dict("records")]
series["concept_mapping_relationship"] = [
    " | ".join(sorted({relationship_note(wave, str(r.get("Variable.Name", "")), module, str(r.get("epcf", "")))
                       for module in str(r.get("source_modules", "")).split(",")
                       for wave in str(r.get("waves", "")).split(",")
                       if relationship_note(wave, str(r.get("Variable.Name", "")), module, str(r.get("epcf", "")))}))
    for r in series.to_dict("records")]
ep_series = series[series["epcf"].isin(["e", "p", "e,p", "p,e"])].copy()
series.to_csv(series_path, index=False, encoding="utf-8-sig")
series_json = json.dumps(series.to_dict(orient="records"), ensure_ascii=False, separators=(",", ":"))
(AUDIT / "charls_atlas_candidate_series_v0.json").write_text(series_json, encoding="utf-8")
# The website catalog is wave-field level so each answer label and unit stays
# attached to its exact CHARLS wave/code instead of being merged across waves.
site_catalog = field_catalog.copy()
site_catalog["waves"] = site_catalog["Source.Wave"]
site_catalog["wave_count"] = "1"
site_catalog["source_modules"] = site_catalog["Data.File.Name"]
site_catalog["value_labels"] = site_catalog["Value.Labels"]
site_catalog["value_label_source"] = site_catalog["Value.Label.Source"]
site_catalog["value_label_review"] = site_catalog["Value.Label.Review"]
site_catalog["harmonization_status"] = site_catalog["Harmonization.Status"]
site_catalog["candidate_concept_ids"] = site_catalog["Concept.ID.Candidates"]
site_catalog["candidate_concept_alias_ids"] = site_catalog["Concept.Alias.IDs"]
site_catalog["candidate_concept_labels"] = site_catalog["Concept.Label.Candidates"]
site_catalog["concept_mapping_sources"] = site_catalog["Concept.Mapping.Source"]
site_catalog["concept_mapping_statuses"] = site_catalog["Concept.Mapping.Status"]
site_catalog["concept_mapping_caveats"] = site_catalog["Concept.Mapping.Caveat"]
site_catalog["concept_mapping_collision"] = site_catalog["Concept.Mapping.Collision"]
site_catalog["concept_mapping_relationship"] = site_catalog["Concept.Mapping.Relationship"]
site_catalog["candidate_concept_units"] = site_catalog["Concept.Unit.Candidates"]
site_json = json.dumps(site_catalog.to_dict(orient="records"), ensure_ascii=False, separators=(",", ":"))
(AUDIT / "charls_atlas_candidate_fields_v0.json").write_text(site_json, encoding="utf-8")
(ROOT / "site-prototype" / "dist" / "catalog.json").write_text(site_json, encoding="utf-8")

e_only = summary[summary["Role"].eq("e")]["Concept.ID"].nunique()
dual = summary[summary["Role"].eq("e,p")]["Concept.ID"].nunique()
p_only = summary[summary["Role"].eq("p")]["Concept.ID"].nunique()
e_total, p_total = e_only + dual, p_only + dual
unmapped = ep_series[ep_series["candidate_concept_ids"].eq("")]
unmapped_top = (unmapped.groupby(["epcf", "category", "subcategory"]).size()
                .sort_values(ascending=False).head(15))
label_rows = int(ep_fields["Value.Labels"].fillna("").str.strip().ne("").sum())
label_pairs = int(ep_fields[ep_fields["Value.Labels"].fillna("").str.strip().ne("")]
                  .drop_duplicates(["Source.Wave", "Variable.Name"]).shape[0])
conflicts = int(ep_fields["Value.Label.Review"].eq("conflict").sum())
alias_source_links = int(master["Source.Concept.ID"].str.contains(" | ", regex=False).sum())
collision_count = len(collision_table)
c_mappings = int(master["Role"].eq("c").sum())
c_rows = master[master["Role"].eq("c")]
ep_rows = master[master["Role"].ne("c")]
lines = [
    "# E/P 候选概念映射覆盖审计",
    "",
    f"更新：{date.today().isoformat()}。由 scripts/build_ep_concept_source_crosswalk.py 从字段级审计 crosswalk 组装；概念 ID 均为候选，来源状态原样保留，不能当作已冻结的统计检验变量。",
    "",
    f"- E/P 目录：{len(ep_fields):,} 条字段—角色—类别行；{len(ep_series):,} 条去重变量码—角色—类别序列。另有C类候选 {len(field_catalog) - len(ep_fields):,} 条字段行/{len(series) - len(ep_series):,} 条变量码—角色—类别序列。",
    f"- 候选概念 ID：E-only {e_only}、P-only {p_only}、双角色 {dual}；E 侧 {e_total}、P 侧 {p_total}，去重 E/P 概念 ID {summary[summary['Role'].ne('c')]['Concept.ID'].nunique()}。",
    f"- 概念—源字段 crosswalk：{len(master):,} 条映射；E/P {len(ep_rows):,} 条全部匹配字段目录。C类映射 {c_mappings:,} 条（{int(c_rows['Catalog.Match'].eq('matched').sum())} 条匹配、{int(c_rows['Catalog.Match'].ne('matched').sum())} 条为非E/P测量资格/协议记录），不计入E/P候选。",
    f"- 来源追溯：已合并 {source_provenance_duplicates_collapsed:,} 条相同概念—字段的重复出处记录；按显式别名表规范 {len(aliases):,} 个概念别名、覆盖 {alias_source_links:,} 条字段链接，旧Concept ID仍保存在Source.Concept.ID/网站别名字段。",
    f"- 多概念字段重叠：规范别名后仍有 {collision_count:,} 个波次—字段—角色键关联多个候选概念；分类与分析边界见 ep_concept_link_relationship_review_v1.csv，网站字段显示关系提示。",
    f"- E/P字段目录中 {int(ep_fields['Concept.ID.Candidates'].ne('').sum()):,} 条字段行已附候选概念 ID；当前无候选Concept ID的E/P字段为 {len(unmapped):,} 条。已有候选映射不等于分析资格确认。",
    f"- 已审值标签/响应语义 {label_rows:,} 条，覆盖 {label_pairs:,} 个波次—字段码；目录自动标签检查发现 {conflicts} 条冲突。此自动计数仅覆盖 Value.Label.Review 列；已知的官方来源冲突仍需按专题审计处理，例如2011工作史 FB010 问卷与代码本编码不一致，未解决前不得分析。",
    "",
    "## 当前未归属概念ID的编码—类别记录较多的领域",
    "",
    "| 角色 | 类别 | 子类 | 编码—类别记录数 |",
    "|---|---|---|---:|",
]
for (role, category, subcategory), count in unmapped_top.items():
    lines.append(f"| {role} | {category} | {subcategory} | {int(count):,} |")
lines.extend([
    "",
    "候选概念数低于源字段数是预期现象：一个疾病领域可含诊断、复核、诊断时间、治疗/药物等不同测量；养老金与收入包含大量计划槽位、金额上下界和家庭/个人层级字段；每个领域都需要按官方题目和目标估计量再折叠。不得把目录记录数解释为最终暴露或表型指标数。",
    "",
    "完整映射见 ep_concept_source_crosswalk_v1.csv；按概念聚合的波次/字段和映射状态见 ep_concept_candidate_summary_v1.csv；网站E/P表同步展示候选概念ID与映射状态。",
])
(AUDIT / "ep_concept_mapping_coverage_v1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"concept_source_rows={len(master)}")
print(f"unique_role_concepts={summary.groupby('Role')['Concept.ID'].nunique().to_dict()}")
print(f"catalog_matches={master['Catalog.Match'].value_counts().to_dict()}")
print(f"unmatched role concepts={summary[summary.mapped_wave_module_fields.eq(0)].groupby('Role')['Concept.ID'].nunique().to_dict()}")

