# WORKER TASK — PROGRESSIVE PASS 2 OPTIONAL DOSSIER INBOX STAGING RECOVERY FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`

Base branch / source of truth: `main`

Repository scope guard: do not search, read, change, or use any other repository.

Task ID: `progressive-pass2-optional-dossier-inbox-staging-recovery-fix-01`

Mode: `IMPLEMENT`

## User authorization

The user explicitly authorized proceeding after the Director checked the current PASS 2 failure.

Fix only the confirmed GitHub-owned PASS 2 ingest persistence blocker and restore canonical ingest of already-created current PASS 2 result artifacts without rerunning semantic Deep work.

## START

First execute the current `CHAT_PROTOCOL.md` START gate and read this task fully before broad investigation.

Read only the minimum current surfaces needed, including:

- `.github/workflows/ingest-progressive-pass2.yml`
- `scripts/ingest_progressive_pass2.py`
- `scripts/test_progressive_pass2.py`
- relevant PASS 2 integration/regression tests
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `data/production/pre_ai/progressive_pass2_work.json`
- `data/cache/progressive_pass2_state.json`
- the current relevant result artifacts under `data/ai_inbox/progressive_pass2/results/`
- `reviews/worker_reports/progressive-deep-production-activation-live-acceptance-01.md`
- current ownership/concurrency contract required by protocol.

## Confirmed trigger

Current failed GitHub Actions run:

- workflow: `Ingest Progressive PASS 2 item`
- run id: `35900791199`
- job id: `107316158662`
- source head: `f082952fe52aca1de69c516e02e3257dc29fb203`

Observed sequence in the failed job:

1. Dossier inbox reconciliation completed.
2. Dossier validation completed.
3. PASS 2 work recomputation completed:
   `PROGRESSIVE_PASS2_WORK=READY ... target=511 first_pass_attempted=0 authoritative=0 waiting_dossier=502 ready_or_pending=9 recovery_pending=0`.
4. `scripts/ingest_progressive_pass2.py` itself completed successfully:
   - `processed_result_artifact_count=4`
   - `accepted_result_count=1`
   - `PROGRESSIVE_PASS2_INGEST=PASS`
5. PASS 2 revalidation passed.
6. Persistence then failed in the workflow commit/staging step with:
   `fatal: pathspec 'data/ai_inbox/taste_steam_review_dossiers' did not match any files`
   and exit code 128.

Current `main` therefore still shows:

- PASS 2 active;
- current projection uses Dossier evidence revision `semantic-bounded-retrieval-2026-09-23`;
- `deep_first_pass_attempted_count=0`;
- `deep_authoritative_completed_count=0`;
- `deep_waiting_for_dossier_count=502`;
- `deep_ready_or_pending_count=9`;
- canonical PASS 2 state still contains only the earlier Monster Train incomplete entry and does not contain the newly accepted-in-working-tree current result.

The currently relevant exact-compatible current result artifact already exists create-only for:

- `Shadow Warrior 3: Definitive Edition`
- appid `1036890`
- work_id `e7fa6fa96ab0a7ea01528df4ce0e634eed0877d0e0c320efefb8454f8b9bf987`
- outcome `analysis_incomplete`
- current Dossier revision `semantic-bounded-retrieval-2026-09-23`.

Three older PASS 2 inbox result artifacts also exist with the prior Dossier binding revision. Do not manually reinterpret, delete, overwrite, rebind, or count them. Let the canonical ingest path classify them under current rules.

## Architecture preflight

Before editing, record:

1. current owner of PASS 2 ingest/persistence;
2. why this is a staging robustness defect inside the existing canonical-writer workflow, not a reason for a new scheduler/retry/queue;
3. why `data/ai_inbox/taste_steam_review_dossiers` is optional/absent-capable at this commit point;
4. how the fix preserves the shared `taste-steam-review-dossier-canonical-writer` concurrency boundary and state-based Dossier reconciliation;
5. how already-created immutable PASS 2 result artifacts can be ingested without another semantic attempt.

## Required implementation

Implement the smallest robust fix so absence of the optional Dossier inbox path cannot fail PASS 2 canonical persistence after successful ingest.

At minimum:

1. Make staging of `data/ai_inbox/taste_steam_review_dossiers` absence-safe.
2. Audit the same commit block for directly analogous optional pathspec hazards and make only the bounded consistency changes needed to prevent the same class of failure there.
3. Do not weaken staging for required PASS 2 state/work/result paths.
4. Preserve Dossier reconciliation before PASS 2 recomputation/ingest.
5. Preserve create-only PASS 2 transport, exact bindings, one first-pass attempt accounting, recovery ownership, and shared canonical-writer concurrency.
6. Add/adjust a focused regression reproducing the observed absent optional Dossier inbox directory and proving the workflow commit/staging path remains successful.
7. Re-run the relevant PASS 2 and canonical-writer/coalescing regression suites.

## Recovery requirement

After the fix is merged and validated, recover the **already-created** PASS 2 inbox artifacts through the existing GitHub-owned canonical ingest path.

Do not run the Progressive Deep Scheduled Task and do not perform another semantic attempt for an item whose exact result/receipt path already exists.

If the available GitHub tooling in the worker chat can safely invoke the existing `workflow_dispatch` of `Ingest Progressive PASS 2 item`, exactly one bounded recovery dispatch is authorized after the fix is on current `main`.

If the available tooling cannot dispatch that workflow, do **not** invent another trigger and do not mutate immutable result artifacts merely to trigger ingest. Finish with `needs_user_decision` or `complete_ready_for_director_acceptance` as appropriate and state that one operator GitHub Actions `workflow_dispatch` is still required for recovery.

After any authorized recovery run, verify from fresh `main`:

- canonical PASS 2 state persisted the currently valid result(s) exactly once;
- attempt accounting is correct;
- current work projection advanced/recomputed;
- stale/old-binding artifacts were handled only by canonical ingest rules;
- visual rebuild behavior is consistent with the existing accepted architecture;
- no second semantic attempt was consumed for the same current work identity.

## Explicit prohibitions

Do not:

- create/edit/enable/disable/run any ChatGPT Scheduled Task;
- press Deep `Run now`;
- rerun semantic Deep work;
- overwrite/delete/rename/rebind an existing PASS 2 result or terminal receipt;
- fabricate a terminal receipt;
- manually mark PASS 2 attempts complete;
- edit Fast/PASS 1 semantic state;
- edit Dossier semantic evidence/history;
- create a second retry loop, queue, scheduler, concurrency group, or persistence owner;
- repair the unrelated Progressive PASS 1 baseline regression unless this exact task proves it blocks the required PASS 2 fix.

## Acceptance checks

- FIX-01: exact run `35900791199` failure reproduced/explained from current workflow.
- FIX-02: absent `data/ai_inbox/taste_steam_review_dossiers` is safe during staging.
- FIX-03: no required PASS 2 staging path was made optional accidentally.
- FIX-04: canonical Dossier reconciliation and shared writer concurrency remain intact.
- FIX-05: focused regression covers the absent optional directory.
- FIX-06: relevant PASS 2 regression suite passes.
- FIX-07: relevant canonical-writer/coalescing regression passes, or any unrelated pre-existing failure is explicitly isolated with evidence.
- FIX-08: no Deep semantic rerun / Scheduled Task action occurred.
- FIX-09: if recovery dispatch is possible, current valid inbox result is canonically persisted exactly once and projection advances; otherwise exact operator action remaining is stated.
- FIX-10: stale/old-binding result artifacts are not manually reinterpreted or rewritten.
- FIX-11: no new orchestration/control-plane owner introduced.

## Durable report

Write and commit:

`reviews/worker_reports/progressive-pass2-optional-dossier-inbox-staging-recovery-fix-01.md`

Allowed final statuses:

- `complete_ready_for_director_acceptance`
- `needs_user_decision`
- `blocked`

Before completion, reread the committed report from fresh `main`.
