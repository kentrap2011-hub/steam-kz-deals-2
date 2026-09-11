# DIRECTOR TASK BOARD

## Current rules
- Keep at most two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots.
- No autonomous IMPLEMENT without separate user approval.
- Reconcile Board -> exact task -> exact durable report before assigning follow-up work.
- Proactive gap detection follows `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`; the user is not the project's monitoring layer.

## NEEDS FOLLOW-UP — Steam partial publish + failure isolation
Task:
`WORKER_TASK_STEAM_PARTIAL_PUBLISH_FAILURE_QUEUE_01.md`

Task ID:
`steam-partial-publish-failure-queue-01`

Worker slot:
`ЧАТ 1`

Review status:
`needs_followup_before_acceptance`

Worker branch:
`worker/steam-partial-publish-failure-queue-01`

Worker head:
`43df55f5041d4eb6b4022bbc9482f6159cd4bd36`

Observed implementation:
- branch is 3 commits ahead of main;
- added `scripts/steam_partial_publish.py`;
- added `scripts/steam_partial_publish_runner.py`;
- added `scripts/test_steam_partial_publish.py` with five short regression tests.

Director acceptance gaps:
1. required durable report `reviews/worker_reports/steam-partial-publish-failure-queue-01.md` is missing;
2. no durable evidence was found that the five tests were actually executed and passed;
3. implementation writes `complete: true` / `source_complete: true` even when failed catalog segments are recorded, which is contradictory to known partial source coverage and must not falsely claim full completeness;
4. failure-queue loader currently resets to empty state on malformed/unreadable JSON, which can silently lose unresolved failures; a corrupt file must not remain the active source and must not be overwritten as if nothing happened;
5. changes are still only on the worker branch, not accepted/integrated into main;
6. before acceptance, worker must prove the actual production invocation path will use the new partial-publish runner/rules rather than the old strict path.

Do NOT run the real Steam refresh yet.
Continue in the SAME `ЧАТ 1`; do not start a new worker slot for these follow-up fixes.

Required behavior remains:
- process the Steam catalog once;
- publish successfully processed games without waiting for failed/problematic games;
- keep last known good data for already-known failed games;
- record failed/unread catalog segments separately;
- count drift is informational;
- unresolved problems must not silently disappear;
- short deterministic tests only before real refresh.

Expected final report:
`reviews/worker_reports/steam-partial-publish-failure-queue-01.md`

Expected final status:
- `complete_ready_for_real_steam_refresh`
- or `blocked_requires_followup`

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
- implement and verify `steam-partial-publish-failure-queue-01` first so the exact canonical report path/schema is known.

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
- the full Steam commercial collector tries to prove exact completeness against a live, changing offset-paginated catalog;
- source membership/total can move during the traversal;
- the strict collector therefore fails before giveaway production runs;
- current site still has the previous 115 ordinary games and stale/missing current giveaways.

The old `visual_source_history_mismatch` defect was repaired; latest no-build reason became `upstream_prerequisite_not_ready` because Steam production failed earlier.

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

## DEFERRED — Taste queue age-priority ordering
Task:
`WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md`

Report:
`reviews/worker_reports/taste-queue-age-priority-order-01.md`

Status:
`queued_before_next_new_semantic_batch`

Required ordering for newly constructed Taste work:
1. never successfully canonically Taste-checked;
2. then previously checked from oldest successful canonical Taste evaluation to newest.

Rules:
- failed/rejected/unaccepted attempts do not count as a check;
- deterministic stable tie-breaker;
- do not invent a timestamp source;
- do not silently mutate an already active exact pin.

## After ordering — resume real backlog drain
Resume bounded real Taste semantic processing from canonical state. Process actual games, checkpoint accepted batches, and continue until genuine blocker/safe stop/practical execution limit. Do not mistake infrastructure defects for semantic capacity.

## Proactive Project Auditor — standing role
Protocol:
`PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`

The auditor should proactively catch stale canary prompts, wrong cadence, queue-order mismatches, stale design assumptions, incomplete production wiring, unnecessary reprocessing, and system defects being mistaken for normal behavior.

## Code Architect — standing role
Protocol:
`CODE_ARCHITECT_ROLE.md`

Status:
`standing_read_only_role`

Purpose:
- review code/repository structure for unnecessary complexity, monolithic files, duplicated paths, weak module boundaries, poor navigation, and avoidable layers;
- recommend splitting by responsibility when useful, not by arbitrary line count;
- recommend clear section anchors/headings for intentionally large cohesive files;
- do not implement refactors without separate user authorization;
- use a free reusable `ЧАТ 1` or `ЧАТ 2` slot when activated rather than becoming a permanent third implementation worker.

Immediate review target:
- before accepting the current Steam partial-publish implementation, assess whether the new 425-line runner is the simplest safe structure, whether it duplicates the existing production path, and what should be integrated/split/anchored instead.

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
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued.

`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.
