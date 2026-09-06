# WORKER TASK — Giveaway Empty Feed Recurrence Recon 01

## Task ID
`giveaway-empty-feed-recurrence-recon-01`

## Mode
`READ-ONLY / RECON`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`

## Fresh user-visible incident
On 2026-09-06 the user provided a real Android screenshot of the published site showing:
- page header: `Игры со скидками`
- displayed data timestamp: `Данные: 31 авг., 00:37`
- active section: `🎁 Раздачи (!)`
- section title: `🎁 Бесплатные раздачи`
- warning: `Раздачи временно не удалось проверить полностью.`
- no giveaway cards visible.

Treat this as a real production recurrence. Do not dismiss it as a local browser issue without evidence.

## Context
A previous giveaway cache/identity/production-shape incident was stabilized and user-verified earlier. Relevant durable predecessor:
`reviews/worker_reports/giveaway-cache-identity-production-shape-fix-01.md`

The recurrence may or may not share the same cause. Determine current truth from `main`, current published artifact/state, and current canonical giveaway pipeline evidence.

## Goal
Identify exactly why the currently published giveaway section is fail-closed/empty and stale-looking, and determine the smallest safe next action.

## Required investigation
At minimum determine:
1. What current published artifact/data version the screenshot corresponds to, and whether `31 авг., 00:37` is genuinely the current site payload timestamp.
2. Current canonical giveaway source/cache/completeness state on `main`.
3. Whether the warning is triggered by:
   - stale/missing giveaway cache;
   - provider/source failure;
   - completeness/identity validation failure;
   - deploy/publication lag;
   - schema/production-shape regression;
   - another exact cause.
4. Whether valid current giveaway rows exist upstream but are blocked from publication, or whether upstream collection itself is empty/incomplete.
5. Whether the previous cache-identity fix regressed, was bypassed, or is unrelated.
6. Exact current GitHub Actions/deploy evidence only as needed to establish the cause.
7. Whether the incident can be fixed by one bounded existing-path IMPLEMENT, without introducing a second giveaway writer/scheduler.

## Hard rules
- READ-ONLY / RECON only.
- No production mutation.
- No manual cache patching.
- No second giveaway scheduler/writer.
- Do not weaken fail-closed completeness just to make cards appear.
- Preserve Steam/GOG/Epic regional semantics and existing identity contracts.
- Do not conflate this with the separate Epic RU source-probe research unless evidence shows direct causality.

## Required report
Save exactly:
`reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`

Report must include:
- `Status: complete | blocked | needs_followup`
- exact root cause or narrowest proven cause boundary;
- current published-data freshness truth;
- whether valid giveaway rows exist upstream;
- whether prior incident fix is still present/effective;
- one recommended next bounded action only;
- explicit statement whether the user should or should not re-check the site yet.

Do not implement the fix in this task.
