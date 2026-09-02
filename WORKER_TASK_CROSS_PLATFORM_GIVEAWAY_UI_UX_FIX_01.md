# WORKER TASK — CHAT 1

Task ID: `cross-platform-giveaway-ui-ux-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/cross-platform-giveaway-ui-ux-fix-01.md`

## Context

Real-device verification of `cross-platform-giveaway-ui-01` failed on UX/content completeness.

Observed on phone:
- the separate giveaway block is present and technically works;
- however it is too tall and permanently consumes a large part of the screen;
- each giveaway currently shows only title/store/deadline/CTA, which is not enough for the user to decide whether the game is worth claiming.

User requirements from real-device acceptance:
1. the giveaway surface must be hidden behind a compact button/summary by default;
2. tapping it expands/collapses the giveaway block;
3. each giveaway game should show useful game information similar in spirit to normal cards: at minimum a description plus concrete pros and cons;
4. do not invent or weakly match cross-store identity to obtain those fields.

Do not repeat source discovery or giveaway classification.

## Read first

- `reviews/worker_reports/cross-platform-giveaway-ui-01.md`
- `reviews/worker_reports/cross-platform-giveaway-ui-recon-01.md`
- current giveaway visual payload/handoff files
- current `web/giveaway-ui.js`, `web/giveaway-ui.css`, relevant `web/index.html` / `web/app.js`
- current canonical normal-card description/positive/negative fields and their owning producer only as needed
- current canonical identity artifacts only as needed to determine whether a giveaway game can safely bind to existing game-analysis data
- relevant `PROJECT_ROUTES.md` and `KNOWN_WORKER_PITFALLS.md` only if directly triggered

Do not perform broad history archaeology.

## Part A — compact collapsed UI (required implementation)

Replace the permanently expanded large giveaway panel with a compact, always-visible summary control.

Required behavior:
- default state on page load: collapsed;
- compact control clearly communicates that giveaways exist, e.g. `🎁 Бесплатные раздачи (2)`; wording may be adjusted to fit existing UI style;
- tapping toggles expanded/collapsed state;
- collapsed state must not reserve the current large vertical area;
- active/unavailable/empty semantics remain truthful;
- paid feed remains immediately reachable below;
- do not make the control so subtle that time-limited giveaways become easy to miss;
- no changes to paid swipe/ranking/final/wishlist behavior.

Add behavioral/mobile regressions for collapsed default, expand, collapse, and paid-feed non-mutation.

## Part B — description + pros + cons per giveaway

The expanded giveaway view must provide enough information to decide whether the game is interesting.

Target presentation per giveaway game:
- title;
- store(s), deadline(s), claim CTA(s);
- concise Russian description;
- `Плюсы` / `Почему может зайти` style content;
- `Минусы` / `Риски` style content;
- clear incomplete state if analysis data is genuinely unavailable.

### Identity/evidence preflight — mandatory

Before binding any existing analysis data to an Epic/GOG giveaway, prove an exact canonical identity relationship.

Allowed:
- exact existing canonical cross-store/game identity mapping;
- exact already-owned canonical metadata binding that unambiguously points to the same game.

Forbidden:
- normalized-title-only matching;
- fuzzy title/publisher matching presented as certainty;
- copying Steam analysis merely because names look the same;
- fabricating pros/cons to fill the card.

### If safe existing analysis is available

Reuse canonical existing description/positive/negative evidence through the single visual payload. Do not introduce browser-side source fetches.

Preserve provenance semantics:
- grounded positive/negative only;
- no generic `passed taste filter` praise;
- no `no downside found` filler;
- if the normal-card analysis marks a field incomplete, preserve that truthfully.

### If safe existing analysis is NOT available

Do not fake it and do not silently omit the requirement.

In the same task:
1. identify the smallest canonical producer/contract gap;
2. implement only if the existing ownership/source architecture already supports a generic bounded enrichment route without a new scheduler or unsafe matching;
3. otherwise stop that subpart as `blocked`/`needs_fix` with one exact next-step task recommendation.

Part A should still be completed and validated even if Part B encounters a genuine architecture blocker.

## Payload / ownership constraints

Keep the existing single route:

`data/production/giveaways/v1/current.json`
→ canonical visual producer/handoff
→ `data/production/visual/current.json`
→ existing Pages deploy
→ `web/data/current.json`
→ web renderer.

Do NOT add:
- a second browser fetch;
- a second scheduler;
- a chat-owned production queue;
- manual per-giveaway curation;
- a title-only cross-store identity table.

## Validation

Required deterministic checks:
- collapsed by default on mobile;
- compact button shows current giveaway count/state without large reserved space;
- expand/collapse works repeatedly;
- active offers retain correct CTA/deadline;
- stale/unavailable/expired fail-closed behavior still works;
- paid feed state remains untouched;
- if description/pros/cons are emitted, each row has exact proven identity provenance to the reused analysis source;
- no fuzzy/title-only binding;
- no fabricated positive/negative fallback;
- bounded current production sample for all currently active giveaway games.

Then run the smallest canonical production visual refresh + Pages deploy needed to verify the changed UI.

## Real-device acceptance — mandatory

After successful deploy, status must be `needs_user_verification`.

User should verify on phone:
1. giveaway area is compact/collapsed on initial load;
2. one tap expands it and another collapses it;
3. expanded game entries contain useful description/pros/cons, or an explicit honest incomplete-analysis state where the repository cannot yet provide them;
4. normal paid feed remains visually and behaviorally intact.

Do not claim final completion before this user verification.

## Hard boundaries

Do NOT:
- redo giveaway source recon;
- alter Steam/Epic/GOG classification logic without a proven integration defect;
- weaken freshness/completeness rules;
- fuzzy-match storefront games to Steam analysis;
- fabricate game analysis;
- broaden paid ranking/Taste logic;
- remove real-device acceptance.

## Report format

Save:
`reviews/worker_reports/cross-platform-giveaway-ui-ux-fix-01.md`

### User acceptance defect
What failed on phone.

### Compact UI change
Exact behavior/files/tests.

### Analysis enrichment route
Exact identity proof/source fields, or exact blocker.

### Current giveaway sample
How every current active giveaway renders after the change.

### Production validation
Exact build/deploy refs.

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
One bounded step only.