# CHARLS 2011 community weather estimates: source review

Updated 2026-10-24. This is a metadata-only review based on the official CHARLS 2011 Community Questionnaire and Codebook. No community responses, codebook frequencies, summary statistics, or linked external weather data are used.

The questionnaire asks a community informant about the prior calendar year (2010): `JA039_1` lowest temperature and `JA039_2` highest temperature, both in degrees Celsius; `JA040` rainy days and `JA041` snowy days, both in days. These remain four separate numeric fields under one searchable community-weather concept. They are estimates reported for the village/community, not station-linked meteorological observations, measured personal exposures, or a continuous individual weather dose.

The catalogue now shows field-specific units and caveats. Before any analysis, verify the respondent/informant route, special missing-value codes, plausible ranges, community-person linkage, clustering and the intended estimand. Do not silently aggregate these estimates into a climate score, impute station data, or assign them as personal dose.

## Official source files

- `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt`, Part A, printed pp. 7–8 (PDF pp. 10–11), items JA039–JA041.
- `sources_official/CHARLS_2011_Codebook_extracted.txt`, official field labels for `ja039_1`, `ja039_2`, `ja040`, `ja041`; descriptive statistics were not copied.
- Reproducible catalogue: `scripts/build_community_exposure_crosswalk.py`; outputs `audit/community_exposure_crosswalk_v1.csv` and `site-prototype/dist/community_exposures_v1.json`.
