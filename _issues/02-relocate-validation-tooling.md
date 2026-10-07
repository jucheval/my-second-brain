# 02: Relocate validation tooling without changing its interface

**What to build:** The validator still installs and runs from the repository root after its package, schemas, tests, and project configuration move under `_config`.

**Blocked by:** 01: Align note validation with the new contract

**Status:** ready-for-agent

- [ ] Preserve the `brain-validate` command and repository-root schema resolution, including in temporary-repository tests.
- [ ] Update the pre-commit hook to run the retained validator only.
- [ ] Document the installation workflow for the relocated tooling.
