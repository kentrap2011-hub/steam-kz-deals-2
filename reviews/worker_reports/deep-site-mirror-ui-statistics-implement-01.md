# Worker report — Deep mirrored site UI and Statistics implementation 01

- **Date:** 2026-10-08
- **Task:** `WORKER_TASK_DEEP_SITE_MIRROR_UI_STATISTICS_IMPLEMENT_01.md`
- **Source of truth:** `main` at START; branch `implement/deep-site-mirror-ui-statistics-01`
- **Pull request:** https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/168
- **Status:** `implementation_complete_ready_for_review_non_active`. PR is **not merged** and no production/cutover is claimed.

## Implemented

1. **GitHub-owned, non-active site projection** — `scripts/deep_two_stage_site_projection.py` consumes Stage-1 work/accepted state and exact result files with SHA/provenance checks, Stage-2 canonical state, and existing Dossier status. It publishes the frozen `DEEP-TWO-STAGE-SITE-PROJECTION-V1` per-game/status marker, explicit Dossier/Stage 1/Stage 2 states, detailed Stage-1 findings and dynamic point evidence, Stage-2 comparative change, calibrated score, neighbor rationale, and producer-owned counters/attempt/success timestamps. Stage-2 anchor IDs map to published game titles where available and otherwise to exact Steam AppIDs. It is **not wired into the active production builder**.
2. **Statistics UI** — separate Dossier, `Deep Stage 1 — Анализ игры`, and `Deep Stage 2 — Сравнительная калибровка` blocks with accepted/completed/pending/diagnostic, canonical denominator/progress, last attempt and last successful result. Old Fast/legacy Deep blocks are not exposed as new-stage equivalents on marked two-stage payloads. Existing translation and publication diagnostics remain.
3. **Compact and detail** — calibrated Stage-2 result alone authorizes personal /60 and offer /100; pending Stage 1, Stage-1 not-fit, pending calibration and calibration diagnostics have distinct no-score states. The provisional Stage-1 score is visible **only in detail**. Six ordered detail sections show conclusion, positives, negatives, nuances, Stage-1-to-Stage-2 evolution with evidence-backed point breakdown, and why above/below neighboring games. Wishlist +4, purchase /40, rank and each stage state are visible.
4. **Legacy mode preserved** — the new UI/projection activates only for exact `deep_two_stage_site_contract`; existing running site continues using its current Fast/Dossier/Deep model until a separate integration/cutover action. Legacy score decorator cannot override the new card. UI does not compute semantic scores, ranking, queue scope or retry.
5. **Regression and CI** — `scripts/test_deep_two_stage_site_projection.py`, `web/deep-two-stage-ui.test.js`, and `.github/workflows/validate-deep-site-mirror-ui.yml`; existing legacy progressive and score-detail tests run alongside the new tests.

## Frozen interface / ownership

- Consumed unchanged: `config/deep_two_stage_architecture_contract.json`, `config/deep_two_stage_site_projection_contract.json`, `config/deep_two_stage_dependency_map.json`.
- Owner: GitHub deterministic producer for score/status/progress/explanation projection; browser read-only. No new recurring stage, semantic worker, queue/retry owner, Scheduled Task or scheduler edits.
- Deliberately untouched: Stage-1 and Stage-2 semantic implementation, Fast backend/ranking migration, `scripts/build_final_visual_payload.py` active call path, production data and integration/cutover.
- The later integration task must explicitly connect the non-active projection to the newly authoritative score/ranking/purchase producer, remove legacy ranking authority, and validate end-to-end publication. This task does **not** assert that the current production feed already emits the new marker or calibrated scores.

## Validation evidence

PR head before last presentation-only updates: `71ecee51bcdfc2fb2bf4fb3dfa2342c1a56fe4dd`.

- **PASS** — `Validate Deep site mirror UI`, run **37778452925**: Python projection tests, new Node UI tests, legacy statistics and score UI compatibility.
- **PASS** — `Validate site publication resilience`, run **37778452379**.
- **PASS** — `Validate package purchase value`, run **37778452351**.
- `Validate Progressive PASS 2 core` **37778452789**: still running at this report snapshot; previous head `137c9c10fd4051d005ba6b67cf9443f2d993b74d` run **37777875331** succeeded.
- **Unrelated existing shared-state regression** — `Validate site task registry and page`, run **37778452411** failed on assertions hardcoded to older “recent completed” identities (`site-tasks`, `deep-stage1`), while current `main` registers more recent `historical-backlog-audit` and `deep-ranking`. No task-registry, task-page or shared Director files were changed by this PR; this separate issue is **not** claimed fixed. CI is therefore not fully green.

## Remaining limitations / acceptance

- Dossier's current `dossier_last_write_at_utc` is a truthful last-write/attempt proxy; an exact successful-result timestamp is shown only if the canonical Dossier source supplies `dossier_last_successful_result_at_utc`. No success time is invented.
- Full real-production runtime/site deployment and score/rank cutover checks are **intentionally pending the separate integration/cutover task**.
- Because other workers concurrently write `CURRENT_TASK.md`, this PR leaves their shared handoff untouched and records this task here rather than overwriting shared work.
- PR stays open for Director review. No merge, production promotion, scheduled worker run or next task was performed.

## Context / verification efficiency

Read canonical START gate and task, then bounded frozen contracts and the specific UI/stage files. Added a dedicated CI workflow for future bounded UI and projection verification; the unrelated site-tasks regression remains owned outside this task.
