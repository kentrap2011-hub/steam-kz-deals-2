# WORKER TASK — TASTE ACTIVE PRODUCER RESTORE DESIGN 01

## Task ID
`taste-active-producer-restore-design-01`

## Mode
`READ-ONLY / CONTROL-PLANE + CONTRACT DESIGN`

## Priority
`VERY_HIGH_TASTE_RECOVERY`

## Expected report
`reviews/worker_reports/taste-active-producer-restore-design-01.md`

## Why this task exists
The automatic ChatGPT/Taste producer is currently not running.

Direct user UI evidence establishes:
- the old `Taste Semantic Producer` is `Completed`;
- its Date/Time fields are not editable;
- the ChatGPT Scheduled `Active` filter is empty;
- therefore there is currently no active recurring ChatGPT Scheduled Taste producer.

The old completed producer has durable repository identity:
- old task/jawbone id: `6a9d6fdddc00819193ed670d782045c4`;
- old canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- old producer generation: `1`.

The previous read-only recon could not prove same-id reactivation, and the user UI later showed that the completed task is not editable. We therefore need a bounded design for restoring exactly one ACTIVE producer without accidentally creating two producers, breaking ingest identity, or using a paid API.

## Required reading
Start from GitHub truth and read:
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`
- `reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`
- `reviews/worker_reports/taste-singleton-disabled-state-confirm-01.md`
- `reviews/worker_reports/taste-pre-ai-deal-contract-guard-fix-implement-01.md`
- `reviews/worker_reports/taste-daily-automation-failure-forensic-recon-01.md`
- `config/execution_ownership_contract.json`
- `config/taste_result_contract.json`
- any current Taste producer/ingest/run-key contracts directly needed to design the migration.

Use current official OpenAI documentation for Scheduled Tasks where product behavior matters. Do not rely on old remembered UI behavior.

## Goal
Design the narrowest safe way to restore exactly one active recurring ChatGPT Scheduled Taste producer, beginning with one controlled fresh-game canary and later widening the SAME active producer after acceptance.

This task is DESIGN ONLY. Do not create, edit, enable, disable, delete, or schedule any ChatGPT task yet.

## Questions that must be answered
1. Given the completed non-editable old task, is a replacement active Scheduled Task now the narrowest viable route, or is there any currently proven same-task recovery path?
2. If a replacement is required, what should happen to the old completed task during migration? It must not be deleted merely for tidiness before acceptance/provenance no longer needs it.
3. How must canonical producer identity change in repository contracts when the new Scheduled Task receives a new immutable task/jawbone id?
4. Should producer generation advance from `1` to `2`? Identify every exact contract/state location that must change and every location that must NOT be changed.
5. In what order must control-plane creation and repository contract changes occur so that the new task cannot produce an accidentally accepted result under the wrong identity?
6. How do we guarantee there is never more than one ACTIVE Taste producer?
7. What exact first-run/canary design lets us test one fresh current game without creating a disposable one-time task that immediately becomes non-editable again?
8. Prefer, if product capability safely allows it, one ACTIVE recurring task whose initial prompt is canary-bounded to one exact fresh AppID/run key; subsequent scheduled runs before widening must safely no-op rather than process additional games.
9. How should the first run be timed so there is enough time to persist the new task id/generation contract before the run can occur?
10. After a successful canary, what exact independent System Audit gate is required before changing the SAME active task from canary-bounded behavior to normal daily production behavior?
11. What exact normal daily cadence should the restored producer use? Reconcile it with the current repository contract and the intended 01:00 Europe/Samara Taste cycle.
12. What should happen if task creation succeeds but repository identity migration fails before the first run? Design fail-closed rollback/containment.
13. What should happen if the first canary run fails, never dispatches, or produces a result rejected by ingest?
14. How will the Director/user verify in ChatGPT Scheduled UI that there is exactly one ACTIVE Taste producer and the old completed task is not running?
15. Can the implementation be completed with ChatGPT Scheduled Tasks + GitHub only, with zero separately billed OpenAI API/Copilot/external automation cost?

## Hard constraints
- No paid OpenAI API.
- No Copilot automation dependency.
- No external paid scheduler/service.
- No authenticated Steam Store session.
- Do not create a second active Taste producer during this design task.
- Do not mutate any Scheduled Task in this design task.
- Do not process any game in this design task.
- Do not reuse the old Prototype/App_10150 canary result.
- The next canary must use fresh current prepared data.
- Do not lower fail-closed identity checks merely to accept a replacement task.
- Do not preserve generation `1` if that would make a new immutable task id indistinguishable from the old producer lineage.
- Do not delete the old completed task before the new producer is accepted unless there is a documented unavoidable product constraint and Director explicitly approves it later.
- Do not start the implementation task.

## Required implementation plan output
The report must contain one concrete next IMPLEMENT task design, including:
- exact proposed task filename and report path;
- exact mutation order;
- old vs new task lifecycle;
- new producer-id/generation migration plan;
- exact canary containment strategy;
- exact first-run scheduling strategy;
- exact no-overlap proof;
- exact rollback/containment if any step fails;
- exact acceptance gates before widening;
- user action required, if any, stated in ordinary Russian;
- whether the old completed Scheduled Task should remain preserved after canary and after final acceptance.

If current OpenAI product behavior prevents the proposed safe same-active-task canary→daily transition, say so plainly and give the narrowest safe alternative without silently creating disposable tasks.

## Durability
Create the exact report path early with status `in_progress` and persist to `main` before expensive research.
Checkpoint the same report before long verification.
Before final response, persist the final report and re-read it from `main`.

## Final status — exactly one
- `complete_restore_plan_ready`
- `blocked_product_control_plane`
- `blocked_contract_migration`

Do not implement the plan.
Do not create or mutate a Scheduled Task.
Do not start another task.
