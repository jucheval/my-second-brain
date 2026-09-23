from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
import yaml

WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
CONTRACT_FILES = ("note.schema.json", "source.schema.json", "vocabulary.json")


class _YamlLoader(yaml.SafeLoader):
    pass


_YamlLoader.yaml_implicit_resolvers = {
    key: [
        resolver
        for resolver in resolvers
        if resolver[0] != "tag:yaml.org,2002:timestamp"
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML front matter")

    _, front_matter, _ = text.split("---", 2)
    metadata = yaml.load(front_matter, Loader=_YamlLoader)
    if not isinstance(metadata, dict):
        raise ValueError("front matter must be a YAML mapping")
    return metadata


def _note_schema_validator(
    root: Path, allow_extra_properties: bool = False
) -> Draft202012Validator:
    schema_directory = root / "schema"
    note_path = schema_directory / "note.schema.json"
    source_path = schema_directory / "source.schema.json"
    vocabulary_path = schema_directory / "vocabulary.json"
    note_schema = json.loads(note_path.read_text(encoding="utf-8"))
    source_schema = json.loads(source_path.read_text(encoding="utf-8"))
    vocabulary = json.loads(vocabulary_path.read_text(encoding="utf-8"))
    if allow_extra_properties:
        note_schema = copy.deepcopy(note_schema)
        note_schema["additionalProperties"] = True
    registry = Registry().with_resources(
        [
            ("note.schema.json", Resource.from_contents(note_schema)),
            ("source.schema.json", Resource.from_contents(source_schema)),
            ("vocabulary.json", Resource.from_contents(vocabulary)),
        ]
    )
    return Draft202012Validator(
        note_schema,
        registry=registry,
        format_checker=FormatChecker(),
    )


def _contract_errors(root: Path) -> list[str]:
    errors = []
    for filename in CONTRACT_FILES:
        path = root / "schema" / filename
        if not path.is_file():
            errors.append(f"missing schema contract: {_display_path(path, root)}")
            continue
        try:
            contract = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(contract)
        except (OSError, json.JSONDecodeError, SchemaError) as error:
            errors.append(
                f"{_display_path(path, root)}: invalid schema contract: {error}"
            )
    return errors


def _schema_errors(
    root: Path, metadata: dict, allow_extra_properties: bool = False
) -> list[str]:
    validator = _note_schema_validator(root, allow_extra_properties)
    errors = []
    for error in sorted(
        validator.iter_errors(metadata), key=lambda item: list(item.path)
    ):
        field = ".".join(str(part) for part in error.path) or "front matter"
        errors.append(f"{field}: {error.message}")
    return errors


def _display_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _record_identifiers(
    identifiers: dict[str, list[str]], path: Path, root: Path, metadata: dict
) -> None:
    display_path = _display_path(path, root)
    note_id = metadata.get("id")
    if isinstance(note_id, str):
        identifiers.setdefault(note_id, []).append(display_path)

    sources = metadata.get("sources")
    if isinstance(sources, list):
        for index, source in enumerate(sources):
            if isinstance(source, dict) and isinstance(source.get("id"), str):
                location = f"{display_path}:sources[{index}]"
                identifiers.setdefault(source["id"], []).append(location)


def _required_root_index_errors(root: Path) -> list[str]:
    errors = []
    for folder_name in ("knowledge", "projects"):
        folder = root / folder_name
        if folder.exists() and not (folder / "index.md").is_file():
            errors.append(f"missing required index: {folder_name}/index.md")
    return errors


def _required_folder_index_errors(root: Path) -> list[str]:
    errors = []
    for folder_name in ("knowledge", "projects"):
        canonical_root = root / folder_name
        if not canonical_root.is_dir():
            continue
        for folder in sorted(
            path for path in canonical_root.rglob("*") if path.is_dir()
        ):
            if not (folder / "index.md").is_file():
                errors.append(
                    f"missing required index: {_display_path(folder, root)}/index.md"
                )
    return errors


def _folder_depth_errors(root: Path) -> list[str]:
    errors = []
    for folder_name in ("knowledge", "projects"):
        canonical_root = root / folder_name
        if not canonical_root.is_dir():
            continue
        for folder in sorted(
            path for path in canonical_root.rglob("*") if path.is_dir()
        ):
            depth = len(folder.relative_to(canonical_root).parts)
            if depth > 2:
                errors.append(
                    f"maximum folder depth exceeded: {_display_path(folder, root)}"
                )
    return errors


def _minimal_metadata_errors(
    metadata: dict, expected_type: str, expected_title: str | None = None
) -> list[str]:
    errors = []
    if metadata.get("type") != expected_type:
        errors.append(f"type: expected '{expected_type}'")
    if not isinstance(metadata.get("title"), str) or not metadata["title"]:
        errors.append("title: must be a non-empty string")
    elif expected_title is not None and metadata["title"] != expected_title:
        errors.append(f"title: expected '{expected_title}'")
    unexpected = sorted(set(metadata) - {"type", "title"})
    for field in unexpected:
        errors.append(f"unexpected field '{field}'")
    return errors


def _metadata_errors_for_path(root: Path, path: Path, metadata: dict) -> list[str]:
    if path.name == "index.md":
        return _minimal_metadata_errors(metadata, "index")
    if path.name == "CONTEXT.md":
        expected_title = "root-context" if path == root / "CONTEXT.md" else None
        return _minimal_metadata_errors(metadata, "context", expected_title)
    return _schema_errors(root, metadata, path.relative_to(root).parts[0] == "inbox")


def _authored_markdown_files(root: Path) -> list[Path]:
    paths = [root / "CONTEXT.md"] if (root / "CONTEXT.md").is_file() else []
    for folder_name in ("inbox", "journal", "knowledge", "projects"):
        folder = root / folder_name
        if folder.is_dir():
            paths.extend(path for path in folder.rglob("*.md") if path.is_file())
    return sorted(paths)


def _wikilink_targets_for_path(path: Path, root: Path) -> set[str]:
    relative = path.relative_to(root).with_suffix("").as_posix()
    targets = {relative, path.stem}
    parts = PurePosixPath(relative).parts
    if parts and parts[0] in {"knowledge", "projects"}:
        targets.add(PurePosixPath(*parts[1:]).as_posix())
    return targets


def _wikilink_errors(
    path: Path, root: Path, known_targets: set[str], text: str
) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []
    canonical = path.relative_to(root).parts[0] != "inbox"
    for match in WIKILINK_PATTERN.finditer(text):
        target = match.group(1).strip()
        if target in known_targets:
            continue
        message = f"unresolved wikilink '{target}'"
        (errors if canonical else warnings).append(message)
    return errors, warnings


def _source_warnings(path: Path, root: Path, metadata: dict) -> list[str]:
    warnings = []
    sources = metadata.get("sources")
    if not isinstance(sources, list):
        return warnings
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            continue
        url = source.get("url")
        if isinstance(url, str) and url.startswith("http://"):
            warnings.append(
                f"{_display_path(path, root)}: HTTP source URL '{url}' "
                f"(sources[{index}])"
            )
        location = source.get("location")
        if not isinstance(location, str):
            continue
        source_path = root.joinpath(*PurePosixPath(location).parts)
        if not source_path.is_file():
            warnings.append(
                f"{_display_path(path, root)}: missing local source file "
                f"'{location}' (sources[{index}])"
            )
    return warnings


def _journal_path_errors(path: Path, root: Path) -> list[str]:
    relative = path.relative_to(root / "journal")
    if len(relative.parts) != 1:
        return ["journal notes must be flat"]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", path.name):
        return ["journal note filename must be YYYY-MM-DD.md"]
    return []


def _index_completeness_errors(root: Path, markdown_files: list[Path]) -> list[str]:
    errors = []
    canonical_roots = {root / "knowledge", root / "projects"}
    for index_path in markdown_files:
        if (
            index_path.name != "index.md"
            or index_path.parent not in canonical_roots
            and not any(
                index_path.parent.is_relative_to(canonical_root)
                for canonical_root in canonical_roots
            )
        ):
            continue
        try:
            index_text = index_path.read_text(encoding="utf-8")
        except OSError as error:
            errors.append(f"{_display_path(index_path, root)}: {error}")
            continue
        linked_targets = {
            match.group(1).strip() for match in WIKILINK_PATTERN.finditer(index_text)
        }
        for note_path in sorted(index_path.parent.glob("*.md")):
            if note_path.name in {"index.md", "CONTEXT.md"}:
                continue
            targets = {
                note_path.stem,
                note_path.relative_to(root).with_suffix("").as_posix(),
            }
            try:
                metadata = _front_matter(note_path)
            except (OSError, ValueError, yaml.YAMLError):
                metadata = {}
            note_id = metadata.get("id")
            if isinstance(note_id, str):
                targets.add(note_id)
            if not targets & linked_targets:
                errors.append(
                    f"{_display_path(index_path, root)}: missing link to "
                    f"{_display_path(note_path, root)}"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="brain-validate")
    parser.add_argument("path", nargs="?", default=".")
    arguments = parser.parse_args(argv)
    root = Path(arguments.path).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    identifiers: dict[str, list[str]] = {}
    errors.extend(_contract_errors(root))
    errors.extend(_required_root_index_errors(root))
    errors.extend(_required_folder_index_errors(root))
    errors.extend(_folder_depth_errors(root))

    markdown_files = _authored_markdown_files(root)
    for path in markdown_files:
        if path.relative_to(root).parts[0] == "journal":
            errors.extend(
                f"{_display_path(path, root)}: {error}"
                for error in _journal_path_errors(path, root)
            )
        try:
            metadata = _front_matter(path)
            if path.name not in {"index.md", "CONTEXT.md"}:
                _record_identifiers(identifiers, path, root, metadata)
            for error in _metadata_errors_for_path(root, path, metadata):
                errors.append(f"{_display_path(path, root)}: {error}")
            warnings.extend(_source_warnings(path, root, metadata))
        except (
            OSError,
            ValueError,
            json.JSONDecodeError,
            SchemaError,
            yaml.YAMLError,
        ) as error:
            errors.append(f"{_display_path(path, root)}: {error}")

    known_targets = set(identifiers)
    for path in markdown_files:
        known_targets.update(_wikilink_targets_for_path(path, root))
    errors.extend(_index_completeness_errors(root, markdown_files))

    for path in markdown_files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as error:
            errors.append(f"{_display_path(path, root)}: {error}")
            continue
        link_errors, link_warnings = _wikilink_errors(path, root, known_targets, text)
        errors.extend(f"{_display_path(path, root)}: {error}" for error in link_errors)
        warnings.extend(
            f"{_display_path(path, root)}: {warning}" for warning in link_warnings
        )

    for identifier, locations in sorted(identifiers.items()):
        if len(locations) > 1:
            errors.append(f"duplicate id '{identifier}': {', '.join(locations)}")

    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
