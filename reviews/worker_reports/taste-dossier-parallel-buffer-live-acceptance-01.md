# Taste Dossier Parallel Buffer Live Acceptance 01 — worker report

Status: `partial_live_acceptance_more_runtime_evidence_needed`

Task: `taste-dossier-parallel-buffer-live-acceptance-01`
Repository: `kentrap2011-hub/steam-kz-deals-2`
Mode: `READ / VALIDATE`
Validated against `main` after the first real Scheduled ChatGPT run under the parallel-buffer contract.

No runtime, contract, prompt, schema, workflow, queue, cache, retry, or recovery fix was made. This report is the only intentional write from this task.

## Architecture preflight

PASS.

1. **Current owner of canonical scope/order/validation/persistence/progress:** GitHub control plane, per `config/execution_ownership_contract.json` and `config/taste_steam_review_dossier_contract.json`.
2. **Canonical authority for the observed behavior:** the active dossier contract, active web-evidence contract, active worker prompt, immutable worker index/group descriptors, GitHub candidate-ingest workflow, canonical work/progress state, and validation status.
3. **Control-plane transfer check:** none. Scheduled ChatGPT only performed bounded evidence synthesis plus create-only candidate publication; GitHub performed validation, persistence, progress advancement, and candidate cleanup.
4. **New scheduler/queue/retry/checkpoint/ownership check:** none. This task is read/validate only and introduces no new runtime responsibility.

The observed live path therefore stays inside the intended producer-buffer-validator ownership boundary.

## Authoritative user-supplied Scheduled Task result

The task file defines the following Scheduled Task result as authoritative UI evidence:

> Опубликован immutable candidate-buffer для группы 1 из 211. Это только transport/persistence progress, не canonical acceptance и не завершение snapshot. Canonical control plane на момент последней проверки всё ещё показывал canonical_expected_sequence=1, remaining_required_count=633.
>
> Следующая локальная группа по неизменившемуся плану — g000002 (Blacksad: Under the Skin, Prototype™, Welcome to Elk).

This UI result is consistent with the GitHub state at the candidate-publication commit: canonical progress had not yet advanced when the worker reported publication.

## Active snapshot, binding, and expected group

Active snapshot:

- `snapshot_id`: `d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71`
- `prepared_required_sha256`: `a73cb560704b79bf1069191dd1bd8d52af7e2c7969f619e3e9be11c7351fb95d`
- `group_plan_sha256`: `2d5453942dd473f73c18c6484ca57d1d4bca40a7c8dcce5f70766bfa3c378c45`
- prepared required count: `633`
- group count: `211`
- group/checkpoint size: `3`
- source queue SHA-256: `cda060dbcdbbf104fc87766bad7a35775ccaead0762e0678fb397f871e485cfa`

Active compatibility binding includes:

- evidence contract revision: `parallel-buffer-validation-2026-09-17`
- evidence contract SHA-256: `f12bd44759b52197f4908e0d0f8cadfcf0ceceec38cdee17df422da37c2e871a`
- worker schema revision: `contract-gaps-2026-09-17`
- worker schema SHA-256: `683c310bf9ea7364485f5e39456bcde0f5fb4a8cdf0106bb96d6aa9ea25b73be`
- worker prompt SHA-256: `deb6d68227f47766c9f159d1461341f540a0f360e848e1c230eb6bf6e32a6478`

The immutable expected descriptor `g000001` is exactly:

- sequence: `1`
- range: `[0, 3)`
- appids: `2378500`, `1000360`, `1003590`
- titles: `Baldur's Gate 3 - Digital Deluxe Edition DLC`, `Hellish Quart`, `Tetris® Effect: Connected`
- items SHA-256: `48256e357c57025236475a74cadcc1c2c64b72cbd199287869abe454712ab6bf`
- group SHA-256: `86787700a4f6f224542a774408fd3336a24b71143cc7c28ed103380d7cbd234a`

The next immutable descriptor `g000002` is exactly:

- sequence: `2`
- range: `[3, 6)`
- appids: `1003890`, `10150`, `1015940`
- titles: `Blacksad: Under the Skin`, `Prototype™`, `Welcome to Elk`
- items SHA-256: `c031ffaefcc0ca6bb47da3c747d6993f2b9ecb7ca90384d4a930efa66a85b975`
- group SHA-256: `aaf90ecbc631b2629dad2daf961878d646fe3599b294eb2d4131614b03ec786a`

## Exact candidate publication and identity

The real Scheduled worker published exactly the deterministic `g000001` candidate:

`data/ai_inbox/taste_steam_review_dossiers/d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71--g000001--86787700a4f6f224542a774408fd3336a24b71143cc7c28ed103380d7cbd234a.json`

Publication commit:

- commit: `b65df84316697b6de3728d4f1db50b3d07c3ffbc`
- message: `Buffer Taste Steam review dossier group 1`
- candidate file status in the commit: `added`
- candidate blob SHA: `6bdb9ba31fd695743d9d6ec5904d0d15f259ee62`
- the commit adds the single deterministic candidate file rather than updating an existing artifact.

The buffered object matches the active snapshot and exact `g000001` descriptor identity: sequence/range, ordered items, ordered appids, `items_sha256`, `group_sha256`, source queue binding, and the active evidence/prompt binding copied into its dossiers.

At that publication commit, the candidate directory contains exactly that one current-snapshot candidate. No `g000002` artifact is present there.

The exact deterministic `g000002` candidate path has no commit history at all for this snapshot:

`data/ai_inbox/taste_steam_review_dossiers/d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71--g000002--aaf90ecbc631b2629dad2daf961878d646fe3599b294eb2d4131614b03ec786a.json`

The current-snapshot inbox history for this live run consists of the `g000001` add followed by GitHub's drain/removal. Older `g000002`/`g000003` commits in the directory history belong to prior snapshots/runs and are not evidence for this invocation.

**Conclusion:** `g000002` was only named as the next local group in the authoritative UI result. It was not actually buffered. There is no GitHub evidence of any later current-snapshot group from this invocation.

## GitHub strict validation and canonical acceptance of g000001

The `g000001` publication commit automatically triggered:

- workflow: `Ingest Steam review dossier checkpoint`
- run: `35193329075`
- job: `105110653936`
- conclusion: `success`

The job successfully executed the relevant GitHub-owned stages:

1. `Drain maximal valid contiguous dossier prefix from current repository state`;
2. `Record strict validation status for all current-snapshot candidate groups`;
3. `Commit dossier recovery transport validation canonical progress and worker projection atomically`.

The active workflow's drain stage calls `scripts/ingest_taste_steam_review_dossier_inbox.py --reconcile-nonfatal`. Under the active contract this drain performs the canonical strict buffered validation before persistence and can advance only the maximal valid contiguous prefix.

GitHub then committed the accepted result as:

- commit: `9f2ee053f34c32dff5ab9d54ede44da84cf98d99`
- message: `Drain and validate Steam review dossier buffer`
- parent: the `g000001` publication commit `b65df84316697b6de3728d4f1db50b3d07c3ffbc`.

That single GitHub drain commit:

- removes the consumed immutable `g000001` candidate from the inbox;
- canonically persists all three dossiers (`App_2378500`, `App_1000360`, `App_1003590`);
- advances the work manifest/projection to the next exact group;
- advances canonical counts by exactly one 3-item group.

Therefore the durable state of `g000001` is **accepted and canonically persisted**, not pending and not merely buffered.

## Canonical progress before and after

Immediately after candidate publication and before GitHub drain acceptance:

- `canonical_expected_sequence = 1`
- `completed_required_count = 0`
- `remaining_required_count = 633`
- `full_backlog_complete = false`

After GitHub validation/persistence:

- `canonical_expected_sequence = 2`
- `completed_required_count = 3`
- `remaining_required_count = 630`
- `full_backlog_complete = false`

This is exactly one group of three items of canonical progress. It is consistent with the authoritative UI result having observed the control plane before the asynchronous GitHub drain completed.

## Durable validation status and invalid-state check

Current canonical observational status:

- `canonical_expected_sequence = 2`
- `completed_required_count = 3`
- `remaining_required_count = 630`
- `candidate_count = 0`
- `valid_candidate_count = 0`
- `invalid_candidate_count = 0`
- `invalid_expected_group = null`
- `candidate_groups = []`
- `malformed_current_snapshot_artifacts = []`
- `retry_state = false`

The zero candidate count is the correct post-drain state: the valid `g000001` candidate was consumed after canonical persistence. The status file is observational rather than canonical progress authority and therefore does not need to retain an `accepted` candidate record after cleanup.

**No durable invalid marker/status was produced for `g000001`. No strict validation defect was found.**

## Live proof matrix

| Intended property | Live result | Evidence / limitation |
| --- | --- | --- |
| Local Python/prepublication requirement removed in live runtime | **PROVEN LIVE** | Active contract/prompt explicitly make repository Python optional CI/developer parity only, and the real Scheduled worker successfully reached create-only publication instead of stopping on `prepublication_validator_unavailable`. |
| Create-only candidate publication works | **PROVEN LIVE** | `b65df843...` adds the deterministic immutable `g000001` path as a new file; no overwrite/update path was used. |
| GitHub validation of candidate works | **PROVEN LIVE** | Candidate push triggered run `35193329075`; strict drain/validation stages succeeded and GitHub persisted the group. |
| Canonical contiguous-prefix acceptance works | **PROVEN LIVE for the observed valid-prefix case** | With expected sequence `1` and only `g000001` present, GitHub accepted exactly that one group and moved to sequence `2` / `3 completed` / `630 remaining`. It did not cross the missing `g000002` gap. The separate invalid-middle-group branch remains deterministic-regression evidence rather than live evidence because this run produced no invalid candidate. |
| Same-invocation publication of multiple groups while canonical validation lags works | **UNPROVEN LIVE** | Only `g000001` was actually published. `g000002` was named as next but its deterministic path has no commit. No two current-snapshot candidate publications from this invocation exist to establish multi-group same-invocation buffering. |

## Is multi-group same-invocation buffering disproven?

No. It is **still unproven**, not disproven.

The active worker prompt requires local traversal from `N` to `N+1` after successful create-only publication without using lagging `canonical_expected_sequence` as the same-invocation gate. It also explicitly permits stopping on an ordinary invocation/time/runtime limit, a true liveness-binding change, descriptor inconsistency, or transport failure.

The authoritative UI result says `g000002` was the next local group and the plan was unchanged, but it does not supply an authoritative stop reason or evidence about the remaining runtime budget. GitHub proves only that `g000002` was not published. That is insufficient to distinguish an allowed invocation/runtime stop from an incorrect early stop, so this acceptance does not speculate or declare a runtime defect.

## Invalid/unvalidated-gap and per-game behavior

No canonical data crossed an invalid or unvalidated gap:

- canonical expected sequence began at `1`;
- only the exact current `g000001` candidate was present;
- GitHub strictly validated and persisted that group;
- canonical progress stopped at sequence `2`, where no current-snapshot candidate existed.

No per-game split/retry behavior appeared:

- the acceptance unit remained the exact group of three;
- all three dossier cache entries were persisted by the same GitHub drain commit;
- completed count advanced by exactly `3`;
- `retry_state` is `false`;
- no per-game candidate, retry, repair, or alternate publication artifact was created.

## Final acceptance classification

`partial_live_acceptance_more_runtime_evidence_needed`

Rationale: the first real run proves the removal of the local prepublication-Python gate, deterministic create-only candidate publication, automatic GitHub strict validation, whole-group canonical persistence, and correct one-group contiguous-prefix advancement. It does **not** prove the defining multi-group same-invocation buffering behavior because only `g000001` was published. There is no validation defect and no evidence sufficient to classify the absence of `g000002` as a worker defect.

## Exactly one next step

Run the existing Scheduled Task exactly once more under the unchanged current snapshot/binding and perform a narrowly targeted live validation of whether that single invocation publishes at least two consecutive planned groups in descriptor order without treating GitHub canonical acceptance as the worker's traversal gate.