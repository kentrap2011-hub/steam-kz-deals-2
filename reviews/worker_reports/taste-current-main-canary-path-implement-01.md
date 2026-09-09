# taste-current-main-canary-path-implement-01

## Task
Implement the approved lightweight read-only current-main canary preparation path for exactly one Taste AppID, without semantic execution, canonical writes, production rebuild, historical rerun, or Scheduled Task mutation.

## Lifecycle
- Status: `in_progress`
- Last checkpoint UTC: `2026-09-09T15:55:40Z`
- Current state: implementation is committed; the only remaining work is the explicitly permitted non-semantic preparation-only validation with a temporary artifact.
- Next concrete action: trigger the temporary read-only validation path against current `main`, record the exact GitHub Actions run/job IDs immediately, inspect no more than the anti-stall limit, then remove the temporary validator and finalize this report.

## Architecture preflight
- `config/execution_ownership_contract.json` keeps deterministic scope/queue construction and validation in the GitHub control plane; this implementation does not create or transfer a recurring semantic worker.
- The permanent workflow is manual `workflow_dispatch` only, has `contents: read`, checks out `refs/heads/main`, verifies `HEAD == refs/remotes/origin/main`, and has no schedule, commit, push, ingest, or semantic step.
- The harness bounds the requested `App_<appid>` before invoking the existing Taste projection/payload producers. It reuses current producer code inside an output sandbox outside the repository checkout rather than forking Taste semantics.
- Broad StoreBrowse/AppDetails refresh is forbidden. The target must already have committed `storebrowse_basic_info` context; otherwise the harness fails closed.
- Canonical profile/wishlist network refetch is disabled for this path. Their binding/context is taken from the source-aligned committed current-main pre-AI artifacts.

## Changes
- Added `scripts/build_taste_current_main_canary.py` (`783ca99e928d7e9e2257fa9ebcfefb1354dd7ac6`).
- Added `tests/test_taste_current_main_canary.py` (`79dfbc20eebcb6a4eab8b6b1a8bfe40a6b075c08`).
- Added `.github/workflows/taste-current-main-canary.yml` (`1f94f11f88d86d6c781038dbcee0be59541a033c`).
- Permanent workflow has no `schedule`, no push trigger, no write permission, and uploads only temporary proof artifacts.

## Validation
- Local syntax/import validation passed for the new harness/tests.
- Focused local unit suite: 7 tests passed.
- Covered: exactly-one numeric AppID, one-family bounding, output isolation outside checkout, queue cardinality `0..1`, queue/profile/model/context binding consistency, other-AppID leakage rejection, and fail-closed missing/ambiguous candidate context.
- Current-main preparation-only GitHub Actions validation: pending.

## Safety state before runtime validation
- Chernobylite semantic evaluation: not run.
- `scripts/ingest_taste_results.py`: not run.
- Canonical Taste cache/overlay writes: not performed.
- Production rebuild / historical workflow rerun: not performed.
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9`: not modified.
- Paid API / Copilot / external scheduler: not used.

## Unresolved
- Need one real preparation-only execution to prove current-main SHA provenance, target cardinality, no production mutation, bindings, and wall runtime on GitHub runner.

## Final status
- pending
