# WORKER TASK — Deep mirrored site UI and Statistics implementation 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Dependency: accepted `WORKER_TASK_DEEP_TWO_STAGE_ARCHITECTURE_FREEZE_01.md`.
Mode: `IMPLEMENT / VALIDATE`

Frozen interfaces (do not redefine):
- `config/deep_two_stage_architecture_contract.json`
- `config/deep_two_stage_site_projection_contract.json`
- `config/deep_two_stage_dependency_map.json`

Implement only the frozen website presentation/state model.

## Statistics

Separate visible blocks:
- Dossier;
- Deep Stage 1 — analysis;
- Deep Stage 2 — comparative calibration.

Each Stage block shows meaningful completed/pending/diagnostic counts, progress, last attempt and last success.

Fast must not appear as an equivalent current semantic stage after cutover.

## Compact card

After Stage 2:
- show authoritative final post-calibration personal score /60 and existing combined offer score /100 as appropriate.

Before Stage 2:
- show clear awaiting-calibration/not-yet-analyzed state;
- never display Stage-1 provisional score as final;
- never fall back to Fast.

## Detail view

Strict top-to-bottom structure:
1. short conclusion;
2. positives;
3. negatives;
4. other / nuances;
5. score evolution Stage 1 -> Stage 2;
6. why above / below neighboring games.

Expose:
- Stage-1 provisional Deep fit;
- Stage-1 detailed game-specific point breakdown;
- Stage-2 comparative adjustment;
- Stage-2 calibrated Deep fit;
- Wishlist +4 when present;
- personal total /60;
- purchase/deal /40;
- total /100;
- current pipeline states.

The site should mirror repository state closely enough that the user can understand what stage a game is in and why its score/rank exists without opening GitHub.

Do not implement semantic-worker logic, Fast backend migration, ranking policy, or Scheduled Task changes.

Report: `reviews/worker_reports/deep-site-mirror-ui-statistics-implement-01.md`.
