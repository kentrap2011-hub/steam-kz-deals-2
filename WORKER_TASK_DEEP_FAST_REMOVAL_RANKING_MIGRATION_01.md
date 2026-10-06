# WORKER TASK — Fast removal and ranking migration 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Dependency: accepted `WORKER_TASK_DEEP_TWO_STAGE_ARCHITECTURE_FREEZE_01.md`.
Mode: `IMPLEMENT / VALIDATE / NO PARTIAL CUTOVER`

Frozen interfaces (do not redefine):
- `config/deep_two_stage_architecture_contract.json`
- `config/deep_two_stage_migration_contract.json`
- `config/deep_two_stage_dependency_map.json`

Trace and remove Fast semantic output from all current ranking/decision authority:
- ranking;
- fallback score;
- card reasons;
- Deep eligibility/order if applicable;
- publication;
- Statistics/current-stage semantics;
- migration/recovery consumers.

Historical Fast artifacts may remain read-only when required for migration/audit, but no production decision path may use them after cutover.

Implement the frozen score composition:
- calibrated Deep fit 0–56;
- Wishlist deterministic +4;
- personal 0–60;
- purchase/deal deterministic 0–40;
- total 0–100.

Audit old duration/risk/achievement arithmetic and prevent double counting with Stage-1 semantic analysis. Preserve direct user ratings as strong calibration anchors.

Do not enable mixed legacy/new ranking. Prepare migration/cutover state and tests only unless all frozen prerequisites already exist.

Do not implement semantic workers or site redesign. No Scheduled Task changes.

Report: `reviews/worker_reports/deep-fast-removal-ranking-migration-01.md`.
