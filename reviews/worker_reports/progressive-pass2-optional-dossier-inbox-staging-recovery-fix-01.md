# Progressive PASS 2 Optional Dossier Inbox Staging Recovery Fix 01

Task: `progressive-pass2-optional-dossier-inbox-staging-recovery-fix-01`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Branch/source of truth: `main`  
Status: `complete_ready_for_director_acceptance`

## Scope and architecture preflight

This task fixes only the confirmed GitHub-owned PASS 2 canonical persistence blocker after successful ingest.

1. PASS 2 ingest, attempt accounting, canonical persistence, work recomputation, and recovery ownership remain GitHub/GitHub Actions control-plane responsibilities under `config/execution_ownership_contract.json` and `config/progressive_pass2_contract.json`.
2. The defect is a commit/staging robustness failure inside the existing canonical-writer workflow, not a reason to add a scheduler, queue, retry loop, checkpoint owner, or persistence owner.
3. `data/ai_inbox/taste_steam_review_dossiers` is an optional/absent-capable Dossier transport inbox at the PASS 2 commit point: reconciliation may have no transport directory to stage, while canonical Dossier state/work/projection paths remain required.
4. The existing shared serialization boundary remains `taste-steam-review-dossier-canonical-writer` with `cancel-in-progress: false`. Dossier reconciliation remains before PASS 2 recomputation/ingest.
5. Existing immutable PASS 2 result artifacts can be replayed through the same canonical ingest path. No new Deep semantic execution is required or permitted when the exact result/terminal-receipt path already exists.

## Confirmed failure reproduction / explanation

Observed failed GitHub Actions run:
- workflow: `Ingest Progressive PASS 2 item`
- run: `35900791199`
- job: `107316158662`
- source head: `f082952fe52aca1de69c516e02e3257dc29fb203`

The job proved that semantic/ingest processing was already successful before persistence failed:
- Dossier reconciliation completed.
- Dossier validation completed.
- PASS 2 work recomputation completed.
- `scripts/ingest_progressive_pass2.py` completed with `processed_result_artifact_count=4`, `accepted_result_count=1`, and `PROGRESSIVE_PASS2_INGEST=PASS`.
- PASS 2 revalidation passed.
- The next commit/staging block failed with:
  `fatal: pathspec 'data/ai_inbox/taste_steam_review_dossiers' did not match any files`
  and exit code 128.

Therefore the confirmed blocker was a required-looking Git pathspec for an optional absent directory after successful ingest, not a semantic validation or PASS 2 authorization failure.

## Implementation

### 1. PASS 2 canonical-writer staging helper

Created:
- `scripts/stage_progressive_pass2_canonical_writer.sh`
- creation commit: `8c9ee2af9aad14c29a5649f787f803f41647ec0b`
- current blob on validated main: `0ff6c6b588934bd2ff36595aef296de08400cb1e`

Required paths remain strict and are staged by one unconditional `git add -A -- ...` block:
- `data/ai_inbox/progressive_pass2`
- `data/cache/progressive_pass2_state.json`
- `data/cache/progressive_pass2_ingest_receipts`
- `data/production/pre_ai/progressive_pass2_work.json`
- canonical Dossier store/work/index/validation/worker-groups paths.

Only absence-capable paths use an existence-or-tracked check before `git add -A -- <path>`:
- `data/cache/progressive_pass2_execution_receipts`
- `data/ai_inbox/taste_steam_review_dossiers`
- `data/quarantine/taste_steam_review_dossier_inbox`
- `data/audit/taste_steam_review_dossier_group_failures.jsonl`

This preserves staging of optional additions and tracked deletions while making a completely absent/untracked optional path safe.

### 2. Production workflow

Updated:
- `.github/workflows/ingest-progressive-pass2.yml`
- implementation commit: `30595a05e807f5fcf5cdd1da2a9531d83f570ff2`
- current validated blob: `ca269924e4546965cd5396a2e2c0530c2589f972`

The commit block now calls:
`bash scripts/stage_progressive_pass2_canonical_writer.sh`

Unchanged architecture verified on fresh main:
- shared concurrency group remains `taste-steam-review-dossier-canonical-writer`;
- `cancel-in-progress: false` remains;
- Dossier reconciliation still executes before PASS 2 ingest;
- PASS 2 recomputation, activation guard, ingest, and post-ingest revalidation remain in the existing sequence.

### 3. Focused regression

Created:
- `scripts/test_progressive_pass2_workflow_staging.py`
- creation commit: `ee63ae18732202a95185a0040d4fd4060c132ba2`
- current blob: `47a7c2f664666c286e35fa7a9e76857c537c024e`

The regression uses temporary Git repositories and specifically reproduces the failed persistence shape:
- required PASS 2 result transport is consumed/staged as a deletion;
- PASS 2 state changes;
- `data/ai_inbox/taste_steam_review_dossiers` is completely absent;
- staging and commit still succeed.

It also proves:
- optional tracked deletions are still staged;
- optional additions are still staged;
- required PASS 2 paths remain strict and are not silently converted to optional paths.

### 4. Integration and CI wiring

Updated:
- `scripts/test_progressive_pass2_integration.py` — commit `2a751236b5435feaf4c9eee5dd0bc906e4a64f0a`
- `.github/workflows/validate-progressive-pass2-core.yml` — final scoping commit `ca26b2bbd1e4e7f2d314dd6227bff021166f9902`

The PASS 2 core validation now permanently runs the focused staging regression.

## Validation

Final PASS 2 validation:
- workflow: `Validate Progressive PASS 2 core`
- run: `35904500536`
- job: `107328640544`
- head: `ca26b2bbd1e4e7f2d314dd6227bff021166f9902`
- conclusion: `success`

Successful steps include:
- PASS 2 core regression;
- PASS 2 Dossier integration regression;
- PASS 2 canonical-writer staging regression;
- PASS 1 regression;
- PASS 1 ingest activation regression;
- PASS 1 canonical-writer staging regression;
- Progressive personalization regression;
- current staged projection accounting;
- unresolved-row preservation;
- visual activation routing;
- UI provenance;
- active production eligibility recomputation without consuming attempts.

Execution ownership validation:
- run `35904500434`
- head `ca26b2bbd1e4e7f2d314dd6227bff021166f9902`
- conclusion: `success`.

### Canonical-writer/coalescing suite isolation

The requested existing coalescing regression was explicitly run in `Validate Progressive PASS 2 core` run `35904262648`, job `107327837642`.

Relevant PASS 2 checks completed first and passed:
- PASS 2 core regression;
- PASS 2 Dossier integration regression;
- new PASS 2 canonical-writer staging regression.

The generic Dossier coalescing test then stopped on an unrelated pre-existing PASS 1 static assertion:
- test: `CanonicalWriterCoalescingLivenessTests.test_every_shared_writer_reconciles_state_before_dependent_projection_or_write`
- assertion: expected literal `data/cache/taste_steam_review_dossiers` inside `.github/workflows/ingest-progressive-pass1.yml`.
- current PASS 1 workflow delegates staging to `scripts/stage_progressive_pass1_canonical_writer.sh`, so that path is intentionally no longer inline in the workflow.

This task did not repair that unrelated PASS 1 baseline regression, per the explicit task prohibition. The temporary addition of the generic coalescing suite to PASS 2 core CI was removed; the task-specific PASS 2 staging regression remains permanent. PASS 2 shared-writer/concurrency/reconciliation invariants are also covered by the passing PASS 2 integration regression.

## Fresh pre-recovery state

Fresh main inspection after validation shows four immutable PASS 2 result artifacts still present.

Current exact-compatible result:
- title: `Shadow Warrior 3: Definitive Edition`
- appid: `1036890`
- work_id: `e7fa6fa96ab0a7ea01528df4ce0e634eed0877d0e0c320efefb8454f8b9bf987`
- authorization_id: `6c421679773f4d3fd0d533469e5b2e90c153bcf8b7041302e68cdf28ba77e160`
- outcome: `analysis_incomplete`
- issue: `insufficient_evidence`
- Dossier revision: `semantic-bounded-retrieval-2026-09-23`
- result blob: `e7369c686feb98730ce9b4e076a7f97bc2e8ce0e`

The other three present result artifacts have the prior Dossier revision `validator-generator-parity-fix-2026-09-20`. They were not deleted, overwritten, renamed, rebound, or manually reinterpreted.

Fresh canonical PASS 2 state still contains only the earlier Monster Train incomplete entry. Fresh work before recovery reports:
- `deep_total_current_coverage_target=511`
- `deep_first_pass_attempted_count=0`
- `deep_authoritative_completed_count=0`
- `deep_waiting_for_dossier_count=499`
- `deep_ready_or_pending_count=12`
- `recovery_pending_count=0`

This confirms that this implementation task itself consumed no additional Deep attempt.

## Recovery status

The available GitHub connector in this worker chat exposes read/validation/rerun operations but no action capable of invoking a workflow's `workflow_dispatch`.

Per task contract, no substitute trigger was invented and no immutable result artifact was touched merely to wake ingest.

Exactly one operator action remains:

1. In GitHub Actions, run the existing workflow **`Ingest Progressive PASS 2 item`** via its **`workflow_dispatch`** on `main`, once.

Do **not** run the `Progressive Deep Worker` Scheduled Task and do **not** perform a new semantic Deep attempt for the already-created result.

After that one canonical ingest dispatch, verification should read fresh `main` and confirm:
- the exact-compatible current result is persisted exactly once;
- first-pass attempt accounting advances exactly once for that identity;
- work projection recomputes;
- the three old-binding artifacts are classified only by canonical ingest rules;
- downstream visual behavior follows the existing architecture;
- no second semantic attempt was consumed.

No recovery dispatch was performed by this worker chat, so those post-recovery runtime assertions are intentionally not claimed as completed.

## Acceptance checklist

- FIX-01: PASS — exact run `35900791199` failure reproduced/explained from job log.
- FIX-02: PASS — absent optional Dossier inbox is safe during PASS 2 staging.
- FIX-03: PASS — required PASS 2 state/work/result staging remains strict.
- FIX-04: PASS — Dossier reconciliation ordering and shared writer concurrency remain intact.
- FIX-05: PASS — focused regression reproduces absent optional directory and successful commit/staging.
- FIX-06: PASS — final relevant PASS 2 regression suite run `35904500536` succeeded.
- FIX-07: PASS WITH ISOLATED PRE-EXISTING FAILURE — generic coalescing suite was run; it stopped on the unrelated stale PASS 1 inline-staging assertion described above. Task-specific PASS 2 writer/staging and integration checks pass.
- FIX-08: PASS — no Progressive Deep Scheduled Task action and no semantic Deep rerun occurred.
- FIX-09: READY / OPERATOR ACTION REQUIRED — connector cannot issue `workflow_dispatch`; exactly one operator dispatch of existing `Ingest Progressive PASS 2 item` remains before post-recovery acceptance can be observed.
- FIX-10: PASS — old-binding artifacts were not reinterpreted or rewritten.
- FIX-11: PASS — no new orchestration/control-plane owner was introduced.

## Final result

The confirmed PASS 2 persistence blocker is fixed and validated on `main`. The implementation is ready for Director acceptance. Canonical recovery of the already-created inbox artifacts still requires exactly one operator GitHub Actions `workflow_dispatch` of the existing PASS 2 ingest workflow; no Deep semantic rerun is required.
