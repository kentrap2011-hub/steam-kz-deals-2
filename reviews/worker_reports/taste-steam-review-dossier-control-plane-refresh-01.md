# Taste Steam Review Dossier Control-Plane Refresh 01

## Status

`complete_ready_for_user_run_now_validation`

## Task authority

Implemented `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_CONTROL_PLANE_REFRESH_01.md` as the authoritative task. `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_DAILY_SNAPSHOT_CONTRACT_01.md` was not executed and is treated as superseded for this work, per the user correction.

## Old defect

The prior production model exposed only a bounded checkpoint and then used `persist checkpoint -> rebuild current scope from current queue/store`. A manual `Run now` could therefore see a stale `ready_from_fresh_cache` work manifest that had been prepared before later queue/state changes. The semantic worker correctly refused to invent scope, so that invocation could process zero even though current eligible Taste work later existed.

The defect was control-plane scope publication, not semantic-worker willingness. The fix is not to let ChatGPT discover or refresh work on demand; GitHub must publish the complete daily scope in advance.

## Actual daily preparation route

The production route is the existing GitHub workflow:

- workflow name: `Build pre-AI deterministic payload`;
- workflow file: `.github/workflows/build-pre-ai-store-snapshot.yml`;
- canonical Taste source: `data/production/pre_ai/chatgpt_taste_queue.jsonl`;
- queue is built by `Build split ChatGPT consumer bundle`;
- immediately after that, `Prepare fixed daily full Steam review dossier backlog` runs `python scripts/build_taste_steam_review_dossier_work.py`;
- `data/production/pre_ai/taste_steam_review_dossier_work.json` is added to the same atomic pre-AI commit before external semantic consumption.

No unrelated recurring GitHub workflow was created. Dossier-store checkpoint persistence is deliberately not a trigger for this pre-AI workflow, so persisting a checkpoint cannot silently rebuild the daily scope.

## Full-day manifest/state model

Canonical contract is now `TASTE-STEAM-REVIEW-DOSSIER-CONTRACT-V2`; work manifest is `TASTE-STEAM-REVIEW-DOSSIER-WORK-V2`.

One daily preparation reads the current canonical eligible Taste queue once, excludes non-Taste/base-support-only rows, deduplicates by `appid` in first canonical queue occurrence order, reuses fresh dossiers, and places every missing/stale/invalid eligible dossier in one immutable `prepared_required_items[]` list.

Immutable snapshot identity/provenance includes `snapshot_id`, Samara `prepared_for_date`, source queue path/hash, eligible-scope binding and the full prepared-required binding. Mutable progress is separate: `remaining_required_items`, completed count, `current_checkpoint_items`, current checkpoint binding and `full_backlog_complete`.

An empty prepared backlog is a valid complete daily snapshot. Default dossier TTL remains 20 days.

## Checkpoint, persistence and resume

`checkpoint_size=10` is only an internal durability boundary. It is not a run quota, daily quota, production limit or total scope limit.

The semantic worker may process only the exact GitHub-owned `current_checkpoint_items[]`. On accepted ingest, `scripts/ingest_taste_steam_review_dossiers.py` no longer reads the canonical queue and no longer rebuilds work from current queue/store. It validates the complete current checkpoint, persists its dossiers, and advances only `remaining_required_items` inside the same `snapshot_id`.

A 25-item prepared snapshot therefore progresses 10 -> 10 -> 5 -> 0 without rebuilding scope. If execution stops after 10 or 20 accepted items, the next invocation resumes the remaining prefix of the same snapshot and does not redo accepted checkpoints. An invalid later checkpoint is rejected without discarding earlier durable progress. Completion is true only when the same snapshot reaches `remaining_required_count=0`.

Queue changes after daily preparation cannot mutate the current snapshot through ingest; they enter scope at the next daily preparation.

## Manual Run now behavior

Manual `Run now` consumes the most recent already-prepared daily snapshot exactly as published/progressed. It does not refresh GitHub scope on demand. If the latest prepared snapshot is complete/empty, the invocation is a no-op. If it has remaining work, it resumes that same snapshot.

This implementation did not press `Run now` and did not execute the real production backlog. That final behavior remains intentionally reserved for user validation after Director review.

## Scheduled Task prompt and Taste Semantic Producer

Scheduled Task object prompt change: **none**. No automation create/update call was performed and no new recurring ChatGPT task was created.

The canonical repository worker contract `config/taste_steam_review_dossier_worker_prompt.md` was updated from V1 checkpoint->rebuild wording to V2 fixed-daily-snapshot wording: read the latest prepared V2 snapshot, process only `current_checkpoint_items[]`, bind submissions to `snapshot_id` plus current scope/provenance, reload the advanced same snapshot after ingest, continue successive durability checkpoints, and never perform on-demand scope refresh.

The existing `Taste Semantic Producer`, its scheduling/limits, and active Taste pin authority were not modified. `scripts/build_taste_semantic_dossier_input.py` still builds fail-closed semantic input from the exact active pin; only its dossier-contract loader moved to V2.

## Ownership split

GitHub remains the control plane and owns daily full scope selection, deterministic order/deduplication, fresh/stale decision at preparation time, snapshot publication, checkpoint boundary, validation, durable persistence, same-snapshot progress and completeness.

Scheduled ChatGPT remains a constrained semantic data-plane worker: it inspects Steam Store/review evidence only for the exact current checkpoint supplied by GitHub and returns neutral dossier submissions. It does not own queue selection, retry/completeness policy, checkpoint quota, ordering or downstream Taste decisions.

## Files changed

Implementation PR #18 changed:

- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `PROJECT_DECISIONS.md` (`TASTE-005`, explicitly superseding only the checkpoint-rebuild portion of `TASTE-004`)
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `scripts/build_taste_semantic_dossier_input.py`
- `scripts/build_taste_steam_review_dossier_work.py`
- `scripts/ingest_taste_steam_review_dossiers.py`
- `scripts/taste_steam_review_dossier_cleanup.py`
- `scripts/taste_steam_review_dossier_daily.py`
- `scripts/test_taste_steam_review_dossier_daily_snapshot.py`

No temporary validation/helper workflow remained in the merged diff.

## Deterministic acceptance and workflow smoke

Exact task-branch GitHub-hosted validation succeeded:

- Actions run: `34763260187`
- job: `103739651104`
- Python compile of all V2 control-plane entrypoints: success
- fixed daily snapshot acceptance tests: success

The acceptance suite verifies:

1. 25 missing/stale items produce one prepared manifest containing all 25.
2. Progress is 10/10/5 to complete without a queue/store scope rebuild.
3. Stop/resume uses the same snapshot and does not redo accepted items.
4. Complete is true only at zero remaining.
5. Empty snapshot is valid complete state.
6. Fresh dossiers are excluded; stale/missing are included.
7. Non-Taste/base-support-only rows are excluded.
8. Appids are deterministically deduplicated in canonical order.
9. Downstream semantic input remains exact active-pin bound.
10. A queue mutation after preparation does not mutate the saved snapshot; the next daily preparation sees it.
11. A failed later checkpoint leaves earlier progress intact.
12. Workflow ordering is `consumer bundle -> fixed daily dossier snapshot -> atomic pre-AI commit` and the manifest is part of that commit.

The local container could not clone GitHub because its network returned the exact error `Could not resolve host: github.com`; this did not block verification because the exact branch was compiled and tested successfully by GitHub Actions. The temporary branch-only validation workflow was removed before merge.

## Integration refs

- implementation PR: `#18`
- implementation merge commit: `efc754a094199a8c41ae686494c8f2a5e4741cef`
- successful exact-branch validation run: `34763260187`
- durable architecture decision: `PROJECT_DECISIONS.md -> TASTE-005`

## Remaining validation boundary

There is no known implementation blocker. The only intentionally unperformed production action is the requested manual validation of the existing `Taste Steam Review Dossier` task against the newly published V2 control plane. Exact Scheduled Task clock time was not changed or relied upon by this implementation; ordering is enforced by publishing the manifest in the canonical nightly pre-AI control-plane path before semantic consumption.

## Next step

Director reviews durable report; then user manually presses Run now on existing `Taste Steam Review Dossier` and validate.
