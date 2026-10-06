# WORKER TASK — Deep two-stage architecture freeze 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `DEEP_TWO_STAGE_ARCHITECTURE_FREEZE_01`
Mode: `ARCHITECT / CONTRACT-FREEZE / NO PRODUCTION CUTOVER`

## Purpose

Turn the approved two-stage Deep product design into frozen interfaces so multiple later worker chats can implement independently without redefining semantics.

This task replaces the monolithic implementation responsibility previously placed in `WORKER_TASK_DEEP_TWO_STAGE_COMPARATIVE_CALIBRATION_IMPLEMENT_01.md`. Read that task as the full requirements source, but do not implement the whole system here.

## Freeze exactly

1. Pipeline:
`Dossier -> Deep Stage 1 -> Deep Stage 2 -> ranking/publication`.

2. Separate semantic workers:
- Stage 1 = independent analysis worker.
- Stage 2 = comparative calibration worker.
- Different prompts, work manifests, result schemas, ingest state and responsibilities.

3. Score model:
- calibrated Deep fit: 0–56;
- deterministic Wishlist: +4;
- personal total: 0–60;
- deterministic purchase/deal: 0–40;
- combined offer total: 0–100.
- direct user ratings remain strong calibration anchors.
- active calibrated fit candidates require strict monotonic unique displayed personal scores; integer-only scoring is forbidden.

4. Stage 1:
- structured summary;
- positives;
- negatives;
- other nuances;
- fit/not-fit/confidence;
- provisional 0–56 score;
- game-specific transparent point breakdown whose arithmetic reconciles to provisional score.
- no neighbor comparison.

5. Stage 2:
- only accepted Stage-1 evidence + GitHub-selected calibrated neighbors;
- no new web research/facts;
- relative above/below judgments;
- comparative adjustment;
- calibrated 0–56 score;
- why above/below neighbors;
- GitHub owns window selection/expansion.

6. Site contract:
- compact card shows only final Stage-2 score; pending Stage 2 shows status, no Fast fallback;
- detail order: short summary -> positives -> negatives -> other/nuances -> Stage-2 change -> why above/below;
- detail exposes both Stage-1 and Stage-2 scores + delta + Wishlist + personal /60 + purchase /40 + total /100;
- Statistics has separate Dossier / Stage 1 / Stage 2 blocks;
- Fast disappears as current semantic stage.

7. Migration:
- preserve valid existing Dossier/Deep evidence;
- classify legacy Deep into reusable-as-Stage1 vs requires reanalysis;
- no mixed legacy/new production authority;
- no mass semantic execution here.

## Deliverables

Create canonical schemas/contracts/interfaces and an explicit dependency map for the following later tasks:
- `WORKER_TASK_DEEP_STAGE1_WORKER_IMPLEMENT_01.md`
- `WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md`
- `WORKER_TASK_DEEP_FAST_REMOVAL_RANKING_MIGRATION_01.md`
- `WORKER_TASK_DEEP_SITE_MIRROR_UI_STATISTICS_IMPLEMENT_01.md`
- `WORKER_TASK_DEEP_TWO_STAGE_INTEGRATION_CUTOVER_01.md`

Freeze names/fields/ownership so these tasks can work independently.

## Hard boundaries

Do not implement full Stage-1 runtime, Stage-2 runtime, site redesign, Fast production cutover, or semantic migration in this task.
Do not change Scheduled Tasks.
Do not run semantic workers.

## Report

`reviews/worker_reports/deep-two-stage-architecture-freeze-01.md`

Final status:
- `complete_interfaces_frozen`
- `needs_director_decision`
- `blocked`
