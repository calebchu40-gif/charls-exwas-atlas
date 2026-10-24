import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SubjectiveLifeExpectancyCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit" / "subjective_life_expectancy_2011_2018_crosswalk_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.reviewed = list(csv.DictReader(stream))
        with (ROOT / "audit" / "ep_concept_source_crosswalk_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.crosswalk = list(csv.DictReader(stream))
        with (ROOT / "audit" / "charls_atlas_candidate_fields_v0.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.catalog = list(csv.DictReader(stream))

    def test_source_wave_fields_are_added_without_claiming_a_common_target_age(self):
        self.assertEqual({r["wave"] for r in self.reviewed}, {"2011", "2013", "2015", "2018"})
        self.assertTrue(all(r["code"].lower() == "da081" for r in self.reviewed))
        concept_rows = [r for r in self.crosswalk if r["Concept.ID"] == "subjective_life_expectancy"]
        self.assertEqual({r["Wave"] for r in concept_rows}, {"2011", "2013", "2015", "2018", "2020"})
        for row in self.reviewed:
            self.assertIn("[...]", row["caveat"])
            self.assertIn("target-age", row["mapping_status"])
            self.assertIn("百分比", row["caveat"])
        p_rows = [
            r for r in self.catalog
            if r["Concept.ID.Candidates"] == "subjective_life_expectancy" and r["epcf"] == "p"
        ]
        self.assertEqual({r["Source.Wave"] for r in p_rows}, {"2011", "2013", "2015", "2018", "2020"})
        early_codes = {r["Source.Code"].lower() for r in concept_rows if r["Wave"] != "2020"}
        wave5_codes = {r["Source.Code"].lower() for r in concept_rows if r["Wave"] == "2020"}
        self.assertEqual(early_codes, {"da081"})
        self.assertEqual(wave5_codes, {"da029"})

    def test_five_steps_are_ordinal_and_2018_dont_know_is_separate(self):
        for row in self.reviewed:
            for label in (
                "1=Almost impossible", "2=Not very likely", "3=Maybe",
                "4=Very likely", "5=Almost certain",
            ):
                self.assertIn(label, row["value_labels"])
            self.assertIn("do not convert steps to percentages", row["value_label_status"])
            self.assertIn("no Codebook frequencies copied", row["value_label_status"])
        wave_2018 = next(r for r in self.reviewed if r["wave"] == "2018")
        self.assertIn("997=Don't know", wave_2018["value_labels"])

    def test_official_questionnaires_show_the_target_age_as_a_placeholder(self):
        sources = {
            "2011": "CHARLS_2011_Baseline_Questionnaire_official_extracted.txt",
            "2013": "CHARLS_2013_Questionnaire_extracted.txt",
            "2015": "CHARLS_2015_Questionnaire_extracted.txt",
            "2018": "CHARLS_2018_Questionnaire_extracted.txt",
        }
        for wave, filename in sources.items():
            text = (ROOT / "sources_official" / filename).read_text(
                encoding="utf-8", errors="replace"
            ).replace("\x00", "")
            self.assertIn("DA081", text, wave)
            self.assertIn("chance in reaching the age of [...]", text, wave)


if __name__ == "__main__":
    unittest.main()
