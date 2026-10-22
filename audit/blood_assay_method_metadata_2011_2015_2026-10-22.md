# CHARLS blood assay metadata audit (2011 vs 2015)

## Scope and source basis

This is a metadata-only audit. It does not inspect respondent records or estimate associations. The 2011 assay details below were transcribed from the official [2011 Blood Data Users' Guide](../sources_official/CHARLS_2011_Blood_User_Guide.pdf), Table 2 (printed p. 7; PDF p. 12). The 2015 field definitions and displayed units were checked against the official [2015 Blood Data Release Note](../sources_official/CHARLS_2015_Blood_Release_Note.pdf), Table 1 (PDF p. 5).

The 2011 guide's table column is titled “Detection limits.” The website stores and labels these as **guide-reported detection ranges**; this audit does not reinterpret the ranges as limits of detection (LOD). CV values retain the guide's inequality signs and reported precision.

## 2011 assay table

| Concept | Method in 2011 guide | Within-assay CV | Between-assay CV | Guide-reported detection range |
|---|---|---:|---:|---:|
| hsCRP | Immunoturbidimetric assay | <1.3% | <5.7% | 0.1–20 mg/L |
| HbA1c | Boronate affinity HPLC | 1.90% | 2.10% | 0–40% |
| Total cholesterol | Enzymatic colorimetric test | 0.80% | 1.70% | 3–800 mg/dL |
| HDL-C | Enzymatic colorimetric test | 1.00% | 1.30% | 3–120 mg/dL |
| LDL-C | Enzymatic colorimetric test | 0.70% | 1.20% | 3–400 mg/dL |
| Triglycerides | Enzymatic colorimetric test | 1.50% | 1.80% | 4–1000 mg/dL |
| BUN | Enzymatic UV method with urease | <4.4% | <4.1% | 5–100 mg/dL |
| Creatinine | Rate-blanked and compensated Jaffe method | <1.6% | <2.1% | 0.1–25 mg/dL |
| Glucose | Enzymatic colorimetric test | 0.90% | 1.80% | 2–450 mg/dL |
| Uric acid | UA Plus method | 1.10% | 1.90% | up to 20 mg/dL |
| Cystatin C | Particle-enhanced turbidimetric assay | <5% | <5% | 0.5–8 mg/L |

The same guide says CBC testing took place in county laboratories, but its analyte-specific methods/CV/range table does not cover the five CBC measures mapped here. The catalogue therefore reports the absence of per-analyte assay details instead of implying a centralized method or borrowing chemistry details.

## 2015 boundary

The 2015 release note provides variable names, descriptions, units, fasting status and a triglyceride top-coding flag. It does not provide analyte-level assay method, within/between CV or detection range in the cited table. All 2015 rows leave these fields blank and display that the source does not report them. In particular, 2011 methods and performance values must not be copied into the 2015 wave.

The release note's source spelling is preserved in a separate `source_unit_text` field where it differs from the display unit. Examples include WBC (“1000”) and MCV (“fl”) in 2015; the 2011 guide says WBC “in thousands” and does not state MCV units in its CBC summary table. Any normalized display unit is a presentation convention, not evidence that assay protocols were equivalent.

## Analysis implications

- Keep assay metadata wave-specific. Same concept, unit or variable label does not establish comparability across 2011 and 2015.
- Retain 2015 fasting information and triglyceride top-code flag as interpretation/quality metadata, not outcomes.
- The 2011 cystatin C age-stratified subsample still requires selection and weight review; this metadata table does not validate coverage by `bloodweight`.
- Laboratory measurements are internal clinical/physiological measures and remain phenotype candidates in the reviewed source crosswalk. They are not environmental contaminant measurements.
- The website remains a variable lookup, not a result atlas: no participant-level data, sample sizes, p-values or association claims are published.

The generated fields are in `audit/blood_biomarker_crosswalk_v1.csv` and `site-prototype/dist/blood_biomarkers_v1.json`; the generation logic is `scripts/build_blood_biomarker_crosswalk.py`.
