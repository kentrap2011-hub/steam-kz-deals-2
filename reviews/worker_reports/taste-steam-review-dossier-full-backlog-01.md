# Taste Steam Review Dossier — Full Backlog

**Task:** `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_FULL_BACKLOG_01.md` + continuation `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_FULL_BACKLOG_CONTINUE_01.md`

**Branch:** `worker/taste-dossier-full-backlog-01`

**Continuation status:** `ready_for_main_integration` — implementation and focused validation are complete on the worker branch; final task status is intentionally not claimed until the verified changes reach `main` through the normal safe integration path.

## START gate and architecture preflight

The continuation started by reading `CHAT_PROTOCOL.md` from `main`, then `CHAT_CONTEXT.md`, `PROJECT_ROUTES.md`, `CURRENT_TASK.md`, the continuation/original worker tasks, the relevant ownership contract, and the focused queue/checkpoint pitfall. The architecture preflight confirmed that GitHub remains the control plane for dossier scope, ordering, checkpoint progression, persistence and completeness. ChatGPT remains a constrained semantic data-plane worker and cannot invent scope or turn checkpoint size into a quota.

The six required pre-existing commits were confirmed on `worker/taste-dossier-full-backlog-01` before continuation work:

- `66c8901745c7b953d88c20b8de69f1bf8f6549cd`
- `28a6cdae17518fb6324332517f139497b2ced450`
- `f01845137023189da20abadcec1f8e9ee4bab647`
- `131c4629c54af07a9955478af872587e87a6dcc9`
- `9f50843adae9692bf2c0386bf79ef5d88b9856c8`
- `83aa9abc2c5d9c96d979f29dee92b8bf1b2e1f5d`

The continuation handoff itself exists only on `main`, so the worker branch legitimately diverges from `main` by one handoff commit while carrying the implementation commits.

## Architecture rationale

The dossier preparation scope is the **full current eligible Taste backlog** derived by GitHub from `data/production/pre_ai/chatgpt_taste_queue.jsonl`, preserving canonical queue order and deduplicating by Steam `appid` on first eligible occurrence.

Eligibility is explicitly Taste-semantic work. Rows whose `work_required` contains at least one of:

- `evaluate_taste_fit`
- `evaluate_normalized_taste_factors`
- `resolve_grounded_negative_analysis`

are eligible for dossier preparation. Rows whose work is only `resolve_base_support_condition` or other non-Taste support work are excluded. Mixed rows remain eligible when they also contain a Taste-semantic work item.

The active Taste pin (`data/production/pre_ai/taste_active_work_unit.json`) remains deliberately **downstream-only**. It binds the exact semantic producer input and is not the total dossier-preparation scope. The exact active pin behavior was regression-protected and not changed.

This rationale is now durable in `PROJECT_DECISIONS.md` as `TASTE-004`.

## Implemented checkpoint model

Checkpoint size `10` is a durability/runtime boundary, **not** a per-run quota, daily cap, production limit or completion threshold.

GitHub now owns all of the following explicitly:

1. build the entire current required dossier set from the full eligible backlog;
2. expose only the next bounded checkpoint in `required_items[]`;
3. require an exact, ordered submission for that checkpoint;
4. atomically persist accepted dossier files;
5. immediately rebuild the work manifest from the unchanged canonical queue plus the durable dossier store;
6. expose the next checkpoint when work remains;
7. declare full backlog ready only when `remaining_required_count == 0`.

`persist_submission_and_rebuild_work(...)` also binds ingest to the exact canonical queue snapshot used to prepare the manifest. If the queue changes before ingest, the operation fails closed before persistence and requires a fresh work build.

The CLI ingest path rewrites the canonical work manifest after each successful checkpoint, so a scheduled invocation can continue through successive GitHub-prepared checkpoints. If a real platform/tool/runtime limit interrupts the invocation, already accepted checkpoints remain durable and a later invocation deterministically resumes the remaining scope.

## Cleanup and freshness

TTL remains `20` days by default and remains configurable only within the existing contract bounds.

- fresh dossier: reused without reanalysis;
- missing dossier: create required;
- stale eligible in-scope dossier: refresh required and preserved until replacement succeeds;
- stale dossier outside the full eligible dossier scope: cleanup-eligible under the existing GitHub-owned cleanup rule;
- invalid dossier: preserved fail-closed for follow-up rather than silently deleted.

Cleanup now uses the same full eligible dossier scope as work preparation, not the active checkpoint or active Taste pin.

## Worker contract

The semantic worker prompt now states explicitly that:

- current `required_items[]` is one GitHub-prepared durability checkpoint;
- normal checkpoint size `10` is not a quota;
- after successful ingest, the worker continues with the rebuilt GitHub checkpoint in the same invocation while `status=work_required`;
- normal completion requires `full_backlog_complete=true` / zero remaining work;
- a real platform/tool/runtime interruption must not be reported as completion;
- base-support-only/non-Taste rows are outside dossier scope;
- submissions bind to `scope_sha256`, `scope_source` and `source_queue_sha256` and exactly cover only the current checkpoint.

## Validation

Focused regression command:

`PYTHONPATH=scripts python -m unittest -v test_taste_steam_review_dossier test_taste_steam_review_dossier_cleanup`

Result: **22/22 passed**.

Coverage includes the required continuation matrix:

- backlog larger than 10 and larger than 100;
- deterministic sequential progression `25 → 10 → 10 → 5 → READY`;
- partial durable progress/resume from the first remaining appid;
- final remainder smaller than checkpoint size;
- READY only after the entire required backlog is exhausted;
- exact checkpoint submission fail-closed, with partial checkpoint rejected before persistence;
- canonical queue snapshot change fail-closed before persistence;
- fresh reuse, stale refresh, missing create;
- deterministic appid dedupe and canonical order;
- unchanged exact active semantic 10-pin behavior and fail-closed semantic input;
- exclusion of base-support-only and other non-Taste-only rows;
- stale base-support-only dossier treated as out-of-scope for cleanup;
- adaptive review ceilings, Russian lane, raw-review/personalized-content guards retained.

A separate CLI smoke used 12 synthetic eligible rows and the actual builder/ingest command paths:

- initial build: `remaining_required_count=12`, current checkpoint `10`;
- first ingest: persisted `10`, manifest automatically rebuilt to checkpoint `2`;
- second ingest: persisted `2`, `remaining_required_count=0`, `full_backlog_complete=true`;
- final manifest: `ready_from_fresh_cache`; exactly 12 dossier files were durable.

No real production dossier backlog, Steam review population, Scheduled Task `Run now`, throughput benchmark or production semantic generation was executed during this continuation.

## Explicitly unchanged

- existing `Taste Steam Review Dossier` Scheduled Task was not modified or triggered;
- existing Taste Semantic Producer was not modified or triggered;
- active Taste pin authority was not changed;
- no second scheduler/producer was created;
- no age-priority rule was introduced;
- no new production quota/limit was introduced;
- no real dossier backlog was populated by this worker.

## Integration gate

The worker branch implementation is validated and ready for a normal pull-request integration into `main`. Per the continuation task, this report must be updated to the final continuation status only after that safe integration succeeds. The next user action after successful `main` integration will be the requested fresh manual `Run now` validation of the existing `Taste Steam Review Dossier` Scheduled Task.
