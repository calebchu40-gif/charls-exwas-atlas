import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResidualBehaviorExposureCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "audit" / "residual_behavior_exposure_crosswalk_v1.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            cls.rows = list(csv.DictReader(stream))
        cls.sleep = {
            row["code"].lower(): row
            for row in cls.rows
            if row["concept_id"] == "previous_day_sleep_schedule"
        }
        cls.guest_meals = {
            row["wave"]: row
            for row in cls.rows
            if row["concept_id"] == "household_meals_provided_to_guests"
        }

    def test_sleep_timing_is_limited_to_the_2013_previous_day_recall(self):
        self.assertEqual(len(self.sleep), 10)
        self.assertTrue(all(row["wave"] == "2013" for row in self.sleep.values()))
        self.assertTrue(all("yesterday" in row["value_semantics"] for row in self.sleep.values()))
        self.assertTrue(all("not usual sleep timing" in row["caveat"] for row in self.sleep.values()))
        self.assertTrue(all("no established temporal direction" in row["caveat"] for row in self.sleep.values()))

    def test_split_time_components_preserve_am_and_pm_rows(self):
        for code in ("wb03", "wb04"):
            self.assertEqual(self.sleep[code]["value_labels"], "1=AM; 2=PM (official codebook response codes)")
            for suffix in ("_1", "_2"):
                self.assertIn("AM-row", self.sleep[code + suffix]["value_labels"])
            for suffix in ("_3", "_4"):
                self.assertIn("PM-row", self.sleep[code + suffix]["value_labels"])
        self.assertTrue(all("verify release storage" in row["value_labels"] for code, row in self.sleep.items() if code not in {"wb03", "wb04"}))
        self.assertTrue(all("verify released-file storage" in row["caveat"] for row in self.sleep.values()))

    def test_public_wave_catalog_receives_the_component_notes(self):
        path = ROOT / "site-prototype" / "dist" / "catalog_e.json"
        with path.open(encoding="utf-8") as stream:
            public_rows = __import__("json").load(stream)
        public_sleep = {
            row["Variable.Name"].lower(): row
            for row in public_rows
            if "previous_day_sleep_schedule" in row.get("candidate_concept_ids", "")
        }
        self.assertEqual(set(public_sleep), set(self.sleep))
        self.assertIn("AM-row component", public_sleep["wb03_1"]["Value.Labels"])
        self.assertIn("PM-row component", public_sleep["wb03_3"]["Value.Labels"])
        self.assertIn("verify released-file storage", public_sleep["wb03_1"]["harmonization_status"])

    def test_yesterday_mood_pair_is_marked_as_same_day_and_noncausal(self):
        path = ROOT / "site-prototype" / "dist" / "candidate_pair_explorer_v1.json"
        with path.open(encoding="utf-8") as stream:
            wave = __import__("json").load(stream)["waves"]["2013"]
        exposure = next(x for x in wave["exposures"] if x["concept_id"] == "previous_day_sleep_schedule")
        phenotype = next(x for x in wave["phenotypes"] if x["concept_id"] == "affect_sad_yesterday")
        sleep_note = " ".join(field["caveat"] for field in exposure["source_fields"])
        self.assertIn("no established temporal direction", sleep_note)
        self.assertTrue(any(field["code"] == "wb06" for field in phenotype["source_fields"]))
        self.assertEqual(wave["candidate_pair_count"], wave["exposure_count"] * wave["phenotype_count"] - len(
            {x["concept_id"] for x in wave["exposures"]} & {x["concept_id"] for x in wave["phenotypes"]}
        ))

    def test_household_guest_meals_are_source_reviewed_without_person_level_overclaim(self):
        expected = {"2011": "ge005", "2013": "ge005", "2015": "ge005", "2018": "ge005", "2020": "gf005"}
        self.assertEqual(set(self.guest_meals), set(expected))
        for wave, code in expected.items():
            row = self.guest_meals[wave]
            self.assertEqual(row["code"].lower(), code)
            self.assertEqual(row["unit"], "guest person-meals during the prior week")
            self.assertEqual(row["value_labels"], "")
            self.assertIn("official questionnaire wording and Codebook field label reviewed", row["mapping_status"])
            self.assertIn("household-level", row["caveat"].lower())
            self.assertIn("do not duplicate", row["caveat"].lower())
            self.assertIn("cross-wave equivalence require validation", row["mapping_status"])
            self.assertIn("Questionnaire", row["source_archive"])
            self.assertIn("Codebook_extracted.txt", row["source_archive"])

    def test_household_guest_meals_review_reaches_public_catalog_without_frequencies(self):
        path = ROOT / "site-prototype" / "dist" / "catalog_e.json"
        with path.open(encoding="utf-8") as stream:
            public_rows = __import__("json").load(stream)
        rows = [r for r in public_rows if "household_meals_provided_to_guests" in r.get("candidate_concept_ids", "")]
        self.assertEqual({r["Source.Wave"]: r["Variable.Name"].lower() for r in rows},
                         {"2011": "ge005", "2013": "ge005", "2015": "ge005", "2018": "ge005", "2020": "gf005"})
        self.assertTrue(all("guest person-meals" in r["Concept.Unit.Candidates"] for r in rows))
        self.assertTrue(all("household-level" in r["Harmonization.Status"].lower() for r in rows))
        self.assertTrue(all(not r.get("Value.Labels") for r in rows))


if __name__ == "__main__":
    unittest.main()
