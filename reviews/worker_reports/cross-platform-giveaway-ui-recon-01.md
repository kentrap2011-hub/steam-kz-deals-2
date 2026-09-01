# Cross-platform giveaway UI recon 01

Task ID: `cross-platform-giveaway-ui-recon-01`  
Mode: `READ-ONLY / RECON`  
Date: 2026-09-01

## Task

Inspected only the already-authorized UI/visual route needed to place the live `CROSS-PLATFORM-GIVEAWAY-V1` data in the user-facing application. Steam/Epic/GOG source discovery, classification, adapters and giveaway data-plane semantics were intentionally not re-investigated.

Bounded inputs inspected:

- task: `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_UI_RECON_01.md` (blob `e04399ceff1458ecac7fde07ca213166835e75df`);
- prior production closure: `reviews/worker_reports/steam-recommendation-count-fix-01.md`;
- existing giveaway contract: `config/cross_platform_giveaway_contract.json`;
- current giveaway artifacts: `data/production/giveaways/index.json` and `data/production/giveaways/v1/current.json`;
- UI/visual ownership: `config/execution_ownership_contract.json` and the relevant `PROJECT_ROUTES.md` route;
- final visual producer: `scripts/build_final_visual_payload.py` (current inspected blob `83e653f32bfa73db7a3479b63accdeaa276ddfbf`);
- visual build workflow: `.github/workflows/build-daily-visual-payload.yml` (blob `e9d9833b3bf1d3d947ec5f49c33fe3d0d84d7b02`);
- web consumer: `web/app.js` (blob `cf911ead0565b9cac1c6233a9b8696e8d7705bc6`);
- web structure: `web/index.html` (blob `0dfed00334ee5f8601d7e63006d0bdb60aa370a9`);
- Pages deploy: `.github/workflows/deploy-visual.yml` (blob `d2323021bd41f136075103ea70713aaf736db272`).

Current live giveaway production reference used only as an input/sample, not re-researched:

- production commit `50b763ba7ecb1b6e781be48ca2b17b0599d9d4ac` — `Update Steam KZ production and giveaways`;
- current giveaway index blob from that production result: `4d3431540bdc669e1fd646da9d611f337cf22a87`;
- current giveaway snapshot blob from that production result: `9a582fc18180807d44a514c2d1c1294655604574`.

## Canonical UI route

The repository already has one canonical read-only UI route, so no second UI writer or second browser-side data source is needed.

Exact path:

```text
data/production/giveaways/v1/current.json
        ↓ read-only input during visual build
scripts/build_final_visual_payload.py
        ↓ single final UI payload writer
data/production/visual/current.json
        ↓ existing Pages deploy copy
.github/workflows/deploy-visual.yml
        ↓
web/data/current.json
        ↓ single browser fetch
web/app.js (`DATA_URL = 'data/current.json'`)
```

`web/app.js` currently consumes only `data/current.json`. `.github/workflows/deploy-visual.yml` explicitly validates `data/production/visual/current.json`, creates `web/data`, and copies that one file to `web/data/current.json` before uploading the whole `web` directory to Pages.

Therefore the smallest correct ownership-preserving integration is:

1. `scripts/build_final_visual_payload.py` reads the canonical giveaway snapshot as an additional read-only input;
2. it derives a versioned, presentation-oriented `giveaways` field inside `data/production/visual/current.json`;
3. the existing Pages deploy continues copying the same single visual payload;
4. `web/app.js` renders the derived field and never fetches `data/production/giveaways/**` directly.

This keeps `scripts/build_final_visual_payload.py` as the one final visual producer and keeps the web app read-only. It creates no new scheduler, cache, source owner or chat-owned state.

### Exact UI placement

Inside `web/index.html`, the giveaway block should be a sibling at the top of `#feedView`, immediately before the existing `.position-row` and `#gameCard` paid recommendation queue.

Conceptually:

```html
<section id="feedView">
  <section id="giveawayBlock">...</section>
  <div class="position-row">...</div>
  <article id="gameCard">...</article>
  ...
</section>
```

This location satisfies all existing product boundaries:

- the block is clearly visible instead of disappearing inside the paid feed;
- it is encountered before the monthly paid recommendation card;
- it does not enter the paid swipe queue;
- it does not inherit paid ranking cutoff, `urgency_first`, wishlist/final state, score, Taste or purchase-option sorting;
- it remains part of the same canonical page/payload rather than becoming another application surface.

The block should not be collapsed by default. The user requirement is that giveaways remain visibly separate and not hidden by paid-feed ranking.

## Giveaway artifact handoff

Use a **direct canonical read during final visual build plus a versioned derived field in the visual payload**.

Recommended derived shape:

```json
{
  "giveaways": {
    "schema_version": 1,
    "source_contract": "CROSS-PLATFORM-GIVEAWAY-V1",
    "state": "active",
    "generated_at_utc": "2026-09-01T19:30:40.405647Z",
    "fresh_until_utc": "2026-09-03T01:30:40.405647Z",
    "accepted_offer_count_at_build": 2,
    "source_health": {
      "steam": {"status": "ok", "complete": true},
      "epic": {"status": "ok", "complete": true},
      "gog": {"status": "ok", "complete": true}
    },
    "games": [
      {
        "game_key": "meta-v1:...",
        "title": "Breathedge",
        "offers": [
          {
            "storefront": "epic",
            "claim_url": "https://store.epicgames.com/en-US/p/breathedge",
            "promotion_end_utc": "2026-09-03T15:00:00Z",
            "base_price": 690000,
            "final_price": 0,
            "currency": "KZT",
            "discount_percent": 100
          }
        ]
      }
    ]
  }
}
```

`state` should be a builder-owned presentation state, not a source reclassification. Suggested deterministic values:

- `active` — source snapshot is valid/complete/fresh at build time and at least one offer remains active;
- `empty` — source snapshot is valid/complete/fresh and it had zero active accepted offers at build time;
- `unavailable` — missing, malformed, wrong contract/country, incomplete, stale, or otherwise not safe to present as current complete data.

The derived payload should intentionally omit audit/source-provenance internals and classifier reason-code detail from the primary UI. The browser needs only user-facing claim data plus enough snapshot state/freshness metadata to fail closed.

Cross-store grouping must be preserved exactly as emitted by the giveaway artifact: one canonical giveaway game entry may contain multiple store offers. The UI must never re-deduplicate by title.

## Freshness / expiry

Visibility must fail closed at **both build time and render time**.

### Build-time rule

`build_final_visual_payload.py` may expose current giveaway cards only when all of the following hold:

1. artifact parses and matches `CROSS-PLATFORM-GIVEAWAY-V1` / expected schema / `KZ`;
2. `snapshot_status == "complete"`;
3. required Tier-1 coverage is complete according to the canonical snapshot;
4. current build time is not later than `fresh_until_utc`;
5. each exposed offer has a valid known claim URL and `promotion_end_utc > build_time`.

A missing/malformed/incomplete/stale source snapshot must **not** be transformed into “no giveaways”. It becomes `giveaways.state = "unavailable"` with no claim cards.

A valid complete fresh snapshot whose accepted active count is genuinely zero becomes `state = "empty"`.

This distinction matters:

- `empty`: trusted statement — “Сейчас активных раздач не найдено.”
- `unavailable`: coverage statement — “Раздачи временно не удалось проверить полностью.”

The paid recommendation feed should still build and render if only the giveaway artifact is unavailable; giveaway degradation is a separate auxiliary-surface state and must not destroy the monthly paid UI.

### Render-time expiry rule

The browser must defensively compare each derived offer's `promotion_end_utc` with browser time before displaying it. If `promotion_end_utc <= now`, remove the CTA/card immediately without waiting for the next repository build/deploy.

This is a display guard, not a new source/classification rule.

Important edge case: if the visual payload was built with accepted offers, but all of those offers expire in the browser before the next visual rebuild, the UI must **not** reinterpret that as a freshly verified `empty` source result. Instead, after suppressing all expired CTAs, show an update/unavailable-style message such as “Текущие раздачи закончились, данные обновляются.” until a newer complete snapshot arrives.

If the derived giveaway snapshot itself has passed `fresh_until_utc` at browser time, show `unavailable` and no claim CTA even if a copied offer row still exists.

Thus expired giveaways disappear automatically while stale data can never masquerade as current complete coverage.

## Relevance policy

Safe classification under the task's three allowed routes:

**`no reliable cross-store personal relevance mapping exists yet`**.

Evidence from the current repository surface:

- giveaway groups expose their own `canonical_game_key` / identity confidence for safe giveaway grouping;
- targeted repository search found no existing consumer/table that maps that giveaway key into the Steam/Taste identity used by personalized recommendations;
- no existing canonical cross-store identity table was found that safely maps Epic/GOG product identities into a Steam app identity;
- the current paid Taste/profile machinery is tied to existing Steam-oriented recommendation identities;
- giveaway `identity_confidence=high` proves safe grouping inside the giveaway contract, **not** a Taste-profile binding.

Therefore the first UI implementation must not:

- match Epic/GOG giveaways to Taste by normalized title;
- use fuzzy title/publisher similarity as personal evidence;
- copy a paid score onto a giveaway;
- insert giveaway entries into the paid ranked `items` array;
- order or hide giveaways by the monthly paid ranking cutoff;
- label a giveaway “подходит вам” unless a future explicit identity contract proves that mapping.

### Smallest honest fallback

Show **all currently verified Tier-1 claim-to-keep full-game offers** from the complete giveaway snapshot in the separate block.

This is not truly “unconditional junk”: the existing giveaway contract has already removed permanent F2P/access-only/subscription/non-game/unknown-region/unknown-ownership cases before they reach accepted UI rows. That verified Tier-1/full-game boundary is the only defensible relevance floor presently available without inventing identity.

Tradeoff: some shown games may not match the user's taste. Hiding them would require personal evidence the repository does not currently possess. Since claiming a free game is a separate, time-sensitive utility action with effectively zero purchase cost, displaying the small verified set is more honest than silently discarding offers with an invented relevance model.

For v1, deterministic display order should be:

1. earliest `promotion_end_utc` first;
2. title as deterministic tie-breaker;
3. storefront/source offer identity as final tie-breaker.

No Taste score participates.

If a future explicit cross-store identity mapping contract is added, personal annotation/filtering can be reconsidered as a separate task. It is not required or authorized here.

## Current sample

Using only the current canonical snapshot produced by production commit `50b763ba7ecb1b6e781be48ca2b17b0599d9d4ac`:

- snapshot: `complete`;
- Steam: `ok`, complete, accepted `0`;
- Epic: `ok`, complete, accepted `2`;
- GOG: `ok`, complete, accepted `0`;
- unverified accepted-surface rows: `0`;
- accepted game groups: `2`.

The proposed UI would therefore show a visible `Бесплатные раздачи` block above the paid recommendation queue with two game entries, neither carrying a Taste score/personal badge:

1. **Breathedge**
   - store: Epic Games;
   - price: `Бесплатно`;
   - previous/base price may be rendered from the existing KZT base-price field if desired;
   - deadline: `2026-09-03T15:00:00Z`, localized by the browser;
   - CTA: `Забрать в Epic Games` using the exact canonical `claim_url`.

2. **Rival Stars Horse Racing : Desktop Edition**
   - store: Epic Games;
   - price: `Бесплатно`;
   - previous/base price may be rendered from the existing KZT base-price field if desired;
   - deadline: `2026-09-03T15:00:00Z`, localized by the browser;
   - CTA: `Забрать в Epic Games` using the exact canonical `claim_url`.

Both current offers have the same promotion deadline, so deterministic title order places `Breathedge` first.

Steam and GOG having zero accepted current offers should not generate empty store sub-sections. Their health matters only for establishing that the overall snapshot is trusted complete. Under healthy complete coverage, there is no reason to expose technical source-status badges in the normal active state.

Suggested copy for the block:

- heading: `Бесплатные раздачи`;
- helper: `Заберите до указанного срока — после получения игра остаётся в библиотеке.`;
- offer CTA: `Забрать в Steam` / `Забрать в Epic Games` / `Забрать в GOG`;
- complete empty: `Сейчас активных раздач не найдено.`;
- unavailable/incomplete/stale: `Раздачи временно не удалось проверить полностью.`

If one game later has multiple accepted storefront offers, render one game row/card with one CTA/deadline row per canonical offer; do not merge or discard those offers in the browser.

## Recommended IMPLEMENT

Create one bounded implementation task, suggested ID `cross-platform-giveaway-ui-01`, with **no changes to `scripts/giveaway_*`, source discovery, classification, paid ranking or Taste**.

### Files/components to change

1. `scripts/build_final_visual_payload.py`
   - add canonical read of `data/production/giveaways/v1/current.json`;
   - validate only the UI-facing contract/freshness/completeness invariants needed for safe presentation;
   - derive `giveaways.schema_version = 1`, `state`, freshness metadata and minimal game/offer presentation rows;
   - keep giveaway data outside the paid `items` array and do not modify paid order/scores.

2. Add `scripts/test_giveaway_visual_handoff.py`
   - pure/deterministic fixtures for source snapshot → derived visual field.

3. `.github/workflows/build-daily-visual-payload.yml`
   - add `data/production/giveaways/v1/current.json` and the new handoff test/builder-related file to relevant `push.paths`;
   - execute the new deterministic handoff test in the existing visual-build job;
   - use the existing workflow/concurrency/schedule ownership only; add no new recurrence.

4. `web/index.html`
   - add `#giveawayBlock` at the top of `#feedView`, immediately before `.position-row`;
   - if a helper module is used, load it as a normal static web asset.

5. Add `web/giveaway-ui.js`
   - isolated formatter/renderer for the giveaway presentation field;
   - render state, games, deadlines and store CTAs;
   - perform render-time freshness/expiry suppression;
   - do not touch paid queue state.

6. Add `web/giveaway-ui.test.js`
   - deterministic DOM-light/pure helper tests where possible.

7. `web/app.js`
   - after the existing single `data/current.json` load, pass `data.giveaways` to the giveaway renderer;
   - do not introduce a second fetch.

8. `web/styles.css`
   - visually separate the utility block from the paid recommendation card and make CTA/deadline readable on narrow/mobile layouts.

9. `.github/workflows/deploy-visual.yml`
   - add `node web/giveaway-ui.test.js` to the existing `Run UI regressions` step;
   - keep the existing `data/production/visual/current.json → web/data/current.json` copy unchanged.

### Deterministic behavioral tests

Builder/handoff tests must cover:

1. complete + fresh + one accepted offer → `state=active`, one exact CTA row;
2. complete + fresh + zero accepted → `state=empty`;
3. incomplete snapshot → `state=unavailable`, no CTA rows;
4. stale `fresh_until_utc` → `state=unavailable`, no CTA rows;
5. missing/malformed/wrong contract/wrong country → fail-safe `unavailable`, while paid payload remains buildable;
6. accepted row already expired at build time → not emitted;
7. multiple accepted storefront offers under one canonical game → one game, every offer preserved;
8. ordering by deadline then title then stable source offer identity;
9. source-internal provenance/reason-code data is not accidentally copied as required UI shape;
10. existing paid `items` order/count/score fields are unchanged by adding the giveaway input.

Frontend tests must cover:

1. `active` renders a separate visible giveaway block before the paid queue;
2. exact `claim_url` and correct storefront CTA label are used;
3. deadline formatting is present;
4. multiple store offers render under one game without title-based browser dedup;
5. `empty` and `unavailable` use different copy;
6. stale derived snapshot produces no claim CTA;
7. offer whose deadline passes at render time disappears immediately;
8. when all previously accepted rows have just expired, renderer shows update/unavailable wording rather than claiming a newly verified empty source result;
9. giveaway rendering does not mutate paid `items`, queue cursor, urgency toggle, wishlist/liked/final state or score/ranking data.

### Generated-output checks

After implementation, the canonical visual build must prove:

- `data/production/visual/current.json` contains a versioned `giveaways` sibling field;
- it still has the existing read-only UI mode and normal paid payload;
- no second browser data artifact/fetch was introduced;
- a current complete giveaway snapshot yields the expected derived state/count;
- a stale/incomplete fixture never emits active CTAs;
- the Pages staging step still copies only the canonical final visual payload to `web/data/current.json`.

Then run the existing `Build daily visual payload` and `Deploy visual mailing` paths and record their exact run/job refs.

### User/device acceptance

Yes — one post-deploy visual acceptance is appropriate because “separate clearly visible block” is a layout/user-perception requirement, not fully proven by JSON/unit tests.

Minimum acceptance:

- narrow/mobile viewport: giveaway block is visible before the paid card, readable, CTAs usable, no horizontal overflow;
- normal desktop viewport: block remains visually separate and does not displace/break the paid queue;
- CTA opens the exact canonical storefront URL;
- paid swipe/like/final interactions still behave as before.

This is acceptance of presentation only; it does not reopen source/data-plane research.

Efficiency / reusable lesson: candidate — for auxiliary read-only surfaces, route new canonical data through the existing final visual producer rather than giving the browser a second production-data dependency; this preserves ownership and gives one place to derive fail-closed presentation state.

## Status

`complete`

The repository already provides the required authority and serving route. No new contract, source investigation, scheduler, personal semantic queue or user product decision is required before a bounded UI implementation.

## Recommended next step

Run one bounded `IMPLEMENT` task `cross-platform-giveaway-ui-01`: derive the versioned `giveaways` field in `scripts/build_final_visual_payload.py`, render the separate fail-closed block at the top of `#feedView`, add the deterministic handoff/frontend regressions above, then validate one canonical visual build + Pages deploy and one mobile/desktop presentation acceptance. Do not change giveaway sources/data-plane or paid ranking/Taste.
