# Parent-record hukou context candidates (2026-10-22)

## Official identity and record unit

The CHARLS 2013 and 2015 codebooks identify separate Parent modules with respondent `ID`, household/community identifiers, and a `parentID` relationship code. In 2013 `parentID` distinguishes father, mother, father-in-law, and mother-in-law; the parent-type field `ca003` identifies biological, adoptive, step, other biological relative, or another person who raised the respondent. In 2015 `parentID` distinguishes biological father/mother from step/foster and spouse-parent slots. These are long-form parent records, not one row per respondent.

## Added exploratory candidates

Six source links now index three candidate concepts for 2013 and 2015: parent hukou and current-residence concordance (`ca018`), parent current hukou location relation (`ca019`), and parent current hukou type (`ca020`). Official codebook response labels are recorded without codebook frequencies. Wave-specific categories are retained; 2013 lacks the explicit “no hukou” category for `ca020` that appears in 2015. `ca019` is indexed only as coded relational categories; detailed location text is excluded.

## Analysis gate

These candidates are discovery-only. Any respondent-level analysis must link parent records to respondent IDs, choose the target relation in advance, and preserve separate father and mother records. For 2013, biological-parent restriction also requires the parent-type field; for 2015, only the biological father/mother `parentID` categories qualify. Do not combine in-laws, spouse's parents, step/adoptive/foster parents, or other relatives, and do not collapse the long table without a prespecified estimand. Structural skips are not substantive responses. No individual records or response frequencies were read and no analysis was run.

## Build result

The catalog gained 3 E-role candidate concepts and 6 wave-field links without changing the number of source catalog rows. Current totals are 1,275 candidate E/P concepts (E=1,005, P=279, dual=9); 6,231 E/P source links; 6,404 full crosswalk rows (173 C, of which 170 match the catalog and 3 are external design/eligibility rows); and 7,866 catalog rows (7,190 E/P, 676 C). Metadata co-availability pairs are 104,741 (2011), 110,082 (2013), 112,039 (2015), 89,193 (2018), and 12,598 (2020); these are not sample sizes.


The same official relationship gate also allowed four Parent-module education source links (2013/2015 × biological father/mother) to connect to the existing father- and mother-education concepts. No concepts were duplicated. The matching fixed Family_Information fields remain separate source rows; select one representation or reconcile by a prespecified rule to avoid double counting. See `parent_roster_education_crosswalk_v1.csv`.
