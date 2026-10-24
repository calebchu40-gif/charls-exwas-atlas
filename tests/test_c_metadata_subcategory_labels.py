import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "site-prototype" / "dist" / "catalog_c.json"
APP = ROOT / "site-prototype" / "dist" / "app.js"
INDEX = ROOT / "site-prototype" / "dist" / "index.html"


class CMetadataSubcategoryLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.app = APP.read_text(encoding="utf-8")
        cls.index = INDEX.read_text(encoding="utf-8")
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

    def test_page_references_the_cache_busted_script_version(self):
        self.assertRegex(self.index, r'app\.js\?v=\d+')

    def test_automated_discovery_status_does_not_misstate_current_review_state(self):
        self.assertIn("自动发现纳入候选目录；逐字段核验状态见来源与值标签列", self.app)
        self.assertIn("x['Candidate.Status']||'来源/测量元数据'", self.app)


if __name__ == "__main__":
    unittest.main()
