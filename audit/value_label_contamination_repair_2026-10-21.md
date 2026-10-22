# Value-label frequency-artifact review (2026-10-21)

A scan of the built CHARLS candidate catalog found four categorical-label strings containing Codebook frequency-table remnants. These were not valid answer options. The label-generation scripts now rebuild the category text from official field menus and strip frequencies/table headings.

| Wave-field | Correct retained categories | Evidence |
|---|---|---|
| 2015 `FM043` | 1 Excellent; 2 Very good; 3 Good; 4 Fair; 5 Poor | 2015 questionnaire; retirement-health question |
| 2015 `FN057_W3_6_3_` | The 8 official pension nonreceipt-reason codes | 2015 Codebook field identity and category labels |
| 2015 `FN076_W3_2_S1` | 1 Myself (selected slot only) | 2015 Codebook; checkbox slot, unselected storage not inferred |
| 2015 `FN047_W2` | 1 Annual Payment; 2 Lump-sum Amount | 2015 questionnaire and Codebook |

Thirteen other scanner hits (12 unit selectors in the 2015 FN072/FN075 series and one in the 2018 FN072 series) were valid unit-selector labels (`1=Yuan; 2=10,000 Yuan`); the number 10,000 is the response-unit option, not a frequency, so those were preserved. The scan is a review aid and does not establish that every other label is fully harmonized. No microdata or response frequencies are included in the site label layer.
