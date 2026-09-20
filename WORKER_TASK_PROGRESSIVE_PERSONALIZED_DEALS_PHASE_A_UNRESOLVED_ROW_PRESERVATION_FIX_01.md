# WORKER TASK — PROGRESSIVE PERSONALIZED DEALS PHASE A UNRESOLVED ROW PRESERVATION FIX 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `progressive-personalized-deals-phase-a-unresolved-row-preservation-fix-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

This is a narrow continuation of the already user-authorized Phase A implementation.

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.

Затем открой:
- `WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_PHASE_A_IMPLEMENT_01.md`
- `WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_PHASE_A_ACTIVATION_ROUTING_FIX_01.md`
- `reviews/worker_reports/progressive-personalized-deals-phase-a-implement-01.md`

Не начинай Phase A заново.

## Accepted current state

Already proven:
- progressive input on main contains 719 current candidates;
- activation routing is fixed;
- full progressive build now runs;
- UI regressions and Pages deployment run successfully;
- current blocker is inside history/expiry enrichment;
- unresolved Tier 2/3 rows are stripped correctly but then dropped instead of retained;
- resulting deployed payload is empty despite 719 current candidates;
- PASS 1/PASS 2/Scheduled ChatGPT have not run.

## Exact blocker to fix

Current behavior in `scripts/build_daily_visual_payload.py::enrich_history_and_remove_expired()` (or exact owning equivalent):

For rows whose `analysis_state` is unresolved:
- unsupported personalization is stripped;
- code then exits the row path without appending that row to the kept/final collection.

This violates Phase A:
- `analysis_incomplete` must remain visible Tier 2;
- `not_analyzed` must remain visible Tier 3.

## Goal

Fix ONLY row preservation for unresolved progressive states through history/expiry enrichment.

After the fix:
- unresolved rows keep current deterministic deal/source/history-safe facts;
- unsupported personalized fields remain stripped;
- rows are retained unless an existing hard deterministic exclusion/expiry/source-integrity rule legitimately removes them;
- full build produces a non-empty progressive payload from the current 719-candidate input;
- existing Tier 1 analyzed-fit behavior remains unchanged.

## Scope

Allowed:
- inspect the exact owning history/expiry enrichment function and focused tests;
- modify the smallest code path necessary to retain unresolved progressive rows;
- add/update focused regression for this defect;
- run normal full build/validation/deploy;
- update the existing Phase A durable report.

Forbidden:
- redesign progressive states;
- change tier ordering;
- change UI labels/counters;
- change Taste/Dossier semantics;
- implement PASS 1/PASS 2;
- run Scheduled ChatGPT;
- change source/business eligibility rules;
- disable expiry/history validation globally;
- broaden into unrelated cleanup.

## Required behavior

For `analysis_incomplete` and `not_analyzed`:

1. Strip unsupported semantic/personalized fields exactly as Phase A requires.
2. Preserve the row through history/expiry enrichment.
3. Still apply legitimate deterministic expiry/history/source rules that are independent of personalization.
4. Do not invent history, SteamDB facts, score, why-fit, risks, or semantic conclusions.
5. Preserve producer-owned analysis state/tier/count contribution.

For `analyzed_fit`:
- existing enrichment/ranking behavior remains unchanged.

For `analyzed_not_fit`:
- remains excluded from normal visible list according to canonical progressive semantics.

## Validation

Prove at minimum:

ROW-01 — unresolved `not_analyzed` survives history/expiry enrichment when offer is still valid.

ROW-02 — unresolved `analysis_incomplete` survives history/expiry enrichment when offer is still valid.

ROW-03 — unsupported personalized fields remain stripped on both unresolved states.

ROW-04 — legitimately expired/ineligible unresolved item is still removed by existing deterministic rules.

ROW-05 — analyzed-fit path remains unchanged.

ROW-06 — analyzed-not-fit remains excluded.

ROW-07 — aggregate counts after build reconcile with the surviving progressive candidate population.

ROW-08 — full current build from the real 719-candidate progressive input produces a non-empty progressive payload.

ROW-09 — deployed payload contains visible Tier 2/3 items and correct processing counts.

ROW-10 — UI regressions and Pages deployment pass.

ROW-11 — no Scheduled ChatGPT/PASS 1/PASS 2 execution occurs.

ROW-12 — no unrelated architecture changes.

## Durable report

Update the existing report only:
`reviews/worker_reports/progressive-personalized-deals-phase-a-implement-01.md`

Append/finalize:
- exact producer defect;
- exact fix;
- files changed;
- ROW-01..12;
- final PHASEA-01..16 status;
- full build run refs;
- deploy run refs;
- resulting current payload counts;
- user-visible site state;
- unresolved blockers, if any;
- final Phase A status.

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `complete_code_waiting_external_live_acceptance`
- `needs_fix`
- `blocked_external`

## Completion rule

Before claiming completion:
- commit report to `main`;
- reread report from `main`;
- verify exact run/commit refs;
- verify deployed/current payload is not empty solely because unresolved rows were dropped.

## Exactly one next step

If Phase A becomes functionally live:
- return to Director for acceptance before Phase B.

If another blocker appears:
- stop;
- record the exact blocker in the same Phase A report;
- do not broaden scope.
