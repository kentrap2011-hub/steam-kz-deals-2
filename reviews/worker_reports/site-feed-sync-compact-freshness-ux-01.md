# Worker report — compact, truthful site feed freshness (Chat 2)

- Task: `WORKER_TASK_SITE_FEED_SYNC_COMPACT_FRESHNESS_UX_FIX_01.md`, ID `site-feed-sync-compact-freshness-ux-01`.
- Source of truth: `main`; bounded branch `fix/site-feed-sync-compact-freshness-ux-01`; [PR #199](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/199); PR-only work; **not merged**.
- Authorization: read-only website bootstrap/UI and isolated PR regression. No scheduled tasks, production data, data writers, canonical Deep/Dossier/ranking, deployment, user storage clearance or semantic work touched.

## Source and authority preflight

Read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, task file, targeted `PROJECT_ROUTES.md` site/publication route, PR #196 worker report, implementation, focused regression/workflow and `config/execution_ownership_contract.json`. GitHub owns semantic publication and authoritative snapshot/identity; browser displays prebuilt current feed, may read/retry network and preserve local state. This repair changes no control-plane/retry policy, recurring workflow or queue owner. Parallel worker in Chat 1 remains independent: do not overwrite shared `CURRENT_TASK.md`.

## Evidence, causal boundary and semantics

- **Observed (user Android screenshot, 2026-10-11):** after PR #196 was deployed, Strange Horticulture's Deep marker correctly lit at position #26. A multiline amber `feedSyncNotice` with long refresh button occupied the header. It reported an ostensibly stale feed just after its recorded producer generation minute.
- **Confirmed code cause:** PR #196 bootstrap had `freshnessNotice('stale')` on *every* failed background verification regardless of `generated_at_utc` age. Failure to reach the network is not proof of a newer version. The long card was mounted between header and navigation and always displayed a large refresh button.
- **Unproven device-specific cause:** the reason the user's Android normal profile originally kept old Deep data (local Cache Storage/SW/navigation/connection history) remains unproven without on-device inspection. This UI task must not assert it was a specific service worker/cache cause.

The site now distinguishes:
1. `network_verified`: initial fetch or refreshed identical/accepted-newer payload checked over network; records `lastVerifiedAt` separately from producer `generated_at_utc`.
2. `cached_unverified` / `checking`: last known good snapshot rendered quickly, verification not yet established.
3. `verification_failed`: online check failed; keeps last known good and states **not verified**, not "outdated"; only if producer timestamp is >36h old, includes a coarse age note based on daily publication cadence.
4. `confirmed_older_or_conflict`: a concrete network comparison finds older or same-time ambiguous content; rejects downgrade of Deep.
5. `no_feed`: no valid cached feed and network unavailable; accessible retry remains.

The independent discount time in `#freshness` remains the source mailing update, not network verification time. Independent `data/status.json` Statistics never certifies the cards.

## Android screenshot before / after expected footprint

| State | Before (observed screenshot) | After (expected rendering; not a device screenshot) |
| --- | --- | --- |
| Normal header | Full-width amber notice with multi-line explanation and large `Проверить свежие данные` button, pushing tabs/cards down by the notice height | Single compact icon adjacent to existing source timestamp; **no separate status row/card**; 44×44px invisible-to-layout tap target, initially closed |
| Recent cache + offline | "отметки Deep могут устареть" immediately after snapshot creation | Small amber `!` icon, tap reveals "Проверка сети не удалась. Это не означает, что лента устарела" and manual retry |
| Confirmed feed | Green full-row message + refresh button | Small subdued `✓` icon; details available only on demand |
| Older/conflict or empty outage | Permanent warning card | Small red `!` icon; tap expands diagnostic/retry popover **over** the tabs, never pushes game cards down |

The tap target has min 44×44px, buttons support Tab/Enter/Space natively and Escape closes details; `aria-expanded`, `aria-controls`, a separate polite live-region and accessible names announce relevant state changes. CSS keeps a responsive <=430px (including ~350px) max-width popover. This is implementation/static-contract evidence, **not** a measured Chrome/Android pixel screenshot.

## Regression and risk controls

The existing synthetic test still exercises real `web/app.js` queue/render and real `web/feed-bootstrap.js` against in-memory Cache Storage/localStorage. Added fresh (~1 min) saved snapshot failing twice without "old" allegation; producer snapshot >36h with coarse age note but still unverified; equal checked payload with separate verified timestamp; disclosure toggle and Escape; static mobile viewport, 44px hit target and no-flow overlay assertions. Existing tests cover updated/Deep-lit, older/ambiguous rejection **with actionable retry after either conflict**, malformed/corrupt cache, first-visit no-cache outage/manual retry, hidden→visible recovery, reused `init()`, separate Statistics and saved `manual_end_at`, liked/final/seen/cursor/urgency settings. Existing PR-only giveaway identity and Progressive indicator regressions kept.

`web/index.html` pins new `?v=compact-freshness-ux-01` values for both feed bootstrap JS and CSS to bust persistent-browser asset URLs. No `localStorage.clear()`, Cache Storage wipe, auto-refresh polling, SW unregister or production writes were introduced.

## Verification and release boundary

- Focused PR-only workflow: `.github/workflows/validate-browser-deep-feed-refresh.yml` (Node 22, synthetic, PR-only).
- **PASS** final code head `9079a4ad4fdc9f3b8bebdf455e54e4ab5f3b6017`: focused browser Deep/feed synthetic + syntax + accessibility + cache identity + manual queue + Progressive indicators, [run 38135825875](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38135825875), success.
- **PASS** other PR-only checks on same code head: site task registry `38135825884`, package purchase value `38135825872`, Deep site mirror `38135825887`, backlog dispositions `38135825899` — success; Progressive PASS 2 core `38135825876` — pending at report update (previous code head passed `38135656078`).
- A prior focused run failed only on an old test expectation for changed first-visit outage wording; corrected, rerun successful.
- No live browser/device measurement, Pages deployment, runtime freshness verification or user acceptance is claimed.
- PR must remain unmerged for Director acceptance. After merge/deploy, user can inspect regular Android browser without deleting any personal state: icon next to source timestamp, tap for details/retry, verify Strange Horticulture Deep and saved queue.

Task route: `web/feed-bootstrap.js` + `web/feed-sync.css` + `web/index.html` → `web/site-deep-status-browser-feed-refresh.test.js` → PR-only `validate-browser-deep-feed-refresh.yml`. Existing site/publication route in `PROJECT_ROUTES.md` otherwise unchanged.
