# WORKER TASK — Taste Steam review dossier scheduler 01

Task ID: `taste-steam-review-dossier-scheduler-01`

Status: `authorized_ready_for_worker`

Mode: `IMPLEMENT_AND_VALIDATE`

## Goal

Create and validate a **separate ChatGPT Scheduled Task** that runs the already-implemented Steam review dossier preparation mechanism before the existing `Taste Semantic Producer`.

The dossier preparation mechanism itself is already implemented and validated by:
`WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PREPARER_01.md`
with durable report:
`reviews/worker_reports/taste-steam-review-dossier-preparer-01.md`

This task is only about operationalizing that mechanism as its own Scheduled Task and validating the handoff. Do not redesign the dossier architecture unless an actual scheduler integration blocker is found.

## Existing task that must remain unchanged

Existing Scheduled Task:
- title: `Taste Semantic Producer`
- id: `6aa032f37e688191a5c9a1a83f91c5d9`

Do not modify, replace, duplicate, disable, or delete it in this task.

## Required scheduler behavior

Create exactly one new Scheduled Task dedicated to Steam dossier preparation.

It must:
- use the implemented dossier preparation mechanism;
- operate only on games that the canonical control-plane says need a dossier or refresh;
- use Steam store description and Steam user reviews, including Russian-language reviews;
- persist compact neutral dossiers through the existing canonical mechanism;
- respect the configurable dossier TTL (default 20 days);
- let GitHub/control-plane own deterministic stale cleanup; ChatGPT must not perform ad-hoc cleanup logic itself;
- never perform personalized Taste scoring;
- never modify the existing `Taste Semantic Producer` task;
- never continue the old throughput benchmark.

## Scheduling rule

The new dossier task must run **before** the existing `Taste Semantic Producer` with a meaningful safety gap.

Use the existing Taste task's actual configured schedule/timezone as the authority. Schedule the dossier task **2 hours before it in the same timezone**, unless the platform cannot represent that exact relationship. If a platform limitation prevents it, use the closest safe earlier daily time and document the deviation.

Do not change the existing Taste task's schedule.

The downstream control-plane must still fail/hold safely if dossier preparation is incomplete; the time gap is not a correctness guarantee.

## Prompt requirements

The Scheduled Task prompt must be concise and operational. It should tell the future run to:
1. enter the repository protocol correctly;
2. use the implemented dossier preparation path rather than re-designing it;
3. process the canonical required dossier scope;
4. persist results through the canonical mechanism;
5. stop cleanly if there is no work;
6. report only actionable blockers/errors rather than re-running unrelated implementation work.

Do not embed large architecture documentation into the recurring prompt if the repository already contains the canonical instructions.

## Validation

Before finalizing, verify and record:

1. exactly one new dossier Scheduled Task exists;
2. existing `Taste Semantic Producer` still exists unchanged with id `6aa032f37e688191a5c9a1a83f91c5d9`;
3. dossier task schedule is 2 hours earlier in the same timezone, or documented closest-safe equivalent;
4. task prompt points to the correct repository/protocol/mechanism;
5. no second Taste producer was created;
6. no throughput limit or production Taste batch size was changed;
7. no age-priority work was started;
8. if possible without unsafe side effects, perform a safe dry/no-op validation of the recurring path. Do not fabricate or overwrite production semantic results merely to test the scheduler.

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
- whether the system is ready for the next step: a new clean Taste throughput measurement.

## Allowed final statuses

- `complete_scheduler_ready_for_clean_throughput_measurement`
- `blocked_requires_followup`
