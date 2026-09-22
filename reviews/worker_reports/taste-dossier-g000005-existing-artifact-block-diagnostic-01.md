# Taste Dossier g000005 Existing-Artifact Block Diagnostic 01

Status: `complete_root_cause_proven`

## Verified facts

- Repository/source of truth: `kentrap2011-hub/steam-kz-deals-2` / `main`.
- Evidence baseline immediately before report creation: `main` head `611525ecc82249d8c7692439e9129e7ebc920af8`.
- Active snapshot: `04298ca0b80d00cd819af116323de3d1c4906d6ed71e84f40c15c6978d0d08d8`.
- Active prepared set: `prepared_required_sha256=271d2a484f3c644e9a53687b60385ad3c89dbbc654ba3c9247d9e829b0e0b174`.
- Canonical progress still expects `g000005`: `canonical_expected_sequence=5`.
- Current backlog is not complete: `completed_required_count=12`, `remaining_required_count=708`, `full_backlog_complete=false`.
- Exact current descriptor: `data/production/pre_ai/taste_steam_review_dossier_worker_groups/04298ca0b80d00cd819af116323de3d1c4906d6ed71e84f40c15c6978d0d08d8/g000005.json`.
- Exact deterministic artifact exists at:
  `data/ai_inbox/taste_steam_review_dossiers/04298ca0b80d00cd819af116323de3d1c4906d6ed71e84f40c15c6978d0d08d8--g000005--c7df88a7b625aa61cf040abe21ce79e51b287066818abf5ca149657b5dde4cbd.json`.
- Descriptor/artifact group binding is current and exact: `group_sha256=c7df88a7b625aa61cf040abe21ce79e51b287066818abf5ca149657b5dde4cbd`; `items_sha256=8a7148be01331f3ea6ca1dc3017285c1b2b6db85649ab5d6598cdc2a00a4bdee`; appids `1058450,1062040,1066780`.
- The artifact first entered `main` in commit `51c9b3eb8e0fb0b978f44dd043814d93009bf401` (`Buffer Taste Steam review dossier group 000005`).
- GitHub-owned ingest did observe the publication. Actions run `35647796769`, job `106492426418` (`ingest`) completed successfully as a workflow execution while recording:
  - `blocked_reason=invalid_expected_group`
  - `canonical_expected_sequence=5`
  - validator error: `observation 0 evidence_languages must exactly equal the canonical bound-record language projection`.
- Current `data/production/pre_ai/taste_steam_review_dossier_validation_status.json` still records g000005 as the invalid canonical expected group.

## Root cause

The deadlock is caused by the interaction of a rejected current candidate with immutable create-only transport semantics.

The Scheduled semantic worker successfully published the exact current deterministic g000005 transport artifact. GitHub's canonical ingest/drain then validated it and rejected it on dossier semantics (`evidence_languages` did not equal the canonical bound-record language projection). Because the current expected candidate was invalid, GitHub correctly did not advance canonical progress, so sequence 5 remained expected.

The rejected candidate remains at the same deterministic inbox path as immutable transport evidence. The persistence bridge explicitly separates transport existence from canonical progress: buffered inbox artifacts are not canonical acceptance, and GitHub owns validation/progress/cleanup. Therefore it is contract-consistent for the exact g000005 artifact to exist while canonical state still expects g000005.

On the next invocation the worker reloads canonical expected sequence 5, derives that same deterministic path, finds it occupied, and must stop. The canonical worker prompt/persistence bridge forbid overwrite, rename, skip, alternate filename, buffer-scanning resume, or worker-side healing.

## Existing artifact versus active snapshot

The existing g000005 artifact is not stale or foreign. Its snapshot, prepared-set binding, sequence, group hash, item hash, and appids match the current active g000005 descriptor. Its blocker is semantic invalidity, not snapshot/path incompatibility.

## Expected GitHub drain/validation path and failure point

Expected path:

`buffered publication -> ingest-taste-steam-review-dossier-checkpoint -> canonical validation -> contiguous drain -> canonical progress update`.

The observable failure point is canonical validation of the current expected candidate. The GitHub-owned workflow did run; it did not miss the artifact. It stopped the drain at g000005 because validation returned `invalid_expected_group`. Advancing sequence past this candidate would violate the fail-closed contiguous-drain contract.

Relevant refs:

- `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `data/production/pre_ai/taste_steam_review_dossier_validation_status.json`
- Actions run `35647796769`, job `106492426418`.

## Canonical recovery path

A safe recovery path already exists in `config/taste_steam_review_dossier_recovery_contract.json`.

For an invalid current expected artifact, recovery is owned by `github_control_plane`, not the semantic worker. The allowed bounded action is `quarantine_invalid_expected` for only the current canonical expected sequence and exact deterministic path. It requires canonical validator failure, forbids alternate retry filenames, preserves later pending groups, does not itself advance canonical progress, and permits the same deterministic path to be created again after recovery.

This diagnostic did not execute recovery.

## Scheduled Task self-disable authority

User-observed runtime fact: after encountering the existing-artifact block, the Scheduled worker disabled the hourly Taste Steam Review Dossier task.

That self-disable is not authorized by the inspected canonical repository contracts as a completion transition. The canonical worker prompt defines `full_backlog_complete=true` as the backlog-complete terminal condition. Current state is `full_backlog_complete=false` with sequence 5 still expected.

For an existing expected artifact while canonical progress has not advanced, the worker is instructed to stop the invocation and leave recovery/validation to the GitHub control plane. `config/execution_ownership_contract.json` likewise assigns canonical validation, checkpoint/progress, completeness, persistence, and recovery authority to GitHub rather than the scheduled semantic data-plane worker.

Therefore the existing-artifact STOP was correct, but disabling the recurring task because of that invocation-level STOP was a separate runtime/entrypoint contract violation. The exact external scheduler transition is not reconstructable from repository state; this finding uses the task's user-observed self-disable fact and the current canonical authority rules.

## Would hourly reruns make progress?

No. Without GitHub control-plane recovery, each rerun would reload `canonical_expected_sequence=5`, derive the same deterministic g000005 path, find the same immutable invalid artifact, and be required to stop again. Repetition alone cannot clear the block because the Scheduled semantic worker has no authority to quarantine/delete/overwrite the artifact or advance canonical progress.

## Classification

Overall classification: `MIXED`.

- `DATA_CONTRACT`: g000005 candidate is semantically invalid on `evidence_languages`, which pins canonical progress.
- `CONTROL_PLANE`: recovery of an invalid current expected artifact is GitHub-owned and must occur through the defined recovery path.
- `RUNTIME/ENTRYPOINT`: the existing-path STOP is correct; the reported self-disable while `full_backlog_complete=false` is a separate contract violation.
- `WORKFLOW` is not the primary defect here: the GitHub ingest/drain path observed g000005 and correctly refused to advance it.

## Exactly one bounded follow-up

Execute the existing GitHub-owned `quarantine_invalid_expected` recovery for only the current g000005 deterministic artifact, preserving canonical sequence 5 and later buffered groups, then let the contract-defined GitHub reconciliation/drain path resume from canonical state.

Do not implement this in the Scheduled semantic worker; do not overwrite/delete the artifact in place; do not choose an alternate retry filename; do not skip g000005.

## Scope confirmation

This task performed diagnosis only. No Scheduled Task was run or edited; no recovery was executed; no artifact was overwritten/deleted/quarantined; no canonical progress was manually advanced; no PASS 1/PASS 2 state or source/contract/workflow was changed. The durable report is the only write.
