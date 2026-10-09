# WORKER TASK — Dossier two-stage asynchronous pipeline amendment 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Mode: `ARCHITECTURE AMEND / IMPLEMENT INACTIVE / VALIDATE`

## User-approved correction

The two semantic stages must NOT use a synchronous per-item handshake with GitHub.

Research must not:
`finish item A -> wait for GitHub acceptance -> receive permission -> start item B`.

Assembly must not:
`finish dossier A -> wait for GitHub acceptance -> receive permission -> start dossier B`.

GitHub remains the authority for queue/order/bindings/validation/acceptance/recovery, but it must operate asynchronously around continuously working semantic stages.

## Target steady-state model

Research:
- receives GitHub-prepared bounded work ahead of time / buffered manifest;
- processes its exact authorized items in order;
- after emitting the create-only Research result for item A, immediately proceeds to the next already-authorized Research item;
- does not wait for acceptance/rejection of A before starting B;
- does not choose/reorder/expand scope or invent retries.

GitHub Research ingest:
- asynchronously validates submitted Research packages;
- writes accepted/rejected receipts/state;
- accepted packages become eligible for Assembly staging;
- rejection of one item affects only that item.

Assembly:
- consumes a GitHub-prepared buffer/manifest of already accepted Research packages;
- after emitting the create-only Assembly/Dossier candidate for item A, immediately proceeds to the next already-authorized Assembly item;
- does not wait for final GitHub acceptance/rejection of A before starting B;
- does not choose/reorder/expand scope or invent retries.

GitHub Assembly/final ingest:
- asynchronously validates Assembly outputs through the unchanged strict final Dossier authority;
- canonical acceptance/recovery remains GitHub-owned;
- failure of one item must not block unrelated accepted work.

The pipeline should be capable of steady state:
`Research N+1` while `Assembly N` while GitHub independently ingests earlier Research/Assembly outputs.

## Scope

Amend the accepted inactive P1/P2 architecture/contracts/staging implementation from PRs #171/#173/#175 so their lifecycle semantics explicitly support the asynchronous buffered model above.

Implement only the deterministic/inactive control-plane changes required for that model.

Do NOT implement the Research or Assembly semantic prompts/workers in this task.

## Required design properties

1. **No per-item blocking acknowledgement**
   - submission of one Research or Assembly artifact is not a prerequisite for starting the next pre-authorized item;
   - worker liveness must not depend on observing its immediately preceding acceptance receipt.

2. **GitHub-owned preauthorization**
   - Research may only process items already present in an immutable GitHub-prepared Research work buffer/manifest;
   - Assembly may only process items already present in an immutable GitHub-prepared Assembly work buffer/manifest derived from accepted Research packages;
   - workers cannot self-assign additional items.

3. **Buffered independence**
   - support multiple Research assignments already available to Research;
   - support multiple accepted Research packages / Assembly assignments already available to Assembly;
   - one rejected/stale/malformed item does not stall subsequent unrelated authorized items.

4. **Immutable bindings**
   Preserve exact game/snapshot/group/assignment/package/result bindings and create-only semantics.

5. **Out-of-order completion safety**
   Semantic completion timing may differ from GitHub ingestion timing.
   Validation/acceptance must remain deterministic even if later authorized work finishes before earlier GitHub ingest completes, where contractually safe.
   Canonical order/accounting remains GitHub-owned.

6. **Retry/recovery**
   GitHub alone decides retry/recovery.
   A worker never retries an item merely because it has not yet seen an acknowledgement.
   Retry work must appear as a new explicit GitHub authorization.

7. **No hidden global barrier**
   Do not require an entire Research group/buffer to be accepted before unrelated accepted members can feed Assembly unless the unchanged strict final canonical group boundary truly requires it.
   Keep final canonical Dossier validation semantics unchanged.

8. **Backpressure**
   Define deterministic bounded buffers so GitHub can prevent unbounded staging while still keeping both semantic workers busy.
   Backpressure must be based on queue/buffer capacity, not synchronous item-by-item waiting.

## Required tests

Add deterministic tests proving at minimum:

- Research item B remains authorized/executable after Research A is submitted but before A has an acceptance receipt.
- Research rejection for A does not revoke unrelated preauthorized B/C.
- Assembly item B remains authorized/executable after Assembly A is submitted but before final A acceptance.
- Assembly rejection for A does not revoke unrelated B/C.
- Assembly can consume already accepted Research work while Research continues with later items.
- stale/mismatched/duplicate artifacts still fail closed.
- workers cannot invent new scope/retries.
- bounded buffer/backpressure is deterministic.
- current one-stage Dossier authority is unchanged.
- all two-stage contracts remain inactive/non-authoritative.

## Compatibility / boundaries

- Current one-stage Dossier remains production authority.
- Strict Dossier validator remains unchanged unless a test-only interface adaptation is strictly required; never weaken its semantics.
- No production activation.
- No Research semantic worker.
- No Assembly semantic worker.
- No Deep/ranking/Steam/translation/UI changes.
- Do not modify current commercial refresh behavior.
- No Scheduled Task / automation changes.
- Do not create a second scheduler or queue owner.

## Deliverable

Create:
`reviews/worker_reports/dossier-two-stage-async-pipeline-amendment-01.md`

Report:
1. old blocking semantics found in P1/P2;
2. exact new asynchronous lifecycle;
3. buffer/backpressure semantics;
4. files changed;
5. tests for non-blocking progress and failure isolation;
6. proof current one-stage production is untouched;
7. what remains for future Research and Assembly semantic worker implementation.

Create PR and stop.