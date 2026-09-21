# WORKER TASK — PROGRESSIVE PERSONALIZED DEALS PHASE B PASS 1 LIVE ACCEPTANCE 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `progressive-personalized-deals-phase-b-pass1-live-acceptance-01`
Mode: `LIVE ACCEPTANCE / BOUNDED PRODUCTION VALIDATION`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.

Затем открой этот task-файл.

Direct prerequisites:
- `reviews/worker_reports/progressive-personalized-deals-phase-b-pass1-implement-01.md`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass1_worker_prompt.md`
- current canonical work manifest referenced by Phase B PASS 1.

Do not reopen the Phase B implementation architecture.

## Accepted baseline

Already complete:
- Phase B PASS 1 code/control-plane activation;
- GitHub-owned item-level work manifest;
- current visual is Phase B;
- `pass1_active=true`;
- `pass2_active=false`;
- current visible catalogue is non-empty;
- current production state before this acceptance has zero real PASS 1 accepted items;
- no PASS 2 work exists.

## Goal

Prove exactly ONE real PASS 1 item through the full production chain:

GitHub-prepared work
→ Scheduled semantic worker
→ exact item result artifact
→ GitHub ingest/validation
→ durable item state
→ progressive visual rebuild
→ site state/count update.

Do not process the backlog.

## Critical boundedness

This task MUST validate only one current PASS 1 item.

Do not:
- process multiple items for convenience;
- start a continuous worker drain;
- start PASS 2;
- retry a failed item manually;
- choose a different item after failure unless the canonical control plane itself requires a fresh current item after binding invalidation;
- alter queue order;
- repair semantic evidence manually;
- change business/source rules;
- broaden into implementation fixes unless a concrete blocker is proven.

## Item selection

Use GitHub's exact current expected/runnable PASS 1 item according to the canonical manifest/order.

Do not choose an item manually.

Record:
- semantic generation id;
- work_id;
- exact candidate/app identity;
- exact submission path;
- current pre-attempt state.

## Scheduled worker execution

Use the existing authorized Scheduled PASS 1 worker path exactly as currently configured.

Before execution:
- verify the current manifest/binding is still active;
- verify item has not already consumed its one PASS 1 attempt;
- verify PASS 2 remains inactive.

Run exactly one bounded PASS 1 item.

If the external Scheduled worker interface cannot be invoked from this worker environment:
- do not fake a result;
- stop with exact boundary;
- report `blocked_external`.

## Acceptance outcomes

Any of the three valid outcomes is acceptable for end-to-end proof:

- `analyzed_fit`;
- `analyzed_not_fit`;
- `analysis_incomplete`.

The acceptance is about the pipeline, not whether the game is a fit.

For the one real item verify:
- result artifact exists at the exact prepared path;
- GitHub ingest runs;
- exact binding/schema validation occurs;
- exactly one PASS 1 attempt is consumed;
- durable state updates;
- unrelated items remain untouched/runnable;
- counts reconcile;
- visual update is incremental;
- site publication remains available;
- no global queue completion is required.

## Failure acceptance

If the Scheduled worker returns an invalid result or fails:
- do not repair it manually;
- verify whether canonical rules correctly record typed `analysis_incomplete` for that exact attempt or safely reject it without blocking later items;
- stop after this single attempt;
- do not run another item.

If the failure exposes a code/contract defect:
- stop and document the exact defect;
- do not broaden scope.

## Required checks

LIVE-01 — exact current item chosen only by GitHub-owned order.

LIVE-02 — exactly one real PASS 1 attempt is executed.

LIVE-03 — no PASS 2 / no retry loop.

LIVE-04 — exact result artifact path matches prepared work.

LIVE-05 — ingest validates exact current binding.

LIVE-06 — one attempt is consumed for that work_id/generation.

LIVE-07 — resulting durable state is one of fit / not-fit / incomplete or exact fail-closed blocker is recorded.

LIVE-08 — later unrelated work remains runnable.

LIVE-09 — processing counts remain arithmetically valid.

LIVE-10 — visual/site remains available and reflects the accepted state if ingest succeeds.

LIVE-11 — untouched Tier 3 catalogue remains visible.

LIVE-12 — no backlog drain or second item execution occurs.

## Durable report

Write:
`reviews/worker_reports/progressive-personalized-deals-phase-b-pass1-live-acceptance-01.md`

Required sections:
1. Task / repo / mode.
2. Baseline.
3. Exact selected work item.
4. Scheduled worker execution.
5. Result artifact.
6. Ingest/validation.
7. Durable state transition.
8. Visual/site update.
9. LIVE-01..12.
10. Any blocker.
11. Status.
12. Exactly one recommended next step.
13. Exact refs.

Allowed statuses:
- `complete_live_acceptance`
- `blocked_external`
- `needs_fix`

## Exactly one next step

If `complete_live_acceptance`:
- return to Director;
- only then authorize normal canonical PASS 1 backlog processing.

If `blocked_external`:
- return exact external action needed.

If `needs_fix`:
- return exact single blocker; do not process another item.
