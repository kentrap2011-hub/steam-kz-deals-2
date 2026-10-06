# WORKER TASK — Deep Stage 2 comparative calibration worker implementation 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Dependency: `WORKER_TASK_DEEP_TWO_STAGE_ARCHITECTURE_FREEZE_01.md` must be accepted first.
Mode: `IMPLEMENT / VALIDATE`

Implement only the Stage-2 semantic-worker/control-plane path from the frozen contracts.

Stage 2 consumes:
- immutable accepted Stage-1 result;
- pinned user profile;
- GitHub-selected already-calibrated neighbor window.

It outputs:
- above/below/near-tie judgments;
- reasons versus relevant lower/upper anchors;
- explicit comparative adjustment;
- calibrated Deep fit 0–56;
- diagnostic if Stage-1 evidence is contradictory.

No web research, new facts, or rewriting Stage-1 positives/negatives.

GitHub owns anchor selection, bounded window expansion, exact ordering, retry, persistence and unique monotonic numeric placement. Implement enough decimal precision so distinct active calibrated fit positions do not display tied scores.

Provide a separate manual semantic-worker prompt, work manifest, result schema, ingest/validation and progress state.

Do not implement Stage 1, site UI, Fast removal, production cutover or Scheduled Task changes.

Report: `reviews/worker_reports/deep-stage2-calibration-worker-implement-01.md`.
