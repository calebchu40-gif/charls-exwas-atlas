"""Structural guards for the public atlas site.

Every regression fixed in the overnight pass was structural rather than
statistical: a tab strip that shared the view-router class, a helper name defined
twice across scripts, an in-page anchor treated as a view, a dropdown anchored
outside the viewport. These checks are cheap, run without a browser, and fail the
build the moment that class of fault returns.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site-prototype" / "dist"


class SiteStructureGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = (SITE / "index.html").read_text(encoding="utf-8")
        cls.scripts = {path.name: path.read_text(encoding="utf-8", errors="ignore")
                       for path in SITE.glob("*.js")}

    def test_every_navigation_target_has_a_section(self) -> None:
        sections = set(re.findall(r'<section class="view[^"]*" id="([^"]+)"', self.html))
        targets = set(re.findall(r'data-view="([^"]+)"', self.html))
        self.assertEqual(targets - sections, set(),
                         "navigation points at ids with no view section")

    def test_tab_strip_is_not_the_view_router(self) -> None:
        self.assertNotIn('class="viewnav" id="moduleTabs"', self.html,
                         "module tabs must not share the view-router class")
        self.assertIn('class="moduletabs" id="moduleTabs"', self.html)

    def test_no_helper_is_defined_in_two_scripts(self) -> None:
        owners: dict[str, set[str]] = {}
        for name, text in self.scripts.items():
            for match in re.finditer(r'^function\s+([A-Za-z_$][\w$]*)\s*\(', text, re.M):
                owners.setdefault(match.group(1), set()).add(name)
            for match in re.finditer(r'^const\s+([A-Za-z_$][\w$]*)\s*=', text, re.M):
                owners.setdefault(match.group(1), set()).add(name)
        duplicates = {name: sorted(files) for name, files in owners.items() if len(files) > 1}
        self.assertEqual(duplicates, {},
                         "a top-level helper or constant is defined in more than one script")

    def test_every_module_tab_has_a_render_branch(self) -> None:
        tabs = set(re.findall(r'data-module="([^"]+)"', self.html))
        branches = set(re.findall(r"active === '([^']+)'", self.scripts.get("modules.js", "")))
        missing = tabs - branches - {"forest"}
        self.assertEqual(missing, set(), "module tabs exist without a render branch")

    def test_script_queries_are_present_and_files_exist(self) -> None:
        for src in re.findall(r'<script src="\./([^"]+)"', self.html):
            self.assertRegex(src, r'\?v=\d+', f"{src} lacks a cache-busting version")
            self.assertTrue((SITE / src.split("?")[0]).is_file(), f"{src} is missing on disk")

    def test_in_page_anchor_exists_and_is_not_a_view(self) -> None:
        anchors = set(re.findall(r'href="#([^"]+)"', self.html))
        sections = set(re.findall(r'<section class="view[^"]*" id="([^"]+)"', self.html))
        for anchor in anchors:
            self.assertIn(f'id="{anchor}"', self.html, f"anchor #{anchor} has no target")
            self.assertNotIn(anchor, sections, f"anchor #{anchor} collides with a view id")

    def test_primary_nav_keeps_the_reference_entry_points(self) -> None:
        start = self.html.index('<div class="primary-nav">')
        stop = self.html.index('<div class="secondary-nav"', start)
        segment = self.html[start:stop]
        views = re.findall(r'data-view="([^"]+)"', segment)
        self.assertEqual(views, ["overview", "byPhenotype", "byExposure", "groups",
                                 "exposures", "phenotypes"],
                         "the six reference entry points and their order are fixed")


if __name__ == "__main__":
    unittest.main()
