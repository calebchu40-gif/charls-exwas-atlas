# 2014 WORKHISTORY F112 employment income-mode review

## Sources and scope

Reviewed the 2014 CHARLS Life History Questionnaire and Codebook entries for F112/F112_a. This is a metadata-only source audit; it does not inspect participant responses, calculate income distributions or eligible sample sizes, or fit associations.

## Question routing and constructs

The questionnaire routes F102–F112b to employment episodes coded F_3=2 or 3. At job start (F112), respondents report net average monthly income after personal income tax and social-insurance contributions. A Yuan response records the monetary amount in F112_a1 and skips the workpoint follow-up. A workpoint response routes to daily workpoints (F112_1_1) and reported money value per point (F112_1_2). The analogous middle-period question uses F112_a/F112_a_a1 and F112_1_a_1/F112_1_a_2.

The 76 Codebook fields are mapped into three concepts, without collapsing measurement modes or job phases:

- 24 payment-mode fields: 15 job-start slots (suffixes 0–13 and 15) and nine middle-period slots (1–8 and 11);
- 24 Yuan amount fields: the same start/middle slot coverage, conditional on selecting Yuan; and
- 28 workpoint components: 16 fields at job start across eight slots and 12 fields in the middle period across six slots, with daily point count and Yuan value per point retained as distinct components.

No suffix-14 job slot appears in these Codebook families. Do not treat a payment-mode code as a quantity, a skip after workpoints as zero currency income, or Yuan-per-point as actual cash received. Do not combine historical nominal income amounts across episodes or eras without a documented price-year and comparability plan. Do not derive totals by multiplying workpoint count and point value until the authorized-release coding and interpretation are validated.

## Resulting local catalogue

After rebuilding, the Life History catalogue has 131 concepts / 4,546 source-field mappings (E=4,500, P=46). WORKHISTORY now has 1,705 mapped candidate fields and 282 substantive fields deferred for further review; all exclusion categories remain explicit. These are mapping counts, not analysis-ready indicators, sample sizes or results. Formal association models remain zero.
