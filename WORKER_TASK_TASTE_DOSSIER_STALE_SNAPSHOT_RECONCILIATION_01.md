# WORKER TASK — TASTE DOSSIER STALE SNAPSHOT RECONCILIATION 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2` for this task;
- do not search, read, modify, or use another repository;
- if GitHub/tool opens another repository by default or the target is ambiguous, stop and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-stale-snapshot-reconciliation-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/taste-dossier-stale-snapshot-reconciliation-01.md`

## Goal

Establish from fresh canonical `main` whether the obsolete failed Dossier group `g000001` from the old snapshot still requires any explicit cleanup/reconciliation/recovery after the accepted binding/snapshot rollover.

This task decides only whether action is required. It must not perform that action.

## Known starting point — verify, do not assume

Latest Director bootstrap/Board says:
- current binding: `github-derived-temporal-classification-2026-09-27`;
- current snapshot: `81e44a924e2df85dcd3acab12954c12a5b2a04ab42f09405460a53d42ea241ea`;
- current sequence 1 was pending, with 140 groups / 418 dossiers remaining and 0 accepted / 0 failed at the last Director check;
- obsolete failed experiment snapshot: `b98f8691529d9c4d1bdf66227f08537fbb5dd385ba8798280da05aa98f4054d5`;
- old candidate commit: `2a3a2e2dbd99faf784f22878f0b7ec2252d1f5fa`;
- old failed ingest run: `36241650284`;
- PR #99 fixed GitHub-derived temporal classification and atomic failed-group staging;
- no old-group recovery/reconciliation has been authorized.

Treat all of the above as hypotheses until checked against current `main`.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully and make a task checklist before investigation.

Read minimally:
1. current `CHAT_CONTEXT.md`;
2. the current top section of `DIRECTOR_TASK_BOARD.md`;
3. `PROJECT_ROUTES.md`, section **Taste Steam review dossier: non-blocking per-group progress and immutable recovery**;
4. `config/taste_steam_review_dossier_contract.json`;
5. current `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`;
6. only the smallest additional current-state/progress/recovery artifacts needed to answer the questions below.

Use bounded retrieval. Do not reconstruct project history or reread unrelated old Board sections.

## Questions that must be proven

### A. Current truth

Verify from fresh `main`:
- current Dossier binding/revision;
- current snapshot id;
- current `next_pending_sequence`;
- accepted / failed / pending counts and remaining required dossier count;
- whether the current worker index or current progress state references the old `b98f... / g000001` at all.

If production advanced since the Director bootstrap, report the new values rather than treating the bootstrap numbers as errors.

### B. Old snapshot isolation

Determine whether artifacts from old snapshot
`b98f8691529d9c4d1bdf66227f08537fbb5dd385ba8798280da05aa98f4054d5`
are:
- automatically isolated/superseded by the new snapshot and irrelevant to current forward progress; or
- still present in a canonical current recovery/reconciliation set that requires an explicit action.

Prove this from the current contract/state. Do not infer it merely because the snapshot id changed.

### C. Required action, if any

Answer exactly one of these:

1. **No explicit reconciliation required** — current canonical state is cleanly on the new snapshot and the old group is historical/stale only. State why normal current-snapshot production can continue safely.

2. **Explicit reconciliation required** — identify the exact canonical state that still requires it, the owning component, and the smallest action class required. Do not execute it.

3. **Cannot determine** — identify the exact missing/conflicting evidence. Do not guess.

Also determine whether any cleanup such as deleting/rewriting the old candidate is required by contract. The accepted Director instruction is **do not manually rewrite or repair the old candidate** unless current canonical truth proves a separate action is required.

## Hard prohibitions

Do not:
- modify source, workflow, runtime, contracts, prompts, production data, cache, progress, audit or quarantine state;
- run or trigger a Scheduled Task;
- create/edit/enable/disable/pause/delete/reschedule/rename any Scheduled Task;
- trigger Dossier production, Tiny Snow, old `g000001`, recovery, Deep recovery, backlog processing or semantic reruns;
- invoke a recovery workflow;
- delete, rewrite, rename or “clean up” old snapshot artifacts;
- treat the Director chat or worker chat as a production worker;
- change `CURRENT_TASK.md`.

The only allowed repository write is the durable report named above.

## Acceptance

The report must make the Director able to decide the next step without reopening large logs.

It must contain:
1. `Task`
2. `Verified facts`
3. `Changes` — report only
4. `Validation`
5. `Unresolved`
6. `Status` — one of `complete`, `blocked`, `needs_fix`, `needs_user_decision`
7. `Recommended next step` — exactly one bounded next step
8. exact file/commit/run refs sufficient to verify the conclusion
9. `Efficiency / reusable lesson` — `none` unless a genuine route/pitfall candidate was found

The report must explicitly state one conclusion:
- `NO_EXPLICIT_RECONCILIATION_REQUIRED`
- `EXPLICIT_RECONCILIATION_REQUIRED`
- `UNDETERMINED`

If `EXPLICIT_RECONCILIATION_REQUIRED`, do not implement it; return it for separate Director/user authorization.

## Expected next step after this task

Director reads only this report and minimal supporting state if needed, then either:
- accepts that normal current-snapshot Dossier production may continue with no old-snapshot action; or
- asks the user for separate authorization for the exact bounded reconciliation action proven necessary.
