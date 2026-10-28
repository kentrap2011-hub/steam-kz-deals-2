# ЧАТ 3 — typed REGISTER pre-write implementation

**Task:** director-typed-registration-prewrite-implement-01
**Verdict:** IMPLEMENTED_PENDING_EXACT_HEAD_CI (to be updated after PR checks).
**Scope:** one implementation PR; no active registry/Board/task-state or production writes.

## Implementation

- `scripts/director_registration_prewrite.js`: pure `prepare` plus GitHub connector `publish`, validation of all newly/touched public fields, exact enums, times, task bindings, dependencies, authorized slots and explicit old-ID transitions; error aggregation before first write; single Git tree commit, exact base race check.
- Real connector interface is explicit `functions.exec` dynamic evaluation of pinned source; **not** a supported import. It was checked that `Function()` and the Git data tools are available, but full first live REGISTER cannot be executed without an authorized new task registration. The branch commit for this implementation exercises Git tree.
- `scripts/test_director_registration_prewrite.js`: #317 and #338 failures before any GitHub writes, two valid tasks/two completions, unrelated immutability, exact base race, URLs, secrets, IDs, timestamps, bad slots and dependencies.
- Existing `validate-site-tasks-page.yml` extended by two Node commands; no new workflow or scheduled tasks. `DIRECTOR_PROTOCOL.md` replaces free-form multi-file REGISTER rule with this boundary.

## Remaining director gate

- Existing site tasks/backlog required CI at exact PR HEAD, Director review and merge decision; **not merged**.
- Explicit user authorization and physical chat availability are external facts; the gate checks only that they are represented in an allowlist.
