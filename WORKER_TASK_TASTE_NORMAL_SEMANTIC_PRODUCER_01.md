# TASK — taste-normal-semantic-producer-01

Status: `authorized_corrected_resume_chat_1`
Mode: `IMPLEMENT_AND_MEASURE_THROUGHPUT`

## Goal

Prepare the working normal ChatGPT/Taste semantic-processing mechanism, then perform a real throughput measurement in the current `ЧАТ 1` working run.

The purpose of this task is to measure how many games ChatGPT can actually evaluate and durably save in one uninterrupted working run.

This task does **not** choose the final production limit for the Scheduled Task.

## Critical distinction: measurement step vs production limit

For the throughput measurement, work in sequential steps of exactly `10` games:

`10 processed + durably saved` → `next 10 processed + durably saved` → `next 10` → continue until a real execution/blocking limit is reached.

`10` is only the **measurement/checkpoint step size**.

It is NOT:
- the future Scheduled Task limit;
- a permanent per-invocation limit;
- proof that production should use 10;
- a production configuration decision.

Do not hardcode the future normal producer around a permanent 10-game production ceiling merely because the measurement uses 10-game checkpoints.

## Separate deferred task: queue age-priority ordering

Do **not** implement, test, or depend on age-priority ordering in this task.

The rules:
- never successfully checked first;
- then previously checked from oldest successful canonical Taste evaluation to newest;

belong only to the separate deferred task:
`WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md`.

That task must not block this throughput measurement.

For this task, use the current canonical queue/order exactly as it already exists. Do not redesign or reorder it.

## Existing Scheduled Task

There is already one ChatGPT Scheduled Task for this producer:
- title: `Taste Semantic Producer`;
- id: `6aa032f37e688191a5c9a1a83f91c5d9`;
- current state: old Chernobylite one-game canary prompt;
- current cadence: daily at 01:00 Europe/Samara.

Do NOT create a second producer.
Do NOT change this Scheduled Task yourself.
Do NOT switch its prompt, cadence, or production limit as part of this task.

After the measurement, the Director must first report the measured result to the user. The final production limit will be chosen separately with the user and may intentionally be lower than the measured maximum.

## Phase A — prepare the working normal Taste mechanism

Read only the exact existing Taste protocols/state/result-ingest contracts needed for this task.

Implement the smallest reliable mechanism needed so that ChatGPT can:
- obtain the next canonical Taste work from existing repository state;
- evaluate real games using the established Taste profile/context contract;
- persist results through the established durable repository handoff/ingest path;
- preserve accepted historical Taste results and provenance;
- retry safely without duplicate canonical evaluations;
- continue from one completed measurement step to the next without losing already accepted work.

The mechanism must not be hardcoded to Chernobylite or any single game.

No paid OpenAI API, Copilot, new paid service, external scheduler, or second ChatGPT producer.

Do not broaden into unrelated Taste redesign.

## Phase A verification

Before the real measurement, use only short deterministic tests sufficient to prove the mechanism is safe to exercise.

At minimum prove:
- current canonical work selection is deterministic under the existing ordering rules;
- result persistence/ingest is durable;
- retries do not create duplicate accepted canonical results;
- accepted historical Taste results/provenance are preserved;
- the mechanism is not hardcoded to one game;
- a completed measurement checkpoint can be followed by another checkpoint in the same working run.

Do NOT add age-priority sorting tests here.

## Phase B — real throughput measurement

After Phase A is ready, immediately run the real measurement in this same `ЧАТ 1` working execution.

Rules:
1. Process the next `10` real games using the current canonical queue/order.
2. Persist those results through the established durable result/ingest path.
3. Verify that the completed results are durably accepted before counting the checkpoint as complete.
4. Update the durable worker report with the cumulative confirmed count after every completed 10-game checkpoint.
5. Without asking the user to continue, take the next `10` real games and repeat.
6. Continue 10-by-10 in the same uninterrupted working run until ChatGPT reaches a real execution/context/tool/canonical blocker or other genuine limit.
7. Do not intentionally stop merely because 10, 20, 30, 50, 100, or another round number was reached.
8. Do not treat an evaluated-but-not-durably-accepted partial checkpoint as completed throughput. Record partial/incomplete work separately if relevant.
9. Do not change queue age-priority behavior during the measurement.
10. Do not change the Scheduled Task during or after the measurement.

The confirmed throughput result is the number of real game evaluations durably accepted during this single corrected measurement run.

If the run stops because of a real limit, record the concrete reason when known. If execution is cut off before a clean closeout, the latest durable 10-game checkpoint remains the confirmed lower-bound result and must not be inflated by unsaved/uncertain work.

A later user/Director continuation is not automatically added to the same throughput measurement unless explicitly designated as a new measurement run.

## Durable report

Update:
`reviews/worker_reports/taste-normal-semantic-producer-01.md`

The prior `blocked_requires_followup` conclusion based on age-priority/current-active-10 gating is superseded by this corrected task and is not a blocker for the throughput measurement.

The report must include:
- files changed for the normal mechanism;
- canonical queue/state and result persistence/ingest path actually used;
- short deterministic verification performed before measurement;
- a checkpoint log after every completed 10 real games;
- cumulative count of durably accepted games;
- retries/errors/blockers encountered;
- where and why the measurement stopped;
- whether the run was stable across completed checkpoints;
- the measured factual throughput result;
- proof that no age-priority sorting implementation was performed;
- proof that no second producer/scheduler was created;
- proof that Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` was not changed;
- an explicit statement that the measured maximum is **not** automatically the production limit.

Do NOT select or install the final production limit in this report.
Do NOT activate the normal Scheduled Task in this task.

Final status exactly one of:
- `complete_throughput_measured_ready_for_user_limit_decision`
- `blocked_requires_followup`
