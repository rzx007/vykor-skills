import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from market import package_skill


class MarketTest(unittest.TestCase):
    def test_packages_pinned_skill_with_references_and_license(self):
        source = io.BytesIO()
        with zipfile.ZipFile(source, "w") as z:
            z.writestr("upstream/SKILL.md", "---\nname: example\n---\nRead refs.")
            z.writestr("upstream/references/guide.md", "guide")
            z.writestr("upstream/tests/test.py", "not runtime content")
            z.writestr("upstream/LICENSE", "upstream notice")
        entry = {
            "name": "example", "license": "MIT",
            "path": ".", "include": ["SKILL.md", "references"],
            "licensePath": "LICENSE",
        }
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "example.zip"
            package_skill(entry, source, output)
            first = output.read_bytes()
            package_skill(entry, source, output)
            self.assertEqual(first, output.read_bytes())
            with zipfile.ZipFile(output) as z:
                self.assertEqual(z.namelist(), ["LICENSE", "SKILL.md", "references/guide.md"])
                self.assertEqual(z.read("LICENSE"), b"upstream notice")

    def test_rejects_traversal_and_name_mismatch(self):
        entry = {"name": "example", "license": "MIT", "path": ".", "licensePath": "LICENSE"}
        for path, name, error in [
            ("references/../unexpected", "example", "unsafe"),
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


if __name__ == "__main__":
    unittest.main()
