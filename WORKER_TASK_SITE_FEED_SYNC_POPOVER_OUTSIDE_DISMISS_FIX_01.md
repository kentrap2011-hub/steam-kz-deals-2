# WORKER TASK — dismiss compact freshness-details popover on outside tap

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth / base: `main`
Physical worker: **НОВЫЙ ЧАТ — ЧАТ 2**
Task ID: `site-feed-sync-popover-outside-dismiss-01`
Authorization: **bounded site frontend interaction bug fix with isolated PR-only tests**. Never modify production data or Scheduled Tasks.

## Real user acceptance feedback
After PR #199 merged/deployed the small freshness icon and its diagnostic popover are visibly much better. User's Android screenshot (2026-10-11, ~16:06) shows the expanded details panel over the feed after tapping the status icon. **The panel does not reliably close when tapping an empty area outside it**, making it obstruct cards and navigation. The user expects usual tap-outside dismissal without a second precise tap on the tiny icon.

Director confirmed in current `main` that `web/feed-bootstrap.js` binds `feedStatusToggle.click` and Escape keydown to the popover, but **no document-level outside-click/pointer handler exists**. This is the concrete missing behavior. Do not invent a data-freshness/caching issue; PR #199's truthful freshness semantics and Deep refresh already work.

## START
Fully read latest `CHAT_PROTOCOL.md` from `main` and execute START gate, then `CHAT_CONTEXT.md`, this exact task, relevant site route of `PROJECT_ROUTES.md`, PR #199 worker report `reviews/worker_reports/site-feed-sync-compact-freshness-ux-01.md`, `web/feed-bootstrap.js`, `web/index.html`, `web/feed-sync.css`, current synthetic browser tests and PR-only CI. Only specified repository.

## Required narrow correction and acceptance
- When the `#feedSyncDetails` popover is expanded, **a tap/click anywhere outside `#feedSyncDetails` and `#feedStatusToggle` must dismiss it immediately**, including empty background, game card and navigation tabs. Inside taps (reading text, clicking `Повторить проверку ленты`) must not dismiss it accidentally. Tapping toggle again closes as before; Escape closes with focus restored; keyboard navigation and accessibility (`aria-expanded`, hidden state, role/live text) remain synchronized.
- Mobile touch must behave reliably. Avoid opening-then-immediately-closing because the opener event also bubbles to document. Do **not** place an opaque overlay over cards, block normal navigation or intercept outside interactions; the same tap should reach its natural underlying target.
- If a view/tab/navigation event naturally changes the UI, the popover must not stay visually stranded or block the next view. Prefer minimal event handling over broad rerender changes. Ensure document listener is registered only once per controller and **removed by `destroy()`**; no leaks or duplicate listeners after lifecycle/reinit.
- Preserve original PR #196/#199 safeguards: cached vs network verified accuracy, bounded refresh/retry and Android resume, Deep indicator updates (e.g. Strange Horticulture), cached-feed downgrade rejection, 44px tap target, small non-layout-blocking floating details, no permanent full-width bar, no user queue/reset/seen/liked/final/urgency/manual-end/Cache Storage change. No JS schema or producer mutation.
- Extend *existing synthetic actual bootstrap/app* browser regression with deterministic touch/click outside, opener click, inside text/button, re-click toggle, Escape, view/tab click, saved queue after dismissal, repeat install/destroy and no click interception. Update versioned `feed-bootstrap.js` asset in `web/index.html` if code changes so Android persistent browser fetches it. Run existing browser Deep/cache identity/regression suites in PR-only CI.
- Report exact cause, targeted change, passing tests, and a short verification step in the ordinary Android browser; do not claim actual-device validation until user sees it.

## Boundaries/deliverables
Small worker branch + PR (**DO NOT MERGE**), report `reviews/worker_reports/site-feed-sync-popover-outside-dismiss-01.md`. Prefer edits only `web/feed-bootstrap.js`, existing `web/site-deep-status-browser-feed-refresh.test.js`, `web/index.html`, and test workflow only if essential. Do not touch Chat 1 Dossier files, Director plan, semantic/production/cache data, site publication pipeline, Scheduled Tasks, any automation, deployment, other repo or `manual-shell-write.yml`.
