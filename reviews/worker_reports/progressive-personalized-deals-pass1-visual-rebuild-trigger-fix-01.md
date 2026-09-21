# Progressive PASS 1 Visual Rebuild Trigger Fix 01

## 1. Task / repo / mode

- Task: `WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_PASS1_VISUAL_REBUILD_TRIGGER_FIX_01.md`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Source of truth: `main`
- Mode: `IMPLEMENT / ACTIVATE / VALIDATE`
- Date: 2026-09-21
- Final status: `complete_ready_for_director_acceptance`

This task fixed only the missing downstream edge from accepted Progressive PASS 1 ingest to the existing GitHub-owned progressive visual/site refresh path.

No Scheduled PASS 1 semantic worker run, incomplete-item retry, new semantic result artifact, or PASS 2 execution was performed.

## 2. Architecture / ownership preflight

Canonical ownership was checked before implementation.

`config/execution_ownership_contract.json` assigns Progressive Phase B PASS 1 to the GitHub control plane and explicitly includes:

- semantic generation identity;
- current PASS 1 scope/order;
- attempt state;
- validation/persistence;
- processing counts;
- `visual_rebuild_trigger`.

The existing owners are:

- PASS 1 ingest: `.github/workflows/ingest-progressive-pass1.yml`;
- progressive visual projection/rebuild: `.github/workflows/build-daily-visual-payload.yml` plus the existing progressive routing/build scripts;
- site publication: `.github/workflows/deploy-visual.yml`.

No ownership moved to Scheduled ChatGPT or the interactive chat. No new scheduler, queue, retry loop, checkpoint owner, or semantic execution path was introduced.

The narrowest safe integration was to add the existing `Ingest Progressive PASS 1 item` workflow as another `workflow_run` upstream of the existing `Build daily visual payload` workflow.

This preserves the normal chain:

`Scheduled semantic worker -> PASS 1 inbox -> GitHub ingest -> durable state/work commit -> Build daily visual payload -> Deploy visual mailing`.

## 3. Exact defect cause

Before the fix, `Build daily visual payload` already contained all required projection logic:

- `scripts/progressive_visual_activation_routing.py` compares the canonical PASS 1 state blob stored in the visual provenance against current `data/cache/progressive_pass1_state.json`;
- a PASS 1 state mismatch sets `full_progressive_build_required=true`;
- the build workflow checks out current `main`, rebuilds the full progressive visual, persists it, emits a freshness receipt, and the existing deploy workflow publishes it.

The missing edge was trigger wiring.

Before the fix, `Build daily visual payload` listened to `workflow_run` completion for:

- `Build pre-AI deterministic payload`;
- `Ingest context-bound taste batch`;

but not:

- `Ingest Progressive PASS 1 item`.

The build workflow also had a `push` path for `data/cache/progressive_pass1_state.json`, but the PASS 1 state commit is created from inside the ingest GitHub Actions workflow. The accepted live run demonstrated that this did not start a downstream visual build.

Therefore accepted PASS 1 state/work could become durable while the published visual remained bound to the older PASS 1 state blob.

## 4. Implementation

Implementation commit:

`831e39109e6175abb3883be596691d039efc2baf`
— `Trigger visual rebuild after Progressive PASS1 ingest`

Changed exactly two implementation files:

1. `.github/workflows/build-daily-visual-payload.yml`
   - added `"Ingest Progressive PASS 1 item"` to the existing `workflow_run.workflows` list;
   - retained existing `daily-visual-payload` concurrency with `cancel-in-progress: true`;
   - retained checkout of current `main`, existing routing, build, persistence and freshness-receipt logic.

2. `scripts/test_progressive_visual_activation_routing.py`
   - added ROUTE-00 regression requiring the build workflow to retain the PASS 1 ingest upstream trigger.

Exact implementation blobs after commit:

- build workflow blob: `8278cdea5e05f242140c65f8d721dc91e4427c30`;
- routing regression blob: `9ebcc2f1622490ba398e3a213865c8e78b34aa9f`.

No production semantic prompt or PASS 1/PASS 2 contract was changed.

## 5. Trigger ordering and multi-item safety

The new downstream event is `workflow_run: completed` for `Ingest Progressive PASS 1 item`.

The build job already requires, for workflow-run invocations:

- upstream conclusion `success`;
- upstream head branch `main`.

The ingest workflow's successful completion occurs only after its canonical validation/ingest/revalidation and `Commit PASS 1 state and remaining work` step succeeds.

Therefore an accepted result cannot cause the new downstream build before the ingest workflow has completed its durable-state step.

Several closely spaced accepted ingests remain safe because the existing visual workflow keeps:

- concurrency group `daily-visual-payload`;
- `cancel-in-progress: true`;
- `Checkout current main` before classification/build.

Each surviving build therefore projects from current canonical GitHub state rather than from event-local attempt counters. A later invocation supersedes an older in-flight visual build instead of allowing an older event payload to become a second state owner.

## 6. Before activation

Canonical PASS 1 state immediately before implementation activation:

- `data/cache/progressive_pass1_state.json`
  - blob: `d9aae43a3ab2564321b6939a06398d49a0fd4ac7`;
  - durable entries: `6`.

Current PASS 1 work:

- `data/production/pre_ai/progressive_pass1_work.json`
  - blob: `d29dfe64096f84fe70680d2b6f1cfbd12797ff83`;
  - current total scope: `493`;
  - attempted: `5`;
  - remaining: `488`;
  - expired-before-PASS1: `228`;
  - PASS 1 active;
  - PASS 2 inactive.

Stale visual before the fix, from the preceding live-acceptance proof:

- `data/production/visual/current.json`
  - blob: `afd90ca08a7627a86a581ca0ae659ad56508ab39`;
  - visible/current rows: `720`;
  - analyzed fit: `0`;
  - analysis incomplete: `0`;
  - not analyzed: `720`;
  - PASS 1 attempted shown: `0`;
  - PASS 1 remaining shown: `720`.

That visual was stale relative to the already durable PASS 1 state.

## 7. Activation

The implementation push automatically started the existing canonical visual workflow; no semantic worker was invoked.

Visual build:

- workflow: `Build daily visual payload`;
- run ID: `35642575257`;
- event: `push`;
- conclusion: `success`;
- implementation head: `831e39109e6175abb3883be596691d039efc2baf`;
- scope job: `106475178585`;
- build job: `106475294714`.

The routing step reported:

- `source_integrity_ok=true`;
- `compatible=false`;
- `full_progressive_build_required=true`;
- reason: `progressive_pass1_state_provenance_mismatch`.

It then selected:

`VISUAL_SCOPE full_progressive_build=true reason=progressive_visual_incompatible`

and explicitly disabled bounded giveaway/commercial refresh for this invocation.

Relevant progressive regressions passed inside the build:

- `progressive visual activation routing regression: ok`;
- `progressive personalization Phase A fallback / Phase B regression: ok`;
- `progressive PASS 1 item-level regression: ok`;
- `progressive unresolved row preservation regression: ok`.

The producer reported before current-expiry filtering:

`visual progressive items=721 total=721 fit=3 incomplete=3 not_analyzed=715`

and then built the current visual with:

- `items=493`;
- `expired_removed=228`.

The canonical visual commit produced by the normal workflow is:

`22cc8c47635fb8a6521446a4395eac22460e7e95`
— `Refresh daily visual payload`

Current visual blob after activation:

`f2619b2f640b57c1795bdf18629546196402a3c9`.

## 8. After activation: canonical counts and item projection

PASS 1 state/work blobs did not change during activation:

- state blob remains `d9aae43a3ab2564321b6939a06398d49a0fd4ac7`;
- work blob remains `d29dfe64096f84fe70680d2b6f1cfbd12797ff83`;
- inbox contains no Progressive PASS 1 result artifacts.

Therefore activation caused no new semantic PASS 1 attempts.

Current canonical scope remains:

- total current PASS 1 scope: `493`;
- current attempted: `5`;
- current remaining: `488`;
- expired-before-PASS1: `228`;
- PASS 2 inactive.

The six historical durable entries consist of:

- 3 `analyzed_fit`;
- 3 `analysis_incomplete`.

Tower Dominion is the accepted incomplete entry that is no longer in the current 493-item scope after expiry. Therefore the current 493-item projection reconciles as:

- analyzed fit: `3`;
- analyzed not fit: `0`;
- analysis incomplete: `2`;
- not analyzed: `488`;
- analyzed success: `3`;
- normal visible: `493`;
- PASS 1 attempted: `5`;
- PASS 1 remaining: `488`.

Arithmetic:

`493 = 3 fit + 0 not-fit + 2 incomplete + 488 not-analyzed`

and:

`493 = 5 attempted + 488 remaining`.

The current ranking review confirms accepted visible results now project ahead of untouched work:

1. Green Hell — `fit=moderate`;
2. Lucid Blocks — `fit=moderate`;
3. SAEKO: Giantess Dating Sim — `fit=moderate`;
4. Star Traders: Frontiers — accepted incomplete;
5. Sweet Home — accepted incomplete;
6+ — untouched current work.

Before the rebuild all five of those still-current accepted items were falsely displayed from the stale payload as `not_analyzed` / Tier 3. The refreshed projection now reflects the three fit results as fit-bearing Tier-1 rows and places the two incomplete results ahead of untouched Tier-3 work, consistent with the canonical tier order.

## 9. Site publication / deployment

The normal existing deploy path ran after the visual build.

Deploy:

- workflow: `Deploy visual mailing`;
- run ID: `35642669590`;
- event: `workflow_run`;
- conclusion: `success`;
- deployed visual commit: `22cc8c47635fb8a6521446a4395eac22460e7e95`;
- deploy job: `106475490132`.

Successful deploy checks included:

- visual freshness receipt contract;
- exact triggering build receipt download;
- general visual mutation classification;
- meaningful Russian-description validation;
- giveaway payload validation;
- UI regressions;
- staged precomputed payload;
- binding staged publication to the exact triggering build freshness receipt;
- Pages artifact upload;
- GitHub Pages deployment.

Freshness proof:

`VISUAL_FRESHNESS=fresh scope=full_visual run_id=35642575257 ... visual_blob=f2619b2f640b57c1795bdf18629546196402a3c9 visual_commit=22cc8c47635fb8a6521446a4395eac22460e7e95`

and:

`VISUAL_PUBLICATION_OUTCOME=fresh`.

Thus the normal publication/deploy path served the refreshed canonical visual artifact rather than the stale pre-PASS1 projection.

## 10. FIX-01..10

- FIX-01 — **PASS**: ingest/rebuild/publication remain GitHub-owned; existing build/deploy paths are reused.
- FIX-02 — **PASS**: new trigger is downstream `workflow_run: completed`; build accepts successful `main` upstream completion only, after ingest's durable commit step.
- FIX-03 — **PASS**: existing `daily-visual-payload` concurrency uses `cancel-in-progress: true`; every build checks out current `main`, preventing event-local stale counters from becoming authority.
- FIX-04 — **PASS**: activation routing compared current canonical PASS 1 state blob to visual provenance and rebuilt on `progressive_pass1_state_provenance_mismatch`.
- FIX-05 — **PASS**: already accepted PASS 1 state was rebuilt/published without another semantic `Run now`.
- FIX-06 — **PASS**: current counts reconcile at `493 = 5 + 488`, with current semantic breakdown `3 fit + 2 incomplete + 488 not-analyzed`; expired-before-PASS1 remains `228`.
- FIX-07 — **PASS**: the three accepted fit items now carry `moderate` fit in the refreshed ranking; accepted incomplete Star Traders and Sweet Home are projected immediately after them and before untouched current work instead of remaining stale Tier 3.
- FIX-08 — **PASS**: PASS 1 state/work blobs remained unchanged during activation, inbox is empty, no semantic worker ran, no incomplete retry occurred, PASS 2 remains false.
- FIX-09 — **PASS**: normal deploy run `35642669590` succeeded and publication freshness is `fresh` for visual commit `22cc8c47…`.
- FIX-10 — **PASS**: routing, progressive personalization, PASS 1 item-level, unresolved-row preservation, visual freshness, description/giveaway and UI regressions all passed in the normal build/deploy chain. Execution ownership validation run `35642575303` also succeeded.

## 11. No semantic side effects

Before implementation:

- PASS 1 state blob: `d9aae43a3ab2564321b6939a06398d49a0fd4ac7`;
- PASS 1 work blob: `d29dfe64096f84fe70680d2b6f1cfbd12797ff83`;
- current attempted: `5`;
- current remaining: `488`;
- PASS 2: false.

After activation/deployment:

- PASS 1 state blob: unchanged;
- PASS 1 work blob: unchanged;
- current attempted: `5`;
- current remaining: `488`;
- PASS 2: false;
- Progressive PASS 1 inbox: empty.

Therefore this task performed projection/publication only and did not advance semantic execution.

## 12. Status

`complete_ready_for_director_acceptance`

The confirmed downstream defect is fixed and the already accepted canonical PASS 1 state has been projected and published through the existing GitHub-owned visual/site path.

## 13. Exactly one recommended next step

Return to Director to accept this fix and close the outstanding Progressive PASS 1 live-acceptance publication defect; no additional semantic `Run now` is required to validate this fix.

## 14. Exact refs

- task: `WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_PASS1_VISUAL_REBUILD_TRIGGER_FIX_01.md`
- prior live acceptance report: `reviews/worker_reports/progressive-personalized-deals-phase-b-pass1-live-acceptance-01.md`
- ownership contract: `config/execution_ownership_contract.json`
- PASS 1 contract: `config/progressive_pass1_contract.json`
- implementation commit: `831e39109e6175abb3883be596691d039efc2baf`
- implementation workflow blob: `8278cdea5e05f242140c65f8d721dc91e4427c30`
- regression blob: `9ebcc2f1622490ba398e3a213865c8e78b34aa9f`
- activation build run: `35642575257`
- activation scope job: `106475178585`
- activation build job: `106475294714`
- visual commit: `22cc8c47635fb8a6521446a4395eac22460e7e95`
- visual blob after activation: `f2619b2f640b57c1795bdf18629546196402a3c9`
- deploy run: `35642669590`
- deploy job: `106475490132`
- execution ownership validation run: `35642575303`
- PASS 1 state blob before/after: `d9aae43a3ab2564321b6939a06398d49a0fd4ac7`
- PASS 1 work blob before/after: `d29dfe64096f84fe70680d2b6f1cfbd12797ff83`
- stale visual blob before fix: `afd90ca08a7627a86a581ca0ae659ad56508ab39`
