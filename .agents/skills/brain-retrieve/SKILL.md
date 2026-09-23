---
name: brain-retrieve
description: Search repository notes and synthesize an answer with explicit statuses, links, conflicts, and source provenance.
disable-model-invocation: true
---

# Retrieve

Answer a user question from the repository's Markdown notes and, when necessary, their referenced sources. Keep evidence visible: every note result has a status, stable notes rank first, and unresolved conflicts remain unresolved in the answer.

## Retrieval contract

Use these repository-root JSON schemas when interpreting front matter:

- `schema/note.schema.json` defines note fields and statuses.
- `schema/vocabulary.json` defines types, tags, IDs, author identities, and timestamps.
- `schema/source.schema.json` defines source-entry fields and source locations.

Search `inbox/`, `journal/`, `knowledge/`, and `projects/`, including their `index.md` and `CONTEXT.md` files when relevant. Use Foam wikilinks and repository-relative paths as evidence references.

By default, include all note statuses and rank them in this order:

1. `stable`
2. `draft`
3. `deprecated`

Display the status of every note used or returned. Apply an explicit status filter when the user requests one.

## Steps

1. Parse the request into the question, requested scope, status filter, time or folder constraints, and any source requirement. Ask one focused clarification when the request has multiple materially different interpretations.
2. Search note titles, front matter, tags, headings, body text, indexes, and relevant context files. Use exact terms first, then linked or clearly related terms. Keep a record of the paths and statuses considered.
3. Rank candidate notes by status, direct relevance, and link proximity. Read the strongest candidates and follow relevant wikilinks to stable notes. Read an applicable `CONTEXT.md` before interpreting domain terminology.
4. Surface terminology conflicts. When the user's wording conflicts with a relevant `CONTEXT.md`, show the repository term and the user's term, then ask the user which meaning to use. Preserve the ambiguity in any interim report.
5. Compare claims across the selected notes. When notes contradict one another, show the conflicting note paths, statuses, and claims, then ask the user to resolve the conflict. Keep the conflicting claims separate; provide no synthesized conclusion from them.
6. Inspect source entries only when repository notes do not provide enough evidence or the user asks about the source itself. Validate source metadata against `schema/source.schema.json` before using it.
7. Use an existing local source file when `location` is present and the file exists. When source knowledge is needed and the file is absent, ask the user for a complete repository-relative `location` before downloading.
8. Download only public PDF or webpage sources through direct `http` or `https` URLs. Keep the file in the user-provided dedicated source directory under `assets/`. Convert a webpage to Markdown under `assets/webpages/` when Markdown is the useful reading format. Read the local file after downloading it.
9. If a download fails, report the source and failure and ask the user to download it manually. State clearly which conclusions rely only on repository notes. Never claim to have read an unavailable source.
10. Synthesize the answer from the evidence that remains. Link each material claim to the relevant note or source, distinguish quotation from inference, and label uncertainty. Return the answer without editing notes, metadata, indexes, or Git state.

## Source and mutation boundaries

Retrieve may create or update an ignored local source-cache file only when the source is required for the current retrieval. It may not change a note, front matter, `index.md`, `CONTEXT.md`, branch, commit, or tracked asset.

Source downloads use public direct URLs. Authentication, paywall, and access-control bypasses are outside the retrieval path. A source with no URL or invalid required metadata is unresolved and must be reported as such.

## Completion checks

Retrieval is complete only when all applicable conditions are satisfied:

- The request's interpretation or clarification is explicit.
- Search coverage includes the relevant repository areas and context files.
- Every returned or cited note has its path and `status` shown.
- Stable notes are ranked before draft and deprecated notes unless the user supplied another filter.
- Relevant wikilinks were followed or the remaining search boundary is reported.
- Terminology conflicts are visible and unresolved conflicts are presented without a fabricated conclusion.
- Every material claim has a repository note or source reference.
- Any source needed for the answer was read locally, or its missing/download failure was reported.
- No unavailable source is represented as read evidence.
- No note, metadata, index, context file, tracked asset, or Git state was modified.

Report the answer, evidence links, statuses, unresolved conflicts, and search limitations. When evidence is insufficient, say what was searched and what additional decision or source is required instead of filling the gap with an assumption.
