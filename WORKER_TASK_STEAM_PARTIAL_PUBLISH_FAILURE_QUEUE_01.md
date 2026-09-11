# TASK — steam-partial-publish-failure-queue-01

Status: `prepared_awaiting_user_authorization`
Mode when authorized: `IMPLEMENT`

## User-required behavior

The Steam catalog update must NOT wait for every problematic game/page before publishing the successfully processed majority.

Required flow:
1. Process the full current Steam catalog once.
2. Every game that processes successfully enters the normal current result set and may be published in the same cycle.
3. A game that cannot be processed must NOT block the rest of the catalog and must NOT block publication of successfully processed games.
4. Every failed/problematic game is written to a separate durable problem list.
5. After the run, the system must produce a clear summary such as: `10 games could not be processed`.
6. The durable problem list must contain enough information to investigate each game independently, including at minimum canonical identity/AppID or package identity, name when known, failed stage, first real error/root symptom, attempt/run reference, and whether prior known site data exists.
7. The Director must be able to surface this failure count/list to the user after the run so each problematic game can be investigated separately.
8. Do NOT hold the successful catalog publication while waiting for manual investigation of the problem list.
9. Do NOT silently discard failures; every unresolved game stays explicitly visible in the durable problem list until later resolved or deliberately dispositioned.
10. If a problematic game already has previously accepted/published data, keep that last known good data on the site while the game remains in the problem list. A temporary refresh failure must not make an already known game disappear solely because its latest refresh failed.

## Important distinction

Normal live-catalog count drift is not itself a failed game. The collected successful unique set is publishable. Only concrete per-game/per-request processing failures belong in the separate problem list.

If an entire catalog page/segment cannot be fetched, record it as a catalog-segment problem rather than inventing game identities that were never observed.

## Not part of this task

- Do not decouple giveaways here; that is separately queued in `WORKER_TASK_GIVEAWAY_DECOUPLE_FROM_STEAM_CRAWL_01.md`.
- Do not change Taste semantics.
- Do not investigate each failed game during the bulk catalog run.
- Do not create or enable the ChatGPT error-monitoring scheduled task here; that is a separate queued-later task.

## Acceptance intent

A test/proof run should demonstrate that intentionally failing one or more game-level operations produces:
- successful publication of all other valid games;
- retention of last known good published data for already-known failed games;
- a durable exact failed-game list;
- a durable exact failed catalog-segment list when applicable;
- a concise end-of-run failure count;
- no global failure merely because some individual games failed.
