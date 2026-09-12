# ЧАТ — TASTE QUEUE AGE PRIORITY ORDERING

Task ID: `taste-queue-age-priority-order-01`
Status: `deferred_separate_do_not_block_throughput_measurement`
Mode: `IMPLEMENT_LATER_ONLY_AFTER_SEPARATE_AUTHORIZATION`

## Separation from current throughput measurement

This is a separate later task.

It is NOT part of `WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md` and must not block, alter, or be invoked by the current normal Taste throughput measurement.

During the current throughput measurement, keep the existing canonical queue/order unchanged.

Start this task only after separate Director/user authorization.

## Goal

Make future Taste work processing order follow the user's required priority:

1. games/items that have **never had a canonically accepted successful Taste semantic result**;
2. then previously checked games/items from **oldest successful canonical Taste evaluation to newest**.

The currently pinned/in-flight exact work-unit must never be reordered mid-flight. Apply the rule when constructing a later new canonical queue/work-unit after this task is separately authorized.

## Exact semantics of "checked"

A game/item counts as checked only when a Taste semantic result was successfully accepted into canonical state.

Do NOT treat as a completed check:
- merely appearing in a queue;
- semantic generation that was never accepted;
- failed or rejected ingest;
- a failed workflow attempt;
- an unconsumed inbox result.

## Ordering requirements

Canonical ordering key must behave as:
- priority class 0: no accepted successful Taste result ever;
- priority class 1: at least one accepted successful Taste result;
- within class 1: ascending last successful canonical Taste evaluation time (oldest first);
- deterministic stable tie-breaker for equal/missing-equivalent values using an existing canonical stable identity such as exact key/appid, so the queue cannot reshuffle nondeterministically.

Do not use commercial priority, price, discount, review score, wishlist status, or ChatGPT preference to break this ordering unless an existing higher-level canonical rule explicitly requires a separate hard eligibility gate before Taste ordering.

## First step — prove the timestamp source

Before changing logic, identify the existing canonical source that can reliably answer "when was this game last successfully Taste-checked?"

Preferred: an explicit semantic acceptance/evaluation timestamp already stored in canonical Taste result/cache/receipt state.

Do not silently substitute:
- source mailing timestamp;
- queue creation time;
- arbitrary Git commit time;
- failed attempt time;
- profile update time.

If there is no reliable canonical successful-evaluation timestamp, STOP implementation and report `blocked_missing_canonical_last_successful_evaluation_time` with the smallest explicit state addition needed. Do not invent an approximation.

## Preserve

- current pinned work-unit lifecycle and exact immutable bindings;
- single producer ownership;
- exact deterministic queue construction;
- existing fail-closed validation;
- no manual queue/cache mutation;
- no result regeneration as part of this task;
- no Scheduled Task cadence/prompt change here;
- no semantic throughput measurement here.

## Validation

Prove at minimum with focused tests/fixtures:
1. never-checked item sorts before any checked item;
2. among checked items, older successful evaluation sorts before newer;
3. failed/unaccepted attempt does not make an item "recently checked";
4. deterministic tie ordering is stable;
5. an already active pinned work-unit is preserved unchanged;
6. next newly constructed work-unit reflects the new ordering;
7. no unrelated business ranking changed.

## Report first

Create/update before implementation:
`reviews/worker_reports/taste-queue-age-priority-order-01.md`

Record lifecycle, UTC, exact timestamp authority found/not found, files expected to change, and next action.

## Final report

Final status must be one of:
- `complete_age_priority_ordering_implemented`
- `blocked_missing_canonical_last_successful_evaluation_time`
- `failed_closed_root_cause_proven`
- `failed_closed_root_cause_unknown`

Include exact changed files, tests, commit(s), and whether real backlog processing may resume.

Do not process any semantic games in this task. Stop after implementation/validation/report.
