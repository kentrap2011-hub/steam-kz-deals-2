# WORKER TASK — Visual Main List Freshness Recon 01

## Task ID
`visual-main-list-freshness-recon-01`

## Mode
`READ-ONLY / RECON`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/visual-main-list-freshness-recon-01.md`

## User-visible evidence
User verified on Android:
- giveaway section is working again;
- header still shows `Данные: 31 авг., 00:37`;
- in the main list, the first three games already show `скидка закончилась`.

The user explicitly rejects a cosmetic relabel to `Рассылка:` as insufficient. The useful requirement is to show a date that reflects how fresh the currently displayed list really is, and first establish whether the main list itself is stale.

## Context
Previous recon:
`reviews/worker_reports/visual-header-data-date-recon-01.md`

That recon proved the current label uses `source_mailing_updated_at_utc`, but this new task must go further and determine actual freshness of the displayed main list and whether the top rows are stale.

The previously created task `WORKER_TASK_VISUAL_HEADER_DATA_LABEL_IMPLEMENT_01.md` is superseded by this recon and must NOT be executed unless a later Director decision explicitly revives it.

## Goal
Establish the real freshness state of the main discounted-games list visible to the user, explain why several top rows already say their discounts ended, and determine what timestamp/status the UI should actually show so the user can tell whether the displayed list is current.

## Required investigation
1. Read current `main`.
2. Read:
   - `CHAT_PROTOCOL.md`
   - `CHAT_CONTEXT.md`
   - `DIRECTOR_PROTOCOL.md`
   - `reviews/worker_reports/visual-header-data-date-recon-01.md`
   - current visual production/deploy contracts and the main-list source pipeline.
3. Identify the exact production artifact currently feeding the main discounted-games list on Pages.
4. Determine the exact last successful refresh time of the main discounted-games data that the user sees, not just the mailing source timestamp.
5. Inspect the first three currently displayed main-list rows and determine why each says `скидка закончилась`:
   - because the sale truly ended after the last successful refresh;
   - because the row is intentionally retained after sale end;
   - because commercial/price data is stale;
   - because the main list has not refreshed due to Taste or another gate;
   - or another exact cause.
6. Determine whether the main list is currently stale enough that the user should distrust its active-sale state.
7. Determine the narrowest blocking boundary preventing current commercial/main-list refresh, if any.
8. Define what the header should show to be genuinely useful. Evaluate at least:
   - actual successful main-list refresh time;
   - separate freshness for main deals vs giveaways;
   - an explicit stale/degraded warning when the main list could not refresh;
   - whether a single global timestamp is fundamentally misleading.
9. Recommend one minimal correct next action. If the main list is stale, prioritize fixing freshness/publication truth over cosmetic label changes.

## Important semantic rule
Do not recommend `generated_at_utc` merely because it is newer. A timestamp is useful only if it proves the displayed main-list commercial data was actually refreshed/validated at that time.

If the system cannot truthfully produce one universal page freshness timestamp because sections refresh independently, say so and specify the smallest truthful alternative.

## Forbidden
- READ-ONLY / RECON only.
- Do not change UI/code/data/workflows.
- Do not manually refresh prices or edit rows.
- Do not delete expired rows manually.
- Do not weaken fail-closed or freshness rules.
- Do not change Taste/ranking semantics.
- Do not create another writer/scheduler.
- Do not execute `WORKER_TASK_VISUAL_HEADER_DATA_LABEL_IMPLEMENT_01.md`.
- Do not start another task.

## Required report
Save exactly:
`reviews/worker_reports/visual-main-list-freshness-recon-01.md`

Report must contain:
1. Final status exactly one of:
   - `complete`
   - `blocked`
2. Exact current main-list production artifact/source.
3. Exact last successful main-list refresh/acceptance time that applies to displayed rows.
4. Analysis of the first three displayed rows with `скидка закончилась` and why they are present.
5. Whether the main list is currently stale/degraded.
6. Exact blocking boundary if freshness is not current.
7. What date/status the user should see instead of the current misleading header.
8. Whether freshness should be separate for main deals and giveaways.
9. Exactly one minimal next IMPLEMENT action.
10. Explicit confirmation that the old label-only task is insufficient/sufficient based on evidence.

Do not implement the fix in this recon.
