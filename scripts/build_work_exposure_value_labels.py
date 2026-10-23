"""Extract response labels (without published frequency counts) for mapped work fields."""
from pathlib import Path
import json
import re
import unicodedata
from difflib import SequenceMatcher
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
SRC = ROOT / "sources_official"
BOOKS = {
    "2011": SRC / "CHARLS_2011_Codebook_extracted.txt",
    "2013": SRC / "CHARLS_2013_Codebook_extracted.txt",
    "2015": SRC / "CHARLS_2015_Codebook_extracted.txt",
    "2018": SRC / "CHARLS_2018_Codebook_extracted.txt",
    "2020": SRC / "CHARLS_2020_Codebook_extracted.txt",
}
HEADING = re.compile(r"^\s*(?:[•●]\s*)?([A-Za-z][A-Za-z0-9_]*(?:\s+[A-Za-z0-9_]+)?)\s*:\s*(.*?)\s*$", re.M)
VALUE = re.compile(r"^\s*(\d+)\s+(.+?)\s*$")
FREQUENCY_TAIL = re.compile(r"\s+[\d,]+\s+[\d.]+%?\s*$")


def read_codebook(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = list(HEADING.finditer(text))
    out = {}
    for i, h in enumerate(hits):
        block = text[h.end(): hits[i + 1].start() if i + 1 < len(hits) else len(text)]
        values = []
        for line in block.splitlines():
            m = VALUE.match(line)
            if m:
                label = unicodedata.normalize("NFKC", FREQUENCY_TAIL.sub("", m.group(2).strip()).strip())
                # Remove line-break artifacts and keep only the category text.
                label = re.sub(r"\s+", " ", label)
                if label and label[0].isalpha() and label.lower() not in {"total", "obs"}:
                    values.append((m.group(1), label))
        # The extracted 2011 Codebook often renders underscores as spaces
        # (for example, `fd005 indc` for `fd005_indc`). Normalize both forms
        # so exact source-field lookup does not depend on PDF text layout.
        code = re.sub(r"[^a-z0-9]", "", h.group(1).lower())
        out.setdefault(code, []).append((h.group(2).strip(), values))
    return out


def main():
    fields = pd.read_csv(AUDIT / "work_exposure_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
    books = {wave: read_codebook(path) for wave, path in BOOKS.items() if path.exists()}
    rows = []
    for r in fields.itertuples(index=False):
        wave, code = str(r.wave), str(r.code).lower()
        code_key = re.sub(r"[^a-z0-9]", "", code)
        entries = books.get(wave, {}).get(code_key, [])
        target = re.sub(r"[^a-z0-9]+", " ", str(r.source_label).lower()).strip()
        ranked = sorted(entries, key=lambda x: SequenceMatcher(None, target, re.sub(r"[^a-z0-9]+", " ", x[0].lower()).strip()).ratio(), reverse=True)
        entry = ranked[0] if ranked else None
        title_score = SequenceMatcher(None, target, re.sub(r"[^a-z0-9]+", " ", entry[0].lower()).strip()).ratio() if entry else 0
        if entry is None or title_score < 0.48:
            labels, status, source = "", "official codebook category labels not located", ""
        else:
            _, vals = entry
            labels = "; ".join(f"{v}={label}" for v, label in vals)
            if labels:
                if re.search(r"s\d+$", code):
                    status = "official selected-option label; checkbox slot, absence is not a negative response"
                else:
                    status = "official codebook response labels; frequencies omitted"
            else:
                status = "codebook field located; continuous/open response or no categorical labels"
            source = str(BOOKS[wave].relative_to(ROOT)).replace("\\", "/")
            if code == "fb010" and wave == "2011":
                status = ("DO NOT ANALYZE; questionnaire: 1=Family, 2=Health, 3=School, 4=Unemployment/layoff, 5=Other; "
                          "Codebook labels retained for reference: 1=Family, 2=Health, 4=School, 5=Unemployment/layoff, 6=Other; "
                          "released-data coding unresolved")
                source += "; sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"
        rows.append({
            "wave": wave, "code": r.code, "concept_id": r.concept_id,
            "source_label": r.source_label, "value_labels": labels,
            "value_label_status": status, "value_label_source": source,
        })
    out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
    classification = out["code"].str.lower().str.endswith(("_gb", "_isco", "_indc"))
    for idx in out.index[classification]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = ""
        out.at[idx, "value_label_status"] = (
            "occupation/industry classification code; not a numeric scale or response menu; "
            "use the matching official classification lookup; Codebook frequencies omitted"
        )
        out.at[idx, "value_label_source"] = str(BOOKS[wave].relative_to(ROOT)).replace("\\", "/")
    # The codebook prints observed response categories with frequencies; FL016's
    # questionnaire defines the full 1-10 menu, including options not observed
    # in a given release. Keep the full official menu and do not carry counts.
    ownership_menu = "1=100% state-owned firm; 2=state-controlled firm; 3=100% collective-owned firm; 4=collective-controlled firm; 5=100% private firm; 6=private-controlled firm; 7=100% foreign-owned firm; 8=joint venture; 9=other joint-ownership firm; 10=other (specify)"
    ownership = out["code"].str.lower().eq("fl016")
    for idx in out.index[ownership]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = ownership_menu
        out.at[idx, "value_label_status"] = "official questionnaire response categories; codebook frequencies omitted; firm-only route"
        out.at[idx, "value_label_source"] = f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    current_ownership = out["code"].str.lower().eq("fd010") & out["wave"].astype(str).isin({"2013", "2015", "2018"})
    full_ownership_menu = "1=100% state-owned firm; 2=state-controlled firm; 3=100% collective-owned firm; 4=collective-controlled firm; 5=100% private firm; 6=private-controlled firm; 7=100% foreign-owned firm; 8=joint venture; 9=other joint-ownership firm; 10=other"
    for idx in out.index[current_ownership]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = full_ownership_menu
        out.at[idx, "value_label_status"] = "full official questionnaire response menu transcribed without frequencies; current employer firm route"
        out.at[idx, "value_label_source"] = f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt"
    self_employment_status = out["code"].str.lower().eq("fl012") & out["wave"].astype(str).isin({"2011", "2013", "2015"})
    for idx in out.index[self_employment_status]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = "1=Self-employed with employees; 2=Self-employed without employees; 3=Family business worker without pay"
        out.at[idx, "value_label_status"] = "official questionnaire categories transcribed without frequencies; preserve three-category employment/family-business status"
        questionnaire = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt"
        out.at[idx, "value_label_source"] = f"sources_official/{questionnaire}"
    first_workplace = out["code"].str.lower().eq("fb004") & out["wave"].astype(str).isin({"2011", "2013"})
    first_workplace_menus = {
        "2011":"1=Same village/community; 2=Other village/community in same county/city; 3=Another county/city in this province; 4=Another province",
        "2013":"1=Same as permanent address; 2=Another village/neighborhood in permanent-address county/city/district; 3=Other; 4=Abroad",
    }
    for idx in out.index[first_workplace]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = first_workplace_menus[wave]
        out.at[idx, "value_label_status"] = "wave-specific official questionnaire categories transcribed without frequencies; retrospective first-workplace location"
        questionnaire = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt"
        out.at[idx, "value_label_source"] = f"sources_official/{questionnaire}"
    retirement_health = out["code"].str.lower().eq("fm043") & out["wave"].astype(str).isin({"2011", "2013", "2015", "2018"})
    retirement_health_menu = "1=Excellent; 2=Very good; 3=Good; 4=Fair; 5=Poor"
    for idx in out.index[retirement_health]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = retirement_health_menu
        out.at[idx, "value_label_status"] = "official questionnaire response labels transcribed without frequencies; retrospective health at retirement"
        questionnaire = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt"
        out.at[idx, "value_label_source"] = f"sources_official/{questionnaire}"
    civil = out["code"].str.lower().eq("fl015")
    for idx in out.index[civil]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = "1=Yes; 2=No"
        out.at[idx, "value_label_status"] = "official questionnaire response categories; codebook frequencies omitted; government-only route"
        out.at[idx, "value_label_source"] = f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    job_search = out["code"].str.lower().eq("fk002") & out["wave"].astype(str).isin({"2011", "2013", "2015", "2018"})
    for idx in out.index[job_search]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = "1=Yes; 2=No"
        out.at[idx, "value_label_status"] = "official questionnaire/codebook response labels; frequencies omitted; preserve wave-specific job-search route"
        questionnaire = ("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt")
        codebook = ("sources_official/CHARLS_2011_Codebook_extracted.txt" if wave == "2011" else f"sources_official/CHARLS_{wave}_Codebook_extracted.txt")
        out.at[idx, "value_label_source"] = f"sources_official/{questionnaire}; {codebook}"
    # The 2011 questionnaire confirms the option wording and separate checkbox fields,
    # but does not establish the released selected/unselected/missing value codes.
    fl020_2011_options = {
        1: "Business closed", 2: "Quit", 3: "I was laid off", 4: "I was fired",
        5: "I went to school", 6: "I went abroad", 7: "Stopped working for health reasons",
        8: "Stopped working for family reasons", 9: "Transferred to another job",
        10: "Sent down to the countryside for manual labor", 11: "Started working off-farm locally",
        12: "Went to work away from home", 13: "Better job in the local area",
        14: "Better job in another location", 15: "Retired", 16: "Other",
    }
    for option, meaning in fl020_2011_options.items():
        mask = out["code"].str.lower().eq(f"fl020s{option}") & out["wave"].astype(str).eq("2011")
        for idx in out.index[mask]:
            out.at[idx, "value_labels"] = f"questionnaire option: {meaning} (not an answer-value code)"
            out.at[idx, "value_label_status"] = "DO NOT ANALYZE; official 2011 baseline questionnaire option label; selected/unselected/missing value coding not verified; absence is not No"
            out.at[idx, "value_label_source"] = "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"
    job_exit = out["code"].str.lower().eq("fl021")
    for idx in out.index[job_exit]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = "1=Yes; 2=No"
        if wave == "2011":
            out.at[idx, "value_label_status"] = "official questionnaire response labels; 2011 extracted codebook distribution not located; frequencies omitted"
            source = "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"
        else:
            out.at[idx, "value_label_status"] = "official questionnaire/codebook response labels; frequencies omitted; wording and route are wave-specific"
            source = f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        out.at[idx, "value_label_source"] = source
    continuity = out["code"].str.lower().eq("fd012_w2_3")
    for idx in out.index[continuity]:
        out.at[idx, "value_labels"] = "1=Yes; 2=No"
        out.at[idx, "value_label_status"] = "official questionnaire response categories transcribed without frequencies; continuity of the specific prior-wave work activity"
        out.at[idx, "value_label_source"] = "sources_official/CHARLS_2013_Questionnaire_extracted.txt"
    corrected_exit_reason = out["code"].str.lower().eq("fa019") & out["wave"].astype(str).eq("2020")
    for idx in out.index[corrected_exit_reason]:
        out.at[idx, "value_labels"] = "1=Forced to leave; 2=Bad business or poorly paid; 3=Non-pecuniary reason; 4=Health issues; 5=Family issues/caregiving; 6=Formal retirement; 7=Temporary layoff; 8=Other (specify)"
        out.at[idx, "value_label_status"] = "official questionnaire categories transcribed without frequencies; DO NOT ANALYZE until prior-status correction logic and released-data coding are reconciled"
        out.at[idx, "value_label_source"] = "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt"
    farm_status = out["code"].str.lower().isin({"fc001", "fc008"}) & out["wave"].astype(str).isin({"2011", "2013", "2015", "2018"})
    for idx in out.index[farm_status]:
        wave = str(out.at[idx, "wave"])
        code = str(out.at[idx, "code"]).lower()
        out.at[idx, "value_labels"] = "1=Yes; 2=No"
        questionnaire = ("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt")
        codebook = ("sources_official/CHARLS_2011_Codebook_extracted.txt" if wave == "2011" else f"sources_official/CHARLS_{wave}_Codebook_extracted.txt")
        out.at[idx, "value_label_source"] = f"sources_official/{questionnaire}; {codebook}"
    pension_source_slots = {
        "fm019s1": "Government",
        "fm019s2": "Previous work unit",
        "fm019s3": "Social insurance agency",
        "fm019s4": "Commercial insurance company",
        "fm019s5": "Other",
    }
    for code, meaning in pension_source_slots.items():
        mask = out["code"].str.lower().eq(code) & out["wave"].astype(str).eq("2011")
        for idx in out.index[mask]:
            out.at[idx, "value_labels"] = f"questionnaire option slot={meaning} (not an answer-value label)"
            out.at[idx, "value_label_status"] = "questionnaire slot meaning verified; respondent-level checkbox storage unverified; DO NOT ANALYZE"
            out.at[idx, "value_label_source"] = "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        if code == "fc008" and wave == "2018":
            out.at[idx, "value_label_status"] = "1=Yes; 2=No; questionnaire asks at least 10 days, but codebook title says at least one month; DO NOT ANALYZE until eligibility route is clarified"
        else:
            out.at[idx, "value_label_status"] = "official questionnaire/codebook response labels; frequencies omitted; agricultural work route is wave-specific"
    pandemic_menus = {
        "fg001": "1=Yes; 2=No",
        "fg002": "1=Yes, paid less than normal wage; 2=Yes, paid more than normal wage; 3=No such situation",
        "fg003": "1=Would not do household agricultural work anyway; 2=Worked less; 3=Worked more; 4=Not affected; 999=Refuse",
        "fg004": "1=Would not work for pay anyway; 2=Worked less; 3=Worked more; 4=Not affected; 999=Refuse",
        "fg005": "1=Would not run a non-agricultural business anyway; 2=Worked less; 3=Worked more; 4=Not affected; 999=Refuse",
        "fg008": "1=No effect; 2=Worked fewer hours per week; 3=Worked more hours per week; 4=Has not worked since Chinese New Year; 999=Refuse",
        "fg009": "1=Yes; 2=No",
        "ff005": "1=Planned work-stop brought forward; 2=Planned work-stop delayed; 3=Not affected; 997=Don't know; 999=Refuse",
        "ff002": "1=Yes; 2=No",
        "ff004": "1=Until an age; 2=After some years; 3=Work as long as health permits; 997=Don't know; 999=Refuse",
    }
    pandemic = out["code"].str.lower().isin(pandemic_menus)
    for idx in out.index[pandemic]:
        wave = str(out.at[idx, "wave"])
        code = str(out.at[idx, "code"]).lower()
        out.at[idx, "value_labels"] = pandemic_menus[code]
        if code in {"ff002", "ff004"}:
            out.at[idx, "value_label_status"] = "official 2020 questionnaire/codebook response labels; frequencies omitted; verify FF module denominator; not a harmonized retirement definition"
            out.at[idx, "value_label_source"] = f"sources_official/CHARLS_{wave}_Questionnaire_English_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        else:
            out.at[idx, "value_label_status"] = ("official questionnaire response categories; codebook frequencies omitted; 2020 pandemic module; apply xfgsample"
                                                  if code != "ff005" else "official questionnaire response categories; codebook frequencies omitted; 2020 FF item; preserve FF004 route; xfgsample not assumed")
            out.at[idx, "value_label_source"] = f"sources_official/CHARLS_{wave}_Questionnaire_English_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    # The 2020 codebook prints some category headings without numeric prefixes,
    # so keep the option codes from the official questionnaire. Do not copy counts.
    transition_menus = {
        "fa013": "1=Yes; 995=Deny the prior nonworking record; 999=Refuse",
        "fa015": "1=Economic reasons/need more income; 2=Recovery from poor health; 3=No need for caregiving; 4=Work as exercise; 5=No particular reason/just want to work; 6=Other (free text)",
        "fa016": "1=Yes; 995=Deny the prior working record; 999=Refuse",
        "fa019": "1=Forced to leave (e.g., fired); 2=Bad business or poorly paid; 3=Non-pecuniary reason; 4=Health issues; 5=Family issues (e.g., caregiving); 6=Formal retirement; 7=Temporary layoff; 8=Other (free text)",
    }
    transition = out["code"].str.lower().isin(transition_menus)
    for idx in out.index[transition]:
        code = str(out.at[idx, "code"]).lower()
        out.at[idx, "value_labels"] = transition_menus[code]
        out.at[idx, "value_label_status"] = ("official 2020 questionnaire response categories; frequencies omitted; conditional prior-status correction route; DO NOT ANALYZE pending route and released-data reconciliation"
                                              if code == "fa019" else "official 2020 questionnaire response categories; frequencies omitted; conditional work-history transition route")
        out.at[idx, "value_label_source"] = "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt"
    transition_components = out["code"].str.lower().isin({"fa013_1", "fa013_2", "fa016_1", "fa016_2", "fa018_1", "fa018_2"})
    for idx in out.index[transition_components]:
        code = str(out.at[idx, "code"]).lower()
        out.at[idx, "value_labels"] = ""
        out.at[idx, "value_label_status"] = ("continuous date component; preserve year/month unit and conditional prior-status correction route; month -1 indicates unable to report; DO NOT ANALYZE pending route and released-data reconciliation"
                                              if code.startswith("fa018") else "continuous date component; preserve year/month unit and conditional transition/correction route; month -1 indicates unable to report where specified")
        out.at[idx, "value_label_source"] = "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt"
    # Questionnaire-verified current work classifications and route flags.
    for idx in out.index[out.code.str.lower().isin({"fc020", "fc021"}) & out.wave.astype(str).isin({"2011", "2013", "2015"})]:
        out.at[idx, "value_labels"] = "1=Employed; 2=Self-employed; 3=Unpaid family business"
        out.at[idx, "value_label_status"] = "official questionnaire categories; frequencies omitted; FC020 multiple-job main-work route or FC021 single nonfarm-job route"
        wave = str(out.at[idx, "wave"])
        questionnaire = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt"
        out.at[idx, "value_label_source"] = f"sources_official/{questionnaire}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    for idx in out.index[out.code.str.lower().eq("fc019") & out.wave.astype(str).isin({"2011", "2013", "2015"})]:
        out.at[idx, "value_labels"] = "1=Yes, more than one current non-agricultural job; 2=No, one job"
        out.at[idx, "value_label_status"] = "official questionnaire categories; frequencies omitted; 2011 question wording controls its scope"
        wave = str(out.at[idx, "wave"])
        questionnaire = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt"
        out.at[idx, "value_label_source"] = f"sources_official/{questionnaire}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    for idx in out.index[out.code.str.lower().eq("fg014") & out.wave.astype(str).isin({"2011", "2013"})]:
        out.at[idx, "value_labels"] = "1=Yes; 2=No"
        out.at[idx, "value_label_status"] = "official questionnaire/codebook categories; frequencies omitted; current employer benefit route"
        wave = str(out.at[idx, "wave"])
        questionnaire = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt"
        out.at[idx, "value_label_source"] = f"sources_official/{questionnaire}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    for idx in out.index[out.code.str.lower().eq("fc017") & out.wave.astype(str).eq("2011")]:
        out.at[idx, "value_labels"] = "1=Yes, expects to return within a definite time or six months; 2=No"
        out.at[idx, "value_label_status"] = "official questionnaire categories; frequencies omitted; conditional agricultural-wage/other-job temporary-absence route"
        out.at[idx, "value_label_source"] = "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
    occupation_codes = out.code.str.lower().isin({"fh015_gb", "fh015_isco"})
    for idx in out.index[occupation_codes]:
        out.at[idx, "value_labels"] = ""
        out.at[idx, "value_label_status"] = "occupation classification code; codebook frequency distribution omitted; classification definitions are not response labels"
        out.at[idx, "value_label_source"] = "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
    # These are CHARLS CAPI formulas, not standalone questionnaire response
    # labels. Keep the derived coding from the official formula and omit all
    # descriptive frequencies printed in the codebook.
    capi_labels = {
        "xworking": "0=No qualifying work route; 1=At least one of FA001/FA004/FA007/FA008 equals 1",
        "xemployed": "0=Self-employed or unpaid family-business main work; 1=Employed work (including paid farm work)",
        "xworkjuststarted": "0=Not within the formula's recent-start windows; 1=Started within the most recent month; 2=Started within the past year",
        "xgetjob": "0=No prior-nonworking to current-working transition; 1=ZWorking=0 and XWorking=1",
        "xquitjob": "0=No prior-working to current-nonworking transition; 1=ZWorking=1 and XWorking=0",
        "xsidejobdays": "Derived days/year = FE001 days/week × 52; missing product is set to 0 by questionnaire formula",
    }
    capi = out["code"].str.lower().isin(capi_labels)
    for idx in out.index[capi]:
        code = str(out.at[idx, "code"]).lower()
        out.at[idx, "value_labels"] = capi_labels[code]
        out.at[idx, "value_label_status"] = "official 2020 questionnaire CAPI formula manually transcribed; descriptive codebook frequencies omitted; generated-field interpretation requires route validation"
        out.at[idx, "value_label_source"] = "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt (printed pp.57, 69-71); sources_official/CHARLS_2020_Codebook_extracted.txt"
    pandemic_components = out["code"].str.lower().str.match(r"^(fg002_[12]|fg00[345]_[12]|fg008_[12]|fg010_[12]|ff005_[12])$")
    for idx in out.index[pandemic_components]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = ""
        out.at[idx, "value_label_status"] = ("continuous conditional component; unit and route reviewed; no response-category labels; codebook frequencies omitted"
                                              if not code.startswith("ff005_") else "continuous FF005 component; unit and FF004 route reviewed; no response-category labels; do not assume xfgsample")
        out.at[idx, "value_label_source"] = f"sources_official/CHARLS_{wave}_Questionnaire_English_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    # The 2011 Codebook omits FL014, and later codebooks omit menu choices with zero observed frequency.
    # Use the full questionnaire menu while deliberately excluding all frequencies.
    recent_job_type = out["code"].str.lower().eq("fl014") & out["wave"].astype(str).isin({"2011", "2013", "2015", "2018"})
    employer_menu = "1=Government; 2=Institution/public institution; 3=NGO; 4=Firm; 5=Individual firm; 6=Individual farmer; 7=Individual household; 8=Other (specify where asked)"
    for idx in out.index[recent_job_type]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = employer_menu
        questionnaire = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt"
        source = f"sources_official/{questionnaire}"
        if wave != "2011":
            source += f"; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        out.at[idx, "value_label_status"] = "full questionnaire menu transcribed without frequencies; 2011 codebook omits FL014 and later codebook menus may omit unobserved categories; not-currently-working prior-job route"
        out.at[idx, "value_label_source"] = source
    # The 2018 FG001 options are separate checkbox slots. Publish the menu and
    # the documented slot coding without copying the codebook frequencies.
    fringe = out["wave"].astype(str).eq("2018") & out["code"].str.lower().str.match(r"fg001_s\d+$")
    for idx in out.index[fringe]:
        code = out.at[idx, "code"].lower()
        slot = int(code.rsplit("s", 1)[1])
        menu = {
            1:"Free lunch",2:"Free breakfast",3:"Free dinner",4:"Meal allowance",
            5:"Transportation allowance",6:"Free housing",7:"Housing allowance",
            8:"Company car",9:"Free employee shuttle",10:"Other allowance",
            11:"None",
        }.get(slot, "Selected option")
        out.at[idx, "value_labels"] = f"0=Not selected; 9={menu} selected"
        out.at[idx, "value_label_status"] = "official questionnaire checkbox menu and codebook slot coding; frequencies omitted; absence is not a negative response outside the routed checklist"
        out.at[idx, "value_label_source"] = "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"
    unresolved_status = (out["code"].str.lower().eq("fd009") & out["wave"].astype(str).eq("2011")) | (out["code"].str.lower().eq("fc008") & out["wave"].astype(str).eq("2020"))
    for idx in out.index[unresolved_status]:
        wave = str(out.at[idx, "wave"])
        out.at[idx, "value_labels"] = "1=Yes; 2=No"
        out.at[idx, "value_label_status"] = "questionnaire/Codebook item-identity conflict; DO NOT ANALYZE until official source identity and released-data coding are reconciled"
        questionnaire = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else "CHARLS_2020_Questionnaire_English_extracted.txt"
        out.at[idx, "value_label_source"] = f"sources_official/{questionnaire}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    # The 2011 English questionnaire documents wording/routes for several
    # work-module fields whose released numeric coding is absent from the
    # extracted Codebook. Keep option wording distinct from verified values.
    questionnaire_2011 = "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"
    questionnaire_only_options = {
        "fi004": "I was laid-off but the employment contract was not terminated; on leave from this employer; kept my position but received no pay; a friend in the work unit helped; other",
        "fi008": "I know my own and the work unit's amounts; I know my own amount but not the work unit's; I know neither amount",
        "fl001": "Employed; self-employed; unpaid family business; farming",
        "fl013": "Regular wage worker; contract worker; temporary wage worker; casual wage worker",
    }
    for code, menu in questionnaire_only_options.items():
        mask = out["wave"].astype(str).eq("2011") & out["code"].str.lower().eq(code)
        for idx in out.index[mask]:
            out.at[idx, "value_labels"] = f"Questionnaire options (numeric answer codes unverified): {menu}"
            out.at[idx, "value_label_status"] = "official questionnaire option wording only; released numeric value codes not verified; DO NOT ANALYZE until reconciled to authorized release"
            out.at[idx, "value_label_source"] = questionnaire_2011
    fl007_2011 = out["wave"].astype(str).eq("2011") & out["code"].str.lower().eq("fl007")
    for idx in out.index[fl007_2011]:
        out.at[idx, "value_labels"] = "Questionnaire answers (release coding unverified): Yes; No"
        out.at[idx, "value_label_status"] = "official questionnaire answer wording; released numeric value codes not verified; DO NOT ANALYZE until reconciled to authorized release"
        out.at[idx, "value_label_source"] = questionnaire_2011
    # Unlike the above unnumbered choices, the questionnaire explicitly
    # numbers the workplace-location answers. The released coding still needs
    # confirmation; zero is an interviewer instruction for no fixed address.
    fl004_2011 = out["wave"].astype(str).eq("2011") & out["code"].str.lower().eq("fl004")
    for idx in out.index[fl004_2011]:
        out.at[idx, "value_labels"] = "Questionnaire categories (release coding unverified): 1=This village/community; 2=Other village/community in this county/city; 3=Another county/city in this province; 4=Another province; interviewer instructed 0 when no fixed address"
        out.at[idx, "value_label_status"] = "numbered official questionnaire categories; released-data value coding and no-fixed-address storage unverified; DO NOT ANALYZE pending reconciliation"
        out.at[idx, "value_label_source"] = questionnaire_2011
    questionnaire_measurements = {
        "fi009": "Questionnaire measurement: work unit's total contribution, Yuan per month; no categorical response menu",
        "fi012": "Questionnaire measurement: planned age to stop all income-related work, 0-120 years; 0 means plans to continue while physically able",
        "fl008": "Questionnaire measurement: usual hours worked per week, 0-168; soft verification prompt above 80 hours; employed route only",
        "fl009": "Questionnaire measurement: monthly wages, bonuses and subsidies before leaving the job, Yuan; interviewer instructed 0 for no net income and 999997 for running a deficit",
        "fl022_1": "Questionnaire measurement: job-exit compensation amount, Yuan; asked on the conditional compensation route; refusal/don't-remember bracket follow-up",
        "fl022_2": "Questionnaire measurement: years of work used for compensation, 0-120 years; asked on the conditional compensation route",
        "fm051": "Questionnaire measurement: grandchildren below age 6 at retirement, 0-50 persons; interviewer instructed 0 if none",
    }
    for code, note in questionnaire_measurements.items():
        mask = out["wave"].astype(str).eq("2011") & out["code"].str.lower().eq(code)
        for idx in out.index[mask]:
            out.at[idx, "value_labels"] = note
            out.at[idx, "value_label_status"] = "official questionnaire measurement/range note; continuous or count response, not categorical answer labels; route and special-value handling require release-level review"
            out.at[idx, "value_label_source"] = questionnaire_2011
    out.to_csv(AUDIT / "work_exposure_value_labels_v1.csv", index=False, encoding="utf-8-sig")

    json_path = ROOT / "site-prototype" / "dist" / "work_exposures_v1.json"
    concepts = json.loads(json_path.read_text(encoding="utf-8"))
    lookup = {(r.wave, r.code.lower(), r.concept_id): r for r in out.itertuples(index=False)}
    labeled = 0
    for concept in concepts:
        for field in concept["source_fields"]:
            row = lookup.get((field["wave"], field["code"].lower(), concept["concept_id"]))
            if row:
                field["value_labels"] = row.value_labels
                field["value_label_status"] = row.value_label_status
                field["value_label_source"] = row.value_label_source
                labeled += bool(row.value_labels)
    json_path.write_text(json.dumps(concepts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"work value-label mappings={len(out)}; mappings with extracted category labels={int(labeled)}")


if __name__ == "__main__":
    main()
