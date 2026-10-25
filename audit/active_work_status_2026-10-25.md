# CHARLS ExWAS Atlas active work status (2026-10-25)

## Delivered and live

- Public metadata atlas and candidate-pair explorer: <https://calebchu40-gif.github.io/charls-exwas-atlas/>.
- Current generated catalogue: 1,486 deduplicated E/P concepts (1,208 exposure, 303 phenotype, 25 dual-role), 6,821 E/P concept-to-source-field links, and five survey waves (2011–2020). These are metadata counts, not measured association counts or analytic sample sizes.
- No formal association model or actual pairwise analytic N has been produced. The public site contains metadata only.
- The current 92 `DO NOT ANALYZE` locks remain aligned with the triage inventory. Generic pending value-label status is zero across E/P/C; source-specific route, release-version, and design caveats still apply.

## Latest work

Commit `762596d` adds a fail-closed allowlist for the GitHub Pages payload. The deploy requires non-empty entry-point files, allows only known browser asset types, rejects statistical-data/archive/unknown file extensions, and parses JSON recursively. Four focused tests and all 421 local Python tests passed. GitHub Pages Deploy #208 succeeded; the public homepage returned HTTP 200. GitHub Validate #424's `validate` and `synthetic-survey-engine` jobs both reported success on their job pages. Details: [`public_pages_payload_guard_2026-10-25.md`](public_pages_payload_guard_2026-10-25.md).

## Main analysis gate

The official CHARLS 2013 `Weights.dta` is still absent from the protected local intake directory. The existing 2013 prepared table lacks the official `crosssection` and `longitudinal` flags, so 2013 sample eligibility cannot be reconstructed and analysis stays blocked. The checksum-pinned, fail-closed merge script is ready for the authorized official file. No credentials were used and no restricted portal access was attempted. Wave-specific variance design and biomarker eligibility/weights also need source confirmation; do not infer strata from geography or apply a weight beyond its official target population.

## Next work

Continue source-backed field and wave-coverage review, update reproducible metadata/build documentation, and maintain the synthetic survey-engine checks. When the official 2013 weight file becomes available through an authorized CHARLS account, verify its release checksum, merge only the official flags/weights, run aggregate-only QA in protected local storage, and reassess wave-specific analysis gates. Only after those gates are documented should the first E/P model family be frozen and fitted. Do not publish participant-level records or unreviewed association results.

## Repository state

Branch `main`, GitHub repository `calebchu40-gif/charls-exwas-atlas`. All source/metadata changes are recorded in GitHub; restricted participant-level data stay outside the repository and public site.
