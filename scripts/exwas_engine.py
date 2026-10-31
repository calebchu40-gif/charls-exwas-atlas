#!/usr/bin/env python3
"""Generic, protected exposure-phenotype scan engine for CHARLS.

Design goals
------------
* One engine, many waves: the *variable registry* decides what is scanned,
  the *design specification* decides weights / PSU / domain / covariates.
  Nothing about 2011 water or cooking fuel is hard-coded.
* Fail closed: the supported real-data CLI requires a private approval record
  bound to the exact frame, registry, design, wave, model IDs, and family.
  This engine module should not be called directly for real CHARLS data.
* Reproducible: every result row carries a deterministic ``analysis_id`` and
  the design note, so a later schema-v3 writer can map it without guesswork.
* No microdata is written anywhere by this module. Callers decide where the
  result table goes; the CLI refuses non-private output paths.

This module contains **no CHARLS values**. It is exercised by synthetic tests
in ``tests/test_exwas_engine.py`` and by the CLI ``run_exwas_scan.py``.

Survey estimation uses ``svy`` (pinned in requirements-survey-audit.txt) with
a with-replacement, unstratified Taylor approximation unless the design
specification provides an official stratum column. The design note written to
every row states exactly which design was used.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import polars as pl
import svy

EXPECTED_SVY = "0.35.0"
ROLES = {"E", "P"}
KINDS = {"continuous", "binary", "categorical"}
FAMILIES = {"gaussian", "binomial"}

REQUIRED_REGISTRY_FIELDS = ("concept_id", "role", "wave", "variable", "kind")
OPTIONAL_REGISTRY_FIELDS = (
    "label", "unit", "transform", "valid_min", "valid_max",
    "levels", "reference", "family",
)

RESULT_COLUMNS = (
    "analysis_id", "wave", "model_id", "multiple_testing_family",
    "exposure_concept_id", "exposure_variable", "exposure_term", "exposure_contrast",
    "phenotype_concept_id", "phenotype_variable", "phenotype_family",
    "estimate_type", "estimate", "standard_error", "ci_lower", "ci_upper",
    "p_value", "design_df", "n_model", "n_psu", "kish_effective_n",
    "outcome_mean", "outcome_sd", "exposure_scale", "fit_status",
    "engine_warnings", "design_note",
)


class RegistryError(ValueError):
    """The variable registry is malformed or internally inconsistent."""


class DesignError(ValueError):
    """The design specification is missing a required, verifiable element."""


@dataclass(frozen=True)
class VariableSpec:
    concept_id: str
    role: str
    label: str
    wave: str
    variable: str
    kind: str
    unit: str = ""
    transform: str = ""
    valid_min: float | None = None
    valid_max: float | None = None
    levels: tuple[str, ...] = ()
    reference: str = ""
    family: str = "gaussian"

    def numeric_ok(self) -> bool:
        return self.kind in {"continuous", "binary"}


DEFAULT_VARIANCE_LIMITATION = (
    "official CHARLS variance strata and replicate weights are not released; "
    "the county-level systematic PPS implicit stratification is not reproduced"
)


@dataclass
class DesignSpec:
    weight: str
    psu: str
    strata: str | None = None
    age_field: str | None = None
    age_min: int | None = None
    covariate_sets: dict[str, list[str]] = field(default_factory=dict)
    scale_outcome: bool = True
    variance_limitations: str = ""

    def model_covariates(self, model_id: str) -> list[str]:
        return list(self.covariate_sets.get(model_id, []))

    def note(self) -> str:
        """Describe the design used, including an explicit limitation label.

        The scale-up executor requires every frozen configuration to state the
        variance method *and* its limitation. The generic engine mirrors that
        rule: when no official stratum column is supplied, the note carries a
        ``limitation:`` label so a reader cannot mistake the approximation for
        a full design-based variance.
        """
        if self.strata:
            return (f"{self.weight} weight; {self.psu} PSU; official stratum {self.strata}; "
                    "Taylor linearisation")
        limitation = (self.variance_limitations or "").strip() or DEFAULT_VARIANCE_LIMITATION
        return (f"{self.weight} weight; {self.psu} PSU; unstratified with-replacement "
                f"Taylor approximation; not full design variance; limitation: {limitation}")


def _to_float(value: str | None) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def load_registry(path: Path) -> list[VariableSpec]:
    """Read and validate a variable registry CSV."""
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = [name for name in REQUIRED_REGISTRY_FIELDS if name not in (reader.fieldnames or [])]
        if missing:
            raise RegistryError("registry is missing fields: " + ", ".join(missing))
        specs: list[VariableSpec] = []
        seen: set[tuple[str, str, str]] = set()
        for line, row in enumerate(reader, start=2):
            concept = (row.get("concept_id") or "").strip()
            role = (row.get("role") or "").strip().upper()
            wave = (row.get("wave") or "").strip()
            variable = (row.get("variable") or "").strip()
            kind = (row.get("kind") or "").strip().lower()
            if not concept or not wave or not variable:
                raise RegistryError(f"registry row {line}: concept_id, wave and variable are required")
            if role not in ROLES:
                raise RegistryError(f"registry row {line}: role must be E or P")
            if kind not in KINDS:
                raise RegistryError(f"registry row {line}: kind must be one of {sorted(KINDS)}")
            key = (concept, wave, variable)
            if key in seen:
                raise RegistryError(f"registry row {line}: duplicate concept/wave/variable {key}")
            seen.add(key)
            levels = tuple(part.strip() for part in (row.get("levels") or "").split("|") if part.strip())
            family = (row.get("family") or "gaussian").strip().lower() or "gaussian"
            if family not in FAMILIES:
                raise RegistryError(f"registry row {line}: family must be one of {sorted(FAMILIES)}")
            if kind == "categorical" and len(levels) < 2:
                raise RegistryError(f"registry row {line}: categorical variables need >=2 levels")
            if kind == "categorical" and (row.get("reference") or "").strip() not in levels:
                raise RegistryError(f"registry row {line}: categorical reference must be one of levels")
            valid_min = _to_float(row.get("valid_min"))
            valid_max = _to_float(row.get("valid_max"))
            if valid_min is not None and valid_max is not None and valid_min > valid_max:
                raise RegistryError(f"registry row {line}: valid_min exceeds valid_max")
            specs.append(VariableSpec(
                concept_id=concept, role=role, label=(row.get("label") or "").strip(),
                wave=wave, variable=variable, kind=kind, unit=(row.get("unit") or "").strip(),
                transform=(row.get("transform") or "").strip().lower(),
                valid_min=valid_min, valid_max=valid_max,
                levels=levels, reference=(row.get("reference") or "").strip(), family=family,
            ))
    if not specs:
        raise RegistryError("registry contains no variables")
    return specs


def load_design(path: Path) -> DesignSpec:
    """Read and validate a design specification JSON."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DesignError("design specification must be a JSON object")
    weight = str(payload.get("weight", "")).strip()
    psu = str(payload.get("psu", "")).strip()
    if not weight or not psu:
        raise DesignError("design specification requires explicit 'weight' and 'psu' fields")
    if weight == psu:
        raise DesignError("weight and PSU must be different columns")
    covariate_sets = payload.get("covariate_sets") or {}
    if not isinstance(covariate_sets, dict) or not all(
            isinstance(k, str) and isinstance(v, list) for k, v in covariate_sets.items()):
        raise DesignError("covariate_sets must map model_id to a list of column names")
    age_min = payload.get("age_min")
    return DesignSpec(
        weight=weight, psu=psu,
        strata=(str(payload["strata"]).strip() or None) if payload.get("strata") else None,
        age_field=(str(payload["age_field"]).strip() or None) if payload.get("age_field") else None,
        age_min=int(age_min) if age_min is not None else None,
        covariate_sets={k: [str(x) for x in v] for k, v in covariate_sets.items()},
        scale_outcome=bool(payload.get("scale_outcome", True)),
        variance_limitations=str(payload.get("variance_limitations", "") or "").strip(),
    )


def _numeric(column: str) -> pl.Expr:
    return pl.col(column).cast(pl.Float64, strict=False)


def _valid_expr(spec: VariableSpec) -> pl.Expr:
    expr = _numeric(spec.variable).is_not_null()
    if spec.valid_min is not None:
        expr = expr & (_numeric(spec.variable) >= spec.valid_min)
    if spec.valid_max is not None:
        expr = expr & (_numeric(spec.variable) <= spec.valid_max)
    return expr


def prepare_frame(frame: pl.DataFrame, design: DesignSpec,
                  specs: Sequence[VariableSpec]) -> pl.DataFrame:
    """Validate required columns and build the analysis weight / PSU columns."""
    required = {design.weight, design.psu}
    if design.strata:
        required.add(design.strata)
    if design.age_field:
        required.add(design.age_field)
    for spec in specs:
        required.add(spec.variable)
    for columns in design.covariate_sets.values():
        required.update(columns)
    missing = sorted(name for name in required if name not in frame.columns)
    if missing:
        raise DesignError("frame is missing required columns: " + ", ".join(missing))

    weight = _numeric(design.weight)
    frame = frame.with_columns(
        pl.when(weight.is_not_null() & (weight > 0)).then(weight).otherwise(0.0).alias("_analysis_weight"),
        pl.col(design.psu).cast(pl.String).alias("_psu"),
    )
    if design.strata:
        frame = frame.with_columns(pl.col(design.strata).cast(pl.String).alias("_stratum"))
    if frame.filter(pl.col("_analysis_weight") > 0).height == 0:
        raise DesignError("no record has a positive analysis weight; refusing to fit")
    positive_weight = pl.col("_analysis_weight") > 0
    if frame.filter(positive_weight & pl.col("_psu").is_null()).height:
        raise DesignError("positive-weight records have missing PSU values; refusing to fit")
    if design.strata and frame.filter(positive_weight & pl.col("_stratum").is_null()).height:
        raise DesignError("positive-weight records have missing stratum values; refusing to fit")
    return frame


def enumerate_pairs(registry: Sequence[VariableSpec], wave: str) -> list[tuple[VariableSpec, VariableSpec]]:
    exposures = [s for s in registry if s.wave == wave and s.role == "E"]
    phenotypes = [s for s in registry if s.wave == wave and s.role == "P"]
    pairs = []
    for e in exposures:
        for p in phenotypes:
            if e.concept_id == p.concept_id:
                continue  # a concept is never regressed on itself
            pairs.append((e, p))
    return pairs


def _weighted_mean_sd(values: np.ndarray, weights: np.ndarray) -> tuple[float, float]:
    total = float(weights.sum())
    if total <= 0:
        raise ValueError("non-positive weight total")
    mean = float(np.average(values, weights=weights))
    variance = float(np.average(np.square(values - mean), weights=weights))
    return mean, math.sqrt(max(variance, 0.0))


def _exposure_terms(frame: pl.DataFrame, spec: VariableSpec) -> tuple[list[str], dict[str, str]]:
    """Return (design columns, term->contrast label) for one exposure spec."""
    column = spec.variable
    if spec.kind == "continuous":
        return ([column], {column: f"{spec.label or column}: per unit"})
    if spec.kind == "binary":
        return ([column], {column: f"{spec.label or column}: 1 vs 0"})
    terms, labels = [], {}
    numeric = _numeric(column).cast(pl.String)
    for level in spec.levels:
        if level == spec.reference:
            continue
        name = f"__{spec.concept_id}_lvl{level}"
        frame.with_columns((numeric == level).cast(pl.Float64).alias(name))
        terms.append(name)
        labels[name] = f"{spec.label or column}: {level} vs {spec.reference}"
    return terms, labels


def _level_expr(column: str, level: str) -> pl.Expr:
    """Compare a raw column to a registry level, numerically when possible."""
    try:
        return _numeric(column) == float(level)
    except (TypeError, ValueError):
        return pl.col(column).cast(pl.String) == level


def _apply_exposure_columns(frame: pl.DataFrame, spec: VariableSpec) -> tuple[pl.DataFrame, list[str], dict[str, str]]:
    if spec.kind == "categorical":
        terms, labels = [], {}
        new_columns = []
        for level in spec.levels:
            if level == spec.reference:
                continue
            name = f"__{spec.concept_id}_lvl{level}"
            new_columns.append(_level_expr(spec.variable, level).cast(pl.Float64).alias(name))
            terms.append(name)
            labels[name] = f"{spec.label or spec.variable}: {level} vs {spec.reference}"
        return frame.with_columns(new_columns), terms, labels
    terms, labels = _exposure_terms(frame, spec)
    return frame, terms, labels


def _domain_expr(design: DesignSpec, extra: Iterable[pl.Expr]) -> pl.Expr:
    expr = pl.col("_analysis_weight") > 0
    if design.age_field and design.age_min is not None:
        expr = expr & (_numeric(design.age_field) >= design.age_min)
    for item in extra:
        expr = expr & item
    return expr


def _analysis_id(*parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:16]
    return "exwas-" + digest


def fit_pair(frame: pl.DataFrame, exposure: VariableSpec, phenotype: VariableSpec,
             design: DesignSpec, model_id: str) -> list[dict[str, Any]]:
    """Fit one exposure-phenotype pair under one model and return long rows."""
    frame, terms, labels = _apply_exposure_columns(frame, exposure)
    covariates = design.model_covariates(model_id)
    outcome = phenotype.variable

    extra = [_valid_expr(exposure), _valid_expr(phenotype)]
    extra += [_numeric(name).is_not_null() for name in covariates]
    domain = _domain_expr(design, extra)

    pair = frame.filter(domain)
    if pair.height == 0:
        return [_blocked_row(exposure, phenotype, design, model_id, terms, labels,
                             "no_eligible_records", "domain selects no complete cases")]
    psus = pair["_psu"].n_unique()
    if psus < 2:
        return [_blocked_row(exposure, phenotype, design, model_id, terms, labels,
                             "insufficient_psu", "fewer than two PSUs in the pair-specific domain")]

    outcome_values = pair[outcome].cast(pl.Float64, strict=False).to_numpy()
    weights = pair["_analysis_weight"].to_numpy()
    if phenotype.family == "binomial":
        unique = set(np.unique(outcome_values[~np.isnan(outcome_values)]).tolist())
        if not unique.issubset({0.0, 1.0}):
            return [_blocked_row(exposure, phenotype, design, model_id, terms, labels,
                                 "invalid_binary_outcome", f"outcome values {sorted(unique)[:5]}")]
        outcome_column = "__outcome"
        scaled = pair.with_columns(pl.Series("__outcome", outcome_values).cast(pl.Float64))
        mean = float(np.average(outcome_values, weights=weights))
        sd = float(np.sqrt(np.average(np.square(outcome_values - mean), weights=weights)))
        family, estimate_type = "binomial", "odds_ratio"
    else:
        mean, sd = _weighted_mean_sd(outcome_values, weights)
        if design.scale_outcome:
            if not math.isfinite(sd) or sd <= 0:
                return [_blocked_row(exposure, phenotype, design, model_id, terms, labels,
                                     "zero_outcome_variance", f"weighted SD={sd}")]
            outcome_column = "__outcome_z"
            scaled = pair.with_columns(
                ((pl.col(outcome).cast(pl.Float64, strict=False) - mean) / sd).alias(outcome_column))
        else:
            outcome_column = "__outcome"
            scaled = pair.with_columns(pl.col(outcome).cast(pl.Float64, strict=False).alias(outcome_column))
        family, estimate_type = "gaussian", "beta"

    xvars = list(terms) + covariates
    exposure_scale = "raw"
    if exposure.kind == "continuous" and exposure.transform == "z":
        exposure_values = pair[exposure.variable].cast(pl.Float64, strict=False).to_numpy()
        try:
            exposure_mean, exposure_sd = _weighted_mean_sd(exposure_values, weights)
        except ValueError:
            return [_blocked_row(exposure, phenotype, design, model_id, terms, labels,
                                 "nonpositive_weight_total", "analysis weights sum to zero")]
        if not math.isfinite(exposure_sd) or exposure_sd <= 0:
            return [_blocked_row(exposure, phenotype, design, model_id, terms, labels,
                                 "zero_exposure_variance", f"weighted SD={exposure_sd}")]
        scaled = scaled.with_columns(
            ((pl.col(exposure.variable).cast(pl.Float64, strict=False) - exposure_mean) / exposure_sd)
            .alias(exposure.variable))
        exposure_scale = "weighted_z"
    sample = svy.Sample(
        data=scaled,
        design=svy.Design(psu="_psu", wgt="_analysis_weight",
                          stratum="_stratum" if design.strata else None,
                          wr=True),
    )
    import warnings
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = sample.glm.fit(
            y=outcome_column, x=xvars, family=family,
            where=domain, drop_nulls=True, alpha=0.05,
        ).to_polars()
    warnings_text = " | ".join(str(item.message) for item in caught)
    table = {row["term"]: row for row in result.to_dicts()}
    psus = pair["_psu"].n_unique()
    rows: list[dict[str, Any]] = []
    for term in terms:
        record = table.get(term)
        if record is None:
            rows.append(_blocked_row(exposure, phenotype, design, model_id, [term], labels,
                                     "engine_omitted_term", "exposure term missing from engine output"))
            continue
        estimate = _to_float(str(record.get("estimate")))
        se = _to_float(str(record.get("std_err")))
        low = _to_float(str(record.get("conf_low")))
        high = _to_float(str(record.get("conf_high")))
        p_value = _to_float(str(record.get("p_value")))
        df = _to_float(str(record.get("df")))
        status = "success" if all(v is not None for v in (estimate, se, low, high, p_value, df)) else "numerically_unavailable"
        if family == "binomial" and status == "success":
            # Coefficient and standard error are on the log-odds scale. Report
            # OR-scale limits and a delta-method OR-scale standard error.
            try:
                odds_ratio = math.exp(estimate)
                low_or, high_or = math.exp(low), math.exp(high)
                if (not all(math.isfinite(v) for v in (odds_ratio, low_or, high_or))
                        or odds_ratio <= 0 or low_or <= 0 or high_or <= 0):
                    raise OverflowError("non-finite or underflowed odds-ratio scale")
                estimate, se, low, high = (odds_ratio, odds_ratio * se, low_or, high_or)
            except OverflowError:
                status = "numerically_unavailable"
                estimate = se = low = high = None
                p_value = df = None
        rows.append({
            "analysis_id": _analysis_id(exposure.wave, model_id, exposure.concept_id,
                                        phenotype.concept_id, term, phenotype.variable),
            "wave": exposure.wave,
            "model_id": model_id,
            "multiple_testing_family": "",
            "exposure_concept_id": exposure.concept_id,
            "exposure_variable": exposure.variable,
            "exposure_term": term,
            "exposure_contrast": labels.get(term, term),
            "phenotype_concept_id": phenotype.concept_id,
            "phenotype_variable": phenotype.variable,
            "phenotype_family": family,
            "estimate_type": estimate_type,
            "estimate": _fmt(estimate), "standard_error": _fmt(se),
            "ci_lower": _fmt(low), "ci_upper": _fmt(high), "p_value": _fmt(p_value),
            "design_df": _fmt(df), "n_model": pair.height, "n_psu": psus,
            "kish_effective_n": _fmt(_kish(pair)),
            "outcome_mean": _fmt(mean), "outcome_sd": _fmt(sd),
            "exposure_scale": exposure_scale,
            "fit_status": status,
            "engine_warnings": warnings_text,
            "design_note": design.note(),
        })
    return rows


def _kish(frame: pl.DataFrame) -> float | None:
    weights = frame["_analysis_weight"].to_numpy().astype(float)
    denominator = float(np.square(weights).sum())
    if denominator <= 0:
        return None
    return float(weights.sum() ** 2 / denominator)


def _fmt(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return ""
    return f"{value:.10g}"


def _blocked_row(exposure: VariableSpec, phenotype: VariableSpec, design: DesignSpec,
                 model_id: str, terms: Sequence[str], labels: dict[str, str],
                 status: str, note: str) -> dict[str, Any]:
    term = terms[0] if terms else exposure.variable
    return {
        "analysis_id": _analysis_id(exposure.wave, model_id, exposure.concept_id,
                                    phenotype.concept_id, term, phenotype.variable),
        "wave": exposure.wave, "model_id": model_id, "multiple_testing_family": "",
        "exposure_concept_id": exposure.concept_id, "exposure_variable": exposure.variable,
        "exposure_term": term, "exposure_contrast": labels.get(term, term),
        "phenotype_concept_id": phenotype.concept_id, "phenotype_variable": phenotype.variable,
        "phenotype_family": phenotype.family, "estimate_type": ("odds_ratio" if phenotype.family == "binomial" else "beta"),
        "estimate": "", "standard_error": "", "ci_lower": "", "ci_upper": "", "p_value": "",
        "design_df": "", "n_model": "", "n_psu": "", "kish_effective_n": "",
        "outcome_mean": "", "outcome_sd": "", "exposure_scale": "",
        "fit_status": status, "engine_warnings": note, "design_note": design.note(),
    }


def assign_families(rows: list[dict[str, Any]], family_prefix: str) -> None:
    """Tag every row with its frozen multiple-testing family and recompute q-values.

    The family is defined *after* the full hypothesis list is known but
    *before* any q-value is read: it covers every predeclared row for one
    wave and model, including non-estimable rows (``None`` p-values still
    count toward K).
    """
    from adjust_exwas_pvalues import adjust_pvalues  # local import: repo helper

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["wave"], row["model_id"]), []).append(row)
    for (wave, model_id), members in grouped.items():
        family = f"{family_prefix}.{wave}.{model_id}"
        p_values = [_to_float(row["p_value"]) if row["fit_status"] == "success" else None
                    for row in members]
        adjusted = adjust_pvalues(p_values)
        for row, bonferroni, q_value in zip(members, adjusted["p_bonferroni"], adjusted["q_value_by"]):
            row["multiple_testing_family"] = f"{family};K={len(members)}"
            row["p_bonferroni"] = _fmt(bonferroni)
            row["q_value_by"] = _fmt(q_value)


def scan(frame: pl.DataFrame, registry: Sequence[VariableSpec], design: DesignSpec,
         wave: str, models: Sequence[str], family_prefix: str = "charls_exwas") -> list[dict[str, Any]]:
    """Run every registered pair for one wave and return the long result rows."""
    if not models or len(set(models)) != len(models):
        raise DesignError("models must be a nonempty list of unique model IDs")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", family_prefix):
        raise DesignError("family_prefix contains unsupported characters")
    unknown_models = sorted(set(models) - set(design.covariate_sets))
    if unknown_models:
        raise DesignError("model IDs lack explicit covariate sets: " + ", ".join(unknown_models))
    frame = prepare_frame(frame, design, registry)
    pairs = enumerate_pairs(registry, wave)
    if not pairs:
        raise DesignError("registry has no exposure-phenotype pairs for the requested wave")
    rows: list[dict[str, Any]] = []
    for exposure, phenotype in pairs:
        for model_id in models:
            try:
                rows.extend(fit_pair(frame, exposure, phenotype, design, model_id))
            except Exception as exc:  # noqa: BLE001 - a failed fit must become a row, not a crash
                rows.append(_blocked_row(
                    exposure, phenotype, design, model_id, [], {},
                    "numerically_unavailable",
                    f"model fit raised {type(exc).__name__}: {exc}"[:400]))
    assign_families(rows, family_prefix)
    return rows


def write_rows(rows: Sequence[dict[str, Any]], path: Path) -> None:
    columns = list(RESULT_COLUMNS) + ["p_bonferroni", "q_value_by"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in columns})
