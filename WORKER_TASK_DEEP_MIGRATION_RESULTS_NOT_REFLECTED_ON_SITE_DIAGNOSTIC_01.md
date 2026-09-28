# WORKER TASK — DEEP MIGRATION RESULTS NOT REFLECTED ON SITE DIAGNOSTIC 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or target is ambiguous, stop and switch first.

Task ID: `deep-migration-results-not-reflected-on-site-diagnostic-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/deep-migration-results-not-reflected-on-site-diagnostic-01.md`

## User-observed symptom

User screenshot of the published site shows:

Dossier:
- total 399
- ready 46
- waiting 353
- recovery 0
- last write: "ещё не было записей"

Deep:
- total 399
- authoritative completed 0
- fit 0
- not-fit 0
- incomplete/recovery 0
- waiting for dossier 361
- ready/pending 38
- remaining 399
- last write: "ещё не было записей"

But the canonical Deep migration was subsequently observed by Director to be complete in GitHub-owned PASS 2 state/work:
- migration total 30
- accepted 30
- accepted_completed 30
- 26 analyzed_fit
- 4 analyzed_not_fit
- 0 incomplete
- migration complete true
- 23 confirmed-risk results
- 7 caution results
- no fit-outcome changes
- migration last accepted at 2026-09-28T10:36:02+00:00
- ordinary Deep work unpaused afterward.

The user asks why the site still appears as if Deep has nothing.

## Important parallel work

ЧАТ 1 is independently implementing:
`WORKER_TASK_DOSSIER_DEEP_RELEASE_YEAR_IDENTITY_COMPATIBILITY_FIX_01.md`

This diagnostic must not interfere with it.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. relevant Deep visual/publication routes in `PROJECT_ROUTES.md`;
4. accepted reports for:
   - legacy Deep full reanalysis migration preparation;
   - analysis last-write timestamps UI;
   - Deep visual authoritative binding fix;
5. current canonical PASS 2 state/work;
6. current visual payload source and generated/publication artifacts;
7. current Pages/deploy metadata only as needed;
8. only the smallest projection/build files necessary to prove the cause.

## Required diagnostic

Pin the diagnosis to exact current `main` and exact deployed artifact/page generation if available.

Prove where the divergence occurs between:

1. canonical PASS 2 migration state;
2. effective current Deep state after migration promotion;
3. processing/statistics projection;
4. generated visual payload;
5. deployed Pages artifact/browser presentation.

### A. Canonical truth

Confirm exact current:
- migration 30/30 accepted or current equivalent if concurrent changes occurred;
- current authoritative Deep completed count;
- fit/not-fit/incomplete counts;
- Deep last accepted/write timestamp;
- ordinary ready/pending count;
- whether migration revisions are considered current authoritative Deep by normal stage metrics.

Do not assume the migration-specific counter must automatically equal normal Deep completed counter; prove intended semantics from contract.

### B. Site truth

Identify the exact data artifact used by the deployed Statistics page and record its values for:
- Deep completed;
- fit;
- not-fit;
- incomplete/recovery;
- waiting for Dossier;
- ready/pending;
- remaining;
- last write.

Determine whether the user's screenshot is:
- current deployed data;
- stale Pages artifact/cache;
- current payload with a projection bug;
- browser-only presentation bug;
- another proven cause.

### C. Exact divergence point

Find the first boundary where canonical truth becomes zeros/stale values.

Possible categories to prove or reject:
- migration revisions accepted but not included in normal authoritative Deep counters;
- deterministic recomputation reset/ignored migrated current revisions;
- visual build reading old state or wrong generation;
- visual publication guard prevented refresh;
- Pages deployed an older artifact;
- browser/service-worker cache;
- last-write timestamp excludes migration acceptance;
- another exact cause.

Do not patch anything.

### D. Interaction with ordinary Deep

Clarify whether:
- the 30 migrated results should count inside "Окончательно разобрано";
- they should count separately only;
- ordinary Deep counters were intentionally reset by a new semantic generation;
- or the zeros are a defect.

Use canonical decisions/contracts, not intuition.

### E. User-facing consequence

Explain:
- whether cards themselves already use migrated results;
- whether only Statistics is stale/wrong;
- whether ranking/risk presentation is affected;
- whether further Deep runs would overwrite or correctly continue from current truth.

## Scope limits

READ-ONLY diagnosis only.

Do NOT:
- implement a fix;
- rebuild/redeploy manually unless a read-only inspection route requires artifact fetch;
- run Deep/Fast/Dossier;
- modify migration state;
- modify ЧАТ 1 work;
- change Scheduled Tasks;
- change visual state;
- clear caches or trigger workflows.

## Report

Write:
`reviews/worker_reports/deep-migration-results-not-reflected-on-site-diagnostic-01.md`

Required sections:
1. `Task`
2. `Pinned current truth`
3. `Canonical Deep state`
4. `Published site state`
5. `First divergence point`
6. `Why the screenshot shows zeros`
7. `Migration-vs-normal-counter semantics`
8. `Cards/ranking impact`
9. `Interaction with ЧАТ 1`
10. `Changes` — report only
11. `Unresolved`
12. `Status`
13. `Recommended next step` — exactly one bounded next step
14. exact commit/run/artifact refs
15. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete`
- `needs_fix`
- `blocked`
- `needs_user_decision`

Do not start another task after this one.
