# 2014 Life History Sample_Infor review (2026-10-26)

## Official source findings

The official Life History release note identifies `Sample_Infor.dta` as sample identification, death and interview-time data. It states that the file includes the first two waves' live longitudinal respondents, the Wave 1 refresh sample, and attempted nonrespondents; respondents younger than 45 can therefore appear. Only responded samples are released, deceased persons can be identified in this file, and no weight is provided. The note also says individual, household and community IDs can link to the first two waves but must be adjusted for Wave 1 following the Wave 2 release note.

The official Codebook has eight fields. `life_history_sample_information_coverage_2014_v1.csv` gives each exactly one disposition without copying the Codebook's descriptive frequencies.

## Candidate and metadata decisions

| Field(s) | Disposition | Rationale |
|---|---|---|
| `died` | One P candidate: sample vital status | The release note explicitly says deceased persons can be identified. This is a mortality/selection-status marker, not a death date, cause, population rate or nationally representative outcome. Keep metadata only; do not publish participant status or frequencies. |
| `longitudinal` | Sample/design metadata, excluded from E/P | Sample membership is a design/selection characteristic, not an exposure or phenotype. |
| `iyear`, `imonth` | Interview-timing metadata, excluded from E/P | These describe data collection, not event time or environmental exposure. |
| `id`, `householdid`, `communityid` | Linkage keys excluded | Never expose values. Wave 1 key adjustment must follow official instructions in controlled authorized joins. |
| `versionid` | Release metadata, excluded | Bookkeeping field. |

The special Life History sample remains independent from the regular five-wave weighted analysis and does not contribute to its pair-coavailability index. In particular, the `died` status must not be used to estimate population mortality or be joined to outcomes without a defined target population, approved data access, and a defensible selection/weighting strategy.

## Reproducibility

`scripts/build_life_history_exposure_crosswalk.py` now writes the eight-row coverage ledger and includes only `died` as a candidate P metadata record. Tests enforce the field count, disposition counts and absence of Codebook `OBS:` strings in the candidate metadata. No frequency, participant-level record or identifier is used.

