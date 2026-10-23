# 2018 housing roster context review

Reviewed the Wave 4 questionnaire and Codebook for HA025_W4[i] property-location fields (i=1–11) and HA057_W3 monthly mortgage payment. The 11 location rows use the questionnaire's four response labels; Codebook frequencies were not transcribed because they are descriptive release summaries, not category definitions. These are C metadata entries and do not recommend covariate adjustment.

HA025 labels: 1=City or town central areas; 2=Town or semi-rural areas; 3=Rural areas; 4=Special regions. Each suffix denotes a listed house-property slot. It must not be interpreted as respondent current residence, a community measure, or 11 independent exposures. Keep property-to-household/person linkage and eligible roster denominators explicit.

HA057_W3 is a continuous 10,000 Yuan/month household mortgage payment on the active-mortgage route. The 2018 questionnaire asks about mortgages for the respondent's/spouse's houses and excludes properties with a paid-off mortgage. Do not merge it with outstanding principal or unpaid interest. Multiple-property aggregation, special values, and release storage need authorized-data QA.

Sources: `sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt`. No respondent data, Codebook frequencies, minima, maxima, or other descriptive statistics were used.
