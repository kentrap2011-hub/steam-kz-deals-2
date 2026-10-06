# WORKER TASK — Deep Stage 1 worker implementation 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Dependency: `WORKER_TASK_DEEP_TWO_STAGE_ARCHITECTURE_FREEZE_01.md` must be accepted first.
Mode: `IMPLEMENT / VALIDATE`

Implement only the Stage-1 semantic-worker path from the frozen contracts.

Stage 1 owns independent per-game analysis:
- short conclusion;
- detailed positives;
- detailed negatives;
- other nuances/uncertainty;
- fit/not-fit/confidence;
- provisional Deep fit 0–56;
- dynamic, game-specific point breakdown reconciling exactly to the provisional score.

It must not compare ranking neighbors or write Stage-2 artifacts.

Provide separate manual semantic-worker prompt, exact GitHub work manifest, result schema, ingest/validation, nonblocking diagnostics and progress state.

Preserve Dossier as factual evidence input. Wishlist remains outside Stage 1. Do not implement site UI, Fast removal, ranking cutover, Stage 2, or Scheduled Task changes.

Report: `reviews/worker_reports/deep-stage1-worker-implement-01.md`.
