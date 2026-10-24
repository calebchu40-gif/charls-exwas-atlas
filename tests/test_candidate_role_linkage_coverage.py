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

    def test_unlinked_discovery_roles_are_documented_internal_biomarker_candidates(self):
        # Automatic E/P discovery labels are broader than the manually audited
        # concept-source map. The only current exception is internal clinical
        # and physical biomarkers: they remain P-linked, but are not approved
        # as exogenous E sources by default.
        self.assertTrue(self.unlinked)
        self.assertTrue(all(role == "e" for role, *_ in self.unlinked))
        self.assertTrue(all(row.get("category", "").lower() == "internal biomarker"
                            for _, _, _, row in self.unlinked))
        self.assertTrue(all((wave, code, "p") in self.links
                            for _, wave, code, _ in self.unlinked))
        self.assertEqual(len({(wave, code) for _, wave, code, _ in self.unlinked}), 49)

    def test_every_other_candidate_e_or_p_wave_field_has_a_concept_source_role(self):
        self.assertEqual(len(self.unlinked), 49)
        self.assertTrue(all((role, wave, code) == ("e", wave, code)
                            for role, wave, code, _ in self.unlinked))

    def test_public_blood_catalogue_explains_discovery_role_boundary(self):
        page = (ROOT / "site-prototype/dist/index.html").read_text(encoding="utf-8")
        self.assertIn("自动E/P双角色只用于发现和人工复核", page)
        self.assertIn("不代表已批准的E来源映射", page)


if __name__ == "__main__":
    unittest.main()
