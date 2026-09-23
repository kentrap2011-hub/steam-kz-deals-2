# Taste Dossier clean Scheduled Task regulation 01

**Task:** `WORKER_TASK_TASTE_DOSSIER_CLEAN_SCHEDULED_TASK_REGULATION_01.md`  
**Date:** 2026-09-23  
**Status:** `complete_ready_for_director_acceptance`

## Result

Created the dedicated canonical copy-paste entry/bootstrap regulation for a future **NEW** external ChatGPT Scheduled Task/chat:

`config/taste_steam_review_dossier_scheduled_task_regulation.md`

The regulation intentionally does not fork the Dossier semantic contract. Every invocation starts from current `main`, rereads the current runtime/worker prompts, ownership/contracts, semantic schema/evidence contract, and V2 worker index, and treats repository truth as authoritative over remembered conversation or prior-run state.

The accepted operator hypothesis that a fresh chat may reduce stale-context effects remains only a hypothesis. This task does not claim that a fresh chat fixes the previously observed behavior.

## Files changed

1. `config/taste_steam_review_dossier_scheduled_task_regulation.md`
   - new canonical entry/bootstrap regulation for a future NEW external Scheduled Task/chat;
   - implementation commit: `f911c0995eaf00ef3a4d4a433911cfe3e4bb1139`;
   - committed blob verified from fresh `main`: `c4cc3564744ef2d44f8cacdc5aa694d8479e262c`.
2. `CURRENT_TASK.md`
   - temporary operational handoff entry for this worker task, as required by `CHAT_PROTOCOL.md`;
   - initial tracking commit: `57693accc8b46b3812ede617c732f0eb482c4fd5`.
3. `reviews/worker_reports/taste-dossier-clean-scheduled-task-regulation-01.md`
   - this durable report.

No worker/runtime/schema/evidence/ownership/persistence/index/work-manifest/production-state file was modified.

## Architecture / ownership conclusion

Architecture preflight is satisfied:

1. **Current owner:** GitHub remains control-plane owner for Dossier scope, ordering, immutable group plan, worker projection, validation, persistence, progress, failed-group recovery/retry state, completeness, cleanup, and downstream state. Scheduled ChatGPT remains only the bounded semantic candidate producer using the existing create-only transport. External Scheduled Task lifecycle/configuration remains operator-owned.
2. **Authority for this change:** the task authorizes a dedicated entry/bootstrap regulation only. The current `config/execution_ownership_contract.json`, Dossier contract, persistence bridge, runtime prompt, and worker prompt explicitly preserve the ownership fence.
3. **No responsibility transfer:** the new regulation delegates semantic/runtime truth back to current canonical repository files and transfers no GitHub control-plane responsibility into Scheduled ChatGPT or this interactive worker chat.
4. **No new orchestration:** no recurring stage, scheduler, queue, retry loop, checkpoint authority, persistence path, recovery mechanism, quota, or backlog manager was added.

The regulation explicitly states that `STOP`, fail-closed, no work, stale/changed binding, existing deterministic artifact, validation lag, runtime/transport failure, and ordinary runtime-budget exhaustion can end **only the current invocation**. None authorizes enabling, disabling, pausing, deleting, rescheduling, renaming, recreating, or editing the recurring Scheduled Task.

## Current canonical truth checked

Required current `main` sources were read before implementation:

- `config/taste_steam_review_dossier_worker_prompt.md` — blob `49d6a7e19e6b6f52aa75a0db96f30721db0e1895`;
- `config/taste_steam_review_dossier_runtime_prompt.md` — blob `3ab7946cc5cc9241d8433155b85559a68226a4c9`;
- `config/taste_steam_review_dossier_contract.json` — blob `c9765f9a3330f90aa00899309949e5348e6bcb21`;
- `config/taste_steam_review_dossier_persistence_bridge.json` — blob `4d53faade7de382d63539bdb5e4ed2797c601400`;
- `config/execution_ownership_contract.json` — blob `76f1132bf8dceda9792e303d70e64cabd49b1a0e`;
- `data/production/pre_ai/taste_steam_review_dossier_worker_index.json` — blob `9609b51181d4f97da89899f93bdb7b4b86849a8c`;
- `reviews/worker_reports/taste-dossier-worker-prompt-v2-alignment-fix-01.md` — blob `e8f73da50c6c56e1623bb81d1a6236d74add65b6`;
- `reviews/worker_reports/taste-dossier-scheduled-task-self-disable-ownership-diagnostic-01.md` — blob `df13de390ed90da17503ad259d43eec9c42ae0b9`.

Fresh-main verification after the regulation commit confirms:

- worker index schema: `TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2`, version `2`;
- current snapshot: `bae494b435e752f23beea70ee238d7f480f45cf94d9d27e8827525bb4b67fc09`;
- `next_pending_sequence=1`;
- `pending_group_count=187`;
- runtime revision: `nonblocking-group-progress-v2-exact-buffer-identity`;
- canonical worker prompt uses the V2 worker index and contains no `canonical_expected_sequence`;
- canonical runtime prompt contains the explicit self-scheduler mutation prohibition.

## Validation performed

A fresh-main structural validation of the committed regulation checked all of the following and returned PASS:

- identifies itself as the complete bootstrap for a **NEW** external task/chat;
- rereads current `main` on every invocation;
- makes remembered/old chat state non-authoritative;
- binds normal work to V2 `next_pending_sequence` / `pending_group_sequences`;
- explicitly forbids using `canonical_expected_sequence` as current work authority;
- separates invocation STOP from recurring scheduler lifecycle;
- leaves scheduler lifecycle/configuration operator-owned;
- preserves GitHub control-plane ownership;
- preserves immutable create-only candidate transport;
- references semantic/evidence/privacy/exact-product rules instead of forking them;
- forbids new scheduler/queue/retry/checkpoint/persistence/recovery ownership;
- defines compact success/no-work/fail-closed operator-visible responses;
- states that a fresh chat is not proof of a fix.

No new anti-drift test was added. This was intentional: the regulation is a bootstrap indirection to current canonical files, not a new semantic/runtime binding. The existing V2 live alignment regression remains unchanged; the required alignment report records its successful run `35875165680` / job `107229124431`. No runtime/worker/index semantic surface was changed by this task.

## Acceptance checks

| Gate | Status | Evidence |
|---|---|---|
| REG-01 | **PASS** | `config/taste_steam_review_dossier_scheduled_task_regulation.md` exists on `main` and is written as a complete copy-paste bootstrap prompt for a NEW task/chat. |
| REG-02 | **PASS** | Regulation requires V2 worker-index traversal via `next_pending_sequence` / `pending_group_sequences` and explicitly forbids `canonical_expected_sequence` as current authority. |
| REG-03 | **PASS** | Invocation STOP/fail-closed/no-work/runtime failure is explicitly separated from recurring Scheduled Task lifecycle. |
| REG-04 | **PASS** | Scheduled Task enable/disable/pause/delete/reschedule/rename/recreate/edit remains external operator-owned and worker-forbidden. |
| REG-05 | **PASS** | GitHub remains control plane for scope/order/projection/validation/persistence/progress/recovery/completeness. |
| REG-06 | **PASS** | Create-only transport and semantic/evidence/privacy/exact-product behavior are preserved by reference to current canonical prompts/contracts rather than duplicated. |
| REG-07 | **PASS** | Old chat messages, prior worker conclusions, previous snapshot/binding assumptions, and old task state are explicitly non-authoritative without current-main revalidation. |
| REG-08 | **PASS** | No Scheduled Task UI/action, create/edit/enable/disable/delete, `Run now`, Dossier semantic production, recovery action, or scheduler creation was performed. |
| REG-09 | **PASS** | No new guard was necessary or added; existing V2 alignment/ownership guards were not modified, and current canonical V2/runtime ownership bindings were revalidated read-only. |
| REG-10 | **PASS** | This exact durable report is committed to `main`; the worker final response is permitted only after a fresh-main reread of this committed report. |

## External / production non-actions

- no ChatGPT Scheduled Task was created, edited, enabled, disabled, paused, deleted, renamed, rescheduled, recreated, or run;
- no `Run now` was used;
- no Dossier candidate artifact was produced;
- no Dossier semantic production was executed;
- no Dossier recovery was executed;
- no current Dossier canonical progress/state was edited;
- no Fast/PASS 1 or Deep/PASS 2 source/state/attempt/history/runtime was changed;
- no historical group, including `g000012`, was repaired or special-cased.

## Copy-paste regulation path

`config/taste_steam_review_dossier_scheduled_task_regulation.md`

## Next step

After Director acceptance, the user may create a **NEW** external ChatGPT Scheduled Task/chat and paste the canonical regulation for the separately controlled test. That external action was not performed by this worker.
