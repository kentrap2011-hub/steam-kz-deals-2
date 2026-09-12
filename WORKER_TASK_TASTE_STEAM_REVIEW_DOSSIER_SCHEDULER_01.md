# WORKER TASK — Taste Steam review dossier initial backfill + scheduler 01

Task ID: `taste-steam-review-dossier-scheduler-01`

Status: `authorized_corrected_ready_for_worker`

Mode: `IMPLEMENT_AND_VALIDATE`

## Goal

Before creating the recurring Scheduled Task, perform a **one-time initial backfill now** so the already-existing canonical Taste candidate/work scope does not have to wait for dossiers to be gradually created by future daily runs.

After the initial backfill is durably complete, create and validate a **separate ChatGPT Scheduled Task** whose normal responsibility is only to maintain dossier freshness for needed games: create dossiers for newly required games and refresh dossiers that are missing/stale under the existing 20-day TTL policy.

The dossier preparation mechanism itself is already implemented and validated by:
`WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PREPARER_01.md`
with durable report:
`reviews/worker_reports/taste-steam-review-dossier-preparer-01.md`

Do not redesign that mechanism unless an actual operational blocker is found.

## User intent that must not be weakened

The user does **not** want the first days of the recurring task spent slowly filling the current backlog.

Required sequence:

1. determine the complete current canonical set of games for which Taste may need a dossier from the already-existing Taste candidate/work scope;
2. prepare and durably persist dossiers for that entire current set **now**, using the implemented dossier mechanism;
3. verify that the current set is fully covered by fresh dossiers (or report an explicit blocker/remaining count if the platform genuinely prevents completion);
4. only then create the daily dossier-maintenance Scheduled Task;
5. future daily runs should normally be incremental maintenance: new-needed + missing + stale/expired refresh, not the initial bulk population.

Do not intentionally defer the current dossier backlog to future daily scheduler runs.

## Existing task that must remain unchanged

Existing Scheduled Task:
- title: `Taste Semantic Producer`
- id: `6aa032f37e688191a5c9a1a83f91c5d9`

Do not modify, replace, duplicate, disable, or delete it in this task.

## One-time initial backfill requirements

Use the canonical control-plane to identify the **entire currently relevant Taste dossier scope**. Do not substitute a hand-picked sample or only the next 10 games.

For every game in that current scope:
- reuse an already-fresh dossier if one exists;
- otherwise prepare a fresh dossier through the implemented path;
- use Steam store description and Steam user reviews, including Russian-language reviews;
- persist the compact neutral dossier through the canonical mechanism;
- do not perform personalized Taste scoring;
- do not store an unlimited raw-review archive.

The initial backfill may be checkpointed in bounded batches for durability, but the batch/checkpoint size is not a total quota. Continue through the full current scope in this worker task until either:
- the current scope is fully covered by fresh dossiers; or
- a real platform/tool/runtime blocker prevents further progress.

If a real blocker stops the run, record exactly:
- total required dossiers in the initial scope;
- fresh/reused count;
- newly generated count;
- remaining count;
- last durable checkpoint;
- concrete blocker/error.

Do not claim initial backfill complete while required current-scope dossiers remain missing or stale.

## Required recurring scheduler behavior

After successful initial backfill, create exactly one new Scheduled Task dedicated to Steam dossier maintenance.

It must:
- use the implemented dossier preparation mechanism;
- operate only on games that the canonical control-plane says need a dossier or refresh;
- create dossiers for newly required games;
- refresh missing/stale dossiers;
- reuse fresh dossiers without unnecessary re-analysis;
- use Steam store description and Steam user reviews, including Russian-language reviews;
- persist compact neutral dossiers through the existing canonical mechanism;
- respect the configurable dossier TTL (default 20 days);
- let GitHub/control-plane own deterministic stale cleanup; ChatGPT must not perform ad-hoc cleanup logic itself;
- never perform personalized Taste scoring;
- never modify the existing `Taste Semantic Producer` task;
- never continue the old Taste throughput benchmark.

The recurring task is a **maintenance task**, not the intended mechanism for the initial current backlog.

## Scheduling rule

The new dossier task must run **before** the existing `Taste Semantic Producer` with a meaningful safety gap.

Use the existing Taste task's actual configured schedule/timezone as the authority. Schedule the dossier task **2 hours before it in the same timezone**, unless the platform cannot represent that exact relationship. If a platform limitation prevents it, use the closest safe earlier daily time and document the deviation.

Do not change the existing Taste task's schedule.

The downstream control-plane must still fail/hold safely if dossier preparation is incomplete; the time gap is not a correctness guarantee.

## Prompt requirements

The recurring Scheduled Task prompt must be concise and operational. It should tell the future run to:
1. enter the repository protocol correctly;
2. use the implemented dossier preparation path rather than re-designing it;
3. process only the canonical incremental maintenance scope (new-needed / missing / stale);
4. persist results through the canonical mechanism;
5. stop cleanly if there is no work;
6. report only actionable blockers/errors rather than re-running unrelated implementation work.

Do not embed large architecture documentation into the recurring prompt if the repository already contains the canonical instructions.

## Validation

Before finalizing, verify and record:

1. the one-time initial current Taste dossier scope was determined canonically;
2. all games in that current scope have fresh dossiers, with exact required/reused/generated/remaining counts;
3. exactly one new dossier-maintenance Scheduled Task exists;
4. existing `Taste Semantic Producer` still exists unchanged with id `6aa032f37e688191a5c9a1a83f91c5d9`;
5. dossier task schedule is 2 hours earlier in the same timezone, or documented closest-safe equivalent;
6. task prompt points to the correct repository/protocol/mechanism and is incremental-maintenance oriented;
7. no second Taste producer was created;
8. no throughput limit or production Taste batch size was changed;
9. no age-priority work was started;
10. if possible without unsafe side effects, perform a safe dry/no-op validation of the recurring maintenance path after the backfill. Do not fabricate or overwrite production semantic Taste results merely to test the scheduler.

## Durable report

Write:
`reviews/worker_reports/taste-steam-review-dossier-scheduler-01.md`

Report must include:
- initial backfill scope/count;
- fresh dossiers reused;
- dossiers newly generated now;
- remaining missing/stale dossiers (must be zero for successful completion);
- durable checkpoint/provenance for the backfill;
- new Scheduled Task title and id;
- exact schedule/timezone;
- relationship to existing Taste task schedule;
- exact recurring prompt or a concise canonical representation of it;
- validation results;
- confirmation that existing Taste task was not changed;
- whether the system is ready for the next step: a new clean Taste throughput measurement.

## Allowed final statuses

- `complete_initial_backfill_and_scheduler_ready_for_clean_throughput_measurement`
- `blocked_requires_followup`
