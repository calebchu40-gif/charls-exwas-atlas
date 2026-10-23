import json
import unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
class DemographicValueLabelReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.mapping=pd.read_csv(ROOT/"audit/demographic_social_exposure_mapping_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
  cls.catalog=json.loads((ROOT/"site-prototype/dist/catalog_e.json").read_text(encoding="utf8"))
 def entry(self,w,c):
  x=self.mapping[(self.mapping.wave==w)&(self.mapping.code.str.lower()==c.lower())];self.assertEqual(len(x),1);return x.iloc[0]
 def site(self,w,c):
  x=[r for r in self.catalog if r.get("Source.Wave")==w and r.get("Variable.Name","").lower()==c.lower()];self.assertTrue(x);return x[0]
 def test_wave_specific_education_categories_are_not_collapsed(self):
  self.assertIn("10=Master’s degree",self.entry("2011","bd001").value_labels)
  self.assertNotIn("11=Doctoral",self.entry("2011","bd001").value_labels)
  self.assertIn("12=No change",self.entry("2015","bd001_w2_4").value_labels)
  self.assertIn("11=Doctoral degree/Ph.D.",self.site("2020","ba010")["Value.Labels"])
 def test_hukou_labels_reach_site_and_2013_alias_is_documented(self):
  self.assertIn("Unified Residence Hukou",self.site("2018","bc002_w3_1")["Value.Labels"])
  self.assertIn("Z-prefixed alias",self.entry("2013","bc001").caveat)
  self.assertIn("frequencies omitted",self.entry("2020","ba009").value_label_status)
if __name__=="__main__":unittest.main()
