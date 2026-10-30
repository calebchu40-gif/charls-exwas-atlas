#!/usr/bin/env python3
"""Run the protected, frozen CHARLS 2011 K150/K90 household-environment block.

This runner cannot fit models unless the exact official source/frame and a
reviewed, hash-bound scale-up configuration pass the Wave 1 readiness gates.
All inputs and outputs remain under LOCALAPPDATA/CHARLS_ExWAS_Atlas.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import subprocess
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from project_paths import PRIVATE_ROOT, require_private_path
from run_2011_water_blood_pilot import AGE, DATA, PRIVATE, ROOT, read_analytes
from require_verified_wave1_frame import (
    analysis_plan_fingerprint,
    require_verified_wave1_frame,
    require_wave1_analysis_readiness,
)
from audit_wave1_scaleup_metadata_readiness import audit as audit_scaleup_metadata


EXPECTED_SVY = "0.35.0"
PLAN_KEY = "household_environment_scaleup"
CONFIG_PATH = PRIVATE / "analysis_review" / "wave1_household_environment_scaleup_model_config.json"
REGISTER = ROOT / "audit" / "wave1_household_environment_hypothesis_register_v0.csv"
OUTPUT_DIR = PRIVATE / "scaleup_2011_household_environment"
ID_FIELD = "ID"
OUTCOME_TERMS = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required protected analysis configuration is missing: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Scale-up configuration must be a JSON object")
    return value


def _load_registry() -> list[dict[str, str]]:
    with REGISTER.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    return rows


def _numeric_code(value: object, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid numeric code in frozen configuration: {label}") from exc
    if not math.isfinite(result):
        raise ValueError(f"Invalid non-finite numeric code in frozen configuration: {label}")
    return result


def _validate_configuration(
    config: dict[str, Any], analytes: list[dict[str, str]], registry: list[dict[str, str]]
) -> None:
    if config.get("status") != "frozen":
        raise ValueError("Scale-up configuration is not frozen")
    for section in ("target", "frame", "design", "exposure_field_mapping", "model", "outcome_transformations", "outcome_validity_rules"):
        if not isinstance(config.get(section), dict):
            raise ValueError(f"Scale-up configuration lacks {section}")
    for key in ("estimand", "population_description", "age_domain_method"):
        if not str(config["target"].get(key, "")).strip():
            raise ValueError(f"Frozen target specification lacks {key}")
    frame = config["frame"]
    if frame.get("analysis_sample_rule") != "finite_positive_bloodweight_respondents":
        raise ValueError("Wave 1 blood analyses require the observed positive-bloodweight respondent sample")
    age_fields = (
        frame.get("age_lower_field"), frame.get("age_upper_field"),
        frame.get("age_covariate_field"),
    )
    if any(not isinstance(field, str) or not field.strip() for field in age_fields):
        raise ValueError("Frozen frame specification must declare lower/upper age fields and an age covariate field")
    age_domain_bound = frame.get("age_domain_bound")
    if age_domain_bound not in {"lower", "upper", "full"}:
        raise ValueError("Frozen frame specification lacks a supported age-domain rule")
    if age_domain_bound != "full" and frame.get("minimum_age") is None:
        raise ValueError("Age-restricted domain requires a minimum_age")
    if any(not OUTCOME_TERMS.fullmatch(field) or field == ID_FIELD for field in age_fields):
        raise ValueError("Frozen age fields must be valid non-key field names")
    if len(set(age_fields)) != len(age_fields):
        raise ValueError("Age lower bound, upper bound, and model midpoint fields must be distinct")
    if frame.get("minimum_age") is not None:
        minimum_age = _numeric_code(frame["minimum_age"], "frame.minimum_age")
        if minimum_age < 0:
            raise ValueError("Frozen minimum age cannot be negative")
    if not str(frame.get("full_design_frame_definition", "")).strip():
        raise ValueError("Frozen frame specification lacks full_design_frame_definition")

    design = config["design"]
    for key in ("weight_field", "psu_field", "variance_method", "variance_limitations"):
        if not str(design.get(key, "")).strip():
            raise ValueError(f"Frozen design specification lacks {key}")
    if design.get("variance_method") != "Taylor linearization":
        raise ValueError("This runner currently supports only an approved Taylor-linearization design")
    if design.get("weight_field") != "bloodweight":
        raise ValueError("Wave 1 blood outcomes require the official bloodweight field")
    if not isinstance(design.get("with_replacement"), bool):
        raise ValueError("Frozen design specification must state with_replacement as true/false")
    if not isinstance(design.get("stratum_fields"), list):
        raise ValueError("Frozen design specification must provide stratum_fields, including an explicit empty list if none apply")
    if design.get("replicate_weight_fields"):
        raise ValueError("Replicate-weight designs are not supported by this Taylor-only runner; use an approved implementation")
    if design.get("singleton_psu_method") not in {
        "center", "scale", "skip", "self_representing", "collapse", "pool"
    }:
        raise ValueError("Singleton PSU method is not supported by the pinned svy engine")
    if design.get("domain_singleton_method") not in {"standard", "apply"}:
        raise ValueError("Frozen design must explicitly choose standard or apply domain-singleton handling")
    if design.get("on_domain_singletons") not in {"error", "warn", "ignore"}:
        raise ValueError("Frozen design must explicitly set the domain-singleton diagnostic policy")

    exposure_map = config["exposure_field_mapping"]
    required_exposures = {"i016", "i017", "i019", "i020", "i021", "i022"}
    if set(exposure_map) != required_exposures or any(not str(v).strip() for v in exposure_map.values()):
        raise ValueError("Frozen exposure_field_mapping must map each planned 2011 item i016-i022 exactly once")
    if len(set(exposure_map.values())) != len(exposure_map):
        raise ValueError("Each planned household questionnaire item must map to a distinct prepared-table field")
    model = config["model"]
    if model.get("family") != "gaussian" or not str(model.get("primary_model_id", "")).strip():
        raise ValueError("Frozen model must declare a primary_model_id and Gaussian family")
    for key, expected_type in (
        ("continuous_covariates", list), ("binary_covariates", list),
        ("categorical_covariates", dict),
    ):
        if not isinstance(model.get(key), expected_type):
            raise ValueError(f"Frozen model {key} must be {expected_type.__name__}")
    if not str(model.get("missing_data_rule", "")).strip() or not str(model.get("outcome_scale_rule", "")).strip():
        raise ValueError("Frozen model must state missing-data and outcome-scale rules")

    expected_outcomes = {row["concept_id"] for row in analytes}
    transforms = config["outcome_transformations"]
    if set(transforms) != expected_outcomes:
        raise ValueError("Frozen transformations must cover exactly the 15 registered blood phenotypes")
    if any(not isinstance(value, str) or value not in {"identity", "log"} for value in transforms.values()):
        raise ValueError("Each blood outcome transformation must be frozen as identity or log")
    validity = config["outcome_validity_rules"]
    if set(validity) != expected_outcomes:
        raise ValueError("Frozen validity rules must cover exactly the 15 registered blood phenotypes")
    required_validity_fields = (
        "review_status", "reviewer", "reviewed_at", "source_anchor", "unit",
        "valid_domain_rule", "valid_min", "valid_max", "invalid_codes",
        "lod_censoring_rule", "topcode_rule", "fasting_rule",
    )
    for analyte in analytes:
        concept = analyte["concept_id"]
        rule = validity[concept]
        if not isinstance(rule, dict) or any(key not in rule for key in required_validity_fields):
            raise ValueError(f"Frozen validity rule for {concept} is incomplete")
        if rule["review_status"] != "approved":
            raise ValueError(f"Frozen validity rule for {concept} has not been independently approved")
        for key in ("reviewer", "reviewed_at", "source_anchor", "valid_domain_rule"):
            if not isinstance(rule.get(key), str) or not rule[key].strip():
                raise ValueError(f"Frozen validity rule for {concept} lacks {key}")
        if rule["lod_censoring_rule"] not in {"none_reported", "handled_by_invalid_codes_or_bounds"}:
            raise ValueError(f"Frozen validity rule for {concept} uses unsupported LOD handling")
        if rule["topcode_rule"] not in {"none_reported", "handled_by_invalid_codes_or_bounds"}:
            raise ValueError(f"Frozen validity rule for {concept} uses unsupported top-code handling")
        fasting = rule["fasting_rule"]
        if not isinstance(fasting, dict) or fasting.get("mode") not in {"not_applicable", "retain_all", "restrict"}:
            raise ValueError(f"Frozen validity rule for {concept} has unsupported fasting handling")
        if fasting["mode"] == "restrict":
            if not isinstance(fasting.get("field"), str) or not OUTCOME_TERMS.fullmatch(fasting["field"]):
                raise ValueError(f"Frozen validity rule for {concept} fasting restriction lacks a valid field")
            if not isinstance(fasting.get("eligible_codes"), list) or not fasting["eligible_codes"]:
                raise ValueError(f"Frozen validity rule for {concept} fasting restriction lacks eligible codes")
            for value in fasting["eligible_codes"]:
                _numeric_code(value, f"{concept}.fasting eligible code")
        elif fasting.get("field") not in (None, "") or fasting.get("eligible_codes", []) not in (None, []):
            raise ValueError(f"Frozen validity rule for {concept} must not specify fasting codes unless mode=restrict")
        if rule["unit"] != analyte["unit"]:
            raise ValueError(f"Frozen validity rule for {concept} has a unit inconsistent with the reviewed crosswalk")
        if not isinstance(rule["invalid_codes"], list):
            raise ValueError(f"Frozen validity rule for {concept} must provide invalid_codes as a list")
        invalid_codes = [_numeric_code(value, f"{concept}.invalid_codes") for value in rule["invalid_codes"]]
        for key in ("valid_min", "valid_max"):
            value = rule[key]
            if value is not None:
                _numeric_code(value, f"{concept}.{key}")
        lower, upper = rule["valid_min"], rule["valid_max"]
        if lower is not None and upper is not None and float(lower) > float(upper):
            raise ValueError(f"Frozen validity rule for {concept} has reversed valid_min/valid_max")
        if (
            rule["lod_censoring_rule"] == "handled_by_invalid_codes_or_bounds"
            or rule["topcode_rule"] == "handled_by_invalid_codes_or_bounds"
        ) and not invalid_codes and lower is None and upper is None:
            raise ValueError(f"Frozen validity rule for {concept} claims handled censoring without executable codes/bounds")
        if len(invalid_codes) != len(set(invalid_codes)):
            raise ValueError(f"Frozen validity rule for {concept} contains duplicate invalid_codes")

    # Validate model terms before touching the prepared participant table.
    def require_term(name: object, context: str) -> str:
        term = str(name or "")
        if not OUTCOME_TERMS.fullmatch(term):
            raise ValueError(f"Invalid prepared-table field name for {context}")
        return term

    for item in model["continuous_covariates"]:
        if not isinstance(item, dict):
            raise ValueError("Continuous covariates must use explicit field/transform objects")
        require_term(item.get("field"), "continuous covariate")
        if item.get("transform") not in {"identity", "centered_linear", "centered_quadratic"}:
            raise ValueError("Unsupported continuous covariate transform")
        if item.get("transform") != "identity" and item.get("center") is None:
            raise ValueError("Centered covariate terms must declare a center")
        if item.get("center") is not None:
            _numeric_code(item["center"], "continuous covariate center")
    age_covariate = frame["age_covariate_field"]
    age_terms = [item for item in model["continuous_covariates"] if item.get("field") == age_covariate]
    if len(age_terms) != 2 or {item.get("transform") for item in age_terms} != {"centered_linear", "centered_quadratic"}:
        raise ValueError("The age midpoint must enter the primary model as centered linear and quadratic terms")
    if len({str(item.get("center")) for item in age_terms}) != 1:
        raise ValueError("Age midpoint linear and quadratic terms must use the same predeclared center")
    for item in model["binary_covariates"]:
        if not isinstance(item, dict):
            raise ValueError("Binary covariates must use explicit field/code objects")
        require_term(item.get("field"), "binary covariate")
        if item.get("positive_value") is None or item.get("reference_value") is None:
            raise ValueError("Binary covariates must specify positive_value and reference_value")
        if _numeric_code(item["positive_value"], "binary positive code") == _numeric_code(
            item["reference_value"], "binary reference code"
        ):
            raise ValueError("Binary covariate positive and reference codes must differ")
    for label, item in model["categorical_covariates"].items():
        require_term(item.get("field"), f"categorical covariate {label}")
        if not isinstance(item.get("levels"), list) or len(item["levels"]) < 2:
            raise ValueError(f"Categorical covariate {label} must list at least two levels")
        if item.get("reference") not in item["levels"]:
            raise ValueError(f"Categorical covariate {label} reference must be one of its declared levels")
        levels = [_numeric_code(value, f"categorical level {label}") for value in item["levels"]]
        if len(set(levels)) != len(levels):
            raise ValueError(f"Categorical covariate {label} has duplicate numeric levels")
        _numeric_code(item["reference"], f"categorical reference {label}")

    for row in registry:
        _numeric_code(row["exposure_code_candidate"], "registered exposure code")
        _numeric_code(row["reference_code_candidate"], "registered reference code")


def _selected_fields(config: dict[str, Any], analytes: list[dict[str, str]], registry: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    frame, design, model = config["frame"], config["design"], config["model"]
    age_lower = str(frame["age_lower_field"])
    age_upper = str(frame["age_upper_field"])
    age_covariate = str(frame["age_covariate_field"])
    age_file_fields = [age_lower, age_upper]
    generated_age_fields = set(age_file_fields) | {age_covariate}
    fields = {
        ID_FIELD, design["weight_field"], design["psu_field"],
        *design["stratum_fields"], *config["exposure_field_mapping"].values(),
    }
    for item in model["continuous_covariates"]:
        if item["field"] not in generated_age_fields:
            fields.add(item["field"])
    for item in model["binary_covariates"]:
        if item["field"] not in generated_age_fields:
            fields.add(item["field"])
    for item in model["categorical_covariates"].values():
        if item["field"] not in generated_age_fields:
            fields.add(item["field"])
    for analyte in analytes:
        fields.add(analyte["variable"])
        fasting = config["outcome_validity_rules"][analyte["concept_id"]]["fasting_rule"]
        if fasting["mode"] == "restrict":
            fields.add(fasting["field"])
    if any(not OUTCOME_TERMS.fullmatch(str(field)) for field in fields):
        raise ValueError("Configuration contains an invalid prepared-table field name")
    if ID_FIELD in config["exposure_field_mapping"].values():
        raise ValueError("A participant key cannot be used as an exposure field")
    registry_fields = {row["exposure_field_candidate"] for row in registry}
    if not registry_fields.issubset(set(config["exposure_field_mapping"])):
        raise ValueError("Frozen exposure mapping does not cover all registry source fields")
    return sorted(fields), age_file_fields


def _read_protected_frame(config: dict[str, Any], analytes: list[dict[str, str]], registry: list[dict[str, str]], pyreadstat: Any, pl: Any) -> Any:
    if not DATA.is_file() or not AGE.is_file():
        raise FileNotFoundError("Protected prepared Wave 1 table or age file is missing")
    fields, age_fields = _selected_fields(config, analytes, registry)
    person, _ = pyreadstat.read_dta(str(DATA), usecols=fields, output_format="polars")
    if person.height == 0 or ID_FIELD not in person.columns:
        raise ValueError("Protected prepared frame is empty or lacks its join key")
    if person[ID_FIELD].null_count() or person[ID_FIELD].n_unique() != person.height:
        raise ValueError("Protected prepared-frame person key is missing or non-unique")
    age, _ = pyreadstat.read_dta(str(AGE), usecols=[ID_FIELD, *age_fields], output_format="polars")
    if age[ID_FIELD].null_count() or age[ID_FIELD].n_unique() != age.height:
        raise ValueError("Protected age file person key is missing or non-unique")
    data = person.join(age, on=ID_FIELD, how="left", validate="1:1")
    if data.height != person.height:
        raise ValueError("Age join changed the prepared frame row count")

    numeric_fields = set(fields) - {ID_FIELD, config["design"]["psu_field"], *config["design"]["stratum_fields"]}
    numeric_fields.update(age_fields)
    numeric_exprs = []
    for field in numeric_fields:
        value = pl.col(field).cast(pl.Float64, strict=False)
        numeric_exprs.append(pl.when(value.is_finite()).then(value).otherwise(None).alias(field))
    data = data.with_columns(numeric_exprs)
    age_lower, age_upper = (pl.col(field) for field in age_fields)
    midpoint = pl.when(age_lower.is_not_null() & age_upper.is_not_null()) \
        .then((age_lower + age_upper) / 2.0).otherwise(None)
    data = data.with_columns(midpoint.alias(config["frame"]["age_covariate_field"]))

    frame = config["frame"]
    weight = pl.col(config["design"]["weight_field"])
    data = data.filter(weight.is_not_null() & weight.is_finite() & (weight > 0))
    if data.height == 0:
        raise ValueError("Positive-bloodweight rule selected no observed blood respondents")
    design = config["design"]
    weight = pl.col(design["weight_field"])
    if data.filter(weight.is_null() | ~weight.is_finite() | (weight <= 0)).height:
        raise ValueError("Frozen design frame contains missing, non-finite, or non-positive survey weights")
    if data[design["psu_field"]].null_count():
        raise ValueError("Frozen design frame contains missing PSU values")
    for field in design["stratum_fields"]:
        if data[field].null_count():
            raise ValueError(f"Frozen design frame contains missing values for stratum field {field}")

    data = data.with_columns(
        pl.col(design["psu_field"]).cast(pl.String).alias("__design_psu"),
        pl.col(design["weight_field"]).alias("__design_weight"),
    )
    # Construct approved exposure and covariate terms while still inside the
    # protected local process. Participant IDs are removed before model fitting.
    exprs = []
    for family_id in ("wave1_household_environment_K150", "wave1_heating_route_K90"):
        family_rows = [row for row in registry if row["family_id"] == family_id]
        groups: dict[tuple[str, str], list[dict[str, str]]] = {}
        for row in family_rows:
            groups.setdefault((row["exposure_concept_id"], row["exposure_field_candidate"]), []).append(row)
        for (_concept, candidate_field), rows in groups.items():
            field = config["exposure_field_mapping"][candidate_field]
            values = sorted({_numeric_code(row["exposure_code_candidate"], "exposure code") for row in rows}
                            | {_numeric_code(row["reference_code_candidate"], "reference code") for row in rows})
            contrast_specs = {row["contrast_id"]: row for row in rows}
            for row in contrast_specs.values():
                code = _numeric_code(row["exposure_code_candidate"], "exposure code")
                contrast = row["contrast_id"]
                term = f"exp_{_concept}_{contrast}"
                exprs.append(
                    pl.when(pl.col(field).is_in(values))
                    .then((pl.col(field) == code).cast(pl.Float64))
                    .otherwise(None).alias(term)
                )
    data = data.with_columns(exprs)

    cov_exprs = []
    term_map: dict[str, list[str]] = {"continuous": [], "binary": [], "categorical": []}
    for index, item in enumerate(config["model"]["continuous_covariates"]):
        field, transform = item["field"], item["transform"]
        term = f"cov_cont_{index + 1}"
        value = pl.col(field)
        if transform == "centered_linear":
            value = value - float(item["center"])
        elif transform == "centered_quadratic":
            value = (value - float(item["center"])) ** 2
        cov_exprs.append(value.cast(pl.Float64).alias(term))
        term_map["continuous"].append(term)
    for index, item in enumerate(config["model"]["binary_covariates"]):
        field, pos = item["field"], _numeric_code(item["positive_value"], "binary positive code")
        ref = _numeric_code(item["reference_value"], "binary reference code")
        term = f"cov_binary_{index + 1}"
        cov_exprs.append(
            pl.when(pl.col(field) == pos).then(1.0)
            .when(pl.col(field) == ref).then(0.0).otherwise(None).alias(term)
        )
        term_map["binary"].append(term)
    for index, (label, item) in enumerate(config["model"]["categorical_covariates"].items()):
        field = item["field"]
        levels = [_numeric_code(level, f"categorical level {label}") for level in item["levels"]]
        reference = _numeric_code(item["reference"], f"categorical reference {label}")
        if reference not in levels:
            raise ValueError(f"Reference level for categorical covariate {label} is not declared")
        for level_index, level in enumerate(level for level in levels if level != reference):
            term = f"cov_cat_{index + 1}_{level_index + 1}"
            cov_exprs.append(
                pl.when(pl.col(field).is_in(levels))
                .then((pl.col(field) == level).cast(pl.Float64))
                .otherwise(None).alias(term)
            )
            term_map["categorical"].append(term)
    if cov_exprs:
        data = data.with_columns(cov_exprs)
    data = data.drop([ID_FIELD])
    return data, term_map


def _term_for(row: dict[str, str]) -> str:
    return f"exp_{row['exposure_concept_id']}_{row['contrast_id']}"


def _outcome_expression(config: dict[str, Any], analyte: dict[str, str], pl: Any) -> Any:
    validity = config["outcome_validity_rules"][analyte["concept_id"]]
    raw_outcome = pl.col(analyte["variable"])
    valid_outcome = raw_outcome.is_finite()
    if validity["valid_min"] is not None:
        valid_outcome &= raw_outcome >= float(validity["valid_min"])
    if validity["valid_max"] is not None:
        valid_outcome &= raw_outcome <= float(validity["valid_max"])
    if validity["invalid_codes"]:
        invalid_codes = [_numeric_code(value, f"{analyte['concept_id']}.invalid_codes") for value in validity["invalid_codes"]]
        valid_outcome &= ~raw_outcome.is_in(invalid_codes)
    if config["outcome_transformations"][analyte["concept_id"]] == "identity":
        return pl.when(valid_outcome & (raw_outcome >= 0)).then(raw_outcome).otherwise(None)
    return pl.when(valid_outcome & (raw_outcome > 0)).then(raw_outcome.log()).otherwise(None)


def _age_domain_expr(frame: dict[str, Any], pl: Any) -> Any:
    bound = frame["age_domain_bound"]
    if bound == "full":
        return pl.lit(True)
    field = frame[f"age_{bound}_field"]
    age = pl.col(field)
    return age.is_not_null() & (age >= float(frame["minimum_age"]))


def _reference_outcome_scale(data: Any, config: dict[str, Any], analyte: dict[str, str], pl: Any, np: Any) -> dict[str, Any]:
    """Compute one wave/phenotype scale before applying exposure/covariate complete-case rules."""
    frame = config["frame"]
    domain = _age_domain_expr(frame, pl)
    fasting = config["outcome_validity_rules"][analyte["concept_id"]]["fasting_rule"]
    if fasting["mode"] == "restrict":
        allowed_fasting = [_numeric_code(value, f"{analyte['concept_id']}.fasting eligible code") for value in fasting["eligible_codes"]]
        domain &= pl.col(fasting["field"]).is_in(allowed_fasting)
    outcome = "__reference_outcome"
    reference = data.with_columns(_outcome_expression(config, analyte, pl).alias(outcome)).filter(
        domain & pl.col(outcome).is_not_null()
    )
    if reference.height == 0:
        return {"status": "no_valid_reference_outcome", "n_reference_private": 0}
    weights = np.asarray(reference["__design_weight"].to_list(), dtype=float)
    values = np.asarray(reference[outcome].to_list(), dtype=float)
    if not np.isfinite(weights).all() or (weights <= 0).any() or not np.isfinite(values).all():
        raise ValueError(f"Invalid reference-scale values or weights for {analyte['concept_id']}")
    mean = float(np.average(values, weights=weights))
    sd = float(np.sqrt(np.average(np.square(values - mean), weights=weights)))
    if not math.isfinite(sd) or sd <= 0:
        return {"status": "zero_or_invalid_reference_sd", "n_reference_private": reference.height}
    return {"status": "ready", "mean": mean, "sd": sd, "n_reference_private": reference.height}


def _fit_exposure_group(data: Any, config: dict[str, Any], analyte: dict[str, str], rows: list[dict[str, str]], family_id: str, terms: list[str], term_map: dict[str, list[str]], reference_scale: dict[str, Any], pl: Any, np: Any, svy: Any) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    field_candidate = rows[0]["exposure_field_candidate"]
    field = config["exposure_field_mapping"][field_candidate]
    valid_codes = sorted({_numeric_code(row["exposure_code_candidate"], "exposure code") for row in rows}
                         | {_numeric_code(row["reference_code_candidate"], "reference code") for row in rows})
    domain = _age_domain_expr(config["frame"], pl)
    domain &= pl.col(field).is_in(valid_codes)
    validity = config["outcome_validity_rules"][analyte["concept_id"]]
    fasting = validity["fasting_rule"]
    if fasting["mode"] == "restrict":
        allowed_fasting = [_numeric_code(value, f"{analyte['concept_id']}.fasting eligible code") for value in fasting["eligible_codes"]]
        domain &= pl.col(fasting["field"]).is_in(allowed_fasting)
    if family_id == "wave1_heating_route_K90":
        heating_field = config["exposure_field_mapping"]["i020"]
        domain &= pl.col(heating_field) == 2

    outcome_term = "__outcome_transformed"
    if reference_scale["status"] != "ready":
        return {}, {"n_complete": 0, "n_reference_private": reference_scale.get("n_reference_private", 0),
                    "status": reference_scale["status"]}
    outcome_expr = _outcome_expression(config, analyte, pl)
    model_data = data.with_columns(outcome_expr.alias(outcome_term))

    covariates = term_map["continuous"] + term_map["binary"] + term_map["categorical"]
    xvars = terms + covariates
    complete = domain & pl.col(outcome_term).is_not_null()
    for term in xvars:
        complete &= pl.col(term).is_not_null()
    pair = model_data.filter(complete)
    if pair.height == 0:
        return {}, {"n_complete": 0, "status": "no_complete_cases"}
    weights = np.asarray(pair["__design_weight"].to_list(), dtype=float)
    mean = float(reference_scale["mean"])
    sd = float(reference_scale["sd"])
    if not math.isfinite(sd) or sd <= 0:
        return {}, {"n_complete": pair.height, "status": "zero_or_invalid_weighted_sd"}
    model_data = model_data.with_columns(
        ((pl.col(outcome_term) - mean) / sd).alias("__outcome_z"),
        domain.fill_null(False).alias("__model_domain"),
    )

    design = config["design"]
    stratum_fields = tuple(design["stratum_fields"])
    kwargs: dict[str, Any] = {
        "psu": "__design_psu",
        "wgt": "__design_weight",
        "wr": design["with_replacement"],
        "singleton": svy.Singleton(
            design["singleton_psu_method"],
            domains=design["domain_singleton_method"],
            on_domain_singletons=design["on_domain_singletons"],
        ),
    }
    if stratum_fields:
        kwargs["stratum"] = stratum_fields[0] if len(stratum_fields) == 1 else stratum_fields
    fit_columns = ["__design_psu", "__design_weight", "__outcome_z", "__model_domain", *xvars, *stratum_fields]
    fit_data = model_data.select(list(dict.fromkeys(fit_columns)))
    survey = svy.Sample(data=fit_data, design=svy.Design(**kwargs))
    domain_singleton_count = survey.domain_singletons(where=pl.col("__model_domain")).height
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fit = survey.glm.fit(
            y="__outcome_z", x=xvars, family="gaussian", where=pl.col("__model_domain"),
            method="taylor", drop_nulls=True, alpha=0.05,
        ).to_polars()
    by_term = {str(item.get("term")): item for item in fit.to_dicts()}
    support = pair.group_by(field).agg(
        pl.len().alias("n"), pl.col("__design_psu").n_unique().alias("psus")
    ).sort(field).to_dicts()
    n_psu = int(pair["__design_psu"].n_unique())
    warning_text = " | ".join(str(item.message) for item in caught)
    estimates: dict[str, dict[str, Any]] = {}
    for row, term in zip(rows, terms, strict=True):
        result = by_term.get(term)
        if result is None:
            continue
        estimate = _finite(result.get("estimate"))
        standard_error = _finite(result.get("std_err"))
        ci_lower = _finite(result.get("conf_low"))
        ci_upper = _finite(result.get("conf_high"))
        engine_p_value = _finite(result.get("p_value"))
        design_df = _finite(result.get("df"))
        inference_complete = (
            estimate is not None
            and standard_error is not None and standard_error > 0
            and ci_lower is not None and ci_upper is not None and ci_lower <= ci_upper
            and engine_p_value is not None and 0 <= engine_p_value <= 1
            and design_df is not None and design_df > 0
        )
        estimates[row["contrast_id"]] = {
            "estimate": estimate,
            "standard_error": standard_error,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            # Only complete design-based inference enters multiplicity
            # adjustment. Preserve an engine p-value privately for diagnosis.
            "p_value": engine_p_value if inference_complete else None,
            "engine_p_value_private": engine_p_value,
            "design_df": design_df,
            "weighted_outcome_sd": sd,
            "estimate_scale": "wave_phenotype_target_domain_standard_deviation",
            "estimate_transformed_unit_scale": estimate * sd if estimate is not None else None,
            "se_transformed_unit_scale": standard_error * sd if standard_error is not None else None,
            "fit_status": "success" if inference_complete else "incomplete_inference",
            "n_complete_private": pair.height,
            "n_psu_private": n_psu,
            "support_by_exposure_private": json.dumps(support, separators=(",", ":")),
            "engine_warnings_private": warning_text,
        }
    return estimates, {
        "n_complete": pair.height, "n_psu": n_psu,
        "domain_singleton_strata_private": domain_singleton_count,
        "status": "fit_complete",
    }


def _finite(value: object) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def run_scaleup() -> dict[str, Any]:
    if PRIVATE.resolve() != PRIVATE_ROOT.resolve() or not PRIVATE.resolve().is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Refusing to run outside the configured local protected CHARLS root")
    metadata = audit_scaleup_metadata()
    if metadata.get("status") != "passed_metadata_crosswalk_only":
        raise ValueError("Public-source K150/K90 metadata audit did not pass")

    provenance = require_verified_wave1_frame(PRIVATE, DATA)
    readiness = require_wave1_analysis_readiness(PRIVATE, provenance, PLAN_KEY)
    config = _load_json(CONFIG_PATH)
    analytes = read_analytes()
    registry = _load_registry()
    _validate_configuration(config, analytes, registry)

    # Data-access dependencies are imported only after the source and review gates.
    import numpy as np
    import polars as pl
    import pyreadstat
    import svy
    if getattr(svy, "__version__", None) != EXPECTED_SVY:
        raise RuntimeError(f"Expected svy {EXPECTED_SVY}, found {getattr(svy, '__version__', 'unknown')}")
    data, term_map = _read_protected_frame(config, analytes, registry, pyreadstat, pl)
    reference_scales = {
        analyte["concept_id"]: _reference_outcome_scale(data, config, analyte, pl, np)
        for analyte in analytes
    }

    from adjust_exwas_pvalues import adjust_pvalues
    family_ids = ("wave1_household_environment_K150", "wave1_heating_route_K90")
    results: list[dict[str, Any]] = []
    pair_qa: list[dict[str, Any]] = []
    for family_id in family_ids:
        family = [row for row in registry if row["family_id"] == family_id]
        group_specs: dict[tuple[str, str], list[dict[str, str]]] = {}
        for row in family:
            group_specs.setdefault((row["exposure_concept_id"], row["exposure_field_candidate"]), []).append(row)
        for (concept, field_candidate), exposure_rows in group_specs.items():
            contrast_rows = list({row["contrast_id"]: row for row in exposure_rows}.values())
            terms = [_term_for(row) for row in contrast_rows]
            for analyte in analytes:
                expected_rows = [row for row in exposure_rows if row["phenotype_concept_id"] == analyte["concept_id"]]
                estimates, qa = _fit_exposure_group(
                    data, config, analyte, contrast_rows, family_id, terms, term_map,
                    reference_scales[analyte["concept_id"]], pl, np, svy
                )
                pair_qa.append({
                    "family_id": family_id, "exposure_concept_id": concept,
                    "exposure_field_candidate": field_candidate,
                    "phenotype_concept_id": analyte["concept_id"], **qa,
                })
                estimate_by_contrast = estimates
                for row in expected_rows:
                    estimate = estimate_by_contrast.get(row["contrast_id"])
                    results.append({
                        "hypothesis_id": row["hypothesis_id"],
                        "family_id": family_id,
                        "family_size": int(row["family_size"]),
                        "family_role": row["family_role"],
                        "wave": "2011",
                        "exposure_concept_id": row["exposure_concept_id"],
                        "exposure_variable_candidate": row["exposure_field_candidate"],
                        "contrast_id": row["contrast_id"],
                        "exposure_label": row["exposure_label_candidate"],
                        "reference_label": row["reference_label_candidate"],
                        "route": row["route_candidate"],
                        "phenotype_concept_id": row["phenotype_concept_id"],
                        "phenotype_variable_candidate": row["phenotype_field_candidate"],
                        "phenotype_unit": row["phenotype_unit_candidate"],
                        "outcome_transform": config["outcome_transformations"][row["phenotype_concept_id"]],
                        "model_id": config["model"]["primary_model_id"],
                        **(estimate or {
                            "estimate": None, "standard_error": None, "ci_lower": None,
                            "ci_upper": None, "p_value": None, "q_value_by_batch": None,
                            "p_bonferroni_batch": None,
                            "fit_status": "term_not_returned_by_engine" if qa.get("status") == "fit_complete" else qa.get("status", "not_estimable"),
                            "n_complete_private": qa.get("n_complete"),
                            "n_psu_private": qa.get("n_psu"),
                        }),
                        "release_status": "not_approved",
                    })

    for family_id in family_ids:
        family_rows = [row for row in results if row["family_id"] == family_id]
        expected_size = 150 if family_id.endswith("K150") else 90
        if len(family_rows) != expected_size:
            raise RuntimeError(f"Predeclared family {family_id} is incomplete: expected {expected_size}, found {len(family_rows)}")
        adjusted = adjust_pvalues([_finite(row.get("p_value")) for row in family_rows])
        for row, q_value, bonf in zip(family_rows, adjusted["q_value_by"], adjusted["p_bonferroni"], strict=True):
            row["q_value_by_batch"] = q_value
            row["p_bonferroni_batch"] = bonf
            row["multiplicity_scope"] = "provisional batch diagnostic only; final inference requires the frozen atlas-wide family"

    run_time = datetime.now(timezone.utc).isoformat()
    manifest = {
        "run_utc": run_time,
        "analysis_id": config["plan_id"],
        "status": "protected exploratory scale-up; not approved for public release",
        "source_manifest_id": provenance["source_manifest_id"],
        "prepared_frame_sha256": provenance["prepared_output_sha256"],
        "model_configuration_sha256": readiness["frozen_scaleup_configuration_sha256"],
        "analysis_plan_sha256": analysis_plan_fingerprint(PLAN_KEY),
        "code_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip(),
        "python": sys.version,
        "svy_version": svy.__version__,
        "primary_model_id": config["model"]["primary_model_id"],
        "primary_families": {family_id: sum(row["family_id"] == family_id for row in results) for family_id in family_ids},
        "family_adjustments": "BY and Bonferroni are batch diagnostics only; do not interpret as final atlas-wide error control",
        "participant_data_release": False,
        "public_release_status": "not_approved",
    }
    output_dir = require_private_path(OUTPUT_DIR)
    if not output_dir.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Refusing scale-up output outside protected local storage")
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "wave1_household_environment_scaleup_results_private.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        fields = sorted({key for row in results for key in row})
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    with (output_dir / "wave1_household_environment_scaleup_pair_qa_private.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        fields = sorted({key for row in pair_qa for key in row})
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(pair_qa)
    (output_dir / "wave1_household_environment_scaleup_manifest_private.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {
        "run": "complete",
        "result_rows": len(results),
        "families": manifest["primary_families"],
        "participant_data_release": False,
        "public_release_status": "not_approved",
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the approved protected Wave 1 K150/K90 scale-up.")
    parser.add_argument("--run", action="store_true", required=True,
                        help="explicitly authorize a local protected analysis after all review gates pass")
    parser.parse_args(argv)
    print(json.dumps(run_scaleup(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
