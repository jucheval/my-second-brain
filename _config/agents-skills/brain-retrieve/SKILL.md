---
name: brain-retrieve
description: Use when the user invokes /brain-retrieve or asks to search, compare, or synthesize knowledge-base notes for the current prompt through the configured read-only Foam MCP server.
disable-model-invocation: true
---

<!-- LEGACY -->

# Retrieve

Answer the user's current question using relevant notes from the configured Foam knowledge base. This skill is user-invoked only; do not preload it for unrelated prompts or delegate the retrieval to a per-session agent.

## Read-only boundary

- Use the configured `foam` MCP server and its read tools only. Discover available tools from the server rather than assuming unavailable capabilities.
- Start with `get_workspace_info` when available to confirm the connected knowledge base. If the server is unavailable, disconnected, or points to the wrong workspace, stop and report that; do not silently fall back to workspace-wide file searches.
- Search and inspect notes with read tools such as `search_resources`, `search_by_property`, `search_by_tag`, `list_resources`, `get_resource`, and `read_resource`. Follow relevant links with `get_connections` or `traverse_graph` when available.
- Never call note or tag creation, update, deletion, move, or rename tools. Do not edit notes, metadata, indexes, context files, assets, or Git state.

## Retrieval steps

1. Use the current prompt and conversation context to identify the question, likely concepts, requested scope, status or time filters, and whether sources are needed. Ask one focused clarification only when materially different interpretations would change the search.
2. Search the Foam graph for exact terms first, then relevant related terms. Search titles, note text, tags, and frontmatter properties as supported by the available read tools. Keep searches within the configured knowledge base.
3. Rank relevant notes by directness and status: `stable`, then `draft`, then `deprecated`, unless the user specifies a different filter. Include all statuses when no filter is requested.
4. Read the strongest candidate notes and follow relevant Foam links. Read applicable `CONTEXT.md` and `index.md` resources when they help interpret terminology or locate related notes.
5. Preserve terminology conflicts and contradictory claims. Show which notes disagree and ask the user to resolve the conflict when it blocks an answer; do not merge conflicting claims into a fabricated conclusion.
6. Use source metadata and locally indexed source resources only when they are returned by Foam MCP. Distinguish note claims from source evidence, and never imply that an unavailable source was read.
7. Synthesize only what the retrieved evidence supports. Cite each material point with the note title, status, and workspace-relative path or Foam link when available. Label inference and uncertainty; report relevant search limits.

## Completion checks

- The answer is based on MCP reads from the configured knowledge base, and relevant search coverage or limits are clear.
- Every note used or returned has a status and an identifiable path or Foam link when available.
- Stable notes are ranked before draft and deprecated notes unless the user requests otherwise.
- Relevant links, terminology conflicts, and source limitations are surfaced.
- No MCP write tool or local mutation was used.

Report the answer, evidence, statuses, conflicts, and remaining limitations concisely.
