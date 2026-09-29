# Worker report — expired-sale-immediate-visibility-fix-01

## 1. Task

Task: `WORKER_TASK_EXPIRED_SALE_IMMEDIATE_VISIBILITY_FIX_01.md`.

Repository/source of truth: `kentrap2011-hub/steam-kz-deals-2`, `main`.

Implementation PR: #121 — `Hide expired sales immediately in active browser feed`.

PR #121 is merged into `main` as merge commit `9a500cefd3ec3bf460cf3c51afe92c35e55ab97b`.

Final scoped behavior: a paid active-sale card with a valid known `sale_end_utc <= now` is removed locally from the browser-visible active sale set without a new Steam request or production rebuild. Unknown/null/malformed sale end remains visible.

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

Final rebuilt PR head:
`382432734586d2b7951dde060ad05dd40a13903a`.

Required checks on that rebuilt head all passed:
- Validate Progressive PASS 2 core: run `36518539660` / run #385 — success;
- PASS 2 validate job: `109246150807` — success;
- `UI provenance regression` step — success and executes `node web/progressive-personalization-ui.test.js`;
- Validate backlog dispositions: run `36518539741` / run #1415 — success;
- Validate package purchase value: run `36518539636` / run #35 — success.

Post-merge checks on `main@9a500cef...` also passed:
- Validate Progressive PASS 2 core: run `36518618397` / run #386 — success;
- Validate backlog dispositions: run `36518618404` / run #1416 — success.

## 9. Fresh-main reconciliation

The original PR branch had fallen behind because concurrent ЧАТ 1 and production/Dossier work continued writing `main`.

Final rebuild procedure:
1. Read exact current `main` branch ref.
2. Use fresh `main@93d3c7b969fb55c25944a5707a6c1f70b1168b71` as the parent/base tree.
3. Reapply only the exact task blobs:
   - `web/app.js`;
   - `web/progressive-personalization-ui.js`;
   - `web/progressive-personalization-ui.test.js`;
   - this worker report.
4. Do not carry the worker branch's old `CURRENT_TASK.md`; the fresh `main` version was preserved.
5. Force-move the existing PR branch to rebuilt commit `382432734586d2b7951dde060ad05dd40a13903a`.

After the rebuild, `main` continued to advance independently. The intervening commits touched Chat 1 / routing / Progressive tests and then fresh pre-AI/Dossier production state, but did not touch the three implementation `web/**` files.

Immediately before merge, PR #121 reported `mergeable=true`, `mergeable_state=clean`, and all required PR checks were green.

The actual merge commit is:
`9a500cefd3ec3bf460cf3c51afe92c35e55ab97b`.

Its parents are:
- first parent `4836bea4c7c0822baa08c954cfbcfe6651ccb0d5` — the then-current `main`, containing the newest Chat 1 and production/Dossier writes;
- second parent `382432734586d2b7951dde060ad05dd40a13903a` — the rebuilt PR head.

Therefore the merge preserved all concurrent `main` work and added only the scoped task changes; it did not roll back Chat 1 or production/Dossier state.

## 10. Publication validation

Implementation is merged in `main`, but live visual publication proof remains independently blocked.

The merge push triggered full visual build run `36518618313`:
- scope job succeeded;
- build job `109246437198` reached `Require meaningful Russian descriptions before canonical commit`;
- that unchanged gate failed with `invalid_count=2`;
- exact unresolved cards were:
  - `game:13500` / `Prince of Persia: Warrior Within™` — `needs_translation`;
  - `game:1155970` / `Roadwarden` — `needs_translation`.

This is the same independent Russian-description publication blocker class already documented outside this task. The expired-sale implementation did not weaken or bypass that gate.

Deploy visual runs associated with the merge did not establish a new live payload:
- `36518618351` — cancelled;
- `36518623279` — skipped;
- `36518660075` — skipped.

Therefore:
- source implementation is merged and regression-validated in `main`;
- no new live Pages/publication success is claimed;
- the local expiry rule is intentionally capable of hiding a passed known timestamp even when the browser receives an older/stale payload.

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

No scoped implementation or regression issue remains.

Only publication proof remains unavailable because the independent meaningful-Russian gate blocks a new canonical visual payload. That blocker is outside this task and was not modified here.

## 13. Status

`complete_ready_for_director_acceptance`

PR #121 is merged into `main`; required regressions pass before and after merge. Live publication proof is separately blocked by the already-known Russian-description gate and is not treated as a failure of this scoped task.

## 14. Recommended next step

none

## 15. Exact PR/commit/run/artifact refs

- PR: #121 — `Hide expired sales immediately in active browser feed`.
- Rebuilt PR head: `382432734586d2b7951dde060ad05dd40a13903a`.
- Merge commit in `main`: `9a500cefd3ec3bf460cf3c51afe92c35e55ab97b`.
- Merge first parent / preserved then-current `main`: `4836bea4c7c0822baa08c954cfbcfe6651ccb0d5`.
- Merge second parent / task head: `382432734586d2b7951dde060ad05dd40a13903a`.
- Fresh-main rebuild anchor: `93d3c7b969fb55c25944a5707a6c1f70b1168b71`.
- PR PASS 2 core: `36518539660`, job `109246150807`.
- PR backlog dispositions: `36518539741`.
- PR package purchase value: `36518539636`.
- Post-merge PASS 2 core: `36518618397`.
- Post-merge backlog dispositions: `36518618404`.
- Post-merge full visual build: `36518618313`, build job `109246437198` — blocked by meaningful-Russian gate.
- Post-merge deploy attempts: `36518618351` cancelled; `36518623279` skipped; `36518660075` skipped.

## 16. Efficiency / reusable lesson

Two reusable operational lessons were confirmed:
1. A recent-commit search is not a safe substitute for reading the explicit `main` branch ref before creating/rebasing a worker branch. The branch endpoint/ref must be the authoritative HEAD check.
2. When concurrent production workers continuously move `main`, fresh-main reconciliation should compare the changed paths. If drift is confined to unrelated production state and GitHub reports the PR mergeable, repeatedly rebuilding the worker branch after every independent data commit only creates churn.

The task route itself was already documented: browser-local queue/view overrides live in `web/app.js`; no broad repository rediscovery was needed after `PROJECT_ROUTES.md` was consulted.
