# Taste Steam Review Dossier Persistence Bridge 01 — durable worker report

Status: `complete_ready_for_user_run_now_validation`

## Authority and scope

Authoritative task: `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PERSISTENCE_BRIDGE_01.md`.

This task repaired only the persistence bridge between the existing Scheduled ChatGPT `Taste Steam Review Dossier` worker and the existing GitHub-owned dossier validation/persistence path. It did not regenerate or process the real 591-item backlog, did not run production `Run now`, and did not modify Taste Semantic Producer, `ingest-taste-batch.yml`, their schedules, limits, queues, or state.

## Architecture preflight result

The ownership model remains GitHub/GitHub Actions control-plane ownership for validation, canonical dossier persistence, same-snapshot progress, and completeness. Scheduled ChatGPT remains a constrained semantic producer and may submit only a structured checkpoint artifact.

The callable submission primitive available to the Scheduled ChatGPT environment is the connected GitHub Contents create-file action. The worker creates exactly one create-only artifact at:

`data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--{scope_sha256}.json`

The worker does not directly write `data/cache/taste_steam_review_dossiers/**` or `data/production/pre_ai/taste_steam_review_dossier_work.json`. No second scheduler, queue, retry loop, quota authority, or backlog-completeness authority was introduced.

## Production implementation

Implementation PR: #21 `Restore Steam dossier persistence bridge`.

Merge commit: `8916348d651afbdeaa13ba71e517bd2a967ce777`.

Production/test changes merged to `main`:

- `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `scripts/ingest_taste_steam_review_dossier_inbox.py`
- `scripts/ingest_taste_steam_review_dossiers.py`
- `scripts/test_taste_steam_review_dossier_persistence_bridge.py`

The event-driven workflow accepts only an exact newly created dossier inbox artifact, invokes the existing canonical ingest/persistence path, persists accepted dossier files and same-snapshot manifest progress atomically in one Git commit, and removes the accepted inbox artifact in that same canonical commit. The resulting cleanup push is recognized as a canonical no-op by the bridge workflow.

The canonical ingest continues to use `persist_submission_and_advance_snapshot`; it does not reread the Taste queue or rebuild scope from current queue/store state. Checkpoint size remains a durability boundary only.

## Fail-closed binding and replay behavior

Each submission is bound to the current manifest's exact:

- `snapshot_id`;
- `scope_sha256`;
- `scope_source`;
- `source_queue_sha256`;
- current checkpoint appids, exactly and in order.

The inbox filename is independently required to match `{snapshot_id}--{scope_sha256}.json`. Partial checkpoint submissions, wrong snapshot/scope, missing or extra appids, stale/replayed submissions, and invalid dossier contract data fail before canonical advancement. A failed later checkpoint leaves earlier accepted checkpoint progress intact.

## Focused GitHub-hosted regression validation

Final focused validation on the implemented bridge:

- workflow run: `34804961025`;
- job: `103854918217`;
- result: success.

The focused regression covers a synthetic 25-item fixed snapshot progressing `10 -> 10 -> 5 -> 0`, same-snapshot continuity, resume without repeats, replay rejection, partial rejection, wrong snapshot, wrong scope, missing appid, invalid dossier contract data, failed-later-checkpoint preservation of prior accepted progress, and static ownership/route assertions.

## Hosted create-file end-to-end acceptance

The exact Scheduled-ChatGPT submission technology was exercised through real connected GitHub create-file calls on an isolated synthetic acceptance branch. The synthetic snapshot contained 25 test appids only and was never merged to `main`.

An initial integration run `34804863149` / job `103854633980` failed closed before ingest. Confirmed cause: GitHub Contents API push events did not populate the assumed `head_commit.added/modified/removed` file lists. No canonical dossier state advanced. The workflow resolver was corrected to derive the inbox change from the authoritative pushed commit diff (`git diff-tree`).

The corrected bridge then passed the complete hosted acceptance on one fixed synthetic snapshot:

- checkpoint 1: run `34805024999`, job `103855113442`, persisted 10, same snapshot, remaining 15;
- checkpoint 2: run `34805127448`, job `103855411810`, persisted 10, same snapshot, remaining 5;
- checkpoint 3: run `34805164824`, job `103855527702`, persisted 5, same snapshot, remaining 0.

Final synthetic state on that same snapshot: `completed_required_count=25`, `remaining_required_count=0`, `current_checkpoint_count=0`, `full_backlog_complete=true`.

This proves the callable bridge itself, not only a local/unit approximation: connected GitHub create-file -> push-triggered GitHub workflow -> canonical dossier validation/persistence -> same-snapshot progress -> next exact checkpoint -> exhaustion.

## Scheduled task and unrelated production state

No new recurring ChatGPT task was created. No automation create/update call was performed as part of this task. The canonical repository worker prompt was updated with the exact create-file submission contract. No claim is made that an external Scheduled Task object was mutated.

Taste Semantic Producer and `ingest-taste-batch.yml` were not changed. Production `Run now` was not pressed. The real 591-item backlog was not processed by implementation or acceptance work.

Old PR #20 was closed unmerged as superseded after its branch became stale against Director changes; the clean six-file integration was merged through PR #21.

## Final status

`complete_ready_for_user_run_now_validation`

No known implementation blocker remains within the worker task's acceptance boundary.

## Next step

Director reads durable report; then user manually presses Run now on existing Taste Steam Review Dossier once and validates.
