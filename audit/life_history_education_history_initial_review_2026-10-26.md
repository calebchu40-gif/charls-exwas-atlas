# 2014 Life History EDUCATIONHISTORY initial review (2026-10-26)

## Scope

Compared the first EDUCATION HISTORY section of the official questionnaire (items E000–E011) with matching Codebook fields. The module has 1,105 Codebook fields. This initial batch reviews 33 fields in five concepts. It does **not** claim full review of the 1,105-field module: the remaining 1,068 substantive fields are explicitly marked `deferred_source_review` in `life_history_education_history_coverage_2014_v1.csv` and are excluded from the public candidate directory until reviewed.

## Candidate concepts

| Concept | Fields | Definition and route |
|---|---:|---|
| Educational stages ever attended | 12 | E000 checklist spans home school through PhD plus a none option. The none marker is a checklist response, not an attainment level; completion, duration and age at attendance are not inferred. `errore000` prior-wave consistency check is deferred. |
| Self-reported ability to read or write | 1 | E001 literacy item, routed according to E000 selections; social/educational context rather than a validated cognitive phenotype. |
| School attendance and interruption during the Cultural Revolution | 7 | E002–E003a; only respondents born 1946–1961 inclusive. E003 closure dates are conditional; E003a is skipped when E002=Yes. |
| Interruption and return during a school stage | 9 | E004/E005; interruption means leaving for at least one semester and returning. Gaps between school stages are explicitly excluded. E005 is conditional on E004=Yes. |
| School-dormitory residence during primary through high school | 4 | E010/E011; E011 is conditional on Yes and selects school stage. Questionnaire definition also mentions staying with nearby relatives/friends. This is a broad residential context, not a measured housing condition. |

These are retrospective, self-reported educational/social context candidates. They are not automatically selected as model covariates or causal exposures; authorized-release storage, special values, and skip semantics need data-level QA before analysis.

## Module inventory status

The 1,105-row ledger gives every field a single status:

| Disposition | Fields | Meaning |
|---|---:|---|
| Mapped candidate | 33 | Source-checked E000–E011 concepts above |
| Deferred source review | 1,068 | Not yet checked field-by-field against the questionnaire for routing, referent, free text, privacy and repeated-episode structure; excluded from candidate catalog and analysis |
| Linkage keys | 3 | Controlled joins only when authorized and needed |
| Version metadata | 1 | Release bookkeeping |
| **Total** | **1,105** | **One explicit disposition for each Codebook field** |

## Reproducibility and privacy

`scripts/build_life_history_exposure_crosswalk.py` produces the 1,105-row inventory and only puts the 33 reviewed fields in the public JSON. Institutional names, addresses, participant records and Codebook frequency tables are not included. This is an initial Education History batch, not module completion.

