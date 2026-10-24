"""Synthetic-only probe of svy 0.35.0; this script never reads CHARLS files."""
from __future__ import annotations

import json
import warnings

import numpy as np
import polars as pl
import svy
from scipy.optimize import root
from scipy.special import expit
from scipy.stats import t as student_t
from svy.errors.singleton_errors import SingletonError


EXPECTED_VERSION = "0.35.0"


def main() -> None:
    version = getattr(svy, "__version__", "unknown")
    if version != EXPECTED_VERSION:
        raise RuntimeError(
            f"This recorded probe is pinned to svy {EXPECTED_VERSION}; found {version}"
        )

    rows = []
    for stratum in range(4):
        for psu in range(2):
            for person in range(12):
                rows.append(
                    {
                        "stratum": stratum,
                        "psu": f"{stratum}-{psu}",
                        "person": person,
                        "weight": 1.0 + (person % 3) * 0.15,
                        "outcome": stratum * 2 + psu + person * 0.25,
                        "exposure": stratum + psu + person % 3,
                        "domain": psu == 0,
                    }
                )
    data = pl.DataFrame(rows)

    # Independent one-stage, with-replacement Taylor variance check for the mean.
    weight = np.asarray(data["weight"].to_list(), dtype=float)
    outcome = np.asarray(data["outcome"].to_list(), dtype=float)
    psu = np.asarray(data["psu"].to_list())
    stratum = np.asarray(data["stratum"].to_list())
    exposure = np.asarray(data["exposure"].to_list(), dtype=float)
    total_weight = weight.sum()
    weighted_mean = float(np.sum(weight * outcome) / total_weight)
    linearized = weight * (outcome - weighted_mean)
    cluster_totals = {}
    for h, p in sorted(set(zip(stratum.tolist(), psu.tolist()))):
        in_psu = (stratum == h) & (psu == p)
        cluster_totals[(h, p)] = float(linearized[in_psu].sum())

    # Independent weighted least-squares Taylor sandwich check for Gaussian GLM.
    model_matrix = np.column_stack((np.ones(len(exposure)), exposure))
    bread = np.linalg.inv(model_matrix.T @ (weight[:, None] * model_matrix))
    beta = bread @ (model_matrix.T @ (weight * outcome))
    residual = outcome - model_matrix @ beta
    cluster_scores = {}
    for h, p in sorted(set(zip(stratum.tolist(), psu.tolist()))):
        in_psu = (stratum == h) & (psu == p)
        cluster_scores[(h, p)] = model_matrix[in_psu].T @ (
            weight[in_psu] * residual[in_psu]
        )

    outputs = {}
    designs = {
        "synthetic_known_strata": svy.Design(
            stratum="stratum", psu="psu", wgt="weight", wr=True
        ),
        "synthetic_stratum_omitted": svy.Design(psu="psu", wgt="weight", wr=True),
    }
    for name, design in designs.items():
        sample = svy.Sample(data=data, design=design)
        mean = sample.estimation.mean(y="outcome").to_polars().to_dicts()[0]
        glm = sample.glm.fit(
            y="outcome", x=["exposure"], family="gaussian"
        ).to_polars().to_dicts()
        exposure_term = next(row for row in glm if row["term"] == "exposure")
        variance_strata = (
            [
                [value for (cluster_stratum, _), value in cluster_totals.items()
                 if cluster_stratum == h]
                for h in sorted(set(stratum.tolist()))
            ]
            if name == "synthetic_known_strata"
            else [list(cluster_totals.values())]
        )
        manual_variance = 0.0
        for psu_totals in variance_strata:
            totals = np.asarray(psu_totals, dtype=float)
            n_psu = len(totals)
            manual_variance += (
                n_psu / (n_psu - 1) * np.sum((totals - totals.mean()) ** 2)
            )
        manual_mean_se = float(np.sqrt(manual_variance) / total_weight)
        if not np.isclose(mean["se"], manual_mean_se, rtol=1e-12, atol=1e-12):
            raise AssertionError(
                f"{name}: svy mean SE {mean['se']} != manual SE {manual_mean_se}"
            )
        score_strata = (
            [
                [score for (score_stratum, _), score in cluster_scores.items()
                 if score_stratum == h]
                for h in sorted(set(stratum.tolist()))
            ]
            if name == "synthetic_known_strata"
            else [list(cluster_scores.values())]
        )
        glm_meat = np.zeros((2, 2))
        for psu_scores in score_strata:
            scores = np.asarray(psu_scores, dtype=float)
            n_psu = len(scores)
            centered = scores - scores.mean(axis=0)
            glm_meat += n_psu / (n_psu - 1) * centered.T @ centered
        manual_glm_covariance = bread @ glm_meat @ bread
        manual_glm_se = float(np.sqrt(manual_glm_covariance[1, 1]))
        manual_glm_beta = float(beta[1])
        manual_glm_p_value = float(
            2 * student_t.sf(
                abs(manual_glm_beta / manual_glm_se), exposure_term["df"]
            )
        )
        if not np.isclose(
            exposure_term["estimate"], manual_glm_beta, rtol=1e-12, atol=1e-12
        ):
            raise AssertionError(
                f"{name}: svy GLM beta {exposure_term['estimate']} != manual beta {manual_glm_beta}"
            )
        if not np.isclose(
            exposure_term["std_err"], manual_glm_se, rtol=1e-12, atol=1e-12
        ):
            raise AssertionError(
                f"{name}: svy GLM SE {exposure_term['std_err']} != manual SE {manual_glm_se}"
            )
        if not np.isclose(
            exposure_term["p_value"], manual_glm_p_value, rtol=1e-10, atol=1e-14
        ):
            raise AssertionError(
                f"{name}: svy GLM p-value {exposure_term['p_value']} "
                f"!= Student-t calculation {manual_glm_p_value}"
            )
        outputs[name] = {
            "mean": mean["est"],
            "mean_se": mean["se"],
            "manual_mean_se": manual_mean_se,
            "mean_se_matches_manual": True,
            "mean_df": mean["df"],
            "glm_exposure_beta": exposure_term["estimate"],
            "manual_glm_exposure_beta": manual_glm_beta,
            "glm_exposure_se": exposure_term["std_err"],
            "manual_glm_exposure_se": manual_glm_se,
            "glm_exposure_se_matches_manual": True,
            "glm_p_value_matches_t_reference": True,
            "glm_exposure_df": exposure_term["df"],
            "n": mean["n"],
        }

    # A domain that has observations in only one of two PSUs per stratum.
    domain_data = data.with_columns(
        pl.when(pl.col("domain"))
        .then(pl.col("outcome"))
        .otherwise(None)
        .alias("outcome"),
        pl.when(pl.col("domain"))
        .then(pl.col("exposure"))
        .otherwise(None)
        .alias("exposure"),
    )
    full_design = svy.Sample(
        data=domain_data,
        design=svy.Design(stratum="stratum", psu="psu", wgt="weight", wr=True),
    )
    domain = svy.col("domain")
    domain_model = full_design.glm.fit(
        y="outcome", x=["exposure"], family="gaussian", where=domain
    ).to_polars().to_dicts()
    domain_exposure = next(row for row in domain_model if row["term"] == "exposure")
    domain_indicator = np.asarray(data["domain"].to_list(), dtype=float)
    domain_weight = weight * domain_indicator
    domain_bread = np.linalg.inv(
        model_matrix.T @ (domain_weight[:, None] * model_matrix)
    )
    domain_beta = domain_bread @ (
        model_matrix.T @ (domain_weight * outcome)
    )
    domain_residual = outcome - model_matrix @ domain_beta
    domain_cluster_scores = {}
    for h, p in sorted(set(zip(stratum.tolist(), psu.tolist()))):
        in_psu = (stratum == h) & (psu == p)
        domain_cluster_scores[(h, p)] = model_matrix[in_psu].T @ (
            domain_weight[in_psu] * domain_residual[in_psu]
        )
    domain_meat = np.zeros((2, 2))
    for h in sorted(set(stratum.tolist())):
        scores = np.asarray(
            [
                value for (score_stratum, _), value
                in domain_cluster_scores.items()
                if score_stratum == h
            ],
            dtype=float,
        )
        centered = scores - scores.mean(axis=0)
        domain_meat += len(scores) / (len(scores) - 1) * centered.T @ centered
    domain_covariance = domain_bread @ domain_meat @ domain_bread
    manual_domain_beta = float(domain_beta[1])
    manual_domain_se = float(np.sqrt(domain_covariance[1, 1]))
    if not np.isclose(
        domain_exposure["estimate"], manual_domain_beta, rtol=1e-12, atol=1e-12
    ):
        raise AssertionError("Domain GLM coefficient does not match manual WLS estimate")
    if not np.isclose(
        domain_exposure["std_err"], manual_domain_se, rtol=1e-12, atol=1e-12
    ):
        raise AssertionError("Domain GLM SE does not match manual full-design sandwich")
    if full_design.domain_singletons(where=domain).height != 4:
        raise AssertionError("The synthetic domain should have one in-domain PSU per stratum")
    try:
        filtered = data.filter(pl.col("domain"))
        svy.Sample(
            data=filtered,
            design=svy.Design(
                stratum="stratum", psu="psu", wgt="weight", wr=True
            ),
        ).glm.fit(y="outcome", x=["exposure"], family="gaussian")
    except SingletonError:
        filtered_domain_raises = True
    else:
        raise AssertionError("Filtering the domain should expose four singleton strata")
    outputs["synthetic_domain_full_design"] = {
        "domain_rows": int(data.filter(pl.col("domain")).height),
        "full_design_rows_retained": full_design.data.height,
        "domain_singleton_strata": full_design.domain_singletons(where=domain).height,
        "glm_exposure_beta": domain_exposure["estimate"],
        "manual_glm_exposure_beta": manual_domain_beta,
        "glm_exposure_se": domain_exposure["std_err"],
        "manual_glm_exposure_se": manual_domain_se,
        "domain_glm_matches_manual": True,
        "glm_df": domain_exposure["df"],
        "prefiltering_raises_singleton_error": filtered_domain_raises,
    }

    # One pairwise-complete loss inside the domain; keep full design rows.
    missing_pair = (pl.col("psu") == "0-0") & (pl.col("person") == 0)
    pair_data = domain_data.with_columns(
        pl.when(missing_pair).then(None).otherwise(pl.col("outcome")).alias("outcome"),
        pl.when(missing_pair).then(None).otherwise(pl.col("exposure")).alias("exposure"),
    )
    pair_sample = svy.Sample(
        data=pair_data,
        design=svy.Design(stratum="stratum", psu="psu", wgt="weight", wr=True),
    )
    pair_model = pair_sample.glm.fit(
        y="outcome", x=["exposure"], family="gaussian", where=domain,
        drop_nulls=True,
    )
    pair_exposure = next(
        row for row in pair_model.to_polars().to_dicts()
        if row["term"] == "exposure"
    )
    pair_complete_mask = ~np.asarray(
        [stratum_value == 0 and psu_value == "0-0" and person == 0
         for stratum_value, psu_value, person in zip(
             stratum.tolist(), psu.tolist(), data["person"].to_list()
         )],
        dtype=bool,
    )
    pair_weight = domain_weight * pair_complete_mask
    pair_bread = np.linalg.inv(
        model_matrix.T @ (pair_weight[:, None] * model_matrix)
    )
    pair_beta = pair_bread @ (model_matrix.T @ (pair_weight * outcome))
    pair_residual = outcome - model_matrix @ pair_beta
    pair_meat = np.zeros((2, 2))
    for h in sorted(set(stratum.tolist())):
        stratum_scores = []
        for p in sorted(set(psu[stratum == h].tolist())):
            in_psu = (stratum == h) & (psu == p)
            stratum_scores.append(
                model_matrix[in_psu].T @ (pair_weight[in_psu] * pair_residual[in_psu])
            )
        scores = np.asarray(stratum_scores, dtype=float)
        centered = scores - scores.mean(axis=0)
        pair_meat += len(scores) / (len(scores) - 1) * centered.T @ centered
    pair_covariance = pair_bread @ pair_meat @ pair_bread
    pair_manual_beta = float(pair_beta[1])
    pair_manual_se = float(np.sqrt(pair_covariance[1, 1]))
    if pair_sample.data.height != data.height or pair_model.fitted.stats.n != 47:
        raise AssertionError("Pairwise complete-case fitting must retain the design rows and count 47 cases")
    if not np.isclose(pair_exposure["estimate"], pair_manual_beta, rtol=1e-12, atol=1e-12):
        raise AssertionError("Pairwise complete-case coefficient differs from manual WLS")
    if not np.isclose(pair_exposure["std_err"], pair_manual_se, rtol=1e-12, atol=1e-12):
        raise AssertionError("Pairwise complete-case SE differs from full-design manual sandwich")
    outputs["synthetic_pairwise_complete_case"] = {
        "pair_complete_n": pair_model.fitted.stats.n,
        "design_rows_retained": pair_sample.data.height,
        "manual_glm_exposure_beta": pair_manual_beta,
        "glm_exposure_beta": pair_exposure["estimate"],
        "manual_glm_exposure_se": pair_manual_se,
        "glm_exposure_se": pair_exposure["std_err"],
        "pairwise_model_matches_full_design_manual": True,
    }

    # Independent design-sandwich check for a synthetic binary-outcome logit.
    # Cluster effects induce within-PSU dependence; the model intentionally
    # omits them, so PSU-level score aggregation is essential for its SE.
    logit_rng = np.random.default_rng(20261024)
    cluster_effects = np.array(
        [-0.45, 0.15, 0.40, -0.20, 0.25, -0.10, 0.35, -0.30, 0.20,
         -0.25, 0.10, 0.30, -0.40, 0.45, 0.05, -0.15, 0.25, -0.35]
    )
    logit_rows = []
    cluster_index = 0
    for h in range(6):
        for p in range(3):
            cluster_effect = cluster_effects[cluster_index]
            cluster_index += 1
            for person in range(12):
                x_value = float(logit_rng.normal())
                weight_value = 0.8 + 0.1 * (person % 4) + 0.05 * p
                probability = float(expit(-0.35 + 0.75 * x_value + cluster_effect))
                logit_rows.append(
                    {
                        "stratum": h,
                        "psu": f"{h}-{p}",
                        "x": x_value,
                        "y": int(logit_rng.random() < probability),
                        "weight": weight_value,
                    }
                )
    logit_data = pl.DataFrame(logit_rows)
    logit_sample = svy.Sample(
        data=logit_data,
        design=svy.Design(stratum="stratum", psu="psu", wgt="weight", wr=True),
    )
    logit_result = logit_sample.glm.fit(
        y="y", x=["x"], family="binomial", link="logit"
    ).to_polars().to_dicts()
    logit_term = next(row for row in logit_result if row["term"] == "x")

    logit_x = np.column_stack(
        (np.ones(len(logit_rows)), np.asarray(logit_data["x"].to_list(), dtype=float))
    )
    logit_y = np.asarray(logit_data["y"].to_list(), dtype=float)
    logit_weight = np.asarray(logit_data["weight"].to_list(), dtype=float)
    logit_stratum = np.asarray(logit_data["stratum"].to_list())
    logit_psu = np.asarray(logit_data["psu"].to_list())

    def logit_score(coef: np.ndarray) -> np.ndarray:
        return logit_x.T @ (
            logit_weight * (logit_y - expit(logit_x @ coef))
        )

    logit_solution = root(logit_score, np.zeros(2), tol=1e-12)
    if not logit_solution.success or np.max(np.abs(logit_score(logit_solution.x))) > 1e-9:
        raise AssertionError(f"Independent synthetic logit solver failed: {logit_solution.message}")
    manual_logit_beta = logit_solution.x
    fitted_probability = expit(logit_x @ manual_logit_beta)
    logit_bread = np.linalg.inv(
        logit_x.T @ ((logit_weight * fitted_probability * (1 - fitted_probability))[:, None] * logit_x)
    )
    logit_meat = np.zeros((2, 2))
    for h in sorted(set(logit_stratum.tolist())):
        psu_scores = []
        for p in sorted(set(logit_psu[logit_stratum == h].tolist())):
            in_psu = (logit_stratum == h) & (logit_psu == p)
            psu_scores.append(
                logit_x[in_psu].T
                @ (logit_weight[in_psu] * (logit_y[in_psu] - fitted_probability[in_psu]))
            )
        scores = np.asarray(psu_scores, dtype=float)
        centered = scores - scores.mean(axis=0)
        logit_meat += len(scores) / (len(scores) - 1) * centered.T @ centered
    logit_covariance = logit_bread @ logit_meat @ logit_bread
    manual_logit_se = float(np.sqrt(logit_covariance[1, 1]))
    manual_logit_p = float(
        2 * student_t.sf(
            abs(manual_logit_beta[1] / manual_logit_se), logit_term["df"]
        )
    )
    for label, observed, expected in (
        ("coefficient", logit_term["estimate"], manual_logit_beta[1]),
        ("PSU-sandwich SE", logit_term["std_err"], manual_logit_se),
        ("Student-t p-value", logit_term["p_value"], manual_logit_p),
    ):
        if not np.isclose(observed, expected, rtol=1e-8, atol=1e-10):
            raise AssertionError(f"Synthetic logistic {label} {observed} != manual {expected}")
    outputs["synthetic_logistic_binary_outcome"] = {
        "n": logit_data.height,
        "strata": 6,
        "psus": 18,
        "exposure_beta": logit_term["estimate"],
        "manual_exposure_beta": float(manual_logit_beta[1]),
        "exposure_se": logit_term["std_err"],
        "manual_exposure_se": manual_logit_se,
        "p_value": logit_term["p_value"],
        "manual_t_p_value": manual_logit_p,
        "df": logit_term["df"],
        "coefficient_se_p_match_manual_score_sandwich": True,
    }

    # Check explicit reference-category coding and both categorical contrasts.
    category_rng = np.random.default_rng(20261025)
    category_effects = np.linspace(-0.35, 0.35, 18)
    category_rows = []
    cluster_index = 0
    category_beta = {"low": 0.0, "medium": 0.45, "high": -0.40}
    for h in range(6):
        for p in range(3):
            cluster_effect = float(category_effects[cluster_index])
            cluster_index += 1
            for person in range(15):
                category = str(category_rng.choice(["low", "medium", "high"], p=[0.40, 0.35, 0.25]))
                probability = float(
                    expit(-0.25 + category_beta[category] + cluster_effect)
                )
                category_rows.append(
                    {
                        "stratum": h,
                        "psu": f"{h}-{p}",
                        "category": category,
                        "y": int(category_rng.random() < probability),
                        "weight": 0.85 + 0.07 * (person % 5) + 0.04 * p,
                    }
                )
    category_data = pl.DataFrame(category_rows)
    category_sample = svy.Sample(
        data=category_data,
        design=svy.Design(stratum="stratum", psu="psu", wgt="weight", wr=True),
    )
    category_result = category_sample.glm.fit(
        y="y",
        x=[svy.Cat("category", ref="low")],
        family="binomial",
        link="logit",
    ).to_polars().to_dicts()
    category_lookup = {row["term"]: row for row in category_result}

    category_values = category_data["category"].to_list()
    category_x = np.column_stack(
        (
            np.ones(len(category_rows)),
            [value == "medium" for value in category_values],
            [value == "high" for value in category_values],
        )
    ).astype(float)
    category_y = np.asarray(category_data["y"].to_list(), dtype=float)
    category_weight = np.asarray(category_data["weight"].to_list(), dtype=float)
    category_stratum = np.asarray(category_data["stratum"].to_list())
    category_psu = np.asarray(category_data["psu"].to_list())

    def category_score(coef: np.ndarray) -> np.ndarray:
        return category_x.T @ (
            category_weight * (category_y - expit(category_x @ coef))
        )

    category_solution = root(category_score, np.zeros(3), tol=1e-12)
    if not category_solution.success or np.max(np.abs(category_score(category_solution.x))) > 1e-9:
        raise AssertionError(
            f"Independent categorical logit solver failed: {category_solution.message}"
        )
    manual_category_beta = category_solution.x
    category_probability = expit(category_x @ manual_category_beta)
    category_bread = np.linalg.inv(
        category_x.T
        @ (
            (category_weight * category_probability * (1 - category_probability))[:, None]
            * category_x
        )
    )
    category_meat = np.zeros((3, 3))
    for h in sorted(set(category_stratum.tolist())):
        psu_scores = []
        for p in sorted(set(category_psu[category_stratum == h].tolist())):
            in_psu = (category_stratum == h) & (category_psu == p)
            psu_scores.append(
                category_x[in_psu].T
                @ (
                    category_weight[in_psu]
                    * (category_y[in_psu] - category_probability[in_psu])
                )
            )
        scores = np.asarray(psu_scores, dtype=float)
        centered = scores - scores.mean(axis=0)
        category_meat += len(scores) / (len(scores) - 1) * centered.T @ centered
    category_covariance = category_bread @ category_meat @ category_bread
    category_se = np.sqrt(np.diag(category_covariance))
    category_checks = []
    for term, index in (("category_medium", 1), ("category_high", 2)):
        model_row = category_lookup[term]
        manual_p_value = float(
            2 * student_t.sf(
                abs(manual_category_beta[index] / category_se[index]), model_row["df"]
            )
        )
        observed = (model_row["estimate"], model_row["std_err"], model_row["p_value"])
        expected = (manual_category_beta[index], category_se[index], manual_p_value)
        if not np.allclose(observed, expected, rtol=1e-8, atol=1e-10):
            raise AssertionError(
                f"Categorical contrast {term}: engine {observed} != manual {expected}"
            )
        category_checks.append(
            {
                "term": term,
                "reference": "low",
                "estimate": model_row["estimate"],
                "manual_estimate": float(manual_category_beta[index]),
                "std_err": model_row["std_err"],
                "manual_std_err": float(category_se[index]),
                "p_value": model_row["p_value"],
                "manual_t_p_value": manual_p_value,
                "df": model_row["df"],
            }
        )
    outputs["synthetic_categorical_logistic_exposure"] = {
        "n": category_data.height,
        "strata": 6,
        "psus": 18,
        "reference": "low",
        "contrasts_match_manual_score_sandwich": category_checks,
    }

    # Perfect separation must be surfaced and cannot produce a releasable fit.
    separated_rows = []
    for h in range(6):
        for p in range(3):
            for person in range(12):
                exposure_value = person % 2
                separated_rows.append(
                    {
                        "stratum": h,
                        "psu": f"{h}-{p}",
                        "exposure": exposure_value,
                        "outcome": exposure_value,
                        "weight": 1.0,
                    }
                )
    separated_data = pl.DataFrame(separated_rows)
    separated_sample = svy.Sample(
        data=separated_data,
        design=svy.Design(stratum="stratum", psu="psu", wgt="weight", wr=True),
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        separated_result = separated_sample.glm.fit(
            y="outcome", x=["exposure"], family="binomial", link="logit"
        ).to_polars().to_dicts()
    separation_warning = any("GLM_SEPARATION" in str(item.message) for item in caught)
    nonfinite_uncertainty = any(
        not np.isfinite(row["std_err"])
        or not np.isfinite(row["p_value"])
        or not np.isfinite(row["conf_low"])
        or not np.isfinite(row["conf_high"])
        for row in separated_result
    )
    if not separation_warning or not nonfinite_uncertainty:
        raise AssertionError(
            "Perfectly separated synthetic logit must warn and return non-finite uncertainty"
        )
    outputs["synthetic_perfect_separation"] = {
        "n": separated_data.height,
        "warning_code_detected": "GLM_SEPARATION" if separation_warning else "missing",
        "nonfinite_uncertainty_detected": nonfinite_uncertainty,
        "release_interpretation": "inestimable; do not publish the finite iteration coefficients",
    }

    # A single contradictory case can leave a finite iteration coefficient but
    # still trigger a term-specific separation warning and non-finite variance.
    near_separated_rows = []
    for h in range(6):
        for p in range(3):
            for person in range(12):
                exposure_value = person % 2
                outcome_value = exposure_value
                if h == 0 and p == 0 and person == 0:
                    outcome_value = 1
                near_separated_rows.append(
                    {
                        "stratum": h,
                        "psu": f"{h}-{p}",
                        "exposure": exposure_value,
                        "outcome": outcome_value,
                        "weight": 1.0,
                    }
                )
    near_separated_data = pl.DataFrame(near_separated_rows)
    near_separated_sample = svy.Sample(
        data=near_separated_data,
        design=svy.Design(stratum="stratum", psu="psu", wgt="weight", wr=True),
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        near_separated_result = near_separated_sample.glm.fit(
            y="outcome", x=["exposure"], family="binomial", link="logit"
        ).to_polars().to_dicts()
    near_separation_warning = any(
        "GLM_SEPARATION" in str(item.message) for item in caught
    )
    near_exposure = next(
        row for row in near_separated_result if row["term"] == "exposure"
    )
    near_intercept = next(
        row for row in near_separated_result if row["term"] == "_intercept_"
    )
    if (
        not near_separation_warning
        or not np.isfinite(near_exposure["estimate"])
        or np.isfinite(near_exposure["std_err"])
        or not np.isfinite(near_intercept["std_err"])
    ):
        raise AssertionError(
            "Near-separated synthetic exposure term must be flagged despite its finite iteration coefficient"
        )
    outputs["synthetic_near_separation"] = {
        "n": near_separated_data.height,
        "contradictory_cases": 1,
        "warning_code_detected": "GLM_SEPARATION" if near_separation_warning else "missing",
        "exposure_iteration_estimate_finite": bool(np.isfinite(near_exposure["estimate"])),
        "exposure_uncertainty_nonfinite": not bool(np.isfinite(near_exposure["std_err"])),
        "intercept_uncertainty_finite": bool(np.isfinite(near_intercept["std_err"])),
        "release_interpretation": "exposure term inestimable; do not release its finite iteration coefficient",
    }

    # A sparse outcome can yield finite-looking results without an engine warning.
    sparse_event_positions = {(0, 0), (1, 2)}
    sparse_event_rows = []
    for h in range(6):
        for p in range(3):
            for person in range(12):
                psu_index = h * 3 + p
                exposure_value = int(person in {0, 1, 4, 5, 8, 9})
                sparse_event_rows.append(
                    {
                        "stratum": h,
                        "psu": f"{h}-{p}",
                        "exposure": exposure_value,
                        "outcome": int((psu_index, person) in sparse_event_positions),
                        "weight": 1.0,
                    }
                )
    sparse_event_data = pl.DataFrame(sparse_event_rows)
    sparse_event_sample = svy.Sample(
        data=sparse_event_data,
        design=svy.Design(stratum="stratum", psu="psu", wgt="weight", wr=True),
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        sparse_event_result = sparse_event_sample.glm.fit(
            y="outcome", x=["exposure"], family="binomial", link="logit"
        ).to_polars().to_dicts()
    sparse_event_warnings = [str(item.message) for item in caught]
    sparse_event_exposure = next(
        row for row in sparse_event_result if row["term"] == "exposure"
    )
    sparse_event_count = int(sparse_event_data["outcome"].sum())
    if (
        sparse_event_count != 2
        or sparse_event_warnings
        or not np.isfinite(sparse_event_exposure["estimate"])
        or not np.isfinite(sparse_event_exposure["std_err"])
    ):
        raise AssertionError(
            "The sparse-event synthetic fixture should return finite output without an engine warning"
        )
    outputs["synthetic_sparse_events_no_warning"] = {
        "n": sparse_event_data.height,
        "event_count": sparse_event_count,
        "warnings": sparse_event_warnings,
        "finite_estimate": bool(np.isfinite(sparse_event_exposure["estimate"])),
        "finite_standard_error": bool(np.isfinite(sparse_event_exposure["std_err"])),
        "estimate": sparse_event_exposure["estimate"],
        "standard_error": sparse_event_exposure["std_err"],
        "p_value": sparse_event_exposure["p_value"],
        "release_interpretation": "finite engine output is not a sparsity safeguard; assess support under prespecified rules",
    }

    print(json.dumps({"svy_version": version, "synthetic_only": True, "outputs": outputs}, indent=2))


if __name__ == "__main__":
    main()
