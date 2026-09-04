# WORKER TASK — TOP SUMMARY FILTER BUTTONS RECON 01

Task ID: `top-summary-filter-buttons-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/top-summary-filter-buttons-recon-01.md`

## User request

The queued UX goal is already defined in:
`WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.

User wants the four top summary cards to become clickable controls using the existing filter state:
- `Новые`
- `Не смотрел`
- `Интересно`
- `Видел`

After top `Интересно` fully replaces the existing lower `Интересно` control, the lower duplicate should be removed.

## Why this task is recon-only now

The giveaway live-site cache incident is still awaiting recovery acceptance and real-device verification. Do not mix another frontend implementation into that production acceptance window.

## Goal

Map the smallest exact implementation for the queued top-summary-filter UX without changing code yet.

## Required checks

1. Exact files/components that render the four top summary cards.
2. Exact existing single source of truth for filter/view state.
3. Which current control/action each card should reuse rather than creating new parallel state.
4. Exact lower `Интересно` control that becomes redundant.
5. Any accessibility/keyboard/tap semantics needed when turning summary cards into interactive controls.
6. Existing focused tests that can be extended, or the smallest regression tests required.
7. Potential conflict surface with `web/feed-bootstrap.js` / current giveaway cache fix. Confirm whether implementation can safely proceed after giveaway acceptance.
8. One bounded IMPLEMENT plan only.

## Boundaries

Do NOT change code, CSS, markup, tests, or production files in this task.
Do NOT touch giveaway data/cache behavior, semantic/Taste/ranking, ITAD/IGDB, or mobile data ownership.
Do not redesign the page.

## Done when

Save:
`reviews/worker_reports/top-summary-filter-buttons-recon-01.md`

Include:
1. Task
2. Current UI/state mapping
3. Exact files
4. Reuse plan
5. Duplicate control removal plan
6. Test plan
7. Conflict assessment
8. One bounded next IMPLEMENT
9. Status
10. Exact refs

Status exactly one:
- `complete`
- `blocked`
- `needs_user_decision`
