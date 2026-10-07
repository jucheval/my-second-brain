# 01: Align note validation with the new contract

**What to build:** Notes validate without index or journal-layout rules, while the retained validation checks continue to work.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Keep globally unique note/source IDs, schema validation, folder-depth limits, and warnings for HTTP sources or missing cached files.
- [ ] Remove index existence/completeness, journal filename/layout, and unresolved-wikilink checks; remove frontmatter requirements for `index.md` and `CONTEXT.md`.
- [ ] Remove `index` and `context` from the vocabulary's note type enum.
- [ ] Tests cover retained checks and confirm removed checks no longer reject notes.
