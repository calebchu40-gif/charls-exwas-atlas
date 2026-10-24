# Grip strength and peak-flow source review (2011–2015)

## Scope and sources

Reviewed the CHARLS 2011 physical-examination questionnaire, 2011 National Baseline User's Guide, and 2013/2015 Biomarker Questionnaires and corresponding Codebooks already stored under `sources_official/`. The review applies only to public instrument and documentation metadata; it does not inspect respondent-level observations, publish Codebook frequencies, or estimate associations.

## Grip strength

The 2011 user guide describes a dynamometer and two measurements for each hand. The questionnaire labels left/right hand readings in kilograms. It separately records a practice with the dominant hand; that practice is not an outcome reading. Preserve each hand and trial as its own candidate phenotype field. The questionnaire defines 993 as tried but unable and 999 as chose not to perform the test; these are status codes, not strength values. Dominant hand, effort, posture and support describe measurement context. Do not select a hand, combine trials, or calculate a summary until the released-file structure and a prespecified summary rule are verified.

2011 instrument items use LI816/LI851/LI852/LI853, while the release Codebook candidates use QC003–QC006. The semantic correspondence is plausible but the exact one-to-one release-field identity has not been established. 2013 and 2015 questionnaires and Codebooks contain QC003–QC006. This confirms instrument labels, not individual-level release availability or analysis eligibility.

## Peak flow

The 2011 guide describes a peak-flow meter with three readings, 30 seconds apart. The questionnaire records LI807–LI809 and states 30 for participants younger than 60, 890 when the pointer passes the final tick mark, 993 after an unsuccessful attempt, and 999 when the participant chooses not to perform the test. The 2013/2015 instruments use QB002–QB004 and document the same special-value instructions. Keep the three readings separate; never treat 890/993/999 as physiological values. The age-related 30 marker requires release-specific interpretation before defining valid values or eligibility.

No explicit peak-flow unit was located in the reviewed questionnaires or Codebooks, so the atlas leaves the unit blank. This test is described as peak flow and must not be labelled full spirometry. The LI-to-QB field identity in 2011 remains unresolved; exact QB fields are documented in 2013/2015.

## Atlas treatment and remaining checks

The site presents these as candidate phenotypes with wave-specific source caveats. No participant data, Codebook frequency tables, analysis models or pairwise sample sizes are published. Before any analysis, confirm the authorized release files, field presence, missing/status-value implementation, age/test routes, valid ranges, and any cross-wave comparability decisions from release documentation. The 89 formal analysis locks remain unchanged.
