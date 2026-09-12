# DIRECTOR TASK BOARD

## Current rules
- Keep at most two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots.
- No autonomous IMPLEMENT without separate user approval.
- Reconcile Board -> exact task -> exact durable report before assigning follow-up work.
- Proactive gap detection follows `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`; the user is not the project's monitoring layer.
- Current priority is operational speed. Architecture review may run in parallel only when read-only and non-blocking.

## ACTIVE — normal ChatGPT/Taste mechanism + throughput measurement
Task:
`WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md`

Task ID:
`taste-normal-semantic-producer-01`

Status:
`corrected_ready_to_resume_chat_1_throughput_measurement`

Mode:
`IMPLEMENT_AND_MEASURE_THROUGHPUT`

Worker slot:
`ЧАТ 1`

Worker context:
- continue in the current Taste working chat named `ЧАТ 1`; do not restart from a new chat;
- the previous `blocked_requires_followup` conclusion was caused by an incorrect task coupling between normal producer work and the separate age-priority task;
- that age-priority dependency is now removed from the active task;
- the current active/pinned 10-item state is not, by itself, a reason to stop the normal mechanism/throughput task;
- `CHAT_PROTOCOL.md` task-first execution rules remain mandatory;
- the worker must reread the corrected `WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md` from `main` and continue from the current chat context.

Goal:
- prepare the working normal Taste semantic-processing mechanism;
- then perform a real throughput measurement in the same uninterrupted `ЧАТ 1` working run;
- measure in durable checkpoints of 10 real games: 10 processed+saved, then next 10, then next 10, continuing until a genuine execution/context/tool/canonical limit is reached;
- `10` is only the measurement/checkpoint step size, NOT the future Scheduled Task limit and NOT a permanent per-invocation ceiling;
- after every completed 10-game checkpoint, durably save/accept the work and update the worker report so already completed work is not lost;
- the factual measurement result is the cumulative number of real game evaluations durably accepted in that single measurement run;
- preserve accepted historical Taste results and provenance;
- keep retry/result ingest durable and idempotent;
- use only short deterministic tests before the real measurement;
- do not implement or test age-priority sorting in this task;
- use the current canonical queue/order unchanged during measurement;
- do not create a second Scheduled Task;
- do not change existing Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` during this task;
- do not choose or install the final production limit after the measurement.

After measurement:
- Director must first report to the user how many games were actually processed and durably accepted;
- report where/why the run stopped if it stopped on a limit/blocker;
- report how stable the completed checkpoints were, including retries/errors;
- then separately ask/decide with the user what safe production limit to use;
- the chosen production limit may intentionally be lower than the measured maximum;
- only after a separate user decision may the existing `Taste Semantic Producer` Scheduled Task be reconfigured.

Expected report:
`reviews/worker_reports/taste-normal-semantic-producer-01.md`

Expected final status:
- `complete_throughput_measured_ready_for_user_limit_decision`
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
`deferred_separate_do_not_block_throughput_measurement`

This is a separate later task and is not part of the current throughput measurement.

Required ordering when separately authorized later:
1. never successfully canonically Taste-checked;
2. then previously checked from oldest successful canonical Taste evaluation to newest.

Do not invoke, implement, or use this task as a blocker for the current `ЧАТ 1` throughput measurement.

## Proactive Project Auditor — standing role
Protocol:
`PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`

## Normal Scheduled Task — still NOT normal producer
Existing task:
- title `Taste Semantic Producer`;
- id `6aa032f37e688191a5c9a1a83f91c5d9`;
- current prompt is still the old Chernobylite one-game canary prompt.

Keep the stale canary safely DAILY 01:00 Europe/Samara during the mechanism implementation and throughput measurement.

After the measurement, do NOT automatically switch the Scheduled Task to the measured maximum and do NOT automatically carry over the 10-game measurement step as its production limit.

First report the measurement result to the user and obtain a separate decision on the safe production limit. Only then may the existing Scheduled Task be reconfigured. Never create a second task.

## Other queued work
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued.
- `WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.
