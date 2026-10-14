from __future__ import annotations

import argparse
import json
from pathlib import Path


VOCABULARY_MARKER = "{{TYPE_CHOICES}}"


def _repository_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "_config" / "schema" / "vocabulary.json").is_file():
            return candidate
    raise ValueError("could not find _config/schema/vocabulary.json")


def _vocabulary(root: Path) -> dict[str, list[str]]:
    path = root / "_config" / "schema" / "vocabulary.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    definitions = schema.get("$defs", {})
    values: dict[str, list[str]] = {}
    for name in ("type", "status", "tag"):
        definition = definitions.get(name, {})
        enum = definition.get("enum")
        if not isinstance(enum, list) or any(not isinstance(value, str) for value in enum):
            raise ValueError(f"{path}: $defs.{name}.enum must be a string array")
        values[name] = enum
        if not values[name]:
            raise ValueError(f"{path}: {name} enum must not be empty")
    return values


def _choices(values: list[str]) -> str:
    escaped = [value.replace("\\", "\\\\").replace(",", "\\,").replace("|", "\\|") for value in values]
    return ",".join(escaped)


def _vocabulary_section(vocabulary: dict[str, list[str]]) -> str:
    labels = (("type", "Types"), ("status", "Statuses"), ("tag", "Tags"))
    lines = ["## Generated vocabulary", ""]
    for key, label in labels:
        values = vocabulary[key]
        if values:
            lines.append(f"- {label}: " + ", ".join(f"`{value}`" for value in values))
    return "\n".join(lines)


def _write_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def generate(root: Path) -> list[Path]:
    # Generate files using the repository vocabulary
    root = root.resolve()
    template_sources_dir = root / "_config" / "foam-templates"
    skill_sources_dir = root / "_config" / "agents-skills"
    vocabulary = _vocabulary(root)
    generated: list[Path] = []

    # Foam templates
    template_sources = sorted(template_sources_dir.glob("*.md"))
    if not template_sources:
        raise ValueError(f"no template sources found in {template_sources_dir}")
    for source in template_sources:
        content = source.read_text(encoding="utf-8")
        if VOCABULARY_MARKER in content:
            content = content.replace(VOCABULARY_MARKER, _choices(vocabulary["type"]))
        output = root / ".foam" / "templates" / source.name
        _write_if_changed(output, content)
        generated.append(output)

    # Skills
    # skill_sources = sorted(skill_sources_dir.glob("*/SKILL.md"))
    # if not skill_sources:
    #     raise ValueError(f"no skill sources found in {skill_sources_dir}")
    # section = _vocabulary_section(vocabulary)
    # for source in skill_sources:
    #     content = source.read_text(encoding="utf-8").rstrip()
    #     content = f"{content}\n\n{section}\n"
    #     output = root / ".agents" / "skills" / source.parent.name / "SKILL.md"
    #     _write_if_changed(output, content)
    #     generated.append(output)

    # VS Code snippets
    snippet: dict[str, object] = {
        "Type metadata": {
            "scope": "yaml",
            "prefix": "type",
            "body": f"type: ${{1|{_choices(vocabulary['type'])}|}}",
            "description": "Insert a type entry",
        },
        "Status metadata": {
            "scope": "yaml",
            "prefix": "status",
            "body": f"status: ${{1|{_choices(vocabulary['status'])}|}}",
            "description": "Insert a status entry",
        },
        "Tags metadata": {
            "scope": "yaml",
            "prefix": "tags",
            "body": 
                [
                    "tags:", 
                    f"  - ${{1|{_choices(vocabulary['tag'])}|}}",
                ],
            "description": "Insert first tag entry",
        },
        "Tags entry": {
            "scope": "yaml",
            "prefix": "tag",
            "body": f"${{1|{_choices(vocabulary['tag'])}|}}",
            "description": "Insert additional tag entry",
        }
    }
    snippet_path = root / ".vscode" / "brain-vocabulary.code-snippets"
    snippet_content = json.dumps(snippet, indent=2, ensure_ascii=False) + "\n"
    _write_if_changed(snippet_path, snippet_content)
    generated.append(snippet_path)
    return generated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="brain-generate-foam")
    parser.add_argument("--root", type=Path, help="repository root; defaults to the current directory or a parent")
    arguments = parser.parse_args(argv)
    try:
        root = _repository_root(arguments.root.resolve() if arguments.root else Path.cwd())
        outputs = generate(root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(f"Generated {len(outputs)} Foam artifacts in {root}")
    return 0
