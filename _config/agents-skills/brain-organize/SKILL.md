---
name: brain-organize
description: Organizes selected draft notes into knowledge or projects.
argument-hint: Which draft notes should be organized?
disable-model-invocation: true
---

<!-- LEGACY -->

# Organize

Organize selected draft notes into `knowledge/` or `projects/`. Preserve the notes' meaning, keep stable knowledge intact, and leave promotion and verification to the human reviewer.

1. Identify the scope of the selected draft notes.
2. Choose a target folder. Ask for a target or scope decision when more than one organization is defensible.
3. If present, read `CONTEXT.md` from the target folder and its parents. Treat terminology in `CONTEXT.md` as binding. Surface a terminology conflict and ask the user to resolve it before changing files.
4. Ask user for approval of the organization.
5. For every selected draft note,
   - [ ] move it to destination,
   - [ ] add Foam wikilinks to and from relevant notes including `index.md`.
6. If a new folder is created, add an `index.md` with relevant wikilinks.
7. **Validate**: run `brain-validate .`. If it is not exposed, tell the user to modify this skill with the correct command.
8. If validation fails, fix the issues and run validation again.

Report the identified scope and validation status.

If the user passed arguments, treat them as a description of the selected draft notes. Otherwise, select all notes in `inbox/`.

<contract>
`knowledge/` contains reusable concepts and reference material. `projects/` contains work with an objective, deliverables, and a lifecycle.

Every canonical topic or project folder has an `index.md`. Root indexes are required at `knowledge/index.md` and `projects/index.md`. `CONTEXT.md` is optional and defines terminology when present.

Do not modify any YAML frontmatter.
</contract>
