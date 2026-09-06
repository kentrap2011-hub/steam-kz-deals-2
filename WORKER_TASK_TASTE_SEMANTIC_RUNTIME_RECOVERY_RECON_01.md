# WORKER TASK — Taste Semantic Runtime Recovery Recon 01

## Task ID
`taste-semantic-runtime-recovery-recon-01`

## Mode
`READ-ONLY / RECON`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/taste-semantic-runtime-recovery-recon-01.md`

## Why this task exists
The accepted Taste Steps 1–3 implementation is still not user-verifiable because the canonical semantic producer is not advancing the current V5 scope. The immediately preceding acceptance report ended `blocked_semantic_runtime` with `701` unresolved semantic rows and `0` resolved rows.

This task stays strictly on the Taste production-unblock path. Do not switch to giveaway/ITAD or unrelated backlog work.

## Required sources
Read at minimum:
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `USER_TASTE_PROFILE.md`
- `reviews/worker_reports/taste-steps-1-3-production-materialization-acceptance-01.md`
- `reviews/worker_reports/semantic-runtime-task-health-recon-01.md`
- `config/execution_ownership_contract.json`
- current semantic queue/result/cache/runtime contracts and workflows on `main`
- current orchestration/provider pilot task/report state only where it materially affects a safe recovery option.

## Objective
Determine the smallest honest way to restore a canonical semantic producer for the current V5 queue so Taste can proceed to materialization, without creating a duplicate scheduler or weakening fail-closed ownership/completeness rules.

## Required investigation

### 1. Recover the intended existing runtime identity
From repository history/contracts/reports and the available ChatGPT task/automation service, determine as far as evidence allows:
- intended task name/identity;
- owner/runtime/account boundary if known;
- enabled/disabled/deleted/unknown state;
- cadence/schedule;
- exact producer input and result interface;
- last known successful execution;
- whether the current V5 queue is compatible with that producer.

Do not infer existence merely from old documentation.

### 2. Inspect the available scheduled-task service
If the environment exposes ChatGPT tasks/automations, inspect it for the exact canonical semantic producer or a provably matching historical task.

Hard rules:
- do not create a new task/scheduler in this READ-ONLY recon;
- do not clone or duplicate a likely task;
- do not alter schedules;
- do not manually process semantic rows.

If an exact existing task is found, document whether it can be safely re-enabled/reconnected in a later bounded IMPLEMENT task.

### 3. If the original task is absent, define canonical recovery options
If the intended scheduled ChatGPT task is genuinely absent/unrecoverable, compare only realistic canonical recovery paths, including where relevant:
- restoring the same ChatGPT scheduled-task ownership under the existing contract;
- explicitly migrating semantic data-plane ownership to an already accepted/validated GitHub-hosted zero-cost worker boundary, **but only if such a provider path has actually been proven and accepted by the time of this recon**;
- any smaller repository-owned deterministic mechanism if and only if it can genuinely perform the semantic work without violating current contracts.

Do not recommend a paid OpenAI API fallback. User policy is zero additional payment.

Do not silently assume the Copilot/provider pilot succeeded. Read its durable report if it exists; otherwise treat that option as not yet accepted.

### 4. Produce one recommended next step
Choose the smallest next step that can actually unblock Taste.

The recommendation must say exactly one of:
- `restore_existing_task`
- `reconnect_existing_task`
- `canonical_migration_required`
- `needs_user_evidence`
- `blocked_external`

For `restore_existing_task` / `reconnect_existing_task`, provide the exact bounded IMPLEMENT action and safety checks.

For `canonical_migration_required`, provide the smallest contract/control-plane changes needed, dependencies on any provider audit/pilot, and why this does not become a second active scheduler.

For `needs_user_evidence`, ask only for evidence that cannot be recovered from repository/task services, and make the request Android-friendly and minimal.

## Required report contents
1. Status/recommendation token exactly from the allowed set above.
2. Evidence about the intended canonical task identity and last known execution.
3. Result of current task-service inspection.
4. Whether an existing task is recoverable without duplication.
5. Whether a zero-cost GitHub-hosted migration path is actually accepted/available now, with durable report references if so.
6. Exact next IMPLEMENT/user action.
7. Explicit proof that no second scheduler, no manual bulk semantic processing, no paid API fallback, and no production mutation occurred in this recon.

## Boundaries
- READ-ONLY / RECON only.
- No scheduler creation or mutation.
- No semantic row processing.
- No Taste policy redesign.
- No giveaway/ITAD work.
- No paid API path.
- No autonomous queue drain.

## Completion
Save exactly:
`reviews/worker_reports/taste-semantic-runtime-recovery-recon-01.md`
