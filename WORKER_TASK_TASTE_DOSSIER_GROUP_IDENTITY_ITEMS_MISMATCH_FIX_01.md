# WORKER TASK — Taste Dossier Group Identity Items Mismatch Fix 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repo by default or the repo target is ambiguous, stop and switch to kentrap2011-hub/steam-kz-deals-2 before doing any work.

Task ID: taste-dossier-group-identity-items-mismatch-fix-01
Mode: DIAGNOSE / IMPLEMENT / VALIDATE
Worker slot: НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2

## START

First open the current `CHAT_PROTOCOL.md` from main and complete its START gate.
Then open this task from main and use current canonical Dossier contracts/runtime prompt/worker projection as source of truth.

## Confirmed live defect

After the accepted non-blocking Dossier redesign, one clean Scheduled `Taste Steam Review Dossier` run on current snapshot

`9cf59f4d94d1b4c7270bece5464666e3eb2359b87bd74cbefe3883b969f90689`

published two exact deterministic create-only candidate groups:

- g000001 — commit `559046f6ae9dd52343bed422b77e9fde7110e24f`
- g000002 — commit `8746ad32e6004b3405eb5699c6dd5a385b18cb4c`

GitHub independently classified both as:

`failed_or_invalid_pending_recovery`

with the same validator error:

`buffered dossier group identity mismatch: items`

Current forward progress is correctly non-blocking:
- accepted groups: 0
- failed groups: 2
- pending groups: 182
- next pending: g000003

This task fixes only the systematic candidate-generation identity mismatch. Do not roll back or weaken the accepted non-blocking progress architecture.

## Goal

Find the exact first divergence between the immutable GitHub descriptor `items` projection and the Scheduled-worker buffered candidate `items` serialization, then fix the producer-facing contract/runtime path so future exact groups serialize the descriptor-bound items exactly as required by the existing strict validator.

The strict validator is presumed correct unless concrete evidence proves a canonical contract contradiction. Do not “fix” this by weakening identity validation.

## Required diagnosis

For g000001 and g000002, compare the exact immutable descriptor-bound `items` with the quarantined submitted candidate `items` and identify the smallest concrete mismatch class, such as:
- missing fields;
- extra fields;
- field normalization;
- null/omitted differences;
- ordering;
- worker reconstruction instead of verbatim descriptor projection;
- stale prompt/schema/runtime binding;
- another proven serialization divergence.

Do not speculate. Record the exact first differing field/path and why the worker produced it.

Also verify whether the same generator path would affect g000003+.

## Implementation constraints

Preserve:
- GitHub as control plane;
- immutable predeclared group descriptors;
- create-only per-group transport;
- exact snapshot/plan/group binding;
- per-group independent acceptance/failure;
- failed-group recovery separation;
- strict semantic validation;
- current Dossier evidence semantics;
- current Scheduled cadence outside this task.

Forbidden:
- weakening `items` equality;
- accepting “semantically equivalent” but non-exact identity;
- manual acceptance of g000001/g000002;
- rewriting quarantined artifacts;
- reopening failed groups merely to hide the defect;
- reverting to contiguous-prefix blocking;
- PASS 1/PASS 2 behavior changes;
- Taste Semantic Producer changes;
- Scheduled Task create/edit/enable/disable/run from the worker.

If a canonical contract contradiction is actually proven, make the minimum consistent contract+generator correction and preserve fail-closed validation.

## Validation

At minimum prove:

- ITEM-ID-01: exact first divergence for g000001 is identified.
- ITEM-ID-02: exact first divergence for g000002 is identified and shown to share or not share the same root cause.
- ITEM-ID-03: the fix makes a synthetic/current-descriptor candidate serialize `items` byte-for-structure exactly as validator expects.
- ITEM-ID-04: missing/extra/reordered/normalized item mutations still fail strict validation.
- ITEM-ID-05: non-blocking per-group progression remains intact.
- ITEM-ID-06: failed g000001/g000002 remain failed/recovery-owned; they are not silently accepted or rewritten.
- ITEM-ID-07: g000003+ future generation path uses the corrected exact descriptor projection.
- ITEM-ID-08: no PASS 1/PASS 2/Taste Semantic Producer behavior changes.
- ITEM-ID-09: no Scheduled Task configuration or production Run now occurs inside this task.
- ITEM-ID-10: relevant Dossier regressions and canonical build/validation pass.
- ITEM-ID-11: durable report committed and reread from main before completion.

Do not consume the user's live validation run inside this worker task. The post-fix live acceptance is one separate user-triggered `Run now` after Director review.

## Durable report

Create and commit:

`reviews/worker_reports/taste-dossier-group-identity-items-mismatch-fix-01.md`

Keep it compact and include:
- exact root cause;
- exact first divergence for g000001/g000002;
- exact files changed;
- why validator semantics remain safe;
- validation ITEM-ID-01..11;
- current state of failed g000001/g000002;
- whether future g000003+ path is corrected;
- exact refs;
- final status;
- exactly one recommended next step.

Allowed statuses:
- complete_ready_for_user_scheduled_validation
- complete_ready_for_director_acceptance
- needs_fix
- blocked_external_operator_action
- needs_user_decision

Before final response, commit the report and reread the exact report from main.
