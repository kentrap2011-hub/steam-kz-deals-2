# WORKER TASK — CHAT 1

Task ID: `taste-runtime-trigger-status-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/taste-runtime-trigger-status-01.md`

## Context

Direct continuation of completed Trine 4 diagnosis:
`reviews/worker_reports/trine4-missing-diagnosis-01.md`.

Known and already proven:
- Trine 4 is `App_690640`;
- current KZ sale state is valid and captured;
- it disappears only because its required Taste analysis is unresolved;
- `App_690640` is already present in the existing GitHub-prepared Taste work queue;
- do NOT repeat the Trine trace or manually analyze the game.

The user now asks three operational questions:
1. Is the normal automatic Taste processing actually running now, or is the item only waiting in a queue?
2. Can the existing normal processing be safely started manually/early instead of waiting for its schedule?
3. Who/what detects completion for `App_690640` and ensures the downstream list is rebuilt/checked?

## Goal

Answer those three questions from the current canonical execution route, using the smallest possible investigation.

## Required checks

### 1. Existing owner and schedule

Identify the exact existing scheduled Taste processing mechanism that consumes:
`data/production/pre_ai/chatgpt_taste_queue.jsonl`.

Record:
- exact owner/mechanism;
- schedule/cadence if defined;
- last relevant execution/result if canonical evidence exists;
- whether a relevant execution is currently active at report time.

Do not infer `running` merely because a queue row exists.

### 2. Manual/early start

Determine whether the SAME existing processing mechanism has a supported manual/early trigger.

Classify exactly one:
- `manual_trigger_available`
- `scheduled_only`
- `manual_trigger_exists_but_unsafe_or_not_authorized`
- `cannot_determine_from_current_canonical_route`

If a normal manual trigger exists, document the exact existing trigger route and whether using it would process the canonical queue normally.

Do NOT create or run a second scheduler/worker/queue.
Do NOT manually produce a Taste answer for Trine 4.

This task is read-only: do not invoke the manual trigger yet. The Director/user will decide after seeing the report.

### 3. Completion detection for Trine 4

For `App_690640`, identify the exact durable signals proving:
- its analysis result was produced;
- result was ingested/validated;
- downstream rebuild occurred;
- Trine 4 either appeared in the final list or was legitimately rejected for a recorded reason.

Determine whether the current system already has a specific notification/watch for completion of this one game.

Do not confuse generic queue persistence with a user-facing notification.

### 4. Recommended action now

Recommend exactly one of:
- `trigger_existing_processing_now`
- `wait_until_exact_next_scheduled_run`
- `fix_missing_or_broken_processing_trigger`
- `add_completion_watch_only`

If recommending a wait, give the exact next expected scheduled opportunity when determinable.
If recommending a manual trigger, prove it is the normal existing path and not a bypass.

## Hard boundaries

Do NOT:
- repeat Trine 4 commercial/price/ranking diagnosis;
- manually judge whether Trine 4 fits the user;
- manually insert Trine 4;
- create a new queue, scheduler, polling worker, or semantic runtime;
- modify production in this RECON;
- perform broad repository/history archaeology.

## Report format

Save:
`reviews/worker_reports/taste-runtime-trigger-status-01.md`

### Current processing state
Is it queued only, currently running, or already completed? Exact evidence.

### Schedule
Existing normal cadence/owner.

### Manual start
Classification + exact supported route if any.

### Completion detection
Exact signals for `App_690640`; whether specific monitoring already exists.

### Recommended action now
One action only.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Final response must include report path and exact refs.