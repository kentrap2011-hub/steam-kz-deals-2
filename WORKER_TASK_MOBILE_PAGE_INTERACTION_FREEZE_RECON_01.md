# WORKER TASK — MOBILE PAGE CONTENT MISSING RECON 01

Task ID: `mobile-page-interaction-freeze-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`

## Corrected user-visible incident

User clarified the 2026-09-03 production incident with a real-device screenshot.

The page UI itself remains interactive:
- top navigation/tab buttons respond;
- search/button controls are present and clickable;
- this is **not** a general pointer/click freeze.

The defect is that the main game content/list is absent after normal load or refresh. The screenshot shows the page shell, navigation and swipe hint, but no game card/content where the feed should be.

Observed lifecycle symptom:
- after normal page load / refresh, the page shell renders but game content is missing;
- switching to another app and returning causes the content to appear/work temporarily;
- after another refresh/reload, content is missing again.

This is a current production usability incident and is higher priority than ordinary backlog work. Do not assume it is caused by current visual-freshness branch work unless evidence proves that.

## Goal

Localize the earliest failure in the production data-load/render lifecycle that explains:

`cold load / refresh -> shell rendered + controls interactive + feed content absent`

followed by:

`app background/foreground resume -> content becomes visible/loaded`.

Define the smallest safe fix contract. Diagnosis only; do not implement yet.

## Read first

Use only the smallest relevant current refs needed, including:
- current production web entry files under `web/`;
- browser-side JavaScript that fetches/loads `web/data/current.json` or equivalent canonical payload and renders the main feed/cards;
- current tab/view initialization and feed filtering code;
- visibility/pageshow/focus/resume lifecycle hooks;
- service-worker/PWA/cache code if present;
- the smallest current production payload metadata needed to determine whether data exists but is not rendered;
- `DIRECTOR_TASK_BOARD.md` only for task context.

Do not perform broad Git-history archaeology.

## Required investigation

Test the corrected symptom against these bounded failure classes, without assuming one in advance:

1. **Initial data fetch/load does not complete or is discarded**
   - fetch promise/retry/race problem;
   - wrong cache mode/versioned URL;
   - payload parse/validation path aborts rendering;
   - initial request fails but a later lifecycle event retries it.

2. **Data exists in memory but first render/filter produces zero visible cards**
   - initial selected tab/view/filter state is wrong or stale;
   - render runs before state/data is ready and is not rerun until visibility/focus/pageshow;
   - empty result is treated as final instead of pending/degraded.

3. **Lifecycle hook performs the missing second render/load**
   - `visibilitychange`, `pageshow`, focus, resize or resume causes fetch/render that cold load failed to perform;
   - identify the exact function/path that app-switch return triggers.

4. **Service-worker/cache asset/data mismatch**
   - HTML/JS/current.json versions are inconsistent after refresh;
   - stale cached payload or asset mismatch makes first render fail/empty;
   - resume causes network/cache revalidation that repairs the view.

5. **Runtime exception / rejected initialization path after shell render**
   - shell/navigation listeners attach, but feed load/render path throws or exits early;
   - identify exact earliest failing call/condition.

6. **Canonical production payload is actually empty/incompatible**
   - distinguish frontend render failure from genuinely empty current payload;
   - if payload is non-empty but UI shows none, prove that boundary explicitly.

The screenshot/user evidence should be treated as real-device evidence that controls remain interactive while content is absent.

If exact device/browser reproduction is unavailable, classify findings as `proven`, `strongly_supported`, or `hypothesis` and do not overclaim.

## Important boundaries

Do NOT:
- change production code;
- redesign UI;
- modify ranking/Taste/data semantics;
- merge/release the separate visual-freshness branch;
- blame the visual-freshness work without evidence;
- create a second frontend/data-loading path;
- perform broad unrelated refactors;
- ask user for developer-console logs unless code/current-payload evidence cannot localize a bounded next step.

## Required result

Report exactly:
1. `Incident reproduced/localized`: `yes | partial | no`
2. Is current production payload itself non-empty/usable: `yes | no | cannot_determine`
3. Earliest failing data-load/render lifecycle step.
4. Evidence classification: `proven | strongly_supported | hypothesis`.
5. Why app-switch/background->foreground return restores content temporarily.
6. Why refresh/reload returns to shell-without-content state.
7. Smallest fix surface, maximum 3 files/components.
8. Whether an `IMPLEMENT` task is ready now.
9. Real-device verification required after fix: `yes`.
10. One recommended next step only.

Status exactly one:
- `complete`
- `needs_fix`
- `blocked`
- `needs_user_evidence`

## Completion

Save:
`reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`

Final answer must state exact report path, status and exact refs.