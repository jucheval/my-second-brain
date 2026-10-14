---
name: brain-capture
description: Creates a draft note in inbox from the user's supplied idea, text, or source reference.
argument-hint: What idea or source reference should be captured?
disable-model-invocation: true
---

<!-- LEGACY -->

# Capture

Create one draft in `inbox/` from the user's supplied material. Preserve the user's meaning.

1. Read and apply the repository-root JSON schemas before choosing metadata.
2. Identify the capture material.
3. Write the note to `inbox/<id>.md` with metadata satisfying the `<contract>`.
4. **Validate**: run `brain-validate .`. If it is not exposed, tell the user to modify this skill with the correct command.
5. If validation fails, fix the issues and run validation again.

Report the new file and validation status.

<contract>
Use these repository-root JSON schemas as the metadata authority for every captured note:

- `_config/schema/note.schema.json` defines required note keys (`id`, `type`, `title`, `generated`, and `status`) and optional keys shape.
- `_config/schema/vocabulary.json` defines allowed types, tags, statuses, IDs, author identities, and timestamps.
- `_config/schema/source.schema.json` defines source-entry keys and constraints.

Each draft note must have a YAML front matter with these required keys:

```yaml
---
id: <unique-id>
type: <allowed-type>
title: <title>
generated:
  - by: ai:<model>[@<version>]
    at: <YYYY-MM-DDTHH:MM:SS+HH:MM>
status: draft
---
```

Add `description`, `tags`, and `sources` only when supported by the supplied material.

Write only allowed tags and list others as candidates.

Use lowercase ASCII kebab-case for IDs, beginning and ending with an alphanumeric character. Generated IDs use `-2`, `-3`, and so on for collisions across the repository.

The `generated` list is append-only. Each entry contains:

- `by`: `ai:<model>[@<version>]`, where `<model>` is your own model name with no spaces.
- `at`: the output of `python3 -c 'import datetime; print(datetime.datetime.now().astimezone().isoformat(timespec="seconds"))'`.

Each source entry requires `id`, `title`, and a `url`.
</contract>
