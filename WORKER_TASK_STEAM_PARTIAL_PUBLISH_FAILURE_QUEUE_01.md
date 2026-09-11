# TASK — steam-partial-publish-failure-queue-01

Status: `authorized_dispatched_chat_1`
Mode: `IMPLEMENT`

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
11. Normal live-catalog total drift is informational only. Do not fail the whole run because the initial/reported count differs from the unique set actually collected.
12. Do not repeatedly refetch effectively static fields for already-known games when the existing canonical data is valid and sufficient. Refresh changing commercial data needed for the current shortlist; preserve stable known fields unless missing or explicitly required.

## Catalog-segment failures

If an entire catalog page/segment cannot be fetched:
- continue the rest of the catalog;
- record the exact failed segment/request separately;
- do not invent game identities that were never observed;
- do not block publication of successful results solely because a segment failed.

## Tests required before any real Steam production refresh

Add only short deterministic automated tests for the new behavior. No full fake Steam crawl.

At minimum prove:
- one game-level failure does not block other successful games;
- an already-known failed game keeps its last known good published data;
- a failed catalog segment is recorded separately and does not stop the rest;
- live catalog count drift does not fail the run;
- unresolved failures are durably recorded and summarized.

## Scope limits

- Do NOT run the real full Steam production refresh in this task. Stop after implementation + short tests + durable report.
- Do not decouple giveaways here; that remains separately queued in `WORKER_TASK_GIVEAWAY_DECOUPLE_FROM_STEAM_CRAWL_01.md`.
- Do not create or enable the ChatGPT error-monitoring scheduled task; that remains queued in `WORKER_TASK_STEAM_ERROR_NOTIFICATION_WATCH_01.md`.
- Do not change Taste semantics, queue, overlay, or Scheduled Task.
- Do not investigate individual failed games here.

## Deliverable

Write/update durable report:
`reviews/worker_reports/steam-partial-publish-failure-queue-01.md`

Report must include:
- exact files changed;
- exact behavior implemented;
- exact test commands/results;
- any migration/backward-compatibility effect;
- whether a real Steam refresh is now safe to run under the new rules;
- commit SHA(s);
- unresolved blockers, if any;
- mandatory bounded self-diagnosis if final status is failure/blocked/follow-up.

Final status should be one of:
- `complete_ready_for_real_steam_refresh`
- `blocked_requires_followup`
