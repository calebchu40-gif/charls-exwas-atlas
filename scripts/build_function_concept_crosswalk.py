"""Map CHARLS functional questionnaire items to reviewable concepts.

Metadata-only: no respondent-level records are opened. Source labels and wave
coverage are preserved; the script does not create scale scores.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


CONCEPTS = [
    ("mobility_run", "跑步/慢跑困难", "physical limitation", r"running|jogging"),
    ("mobility_walk_1km", "步行约1公里困难", "physical limitation", r"walk(?:ing|inf)\s*1\s*km|walk\s*1\s*km"),
    ("mobility_walk_100m", "步行100米困难", "physical limitation", r"walking\s*100\s*metres|walk\s*100\s*metres"),
    ("mobility_chair", "久坐后起身/坐姿困难", "physical limitation", r"getting up from a chair|difficulty with sitting"),
    ("mobility_stairs", "爬楼困难", "physical limitation", r"climbing several flights|difficulty with climbing"),
    ("mobility_bend", "弯腰/下蹲困难", "physical limitation", r"stooping|kneeling|crouching"),
    ("mobility_reach", "伸手/举臂困难", "physical limitation", r"reaching or extending"),
    ("mobility_lift", "提举/搬运困难", "physical limitation", r"lifting or carrying|difficulty with lifting"),
    ("mobility_coin", "拾取小物件困难", "physical limitation", r"picking up (?:a )?small coin|difficulty with picking up"),
    ("adl_dressing", "ADL：穿衣困难", "ADL", r"difficulty with dressing"),
    ("adl_bathing", "ADL：洗澡困难", "ADL", r"difficulty with bathing|bathing or showering"),
    ("adl_eating", "ADL：进食困难", "ADL", r"difficulty with eating"),
    ("adl_bed", "ADL：上下床困难", "ADL", r"getting (?:into or )?out of bed|getting into or out of bed"),
    ("adl_toilet", "ADL：如厕困难", "ADL", r"difficulty with using the toilet|using the toilet"),
    ("adl_continence", "ADL：大小便控制困难", "ADL", r"controlling urination and defecation"),
    ("iadl_chores", "IADL：做家务困难", "IADL", r"household chores|doing household chores"),
    ("iadl_meals", "IADL：准备热餐困难", "IADL", r"preparing hot meals"),
    ("iadl_shopping", "IADL：购买日用品困难", "IADL", r"shopping for groceries|difficulty with shopping"),
    ("iadl_phone", "IADL：打电话困难", "IADL", r"making phone calls"),
    ("iadl_medication", "IADL：服药管理困难", "IADL", r"taking medications"),
    ("iadl_money", "IADL：管理钱财困难", "IADL", r"managing your money|managing assets|managing money"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] / "audit/raw_variable_catalog_v1.csv")
    ap.add_argument("--out-csv", type=Path, default=Path(__file__).resolve().parents[1] / "audit/functional_concept_variable_mapping_v1.csv")
    ap.add_argument("--out-json", type=Path, default=Path(__file__).resolve().parents[1] / "site-prototype/dist/functional_concepts_v1.json")
    args = ap.parse_args()

    source = pd.read_csv(args.catalog, dtype=str, encoding="utf-8-sig").fillna("")
    source = source[source.variable.str.fullmatch(r"(?i)db\d{3}") & source.module.str.contains("health_status_and_functioning", case=False, regex=True)]
    rows: list[dict[str, str]] = []
    concepts_json: list[dict[str, object]] = []
    for cid, label, domain, pattern in CONCEPTS:
        matches = source[source.variable_label.str.contains(pattern, case=False, regex=True, na=False)]
        wave_fields=[]
        for _, row in matches.sort_values(["wave", "variable"]).iterrows():
            item={"wave":row.wave,"code":row.variable,"source_label":row.variable_label,"module":row.module}
            wave_fields.append(item)
            note = "候选映射；题目响应尺度、跳转和缺失规则仍需逐波核验。"
            if row.wave == "2013" and row.variable == "db002":
                note = "变量目录标签有拼写错误‘Walkinf’；2013官方问卷原题确认是步行1公里困难。"
            if row.wave in {"2013", "2015"} and row.variable == "db004":
                note = "变量目录标签简写为‘Difficulty with Sitting’；官方问卷原题确认是久坐后从椅子上站起困难。"
            item["note"] = note
            rows.append({"concept_id":cid,"concept_label":label,"domain":domain,**item,
                "mapping_status":"字段标签候选映射；已抽查逐波官方问卷措辞",
                "harmonization_note":note+" 不据此生成ADL/IADL总分；2020题号重排，需按题意对照。"})
        concepts_json.append({"concept_id":cid,"label":label,"domain":domain,"source_fields":wave_fields,
            "status":"候选题目映射；量表/派生定义待审","caveat":"按官方标签匹配源字段；未生成合成分数，题目措辞和响应尺度需回查逐波问卷。"})
    args.out_csv.parent.mkdir(parents=True,exist_ok=True);args.out_json.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(args.out_csv,index=False,encoding="utf-8-sig")
    args.out_json.write_text(json.dumps(concepts_json,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Mapped {len(rows)} source rows across {len(concepts_json)} candidate concepts; no respondent data read.")


if __name__ == "__main__":
    main()
