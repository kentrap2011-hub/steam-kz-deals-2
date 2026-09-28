# WORKER TASK — DOSSIER / DEEP READY COUNT GAP DIAGNOSTIC 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or target is ambiguous, stop and switch first.

Task ID: `dossier-deep-ready-count-gap-diagnostic-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/dossier-deep-ready-count-gap-diagnostic-01.md`

## User question

The site/current production counters show approximately:

- Dossier prepared/accepted: **46**
- ordinary Deep ready/pending: **38**

The user wants to know exactly why these numbers differ.

Do not assume the reason from prior chats. Re-derive it from current `main`.

## Important current context

A separate one-off legacy Deep reanalysis migration exists:

`deep-legacy-full-reanalysis-with-preserved-positives-01`

At Director acceptance it had:
- 30 migration targets;
- migration semantic execution still pending;
- ordinary Deep ready/pending counted separately.

This diagnostic must distinguish:
1. Dossier accepted/prepared counts;
2. ordinary Deep ready/pending counts;
3. legacy migration scope/counts;
4. already completed or otherwise excluded Deep identities.

Do not mix these denominators.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read only what is necessary:
1. this task;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. relevant Dossier/Deep routes in `PROJECT_ROUTES.md`;
4. current Dossier worker index/work projection;
5. current PASS 2 work projection and PASS 2 state;
6. current visual processing counters;
7. current accepted Dossier store only for the exact discrepant identities;
8. current contracts governing Deep Dossier compatibility/eligibility.

## Required diagnostic

Pin the diagnostic to one exact current `main` commit and record it.

Then prove the arithmetic.

### A. Establish the exact counters

Identify the canonical source for:
- Dossier accepted/prepared count shown as 46;
- ordinary Deep ready/pending count shown as 38;
- Deep waiting-for-Dossier count;
- legacy full-reanalysis migration count.

State whether each is:
- current-card scope;
- Dossier file freshness scope;
- ordinary Deep eligibility scope;
- migration scope;
- another scope.

### B. Reconcile Dossier 46 -> Deep 38

Produce the exact set difference.

For every Dossier item counted in the 46 but not counted in the ordinary Deep 38, list:
- AppID;
- title;
- Dossier state;
- Deep state;
- exact reason it is not ordinary Deep-ready;
- canonical file/contract evidence supporting that reason.

Classify each difference into an explicit reason category, for example:
- current Dossier file exists/fresh but is not compatible with current Deep identity;
- title/release-year/exact-product mismatch;
- stale semantic/work identity;
- already authoritative-completed Deep;
- migration-owned rather than ordinary Deep;
- recovery/incomplete state;
- package/family identity handling;
- another proven reason.

Do not invent categories before inspecting the exact data.

### C. Decide whether this is expected or a defect

Answer separately:

1. Is the difference **46 vs 38** expected under current contracts?
2. If yes, explain why the UI/count labels are still semantically correct or whether they are confusing.
3. If no, identify the exact broken boundary and what should have happened.
4. Are any of the discrepant 8 blocked indefinitely, or will normal GitHub/Dossier/Deep projection eventually make them eligible?
5. Does the active 30-game legacy migration affect the 46->38 difference, or is it a separate count?

## Scope limits

This is diagnosis only.

Do NOT:
- implement a fix;
- edit Dossier/Deep contracts or runtime;
- rerun Dossier/Fast/Deep;
- process backlog manually;
- change migration state;
- change Scheduled Tasks;
- create recovery authorizations;
- modify Board except through the report/normal task closeout if canonical protocol requires it.

The user explicitly asked for this discrepancy to be diagnosed by a worker chat. Do not rely on Director-side exploratory conclusions from previous conversation context; use current repository truth.

## Report

Write:
`reviews/worker_reports/dossier-deep-ready-count-gap-diagnostic-01.md`

Required sections:
1. `Task`
2. `Pinned current truth`
3. `Counter definitions`
4. `46 -> 38 arithmetic`
5. `Exact discrepant identities`
6. `Reason per identity`
7. `Legacy migration interaction`
8. `Expected vs defect`
9. `User-facing explanation`
10. `Changes` — report only
11. `Unresolved`
12. `Status`
13. `Recommended next step` — exactly one bounded next step
14. exact file/commit refs
15. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete`
- `needs_fix`
- `blocked`
- `needs_user_decision`

Do not start another task after this one.
