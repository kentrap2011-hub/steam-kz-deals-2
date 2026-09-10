# DIRECTOR TASK BOARD

## Current rules
- Keep at most two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots.
- No autonomous IMPLEMENT without separate user approval.
- Reconcile Board -> exact task -> exact durable report before assigning follow-up work.
- Proactive gap detection follows `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`; the user is not the project's monitoring layer.

## CURRENT TOP PRIORITY — FINISH CURRENT WEBSITE RECOVERY
The user explicitly changed priority: before Taste queue ordering or more backlog processing, the real site must show the current canonical publishable games and the current eligible free-game entries.

Primary sequence now:
1. finish giveaway-source refresh and publication freshness correctness;
2. verify current eligible Epic giveaways appear in the deployed Pages artifact/site;
3. only then return to Taste queue age-ordering;
4. then resume real Taste backlog processing;
5. later implement selective profile-change reevaluation.

## PARTIALLY COMPLETE — first site recovery
Task:
`WORKER_TASK_SITE_CURRENT_GAMES_AND_FREE_GAME_RECOVERY_01.md`

Report:
`reviews/worker_reports/site-current-games-and-free-game-recovery-01.md`

Final status:
`failed_closed_root_cause_proven`

Completed:
- original `Build daily visual payload` failure diagnosed and repaired;
- several pending-AI visual/semantic validation gates corrected without weakening completed-semantic checks;
- final build run `34498384650` succeeded;
- final deploy run `34498439445` succeeded;
- GitHub Pages deployment completed;
- deployed Pages artifact contains 115 non-giveaway entries.

Still broken:
1. deployed freshness is `degraded/no_fresh_build`, reason `visual_source_history_mismatch`;
2. canonical giveaway snapshot is stale across the 2026-09-10 Epic rotation;
3. deployed giveaway block is `state=unavailable`, `games=[]`;
4. current Epic giveaways identified in the report are `Astral Ascent` and `Luftrausers`, both absent from the deployed artifact.

Do NOT mark the site fully current until both giveaway freshness and publication freshness are resolved.

## PREPARED FOLLOW-UP — giveaway + freshness recovery
Task:
`WORKER_TASK_SITE_GIVEAWAY_AND_FRESHNESS_RECOVERY_02.md`

Report:
`reviews/worker_reports/site-giveaway-and-freshness-recovery-02.md`

Status:
`prepared_awaiting_user_authorization`

Goal:
- identify and repair why canonical giveaway source did not refresh after rotation;
- restore current eligible giveaway entries end-to-end;
- diagnose and repair `visual_source_history_mismatch` without weakening freshness checks;
- rebuild, deploy, and verify the exact deployed Pages artifact is fresh and contains current giveaways.

This is a direct continuation of the same site goal and should preferably use the same CHAT 1 while its context remains useful.

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

## DEFERRED UNTIL SITE IS CURRENT — Taste queue age-priority ordering
Task:
`WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md`

Report:
`reviews/worker_reports/taste-queue-age-priority-order-01.md`

Status:
`queued_after_site_recovery_before_next_new_semantic_batch`

Required ordering for newly constructed Taste work:
1. never successfully canonically Taste-checked;
2. then previously checked from oldest successful canonical Taste evaluation to newest.

Rules:
- failed/rejected/unaccepted attempts do not count as a check;
- deterministic stable tie-breaker;
- do not invent a timestamp source;
- do not silently mutate an already active exact pin.

## After site + ordering — resume real backlog drain
Resume bounded real Taste semantic processing from canonical state. Process actual games, checkpoint accepted batches, and continue until genuine blocker/safe stop/practical execution limit. Do not mistake infrastructure defects for semantic capacity.

## Proactive Project Auditor — standing role
Protocol:
`PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`

The auditor should proactively catch stale canary prompts, wrong cadence, queue-order mismatches, stale design assumptions, incomplete production wiring, unnecessary reprocessing, and system defects being mistaken for normal behavior.

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
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste/site priority.

`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.
