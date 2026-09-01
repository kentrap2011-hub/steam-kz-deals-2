# Backlog Disposition Validator 01

### Task
`backlog-disposition-validator-01` — implement the smallest durable machine-checkable guard that fails closed when a task disappears from `BACKLOG.md` without an explicit durable disposition in the same operational change.

### Contract
- GitHub remains the control-plane owner; interactive ChatGPT/director runtime does not own backlog validation or task-state persistence.
- Task identity is the exact `###` heading under `## Отложенные задачи`; no backlog-wide ID rewrite was required.
- A deleted heading requires exactly one newly added durable `backlog-disposition` JSON marker in a Markdown state/evidence file from the same git change.
- Accepted dispositions are:
  1. `active`: marker lives in the exact `WORKER_TASK*.md`, which must expose a `Task ID:` and the exact expected `reviews/worker_reports/*.md` path;
  2. `completed`: marker lives in the exact durable evidence file, which must be changed in the same change and contain `### Status` = `complete`;
  3. `cancelled` / `superseded`: marker lives in canonical state/decision evidence (or durable worker report), records a reason, and names the exact deleted task.
- `needs_user_verification` is fail-closed:
  - completion requires `acceptance=user_verified` plus non-empty durable acceptance evidence;
  - implementation-only evidence cannot close it;
  - active transfer requires `verification=pending|preserved` and the destination task file must explicitly retain `needs_user_verification`.
- Ordinary backlog edits with no deleted task require no marker.

### Changes
- Added `scripts/validate_backlog_dispositions.py`.
  - compares base/head `BACKLOG.md` via git;
  - extracts exact deferred-task headings;
  - detects deletions;
  - reads only newly added disposition markers from durable Markdown files outside `BACKLOG.md`;
  - validates exactly one accepted disposition per deletion;
  - exits non-zero on missing, duplicate, malformed, implementation-only, or structurally invalid disposition evidence.
- Added `scripts/test_backlog_disposition_validator.py` with focused regressions for all required pass/fail cases plus duplicate-disposition and accepted-user-verification coverage.
- Added `.github/workflows/validate-backlog-disposition.yml`.
  - event-driven only (`pull_request` and `push` to `main`), not recurring;
  - triggers on `BACKLOG.md` and the canonical task/state/report files that can carry dispositions;
  - runs the regression suite, then validates the exact event base/head diff;
  - `permissions: contents: read`.
- No product feature, production queue, schedule, priority, or backlog content was changed.
- Implementation was isolated in PR #10 and squash-merged as `e41880125d306acb369eacdaa1e79b41942f77a3`.
- First canonical main run `33534091647` correctly exposed an integration false-positive: the validator parsed its own non-durable Python docstring example as a marker. This was fixed by restricting marker discovery to durable Markdown evidence files outside `BACKLOG.md` in commit `112af616153312dbfbfcaf622ddaebb6c1975cd2`.

### Validation
- Local focused regression suite: `python scripts/test_backlog_disposition_validator.py` -> pass.
- Local synthetic git-diff integration:
  - delete -> exact active task/report marker -> pass;
  - delete without marker -> fail with `requires exactly one`.
- Required regression cases covered and passing:
  - pass: delete -> exact active task + expected report;
  - pass: delete -> completed evidence;
  - pass: delete -> explicit user cancellation;
  - fail: delete with no disposition;
  - fail: delete `needs_user_verification` with implementation-only evidence;
  - pass: move pending verification to exact active task preserving verification;
  - pass: unrelated backlog edit with no deletion.
- Extra regressions:
  - duplicate dispositions -> fail;
  - `needs_user_verification` + explicit durable user acceptance -> pass.
- Canonical GitHub Actions validation after the integration fix:
  - workflow run `33534211167` (`Validate backlog dispositions`) -> success;
  - job `99944399384` (`backlog-disposition`) -> success;
  - `Run backlog disposition regressions` -> success;
  - `Validate backlog deletion dispositions` -> success;
  - validated head commit `112af616153312dbfbfcaf622ddaebb6c1975cd2` on `main`.
- The existing production validation workflows were not overloaded: there was no generic project-state CI route suitable for this concern, so the guard uses one small non-recurring state-change workflow instead of a new schedule or production stage.

### Unresolved
No scoped correctness blocker remains. Repository branch-protection policy was not changed; that is separate repository-governance scope. The validator itself is wired to both pull-request changes and direct pushes to `main` and fails deterministically on an invalid deletion.

### Status
complete

### Recommended next step
Director may close this worker slot using this report and the exact refs above. For future backlog deletions, keep the operational change small and place exactly one valid disposition marker in the durable destination/evidence file; no marker is needed for edits that do not delete a backlog task.
