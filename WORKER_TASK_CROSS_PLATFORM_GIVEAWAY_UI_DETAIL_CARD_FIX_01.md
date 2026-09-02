# WORKER TASK — CHAT 1

Task ID: `cross-platform-giveaway-ui-detail-card-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/cross-platform-giveaway-ui-detail-card-fix-01.md`

## Context

This is the direct continuation of failed real-device acceptance for `cross-platform-giveaway-ui-ux-fix-01`.

Phone screenshot confirmed:
- the collapsed top-level control is an improvement;
- after expanding, each giveaway row still renders a large analysis block inline;
- this makes the expanded list too tall and visually heavy;
- user wants the expanded list to remain compact;
- description / pros / cons must live in a **separate per-game detail card**, opened only for the selected game.

Do not repeat giveaway source recon, identity preflight, or the previous UX investigation.

## Goal

Split giveaway UI into two interaction levels:

1. **Compact giveaway list** — quick overview only.
2. **Separate game detail card** — description/pros/cons and analysis state for one selected game.

## Required behavior

### A. Top-level giveaway control

Keep the current collapsed-by-default top-level control.

On expand, show a compact list only.

### B. Compact expanded list

Each giveaway row should remain small and scan-friendly.

Show only fields needed for quick action/navigation, for example:
- game title;
- storefront;
- deadline / time remaining;
- compact `Забрать` CTA;
- compact `Подробнее` / row-tap affordance for opening the detail card.

Do NOT render inline in the list:
- long incomplete-analysis explanations;
- description body;
- pros body;
- cons body;
- repeated identity warning paragraphs.

The expanded list should fit multiple giveaway rows on a mobile viewport without turning into a long article.

### C. Separate per-game detail card

Opening one giveaway game should show a separate detail surface for that game only.

Use the smallest UI pattern consistent with the existing mobile site, such as:
- modal / sheet;
- dedicated overlay card;
- or another existing one-at-a-time detail pattern.

Do not create a second page/data fetch unless the existing UI architecture already has a canonical route for it. Prefer the current single visual payload and in-page state.

Detail card should contain:
- title;
- store / deadline / claim CTA;
- `Описание`;
- `Плюсы`;
- `Минусы`;
- close/back control.

Only one giveaway detail card should be open at a time.

### D. Analysis state

The previous task already proved there is no safe current Epic/GOG -> Steam analysis identity binding.

Do not redo that recon and do not map by title.

Until a safe canonical analysis identity exists:
- the separate detail card may show the honest incomplete-analysis state;
- but keep it concise and contained inside the detail card;
- do not repeat long cross-store identity explanations under every item in the compact list.

Prefer concise copy such as `Анализ игры пока не готов: нет подтверждённой cross-store связи.` with description/pros/cons marked unavailable/incomplete, rather than multiple paragraphs repeating the same warning.

Do not fabricate description/pros/cons.

### E. Paid feed isolation

Opening/closing giveaway list or giveaway detail card must not mutate:
- paid swipe position;
- paid ranking;
- wishlist state;
- interesting/final state;
- current paid card state.

## Validation

Add deterministic regressions for:
- top-level giveaways collapsed on initial load;
- expanded giveaway list remains compact and contains no inline analysis bodies;
- every active giveaway has a detail affordance;
- selecting one game opens only that game's detail card;
- close/back returns to compact list without losing list state;
- switching between giveaway games shows the correct game detail;
- claim CTA remains correct in both compact/detail contexts if present;
- incomplete-analysis copy is contained in detail card only;
- no title-only/fuzzy Steam analysis is rendered;
- paid feed state remains unchanged;
- stale/expired/unavailable behavior remains fail-closed.

Then run the smallest canonical production visual/UI validation and Pages deploy needed for the changed web surface.

## Real-device acceptance — mandatory

After successful deploy, status must be `needs_user_verification`.

User verifies on phone:
1. collapsed top-level control is compact;
2. expanded list contains compact rows only;
3. tapping a game opens a separate detail card;
4. description/pros/cons/incomplete-analysis state are visible only in that detail card;
5. closing detail returns to the compact list;
6. paid feed remains intact.

Do not call complete before this check.

## Hard boundaries

Do NOT:
- redo giveaway source recon;
- redo cross-store identity recon;
- title/fuzzy-match Steam analysis;
- fabricate game analysis;
- add a second browser data source;
- change paid ranking/Taste logic;
- weaken freshness/expiry checks.

## Report format

Save:
`reviews/worker_reports/cross-platform-giveaway-ui-detail-card-fix-01.md`

### User acceptance defect
Exact mobile issue being fixed.

### Compact list
Exact rendered fields and interaction.

### Detail card
Exact interaction/content/state.

### Validation
Tests/build/deploy refs.

### User verification
Exact phone checks.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_verification`

### Recommended next step
One bounded next step only.