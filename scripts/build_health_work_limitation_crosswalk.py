"""Build wave-specific CHARLS mappings for health-related work limitations.

Uses public variable metadata, official codebooks and questionnaires only.
No respondent-level data are opened.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = pd.read_csv(ROOT / "audit/raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
CONCEPTS = {
    "work_specific_health_limitation": {"label": "因健康/残疾难以持续完成特定工作", "domain": "work-related functional limitation", "caveat": "2015题询问特定工作是否做不了或无法长时间做；DB036_W3=Yes后跳至DB038_W3_1，DB037_W3不适用。此条仅在2015发现，不能与总体工作能力题互换。", "fields": [("2015", "db036_w3", "1=Yes; 2=No; 3=Too old to do the work", "sources_official/CHARLS_2015_Codebook_extracted.txt", "specific work cannot be done or cannot be sustained because of disability/health; DB036_W3 route")]},
    "housework_specific_health_limitation": {"label": "因健康/残疾难以持续完成特定家务", "domain": "work-related functional limitation", "caveat": "2015题询问特定家务是否做不了或无法长时间做；仅在DB036_W3为No/Too old时提问；DB037_W3=Yes后跳至DB038_W3_2。结构性跳题不能作No。", "fields": [("2015", "db037_w3", "1=Yes; 2=No; 3=Too old to do the housework", "sources_official/CHARLS_2015_Codebook_extracted.txt", "specific housework cannot be done or cannot be sustained because of disability/health; conditional DB036_W3 route")]},
    "work_capacity_health_limitation": {"label": "因健康/残疾导致的工作能力受限", "domain": "work-related functional limitation", "caveat": "跨波问法与量表不同：2015是二分类且仅向特定工作受限者追问完全不能工作；2018/2020为三级自评。保留逐波原值，不直接合并或当作就业状态。2020需同时审查代理回答字段DB045。", "fields": [("2015", "db038_w3_1", "1=Yes; 2=No", "sources_official/CHARLS_2015_Codebook_extracted.txt", "completely unable to work because of disability/health; asked after DB036_W3=Yes"), ("2018", "db036_w4", "1=I can't work at all; 2=I can't work for long time; 3=I have no problem working", "sources_official/CHARLS_2018_Codebook_extracted.txt", "self-rated work limitation; option 1 skips DB037_W4"), ("2020", "db043", "1=I can't work at all; 2=I can't work long hours; 3=I don't have any problem", "sources_official/CHARLS_2020_Codebook_extracted.txt", "self-rated work limitation; response assistance/proxy recorded separately in DB045")]},
    "housework_capacity_health_limitation": {"label": "因健康/残疾导致的家务能力受限", "domain": "work-related functional limitation", "caveat": "跨波问法与量表不同：2015是二分类且仅向特定家务受限者追问完全不能做家务；2018/2020为三级自评。保留逐波原值；2018工作能力题的完全不能选项会跳过家务题。2020需同时审查代理回答字段DB045。", "fields": [("2015", "db038_w3_2", "1=Yes; 2=No", "sources_official/CHARLS_2015_Codebook_extracted.txt", "completely unable to do any housework because of disability/health; asked after DB037_W3=Yes"), ("2018", "db037_w4", "1=I can't do at all; 2=I can't do for long time; 3=I have no problem", "sources_official/CHARLS_2018_Codebook_extracted.txt", "self-rated housework limitation; structural skip when DB036_W4 option 1"), ("2020", "db044", "1=I can't do housework at all; 2=I can't do housework for an extended period; 3=I don't have any problem", "sources_official/CHARLS_2020_Codebook_extracted.txt", "self-rated housework limitation; response assistance/proxy recorded separately in DB045")]},
}

rows=[]
for cid, concept in CONCEPTS.items():
    for wave, code, labels, doc, semantics in concept["fields"]:
        source = RAW[(RAW.wave==wave) & (RAW.variable.str.lower()==code.lower())]
        if source.empty: raise ValueError(f"Missing source field {wave} {code}")
        src=source.iloc[0]
        rows.append({"concept_id":cid,"concept_label":concept["label"],"domain":concept["domain"],"wave":wave,"code":code,"source_label":src.variable_label,"module":src.module,"value_labels":labels,"value_label_status":"matched to wave-specific official codebook response categories","value_label_source":doc,"value_semantics":semantics,"mapping_status":"official questionnaire/codebook mapping; candidate phenotype; routing and harmonization remain wave-specific","note":concept["caveat"]})

pd.DataFrame(rows).to_csv(ROOT/"audit/health_work_limitation_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
items=[]
for cid, concept in CONCEPTS.items():
    fields=[{k:r[k] for k in ("wave","code","source_label","module","value_labels","value_label_status","value_label_source","value_semantics","mapping_status","note")} for r in rows if r["concept_id"]==cid]
    items.append({"concept_id":cid,"label":concept["label"],"domain":concept["domain"],"source_fields":fields,"status":"候选表型；需按波次和问卷路由解释","caveat":concept["caveat"]})
(ROOT/"site-prototype/dist/health_work_limitations_v1.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
lines=["# 因健康/残疾导致的工作与家务能力受限：编码映射审计 v1","","日期：2026-10-16。仅使用CHARLS官方问卷、代码本和公开变量元数据；未读取受访者记录。",f"","整理出{len(CONCEPTS)}个候选概念、{len(rows)}条波次—字段映射。", "", "## 定义与波次限制", "", "工作/家务能力限制与ADL/IADL日常生活困难并非同一构念。2015字段包含跳题：特定工作/家务受限题触发后续‘完全不能’追问；未进入追问的空值是结构性跳题，不能视为否。2018和2020使用三级自评类别，保留原始等级，不折叠成跨波二元状态。2020的代理回答情况由DB045另记，需在模型资格审查时处理。", "", "具体字段、值标签、原始变量标签和来源列于`audit/health_work_limitation_crosswalk_v1.csv`。页面JSON为`site-prototype/dist/health_work_limitations_v1.json`。", "", "## 官方证据", "", "- 2015官方问卷Health Status and Functioning：DB036_W3、DB037_W3、DB038_W3_1/2的题干与跳转。", "- 2018官方问卷：DB036_W4、DB037_W4三级自评及DB036选项1的跳转。", "- 2020官方问卷：DB043、DB044及DB045代理/协助回答观察项。", "- 对应官方代码本列出各字段有效响应类别；类别频数不进入项目映射或网站。", "", "这些是候选功能结局，不等于已冻结的分析变量；不得将身体健康原因推断为失业或实际家务参与。"]
(ROOT/"audit/health_work_limitation_mapping_review_v1.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(f"health/work limitation mappings={len(rows)}; concepts={len(CONCEPTS)}")
