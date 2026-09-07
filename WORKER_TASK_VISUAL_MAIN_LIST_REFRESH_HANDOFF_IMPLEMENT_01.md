# WORKER TASK — Visual Main List Refresh Handoff Implement 01

## Task ID
`visual-main-list-refresh-handoff-implement-01`

## Mode
`IMPLEMENT / ACCEPTANCE`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`

## Direct predecessor
Read first:
`reviews/worker_reports/visual-main-list-freshness-recon-01.md`

Accepted predecessor conclusion:
- the published paid-discount main list is stale and must not be treated as current;
- last proven commercial freshness represented by published paid `items` is the source snapshot shown to the user as `31 авг. 2026, 00:37`;
- later visual/giveaway writes did not refresh paid commercial items;
- expired top rows are old commercial rows whose stored sale end passed after the stale snapshot;
- Steam collection is still running;
- exact blocker is a commercial refresh handoff/orchestration gap between fresh daily shortlist and the existing canonical commercial mailing/visual publication path;
- do not hide the problem by deleting expired rows or changing the header cosmetically;
- freshness must be truthful by domain, with paid-list freshness independent from giveaway freshness.

## Goal
Repair/reconnect the existing canonical commercial refresh handoff so that each successful fresh daily Steam shortlist can reach the existing single commercial mailing/visual build-and-publish path and produce genuinely fresh paid `items` on the site.

Also expose/persist a truthful paid-list freshness timestamp/status that advances only after a successful canonical paid-list publication, without confusing it with giveaway freshness.

## Required implementation
1. Start from current `main`.
2. Read:
   - `CHAT_PROTOCOL.md`
   - `CHAT_CONTEXT.md`
   - `DIRECTOR_PROTOCOL.md`
   - predecessor report above;
   - current daily Steam shortlist workflow;
   - canonical mailing/commercial handoff;
   - canonical visual build/deploy workflow;
   - existing freshness receipts/contracts.
3. Identify and minimally repair the missing active handoff/orchestration link between successful daily shortlist refresh and the existing canonical commercial mailing/visual build.
4. Reuse existing canonical writer/build/deploy paths. Do not create a parallel commercial pipeline.
5. Preserve fail-closed and all existing commercial freshness/validation gates.
6. After the repair, execute/observe the normal route and prove that fresh commercial source reaches published paid `items`.
7. Ensure rows whose sales have ended are no longer retained merely because the old commercial snapshot never advanced.
8. Persist/expose truthful paid-list freshness identity/timestamp based on the successful canonical paid-list refresh/publication event.
9. Keep giveaway freshness independent. A giveaway-only refresh must not advance paid-list freshness.
10. If the current frontend already has a suitable status location, implement the minimum truthful display for paid-list freshness/staleness. If a UI change would require a broader redesign, keep this task to the smallest safe display necessary for acceptance and report any follow-up separately.

## Hard boundaries
Do NOT:
- create a second scheduler for the same commercial refresh purpose;
- create a second commercial writer;
- create a parallel mailing source;
- manually patch prices, rows, caches, handoffs or production visual JSON;
- manually delete expired games;
- weaken freshness or fail-closed gates;
- fake a new timestamp from artifact generation time alone;
- let giveaway-only publication advance paid-list freshness;
- change Taste recommendation semantics/ranking;
- run or modify the Taste Scheduled Task;
- use paid OpenAI API or Copilot;
- work on unrelated backlog.

## Acceptance
Status `complete_ready_for_user_verification` only if:
1. the existing daily Steam/commercial chain reaches the canonical paid-list source again;
2. the existing canonical visual writer publishes fresh paid `items`;
3. normal deploy/publication succeeds;
4. the paid-list source freshness is newer than the stale 31 Aug snapshot and is tied to the actually published paid items;
5. expired rows from the old snapshot are not present merely due to stale carryover;
6. no second scheduler/writer/pipeline was created;
7. giveaway remains independently functional;
8. paid-list freshness shown/persisted to the user cannot be advanced by giveaway-only refresh;
9. no Taste semantics were changed.

## Final status — exactly one
- `complete_ready_for_user_verification`
- `blocked`
- `needs_followup_fix`

## Required report
Save exactly:
`reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`

Include:
- final status;
- exact root implementation change;
- commit(s);
- exact workflows/runs used for acceptance;
- proof fresh shortlist/commercial source reached canonical paid `items`;
- old vs new paid-list freshness identity/timestamp;
- proof the timestamp/status is tied to the published paid list, not artifact time or giveaway time;
- proof no duplicate scheduler/writer/pipeline was added;
- deploy evidence;
- whether Android verification can now begin;
- any remaining blocker.

Do not start another task.
