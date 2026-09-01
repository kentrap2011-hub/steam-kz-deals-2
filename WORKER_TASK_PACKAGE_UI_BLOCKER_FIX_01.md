# WORKER TASK — CHAT 1

Task ID: `package-ui-blocker-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/package-ui-blocker-fix-01.md`

## Goal

Fix the pre-existing package/UI regression that currently blocks the canonical pre-AI workflow before the Russian-description translation stages can run.

Known failure:
`AssertionError: missing package UI override contract: window.renderPackageDeal=function(g)`

This is a narrow unblock task. Do not redesign package UI, purchase logic, translation logic, duration logic, ranking, or Taste.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- relevant package/UI regression tests and current web/package rendering code
- `reviews/worker_reports/ru-translation-implement-01.md`
- prior package/UI reports if the route points to them

## Required approach

1. Reproduce/confirm the failing regression from current `main`.
2. Determine whether the contract/test is stale or the UI implementation actually regressed.
3. Fix the owning component, not by weakening/removing the regression check unless repo evidence proves the check itself is obsolete.
4. Preserve all current package economics and compact purchase-option behavior that previously passed phone verification.
5. Keep changes minimal and scoped only to restoring the canonical package/UI contract needed by the workflow.
6. Re-run the relevant package/UI regressions and the canonical pre-AI workflow far enough to prove this blocker is cleared.

## Hard boundaries

Do NOT:
- change Russian translation scope/runtime/cache logic;
- manually translate descriptions;
- change duration/IGDB code;
- change ranking/Taste;
- redesign UI;
- alter package economics semantics;
- suppress or skip unrelated failing tests without proving they are obsolete.

## Done when

- the specific `window.renderPackageDeal=function(g)` blocker is resolved correctly;
- relevant package/UI regressions pass;
- the canonical pre-AI workflow no longer stops at this blocker and reaches the translation-related stages or the next genuine independent blocker;
- no unrelated product behavior changed.

## Report format

Save:
`reviews/worker_reports/package-ui-blocker-fix-01.md`

### Task
What failed and why.

### Verified facts
Whether implementation or test was wrong.

### Changes
Exact files/commits.

### Validation
Relevant tests/workflow run refs.

### Unresolved
`none` or exact next blocker.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
If complete, recommend the bounded Russian translation runtime acceptance next.

Final response must include report path and commit refs.