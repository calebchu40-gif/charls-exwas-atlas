
"""Build metadata-only mappings for CHARLS disability history items."""
from pathlib import Path
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = pd.read_csv(ROOT / "audit/raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
BOOKS = {
    "2011": ROOT / "sources_official/CHARLS_2011_Codebook_extracted.txt",
    "2013": ROOT / "sources_official/CHARLS_2013_Codebook_extracted.txt",
    "2015": ROOT / "sources_official/CHARLS_2015_Codebook_extracted.txt",
    "2018": ROOT / "sources_official/CHARLS_2018_Codebook_extracted.txt",
}
QUESTIONNAIRES = {
    "2011": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc, Word p.62 (DA005–DA006)",
    "2013": "sources_official/CHARLS_2013_Questionnaire.pdf",
    "2015": "sources_official/CHARLS_2015_Questionnaire.pdf",
    "2018": "sources_official/CHARLS_2018_Questionnaire.pdf",
}
ARCHIVES = {"2011":"household_and_community_questionnaire_data.rar", "2013":"CHARLS2013_Dataset.zip", "2015":"CHARLS2015r.zip", "2018":"CHARLS2018r.zip"}
TYPES = [
    (1, "physical", "躯体残疾", "Physical disabilities"),
    (2, "brain_intellectual", "脑损伤/智力障碍", "Brain damage/intellectual disability"),
    (3, "vision", "视力障碍", "Vision problem"),
    (4, "hearing", "听力障碍", "Hearing problem"),
    (5, "speech", "言语障碍", "Speech impediment"),
]
NEXT = re.compile(r"^\s*(?:[•●]\s*)?[A-Za-z][A-Za-z0-9_]*\s*:")
VALUE = re.compile(r"^\s*(\d+)\s+(.+?)\s*$")
FREQ_TAIL = re.compile(r"\s+[\d,]+\s+[\d.]+%?\s*$")

def code_values(wave: str, code: str, *, question: str) -> list[tuple[str,str]]:
    lines = BOOKS[wave].read_text(encoding="utf-8", errors="replace").splitlines()
    if wave == "2011":
        idx = int(code.split()[-1])
        heading = re.compile(rf"^\s*[•●]?\s*{re.escape(question)}\s+{idx}\s*:", re.I)
    else:
        heading = re.compile(rf"^\s*[•●]?\s*{re.escape(code)}\s*:", re.I)
    start = next((i for i,line in enumerate(lines) if heading.search(line)), None)
    if start is None:
        raise ValueError(f"Codebook heading missing: {wave} {code}")
    next_heading = (re.compile(r"\bda\d{3}\s+\d+\s*:", re.I) if wave == "2011" else NEXT)
    end = next((i for i in range(start+1,len(lines)) if next_heading.search(lines[i])),len(lines))
    vals=[]
    for line in lines[start+1:end]:
        clean=re.sub(r"\s+"," ",FREQ_TAIL.sub("",line.strip())).strip()
        m=VALUE.match(clean)
        if m and m.group(2).lower() not in {"total","no observations"}:
            vals.append((m.group(1),m.group(2).strip()))
    return list(dict.fromkeys(vals))

def source(wave: str, code: str) -> dict:
    rows=RAW[(RAW.wave==wave)&RAW.variable.str.lower().eq(code.lower())]
    if rows.empty: raise ValueError(f"Raw catalog missing {wave} {code}")
    r=rows.iloc[0]
    return {"module":r.module,"source_label":r.variable_label,"source_archive":r.source}

def main() -> None:
    rows=[]; items=[]
    for idx,key,label_zh,label_en in TYPES:
        concept=f"reported_disability_{key}"
        label=f"自报残疾史：{label_zh}"
        fields=[]
        for wave in ("2011","2013","2015","2018"):
            status_code=f"da005_{idx}_"
            onset_code=f"da006_{idx}_"
            status_src=source(wave,status_code); onset_src=source(wave,onset_code)
            code_for_book=f"da005 {idx}" if wave=="2011" else status_code
            labels=code_values(wave,code_for_book,question="da005")
            if labels != [("1","Yes"),("2","No")]:
                raise ValueError(f"Unexpected response labels {wave} {status_code}: {labels}")
            status_text="; ".join(f"{v}={lab}" for v,lab in labels)
            status_review=("official codebook confirms 1=Yes; 2=No; baseline questionnaire confirms 2011 item wording and routing" if wave=="2011" else "official codebook confirms 1=Yes; 2=No; questionnaire route still governs whether item was asked")
            common_caveat=("Prior-wave preload/verification and conditional routing may affect this field. In 2011 DA005 is the five-type disability screen; DA006 asks onset year conditional on the selected DA005 type. This field alone is not a complete current-status variable. Preserve structural skips and unknowns; do not infer No from an empty field.")
            status_sem="current-wave disability item; interpret with the wave-specific questionnaire route and prior-wave preload"
            status_doc=f"{BOOKS[wave].relative_to(ROOT).as_posix()}; {QUESTIONNAIRES[wave]}"
            rows.append({"wave":wave,"code":status_code,"concept_id":concept,"concept_label":label,"domain":"physical function","module":status_src["module"],"source_label":status_src["source_label"],"value_labels":status_text,"value_label_status":status_review,"value_label_source":status_doc,"source_archive":ARCHIVES[wave],"mapping_status":"official disability item; candidate phenotype; routing/longitudinal derivation pending","construct":"reported disability history","subtype":key,"field_role":"current-wave item","value_semantics":status_sem,"caveat":common_caveat})
            fields.append({"wave":wave,"code":status_code,"module":status_src["module"],"source_label":status_src["source_label"],"field_role":"current-wave item","value_labels":status_text,"value_label_status":status_review,"value_label_source":status_doc,"source_archive":ARCHIVES[wave],"caveat":common_caveat})
            # ZDA005 / ZDISABILITY are prior-wave preload states used to route
            # return interviews. Preserve them as historical status fields;
            # they are not current-wave answers or population-wide No/Yes items.
            prior_code = (f"zda005_{idx}_" if wave in {"2013", "2015"}
                          else f"zdisability_{idx}_" if wave == "2018" else "")
            if prior_code:
                prior_src = source(wave, prior_code)
                prior_labels = code_values(wave, prior_code, question="")
                if not prior_labels or prior_labels[0] != ("1", "Yes"):
                    raise ValueError(f"Unexpected prior-wave disability labels {wave} {prior_code}: {prior_labels}")
                prior_label_text = "; ".join(f"{v}={lab}" for v,lab in prior_labels)
                prior_caveat = ("Prior-wave disability preload used in the return-interview route. In 2015/2018 the codebook lists only the positive preloaded state; absence is not a No response. In 2013 the 1/2 labels are retained, but this remains prior-wave history, not current-wave status.")
                prior_semantics = "prior-wave disability status/preload for this type; conditional routing; not a current-wave response"
                prior_doc = f"{BOOKS[wave].relative_to(ROOT).as_posix()}; {QUESTIONNAIRES[wave]}"
                rows.append({"wave":wave,"code":prior_code,"concept_id":concept,"concept_label":label,"domain":"physical function","module":prior_src["module"],"source_label":prior_src["source_label"],"value_labels":prior_label_text,"value_label_status":"official codebook response labels extracted without frequencies; prior-wave route retained","value_label_source":prior_doc,"source_archive":ARCHIVES[wave],"mapping_status":"official prior-wave preload/status field; ancillary longitudinal context","construct":"reported disability history","subtype":key,"field_role":"prior-wave preload status","value_semantics":prior_semantics,"caveat":prior_caveat})
                fields.append({"wave":wave,"code":prior_code,"module":prior_src["module"],"source_label":prior_src["source_label"],"field_role":"prior-wave preload status","value_labels":prior_label_text,"value_label_status":"official codebook response labels extracted without frequencies; prior-wave route retained","value_label_source":prior_doc,"source_archive":ARCHIVES[wave],"caveat":prior_caveat})
            onset_labels=""
            onset_status="continuous calendar-year response; special values and out-of-range years must be preserved pending row-level quality review"
            onset_sem="reported year the respondent became disabled; conditional on disability route; not biological onset or necessarily physician-diagnosis year"
            onset_caveat=(" 2011 questionnaire gives a 1900–2011 year range and requires four digits; check codebook/released values for special codes before derivation." if wave=="2011" else " Verify special values and route rules against the wave-specific questionnaire and codebook before deriving onset year.")
            rows.append({"wave":wave,"code":onset_code,"concept_id":concept,"concept_label":label,"domain":"physical function","module":onset_src["module"],"source_label":onset_src["source_label"],"value_labels":onset_labels,"value_label_status":onset_status,"value_label_source":f"{BOOKS[wave].relative_to(ROOT).as_posix()}; {QUESTIONNAIRES[wave]}","source_archive":ARCHIVES[wave],"mapping_status":"official onset-year field; ancillary measure under the disability concept","construct":"reported disability history","subtype":key,"field_role":"reported onset year","value_semantics":onset_sem,"caveat":common_caveat+onset_caveat})
            fields.append({"wave":wave,"code":onset_code,"module":onset_src["module"],"source_label":onset_src["source_label"],"field_role":"reported onset year","value_labels":"","value_label_status":onset_status,"value_label_source":f"{BOOKS[wave].relative_to(ROOT).as_posix()}; {QUESTIONNAIRES[wave]}","source_archive":ARCHIVES[wave],"caveat":onset_sem})
            if wave=="2018":
                verify_code=f"da006_w4_{idx}_"
                year_code=f"da006_w4_1_{idx}_"
                verify_src=source(wave,verify_code); year_src=source(wave,year_code)
                verify_labels=code_values(wave,verify_code,question="da006")
                if ("1","Yes") not in verify_labels or ("99","Never had it") not in verify_labels:
                    # Codebook wording is field-specific and may spell out “the disability”.
                    if ("1","Yes") not in verify_labels or not any(v=="99" and "never" in text.lower() for v,text in verify_labels):
                        raise ValueError(f"Unexpected 2018 verification labels {verify_code}: {verify_labels}")
                verify_text="; ".join(f"{v}={lab}" for v,lab in verify_labels)
                verify_caveat="2018 return-respondent branch verifies a preloaded prior-wave disability. Code 99 means never had that disability in this verification question; it is not a general current-wave No code."
                rows.append({"wave":wave,"code":verify_code,"concept_id":concept,"concept_label":label,"domain":"physical function","module":verify_src["module"],"source_label":verify_src["source_label"],"value_labels":verify_text,"value_label_status":"2018 official codebook labels verified; frequencies excluded","value_label_source":f"{BOOKS[wave].relative_to(ROOT).as_posix()}; {QUESTIONNAIRES[wave]}","source_archive":ARCHIVES[wave],"mapping_status":"2018 prior-wave disability verification; ancillary route only","construct":"reported disability history","subtype":key,"field_role":"prior-wave verification","value_semantics":"1=Yes; 99=Never had it in the prior-record verification route","caveat":verify_caveat})
                fields.append({"wave":wave,"code":verify_code,"module":verify_src["module"],"source_label":verify_src["source_label"],"field_role":"prior-wave verification","value_labels":verify_text,"value_label_status":"2018 official codebook labels verified; frequencies excluded","value_label_source":f"{BOOKS[wave].relative_to(ROOT).as_posix()}; {QUESTIONNAIRES[wave]}","source_archive":ARCHIVES[wave],"caveat":verify_caveat})
                year_labels=""
                year_status="continuous year response in a conditional prior-wave verification branch; preserve special values"
                rows.append({"wave":wave,"code":year_code,"concept_id":concept,"concept_label":label,"domain":"physical function","module":year_src["module"],"source_label":year_src["source_label"],"value_labels":year_labels,"value_label_status":year_status,"value_label_source":f"{BOOKS[wave].relative_to(ROOT).as_posix()}; {QUESTIONNAIRES[wave]}","source_archive":ARCHIVES[wave],"mapping_status":"2018 prior-wave onset-year follow-up; ancillary route only","construct":"reported disability history","subtype":key,"field_role":"prior-wave reported onset year","value_semantics":"Year response for the prior-wave disability record when the regular onset-year response was not available","caveat":verify_caveat})
                fields.append({"wave":wave,"code":year_code,"module":year_src["module"],"source_label":year_src["source_label"],"field_role":"prior-wave reported onset year","value_labels":"","value_label_status":year_status,"value_label_source":f"{BOOKS[wave].relative_to(ROOT).as_posix()}; {QUESTIONNAIRES[wave]}","source_archive":ARCHIVES[wave],"caveat":verify_caveat})
        items.append({"concept_id":concept,"label":label,"label_en":label_en,"domain":"physical function","disability_type":key,"source_fields":fields,"caveat":"Candidate self-reported disability phenotype. The questionnaire distinguishes new/previous-wave cases and asks onset year conditionally. Do not combine across waves or infer absence from structural skip until preloads, nonresponse, and module eligibility are reconciled."})
    out=pd.DataFrame(rows)
    out.to_csv(ROOT/"audit/disability_history_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
    (ROOT/"site-prototype/dist/disability_history_v1.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
    assert len(out)==65 and out.concept_id.nunique()==5
    assert not any("Freq." in x or "%" in x for x in out.value_labels)
    print(f"disability history mappings={len(out)}; concepts={out.concept_id.nunique()}; status/onset fields and 2018 follow-up verified")

if __name__=="__main__":main()


