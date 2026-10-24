# Standing-balance test source review (2011–2015)

## Scope

Reviewed the 2011 CHARLS physical-examination questionnaire and baseline user guide, plus the 2013 and 2015 Biomarker Questionnaires and wave Codebooks. This is a questionnaire/Codebook metadata review only; it does not use respondent records, Codebook frequency tables or association estimates.

## Test protocols

Semi-tandem and side-by-side stands are each assessed up to 10 seconds. Full-tandem target duration is age graded: 30 seconds for participants aged 70 or older and 60 seconds for younger participants. Instruments distinguish full-duration completion from elapsed time when the target is not achieved and separately ask about compensatory movements. The questionnaire also routes participants based on safety, consent, understanding and preceding tests. Preserve these status, time, context and route fields separately; an unasked or routed-out duration is not zero.

The questionnaires define 993 as tried but unable and 999 as chose not to perform the test. These are status codes, not durations. Cross-wave age-eligibility, the exact released field/value implementation and summary rules remain unverified. No duration, test score or summary is computed by this review.

## Field identity

The 2011 questionnaire uses LI* item identifiers for these items while the Codebook candidates use QD/QE/QF* field names. The conceptual mapping is plausible, but the exact release-level one-to-one crosswalk remains unresolved. The 2013 and 2015 questionnaires and Codebooks contain the exact QD/QE/QF* source fields; this does not establish availability in the authorized respondent-level release.

## Atlas treatment

The atlas describes the three balance protocols as candidate phenotypes, with repeated completion/time/context fields and wave-specific caveats. Formal analysis locks remain intact. Before any modeling, confirm the released field identities, routing, valid and missing codes, eligible test population, and prespecified way to summarize completion or duration.
