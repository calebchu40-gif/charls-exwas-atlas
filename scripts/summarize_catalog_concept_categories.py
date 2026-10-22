"""Summarize searchable E/P candidate concepts by non-exclusive catalog category."""
from pathlib import Path
import json
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / "site-prototype/dist/catalog.json").read_text(encoding="utf-8"))
rows = []
for role in ("e", "p"):
    buckets = {}
    for item in records:
        roles = {x.strip() for x in str(item.get("epcf", "")).split(",")}
        if role not in roles:
            continue
        category = str(item.get("category", "")).strip() or "Uncategorized"
        code = str(item.get("Variable.Name", "")).strip().lower()
        waves = {x.strip() for x in str(item.get("waves", item.get("Source.Wave", ""))).split(",") if x.strip()}
        concept_ids = {x.strip() for x in str(item.get("Concept.ID.Candidates", "")).split(";") if x.strip()}
        for concept_id in concept_ids:
            b = buckets.setdefault(category, {"concepts": set(), "rows": 0, "wave_codes": set()})
            b["concepts"].add(concept_id)
            b["rows"] += 1
            if code:
                b["wave_codes"].update((wave, code) for wave in waves)
    for category, b in buckets.items():
        rows.append({"role": role, "category": category,
                     "candidate_concept_ids": len(b["concepts"]),
                     "catalog_field_role_category_rows": b["rows"],
                     "distinct_wave_variable_codes": len(b["wave_codes"]),
                     "counts_are_nonexclusive": True})
frame = pd.DataFrame(rows).sort_values(["role", "candidate_concept_ids", "category"], ascending=[True, False, True])
frame.to_csv(ROOT / "audit/candidate_concept_category_counts_v1.csv", index=False, encoding="utf-8-sig")
lines = ["# 候选概念按网站检索类别分布", "",
         "数据来源：当前网站主目录 `site-prototype/dist/catalog.json`。按Concept ID在每个角色和类别中去重；一个Concept ID可出现在多个类别或角色中，因此类别计数是非互斥的，不能相加为总概念数。字段行和波次—变量码也不是独立分析指标或样本量。", "",
         "|角色|检索类别|候选Concept ID数|字段—角色—类别行|不同波次—变量码|", "|---|---|---:|---:|---:|"]
for r in frame.itertuples(index=False):
    lines.append(f"|{r.role}|{r.category}|{r.candidate_concept_ids}|{r.catalog_field_role_category_rows}|{r.distinct_wave_variable_codes}|")
scope = json.loads((ROOT / "audit/directory_scope_counts_v1.json").read_text(encoding="utf-8"))
dual = scope["exposure_concept_ids_including_dual"] + scope["phenotype_concept_ids_including_dual"] - scope["candidate_concept_ids"]
lines += ["", f"总量（去重）以 `audit/directory_scope_counts_v1.json` 为准：E/P候选概念共{scope['candidate_concept_ids']}个（E={scope['exposure_concept_ids_including_dual']}、P={scope['phenotype_concept_ids_including_dual']}，{dual}个兼具角色）。本表为检索分类浏览，不是正式分析变量冻结表。", ""]
(ROOT / "audit/candidate_concept_category_counts_v1.md").write_text("\n".join(lines), encoding="utf-8")
print(frame.to_string(index=False))
