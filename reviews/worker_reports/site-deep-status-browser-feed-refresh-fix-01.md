# Worker report — browser Deep feed freshness and non-destructive recovery

- Task: `site-deep-status-persistent-cache-refresh-fix-01`
- Worker: **НОВЫЙ ЧАТ — ЧАТ 2**
- Base: `main`; branch: `fix/site-deep-status-browser-feed-refresh-01`
- Mode: site/bootstrap repair with synthetic PR-only regressions; no semantic execution, production state writes or Scheduled Tasks.

## Evidence and root cause

User observed **Strange Horticulture** (`game:1574580`) as #45 with an unlit Deep marker in the normal browser, and a lit Deep marker in incognito. The producer's independently confirmed snapshot had `deep_stage_state=completed`/`deep_stage_outcome=fit`; `web/progressive-personalization-ui.js::deepIndicator` directly maps that pair to the lit/positive symbol. A saved `manual_end_at` *can* explain position #45; it does not cause a missing marker for the same loaded object.

Concrete site-code defect: `web/feed-bootstrap.js` returns `steam-deals-feed-lkg-v1` Cache Storage first while independently refreshing network. Before this fix: (1) failed background refresh was **not exposed** to the user, and retry on visibility/reopen exited whenever the cached feed was already ready; (2) `refreshPromise` remained latched after a failure; (3) `bootstrapPromise` remained the **original cached response**, so ordinary `init()` re-entry could replay stale cards over an already refreshed display; (4) nonidentical payloads were applied without rejecting older producer timestamps; (5) independently fetched `data/status.json` could report newer counts while the stale feed appeared current; (6) refresh application failure could leave `refreshOutcome=pending` without actionable UI.

Those behaviors are reproducible in code and synthetic tests. **No forensic access exists to the user's normal Android browser**, its Cache Storage, localStorage, legacy Service Worker registrations, active page JS hashes, or connection history. Therefore this report does **not** claim that a particular local cache/worker is proven responsible.

## Repair and invariants

- `web/feed-bootstrap.js`: requires valid producer timestamp plus unique stable item IDs for accepting cache/network payloads; cache-first quick render preserved. Background verification compares complete payloads and timestamp, rejects older versions, rejects same-time Deep/material ambiguities fail-closed, and accepts the existing same-time giveaway-only republish when items are exactly identical. A fresh accepted render replaces the reusable response used by subsequent `init()` calls; background refresh failure remains retryable through explicit action and tab resume, each attempt remaining bounded by the existing two-attempt timeout. No cache-wide clear or SW uninstall.
- `web/index.html` + `web/feed-sync.css`: a compact `aria-live` notice identifies cached/checking/stale/older/current feed with the producer timestamp; visible keyboard-accessible `Проверить свежие данные` button refreshes **only** the feed, without wiping state; site JS and CSS use versioned URLs so a prior downloaded script is invalidated by asset key. Independent Statistics can still show more recent global counts, explicitly signposted when cache is stale.
- The app's `localStorage['steam-deals-visual-state-v1']`, `manual_end_at`, `seen`, `liked/final`, cursor and `urgency_first` are neither deleted nor reset; fresh `app.js::buildQueue` reconciles item state and retains explicit manual deferral. A manually postponed game may remain at #45, but its `deepIndicator` must update once network feed is accepted.
- Unchanged: `web/app.js` business logic, `web/progressive-personalization-ui.js` Deep indicator, GitHub producer/Deep/Dossier/Fast/ranking, `deploy-visual.yml`, status generation, Saved Tasks, live content and scheduler configuration.

## Isolated regression coverage

New `web/site-deep-status-browser-feed-refresh.test.js` exercises real bootstrap + app queue/render in synthetic DOM, fake Cache Storage and saved localStorage:
1. Older cached `game:1574580` unlit → newly published network Deep fit lit; preserved manual deferral, seen/final/liked, urgency preference and current cursor; re-entry `init()` cannot reintroduce old Deep state.
2. Cache-first failure exposes stale notice; direct refresh succeeds without data removal; mobile tab hidden→visible restores background check.
3. Newer cached producer cannot be downgraded by older network; malformed network payload is rejected until a valid retry; corrupt cached identity rejected.
4. Network-fresh first visit; independently newer Statistics do not certify a cached game as fresh.
5. Original `scripts/test_feed_bootstrap_cache_identity.js`, `web/site-deep-count-queue.test.js` and `web/progressive-personalization-ui.test.js` remain in the PR-only workflow. Asset version and refresh UI accessibility have a static guard.

CI workflow `.github/workflows/validate-browser-deep-feed-refresh.yml` is **pull_request only**, Node 22, isolated inputs. Initial report recorded before CI outcome; append verified test/check status after run.

## Immediate user-safe verification after merge and Pages deployment

1. Open the ordinary browser and reload site normally (no data erasure or storage reset). Read the `Лента` notice and its timestamp. If it says saved/stale/older, click **Проверить свежие данные** once and check the reported result.
2. Search **Strange Horticulture**, open that game in the feed and inspect the `◆` Deep indicator title. `completed/fit` must be lit after the page confirms a network-verified feed. It may still be around position #45 because of saved `В конец очереди`.
3. Confirm existing `Интересно`/`Финал`, seen progress, manual postponement and urgency setting remain. Compare the regular browser against incognito. If old indicator persists while notice states network verified, capture the notice timestamp, visible card and browser console `FeedBootstrapResilience.state`, and check whether a legacy Service Worker still controls the persistent profile; this is a separate device evidence boundary.

No `localStorage.clear()`, Cache Storage mass deletion, SW unregistration, forced reordering or production writes are required.
