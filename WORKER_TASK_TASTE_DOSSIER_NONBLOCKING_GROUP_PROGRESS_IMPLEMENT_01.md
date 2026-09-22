# WORKER TASK — Taste Dossier Non-Blocking Group Progress Implement 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repo by default or the repo target is ambiguous, stop and switch to kentrap2011-hub/steam-kz-deals-2 before doing any work.

Task ID: taste-dossier-nonblocking-group-progress-implement-01
Mode: IMPLEMENT / ACTIVATE / VALIDATE
Worker slot: СУЩЕСТВУЮЩИЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1

## START

First open the current CHAT_PROTOCOL.md from main and complete its START gate.
Then open this task from main and use the current canonical contracts/routes/prompts as source of truth.

Direct continuation of:
- WORKER_TASK_TASTE_DOSSIER_G000005_DUPLICATE_ARTIFACT_BLOCK_DIAGNOSTIC_01.md
- reviews/worker_reports/taste-dossier-g000005-existing-artifact-block-diagnostic-01.md

Do not repeat the broad diagnosis.

## User-authoritative product correction

One bad Dossier group must never block all later groups.

The intended behavior is:

- every predeclared group is attempted independently;
- valid groups persist independently;
- an invalid/failed group is recorded as failed/incomplete and moved out of the forward-progress path;
- later groups continue in the same invocation when budget allows, or on later invocations;
- future invocations resume from the next not-yet-attempted eligible group, not from the first historical failure;
- failed groups/items remain available for separate later recovery/diagnosis;
- no failed group may globally pin Dossier progress or prevent unrelated Dossiers from being produced;
- the Scheduled Dossier worker must never disable/edit its own schedule because of a group-level failure; it may only stop the current invocation when a true runtime/transport failure makes safe forward progress impossible.

## Goal

Replace the current maximal-contiguous-prefix / single canonical_expected_sequence blocking model with a GitHub-owned non-blocking per-group progress model that preserves immutable create-only transport, strict per-group validation, exact scope/order/binding, and fail-closed semantics for the affected group only.

Activate the new model on the current snapshot without losing already accepted work and without fabricating acceptance for invalid g000005.

## Architecture preflight

Before implementation, explicitly identify:
- canonical owner of per-group state, failure state, recovery eligibility, next-work projection, validation, persistence, completeness;
- whether any new queue/retry/checkpoint owner is introduced;
- migration path from current contiguous-prefix state;
- exact relationship between worker index/descriptors, inbox artifacts, canonical dossier cache, validation status, and recovery contract;
- how same-snapshot daily rollover/snapshot replacement remains safe.

GitHub must remain sole control-plane owner. Scheduled ChatGPT remains bounded semantic data-plane only.

## Required design semantics

Use a minimal per-group canonical status model sufficient to represent at least:
- pending / not yet attempted;
- accepted;
- failed_or_invalid_pending_recovery;
- stale/superseded if needed by existing snapshot rollover semantics.

Do not invent extra states without need.

The canonical control plane must be able to derive:
- next normal Dossier work from pending groups only;
- failed groups separately from normal forward-progress work;
- accepted count;
- failed/incomplete count;
- pending count;
- full-backlog completion for the normal first pass when no pending groups remain, even if failed groups remain unresolved.

Clarify naming if existing `full_backlog_complete` cannot safely retain its old meaning. Do not silently redefine a field in a way that breaks consumers.

## Required implementation behavior

1. Remove the global rule that only the maximal valid contiguous prefix can advance.
2. A valid group must be accepted/persisted independently even if an earlier different group failed.
3. An invalid current group must be recorded as failed/incomplete for that exact snapshot/group identity and must not block later groups.
4. The worker's next-start projection must skip groups already accepted or already classified failed/incomplete in the normal first-pass path.
5. The worker may continue from group N to N+1 (or the next pending predeclared group) after a group-level semantic invalid result has been canonically classified, provided transport/runtime remains healthy.
6. Create-only immutable deterministic transport remains mandatory. No overwrite/update/alternate retry filename from Scheduled ChatGPT.
7. Failed-group recovery remains GitHub-owned and separate from normal forward progress. A recovery attempt must not be confused with normal first-pass traversal.
8. Existing strict dossier semantic validation must not be weakened.
9. Existing snapshot/plan/binding exactness must not be weakened.
10. Preserve already accepted groups from the current snapshot.
11. Migrate the current invalid g000005 into the new failed/incomplete state without marking it accepted and without requiring it to succeed before g000006+ can proceed.
12. Ensure current/later buffered groups can drain/validate independently under the new model.
13. Update worker index/prompt so a later invocation resumes from GitHub-owned next pending group rather than a globally blocking expected sequence.
14. Explicitly forbid the Scheduled worker from enabling/disabling/editing its own schedule. Group failure or existing invalid artifact must never disable the recurring task.
15. Preserve the user's hourly cadence; do not create another scheduler.
16. Update/reconcile recovery contract so failed groups are recoverable later without blocking first-pass progress.
17. Update/reconcile any downstream completeness checks so "normal Dossier first pass finished with some failures" is distinguishable from "all Dossiers accepted", and downstream consumers do not treat failed groups as accepted evidence.

## Activation / current g000005

During activation:
- preserve all prior accepted groups exactly;
- classify the already-rejected current g000005 as failed/incomplete under the new model using existing validator evidence;
- move its immutable invalid artifact out of the active normal-forward-progress path using the canonical GitHub-owned recovery/quarantine mechanism or an equivalent contract-safe migration owned by GitHub;
- do not fabricate or manually rewrite a valid g000005 dossier;
- allow the normal next-work projection to advance to later pending groups.

Do not process the entire backlog interactively.

## Validation

Prove with focused tests/synthetic fixtures and current-state activation that:

- BAD g000005 / GOOD g000006 => g000006 can be accepted even while g000005 remains failed;
- BAD g000005 / GOOD g000006 / GOOD g000007 => both later groups persist independently;
- a failed group does not reappear as normal first-pass head on every invocation;
- failed groups remain visible to a separate recovery projection;
- accepted groups are never reprocessed;
- stale/wrong-snapshot/wrong-binding groups cannot mutate current state;
- create-only deterministic filenames remain authoritative;
- no alternate retry filename is introduced;
- the worker cannot disable/edit its own schedule under the canonical prompt/entrypoint contract;
- existing accepted current-snapshot progress is preserved;
- current g000005 is not accepted but no longer blocks g000006+;
- no PASS 1/PASS 2/Taste Semantic Producer behavior is changed.

If safe production validation requires a Scheduled run that the worker cannot invoke authoritatively, stop before inventing it and report the exact remaining user/operator validation step. Repository/GitHub activation should still be completed as far as safely possible.

## Scope exclusions

Do not:
- weaken semantic validation;
- turn failures into acceptance;
- add conversational retries;
- let Scheduled ChatGPT own retry/order/completeness;
- modify PASS 1;
- implement PASS 2;
- modify Taste Semantic Producer;
- change hourly cadence;
- create another Scheduled Task;
- process the whole Dossier backlog manually.

## Acceptance checks

- NB-01: one invalid group cannot block later normal groups.
- NB-02: valid groups persist independently of earlier failures.
- NB-03: failed groups are canonically recorded and excluded from normal first-pass traversal.
- NB-04: failed groups remain separately recoverable.
- NB-05: create-only immutable transport preserved.
- NB-06: strict semantic validation preserved.
- NB-07: exact snapshot/plan/binding validation preserved.
- NB-08: GitHub owns per-group state/order/recovery/completeness.
- NB-09: current accepted progress preserved.
- NB-10: current invalid g000005 becomes failed/incomplete, not accepted, and no longer pins g000006+.
- NB-11: worker resume uses next pending canonical group, not first historical failure.
- NB-12: Scheduled worker self-disable/schedule-edit is explicitly forbidden.
- NB-13: hourly cadence preserved; no new scheduler.
- NB-14: downstream completeness semantics distinguish first-pass exhaustion from all-evidence-success.
- NB-15: no unrelated PASS 1/PASS 2/Taste Semantic Producer mutation.
- NB-16: durable report committed and reread from main before completion.

## Durable report

Create and commit:
reviews/worker_reports/taste-dossier-nonblocking-group-progress-implement-01.md

Keep it compact. Include:
- architecture preflight;
- exact canonical files changed;
- old vs new progress model;
- migration/current g000005 handling;
- validation results;
- current snapshot counts/status after activation;
- any remaining operator validation step;
- NB-01..16;
- exact refs;
- final status;
- exactly one recommended next step.

Allowed statuses:
- complete_ready_for_director_acceptance
- complete_ready_for_user_scheduled_validation
- needs_fix
- blocked_external_operator_action
- needs_user_decision

Before final response, commit the report and reread the exact report from main.
