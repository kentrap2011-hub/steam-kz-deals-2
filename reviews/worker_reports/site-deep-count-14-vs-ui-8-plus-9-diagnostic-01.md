# Worker report B — site Deep 14 vs ordinary browser 8+9

**Worker:** НОВЫЙ ЧАТ — ЧАТ 2  
**Task:** `WORKER_TASK_DOSSIER_SHADOW_TRIAL_PLAN_AND_SITE_DEEP_COUNT_QA_01.md`  
**Status:** `producer_reconciled_browser_local_cause_not_yet_observed`  
**Authorization:** bounded read-only diagnosis; **NO UI/production fix in this PR**.

## Confirmed observations and exact denominators

The user directly reproduced a **browser-mode difference**: ordinary profile shows 8 Deep-analyzed games followed by 9 without; incognito shows all 14 Deep suitable at that moment. Treat the difference as real observation, **not** proof that 6 cards disappeared from producer. The 17 cards the user inspected are a **viewed prefix/subset**, whereas Statistics' 14 is an aggregate for all 303 current semantic candidates.

| Source/time (UTC 2026-10-11) | Universe | Deep-fit | Deep-not-fit | Deep unresolved | Other |
| --- | ---: | ---: | ---: | ---: | ---: |
| Historical canonical final visual at commit `9fd39494dfb8`, 09:22:20 | 297 **published cards**, derived from 303 Deep-coverage candidates | **14** (all 14 materialized as `completed/fit`) | 6, excluded from cards by producer | 2 | 281 pending/not-analyzed card rows |
| Independent `data/production/site/current_status.json`, generated 09:45:56 | **303** coverage candidates | **18** | **7** | **2** | 276 waiting/eligible |
| Frozen PR base `6bdd2a26f408d52eb533e1ef2135347f11956f57`, final visual generated 09:49:02 | **296** published cards | **18** (all 18 `completed/fit`) | **7**, excluded | **2** | 276 (`waiting_for_dossier=186`, `eligible_or_pending=90`) |

Arithmetic: at 09:22, `303 - 6 not_fit = 297`; `14 fit + 2 unresolved + 281 other = 297`. At 09:49, `303 - 7 not_fit = 296`; `18 fit + 2 unresolved + 276 other = 296`. The later 18 is **new progress**, not a contradiction of the earlier 14 or evidence of UI loss. `deep_completed_not_fit_count` is **not** a list of visible negative-fit cards; the producer does not publish them into the offer feed. No card is "lost" when reconciling global statistics to the final visual by these counters.

**Conclusion proved from canonical snapshots:** producer carried **all 14 of 14** at the 09:22 comparison and **all 18 of 18** at 09:49. There is no producer/visual omission of the six historical Deep-fit cards. The user-local ordinary-profile difference requires per-browser-state diagnostics to distinguish ordering from stale cache. The web tool could not retrieve the live GitHub Pages page/status in this environment; do **not** claim an independent live HTTP or ordinary-profile proof. Deployment workflow stages `data/production/visual/current.json` as `web/data/current.json`, which is a generated Pages artifact, **not** a committed `web/data/current.json` in main.

## UI path and cause candidates, narrowed by actual code

**Exact route:** `data/production/site/current_status.json` → Pages `data/status.json` → `web/app.js::renderStatisticsView` (usually status preferred); separately producer `data/production/visual/current.json` → `.github/workflows/deploy-visual.yml` stages `web/data/current.json` → `web/feed-bootstrap.js`/ `web/app.js::init` → `syncActiveSaleItems` → `buildQueue` → `renderFeed`.

1. **Leading, deterministic local-state explanation: "В конец очереди".** `localStorage['steam-deals-visual-state-v1']` contains `games[id].manual_end_at` and persistent `queue.ids/cursor`; `canonicalQueueIds()` places **every manually deferred card after every non-manually deferred card regardless of Deep score/stage**. `QUEUE_VERSION=6` does not clear `manual_end_at`, and an incognito profile has no such flags. If **six of the 14** Deep-fit games were previously moved to the end, ordinary-profile order becomes exactly **8 Deep fit → non-Deep cards (including at least nine) → six deferred Deep fit at the absolute tail**, while incognito starts with all 14 Deep-fit in canonical rank order. This is a deterministic **mechanism reproducing the observed prefix**, but **six actual flags are not yet proven on the user's device**.
2. **Distinct possible stale-payload mechanism:** `web/feed-bootstrap.js` explicitly returns an old known-good payload from browser **Cache Storage** `steam-deals-feed-lkg-v1` first and triggers background `fetch` refresh, with 9-second bounded request timeout/retry. If refresh fails, ordinary mode may continue showing an older list while `STATUS_URL` (fetched separately, `cache:'no-store'`) shows newer global counts. Incognito starts with empty Cache Storage and fetches current content. This is a legitimate site-client freshness risk, *not proven* as the user's actual cause. Inspect `window.FeedBootstrapResilience.state.source/currentIdentity/refreshOutcome` and `[feed-bootstrap]` logs before attributing a cache failure.
3. **Explicitly ruled out as sufficient explanation:** `urgency_first` reorders only **within** producer ranking stage and cannot put a non-Deep card above still-automatic Deep-fit; `liked`/`final` statuses do **not** remove a card from feed; saved queue gets all active IDs restored/reconciled; search result truncation (50/30) affects search only; no generic hidden-game toggle is present. `filterActiveSaleItems` removes known-expired discounts, but every Deep-fit card in the 09:49 snapshot has a `sale_end_utc` after 2026-10-11 (earliest 15 Oct) and the producer reports `expired_family_count_removed_at_build=0`; expiry cannot account for these particular six at that reference time.
4. **Service Worker:** no registration is present in the current `web/index.html`, `web/app.js` or `web/feed-bootstrap.js` path; the observed Cache Storage fallback works **without** a Service Worker. It is not possible to rule out a *legacy registered* worker within the user's persistent browser profile without inspecting `navigator.serviceWorker.getRegistrations()`. Treat that as a separate device check, not a proven cause.

The relevant asset URLs in `web/index.html` use versioned JS file querystrings; `app.js` requests current and status with `cache:'no-store'`, but the bootstrap wraps `window.fetch` and may still serve saved known-good content. Normal vs private mode, by itself, is **not** enough to uniquely distinguish six `manual_end_at` flags from stale feed content/legacy SW.

## Reproduction evidence (isolated, synthetic, no live mutation)

Proposed PR-only test `web/site-deep-count-queue.test.js` runs actual `web/app.js::buildQueue()`/canonical order in a synthetic, in-memory DOM/localStorage with exact-category fake items:
- fresh incognito-like state: 14 `deep_fit` appear before 9 `not_analyzed`;
- six `manual_end_at` flags in ordinary-like localStorage: first 8 `deep_fit`, then 9 `not_analyzed`, last six Deep-fit; 23 items remain present;
- `liked`, `final`, `seen` and `urgency_first` remain untouched; no producer, browser Cache Storage, network, GitHub runtime or Scheduler is mutated.

**What this proves:** code-path capability and denominator mismatch. **What it cannot prove:** user's precise localStorage flags, actual deployed JS build/cache refresh state, or which six Deep games were deferred. Do not conflate a reproducible mechanism with device forensic evidence.

## Six-candidate appendix — unproven until user's local view is bound to GitHub data

Historical 09:22 snapshot contained 14 positive Deep cards. The *identities* of the six not in the user's first 17 visible cards **cannot be deduced** merely from the counts 8+9; in particular they need not be ranks 9–14 if one or more top-ranked cards had been deferred. The evidence permits only the following accounting, not invented six names:

| Candidate slot | Status |
| --- | --- |
| 1–6 (six possible omitted-from-prefix Deep-fit IDs) | `not_identified; exact local queue/manual_end_at/loaded payload needed` |
| Sum | `14 producer fit - 8 observed in front = 6 not observed in viewed prefix`; **not proof they are absent from queue** |

To identify them, compare **exact page-loaded data** `data.items[]` Deep-fit IDs with visible first-17 queue IDs and `games[id].manual_end_at`. If all six appear at the end, explanation is definitively manual queue ordering; if six are absent from the *loaded* payload, check bootstrap Cache Storage/deployment and loaded `generated_at_utc`; if in the loaded payload but not in `queue.ids`, this is a distinct queue reconciliation defect.

## Minimal read-only operator evidence requested

At the **same time, on the same device**, before deleting anything:
1. Screenshot ordinary **Лента** showing 8th Deep and 9th following non-Deep and the total `Лента (N)`; screenshot top header **Данные: ...** and `Срочные` state. Capture those two card titles/positions. Screenshot same in incognito; specify whether "8+9" means 17 fully browsed cards or total queue length.
2. Browser console on ordinary profile: collect `data.generated_at_utc`, `data.items.length`, `data.items.filter(g=>g.deep_stage_state==='completed'&&g.deep_stage_outcome==='fit').map(g=>g.id)`, `state.queue.ids.slice(0,20)`, `state.queue.ids.length`, and `Object.entries(state.games).filter(([,v])=>v.manual_end_at).map(([id])=>id)` (the `data` and `state` variables are page JS globals for the console context). Do not copy all stored state; only IDs, counters and timestamps are needed.
3. Browser console: `window.FeedBootstrapResilience?.state` (`source`, `refreshOutcome`, `currentIdentity`); check console `[feed-bootstrap] cache-hit / refresh-identical / refresh-failed / refresh-apply` events; optionally `navigator.serviceWorker?.getRegistrations().then(x=>x.map(r=>r.scope))`. These are read-only, preserve all user preferences.

If mobile browser DevTools are unavailable, the screenshots/header times/total count plus exact six game titles shown via site search and whether **"В конец очереди"** was used are the minimal substitute, but cannot definitively certify the localStorage cause.

## Decision and safe correction (REQUIRES SEPARATE AUTHORIZATION)

- **If manual queue ordering verified:** behavior follows current intentional `manual_end_at` override, *no missing Deep verdicts*. Recommend explicitly showing "Отложено в конец: N (Deep: M)" and a separately confirmed **"Вернуть обычный порядок"** command that deletes **only** `manual_end_at` for the selected/all deferred items and rebuilds `state.queue.ids`; **keep** `status liked/final`, `seen`, `first_source`, `urgency_first` and unrelated browser storage. Never suggest `localStorage.clear()` or "clear site data".
- **If stale last-known-good verified:** retain offline fallback but visually label `source=cache` and `generated_at_utc`, surface a non-destructive "Проверить свежие данные" action with observable refresh/error; inspect bounded fetch timeout, identity and reload behavior in PR-only synthetic tests. Do not clear all caches or user settings.
- **If JS/deployment mismatch verified:** separately authorize a minimal test+asset cache-version/deploy correction only after extracting exact deployed and loaded hashes and Page publication run; do not trigger semantic work or production recomputation.

**No production UI update in this PR, no Scheduled Tasks, no semantic run and no current GitHub Deep/Dossier state mutation.** The separate Dossier quality plan is `dossier-shadow-trial-prospective-plan-01.md`. The next decision is **read-only device evidence**, then one precise follow-up corrective task only if necessary.
