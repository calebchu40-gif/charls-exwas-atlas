"""Summarise pilot v3 and check overlap with the published 950-result family."""
import json
from collections import Counter
from pathlib import Path

import polars as pl

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
pilot = pl.read_csv(BASE / "private/results/pilot_2011_core_v3.csv", infer_schema_length=5000)
print("rows", pilot.height)
print("status", Counter(pilot["fit_status"].to_list()))

bad = pilot.filter(pl.col("fit_status") != "success")
if bad.height:
    print("failure kinds:", Counter(bad["engine_warnings"].to_list()).most_common(5))
    print("fail exposures:", Counter(bad["exposure_concept_id"].to_list()).most_common(8))
    print("fail phenotypes:", Counter(bad["phenotype_concept_id"].to_list()).most_common(8))

ok = pilot.filter(pl.col("fit_status") == "success")
print("successful pairs:", ok.select(["exposure_concept_id", "phenotype_concept_id"]).unique().height)
print("p<0.05 count:", ok.filter(pl.col("p_value") < 0.05).height,
      "of", ok.height, "=", round(100 * ok.filter(pl.col("p_value") < 0.05).height / ok.height, 1), "%")

# overlap with the published family
published = json.loads((BASE / "code/site-prototype/dist/association_results_v1.json").read_text(encoding="utf-8"))
rows = [row for family in published["families"] for row in family["rows"]]
print("published rows", len(rows), "sample keys", list(rows[0].keys())[:8])
print("published exposures (first 5):", sorted({r.get("exposure_concept_id", "") for r in rows})[:5])
