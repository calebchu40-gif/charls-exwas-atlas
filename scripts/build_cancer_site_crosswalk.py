"""Map CHARLS site-specific cancer history items from codebooks and questionnaires."""
from pathlib import Path
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BOOKS = {
    "2011": ROOT / "audit" / "CHARLS_2011_Codebook_extracted.txt",
    "2013": ROOT / "sources_official" / "CHARLS_2013_Codebook_extracted.txt",
    "2015": ROOT / "sources_official" / "CHARLS_2015_Codebook_extracted.txt",
    "2018": ROOT / "sources_official" / "CHARLS_2018_Codebook_extracted.txt",
}
ARCHIVES = {"2011": "household_and_community_questionnaire_data.rar", "2013": "CHARLS2013_Dataset.zip",
            "2015": "CHARLS2015r.zip", "2018": "CHARLS2018r.zip"}
QUESTIONNAIRES = {
    "2011": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc, Word p.64 (DA017; conditional on DA007=4; all-that-apply, includes primary and metastatic sites; ask even if cured)",
    "2013": "CHARLS_2013_Questionnaire.pdf",
    "2015": "CHARLS_2015_Questionnaire.pdf",
    "2018": "CHARLS_2018_Questionnaire.pdf",
}
SITES = [
    "Brain", "Oral cavity", "Larynx", "Other pharynx", "Thyroid", "Lung", "Breast",
    "Oesophagus", "Stomach", "Liver", "Pancreas", "Kidney", "Prostate", "Testicle",
    "Ovary", "Cervix", "Endometrium", "Colon or rectum", "Bladder", "Skin",
    "Non-Hodgkin lymphoma", "Leukemia", "Other organ",
]
FREQUENCY_TAIL = re.compile(r"\s+[\d,]+\s+[\d.]+%?\s*$")
VALUE = re.compile(r"^\s*(\d+)\s+(.+?)\s*$")
NEXT_HEADING = re.compile(r"^\s*(?:[•●]\s*)?[A-Za-z][A-Za-z0-9_]*\s*:")


def codebook_values(wave: str, code: str) -> list[tuple[str, str]]:
    lines = BOOKS[wave].read_text(encoding="utf-8", errors="replace").splitlines()
    heading = re.compile(rf"^\s*(?:[•●]\s*)?{re.escape(code)}\s*:", re.I)
    start = next((i for i, line in enumerate(lines) if heading.search(line)), None)
    if start is None:
        raise ValueError(f"Official codebook heading not found: {wave} {code}")
    end = next((i for i in range(start + 1, len(lines)) if NEXT_HEADING.search(lines[i])), len(lines))
    values: list[tuple[str, str]] = []
    for line in lines[start + 1:end]:
        clean = re.sub(r"\s+", " ", FREQUENCY_TAIL.sub("", line.strip())).strip()
        match = VALUE.match(clean)
        if not match:
            continue
        value, label = match.groups()
        if label.lower() not in {"total", "no observations", "no"}:
            values.append((value, label.strip()))
        elif label.lower() == "no":
            values.append((value, label.strip()))
    # Preserve source order and avoid repeated rows from codebook page artifacts.
    return list(dict.fromkeys(values))


def normalize(text: str) -> str:
    text = text.lower().replace("oesophagus", "esophagus")
    return re.sub(r"[^a-z0-9]+", "", text)


def main() -> None:
    raw = pd.read_csv(ROOT / "audit" / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
    rows = []
    items = []
    for index, site in enumerate(SITES, start=1):
        concept_id = "reported_cancer_site_" + re.sub(r"[^a-z0-9]+", "_", site.lower()).strip("_")
        concept_label = f"自报癌症部位/既往史：{site}"
        source_fields = []
        for wave in ("2011", "2013", "2015", "2018"):
            code = f"da017s{index}" if wave != "2018" else f"da017_s{index}"
            match = raw[(raw.wave == wave) & raw.variable.str.lower().eq(code.lower())]
            if match.empty:
                raise ValueError(f"Source catalog field not found: {wave} {code}")
            variable_label = str(match.iloc[0].variable_label)
            module = str(match.iloc[0].module)
            labels = codebook_values(wave, code)
            site_values = [(value, label) for value, label in labels if normalize(label) == normalize(site)]
            no_labels = [(value, label) for value, label in labels if label.lower() == "no"]
            if labels and not site_values and not (wave == "2018" and no_labels and all(value == "0" for value, _ in no_labels)):
                raise ValueError(f"Site label mismatch in official codebook: {wave} {code}; expected {site}; got {labels}")
            if not labels:
                response_labels = ""
                status = ("official codebook reports no observed categories; 2011 option position follows baseline questionnaire DA017 list; no affirmative category observed"
                          if wave == "2011" else "official codebook reports no observed categories; option index follows CHARLS questionnaire list; wave-specific confirmation pending")
            elif not site_values:
                response_labels = "; ".join(f"{value}={label}" for value, label in labels)
                status = ("official codebook shows 0=No and no observed affirmative site category; 2011 questionnaire DA017 confirms this site option position"
                          if wave == "2011" else "official codebook shows 0=No and no observed affirmative site category; option index confirmed by questionnaire")
            else:
                response_labels = "; ".join(f"{value}={label}" for value, label in labels)
                status = "official codebook category verified; no frequencies included"
            if wave == "2018" and labels:
                if not no_labels or no_labels[0][0] != "0":
                    raise ValueError(f"Expected official 2018 0=No category for {code}; got {labels}")
            if wave == "2018":
                status += "; questionnaire confirms all-that-apply site item"
            else:
                status += "; preserve wave-specific selected-slot/missing semantics"
            caveat = (
                "Conditional on reported cancer diagnosis/known-history route; includes current or past cancer. "
                "The 2018 question includes primary and metastatic sites, so a selected site does not establish a primary tumor location. "
                "Sparse site categories require sample-size and disclosure review. Do not infer No from a structural skip or unobserved slot."
            )
            rows.append({
                "wave": wave, "code": code, "concept_id": concept_id, "concept_label": concept_label,
                "domain": "chronic disease ancillary", "module": module, "source_label": variable_label,
                "value_labels": response_labels, "value_label_status": status,
                "value_label_source": f"{BOOKS[wave].relative_to(ROOT).as_posix()}; {QUESTIONNAIRES[wave]}",
                "source_archive": ARCHIVES[wave],
                "mapping_status": "official site-specific cancer history item; conditional route; candidate phenotype only",
                "construct": "reported cancer-site history", "subtype": site,
                "caveat": caveat,
            })
            source_fields.append({
                "wave": wave, "code": code, "module": module, "source_label": variable_label,
                "value_labels": response_labels, "value_label_status": status,
                "value_label_source": f"{BOOKS[wave].relative_to(ROOT).as_posix()}; {QUESTIONNAIRES[wave]}",
                "source_archive": ARCHIVES[wave],
            })
        items.append({
            "concept_id": concept_id, "label": concept_label, "domain": "chronic disease ancillary",
            "site": site, "source_fields": source_fields,
            "caveat": "Conditional self-reported cancer site/history item; includes known/ever cancer route. Site choice may include metastasis (explicit in 2018 wording); do not interpret as primary-site incidence or population prevalence. Sparse cells require analysis eligibility and disclosure review.",
        })
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "audit" / "cancer_site_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
    (ROOT / "site-prototype" / "dist" / "cancer_sites_v1.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    assert len(out) == 92 and out.concept_id.nunique() == 23
    assert all(not re.search(r"\b(?:Freq|Obs|Total|\d+\.\d+%)\b", x, re.I) for x in out.value_labels)
    print(f"site-specific cancer history mappings={len(out)}; concepts={out.concept_id.nunique()}; waves={out.wave.nunique()}; labels without frequencies verified")


if __name__ == "__main__":
    main()
