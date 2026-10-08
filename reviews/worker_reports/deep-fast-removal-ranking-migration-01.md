# Worker report — Deep Fast removal / ranking migration 01

**Задача:** `WORKER_TASK_DEEP_FAST_REMOVAL_RANKING_MIGRATION_01.md`  
**Репозиторий:** `kentrap2011-hub/steam-kz-deals-2`  
**Основа:** `main`, initial base `7cd43a2c079d9ea39f2299a0e280214fafbc6d9e`  
**Рабочая ветка:** `implement/deep-fast-removal-ranking-migration-01`  
**Режим:** implementation candidate + validation, **production not activated**.

## Architecture preflight

1. **Owner:** GitHub control plane; new calculation runs only in GitHub producer after a separate atomic integration/cutover. ChatGPT workers cannot decide ranking arithmetic, scope or fallback.
2. **Authority:** `config/deep_two_stage_architecture_contract.json`, `config/deep_two_stage_migration_contract.json`, `config/deep_two_stage_dependency_map.json`, `PROJECT_DECISIONS.md#PPD-013`; Stage-1/Stage-2 interfaces unchanged.
3. **Ownership preservation:** proposed scorer only consumes accepted, exact-matched Stage-1/Stage-2 state + deterministic wishlist/purchase; never executes semantic inference, queue selection or worker migration.
4. **No new recurring processing:** no scheduler, ingestion, control plane, quota, retry/backlog or runtime changes.

## Implementation

- `scripts/deep_two_stage_ranking.py`: *isolated, non-active* post-cutover ranking candidate. It requires explicit **current GitHub-owned Stage-1 work bindings** and strictly matched accepted Stage-1 state, plus authoritative Stage-2 calibrated identity/path/hash. Stale Stage-2 state is non-authoritative; multiple current candidates and duplicate calibrated 0.01 scores are fail-closed.
- Score is exactly Stage-2 calibrated Deep fit **0–56 (0.01 precision)** + Wishlist **0 or +4** = personal **0–60**, plus unchanged deterministic purchase **0–40** = combined **0–100**. Deterministic purchase is reused via `priority_ranking.build_purchase_breakdown`, including standalone and eligible fixed-package comparison. No dependency on old `build_score_breakdown` or full V2 personal scorer.
- Pending Stage 2, diagnostic-incomplete and not-analyzed games have **no semantic/personal/combined score**. Their operational ordering uses **purchase-only**, never Fast or Stage-1 provisional values. Accepted Stage-1 not-fit does not receive a positive rank.
- Output is a strict isolated projection, **not an overlay that retains stale score/reasons** from legacy Fast cards. The only personal component IDs are `calibrated_deep_fit` and `wishlist`; achievements/duration/risk are retired as *separate arithmetic*, remaining semantic evidence for Stage 1 instead of adding a second numeric influence. Exact direct user ratings are not turned into score multipliers/bonuses: their anchor role belongs to Stage-1/Stage-2 semantics.
- No `web/app.js`, production producer or `config/final_ranking_policy.json` wiring was altered. It is deliberately impossible for this PR alone to change the live ranking.

## Fast-authority / legacy consumer inventory

| Surface | Current legacy authority | Post-cutover boundary / separate owner |
| --- | --- | --- |
| `scripts/progressive_personalization.py::build_state_index` | PASS 1 / compatible Taste fallback when Deep missing, effective Fast source, migration/recovery diagnostics | Replace producer input with current Stage-1 + Stage-2 accepted authority **only during integration**; old Fast state becomes audit history. |
| `scripts/progressive_personalization.py::ranking_stage_from_state`, `apply_progressive_order` | `fast_fit` stage and `total_score` based on legacy personal subweights; purchase-only unresolved fallback | Prepared `project_candidate_ranking` accepts no Fast authority, only calibrated/purchase-only nonsemantic pending; integration owns atomic switch. |
| `scripts/priority_ranking.py::_taste_component`, `build_score_breakdown` | Direct rating as score multiplier; normalized/fixed taste factor weights, coarse Fast fallback, independent achievements/duration/risk, Wishlist and purchase | Retain `build_purchase_breakdown` only in candidate; Stage-2 score + Wishlist replace old personal arithmetic, no double counting. |
| `scripts/build_final_visual_payload.py` + `scripts/refine_visual_ranking.py` + `scripts/card_explanation_policy.py` | Existing legacy semantic card reasons, score/risk enrichment, filtering and published V2 ranks | Integration must select producer-owned Stage-1 facts, Stage-2 comparative reasons and isolated score; site mirror task owns rendering, not this worker. |
| `scripts/progressive_pass1.py`, `scripts/progressive_pass2.py`; corresponding cache/state/recovery | Legacy Fast and monolithic Deep history, exact old recovery provenance and projection | Keep read-only audit for migration classification; **never** use legacy numeric scores as proposed ranking/recovery fallback. Legacy classification execution remains integration-exclusive. |
| `web/app.js`; Statistics/current-stage display | Existing Fast names/score and published legacy ranking stage | Site mirror worker controls UI/Statistics; integration must prove Fast card/Statistics publication is absent after authority switch, not infer stage from old card text. |
| `config/final_ranking_policy.json` | Canonical `FINAL-PRIORITY-RANKING-V2` until cutover | Still authoritative for **today's** production and 0–40 purchase. Atomic policy switch is integration-exclusive, not partial in this PR. |

## Migration guard and remaining integration prerequisites

- Legacy Dossier exact-compatible accepted evidence can be reused; old score without complete Stage-1 structured fields and evidence-bound dynamic point breakdown **requires Stage-1 reanalysis**, per frozen contract.
- Old `score_findings`/five fixed taste factors cannot be reinterpreted as a 0–56 holistic Stage-1 score. A numeric value alone cannot prove Stage-1 compatibility.
- Stage-1 and Stage-2 state are presently `implemented_not_active`; this PR neither seeds Stage-2 calibration anchors nor creates a migration/recovery authorization.
- No partial cutover: integration must atomically route producer, publication, Statistics, and ranking to new authoritative state, including a fail-closed check for mismatched legacy/Fast authority; separate site mirror task and explicit gate acceptance remain necessary.

## Tests

`scripts/test_deep_fast_removal_ranking_migration.py` covers 56+4+40 with exact 0.01 precision, purchase reuse, stale/duplicate binding rejection, not-fit and pending cases, poisoned legacy Fast and direct-rating arithmetic, no achievements/duration/risk double counting, no card reasons leakage, no active production wiring.  
`.github/workflows/validate-deep-fast-removal-ranking.yml` runs compile, isolated regression, existing V2 production regression and frozen-architecture regression.

**PR:** [#164](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/164).  
**Reconciliation (2026-10-08):** This branch was rebuilt onto latest observed `main` `b9ad7aed7bcc76237fb3402a291cb632ac730598` while preserving the untouched full main tree, including `DIRECTOR_TASK_BOARD.md`, `config/director_task_plan.json`, the site tasks page/closeout, and all independent production, Dossier and translation writes. The PR diff is restricted to ranking scripts/test/workflow, this report and an 8-line minimal `CURRENT_TASK.md` closeout. No activation/cutover. On this base, new ranking `37768591347` passed before this further merge; **fresh final-head CI must be rechecked**.  
**Status:** `implementation_complete_pending_final_ci`.  
**Stop boundary:** no integration/cutover, semantic execution, site redesign, Scheduled Tasks or other worker task.
