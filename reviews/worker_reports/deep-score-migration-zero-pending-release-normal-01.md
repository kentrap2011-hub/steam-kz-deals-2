# Deep score migration zero-pending release — worker report

- Task: `WORKER_TASK_DEEP_SCORE_MIGRATION_ZERO_PENDING_RELEASE_NORMAL_01.md`
- Worker slot: NEW CHAT 1
- Date: 2026-10-15
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Base: `main`
- Branch: `fix/deep-score-migration-exhausted-release-normal-01`
- Status: implementation proposed; CI and main producer rerun must be checked independently.

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
- CI: pending check; see PR checks.
- Other PASS 2 / Deep-history / priority coverage: pending PR CI.
- One specific frozen target is still `stale_or_missing_prior`; CI diagnostics identify its exact family/current AppID and authorization from state and frozen snapshot without rewriting that state. No assumption of acceptance or semantic reprocessing is made.

## Next action

Review exact PR test results and checks. Upon approval, merge through normal owner process. A subsequent authorized GitHub producer cycle (not this worker chat) must regenerate the queue and demonstrate a positive actual normal Deep item count; worker must not change canonical production state directly.
