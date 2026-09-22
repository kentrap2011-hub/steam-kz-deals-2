# Taste Steam Review Dossier g000005 Existing-Artifact Block Diagnostic 01

## Status

- Result: `complete_root_cause_proven`
- Root-cause classification: `MIXED`
- Scope: diagnostic only.
- Repository/source of truth: `kentrap2011-hub/steam-kz-deals-2` / `main`.
- Evidence baseline immediately before this report commit: `main` head `a3aadfb1c5c6e2ada12a5461e48f00be76ae7fb0`.
- No config, production data, workflow, recovery request, or scheduler state was changed by this task.

## Executive finding

The g000005 block is a deterministic fail-closed chain, not a case where GitHub accepted the group and then lost progress.

The scheduled semantic worker published the exact deterministic g000005 inbox artifact. GitHub's control-plane ingest/drain then validated that candidate and rejected it because the dossier payload was semantically invalid: `observation 0 evidence_languages must exactly equal the canonical bound-record language projection`. GitHub therefore correctly kept `canonical_expected_sequence=5` instead of advancing canonical progress.

The rejected candidate remains an immutable transport artifact at the same deterministic inbox path. Because the persistence bridge defines inbox artifacts as transport rather than canonical progress, artifact existence and canonical acceptance are intentionally different facts. The next scheduled worker invocation reloads GitHub's canonical expected sequence, derives the same deterministic g000005 path, sees that it already exists, and is required to stop without overwrite, rename, skip, alternate filename, or worker-side healing.

The reported self-disable after that per-run terminal failure is not supported as a backlog-completion transition by the canonical repository contracts. Current canonical state has `full_backlog_complete=false`; a per-invocation existing-artifact failure is therefore not equivalent to completed backlog.

## Exact current evidence

At the pre-report evidence head, the canonical worker state is still blocked on g000005:

| Evidence | Current value |
| --- | --- |
| Work manifest | `data/production/pre_ai/taste_steam_review_dossier_work.json` blob `043d7dc64e5725a342765aedaadbd77740fd212d` |
| Worker index | `data/production/pre_ai/taste_steam_review_dossier_worker_index.json` blob `e39ea5de8218a2ca1b11c6eda59ff77e99adcbf9` |
| Validation status | `data/production/pre_ai/taste_steam_review_dossier_validation_status.json` blob `f93303617e07f91752e4daf0cfa27ba205072b89` |
| g000005 descriptor | `data/production/pre_ai/taste_steam_review_dossier_worker_groups/04298ca0b80d00cd819af116323de3d1c4906d6ed71e84f40c15c6978d0d08d8/g000005.json` blob `82a2ce44299264ab62d159df3c3aade1a59c816e` |
| Exact g000005 artifact | `data/ai_inbox/taste_steam_review_dossiers/04298ca0b80d00cd819af116323de3d1c4906d6ed71e84f40c15c6978d0d08d8--g000005--c7df88a7b625aa61cf040abe21ce79e51b287066818abf5ca149657b5dde4cbd.json` blob `c88abf09e96b350609d84dac396a548c74d91437` |
| Worker prompt | `config/taste_steam_review_dossier_worker_prompt.md` blob `1ba4a390923e6bfbc655c7f0094db70ba395b9a6` |
| Execution ownership | `config/execution_ownership_contract.json` blob `815e1c509e8879a41a883147b9bfef2d5a953c7b` |
| Persistence bridge | `config/taste_steam_review_dossier_persistence_bridge.json` blob `db9bd5e13d7b36b0e7458c76da4c97416402ad80` |
| Recovery contract | `config/taste_steam_review_dossier_recovery_contract.json` blob `664a6b432f399017adda76b2e43d2743b032398e` |
| Ingest workflow | `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml` blob `ef20673f77293ce6a0f26991eade96abb64a5a32` |

Current canonical values are:

- `snapshot_id=04298ca0b80d00cd819af116323de3d1c4906d6ed71e84f40c15c6978d0d08d8`
- `prepared_required_sha256=271d2a484f3c644e9a53687b60385ad3c89dbbc654ba3c9247d9e829b0e0b174`
- `canonical_expected_sequence=5`
- `completed_required_count=12`
- `remaining_required_count=708`
- `full_backlog_complete=false`
- g000005 `group_sha256=c7df88a7b625aa61cf040abe21ce79e51b287066818abf5ca149657b5dde4cbd`
- g000005 `items_sha256=8a7148be01331f3ea6ca1dc3017285c1b2b6db85649ab5d6598cdc2a00a4bdee`
- g000005 current appids: `1058450, 1062040, 1066780`
- validation status identifies g000005 as `canonical_position=expected`, `validation=invalid`
- `invalid_expected_group.validator_error=observation 0 evidence_languages must exactly equal the canonical bound-record language projection`

The exact artifact path first entered `main` in commit `51c9b3eb8e0fb0b978f44dd043814d93009bf401` (`Buffer Taste Steam review dossier group 000005`, 2026-09-21T19:55:00Z).

GitHub Actions run `35647796769`, job `106492426418` (`ingest`), completed successfully as a control-plane run while explicitly recording:

- `blocked_reason=invalid_expected_group`
- `canonical_expected_sequence=5`
- `invalid_expected_group`
- validator error `observation 0 evidence_languages must exactly equal the canonical bound-record language projection`

The workflow's successful conclusion therefore means the fail-closed ingest/drain process itself ran successfully; it does **not** mean g000005 was accepted.

## Causal chain

1. GitHub prepared canonical g000005 and made sequence 5 the canonical expected group.
2. The scheduled semantic worker created the exact deterministic g000005 candidate at the contract-defined inbox path.
3. That push woke the GitHub control plane.
4. GitHub re-derived current canonical state and validated the expected candidate.
5. Validation rejected g000005 on dossier semantic content: the observation's `evidence_languages` did not equal the canonical bound-record language projection.
6. Because the expected candidate was invalid, GitHub did not advance canonical progress. Sequence 5 remained canonical expected.
7. The invalid candidate remained at its immutable create-only transport path. The recovery contract has `automatic_recovery=false`; the scheduled worker has no authority to delete, overwrite, rename, quarantine, or repair it.
8. On a later scheduled invocation, the worker reloads `canonical_expected_sequence=5`, derives the same deterministic artifact path, sees the existing file, and must stop without overwrite, alternate path, skip, or worker-side retry.
9. The task's incident record reports that the scheduled task then self-disabled. That scheduler transition is not independently reconstructable from repository state or the accessible live scheduler metadata in this diagnostic, but its compatibility with the canonical contracts can still be assessed from the repository authority model.

## Why the artifact can exist while sequence 5 remains expected

The persistence bridge explicitly separates transport from canonical progress:

- buffered inbox artifacts have `canonical_progress=false`;
- GitHub Actions owns validation, persistence, progress, completeness, and buffer cleanup;
- `expected_sequence_source` is GitHub-owned canonical progress;
- an existing expected artifact must not be overwritten or treated by the worker as permission to resume later work.

Therefore the presence of the g000005 file proves only that a candidate was published. It does not prove acceptance. Because semantic validation failed, the canonical sequence did not advance. Because the invalid candidate is retained as immutable evidence and automatic recovery is disabled, the deterministic path remains occupied at the same time sequence 5 remains expected. Those two facts are contract-consistent.

## Did GitHub workflow advance or should it have advanced?

No. The GitHub control plane did run, and it correctly did **not** advance.

The current validation status identifies g000005 as the invalid expected group, and the ingest job log records both `canonical_expected_sequence=5` and the semantic validator error. Advancing past an invalid expected group would violate the fail-closed contiguous-drain rules. The workflow behavior is therefore evidence against a primary `WORKFLOW` defect in this incident.

The recovery contract instead assigns invalid-expected-artifact recovery to `github_control_plane`. It explicitly gives the worker `worker_authority=false`, GitHub `github_authority=true`, requires a canonical validator failure, forbids alternate retry filenames, preserves later pending groups, and does not advance canonical progress as part of recovery.

## Scheduled-worker self-disable assessment

The canonical worker contract distinguishes two different terminal conditions:

- backlog completion: `full_backlog_complete=true`;
- an invocation-level failure such as finding the deterministic artifact for the current expected group already present while canonical progress has not advanced.

For the second case, the worker must stop the invocation and leave recovery/validation state to GitHub. It must not interpret the existing inbox artifact as queue progress and must not heal around the collision.

At the evidence baseline, `full_backlog_complete=false`, `remaining_required_count=708`, and `canonical_expected_sequence=5`. Nothing in the inspected worker prompt, ownership contract, persistence bridge, or recovery contract promotes this per-run failure into backlog completion or transfers recovery ownership to the scheduled worker.

Accordingly, self-disabling the recurring dossier worker **because of this g000005 existing-artifact STOP condition** is contract-incompatible while `full_backlog_complete=false`. The precise external scheduler action that produced the reported disabled state is not directly observable from the repository evidence available to this diagnostic; that limitation does not change the contract conclusion.

## Root-cause classification: MIXED

The incident is best classified as `MIXED`, with three proven components:

| Component | Finding |
| --- | --- |
| `DATA_CONTRACT` | The published g000005 candidate fails canonical semantic validation on `evidence_languages`. This is the reason canonical progress remains pinned. |
| `RUNTIME` | The next scheduled invocation correctly hits the create-only existing-path guard. The reported self-disable after that invocation-level failure is not a valid substitute for `full_backlog_complete=true`. |
| `CONTROL_PLANE` | Clearing an invalid expected artifact is deliberately GitHub-owned and non-automatic. Until the explicit recovery path is invoked, the deterministic slot remains occupied and the worker is required to remain fail-closed. |

`WORKFLOW` is not the primary cause: the available GitHub Actions evidence shows the control-plane job ran and correctly refused to advance an invalid expected group.

## Exactly one smallest safe bounded follow-up fix scope

Use the already-defined GitHub-owned `CURRENT_EXPECTED_DOSSIER_ARTIFACT_INVALID` recovery for **only the current g000005 deterministic artifact**: perform the recovery contract's `quarantine_invalid_expected` action with its audit record, preserving canonical sequence 5 and all later buffered groups, then execute the contract-defined `drain_after_recovery` reconciliation.

This is one bounded control-plane recovery scope. It must not be implemented by the scheduled semantic worker, must not overwrite/delete the candidate in place, must not skip sequence 5, and must not alter unrelated prompt/workflow/scheduler behavior. It is **not implemented by this diagnostic task**.

## Conclusion

Status is `complete_root_cause_proven`.

The exact g000005 candidate exists because the semantic worker successfully published a transport artifact. Sequence 5 remains expected because GitHub correctly rejected that artifact and fail-closed. The deterministic path then blocks the next create-only invocation by design. Recovery belongs to GitHub control plane, not the semantic worker. A per-run existing-artifact failure is not evidence of full backlog completion and does not justify treating the recurring dossier task as complete while `full_backlog_complete=false`.
