# WORKER TASK — MOBILE PAGE INTERACTION FREEZE RECON 01

Task ID: `mobile-page-interaction-freeze-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`

## User-visible incident

User reports on 2026-09-03 that the discounts page is currently badly broken on mobile:

- nothing opens/responds after page load;
- switching to another app and then returning makes the page work temporarily;
- after the first refresh/reload, interactions stop working again.

This is a current production usability incident and is higher priority than ordinary backlog work. Do not assume it is caused by current data freshness work unless evidence proves that.

## Goal

Localize the first concrete failure mechanism that can explain the exact lifecycle symptom above and define the smallest safe fix contract.

The task is diagnosis only. Do not implement a fix yet.

## Read first

Use only the smallest relevant current refs needed, including:
- current production web entry files under `web/`;
- current browser-side JavaScript that owns navigation, card opening, overlays/dialogs, refresh/reload or lifecycle handling;
- current service-worker/PWA/cache code if present;
- the smallest recent user-visible web/UI implementation refs needed to understand current ownership;
- `DIRECTOR_TASK_BOARD.md` only for current task context.

Do not perform broad Git-history archaeology.

## Required investigation

Test the symptom against likely classes of failure, but do not assume any one in advance:

1. **Invisible blocking layer / overlay / pointer interception**
   - stale modal/backdrop/skeleton/loading layer;
   - `pointer-events`, z-index, touch interception;
   - element left active after initial load or refresh.

2. **Event binding / hydration / initialization failure**
   - click/touch handlers not attached after cold load or reload;
   - handlers restored by `visibilitychange`, `pageshow`, focus/resume, or similar lifecycle event when returning from another app;
   - duplicate or aborted initialization.

3. **Mobile lifecycle / bfcache / visibility state**
   - page only becomes interactive after `visibilitychange`, `pageshow`, focus, resize or resume;
   - incorrect handling of `document.hidden`, frozen page state, bfcache, or Android browser lifecycle.

4. **Service worker / cache / stale asset mismatch**
   - HTML and JS from incompatible versions after refresh;
   - stale service-worker response or cache invalidation issue;
   - asset load failure that would explain why returning from another app changes behavior.

5. **Runtime exception / rejected initialization promise**
   - exact error path that prevents interactive setup while leaving page visually rendered.

Use current code and bounded reproduction/inspection evidence only. If the exact mobile browser/device cannot be reproduced, say so explicitly and distinguish `proven`, `strongly_supported`, and `hypothesis`.

## Important boundaries

Do NOT:
- change production code;
- redesign the UI;
- modify data/ranking/Taste semantics;
- merge/release the separate visual-freshness branch;
- blame the current visual-freshness work without evidence;
- create a second frontend/runtime path;
- perform broad unrelated refactors;
- require the user to collect developer-console logs unless the code evidence is genuinely insufficient to localize the next bounded step.

## Required result

Report exactly:

1. `Incident reproduced/localized`: `yes | partial | no`
2. First failing mechanism / earliest broken lifecycle step.
3. Evidence classification: `proven | strongly_supported | hypothesis`.
4. Why switching away and returning temporarily restores interaction.
5. Why refresh/reload causes the broken state again.
6. Smallest fix surface, maximum 3 files/components.
7. Whether an `IMPLEMENT` task is ready now.
8. Whether a user real-device verification will be required after fix (`yes` expected for this UI incident unless clearly impossible).
9. One recommended next step only.

Status exactly one:
- `complete`
- `needs_fix`
- `blocked`
- `needs_user_evidence`

## Completion

Save:
`reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`

Final answer must state exact report path, status and exact refs.