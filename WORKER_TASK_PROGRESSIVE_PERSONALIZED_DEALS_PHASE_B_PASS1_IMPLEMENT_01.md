# WORKER TASK — PROGRESSIVE PERSONALIZED DEALS PHASE B PASS 1 IMPLEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `progressive-personalized-deals-phase-b-pass1-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

User authorization:
- explicit approval to proceed with Phase B / PASS 1 after Director accepted Phase A.

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.

Затем открой этот task-файл из `main`.

Direct prerequisites:
- `reviews/worker_reports/progressive-personalized-deals-architecture-amendment-01.md`
- `reviews/worker_reports/progressive-personalized-deals-phase-a-implement-01.md`

Phase A is accepted and live. Do not reopen Phase A architecture unless a proven blocker requires it.

## Current accepted production baseline

Current progressive site state:
- current deterministic progressive candidate input: 721 before expiry;
- final visible current payload: 720;
- current visible states: 720 × `not_analyzed` / Tier 3;
- `analyzed_fit = 0`;
- `analyzed_not_fit = 0`;
- `analysis_incomplete = 0`;
- source/business/identity gates remain strict;
- Phase A publication does NOT require semantic queue closure;
- PASS 1/PASS 2 are currently inactive.

Phase B must preserve this availability invariant throughout implementation and rollback.

## Phase B objective

Implement GitHub-owned item-level PASS 1 so the current unresolved catalogue progressively moves from:

`not_analyzed`

to exactly one accepted first-pass outcome:

- `analyzed_fit`;
- `analyzed_not_fit`;
- `analysis_incomplete`.

Critical product invariant:
- one item's semantic/retrieval/validation failure must never block later unrelated items;
- site publication must continue while PASS 1 is open;
- PASS 1 prioritizes coverage of the entire catalogue, not deep recovery of difficult items.

PASS 2 remains explicitly out of scope.

## Architecture preflight / ownership

Before writes, verify and record:

1. GitHub owns:
   - current semantic generation identity;
   - PASS 1 scope;
   - deterministic PASS 1 order;
   - per-item attempt state;
   - immutable work preparation;
   - validation;
   - accepted outcome persistence;
   - retry eligibility;
   - processing counts;
   - visual rebuild trigger.

2. Scheduled ChatGPT is only bounded semantic data-plane execution.

3. Interactive ChatGPT is not a production worker/backlog manager.

4. No new independent scheduler/retry owner is created.

5. If existing queue/checkpoint/group semantics conflict with item-level progress, amend the canonical contracts before activating PASS 1.

## PASS 1 semantic path — authoritative

Use the accepted Phase B path:

**compatible-cache fast path + lightweight PASS 1 semantic analysis**

Full Dossier/deep recovery is NOT a universal PASS 1 prerequisite.

A PASS 1 attempt should seek a trustworthy fit/not-fit decision using the lightest contract-valid candidate-specific semantic evidence available.

Do not require, merely for PASS 1:
- fresh Russian Steam review;
- complete multi-source Dossier;
- exhaustive current-state research;
- deep risk recovery.

If lightweight evidence is insufficient to reach a trustworthy fit/not-fit conclusion:
- outcome = `analysis_incomplete`;
- record safe typed reason;
- move on immediately;
- do NOT deep-recover inside PASS 1.

## Successful outcome rules

### analyzed_fit

Requires:
- exact candidate/profile/model/fingerprint binding;
- valid current semantic result;
- current Taste threshold still met (moderate+ or current canonical equivalent);
- candidate-specific grounded positive evidence under existing intrinsic Taste rules;
- normalized personalized ranking inputs required by Tier 1;
- no guessed candidate properties.

May publish:
- supported personalized score;
- supported why-fit;
- only supported risk/current-state claims.

Missing optional rich enrichment remains unknown.

### analyzed_not_fit

Requires:
- trustworthy completed below-threshold or confirmed-negative semantic conclusion;
- enough evidence to distinguish real non-fit from missing information.

Do NOT classify as not-fit merely because evidence is insufficient.

### analysis_incomplete

Use when:
- semantic evidence is insufficient;
- external evidence needed by the lightweight PASS 1 route cannot be obtained;
- returned semantic result is invalid;
- worker/runtime attempt fails after GitHub has durably recorded that first-pass attempt;
- exact binding fails and no trustworthy first-pass result can be accepted.

The item remains visible Tier 2.

## Attempt budget

For one current semantic generation:

- each `not_analyzed` item gets at most ONE PASS 1 attempt;
- success -> analyzed_fit or analyzed_not_fit;
- unresolved/failed -> analysis_incomplete;
- no automatic PASS 1 retry;
- retry/deep recovery belongs to future PASS 2.

A new commercial price refresh alone must not reset PASS 1 attempt state.

A material semantic binding/profile/model/fingerprint generation change may reproject affected items to `not_analyzed` according to canonical rules.

## PASS 1 ordering

GitHub owns deterministic order.

Use the accepted architecture ordering unless current canonical constraints prove a narrower equivalent:

1. sale-expiry urgency when known;
2. existing taste-independent purchase/deal value;
3. stable candidate key/source order as tie-break.

The order is operational only.
It must not change the site tier-ranking contract.

Coverage requirement:
- every runnable `not_analyzed` item must eventually receive its one PASS 1 attempt;
- do not repeatedly favor a failing/urgent item over untouched later items.

## Work-unit / transport semantics

Canonical outcome and progress MUST be item-level.

Transport MAY batch multiple items for efficiency only if all of the following hold:

- each child has immutable exact identity/binding;
- each child has independent validation/outcome;
- valid sibling A can persist even if sibling B fails;
- invalid sibling B becomes/retains `analysis_incomplete`;
- valid sibling C can persist;
- later work is not blocked by one invalid child;
- no maximal-contiguous-prefix rule controls semantic progress.

Prefer the smallest implementation that reuses existing transport safely.

Do not keep group-of-three atomic acceptance merely for compatibility.

## GitHub-owned PASS 1 state

Implement the minimal durable machine state needed to answer:

Per current candidate:
- current analysis state;
- current semantic generation id/binding;
- whether PASS 1 was attempted for this generation;
- accepted PASS 1 outcome;
- safe issue code if incomplete;
- accepted-at timestamp if applicable;
- immutable work identity needed for validation.

Global:
- pass1_active;
- pass1_total_scope;
- pass1_attempted_count;
- pass1_remaining_count;
- analyzed_fit_count;
- analyzed_not_fit_count;
- analysis_incomplete_count;
- not_analyzed_count;
- last_accepted_analysis_at_utc;
- optional last_attempt_at if operationally useful.

Do not create a durable `analysis_in_progress` user state.

During a live attempt:
- item stays in its prior durable state until GitHub accepts/records the outcome.

## Canonical contract updates

Implement the smallest required changes to existing canonical contracts.

Expected surfaces may include:
- `config/progressive_personalization_contract.json`;
- `config/taste_result_contract.json`;
- `config/execution_ownership_contract.json`;
- `config/daily_execution_contract.json`;
- semantic worker prompt/contract;
- work manifest/persistence bridge if the current path requires them.

Required semantics:
- item-level acceptance/progress;
- PASS 1 one-attempt budget;
- no deep recovery in PASS 1;
- insufficient information -> incomplete, not not-fit;
- site publication independent of PASS 1 completion;
- GitHub-owned queue/order/retry/completeness.

Do not alter the Taste threshold merely to increase completion rate.

## Queue / work preparation

Build a GitHub-owned PASS 1 work projection containing only current `not_analyzed` items that:
- have no exact-compatible accepted result already usable;
- have not consumed their PASS 1 attempt for the active semantic generation.

Compatible accepted cache must short-circuit work:
- fit -> analyzed_fit;
- trustworthy not-fit -> analyzed_not_fit;
- current accepted incomplete/attempt record -> analysis_incomplete;
- no new PASS 1 invocation for those already resolved for the current generation.

The queue/order must be reproducible from canonical state.

## Scheduled semantic worker changes

Modify the existing semantic worker path only as required for PASS 1.

Worker must:
- consume only GitHub-prepared immutable work;
- process each child independently;
- use lightweight PASS 1 evidence strategy;
- stop semantic depth once trustworthy fit/not-fit is possible;
- return typed incomplete when not possible;
- never invent retry order;
- never start PASS 2;
- never process non-current/unprepared items;
- never turn missing data into negative Taste.

If the worker receives a small transport batch, it must still emit independently attributable child outcomes.

## Ingest / acceptance

GitHub ingest must:

For each child independently:
1. verify exact work identity and semantic generation/bindings;
2. validate schema/evidence/provenance;
3. accept fit, not-fit, or incomplete;
4. persist valid outcome;
5. mark first-pass attempt consumed for that item/generation;
6. reject invalid semantic claims;
7. for an invalid first-pass return, record safe `analysis_incomplete` attempt outcome if canonical rules permit proving the attempt identity; otherwise preserve safe fail-closed state without blocking later items;
8. continue to unrelated siblings/later work.

One invalid child must not roll back valid siblings.

## Visual update behavior

After accepted PASS 1 progress, normal GitHub production path must update the progressive visual state without waiting for PASS 1 completion.

Expected site transitions:

`not_analyzed` -> `analyzed_fit`
- card rises to Tier 1 and uses personalized ranking.

`not_analyzed` -> `analysis_incomplete`
- card rises to Tier 2 and shows “Разбор не завершён”.

`not_analyzed` -> `analyzed_not_fit`
- card disappears from normal visible list;
- aggregate not-fit count increments.

Counts must remain reconciled after every accepted progress step.

## Failure behavior

Prove exact behavior for:

1. one successful fit item;
2. one successful not-fit item;
3. one insufficient-evidence item;
4. one invalid semantic result;
5. one worker/tool failure for one item;
6. one bad child in a multi-item transport batch;
7. stale/incompatible return after semantic generation changes;
8. Scheduled ChatGPT does not run;
9. current commercial source refresh occurs while PASS 1 remains open.

Required invariant in all cases:
- unrelated current deals remain published;
- unrelated PASS 1 work remains runnable;
- no global rollback to an empty/legacy visual;
- no hidden head-of-line block.

## Activation strategy

This task is IMPLEMENT / ACTIVATE / VALIDATE.

After code/contracts/tests:
1. merge through normal repository path;
2. activate PASS 1 control-plane state on current production generation;
3. prove the work manifest/queue contains the expected unresolved current scope;
4. perform only the smallest bounded live semantic acceptance needed to validate end-to-end item-level progression, if the existing authorized Scheduled worker path can be invoked safely;
5. do NOT attempt to process all ~720 games inside this worker task;
6. once the end-to-end path is proven, leave the remaining PASS 1 backlog under the canonical GitHub/Scheduled-worker production mechanism.

If live Scheduled ChatGPT invocation is not available through worker tooling:
- do not fake it;
- validate GitHub preparation/ingest synthetically;
- activate only what can be truthfully activated;
- report exact external live-acceptance boundary.

Do not manually semantically analyze games in this interactive worker chat.

## Required production safety

Phase A must remain a valid rollback/fallback throughout:

If PASS 1 activation fails:
- the site still publishes current Tier 3 catalogue from Phase A;
- do not revert to the old 3-card/global-completion behavior;
- do not hide untouched games.

No PASS 1 failure may make the current site unavailable.

## Required validation scenarios

At minimum:

PASS1-01 — one fit child independently persists and becomes Tier 1.

PASS1-02 — one trustworthy not-fit child independently persists and is excluded/counts as not-fit.

PASS1-03 — insufficient evidence becomes `analysis_incomplete`, not not-fit.

PASS1-04 — invalid child cannot block valid sibling/later child.

PASS1-05 — batch transport, if retained, has independent child acceptance.

PASS1-06 — maximal-contiguous-prefix/global group completion no longer controls PASS 1 progress.

PASS1-07 — one PASS 1 attempt maximum per item/generation.

PASS1-08 — compatible accepted cache skips new PASS 1 work.

PASS1-09 — stale/incompatible result is rejected without hiding the item or blocking later work.

PASS1-10 — PASS 1 open/nonzero remaining count does not block site publication.

PASS1-11 — counts reconcile after partial progress.

PASS1-12 — accepted fit reorders to Tier 1 correctly.

PASS1-13 — incomplete reorders to Tier 2 correctly.

PASS1-14 — not-fit disappears from visible list but remains in counts.

PASS1-15 — Scheduled worker absence leaves remaining Tier 3 visible and does not damage publication.

PASS1-16 — commercial refresh while PASS 1 open preserves semantic progress/state.

PASS1-17 — no PASS 2/deep recovery loop exists.

PASS1-18 — no new control-plane owner outside GitHub.

PASS1-19 — normal Phase A full/current publication regressions remain green.

PASS1-20 — durable report committed/reread from `main`.

## Scope exclusions

Do NOT:
- implement PASS 2;
- add repeated automatic retries;
- require Dossier for every PASS 1 item;
- make Russian-review retrieval a universal PASS 1 blocker;
- process the full 720-item backlog manually inside this task;
- change hard business/source eligibility;
- weaken evidence identity/provenance/privacy;
- reintroduce global semantic-completion publication gate;
- redesign Phase A UI unless a strictly necessary PASS 1 status field is missing;
- add unrelated observability infrastructure.

## Durable report

Write:
`reviews/worker_reports/progressive-personalized-deals-phase-b-pass1-implement-01.md`

Required sections:
1. Task / repo / mode.
2. Architecture preflight.
3. Accepted Phase A baseline.
4. Canonical PASS 1 semantics implemented.
5. Semantic generation identity.
6. PASS 1 work projection/order.
7. Worker transport semantics.
8. Worker prompt/contract changes.
9. Item-level ingest/acceptance.
10. Attempt budget / no-retry semantics.
11. Visual/site incremental update behavior.
12. Failure behavior.
13. Files/components changed.
14. PASS1-01..20.
15. Test/workflow evidence.
16. Activation state.
17. Bounded live acceptance evidence or exact external boundary.
18. Current processing counts after activation.
19. Explicitly not implemented: PASS 2.
20. Rollback/fallback proof.
21. Unresolved.
22. Status.
23. Exactly one recommended next step.
24. Exact commit/PR/run refs.
25. Efficiency / reusable lesson.

Allowed statuses:
- `complete_ready_for_director_acceptance`
- `complete_code_waiting_external_live_acceptance`
- `needs_fix`
- `blocked_external`
- `needs_user_decision`

## Completion rule

Do not claim Phase B complete until:
- report exists at exact path in `main`;
- report is reread from `main`;
- item-level progression is proven by focused validation;
- Phase A fallback remains intact;
- no PASS 2 work occurred.

## Exactly one next step

If Phase B is implemented and end-to-end accepted:
- return to Director;
- then start/continue the remaining PASS 1 backlog only through the canonical GitHub-owned production mechanism;
- do not begin PASS 2 until Director separately accepts Phase B.

If live Scheduled-worker invocation remains external:
- return to Director for one explicit bounded live acceptance step before declaring production PASS 1 fully active.
