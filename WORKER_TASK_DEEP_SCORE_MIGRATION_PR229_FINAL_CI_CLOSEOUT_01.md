# ЧАТ 1 — завершить PR #229 без ложнозелёной Stage-1 проверки

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: deep-score-migration-pr229-final-ci-closeout-01
Worker slot: СУЩЕСТВУЮЩИЙ физический ЧАТ 1 — ПРЯМОЕ продолжение его PR #229
Mode: narrow IMPLEMENT / verification on SAME existing PR #229, no second PR, no self-merge
Worker report: reviews/worker_reports/deep-score-migration-pr229-final-ci-closeout-01.md

## START and confirmed Director evidence
Completely read latest main CHAT_PROTOCOL.md and execute START, then CHAT_CONTEXT.md, this task, previous task WORKER_TASK_DEEP_SCORE_MIGRATION_ZERO_PENDING_RELEASE_NORMAL_01.md and existing PR #229 report, focused current Deep score-migration contract, exact `.github/workflows/validate-deep-stage1-migration-preparation.yml` and `scripts/prepare_deep_stage1_migration_work.py`. Read relevant PROJECT_ROUTES.md / PROJECT_DECISIONS.md as required. Work exclusively in kentrap2011-hub/steam-kz-deals-2. Confirm current PR #229 exact branch/head before edits. Normal Deep producer work remains GitHub control plane; no interactive semantics.

As of Director check 2026-10-15 PR #229 (final head `c4296e4c683bd9f8ddd2ed8fc1b8677e530c9c91`) has **2 success, 1 failure** GitHub Actions:
- `Validate Progressive PASS 2 core`, run `38776153564` — SUCCESS; PR-only read-only producer recomputation showed 158 normally eligible Deep tasks, preserving score migration 43/42 accepted incl. already compliant/1 stale/0 pending and immutable prior analyses.
- `Validate backlog dispositions`, run `38776152947` — SUCCESS.
- `Validate Deep Stage 1 migration preparation`, run `38776152910` — FAILURE in `Produce read-only current canonical Stage-1 migration plan` AFTER six isolated Stage1 unit tests PASS. Exact failure: `PreparationError: current canonical one-stage Deep work not available`. The legacy Stage1 preview reads the **committed current production PASS2 work file**, still `items=[]` and `projection_status=score_explainability_migration_active`. PR #229 never re-generated or overwrote that canonical production artifact. Do NOT fabricate that a new production producer run occurred. New PR #228 was independently merged to main; its changed files do not overlap Deep task.

## Concrete requirement
Finish PR #229 **without bypassing safety**, not another generic audit or a new major Deep Stage1 implementation:
1. Verify the red Stage1 workflow cause from real run logs and exact source. Prove it is solely an unrefreshed *committed pre-fix current-work projection*, not an actual conflict/regression in score-migration Deep producer or authorized Stage1 migration preview.
2. Find the smallest targeted **PR-only** validation strategy that proves all simultaneously: (a) normal Deep producer currently computes nonempty correct-mode exact work from current canonical input in **read-only/disposable** testing, (b) Stage1 migration preview remains inactive/non-executable and refuses incompatible/stale canonical work in production, (c) normal Stage1 unit tests still run, (d) tests don't require a direct manual rewrite of production PASS2 work. If a fail-closed Stage1 preview is intentionally expected on the old committed snapshot, classify it honestly in CI and still perform meaningful verification of Stage1 inactivity; do NOT declare a skipped assertion "passing Stage1 preview" or disable the entire workflow. Prefer tests/CI narrowly adapted to distinction between old committed snapshot and temporary freshly computed preview, rather than modifying Stage1 source runtime or weakening guards.
3. Bring SAME PR #229 safely up to current main if needed, retaining merged Research/Assembly and the user-active one-stage Dossier/Deep state untouched. No force push, accidental migration replays or new control plane. Exact *final* PR head must run full relevant GitHub checks. Acceptance requires all expected checks success OR an explicit technically justified scoped condition where the Director can separately assess a remaining red check (never conceal it).
4. Preserve `score_explainability_migration.complete=false`, `exhausted=true`, frozen stale AppID `1556790` with differing old/current authorization IDs, existing 42 accepted, 0 pending, all historical results, migration priority whenever pending>0, Deep-first exact queue ordering and V2 marker/confirmed receipt safeguards. No new attempts, recovery or scoring shortcuts.
5. Run actual PR-only 43/42/1/0, pending migration vs ordinary work, Deep history and Stage1 nonactivation focused regressions; identify exact GitHub Actions run IDs and final head. Update existing PR #229 (not new PR) and create short worker report at exact path. Stop; do not self-merge.

## Boundaries
Do not run actual Deep semantic work, update `data/production/**` or `data/cache/**` directly, modify Deep Stage1/2 implementation/activation/cutover, Dossier, Fast, ranking, web UI, scheduler/Scheduled Tasks, marker/recovery/attempt policies. No unrelated broad audits. No changes to `CURRENT_TASK.md`, Director Board/registry, accepted Dossier #228 files or frozen Research sandbox. Existing normal one-stage Deep must remain source of truth.
