# Wave 1 outcome-rule state inventory

**Date:** 2026-10-30  
**Scope:** Status metadata from the server-private candidate rule JSON only. No CHARLS participant records, outcome values, pair-level QA, or estimates were read.

The current candidate file contains 15 registered outcomes. All 15 remain `candidate_not_frozen`; the proposed default is the original measurement scale, with Stata missing values excluded and finite release values retained without assay-range filtering, subject to methods approval. The finite numeric special-code rule remains unresolved for all 15, so this candidate is not sufficient to open model fitting.

Thirteen outcomes are marked blocked pending common source and methods review. Two fasting-dependent outcomes are additionally blocked by the unresolved Wave 1 `qc1_va003` numeric mapping. Thus 91 registered coefficients are not yet approved, and 14 remain explicitly blocked by the fasting measurement rule. These counts describe registration state only, not fitted or estimable associations.

Official file 138 (`Medical-questionnaire-2011.doc`) has now been retrieved through the direct public-document link on the official CHARLS Wave 1 page and verified against the platform MD5. Read-only review with macros disabled found a 2011 physical-measurement questionnaire but no `qc1_va003`, fasting/空腹 definition, or blood-draw fasting item. It is stored separately from raw data under server-private `source_documents/`. The file does not resolve the fasting-code issue. The independent methods response is also absent. No real-data association was fitted, and the public result payload remains unpublished.

Next gate: resolve each outcome's measurement/special-code policy and obtain a dated, named, hash-bound independent review of the estimator and analysis plan. Until then, preserve the fail-closed model gate.
