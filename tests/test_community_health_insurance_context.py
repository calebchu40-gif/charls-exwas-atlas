import csv
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class CommunityHealthInsuranceContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'audit/community_exposure_crosswalk_v1.csv').open(encoding='utf-8-sig', newline='') as f:
            cls.rows = list(csv.DictReader(f))
        data = json.loads((ROOT / 'site-prototype/dist/community_exposures_v1.json').read_text(encoding='utf-8'))
        cls.concepts = {x['concept_id']: x for x in data}

    def test_programs_keep_separate_questionnaire_routes_and_time_series(self):
        expected = {
            'community_urban_resident_medical_insurance_context': {'jf010s1','jf011','jf013', *[f'jf012_{i}' for i in range(1,7)]},
            'community_rural_cooperative_medical_insurance_context': {'jf010s2','jf014','jf016', *[f'jf015_{i}' for i in range(1,9)]},
        }
        units = {r['code'].casefold(): r['unit'] for r in self.rows}
        for cid, codes in expected.items():
            with self.subTest(concept=cid):
                rows = {r['code'].casefold(): r for r in self.rows if r['concept_id'] == cid}
                self.assertEqual(set(rows), codes)
                self.assertEqual(len(self.concepts[cid]['source_fields']), len(codes))
                self.assertTrue(all(r['wave'] == '2011' for r in rows.values()))
                self.assertTrue(all('analysis eligibility pending' in r['mapping_status'] for r in rows.values()))
        self.assertEqual(units['jf011'], 'year')
        self.assertEqual(units['jf014'], 'year')
        self.assertEqual(units['jf012_1'], 'households')
        self.assertEqual(units['jf012_6'], 'households')
        self.assertEqual(units['jf015_1'], 'households')
        self.assertEqual(units['jf015_8'], 'households')
        self.assertEqual(units['jf013'], 'Yuan/year')
        self.assertEqual(units['jf016'], 'Yuan/year')

    def test_official_routes_and_nonindividual_boundary_are_explicit(self):
        q = re.sub(r'\s+', ' ', (ROOT / 'sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt').read_text(encoding='utf-8').casefold())
        cb = (ROOT / 'sources_official/CHARLS_2011_Codebook_extracted.txt').read_text(encoding='utf-8').casefold()
        cb_alnum = ''.join(ch for ch in cb if ch.isalnum())
        for code in ('jf010s1','jf010s2','jf011','jf012_1','jf012_6','jf013','jf014','jf015_1','jf015_8','jf016'):
            self.assertIn(''.join(ch for ch in code if ch.isalnum()), cb_alnum)
        self.assertIn('if chosen, answer jf011 - jf013', q)
        self.assertIn('if chosen, answer jf014 - jf016', q)
        for cid in ('community_urban_resident_medical_insurance_context','community_rural_cooperative_medical_insurance_context'):
            self.assertIn('not sampled-household enrollment', self.concepts[cid]['caveat'])
        for r in self.rows:
            if r['code'].casefold().startswith(('jf010s','jf011','jf012_','jf013','jf014','jf015_','jf016')):
                self.assertNotIn('Freq.', r['source_evidence'])
                self.assertNotIn('Mean', r['source_evidence'])

if __name__ == '__main__':
    unittest.main()
