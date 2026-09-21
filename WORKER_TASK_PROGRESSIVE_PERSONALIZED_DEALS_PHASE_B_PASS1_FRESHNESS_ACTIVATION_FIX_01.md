# WORKER TASK — PROGRESSIVE PERSONALIZED DEALS PHASE B PASS 1 FRESHNESS ACTIVATION FIX 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `progressive-personalized-deals-phase-b-pass1-freshness-activation-fix-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

This is a narrow continuation of the already user-authorized Phase B / PASS 1 work.

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.

Затем открой:
- `WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_PHASE_B_PASS1_IMPLEMENT_01.md`
- `reviews/worker_reports/progressive-personalized-deals-phase-b-pass1-implement-01.md`

Не продолжай широкий Phase B IMPLEMENT.

## Accepted checkpoint state

Already implemented/merged:
- canonical PASS 1 contract;
- GitHub-owned semantic generation identity;
- item-level immutable work manifest;
- one-attempt-per-item/generation state;
- independent item ingest;
- no maximal-contiguous-prefix semantics;
- lightweight PASS 1 worker contract;
- active real work manifest:
  - total scope = 721
  - attempted = 0
  - remaining = 721
- Phase A fallback remains live with 720 visible Tier 3 cards.

Current exact blocker:
- normal daily visual build fails before Phase B activation;
- failing regression:
  `scripts/test_visual_freshness_receipt.py::test_progressive_open_semantic_queue_is_fresh_current_catalogue`
- the fixture represents Phase A fallback without explicit `pass1_active=false` / `pass2_active=false`;
- current freshness helper requires those explicit flags;
- as a result the build classifies the valid fallback incorrectly and fails before producing a Phase B-aware visual.

## Goal

Fix ONLY the freshness-receipt compatibility regression so that:

- the accepted Phase A fallback remains valid while PASS 1 work is open;
- current Phase B control-plane state can activate through the normal full visual build;
- open/nonzero PASS 1 remaining work does not make the current catalogue stale/invalid;
- source-integrity and semantic binding guards remain strict.

Then rerun the existing normal full visual build/deploy path.

## Scope

Allowed:
- inspect the exact freshness helper and the failing focused fixture/test;
- make the smallest compatible fix in fixture/helper/schema handling;
- preserve explicit Phase A/Phase B semantics;
- rerun focused test;
- rerun normal daily visual build/deploy;
- update the existing Phase B report.

Forbidden:
- change PASS 1 queue semantics;
- change work manifest ordering;
- change worker prompt strategy;
- change item-level ingest;
- run Scheduled ChatGPT;
- ingest a real PASS 1 semantic item;
- implement PASS 2;
- modify UI feature set;
- change source/business eligibility;
- broaden into unrelated freshness cleanup.

## Required behavior

A valid Phase A fallback visual must remain fresh/current when:
- source lineage is current;
- unresolved catalogue is valid;
- no contradictory progressive state exists;
- PASS 1 control-plane work is open but no item outcome has yet been accepted.

A Phase B-aware visual must be able to report:
- `pass1_active=true`;
- remaining count > 0;
- site still published;
- untouched items remain Tier 3.

Do not make missing/ambiguous flags globally permissive. The fix must preserve fail-closed behavior for truly contradictory/stale progressive metadata.

## Validation

FRESH-01 — failing freshness regression becomes green.

FRESH-02 — explicit Phase A fallback with PASS 1 inactive remains accepted.

FRESH-03 — Phase B active/open PASS 1 with remaining work remains publishable.

FRESH-04 — contradictory progressive state still fails closed.

FRESH-05 — source-integrity mismatch still fails closed.

FRESH-06 — normal daily full visual build succeeds.

FRESH-07 — resulting current visual exposes Phase B/PASS 1 active state with remaining > 0 and non-empty visible catalogue.

FRESH-08 — Phase A fallback safety remains intact if no PASS 1 result exists.

FRESH-09 — deploy/UI regressions succeed.

FRESH-10 — no Scheduled ChatGPT/PASS 1 semantic item execution/PASS 2 occurs.

## Durable report

Update the existing report only:
`reviews/worker_reports/progressive-personalized-deals-phase-b-pass1-implement-01.md`

Append/finalize:
- exact freshness defect;
- exact fix;
- files changed;
- FRESH-01..10;
- updated PASS1-01..20;
- exact build/deploy refs;
- current manifest counts;
- current visual Phase B status;
- whether Phase B is now ready for one bounded real item acceptance;
- unresolved blockers, if any;
- final allowed status.

Allowed status after this fix:
- `complete_code_waiting_external_live_acceptance` if code/control-plane/visual activation is green but no real Scheduled PASS 1 item has been accepted;
- `complete_ready_for_director_acceptance` only if task completion rule is truthfully satisfied;
- `needs_fix`;
- `blocked_external`.

## Exactly one next step

If freshness activation becomes green and no real PASS 1 item has yet been accepted:
- stop;
- return to Director for one bounded real Scheduled PASS 1 item acceptance.

Do not process the backlog.
Do not start PASS 2.
