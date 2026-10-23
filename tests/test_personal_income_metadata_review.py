import json
import unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
class PersonalIncomeMetadataReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=pd.read_csv(ROOT/"audit/personal_income_exposure_mapping_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
        cls.catalog=json.loads((ROOT/"site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
    def mapping_row(self,wave,code):
        rows=self.mapping[(self.mapping.wave==wave)&(self.mapping.code.str.lower()==code.lower())]
        self.assertEqual(len(rows),1)
        return rows.iloc[0]
    def catalog_row(self,wave,code):
        rows=[r for r in self.catalog if r.get("Source.Wave")==wave and r.get("Variable.Name","").lower()==code.lower()]
        self.assertTrue(rows,(wave,code))
        return rows[0]
    def test_wave_specific_wage_units_are_kept_separate(self):
        self.assertIn("Yuan/year",self.mapping_row("2011","ga002").value_semantics)
        self.assertIn("Yuan/month",self.mapping_row("2011","ga002_1").value_semantics)
        self.assertIn("Yuan/year",self.mapping_row("2013","ga002_1").value_semantics)
    def test_special_response_codes_and_checkbox_limits_reach_site(self):
        self.assertIn("999=Refused",self.catalog_row("2018","hc007")["Value.Labels"])
        self.assertIn("997=Do not know",self.catalog_row("2020","ga003")["Value.Labels"])
        row=self.catalog_row("2011","hd008s1")
        self.assertEqual(row["Value.Labels"],"")
        self.assertIn("unselected storage",row["Value.Label.Review"])
    def test_fraud_event_count_is_continuous_metadata(self):
        row=self.catalog_row("2018","hd005_w4_0")
        self.assertEqual(row["Value.Labels"],"")
        self.assertIn("continuous amount/count",row["Value.Label.Review"])
if __name__=="__main__":unittest.main()
