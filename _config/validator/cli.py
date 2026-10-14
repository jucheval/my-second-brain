from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
import yaml

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
    schema_directory = root / "_config" / "schema"
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
        path = root / "_config" / "schema" / filename
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


def _authored_markdown_files(root: Path) -> list[Path]:
    paths = []
    for folder_name in ("inbox", "journal", "knowledge", "projects"):
        folder = root / folder_name
        if folder.is_dir():
            paths.extend(
                path
                for path in folder.rglob("*.md")
                if path.is_file() and path.name not in {"index.md", "CONTEXT.md"}
            )
    return sorted(paths)


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="brain-validate")
    parser.add_argument("path", nargs="?", default=".")
    arguments = parser.parse_args(argv)
    root = Path(arguments.path).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    identifiers: dict[str, list[str]] = {}
    errors.extend(_contract_errors(root))
    errors.extend(_folder_depth_errors(root))

    markdown_files = _authored_markdown_files(root)
    for path in markdown_files:
        try:
            metadata = _front_matter(path)
            _record_identifiers(identifiers, path, root, metadata)
            for error in _schema_errors(
                root, metadata, path.relative_to(root).parts[0] == "inbox"
            ):
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
