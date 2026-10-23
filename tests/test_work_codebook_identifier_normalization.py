import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_work_exposure_value_labels as work_labels


class WorkCodebookIdentifierNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book = work_labels.read_codebook(work_labels.BOOKS["2011"])

    def test_spaces_in_extracted_2011_codes_match_canonical_underscores(self):
        key = re.sub(r"[^a-z0-9]", "", "fd005_indc")
        self.assertEqual(self.book[key][0][0], "Employed Industry Code")
        self.assertEqual(self.book[key][0][1], [])

    def test_numeric_and_date_fields_are_located_without_invented_categories(self):
        for code, title in (("fd021_1", "Years"), ("fm017_a", "Min Bracket")):
            key = re.sub(r"[^a-z0-9]", "", code)
            self.assertEqual(self.book[key][0][0], title)
            self.assertEqual(self.book[key][0][1], [])

    def test_categorical_codebook_labels_are_kept_without_frequency_columns(self):
        values = self.book["fd002"][0][1]
        self.assertEqual(values[0], ("1", "Government"))
        self.assertIn(("8", "Other"), values)
        self.assertTrue(all("%" not in label and "," not in label for _, label in values))


if __name__ == "__main__":
    unittest.main()
