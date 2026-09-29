# Worker report — expired-sale-immediate-visibility-fix-01

## 1. Task

Task: `WORKER_TASK_EXPIRED_SALE_IMMEDIATE_VISIBILITY_FIX_01.md`.

Repository/source of truth: `kentrap2011-hub/steam-kz-deals-2`, `main`.

Implementation PR: #121 — `Hide expired sales immediately in active browser feed`.

Goal completed at code/regression level: a paid active-sale card with a valid known `sale_end_utc <= now` is removed locally from the browser-visible active sale set without a new Steam request or production rebuild. Unknown/null/malformed sale end remains visible.

## 2. Architecture preflight

- This defect is presentation-time commercial visibility, not Taste/Fast/Dossier/Deep semantic logic.
- Canonical persisted commercial truth remains GitHub-owned. The browser consumes only the already-published `sale_end_utc`.
- No new price, discount, review, Steam, SteamDB or other network lookup is introduced at expiry time.
- No semantic result is invalidated, rewritten or rerun.
- Browser filtering happens before local queue/manual-end/urgency reconciliation, so local state cannot keep an expired paid-sale card visible.
- The next daily GitHub commercial refresh remains authoritative for a later new sale and its new price/discount/end.
- Scheduled Tasks are unchanged.
- No queue/retry/checkpoint/scheduler ownership moved out of GitHub.

Canonical basis:
- `PROJECT_RULES.md`: known sale end may be applied locally; ended offer is not shown; Taste result remains reusable; unknown sale end does not exclude.
- `PROJECT_DECISIONS.md#RANK-013`: urgency is only an ordering override inside a ranking stage and cannot redefine eligibility.
- `config/execution_ownership_contract.json`: browser remains read-only presentation over producer-owned facts.

## 3. Pinned Titanfall case

Pinned observed case from the task:
- title: `Titanfall® 2`
- AppID: `1237970`
- observed published sale end: `2026-09-28T17:00:00+00:00`
- observed symptom after that instant: card still visible while `deadlineText()` rendered `⚠ Скидка закончилась`.

The exact AppID/timestamp pair is now a regression fixture. At a test time after the timestamp, `filterActiveSaleItems()` returns no Titanfall card.

A fresh canonical visual payload could not be published during this task because the independent publication chain remains blocked; therefore this report does not claim a new production payload containing or removing Titanfall.

## 4. Root cause

First missing boundary: browser eligibility/visible-set construction.

Before the fix:
- `deadlineText()` independently compared `sale_end_utc` with `Date.now()`, so the UI could correctly say `Скидка закончилась`;
- `canonicalQueueIds()` still sorted every item supplied by the payload;
- `buildQueue()` treated every payload item as active;
- manual `В конец очереди`, urgency mode, restored local queue state, counts and current cursor therefore all operated on a set that still contained the expired card;
- search and active saved-list views also used the unfiltered `items`.

Expiry was therefore a label/urgency fact, not a visibility gate.

## 5. Changes

### `web/progressive-personalization-ui.js`

Added pure local helpers:
- `saleEndTimeMs(value)`
- `hasKnownExpiredSale(game, nowMs)`
- `filterActiveSaleItems(items, nowMs)`
- `cursorForVisibleIds(oldIds, oldCursor, visibleIds)`

The helpers only interpret the already-published timestamp. They do not mutate card/semantic data.

### `web/app.js`

- Added `payloadItems()` and `syncActiveSaleItems()`.
- `buildQueue()` now filters the raw payload to the active sale set before automatic ordering, manual-end reconciliation, cursor and count logic.
- `render()` invokes `buildQueue()`, so expiry is re-evaluated on every existing render event.
- `searchRender()` also re-evaluates the active set before active-list search.
- Initial loading now goes through the same render/filter path, including stale/LKG payloads.
- Cursor reconciliation uses the tested pure `cursorForVisibleIds()` helper.
- Malformed date display is treated as unknown instead of producing a broken date/deadline string.
- The redundant pre-render `buildQueue()` call in urgency toggle was removed because `render()` now owns re-evaluation.

### `web/progressive-personalization-ui.test.js`

Added executable expiry/visibility regressions and bounded integration assertions.

## 6. Local expiry semantics

Rule implemented:

`valid parsed sale_end_utc <= current browser time => excluded from active paid-sale set`.

Exact boundary is inclusive: equality with `now` is expired.

Fail-safe unknown behavior remains:
- null => visible;
- missing => visible;
- blank => visible;
- malformed/unparseable => visible.

No grace period was introduced.

The raw `data.items` payload remains intact in memory. Only the derived browser `items`/lookup used for active-sale surfaces is filtered. A later fresh payload containing the same game with a new future `sale_end_utc` becomes visible normally.

## 7. Queue/cursor/count behavior

Filtering occurs before queue reconciliation.

Consequences:
- an expired item is absent from canonical automatic order;
- an expired item is absent from urgency order;
- stored `manual_end_at` cannot resurrect it;
- restored old queue IDs are reconciled against the filtered active IDs;
- when the currently open card expires, the cursor stays at the same visible index where possible, which advances to the next remaining card; if no later card exists it clamps to the last remaining card;
- feed count uses the filtered queue;
- position text therefore uses the filtered visible set;
- wishlist/liked/final active-sale lists render from the filtered `items`;
- active-list search renders from the filtered `items`.

The user's local history record is not deleted. It simply no longer makes an expired active sale visible.

## 8. Regression coverage

Executable coverage in `web/progressive-personalization-ui.test.js` proves:
- sale end in past => hidden;
- sale end exactly now => hidden;
- sale end in future => visible;
- null/missing sale end => visible;
- malformed sale end => visible under unknown-date semantics;
- expired Deep-fit => hidden;
- expired Fast-fit => hidden;
- expired unresolved => hidden;
- expired item remains hidden regardless of manual-end-like state;
- pinned Titanfall AppID 1237970 / `2026-09-28T17:00:00+00:00` => hidden after expiry;
- filtered active set gives a 2-card count from a 3-card payload when the current first card has expired;
- expired current card advances to the next visible card at position `1 из 2`;
- urgency sorting cannot resurrect an expired card;
- semantic object identity and Fast/Dossier/Deep fields are unchanged by filtering;
- a later fresh sale with a future end becomes visible again.

Integration assertions prove the active-sale filter runs before queue/manual reconciliation and that render/search both trigger re-evaluation.

Final functional implementation head before report-only closeout:
`82946194677cb32b71e9fef007edf3bf6071ff15`.

PR validation for that head:
- Validate Progressive PASS 2 core: run `36517131643` / run #377 — success.
- PASS 2 validate job: `109241827175` — success.
- UI provenance regression step — success and executes `node web/progressive-personalization-ui.test.js`.
- Validate backlog dispositions: run `36517131563` / run #1406 — success.
- Validate package purchase value: run `36517131574` / run #32 — success.

An earlier implementation head `1718eece3c3ba8327f36bb9aeb74c02bebe855e6` also passed all three workflows; the later head adds executable cursor/count/urgency proof.

## 9. Fresh-main reconciliation

Concurrent workers continued advancing `main` during this task.

Important reconciliation points:
- after detecting that a generic recent-commit listing is not authoritative for `main` HEAD, the worker branch was explicitly anchored through the `main` branch ref before substantive re-application;
- the implementation was reapplied from fresh `main` commit `c25762948500d6f64158047de01c7e4f5952911f`;
- `main` later advanced through `41c03df2d5a670ba9cc4e09d056b433fc9452d2d` and was most recently observed at `10925294b0ba7c393cc6b182c8d11e1d59e2b699`;
- comparison from `c257629...` to that newer `main` showed concurrent changes in `CURRENT_TASK.md`, `DIRECTOR_TASK_BOARD.md`, Russian-description report and Dossier/Deep production state, but no changes to `web/app.js`, `web/progressive-personalization-ui.js` or its test;
- raw GitHub PR state for #121 reported `mergeable=true`; the branch is behind only because unrelated concurrent production/control-plane writes continue landing on `main`.

No unrelated concurrent production state was copied into or modified by this implementation.

## 10. Publication validation

No live/publication success is claimed.

Independent current publication state from `main`:
- Russian-description fix PR #119 is merged at `c25762948500d6f64158047de01c7e4f5952911f`;
- fresh full visual run `36516631672` still failed the meaningful-Russian gate with App_13500 and App_1155970 in `needs_translation`;
- post-merge pre-AI run `36516631678` is additionally stopped earlier by the pre-existing Progressive current-binding regression for `game:1143810`;
- latest documented canonical visual remains stale commit `2202a668cad11f67f0659aa6bcfe5e6cf34bb9ab`;
- degraded Pages deploy run `36516701438`, artifact `11011058068`, deployed that existing stale visual.

This task is deliberately designed to work against a stale payload once its stored end timestamp has passed. PR-level behavior is validated, but the source change is not live until PR #121 is accepted/merged and the normal Pages source is deployed.

## 11. Changes not made

Not changed:
- Fast execution/results;
- Dossier execution/results;
- Deep execution/results;
- Taste cache or verdicts;
- score weights/formulas;
- RANK-013;
- producer-owned commercial values or sale-end timestamps;
- price/discount/history data;
- Scheduled Tasks;
- GitHub scheduler/queue/retry/checkpoint ownership;
- Russian-description blocker logic;
- stale-visual rebase-race logic;
- Deep-first ranking implementation.

No sale data was edited by hand and no expiry network polling was added.

## 12. Unresolved

- Live Pages proof is not available before PR #121 is merged/deployed.
- The independent visual publication chain remains blocked as described above.
- The current production visual was not rewritten by this task; only the browser's visibility behavior is fixed.

No unresolved implementation or regression failure is known for the scoped expiry rule.

## 13. Status

`complete_ready_for_director_acceptance`

The scoped implementation and required regressions are complete. Publication proof is separately blocked and is not treated as an implementation failure per the task contract.

## 14. Recommended next step

Director reviews and accepts PR #121 against the then-current `main`, merging it only if GitHub still reports a clean/mergeable change set.

## 15. Exact PR/commit/run/artifact refs

- PR: #121 — `Hide expired sales immediately in active browser feed`.
- Functional implementation head: `82946194677cb32b71e9fef007edf3bf6071ff15`.
- Main base used for final functional re-application: `c25762948500d6f64158047de01c7e4f5952911f`.
- Latest main observed during reconciliation: `10925294b0ba7c393cc6b182c8d11e1d59e2b699`.
- PASS 2 core: `36517131643`, job `109241827175`.
- Backlog dispositions: `36517131563`.
- Package purchase value: `36517131574`.
- Independent Russian-description full visual: `36516631672`.
- Independent pre-AI blocker run: `36516631678`.
- Degraded Pages deploy: `36516701438`, artifact `11011058068`.
- Existing stale canonical visual commit: `2202a668cad11f67f0659aa6bcfe5e6cf34bb9ab`.

## 16. Efficiency / reusable lesson

Two reusable operational lessons were confirmed:
1. A recent-commit search is not a safe substitute for reading the explicit `main` branch ref before creating/rebasing a worker branch. The branch endpoint/ref must be the authoritative HEAD check.
2. When concurrent production workers continuously move `main`, fresh-main reconciliation should compare the changed paths. If drift is confined to unrelated production state and GitHub reports the PR mergeable, repeatedly rebuilding the worker branch after every independent data commit only creates churn.

The task route itself was already documented: browser-local queue/view overrides live in `web/app.js`; no broad repository rediscovery was needed after `PROJECT_ROUTES.md` was consulted.
