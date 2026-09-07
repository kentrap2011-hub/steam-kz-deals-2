# WORKER TASK — Taste Singleton Disabled State Confirm 01

## Task ID
`taste-singleton-disabled-state-confirm-01`

## Mode
`READ-ONLY / CONTROL-PLANE CONFIRMATION`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/taste-singleton-disabled-state-confirm-01.md`

## Goal in plain terms
Confirm one fact only: whether the existing replacement ChatGPT automation for Taste is currently disabled, so that a future one-game test cannot accidentally overlap with another run.

## Exact task identity
- title: `Taste Semantic Producer`
- task instance id: `6a9d6fdddc00819193ed670d782045c4`
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`
- producer generation: `1`

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `reviews/worker_reports/taste-pre-ai-deal-contract-guard-fix-implement-01.md`
- `reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`

## Required work
Use the authoritative Scheduled Tasks control surface available to the worker and inspect only the exact existing task above.

Prove one of:
- the exact task exists and is disabled;
- the exact task exists and is enabled;
- authoritative state cannot be read.

If enabled, DO NOT change it in this read-only task. Report that fact and stop.

## Boundaries
- Do not enable, disable, update, clone, recreate, or delete the task.
- Do not create a second task.
- Do not process any Taste row.
- Do not run a one-game test.
- Do not touch GitHub production data except the required report.
- Do not use paid API/Copilot.

## Durability
Create the exact report path first with `in_progress`, then perform the state read, then finalize the same report.

## Required report
State:
- exact task id checked;
- authoritative enabled/disabled value if exposed;
- whether it is safe for Director to prepare exactly one future one-game test using this same task;
- no state-changing action was performed.

Final status exactly one of:
- `complete_confirmed_disabled`
- `complete_found_enabled`
- `blocked_state_unavailable`

Do not start the next task.