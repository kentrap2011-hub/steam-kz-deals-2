# Worker Report — Existing 10-Result Taste Batch Pinned Ingest 01

- task_id: `taste-existing-batch-pinned-ingest-01`
- lifecycle: `terminal_blocked`
- started_utc: `2026-09-10T13:15:51Z`
- Last checkpoint UTC: `2026-09-10T13:23:46Z`
- target_package: `data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json`
- target_package_blob_sha: `54faa8bc16064b15df8dd781d1988986b05e0e1c`
- expected_result_count: `10`
- queue_count_before_ingest: `539`
- ingest_launch_count: `0`
- workflow_run_id: `not_launched`
- workflow_job_id: `not_launched`
- final_status: `blocked_workflow_dispatch_not_exposed_by_connected_github_api`
- next_action: `Issue exactly one workflow_dispatch for .github/workflows/ingest-taste-batch.yml on ref main (REST: POST /repos/kentrap2011-hub/steam-kz-deals-2/actions/workflows/ingest-taste-batch.yml/dispatches with body {"ref":"main"}; equivalent gh command: gh workflow run ingest-taste-batch.yml --repo kentrap2011-hub/steam-kz-deals-2 --ref main). Immediately after that single dispatch, resolve and persist the exact new workflow run ID and ingest job ID in this report before polling. Do not rerun old job 98473122297 / run 34454681107.`

## Scope

Authorized production ingest of the existing untouched 10-result Taste package only through the completed pinned-profile lifecycle production path. Semantic results must not be regenerated or edited. No next games/batch, manual queue/cache/overlay state edits, Scheduled Task changes, or code/config changes are authorized.

## Report-first checkpoint

This report was the first repository mutation after reading `WORKER_TASK_TASTE_EXISTING_BATCH_PINNED_INGEST_01.md`.

At report creation:

- target package existed at the exact required path;
- current canonical queue count was `539`;
- ingest had not been launched.

## Fail-closed preflight result

Repository/state preconditions for the package itself passed:

1. Accepted lifecycle authority report is terminal `complete_pinned_profile_lifecycle_fix_ready_for_acceptance` and explicitly leaves this package uningested and grandfatherable.
2. Current target package Git blob SHA is still exactly `54faa8bc16064b15df8dd781d1988986b05e0e1c`.
3. Git history for the target path contains exactly the original result-introduction commit `f138d5216248c999fde588c47ca5088ff9c076ee`; its direct parent is exact pre-semantic checkpoint `0ec1ed0ec10e8950f86e6f600bc360325481ae9b`.
4. Current production `scripts/taste_pinned_work_unit.py` encodes those exact `LEGACY_RESULT_PATH`, `LEGACY_RESULT_COMMIT`, and `LEGACY_PIN_COMMIT` values and reconstructs the legacy pin from the checkpoint projection/queue before validating the unchanged document.
5. The checkpoint projection at `0ec1ed0ec10e8950f86e6f600bc360325481ae9b` is complete and bound to profile blob `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`, model `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`, and source mailing `2026-09-08T20:46:16.637935+00:00`; the checkpoint queue begins with the same ordered package work.
6. No canonical receipt exists at `data/cache/taste_ingest_receipts/manual-throughput-drain-01-batch-001.json` or at the checked production receipt alias, so there is no evidence of a later successful consumption of this exact package. The package itself is still present and unchanged.
7. Current canonical `data/production/pre_ai/chatgpt_payload.json` reports `ai_queue_count: 539`; this is the truthful pre-launch baseline to use for post-success comparison.
8. `data/production/pre_ai/taste_active_work_unit.json` is currently absent. For this exact grandfathered package this is allowed by the accepted lifecycle: the legacy package is not permitted to retire an unrelated active pin; after a successful legacy transaction, current live work is prepared as the next active pin.
9. GitHub Actions reports zero `in_progress` and zero `queued` runs on `main` at preflight time; no conflicting production Actions run/concurrency holder was observed.
10. Current `.github/workflows/ingest-taste-batch.yml` is the corrected production path: the ingest step receives `${{ github.token }}` and the commit step explicitly stages `taste_active_work_unit.json` when created/changed.

## Launch gate and exact blocker

No ingest attempt was launched.

The only authorized safe launch at this point is a **new** `workflow_dispatch` of the current `main` version of `.github/workflows/ingest-taste-batch.yml`.

The connected GitHub action surface available to this worker exposes repository reads/writes, Actions reads/logs and rerun of an existing job, but it does **not** expose creation of a new workflow-dispatch event. Plugin discovery for `GitHub Actions workflow dispatch` returned no additional installable capability.

Using another mechanism would violate the task:

- modifying/reintroducing the inbox package merely to cause a `push` event is forbidden and would alter its provenance/history;
- changing workflow/scripts/config merely to cause a `push` event is forbidden;
- rerunning old run `34454681107` / job `98473122297` is not equivalent to launching the corrected production workflow: that run was created from the pre-fix workflow definition, whose ingest step had no `GITHUB_TOKEN` environment and whose commit step did not stage `data/production/pre_ai/taste_active_work_unit.json`.

Therefore fail-closed behavior requires stopping with **zero launch attempts**, rather than consuming the one allowed attempt through a known-wrong path.

## Required exact upstream operation

Execute exactly once against current `main`:

```text
POST /repos/kentrap2011-hub/steam-kz-deals-2/actions/workflows/ingest-taste-batch.yml/dispatches
{"ref":"main"}
```

Equivalent GitHub CLI operation:

```text
gh workflow run ingest-taste-batch.yml --repo kentrap2011-hub/steam-kz-deals-2 --ref main
```

Immediately after that single dispatch, resolve the exact new workflow run ID and the `ingest` job ID and persist both in this report **before polling the run**. Then poll only those exact IDs. If that attempt fails, do not dispatch again; diagnose the exact root cause and write it here. If it succeeds, verify receipt, exact queue transition, next active pin, canonical persistence of all 10 results, unchanged package semantics, and absence of unrelated state changes.

## Mutation / safety confirmation

During this worker task so far:

- semantic results were not recalculated, regenerated, or edited;
- target package was not rewritten, deleted, moved, or reintroduced;
- production ingest launch count is exactly `0`;
- no next games/batch were started;
- Scheduled Task was not changed;
- canonical queue/cache/overlay were not manually changed;
- workflow/scripts/config were not changed;
- old failed ingest was not rerun.

## Terminal status

`blocked_workflow_dispatch_not_exposed_by_connected_github_api`

This is an execution-interface/API capability blocker, not a repository validation failure and not an ingest failure. No workflow run/job ID exists to record because no authorized production attempt was launched.