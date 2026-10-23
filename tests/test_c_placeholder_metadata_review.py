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
        cls.by_key={(r["Source.Wave"],r["Variable.Name"].lower()):r for r in cls.rows}
    def test_audited_family_counts_and_sources(self):
        self.assertEqual(len(self.audit),48)
        counts={family:sum(r["metadata_family"]==family for r in self.audit) for family in {r["metadata_family"] for r in self.audit}}
        self.assertEqual(counts,{"unsupported prior-wave disease-awareness slots":15,"unlisted chronic-disease index placeholder":5,"inactive household lending and debt legacy fields":4,"household debt unfolding-bracket response metadata":8,"personal wage deduction scope and response-unit selectors":3,"household income response-format selectors":3,"chair setup for repeated chair-stand test":4,"household financial respondent source":2,"inactive fixed-capital legacy/format fields":2,"2020 pandemic work-module selection flag":1,"unresolved questionnaire and Codebook field identity conflict":1})
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
            self.assertIn("metadata only",row["Value.Label.Review"])
        selector=self.by_key[("2015","qh006")]
        self.assertEqual(selector["Value.Labels"],"1=CHARLS chair with 42 cm height; 2=Other chair")
if __name__=="__main__":unittest.main()
