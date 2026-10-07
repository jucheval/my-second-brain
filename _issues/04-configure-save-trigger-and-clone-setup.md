# 04: Add save-triggered generation and clone setup

**What to build:** After setup, saving the vocabulary regenerates the artifacts, and a fresh clone has a documented path to get started.

**Blocked by:** 02: Relocate validation tooling; 03: Generate Foam artifacts

**Status:** ready-for-agent

- [x] Configure the save-trigger extension to run generation when the vocabulary is saved.
- [x] Retain a documented manual fallback if saving an unchanged file does not trigger generation.
- [x] Exclude generator sources from Foam without hiding generated templates.
- [x] Document installation, generation, validation, optional indexes, and interactive-only link checking.
