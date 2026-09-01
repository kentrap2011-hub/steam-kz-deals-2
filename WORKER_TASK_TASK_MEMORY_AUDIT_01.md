# WORKER TASK — SECOND NEXT FREE SLOT

Task ID: `task-memory-audit-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/task-memory-audit-01.md`

## Goal

Audit the project's durable task memory to find planned/user-requested tasks that may have disappeared from active/backlog state without proof of completion, cancellation, or explicit transfer.

This task exists because `BACKLOG.md` was created on 2026-08-30 without a full migration of earlier user agreements, and later backlog cleanups removed multiple items at once. The free-game giveaway requirement has already been recovered; the old media/screenshots user-verification tail has also been restored for reconciliation.

This is management-state recon only. Do not implement product features or rewrite production code.

## Read first

- `DIRECTOR_PROTOCOL.md`
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_TASK_BOARD.md`
- `BACKLOG.md`
- `CURRENT_TASK.md`
- `PROJECT_RULES.md`
- `PROJECT_DECISIONS.md`
- `PROJECT_ROUTES.md`
- `reviews/worker_reports/` index/relevant reports only as needed

## Evidence scope

Use Git history selectively, with special attention to:
- creation/history of `BACKLOG.md` from 2026-08-30 onward;
- historical `CURRENT_TASK.md` transitions;
- historical task files / worker reports;
- project rules or decisions that describe a future product requirement but have no current backlog/active/closed evidence;
- backlog items removed in bulk cleanup commits.

Do not read every production artifact or code file. This is a task-lifecycle audit, not a code audit.

## Required classification

Build a compact ledger of every historically identified planned task that is relevant to this audit and classify it into exactly one:

1. `active_or_blocked_durable`
   - currently active, or blocked with explicit durable state and next trigger.

2. `completed_with_evidence`
   - implementation/acceptance/user verification is durably evidenced by report/commit/decision as appropriate.

3. `explicitly_cancelled_or_superseded`
   - user or canonical decision deliberately cancelled/replaced it.

4. `backlog_current`
   - still correctly represented in current `BACKLOG.md`.

5. `orphaned_probable`
   - disappeared without adequate completion/cancellation/transfer evidence and should likely be restored.

6. `ambiguous_user_decision_needed`
   - evidence conflicts or task intent cannot be reconstructed safely.

## Known checkpoints to verify

Do not assume these conclusions; verify them:
- free-game giveaways existed as a product rule before backlog migration and are now restored as cross-platform, not Steam-only;
- compact score UI / misleading wishlist display were later completed and user-verified;
- Chrome shortcut icon had a later positive user verification and should not be restored merely because it vanished from backlog;
- played-game achievement weighting was implemented after being removed from backlog;
- normalized Taste factors were implemented/cut over after being removed from backlog;
- bundles/packages were explicitly moved into active work and later completed;
- old media/screenshots task had `needs_user_verification`, user later reported the expected result still was not visible, and no durable later positive verification has yet been established; current backlog now restores it only as reconciliation, not as a claim that the bug definitely remains.

## Pre-backlog gap check

Because `BACKLOG.md` did not exist before 2026-08-30, compare the durable project rules/decisions/routes and historical task state from before that date against current backlog + active/blocked + completed reports.

Look specifically for **product requirements that imply unfinished implementation work**, not every existing business rule. A rule already fully implemented is not a backlog item.

If a requirement appears only as a rule but implementation status is uncertain, classify it `ambiguous_user_decision_needed` rather than inventing a task.

## Removal integrity audit

For each historical backlog removal, determine its destination:
- exact active task/task-file/report;
- completion evidence;
- explicit cancellation/supersession;
- or no durable destination.

Identify the commits/pattern that caused any orphaning.

## Prevention recommendation

Recommend the smallest durable process fix necessary so future user phrases such as “сделаем потом”, “добавь это позже”, “пока отложим” cannot disappear when chats are deleted or backlog is cleaned.

Do not design a heavy project-management system unless evidence requires it. Prefer simple invariant/check tooling if sufficient.

## Hard boundaries

Do NOT:
- implement orphaned product tasks;
- modify backlog/board/rules in this worker task except writing the report;
- declare a task complete only because code exists if user verification was explicitly part of completion;
- treat Git commit message alone as proof when the task required production/device acceptance;
- crawl production data.

## Done when

- backlog creation/migration gap is explained with exact history refs;
- all historical backlog removals in the relevant period have destinations or are flagged;
- pre-backlog durable requirements have been checked for missing implementation tasks;
- any additional probable orphaned/ambiguous tasks are listed compactly;
- one prevention step is recommended.

## Report format

Save:
`reviews/worker_reports/task-memory-audit-01.md`

### Root cause
Why tasks could disappear.

### Historical task ledger
Compact table: task | historical evidence | current destination/status | classification.

### Orphaned / ambiguous candidates
Only items needing action.

### Confirmed safe removals
Compact list with destination evidence.

### Prevention gap
Exact process weakness.

### Validation
History/files inspected; no product changes.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only.

Final response must include report path and commit ref.