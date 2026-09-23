# Agent Guide

## Repository Role

This repository is a Markdown-and-Git knowledge base. Markdown is the source of truth. It is designed to be read and maintained by both humans and AI agents.
Use [CONTEXT.md](CONTEXT.md) for domain vocabulary.

## Route Requests

- Raw idea or supplied material: read `brain-capture`.
- Move or classify existing notes: read `brain-organize`.
- Search, compare, or synthesize knowledge: read `brain-retrieve`.
- Validation or repository maintenance: use `brain-validate .` and preserve unrelated changes.

## Before Acting

1. Read [CONTEXT.md](CONTEXT.md) when terminology matters.
2. Read the relevant folder `index.md` and `CONTEXT.md`.
3. Use the JSON schemas as metadata authority; never invent types or tags.
4. Ask when scope, terminology, target location, or status is ambiguous.

## Global Boundaries

- AI may create drafts and proposals.
- Only a human promotes notes to stable or deprecated status.
- Only a human adds verification.
- Do not silently resolve terminology conflicts or contradictory notes.
- Do not claim to have read unavailable sources.

## Repository Map

- `inbox/`: captured drafts
- `journal/`: dated records
- `knowledge/`: reusable knowledge
- `projects/`: goal-oriented work
- `schema/`: machine-readable contracts
- `.agents/skills/`: task-specific workflows

## Completion

Run `brain-validate .` after content or metadata changes. Write a concise report.
