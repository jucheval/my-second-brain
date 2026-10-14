# 05: Provide prompt-driven knowledge retrieval with Foam MCP

**What to build:** A user-invoked skill retrieves relevant knowledge for the current prompt through read-only Foam MCP, without automatic preload or per-session agents.

**Blocked by:** 03: Generate Foam artifacts

**Status:** ready-for-agent

- [x] The generated skill searches based on the current prompt and adds relevant context.
- [x] Document how to place the generated retrieval skill in Copilot's user scope and configure the knowledge-base path.
- [x] Foam MCP access is read-only; the workflow does not enable writes.
