# CHARLS pilot success criteria and scale-up sequence

**Purpose.** Decide whether the Wave 1 pilot is ready to scale based on source integrity, survey-design validity, reproducibility, and disclosure review. Statistical significance is not a criterion for calling the pilot successful.

**CHARLS use boundary.** The official [data-use agreement](https://charls.charlsdata.com/users/sign_up/agreement/en.html) restricts the data to academic research, prohibits publishing original microdata, and requires analytical results not to identify individual respondents. It also prohibits granting other people access to the data. Therefore, code and documentation may be public, but participant-level source/derived data and restricted outputs must stay within the authorized user's protected workspace; only approved non-identifying aggregate results may be considered for release.

## Current position

- The local 2011 pilot scripts run on an existing derived table, but their outputs remain exploratory and private.
- The official Wave 1 all-data ZIP, PSU, Weight, and Blood inputs have not been staged in the protected intake folder.
- Aggregate-only preflight found that the local derived frame does not reconcile to the official blood-guide target denominator. It also found incomplete candidate-age and bloodweight coverage. Exact counts are in the protected local report, not this repository.
- The candidate PSU key map joins to the derived table, but its provenance, final PSU definition, split-community treatment, and variance-stratum status are not authenticated.
- Formal, reviewed associations in the public result set remain zero.

## What counts as a successful pilot

All of these gates must pass before expanding beyond the predeclared Wave 1 pilot family:

1. **Source gate:** retain the official download evidence and identify exact release/version for the full Wave 1, PSU, Weight, and Blood inputs. Verify module identity, join keys, and source fields. A locally computed hash documents the received bytes; it does not replace an official source or checksum.
2. **Frame gate:** reproduce the official blood-target/person frame and reconcile row/ID coverage against the guide and released eligibility fields. Explain any exclusions or unmatched records. Rebuild age and respondent/spouse eligibility from official fields if the current derived candidates are incomplete.
3. **Weight gate:** document which released weight is appropriate for blood response, who receives a valid weight, how nonresponse is encoded, and whether the intended age domain is supported. Do not replace missing weights with a general interview weight or zero without a source-based reason.
4. **Design gate:** verify the final PSU and any released variance strata/Sample Info fields. Record how the 30 split communities map to the final sampling units. If no official variance-stratum field or variance instructions can be found, seek authoritative clarification and explicitly limit inference; do not infer strata from province, region, urbanicity, or other correlates.
5. **Frozen-analysis gate:** preserve the predeclared primary family of 105 water/fuel × blood-analyte contrasts and the separate M1/M2 roles. Define treatment of non-estimable pairs before fitting and retain them in the output. Run age≥45 as a domain within the full valid design frame, not by deleting younger spouses before design construction.
6. **Estimation gate:** require correct convergence/estimation status, finite estimates and design-based uncertainty, adequate PSU support for the declared design, interpretable degrees of freedom, and explicit warnings for unstable or unsupported terms. Reproduce selected predeclared coefficients with a second established survey-analysis implementation after the design is verified. Keep pair-level sample counts and support details private unless disclosure review approves release.
7. **Multiplicity and interpretation gate:** adjust the complete predeclared family (BY-FDR and Bonferroni as already specified), without dropping failed or null pairs. Pilot success means the analysis is valid and reproducible; it does not require any association to pass an FDR threshold.
8. **Release gate:** independent methods review and CHARLS disclosure review must approve each aggregate result table before website integration. Never publish participant-level rows, identifiers, microdata, or small-cell diagnostics.

## Go / no-go decisions

| Outcome | Decision | Next action |
|---|---|---|
| Official files absent or source identity unverified | No-go for new association fitting | Continue documentation, catalogue mapping, release-safe site work, and local code preparation; rerun intake preflight when authorized files arrive. |
| Frame, age, weight, PSU, or variance gate unresolved | No-go for national-representative claims and scale-up | Resolve from official files/guides or CHARLS support; if not resolvable, redefine the estimand and label the limitation before any model run. |
| All design gates pass but the pilot code/engine fails | No-go for scale-up | Repair the pipeline, then rerun the same frozen 105-pair family once; do not select pairs by preliminary p-values. |
| Design-valid pilot completes with reproducible estimates and acceptable diagnostics | Go to Wave 1 expansion | Freeze code, source manifest, model specification, multiplicity family, and review record; then run the predeclared broader household-environment family. |
| Pilot is statistically null but passes all validity and reproducibility gates | Go to Wave 1 expansion if scientific scope still holds | Null findings are a valid outcome; do not add exposures/outcomes solely to obtain significance. |
| Any pair is unstable, non-estimable, or disclosure-sensitive | Pair-specific hold | Preserve the failure/hold status privately and keep the public result blank for that pair. |

## Scale-up sequence after a valid pilot

1. Freeze a tagged, reproducible Wave 1 release with the complete primary 105-coefficient pilot family and independent method-review sign-off.
2. Run the already predeclared Wave 1 household-environment expansion (primary family K=150; heating-condition subdomain K=90 separately adjusted), preserving all planned contrasts and failures.
3. Expand to other waves only after establishing each wave’s own outcome availability, exposure wording/units, weights, PSU/variance design, and estimand. Start with wave-specific models; pool waves only with an explicit, justified harmonization and design strategy.
4. Generate disclosure-reviewed aggregate result files and metadata for the website. Keep catalog availability, analyzed pairs, reviewed results, and publicly released results as distinct statuses.

This sequence intentionally separates **technical completion** (all declared models run), **analysis validity** (sources/design/diagnostics reviewed), and **scientific findings** (the direction and multiplicity-adjusted evidence). A successful first does not automatically imply the other two.
