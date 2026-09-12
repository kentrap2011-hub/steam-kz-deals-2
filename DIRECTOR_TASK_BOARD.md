# DIRECTOR TASK BOARD

## Current rules
- Keep at most two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots.
- No autonomous IMPLEMENT without separate user approval.
- Reconcile Board -> exact task -> exact durable report before assigning follow-up work.
- Proactive gap detection follows `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`; the user is not the project's monitoring layer.
- Current priority is operational speed. Architecture review may run in parallel only when read-only and non-blocking.

## ACTIVE — normal ChatGPT/Taste semantic producer
Task:
`WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md`

Task ID:
`taste-normal-semantic-producer-01`

Status:
`authorized_dispatched_chat_1`

Mode:
`IMPLEMENT_AND_VERIFY_READY_FOR_SCHEDULE`

Worker slot:
`ЧАТ 1`

Worker context:
- use a NEW clean working chat named `ЧАТ 1`;
- the previous Steam `ЧАТ 1` is closed and must not be reused for this task.

Goal:
- implement the normal deterministic Taste queue producer for ChatGPT evaluation;
- process at most 10 games per invocation;
- integrate never-checked-first, then oldest-successfully-checked-first ordering;
- preserve accepted historical Taste results and provenance;
- make retry/result ingest durable and idempotent;
- use short deterministic tests only;
- do not run a large real semantic batch;
- do not create a second Scheduled Task;
- do not change existing Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` yet;
- prepare the exact prompt contract and recommended cadence for the Director to activate later.

Expected report:
`reviews/worker_reports/taste-normal-semantic-producer-01.md`

Expected final status:
- `complete_ready_for_normal_scheduled_producer`
- or `blocked_requires_followup`

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
- source coverage was complete with 17,299 observed / 17,299 reported;
- 17,287 items processed successfully;
- shortlist contained 676 games;
- 12 unresolved game-level problems at `review_enrichment`;
- 0 unresolved catalog segments;
- 0 system-state problems;
- production and downstream visual refresh succeeded.

Previous Steam worker chat is closed. Its reusable slot number `ЧАТ 1` has been reassigned to the new clean Taste worker chat above.

## ACCEPTED — read-only architecture review
Task:
`WORKER_TASK_CODE_ARCHITECT_SYSTEM_REVIEW_01.md`

Task ID:
`code-architect-system-review-01`

Report:
`reviews/worker_reports/code-architect-system-review-01.md`

Final status:
`review_complete_recommendations_ready`

Accepted conclusions:
- no blocking structural issue was found;
- current Steam partial-publish path is operationally sound and should remain the canonical production entry point;
- highest-value Steam cleanup later is to replace the source-text/`exec` loading boundary with a normal importable Steam core, while keeping `steam_partial_publish.py` separate;
- pair that refactor with direct deterministic tests of the real runner boundary;
- document canonical entry points/legacy paths before larger cleanup because this has high benefit and low cost;
- keep large cohesive coordinators such as `build_final_visual_payload.py` and `director_orchestration_controller.py` intact for now, improving navigation with section anchors instead of splitting by size;
- extract deterministic policy logic from large workflow heredocs later rather than replacing GitHub Actions orchestration wholesale;
- audit/retire or clearly label legacy Steam/visual execution paths after consumer confirmation;
- do not mass-reorganize the `scripts/` tree;
- all structural refactors are non-blocking and may wait while operational speed is the priority.

Evidence notes:
- architecture report reviewed the accepted Steam head and post-integration `main` state;
- report commit `9f4e5891ec5ae44e06eb860881e780eed62d4129` added only the architecture report and did not modify production code/workflows/data.

`ЧАТ 2` is now free and may be deleted/reused.

## QUEUED LATER — reduce Steam catalog before local filtering
Task:
`WORKER_TASK_STEAM_SERVER_SIDE_PREFILTER_OPTIMIZATION_01.md`

Task ID:
`steam-server-side-prefilter-optimization-01`

Status:
`queued_later_do_not_start_now`

Mode when authorized:
`MEASURE_FIRST_THEN_PROPOSE`

Goal:
- investigate whether safe Steam-side/coarse prefilters can reduce the ~17,299-item input substantially before expensive local/review processing;
- do not target exactly 600 items; target the smallest safe candidate set that preserves canonical shortlist recall;
- use the successful run `34643249267` and its 676-item shortlist as a control baseline;
- measure candidate strategies instead of guessing;
- reject filters that can lose currently eligible games;
- separately measure whether the ~14k review-enrichment candidate gate can be reduced using earlier checks or durable known metadata;
- prefer bounded/offline comparisons and limited Steam queries rather than repeated full production crawls.

Important:
- measurement/recommendation first;
- no production implementation until separate user/Director authorization after measurements;
- do not change canonical price/discount/tag/review selection rules just to improve speed.

Expected measurement report:
`reviews/worker_reports/steam-server-side-prefilter-optimization-01.md`

Expected measurement status:
- `measurement_complete_safe_optimization_found`
- `measurement_complete_no_safe_material_reduction_found`
- or `blocked_requires_followup`

## ACCEPTED — Steam partial publish + failure isolation implementation
Task:
`WORKER_TASK_STEAM_PARTIAL_PUBLISH_FAILURE_QUEUE_01.md`

Task ID:
`steam-partial-publish-failure-queue-01`

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
