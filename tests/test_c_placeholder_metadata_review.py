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
        self.assertEqual(len(self.audit),24)
        counts={family:sum(r["metadata_family"]==family for r in self.audit) for family in {r["metadata_family"] for r in self.audit}}
        self.assertEqual(counts,{"unsupported prior-wave disease-awareness slots":15,"unlisted chronic-disease index placeholder":5,"inactive household lending and debt legacy fields":4})
        for item in self.audit:self.assertTrue((ROOT/item["official_source"]).exists())
    def test_placeholders_remain_c_only_and_do_not_gain_labels(self):
        for item in self.audit:
            row=self.by_key[(item["wave"],item["code"].lower())]
            self.assertEqual(row["epcf"],"c");self.assertEqual(row["Value.Labels"],"")
            self.assertNotEqual(row["Value.Label.Review"],"not yet reviewed")
            self.assertIn("C metadata only",row["Value.Label.Review"])
if __name__=="__main__":unittest.main()
