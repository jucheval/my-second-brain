import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from brain_validator.cli import main

REPOSITORY_ROOT = Path(__file__).parents[1]


def _copy_schema(root: Path) -> None:
    schema_directory = root / "_config" / "schema"
    schema_directory.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(REPOSITORY_ROOT / "schema", schema_directory)


class ValidatorCliTests(unittest.TestCase):
    def test_accepts_valid_inbox_note(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inbox").mkdir()
            _copy_schema(root)
            (root / "inbox" / "first-note.md").write_text(
                "---\n"
                "id: first-note\n"
                "type: concept\n"
                "title: First note\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T14:00:00+02:00\n"
                "status: draft\n"
                "---\n\n"
                "A useful draft.\n",
                encoding="utf-8",
            )

            with contextlib.redirect_stdout(io.StringIO()):
                result = main([str(root)])

            self.assertEqual(result, 0)

    def test_reports_missing_required_field(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inbox").mkdir()
            _copy_schema(root)
            (root / "inbox" / "incomplete.md").write_text(
                "---\n"
                "id: incomplete-note\n"
                "type: concept\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "---\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 1)
            self.assertIn("inbox/incomplete.md", output.getvalue())
            self.assertIn("title", output.getvalue())

    def test_rejects_unknown_type(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inbox").mkdir()
            _copy_schema(root)
            (root / "inbox" / "unknown-type.md").write_text(
                "---\n"
                "id: unknown-type\n"
                "type: unknown\n"
                "title: Unknown type\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "---\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 1)
            self.assertIn("unknown-type.md", output.getvalue())
            self.assertIn("type", output.getvalue())

    def test_rejects_duplicate_note_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inbox").mkdir()
            _copy_schema(root)
            note = (
                "---\n"
                "id: duplicate-note\n"
                "type: concept\n"
                "title: Duplicate note\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "---\n"
            )
            (root / "inbox" / "first.md").write_text(note, encoding="utf-8")
            (root / "inbox" / "second.md").write_text(note, encoding="utf-8")

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 1)
            self.assertIn("duplicate-note", output.getvalue())
            self.assertIn("duplicate", output.getvalue())

    def test_rejects_source_id_matching_note_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inbox").mkdir()
            _copy_schema(root)
            (root / "inbox" / "note.md").write_text(
                "---\n"
                "id: shared-id\n"
                "type: concept\n"
                "title: Note\n"
                "sources:\n"
                "  - id: shared-id\n"
                "    title: Source\n"
                "    url: https://example.org/source\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "---\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 1)
            self.assertIn("duplicate id 'shared-id'", output.getvalue())
            self.assertIn("sources[0]", output.getvalue())

    def test_indexes_are_optional_and_need_no_front_matter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            topic = root / "knowledge" / "probability"
            topic.mkdir(parents=True)
            _copy_schema(root)
            (root / "knowledge" / "index.md").write_text(
                "A folder overview without metadata.\n", encoding="utf-8"
            )
            (topic / "conditional-probability.md").write_text(
                "---\n"
                "id: conditional-probability\n"
                "type: concept\n"
                "title: Conditional probability\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "---\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 0)

    def test_context_file_needs_no_front_matter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _copy_schema(root)
            (root / "CONTEXT.md").write_text(
                "Repository terminology lives here.\n", encoding="utf-8"
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 0)
            self.assertEqual(output.getvalue(), "")

    def test_validates_canonical_note_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "knowledge").mkdir()
            _copy_schema(root)
            (root / "knowledge" / "index.md").write_text(
                "---\n" "type: index\n" "title: knowledge-index\n" "---\n",
                encoding="utf-8",
            )
            (root / "knowledge" / "bad-note.md").write_text(
                "---\n"
                "id: bad-note\n"
                "type: unknown\n"
                "title: Bad note\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "---\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 1)
            self.assertIn("knowledge/bad-note.md", output.getvalue())
            self.assertIn("type", output.getvalue())

    def test_rejects_canonical_note_beyond_maximum_depth(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deep_folder = root / "knowledge" / "a" / "b" / "c"
            deep_folder.mkdir(parents=True)
            _copy_schema(root)
            (deep_folder / "too-deep.md").write_text(
                "---\n"
                "id: too-deep\n"
                "type: concept\n"
                "title: Too deep\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "---\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 1)
            self.assertIn("maximum folder depth", output.getvalue())

    def test_does_not_check_unresolved_wikilinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "knowledge").mkdir()
            _copy_schema(root)
            (root / "knowledge" / "linked-note.md").write_text(
                "---\n"
                "id: linked-note\n"
                "type: concept\n"
                "title: Linked note\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "---\n\n"
                "See [[missing-note]].\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 0)
            self.assertEqual(output.getvalue(), "")

    def test_warns_when_optional_local_source_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inbox").mkdir()
            _copy_schema(root)
            (root / "inbox" / "source-note.md").write_text(
                "---\n"
                "id: source-note\n"
                "type: concept\n"
                "title: Source note\n"
                "sources:\n"
                "  - id: missing-source\n"
                "    title: Missing source\n"
                "    url: https://example.org/source\n"
                "    location: assets/papers/missing.pdf\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "---\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 0)
            self.assertIn("warning", output.getvalue())
            self.assertIn("missing local source file", output.getvalue())

    def test_warns_for_http_source_url(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inbox").mkdir()
            _copy_schema(root)
            (root / "inbox" / "http-source.md").write_text(
                "---\n"
                "id: http-source\n"
                "type: concept\n"
                "title: HTTP source\n"
                "sources:\n"
                "  - id: http-reference\n"
                "    title: HTTP reference\n"
                "    url: http://example.org/source\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "---\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 0)
            self.assertIn("HTTP source URL", output.getvalue())

    def test_rejects_malformed_schema_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _copy_schema(root)
            (root / "_config" / "schema" / "note.schema.json").write_text(
                "{ malformed\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 1)
            self.assertIn("_config/schema/note.schema.json", output.getvalue())

    def test_rejects_index_and_context_note_types(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inbox").mkdir()
            _copy_schema(root)
            for note_type in ("index", "context"):
                (root / "inbox" / f"{note_type}-type.md").write_text(
                    "---\n"
                    f"id: {note_type}-note\n"
                    f"type: {note_type}\n"
                    f"title: {note_type.title()}\n"
                    "generated:\n"
                    "  - by: ai:test@1\n"
                    "    at: 2026-09-24T12:00:00Z\n"
                    "status: draft\n"
                    "---\n",
                    encoding="utf-8",
                )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 1)
            self.assertIn("type", output.getvalue())
            self.assertIn("'index' is not one of", output.getvalue())
            self.assertIn("'context' is not one of", output.getvalue())

    def test_accepts_crlf_front_matter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inbox").mkdir()
            _copy_schema(root)
            (root / "inbox" / "windows-note.md").write_bytes(
                (
                    "---\n"
                    "id: windows-note\n"
                    "type: concept\n"
                    "title: Windows note\n"
                    "generated:\n"
                    "  - by: ai:test@1\n"
                    "    at: 2026-09-24T12:00:00Z\n"
                    "status: draft\n"
                    "---\n"
                )
                .replace("\n", "\r\n")
                .encode("utf-8")
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 0)

    def test_allows_extra_inbox_capture_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inbox").mkdir()
            _copy_schema(root)
            (root / "inbox" / "capture.md").write_text(
                "---\n"
                "id: capture-note\n"
                "type: concept\n"
                "title: Capture note\n"
                "generated:\n"
                "  - by: ai:test@1\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "capture_context: Preserve this raw context.\n"
                "---\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 0)

    def test_accepts_nested_journal_note_with_non_date_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            journal = root / "journal" / "2026"
            journal.mkdir(parents=True)
            _copy_schema(root)
            (journal / "09-24.md").write_text(
                "---\n"
                "id: journal-entry\n"
                "type: journal\n"
                "title: Journal entry\n"
                "generated:\n"
                "  - by: human:test-user\n"
                "    at: 2026-09-24T12:00:00Z\n"
                "status: draft\n"
                "---\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                result = main([str(root)])

            self.assertEqual(result, 0)
            self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
