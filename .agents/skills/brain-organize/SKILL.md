---
name: brain-organize
description: Propose a coherent organization of draft notes into knowledge or projects on a reviewable Git branch.
disable-model-invocation: true
---

# Organize

Turn one coherent set of draft notes into a reviewable Git proposal. Preserve the notes' meaning, keep stable knowledge intact, and leave promotion and verification to the human reviewer.

## Organization contract

Use these repository-root JSON schemas as the metadata authority:

- `schema/note.schema.json` defines note field shapes and required keys.
- `schema/vocabulary.json` defines allowed types, tags, statuses, IDs, author identities, and timestamps.
- `schema/source.schema.json` defines source-entry keys and constraints.

Read the applicable schemas before editing front matter. Use Foam wikilinks for internal links.

`knowledge/` contains reusable concepts and reference material. `projects/` contains work with an objective, deliverables, and a lifecycle. A project overview uses `type: project`; other project notes use their content type.

The maximum depth is two folder levels below `knowledge/` or `projects/`. Every canonical topic or project folder has an `index.md`. Root indexes are required at `knowledge/index.md` and `projects/index.md`. `CONTEXT.md` is optional and defines terminology when present.

A proposal branch is named:

```text
organize/YYYY-MM-DD-short-description
```

The only status Organize may write is `draft`. Human reviewers set `stable` or `deprecated` and add or update `verified`.

## Steps

1. Identify the notes and scope from the user's request. Organize only the named notes and the directly required index or link updates. Ask for a target or scope decision when more than one organization is defensible.
2. Read each source note, its existing wikilinks, related stable notes, the target folder's `index.md`, and any applicable `CONTEXT.md`. Treat terminology in `CONTEXT.md` as binding. Surface a terminology conflict and ask the user to resolve it before changing files.
3. Inspect the current Git branch and working tree. Preserve unrelated user changes. Require a clean working tree for the proposal; when unrelated changes are present, stop and ask the user to commit or otherwise clear them. Never stash, reset, or discard user changes.
4. Choose a target under `knowledge/` or `projects/` with at most two folder levels below the root. Keep project execution notes under `projects/`. Preserve existing IDs by default; propose an ID change only when the user requests it or an explicit organization decision requires it, and update every affected wikilink in the same proposal.
5. Prepare a change plan before creating the branch. For every note, state its target path, any metadata edit, links to add, and index changes. Keep substantive prose and claims unchanged unless the user explicitly requests an edit.
6. Create a unique branch named `organize/YYYY-MM-DD-short-description`. Add a numeric suffix when that branch name already exists. Keep the proposal isolated from the user's main branch.
7. Apply only the planned organization changes:
   - Move notes into `knowledge/` or `projects/`.
   - Edit `id`, `type`, `title`, `description`, `tags`, or `sources` when the plan requires it and the result validates against the schemas.
   - Append a `generated` entry with the actual namespaced agent identity and the current machine-local time with its numeric UTC offset for material AI edits.
   - Add relevant Foam wikilinks to the draft notes and update affected `index.md` files.
   - Create a new folder's `index.md` with `type: index` and its `path-to-folder-index` title when the target folder does not have one.
8. Keep every organized note at `status: draft`. Preserve `verified` unchanged and leave stable or deprecated notes unchanged. Keep source references explicit and valid; Organize does not download source files.
9. Review the branch diff against the starting point. Stage only planned files and create one proposal commit. Leave the branch unmerged for human review. Report the branch and commit so the human can review, update status and verification metadata, and merge it.
10. If the repository exposes `brain-validate`, run it against the proposal and report the result. If it is not exposed, do not perform or claim the completion checks; report that validation is unavailable and ask the user to perform manual validation.

## Completion checks

When `brain-validate` is available, the proposal is complete only when the validation passes. When it is unavailable, do not perform or claim the completion checks; report that validation is unavailable and ask the user to perform manual validation.

Report the branch and validation status. Stop before creating or modifying files whenever scope, target, terminology, Git state, or required metadata cannot be resolved without inventing a decision.
