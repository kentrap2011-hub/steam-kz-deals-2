# WORKER TASK — Taste Steam Review Dossier Persistence Bridge 01

## Task ID
`taste-steam-review-dossier-persistence-bridge-01`

## Mode
`IMPLEMENT`

User has explicitly authorized this fix.

## Goal
Repair the missing end-to-end production bridge between the existing scheduled ChatGPT task `Taste Steam Review Dossier` and the existing GitHub-owned dossier ingest/persistence logic.

The finished production path must allow the scheduled ChatGPT worker to submit one completed GitHub-prepared dossier checkpoint through a repository-defined runtime artifact interface that the scheduled task can actually invoke, after which GitHub validates, persists the dossier artifacts, advances the same fixed daily snapshot, and exposes the next checkpoint.

Do not replace or bypass GitHub-owned persistence/completeness logic.

## Required background
Read first:
- `CHAT_PROTOCOL.md` and perform START gate;
- `CHAT_CONTEXT.md`;
- this task file completely before broad search;
- `config/execution_ownership_contract.json`;
- relevant dossier route in `PROJECT_ROUTES.md` if present;
- `PROJECT_DECISIONS.md -> TASTE-005` when needed;
- `reviews/worker_reports/taste-steam-review-dossier-control-plane-refresh-01.md`.

Production validation after that report established the following new fact:
- current fixed daily dossier snapshot is valid and contains 591 required items;
- current durability checkpoint contains 10 items;
- `full_backlog_complete=false`;
- the scheduled ChatGPT task can read/prepare the checkpoint but cannot execute `scripts/ingest_taste_steam_review_dossiers.py` because its connected GitHub surface exposes neither arbitrary command execution nor a usable workflow-dispatch action;
- no partial write was made, so the same snapshot/checkpoint remains authoritative;
- existing `ingest-taste-batch.yml` belongs to Taste Semantic Producer and must not be reused or modified for dossier ingestion.

## Architecture preflight — mandatory before writes
Explicitly answer and record in the report:
1. Which component owns checkpoint validation, canonical dossier persistence, snapshot advancement and completeness? Expected authority is GitHub/GitHub Actions under `config/execution_ownership_contract.json`.
2. Which exact repository-defined submission primitive can the existing scheduled ChatGPT task actually invoke with its available GitHub connection?
3. Does the proposed bridge keep ChatGPT limited to submitting structured checkpoint results rather than directly editing canonical dossier store/snapshot state?
4. Does the design avoid creating a second recurring producer, independent queue, retry loop, quota, backlog manager or duplicate completeness authority?

If ownership or the callable submission primitive is not provable, stop implementation and finish as `needs_user_decision` or `blocked` with the exact missing fact. Do not invent a bridge that the real Scheduled Task cannot call.

## Required implementation outcome
Implement the smallest GitHub-owned bridge that makes this real chain possible:

`fixed daily snapshot -> scheduled ChatGPT processes exact current_checkpoint_items -> scheduled ChatGPT submits structured checkpoint artifact through an actually available GitHub action -> GitHub validates and calls canonical dossier ingest/persistence -> same snapshot advances -> next checkpoint becomes available`

Requirements:
- reuse `scripts/ingest_taste_steam_review_dossiers.py` / its canonical persistence logic rather than duplicating merge/completeness logic;
- ChatGPT must not directly write canonical dossier files or directly mutate `taste_steam_review_dossier_work.json` as the persistence mechanism;
- the submission must be bound to the exact current `snapshot_id`, checkpoint binding/provenance and exact expected appids;
- invalid, stale, partial, mismatched or replayed submissions must fail closed;
- accepted submission must atomically preserve the invariant: dossier artifacts and snapshot advancement agree;
- accepted checkpoint must advance within the same prepared snapshot, without rebuilding scope from the current queue/store;
- after checkpoint acceptance the next scheduled-task invocation (or the same invocation if the available interface permits a safe reload) must be able to read the advanced same-snapshot state;
- checkpoint size 10 remains only a durability boundary, not a production quota;
- current 591-item snapshot must remain authoritative; do not regenerate it merely to implement the bridge;
- do not process the real 591-item backlog during implementation.

A repository inbox/artifact + GitHub-owned event-driven ingest route is acceptable if it is the smallest design and is actually callable by the scheduled ChatGPT task. A workflow-dispatch-only solution is not acceptable unless the worker proves that the production Scheduled Task has that dispatch capability.

## Boundaries / do not change
- Do not modify `Taste Semantic Producer` prompt, schedule, limits, queue, state or `ingest-taste-batch.yml` semantics.
- Do not create a second dossier Scheduled Task.
- Do not turn the interactive worker chat into the production executor/backlog manager.
- Do not change the fixed daily full-snapshot model from TASTE-005.
- Do not change daily dossier scope/order/dedupe/TTL except where strictly required for the submission binding itself.
- Do not reinterpret checkpoint 10 as a quota.
- Do not manually write dossier artifacts or snapshot progress to make acceptance pass.
- Do not run real production `Run now` as part of this implementation task; reserve that for post-merge user validation after Director review.

## Acceptance checks
Prove, with focused deterministic tests plus a GitHub-hosted integration/acceptance route where needed, all of the following:

1. The exact submission action available to scheduled ChatGPT is identified and exercised in acceptance; the test must not rely on an unavailable shell or unavailable workflow-dispatch action.
2. A prepared checkpoint of 10 structured dossier results submitted through that interface reaches GitHub-owned ingest and persists all 10 while advancing the same `snapshot_id` to the next checkpoint.
3. A 25-item synthetic fixed snapshot can progress `10 -> 10 -> 5 -> 0` through the bridge without rebuilding scope.
4. Restart/resume after an accepted checkpoint does not repeat already accepted items.
5. Partial checkpoint submission fails closed and does not advance snapshot state.
6. Wrong `snapshot_id`, wrong checkpoint binding, wrong/missing appid, stale/replayed submission and invalid dossier contract fail closed.
7. A failed later checkpoint preserves earlier accepted durable progress.
8. No direct ChatGPT edit to canonical dossier store/snapshot is required for acceptance.
9. No modification to `Taste Semantic Producer` behavior/schedule/limits occurs.
10. The implementation reaches `main` and the final durable report is also present in `main` before the worker reports completion.

Do not claim production readiness solely from unit tests. The acceptance must prove the actual bridge shape and callable GitHub submission route that the scheduled task will use.

## Current task handling
Update `CURRENT_TASK.md` only as required by `CHAT_PROTOCOL.md`, without deleting or overwriting unrelated active work. On completion, leave this task in a correct closed/handed-off state.

## Durable report
Write and merge to `main`:

`reviews/worker_reports/taste-steam-review-dossier-persistence-bridge-01.md`

The report must be compact and include:
- Task;
- architecture-preflight answers;
- Verified facts;
- exact callable submission interface used by Scheduled ChatGPT;
- Changes;
- Validation;
- Unresolved;
- Status;
- exact PR/commit/run/job refs;
- Recommended next step;
- Efficiency / reusable lesson.

Do not present the task as ready for Director acceptance while this report exists only on a worker branch.

## Allowed final statuses
- `complete_ready_for_user_run_now_validation`
- `needs_user_decision`
- `blocked`

## Expected next step after successful completion
Director reads the durable report from `main`. If accepted, user manually runs the existing `Taste Steam Review Dossier` Scheduled Task once. Production validation must demonstrate that at least one real checkpoint is canonically persisted and the fixed snapshot advances before the dossier production path is considered end-to-end repaired.
