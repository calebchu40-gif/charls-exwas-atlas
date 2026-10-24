"""Guard discovery-role rows against being mistaken for approved E/P mappings."""
import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class CandidateRoleLinkageCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.series = read_rows(ROOT / "audit/charls_atlas_candidate_series_v0.csv")
        cls.crosswalk = read_rows(ROOT / "audit/ep_concept_source_crosswalk_v1.csv")
        cls.objective = read_rows(ROOT / "audit/objective_measurement_crosswalk_v1.csv")
        cls.objective_keys = {
            (row.get("wave", "").strip(), code.strip().lower())
            for row in cls.objective
            for code in row.get("variables", "").split(";")
            if row.get("wave", "").strip() and code.strip()
        }
        cls.links = set()
        for row in cls.crosswalk:
            for role in row.get("Role", "").lower().split(","):
                role = role.strip()
                if role in {"e", "p"}:
                    cls.links.add((row.get("Wave", "").strip(),
                                   row.get("Source.Code", "").strip().lower(), role))

        cls.unlinked = []
        for row in cls.series:
            roles = {role.strip().lower() for role in row.get("epcf", "").split(",")}
            waves = [wave.strip() for wave in row.get("waves", "").split(",") if wave.strip()]
            code = row.get("Variable.Name", "").strip().lower()
            for role in roles & {"e", "p"}:
                for wave in waves:
                    if (wave, code, role) not in cls.links:
                        cls.unlinked.append((role, wave, code, row))

    def test_internal_blood_biomarkers_have_explicit_optional_e_and_p_roles(self):
        blood = read_rows(ROOT / "audit/blood_biomarker_crosswalk_v1.csv")
        analytes = [row for row in blood if row.get("concept_id") != "blood_collection_metadata"]
        expected = {(row["wave"], row["variable"].lower(), role)
                    for row in analytes for role in ("e", "p")}
        self.assertEqual(len(analytes), 32)
        self.assertTrue(expected <= self.links)
        self.assertFalse({(wave, code) for _, wave, code, _ in self.unlinked} &
                         {(row["wave"], row["variable"].lower()) for row in analytes})
        for row in self.crosswalk:
            if row.get("Source.File") == "audit/blood_biomarker_crosswalk_v1.csv" and row.get("Role") == "e":
                self.assertIn("optional ExWAS exposure candidate", row.get("Mapping.Status", ""))
                self.assertIn("internal blood biomarker", row.get("Mapping.Status", ""))
                self.assertIn("外部环境化学暴露", row.get("Caveat", ""))
                self.assertIn("血检权重", row.get("Caveat", ""))

    def test_every_other_candidate_e_or_p_wave_field_has_a_concept_source_role(self):
        self.assertEqual(self.unlinked, [])

    def test_official_objective_measurements_are_not_automatic_exposure_candidates(self):
        for row in self.series:
            roles = {role.strip().lower() for role in row.get("epcf", "").split(",")}
            if not roles.intersection({"e", "e,p"}):
                continue
            waves = [wave.strip() for wave in row.get("waves", "").split(",") if wave.strip()]
            code = row.get("Variable.Name", "").strip().lower()
            self.assertFalse(any((wave, code) in self.objective_keys for wave in waves),
                             (row.get("epcf"), code, waves))
        self.assertTrue(self.objective_keys)
        self.assertTrue(all((wave, code, "p") in self.links for wave, code in self.objective_keys))

    def test_public_blood_catalogue_explains_discovery_role_boundary(self):
        page = (ROOT / "site-prototype/dist/index.html").read_text(encoding="utf-8")
        self.assertIn("可选的内部生物标志物E及P候选", page)
        self.assertIn("不是外部环境化学暴露", page)
        self.assertIn("不代表模型纳入批准", page)


if __name__ == "__main__":
    unittest.main()
