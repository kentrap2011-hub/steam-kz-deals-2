# WORKER TASK — Deep invalid-not-fit current-state regression fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Task ID: `deep-invalid-not-fit-current-state-regression-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/deep-invalid-not-fit-current-state-regression-fix-01.md`

## Dependency context

PR #132 `Validate linked Deep card reasons by provenance` is open and blocked only because mandatory Progressive PASS 2 core is red on an unrelated stale regression.

Do NOT modify PR #132 implementation.

## Mandatory START gate

1. Read current `CHAT_PROTOCOL.md` from `main` fully and execute START gate.
2. Read current `DIRECTOR_TASK_BOARD.md` current-state section.
3. Read:
   - `WORKER_TASK_DEEP_INVALID_NOT_FIT_CONTRACT_LOOP_FIX_01.md`
   - `reviews/worker_reports/deep-invalid-not-fit-contract-loop-fix-01.md`
   - `reviews/worker_reports/card-explanation-producer-validator-publication-parity-fix-01.md`
4. Refresh current `main` before writes.

## Confirmed defect

Current mandatory PASS 2 core fails in:

`scripts/test_deep_invalid_not_fit_contract_loop.py`

because the regression pins historical production entries to remain permanently:

`outcome == analysis_incomplete`

That was true immediately after the invalid-not-fit loop reconciliation, but current production state has legitimately advanced through authorized recovery / later Deep processing.

The regression is therefore asserting mutable current state as if it were immutable history.

This blocks unrelated PR #132 even though its task-specific Deep explainability regression is green.

## Required fix

Change the regression so it validates the invariant that matters, not one historical transient outcome.

The test must continue proving:

- the three pinned historical invalid semantic executions were accounted as consumed attempts;
- they did not re-enter ordinary normal-first-pass work as the same exact identity;
- recovery requires GitHub-owned authorization;
- no mechanical `medium -> high` promotion exists;
- malformed/stale/unbound transport still does not falsely consume an attempt;
- exact-bound semantic-contract-invalid execution cannot create an infinite normal retry loop;
- later legitimate recovery/completion is allowed and must not make the historical regression fail.

Use durable historical receipts / attempt provenance / work-mode transitions where appropriate.

Do NOT weaken the actual invalid-not-fit contract.

## Regression expectations

At minimum:

1. Historical pinned evidence remains provable.
2. Current outcome may legitimately be `analysis_incomplete` or later authoritative completion.
3. Same exact work identity must not be reclassified as fresh normal first pass after a consumed semantic-contract failure.
4. Recovery path must remain explicitly authorized.
5. PASS 2 invalid-not-fit loop regression becomes stable under production-state advancement.
6. Existing invalid transport regression remains green.
7. Existing Deep score-evidence explainability regression remains green.
8. Existing frozen-start / async traversal regressions remain green.
9. Backlog dispositions remains green.
10. No production semantic execution.
11. No Dossier/Deep result edits.
12. No Scheduled Task changes.
13. No scheduler/queue/retry owner changes.
14. No RANK-013 changes.

## Coordination with PR #132

This is a separate implementation task.

After this fix is merged to `main`:
- do not edit PR #132 implementation logic;
- PR #132 should refresh/rebase from new `main` and rerun mandatory validation;
- final merge/publication acceptance remains owned by ЧАТ 1 / PR #132 task.

## Delivery

Use a dedicated branch and PR.

Write:
`reviews/worker_reports/deep-invalid-not-fit-current-state-regression-fix-01.md`

Allowed statuses:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `needs_user_decision`
- `blocked`

Do not start another task after this one.
