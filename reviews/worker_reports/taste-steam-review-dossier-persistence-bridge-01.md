# Taste Steam Review Dossier Persistence Bridge 01 — durable worker report

## Task

Authoritative task: `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PERSISTENCE_BRIDGE_01.md`.

This task repaired only the persistence bridge between the existing Scheduled ChatGPT `Taste Steam Review Dossier` worker and the existing GitHub-owned dossier validation/persistence path. It did not regenerate or process the real production backlog, did not run production `Run now`, and did not modify Taste Semantic Producer, `ingest-taste-batch.yml`, their schedules, limits, queues, or state.

## Architecture-preflight answers

1. GitHub/GitHub Actions remains the control-plane owner for validation, canonical dossier persistence, same-snapshot progress, and completeness.
2. The callable submission primitive available to Scheduled ChatGPT is the connected GitHub Contents create-file action.
3. Scheduled ChatGPT remains a constrained semantic producer: it may submit only the exact structured current-checkpoint artifact and does not directly write canonical dossier store or work-manifest state.
4. No second scheduler, queue, retry loop, quota authority, or backlog-completeness authority was introduced.
5. The canonical ingest remains `persist_submission_and_advance_snapshot`; accepted checkpoints advance the same fixed `snapshot_id` without rereading the Taste queue or rebuilding scope from current queue/store state.

## Verified facts

- Implementation was merged through PR #21 `Restore Steam dossier persistence bridge`, merge commit `8916348d651afbdeaa13ba71e517bd2a967ce777`.
- The exact connected GitHub create-file transport was exercised in hosted acceptance, not merely simulated by unit tests.
- A synthetic 25-item fixed snapshot advanced `10 -> 10 -> 5 -> 0` on the same snapshot and reached `full_backlog_complete=true`.
- Production `Run now` was not pressed and no real production dossier backlog was processed by this implementation/acceptance work.
- Taste Semantic Producer and `ingest-taste-batch.yml` scheduling, limits, queue ownership, and state were not changed.
- No new recurring ChatGPT task was created and no automation create/update call was performed. The canonical repository worker prompt was updated; no claim is made that an external Scheduled Task object was mutated.
- Synthetic acceptance data and temporary worker workflows were not merged to `main`.

## Exact callable submission interface

Scheduled ChatGPT uses the connected GitHub Contents **create-file** action with:

- repository: `kentrap2011-hub/steam-kz-deals-2`;
- branch: `main`;
- mode: create-only;
- schema: `TASTE-STEAM-REVIEW-DOSSIER-SUBMISSION-V1`;
- path: `data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--{scope_sha256}.json`.

Each submission is bound to the current manifest's exact `snapshot_id`, `scope_sha256`, `scope_source`, `source_queue_sha256`, and current checkpoint appids exactly and in order. The filename is independently required to match the exact snapshot/scope pair. The worker must not update or overwrite an existing submission path and must not directly edit `data/cache/taste_steam_review_dossiers/**` or `data/production/pre_ai/taste_steam_review_dossier_work.json`.

## Changes

Production/test files merged to `main`:

- `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`;
- `config/taste_steam_review_dossier_persistence_bridge.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `scripts/ingest_taste_steam_review_dossier_inbox.py`;
- `scripts/ingest_taste_steam_review_dossiers.py`;
- `scripts/test_taste_steam_review_dossier_persistence_bridge.py`.

The event-driven workflow accepts one exact newly created inbox artifact, invokes the existing canonical ingest/persistence path, persists accepted dossier files and same-snapshot manifest progress atomically in one Git commit, and removes the accepted inbox artifact in that canonical commit. The resulting cleanup push is recognized as a canonical no-op. Partial checkpoint submissions, wrong snapshot/scope, missing or extra appids, stale/replayed submissions, and invalid dossier data fail before canonical advancement. A failed later checkpoint leaves earlier accepted checkpoint progress intact.

## Validation

Focused GitHub-hosted regression:

- run `34804961025`;
- job `103854918217`;
- result: success.

The focused regression covers synthetic `10 -> 10 -> 5 -> 0` progression, same-snapshot continuity, resume without repeats, replay rejection, partial rejection, wrong snapshot, wrong scope, missing appid, invalid dossier contract data, preservation of prior accepted progress after a later failure, and static ownership/route assertions.

Hosted create-file end-to-end acceptance used the same connected GitHub create-file mechanism expected from Scheduled ChatGPT on an isolated synthetic branch. An initial run `34804863149` / job `103854633980` failed closed before ingest because GitHub Contents API push events did not populate the assumed `head_commit.added/modified/removed` lists. No canonical dossier state advanced. The resolver was corrected to derive the inbox change from the authoritative pushed commit diff (`git diff-tree`).

The corrected bridge then passed the complete hosted acceptance on one fixed synthetic snapshot:

- checkpoint 1: run `34805024999`, job `103855113442`, persisted 10, remaining 15;
- checkpoint 2: run `34805127448`, job `103855411810`, persisted 10, remaining 5;
- checkpoint 3: run `34805164824`, job `103855527702`, persisted 5, remaining 0.

Final synthetic state on the same snapshot: `completed_required_count=25`, `remaining_required_count=0`, `current_checkpoint_count=0`, `full_backlog_complete=true`.

## Unresolved

None within the implementation and acceptance boundary of this worker task. Production behavior still has the explicitly deferred user `Run now` validation boundary; that is not an implementation blocker and was intentionally not executed by this worker.

## Status

`complete_ready_for_user_run_now_validation`

## PR refs

- PR #21: production implementation, merged as `8916348d651afbdeaa13ba71e517bd2a967ce777`.
- PR #20: closed unmerged as superseded after becoming stale against concurrent Director changes.
- PR #22: initial durable closeout (`CURRENT_TASK.md` + report), merged to `main`.
- This report-format amendment is docs-only and adds no runtime/state changes.

## Recommended next step

Director reads durable report; then user manually presses Run now on existing Taste Steam Review Dossier once and validates.

## Efficiency / reusable lesson

For files created through GitHub Contents, do not depend on webhook `head_commit.added/modified/removed` arrays being populated; derive the exact inbox mutation from the pushed commit diff. Keep semantic-worker transport as a create-only inbox artifact while canonical validation, persistence, progress, and completeness remain control-plane-owned. That makes stale/replayed submissions fail closed while preserving same-snapshot durability and resume semantics.
