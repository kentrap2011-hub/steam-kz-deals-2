# Worker report — site-giveaway-and-freshness-recovery-02

- lifecycle: `in_progress`
- UTC: `2026-09-10T17:10:00Z`
- task: restore canonical giveaway refresh, repair publication freshness binding, rebuild/deploy, and verify the exact published Pages artifact.

## Inherited confirmed state

- prior recovery report: `reviews/worker_reports/site-current-games-and-free-game-recovery-01.md`
- original visual build blocker is already repaired.
- last successful visual build before this task: run `34498384650`.
- last successful Pages deploy before this task: run `34498439445`.
- that deployment contained 115 non-giveaway entries.
- canonical giveaway snapshot `data/production/giveaways/v1/current.json` is stale across the `2026-09-10T15:00:00Z` Epic rotation; it still records expired `Alone With You`.
- current expected Epic rotation from the inherited task state: `Astral Ascent` and `Luftrausers`; exact KZ canonical eligibility still needs producer-side proof in this task.
- prior deployment freshness outcome: `degraded/no_fresh_build`, reason `visual_source_history_mismatch`.

## First investigation action

Trace the canonical giveaway producer/scheduler and the freshness-receipt source-history binding on current `main`, then inspect the exact runs/logs that should have refreshed giveaway state after the 15:00Z rotation.

No Taste semantic queue/cache/overlay/Scheduled Task changes are authorized or planned in this task.
