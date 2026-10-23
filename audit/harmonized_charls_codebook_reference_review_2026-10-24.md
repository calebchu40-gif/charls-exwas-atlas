# Harmonized CHARLS D codebook as a secondary harmonization reference

Review date: 2026-10-24. This is a documentation-only review of the CHARLS-hosted Harmonized CHARLS Version D codebook and the Gateway to Global Aging Data creation-code page. No Harmonized CHARLS or respondent-level dataset was downloaded or inspected. Descriptive statistics and frequency tables printed in the codebook were intentionally excluded from this review.

## Why this reference matters

The CHARLS data page lists Harmonized CHARLS Version D (June 2021), covering regular Waves 1–4 (2011–2018), with its codebook and creation code. The Gateway creation-code page separately describes a D.2 creation workflow using Waves 1–4 plus the 2014 Life History Survey and states that D.2 has 4,507 variables. These are distinct release descriptions: do not label the 2021 D codebook as D.2, do not assume it covers Wave 5, and record the version whenever its definitions are used.

The codebook is valuable as a second-source crosswalk because each concept documents construction, raw CHARLS inputs, within-study wave differences, and differences from other HRS-family harmonized measures. It is a derived harmonization product rather than a replacement for the wave-specific CHARLS questionnaire, Codebook, release note, or sampling files. A same-named Harmonized variable does not by itself prove equivalence of the underlying CHARLS questions or eligibility.

## Relevant crosswalk findings

| Analysis concept | Harmonized CHARLS D reference | Source-backed interpretation and use in this project |
|---|---|---|
| Age | `R1AGEY`–`R4AGEY`; derived birth-date group `RABYEAR`, `RABMONTH`, `RABDAY`; `IMONTH`, `IYEAR` | The codebook says age uses the most recently reported birth year/month and interview year/month; lunar dates are converted to solar dates, and missing birth year can be derived from reported age and interview year. The documented age calculation does not use interview day or birth day, so do not describe it as exact day-level completed age. Waves 1–2 ask age directly; Waves 3–4 use ID/hukou and actual birth-date routes. Retain this as a cross-check for our age construction, not a drop-in replacement. Preserve the date-source flags and special missing/failed-conversion values. |
| Gender | `RAGENDER`; `RAFGENDR` decision flag; spouse fields `S1GENDER`–`S4GENDER` | Wave 1 uses the demographic report; later waves may have demographic and health-module reports. The harmonized variable selects the most consistent report, and the flag records how conflicts were resolved. This supports our requirement to inspect module conflicts and not silently choose one raw field. It is a person-level harmonized result, not a wave-specific raw source code. |
| Community urban/rural context | `H1RURAL`–`H4RURAL` | The codebook defines this from PSU/community information and NBS urban/rural classification. Keep it separate from self-reported hukou or personal residence. This does not identify the design stratum used for variance estimation. |
| Hukou urban/rural category | `R1RURAL2`–`R4RURAL2`, built from `RwHUKOU` | This is the respondent's hukou type, not current residential location or community urbanicity. The codebook describes prior-wave carry-forward and unresolved Wave 4 disputes. Preserve change, dispute, and missingness routes; do not merge it with `H*RURAL`. |
| Self-rated health | `R1SHLT`–`R3SHLT`; alternate scale `R1SHLTA`–`R4SHLTA` | The U.S.-comparable `SHLT` question is absent in Wave 4, while the alternate CHARLS scale remains. This supports keeping the 2011–2018 scale variants distinct, as the project catalogue already does. Do not create a single cross-wave ordinal variable without an explicit, justified recode and sensitivity analysis. |
| Measured BMI | `R1MBMI`–`R3MBMI`; Asian BMI category `R1MBMICATA`–`R3MBMICATA` | The codebook says BMI is derived from measured weight and height, and documents measurement eligibility/noncompletion special-missing states. It warns that some extreme height/weight/waist values remain for users to assess. Use as a comparison aid for source fields, derivation and measurement gates; do not import its category cut-points without reconciling the exact official CHARLS source and project estimand. |
| Functional limitation | `RwADLA_C` (four-item ADL summary) | The `_C` suffix flags a CHARLS-specific difference from the HRS measure, including different component items. It illustrates why harmonized labels and apparent naming similarity cannot replace raw-field/scale review. |

The field-level references and wave scope are summarized in [`harmonized_charls_secondary_crosswalk_v1.csv`](harmonized_charls_secondary_crosswalk_v1.csv). The CSV stores documentation mappings only; it contains no observed frequencies, sample counts, or respondent values.

## Survey-design implications

The codebook says CHARLS is a stratified, multistage, PPS sample; it describes stratification by per-capita GDP in urban districts and rural counties and identifies administrative villages/neighborhoods as PSUs. Its weighting chapter distinguishes household, person, biomarker, and longitudinal weights and says design-adjusted standard errors can be produced where the required design information is provided by CHARLS. The reviewed text does not name a released variance-stratum field or provide an exact variance-estimation specification. Therefore this improves the documented design context but does not close the project's stratum/variance gate; do not reconstruct a stratum from GDP, county, province, rural/urban status, or `communityID`.

The codebook describes the selected age-eligible person (45+) as the main respondent and says the spouse is also interviewed regardless of age; ages 40–44 may be held as refreshment sample members. Therefore an analysis targeting people aged 45+ must explicitly define eligible records and the applicable weights; “interviewed in CHARLS” is not itself proof that every record belongs to the same target population. Institutionalized people are not sampled at baseline, though previously enrolled people may be followed after entering an institution. Proxy interviews may occur for frail eligible respondents. These distinctions belong in the sample-flow and estimand definitions.

## Missing values and permissions

Harmonized CHARLS documents separate special missing values for wave nonresponse, age ineligibility, don't know, refusal, routing skip, no children, not applicable, spouse/marital states, and other missing. Those Stata special-missing codes are not the same thing as raw CHARLS release codes; they are a reminder that the project's wave/module eligibility, refusal, and structural-skip categories must remain distinct.

The 828-page codebook contains descriptive statistics and category frequencies. None were transcribed into the catalog, website, or this review. The harmonized dataset itself remains subject to CHARLS registration and data-use conditions; it was not downloaded, copied, or added to the public repository.

## Source and local availability

- Official CHARLS Harmonized Data page: <https://charls.charlsdata.com/pages/Data/harmonized_charls/en.html>. It lists Harmonized CHARLS Version D as of June 2021 and gives the codebook SHA-1 `AF828E94462F26F56CB0B2C188A9C3DAD5CFCAC0` and creation-code SHA-1 `F6FE3E49A9A1D5709E5BA5A6D1B90DD91051BE34`.
- Codebook PDF: <https://charls.charlsdata.com/Public/ashelf/public/uploads/document/harmonized_charls/application/Harmonized_CHARLS_D.pdf>.
- Gateway creation-code description: <https://g2aging.org/harmonized-charls/creation-code>.

The source was read through the official online codebook. A local PDF download attempt failed at the source TLS connection and no local copy is claimed; the SHA-1 values above are the values printed on the CHARLS page, not locally recomputed hashes.

## What changes in our workflow

1. For age, gender, residence, self-rated health, measured BMI, and function, consult this codebook as a secondary mapping reference and retain its construction flags/route caveats in the source audit.
2. Keep raw CHARLS code and wave labels primary; preserve distinct concepts when questionnaires or measurement protocols differ, even if Harmonized CHARLS uses related variables.
3. Add no Wave 5 value from Harmonized CHARLS D, and add no sample size, frequency, or distribution from its codebook.
4. Keep the design-variance and target-population gates open until the actual released design files and the applicable analysis instructions are verified.
