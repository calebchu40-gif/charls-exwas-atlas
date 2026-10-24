"""Synthetic-only probe of svy 0.35.0; this script never reads CHARLS files."""
from __future__ import annotations

import json

import polars as pl
import svy


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
        outputs[name] = {
            "mean": mean["est"],
            "mean_se": mean["se"],
            "mean_df": mean["df"],
            "glm_exposure_beta": exposure_term["estimate"],
            "glm_exposure_se": exposure_term["std_err"],
            "glm_exposure_df": exposure_term["df"],
            "n": mean["n"],
        }

    print(json.dumps({"svy_version": version, "synthetic_only": True, "outputs": outputs}, indent=2))


if __name__ == "__main__":
    main()
