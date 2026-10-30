# CHARLS 2011 Medical Questionnaire source status

**Checked:** 2026-10-30  
**Purpose:** Establish whether the official 2011 physical-examination questionnaire is a real source candidate for the unresolved Wave 1 fasting-code lookup. This note records only public documentation metadata and project intake status; it contains no respondent data.

## Official-source identity

The Peking University Open Research Data Platform lists `Medical-questionnaire-2011.doc` as file 138 in the CHARLS 2011 baseline dataset, version 1.1. Its platform metadata describe it as a 747.5 KB MS Word document titled “体检问卷” (physical examination questionnaire), updated 2015-12-25, with MD5 `d1f9351dff8bdadb0d1f692ff58b75c6`. The page attributes the dataset to CHARLS and displays restricted-data terms. See the [official file page](https://opendata.pku.edu.cn/file.xhtml?datasetVersionId=97&fileId=138) and [2011 baseline dataset page](https://opendata.pku.edu.cn/dataset.xhtml?persistentId=doi%3A10.18170%2FDVN%2FIZU8OF&version=1.1).

The official CHARLS Wave 1 page separately lists the baseline Codebook and Blood data, but its public page does not expose the restricted file contents. The file title/metadata establishes that file 138 is a source worth checking; it does **not** establish that it contains the `qc1_va003` fasting code or define that code.

## Project intake and document review

The protected server intake now contains 137 files, including file 138 downloaded from the direct `public_documents` link on CHARLS's official 2011 documentation page. The downloaded document's MD5 is `d1f9351dff8bdadb0d1f692ff58b75c6`, matching the Open Research Data Platform record; its SHA-256 is `42e71dd420d4fe12d2b94b3ccf5ddf047b0ef300d04468b7a89200800bb95074`. The copy is restricted to the server private intake (`0600`). No authentication or access control was bypassed.

The document was opened read-only with macros disabled and searched in full extracted text. Its title and contents identify a 32-page physical-measurement questionnaire (blood pressure, lung function, grip strength, balance, walking speed, anthropometry and related measurements). Searches found no `qc1_va003`, fasting/`空腹` definition, `LI875`, or blood-collection fasting item. `LI875` appears in the separately reviewed `Biomarker-manual-2011.doc` and concerns recent smoking/exercise/alcohol/food before blood-pressure measurement; it is not a blood-sample fasting code.

Therefore file 138 does not resolve the numeric fasting mapping in the reviewed content. Do not substitute Wave 3 `bl_fasting` codes or infer values from `LI875`; keep the 14 Wave 1 glucose/triglyceride coefficients blocked unless an authoritative Wave 1 mapping is found.

## What this does and does not change

- This closes the file-138 source-identity and content check: it is the official 2011 physical-examination questionnaire, but it does not define the blood-draw fasting code in the reviewed text.
- It does not approve any outcome rule, change the 105-pair registration, or permit model fitting.
- The current Wave 1 outcome crosswalk alignment and source review remain unchanged: 15 mapped fields; finite-value/special-code handling and outcome rules still need adjudication; 14 fasting-dependent coefficients remain blocked.
- The independent methods-review gate remains outstanding.
