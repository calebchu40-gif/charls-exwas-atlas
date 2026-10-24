import csv
import json
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
class CPlaceholderMetadataReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/"audit/c_placeholder_metadata_review_v1.csv").open(encoding="utf-8-sig",newline="") as f: cls.audit=list(csv.DictReader(f))
        cls.rows=json.loads((ROOT/"site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.series=json.loads((ROOT/"audit/charls_atlas_candidate_series_v0.json").read_text(encoding="utf-8"))
        cls.by_key={(r["Source.Wave"],r["Variable.Name"].lower()):r for r in cls.rows}
    def test_audited_family_counts_and_sources(self):
        self.assertEqual(len(self.audit),110)
        counts={family:sum(r["metadata_family"]==family for r in self.audit) for family in {r["metadata_family"] for r in self.audit}}
        self.assertEqual(counts,{"unsupported prior-wave disease-awareness slots":15,"unlisted chronic-disease index placeholder":5,"inactive household lending and debt legacy fields":4,"household debt unfolding-bracket response metadata":8,"personal wage deduction scope and response-unit selectors":3,"household income response-format selectors":3,"chair setup for repeated chair-stand test":4,"household financial respondent source":2,"inactive fixed-capital legacy/format fields":2,"2020 pandemic work-module selection flag":1,"unresolved questionnaire and Codebook field identity conflict":1,"2013 money-management helper relationship option slots":62})
        for item in self.audit:
            for source in item["official_source"].split("; "):
                self.assertTrue((ROOT/source).exists())
    def test_placeholders_remain_c_only_and_do_not_gain_labels(self):
        for item in self.audit:
            row=self.by_key[(item["wave"],item["code"].lower())]
            self.assertEqual(row["epcf"],"c")
            if not (item["wave"] == "2015" and item["code"].lower() == "qh006"):
                self.assertEqual(row["Value.Labels"],"")
            self.assertNotEqual(row["Value.Label.Review"],"not yet reviewed")
            if item["metadata_family"] == "2013 money-management helper relationship option slots":
                self.assertIn("source detail",row["Value.Label.Review"])
                self.assertIn("not a standalone",row["Candidate.Status"])
                self.assertEqual(row["subcategory"],"money-management helper relationship option slots")
                self.assertIn("do not count the 64 options as separate constructs",row["Review.Flag"])
            else:
                self.assertIn("metadata only",row["Value.Label.Review"])
        selector=self.by_key[("2015","qh006")]
        self.assertEqual(selector["Value.Labels"],"1=CHARLS chair with 42 cm height; 2=Other chair")
    def test_helper_option_review_is_synchronized_to_series_catalog(self):
        reviewed={(r["wave"],r["code"].lower()) for r in self.audit if r["metadata_family"]=="2013 money-management helper relationship option slots"}
        series={(wave, r["Variable.Name"].lower()):r for r in self.series for wave in r["waves"].split(";")}
        self.assertEqual(len(reviewed),62)
        for key in reviewed:
            row=series[key]
            self.assertEqual(row["category"],"source-detail metadata")
            self.assertEqual(row["subcategory"],"money-management helper relationship option slots")
            self.assertIn("source detail",row["value_label_review"])
if __name__=="__main__":unittest.main()
