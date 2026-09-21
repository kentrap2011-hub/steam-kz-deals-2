# WORKER TASK — PROGRESSIVE PERSONALIZED DEALS PASS 1 SCHEDULED WORKER CONFIGURE 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repository target неоднозначен — остановись и сначала переключись на `kentrap2011-hub/steam-kz-deals-2`.

Task ID: `progressive-personalized-deals-pass1-scheduled-worker-configure-01`
Mode: `CONFIGURE / VALIDATE — NO PRODUCTION RUN`
Status: `authorized_ready_for_worker`

## User authorization

Director received explicit user authorization to hand this bounded CONFIGURE task to ЧАТ 1.

Authorization covers:
- creating/configuring exactly one dedicated Progressive PASS 1 Scheduled Task/runtime entrypoint;
- validating its identity, schedule, state and prompt binding;
- writing the durable report.

Authorization does NOT cover:
- pressing `Run now / Выполнить сейчас`;
- processing Tower Dominion or any other PASS 1 item;
- creating a PASS 1 result artifact;
- consuming a PASS 1 attempt;
- retry/backlog drain;
- PASS 2;
- changing unrelated Scheduled Tasks.

## START

First read the latest `CHAT_PROTOCOL.md` from `main` and execute the START gate fully.

Then read this task from `main`.

Then read only the compact canonical prerequisites needed for this configuration:
- `config/progressive_pass1_contract.json`
- `config/progressive_pass1_worker_prompt.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `reviews/worker_reports/progressive-personalized-deals-pass1-scheduled-worker-entrypoint-audit-01.md`
- relevant current `DIRECTOR_TASK_BOARD.md`

Do not reopen unrelated implementation history unless a specific blocker requires it.

## Accepted Director finding

The entrypoint audit is accepted with:
`complete_insufficient_observability`.

The user then supplied owner-scope Scheduled Tasks UI evidence. Director classification is now:

`missing_runtime_entrypoint`

for an active, dedicated Progressive PASS 1 Scheduled Task.

Historical/completed/paused tasks are not candidates merely because they are old semantic/runtime tasks.

Do not repurpose or modify:
- `Taste Steam Review Dossier`;
- historical `Taste Semantic Producer`;
- `Nightly Production Runtime`;
- any other old/completed/paused task.

## Goal

Create and validate exactly one dedicated ChatGPT Scheduled Task for Progressive Personalized Deals PASS 1.

The new task must be only the bounded semantic data plane described by:
- `config/progressive_pass1_contract.json`;
- `config/progressive_pass1_worker_prompt.md`.

GitHub remains the sole control-plane owner for:
- semantic generation;
- scope/order;
- work IDs;
- attempt state;
- retry eligibility;
- validation/persistence;
- completeness;
- counts;
- visual rebuilds.

The Scheduled Task must not become an independent queue owner, retry owner, completeness owner or backlog manager.

## Architecture preflight

Before any scheduler write, verify and record:

1. this task changes only the Scheduled ChatGPT runtime/data-plane entrypoint;
2. no GitHub control-plane responsibility is transferred;
3. no second competing Progressive PASS 1 scheduler already exists in the observable active owner scope;
4. no existing Taste/Dossier task is being repurposed;
5. PASS 2 remains inactive;
6. configuration will not create any retry loop outside GitHub.

If any of these cannot be proven safely, stop before creation and use `needs_user_decision` or `blocked_external`.

## Scheduled Task identity

Create exactly one dedicated task.

Preferred title:
`Progressive PASS 1 Worker`

If the platform requires a minor title variation, document the exact final title.

The task must be distinguishable from Taste/Dossier/history tasks.

## Prompt / binding requirement

The Scheduled Task prompt must be concise and loader-based.

At every invocation it must:
1. target only repository `kentrap2011-hub/steam-kz-deals-2`, branch `main`;
2. first read the latest canonical `config/progressive_pass1_worker_prompt.md` fully;
3. read and obey `config/progressive_pass1_contract.json`;
4. use only current GitHub-owned `data/production/pre_ai/progressive_pass1_work.json`;
5. never choose/rebuild/reorder/expand work;
6. create only exact create-only per-item PASS 1 result artifacts at GitHub-provided paths;
7. never auto-retry PASS 1;
8. never start PASS 2;
9. never require Taste Steam Review Dossier or Russian reviews universally;
10. stop cleanly when no current items remain or when runtime/tool budget no longer safely permits another item.

Do not embed a stale copy of the whole semantic contract if a short loader prompt can read the current canonical repo prompt each invocation.

## Schedule rule

Do not invent a recurrence from conversational history.

Derive the safe schedule from current canonical production timing and current GitHub preparation/runtime dependencies.

Required:
- timezone must remain consistent with canonical production timing (`Europe/Samara`) unless current canonical state explicitly says otherwise;
- the worker must run only after the GitHub-owned current PASS 1 manifest/work input can safely exist for that cycle;
- do not change GitHub workflow timing or any other Scheduled Task merely to fit this worker.

If current canonical evidence does not establish a safe recurring clock time with enough certainty to avoid racing GitHub preparation, STOP BEFORE CREATING THE TASK and return `needs_user_decision` with the smallest concrete schedule decision required.

Do not guess a time.

## Strict no-run boundary

This task is configuration only.

After creating/configuring the Scheduled Task:
- DO NOT press `Run now / Выполнить сейчас`;
- DO NOT wait for or trigger a scheduled production execution;
- DO NOT process Tower Dominion;
- DO NOT create any `PROGRESSIVE-PASS1-RESULT-V1` artifact;
- DO NOT consume any PASS 1 attempt;
- DO NOT run a second item;
- DO NOT start backlog drain;
- DO NOT start PASS 2.

The first semantic invocation remains a separate bounded live-acceptance action after Director acceptance.

## Validation

Before completion verify and record:

1. exactly one dedicated Progressive PASS 1 Scheduled Task now exists;
2. exact task title;
3. exact task ID;
4. enabled/disabled state;
5. exact schedule and timezone;
6. exact effective prompt or concise loader representation;
7. prompt loads the canonical `config/progressive_pass1_worker_prompt.md`;
8. prompt is bound to `kentrap2011-hub/steam-kz-deals-2` / `main`;
9. no existing Taste/Dossier/historical task changed;
10. no production run occurred;
11. no PASS 1 artifact was created;
12. no PASS 1 attempt was consumed;
13. PASS 2 remains inactive.

If scheduler inventory is readable after creation, use it for read-only validation.

## Durable report

Write and commit to `main`:

`reviews/worker_reports/progressive-personalized-deals-pass1-scheduled-worker-configure-01.md`

Report must include:
1. task / repo / mode;
2. architecture preflight;
3. scheduler existence check before creation;
4. exact created Scheduled Task title and ID;
5. enabled state;
6. exact schedule/timezone and why it is safe relative to GitHub preparation;
7. exact prompt/loader binding;
8. validation checklist;
9. confirmation that unrelated Scheduled Tasks were unchanged;
10. confirmation that no `Run now` or production semantic execution occurred;
11. unresolved items;
12. final status;
13. exactly one recommended next step;
14. exact scheduler/GitHub refs available;
15. efficiency/reusable lesson.

Allowed final statuses:
- `complete_scheduler_ready_for_bounded_live_acceptance`
- `needs_user_decision`
- `blocked_external`
- `needs_fix`

## Completion rule

Do not claim completion until:
- the durable report exists at the exact path in `main`;
- the report is reread from `main`;
- scheduler configuration is validated read-only;
- no production execution occurred.

## Exactly one next step after success

Return to Director.

Do not perform the live acceptance yourself in this task.

Director will separately authorize/resume the one-item PASS 1 live acceptance only after accepting this configuration report.
