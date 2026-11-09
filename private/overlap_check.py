"""Find overlap between published 950 rows and pilot v3 (pandas for mixed types)."""
import json
from collections import Counter
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
registry = pd.read_csv(BASE / "private/derived_wave_tables/registry_2011_core_v3.csv")
published = json.loads((BASE / "code/site-prototype/dist/association_results_v1.json").read_text(encoding="utf-8"))
rows = [row for family in published["families"] for row in family["rows"]]
pub = pd.DataFrame(rows)

print("published rows", len(pub), "| waves", Counter(pub["wave"]).most_common(6))
print("estimate types", Counter(pub["estimate_type"]).most_common(4))

pub2011 = pub[pub["wave"] == "2011"].copy()
print("published 2011", len(pub2011))

pilot_phens = set(registry.loc[registry["role"] == "P", "source_variable"])
pilot_expos = set(registry.loc[registry["role"] == "E", "source_variable"])

matched = pub2011[pub2011["phenotype_variable"].isin(pilot_phens) & pub2011["exposure_variable"].isin(pilot_expos)]
print("matched on both:", len(matched))
if len(matched):
    print(matched[["exposure_variable", "phenotype_variable", "estimate_type", "estimate", "p_value"]].head(10).to_string())
