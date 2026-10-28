# ЧАТ 3 — typed REGISTER pre-write implementation

**Task:** director-typed-registration-prewrite-implement-01
**Verdict: READY_FOR_DIRECTOR_REVIEW** (after final exact-HEAD CI confirmation; no merge by worker).
**Scope:** one implementation PR; no active registry/Board/task-state or production writes.

## Implementation

- `scripts/director_registration_prewrite.js`: pure `prepare` plus GitHub connector `publish`, validation of all newly/touched public fields, exact enums, times, task bindings, dependencies, authorized slots and explicit old-ID transitions; error aggregation before first write; single Git tree commit, exact base race check.
- Real connector interface is explicit `functions.exec` dynamic evaluation of pinned source; **not** a supported import. It was checked that `Function()` and the Git data tools are available, but full first live REGISTER cannot be executed without an authorized new task registration. The branch commit for this implementation exercises Git tree.
- `scripts/test_director_registration_prewrite.js`: #317 and #338 failures before any GitHub writes, two valid tasks/two completions, unrelated immutability, exact base race, URLs, secrets, IDs, timestamps, bad slots and dependencies.
- Existing `validate-site-tasks-page.yml` extended by two Node commands; no new workflow or scheduled tasks. `DIRECTOR_PROTOCOL.md` replaces free-form multi-file REGISTER rule with this boundary.

## Remaining director gate

- Existing site tasks/backlog required CI at exact PR HEAD, Director review and merge decision; **not merged**.
- Explicit user authorization and physical chat availability are external facts; the gate checks only that they are represented in an allowlist.

## Verified evidence (2026-10-28)

- Draft implementation [PR #345](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/345), branch `implement/director-typed-registration-prewrite-01`, based on `fcbbec1eacdc81cca88193283e97d49e294d1091` main.
- Initial code/test commit `a81acc9a1b2b01a8f68b454084758b7e60a614c1`: site-task CI [40748711959](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40748711959) **SUCCESS** (including new Node fixtures); backlog CI [40748711936](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40748711936) **SUCCESS**.
- In an actual `functions.exec` session, `Function('module',source+';return module.exports;')` evaluated the verified GitHub branch blob `92454c33327d3a6dd6c7099ae83d3627f90fb258`; `publish(tools, request, {dryRun:true})` fetched canonical `main` plan/Board/commit and returned `ok:true, writeCalls:0`, listing exactly Board, registry and one synthetic task file. No test registration branch/task was written.
- The implementation PR itself used the actual GitHub `create_tree(base_tree_sha,tree_elements=[{path,mode,type,content}]) → create_commit(parent_sha) → create_branch(sha)` sequence successfully, proving the typed Git tree interface exists. No import from the repository file was assumed.
- The report-only finalization commit changes no executable inputs, but final PR HEAD and both required CI must still be checked before Director review.

## Invocation contract

Provide one `request` object with `baseSha` (exact current main SHA), a fresh `register/...` branch, 1–10 `registrations` (`{item,content}`), `authorizedSlots`, `transitions`, `authorizedTransitionIds`, `curatedOn` and `boardSection`. Load the source from the **same pinned main SHA** with GitHub `fetch_file`, explicitly evaluate the reviewed text in `functions.exec` as described in `DIRECTOR_PROTOCOL.md`, then call `await gate.publish(tools,request)`. Only after `ok:true`, use the connector's `create_pull_request` once for that branch, await existing CI, and merge only after Director authorization. The implementation does not automatically create a PR, because PR creation/merge are separate Director authorization steps. If the GitHub API changes, fail as `BLOCKED_TOOLING`; never fallback to sequential unvalidated file writes.

