# Deep score migration zero-pending release — worker report

- Task: `WORKER_TASK_DEEP_SCORE_MIGRATION_ZERO_PENDING_RELEASE_NORMAL_01.md`
- Worker slot: NEW CHAT 1
- Date: 2026-10-15
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Base: `main`
- Branch: `fix/deep-score-migration-exhausted-release-normal-01`
- Status: implementation and focused PR CI verified; production recomputation/deployment not performed; separate Stage-1 preview check remains blocked by the current committed empty Deep queue.

## Verified cause and authority

- Existing main producer snapshot: frozen score migration `total_count=43`, `accepted_count=42` (including one `already_compliant`), `stale_or_missing_prior_count=1`, `pending_count=0`, `submitted_count=0`, `complete=false`. Existing deterministic normal recomputation found `normal_pass2_eligible_count=158`, yet emitted `items=[]` with `score_explainability_migration_active`.
- `scripts/progressive_pass2.py::score_explainability_target_status` correctly distinguishes accepted migration results, already-compliant revisions, pending exact-frozen targets and stale/missing frozen prior. Stale is not semantic acceptance. Frozen membership and authority are unchanged.
- `scripts/build_progressive_pass2_work.py` formerly equated `not complete` with exclusive score-migration mode. Thus zero runnable targets blocked normal eligible Deep.
- Architecture preflight: `config/execution_ownership_contract.json` grants GitHub the Deep queue, deterministic scope/order/acceptance/recovery and result validation; `config/progressive_pass2_contract.json` authorizes the finite score migration and eventual resumption. Nothing moves into ChatGPT/browser/scheduler and no new queue, quota or retry mechanism is introduced. `PROJECT_DECISIONS.md#PPD-010` preserves finite immutable migration/history and `#PPD-014` now records exhaustion distinct from acceptance.

## Changes

1. Score metrics keep `complete` strict; add `exhausted=true` only for incomplete frozen score migration with no pending runnable target and at least one stale/missing frozen prior.
2. The canonical GitHub Deep producer prioritizes migration whenever its pending count is positive, including submitted-but-unresolved work; validates work/count consistency fail-closed. When zero pending, it emits existing `order_normal_items` in current generation/profile/Dossier binding and records the unresolved score migration in scope. Never rebinds stale targets or fabricates authorization.
3. Clarified exactly this distinction in the canonical score migration contract and documented rationale in `PROJECT_DECISIONS.md#PPD-014`.
4. Expanded `scripts/test_deep_score_evidence_explainability.py` with isolated producer scenarios: 43/42/1/0 with 158 normal; pending score migration priority (including submitted unresolved); full 43 acceptance; fail-closed inconsistent pending count; and real frozen-target status/identity diagnostics in CI.

## Isolation / preservation

No edits to `data/production/**`, `data/cache/**`, migration manifest, legacy Deep accepted results, historical revisions, Dossier, Fast, ranking, UI, Stage 1/2 cutover, recovery authority, run-start marker, Scheduled Tasks, or `CURRENT_TASK.md`. No semantic work executed; PR will not be self-merged.

## Acceptance and verification

- Producer prediction after merge and next successful canonical recomputation of an unchanged eligible snapshot: **158 ordinary Deep items** rather than zero, with original current-work order. This is a calculation from the verified prior normal eligible count, **not** a claim that production was recomputed/deployed.
- Isolated regression is added to existing PASS 2 core workflow test, and the previous score evidence validation remains active.
- **PASS**: `Validate Progressive PASS 2 core` run `38775881249`, including Deep legacy full reanalysis, score-evidence regression (synthetic 43/42/1/0 and submitted pending/complete cases), PASS2 producer/core, history and non-consuming recompute. Its read-only producer recompute logged `ready=158` and `PROGRESSIVE_PASS2_ACTIVE_PROJECTION=PASS` on the PR head.
- **PASS**: `Validate backlog dispositions` run `38775881091`.
- **BLOCKED (separate existing Stage-1 preview input)**: `Validate Deep Stage 1 migration preparation` run `38775881105`; the isolated six Stage-1 unit tests passed, but `scripts/prepare_deep_stage1_migration_work.py` rejected the **committed production PASS2 work file** with `PreparationError: current canonical one-stage Deep work not available`. That source file still has `items=[]`, `projection_status=score_explainability_migration_active` and is intentionally not rewritten in this PR. This check does not prove a post-merge fresh producer cycle. No Stage1/2 source or cutover was modified to mask it.
- **Exact unresolved frozen target identity (PASS2 CI read-only diagnosis):** `family_id=game:1556790`, `frozen_appid=1556790`, `current_appid=1556790`, `current_taste_subject_key=App_1556790`. `disposition=stale_or_missing_prior`, `frozen_prior_authorization_id=5c33e8bbb941530691cd9b2e324e8935871d9c1a125fe217c9f0fa21477bf16c`, `current_authorization_id=c9cfe21b3080ed74806d89bb1ad410f116b8af2de7c021571d65cda2e2f44bbb`. The present product AppID and frozen AppID agree, but **the authoritative prior authorization does not match**. This is not a valid frozen migration target to rebind or count as accepted; existing state/history remains intact.
- PR checks at tested head `fffdad46a5ec20abae7bbf5f8936deb46c1c58d5`: PASS2 core success, backlog success, Stage1 preparation failure on unregenerated committed work. The PR is not merged.

## Next action

Review exact PR test results and checks. Upon approval, merge through normal owner process. A subsequent authorized GitHub producer cycle (not this worker chat) must regenerate the queue and demonstrate a positive actual normal Deep item count; worker must not change canonical production state directly.
