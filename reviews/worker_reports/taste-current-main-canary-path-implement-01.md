# taste-current-main-canary-path-implement-01

## Task
Implement the approved lightweight read-only current-main canary preparation path for exactly one Taste AppID, without semantic execution, canonical writes, production rebuild, historical rerun, or Scheduled Task mutation.

## Lifecycle
- Status: `complete_implementation_ready_for_canary_execution`
- Completed UTC: `2026-09-09T15:59:00Z`
- Scope completed: implementation plus the explicitly allowed non-semantic, read-only preparation validation only.
- No real semantic Chernobylite canary was executed.

## Architecture preflight
- `config/execution_ownership_contract.json` keeps deterministic scope/queue construction and validation in the GitHub control plane; this implementation does not create or transfer a recurring semantic worker.
- The permanent workflow is manual `workflow_dispatch` only, has `contents: read`, checks out `refs/heads/main`, verifies `HEAD == refs/remotes/origin/main`, and has no schedule, commit, push, ingest, production mutation, or semantic step.
- The harness bounds the requested `App_<appid>` before invoking the existing Taste projection/payload producers. It reuses current producer code inside an output sandbox outside the repository checkout instead of forking Taste semantics.
- Broad StoreBrowse/AppDetails refresh is forbidden. The target must already have committed `storebrowse_basic_info` context; otherwise the harness fails closed.
- Canonical profile/wishlist network refetch is disabled for this path. Their binding/context is taken from source-aligned committed current-main pre-AI artifacts.

## Implementation
- Added `scripts/build_taste_current_main_canary.py` in commit `783ca99e928d7e9e2257fa9ebcfefb1354dd7ac6`.
  - accepts exactly one positive numeric AppID;
  - requires an empty output directory outside the repository checkout;
  - requires a clean checkout with `HEAD == refs/remotes/origin/main`;
  - resolves exactly one `App_<appid>` family and one mailing row before projection/payload expansion;
  - slices committed pre-AI snapshots to the target before calling the current production Taste projection/payload builders;
  - disables AppDetails fallback, canonical profile refetch, canonical wishlist refetch, semantics, ingest, and canonical persistence;
  - validates target-only projection, decision partition, queue cardinality `0..1`, and profile/model/semantics/fingerprint/context bindings;
  - writes only temporary proof files outside the checkout and removes its temporary workspace;
  - proves clean repository state before/after.
- Added `tests/test_taste_current_main_canary.py` in commit `79dfbc20eebcb6a4eab8b6b1a8bfe40a6b075c08`.
- Added permanent `.github/workflows/taste-current-main-canary.yml` in commit `1f94f11f88d86d6c781038dbcee0be59541a033c`.
  - trigger: `workflow_dispatch` only;
  - required input: one `appid`;
  - permissions: `contents: read`;
  - checkout: `refs/heads/main`, `fetch-depth: 0`, `persist-credentials: false`;
  - no schedule, push trigger, semantic step, ingest step, git push, or production write;
  - uploads only the temporary canary proof artifact.

## Focused tests
- Local syntax/import validation passed.
- Local focused unit suite: 7/7 passed.
- GitHub runner focused unit suite in validation run: 7/7 passed.
- Covered: exactly-one numeric AppID, one-family bounding, output isolation outside checkout, queue cardinality `0..1`, binding consistency, other-AppID leakage rejection, fail-closed missing/ambiguous candidate context, and valid zero-queue partition behavior.

## Allowed non-semantic validation
- Temporary validation workflow existed only to exercise the new preparation path because the available connector could not dispatch the permanent manual workflow directly.
- Validation workflow permissions were `contents: read`; it contained no semantic, ingest, push, production-write, or Scheduled Task operation.
- GitHub Actions run: `34373498797`.
- GitHub Actions job: `102540326726`.
- Validation head SHA: `63c19eb2a60fdbc23c5d4191ce6e520136d36ce2`.
- Run conclusion: `success`.
- Preparation-only step conclusion: `success`.
- No-repository/no-production-write proof step conclusion: `success`.
- Temporary artifact upload conclusion: `success`.
- Temporary artifact ID: `10112872321`.
- Artifact ZIP digest: `sha256:adea459f3597b7596a57dfaace0b1ba6509129e47d30e6de59a0a7a12135575b`.
- Temporary validator removed in commit `ef0cbfdfa100f3bb5d04b767b8b338873b62cdb1`; `.github/workflows/taste-current-main-canary-validation.yml` is absent from current `main` after cleanup.

## Current-main proof
- Requested AppID: `1016800`.
- Taste subject key: `App_1016800`.
- Target subject count: `1`.
- Checked-out HEAD: `63c19eb2a60fdbc23c5d4191ce6e520136d36ce2`.
- Resolved `origin/main`: `63c19eb2a60fdbc23c5d4191ce6e520136d36ce2`.
- `HEAD == origin/main`: `true`.
- Source mailing timestamp: `2026-09-08T20:46:16.637935+00:00`.
- Repository status before: clean.
- Repository status after: clean.
- `git diff --exit-code` after preparation: `0`.
- Candidate context provenance: `storebrowse_basic_info`.
- Direct committed description count: `1`.
- AppDetails fallback requested: `0`.

## Taste bindings and decision proof
- Canonical profile identity: `kentrap2011-hub/stopgame-ratings-data:gaming_taste_live.json`.
- Profile blob SHA: `191b6d6c5dec2f9ef2976517f301528740f9bec2`.
- Taste model: `taste-v3`.
- Taste semantics SHA256: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`.
- Target Taste fingerprint: `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`.
- Candidate-context SHA256: `2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`.
- Raw deterministic status: `ai_required`.
- Raw deterministic reason: `taste_cache_key_missing`.
- Queue decision: `semantic_queue_row`.
- Queue cardinality: `1`.
- Queue row AppID: `1016800` only.
- Queue row fingerprint equals projection fingerprint: yes.
- Queue row candidate-context digest equals projection digest: yes.
- Decision partition: queue `1`, ready-without-AI `0`, deterministically-excluded `0`.
- No other AppID leaked into the bounded projection or queue.

## Runtime
- Preparation harness elapsed: `0.510 s`.
- Taste projection elapsed: `0.250 s`.
- Payload/queue preparation elapsed: `0.008 s`.
- Measured end-to-end preparation command wall-time on GitHub runner: `0.580 s`.
- Full validation job ran from `2026-09-09T15:56:11Z` to `2026-09-09T15:56:23Z`, including checkout/setup/tests/artifact upload.

## Safety assertions
- Chernobylite semantic execution attempted: `false`.
- Canonical Taste ingest attempted: `false`.
- Production write attempted: `false`.
- StoreBrowse refresh attempted: `false`.
- Steam AppDetails fallback attempted: `false`.
- Canonical profile refetch attempted: `false`.
- Canonical wishlist refetch attempted: `false`.
- Outputs outside repository checkout: `true`.
- Repository clean before/after: `true`.
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` modified: `false`.
- Production rebuild: not performed.
- Historical workflow rerun: not performed.
- Paid API / Copilot / external scheduler: not used.
- Canonical Taste data: not written.
- System Audit: not started.
- Next task: not started.

## Result
The permanent current-main one-AppID Taste preparation path is implemented and verified non-semantically. It is bounded before projection/payload expansion, read-only with respect to the repository and production state, produces an auditable temporary proof artifact, preserves current Taste bindings, and completes the tested preparation command in under one second on the validation runner. The real semantic Chernobylite canary remains deliberately unexecuted.

## Final status
`complete_implementation_ready_for_canary_execution`
