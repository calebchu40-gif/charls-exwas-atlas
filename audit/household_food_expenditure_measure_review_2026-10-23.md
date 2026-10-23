# Weekly household food and eating-out expenditure measures

The five-wave questionnaire review covers ten fields: household food expenditure (`GE006` in 2011–2015, `GE006_W4` in 2018, `GF006` in 2020) and household eating-out expenditure (`GE007` in 2011–2015, `GE007_W4` in 2018, `GF009` in 2020). All ask for the past week's amount in Yuan, but they are household aggregates, not individual dietary intake, food quality, or nutrient exposure.

Wave-specific scope must remain visible. The 2011 food question explicitly includes food purchased and food consumed from the household's own production. In 2013–2020, own-produced food market value is asked in separate fields, so it must not be assumed to be included in the reported cash expenditure. The 2018 and 2020 food questions explicitly exclude banquets/weddings in addition to eating-out spending, alcohol and tobacco; the earlier prompts differ. The 2018/2020 eating-out items also explicitly exclude banquet/wedding events, while earlier-wave wording does not establish the same exclusion. The measures therefore remain wave-specific candidates until a common expenditure construct is prespecified and the separately valued own-produced food is addressed.

Some questionnaires attach soft checks to unusually high responses; these are interviewer prompts, not validated analytic cutoffs. No Codebook extrema, frequencies, or respondent data were used. The unit, recall period and limitations are applied reproducibly by `scripts/apply_weekly_household_food_expenditure_review.py` after concept-catalog construction.

The same source-review status and wave-specific caveats are propagated to all ten household food/eating-out rows in `audit/food_environment_crosswalk_v1.csv`, keeping the domain explorer in sync with the main E catalog.
