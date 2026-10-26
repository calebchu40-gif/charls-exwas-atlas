# 2014 Life History: respondent-specific sensitive context review

## Scope and source check

Reviewed the official CHARLS 2014 Life History questionnaire items P022–P024, their conditional follow-up questions, and the corresponding fields in the official Codebook. These questions present respondent and spouse/partner options in the same roster-style item. The questionnaire labels distinguish the respondent's own option from the partner slots; the Codebook also has exact respondent-specific fields:

| Concept | Codebook field(s) | Questionnaire route | Catalog handling |
|---|---|---|---|
| Respondent communist-party membership | `p022s1` | P022 respondent option; separate `None` option | One respondent-specific E metadata candidate |
| Respondent minority status and ethnicity | `p023s1`, `p023_1_1_` | P023 respondent option; P023_1 is conditional on the selected minority route | Two respondent-specific E metadata fields |
| Respondent religion and affiliation | `p024s1`, `p024_1_1_` | P024 respondent option; P024_1 is conditional on the selected belief route | Two respondent-specific E metadata fields |

The catalog uses the question/codebook identity only. It does not contain participant-level answers, frequencies, names, or inferred responses. A blank follow-up is not treated as “No.” P022's respondent and `None` options are not conflated.

## Separation from relative slots

Spouse/partner slots and follow-up fields (`p022s2` onward, `p023s2` onward and `p023_1_2_` onward, `p024s2` onward and `p024_1_2_` onward) remain classified as `deferred_sensitive_relative_identity` in the generated full-module coverage ledger. Child-specific party, ethnicity and religion fields remain deferred as well. This separates explicitly identified respondent fields from relatives' sensitive attributes; it does not authorize a participant-level analysis or change the meaning of the special wave.

## Interpretation and safeguards

These are sensitive political, ethnic and religious characteristics, not environmental measurements. They are retained as metadata candidates because the official instrument explicitly records respondent-specific fields; their inclusion is not an endorsement to model every pair. Any future analysis needs an explicit research estimand, authorized use of the applicable restricted microdata, ethics/privacy and disclosure review, and a defensible confounder/causal structure. Do not publish sparse cells, participant values, or identifiable relative-level information.

The 2014 Life History release has no survey weight and is not part of the regular-wave weighted association scans. Keep its fields and any future analyses separate from the regular five-wave inferential atlas unless valid design information and a justified analysis plan are established.

## Rebuild evidence

The metadata generator assigned all 1,920 `DEMOGRAPHICBACKGROUNDS` Codebook fields a unique disposition. After this review, the ledger has 1,251 mapped candidates, 199 deferred sensitive-relative fields, and the remaining categories unchanged. The local Life History JSON contains 195 concepts and 6,103 field mappings (E=6,042; P=61). These are catalog counts, not analytic sample sizes or association results. Builder output and generated ledger were inspected; the full automated test suite was not run in this turn.


## Publication verification

Commit `6539868` was published as app v191 / Life History JSON v57. GitHub Validate #645 and Pages Deploy #323 succeeded. Live homepage and JSON both returned HTTP 200; the served JSON had 195 concepts / 6,103 field rows (E=6,042, P=61) and contained all five respondent-specific fields.
