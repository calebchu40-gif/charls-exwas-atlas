"""Summarize metadata-only E/P concept co-availability by CHARLS wave."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "audit" / "ep_concept_source_crosswalk_v1.csv"
df = pd.read_csv(source, dtype=str, encoding="utf-8-sig").fillna("")
rows = []
for wave in sorted(df.Wave.unique(), key=int):
    subset = df[df.Wave.eq(wave)]
    exposures = set(subset.loc[subset.Role.str.contains("e"), "Concept.ID"])
    phenotypes = set(subset.loc[subset.Role.str.contains("p"), "Concept.ID"])
    pairs = {(e, p) for e in exposures for p in phenotypes if e != p}
    rows.append({
        "wave": wave,
        "exposure_concepts_with_source_fields": len(exposures),
        "phenotype_concepts_with_source_fields": len(phenotypes),
        "distinct_concept_pairs_with_both_roles": len(pairs),
        "actual_pairwise_complete_n": "not computed",
        "status": "metadata co-availability only; not a sample-size or analysis-eligibility count",
    })

result = pd.DataFrame(rows)
result.to_csv(ROOT / "audit" / "ep_candidate_pair_wave_coverage_v1.csv", index=False, encoding="utf-8-sig")
columns = list(result.columns)
markdown_rows = [
    "| " + " | ".join(columns) + " |",
    "| " + " | ".join("---" for _ in columns) + " |",
]
for values in result.itertuples(index=False, name=None):
    cells = [str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ") for value in values]
    markdown_rows.append("| " + " | ".join(cells) + " |")
notes = (
    "# E/P 候选概念按波次共现范围\n\n"
    "本表统计概念crosswalk中至少有一个已映射源字段的 E/P 概念，并计算同一波次同时有字段的不同概念对；共享 E/P 双角色概念的自配对已排除。此表不包含微观数据值、样本量、可用案例数、问卷路由资格、权重/子样本资格或模型结果，不能解释为可分析pair数。每对是否进入分析仍需核对原题、波次兼容性、目标人群和真实配对样本。\n\n"
    + "\n".join(markdown_rows)
    + "\n"
)
(ROOT / "audit" / "ep_candidate_pair_wave_coverage_v1.md").write_text(notes, encoding="utf-8")
print(result.to_string(index=False))
