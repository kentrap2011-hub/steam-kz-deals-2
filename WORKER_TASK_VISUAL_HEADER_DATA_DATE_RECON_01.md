# WORKER TASK — Visual Header Data Date Recon 01

## Task ID
`visual-header-data-date-recon-01`

## Mode
`READ-ONLY / RECON`

## Priority
`HIGH_USER_VISIBLE`

## Expected report
`reviews/worker_reports/visual-header-data-date-recon-01.md`

## Context
The giveaway publication incident has been repaired and the user has verified on Android that the free giveaway is visible again.

However, the site header still shows:
`Данные: 31 авг., 00:37`

This is confusing because the giveaway section is demonstrably fresh after the recovery.

Do not ask Director to investigate this. The worker must establish the exact meaning/source of that displayed date from repository truth.

## Goal
Determine exactly why the site header still shows `31 авг., 00:37`, what that timestamp actually represents, whether it is correct under the current partial/section-level refresh architecture, and whether the UI should be changed.

## Required investigation
1. Read current `main`.
2. Read:
   - `CHAT_PROTOCOL.md`
   - `CHAT_CONTEXT.md`
   - `DIRECTOR_PROTOCOL.md`
   - `reviews/worker_reports/giveaway-visual-publication-recovery-implement-01.md`
3. Identify the exact frontend field/code path that renders `Данные: ...`.
4. Trace that displayed timestamp to its exact source field/artifact.
5. Determine whether it currently represents:
   - full visual generation time;
   - paid/Taste base snapshot time;
   - giveaway section freshness;
   - deploy time;
   - another exact source.
6. Explain why the giveaway can be fresh while this header date remains old.
7. Decide whether the current display is semantically correct or misleading after section-level giveaway refreshes.
8. If misleading, define the smallest correct UX/data-model fix. Consider whether the page should show separate freshness for full data vs giveaways rather than pretending one timestamp represents everything.

## Forbidden
- READ-ONLY only.
- Do not change UI/code/data.
- Do not modify timestamps manually.
- Do not alter giveaway/Taste/ranking logic.
- Do not weaken freshness/fail-closed behavior.
- Do not start another task.

## Required report
Save exactly:
`reviews/worker_reports/visual-header-data-date-recon-01.md`

Report must contain:
- exact field/code path producing the displayed date;
- exact current meaning of `31 авг., 00:37`;
- why giveaways can still be fresh;
- whether the display is correct or misleading;
- one bounded next action;
- final status exactly one of:
  - `complete`
  - `blocked`

Do not implement the recommendation in this recon.
