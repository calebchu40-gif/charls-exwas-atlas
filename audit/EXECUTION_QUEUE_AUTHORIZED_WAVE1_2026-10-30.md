# Authorized Wave 1 execution queue and current gates

**Status date:** 2026-10-30  
**Purpose:** Operational queue after the user confirmed ownership/authorization of CHARLS items 123/117/118/201, selected the community-clustered no-strata Taylor approximation (Option A), and authorized private-server analysis.

## Controlling decisions

- Official Wave 1 inputs are authorized for this project. Their identity and metadata preflight are recorded in the private source manifest. No access credentials are stored in the repository.
- Individual-level data, pair-level counts, exact QA and model results stay under the server's owner-only `private/` tree. Only reviewed, disclosure-cleared aggregates may be copied to the public site.
- Option A is the user's chosen **approximate** variance plan: released `communityID` PSU, no invented strata or FPC, with-replacement Taylor linearization. It omits known features of CHARLS's multistage PPS design and the respondent-to-final-subcommunity membership map. It is not the full CHARLS design and is not known to be conservative.
- The operational pilot registry is the fixed 105 coefficients: one `i017` contrast plus six `i022` fuel contrasts, each across 15 routine blood outcomes. The two fasting-dependent outcomes remain registered but blocked until Wave 1 fasting coding is documented. The pilot is nested inside K=150; final multiplicity counts 240 unique K150/K90 coefficients once.
- Age-domain implementation follows the current recorded candidate: retain the full blood-target frame in the design, estimate the lower-bound age-45+ domain as primary, and predeclare upper-bound age-45+ plus full blood-target sensitivities. This still requires a frozen plan and methods review. It is not a claim about all Chinese adults aged 45+.

## Completed prerequisites

1. Source identity confirmed by the user and stored in the protected manifest; metadata-only preflight succeeded.
2. The Wave 1 person table and Blood-to-`bloodweight` linkage were reconstructed and source-bound in private storage.
3. The lunar date converter was compared against the official CHARLS mapping tables. A private age-interval candidate and aggregate QA exist; uncertain ages are not silently assigned to either side of 45.
4. The 105-coefficient availability audit was run privately. It is availability QA only, not model N, valid-outcome screening, or association evidence.
5. Header review found no attached value-label sets on the planned Blood outcome fields or `qc1_va003`. The official materials reviewed do not map Wave 1 fasting numeric codes.
6. Static registry review confirms 150 K150 + 90 K90 = 240 unique coefficients and the pilot is nested in K150.

## Work queue and stop conditions

### W1 — Outcome data-quality profile (now; private only)

Read only the 15 predeclared outcome columns from the authorized Blood file. Produce a restricted aggregate profile (missing/nonfinite counts, quantiles, range and tail flags) in server `private/qa_outputs/`, mode 600. Do not print the profile, infer fasting codes, declare validity cutoffs from the observed distribution, winsorize, or publish the file. The profile can identify anomalies that need source-based adjudication; it cannot itself authorize exclusions.

### W2 — Freeze source-based outcome rules and age/frame semantics

For every outcome record source field, unit, storage type, Stata missing handling, any documented special codes, measurement/assay caveat, transformation (default none), and unresolved issue. If official sources do not define a numeric validity boundary, retain that uncertainty explicitly; do not invent one from quantiles or assay detection range. Reconcile the age target and frame against the frozen 45+ domain decision. Keep fasting-dependent outcomes blocked until an authoritative Wave 1 mapping is available.

### W3 — Freeze estimator and diagnostic rules

Bind the full frame, domain indicator, `bloodweight`, community PSU, no-strata WR Taylor approximation, coefficient IDs, M1 primary formula, M2 sensitivity formula, multiplicity family, singleton-PSU rule, degrees-of-freedom handling, effect scales, and sensitivity analysis to source and prepared-table hashes. Add a clear caution that results are approximate and that the final subcommunity PSU map is unavailable.

### W4 — Review gate before association fitting

Generate a concise private review packet with the source manifests, age and frame logic, exact analysis configuration, code commit, restricted QA references, and a checklist of unresolved points. Association fitting remains fail-closed until all computational gates pass and an independent methods review is recorded. This is a real gate; an internal code check is not represented as independent review.

### W5 — Pilot and expansion

After W4 approval, fit the fixed 105-coefficient pilot privately, run model/weight/PSU/singleton/influence diagnostics and predeclared sensitivities, then review reproducibility. If sound, run remaining K150/K90 coefficients without duplicating the pilot; apply the frozen family-wide correction once. Continue wave-specific source/frame/weight/design review before adding other waves.

### W6 — Release

Prepare only disclosure-cleared aggregate outputs for the site. Confirm result files, cell thresholds, suppression and metadata before enabling the public result endpoint. Validate the deployed pages and record the public commit and URL.

## Immediate schedule

- **Current work session:** complete W1 and the source reconciliation document; append local and private server logs; sync only code and public-safe documentation.
- **Next execution block:** complete W2/W3 and assemble W4 review packet. These are the critical path; no batch fitting is allowed while review is pending.
- **After review approval:** first model run and full QA; then K150/K90 expansion. Server compute time is not expected to dominate; official documentation gaps and review decisions are the uncertain calendar-time items.

## Progress reporting

Keep the project goal and recurring continuation active. Report only material advances, a gate that requires the user's action, a failure, or completion. Do not label data preparation, synthetic runs or value profiles as fitted CHARLS associations. Current public formal-association count remains **0** until W4 is approved and a real model completes.
