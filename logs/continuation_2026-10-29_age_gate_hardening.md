# Continuation log — official age-source gate hardening

Date: 2026-10-29 (Asia/Shanghai)

Current plan, repository, local protected intakes, server private directories/intake, GitHub main and Pages were rechecked before work. Wave 1 official files remain in the designated protected intake; server private directories are owner-only; Pages responds HTTP 200.

Static review of the 2011 historical pilot confirmed that its age covariate is a provisional Harmonized CHARLS D candidate. Existing readiness asked for an age-domain decision but did not separately require evidence that the age field/derivation itself was official and validated. Added a required `official_age_source_and_derivation` gate to every Wave 1 readiness path, requiring official source tier, field, derivation method, source anchor and validation evidence. Included the readiness schema in the applicable plan fingerprint so prior approvals cannot carry forward across this change. The new gate remains unresolved; no age was derived and no real model was run.

Committed/pushed public code and documentation as f6d9264. `git diff --check` passed before commit; no tests were run. No participant records or private QA were used.

## Current-state recheck — 2026-10-29 21:38 Asia/Shanghai

- Rechecked the repository at `c1f931e` (same as `origin/main`), the active plan, protected local intake, the server project, and the public Pages site. SSH alias `myserver` is reachable; Wave 1 source files remain in the protected local intake and server `private/incoming_2011_official/`. Server Wave 2 All Data/weights and Wave 3 sample-information/weights/blood packages are also present in private intake locations. This was a presence check only; it did not reread participant values or rerun analyses.
- Server active plan still reports the Wave 1 design gate open and formal associations at zero. The age derivation/conversion and final PSU/variance design remain unresolved; Stata is not installed in the checked local shell. No real-data model or test was run.
- Public Pages home and candidate-pair JSON returned HTTP 200; live `app.js` is v194 and `association_results_v1.json` returned HTTP 404. Updated the repository README and active plan so the present input/site state is easy to distinguish from dated historical paragraphs that still mention missing inputs.
- GitHub Actions for commit `844e376` exposed an omitted allowlist entry for the public metadata-only wave/module gate crosswalk CSV. Reviewed the CSV schema and its catalog-only generator, added the exact path to the repository's delimited-text allowlist, and confirmed the repository boundary guard passes locally. The prior two validation runs had failed at this same boundary step; no participant-level file was involved.
