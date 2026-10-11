# Worker report — dismiss feed freshness popover outside its bounds

- Worker: **НОВЫЙ ЧАТ — ЧАТ 2**.
- Task: `WORKER_TASK_SITE_FEED_SYNC_POPOVER_OUTSIDE_DISMISS_FIX_01.md`, ID `site-feed-sync-popover-outside-dismiss-01`.
- Base/source of truth: `main`; branch `fix/site-feed-sync-popover-outside-dismiss-01`; [PR #203](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/203), **OPEN / NOT MERGED**.
- Implementation CI head: `997a0d2df3bba80045aeb9bcc62b6a328763d762`.

## Diagnosis and architecture preflight

- Confirmed cause: `web/feed-bootstrap.js` bound only the small `#feedStatusToggle` click and Escape handlers; it had no document-level outside-click dismissal. Tapping cards, tabs or blank space left `#feedSyncDetails` open.
- This is a narrow browser UI interaction. Under `config/execution_ownership_contract.json` and `CHAT_CONTEXT.md`, GitHub continues to own semantic scope/Deep freshness/publication, while the browser may show/hide read-only presentation. No producer state, queue/retry/checkpoint manager, new scheduled run or delegated control-plane authority was added. No conflicting shared `CURRENT_TASK.md` write was made while parallel workers remain active.

## Exact changes

1. `web/feed-bootstrap.js`: one controller-owned, bubbling document `click` listener dismisses expanded details only when the target is **outside both** `#feedSyncDetails` and `#feedStatusToggle`. Native browser `click` covers Android tap, mouse and keyboard-activated buttons; testing the event target also prevents an opener click from immediately dismissing the panel. No `preventDefault`, `stopPropagation` or overlay is used.
2. All open/close paths share `setStatusDetailsExpanded` to keep state, `aria-expanded` and `.hidden` synchronized. Escape still restores focus. `destroy()` removes the document listener and closes an open panel; `install()` is idempotent and reinstall registers exactly one new handler.
3. `web/site-deep-status-browser-feed-refresh.test.js`: existing **actual `app.js` + `feed-bootstrap.js`** synthetic browser has realistic multiple document listeners and event bubbling; checks opener and nested icon, inside text/retry, touch-generated outside clicks (blank/card), tab and Statistics navigation on the **same** click, manual queue preservation, toggle, Escape/focus and install/destroy/reinstall lifecycle. Preserves existing Deep, retry/cache, queue and stale-verification assertions.
4. `web/index.html`: bootstrap JS asset URL advanced to `feed-bootstrap.js?v=popover-outside-dismiss-01` for persistent Android browser fetching; compact CSS URL and 44px target remain unchanged.
5. `.github/workflows/validate-browser-deep-feed-refresh.yml`: only the related PR-only static JS asset-version assertion was advanced.

No changes to `web/app.js`, `web/feed-sync.css`, saved user data or Cache Storage; no worker actions on semantic Fast/Dossier/Deep, site deployment, production data, CI scheduling, Scheduled Tasks or automations.

## Isolated tests / evidence

- **PASS:** [Validate browser Deep feed refresh, PR-only #38138807967](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38138807967), on implementation head `997a0d2`. This executes JS syntax checks, the real bootstrap/app synthetic browser, cache identity, manual-end/Deep queue and Progressive indicator/statistics regressions, and the static HTML asset/accessibility assertion.
- **PASS:** [Deep site mirror UI #38138807974](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38138807974).
- **PASS:** [Site task registry and page #38138807958](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38138807958).
- **PASS:** [Package purchase value #38138807962](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38138807962).
- **At report authoring:** [Progressive PASS 2 core #38138807966](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38138807966) was still in progress; verify final status before Director acceptance. This worker did not change Deep/PASS 2.
- No Android physical-device testing, merge, deployment or real user acceptance is asserted.

## Post-merge Android browser acceptance

After Director merges and normal site deployment, open the site in the **ordinary existing Android browser** without clearing data. Tap the small freshness icon beside the update time, then tap blank area, game card and a navigation tab: details must close on each outside tap, and card/tab interactions must still work. Reopen: text/retry must remain usable; tapping the icon again closes. Confirm Strange Horticulture's Deep marker and saved liked/final/seen/manual-end/urgency queue remain unchanged. Any observed device-specific problem requires a separate report, not guessed cache clearing.

**Status:** implementation + bounded PR-only browser validation complete; PR unmerged, device acceptance pending.
