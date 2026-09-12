# DIRECTOR TASK BOARD

## Current rules
- Keep at most two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots.
- No autonomous IMPLEMENT without separate user approval.
- Reconcile Board -> exact task -> exact durable report before assigning follow-up work.
- Proactive gap detection follows `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`; the user is not the project's monitoring layer.
- Current priority is operational speed. Architecture review may run in parallel only when read-only and non-blocking.

## ACCEPTED — real Steam partial-publish production refresh
Task:
`WORKER_TASK_STEAM_PARTIAL_PUBLISH_PRODUCTION_REFRESH_01.md`

Task ID:
`steam-partial-publish-production-refresh-01`

Report:
`reviews/worker_reports/steam-partial-publish-production-refresh-01.md`

Final status:
`complete_with_problem_entries_for_separate_review`

Verified real production result:
- integration reached `main` through PR #15; merge commit `c9980e79d002e84a321d2cff089645f81d91c6b7`;
- production workflow run `34643249267` completed `success`;
- partial-publish regression passed;
- Steam partial-publish collector step passed;
- production publish step passed;
- source coverage was complete with 17,299 observed / 17,299 reported;
- 17,287 items processed successfully;
- shortlist contained 676 games;
- 12 unresolved game-level problems, all at `review_enrichment` with root error `Steam Reviews API did not return both required summaries`;
- 0 unresolved catalog segments;
- 0 system-state problems;
- 0 last-known-good preserved entries in that run;
- production commit `a73b9ce8e95f464c67ebf733fa8703f801e744cc` reached `main`;
- downstream visual refresh run `34645306958` completed `success`;
- refreshed ordinary Steam dataset propagated into the normal downstream feed path.

`ЧАТ 1` is now free and may be deleted/reused.

The 12 problem entries are intentionally left for separate review; do not auto-investigate them without authorization.

## NEEDS REPORT/FINISH — read-only architecture review
Task:
`WORKER_TASK_CODE_ARCHITECT_SYSTEM_REVIEW_01.md`

Task ID:
`code-architect-system-review-01`

Worker slot:
`ЧАТ 2`

Mode:
`READ_ONLY_REVIEW`

Current Director observation:
- required report `reviews/worker_reports/code-architect-system-review-01.md` is not yet present on `main`.

Remaining requirement:
- finish the already-authorized read-only review;
- write the durable report;
- do not mutate production code/data/workflows/main beyond adding the review report through the normal worker-report durability mechanism;
- include the accepted Steam partial-publish structure and current post-integration production structure;
- if `main` changed during the review, perform only the bounded final architecture check required by the task rather than restarting from zero.

Expected final status:
- `review_complete_recommendations_ready`
- `review_complete_no_material_architecture_change_needed`
- or `blocked_requires_followup`

## ACCEPTED — Steam partial publish + failure isolation implementation
Task:
`WORKER_TASK_STEAM_PARTIAL_PUBLISH_FAILURE_QUEUE_01.md`

Task ID:
`steam-partial-publish-failure-queue-01`

Accepted worker branch:
`worker/steam-partial-publish-failure-queue-01`

Accepted worker head:
`5556ce5c763d886a42b3c89ba69df711ba745adb`

Report:
`reviews/worker_reports/steam-partial-publish-failure-queue-01.md`

Final status:
`complete_ready_for_real_steam_refresh`

## QUEUED LATER — ChatGPT Steam error notification watch
Task:
`WORKER_TASK_STEAM_ERROR_NOTIFICATION_WATCH_01.md`

Task ID:
`steam-error-notification-watch-01`

Status:
`queued_later_do_not_start_now`

Goal when later authorized:
- separate ChatGPT scheduled check, approximately hourly;
- read the latest canonical Steam problem report from GitHub;
- stay silent when there are no unresolved problems;
- notify only when the unresolved problem set is new or changed;
- do not repeat the same unchanged alert every hour;
- do not automatically repair or investigate failures.

Dependency:
- durable production refresh report now exists.

## QUEUED LATER — decouple giveaways from Steam commercial crawl
Task:
`WORKER_TASK_GIVEAWAY_DECOUPLE_FROM_STEAM_CRAWL_01.md`

Task ID:
`giveaway-decouple-from-steam-crawl-01`

Status:
`queued_later_do_not_start_now`

Goal when later authorized:
- Epic/GOG/Steam giveaway refresh must be able to update independently from the full Steam commercial catalog traversal;
- commercial Steam crawl may remain fail-closed without blocking valid current giveaway state/publication.

## CLOSED / DIAGNOSED — site giveaway + freshness recovery 02
Task:
`WORKER_TASK_SITE_GIVEAWAY_AND_FRESHNESS_RECOVERY_02.md`

Report:
`reviews/worker_reports/site-giveaway-and-freshness-recovery-02.md`

Final status:
`failed_closed_root_cause_proven`

## CLOSED — existing 10-result pinned ingest
Task:
`WORKER_TASK_TASTE_EXISTING_BATCH_PINNED_INGEST_01.md`

Report:
`reviews/worker_reports/taste-existing-batch-pinned-ingest-01.md`

Final status:
`complete_existing_10_result_pinned_ingest_verified`

## DEFERRED — Taste queue age-priority ordering
Task:
`WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md`

Status:
`queued_before_next_new_semantic_batch`

Required ordering for newly constructed Taste work:
1. never successfully canonically Taste-checked;
2. then previously checked from oldest successful canonical Taste evaluation to newest.

## Proactive Project Auditor — standing role
Protocol:
`PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`

## Normal Scheduled Task — still NOT normal producer
Existing task:
- title `Taste Semantic Producer`
- id `6aa032f37e688191a5c9a1a83f91c5d9`
- current prompt is still the old Chernobylite one-game canary prompt.

Keep the stale canary safely DAILY 01:00 Europe/Samara until normal producer implementation is actually ready.

## Other queued work
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued.
- `WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.
