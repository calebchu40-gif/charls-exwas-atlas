"""Synthetic-only probe of svy 0.35.0; this script never reads CHARLS files."""
from __future__ import annotations

import json

import numpy as np
import polars as pl
import svy
from scipy.stats import t as student_t


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
                        "weight": 1.0 + (person % 3) * 0.15,
                        "outcome": stratum * 2 + psu + person * 0.25,
                        "exposure": stratum + psu + person % 3,
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

    print(json.dumps({"svy_version": version, "synthetic_only": True, "outputs": outputs}, indent=2))


if __name__ == "__main__":
    main()
