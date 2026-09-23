# WORKER TASK — PROGRESSIVE PASS 1 COACTIVE INGEST + RECOVERY FIX 01

## Assignment
- Worker slot: **NEW physical ЧАТ 2**
- Mode: **IMPLEMENT / ACTIVATE / VALIDATE**
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Base branch / source of truth: `main`
- Durable report: `reviews/worker_reports/progressive-pass1-coactive-ingest-recovery-fix-01.md`

Do not search, read, modify, or use any other repository.

## START
1. Read current `CHAT_PROTOCOL.md` from `main` and execute its START gate.
2. Read this task fully.
3. Read the accepted audit:
   `reviews/worker_reports/progressive-fast-deep-coactivation-stale-guard-audit-01.md`
4. Read current canonical Progressive contracts and only the implementation files needed for this bounded fix.

## Accepted diagnosis
The audit status is `complete_additional_analogues_found`.

Confirmed production defect:
- current canonical state correctly allows `pass1_active=true` and `pass2_active=true`;
- `scripts/ingest_progressive_pass1.py` still contains the stale pre-Deep guard requiring `pass2_active=false`;
- real ingest run `35812546365` failed with `Progressive PASS 1 work activation flags are invalid`;
- the exact Friends vs Friends result already exists and must not be regenerated.

Audit found no second current production runtime blocker of the same class. Additional findings are only:
- missing focused regression around the production ingest guard;
- validation workflow coverage gap for the PASS 1 ingest entrypoint;
- stale pre-activation wording in `PROJECT_ROUTES.md` and historical PPD-004/PPD-005 status text.

## Required implementation

### FIX-01 — PASS 1 ingest coactivation guard
Align `scripts/ingest_progressive_pass1.py` with the accepted current architecture.

The production ingest must accept the canonical coactive state:
- `pass1_active=true`
- `pass2_active=true`

It must remain fail-closed for incompatible activation state. Do not remove activation validation wholesale.

Do not change Fast/Deep eligibility semantics, attempt budget, ordering, result schema, or ownership.

### FIX-02 — focused regression
Add a focused regression that actually exercises the production ingest activation guard or a pure helper used by that guard.

It must prove at minimum:
- current canonical `true/true` is accepted;
- stale/incompatible flag combinations fail closed;
- the test cannot pass while the live ingest entrypoint still rejects the same state.

### FIX-03 — validation coverage
Extend the appropriate current Progressive validation workflow so changes to the PASS 1 ingest entrypoint and its focused regression are covered by the Fast/Deep activation validation surface.

Do not create a new scheduler or parallel validation architecture.

### FIX-04 — documentation reconciliation
Boundedly update:
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`

Preserve historical rationale, but clearly mark old “Deep inactive / later activation required” statements as superseded by the current production-active `FAST-DOSSIER-DEEP-V1` architecture.

Do not rewrite unrelated historical decisions.

## Existing Friends vs Friends artifact — recovery rules
The current exact artifact was created in commit:
`63ceb92cc4a3628b987a5ee537cb22ca30c35be8`

Identity at the accepted audit:
- appid `1785150`
- work_id `4a85ac1f78ca5a8812a59631c715058f36032959b997b8be2504018c1100eed0`

Do **not**:
- regenerate semantic analysis;
- create a second result;
- overwrite, rename, delete, or edit the existing artifact;
- manually edit PASS 1 state/work counts;
- skip Friends vs Friends.

After the fix is merged to current `main`, recover through the existing GitHub-owned PASS 1 ingest path.

Because the original push event has already occurred, **one bounded manual GitHub `workflow_dispatch` of the existing `.github/workflows/ingest-progressive-pass1.yml` is authorized if needed to consume the already-existing artifact**.

This authorization is only for the GitHub ingest workflow after the fix is live. It is not authorization for:
- Scheduled Task `Run now`;
- new semantic work;
- workflow rerun of the old failed attempt;
- another scheduler;
- arbitrary workflow dispatches.

## Acceptance requirements
Prove on fresh `main`:

1. current coactive Fast+Deep state passes the production PASS 1 ingest activation guard;
2. incompatible activation combinations still fail closed;
3. focused regression and relevant existing Progressive tests pass;
4. validation workflow coverage includes the production ingest guard/regression;
5. the exact pre-existing Friends vs Friends artifact is consumed by GitHub-owned ingest without semantic re-execution;
6. PASS 1 durable state advances by exactly one attempt for that exact work identity from the incident baseline (100 -> 101 if no intervening canonical PASS 1 change occurred);
7. PASS 1 remaining scope decreases correspondingly (460 -> 459 if the same baseline still applies);
8. Friends vs Friends no longer remains the first unprocessed item solely because of the stale guard;
9. PASS 2 recomputation/validation completes through the same canonical writer after PASS 1 ingest;
10. no Fast history is rewritten beyond the exact accepted result; no Deep or Dossier semantic history is rewritten;
11. no Scheduled Task was enabled/disabled/edited and no Scheduled Task `Run now` occurred;
12. documentation is reconciled without changing canonical architecture.

If fresh `main` has changed before activation, use exact current values and prove the equivalent +1/-1 canonical PASS 1 delta for this artifact rather than forcing stale counts.

## Hard prohibitions
Do not:
- change current Fast/Dossier/Deep architecture;
- make Fast a prerequisite for Deep;
- make Deep inactive again;
- add automatic PASS 1 retry;
- add hidden attempt quota;
- create new queue/scheduler/recovery owner;
- touch Dossier Scheduled Task self-disable behavior;
- change external ChatGPT Scheduled Task settings;
- perform new PASS 1 semantic analysis;
- alter unrelated site UI work.

## Validation gates
- **FIX-01** coactive production ingest guard corrected.
- **FIX-02** focused regression proves true/true accepted and incompatible states rejected.
- **FIX-03** validation workflow covers ingest entrypoint/regression.
- **FIX-04** existing Friends result canonically ingested without re-analysis.
- **FIX-05** PASS 1 state/work projection advances exactly once.
- **FIX-06** Deep recompute/validation succeeds after ingest.
- **FIX-07** Fast/Dossier/Deep unrelated histories unchanged.
- **FIX-08** stale documentation reconciled.
- **FIX-09** no Scheduled Task mutation or Scheduled `Run now`.
- **FIX-10** durable report committed to `main` and reread exactly from `main`.

## Live recovery continuation — commit-stage optional-path failure

The operator executed the one authorized manual `workflow_dispatch`.

Observed result:
- PASS 1 ingest step succeeded;
- PASS 2 recompute succeeded;
- PASS 1 revalidation succeeded;
- the workflow then failed only in `Commit PASS 1 state and remaining work`;
- exact failure: `fatal: pathspec 'data/ai_inbox/taste_steam_review_dossiers' did not match any files`;
- failure exit code: 128.

This is a GitHub-owned workflow staging defect inside the same unfinished recovery task.

Required continuation:
1. Fix only the commit/staging robustness needed so optional Dossier inbox/quarantine/audit paths do not make PASS 1 canonical commit fail when absent.
2. Preserve the shared canonical-writer ownership and Dossier reconcile behavior.
3. Add/extend regression coverage so the PASS 1 workflow can commit when those optional paths are absent.
4. Do not regenerate or edit the existing Friends vs Friends result.
5. Do not manually edit PASS 1 state/work.
6. Do not use Scheduled Task `Run now`.
7. Do not dispatch another GitHub workflow from the worker chat.
8. After the fix is merged and validated, stop and update the durable report with exact fresh-main state and whether one additional operator `workflow_dispatch` is required to finish recovery.

The previous one-off operator dispatch has been consumed by the failed commit-stage attempt. A second operator dispatch is **not authorized by this task amendment**; if required, report that exact need for Director/user approval.

## Report
Create:
`reviews/worker_reports/progressive-pass1-coactive-ingest-recovery-fix-01.md`

Final status:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `blocked`

Include exact commits/runs/artifacts sufficient for Director verification, but keep the report compact.
