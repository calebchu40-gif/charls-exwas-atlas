import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def mapping_rows():
    with (ROOT / "audit/behavior_exposure_variable_mapping_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class AlcoholFrequencyRouteReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = mapping_rows()
        cls.topic = json.loads((ROOT / "site-prototype/dist/behavior_exposures_v1.json").read_text(encoding="utf-8"))
        cls.pairs = json.loads((ROOT / "site-prototype/dist/candidate_pair_explorer_v1.json").read_text(encoding="utf-8"))
        cls.audit = (ROOT / "audit/alcohol_frequency_route_review_2026-10-25.md").read_text(encoding="utf-8")

    def row(self, concept, wave, code):
        found = [r for r in self.rows if r["concept_id"] == concept and r["wave"] == str(wave) and r["code"].lower() == code.lower()]
        self.assertEqual(len(found), 1)
        return found[0]

    def test_recent_drinking_threshold_is_separate_from_exact_frequency(self):
        for wave in ("2011", "2013", "2015", "2018"):
            row = self.row("alcohol_recent", wave, "da067")
            self.assertIn("threshold", row["value_semantics"])
            self.assertIn("DA067=2/3", row["value_semantics"])
            self.assertIn("structural absence is not", row["value_semantics"].lower())
        row = self.row("alcohol_recent", "2020", "da051")
        self.assertIn("DA051=1 to DA052", row["value_semantics"])
        self.assertIn("DA051=2/3", row["value_semantics"])

    def test_2020_frequency_is_overall_and_flowchart_routed(self):
        row = self.row("alcohol_frequency", "2020", "da052")
        self.assertIn("not beverage-specific", row["value_semantics"])
        self.assertIn("not directly interchangeable", row["value_semantics"])
        self.assertIn("Flowchart_Chinese.pdf", row["questionnaire_source"])
        self.assertIn("PDF p.30", row["questionnaire_source"])

    def test_wave1_liquor_frequency_denominator_is_not_overstated(self):
        row = self.row("alcohol_frequency", "2011", "da072")
        self.assertIn("does not explicitly require", row["value_semantics"])
        self.assertIn("unresolved", row["value_label_status"])
        self.assertIn("verify its exact released-file route", row["note"])
        for wave in ("2013", "2015", "2018"):
            row = self.row("alcohol_frequency", wave, "da072")
            self.assertIn("selected DA068 beverage type", row["value_semantics"])

    def test_topic_and_pair_browser_keep_wave_specific_route_notes(self):
        frequency = next(x for x in self.topic if x["concept_id"] == "alcohol_frequency")
        wave5 = next(x for x in frequency["source_fields"] if x["wave"] == "2020")
        self.assertIn("not beverage-specific", wave5["value_semantics"])
        wave1 = next(x for x in frequency["source_fields"] if x["wave"] == "2011" and x["code"].lower() == "da072")
        self.assertIn("does not explicitly require", wave1["value_semantics"])
        pair = next(x for x in self.pairs["waves"]["2020"]["exposures"] if x["concept_id"] == "alcohol_frequency")
        self.assertTrue(any("earlier waves use beverage-specific fields" in f["caveat"] for f in pair["source_fields"]))
        self.assertIn("overall-vs-earlier beverage-specific distinction", self.audit)


if __name__ == "__main__":
    unittest.main()
