import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "site-prototype" / "dist" / "catalog_c.json"
APP = ROOT / "site-prototype" / "dist" / "app.js"


class CMetadataSubcategoryLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.app = APP.read_text(encoding="utf-8")
        match = re.search(r"const C_SUBCATEGORY_LABELS=(\{.*?\});", cls.app, re.DOTALL)
        if not match:
            raise AssertionError("C metadata subcategory label dictionary is missing")
        cls.labels = json.loads(match.group(1))

    def test_every_catalogued_c_subcategory_has_a_chinese_label(self):
        subcategories = {row.get("subcategory", "") for row in self.rows}
        self.assertNotIn("", subcategories)
        self.assertEqual(subcategories - self.labels.keys(), set())
        self.assertTrue(all(any("\u4e00" <= char <= "\u9fff" for char in self.labels[key])
                            for key in subcategories))

    def test_table_uses_chinese_label_and_preserves_original_explanation(self):
        self.assertIn("C_SUBCATEGORY_LABELS[x.subcategory]", self.app)
        self.assertIn("原始分类说明：'+x.subcategory", self.app)


if __name__ == "__main__":
    unittest.main()
