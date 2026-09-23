# Progressive PASS 1 coactive ingest recovery fix 01

Date: 2026-09-23  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Branch/source of truth: `main`  
Task: `WORKER_TASK_PROGRESSIVE_PASS1_COACTIVE_INGEST_RECOVERY_FIX_01.md`  
Final status: `blocked`

## Result

Implementation and validation are complete on current `main`; canonical recovery of the already-existing Friends vs Friends result is blocked only at the explicitly authorized one-off GitHub `workflow_dispatch` boundary.

No new PASS 1 semantic analysis was performed. The existing Friends vs Friends result artifact was not regenerated, overwritten, renamed, deleted, or edited. No PASS 1 state/work counts were manually edited. No Scheduled Task setting was changed and no Scheduled Task `Run now` was used.

## Implemented

- FIX-01: commit `c64a3a5706b2a3c2d8416c003a4d64f48b18bd93` — `scripts/ingest_progressive_pass1.py` now accepts canonical `pass1_active=true / pass2_active=true` and remains fail-closed for incompatible/missing flag combinations through `validate_activation_flags`.
- FIX-02: commit `0b97cb01109f906f4da6f2538f87cdcf61e1666a` — added `scripts/test_progressive_pass1_ingest_activation.py`, proving `true/true` accepted and stale/incompatible combinations rejected.
- FIX-03: commits `13d3a84a5f33df3beced90d2aa5dcc2f453624cc` and `aa78ca856aa416b821623d854e0c346a742f2415` — `.github/workflows/validate-progressive-pass2-core.yml` now watches, compiles, and runs the PASS 1 ingest entrypoint/regression for both push and pull_request validation surfaces.
- FIX-04 documentation: commit `08c16eecc1f9ac38ef797c4ed812a6792aef8976` reconciled `PROJECT_ROUTES.md`; commit `fb50a59bfa73b88f7ad16f60977779c317c85948` marked PPD-004/PPD-005 pre-activation status text as historical/superseded while preserving rationale.

## Validation evidence

GitHub validation run `35851821388`, job `107151055183`, conclusion `success`.

Successful steps included:
- PASS 2 core regression;
- PASS 2 Dossier integration regression;
- PASS 1 regression;
- PASS 1 ingest activation regression;
- Progressive personalization regression;
- current staged projection accounting;
- unresolved-row preservation;
- visual activation routing;
- active production eligibility recomputation without attempt consumption.

This proves the live ingest helper used by `scripts/ingest_progressive_pass1.py` accepts canonical coactivation and rejects incompatible states, and that the current Fast/Deep validation surface covers it.

## Recovery state at blocker

Fresh `main` immediately before the blocker record:
- `pass1_active=true`, `pass2_active=true`;
- PASS 1 scope: 560 total / 100 attempted / 460 remaining;
- first unprocessed item remains Friends vs Friends, appid `1785150`;
- work_id `4a85ac1f78ca5a8812a59631c715058f36032959b997b8be2504018c1100eed0`;
- exact existing artifact blob SHA `5643b0ad29ffae4514350d93f99b748d1f487974`;
- artifact outcome remains `analysis_incomplete`, issue_code `insufficient_evidence`;
- no current PASS 1 state entry exists yet for `game:1785150`;
- PASS 2 remains coactive; current projection was 560 target / 1 first-pass attempt / 532 waiting for dossier / 27 ready-or-pending.

The accepted incident baseline therefore has not been advanced by any manual edit or semantic replay.

## Blocker

The task authorizes exactly one bounded manual GitHub `workflow_dispatch` of the existing `.github/workflows/ingest-progressive-pass1.yml` after the fix is live.

The GitHub action surface connected to this chat exposes repository/file writes, workflow-run reads, logs/jobs, and rerun operations, but does not expose a workflow-dispatch operation. The task explicitly forbids substituting:
- rerun of the old failed ingest attempt;
- editing/overwriting the existing Friends artifact to manufacture another push;
- creating a second result;
- artificial inbox trigger artifacts;
- a new scheduler/recovery owner;
- Scheduled Task `Run now`.

Therefore the only contract-compliant recovery action cannot be executed from this chat.

## Acceptance matrix

- FIX-01 coactive ingest guard: PASS.
- FIX-02 focused regression: PASS.
- FIX-03 validation coverage: PASS.
- FIX-04 existing Friends result canonically ingested without re-analysis: BLOCKED at authorized workflow_dispatch.
- FIX-05 PASS 1 exact +1/-1 state/work delta: BLOCKED behind FIX-04.
- FIX-06 Deep recompute/validation after ingest: BLOCKED behind FIX-04.
- FIX-07 unrelated Fast/Dossier/Deep histories unchanged: PASS up to the recovery boundary; final post-ingest proof remains blocked.
- FIX-08 documentation reconciled: PASS.
- FIX-09 no Scheduled Task mutation / Run now: PASS for this execution.
- FIX-10 durable report committed and reread from main: PASS. Initial report commit `ea2afa9ad072a2196fc54fde1e0ec9fc6282bd1e` was reread from `main` as blob `697b4b172c500f3f2877b5da1f2b4502c8002619`; this closeout update must itself be reread from `main` before final response.

## Exact unblock

Execute the one task-authorized `workflow_dispatch` of existing `.github/workflows/ingest-progressive-pass1.yml`, then verify on fresh `main`:
1. the run succeeds through PASS 1 ingest and PASS 2 recomputation;
2. Friends vs Friends is consumed exactly once without semantic re-execution;
3. PASS 1 advances exactly +1 attempt / -1 remaining from the then-current canonical baseline;
4. Friends vs Friends is no longer first unprocessed solely because of the old stale guard;
5. the recovery commit changes only the expected exact PASS 1 ingest/state/work/receipt and derived PASS 2 projection surfaces, with no unrelated Fast/Dossier/Deep semantic-history rewrite.

