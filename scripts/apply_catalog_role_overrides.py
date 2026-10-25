"""Apply audited exact-wave catalog role corrections to candidate metadata only."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from build_charls_atlas_catalog import preserve_existing_catalog_order

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"audit"
overrides=pd.read_csv(AUDIT/"catalog_role_override_review_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
keys={(r.wave.lower(),r.code.lower()) for r in overrides.itertuples(index=False) if r.keep_role.lower() == "p"}
dual_to_p={(r.wave.lower(),r.code.lower()) for r in overrides.itertuples(index=False) if r.keep_role.lower() == "p" and r.remove_role.lower() in {"e", "e,p"}}
metadata_keys={(r.wave.lower(),r.code.lower()) for r in overrides.itertuples(index=False) if r.keep_role.lower() == "c"}
analysis_locked_keys={(r.wave.lower(),r.code.lower()) for r in overrides.itertuples(index=False) if r.keep_role.lower() == "e"}
if len(keys)+len(metadata_keys)+len(analysis_locked_keys)!=len(overrides): raise SystemExit("duplicate or unsupported role override keys")

field_path=AUDIT/"charls_atlas_candidate_fields_v0.csv"
fields=pd.read_csv(field_path,dtype=str,encoding="utf-8-sig").fillna("")
raw_catalog=pd.read_csv(AUDIT/"raw_variable_catalog_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
bracket_labels_path=AUDIT/"pension_exposure_variable_mapping_v1.csv"
if bracket_labels_path.exists():
    bracket_labels=pd.read_csv(bracket_labels_path,dtype=str,encoding="utf-8-sig").fillna("")
    bracket_labels=bracket_labels.loc[bracket_labels["wave"].astype(str).eq("2011") & bracket_labels["code"].astype(str).str.lower().isin({f"fn064_{i}" for i in range(1,5)} | {f"fn070_{i}" for i in range(1,5)})]
    bracket_label_map={str(r.code).lower():r for r in bracket_labels.itertuples(index=False)}
else:
    bracket_label_map={}
concept_col=fields["Concept.ID.Candidates"] if "Concept.ID.Candidates" in fields else pd.Series([""]*len(fields),index=fields.index)
existing={(str(r["Source.Wave"]).lower(),str(r["Variable.Name"]).lower(),str(r["epcf"]).lower()) for _,r in fields.iterrows()}
for wave,code in keys:
    if (wave,code,"p") not in existing:
        raise SystemExit(f"role override lacks P candidate row: {wave}/{code}")
for wave,code in analysis_locked_keys:
    source = raw_catalog[(raw_catalog.wave.str.lower().eq(wave)) & raw_catalog.variable.str.lower().eq(code)]
    if source.empty:
        raise SystemExit(f"analysis-lock override lacks official source field: {wave}/{code}")
for row in overrides.loc[overrides["keep_role"].str.lower().eq("c")].itertuples(index=False):
    wave,code,old_role=row.wave.lower(),row.code.lower(),row.remove_role.lower()
    if (wave,code,old_role) not in existing and (wave,code,"c") not in existing:
        source = raw_catalog[(raw_catalog.wave.str.lower().eq(wave)) & raw_catalog.variable.str.lower().eq(code)]
        if source.empty:
            raise SystemExit(f"metadata role override lacks official source field: {wave}/{code}/{old_role}")
# Remove only redundant automatic E/dual-role rows when the audited override
# retains P and no explicit candidate concept is attached. Preserve the P row
# and any future explicit E concept mapping.
concept_col=fields["Concept.ID.Candidates"] if "Concept.ID.Candidates" in fields else pd.Series([""]*len(fields),index=fields.index)
mask=(fields["epcf"].str.lower().eq("e") & fields.apply(lambda r:(str(r["Source.Wave"]).lower(),str(r["Variable.Name"]).lower()) in keys,axis=1) & concept_col.eq(""))
mask |= (fields["epcf"].str.lower().eq("e,p") & fields.apply(lambda r:(str(r["Source.Wave"]).lower(),str(r["Variable.Name"]).lower()) in dual_to_p,axis=1) & concept_col.eq(""))
removed_fields=int(mask.sum())
fields=fields.loc[~mask].copy()

# Prior-interview answer flags are route/availability metadata. Convert them
# from automatically inferred E roles to C metadata, while preserving an
# already-present C row (zda065) instead of creating a duplicate.
metadata_removed=0
for wave,code in metadata_keys:
    override = overrides.loc[overrides["wave"].str.lower().eq(wave) & overrides["code"].str.lower().eq(code)].iloc[0]
    old_role = str(override["remove_role"]).lower()
    metadata_type = str(override.get("metadata_type", "")).strip().lower()
    if metadata_type == "subjective_expectation_age_target_selector" and old_role == "c":
        # Reclassify the existing auto-discovered C row in place; do not
        # remove it as a duplicate just because its current role is already C.
        selected=(fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code) & fields["epcf"].str.lower().eq("c"))
    elif metadata_type in {"age_year_component_selector", "housing_property_value_measure_selector", "beer_amount_unit_selector"}:
        # These explicit concept-linked rows describe the coding of paired
        # age/year fields; their E role is still metadata and must be removed.
        selected=(fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code) & fields["epcf"].str.lower().eq(old_role))
    else:
        selected=(fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code) & fields["epcf"].str.lower().eq(old_role) & concept_col.eq(""))
    has_c=((fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code) & fields["epcf"].str.lower().eq("c")).any())
    if not selected.any() and not has_c:
        source=raw_catalog[(raw_catalog.wave.str.lower().eq(wave)) & raw_catalog.variable.str.lower().eq(code)].iloc[0]
        same_module=fields[(fields["Source.Wave"].str.lower().eq(wave)) & fields["Data.File.Name"].str.lower().eq(str(source.module).lower())]
        module_description=same_module.iloc[0]["Data.File.Description"] if not same_module.empty else str(source.module)
        fields=pd.concat([fields,pd.DataFrame([{
            "Variable.Name":str(source.variable), "Variable.Description":str(source.variable_label),
            "Data.File.Name":str(source.module), "Data.File.Description":str(module_description),
            "Begin.Year":wave, "EndYear":wave, "Component":str(source.module),
            "Use.Constraints":"CHARLS applicant data; access and publication governed by official agreement",
            "epcf":"c", "category":"measurement metadata", "subcategory":"reviewed source metadata",
            "Source.Wave":wave, "Source.Archive":str(source.source),
            "Candidate.Status":"C metadata; official source field retained for documentation only",
            "Harmonization.Status":"source metadata only; excluded from E/P association matrix",
            "Review.Flag":"exclude from E/P association matrix; do not publish free-text content",
            "Value.Labels":"", "Value.Label.Source":"", "Value.Label.Review":"not applicable to unstructured text"
        }])],ignore_index=True).fillna("")
        metadata_rows=(fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code) & fields["epcf"].str.lower().eq("c"))
        has_c=True
    if not selected.any() and not has_c:
        continue
    if selected.any() and has_c and old_role != "c":
        metadata_removed += int(selected.sum())
        fields=fields.loc[~selected].copy()
    elif selected.any() and old_role != "c":
        fields.loc[selected,"epcf"]="c"
        fields.loc[selected,"category"]="measurement metadata"
        fields.loc[selected,"subcategory"]="prior-interview response-history routing flags"
        fields.loc[selected,"Candidate.Status"]="official questionnaire identifies previous-interview answer-history flag"
        fields.loc[selected,"Harmonization.Status"]="routing/availability metadata only; not a respondent behavior measure"
        fields.loc[selected,"Review.Flag"]="do not treat as exposure or outcome; use only to interpret reinterview skip patterns"
    if str(override.get("metadata_type", "")).strip().lower() == "measurement_completion":
        # A completion/consent field can be auto-classified as both E and P
        # because its source label contains an anthropometric term. Remove any
        # unmapped residual E/P rows after converting the reviewed source row.
        concept_col_now=fields["Concept.ID.Candidates"] if "Concept.ID.Candidates" in fields else pd.Series([""]*len(fields),index=fields.index)
        redundant=(fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code) &
                   fields["epcf"].str.lower().isin({"e","p","e,p"}) & concept_col_now.eq(""))
        metadata_removed += int(redundant.sum())
        fields=fields.loc[~redundant].copy()
    metadata_rows=(fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code) & fields["epcf"].str.lower().eq("c"))
    metadata_type = str(override.get("metadata_type", "")).strip().lower()
    if metadata_type == "community_informant_role":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="community-questionnaire informant role"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt; audit/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official field identifies the community-questionnaire informant role; response categories omitted because this is not participant metadata"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; respondent role for Community Questionnaire Part C; not a sampled-participant characteristic"
        fields.loc[metadata_rows,"Harmonization.Status"]="informant identity/role context only; not an exposure, phenotype, or adjustment covariate"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; never use a community-informant role as a CHARLS participant covariate"
    elif metadata_type == "community_leadership_undefined_slot":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="unresolved JA042 community leadership slot"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt; audit/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="Codebook field label located, but the questionnaire identifies only four named leadership rows; fifth age/tenure slot identity unresolved"
        fields.loc[metadata_rows,"Candidate.Status"]="C source metadata; fifth JA042 age/tenure slot has no verified questionnaire position mapping"
        fields.loc[metadata_rows,"Harmonization.Status"]="do not assign this field to a named leader, combine it with the four verified roles, or analyze it until the official source linkage is resolved"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; unresolved leadership-slot identity; do not infer a role from adjacent slots"
    elif metadata_type == "community_part_b_open_text_metadata":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="community Part B unstructured other-specify text"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt; audit/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official source identifies an other-specify text field; response text and unverified categories are not published"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; unstructured other-specify response, not a standardized participant exposure or phenotype"
        fields.loc[metadata_rows,"Harmonization.Status"]="retain only the existence and source role of the open-text field; do not publish or tokenize response contents"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; no respondent text in public payload"
    elif metadata_type == "community_part_b_informant_role":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="community Part B questionnaire informant role"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt; audit/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official field identifies the Part B community-questionnaire informant; response categories are not participant attributes and are not published"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; Part B informant identity/role, not a sampled-participant characteristic"
        fields.loc[metadata_rows,"Harmonization.Status"]="informant role context only; not exposure, phenotype, or adjustment covariate"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; never use informant role as a CHARLS participant covariate"
    elif metadata_type == "community_part_f_mortality_metadata":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="community mortality and unstandardized cause-of-death metadata"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt; audit/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official questionnaire identifies open-text disease-name slots and corresponding counts; response text and small-cell counts are not published"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; cause text is not standardized and linked death counts are not eligible E/P candidates pending code/denominator review"
        fields.loc[metadata_rows,"Harmonization.Status"]="do not publish response text or counts; preserve the disease-name/death-count slot pairing; no participant-level outcome or denominator is established"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; no response text or small-community mortality counts in public payload"
    elif metadata_type == "community_part_f_informant_role":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="Part F community questionnaire informant role; source conflict"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt; audit/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="questionnaire assigns JF020 to Part F; Codebook labels the field Part D; category values withheld pending source reconciliation"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; informant identity/role, not a CHARLS participant attribute"
        fields.loc[metadata_rows,"Harmonization.Status"]="retain the questionnaire/Codebook module conflict; never use informant role as a participant covariate"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; source conflict unresolved; no response values published"
    elif metadata_type == "activity_random_subsample_marker_unresolved":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="physical-activity randomized-module assignment marker"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(
            lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt"
        )
        fields.loc[metadata_rows,"Value.Label.Review"]="official questionnaire confirms a randomized half-household activity module; Codebook field label is Ca052Random, but released code-to-eligibility meaning is unresolved"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; physical-activity assignment marker retained for design documentation only; do not classify code values as selected/not selected"
        fields.loc[metadata_rows,"Harmonization.Status"]="wave-specific randomized activity-module metadata; questionnaire describes random half-household routing, but the released 1/2 marker mapping to selection/eligibility is unverified and must not be harmonized"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; do not infer respondent or household eligibility from this marker, its code values, or missingness; resolve against official release routing before any denominator/weight use"
    elif metadata_type == "age_year_component_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="age/calendar-year response-format selector"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; official Codebook selector identifies whether the paired smoking/alcohol time component is age or calendar year"
        fields.loc[metadata_rows,"Harmonization.Status"]="response-format selector only; selector code order differs by wave; interpret the paired age/year component using this wave-specific metadata"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; not a smoking/alcohol exposure; use only to interpret the paired age/year response field"
    elif metadata_type == "age_year_component_marker":
        parent=code[:-2]
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="fixed age/calendar-year component-type marker"
        fields.loc[metadata_rows,"Value.Labels"]="1=Age" if code.endswith("s1") else "2=Year"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official Codebook single marker value reviewed; frequencies omitted; not the respondent's reported smoking time"
        fields.loc[metadata_rows,"Candidate.Status"]=f"C metadata; fixed Age/Year component marker; actual response is stored in {parent}_1 or {parent}_2"
        fields.loc[metadata_rows,"Harmonization.Status"]=f"format marker only; the 2011 questionnaire directly labels {parent}_1 as Age and {parent}_2 as Year; do not analyze this fixed marker as an exposure"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; documentation marker only; no participant response value is needed to interpret the paired continuous component"
    elif metadata_type == "age_year_component_selector_source_conflict":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="smoking cessation age/calendar-year response-format selector; component labels conflict"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2018_Questionnaire_extracted.txt:L3089-L3090; sources_official/CHARLS_2018_Codebook_extracted.txt:L43128-L43151"
        fields.loc[metadata_rows,"Value.Label.Review"]="selector role confirmed; component order conflicts between official questionnaire and Codebook; selector category labels withheld"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; DA062 identifies age/year response format, but exact selector-to-component mapping is unresolved"
        fields.loc[metadata_rows,"Harmonization.Status"]="questionnaire labels DA062_1=Age and DA062_2=Year; Codebook labels DA062_1=Year and DA062_2=Age; retain selector only as source metadata until official release clarification"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; selector retained only as metadata while child component mapping conflict is documented"
    elif metadata_type == "none_checklist_option":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="checklist none-option coding"
        fields.loc[metadata_rows,"Value.Labels"]="4=None"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official questionnaire/Codebook option label reviewed; shared none response in multi-select checklist"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; shared None option for the household GD003 multi-select income-source checklist"
        fields.loc[metadata_rows,"Harmonization.Status"]="not a source-specific exposure; preserve as checklist metadata and do not infer No for each source from blanks"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; do not treat as a fourth transfer exposure or reuse as source-specific No"
    elif metadata_type == "beer_amount_unit_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="beer quantity unit selector"
        fields.loc[metadata_rows,"Value.Labels"]="1=Bottles; 2=Mugs"
        fields.loc[metadata_rows,"Value.Label.Source"]=f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official Codebook beer-quantity unit selector labels reviewed; frequencies omitted; not a behavior measure"
        fields.loc[metadata_rows,"Candidate.Status"]="C measurement metadata; DA075 selects the unit used by the subsequent beer-quantity field"
        fields.loc[metadata_rows,"Harmonization.Status"]="measurement unit selector only; interpret da075_1/da075_2 as the corresponding continuous beer quantity; do not include DA075 in an E/P association or infer a quantity from missing values"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret beer quantity units"
    elif metadata_type == "wage_deduction_protocol":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="personal wage deduction scope and response-unit selectors"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; interprets whether reported wages include deductions and the unit used for deduction responses"
        fields.loc[metadata_rows,"Harmonization.Status"]="scope/unit selector only; numeric deductions are stored in separate annual, monthly, percentage or component child fields"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use to interpret conditional wage amount fields and preserve wave-specific routing"
    elif metadata_type == "pension_early_exit_reduction_format_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="early-exit pension reduction amount/percentage selector"
        fields.loc[metadata_rows,"Value.Labels"]="1=Percentage; 2=Yuan amount"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official 2011 questionnaire and Codebook response-format labels; actual percentage and amount are separate child fields"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; FN048 selects percentage versus Yuan reduction in fn048_1/fn048_2 for the hypothetical FN047 early-exit age"
        fields.loc[metadata_rows,"Harmonization.Status"]="response-format selector only; preserve amount and percentage as separate units and retain the FN047 scenario age"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret fn048_1 percentage versus fn048_2 Yuan amount"
    elif metadata_type == "pension_work_unit_province_metadata":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="province-level pension-source work-unit location metadata"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="province-level work-unit location identity reviewed; no locations or frequencies included"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; province of the latest work unit involved in a pension route"
        fields.loc[metadata_rows,"Harmonization.Status"]="former-workplace location detail; not a standalone E/P measure; no province values or geocoding in the atlas"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; do not publish province values or use respondent-level location"
    elif metadata_type == "pension_expected_amount_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="expected formal-retirement benefit amount/percentage selector"
        fields.loc[metadata_rows,"Value.Labels"]="1=Yuan per month; 2=Percent of salary before retirement"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official questionnaire and Codebook response-format categories; paired amount/ratio values are separate fields"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; FM038 selects amount versus pre-retirement-salary percentage; child values are in fm038_1 and fm038_2"
        fields.loc[metadata_rows,"Harmonization.Status"]="response-format selector only; FM011=4 route; do not analyze as an expected benefit amount"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret FM038_1 amount versus FM038_2 salary-ratio response"
    elif metadata_type == "retirement_work_unit_geographic_detail":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="retirement/receding work-unit geographic linkage components"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="geographic name/code component; no observed values are included in the atlas"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; conditional work-unit address components for a geographic linkage workflow"
        fields.loc[metadata_rows,"Harmonization.Status"]="FM004=3/4 route; city/county/province components identify work-unit location and are not standalone exposures"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; do not publish respondent location values or geocode without approved privacy/disclosure review"
    elif metadata_type == "measurement_completion":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="knee-height measurement agreement and instruction comprehension"
        fields.loc[metadata_rows,"Value.Labels"]="1=Yes; 5=No"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official response categories; protocol agreement/comprehension metadata"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; PK001 asks whether the respondent understands and agrees to knee-height measurement; actual measurement is QK002"
        fields.loc[metadata_rows,"Harmonization.Status"]="measurement eligibility/participation only; not knee height, exposure, or phenotype"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret QK002 measurement availability and protocol routing"
    elif metadata_type == "housing_rental_income_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="housing rental amount applicability/response-format selector"
        fields.loc[metadata_rows,"Value.Labels"]="1=Yuan/month amount response; 2=Not applicable (not currently rented)"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt; sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official questionnaire and Codebook response formats; not a direct yes/no rental status"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; selects amount versus not-applicable response in housing-rental question"
        fields.loc[metadata_rows,"Harmonization.Status"]="response/applicability selector only; amount is stored in *_1 child field; do not treat as a binary exposure"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret amount response eligibility; never convert structural skips to zero"
    elif metadata_type == "individual_transfer_income_unit_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="individual transfer-income amount unit selector"
        fields.loc[metadata_rows,"Value.Labels"]="1=Yuan/year; 2=Yuan/month"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2013_Codebook_extracted.txt; sources_official/CHARLS_2013_Questionnaire_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official codebook response-unit categories reviewed; paired amount components are separate fields"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; selects whether the source-specific amount is reported annually or monthly"
        fields.loc[metadata_rows,"Harmonization.Status"]="response-unit selector only; do not analyze as income or combine with amount values"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret the corresponding 2013 GA004 amount unit"
    elif metadata_type == "housing_value_slot_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="current residence total-price versus unit-price selector by slot"
        fields.loc[metadata_rows,"Value.Labels"]="1=Total price (10,000 Yuan)" if code.endswith("_s1") else "2=Unit price (1,000 Yuan/m2)"
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="official questionnaire/codebook slot-specific value-format label reviewed"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; marks the response format selected for the corresponding current-residence slot"
        fields.loc[metadata_rows,"Harmonization.Status"]="format selector only; the total-price and unit-price values are separate incompatible measures"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret the paired HA034 amount fields and retain the residence slot"
    elif metadata_type == "housing_value_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="current home market-value response unit selector"
        fields.loc[metadata_rows,"Value.Labels"]="1=Total price (10,000 Yuan); 2=Unit price (1,000 Yuan/m2)"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt; sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official selector categories; linked numeric responses are separate total-price and unit-price fields"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; HA011 selects one of two incompatible response units for current-home market value"
        fields.loc[metadata_rows,"Harmonization.Status"]="response-unit selector only; preserve the selected route and do not combine total price with unit-area price"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret ha011_1 versus ha011_2 and verify conditional response routing"
    elif metadata_type == "housing_property_value_measure_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="household property total-price versus unit-price response-format selector"
        fields.loc[metadata_rows,"Value.Labels"]="1=Total Value; 2=Unit Value"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official 2018 questionnaire and Codebook response-format categories reviewed; frequencies omitted"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; HA004 selects total-price or unit-price reporting for the indexed household property"
        fields.loc[metadata_rows,"Harmonization.Status"]="response-format selector only; total-price amounts use 10,000 Yuan and unit-price amounts use 1,000 Yuan/square metre; preserve matching property slot"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret corresponding HA004 total/unit amount fields"
        for column in ("Concept.Unit.Candidates", "Unit", "Concept.ID.Candidates", "Concept.Alias.IDs", "Concept.Label.Candidates", "Concept.Mapping.Source", "Concept.Mapping.Status", "Concept.Mapping.Caveat", "Concept.Mapping.Collision", "Concept.Mapping.Relationship", "candidate_concept_ids", "candidate_concept_alias_ids", "candidate_concept_labels", "concept_mapping_sources", "concept_mapping_statuses", "concept_mapping_caveats", "concept_mapping_collision", "concept_mapping_relationship", "candidate_concept_units"):
            if column in fields:
                fields.loc[metadata_rows,column]=""
    elif metadata_type in {"education_record_validation", "hukou_record_validation", "hukou_location_presence_selector"}:
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="prior-wave demographic record verification and response routing"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; verifies or routes a previous-wave demographic record and is not an independent exposure"
        fields.loc[metadata_rows,"Harmonization.Status"]="record-validation/response-route metadata; retain only to interpret the associated prior-wave education or hukou answer"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; do not treat a confirmation, record-quality flag, or address-presence selector as exposure"
    elif metadata_type == "financial_respondent_source":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="household financial respondent source"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; identifies the household member selected to report household financial information"
        fields.loc[metadata_rows,"Harmonization.Status"]="respondent-source/administration metadata; preserve when interpreting household-level income and assets, but do not treat as an exposure"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to describe or prespecify sensitivity analyses by household financial respondent"
    elif metadata_type == "anchoring_vignette":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="subjective living-standard anchoring vignette"
        fields.loc[metadata_rows,"Value.Labels"]="1=Very high; 2=Relatively high; 3=Average; 4=Relatively poor; 5=Poor"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official response categories; hypothetical vignette metadata"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; rating of a hypothetical household, not the respondent's own socioeconomic position"
        fields.loc[metadata_rows,"Harmonization.Status"]="response-scale anchoring only; not a respondent exposure or phenotype"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; may inform a prespecified subjective-scale calibration analysis"
    elif metadata_type == "blood_pressure_test_condition":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="blood pressure recent pretest conditions"
        fields.loc[metadata_rows,"Value.Labels"]="1=Yes; 5=No; 8=Don't know"
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="official codebook labels; measurement-context metadata"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; 2013/2015 official biomarker questionnaire identifies behavior within 30 minutes before BP test; 2011 codebook label only"
        fields.loc[metadata_rows,"Harmonization.Status"]="measurement-context flag; not habitual smoking, physical activity, alcohol, or diet exposure; 2011 instrument-level wording remains to verify"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to describe or sensitivity-check blood pressure measurement context; do not generalize to blood biomarkers"
        manual_2011 = metadata_rows & fields["Source.Wave"].eq("2011")
        fields.loc[manual_2011,"Value.Label.Source"]="sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official.doc; sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[manual_2011,"Value.Label.Review"]="official 2011 physical-examination manual and Codebook reviewed; measurement-context metadata only"
        fields.loc[manual_2011,"Candidate.Status"]="C metadata; 2011 manual item LI875 confirms the QA017 Codebook field asks about behavior within 30 minutes before blood-pressure testing"
        fields.loc[manual_2011,"Harmonization.Status"]="The 2011 physical-examination manual labels the item LI875, while the released-field Codebook label is QA017; wording confirms a combined behavior indicator within 30 minutes before the blood-pressure test. It is not habitual behavior or blood-draw fasting status."
    elif metadata_type == "questionnaire_template_label":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="questionnaire inserted activity-type labels"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]=""
        fields.loc[metadata_rows,"Value.Label.Review"]="not applicable: string template metadata, not an answer field"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; official codebook identifies constant string labels inserted into the DA032-DA035 activity questions"
        fields.loc[metadata_rows,"Harmonization.Status"]="instrument text/template metadata; not respondent-reported activity, intensity, duration, or frequency"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret the 2020 questionnaire wording"
    elif metadata_type == "pension_life_insurance_other_type_text":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="life-insurance other-type open text"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="conditional open-text specify field; no standardized categories"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; open-ended description of other life-insurance type"
        fields.loc[metadata_rows,"Harmonization.Status"]="unstructured conditional text; no standardized category or validated harmonization"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; do not expose respondent text in the public atlas"
    elif metadata_type == "pension_expected_timing_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="expected pension receipt age-versus-years response selector"
        labels="1=Age; 2=Years after interview" if wave == "2018" else "1=At age; 2=In years"
        fields.loc[metadata_rows,"Value.Labels"]=labels
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="official questionnaire/codebook response-format labels; not benefit values"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; parent field selects the response format; numeric age and wait years are stored in distinct child fields"
        fields.loc[metadata_rows,"Harmonization.Status"]="response-format metadata only; age and years-from-interview are distinct units and separate candidate concepts"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret the paired expected receipt timing components"
    elif metadata_type == "cognitive_stimulus_metadata":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="cognitive word-list form and stimulus metadata"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]=""
        fields.loc[metadata_rows,"Value.Label.Review"]="not a respondent answer scale; stimulus/form metadata"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; word-list version, assigned stimulus words, completion status, or refusal reason"
        fields.loc[metadata_rows,"Harmonization.Status"]="test-form/stimulus/administration metadata only; not a cognitive score or respondent phenotype"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret test form, stimuli, or task administration"
    elif metadata_type == "subjective_expectation_age_target_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="subjective life-expectancy target-age metadata"
        fields.loc[metadata_rows,"Value.Labels"]="75; 80; 85; 90; 95; 100; 105; 110; 115"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Codebook_extracted.txt:L65182-L65212; sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt:L4068-L4084"
        fields.loc[metadata_rows,"Value.Label.Review"]="official 2011 Codebook age-category labels transcribed without frequencies; DA081 prompt leaves its age threshold as a placeholder, so direct field linkage remains unverified"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; official Codebook labels flda081_1 as the target age for self-expectation; likely context for DA081, but exact released-field linkage is not documented"
        fields.loc[metadata_rows,"Harmonization.Status"]="target-age context metadata only; do not treat age categories as the respondent's subjective probability or as a phenotype; DA081 linkage remains unverified"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; not an outcome or adjustment variable; preserve only as candidate DA081 target-age context and do not derive probabilities or scores"
    elif metadata_type == "lifecourse_timing_unit_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="life-course timing unit selectors"
        fields.loc[metadata_rows,"Value.Labels"]="1=Age; 2=Calendar year"
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="official questionnaire and codebook response format reviewed"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; selects age versus calendar-year response in paired first-work timing fields"
        fields.loc[metadata_rows,"Harmonization.Status"]="unit selector only; do not analyze as age or calendar year; keep distinct child fields"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; preserve paired child field and unit selection"
    elif metadata_type == "health_anchoring_vignette_metadata":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="hypothetical health anchoring vignettes"
        fields.loc[metadata_rows,"Value.Labels"]="1=None; 2=Mild; 3=Moderate; 4=Severe; 5=Extreme"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official five-level severity response categories; hypothetical-person rating"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; respondent rates a hypothetical person's pain, mobility, or cognition, not their own health"
        fields.loc[metadata_rows,"Harmonization.Status"]="anchoring-vignette response scale only; not a respondent phenotype or exposure"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; retain only as subjective-health scale anchoring metadata"
    elif metadata_type == "interview_assistance_protocol":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="interview assistance / proxy response context"
        fields.loc[metadata_rows,"Value.Labels"]="1=Never; 2=A few times; 3=Most or all of the time"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official assistance-frequency response options; questionnaire/Codebook section-name discrepancy retained"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; financial-section interview assistance frequency, not a respondent exposure or phenotype"
        fields.loc[metadata_rows,"Harmonization.Status"]="interview-process context only; preserve exact wave/module wording and do not treat as a financial measure"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; may describe response assistance only after permitted microdata review"
    elif metadata_type == "nonnumeric_amount_identity_conflict":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="unresolved release-field identity/data-type discrepancy"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2015_Codebook_extracted.txt; sources_official/CHARLS_2015_Questionnaire_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="Codebook identifies a string field; related numeric amount/cash/in-kind child fields exist; exact released-field role unresolved"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; do not interpret the string field as a numeric compensation amount without official release-field clarification"
        fields.loc[metadata_rows,"Harmonization.Status"]="unresolved field/data-type identity; numeric amount fields remain separate and must be reviewed independently"
        fields.loc[metadata_rows,"Review.Flag"]="DO NOT ANALYZE; do not parse or publish string contents as an amount until exact official field identity is confirmed"
    elif metadata_type == "financial_respondent_metadata":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="household income/expenditure respondent source"
        fields.loc[metadata_rows,"Value.Labels"]="1=Primary food purchaser (not financial respondent); 2=Financial respondent; 3=Other"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official interview-process categories; not household income or expenditure"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; identifies who answered household income/expenditure questions"
        fields.loc[metadata_rows,"Harmonization.Status"]="response-source context only; household-level economic values must retain their respondent and household linkage"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use to describe respondent source or prespecified response-source sensitivity checks"
    elif metadata_type == "proxy_interview_metadata":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="2011 proxy interview and Section E assistance context"
        labels={
            "fn081":"1=Never; 2=A few times; 3=Most or all the time; 4=Section completed by proxy",
            "fn082":"1=Spouse; 2=Mother; 3=Father; 4=Mother-in-law; 6=Sibling; 7=Brother/sister-in-law; 8=Child; 9=Child's spouse; 10=Grandchild; 11=Other relative; 12=Helper/non-relative",
            "fn083":"1=Serious physical handicap; 2=Serious mental handicap; 3=Respondent rejected interview; 4=Other",
        }
        code=str(override["code"]).lower()
        fields.loc[metadata_rows,"Value.Labels"]=labels[code]
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official interview-process categories; not respondent exposure or health phenotype"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; records proxy assistance, proxy relationship, or reason for proxy interview"
        fields.loc[metadata_rows,"Harmonization.Status"]="interview mode/measurement context only; retain for response-quality description or prespecified sensitivity analysis"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; may inform proxy-response sensitivity checks when justified"
    elif metadata_type == "pension_amount_unit_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"subcategory"]="pension amount format selector"
        code=str(override["code"]).lower()
        if code == "fn079_w2_9":
            labels="1=Yuan per month; 2=Yuan lump-sum amount"
            subcategory="land-requisition pension expected-benefit amount-format selector"
            candidate="C metadata; parent selects monthly versus lump-sum expected benefit stored in fn079_w2_9_1/_2"
            semantics="response-format selector only; not an expected benefit amount or receipt status"
            review_flag="exclude from E/P association matrix; retain only to interpret expected benefit child units"
        elif code == "fn094_w2":
            labels="1=Yuan per month; 2=Yuan lump-sum amount"
            subcategory="expected pension benefit amount-unit selector"
            candidate="C metadata; parent field selects monthly versus lump-sum response; observed amount is stored in fn094_w2_1 or fn094_w2_2"
            semantics="measurement-unit/response-format selector only; do not treat as expected pension amount or combine the amount components"
            review_flag="exclude from E/P association matrix; retain only to interpret the paired amount component and its unit"
        elif code == "fn056_w2_6":
            labels="1=Monthly; 2=Quarterly; 3=Semi-annually; 4=Annually"
            subcategory="life-insurance contribution payment-period selector"
            candidate="C metadata; selects the premium payment interval; actual premiums are stored in separate period-specific child fields"
            semantics=("payment-period metadata only; do not treat as a contribution amount; Codebook reports no quarterly child observations in 2013"
                       if wave == "2013" else "payment-period metadata only; do not treat as a contribution amount; preserve separate monthly, quarterly, semi-annual and annual child units")
            review_flag="exclude from E/P association matrix; use only to interpret the matching period-specific premium child amount"
        elif code == "fn056_w2_9":
            labels="1=Yuan per month; 2=Yuan lump-sum amount"
            subcategory="life-insurance expected-benefit amount-format selector"
            candidate="C metadata; selects monthly versus lump-sum expected benefit stored in fn056_w2_9_1/_2"
            semantics="response-format selector only; preserve monthly and lump-sum amounts as separate measures"
            review_flag="exclude from E/P association matrix; use only to interpret the paired expected-benefit amount fields"
        elif code == "fn011":
            labels="1=Annual contribution/subsidy; 2=Lump-sum contribution/subsidy"
            subcategory="rural pension contribution frequency selector"
            candidate="C metadata; parent field selects annual or lump-sum response components fn011_1–fn011_6"
            semantics="response-period selector only; the contribution/subsidy values are stored in separate amount fields"
            review_flag="exclude from E/P association matrix; retain only to interpret the selected annual or lump-sum contribution/subsidy components"
        elif code == "fn036":
            labels="1=Yuan per month; 2=Percent of final pay"
            subcategory="expected retirement pension benefit format selector"
            candidate="C metadata; codebook labels fn036 as an amount/percentage response-format selector, but questionnaire uses FN036_w2 and the linkage to unqualified fn036 child fields is unresolved"
            semantics="codebook response-format metadata only; do not infer linkage to questionnaire FN036_w2 or analyze unqualified child fields until release-specific variable identity is confirmed"
            review_flag="exclude from E/P association matrix; retain as unlinked codebook metadata pending confirmation of the 2011 released variable-to-question mapping"
        elif code == "fn036_w2":
            labels="1=Yuan per month; 2=Percentage per month; 3=Yuan lump-sum amount"
            subcategory="firm supplementary pension expected-benefit form selector"
            candidate="C metadata; parent field selects monthly Yuan, percentage/month, or lump-sum amount stored in fn036_w2_1/_2/_3"
            semantics="response-form selector only; amount values are stored in child fields with different units; percentage denominator is unspecified"
            review_flag="exclude from E/P association matrix; use only to interpret the selected expected-benefit child field and its response form"
        elif code in {"fn066_w2_1_", "fn066_w2_2_", "fn066_w2_3_"}:
            labels="1=Yuan per month; 2=Yuan lump-sum amount where listed for this plan/wave"
            subcategory="social-pension expected-benefit form selector"
            candidate="C metadata; scheme-specific parent selects monthly versus lump-sum response in separate child amount fields"
            semantics="plan-specific response-format selector only; not an expected benefit amount; retain the selected plan and child form"
            review_flag="exclude from E/P association matrix; use only to interpret the selected social-pension benefit child field"
        elif code in {"fn075_w3_1_1_", "fn075_w3_1_2_", "fn075_w3_1_3_", "fn075_w3_2_1_", "fn075_w3_2_2_", "fn075_w3_2_3_"}:
            labels="1=Yuan; 2=10,000 Yuan"
            subcategory="social-pension supplementary repayment currency selector"
            candidate="C metadata; parent selects Yuan versus 10,000-Yuan unit for the plan-specific total or personal repayment amount"
            semantics="currency-scale selector only; normalize 10,000-Yuan values to Yuan for combined calculations; never sum total and personal repayment fields"
            review_flag="exclude from E/P association matrix; retain only to interpret repayment amount scale and child field"
        elif (code in {f"fn072_w3_1_{i}_" for i in (1, 2, 3)}
              or code in {f"fn072_w3_2_{i}_" for i in (1, 2, 3)}):
            labels="1=Yuan; 2=10,000 Yuan"
            subcategory="social-pension supplementary repayment currency selector"
            candidate="C metadata; parent selects Yuan versus 10,000-Yuan scale for plan-specific total or personal supplementary amount"
            semantics="currency-scale selector only; normalize 10,000-Yuan amounts to Yuan; never sum total and personal repayment fields"
            review_flag="exclude from E/P association matrix; retain only to interpret repayment amount scale and child field"
        elif code in {"fn035_w4_b", "fn035_w4_c"}:
            labels="1=Yuan per month; 2=Percent of wage"
            payer="employer" if code.endswith("_b") else "respondent"
            children="fn035_w4_b_1/_2" if code.endswith("_b") else "fn035_w4_c_1/_2"
            subcategory=f"2018 {payer} pension contribution amount/share unit selector"
            candidate=f"C metadata; selects monthly Yuan or percent-of-wage response for {payer} contribution stored in {children}"
            semantics="amount/share format selector only; preserve Yuan/month and percentage as separate measures"
            review_flag="exclude from E/P association matrix; retain only to interpret the unit-specific contribution child fields"
        elif code in {"fn062_w4_a", "fn062_w4_b"}:
            labels="1=Yuan/month; 2=Yuan/year"
            subcategory="resident-pension contribution amount period selector"
            candidate="C metadata; selects monthly or annual unit for the corresponding government subsidy or individual contribution amount"
            semantics="measurement format selector only; monthly and annual child values remain separate measures"
            review_flag="exclude from E/P association matrix; use only to interpret the selected amount period"
        elif code in {"fn063_w4_2", "fn063_w4_3"}:
            labels="calendar year" if code.endswith("_2") else "calendar month; 0=month not remembered"
            subcategory="resident-pension balance last-check date component"
            candidate="C metadata; date component records when the respondent last checked the selected plan's balance"
            semantics="measurement-context date component for fn063_w4_1; not a standalone exposure or account balance"
            review_flag="exclude from E/P association matrix; retain as context for interpreting the account balance measurement"
        elif code in {"fn037_w2_2", "fn037_w2_3"} and wave in {"2013", "2015", "2018"}:
            labels="calendar year" if code.endswith("_2") else "calendar month; 0=month not remembered"
            subcategory="defined-contribution pension account balance last-check date component"
            candidate="C metadata; date records when respondent last checked the selected defined-contribution pension account balance"
            semantics="measurement-context date component; not a standalone exposure or account balance; only defined when the account balance check route is Yes"
            review_flag="exclude from E/P association matrix; retain only as the measurement date for the selected defined-contribution account balance"
        elif wave == "2018" and code == "fn072_w3_1":
            labels="1=Yuan; 2=10,000 Yuan"
            subcategory="resident-pension supplementary repayment currency selector"
            candidate="C metadata; selects Yuan versus 10,000-Yuan scale for the selected plan's make-up payment"
            semantics="currency-scale selector only; numeric amounts are held in fn072_w3_1_1/_1_2"
            review_flag="exclude from E/P association matrix; normalize unit-specific child amount only after interpreting this selector"
        elif wave == "2018" and code in {"fn072_w3_1_min", "fn072_w3_1_max"}:
            labels="unfolding bracket lower/upper bound in Yuan"
            subcategory="resident-pension supplementary repayment bracket bound"
            candidate="C metadata; interval-bracket bound for an unknown/refused/zero make-up amount"
            semantics="bracket bound only; not the respondent's point amount and not an independent exposure"
            review_flag="exclude from E/P association matrix; retain only for interval-censored response reconstruction"
        elif code in {"fn062", "fn068"} or (wave in {"2013", "2015"} and code in {"fn065_w2_1_", "fn065_w2_2_", "fn065_w2_3_"}):
            labels="1=At age; 2=In years"
            subcategory="expected pension receipt time format selector"
            candidate="C metadata; parent field selects age or years-until-receipt response stored in scheme-specific numeric child fields"
            semantics="response-time format selector only; age and waiting-year components are separate measures"
            review_flag="exclude from E/P association matrix; use to interpret whether the scheme-specific response is age or waiting years"
        elif wave == "2018" and code == "fn051_w4":
            labels="1=Age; 2=Years"
            subcategory="commercial-pension expected claim timing format selector"
            candidate="C metadata; 2018 questionnaire identifies fn051_w4 as the age-versus-years selector; numerical timing is stored in fn051_w4_1/_2"
            semantics="response-time format selector only; not a binary expected-receipt status; age and years-from-interview are distinct measures"
            review_flag="exclude from E/P association matrix; use only to interpret the paired expected-claim timing components"
        elif wave == "2018" and code == "fn076_w4_a":
            labels="1=Age; 2=Years"
            subcategory="life-insurance expected claim timing format selector"
            candidate="C metadata; 2018 questionnaire identifies fn076_w4_a as the age-versus-years selector; numerical timing is stored in fn076_w4_a_1/_2"
            semantics="response-time format selector only; asked after fn076_w4=Yes; age and years-from-interview are distinct measures"
            review_flag="exclude from E/P association matrix; use only to interpret the routed life-insurance expected-claim timing components"
        elif wave == "2018" and code == "fn093_w2":
            labels="1=Age; 2=Years"
            subcategory="other-pension expected claim timing format selector"
            candidate="C metadata; 2018 questionnaire identifies fn093_w2 as the age-versus-years selector; numerical timing is stored in fn093_w2_1/_2"
            semantics="response-time format selector only; asked after FN087_W2=No; age and years-from-interview are distinct measures"
            review_flag="exclude from E/P association matrix; use only to interpret the routed other-pension expected-claim timing components"
        elif ((wave in {"2013", "2015"} and code == "fn021_w2")
              or (wave == "2018" and code in {"fn021_w2_1_", "fn021_w2_2_", "fn021_w2_3_", "fn021_w2_4_"})):
            labels="1=Yuan; 2=Percent" if wave in {"2013", "2015"} else "1=Yuan/Month; 2=Percentage of Final Pay"
            subcategory="expected pension benefit unit/form selector"
            candidate="C metadata; parent selects the response form; benefit values are stored in separately unit-coded numeric child fields"
            semantics="response-unit selector only; do not treat as a benefit value or combine monthly currency and wage percentage"
            review_flag="exclude from E/P association matrix; use only to interpret the selected amount-versus-percentage child response"
        elif code in {"fn063", "fn069"}:
            labels="1=Yuan per month; 2=Yuan lump-sum amount"
            subcategory="expected pension benefit amount format selector"
            candidate="C metadata; parent field selects monthly versus lump-sum benefit response stored in the paired _1/_2 fields"
            semantics="response-unit/benefit-form selector only; do not treat as an amount or combine monthly and lump-sum components"
            review_flag="exclude from E/P association matrix; use only to interpret paired amount components and their units"
        else:
            raise SystemExit(f"unsupported pension selector metadata code: {code}")
        fields.loc[metadata_rows,"subcategory"]=subcategory
        fields.loc[metadata_rows,"Value.Labels"]=labels
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Codebook_extracted.txt")
        if code in {"fn056_w2_6", "fn056_w2_9"}:
            fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt")
            fields.loc[metadata_rows,"Value.Label.Review"]="official questionnaire and Codebook response-format options; frequencies omitted"
        else:
            fields.loc[metadata_rows,"Value.Label.Review"]="official codebook response-format labels; not benefit values"
        fields.loc[metadata_rows,"Candidate.Status"]=candidate
        fields.loc[metadata_rows,"Harmonization.Status"]=semantics
        fields.loc[metadata_rows,"Review.Flag"]=review_flag
    elif metadata_type == "measurement_completion":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="knee-height measurement consent/completion gate"
        fields.loc[metadata_rows,"Value.Labels"]="1=Yes; 5=No"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official measurement-protocol categories; field is consent/instruction understanding, not the measurement value"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; records whether respondent understood/agreed to knee-height measurement"
        fields.loc[metadata_rows,"Harmonization.Status"]="measurement eligibility/protocol context only; actual knee-height readout is a separate field"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret measurement participation and structural missingness"
    elif metadata_type == "pension_benefit_timing_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="expected supplementary pension benefit timing response selector"
        fields.loc[metadata_rows,"Value.Labels"]="1=At age or in years; 4=Other"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2011_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official 2011 codebook response-format labels; numeric timing components stored separately"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; parent item identifies the expected-benefit timing response form; values are stored separately in fn042_1/fn042_2"
        fields.loc[metadata_rows,"Harmonization.Status"]="response-type metadata only; preserve age and years-from-interview components as different units"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret the paired expected-timing components"
    elif metadata_type == "personal_wage_deduction_unit_selector":
        fields.loc[metadata_rows,"subcategory"]="personal wage-deduction response unit and applicability selector"
        fields.loc[metadata_rows,"Value.Labels"]="1=Yuan/Month; 2=Yuan/Year; 3=Percentage of Wage; 4=No"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official response-format categories; frequency table not used"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; selects monthly amount, annual amount, wage percentage, or no deduction response in GA004 child fields"
        fields.loc[metadata_rows,"Harmonization.Status"]="response-format/applicability selector only; do not enter the association matrix or combine amount units"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret the selected 2020 deduction response field"
    elif metadata_type == "capi_work_formula_unresolved":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="2020 CAPI-derived work-day formula under review"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2020_Questionnaire_English_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official derived-variable formula reviewed; duplicate/repeated condition remains unresolved"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; questionnaire formula contains a repeated branch, so the derived quantity is not ready for analysis"
        fields.loc[metadata_rows,"Harmonization.Status"]="derived work-day measure only; formula identity and interpretation unresolved; retain its source question and formula audit separately"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; DO NOT ANALYZE until the official formula ambiguity is resolved"
    elif metadata_type == "employment_date_confirmation":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="2020 current-employer start-date verification flag"
        fields.loc[metadata_rows,"Value.Labels"]="1=Preloaded year/month correct; 2=Incorrect, corrected start date entered; 999=Refuse"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official questionnaire/codebook verification-response labels; conditional corrected date is stored separately"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; validates or corrects the preloaded employer start date"
        fields.loc[metadata_rows,"Harmonization.Status"]="verification/routing status only; use FC018_1/_2 only when the correction route is selected, and retain FC019_1/_2 as the separately reported start date"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret the conditional corrected start-date fields and resolve date-source precedence"
    elif metadata_type == "demographic_preload_confirmation":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="prior-wave demographic preload and correction route"
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="preloaded prior-wave value or confirmation/response history; not a current-wave response"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; prior-wave demographic preload used to confirm or correct the recorded hukou/education value"
        fields.loc[metadata_rows,"Harmonization.Status"]="historical preload/confirmation route only; substantive corrected or current response is stored in its separate item"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only to interpret prior-wave preload and correction routing"
    elif metadata_type == "birth_date_covariate_source":
        fields.loc[metadata_rows,"category"]="covariate candidate"
        fields.loc[metadata_rows,"subcategory"]="birth-date source and age derivation metadata"
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="date-of-birth/civil-document reference for age covariate; do not expose respondent-level dates"
        fields.loc[metadata_rows,"Candidate.Status"]="C covariate source; official questionnaire uses civil-document date of birth and/or actual-date comparison to derive age"
        fields.loc[metadata_rows,"Harmonization.Status"]="covariate/age derivation source only; retain official date validity and wave-specific correction rules; publish no date values"
        fields.loc[metadata_rows,"Review.Flag"]="exclude as E/P; use only for age covariate derivation under approved data access and disclosure controls"
    elif metadata_type == "survey_home_linkage_derived":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="CAPI-derived survey-home linkage flag"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2020_Questionnaire_English_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="official CAPI-derived indicator; underlying address and household responses are not atlas values"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; CAPI flag derived from current residence address and residence type"
        fields.loc[metadata_rows,"Harmonization.Status"]="survey-home/interview-location linkage only; do not interpret as a neighborhood exposure or publish underlying address"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; retain only as address-routing/linkage metadata subject to disclosure controls"
    elif metadata_type == "questionnaire_codebook_conflict":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="unresolved questionnaire and Codebook field identity conflict"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; official questionnaire identifies slot 18 as None while Codebook reports one numeric value for the corresponding generic durable-value field"
        fields.loc[metadata_rows,"Harmonization.Status"]="unresolved field identity conflict; not harmonizable as an asset value"
        fields.loc[metadata_rows,"Review.Flag"]="DO NOT ANALYZE; retain only to document the questionnaire/Codebook discrepancy pending official release clarification"
    elif metadata_type == "legacy_no_observations":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="inactive legacy questionnaire slots with no observations"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="official Codebook explicitly reports No Observations"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; inactive source slot has no observations in the public release Codebook"
        fields.loc[metadata_rows,"Harmonization.Status"]="inactive legacy slot only; do not infer values, treat as zero, or analyze"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; official Codebook reports No Observations"
    elif metadata_type == "phantom_disability_slot_no_yes_category":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="invalid extra disability slot with no Yes category"
        fields.loc[metadata_rows,"Value.Labels"]="2=No (Codebook lists 13 observations; no Yes category)"
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2013_Codebook_extracted.txt; sources_official/CHARLS_2013_Questionnaire_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="questionnaire DA005 defines five disability types; extra sixth slot has no Yes category"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; invalid extra source slot, not a sixth disability phenotype"
        fields.loc[metadata_rows,"Harmonization.Status"]="retain only to document a phantom sixth slot; do not treat No-only records as a disability phenotype or infer a sixth category"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; official questionnaire lists five disability types and Codebook has no Yes category for this field"
    elif metadata_type == "chronic_disease_auxiliary_metadata":
        metadata_idx=fields.index[metadata_rows]
        codes=fields.loc[metadata_idx,"Variable.Name"].str.lower()
        prior_time=codes.str.startswith("zda009")
        prior_awareness=codes.str.startswith("zda008")
        undefined_index=~(prior_time | prior_awareness)
        fields.loc[metadata_rows,"category"]="measurement metadata"
        ptidx=metadata_idx[prior_time.to_numpy()]
        paidx=metadata_idx[prior_awareness.to_numpy()]
        uidx=metadata_idx[undefined_index.to_numpy()]
        fields.loc[ptidx,"subcategory"]="prior-wave diagnosis-time answer-history flags"
        fields.loc[ptidx,"Candidate.Status"]="C metadata; records only whether the prior interview answered the condition diagnosis/knowledge-time item"
        fields.loc[ptidx,"Harmonization.Status"]="prior-wave response-history/routing flag, not disease status or diagnosis time; exclude from E/P matrix"
        fields.loc[ptidx,"Review.Flag"]="exclude from E/P association matrix; interpret only as prior-interview answer history"
        fields.loc[paidx,"subcategory"]="unsupported prior-wave disease-awareness slots"
        fields.loc[paidx,"Candidate.Status"]="C metadata; prior-wave awareness slot outside the three questionnaire-defined disease items or lacking a valid positive category"
        fields.loc[paidx,"Harmonization.Status"]="do not infer No from an empty slot; retain only to document unasked/no-observation source placeholders"
        fields.loc[paidx,"Review.Flag"]="exclude from E/P association matrix; only 2013 questionnaire-defined ZDA008 items 1, 5, and 11 have supported self-awareness mappings"
        fields.loc[uidx,"subcategory"]="unlisted chronic-disease index placeholder"
        fields.loc[uidx,"Candidate.Status"]="C metadata; source index 15 is not among the 14 conditions defined in official DA007"
        fields.loc[uidx,"Harmonization.Status"]="unlisted disease-slot/response-format placeholder; no standardized disease construct can be inferred"
        fields.loc[uidx,"Review.Flag"]="exclude from E/P association matrix; official DA007 lists 14 conditions and does not define an index-15 phenotype"
    elif metadata_type == "child_roster_link_selector":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="linked child-roster selection identifiers"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="roster-linked child selection identifiers; do not expose child identities or response values"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; selects linked child roster records after old-age support from children is reported"
        fields.loc[metadata_rows,"Harmonization.Status"]="roster-link identifiers are not standardized child-level exposure values; any aggregate number of selected children requires separate derivation and validation"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; do not publish linked child identities or respondent-level selections"
    elif metadata_type == "unstructured_other_specify_text":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="unstructured other-specify response text"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="open-text clarification; no standardized response category"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; open-ended other-specify text attached to a coded hukou transition reason"
        fields.loc[metadata_rows,"Harmonization.Status"]="unstructured, conditional explanatory text; no standardized category or validated harmonization"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; do not expose respondent text in the public atlas"
    elif metadata_type == "sale_proceeds_selector_metadata":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="property-sale proceeds use-category selector slot"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="questionnaire use-category menu reviewed; option-indexed slot coding and link to percentage amount fields require authorized-release QA"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; option-indexed selector for the use category of property-sale proceeds, not the percentage amount"
        fields.loc[metadata_rows,"Harmonization.Status"]="selector and numeric percentage are separate source fields; preserve property slot and validate category mapping, routing, and denominator before analysis"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; do not infer selected categories from blank slots or publish participant values"
    elif metadata_type == "sale_proceeds_other_use_text":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="unstructured other-use response text"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="open-text specification for other use; no standardized category"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; open-ended other-use description attached to property-sale proceeds allocation"
        fields.loc[metadata_rows,"Harmonization.Status"]="unstructured conditional text; no standardized exposure measure; do not include text in public metadata"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; never publish respondent-level free text"
    elif metadata_type == "pension_children_roster_selection_metadata":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="pension child-roster payer selection slots"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="roster-linked child selection slot; no child identity or respondent values included"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; selection slot for child roster records in the pension payment-support question"
        fields.loc[metadata_rows,"Harmonization.Status"]="linked household child roster choice, not an independent standardized respondent exposure; any aggregate indicator requires a separate validated derivation"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; do not publish linked child identities or respondent-level selections"
    elif metadata_type in {"pension_2018_amount_selector_metadata", "pension_2018_bracket_metadata"}:
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="pension amount response-format selector or unfolding-bracket bound"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]="sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"
        fields.loc[metadata_rows,"Value.Label.Review"]="questionnaire confirms a payment-period selector or amount-bracket component; exact values are not exposed as an amount"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; selector/bracket component is not a standalone exposure or exact monetary value"
        fields.loc[metadata_rows,"Harmonization.Status"]="retain response format or interval-bound identity for documentation; do not coerce selectors/bounds to monetary values or use as independent association measures"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; preserve exact parent question and routed payment unit"
    elif metadata_type == "sensitive_address_detail":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="detailed respondent residential address fields"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire" + ("_English" if w == "2020" else "") + "_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="address field or address-source routing; no respondent address or location value included"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; respondent/roster-member detailed residential address source"
        fields.loc[metadata_rows,"Harmonization.Status"]="sensitive location/address detail; do not use as a public E/P variable; any approved geographic derivation must be separately aggregated and disclosure-reviewed"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; do not publish or geocode respondent-level address details"
    elif metadata_type == "sensitive_geographic_detail":
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="detailed hukou/residential geography components"
        fields.loc[metadata_rows,"Value.Labels"]=""
        fields.loc[metadata_rows,"Value.Label.Source"]=fields.loc[metadata_rows,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[metadata_rows,"Value.Label.Review"]="geographic detail/code field; public atlas includes no respondent location values"
        fields.loc[metadata_rows,"Candidate.Status"]="C metadata; conditional geographic detail child field for a hukou/residence question"
        fields.loc[metadata_rows,"Harmonization.Status"]="location-detail child field, not a standalone categorical exposure; do not publish addresses or geographic values"
        fields.loc[metadata_rows,"Review.Flag"]="exclude from E/P association matrix; use only under approved access and separately reviewed geographic aggregation"
    else:
        fields.loc[metadata_rows,"category"]="measurement metadata"
        fields.loc[metadata_rows,"subcategory"]="prior-interview response-history routing flags"
        fields.loc[metadata_rows,"Candidate.Status"]="official questionnaire identifies previous-interview answer-history flag"
        fields.loc[metadata_rows,"Harmonization.Status"]="routing/availability metadata only; not a respondent behavior measure"
        fields.loc[metadata_rows,"Review.Flag"]="do not treat as exposure or outcome; use only to interpret reinterview skip patterns"

# Retain potentially substantive E fields in search while clearly blocking
# analysis where questionnaire and Codebook field identities are unresolved.
for wave,code in analysis_locked_keys:
    selected=(fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code) & fields["epcf"].str.lower().eq("e"))
    override=overrides.loc[overrides["wave"].str.lower().eq(wave) & overrides["code"].str.lower().eq(code)].iloc[0]
    metadata_type=str(override.get("metadata_type","")).strip().lower()
    if metadata_type == "smoking_cessation_component_source_conflict":
        # These substantive components may be heuristically duplicated as C
        # covariates because their source labels are Age or Year. Keep only
        # the E-candidate row, which is explicitly locked below.
        duplicate_c=(fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code) & fields["epcf"].str.lower().eq("c"))
        fields=fields.loc[~duplicate_c].copy()
        selected=(fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code) & fields["epcf"].str.lower().eq("e"))
    if not selected.any():
        # A source field can be omitted from automatic E/P discovery (or be
        # misrouted to C) despite being a substantive component. Keep the
        # reviewed field searchable as a locked E candidate rather than
        # allowing an unresolved source identity to disappear from the atlas.
        exact=(fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code))
        if exact.any():
            fields.loc[exact,"epcf"]="e"
            selected=exact
        else:
            source=raw_catalog[(raw_catalog.wave.str.lower().eq(wave)) & raw_catalog.variable.str.lower().eq(code)].iloc[0]
            same_module=fields[(fields["Source.Wave"].str.lower().eq(wave)) & fields["Data.File.Name"].str.lower().eq(str(source.module).lower())]
            module_description=same_module.iloc[0]["Data.File.Description"] if not same_module.empty else str(source.module)
            row={
                "Variable.Name":str(source.variable), "Variable.Description":str(source.variable_label),
                "Data.File.Name":str(source.module), "Data.File.Description":str(module_description),
                "Begin.Year":wave, "EndYear":wave, "Component":str(source.module),
                "Use.Constraints":"CHARLS applicant data; access and publication governed by official agreement",
                "epcf":"e", "category":"behavioral exposures", "subcategory":"source-conflicted exposure component",
                "Source.Wave":wave, "Source.Archive":str(source.source),
                "Candidate.Status":"DO NOT ANALYZE pending official source identity review",
                "Harmonization.Status":"source-conflicted field retained for search only",
                "Review.Flag":"DO NOT ANALYZE pending official source identity review",
                "Value.Labels":"", "Value.Label.Source":"", "Value.Label.Review":"source conflict; labels withheld",
            }
            for column in fields.columns:
                row.setdefault(column,"")
            fields=pd.concat([fields,pd.DataFrame([row],columns=fields.columns)],ignore_index=True).fillna("")
            selected=(fields["Source.Wave"].str.lower().eq(wave) & fields["Variable.Name"].str.lower().eq(code) & fields["epcf"].str.lower().eq("e"))
    fields.loc[selected,"category"]="social protection"
    if metadata_type == "pension_2015_age_field_identity_conflict":
        fields.loc[selected,"subcategory"]="current pension claim-age eligibility; questionnaire/Codebook title conflict"
        fields.loc[selected,"Candidate.Status"]="DO NOT ANALYZE; questionnaire asks current age eligibility, but Codebook field title describes a different children-payment item"
        fields.loc[selected,"Value.Labels"]="1=Yes; 2=No"
        fields.loc[selected,"Value.Label.Source"]="sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt"
        fields.loc[selected,"Value.Label.Review"]="questionnaire categories and Codebook title conflict recorded; frequencies omitted"
        fields.loc[selected,"Harmonization.Status"]="retain question wording and plan route; do not harmonize or analyze until official release field identity is reconciled"
        fields.loc[selected,"Review.Flag"]="DO NOT ANALYZE pending exact Wave 3 questionnaire-to-Codebook field mapping confirmation"
    elif metadata_type == "pension_string_duration_unresolved":
        fields.loc[selected,"subcategory"]="string-coded years since firm-pension transfer"
        fields.loc[selected,"Candidate.Status"]="DO NOT ANALYZE numerically; questionnaire/Codebook identify years and route is verified, but the release stores strings and one plan field contains nonnumeric text"
        fields.loc[selected,"Value.Labels"]=""
        fields.loc[selected,"Harmonization.Status"]="unit is years; preserve raw route-specific strings; one plan field contains nonnumeric text, so do not parse or use either field continuously until official release encoding and special-text rules are clarified"
        fields.loc[selected,"Review.Flag"]="DO NOT ANALYZE numerically until official release string encoding and special-text/missing rules are confirmed; preserve raw strings"
    elif metadata_type == "smoking_cessation_component_source_conflict":
        fields.loc[selected,"category"]="behavioral exposures"
        fields.loc[selected,"subcategory"]="smoking cessation timing component; questionnaire/Codebook identity conflict"
        fields.loc[selected,"Candidate.Status"]="DO NOT ANALYZE; official 2018 questionnaire and Codebook assign opposite age/year meanings to DA062_1 and DA062_2"
        fields.loc[selected,"Value.Label.Source"]="sources_official/CHARLS_2018_Questionnaire_extracted.txt:L3089-L3090; sources_official/CHARLS_2018_Codebook_extracted.txt:L43140-L43158"
        fields.loc[selected,"Value.Label.Review"]="source conflict recorded; do not display a reconciled unit or categories"
        fields.loc[selected,"Unit"]="unresolved: questionnaire and Codebook disagree"
        fields.loc[selected,"Harmonization.Status"]="questionnaire: DA062_1=Age, DA062_2=Year; Codebook: DA062_1=Year, DA062_2=Age; do not harmonize or analyze until the official release field identity is reconciled"
        fields.loc[selected,"Review.Flag"]="DO NOT ANALYZE pending official clarification of 2018 cessation component identities; preserve source discrepancy"
    elif metadata_type == "pension_2018_candidate_verified":
        fields.loc[selected,"Candidate.Status"]="official 2018 Wave 4 questionnaire and Codebook verify the source item, unit/categories, and routed context; candidate only"
        fields.loc[selected,"Value.Label.Source"]="sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"
        fields.loc[selected,"Value.Label.Review"]="official response categories/unit reviewed; Codebook frequencies omitted"
        if code.startswith(("fn006_w4_", "fn007_w4_")):
            is_receipt=code.startswith("fn006_w4_")
            fields.loc[selected,"subcategory"]="formal-plan receipt location; coarse plan-loop category" if is_receipt else "formal-plan participation location; coarse plan-loop category"
            fields.loc[selected,"Value.Labels"]="1=Current residence; 2=Other township/village/neighborhood in current-residence county/city/district; 3=Other place; 997=Don't know"
            fields.loc[selected,"Harmonization.Status"]="the suffix identifies a selected-plan loop instance, not a precise address; retain loop/plan identity and its denominator"
            fields.loc[selected,"Review.Flag"]="candidate only; coarse current-residence-relative category; do not merge plan loops or expose any separate detailed location text"
        elif code in {"fn070_w4","fn080_w4","fn042_w4","fn096_w4","fn078_w4","fn056_w4","fn074_w4","fn079_w4","fn044_w2","fn034_w4","fn059_w2"}:
            fields.loc[selected,"subcategory"]="plan-specific coarse location relative to current residence"
            fields.loc[selected,"Value.Labels"]="1=Current residence; 2=Other township/village/neighborhood in current-residence county/city/district; 3=Other place; 997=Don't know"
            fields.loc[selected,"Harmonization.Status"]="coarse location category only; retain named plan and receipt-versus-participation meaning; detailed address text is excluded"
            fields.loc[selected,"Review.Flag"]="candidate only; preserve plan-specific route and do not infer skipped values"
        elif code == "fn058_w4":
            fields.loc[selected,"subcategory"]="social-pension family participation/expected receipt/current receipt screening status"
            fields.loc[selected,"Value.Labels"]="1=Yes; 2=No"
            fields.loc[selected,"Harmonization.Status"]="screening item combines current participation, expected receipt, or current receipt; it does not measure current receipt alone"
            fields.loc[selected,"Review.Flag"]="candidate only; keep the screening construct distinct from current benefit receipt"
        elif code == "fn058_w4_a":
            fields.loc[selected,"subcategory"]="selected social-pension program type"
            fields.loc[selected,"Value.Labels"]="1=Urban and Rural Resident Pension; 2=New Rural Resident Pension; 3=Urban Resident Pension; 4=Don't know the type"
            fields.loc[selected,"Harmonization.Status"]="multi-option plan type asked after the social-pension family screen; preserve unknown-type response and plan route"
            fields.loc[selected,"Review.Flag"]="candidate only; do not treat plan options as independent person-level records"
        elif code == "fn033_w2":
            fields.loc[selected,"subcategory"]="years enrolled in the named pension plan"
            fields.loc[selected,"Harmonization.Status"]="2018 wording includes years with different employers under the same plan; retain as Wave 4 definition and preserve plan route"
            fields.loc[selected,"Review.Flag"]="candidate only; continuous years as reported; do not derive from incomplete dates"
        elif code in {"fn066_w2_1","fn066_w2_2"}:
            is_month=code.endswith("_1")
            fields.loc[selected,"subcategory"]="expected formal-plan monthly benefit" if is_month else "expected formal-plan lump-sum benefit"
            fields.loc[selected,"Harmonization.Status"]="selected named formal-pension route; keep monthly and lump-sum response forms separate; -1 is unknown, not an amount"
            fields.loc[selected,"Review.Flag"]="candidate only; do not combine payment forms or infer skipped values as zero"
        elif code == "fn056_w2_8":
            fields.loc[selected,"subcategory"]="life-insurance payout amount already received"
            fields.loc[selected,"Harmonization.Status"]="life-insurance claim route; retain separately from pension receipt and expected life-insurance benefits"
            fields.loc[selected,"Review.Flag"]="candidate only; -1/unknown is not a payout amount"
    elif metadata_type == "pension_2015_candidate_verified":
        fields.loc[selected,"Candidate.Status"]="official 2015 Wave 3 questionnaire and Codebook verify the plan-specific field and response route; candidate only"
        if code.startswith("fn003_w2_"):
            fields.loc[selected,"subcategory"]="institution-pension receipt start-date component"
            fields.loc[selected,"Harmonization.Status"]="government-affiliated institution pension route from FN002_W2; year and month remain separate; month 0 means not remembered"
            fields.loc[selected,"Review.Flag"]="candidate only; preserve plan route and do not derive complete dates from missing components"
        elif code.startswith("fn063_w2"):
            fields.loc[selected,"subcategory"]="2015 residents-pension transfer-from-firm status"
            fields.loc[selected,"Harmonization.Status"]="1=Yes, 2=No; asks specifically about firm-pension transfer for residents or urban-residents plan; do not merge with broad 2011/2013 source status"
            fields.loc[selected,"Review.Flag"]="candidate only; preserve specific source-program and pension-plan route"
        elif code.startswith("fn064_w2"):
            fields.loc[selected,"subcategory"]="2015 source and duration of firm-pension transfer"
            fields.loc[selected,"Harmonization.Status"]="conditional on the matching plan-specific fn063 transfer status; source is firm pension; duration children are string-coded and separately blocked"
            fields.loc[selected,"Review.Flag"]="candidate only; keep source and years-since-transfer fields distinct"
        elif code.startswith("fn068_w3"):
            fields.loc[selected,"subcategory"]="historical pension eligibility and child-support route at scheme rollout"
            fields.loc[selected,"Harmonization.Status"]="plan-specific Wave 3 route; separates age-based direct receipt from a local child-enrollment requirement; not current receipt or a current premium amount"
            fields.loc[selected,"Review.Flag"]="candidate only; preserve initial scheme-rollout context and routed denominator"
        else:
            fields.loc[selected,"subcategory"]="2015 plan-specific pension participation context"
            fields.loc[selected,"Harmonization.Status"]="plan-specific Wave 3 route; preserve source categories and structural skips"
            fields.loc[selected,"Review.Flag"]="candidate only; do not infer No or zero from skipped fields"
    elif metadata_type == "pension_interval_bound_unresolved":
        fields.loc[selected,"subcategory"]="pension amount interval-bound field; unresolved response sequence"
        fields.loc[selected,"Candidate.Status"]="DO NOT ANALYZE as a numeric amount; official Codebook identifies a string Min/Max Bracket bound and release-level response interpretation is unresolved"
        fields.loc[selected,"Harmonization.Status"]="retain as an interval bound only; do not assign a midpoint, convert to a point estimate, or treat as an independent association measure"
        fields.loc[selected,"Review.Flag"]="DO NOT ANALYZE as an amount; confirm exact response sequence and unit before any statistical use"
    elif metadata_type == "pension_unfolding_bracket_sequence":
        fields.loc[selected,"subcategory"]="threshold-specific pension expected-benefit bracket response sequence"
        fields.loc[selected,"Candidate.Status"]="DO NOT ANALYZE as a numeric benefit; official Codebook threshold-specific categories are searchable, but release-level sequence/period interpretation remains unresolved"
        fields.loc[selected,"Harmonization.Status"]="retain threshold-specific category and source concept only; do not combine thresholds, assign a midpoint, or interpret as a Yuan amount"
        fields.loc[selected,"Review.Flag"]="DO NOT ANALYZE as an amount; preserve the exact threshold/category and confirm payment period and sequence interpretation before any statistical use"
        label_row=bracket_label_map.get(code)
        if label_row is not None and str(getattr(label_row,"value_labels","")).strip():
            fields.loc[selected,"Value.Labels"]=str(label_row.value_labels)
            fields.loc[selected,"Value.Label.Source"]=str(getattr(label_row,"value_label_source",""))
            fields.loc[selected,"Value.Label.Review"]="official 2011 questionnaire/Codebook threshold categories transcribed; no response frequencies shown"
    elif metadata_type == "pension_source_identity_verified":
        fields.loc[selected,"subcategory"]="2011 pension source field verified against correct baseline questionnaire"
        if code == "fn015":
            fields.loc[selected,"Candidate.Status"]="official 2011 baseline questionnaire and Codebook confirm resident-pension transfer status; candidate only"
            fields.loc[selected,"Harmonization.Status"]="FN015=1 Yes/2 No; FN016 source is asked only after Yes; preserve selected residents-pension route and do not infer No from missingness"
            fields.loc[selected,"Review.Flag"]="candidate only; distinguish the 2011 FN015 item from the similarly numbered item in the misidentified 2013 questionnaire extract"
        elif code == "fn016":
            fields.loc[selected,"Candidate.Status"]="official 2011 baseline questionnaire and Codebook confirm conditional resident-pension transfer source; candidate only"
            fields.loc[selected,"Harmonization.Status"]="asked only after FN015=Yes; categories are rural pension, firm basic pension, or other; other text is not exposed"
            fields.loc[selected,"Review.Flag"]="candidate only; retain conditional route and source categories; do not publish open text"
        elif code == "fn065":
            fields.loc[selected,"subcategory"]="enrolled residents-pension transfer status"
            fields.loc[selected,"Candidate.Status"]="official 2011 questionnaire and Codebook confirm transfer status among enrolled residents-pension participants; candidate only"
            fields.loc[selected,"Harmonization.Status"]="FN065=1 Yes/2 No; route is enrolled residents-pension participants (FN039=4), aligned with 2013 FN063_W2; distinct from current-recipient FN015"
            fields.loc[selected,"Review.Flag"]="candidate only; preserve enrolled-plan route and do not infer No from missingness"
        elif code == "fn066":
            fields.loc[selected,"subcategory"]="enrolled residents-pension transfer source"
            fields.loc[selected,"Candidate.Status"]="official 2011 questionnaire and Codebook confirm conditional transfer source among enrolled residents-pension participants; candidate only"
            fields.loc[selected,"Harmonization.Status"]="asked after FN065=Yes among FN039=4 enrollees; categories rural pension, firm basic pension, other; aligned with 2013 FN064_W2; distinct from current-recipient FN016"
            fields.loc[selected,"Review.Flag"]="candidate only; preserve conditional enrolled-plan route; do not publish open text"
        elif code == "fn036_1":
            fields.loc[selected,"Candidate.Status"]="official 2011 baseline questionnaire and Codebook confirm expected employer-plan pension benefit in Yuan/month; candidate only"
            fields.loc[selected,"Harmonization.Status"]="conditional on FN034=Yes or FN035=1; keep separate from FN036_2 final-pay percentage and from resident-plan benefits"
            fields.loc[selected,"Review.Flag"]="candidate only; do not infer skipped amount as zero or convert from the paired percentage field"
        elif code == "fn036_2":
            fields.loc[selected,"Candidate.Status"]="official 2011 baseline questionnaire and Codebook confirm expected employer-plan pension benefit as percent of final pay; candidate only"
            fields.loc[selected,"Harmonization.Status"]="conditional on FN034=Yes or FN035=1; denominator is final pay; keep separate from Yuan/month field"
            fields.loc[selected,"Review.Flag"]="candidate only; do not convert to Yuan or combine with monthly amount responses"
        elif code in {"fn051_1", "fn051_2"}:
            component="year" if code.endswith("_1") else "month (0=not remembered)"
            fields.loc[selected,"subcategory"]="commercial pension premium start-date component"
            fields.loc[selected,"Candidate.Status"]=f"official 2011 baseline questionnaire and Codebook confirm commercial pension contribution start {component}; candidate only"
            fields.loc[selected,"Harmonization.Status"]="commercial-pension route only; year and month are separate components; month 0 means not remembered, not January"
            fields.loc[selected,"Review.Flag"]="candidate only; preserve start-date components and do not derive duration from incomplete or skipped dates"
        elif code in {"fn060_1", "fn060_2"}:
            component="year" if code.endswith("_1") else "month (0=not remembered)"
            fields.loc[selected,"subcategory"]="selected resident-pension plan contribution start-date component"
            fields.loc[selected,"Candidate.Status"]=f"official 2011 baseline questionnaire and Codebook confirm selected-plan contribution start {component}; candidate only"
            fields.loc[selected,"Harmonization.Status"]="asked after FN039 selects a rural/resident/urban-resident pension plan; keep plan context and year/month separate; month 0 means not remembered"
            fields.loc[selected,"Review.Flag"]="candidate only; do not collapse pension plans, derive duration from incomplete dates, or treat month 0 as January"

    elif metadata_type == "pension_2013_source_context_verified":
        labels={
            "fn007_w2_1_":"1=Current work unit; 2=Last work unit; 3=Unit processing retirement; 4=None",
            "fn007_w2_2_":"1=Current work unit; 2=Last work unit; 3=Unit processing retirement; 4=None",
            "fn009_w2_1_":"1=Government; 2=Institution; 3=NGO; 4=Firm; 5=Individual; 6=Other",
            "fn009_w2_2_":"1=Government; 2=Institution; 3=NGO; 4=Firm; 5=Individual; 6=Other",
            "fn010_w2_1_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
            "fn010_w2_2_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
            "fn031_w2":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
            "fn044_w2":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
            "fn059_w2_1_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
            "fn059_w2_2_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
            "fn059_w2_3_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
            "fn007_w2_1_":"1=Current work unit; 2=Last work unit; 3=Unit processing retirement; 4=None",
            "fn007_w2_2_":"1=Current work unit; 2=Last work unit; 3=Unit processing retirement; 4=None",
            "fn009_w2_1_":"1=Government; 2=Institution; 3=NGO; 4=Firm; 5=Individual; 6=Other",
            "fn009_w2_2_":"1=Government; 2=Institution; 3=NGO; 4=Firm; 5=Individual; 6=Other",
            "fn010_w2_1_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
            "fn010_w2_2_":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
            "fn044_w2":"1=Same as permanent address; 2=Another village in permanent-address county; 3=Other; 4=Abroad",
        }
        fields.loc[selected,"Candidate.Status"]="official Wave 3 questionnaire and Codebook verify the source field and conditional route; candidate only"
        fields.loc[selected,"Value.Labels"]=labels[code]
        fields.loc[selected,"Value.Label.Source"]=fields.loc[selected,"Source.Wave"].map(lambda w:f"sources_official/CHARLS_{w}_Questionnaire_extracted.txt; sources_official/CHARLS_{w}_Codebook_extracted.txt")
        fields.loc[selected,"Value.Label.Review"]="questionnaire options verified; all offered categories shown, including categories with no Codebook observations; frequencies omitted"
        if code.startswith("fn007"):
            fields.loc[selected,"subcategory"]="pension-source work-unit reference"
            fields.loc[selected,"Harmonization.Status"]="preserve FN006_W2 pension route; 1=current work unit, 2=last work unit, 3=retirement-processing unit, 4=none; skips are not No"
            fields.loc[selected,"Review.Flag"]="candidate only; conditional pension-source context, not an address or independent pension receipt indicator"
        elif code.startswith("fn009"):
            fields.loc[selected,"subcategory"]="pension-source work-unit employer type"
            fields.loc[selected,"Harmonization.Status"]="asked only when FN007_W2=4; preserve government/institution versus firm route; no open-text response is included"
            fields.loc[selected,"Review.Flag"]="candidate only; retain conditional route and full questionnaire options; do not infer a work-unit type from missingness"
        else:
            fields.loc[selected,"subcategory"]="coarse geographic scope of pension participation or source unit"
            fields.loc[selected,"Harmonization.Status"]="retain only coarse relation-to-permanent-address category and the pension-plan route; no linked village/county/province text or geocoding"
            fields.loc[selected,"Review.Flag"]="candidate only; coarse location category; keep plan-specific fields distinct and do not publish linked location details"

# Provisional phenotype corrections can retain a valid P role while explicitly
# blocking analysis when the codebook exists but the matching questionnaire item
# has not been identified.
for override in overrides.loc[overrides["keep_role"].str.lower().eq("p") & overrides["metadata_type"].str.lower().eq("codebook_only_ordinal_phenotype")].to_dict("records"):
    selected=(fields["Source.Wave"].str.lower().eq(str(override["wave"]).lower()) & fields["Variable.Name"].str.lower().eq(str(override["code"]).lower()) & fields["epcf"].str.lower().eq("p"))
    fields.loc[selected,"category"]="health and symptoms"
    fields.loc[selected,"subcategory"]="codebook-only sleep severity item; question identity unresolved"
    fields.loc[selected,"Candidate.Status"]="DO NOT ANALYZE; ordinal symptom response appears in official codebook, but exact questionnaire item and recall period are unresolved"
    fields.loc[selected,"Harmonization.Status"]="retain source item separately; do not merge with other sleep questions or infer a recall period until official question wording is matched"
    fields.loc[selected,"Review.Flag"]="DO NOT ANALYZE pending exact-wave questionnaire/instrument identity and response-route confirmation"
order_reference=AUDIT/".charls_atlas_candidate_fields_order_reference.tmp"
fields=preserve_existing_catalog_order(fields,order_reference if order_reference.exists() else field_path)
fields.to_csv(field_path,index=False,encoding="utf-8-sig")

series_path=AUDIT/"charls_atlas_candidate_series_v0.csv"
fields_for_series=fields.copy()
fields_for_series["_code_key"]=fields_for_series["Variable.Name"].str.lower()
def summarize_label_review(values):
    reviews=[str(value) for value in values if pd.notna(value) and str(value).strip()]
    blocked=next((value for value in reviews if any(marker in value.lower() for marker in ("do not analyze","unresolved","conflict"))),"")
    if blocked:
        return blocked
    partial=next((value for value in reviews if value.startswith("official Codebook extraction exposes only a partial response-code set")),"")
    if partial:
        return partial
    if "officially reviewed" in reviews:
        return "officially reviewed"
    if any("audited measurement component" in value for value in reviews):
        return "audited measurement component"
    if any("continuous measure metadata available" in value for value in reviews):
        return "continuous measure metadata available"
    return "not yet reviewed"
series=(fields_for_series.groupby(["epcf","category","subcategory","_code_key"],dropna=False)
 .agg(**{"Variable.Name":("Variable.Name","first"),
       "Variable.Description":("Variable.Description",lambda s:" | ".join(sorted(set(s))[:3])),
       "waves":("Source.Wave",lambda s:",".join(sorted(set(s)))),
       "wave_count":("Source.Wave","nunique"),
       "source_modules":("Data.File.Name",lambda s:",".join(sorted(set(s)))),
       "value_labels":("Value.Labels",lambda s:" | ".join(sorted({str(v) for v in s if pd.notna(v) and str(v).strip()}))),
       "value_label_source":("Value.Label.Source",lambda s:" | ".join(sorted({str(v) for v in s if pd.notna(v) and str(v).strip()}))),
       "value_label_review":("Value.Label.Review",summarize_label_review)})
 .reset_index().drop(columns=["_code_key"]))
removed_series="rebuilt"
series.to_csv(series_path,index=False,encoding="utf-8-sig")
series_json=AUDIT/"charls_atlas_candidate_series_v0.json"
series_json.write_text(json.dumps(series.to_dict(orient="records"),ensure_ascii=False,separators=(",",":")),encoding="utf-8")
site_json=ROOT/"site-prototype/dist/catalog.json"
site_json.write_text(series_json.read_text(encoding="utf-8"),encoding="utf-8")

# Refresh the two discovery summaries from the corrected field list.
summary=(fields.groupby(["epcf","category","subcategory"],dropna=False)
 .agg(source_field_wave_rows=("Variable.Name","size"),distinct_source_codes=("Variable.Name","nunique"),wave_count=("Source.Wave","nunique"))
 .reset_index().sort_values(["epcf","category","subcategory"]))
summary.to_csv(AUDIT/"charls_atlas_candidate_domain_counts_v0.csv",index=False,encoding="utf-8-sig")
label=fields.assign(_has_label=fields["Value.Labels"].fillna("").str.strip().ne(""),_wave_code=fields["Source.Wave"].astype(str)+"::"+fields["Variable.Name"].astype(str).str.lower())
label=(label.groupby(["epcf","category","subcategory"],dropna=False)
 .agg(field_category_rows=("Variable.Name","size"),distinct_wave_fields=("_wave_code","nunique"),rows_with_reviewed_labels=("_has_label","sum"))
 .reset_index().sort_values(["epcf","category","subcategory"]))
label.to_csv(AUDIT/"charls_ep_catalog_value_label_coverage_v1.csv",index=False,encoding="utf-8-sig")
label=fields.assign(_has_label=fields["Value.Labels"].fillna("").str.strip().ne(""),_wave_code=fields["Source.Wave"].astype(str)+"::"+fields["Variable.Name"].astype(str).str.lower())
label=(label.groupby(["epcf","category","subcategory"],dropna=False)
 .agg(field_category_rows=("Variable.Name","size"),distinct_wave_fields=("_wave_code","nunique"),rows_with_reviewed_labels=("_has_label","sum"))
 .reset_index().sort_values(["epcf","category","subcategory"]))
label.to_csv(AUDIT/"charls_ep_catalog_value_label_coverage_v1.csv",index=False,encoding="utf-8-sig")
print(json.dumps({"role_overrides":len(keys),"removed_E_field_wave_rows":removed_fields,"removed_E_source_series":removed_series,"metadata_rows_reclassified_or_removed":metadata_removed,"remaining_field_rows":len(fields)},ensure_ascii=False))
