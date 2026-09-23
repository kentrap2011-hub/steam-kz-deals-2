# WORKER TASK — TASTE DOSSIER CLEAN SCHEDULED TASK REGULATION 01

Repository: `kentrap2011-hub/steam-kz-deals-2`

Base branch / source of truth: `main`

Repository scope guard: do not search, read, change, or use any other repository. If a tool opens another repository or the repository is ambiguous, stop and return to `kentrap2011-hub/steam-kz-deals-2` before doing any task work.

Task ID: `taste-dossier-clean-scheduled-task-regulation-01`

Mode: `IMPLEMENT`

## Goal

Create a new clean, copy-paste-ready **Scheduled Task regulation / live entry prompt** for a future NEW external ChatGPT task/chat running the existing `Taste Steam Review Dossier` worker.

The new regulation must be robust against stale conversational context and must preserve the current GitHub-owned Dossier architecture. It is an entry/bootstrap contract only: it must not become a second semantic contract, scheduler owner, retry owner, queue owner, checkpoint owner, or persistence owner.

This task does **not** create, enable, disable, edit, run, or delete any external ChatGPT Scheduled Task. The user will perform any later UI action separately after Director acceptance.

## Required START and current truth

First execute the START gate from the current `CHAT_PROTOCOL.md`.

Then read the minimum current canonical sources needed to establish the live boundary, including at least:

- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_runtime_prompt.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/execution_ownership_contract.json`
- `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- `reviews/worker_reports/taste-dossier-worker-prompt-v2-alignment-fix-01.md`
- `reviews/worker_reports/taste-dossier-scheduled-task-self-disable-ownership-diagnostic-01.md`

Use current `main`, not remembered chat state, as authority.

## Background / accepted facts

The prior self-disable diagnostic established that canonical `STOP` means stopping the **current invocation only**. No canonical rule authorizes the Dossier semantic worker to disable/pause/delete/reschedule/edit its recurring Scheduled Task. The unsupported mapping `invocation STOP -> recurring task disable` was classified as worker interpretation / ownership-layer conflation.

The current Dossier worker prompt has already been aligned to the active V2 index/runtime. Do not reintroduce V1 traversal rules or `canonical_expected_sequence`.

The user wants to test a fresh external task/chat because stale conversation context is a plausible operational factor. Treat that as an operator hypothesis, not as a proven root cause.

## Required implementation

Create one dedicated canonical file for the new external Scheduled Task regulation:

`config/taste_steam_review_dossier_scheduled_task_regulation.md`

It must be concise enough to paste into a new Scheduled Task, but complete enough to define the entry/bootstrap boundary without relying on old chat history.

The regulation must:

1. State that every invocation begins from current `main` and reads the current canonical Dossier worker prompt and required ownership/contracts before semantic work.
2. State that current repository files override remembered/prior conversational context and prior run interpretations.
3. Bind to the current V2 worker-index/runtime route and contain no stale V1/`canonical_expected_sequence` behavior.
4. Make the scheduler-ownership boundary explicit:
   - `STOP`, fail-closed, no work, stale binding, existing deterministic artifact, validation lag, or runtime/transport failure may end the **current invocation only**;
   - they are never authority to enable, disable, pause, delete, reschedule, rename, recreate, or edit the recurring Scheduled Task;
   - Scheduled Task lifecycle/configuration changes are external operator actions.
5. Preserve GitHub as control plane for scope/order/projection/validation/persistence/progress/recovery/completeness.
6. Preserve create-only candidate publication and all existing evidence/privacy/exact-product semantics by reference to the current canonical worker prompt/contracts rather than duplicating and drifting the full semantic contract.
7. Explicitly forbid treating old chat messages, previous worker conclusions, previous snapshot/binding assumptions, or old task state as authority without revalidation against current `main`.
8. Define a compact success/fail-closed final response contract sufficient for operator observability without changing canonical progress semantics.
9. Avoid adding any new scheduler, retry loop, queue, checkpoint, persistence path, control-plane state, or semantic ownership.
10. Be ready for the user to paste into a **NEW** external Scheduled Task/chat after Director acceptance.

If a small focused regression or documentation guard is necessary to prevent future drift between this regulation and the current runtime/worker ownership fence, add only the smallest bounded guard. Do not broaden into a Dossier architecture rewrite.

## Explicit prohibitions

Do not:

- create or modify any ChatGPT Scheduled Task;
- press or simulate `Run now`;
- run Dossier semantic production;
- create a second recurring producer;
- change schedule/cadence/production limits;
- change Dossier evidence/schema/privacy/exact-app semantics;
- change canonical progress/retry/recovery ownership;
- change Fast or Deep production;
- repair historical groups or special-case historical `g000012`;
- infer that a fresh chat fixes the issue; this task only prepares a clean regulation for a controlled later test.

## Acceptance checks

The final implementation/report must prove:

- REG-01: the new regulation file exists on `main` and is copy-paste-ready;
- REG-02: it references the current V2 Dossier route and contains no stale V1 traversal rule;
- REG-03: current-invocation STOP and recurring-scheduler lifecycle are unambiguously separated;
- REG-04: external scheduler mutation remains operator-owned and worker-forbidden;
- REG-05: GitHub control-plane ownership is preserved;
- REG-06: semantic/evidence/privacy contract is referenced, not silently forked;
- REG-07: prior chat context is explicitly non-authoritative versus current `main`;
- REG-08: no Scheduled Task UI action, Run now, semantic production, recovery, or scheduler creation occurred;
- REG-09: any added anti-drift guard passes together with relevant existing Dossier alignment/ownership tests;
- REG-10: exact durable report is committed to `main` and reread before final response.

## Durable report

Write and commit:

`reviews/worker_reports/taste-dossier-clean-scheduled-task-regulation-01.md`

Allowed final statuses:

- `complete_ready_for_director_acceptance`
- `needs_user_decision`
- `blocked`

The report must include:
- exact files changed;
- architecture/ownership conclusion;
- validation performed;
- REG-01..10 status;
- confirmation that no external Scheduled Task action was performed;
- the exact path of the copy-paste regulation file.

Before claiming completion, reread the committed report from fresh `main`.

## CURRENT_TASK.md

Update `CURRENT_TASK.md` only if required by the current protocol for the actually executing worker task. Do not overwrite or erase unrelated active work.

## Expected next step

After Director acceptance, the user may create a NEW external ChatGPT Scheduled Task/chat and paste the accepted regulation for a controlled single-run test. Do not perform that step in this worker task.
