---
name: brain-capture
description: Create a valid draft note in inbox from the user's supplied idea, text, or source reference.
disable-model-invocation: true
---

# Capture

Create one useful draft in `inbox/` from the user's supplied material. Preserve the user's meaning and uncertainty; do not organize the note into `knowledge/` or `projects/`.

## Capture contract

Use these repository-root JSON schemas as the metadata authority for every captured note:

- `schema/note.schema.json` defines required ordinary-note keys (`id`, `type`, `title`, `generated`, and `status`) and optional field shapes.
- `schema/vocabulary.json` defines allowed types, tags, statuses, IDs, author identities, and timestamps.
- `schema/source.schema.json` defines source-entry keys and constraints.

Read the applicable schema before choosing metadata. Do not duplicate or extend enum values in this skill.

Each note has one primary `type`. If the type is uncertain, use the least-specific defensible type from `schema/vocabulary.json` and add a `type_candidates` list containing plausible allowed types.

Tags are lowercase and flat. Omit useful tags that are not allowed by `schema/vocabulary.json` and report them as vocabulary candidates.

IDs for notes and sources are globally unique. Use lowercase ASCII kebab-case, beginning and ending with an alphanumeric character. Generated IDs use `-2`, `-3`, and so on for collisions. Do not change an existing ID automatically when a title changes.

The `generated` list is append-only. Each entry contains `by` and `at`; use the actual namespaced agent identity and the current machine-local timestamp with its numeric UTC offset in ISO 8601 format (for example, `2026-09-25T10:33:00+02:00`). Use `Z` only when the machine's local timezone is UTC. Human edits that materially change the note append a human entry. Status-only and verification-only changes do not.

The only status Capture may write is `draft`.

Each source entry requires `id`, `title`, and an `http` or `https` `url`. `location` and `sha256` are optional. When present, `location` must be an explicit repository-relative POSIX path inside `assets/papers/`, `assets/books/`, `assets/webpages/`, `assets/datasets/`, `assets/software/`, or `assets/other/`. Reject absolute paths, `..` traversal, and Windows backslashes. Capture never downloads source files.

## Steps

1. Read and apply the repository-root JSON schemas before choosing metadata.
2. Identify the capture material and decide whether the user is creating a new note or explicitly revising an existing draft. Preserve the existing `id` when revising a named draft.
3. Choose the narrowest defensible `type` allowed by `schema/vocabulary.json`. When the type is uncertain, choose the least-specific defensible type and add `type_candidates` with the plausible alternatives. Never invent a new type during capture.
4. Set the display `title`. If the user did not provide one, derive a concise title from the material and state that it was inferred.
5. Create a lowercase ASCII kebab-case `id` from the title when no ID is provided. Search front matter across the repository for global ID collisions. For a generated ID, append `-2`, `-3`, and so on until it is unique. For a user-supplied ID collision, ask for a replacement instead of silently changing it.
6. Apply only lowercase tags allowed by `schema/vocabulary.json`. If a useful tag is not in the vocabulary, leave it out and report it as a vocabulary candidate; do not add an unknown tag.
7. Copy the supplied Markdown into the note body. Preserve links, code, equations, and explicit uncertainty. Add a single `# {title}` heading only when the body has no equivalent title heading.
8. Add YAML front matter with the required fields:

   ```yaml
   ---
   id: <unique-id>
   type: <allowed-type>
   title: <title>
   generated:
     - by: <actual-agent-identity>
      at: <current-machine-local-time-with-offset>
   status: draft
   ---
   ```

Add `description`, `tags`, `sources`, and `type_candidates` only when supported by the supplied material. Keep `verified` absent. Validate source entries against `schema/source.schema.json`; never fabricate missing source values.

9. Write the note to `inbox/<id>.md`. Do not move it to a canonical folder, change its status beyond `draft`, modify `verified`, create a Git branch, commit changes, or download a source.
10. If the repository exposes `brain-validate`, run it against the new note and report the result. If it is not exposed, do not perform or claim the completion checks; report that validation is unavailable and ask the user to perform manual validation.

## Completion checks

When `brain-validate` is available, the proposal is complete only when the validation passes. When it is unavailable, do not perform or claim the completion checks; report that validation is unavailable and ask the user to perform manual validation.

Report the new file and validation status. Stop before creating or modifying files whenever scope, target, terminology, Git state, or required metadata cannot be resolved without inventing a decision.
