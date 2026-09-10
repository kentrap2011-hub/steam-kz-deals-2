# Worker report — site-current-games-and-free-game-recovery-01

- lifecycle: `in_progress`
- UTC: `2026-09-10T15:26:00Z`
- task: restore the current published site from canonical state and verify the current free-game route end to end.
- current live/site publication state: `not_yet_resolved`; user reports the current free game is missing, and the known downstream visual/deploy chain is stale/broken after successful Taste ingest.
- known failed build run: `34484781975` (`Build daily visual payload`, failure)
- known downstream deploy run: `34484824317` (`Deploy visual mailing`, skipped)
- accepted Taste state remains authoritative: acceptance commit `ddb1a51b8321997bbbb83505d69cfe4031758619`, receipt `data/cache/taste_ingest_receipts/ba86bfdcf8365dfa0195.json`.
- first investigation action: inspect workflow run `34484781975` and identify the first real failing job/step/invariant before making any repair.

No Taste semantic results, queue/cache/overlay, Scheduled Task, or next Taste batch have been changed or started.
