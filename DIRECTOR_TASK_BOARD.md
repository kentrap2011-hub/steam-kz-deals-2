# DIRECTOR TASK BOARD

## Current rules
- Keep at most two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots.
- No autonomous IMPLEMENT without separate user approval.
- Reconcile Board -> exact task -> exact durable report before assigning follow-up work.
- Proactive gap detection follows `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`; the user is not the project's monitoring layer.

## Current user priority — PROCESS REAL GAMES FIRST
Primary sequence:
1. existing 10-result recovery — COMPLETE;
2. implement required Taste queue ordering by successful-check age;
3. resume real backlog processing in bounded batches;
4. get enough canonical results that the user can actually inspect/use them;
5. later implement selective profile-change reevaluation.

Do not pause backlog drain for non-blocking optimization work.

## CLOSED — existing 10-result pinned ingest
Task:
`WORKER_TASK_TASTE_EXISTING_BATCH_PINNED_INGEST_01.md`

Report:
`reviews/worker_reports/taste-existing-batch-pinned-ingest-01.md`

Final status:
`complete_existing_10_result_pinned_ingest_verified`

Verified result:
- exactly one manual `workflow_dispatch` attempt;
- run `34484740625`, job `102896057405`, success;
- acceptance commit `ddb1a51b8321997bbbb83505d69cfe4031758619`;
- receipt `data/cache/taste_ingest_receipts/ba86bfdcf8365dfa0195.json`;
- all 10 original results canonically persisted unchanged under historical profile A;
- queue remained `539 -> 539` intentionally because none of those A results satisfy current profile B;
- current-B work remains pending;
- next active work-unit pin was created for current profile B;
- no next semantic batch was started by the ingest worker.

Old CHAT 1 worker slot is now free.

## IMMEDIATE NEXT — Taste queue age-priority ordering
Task:
`WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md`

Report:
`reviews/worker_reports/taste-queue-age-priority-order-01.md`

Status:
`ready_for_dispatch_before_next_new_semantic_batch`

Required ordering for newly constructed Taste work:
1. never successfully canonically Taste-checked;
2. then previously checked from oldest successful canonical Taste evaluation to newest.

Rules:
- failed/rejected/unaccepted attempts do not count as a check;
- deterministic stable tie-breaker;
- do not invent a timestamp source;
- an already active exact pin is preserved unless a separately authorized safe repin design explicitly changes that rule.

Important transition note:
The successful legacy ingest already created a current-B active pin. Therefore one already-pinned work-unit may remain ahead of the new age-order policy. The ordering task must not silently mutate/retire that active pin. After it is completed/retired through the normal lifecycle, subsequent newly constructed work-units must use the new age ordering.

## After ordering — resume real backlog drain
Resume bounded real Taste semantic processing from canonical state. Process actual games, checkpoint accepted batches, and continue until genuine blocker/safe stop/practical execution limit. Do not mistake infrastructure defects for semantic capacity.

## Proactive Project Auditor — standing role
Protocol:
`PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`

The auditor should proactively catch stale canary prompts, wrong cadence, queue-order mismatches, stale design assumptions, incomplete production wiring, unnecessary reprocessing, and system defects being mistaken for normal behavior.

### QUEUED READ-ONLY AUDIT — downstream visual failure
Task:
`WORKER_TASK_PROACTIVE_VISUAL_DOWNSTREAM_FAILURE_AUDIT_01.md`

Report:
`reviews/worker_reports/proactive-visual-downstream-failure-audit-01.md`

Trigger:
After Taste acceptance commit `ddb1a51b8321997bbbb83505d69cfe4031758619`, downstream `Build daily visual payload` run `34484781975` failed and `Deploy visual mailing` run `34484824317` was skipped.

This does NOT invalidate the successful Taste ingest. Audit is read-only and must determine impact/root cause without blocking Taste unless evidence proves a real blocker.

## Normal Scheduled Task — still NOT normal producer
Existing task:
- title `Taste Semantic Producer`
- id `6aa032f37e688191a5c9a1a83f91c5d9`
- current prompt is still the old Chernobylite one-game canary prompt.

Therefore do not claim it currently drains the queue automatically.

Keep the stale canary safely DAILY 01:00 Europe/Samara until normal producer implementation is actually ready. When enabled, update this SAME task, do not create a second producer.

User-required eventual normal cadence: HOURLY (`RRULE:FREQ=HOURLY`).

## Ready design — bounded normal producer
Report:
`reviews/worker_reports/taste-normal-daily-binding-design-01.md`

Existing recommendation:
- max 10 Taste items per invocation;
- max 1 semantic work-unit per invocation;
- deterministic producer-owned head;
- pinned exact profile/work identity;
- strict atomic ingest/post-ingest verification;
- deterministic suffix resume.

Cadence detail in the old design is superseded by the user's later requirement: normal producer should eventually run hourly.

## QUEUED LATER — selective profile-change reevaluation
Task ID:
`taste-selective-profile-reevaluation-01`

Status:
`queued_after_current_backlog_is_usable`

Goal:
A small live-profile edit should not force hundreds of unaffected games through semantic reevaluation merely because whole-profile blob SHA changed. Later design must invalidate/requeue only materially affected prior results where safely provable, while preserving provenance and fail-closed behavior.

Eventual reevaluation processing cadence: once per hour, meaning process affected pending work hourly, not reanalyze the whole database hourly.

## Other queued work
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste priority.

`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.
