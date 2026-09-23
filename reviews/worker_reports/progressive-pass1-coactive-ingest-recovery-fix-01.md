# Progressive PASS 1 coactive ingest recovery fix 01

Date: 2026-09-23  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Branch/source of truth: `main`  
Task: `WORKER_TASK_PROGRESSIVE_PASS1_COACTIVE_INGEST_RECOVERY_FIX_01.md`  
Final status: `blocked`

## Result

The original coactivation defect and the follow-up commit/staging defect are both fixed and regression-covered on current `main`.

Recovery itself is still not canonically complete because the one authorized operator `workflow_dispatch` successfully performed ingest/recompute/revalidation in its workspace but failed before commit. The task amendment explicitly does not authorize a second operator dispatch.

No semantic result was regenerated or edited by this continuation. No PASS 1 state/work count was manually edited. No Scheduled Task setting was changed and no Scheduled Task `Run now` was used. No new `workflow_dispatch` was launched by this continuation.

## Coactivation fix already landed

- `c64a3a5706b2a3c2d8416c003a4d64f48b18bd93` — live PASS 1 ingest accepts canonical `pass1_active=true / pass2_active=true` and remains fail-closed for incompatible flags.
- `0b97cb01109f906f4da6f2538f87cdcf61e1666a` — focused activation regression.
- `13d3a84a5f33df3beced90d2aa5dcc2f453624cc` + `aa78ca856aa416b821623d854e0c346a742f2415` — activation validation coverage.
- `08c16eecc1f9ac38ef797c4ed812a6792aef8976` + `fb50a59bfa73b88f7ad16f60977779c317c85948` — route/decision documentation reconciled with active `FAST-DOSSIER-DEEP-V1`.

## Consumed operator dispatch and commit-stage defect

Authorized operator dispatch:
- run `35863646555`;
- job `107189704142`;
- source head `72c31348d93b7152ecb23b8c7a54a8c29ea2a4bb`.

Observed execution:
- Dossier reconcile: success;
- PASS 1 regression before ingest: success;
- PASS 1 ingest: success;
- PASS 2 recompute: success;
- PASS 1 revalidation: success;
- canonical commit step: failure.

Ingest workspace summary:
- `processed_artifact_count=5`;
- `accepted_count=5`;
- PASS 1 projected to `105 attempted / 455 remaining`;
- PASS 2 recomputed successfully with target `560`, first-pass attempted `1`, waiting Dossier `532`, ready/pending `27`.

Exact commit-stage failure:
`fatal: pathspec 'data/ai_inbox/taste_steam_review_dossiers' did not match any files`.

Because commit never occurred, the successful workspace ingest did not advance canonical `main`.

## Commit/staging fix

Implementation:
- `66d33ee5a2b99b9044f6205e85b81752ab1c32ab` — added `scripts/stage_progressive_pass1_canonical_writer.sh`;
- `d4f6819b6b11532a326f93db162f769bb1794531` — added focused staging regression;
- `d3405f7390777297280bd7d9094e47e51584d799` — production PASS 1 workflow now delegates staging to the helper;
- `5ab6f94a1318d7689429932cc9a3d8af4988dea1` — current Progressive validation surface watches/compiles/runs the staging regression;
- `264a851dd146155fcec664034d23b73101f43d16` — hardened tracked-path detection without a `pipefail`/SIGPIPE edge;
- `5a113f32eafdcdc233d2dd0dce5a531bf625730e` — existing Deep integration regression now validates PASS 2 projection staging through the production helper.

Staging semantics:
- required PASS 1/PASS 2/Dossier projection paths remain strict;
- optional Dossier inbox, quarantine and failure-audit paths are staged only when present or already tracked;
- tracked deletions are still staged;
- optional newly-created paths are staged;
- absence of optional paths no longer fails the commit step;
- shared `taste-steam-review-dossier-canonical-writer` ownership and Dossier reconcile behavior are unchanged.

Focused regression `scripts/test_progressive_pass1_workflow_staging.py` proves:
1. canonical commit succeeds when all three optional Dossier paths are absent;
2. tracked optional deletions are staged;
3. new optional paths are staged;
4. the live `.github/workflows/ingest-progressive-pass1.yml` actually invokes the tested helper.

## Validation

Final code validation:
- run `35868415779`;
- job `107205837580`;
- conclusion: `success`.

Successful relevant steps:
- PASS 2 core regression;
- PASS 2 Dossier integration regression;
- PASS 1 regression;
- PASS 1 ingest activation regression;
- PASS 1 canonical-writer staging regression;
- Progressive personalization regression;
- current staged projection accounting;
- unresolved-row preservation;
- visual activation routing;
- active production eligibility recomputation without attempt consumption.

The first two validation attempts after the workflow refactor failed only because the pre-existing Deep integration test still expected `progressive_pass2_work.json` to be staged inline in YAML. Commit `5a113f32...` moved that assertion to the production staging helper, after which the full validation surface passed.

Normal push-triggered pre-AI run `35868415798` also completed successfully and committed `6ad53f825117e29b0730c43d3bb78119427ffcf7`; normal visual rebuild followed. Comparison from validated code commit `5a113f32...` to that generated-state update changed generated data/visual artifacts only, not the staging implementation or regression files.

## Fresh-main recovery state

Fresh canonical state after the fix and normal rebuilds:
- PASS 1 flags: `true/true`;
- PASS 1: `560 total / 100 attempted / 460 remaining`;
- Friends vs Friends remains first unprocessed item;
- Friends appid: `1785150`;
- Friends work_id: `4a85ac1f78ca5a8812a59631c715058f36032959b997b8be2504018c1100eed0`;
- exact Friends artifact remains present and unchanged;
- PASS 1 inbox currently contains 5 already-existing result artifacts;
- PASS 2 remains active at target `560`, first-pass attempted `1`, waiting Dossier `532`, ready/pending `27`.

The failed operator dispatch already demonstrated that those same 5 pending artifacts validate and project to `105 attempted / 455 remaining` before commit.

Therefore, if no intervening canonical PASS 1 change occurs, another canonical ingest activation would be expected to persist a +5/-5 delta, including the exact Friends result. It would not be a Friends-only ingest because the production ingest correctly consumes all current inbox artifacts.

## Acceptance matrix

- FIX-01 coactive production ingest guard: PASS.
- FIX-02 focused activation regression: PASS.
- FIX-03 activation validation coverage: PASS.
- FIX-04 exact Friends artifact semantic re-execution avoided: PASS; canonical persistence still pending.
- FIX-05 canonical PASS 1 state/work advance: BLOCKED because the consumed dispatch failed before commit.
- FIX-06 PASS 2 recompute logic: PASS in the failed dispatch workspace and in fresh validation; canonical post-ingest persistence remains pending with FIX-05.
- FIX-07 no unrelated semantic-history rewrite by this continuation: PASS.
- FIX-08 documentation reconciliation: PASS.
- FIX-09 no Scheduled Task mutation / Scheduled `Run now`; no new workflow dispatch in this continuation: PASS.
- commit/staging optional-path defect: PASS.
- staging regression tied to live production workflow: PASS.
- FIX-10 durable report committed and reread from `main`: PASS. Report commit `3061e56595f5e46c7e5fcbdf20b5752162fcc93a` was reread from `main` as blob `2d342d4543c97ab4165cacf31f2f3d202e008738`; this closeout update is reread again before the final response.

## Exact remaining unblock

To finish canonical recovery now, one additional operator run of the existing `.github/workflows/ingest-progressive-pass1.yml` is required unless another legitimate future PASS 1 inbox push naturally activates the same workflow first.

The current task amendment explicitly says the second operator `workflow_dispatch` is not authorized. Director/user approval is therefore required before that dispatch.

No rerun of the old failed attempt, artifact rewrite, manual PASS 1 state edit, new scheduler, or Scheduled Task `Run now` should be substituted.
