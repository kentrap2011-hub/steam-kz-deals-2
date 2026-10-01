# Deep invalid-not-fit current-state regression fix 01

## Task

Task ID: `deep-invalid-not-fit-current-state-regression-fix-01`.

Repository: `kentrap2011-hub/steam-kz-deals-2`.

Branch: `fix/deep-invalid-not-fit-current-state-regression-fix-01`.

Pull request: #133, `Make Deep invalid-loop regression state-aware`.

Scope: repair the stale current-state assumptions in `scripts/test_deep_invalid_not_fit_contract_loop.py` without weakening the invalid-not-fit contract or changing production Deep/Dossier state.

## START / dependency reconciliation

The current `CHAT_PROTOCOL.md` START gate was completed.

Read before implementation:
- `CHAT_CONTEXT.md`;
- current state in `DIRECTOR_TASK_BOARD.md`;
- `WORKER_TASK_DEEP_INVALID_NOT_FIT_CONTRACT_LOOP_FIX_01.md`;
- accepted report `reviews/worker_reports/deep-invalid-not-fit-contract-loop-fix-01.md`;
- `PROJECT_ROUTES.md` Progressive Fast/Dossier/Deep route;
- `config/execution_ownership_contract.json`;
- current PASS 2 contract and the failing regression.

The task also required `reviews/worker_reports/card-explanation-producer-validator-publication-parity-fix-01.md`. That report is not yet present on `main` because PR #132 remains open. The current report was therefore read from the PR #132 implementation branch `fix/card-explanation-producer-validator-publication-parity-01` without modifying that branch or its implementation.

Fresh write base: `main@abab49194b7da2c205893e7bb9880727674ccfa0`.

Architecture preflight: GitHub remains the Deep control-plane owner; this task changes only deterministic regressions/test fixtures. No control-plane responsibility moves to ChatGPT, no scheduler/queue/retry/checkpoint owner changes, and no recurring stage is added.

## Root cause

The invalid-not-fit regression correctly encoded the 2026-09-30 historical reconciliation immediately after PR #129, but then treated mutable top-level production state as immutable history.

For each of the three pinned exact identities it required the current entry to remain forever:
- `outcome=analysis_incomplete`;
- `analysis_issue_code=terminal_execution_failure`;
- `recovery_owned=true`;
- the original prepared recovery authorization still present as the current authorization;
- current work still emitted as `work_mode=recovery`.

Those conditions stop being true after legitimate GitHub-authorized recovery completes or otherwise advances the current entry, even though the original consumed normal-first-pass failure remains durably recorded in `normal_first_pass`.

## Fix

`scripts/test_deep_invalid_not_fit_contract_loop.py` now anchors the three pinned cases to immutable attempt provenance instead of mutable current outcome.

It still requires for each pinned exact identity:
- the exact historical `work_id`;
- `normal_first_pass_attempted=true`;
- the preserved `normal_first_pass` attempt to be `analysis_incomplete / terminal_execution_failure`;
- `attempt_consumption_source=github_derived_semantic_contract_failure`;
- the original semantic-contract failure reason;
- the exact prior result commit and exact historical ingest-rejection commit.

Current state may now legitimately be either unresolved/incomplete or later authoritative completion.

Any persisted recovery attempt must carry:
- `work_mode=recovery`;
- a concrete 64-character `recovery_authorization_id`;
- an allowed GitHub-owned recovery reason;
- a unique consumed authorization identity.

Any still-live recovery authorization must be fresh relative to already-consumed recovery attempts.

Current `progressive_pass2_work.json` is checked only for the invariant that the same exact consumed historical `work_id` is never emitted again as `normal_first_pass`. If it is still present, it must be recovery work; after authoritative completion it may be absent.

The earlier fixture-level checks remain unchanged and continue proving:
- no deterministic `medium -> high` confidence promotion;
- malformed transport consumes no attempt;
- wrong-identity transport consumes no attempt;
- exact-bound semantic-contract-invalid execution consumes the existing first-pass attempt and enters recovery ownership;
- recovery requires explicit GitHub authorization;
- frozen sibling traversal remains nonblocking.

## PASS 2 test-fixture date stabilization

The first PR #133 validation exposed a separate deterministic-test defect before the changed regression could run.

`scripts/test_progressive_pass2.py::dossier_record()` used a default expiry of `2026-10-01T00:00:00Z`. On 2026-10-01 the fixture became expired under `authorize_recovery()`, causing the base PASS 2 unit regression to fail with:

`current Dossier cannot authorize Deep recovery: dossier_expired_or_missing_expiry`.

This was test-fixture time drift, not production semantics. The default fixture expiry was moved to `2099-01-01T00:00:00Z`. No production Dossier expiry rule changed.

The failed pre-stabilization PASS 2 run was `36808215954`; backlog run `36808215876` was already green.

## Validation

Validated code head before this report: `0e59843b1641fcabc554b3255c98fb0b15107cfa`.

GitHub Actions:
- Validate Progressive PASS 2 core: run `36808341769` / #538 — success.
- Validate backlog dispositions: run `36808341778` / #1521 — success.

PASS 2 run `36808341769` passed:
- visual material freshness regressions;
- progressive async traversal + invalid transport;
- Deep parallel frozen-start;
- profile semantic identity stability;
- PASS 2 core;
- PASS 2 Dossier integration;
- Dossier/Deep release-year compatibility;
- Deep balanced negative assessment;
- Deep legacy full reanalysis;
- Deep score evidence explainability;
- Deep invalid not-fit contract loop;
- canonical-writer staging;
- PASS 1 regressions;
- Progressive personalization;
- Deep-first final-score ordering;
- current staged projection accounting;
- unresolved-row preservation;
- visual activation routing;
- UI provenance;
- active production eligibility recomputation without attempt consumption.

## Boundaries

No production semantic execution was performed.

No Dossier or Deep result/state data was edited.

No Scheduled Task was created, edited, enabled, disabled, paused, resumed or run.

No scheduler, queue, retry owner, checkpoint owner, semantic worker or RANK-013 behavior was changed.

PR #132 implementation logic was not modified.

## PR #132 coordination

After PR #133 lands on `main`, PR #132 should refresh/rebase from the new `main` and rerun its mandatory validation.

This worker does not merge or otherwise change PR #132. Final PR #132 merge/publication acceptance remains owned by ЧАТ 1.

## Status

`complete_ready_for_director_acceptance`

## Exact references

- source `main`: `abab49194b7da2c205893e7bb9880727674ccfa0`;
- PR: #133;
- state-aware regression commit: `5de9b8c8b1fdf08562487551add028747fbb9306`;
- cleanup commit: `cefb2be82d18e0e0dba83fadbd282ec6427a8660`;
- deterministic fixture-expiry commit: `0e59843b1641fcabc554b3255c98fb0b15107cfa`;
- green PASS 2 run: `36808341769`;
- green backlog run: `36808341778`;
- dependency PR #132 observed implementation head/report context: `9b2c094aaa1c868162e2e6e269a92789b4dde131`.

## Recommended next step

Merge PR #133, then have ЧАТ 1 refresh PR #132 from the resulting `main` and rerun PR #132 mandatory validation without changing its implementation logic.

## Efficiency / reusable lesson

Long-lived production regressions must pin immutable attempt/provenance facts, not a mutable top-level workflow outcome. When an authorized recovery is allowed to advance current state, the original consumed attempt should remain the historical test anchor while current work is checked only for forbidden re-entry into the old first-pass identity.
