# CHARLS ExWAS Atlas active work status (2026-10-25)

## Delivered and live

- Public metadata atlas and candidate-pair explorer: <https://calebchu40-gif.github.io/charls-exwas-atlas/>.
- Current generated catalogue: 1,486 deduplicated E/P concepts (1,208 exposure, 303 phenotype, 25 dual-role), 6,821 E/P concept-to-source-field links, and five survey waves (2011–2020). These are metadata counts, not measured association counts or analytic sample sizes.
- No formal association model or actual pairwise analytic N has been produced. The public site contains metadata only.
- The current 92 `DO NOT ANALYZE` locks remain aligned with the triage inventory. Generic pending value-label status is zero across E/P/C; source-specific route, release-version, and design caveats still apply.

## Latest work

The latest metadata review adds the official 2011 National Baseline User Guide's labor-module coding context to the FM055 pastime-job review. The guide describes six-digit GB occupation codes (with added categories) and two-digit industry codes, while FM055 is an open-text current paid pastime item asked after FM054=Yes. The 2011 Codebook names `fm055_gb`, `fm055_isco`, and `fm055_indc`, but the guide does not provide the FM055-specific lookup/version or explain its ISCO child mapping. The three fields therefore retain separate source notes and `DO NOT ANALYZE` status. This distinction is covered by regression tests. Full metadata finalization passed; the catalogue remains 1,486 E/P concepts and 6,821 E/P source links, with 92 locks and zero generic pending E/P labels. The wave-specific pair explorer lists metadata co-availability only, not analytic N or association findings. All 421 Python tests, public-payload validation, JSON/JS syntax checks, and lock validation passed. See [`pastime_job_classification_review_2026-10-25.md`](pastime_job_classification_review_2026-10-25.md).

A follow-on consistency pass updated the top-level DO NOT ANALYZE triage so it reflects this guide evidence without implying the three fields are resolved. The targeted 45-test catalog suite and complete 421-test suite passed; public-payload validation, all 92 lock checks, JavaScript syntax, and `git diff --check` passed. Commit `58f304c` was pushed; GitHub Validate #428 and Pages Deploy #210 both succeeded, and live homepage/catalog requests returned HTTP 200. Change log: [`CHANGELOG.md`](../CHANGELOG.md).

Commit `762596d` adds a fail-closed allowlist for the GitHub Pages payload. The deploy requires non-empty entry-point files, allows only known browser asset types, rejects statistical-data/archive/unknown file extensions, and parses JSON recursively. Four focused tests and all 421 local Python tests passed. GitHub Pages Deploy #208 succeeded; the public homepage returned HTTP 200. GitHub Validate #424's `validate` and `synthetic-survey-engine` jobs both reported success on their job pages. Details: [`public_pages_payload_guard_2026-10-25.md`](public_pages_payload_guard_2026-10-25.md).

## Main analysis gate

The official CHARLS 2013 `Weights.dta` is still absent from the protected local intake directory; a current name-only scan found the prepared 2013/2015 person tables but no original 2013/2015 archive or official weight file there. The existing 2013 prepared table lacks the official `crosssection` and `longitudinal` flags, so 2013 sample eligibility cannot be reconstructed and analysis stays blocked. The checksum-pinned, fail-closed merge script is ready for the authorized official `.dta`. The Peking University Open Research Data Platform separately lists a restricted `Weights.tab` artifact (19 fields, 19,679 rows, page-reported MD5 `fe914ea9ba15da968c756217587e5d4b`); it must not be substituted into the `.dta` intake path without source/version/field-definition validation. The intake instructions record both routes. No credentials were used and no restricted portal access was attempted. Wave-specific variance design and biomarker eligibility/weights also need source confirmation; do not infer strata from geography or apply a weight beyond its official target population.

## Next work

Continue source-backed field and wave-coverage review, update reproducible metadata/build documentation, and maintain the synthetic survey-engine checks. When the official 2013 weight file becomes available through an authorized CHARLS account, verify its release checksum, merge only the official flags/weights, run aggregate-only QA in protected local storage, and reassess wave-specific analysis gates. Only after those gates are documented should the first E/P model family be frozen and fitted. Do not publish participant-level records or unreviewed association results.

## Repository state

Branch `main`, GitHub repository `calebchu40-gif/charls-exwas-atlas`. All source/metadata changes are recorded in GitHub; restricted participant-level data stay outside the repository and public site.
