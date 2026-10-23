import json
import unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
class SocialCaregiverReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.map=pd.read_csv(ROOT/"audit/social_exposure_crosswalk_v1.csv",dtype=str,encoding="utf-8-sig").fillna("")
  cls.cat=json.loads((ROOT/"site-prototype/dist/catalog_e.json").read_text(encoding="utf8"))
 def row(self,w,c):
  x=self.map[(self.map.wave==w)&(self.map.code.str.lower()==c.lower())]
  self.assertEqual(len(x),1);return x.iloc[0]
 def site(self,w,c):
  x=[r for r in self.cat if r.get("Source.Wave")==w and r.get("Variable.Name","").lower()==c.lower()]
  self.assertTrue(x);return x[0]
 def test_helper_option_uncertainty_is_not_coded_as_no(self):
  for w,c in [("2011","db022s38"),("2013","db022_w2_1_1_s64"),("2013","db031s37")]:
   r=self.row(w,c);self.assertEqual(r.value_labels,"");self.assertIn("unselected",r.value_label_status)
   self.assertEqual(self.site(w,c)["Value.Labels"],"")
 def test_helper_days_count_has_route_status_without_categories(self):
  r=self.row("2011","db023_38_");self.assertIn("continuous count",r.value_label_status)
  self.assertEqual(self.site("2011","db023_38_")["Value.Labels"],"")
if __name__=="__main__":unittest.main()
