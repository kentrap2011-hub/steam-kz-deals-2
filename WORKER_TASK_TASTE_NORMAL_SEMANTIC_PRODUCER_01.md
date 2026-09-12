# TASK — taste-normal-semantic-producer-01

Status: `authorized_dispatched_chat_1`
Mode: `IMPLEMENT_AND_VERIFY_READY_FOR_SCHEDULE`

## Goal

Replace the old one-game ChatGPT/Taste canary flow with the normal queue-based game-evaluation mechanism, then prove it is ready for the Director to switch the existing ChatGPT Scheduled Task to normal operation.

Current priority: get normal ChatGPT game evaluation running reliably without creating a second producer or paid external API dependency.

## Existing Scheduled Task

There is already one ChatGPT Scheduled Task for this producer:
- title: `Taste Semantic Producer`
- id: `6aa032f37e688191a5c9a1a83f91c5d9`
- current state: old Chernobylite one-game canary prompt;
- current cadence: daily at 01:00 Europe/Samara.

Do NOT create a second producer.
Do NOT change this ChatGPT Scheduled Task yourself.
Keep it on the old safe cadence/prompt until the Director accepts this implementation and performs the final schedule/prompt switch.

## Required normal producer behavior

1. Work from the canonical Taste queue/state already present in the repository.
2. Process at most `10` games per ChatGPT invocation.
3. Exactly one deterministic work unit per invocation.
4. Queue head must be deterministic and reproducible from canonical state.
5. Before the next new semantic batch, enforce age priority:
   - first: games that have never been successfully canonically Taste-checked;
   - then: already checked games from oldest successful canonical Taste evaluation to newest.
6. Do not silently skip a queue-head item because it is inconvenient. If it cannot be evaluated, preserve/report the problem according to existing durable state conventions.
7. Preserve already accepted historical Taste results and profile provenance. Do not overwrite historical accepted results merely to simplify the new producer.
8. Result handoff/ingest must be durable and idempotent enough that one scheduled invocation cannot create duplicate canonical evaluations when retried.
9. The normal producer must be compatible with reusing the SAME Scheduled Task ID above once Director switches it to normal operation.
10. No paid OpenAI API, Copilot, new paid service, external scheduler, or second ChatGPT producer.

## Required investigation / implementation

Read only the exact existing Taste protocols/tasks/reports/state needed to establish the current canonical queue and result-ingest contract.

Implement the smallest production-ready normal queue mechanism needed so that a Scheduled Task invocation can:
- determine the canonical next work unit (max 10 games);
- obtain the exact durable game context required for semantic evaluation;
- produce results in the established canonical format/profile contract;
- hand off/persist those results through the existing repository workflow/state path;
- advance deterministically without duplicate processing.

Integrate the already queued age-priority rule from:
`WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md`
into this normal producer rather than leaving ordering ambiguous.

Do not broaden into unrelated Taste redesign.

## Tests / proof

Use short deterministic tests only.

At minimum prove:
- never-checked games sort before previously checked games;
- among previously checked games, oldest successful canonical evaluation sorts first;
- work unit never exceeds 10 games;
- same canonical state yields same queue head/work unit;
- retry/idempotency behavior does not produce duplicate canonical results;
- historical accepted Taste results/provenance are preserved;
- normal producer path is not hardcoded to Chernobylite or any single game.

Do NOT run a large real semantic production batch during implementation.
Do NOT switch the Scheduled Task yet.

## Final handoff requirement

The report must contain the exact ready-to-use instructions/prompt contract that the Director should place into the EXISTING Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` after acceptance.

It must also state the recommended normal cadence. The intended target is hourly, but if evidence shows a different cadence is required for correctness/rate limits, explain it rather than guessing.

## Durable report

Write:
`reviews/worker_reports/taste-normal-semantic-producer-01.md`

Report must include:
- files changed;
- exact canonical queue/state used;
- exact ordering implementation;
- work-unit construction and max size;
- retry/idempotency behavior;
- result persistence/ingest path;
- deterministic test commands and results;
- proof that no second producer/scheduler was created;
- proof existing Scheduled Task was not changed by the worker;
- exact prompt/instructions for the Director to put into the existing Scheduled Task;
- recommended cadence;
- any blocker before real activation.

Final status exactly one of:
- `complete_ready_for_normal_scheduled_producer`
- `blocked_requires_followup`
