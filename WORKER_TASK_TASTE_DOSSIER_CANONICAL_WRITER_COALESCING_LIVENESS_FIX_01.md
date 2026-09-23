# WORKER TASK — Taste Dossier Canonical-Writer Coalescing Liveness Fix 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repo by default or the repo target is ambiguous, stop and switch to kentrap2011-hub/steam-kz-deals-2 before doing any work.

Task ID: taste-dossier-canonical-writer-coalescing-liveness-fix-01
Mode: IMPLEMENT / VALIDATE
Worker slot: НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1

## START

First open the current `CHAT_PROTOCOL.md` from main and complete its START gate.

Then read and obey:
- `WORKER_TASK_TASTE_DOSSIER_G000012_EXISTING_ARTIFACT_COLLISION_DIAGNOSTIC_01.md`
- `reviews/worker_reports/taste-dossier-g000012-existing-artifact-collision-diagnostic-01.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/execution_ownership_contract.json`
- current workflows/scripts participating in the shared `taste-steam-review-dossier-canonical-writer` boundary
- `DIRECTOR_TASK_BOARD.md`

## Accepted root cause

The g000012 collision was caused by **lost Dossier ingest/drain liveness inside the shared canonical-writer concurrency boundary**.

Proven sequence:
1. an exact immutable Dossier candidate was created at its correct deterministic create-only path;
2. the Dossier push created an ingest workflow run;
3. that Dossier ingest run was cancelled before any job started while another workflow in the same shared concurrency group was active and a newer shared-writer workflow arrived;
4. the surviving non-Dossier workflow did not reconcile the Dossier inbox;
5. canonical Dossier state therefore continued to report the exact group as pending even though the exact candidate already existed;
6. the Scheduled semantic worker later retried the same authorized create-only path and correctly failed closed with HTTP 422.

The deterministic path identity is correct. The Scheduled semantic worker behavior is correct. The historical g000012 artifact is superseded and must not be recovered or restored.

## Goal

Make the existing shared `taste-steam-review-dossier-canonical-writer` boundary **state-based and coalescing-safe** so that a durable current Dossier inbox candidate cannot remain unclassified merely because its original Dossier wake-up run was cancelled/coalesced before job start.

Preserve one serialized GitHub-owned canonical writer domain. Do not add a second scheduler, retry daemon, polling loop, or worker-owned recovery mechanism.

## 1. Enumerate the shared-writer surface

Before implementation, identify every current workflow/path on `main` that:
- uses the exact `taste-steam-review-dossier-canonical-writer` concurrency group or its canonical current equivalent;
- can arrive after a Dossier candidate push and supersede/coalesce/cancel a pending Dossier ingest run;
- writes canonical/derived state whose correctness depends on current Dossier classification.

Record the exact set in the durable report.

Do not assume only PASS 1 is relevant just because PASS 1 caused the observed incident.

## 2. Coalescing-safe state-based reconciliation

Implement the smallest GitHub-owned fix such that every **surviving canonical-writer path capable of superseding a Dossier wake-up** guarantees reconciliation of already-present current-snapshot Dossier inbox state before it can leave the shared writer boundary.

Allowed architecture choices:
- invoke the existing canonical Dossier reconcile/validation/persistence path from each relevant surviving writer; or
- funnel those writer paths through one common canonical-writer entrypoint that always performs Dossier reconciliation first.

Choose the smallest design that preserves current ownership and serialization.

Required invariants:
- repository state, not the original event type, determines whether Dossier inbox work exists;
- if a current exact immutable Dossier candidate is present, at least one surviving writer must classify it even if the original Dossier wake-up was cancelled before job start;
- classification remains exact/current and uses existing strict validation;
- valid candidate persists once;
- invalid candidate enters the existing failed/recovery path once;
- duplicate surviving writer runs are idempotent and do not double-accept, double-fail, or consume semantic attempts twice;
- stale/old-snapshot candidates remain handled by existing stale/quarantine rules;
- no worker scans inbox and promotes transport state itself;
- GitHub remains the sole owner of classification/persistence/progress.

## 3. Ordering with derived state

Where the surviving workflow also rebuilds dependent derived state, Dossier reconciliation must occur early enough that downstream derived projections use the post-reconcile canonical Dossier truth.

In particular, preserve correct ordering for any Deep/PASS 2 eligibility/projection recomputation already attached to the same canonical writer boundary.

Do not weaken exact-binding/liveness checks.

## 4. Preserve existing transport and identity rules

Do NOT change:
- deterministic Dossier candidate pathname format;
- snapshot/group identity rules;
- create-only semantics;
- overwrite prohibition;
- alternate-filename prohibition;
- worker rule against skipping to the next group after a create-only collision;
- strict Dossier validator semantics;
- independent per-group accepted / failed_or_invalid_pending_recovery / pending model;
- Fast/PASS 1 semantic analysis rules;
- Deep/PASS 2 semantic/recovery model;
- ranking weights.

## 5. Regression for the proven race

Add a regression that reproduces the observed causal ordering, equivalent to:

1. canonical writer A is active;
2. exact current Dossier candidate arrives and its Dossier ingest wake-up becomes pending;
3. newer canonical writer B in the same concurrency group arrives;
4. the original Dossier wake-up is cancelled/coalesced before any job runs;
5. surviving writer B completes.

The regression must prove:
- the already-present exact Dossier candidate is still observed from repository state;
- it is validated/classified exactly once;
- canonical per-group progress no longer remains falsely pending;
- a later Scheduled semantic worker would not be re-authorized to recreate the same exact deterministic path;
- dependent Deep eligibility/projection, if applicable, sees the reconciled canonical Dossier truth;
- no extra scheduler/retry owner was introduced.

Also cover repeated surviving-writer reconciliation after classification to prove idempotence.

## 6. Historical and fresh g000012 guards

- Do not recover, restore, rewrite, rename, or rebind the superseded historical g000012 artifact from snapshot `9cf59f4d...`.
- Do not special-case sequence 12.
- The fix must be generic for any current group and any current snapshot.
- Current fresh g000012 must remain ordinary pending work until naturally reached/classified by normal production flow.

## 7. Scheduler ownership

Do not create, edit, enable, disable, pause, resume, reschedule, or run the `Taste Steam Review Dossier` Scheduled Task.

Do not change its prompt or cadence.

This task fixes GitHub workflow liveness only.

If the task is currently disabled externally, leave it disabled; operator restart is a later separate step after Director acceptance.

## 8. Interaction with active Deep activation work

A separate physical ЧАТ 2 owns:
`WORKER_TASK_PROGRESSIVE_DEEP_PRODUCTION_ACTIVATION_LIVE_ACCEPTANCE_01.md`

Do not modify that task, its branch/PR, its report, Deep scheduler configuration, or Deep production activation state.

The fix must remain compatible with the existing shared canonical writer and current Deep recomputation hooks.

## 9. Secondary stale-cleanup observability discrepancy

The diagnostic noted that the rollover log reported one stale artifact quarantined while the durable tree did not preserve the expected stale quarantine target.

This is NOT the proven cause of the collision.

Do not broaden this task into a stale-quarantine redesign. Only touch it if implementation of the coalescing-safe fix directly requires the same code path and a minimal correctness fix is unavoidable; otherwise record it as out of scope.

## Validation gates

Prove at minimum:

- LIV-01: every current workflow/path capable of superseding a pending Dossier wake-up in the shared writer boundary is enumerated.
- LIV-02: surviving writer reconciliation is state-based, not event-type dependent.
- LIV-03: cancelled zero-job Dossier wake-up cannot strand an exact current inbox candidate as pending.
- LIV-04: valid current candidate is accepted/persisted exactly once.
- LIV-05: invalid current candidate is failed/quarantined/recovery-owned exactly once under existing rules.
- LIV-06: repeated reconciliation is idempotent.
- LIV-07: stale/current snapshot rules remain strict.
- LIV-08: deterministic candidate path/create-only rules are unchanged.
- LIV-09: Scheduled semantic worker ownership remains unchanged and no inbox interpretation is moved into ChatGPT.
- LIV-10: downstream Deep/PASS 2 derived projection uses post-reconcile canonical Dossier truth where relevant.
- LIV-11: no second concurrency domain, scheduler, polling loop, retry daemon, queue owner, or hidden retry is introduced.
- LIV-12: regression reproducing the observed race passes.
- LIV-13: normal existing Dossier ingest path still passes.
- LIV-14: Fast/PASS 1 and Deep/PASS 2 semantic state are not rewritten by this implementation.
- LIV-15: historical g000012 is not restored/recovered/special-cased.
- LIV-16: no Scheduled Task setting/action occurs.
- LIV-17: relevant canonical/focused workflows/tests pass.
- LIV-18: durable report is committed and reread from main before completion.

## Durable report

Create and commit:

`reviews/worker_reports/taste-dossier-canonical-writer-coalescing-liveness-fix-01.md`

Keep it compact and include:
- exact shared-writer workflow/path inventory;
- exact implementation;
- why it closes the cancelled-wake-up hole;
- exact ordering relative to Dossier validation/persistence and dependent Deep projection;
- regression scenario and result;
- idempotence proof;
- files changed;
- validation LIV-01..18;
- confirmation that no scheduler setting/action occurred;
- confirmation historical g000012 was untouched;
- exact refs;
- final status;
- exactly one recommended next step.

Allowed statuses:
- complete_ready_for_director_acceptance
- needs_fix
- blocked_external_operator_action
- needs_user_decision

Before final response, commit the report and reread the exact report from `main`.
