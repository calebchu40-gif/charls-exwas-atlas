# CHARLS 2011 other community subsidy roster review (2026-10-25)

## Source-mapped candidate fields

The official 2011 Community Questionnaire Part G asks whether the community has other poverty-related subsidies (JG009), gives an open-text name field, and directs the interviewer to ask JG010–JG012 for each listed program. The Codebook exposes five repeat response slots, five nested open-text program-name fields, and five indexed fields each for start year, 2010 recipient-household count, and average monthly standard. The catalogue preserves all 25 source fields and their suffixes. It records years, households, and Yuan/month units where the item wording supports them.

## Mapping boundary

The questionnaire's flattened repeat instruction and the Codebook's nested field names do not fully establish how every JG009 response slot aligns with each open-text name field and its JG010–JG012 follow-ups. Therefore this is a source-mapped candidate roster, not a normalized subsidy taxonomy. The public catalogue instructs users to verify the emitted release fields and repeat linkage before pairing, pooling, or analyzing them. Do not convert open text to named policy categories without a documented coding protocol. These community-reported measures do not establish sampled-household receipt or individual income.

The source mapping adds 25 community field metadata rows and one concept. It uses public questionnaire wording and Codebook variable labels only; no respondent records, Codebook frequencies, or descriptive statistics are copied. Any pair-count change is metadata co-availability, not sample size or an association result.

## Official sources

- `sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt`, Part G, JG009–JG012, including the JG009 repeat instruction and No-skip to JG013.
- `sources_official/CHARLS_2011_Codebook_extracted.txt`, JG009–JG012 slot-indexed entries.

## Deployment verification

Commit `36dd613` was published as GitHub Pages Deploy #240 (`40179595161`, success). The public homepage returns HTTP 200 and loads `app.js?v=119`; online metadata reports 123 community concepts and 130,759 2011 candidate metadata pairs. The roster retains all 25 indexed fields and the slot-linkage caveat.
