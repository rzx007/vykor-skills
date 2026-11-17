import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import market
from market import package_skill


class MarketTest(unittest.TestCase):
    def test_packages_pinned_skill_with_references_and_license(self):
        source = io.BytesIO()
        with zipfile.ZipFile(source, "w") as z:
            z.writestr("upstream/SKILL.md", "---\nname: example\n---\nRead refs.")
            z.writestr("upstream/references/guide.md", "guide")
            helper = zipfile.ZipInfo("upstream/scripts/run.sh")
            helper.external_attr = 0o100755 << 16
            z.writestr(helper, "#!/usr/bin/env bash")
            z.writestr("upstream/tests/test.py", "not runtime content")
            z.writestr("upstream/LICENSE", "upstream notice")
        entry = {
            "name": "example", "license": "MIT",
            "path": ".", "include": ["SKILL.md", "references", "scripts"],
            "licensePath": "LICENSE",
        }
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "example.zip"
            package_skill(entry, source, output)
            first = output.read_bytes()
            package_skill(entry, source, output)
            self.assertEqual(first, output.read_bytes())
            with zipfile.ZipFile(output) as z:
                self.assertEqual(z.namelist(), ["LICENSE", "SKILL.md", "references/guide.md", "scripts/run.sh"])
                self.assertEqual(z.read("LICENSE"), b"upstream notice")
                self.assertEqual(z.getinfo("scripts/run.sh").external_attr >> 16, 0o100755)

    def test_rejects_traversal_and_name_mismatch(self):
        entry = {"name": "example", "license": "MIT", "path": ".", "licensePath": "LICENSE"}
        for path, name, error in [
            ("references/../unexpected", "example", "unsafe"),
            ("references/clock$.txt", "example", "unsafe"),
            ("references/skill.md", "example", "unsafe"),
            (".VYKOR-SKILL-INSTALL.JSON", "example", "unsafe"),
            (".vykor-skill-install.json/data", "example", "unsafe"),
            ("references/guide.md", "different", "SKILL.md"),
        ]:
            with self.subTest(path=path):
                source = io.BytesIO()
                with zipfile.ZipFile(source, "w") as z:
                    z.writestr("upstream/SKILL.md", f"---\nname: {name}\n---\n")
                    z.writestr("upstream/" + path, "test")
                    z.writestr("upstream/LICENSE", "notice")
                with tempfile.TemporaryDirectory() as temp:
                    output = Path(temp) / "test.zip"
                    with self.assertRaisesRegex(ValueError, error):
                        package_skill(entry, source, output)
                    self.assertFalse(output.exists())


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.dist = self.root / "dist"
        self.enterContext(patch.multiple(market, ROOT=self.root, DIST=self.dist))
        self.skill = {
            "name": "example", "version": "1.0.0",
            "displayName": "Example", "description": "Example skill", "license": "MIT",
            "repository": "https://github.com/owner/repo", "commit": "a" * 40,
            "path": ".", "include": ["SKILL.md"], "licensePath": "LICENSE",
        }

    def write_manifest(self, **updates):
        (self.root / "marketplace.json").write_text(json.dumps({
            "schemaVersion": 1, "release": "skills-v3", "skills": [{**self.skill, **updates}],
        }), encoding="utf-8")

    def build_index(self):
        source = io.BytesIO()
        with zipfile.ZipFile(source, "w") as archive:
            archive.writestr("upstream/SKILL.md", "---\nname: example\n---\nRead refs.")
            archive.writestr("upstream/LICENSE", "notice")
        source.seek(0)
        self.write_manifest()
        with patch.object(market.urllib.request, "urlopen", return_value=source):
            market.build()
        return self.dist / "marketplace.json"

    def test_manifest_rejects_values_the_host_cannot_accept(self):
        for updates in (
            {"requirements": "x" * 501},
            {"requirements": "💡" * 251},
            {"requirements": "\ufeff "},
            {"displayName": "Example".ljust(101)},
            {"name": "com1"},
            {"version": "1" * 29 + ".0.0"},
            {"repository": "https://github.com/owner/" + "x" * 250},
            {"path": "skills/../example"},
        ):
            with self.subTest(field=next(iter(updates))):
                self.write_manifest(**updates)
                with self.assertRaises(ValueError):
                    market.manifest()

    def test_build_derives_public_id_from_name(self):
        self.build_index()
        index = market.verified_index()
        self.assertEqual(index["skills"][0]["id"], "example")
        self.assertTrue((self.dist / "packages" / "example-1.0.0.zip").is_file())

    def test_verify_rejects_changed_public_metadata(self):
        index_path = self.build_index()
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index["skills"][0]["requirements"] = "x" * 501
        index_path.write_text(json.dumps(index), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Index differs from manifest"):
            market.verified_index()

    def test_verify_rejects_reserved_marker_with_matching_digest(self):
        index_path = self.build_index()
        asset = self.dist / "packages" / "example-1.0.0.zip"
        with zipfile.ZipFile(asset, "a") as archive:
            archive.writestr(".VYKOR-SKILL-INSTALL.JSON", "{}")
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index["skills"][0]["artifact"].update(size=asset.stat().st_size, sha256=hashlib.sha256(asset.read_bytes()).hexdigest())
        index_path.write_text(json.dumps(index), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unsafe skill file"):
            market.verified_index()

    def test_publish_checks_all_historical_releases_before_writing(self):
        index_path = self.build_index()
        artifact = json.loads(index_path.read_text(encoding="utf-8"))["skills"][0]["artifact"]
        asset = {
            "name": "example-1.0.0.zip", "size": artifact["size"],
            "digest": "sha256:" + artifact["sha256"],
        }
        self.enterContext(patch.dict(os.environ, {
            "GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": "rzx007/vykor-skills",
            "GITHUB_REF": "refs/heads/main", "GITHUB_SHA": "a" * 40,
        }))
        for mismatch in ({"digest": "sha256:" + "0" * 64}, {"size": asset["size"] + 1}):
            with self.subTest(field=next(iter(mismatch))):
                releases = [[{"tag_name": "skills-v2", "draft": False, "assets": [asset]}],
                            [{"tag_name": "skills-v1", "draft": False, "assets": [{**asset, **mismatch}]}]]
                with patch.object(market, "gh", side_effect=[json.dumps(releases), json.dumps({
                    "tag_name": "skills-v3", "id": 3, "draft": True, "assets": [],
                }), "", ""]) as gh:
                    with self.assertRaisesRegex(ValueError, "skills-v1.*example-1.0.0.zip"):
                        market.publish()
                    gh.assert_called_once_with("api", "repos/rzx007/vykor-skills/releases?per_page=100",
                                               "--paginate", "--slurp")
                self.assertFalse((self.dist / "public").exists())


if __name__ == "__main__":
    unittest.main()
