# WORKER TASK — CHAT 1

Task ID: `cross-platform-giveaway-ui-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/cross-platform-giveaway-ui-01.md`

## Goal

Implement the separate visible user-facing giveaway block using the already-live `CROSS-PLATFORM-GIVEAWAY-V1` snapshot and the exact canonical UI route established by `cross-platform-giveaway-ui-recon-01`.

Do not repeat source recon, adapter work, giveaway classification, or cross-store Taste investigation.

## Read first

- `reviews/worker_reports/cross-platform-giveaway-ui-recon-01.md`
- `config/cross_platform_giveaway_contract.json`
- current `data/production/giveaways/v1/current.json`
- `scripts/build_final_visual_payload.py`
- `web/index.html`
- `web/app.js`
- current web stylesheet(s) used by the page
- `.github/workflows/build-daily-visual-payload.yml`
- `.github/workflows/deploy-visual.yml`
- relevant execution ownership contract
- relevant pitfall only if trigger matches

## Canonical integration

Preserve the one existing UI payload route:

`data/production/giveaways/v1/current.json`
→ `scripts/build_final_visual_payload.py`
→ `data/production/visual/current.json`
→ existing Pages deploy copy
→ `web/data/current.json`
→ `web/app.js`

The browser must not fetch `data/production/giveaways/**` directly.
Do not create a second UI writer, cache, scheduler or data source.

## Required behavior

### 1. Separate visible block

Add a clearly visible `Бесплатные раздачи` block at the top of `#feedView`, before the paid recommendation queue.

It must:
- be visually separate from paid recommendations;
- not be collapsed by default;
- not enter paid swipe/ranking/final/wishlist state;
- not compete with the monthly paid-purchase selection;
- not be hidden by normal paid ranking cutoff.

### 2. Derived visual payload

`build_final_visual_payload.py` should derive a presentation-oriented `giveaways` field from the canonical giveaway snapshot.

Preserve source grouping exactly; never re-deduplicate by title.

Presentation state must distinguish:
- `active` — complete/fresh snapshot with at least one currently active accepted offer;
- `empty` — complete/fresh trusted snapshot with zero active accepted offers;
- `unavailable` — missing/malformed/wrong contract or country/incomplete/stale/untrusted snapshot.

Do not expose stale/incomplete data as trusted empty data.

### 3. Freshness and expiry

Build time:
- accept only expected contract/schema/KZ;
- require complete Tier-1 coverage;
- require snapshot freshness;
- expose only offers with valid claim URL and future promotion end.

Render time:
- suppress an offer immediately when its `promotion_end_utc <= now`;
- suppress all CTAs if the derived snapshot itself is stale;
- if all previously active offers expire before a new verified snapshot arrives, show an updating/unavailable state rather than claiming a freshly verified empty result.

### 4. Relevance policy v1

There is currently no proven safe cross-store personal Taste identity mapping for Epic/GOG.

Therefore v1 must show all verified Tier-1 claim-to-keep full-game offers from the complete snapshot, without:
- title/fuzzy Taste matching;
- paid score copying;
- personal `подходит вам` badge;
- paid ranking/filtering.

This is an honest temporary relevance floor, not a claim of personalization.

Order deterministically:
1. earliest promotion end;
2. title;
3. storefront/offer identity.

### 5. User-facing copy

Use concise copy consistent with the recon, for example:
- heading: `Бесплатные раздачи`;
- helper: `Заберите до указанного срока — после получения игра остаётся в библиотеке.`;
- CTA: `Забрать в Steam` / `Забрать в Epic Games` / `Забрать в GOG`;
- trusted empty: `Сейчас активных раздач не найдено.`;
- unavailable: `Раздачи временно не удалось проверить полностью.`

Do not expose technical source-health details in normal UI.

## Validation

Use behavioral/output checks.

Add deterministic coverage for at least:
- complete fresh snapshot + active offers -> visible block/cards;
- complete fresh zero offers -> trusted empty state;
- incomplete snapshot -> unavailable, no claim CTA;
- stale snapshot -> unavailable, no claim CTA;
- expired offer -> hidden;
- all offers expire client-side -> not misrepresented as freshly verified empty;
- one game with multiple accepted storefront offers preserves all offers;
- similar titles do not merge;
- giveaway entries do not enter paid ranking/swipe/final state;
- browser reads only existing `web/data/current.json` route.

Then run the smallest canonical visual build and Pages deploy route that can prove actual production behavior.

## Real-device acceptance — mandatory

This is a UI task. Do **not** report final acceptance from runner output alone.

After a successful canonical visual payload commit and Pages deploy:
- report exact deployed refs;
- status must be `needs_user_verification`;
- user must verify on the actual phone/site that:
  - the separate block is visible;
  - current giveaway rows/CTAs look correct;
  - paid feed remains intact;
  - expired/stale behavior is not misleading.

Only after user confirmation can the Director close/delete this worker chat.

## Hard boundaries

Do NOT:
- change `scripts/giveaway_*` source/classification logic unless a concrete integration contract bug makes that unavoidable and is reported first;
- add title-only or fuzzy cross-store Taste matching;
- change paid ranking/Taste/wishlist logic;
- add a second scheduler/data writer/browser fetch;
- manually curate offers;
- weaken freshness/completeness fail-closed rules;
- claim completion before production deploy + user verification.

## Report format

Save:
`reviews/worker_reports/cross-platform-giveaway-ui-01.md`

### Task
What changed.

### Canonical handoff
Exact producer/payload/web route.

### Changes
Exact files/commits.

### Validation
Behavioral tests, canonical build/deploy refs, generated output state.

### User verification
Exact visible checks for the phone/site.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_verification`

### Recommended next step
One bounded next step only.