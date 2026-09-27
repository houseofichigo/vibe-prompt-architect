"""Layout and packaging tests for the Skill in this repository (stdlib only)."""

import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import skill_rules as sr  # noqa: E402
import validate_skill  # noqa: E402

REPO_ONLY = {"README.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md", ".gitignore", ".gitattributes"}


class SkillLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_root, cls.roots = sr.find_repo_skill(ROOT)
        cls.dist = ROOT / "dist" / "skill.zip"

    def test_exactly_one_skill(self):
        self.assertIsNotNone(self.skill_root, f"expected one skills/<name>/SKILL.md, found {len(self.roots)}")

    def test_frontmatter_name_matches_folder(self):
        text = (self.skill_root / "SKILL.md").read_text(encoding="utf-8")
        fields, errors, _ = sr.parse_frontmatter(text)
        self.assertEqual(errors, [])
        self.assertEqual(fields.get("name"), self.skill_root.name)

    def test_no_blockers_for_declared_hosts(self):
        _, findings = sr.validate_skill_dir(self.skill_root, validate_skill.DEFAULT_TARGET)
        blockers = [f for f in findings if f[0] == "blocker"]
        self.assertEqual(blockers, [], sr.format_findings(blockers))

    def test_zip_has_single_named_root(self):
        with zipfile.ZipFile(self.dist) as zf:
            files = [n for n in zf.namelist() if not n.endswith("/")]
        name = self.skill_root.name
        self.assertTrue(files)
        self.assertTrue(all(n.startswith(name + "/") for n in files))
        self.assertIn(f"{name}/SKILL.md", files)

    def test_zip_excludes_repository_files(self):
        with zipfile.ZipFile(self.dist) as zf:
            names = zf.namelist()
        self.assertFalse(any(n.split("/", 1)[-1] in REPO_ONLY and n.count("/") == 1 for n in names))
        self.assertFalse(any("/.github/" in n or n.startswith(".github/") for n in names))
        self.assertFalse(any("__pycache__" in n or n.endswith(".pyc") for n in names))

    def test_zip_matches_skill_folder(self):
        diffs = sr.compare_zip(self.skill_root, self.dist, self.skill_root.name)
        self.assertEqual(diffs, [], "dist/skill.zip is stale; run python3 scripts/build_dist.py")


if __name__ == "__main__":
    unittest.main()
