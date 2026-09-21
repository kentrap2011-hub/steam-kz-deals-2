# Progressive PASS 2 Dossier-Ready Gate Amendment 01

## Task / mode / result

- Task: `WORKER_TASK_PROGRESSIVE_PASS2_DOSSIER_READY_GATE_AMENDMENT_01.md`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Source of truth: `main`
- Mode: canonical rule amendment only; no PASS 2 implementation or production execution
- Final status: `complete_ready_for_director_acceptance`

The canonical Progressive Personalized Deals design now requires a current exact-compatible canonically accepted Taste Steam Review Dossier before a specific `analysis_incomplete` item can become PASS 2 eligible. PASS 1 and future PASS 2 are independent GitHub-owned flows and no longer have a global PASS 1 completion barrier between them.

## Files changed

### Canonical rule surfaces

1. `config/progressive_personalization_contract.json`
   - version 2 -> 3;
   - added GitHub ownership for PASS 2 eligibility/order/state/attempt accounting;
   - added `phase_c_pass2_design` as canonical design-only, inactive, not implemented;
   - defined the exact Dossier-ready eligibility predicate, zero-attempt waiting semantics, parallel PASS 1/PASS 2 rule, bounded attempt budget, Dossier acceptance transition, and activation guard.

2. `PROJECT_DECISIONS.md`
   - added `PPD-003 — PASS 2 is dossier-ready per item and independent from global PASS 1 completion`;
   - records the rationale and supersedes the old global `not_analyzed_count == 0` PASS 2 start barrier.

### Historical reconciliation

3. `reviews/worker_reports/progressive-personalized-deals-architecture-amendment-01.md`
   - added an explicit supersession note above the old PASS 2 start section;
   - preserves the historical text but makes clear that its global PASS 1 completion barrier is no longer current.

### Operational handoff only

4. `CURRENT_TASK.md`
   - tracked this worker task while in progress; it is closed to the completed state after report creation.

No Dossier evidence/schema/persistence semantics were changed. No PASS 1 worker behavior was changed.

## Architecture preflight

- Current owner of scope/order/state/retry/validation/persistence: GitHub control plane, per `config/execution_ownership_contract.json`.
- Current PASS 1 owner remains GitHub; Scheduled ChatGPT remains bounded lightweight semantic data-plane only.
- Dossier canonical acceptance/persistence remains GitHub-owned under `config/taste_steam_review_dossier_contract.json` and `config/taste_steam_review_dossier_persistence_bridge.json`.
- This amendment does not transfer queue, retry, state, eligibility, or orchestration ownership into Scheduled ChatGPT or interactive chat.
- No new runtime scheduler, queue processor, recurring stage, or production executor was created by this task.
- PASS 2 remains inactive and unimplemented until a separate implementation task.

## Old rule vs new rule

### Old rule

The earlier architecture report stated:

- PASS 2 starts only after PASS 1 has covered the whole current semantic candidate set;
- operationally this meant `not_analyzed_count == 0`.

That rule delayed recovery even when a particular incomplete item already had enough Dossier evidence for a bounded second pass.

### New rule

There is no global PASS 1 completion gate for PASS 2.

- PASS 1 continues processing current `not_analyzed` items.
- PASS 2 may consider only current `analysis_incomplete` items.
- A specific incomplete item becomes PASS 2 eligible only after GitHub can prove a current exact-compatible canonically accepted Dossier for the same item/work identity.
- PASS 1 does not wait for PASS 2.
- PASS 2 does not wait for full PASS 1 coverage.
- A failure or wait state in one pass does not block the other.

The prior global barrier is explicitly superseded by `PPD-003` and `config/progressive_personalization_contract.json#phase_c_pass2_design`.

## Exact PASS 2 eligibility predicate

For a current item, GitHub may project `pass2_eligible=true` only when **all** of the following are true:

1. Current progressive state is exactly `analysis_incomplete`.
2. The incomplete PASS 1 state is current:
   - `pass1_state.semantic_generation_id == current_progressive_semantic_generation_id`;
   - `pass1_state.work_id == current_item.work_id`.
3. Automatic PASS 2 attempts consumed for that exact `semantic_generation_id + work_id` are `0`.
4. A Dossier exists in the canonical GitHub-owned Dossier store and was accepted/persisted by the canonical GitHub Dossier ingest/validation path.
5. A merely buffered or worker-produced candidate Dossier is insufficient.
6. Exact item identity matches:
   - `dossier.appid == current_item.appid`;
   - `dossier.game_identity.work_title == current_item.semantic_input.title`;
   - when the current item exposes a release year, `dossier.game_identity.release_year == current_item.release_year`;
   - identity is resolved under the current Dossier identity rules;
   - cross-release combination/ambiguity is forbidden.
7. Dossier compatibility is current:
   - `dossier.web_evidence_contract_binding` exactly equals the current active content-complete Dossier compatibility binding required by the canonical Dossier schema/evidence/prompt contracts.
8. Dossier freshness is current at eligibility evaluation time:
   - stale or expired Dossier is not eligible.
9. The future GitHub PASS 2 work unit is immutably bound to:
   - current `semantic_generation_id`;
   - current `work_id`;
   - current `appid`;
   - exact accepted Dossier content SHA-256;
   - current Dossier compatibility binding.

If any one of these conditions is false, the item is not PASS 2 eligible.

## Dossier-ready transition

Before Dossier acceptance:

- item remains `analysis_incomplete`;
- item remains visible in Tier 2;
- item is PASS2-pending but not PASS 2 eligible;
- waiting consumes exactly zero PASS 2 attempts.

After canonical Dossier acceptance:

- the GitHub Dossier persistence/acceptance event becomes an input to PASS 2 eligibility projection;
- GitHub re-evaluates pending `analysis_incomplete` items;
- only the exact matching current item/work identity may be added to future PASS 2 work;
- no interactive intervention is required;
- the Dossier worker itself does not enqueue PASS 2 directly.

A stale, expired, wrong-app, wrong-work, cross-release, ambiguous, or compatibility-mismatched Dossier cannot unlock recovery.

## Attempt budget

For one current `semantic_generation_id + work_id`:

- maximum automatic PASS 2 recovery attempts: **1**;
- waiting for Dossier: **0 attempts consumed**;
- stale/mismatched Dossier: **0 attempts consumed**;
- eligibility projection: **0 attempts consumed**;
- queue presence alone: **0 attempts consumed**;
- price/commercial refresh does not reset the budget;
- a newer Dossier for the same semantic generation/work identity does not reset the budget.

The future implementation must let GitHub consume the one automatic attempt only from either:

- an exact-bound accepted PASS 2 result, or
- an explicit GitHub-owned terminal execution receipt proving the authorized eligible attempt actually ran.

Mere waiting, enqueueing, stale work, or unbound artifacts consume zero attempts.

After the single automatic PASS 2 attempt is consumed without a trustworthy fit/not-fit resolution:

- state remains `analysis_incomplete`;
- the item stays visible in Tier 2;
- automatic PASS 2 eligibility ends for that `semantic_generation_id + work_id`;
- automatic recovery may become available again only if the current semantic generation or work identity changes under the existing semantic-generation rules.

This prevents an infinite retry loop.

## Independent parallel ownership

PASS 1 and PASS 2 are independent at the control-plane level:

- PASS 1 scope: current `not_analyzed` items only.
- PASS 2 scope: current `analysis_incomplete` items only after the Dossier-ready gate.
- PASS 1 is not blocked by incomplete items waiting for Dossier or PASS 2.
- PASS 2 is not blocked by unrelated items still waiting for their first PASS 1 attempt.
- GitHub owns scope, deterministic ordering, exact immutable work identity, eligibility, state transitions, validation, persistence, and attempt accounting for both passes.
- Scheduled ChatGPT may only execute an already prepared bounded semantic work unit.

No runtime PASS 2 implementation was added in this task.

## PASS2-GATE acceptance

- **PASS2-GATE-01 — PASS.** No accepted compatible Dossier => no PASS 2 eligibility.
- **PASS2-GATE-02 — PASS.** Waiting for Dossier consumes zero PASS 2 attempts.
- **PASS2-GATE-03 — PASS.** Accepted exact-compatible Dossier unlocks only the matching current incomplete item/work identity.
- **PASS2-GATE-04 — PASS.** Stale, expired, wrong-app, wrong-work, cross-release, ambiguous, or compatibility-mismatched Dossier cannot unlock recovery.
- **PASS2-GATE-05 — PASS.** PASS 1 and PASS 2 may operate independently in parallel; neither has a global wait/block dependency on the other.
- **PASS2-GATE-06 — PASS.** One automatic PASS 2 recovery attempt per current semantic generation/work identity; no infinite retry loop.
- **PASS2-GATE-07 — PASS.** GitHub owns PASS 2 eligibility, order, state, immutable binding, and attempt accounting.
- **PASS2-GATE-08 — PASS.** No PASS 2 runtime, scheduler, worker, queue processor, Scheduled Task execution, or production PASS 2 execution occurred.
- **PASS2-GATE-09 — PASS.** The old full-PASS-1 start rule is explicitly superseded in `PPD-003` and marked superseded in the earlier architecture report.

## Validation performed

Main was re-read after the rule changes.

Confirmed:

- `config/progressive_personalization_contract.json` parses as valid JSON;
- contract version is `3`;
- current runtime flags remain `pass2_active=false` and `pass2_implemented=false`;
- `phase_c_pass2_design.parallelism.pass2_waits_for_global_pass1_completion=false`;
- current exact-compatible accepted Dossier is mandatory for PASS 2 design eligibility;
- waiting consumes `0` attempts;
- maximum automatic attempts per `semantic_generation_id + work_id` is `1`;
- GitHub is the eligibility owner;
- `PPD-003` exists;
- the earlier architecture report carries the explicit supersession note.

## Unresolved implementation details

These are intentionally not implemented by this rule-only task:

- the concrete PASS 2 work-manifest/result schema and repository paths;
- the deterministic PASS 2 queue ordering policy inside GitHub;
- the exact GitHub terminal-execution receipt mechanism used when an authorized attempt runs but produces no accepted semantic result;
- the GitHub trigger/wiring that recomputes PASS 2 eligibility after canonical Dossier persistence;
- PASS 2 Scheduled worker prompt/runtime/schedule;
- focused regression tests for the future runtime implementation.

These details must implement, not reinterpret, the canonical gate above.

## Final status

`complete_ready_for_director_acceptance`

## Recommended next step

Create one bounded **Progressive PASS 2 Phase C implementation** task that implements the GitHub-owned eligibility/work projection and one-shot execution accounting exactly from `phase_c_pass2_design`, including the Dossier-ingest re-evaluation trigger and regression tests, without changing PASS 1 or Dossier evidence semantics.
