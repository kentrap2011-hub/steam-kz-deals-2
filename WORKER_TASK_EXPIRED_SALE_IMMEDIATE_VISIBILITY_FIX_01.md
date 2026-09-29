# WORKER TASK — EXPIRED SALE IMMEDIATE VISIBILITY FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or target is ambiguous, stop and switch first.

Task ID: `expired-sale-immediate-visibility-fix-01`
Mode: `DIAGNOSE -> CONTRACT-FIRST IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/expired-sale-immediate-visibility-fix-01.md`

## User-observed defect

A current screenshot shows:

- card: `Titanfall® 2`
- current sale end is already passed;
- UI explicitly shows `Скидка закончилась`;
- the card nevertheless remains visible at `Позиция в ленте: 1 из 381`.

The user explicitly wants an expired sale to disappear automatically.

## Canonical existing rule

This is NOT a new product-policy decision.

Current `PROJECT_RULES.md` already states:

- sale urgency cannot rescue an already-ended sale;
- Taste score and current commercial state are separate;
- commercial data refreshes daily;
- a known saved sale end can be evaluated locally without another network request;
- if the saved sale has already ended at display time, the offer must not be shown;
- the Taste analysis/cache remains reusable after the sale ends;
- if a later sale appears, current price/discount/end must come from a new commercial snapshot.

Therefore the screenshot demonstrates a defect against an existing rule.

## Goal

Make every currently visible paid-sale card with a known `sale_end_utc <= now` disappear from the user-visible sale feed immediately, without waiting for the next production build or Steam refresh.

Preserve the underlying Taste/Fast/Deep/Dossier result and cache.

Unknown sale end must NOT cause hiding.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. relevant expiry rules in `PROJECT_RULES.md`;
4. relevant ranking/urgency decisions in `PROJECT_DECISIONS.md`;
5. `PROJECT_ROUTES.md`;
6. `config/execution_ownership_contract.json`;
7. the smallest current browser/feed/render/queue files necessary.

Do not start unrelated tasks.

## Architecture preflight

Before implementation prove:

- this is presentation-time commercial visibility, not semantic Taste/Deep/Dossier logic;
- no Fast/Dossier/Deep result needs to be invalidated or rerun;
- no new Steam/network refresh is required at the expiry moment;
- known `sale_end_utc` is sufficient local factual input;
- browser may apply the already-canonical local expiry visibility rule without becoming owner of commercial truth;
- GitHub remains owner of persisted commercial source data and next daily refresh;
- manual queue state must not keep an expired card visible;
- Scheduled Tasks remain unchanged.

## Phase A — exact diagnosis

Use the current Titanfall 2 case as the pinned regression if it still exists in the current published payload.

Determine exactly why a card with passed `sale_end_utc` remains visible.

Trace:
- canonical/published `sale_end_utc`;
- the code that computes `Скидка закончилась`;
- the code that builds the visible queue;
- whether expiry affects only the label/urgency but not eligibility;
- whether initial feed, mode switches, local queue restore, search, wishlist/final/interesting views, or cached LKG payload bypass filtering;
- whether the displayed feed count still includes expired cards.

Classify the first missing/incorrect boundary.

## Phase B — implementation

Implement the smallest generic fix.

Required behavior:

1. If a paid offer has known `sale_end_utc` and current time is at or after it, the card is excluded from the active sale feed.
2. It disappears without waiting for a production rebuild.
3. It is excluded even if the payload itself is stale.
4. Unknown/null/unparseable sale end remains visible under existing policy unless another canonical exclusion applies.
5. No grace period is invented unless already canonical.
6. Do not mutate or delete the underlying semantic/Taste data.
7. A future fresh sale snapshot may make the game visible again normally.
8. Manual `В конец очереди`, previous display count, local queue history or current cursor cannot keep an expired card visible.
9. Feed totals/position text must reflect the filtered visible set.
10. Explicit urgency mode must also exclude expired offers; expired is not a highest urgency bucket.
11. Search and non-sale historical/detail surfaces should only be changed if they currently present themselves as active-sale surfaces. Do not erase historical data unnecessarily.
12. If the page remains open across the expiry moment, the card should disappear on the next existing render/recompute event; if there is no reasonable existing event, add the smallest bounded local expiry re-evaluation needed, not a recurring network poll.

## Required regressions

At minimum prove:

- sale end in past => card hidden;
- sale end exactly now => hidden;
- sale end in future => visible;
- sale end unknown => visible;
- malformed date => fail safely under current unknown-date semantics, not hidden;
- expired Deep-fit card hidden;
- expired Fast-fit card hidden;
- expired unresolved card hidden;
- manual-end expired card hidden;
- expired top/current card advances cursor to next visible card;
- visible count/position excludes expired cards;
- urgency mode cannot show expired card;
- stale payload with passed timestamp still hides locally;
- Taste/Deep/Fast/Dossier fields remain untouched;
- fresh later sale with new future `sale_end_utc` becomes visible normally.

Include the current Titanfall 2 example if reproducible:
- AppID 1237970;
- published sale end previously observed as `2026-09-28T17:00:00+00:00`;
- card must not remain in the active feed after that instant.

## Interaction with current publication problems

Current site publication is known to be stale for an independent reason.

This task must work even against an old payload when its stored `sale_end_utc` is already known and passed.

Do NOT fold in:
- the Russian-description blocker fix running in active ЧАТ 1;
- the visual stale-snapshot rebase-race fix;
- Deep-first ranking changes.

If a fresh deploy is blocked by the independent Russian-description problem, implementation/regressions may still complete, but report publication proof honestly as blocked by that separate task.

## Hard prohibitions

Do not:
- rerun Fast/Dossier/Deep;
- change semantic results;
- change score weights;
- change RANK-013;
- change sale data by hand;
- invent new sale end dates;
- add a network polling scheduler;
- change Scheduled Tasks;
- weaken unknown-sale-end behavior;
- delete Taste cache/results when sale expires.

## Report

Write:
`reviews/worker_reports/expired-sale-immediate-visibility-fix-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Pinned Titanfall case`
4. `Root cause`
5. `Changes`
6. `Local expiry semantics`
7. `Queue/cursor/count behavior`
8. `Regression coverage`
9. `Fresh-main reconciliation`
10. `Publication validation`
11. `Changes not made`
12. `Unresolved`
13. `Status`
14. `Recommended next step` — exactly one bounded next step or `none`
15. exact PR/commit/run/artifact refs
16. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `blocked`
- `needs_user_decision`

Do not start another task after this one.
