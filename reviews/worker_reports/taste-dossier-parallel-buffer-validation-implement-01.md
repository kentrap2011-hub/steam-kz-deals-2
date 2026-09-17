# Taste Dossier Parallel Buffer Validation Implement 01 — worker report

Status: `complete_ready_for_live_acceptance`

Task: `taste-dossier-parallel-buffer-validation-implement-01`
Repository: `kentrap2011-hub/steam-kz-deals-2`
Baseline `main`: `0efb36c7c5a3de764fa00e20ca18a9bf2368d50e`
Implementation branch durable head before squash merge: `00f63fdac3bdecc35223b1ec9eaddfda56ede76a`
Implementation PR: #39
Implementation squash merge: `7b18995ab813dabdc491697ac3fc3b3f6299adc6`
Contract/status binding follow-up PR: #40
Follow-up squash merge: `29a3c178bd24874bcaa19c2a404e43db1e9f4078`

## Architecture preflight

PASS.

The requested behavior stays inside the existing ownership boundary:

- GitHub remains owner of canonical scope/order, immutable group plan, snapshot identity, strict validation, canonical persistence, progress, recovery and completeness.
- Scheduled ChatGPT remains only the bounded semantic research/synthesis worker plus immutable create-only candidate transport writer.
- No second scheduler, external queue, retry manager, backlog manager or service was introduced.
- Candidate artifacts remain immutable/create-only.
- Canonical progress remains fail-closed and accepts only a contiguous prefix.
- Acceptance remains group-atomic. Canonical `checkpoint_size` remains `3`; the natural final-tail exception remains the existing contract behavior.
- Existing evidence/privacy/content, temporal, item-identity, Russian-evidence, conflict, compatibility-binding and package-member guards were not weakened.
- Downstream Taste/ranking/pricing/commercial behavior was not changed.

## Old synchronous behavior removed

Before this change the Scheduled worker prompt required repository-local execution of:

`python scripts/taste_steam_review_dossier_prepublication.py --artifact ...`

and treated validator unavailability as a pre-publication stop. That is no longer a Scheduled runtime prerequisite.

The active evidence contract now states:

- `validate_complete_group_before_create_only_publication: false`;
- `scheduled_worker_python_execution_required: false`;
- `scheduled_worker_manual_validator_required: false`;
- GitHub strict validation is required after candidate publication.

`scripts/taste_steam_review_dossier_prepublication.py` remains only as a CI/developer parity utility. The worker prompt contains no required `python scripts/taste_steam_review_dossier_prepublication.py` execution command and explicitly says repository-local Python/shell is not a Scheduled-worker prerequisite.

## New Scheduled worker buffering and liveness semantics

At invocation start the worker still starts from GitHub's canonical `canonical_expected_sequence=N` and the exact immutable descriptor for N.

After a successful connected GitHub create-file write for group N:

- the write means only `candidate buffered`, never accepted;
- the worker advances its local traversal target only to N+1;
- it does not wait for GitHub validation or canonical persistence;
- it re-reads only the compact index values needed to prove the same snapshot, prepared scope, group plan, source scope and full compatibility binding are still live;
- `canonical_expected_sequence` may lag during that same invocation and is not used as a N+1 publication gate;
- descriptor order remains strict: N+1 may follow N, but N+2 cannot be skipped to directly;
- the worker stops on a true liveness-binding change, missing/inconsistent descriptor, create-only transport failure, or ordinary invocation/runtime limit.

On a later invocation the worker starts again from GitHub's canonical expected sequence. If that deterministic expected candidate already exists while canonical progress has not advanced, it does not overwrite, rename, skip, invent an alternate artifact or treat the inbox as its own queue.

## GitHub validation and contiguous drain semantics

GitHub remains the only canonical acceptance gate.

The candidate-triggered serialized ingest workflow now:

1. applies only explicit existing recovery if requested;
2. runs the existing strict contiguous buffer drain with `--reconcile-nonfatal`, so a semantic-invalid expected group is represented as blocked canonical state rather than an infrastructure retry request;
3. runs `scripts/taste_steam_review_dossier_parallel_validation.py` to strict-validate all remaining current-snapshot candidates independently for observability;
4. commits canonical progress, immutable buffer state and validation status atomically when there is a state change.

The canonical drain implementation itself was not weakened. It still invokes `scripts/taste_steam_review_dossier_buffered.py::validate_buffer_artifact` before persistence and still stops at the first gap, duplicate, non-deterministic path or invalid expected group. Later candidate validity never grants permission to cross an earlier invalid sequence.

## Durable validation status

The pre-existing drain had durable canonical progress and immutable buffered artifacts, but no durable machine-readable invalid marker because an invalid expected group could terminate ingestion before any invalid outcome was committed.

The smallest added status layer is:

`data/production/pre_ai/taste_steam_review_dossier_validation_status.json`

Schema: `TASTE-STEAM-REVIEW-DOSSIER-PARALLEL-VALIDATION-STATUS-V1`.

It is explicitly observational only and is not canonical progress, a queue, retry state or repair authority. Each present candidate outcome is bound to the current snapshot, group `sequence`, `group_sha256`, exact `web_evidence_contract_binding`, artifact path and artifact SHA-256. Invalid records include the canonical validator error. A new snapshot supersedes prior status naturally through the existing snapshot/binding model.

The follow-up PR #40 aligned the contract's required binding name with the emitted machine field `sequence` and pinned that exact binding plus new-snapshot supersession in regression coverage. It changed no runtime logic.

## Deterministic proof: invalid middle group blocks later buffered work

`scripts/test_taste_steam_review_dossier_parallel_validation.py` constructs four canonical groups of three games each and publishes all four candidate artifacts while canonical progress still starts at sequence 1.

The regression makes:

- group 1 valid;
- group 2 invalid by a strict schema violation;
- groups 3 and 4 valid and already buffered.

Proven result:

- the drain accepts group 1 only;
- canonical `completed_required_count` advances by exactly 3;
- canonical expected sequence becomes 2;
- group 2 remains immutable in the buffer;
- groups 3 and 4 remain byte-for-byte unchanged in the buffer;
- no game from invalid group 2 is persisted individually;
- independent validation status records group 2 as `invalid` at the canonical expected position and groups 3/4 as `valid` but `later_buffered`;
- replanning from the resulting canonical manifest accepts zero further groups and stops again at sequence 2.

This proves later valid work cannot pass an earlier invalid group and that no per-game partial acceptance exists.

## No per-game retry/split architecture

No per-game transport, per-game retry state, per-game acceptance state, semantic repair loop, alternate corrected filename, automatic republish or automatic healing system was introduced.

The acceptance unit remains the immutable predeclared group. The focused regression additionally proves that when a 3-item group is invalid, zero members of that group are canonically persisted.

## CI, merge and activation evidence

Implementation PR #39 final head: `00f63fdac3bdecc35223b1ec9eaddfda56ede76a`.

Canonical PR CI:

- workflow: `Validate buffered Steam review dossier runtime`;
- run: `35187747977`;
- job: `105093367106`;
- conclusion: `success`;
- passed: compile, daily snapshot, buffered submission, same-day preservation, strict recovery, prepublication parity, contract-gap, package identity, and new parallel candidate validation/contiguous-prefix regression.

PR #39 merged as `7b18995ab813dabdc491697ac3fc3b3f6299adc6`.

Post-merge ownership validation:

- run: `35187773981`;
- job: `105093443973`;
- conclusion: `success`.

Automatic GitHub-owned pre-AI activation:

- workflow: `Build pre-AI deterministic payload`;
- run: `35187773986`;
- job: `105093444082`;
- conclusion: `success`;
- atomic pre-AI commit: `4cad3d7e2d5e01eefb96c99573979233833cf92a`.

The activation ran automatically from the merge; no Scheduled Task was manually run.

PR #40 was a two-file contract/test-only follow-up. GitHub did not emit a PR Actions check suite for #40 despite opened/synchronize/reopened events; its complete diff was reviewed before merge and contained only the status binding-name correction plus assertions. It merged as `29a3c178bd24874bcaa19c2a404e43db1e9f4078`. Runtime implementation and strict validator code were unchanged by #40.

## Fresh activated snapshot

Post-activation worker index:

- snapshot id: `d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71`;
- prepared date: `2026-09-17`;
- prepared required count: `633`;
- completed required count: `0`;
- remaining required count: `633`;
- canonical expected sequence: `1`;
- group count: `211`;
- `full_backlog_complete: false`;
- group size / checkpoint size: `3`.

Fresh compatibility binding includes:

- evidence contract revision: `parallel-buffer-validation-2026-09-17`;
- evidence contract SHA-256: `f12bd44759b52197f4908e0d0f8cadfcf0ceceec38cdee17df422da37c2e871a`;
- worker prompt SHA-256: `deb6d68227f47766c9f159d1461341f540a0f360e848e1c230eb6bf6e32a6478`.

The first descriptor is:

- sequence: `1`;
- start index: `0`;
- end index exclusive: `3`;
- appids: `2378500`, `1000360`, `1003590`;
- titles: `Baldur's Gate 3 - Digital Deluxe Edition DLC`, `Hellish Quart`, `Tetris® Effect: Connected`;
- group SHA-256: `86787700a4f6f224542a774408fd3336a24b71143cc7c28ed103380d7cbd234a`.

The first group therefore contains exactly three items. With 633 required items and checkpoint size 3, the activated plan has exactly 211 full 3-item groups and no tail in this snapshot.

## Scheduled Task confirmation

No Scheduled Task `Run now` occurred during implementation, CI, merge, activation validation or report preparation.

## Remaining risks

The repository-side architecture, deterministic regressions and automatic snapshot activation are validated, but the real Scheduled ChatGPT producer has not yet performed a live run under this new asynchronous contract. Therefore actual live evidence generation, sequential same-invocation publication while GitHub acceptance lags, and the resulting candidate-triggered validation status still require the deliberately separate live acceptance step. Also, the worker prompt revision label remains the historical `web-evidence-v2-prepublication-v1`; safety is content-complete because the active prompt content SHA-256 changed and is part of the compatibility binding, but the label is less descriptive than the new runtime semantics.

## Next step

Run the existing Scheduled Task exactly once and perform a separate READ/VALIDATE live acceptance of parallel buffering plus GitHub contiguous-prefix validation.
