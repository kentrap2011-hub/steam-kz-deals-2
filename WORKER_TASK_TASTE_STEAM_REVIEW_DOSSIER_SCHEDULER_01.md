# WORKER TASK — Taste Steam review dossier scheduler 01

Task ID: `taste-steam-review-dossier-scheduler-01`

Status: `authorized_corrected_ready_for_worker`

Mode: `IMPLEMENT_AND_VALIDATE`

## Goal

Create and validate one separate ChatGPT Scheduled Task for the already-implemented Steam review dossier mechanism.

Do **not** perform a separate one-time backfill path before creating the task. The user will use the Scheduled Task's own **Run now / Выполнить сейчас** action for the initial production run. That first manual run is intentionally also the end-to-end validation of the exact mechanism that will later run every day.

The dossier preparation mechanism itself is already implemented and validated by:
`WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PREPARER_01.md`
with durable report:
`reviews/worker_reports/taste-steam-review-dossier-preparer-01.md`

Do not redesign that mechanism unless an actual scheduler integration blocker is found.

## User intent that must not be weakened

There must be only one production path for dossier generation: the Scheduled Task itself.

Required sequence:
1. create the recurring dossier Scheduled Task;
2. validate its configuration and handoff without independently generating the production backlog in the worker chat;
3. leave it ready for the user to press **Run now / Выполнить сейчас**;
4. that first manual run must use the exact same prompt/path as future daily runs and process the current canonical missing/stale dossier scope;
5. future automatic daily runs use the same mechanism to maintain freshness: newly needed games, missing dossiers, and stale dossiers after TTL expiry.

Do not create a special backfill-only implementation that differs from the recurring path.

## Existing task that must remain unchanged

Existing Scheduled Task:
- title: `Taste Semantic Producer`
- id: `6aa032f37e688191a5c9a1a83f91c5d9`

Do not modify, replace, duplicate, disable, or delete it in this task.

## Required recurring scheduler behavior

Create exactly one new Scheduled Task dedicated to Steam dossier preparation/maintenance.

Every run, including the first manual `Run now`, must:
- enter the repository protocol correctly;
- use the already-implemented canonical dossier preparation path;
- ask the canonical control-plane for the **entire currently required dossier work scope** for that run, not a hand-picked sample and not only the next Taste batch;
- reuse fresh dossiers without unnecessary re-analysis;
- create missing dossiers;
- refresh stale/expired dossiers;
- use Steam store description and Steam user reviews, including Russian-language reviews;
- persist compact neutral dossiers through the canonical mechanism;
- checkpoint progress durably as needed;
- continue through the current required scope until it is exhausted or a real platform/tool/runtime limit prevents further work;
- if interrupted by a real limit, preserve completed checkpoints so the next run resumes the remaining canonical work rather than repeating completed work;
- respect the configurable dossier TTL (default 20 days);
- let GitHub/control-plane own deterministic stale cleanup; ChatGPT must not perform ad-hoc cleanup logic itself;
- never perform personalized Taste scoring;
- never modify the existing `Taste Semantic Producer` task;
- never continue the old Taste throughput benchmark.

The first `Run now` is expected to be larger because it may contain the current backlog. Later daily runs should normally be incremental maintenance using the same exact production path.

## Scheduling rule

The new dossier task must run **before** the existing `Taste Semantic Producer` with a meaningful safety gap.

Use the existing Taste task's actual configured schedule/timezone as the authority. Schedule the dossier task **2 hours before it in the same timezone**, unless the platform cannot represent that exact relationship. If a platform limitation prevents it, use the closest safe earlier daily time and document the deviation.

Do not change the existing Taste task's schedule.

The downstream control-plane must still fail/hold safely if dossier preparation is incomplete; the time gap is not a correctness guarantee.

## Prompt requirements

The recurring Scheduled Task prompt must be concise and operational. It must tell every future run, including manual `Run now`, to:
1. enter the repository protocol correctly;
2. use the implemented dossier preparation path rather than re-designing it;
3. determine the complete canonical required dossier scope for that run;
4. process all missing/stale work in that scope, reusing fresh dossiers;
5. checkpoint/persist results through the canonical mechanism;
6. stop cleanly if there is no work;
7. if a real runtime/tool limit is reached, leave completed work durable and report the remaining count/blocker so the next run can continue;
8. report only actionable blockers/errors rather than re-running unrelated implementation work.

Do not embed large architecture documentation into the recurring prompt if the repository already contains the canonical instructions.

## Validation in this worker task

Before finalizing, verify and record:
1. exactly one new dossier Scheduled Task exists;
2. existing `Taste Semantic Producer` still exists unchanged with id `6aa032f37e688191a5c9a1a83f91c5d9`;
3. dossier task schedule is 2 hours earlier in the same timezone, or documented closest-safe equivalent;
4. task prompt points to the correct repository/protocol/mechanism;
5. the prompt clearly makes `Run now` and future daily runs use the same canonical production path;
6. the prompt requests the whole currently required missing/stale scope for each run rather than a fixed small sample;
7. durable checkpoint/resume behavior is preserved if a run hits a real runtime/tool limit;
8. no second Taste producer was created;
9. no throughput limit or production Taste batch size was changed;
10. no age-priority work was started;
11. do not independently execute the production dossier backlog in this worker task merely to simulate `Run now`; the user will trigger the actual task after creation.

## Durable report

Write:
`reviews/worker_reports/taste-steam-review-dossier-scheduler-01.md`

Report must include:
- new Scheduled Task title and id;
- exact schedule/timezone;
- relationship to existing Taste task schedule;
- exact recurring prompt or a concise canonical representation of it;
- validation results;
- confirmation that existing Taste task was not changed;
- explicit confirmation that initial population will be performed by the task's own `Run now` action, not a separate worker-only backfill path;
- instructions/expected evidence for evaluating the first manual run: total required at run start, reused fresh, newly generated/refreshed, remaining at run end, last durable checkpoint, and any concrete blocker;
- whether the scheduler is ready for the user to press `Run now`.

## Allowed final statuses

- `complete_scheduler_ready_for_user_run_now_validation`
- `blocked_requires_followup`
