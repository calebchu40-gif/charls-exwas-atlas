# CHARLS 2011 Medical Questionnaire source status

**Checked:** 2026-10-30  
**Purpose:** Establish whether the official 2011 physical-examination questionnaire is a real source candidate for the unresolved Wave 1 fasting-code lookup. This note records only public documentation metadata and project intake status; it contains no respondent data.

## Official-source identity

The Peking University Open Research Data Platform lists `Medical-questionnaire-2011.doc` as file 138 in the CHARLS 2011 baseline dataset, version 1.1. Its platform metadata describe it as a 747.5 KB MS Word document titled “体检问卷” (physical examination questionnaire), updated 2015-12-25, with MD5 `d1f9351dff8bdadb0d1f692ff58b75c6`. The page attributes the dataset to CHARLS and displays restricted-data terms. See the [official file page](https://opendata.pku.edu.cn/file.xhtml?datasetVersionId=97&fileId=138) and [2011 baseline dataset page](https://opendata.pku.edu.cn/dataset.xhtml?persistentId=doi%3A10.18170%2FDVN%2FIZU8OF&version=1.1).

The official CHARLS Wave 1 page separately lists the baseline Codebook and Blood data, but its public page does not expose the restricted file contents. The file title/metadata establishes that file 138 is a source worth checking; it does **not** establish that it contains the `qc1_va003` fasting code or define that code.

## Project intake status and next source check

At this check, the protected server intake inventory contains 136 files and does not contain `Medical-questionnaire-2011.doc`. The private intake manifest and source inventory therefore do not claim that file 138 was obtained or reviewed. No download was attempted through an unauthenticated route, and no access control was bypassed.

If the authorized account holder later downloads file 138 through the official platform and places it in the approved private intake, first verify its official MD5 and file identity, then inspect only the questionnaire wording and variable mapping for `qc1_va003` (not participant records). If it contains no mapping, retain the fasting-rule block. Do not substitute Wave 3 `bl_fasting` codes or infer values from `LI875`.

## What this does and does not change

- This closes a source-discovery question: official file 138 exists and is specifically the 2011 physical-examination questionnaire.
- It does not resolve the fasting code, approve any outcome rule, change the 105-pair registration, or permit model fitting.
- The current Wave 1 outcome crosswalk alignment and source review remain unchanged: 15 mapped fields; finite-value/special-code handling and outcome rules still need adjudication; 14 fasting-dependent coefficients remain blocked.
- The independent methods-review gate remains outstanding.
