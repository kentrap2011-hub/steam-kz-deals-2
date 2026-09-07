# WORKER TASK — Taste Completed Singleton Reuse Recon 01

## Task ID
`taste-completed-singleton-reuse-recon-01`

## Mode
`READ-ONLY / CONTROL-PLANE RECON`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`

## Goal in plain terms
Determine whether the exact existing completed ChatGPT Scheduled Task used as the replacement Taste semantic producer can be safely reused/reactivated for exactly one future one-game canary **without creating a new task identity**.

Do not run the canary and do not change task state in this recon.

## Exact singleton identity
- title: `Taste Semantic Producer`
- task instance id / jawbone id: `6a9d6fdddc00819193ed670d782045c4`
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`
- producer generation: `1`

## Accepted current control-plane observation
On 2026-09-07 the user directly inspected the task in ChatGPT Scheduled on Android:
- title displayed: `Taste Semantic Producer`;
- state displayed: `Завершено` / `Completed`;
- task menu exposed only notification settings and delete;
- no pause/resume/edit action was visible;
- user has NOT deleted the task.

Treat this as user-supplied current UI evidence. Do not ask the user to repeat it and do not infer that the immutable id was displayed in the UI.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `reviews/worker_reports/taste-pre-ai-deal-contract-guard-fix-implement-01.md`
- `reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`
- `reviews/worker_reports/taste-singleton-disabled-state-confirm-01.md`
- current task/control-plane contracts only as needed.

## Questions to answer
1. Is the exact completed task id `6a9d6fdddc00819193ed670d782045c4` still addressable by the available Scheduled Task control plane?
2. Is there a supported way to reactivate/reuse/update this **same task id** for one future run, rather than creating another task?
3. If yes, what is the minimal exact state change needed later for a one-game canary while preserving the same task id and producer generation?
4. Can that future state change be made in a way that prevents recurrence/overlap after the one canary (for example one-time exact schedule or immediate disable after run), without creating another task?
5. If the same completed id cannot be reused or support cannot be proven, what is the narrowest safe conclusion? Do not propose silently creating a second task.

## Evidence standard
Prefer authoritative current control-plane/tool evidence and official OpenAI Scheduled Tasks documentation. Distinguish clearly between:
- what is proven for this exact task id;
- what generic product documentation says;
- what remains unknown.

Do not infer reusability merely from the task title or from the fact that an update API exists unless the exact existing completed task can be safely addressed by that path.

## Hard boundaries
Do NOT:
- enable, disable, update, reschedule, clone, recreate, or delete the task;
- create a second Scheduled Task;
- run a one-game canary;
- process any Taste row;
- reuse the old Prototype `App_10150` result;
- touch Taste queues/receipts/production data except the required report;
- use paid OpenAI API or Copilot;
- change producer generation;
- work on unrelated backlog.

## Durability
Create the exact report path before expensive investigation with status `in_progress`, checkpoint it before any long external/control-plane research, and finalize only after re-reading it from `main`.

## Required report
Save exactly:
`reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`

Include:
- exact task id checked;
- current exact task addressability evidence;
- whether same-id reuse/reactivation is proven supported;
- minimal later mutation required if proven;
- how one-run/no-overlap safety would be preserved;
- explicit statement that no task mutation and no canary occurred;
- recommended next step.

## Final status — exactly one
- `complete_same_id_reuse_supported`
- `blocked_same_id_reuse_unproven`
- `blocked_task_not_addressable`

Do not start or execute the canary in this task.
