# Deep two-stage architecture freeze 01

Status: `complete_interfaces_frozen`

Task: `WORKER_TASK_DEEP_TWO_STAGE_ARCHITECTURE_FREEZE_01.md`  
Requirements source: `WORKER_TASK_DEEP_TWO_STAGE_COMPARATIVE_CALIBRATION_IMPLEMENT_01.md`  
PR: #156 — `Freeze two-stage Deep architecture interfaces`

## Scope

This task freezes interfaces only. It does **not** activate the new architecture, execute Stage 1 or Stage 2 semantics, migrate production results, remove Fast from current production, change the current ranking producer, redesign the live site, or modify any ChatGPT Scheduled Task.

The currently active production contracts remain:
- `FAST-DOSSIER-DEEP-V1`;
- `config/progressive_pass2_contract.json`;
- `config/final_ranking_policy.json`.

The new contracts are explicitly `frozen_not_active` and `production_cutover_authorized=false`.

## Frozen pipeline

`Dossier -> Deep Stage 1 -> Deep Stage 2 -> ranking/publication`

Stage 1 and Stage 2 are separate semantic workers/chats with:
- different worker identities;
- different future manual prompt paths;
- different work manifests;
- different result schemas;
- different inbox/state paths;
- mutually exclusive write responsibilities.

GitHub remains the control plane for scope, ordering, exact bindings, validation, persistence, retries/completeness, Stage-2 anchor/window selection and final numeric placement.

## Frozen score model

The target model is:

`calibrated_deep_fit_0_56 + wishlist_0_or_4 = personal_quality_0_60`

`personal_quality_0_60 + deterministic_purchase_0_40 = combined_offer_0_100`

Rules:
- Stage 1 produces only a provisional Deep-fit value on 0–56.
- Stage 2 establishes authoritative comparative quality placement.
- Wishlist remains explicit deterministic GitHub-owned +4 and is excluded from Stage-1/Stage-2 semantic scoring.
- Purchase remains deterministic GitHub-owned /40 and Stage 2 cannot compensate for price/discount.
- legacy separate achievements/duration/risk arithmetic is marked for retirement **after cutover**; its relevant personal meaning moves into Stage-1 semantic context to avoid double counting.
- exact direct user ratings remain strong calibration anchors/constraints rather than a hidden additive bonus.

## Stage 1 interface

Canonical:
- `config/deep_stage1_contract.json`
- `config/deep_stage1_result_schema.json`

Frozen future paths:
- prompt: `config/deep_stage1_manual_worker_prompt.md`
- work: `data/production/pre_ai/deep_stage1_work.json`
- inbox: `data/ai_inbox/deep_stage1/results`
- state: `data/cache/deep_stage1_state.json`

Stage 1 owns independent per-game analysis only:
- `summary_ru`;
- structured `positives`;
- structured `negatives`;
- structured `nuances`;
- fit/not-fit/incomplete + confidence;
- `provisional_deep_fit_score_0_56` for fit;
- game-specific signed `point_breakdown`.

The breakdown must arithmetically reconcile to the provisional score, but it is explicitly an explainability projection of a holistic judgment. There is no mandatory category list, no fixed factor ceilings and no fixed additive five-factor authority. Ranking neighbors, Wishlist and deal economics are forbidden Stage-1 inputs.

Authoritative not-fit and incomplete results have no fabricated positive-ladder score.

## Stage 2 interface

Canonical:
- `config/deep_stage2_contract.json`
- `config/deep_stage2_result_schema.json`

Frozen future paths:
- prompt: `config/deep_stage2_manual_worker_prompt.md`
- work: `data/production/pre_ai/deep_stage2_work.json`
- inbox: `data/ai_inbox/deep_stage2/results`
- state: `data/cache/deep_stage2_state.json`

Stage 2 may use only:
- exact accepted target Stage-1 result;
- exact accepted Stage-1 results of GitHub-selected anchors;
- accepted calibrated anchor state;
- pinned profile;
- exact GitHub-provided comparison-window metadata.

Stage 2 may not do web research, invent facts, rewrite Stage-1 findings, choose anchors or expand its window.

It returns strict above/below or near-tie-with-direction comparisons, reasons, `semantic_calibrated_deep_fit_target_0_56`, and `comparative_adjustment_from_stage1`.

A genuine Stage-1 contradiction produces `stage1_contradiction`. If strict direction cannot be justified, the worker returns `calibration_incomplete`; accepted final fit ties are not allowed.

## Numeric placement and precision

The semantic worker supplies comparative placement; GitHub assigns the canonical numeric coordinate `calibrated_deep_fit_score_0_56`.

Frozen invariant:
- if A is placed above B, A's canonical score must be numerically greater;
- distinct active calibrated fit candidates must display distinct scores;
- integer-only scoring is forbidden;
- canonical storage/display uses **two decimal places**;
- local deterministic re-spacing is allowed only where necessary;
- distant unrelated candidates may not be arbitrarily renumbered.

Why two decimals: 0.01 yields 5601 coordinates across 0–56 and 101 positions inside a one-point interval. One decimal cannot guarantee strict display uniqueness if a dense local region contains more than ten distinct candidates. Two decimals is therefore the smallest frozen precision that safely supports roughly 100 active ranked candidates even under strong clustering. The value is documented as a comparative-order coordinate, not physical measurement precision.

## Site mirror contract

Canonical:
- `config/deep_two_stage_site_projection_contract.json`

Compact card:
- Stage-2 calibrated state may show final semantic/personal score;
- pending Stage 2 shows `Ожидает сравнительной калибровки`;
- Stage-1 provisional score may not masquerade as final;
- Fast fallback/label is forbidden after cutover.

Detail order is frozen:
1. short summary;
2. positives;
3. negatives;
4. other/nuances;
5. Stage-2 score change;
6. why above/below neighbors.

The detail projection exposes:
- Stage-1 provisional Deep fit;
- Stage-1 point breakdown;
- Stage-2 calibrated Deep fit;
- Stage-2 delta;
- Wishlist +4;
- personal /60;
- purchase /40;
- combined /100;
- rank and pipeline states.

Statistics top-level blocks are frozen as:
- Dossier;
- Deep Stage 1 — analysis;
- Deep Stage 2 — comparative calibration.

Fast is not an equivalent active semantic block after cutover.

## Migration boundary

Canonical:
- `config/deep_two_stage_migration_contract.json`

Existing exact-compatible Dossiers are preserved.

Legacy Deep is classified by GitHub into:
- `reusable_as_stage1`;
- `requires_stage1_reanalysis`.

Reusable-as-Stage1 requires every mandatory new Stage-1 field to be mappable without semantic invention, including a compatible holistic provisional score and transparent game-specific breakdown that does not resurrect the fixed five-factor formula.

A row may require reanalysis while still preserving valid legacy factual findings as immutable migration/audit evidence.

Known legacy fit rows that lack score findings do not become Stage-1 complete merely because they contain an old number.

No mixed authority:
- before cutover, current FAST/Dossier/Deep remains the only production authority;
- after cutover, positive semantic scoring authority is accepted Stage 2 + Wishlist + deterministic purchase;
- legacy Fast/Deep numeric scores become audit history only;
- partial production cutover is forbidden.

No semantic or mass migration is authorized by the freeze.

## Parallel implementation dependency map

Canonical:
- `config/deep_two_stage_dependency_map.json`

After this freeze is accepted, these four tasks may proceed independently/in parallel:
1. `WORKER_TASK_DEEP_STAGE1_WORKER_IMPLEMENT_01.md`
2. `WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md`
3. `WORKER_TASK_DEEP_FAST_REMOVAL_RANKING_MIGRATION_01.md`
4. `WORKER_TASK_DEEP_SITE_MIRROR_UI_STATISTICS_IMPLEMENT_01.md`

Each task file now names the frozen interfaces it must consume and must not redefine.

Only `WORKER_TASK_DEEP_TWO_STAGE_INTEGRATION_CUTOVER_01.md` owns:
- final legacy classification execution;
- migration/calibration queue activation;
- production authority switch;
- no-mixed-authority acceptance;
- bounded end-to-end cutover.

## Durable architecture records

- `PROJECT_DECISIONS.md#PPD-013` records the rationale and activation boundary.
- `PROJECT_ROUTES.md#Deep two-stage frozen architecture: Stage 1 -> Stage 2 -> ranking` provides the bounded navigation route.
- `scripts/test_deep_two_stage_architecture_freeze.py` proves frozen invariants and, critically, proves that current active production remains unchanged.

## Validation

PR-head validation before report finalization:
- `Validate Progressive PASS 2 core` run `37451342289` — **success**;
  - includes `Deep two-stage architecture freeze regression` — success;
  - existing PASS 2, Dossier integration, balanced-negative, score-explainability, frozen-start, ranking and visual regressions — success;
  - active-production recomputation remained valid and consumed no attempts.
- `Validate backlog dispositions` run `37451342295` — **success**.

Concurrent `main` movement while this task was in progress consisted of Dossier group 31 ingest and visual refresh production data only; none touched the frozen architecture/task/project files. PR #156 remained mergeable.

## Files created

- `config/deep_two_stage_architecture_contract.json`
- `config/deep_stage1_contract.json`
- `config/deep_stage1_result_schema.json`
- `config/deep_stage2_contract.json`
- `config/deep_stage2_result_schema.json`
- `config/deep_two_stage_site_projection_contract.json`
- `config/deep_two_stage_migration_contract.json`
- `config/deep_two_stage_dependency_map.json`
- `scripts/test_deep_two_stage_architecture_freeze.py`
- `reviews/worker_reports/deep-two-stage-architecture-freeze-01.md`

## Files updated

- `.github/workflows/validate-progressive-pass2-core.yml` — validation only, no runtime/cutover behavior.
- `PROJECT_DECISIONS.md`
- `PROJECT_ROUTES.md`
- the five downstream worker-task files, only to bind them to frozen interfaces.
- `CURRENT_TASK.md`

## Explicit non-changes

No production Stage-1/Stage-2 work/state/inbox was created.  
No existing Dossier, Fast or Deep semantic result was changed.  
No active ranking or publication contract was changed.  
No semantic worker was executed.  
No Scheduled Task was created, edited, enabled, disabled, paused, resumed or run.

## Next action

Director may accept this freeze and start the four independent implementation tasks in parallel. Production authority must remain unchanged until the integration/cutover task has all four accepted dependencies and passes its own gates.

Final status: `complete_interfaces_frozen`
