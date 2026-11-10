import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DirectoryScopeKpiTests(unittest.TestCase):
    def test_homepage_reports_exposure_and_phenotype_counts_separately(self):
        scope = json.loads((ROOT / "audit/directory_scope_counts_v1.json").read_text(encoding="utf-8"))
        html = (ROOT / "site-prototype/dist/index.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('五轮常规主调查去重后共有'), 1)
        match = re.search(r'<div class="stats"[^>]*>(.*?)</div>\s*<p class="stats-note">(.*?)</p>', html, re.S)
        self.assertIsNotNone(match)
        cards = re.findall(r'<div class="stat"><b>([^<]+)</b><span>([^<]+)</span></div>', match.group(1))
        self.assertEqual(
            cards,
            [
                ("113,201", "公开关联结果"),
                ("758", "暴露指标"),
                ("181", "结局指标"),
                ("453,993", "次加权模型拟合"),
            ],
        )
        unique = scope["candidate_concept_ids"]
        dual = scope["exposure_concept_ids_including_dual"] + scope["phenotype_concept_ids_including_dual"] - unique
        self.assertIn("91,543", match.group(2))
        self.assertIn("不发布个体数据", match.group(2))
        scope_note = re.search(r'<p class="view-lede">(五轮常规主调查去重后共有.*?)</p>', html, re.S)
        self.assertIsNotNone(scope_note, "the full scope caveat must stay on the homepage")
        self.assertIn(f"{dual} 个同时承担暴露与表型角色", scope_note.group(1))
        self.assertIn("不是样本量或关联结果", scope_note.group(1))
        self.assertIn("2014生命历程特殊调查单独展示", scope_note.group(1))
        self.assertIn("2014 生命历程回顾性调查", html)
        life_history = json.loads((ROOT / "site-prototype/dist/life_history_exposures_v1.json").read_text(encoding="utf-8"))
        life_history_field_rows = sum(len(concept["source_fields"]) for concept in life_history)
        self.assertIn(f"{len(life_history)}个候选概念组、{life_history_field_rows:,}条概念—字段映射", html)
        self.assertIn("不计入上述五波统计", scope_note.group(1))
        self.assertIn("30个大型社区曾按地理子区拆分抽样", html)
        self.assertIn("communityID 仅是 PSU 候选", html)
        self.assertIn("可能包含45岁以下个体", html)
        self.assertIn("该调查没有权重", html)
        self.assertIn("CHARLS官方数据页与文件", html)

    def test_readme_snapshot_matches_generated_catalog_and_pair_index(self):
        scope = json.loads((ROOT / "audit/directory_scope_counts_v1.json").read_text(encoding="utf-8"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        pair_index = json.loads((ROOT / "site-prototype/dist/candidate_pair_explorer_v1.json").read_text(encoding="utf-8"))
        catalogs = {
            role: json.loads((ROOT / f"site-prototype/dist/catalog_{role}.json").read_text(encoding="utf-8"))
            for role in "epc"
        }
        self.assertIn(f"E={len(catalogs['e']):,}、P={len(catalogs['p']):,}、C={len(catalogs['c']):,}", readme)
        self.assertIn(f"{scope['candidate_concept_ids']:,} 个候选概念", readme)
        self.assertIn(f"{scope['exposure_concept_ids_including_dual']:,}", readme)
        self.assertIn(f"{scope['phenotype_concept_ids_including_dual']:,}", readme)
        self.assertIn(f"{scope['wave_field_mapping_rows']:,} 条概念—来源映射", readme)
        for wave, details in pair_index["waves"].items():
            self.assertIn(f"{details['candidate_pair_count']:,}", readme)


if __name__ == "__main__":
    unittest.main()
