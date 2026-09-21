# WORKER TASK — PROGRESSIVE PASS 1 SCHEDULED WORKER DEDUP FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Do not search, read, modify, or use any other repository for this task.
If GitHub/tool opens another repository by default or the repository target is ambiguous, stop and first switch to `kentrap2011-hub/steam-kz-deals-2`.

Task ID: `progressive-personalized-deals-pass1-scheduled-worker-dedup-fix-01`
Mode: `IMPLEMENT / RUNTIME FIX — NO PRODUCTION RUN`
Worker slot: `СУЩЕСТВУЮЩИЙ ЧАТ — ЧАТ 1`

## Trigger

User-side Active Scheduled Tasks UI currently shows THREE active tasks with the title:
`Progressive PASS 1 Worker`

The accepted CONFIGURE report claimed exactly one active task:
`reviews/worker_reports/progressive-personalized-deals-pass1-scheduled-worker-configure-01.md`

Therefore the CONFIGURE result is not accepted as final until runtime deduplication is verified.

## Goal

Identify the three active `Progressive PASS 1 Worker` Scheduled Tasks, determine which single one matches the accepted configuration, keep exactly that one active, and remove or disable only the two duplicate Progressive PASS 1 tasks.

The intended surviving configuration is:
- title: `Progressive PASS 1 Worker`
- daily at `02:00 Europe/Samara`
- loader-bound to current `config/progressive_pass1_worker_prompt.md`
- obeys `config/progressive_pass1_contract.json`
- repo/branch: `kentrap2011-hub/steam-kz-deals-2` / `main`
- enabled
- no `Run now`

The prior report recorded intended task ID:
`6ab14c73f59c8191850959f97197e541`

Do not assume that ID is correct merely because the report says so. Verify all three task IDs and their effective configuration first.

## Required start

1. Read latest `CHAT_PROTOCOL.md` from `main` and complete START gate.
2. Read this task fully.
3. Read only:
   - `reviews/worker_reports/progressive-personalized-deals-pass1-scheduled-worker-configure-01.md`
   - `config/progressive_pass1_worker_prompt.md`
   - `config/progressive_pass1_contract.json`
   - relevant current section of `DIRECTOR_TASK_BOARD.md`

Do not reopen unrelated historical Taste/Nightly task history.

## Fix procedure

1. Inspect the three active `Progressive PASS 1 Worker` tasks read-only first.
2. Record for each:
   - task ID;
   - enabled state;
   - schedule/timezone;
   - effective prompt/loader binding.
3. Select exactly one survivor matching the intended canonical configuration.
4. Disable/delete only the duplicate Progressive PASS 1 tasks.
5. Re-read the Scheduled Tasks inventory and prove that exactly ONE active `Progressive PASS 1 Worker` remains.
6. Do not run it.

If the three tasks are not distinguishable safely, stop with `needs_user_decision` rather than deleting blindly.

## Explicit prohibitions

Do NOT:
- use `Run now`;
- execute PASS 1;
- process Tower Dominion or any game;
- create PASS 1 result artifacts;
- consume PASS 1 attempts;
- start PASS 2;
- modify `Taste Steam Review Dossier`;
- modify historical Taste/Nightly tasks;
- change GitHub business logic or PASS 1 contracts;
- touch another repository.

## Durable reports

Create and commit:
`reviews/worker_reports/progressive-personalized-deals-pass1-scheduled-worker-dedup-fix-01.md`

Also correct the previous configure report if needed so it no longer falsely claims a single-task runtime state that was not true at the time of user verification:
`reviews/worker_reports/progressive-personalized-deals-pass1-scheduled-worker-configure-01.md`

The new FIX report must include:
1. three observed task IDs/configs;
2. survivor task ID and reason;
3. duplicate task IDs and exact action taken;
4. final active inventory proof: exactly one Progressive PASS 1 Worker;
5. confirmation of no production run;
6. status;
7. exact refs.

Allowed statuses:
- `complete_deduplicated_not_run`
- `needs_user_decision`
- `blocked_external`
- `needs_fix`

Before final response, commit and reread the exact FIX report from `main`.

## Completion boundary

Success means:
- exactly one active correctly configured `Progressive PASS 1 Worker` remains;
- no PASS 1 production execution occurred;
- duplicate cause/state is documented;
- durable FIX report is committed and reread.

Then stop and return to Director.
