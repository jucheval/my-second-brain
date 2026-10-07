import json
import tempfile
import unittest
from pathlib import Path

from generator.cli import generate


class FoamGeneratorTests(unittest.TestCase):
    def test_generation_is_deterministic_and_uses_vocabulary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            templates = root / "_config" / "foam-templates"
            skills = root / "_config" / "agents-skills" / "brain-capture"
            templates.mkdir(parents=True)
            skills.mkdir(parents=True)
            (root / "_config" / "schema").mkdir(parents=True)
            (root / "_config" / "schema" / "vocabulary.json").write_text(
                json.dumps(
                    {
                        "$defs": {
                            "type": {"enum": ["concept", "method"]},
                            "status": {"enum": ["draft", "stable"]},
                            "tag": {"enum": ["julia"]},
                        }
                    }
                ),
                encoding="utf-8",
            )
            (templates / "regular-note.md").write_text(
                "type: ${1|{{TYPE_CHOICES}}|}\n", encoding="utf-8"
            )
            (skills / "SKILL.md").write_text(
                "# Capture\n\nHuman-authored workflow.\n", encoding="utf-8"
            )

            outputs = generate(root)
            first = {path.relative_to(root): path.read_bytes() for path in outputs}
            generate(root)
            second = {path.relative_to(root): path.read_bytes() for path in outputs}

            self.assertEqual(first, second)
            template = (root / ".foam" / "templates" / "regular-note.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("${1|concept,method|}", template)
            skill = (root / ".agents" / "skills" / "brain-capture" / "SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Human-authored workflow.", skill)
            self.assertIn("- Types: `concept`, `method`", skill)
            self.assertIn("- Tags: `julia`", skill)
            snippets = json.loads(
                (root / ".vscode" / "brain-vocabulary.code-snippets").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(snippets["Second Brain vocabulary fields"]["prefix"], "brain-vocabulary")


if __name__ == "__main__":
    unittest.main()
