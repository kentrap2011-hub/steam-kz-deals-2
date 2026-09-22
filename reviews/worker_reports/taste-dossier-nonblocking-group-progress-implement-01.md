# Taste Dossier non-blocking group progress implement 01

**Task:** `taste-dossier-nonblocking-group-progress-implement-01`  
**Date:** 2026-09-22  
**Status:** `complete_ready_for_user_scheduled_validation`

## Architecture preflight

- Canonical owner remains **GitHub control plane** for immutable group plan, per-group state, strict validation, persistence, failed-group recovery eligibility, next-work projection, and completeness.
- Scheduled ChatGPT remains bounded semantic data-plane only: it reads the GitHub projection and may publish only the exact deterministic create-only candidate artifact.
- No new queue, retry daemon, checkpoint owner, recurring stage, scheduler, or cadence was introduced.
- Canonical relationships are now: full work manifest = authority; V2 worker index/descriptors = derived read projection; inbox = immutable transport only; dossier cache = accepted evidence only; validation status = observability/recovery projection; recovery contract = GitHub-owned failed-group handling.
- Snapshot replacement remains exact-bound and fail-closed: old artifacts never rebind to a new snapshot and are stale-quarantined by GitHub.

## Old vs new progress model

**Old:** one `canonical_expected_sequence`; GitHub could accept only the maximal contiguous valid prefix. A bad expected group pinned every later group.

**New:** every immutable predeclared group has one GitHub-owned state: `pending`, `accepted`, or `failed_or_invalid_pending_recovery`. Every present pending group is strict-validated independently. Valid groups persist independently; invalid groups are quarantined and classified only for their own identity. Normal traversal uses only pending groups.

`normal_first_pass_complete=true` means no pending groups remain. `all_groups_accepted` / existing `full_backlog_complete` retain the stricter all-required-accepted meaning, so failed groups never become accepted evidence.

## Exact canonical files changed

Primary implementation `79f1c38c218d0d2ea89d7722e4ff5b1c9840d508`:
- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
- `.github/workflows/validate-taste-dossier-buffered.yml`
- `PROJECT_DECISIONS.md`
- `PROJECT_ROUTES.md`
- `config/execution_ownership_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_parallel_validation_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/taste_steam_review_dossier_recovery_contract.json`
- `scripts/build_taste_steam_review_dossier_work.py`
- `scripts/ingest_taste_steam_review_dossier_inbox.py`
- `scripts/taste_steam_review_dossier_buffered.py`
- `scripts/taste_steam_review_dossier_daily.py`
- `scripts/taste_steam_review_dossier_group_progress.py`
- `scripts/taste_steam_review_dossier_parallel_validation.py`
- `scripts/taste_steam_review_dossier_recovery.py`
- `scripts/taste_steam_review_dossier_web.py`
- `scripts/taste_steam_review_dossier_worker_projection.py`
- focused Dossier regression files under `scripts/test_taste_steam_review_dossier_*.py`.

Runtime activation `f0ffb166f37b0ba2da363f8908359373d8b17939`:
- `config/taste_steam_review_dossier_runtime_prompt.md` added as a traversal/schedule-only, non-semantic binding;
- Dossier contract, worker projection, build/validation workflows, parallel-validation regression, and Story-DLC regression aligned to the V2 projection without changing semantic evidence identity.

Regression isolation `93a2bddda9232134147c1960af46681f495c4930`:
- `scripts/ingest_taste_steam_review_dossier_inbox.py`
- `scripts/test_taste_steam_review_dossier_strict_recovery.py`
- removed two proven synthetic test artifacts and their synthetic `data/audit/taste_steam_review_dossier_group_failures.jsonl` entries. The final real workflow did not recreate them.

## Migration and g000005

The diagnosed snapshot was `04298ca0b80d00cd819af116323de3d1c4906d6ed71e84f40c15c6978d0d08d8`. Groups 1–4 had already accepted 12 dossiers. g000005 was validator-rejected for bound-record `evidence_languages` mismatch; g000006 also had a separate strict freshness failure.

The new implementation contains the required same-snapshot migration path: existing accepted prefix becomes accepted per-group state; a present invalid pending group becomes `failed_or_invalid_pending_recovery`; later present valid groups are independently accepted.

During production activation, however, the canonical source scope changed before reconciliation, so GitHub legitimately produced a new snapshot instead of pretending the old group identity was still current. The old g000005 and g000006 artifacts were moved as byte-identical Git renames into:
- `data/quarantine/taste_steam_review_dossier_inbox/stale/04298ca0.../...g000005...json`
- `data/quarantine/taste_steam_review_dossier_inbox/stale/04298ca0.../...g000006...json`

Thus the historical g000005 was **not accepted**, cannot pin current progress, and was not rewritten or rebound. Its exact same-snapshot failed-state transition is covered by focused BAD-g5/GOOD-g6/g7 regression; stale/superseded handling is the correct production state once that snapshot ceased to be current.

All 12 previously accepted group-1..4 appids remain present in `data/cache/taste_steam_review_dossiers/`: 1000010, 1000360, 1003590, 1003890, 1018800, 1025440, 1034860, 1036890, 1047010, 1051310, 1051690, 1054490.

## Validation

- Implementation build run `35706907703` exposed a regression failure and was not treated as acceptance.
- Runtime activation commit `f0ffb166...` then passed canonical build run `35708062857` (#161), job `106681688723`; Dossier prepare, reconcile, validation projection, and fixed-daily regression steps all succeeded. Execution ownership run `35708062863` also succeeded.
- A post-activation audit found test-fixture leakage into production audit/quarantine. Commit `93a2bdd...` isolated failure paths inside `TemporaryDirectory` and removed only the two proven synthetic artifacts.
- Final canonical build run `35721372787` (#164), job `106724811441`, completed successfully. Dossier steps 19–22 and atomic pre-AI commit step 26 all succeeded; emitted commit: `b60aca7f5bc76263bc1b21f522747a5e37a4d095`.
- After that real workflow, `data/audit/taste_steam_review_dossier_group_failures.jsonl` and the synthetic `failed_group` quarantine root are absent, proving the fixture leak did not recur.
- Focused regression covers BAD g5 / GOOD g6 / GOOD g7 independent persistence, failed-group recovery projection, accepted-group non-reprocessing, stale snapshot isolation, deterministic filenames, V2 next-pending traversal, and schedule-edit prohibition.
- No PASS 1, PASS 2, or Taste Semantic Producer behavior was changed by this task.

## Current active state after activation

Current canonical snapshot: `9cf59f4d94d1b4c7270bece5464666e3eb2359b87bd74cbefe3883b969f90689`  
Prepared scope SHA: `39867146352844fbbf1ff442b64adc63ca14ba1d0793570909486c3e602d033d`

- required: 550
- canonical groups: 184
- accepted groups: 0
- failed groups: 0
- pending groups: 184
- next pending: `g000001`
- `normal_first_pass_complete=false`
- `all_groups_accepted=false`
- `full_backlog_complete=false`
- worker index schema: `TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2`
- validation status schema: `TASTE-STEAM-REVIEW-DOSSIER-PARALLEL-VALIDATION-STATUS-V2`
- current buffered candidate count: 0

## Acceptance NB-01..NB-16

- **NB-01 PASS** — one invalid group does not block later pending groups.
- **NB-02 PASS** — valid groups persist independently.
- **NB-03 PASS** — failed groups have canonical failed/incomplete state and leave normal traversal.
- **NB-04 PASS** — failed groups have separate GitHub-owned recovery/reopen semantics.
- **NB-05 PASS** — deterministic create-only immutable transport preserved.
- **NB-06 PASS** — strict semantic validation preserved.
- **NB-07 PASS** — exact snapshot/plan/binding validation preserved.
- **NB-08 PASS** — GitHub owns state/order/recovery/completeness.
- **NB-09 PASS** — all 12 previously accepted dossiers remain in canonical cache; no accepted evidence was lost.
- **NB-10 PASS with rollover-safe production handling** — historical g000005 was never accepted and no longer blocks; because its snapshot was superseded during activation it was stale-quarantined rather than retained as current failed state; exact same-snapshot failed classification is regression-proven.
- **NB-11 PASS** — V2 resume uses GitHub `next_pending_sequence`, not the first historical failure.
- **NB-12 PASS** — runtime prompt and ownership contract explicitly forbid worker schedule enable/disable/pause/delete/reschedule/edit.
- **NB-13 PASS** — hourly external cadence preserved; no scheduler added.
- **NB-14 PASS** — first-pass exhaustion is separate from all-evidence acceptance.
- **NB-15 PASS** — no PASS 1/PASS 2/Taste Semantic Producer behavior changed.
- **NB-16 PASS pending final report commit/reread protocol** — this report is the durable closeout artifact and must be reread from `main` after its commit before final response.

## Remaining operator validation

Repository/GitHub activation is complete. The only remaining external validation is a single clean execution of the existing `Taste Steam Review Dossier` Scheduled Task against the current V2 index. The worker must not change its schedule or create another task.

## Exact refs

- implementation: `79f1c38c218d0d2ea89d7722e4ff5b1c9840d508`
- runtime activation: `f0ffb166f37b0ba2da363f8908359373d8b17939`
- regression isolation: `93a2bddda9232134147c1960af46681f495c4930`
- successful activation build: run `35708062857`, job `106681688723`
- execution ownership validation: run `35708062863`
- final successful build: run `35721372787`, job `106724811441`
- final atomic pre-AI commit: `b60aca7f5bc76263bc1b21f522747a5e37a4d095`

## Recommended next step

Run **exactly one** clean `Run now` of the existing `Taste Steam Review Dossier` Scheduled Task against the current V2 index, without changing its schedule, then allow the normal GitHub ingest workflow to classify whatever exact groups it publishes.
