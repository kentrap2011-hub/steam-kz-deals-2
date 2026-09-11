# Worker report — steam-partial-publish-failure-queue-01

Final status: `complete_ready_for_real_steam_refresh`

Branch: `worker/steam-partial-publish-failure-queue-01`

Implementation head before this report commit: `d1837f13958466a16281945845f4910cf35b0c60`

## Scope

Implemented only `WORKER_TASK_STEAM_PARTIAL_PUBLISH_FAILURE_QUEUE_01.md` and its Director-requested follow-up gaps. No real full Steam refresh was run. Free-game behavior, Taste, ChatGPT notifications, Code Architect review, and unrelated project behavior were not changed.

## Exact files changed

- `.github/workflows/steam-test.yml`
- `scripts/steam_partial_publish.py`
- `scripts/steam_partial_publish_runner.py`
- `scripts/test_steam_partial_publish.py`
- `reviews/worker_reports/steam-partial-publish-failure-queue-01.md`

No production data artifact was intentionally refreshed in this task.

## Behavior implemented

### Game-level isolation

A failure while processing one observed Steam item no longer aborts processing of unrelated items. Game failures are recorded in the durable queue with canonical key/AppID when available, name when known, failed stage, root error, first/last run references, attempts, and whether previous published site data exists.

Successfully processed games continue through normal shortlist generation in the same cycle.

### Last known good preservation

If a failed game existed in the previous accepted shortlist, its previous row is preserved in the newly produced shortlist while the game remains unresolved in the failure queue. The queue entry records `prior_site_data_exists=true` and `last_known_good_preserved=true` when that fallback is used.

### Catalog-segment isolation

A failed Steam catalog page/segment is recorded as an exact request descriptor (`sort_by`, `start`, `count`) and processing advances to later segments. No game identities are invented for an unseen failed segment.

A segment failure does not itself make the run fail if the traversal can still establish the end of the catalog and the remaining quality guards pass.

### Honest partial-source metadata

Failed catalog segments now produce honest partial-source metadata instead of contradictory full-completeness claims.

When `catalog_segment_failures_this_run > 0`:

- production manifest `complete=false`;
- shortlist index `source_complete=false`;
- `source_status="partial"`;
- `source_has_known_gaps=true`;
- `known_catalog_gap_count` records the number of failed segments.

When there are no failed catalog segments, those fields report complete coverage normally.

Live `steam_total_reported` drift remains informational. The run does not fail only because the reported total differs from the unique observed item count.

### Durable unresolved failure state

Canonical active failure state:

`data/cache/steam_partial_publish_failures.json`

Unresolved game and segment failures persist across runs. A successfully reprocessed known game/segment may be removed as resolved; unresolved entries are not silently discarded.

The run summary contains:

- `processed_successfully`;
- `problematic_games`;
- `problematic_catalog_segments`;
- `problematic_system_state`;
- failures observed in the current run;
- whether failure-queue recovery happened in the current run.

### Corrupt/unreadable failure-state handling

A corrupt or structurally invalid failure-state file is no longer treated as an empty healthy queue.

On load failure:

1. The damaged active file is moved out of the working path into a sibling quarantine directory named from the active queue (`data/cache/steam_partial_publish_failures_quarantine/` for production).
2. The quarantined bytes are preserved under a timestamped `.corrupt...` filename.
3. A new active queue is created only after quarantine/recovery.
4. The new queue contains a persistent `system_problems` record with:
   - `problem_type=failure_queue_unreadable`;
   - original path;
   - quarantine path;
   - root load/validation error;
   - run reference and timestamps;
   - `requires_manual_disposition=true`.
5. If the damaged file cannot be moved to quarantine, the code raises and refuses to overwrite the active path.
6. The workflow stages both the active failure queue and any quarantine directory so the evidence survives the production commit.

Existing schema-v1 failure queues without the newer `system_problems` field remain backward-compatible; the field is initialized to an empty list when the otherwise-valid queue is loaded.

## Production invocation path verified and changed

The real Steam production workflow is:

`.github/workflows/steam-test.yml`

Workflow name:

`Steam KZ production shortlist`

It is invoked by both `workflow_dispatch` and the existing nightly schedule (`10 20 * * *`).

Before this task, the real collector step was:

`python scripts/steam_production_cached.py`

On this worker branch it is now:

`python scripts/steam_partial_publish_runner.py`

The new workflow also executes the focused regression test before the collector:

`python scripts/test_steam_partial_publish.py`

The old strict collector remains in the repository as reusable legacy/core code, but the canonical scheduled/manual workflow no longer invokes it directly after this branch is integrated.

The workflow still commits the normal successful shortlist/manifest path and dispatches the existing visual refresh. A partial catalog run can therefore publish the successfully obtained result set while carrying `complete=false/source_complete=false` and explicit known-gap metadata.

No real workflow dispatch and no real full Steam refresh were performed in this task.

## Automated tests actually executed

The branch test/helper snapshots were copied into a temporary local working directory because direct git network transport is unavailable in the execution environment. No network/Steam calls are used by these tests.

Commands executed:

```text
python -m py_compile scripts/steam_partial_publish.py scripts/test_steam_partial_publish.py
python scripts/test_steam_partial_publish.py
```

Result:

```text
test_one_game_failure_does_not_stop_others: PASS
test_known_failed_game_keeps_old_data: PASS
test_segment_failure_is_separate_and_does_not_stop: PASS
test_failed_segment_marks_source_partial: PASS
test_live_total_drift_is_informational: PASS
test_failures_persist_and_are_summarized: PASS
test_corrupt_failure_queue_is_quarantined_and_recorded: PASS
Steam partial publish regressions: 7/7 PASS
```

These tests prove the required bounded behavior without a fake full Steam crawl and without executing production refresh.

## Commits

Initial implementation commits:

- `3ac861e85ac407408b8821204f04af6ee56b3175` — initial durable failure queue
- `518b56fde9efbd393ce98522134b8ff9d6273c7c` — initial focused regressions
- `43df55f5041d4eb6b4022bbc9482f6159cd4bd36` — initial partial-publish runner

Acceptance follow-up commits:

- `e062f864b322eadfd057cc190e05310c02abb683` — corrupt-state quarantine/system-problem hardening
- `d2cbb81804945b41dee7d5ee77df482cb908f5e5` — partial-source and corrupt-state regressions
- `2e7c7f79dd23367296857ce0a3daed2b5ab69b43` — honest partial-source metadata in runner
- `d1837f13958466a16281945845f4910cf35b0c60` — canonical production workflow wiring

## Main/worker integration note

The task contract explicitly requires keeping the changes on the worker branch until Director review. `main` advanced after the worker branch was created, but comparison from the branch base shows those intervening main changes are limited to Director/task-board/task-contract files and do not overlap the four implementation files above.

Therefore this worker result is ready for Director integration/review, but a real Steam refresh should not be launched from current `main` until the Director integrates this worker branch. Once integrated, the next canonical scheduled/manual Steam refresh will enter through `scripts/steam_partial_publish_runner.py` and the new regression step will run before collection.

## Migration / backward compatibility

- No data migration is required before the first run.
- Missing failure-state file starts a new healthy empty queue.
- Existing valid schema-v1 queue remains readable and gains `system_problems=[]` in memory if that field is absent.
- Corrupt/invalid active queue is quarantined instead of overwritten.
- Existing shortlist columns are preserved when usable; prior known-good shortlist rows can be carried forward for failed known games.
- Free-game artifacts are not rewritten by the new partial runner.
- Existing Steam review HTTP cache acceleration remains in use.

## Safety decision for real Steam refresh

Implementation and focused regression status: ready.

A real Steam refresh is safe to run **after Director review/integration of this worker branch into current `main`**. Do not run the real refresh before that integration because current `main` intentionally still represents the pre-review production wiring.

No implementation blocker remains inside this task.

Final status: `complete_ready_for_real_steam_refresh`
