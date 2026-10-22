import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CommunityPollutionLabelOverrideTests(unittest.TestCase):
    def test_questionnaire_anchors_override_misleading_codebook_gloss(self):
        with (ROOT / "audit" / "community_questionnaire_label_overrides_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as f:
            rows = list(csv.DictReader(f))
        by_code = {row["code"]: row for row in rows}
        expected = (
            "1=Very severe (very serious pollution); 2=Some pollution; "
            "3=Almost none; 4=Completely absent"
        )
        for code in ("jb018", "jb019"):
            with self.subTest(code=code):
                self.assertEqual(by_code[code]["value_labels"], expected)
                self.assertIn("questionnaire semantics reconciled", by_code[code]["value_label_status"])
                self.assertIn("higher codes indicate less reported pollution", by_code[code]["rationale"])

    def test_override_is_supported_by_official_questionnaire_text(self):
        questionnaire = (
            ROOT / "sources_official" / "CHARLS_2011_Community_Questionnaire_official_extracted.txt"
        ).read_text(encoding="utf-8")
        for anchor in ("JB018", "JB019", "很严重", "有一些", "基本没有", "完全没有"):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, questionnaire)


if __name__ == "__main__":
    unittest.main()
