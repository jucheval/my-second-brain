# My second brain

A private, portable knowledge base built from Markdown and Git. Notes can be written and read by humans or AI, while Markdown remains the source of truth. It is based on the [Foam](https://foambubble.github.io/foam/) personal knowledge management system and the [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format/tree/main) specification. In particular, notes contain metadata as a YAML front matter (metadata contracts are in `_config/schema/` and are used to validate the structure of the notes). Four [Foam templates](https://docs.foam.md/features/templates/) are provided to create new notes (see [[template|this note]]).

## Getting started

The starting procedure follows the [Foam starting procedure](https://github.com/foambubble/foam-template/). Here it is:

> This documentation assumes that you have a GitHub account and have [Visual Studio Code](https://code.visualstudio.com/) installed on your Linux/macOS/Windows machine.
>
> 1. If you haven't yet, browse over to the main [Foam documentation](https://foambubble.github.io/foam) to get an idea of what Foam is and how to use it.
> 2. Press "Use this template" button above or [second-brain-template](https://github.com/foambubble/foam-template/generate) to fork it to your own GitHub account. If you want to keep your thoughts to yourself, remember to set the repository private.
> 3. Clone the repository to your local machine [from GitHub](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) or directly [from VS Code](https://code.visualstudio.com/docs/sourcecontrol/github#_cloning-a-repository) and open it in VS Code.
>
> 4. When prompted to install recommended extensions, click **Install all** (or **Show Recommendations** if you want to review and install them one by one). The recommendations include Foam and Run On Save.

After setting up the repository, read the rest of this file.

## Repository layout

This repository contains example notes as well as the reusable architecture.

1. Have a look at the example files in `inbox/`, `journal/`, `knowledge/`, and `projects/` before removing them.
2. Adapt the types and tags vocabulary in [`_config/schema/vocabulary.json`](_config/schema/vocabulary.json) to your needs. Their respective definitions start at lines 14 (types) and 46 (tags).

### `./`

The root folder contains the [`CONTEXT.md` (repository vocabulary)](CONTEXT.md) and [`AGENTS.md` (agent routing and boundaries)](AGENTS.md).
Folders may contain an `index.md`. Folder terminology belongs in a nearby `CONTEXT.md` when needed. The maximum depth below `knowledge/` and `projects/` is two folder levels.
The organization workflow expects an `index.md` in each canonical knowledge or project folder. Index files are optional to automated validation, which does not check their presence or contents.

### `journal/`

Dated journal notes organized in a flat way (no sub-folders). Journal notes are chronological by nature rather than reusable reference knowledge.

### `inbox/`

The entry point for draft notes (i.e. new non-journal notes). Drafts may be incomplete, ambiguous, or contain unresolved links. Once complete, a draft should be moved to `knowledge/` or `projects/` and in fine be reviewed by a human. After review, the note's metadata should be updated:

- create or append the `verified` field: start writing "verified" to use the dedicated VS Code snippet;
- promote `status` to `stable`.

### `knowledge/`

Reusable concepts, methods, explanations, and reference material that can inform more than one project. They should rely on sources referenced in the note's metadata (via url or local paths). The maximum depth below `knowledge/` is two folder levels. Each folder may contain:

- `index.md` that lists the notes in that folder and/or its subfolders,
- `CONTEXT.md` that defines the vocabulary used in that folder.

### `projects/`

Work organized around objectives and deliverables. Project notes describe the goal, work, and outcomes of each project. The maximum depth below `projects/` is two folder levels. Each project folder's `index.md` lists notes in that folder and/or its subfolders. A folder may also contain a `CONTEXT.md` that defines the vocabulary used there.

### `assets/`

Local sources referenced by notes. They include papers, books, webpages, images, etc.

## Workflow

The workflow may be AI-assisted thanks to 3 agent skills. Here is the intended 4-step workflow:

1. **Capture**. Create a draft in `inbox/` from an idea or supplied material -> [`/brain-capture` agent skill](./.agents/skills/brain-capture/SKILL.md)
2. **Organize**. Move drafts into `knowledge/` or `projects/` -> [`/brain-organize` agent skill](./.agents/skills/brain-organize/SKILL.md).
3. **Review**. Mandatory human review of the proposal (promotion to `stable` or `deprecated`).
4. **Retrieve**. Search notes and sources -> [`/brain-retrieve` agent skill](./.agents/skills/brain-retrieve/SKILL.md). The skill preserves provenance, terminology conflicts, and uncertainty.

AI may create drafts and proposals. Humans approve stable knowledge and add verification. Local source files are disposable caches; they are not the canonical knowledge.

## Setup

### Prerequisites

Clone the repository, then create a virtual environment and install the validator.

Windows PowerShell:

```powershell
py -3.11 -m venv _config/.venv
_config/.venv\Scripts\python.exe -m pip install -e .\_config
_config\.venv\Scripts\brain-generate-foam.exe
```

macOS or Linux:

```bash
python3.11 -m venv _config/.venv
_config/.venv/bin/python -m pip install -e ./_config
_config/.venv/bin/brain-generate-foam
```

The generation command can be rerun after editing `_config/schema/vocabulary.json`, `_config/foam-templates/`, or `_config/agents-skills/`. Saving the vocabulary file runs it automatically when the Run On Save extension detects a change. Run the command manually after setup or whenever a save does not trigger generation:

```text
brain-generate-foam
```

It writes the Foam templates, agent skills, and vocabulary snippet used by VS Code. Generated files are ignored by Git. The generator sources under `_config/` are excluded from Foam's note graph; generated templates remain in `.foam/templates/`.

### Prompt-driven retrieval

The generated `brain-retrieve` skill searches the current prompt against a Foam MCP server. It is manual-only and uses read tools; Foam MCP is read-only unless `--allow-writes` is explicitly added.

Install the Foam CLI:

```bash
npm install --global foam-cli
```

Add a Foam server to the Copilot user MCP configuration at `~/.copilot/mcp-config.json` (or open it with **MCP: Open User Configuration**). Replace the workspace path with the absolute path to this clone:

```json
{
  "mcpServers": {
    "foam": {
      "command": "foam",
      "args": ["mcp", "--workspace", "/absolute/path/to/my-second-brain"]
    }
  }
}
```

Do not add `--allow-writes`. Generate the skill, then copy it into Copilot's personal skill directory.

In VS Code, run **MCP: List Servers**, start `foam`, and review the server configuration before trusting it.

macOS or Linux:

```bash
mkdir -p ~/.agents/skills/brain-retrieve
cp .agents/skills/brain-retrieve/SKILL.md ~/.agents/skills/brain-retrieve/SKILL.md
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills\brain-retrieve" | Out-Null
Copy-Item .agents\skills\brain-retrieve\SKILL.md "$HOME\.agents\skills\brain-retrieve\SKILL.md" -Force
```

Invoke `/brain-retrieve` in Copilot Chat. See [VS Code Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills) and [Foam MCP](https://foambubble.github.io/foam/user/tools/cli/mcp) for details.

Enable the repository pre-commit hook:

```text
git config core.hooksPath .githooks
```

## Validation

Install the validator into your active virtual environment from the repository root with `python -m pip install -e ./_config`.

Windows PowerShell:

```powershell
_config\.venv\Scripts\brain-validate.exe .
_config\.venv\Scripts\python.exe -m unittest discover -s _config\tests
```

macOS or Linux:

```bash
_config/.venv/bin/brain-validate .
_config/.venv/bin/python -m unittest discover -s _config/tests
```

The validator may be run after changing note metadata, schemas, or repository structure. It does not require `index.md` files or validate their contents, and it does not check Foam wikilinks. Review links interactively in Foam; link checking is not part of automated validation. The pre-commit hook runs the validator automatically once enabled.

[template|this note]: knowledge/foam/template.md "Foam templates"
