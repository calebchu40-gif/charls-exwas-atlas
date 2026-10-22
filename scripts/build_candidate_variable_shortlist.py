"""Create a metadata-only shortlist of CHARLS analysis domains by wave."""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
catalog = pd.read_csv(ROOT / "audit/raw_variable_catalog_v1.csv", encoding="utf-8-sig")
catalog = catalog[catalog.wave.isin(["2011", "2013", "2015", "2018", "2020"])].copy()

domains = {
    "直接测量-血液生化": (r"Blood_Assays|blood", r"blood urea|bun|glucose|creatin|cholesterol|triglycer|hdl|ldl|c-reactive|\bcrp\b|hba1c|glycated|hemoglobin|cystatin|white blood cell"),
    "直接测量-体格/生命体征": (r"Biomarker|biomarkers", r"blood pressure|systolic|diastolic|height|weight measurement|waist|knee height|pulse|grip|peak flow|lung function"),
    "问卷-慢病及功能结局": (r"Health_Status_and_Functioning|health_status_and_functioning", r"diabetes|high blood sugar|hypertension|high blood pressure|heart disease|stroke|cancer|lung disease|arthritis|kidney|memory|depress|adl|iadl|mobility|pain|self-rated health|sleep"),
    "问卷-行为与生活方式暴露": (r"Health_Status_and_Functioning|health_status_and_functioning|Biomarker|biomarkers", r"smok|cigarette|tobacco|alcohol|drank|exercise|physical activ|sleep|diet|food|tea|coffee"),
    "家庭环境代理": (r"Housing_Characteristics|Housing|housing_characteristics", r"water|toilet|sewer|cooking fuel|fuel|heating|ventilat|cook|electricity|floor|roof|kitchen"),
    "社区环境/社会环境代理": (r"community", r"pollution|industrial|water|waste|toilet|fuel|green|traffic|road|health care|hospital|village|community"),
    "社会人口学协变量": (r"Demographic_Background|demographic_background", r"age|gender|sex|education|marital|residence|rural|urban|民族|ethnic"),
    "权重与抽样设计": (r"Weights|weight|PSU|psu|Sample_Infor|Sample_Info", r"weight|psu|strat|sample|community|cluster|biomarker"),
}

out = []
for domain, (mod_re, text_re) in domains.items():
    sel = catalog.module.str.contains(mod_re, case=False, regex=True, na=False) & (
        catalog.variable_label.fillna("").str.contains(text_re, case=False, regex=True, na=False)
        | catalog.variable.fillna("").str.contains(text_re, case=False, regex=True, na=False)
    )
    for row in catalog.loc[sel].itertuples(index=False):
        out.append({"domain_candidate": domain, "wave": row.wave, "module": row.module,
                    "variable": row.variable, "variable_label": row.variable_label,
                    "module_rows": row.module_rows, "module_columns": row.module_columns,
                    "source_archive": row.source})

df = pd.DataFrame(out).drop_duplicates()
df.to_csv(ROOT / "audit/candidate_variable_shortlist_v1.csv", index=False, encoding="utf-8-sig")

summary = df.groupby("domain_candidate").agg(
    variable_wave_entries=("variable", "size"), distinct_variable_names=("variable", "nunique"),
    waves=("wave", lambda x: ",".join(sorted(x.unique()))),
).reset_index()
summary.to_csv(ROOT / "audit/candidate_domain_counts_v1.csv", index=False, encoding="utf-8-sig")
print(summary.to_string(index=False))
print(f"shortlist_rows={len(df)}")
