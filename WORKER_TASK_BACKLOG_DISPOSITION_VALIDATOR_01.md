# WORKER TASK — CHAT 2

Task ID: `backlog-disposition-validator-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/backlog-disposition-validator-01.md`

## Goal

Implement the smallest durable guard that prevents a task from disappearing from `BACKLOG.md` without an explicit durable disposition.

This is the direct follow-up to `task-memory-audit-01`. Do not repeat the historical audit.

## Read first

- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `BACKLOG.md`
- `DIRECTOR_TASK_BOARD.md`
- `reviews/worker_reports/task-memory-audit-01.md`
- existing repository validation/test conventions relevant to lightweight project-state checks

## Required behavior

Add one small validator/check that fails closed when a backlog task is deleted without exactly one valid durable disposition in the same operational change.

Accepted dispositions:
1. transferred to an exact active task/task-file with expected report path;
2. completed with durable completion/acceptance evidence;
3. explicitly cancelled/superseded by user/canonical decision.

Special rule:
- a `needs_user_verification` task may not be treated as complete merely because code exists;
- if user/device acceptance was part of Definition of Done, deletion must require that acceptance evidence or an exact transfer preserving the pending verification.

## Design constraints

- Keep this lightweight. Do not build a project-management system.
- Prefer a stable task key/heading plus deletion -> disposition validation.
- Reuse existing validation/CI route if appropriate rather than adding a separate recurring workflow.
- Do not make ChatGPT or the director the runtime owner of this check.
- Do not rewrite current backlog content merely to make the validator easier, except for the smallest normalization genuinely required for stable identification.
- Do not retroactively reclassify old completed tasks.

## Validation

Cover at least:
- delete -> active task + expected report: pass;
- delete -> completed evidence: pass;
- delete -> explicit cancellation/supersession: pass;
- delete with no disposition: fail;
- delete `needs_user_verification` with only implementation evidence: fail;
- move a pending verification to an exact active task preserving verification: pass;
- unrelated backlog edit with no task deletion: pass.

Run the smallest relevant test/validation suite and prove the check is wired into the canonical project validation path used for these state changes.

## Hard boundaries

Do NOT:
- repeat task-history archaeology;
- implement product features;
- perform a broad backlog cleanup;
- change task priorities;
- create a new recurring schedule;
- require heavyweight metadata for every task if a simple stable key/heading is sufficient.

## Done when

- a task cannot disappear from backlog without a machine-checkable durable disposition;
- `needs_user_verification` deletion is fail-closed;
- normal backlog edits remain simple;
- tests pass and the check is integrated into the existing validation path.

## Report format

Save:
`reviews/worker_reports/backlog-disposition-validator-01.md`

### Task
What guard was added.

### Contract
Accepted dispositions and verification rule.

### Changes
Exact files/commits.

### Validation
Positive/negative test results and CI/validation route.

### Unresolved
Only real remaining process gaps.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only.

Final response must include report path and exact commit refs.