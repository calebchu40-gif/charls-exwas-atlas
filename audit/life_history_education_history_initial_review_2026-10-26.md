# 2014 Life History EDUCATIONHISTORY initial review (2026-10-26)

## Scope

The initial source review compared the official questionnaire's E000–E011 items with matching Codebook fields and mapped 33 fields in five concepts. Subsequent batches reviewed the remaining module, including five E134 acquisition-year fields, and the current ledger now gives each of the 1,105 fields an explicit mapping or non-E/P disposition. The five E134 fields are mapped only as certificate-acquisition year components; certificate names are open text absent from the Codebook inventory and no credential identity is inferred. See the current coverage ledger `life_history_education_history_coverage_2014_v1.csv` and `life_history_skill_certificate_year_review_2026-10-26.md`.

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

The current 1,105-row ledger gives every field a single status. The earlier 33-field E000–E011 snapshot above is only the first source-review batch, not the current module total:

| Disposition | Fields | Meaning |
|---|---:|---|
| Mapped candidate | 1,077 | Source-reviewed candidate fields across the full Education History module |
| Sensitive geography excluded | 22 | Location-specific fields withheld from the public candidate mapping |
| Linkage keys | 3 | Controlled joins only when authorized and needed |
| No-observation field | 1 | Codebook has no respondent observations for this field |
| Data-quality field | 1 | Interview/check metadata, not an E/P measure |
| Version metadata | 1 | Release bookkeeping |
| Deferred source review | 0 | No substantive Codebook field remains generically unreviewed |
| **Total** | **1,105** | **One explicit disposition for each Codebook field** |

## Reproducibility and privacy

`scripts/build_life_history_exposure_crosswalk.py` produces the 1,105-row inventory and includes source-reviewed fields in the public JSON. Institutional names, addresses, participant records and Codebook frequency tables are not included. The 33-field E000–E011 map remains identifiable as the initial batch; the current ledger reflects later module-level review.

