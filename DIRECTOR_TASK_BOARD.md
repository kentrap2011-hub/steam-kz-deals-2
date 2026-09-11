# DIRECTOR TASK BOARD

## Current rules
- Keep at most two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots.
- No autonomous IMPLEMENT without separate user approval.
- Reconcile Board -> exact task -> exact durable report before assigning follow-up work.
- Proactive gap detection follows `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`; the user is not the project's monitoring layer.
- Current priority is operational speed. Architecture review may run in parallel only when read-only and non-blocking.

## IN PROGRESS — real Steam partial-publish production refresh
Task:
`WORKER_TASK_STEAM_PARTIAL_PUBLISH_PRODUCTION_REFRESH_01.md`

Task ID:
`steam-partial-publish-production-refresh-01`

Status:
`authorized_dispatched_chat_1`

Worker slot:
`ЧАТ 1`

User authorization:
- explicit authorization granted for the real Steam production refresh.

Required work:
- safely integrate accepted worker branch `worker/steam-partial-publish-failure-queue-01` into current `main` without losing intervening Director/task files;
- canonical workflow uses `scripts/steam_partial_publish_runner.py`;
- allow/trigger the real Steam workflow;
- wait for completion and verify real production result;
- report successful processed count, unresolved problematic games, unresolved catalog segments, system-state problems, last-known-good preservation, source complete/partial status, production commit and downstream visual refresh/deploy state;
- do not automatically investigate individual problem entries.

Expected report:
`reviews/worker_reports/steam-partial-publish-production-refresh-01.md`

Expected final status:
- `complete_real_steam_refresh_verified`
- `complete_with_problem_entries_for_separate_review`
- or `blocked_requires_followup`

## IN PROGRESS — read-only architecture review
Task:
`WORKER_TASK_CODE_ARCHITECT_SYSTEM_REVIEW_01.md`

Task ID:
`code-architect-system-review-01`

Status:
`authorized_dispatched_chat_2`

Worker slot:
`ЧАТ 2`

Mode:
`READ_ONLY_REVIEW`

Rules:
- run in parallel with `ЧАТ 1`;
- do not mutate code/data/workflows/main and do not interfere with production refresh;
- record exact repository snapshots reviewed because `main` may move during the analysis;
- include accepted Steam partial-publish implementation head `5556ce5c763d886a42b3c89ba69df711ba745adb` in the structural review;
- when architecture choices are genuinely uncertain, perform bounded measurements/comparisons instead of guessing;
- prioritize recommendations by benefit versus implementation cost, with operational speed as the current priority.

Expected report:
`reviews/worker_reports/code-architect-system-review-01.md`

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

Verified before production integration:
- partial source metadata is honest when catalog segments fail;
- corrupt failure-state is quarantined and recorded rather than silently erased;
- seven short regressions reported `7/7 PASS`;
- canonical workflow on worker branch is wired to `scripts/steam_partial_publish_runner.py`;
- no real Steam refresh was run in the implementation task.

## QUEUED LATER — ChatGPT Steam error notification watch
Task:
`WORKER_TASK_STEAM_ERROR_NOTIFICATION_WATCH_01.md`

Task ID:
`steam-error-notification-watch-01`

Status:
`queued_later_do_not_start_now`

User instruction:
- add it to the queue now;
- do NOT create or enable the scheduled task yet.

Goal when later authorized:
- separate ChatGPT scheduled check, approximately hourly;
- read the latest canonical Steam problem report from GitHub;
- stay silent when there are no unresolved problems;
- notify only when the unresolved problem set is new or changed;
- do not repeat the same unchanged alert every hour;
- do not automatically repair or investigate failures.

Dependency:
- real partial-publish production path/report must be established first.

## QUEUED LATER — decouple giveaways from Steam commercial crawl
Task:
`WORKER_TASK_GIVEAWAY_DECOUPLE_FROM_STEAM_CRAWL_01.md`

Task ID:
`giveaway-decouple-from-steam-crawl-01`

Status:
`queued_later_do_not_start_now`

User instruction:
- keep this in the queue;
- do NOT work on it now.

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

Proven remaining root cause:
- the full Steam commercial collector tried to prove exact completeness against a live, changing offset-paginated catalog;
- source membership/total can move during traversal;
- strict behavior blocked production before giveaway processing;
- the accepted partial-publish implementation is intended to remove that global blocker while preserving explicit problem reporting.

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
- all 10 original results canonically persisted unchanged under historical profile A;
- queue remained intentionally pending for current profile B.

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

The auditor should proactively catch stale canary prompts, wrong cadence, queue-order mismatches, stale design assumptions, incomplete production wiring, unnecessary reprocessing, and system defects being mistaken for normal behavior.

## Normal Scheduled Task — still NOT normal producer
Existing task:
- title `Taste Semantic Producer`
- id `6aa032f37e688191a5c9a1a83f91c5d9`
- current prompt is still the old Chernobylite one-game canary prompt.

Keep the stale canary safely DAILY 01:00 Europe/Samara until normal producer implementation is actually ready.

## Other queued work
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued.
- `WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.
