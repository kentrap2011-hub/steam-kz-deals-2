# WORKER TASK — PROGRESSIVE PERSONALIZED DEALS PHASE A ACTIVATION ROUTING FIX 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `progressive-personalized-deals-phase-a-activation-routing-fix-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

This is a narrow continuation of the already user-authorized Phase A implementation.

## START

First open current `CHAT_PROTOCOL.md` from `main` and complete START gate.

Then open:
- `WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_PHASE_A_IMPLEMENT_01.md`
- `reviews/worker_reports/progressive-personalized-deals-phase-a-implement-01.md`

Do not restart the full Phase A implementation.

## Accepted current state

Already merged and accepted as implemented at checkpoint:
- progressive personalization contract/state model;
- per-item projection and counts;
- 719-row `progressive_candidate_context.jsonl`;
- conservative semantic mapping;
- tier-first producer/UI ordering;
- required UI labels and counters;
- focused Phase A regressions.

Exact unresolved blocker:
- normal daily visual scope classifier selects `commercial_refresh`;
- full progressive build is skipped;
- current canonical visual remains the legacy 3-row semantic payload;
- therefore the site does not yet expose Phase A.

## Goal

Fix ONLY the activation routing decision so that when the progressive current catalogue is newly generated, missing, stale, or not represented in the current visual, the canonical daily visual workflow selects the full progressive build rather than `commercial_refresh`.

Then run the normal validation/deploy path and prove Phase A is live.

## Scope

Allowed:
- inspect the existing daily visual scope/routing condition and its compact tests;
- change only the smallest workflow/script/validation surface needed to choose the correct build scope;
- add/update focused regression for this exact routing defect;
- run normal GitHub build/validation/deploy;
- update the existing Phase A report with final activation evidence.

Forbidden:
- redesign progressive state model;
- change sorting semantics;
- change UI feature set;
- change Taste/Dossier semantics;
- implement PASS 1/PASS 2;
- run Scheduled ChatGPT;
- process semantic backlog;
- change business/source eligibility rules;
- broaden into unrelated workflow cleanup.

## Required behavior

Full progressive build MUST be selected when any of these is true:
- current progressive candidate context exists for the active source but current visual has no progressive state block;
- current visual item population is legacy/incompatible with the active progressive candidate set;
- progressive state/count schema is missing/stale for the current source;
- another exact Phase A freshness/binding invariant proves a full rebuild is required.

`commercial_refresh` remains valid only when:
- a compatible progressive visual for the same active semantic/current source lineage already exists;
- only commercial fields need refresh;
- progressive state/count/tier structure remains valid.

Do not turn every commercial refresh into a full build if the compatible progressive payload is already current.

## Validation

Prove at minimum:

ROUTE-01 — current checkpoint state (719 progressive candidates + legacy 3-row visual) selects FULL progressive build.

ROUTE-02 — compatible progressive visual + only commercial source change may still select `commercial_refresh`.

ROUTE-03 — stale/missing progressive processing block cannot select commercial-only refresh.

ROUTE-04 — source-integrity failure remains fail-closed.

ROUTE-05 — full progressive build produces a visual with:
- progressive processing/status block;
- per-item analysis state;
- aggregate counts;
- visible unresolved candidates;
- no fake personalized fields on unresolved items.

ROUTE-06 — deployed site reaches UI regressions and Pages deployment.

ROUTE-07 — urgency/tier UI regressions pass.

ROUTE-08 — current deployed/current visual is no longer the legacy 3-row-only payload unless the deterministic eligible source truly contains only 3 visible candidates.

ROUTE-09 — no Scheduled ChatGPT/PASS 1/PASS 2 execution occurred.

ROUTE-10 — no unrelated architecture changes were made.

## Durable report

Update the existing report:
`reviews/worker_reports/progressive-personalized-deals-phase-a-implement-01.md`

Do not create a competing Phase A result report.

Append/finalize:
- exact routing defect;
- exact fix;
- files changed by this narrow continuation;
- ROUTE-01..10;
- final PHASEA-01..16 status;
- build/deploy run refs;
- resulting current payload counts;
- whether site is live;
- unresolved, if any;
- final allowed Phase A status.

Final allowed statuses:
- `complete_ready_for_director_acceptance`
- `complete_code_waiting_external_live_acceptance`
- `needs_fix`
- `blocked_external`

Before claiming completion:
- commit report to `main`;
- reread exact report from `main`;
- verify exact run/commit refs.

## Exactly one next step

If Phase A becomes live:
- return to Director for acceptance before Phase B.

If this routing fix exposes a different blocker:
- stop and record that blocker in the same Phase A report;
- do not broaden scope.
