# PR #229 Deep score-migration Stage-1 CI closeout

- Task: `WORKER_TASK_DEEP_SCORE_MIGRATION_PR229_FINAL_CI_CLOSEOUT_01.md`
- Worker: existing physical ЧАТ 1, 2026-10-15.
- Repository: `kentrap2011-hub/steam-kz-deals-2`, existing PR **#229**, branch `fix/deep-score-migration-exhausted-release-normal-01`, target `main`.
- Code/verification merge head before this report-only commit: `c673d476f2a50704f3a70e3c4cb571d2b0d7523c` (first parent PR head; second parent latest checked main `ce730b0fb1137deed16dcfbcc8a55aa9afec3a25`). Full final head is GitHub PR #229 head after this report commit, which must be revalidated separately. PR stays open; **no merge to main**.

## Exact original CI failure

- `Validate Deep Stage 1 migration preparation` run `38776152910` executed six existing isolated unit tests successfully, then `scripts/prepare_deep_stage1_migration_work.py` failed with `PreparationError: current canonical one-stage Deep work not available` at its strict `make_plan()` projection-status guard.
- That check consumed the **committed** `data/production/pre_ai/progressive_pass2_work.json`, generated before PR #229 producer fix. The committed document was still `projection_status=score_explainability_migration_active`, `items=[]`, despite `normal_pass2_eligible_count=158` and score migration `43 total / 42 accepted / 1 stale / 0 pending`.
- PR #229 was intentionally forbidden to rewrite any production artifact. The failure was an unrefreshed input to the Stage-1 read-only preview, not evidence of a newly active Stage 1 nor incorrect relaxed Stage-1 authorization. The same unmodified Stage-1 source rejects an intentionally stale/incorrect generation.

## Narrow fix

1. Updated **only PR validation** in `.github/workflows/validate-deep-stage1-migration-preparation.yml`: full checkout history is needed for the unchanged frozen migration authority evidence gate. Keep six independent Stage-1 unit tests, retain explicit canonical Stage-1 nonactive contract/state check and preview artifact upload.
2. New `scripts/test_deep_stage1_migration_pr_preview.py` computes the actual current one-stage PASS2 work document **in memory** via `build_progressive_pass2_work.build_work_document(now=...) ` (never `producer.main()`). Asserts nonempty exact `normal_first_pass` items, sequence/authorization uniqueness, scope/count parity, frozen score migration 43/42 accepted/1 stale/0 pending and `complete=false, exhausted=true`.
3. Invokes the unchanged `prepare_deep_stage1_migration_work.make_plan` with the same **actual** current generation, pinned profile, Dossier binding, ownership, accepted state, and canonical Dossier loader that the Stage-1 CLI uses. Confirms current preview `semantic_execution_authorized=false`, `executable_materialization_authorized=false`, `production_cutover_performed=false`, not active, coherent counts and valid inactive work shape.
4. Explicitly proves the previously committed stale projection is **rejected** for the exact expected reason; separately injects only invalid projection status and incorrect semantic generation and proves each is still rejected by the unchanged Stage-1 gate. Does not mock or bypass strict migration checks.
5. Watches SHA-256 of all four canonical Deep/Stage-1 work/state artifacts before/after and fails if any change. Writes **only** a disposable `RUNNER_TEMP` audit preview JSON.
6. Merged current main into the **same PR branch**, without force push or path overlap. This retained latest merged Dossier Research/Assembly and actual Dossier transport records unchanged; the PR diff remains restricted to Deep score release, focused regression, this PR Stage-1 validation and worker reports.

## Verified PR Actions on the merged code head

- **SUCCESS** `Validate Deep Stage 1 migration preparation` run `38790418278`. Log: `Ran 6 tests`, `DEEP_STAGE1_PR_PREVIEW=PASS committed=confirmed_rejected_stale_committed_snapshot normal_work=158 score_migration=43/42/1/0 stage1_candidates=248 stage1_activation=false canonical_files_unchanged=true`, and `Production canonical Stage-1 work unchanged`.
- **SUCCESS** `Validate backlog dispositions` run `38790418291`.
- **SUCCESS** `Validate Progressive PASS 2 core` run `38790418489` after one rerun of only the failed CI job. The initial attempt had progressed past PASS2/Deep core into unrelated `scripts/test_visual_freshness_receipt.py`, where `tempfile.TemporaryDirectory` cleanup raised `OSError: [Errno 39] Directory not empty: .../.git/objects` (git filesystem cleanup race). Retrying the same head/job succeeded **without modifying** visual/ranking or any test safety gate. Both initial code head `01f137ec6c59b4c14624fe618217ddaf83fc2205` and merged code head passed the focused Stage-1 PR preview; PASS2 core succeeded on the initial code head run `38790192185` and on merged head retry.
- After adding this report the exact **final PR head** must receive its own GitHub Actions checks; previous run IDs are valid evidence only for the code head specified above.

## Preservation and remaining production boundary

Score migration `complete=false`, `exhausted=true`, frozen stale `game:1556790 / App_1556790` with old prior authorization `5c33e8bbb941530691cd9b2e324e8935871d9c1a125fe217c9f0fa21477bf16c` versus current `c9cfe21b3080ed74806d89bb1ad410f116b8af2de7c021571d65cda2e2f44bbb`. **42 accepted, one unresolved and zero migration pending**; no acceptance/retry fabricated. Normal Deep stays in canonical GitHub order and retains strict new score findings, prior history, V2 marker and confirmed receipt. No production/cache edits, semantic runs, new control plane, Stage 1/2 source edits, Dossier/Fast/ranking/UI or Scheduled Task changes. Production producer **has not been run or persisted**, so live normal queue is not yet claimed restored. PR #229 remains unmerged for owner review.
