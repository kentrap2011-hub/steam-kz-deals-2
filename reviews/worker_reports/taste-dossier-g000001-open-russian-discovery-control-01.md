# G000001 OPEN RUSSIAN DISCOVERY CONTROL 01

## 1. Task / targets

Task ID: `taste-dossier-g000001-open-russian-discovery-control-01`

Mode: READ-ONLY / RECON. Production contracts, schema, validator, prompts, dossier artifacts, production state, Scheduled Task and Run now/settings were not changed. Only this durable report is created.

Exact targets:

1. appid `2378500` — Baldur's Gate 3 - Digital Deluxe Edition DLC
2. appid `1000010` — Crown Trick
3. appid `1000360` — Hellish Quart

Control goal: establish what real Russian-language player-generated feedback is publicly discoverable without applying current production usability/serialization filters during discovery.

## 2. Search budget actually used

The diagnostic ceiling was respected.

- Baldur's Gate 3 - Digital Deluxe Edition DLC: 15 search queries.
- Crown Trick: 15 search queries.
- Hellish Quart: 15 search queries.
- Total: 45 queries.

Query mix intentionally covered exact title/appid plus materially different public surfaces: Steam Store / Steam Community, Reddit, Pikabu, DTF, GoHa forums, IXBT forum, generic Russian-language web queries, and exact-title review terms.

Explicit page opens/click-throughs remained well below 40 per game. Search-result documents/snippets were also read as leads, but are not counted here as explicit opens. Direct attempts to open Steam's `/appreviews/<appid>` JSON endpoint from the available web tool failed as inaccessible; after that failure the same endpoint method was not repeatedly retried.

## 3. Compact raw lead inventory grouped by game

### A. appid 2378500 — Baldur's Gate 3 - Digital Deluxe Edition DLC

#### Russian player-feedback leads

**BG3-RU-01 — Steam Store exact DLC review surface**
- Surface: Steam Store user reviews.
- URL: https://store.steampowered.com/app/2378500/Baldurs_Gate_3__Digital_Deluxe_Edition_DLC/?l=russian
- Relation: exact.
- Language: Russian.
- Player-generated: yes.
- Form: aggregate/list surface containing user reviews; individual Russian item locators were not exposed by the available page reader in this run.
- Observation: search-indexed copies of the exact appid page reported roughly 516–523 Russian reviews, overwhelmingly positive, depending on crawl snapshot. This is direct existence evidence for substantial Russian player feedback on the exact DLC appid.

#### Exact/likely-exact identity observations on the base-game community surface

These are player-generated and clearly about Digital Deluxe content, but the concrete posts surfaced in this run were English or Ukrainian rather than Russian. They are retained because the control task explicitly asks how the real internet organizes DLC discussion.

**BG3-ID-01 — base-game community thread about missing Deluxe DLC**
- Surface: Steam Community discussion under base game appid `1086940`.
- URL: https://steamcommunity.com/app/1086940/discussions/0/3808408328760277209/
- Relation: likely exact by content.
- Language: English.
- Player-generated: yes.
- Form: concrete discussion.
- Theme: owner cannot find/access Digital Deluxe content; replies explain where DigitalDeluxe files and dice skin are located.

**BG3-ID-02 — base-game community thread about where Deluxe content is located**
- Surface: Steam Community discussion under base game appid `1086940`.
- URL: https://steamcommunity.com/app/1086940/discussions/0/3808408328765038485/
- Relation: likely exact by content.
- Language: English.
- Player-generated: yes.
- Form: concrete discussion.
- Theme: where in-game chest items, OST and artbook are found.

**BG3-ID-03 — base-game community thread about Digital Artbook**
- Surface: Steam Community discussion under base game appid `1086940`.
- URL: https://steamcommunity.com/app/1086940/discussions/0/3808408328764444717/?l=russian
- Relation: likely exact by content.
- Language: English content on Russian-localized surface.
- Player-generated: yes.
- Form: concrete discussion.
- Theme: access path for Digital Deluxe artbook/files.

**BG3-ID-04 — base-game community discussion explicitly naming Digital Deluxe Edition**
- Surface: Steam Community discussion under base game appid `1086940`.
- URL: https://steamcommunity.com/app/1086940/discussions/0/3776868552312454613/
- Relation: likely exact by content.
- Language: English.
- Player-generated: yes.
- Form: concrete discussion.
- Theme: timing/entitlement for Digital Deluxe add-ons.

**BG3-ID-05 — Ukrainian community branch discussing Digital Deluxe entitlement/content**
- Surface: Steam Community discussion under base game appid `1086940`.
- URL: https://steamcommunity.com/app/1086940/discussions/0/3802776599341884449/?ctp=21&l=russian
- Relation: likely exact by content.
- Language: Ukrainian (Russian-localized Steam UI).
- Player-generated: yes.
- Form: concrete discussion/comments.
- Theme: whether Digital Deluxe was automatically granted, how to verify the DigitalDeluxe folder, and whether bonus content is present.

**Control conclusion for BG3 DLC:** Russian player feedback definitely exists on the exact DLC store surface. In addition, concrete Deluxe-specific player discussion naturally appears inside the base-game community, where the URL identity is the base game rather than appid `2378500`.

### B. appid 1000010 — Crown Trick

#### Russian player-feedback leads

All of the following concrete review bodies were surfaced on the exact Steam Store appid page/search representation:

Primary exact surface:
- https://store.steampowered.com/app/1000010/Crown_Trick/?cc=us&l=russian
- Alternate indexed variant:
  https://store.steampowered.com/app/1000010/Crown_Trick/?curator_clanid=4771213&curator_listid=55690&l=russian

**CT-RU-01**
- Surface: Steam Store user review.
- Relation: exact.
- Language: Russian.
- Player-generated: yes.
- Form: concrete review body exposed on aggregate/list page; no item-level locator surfaced.
- Theme: concise positive recommendation; pleasant game.

**CT-RU-02**
- Surface: Steam Store user review.
- Relation: exact.
- Language: Russian.
- Player-generated: yes.
- Form: concrete review body on aggregate/list page.
- Theme: negative assessment of balance, buildcrafting, metaprogression and QoL; relics described as overly situational/useless despite good art and marketable concept.

**CT-RU-03**
- Surface: Steam Store user review.
- Relation: exact.
- Language: Russian.
- Player-generated: yes.
- Form: concrete review body on aggregate/list page.
- Theme: good idea but boring implementation.

**CT-RU-04**
- Surface: Steam Store user review.
- Relation: exact.
- Language: Russian.
- Player-generated: yes.
- Form: concrete review body on aggregate/list page.
- Theme: positive turn-based roguelike assessment; variety of weapons/perks, story framing, familiars, environmental interaction and art style.

**CT-RU-05**
- Surface: Steam Store user review.
- Relation: exact.
- Language: Russian.
- Player-generated: yes.
- Form: concrete review body on aggregate/list page.
- Theme: describes the game as a turn-based room/arena roguelike; campaign structure is straightforward once weapon/skill choices are understood.

**CT-RU-06**
- Surface: Steam Store user review.
- URL variant: https://store.steampowered.com/app/1000010/Crown_Trick/?curator_clanid=4771213&curator_listid=55690&l=russian
- Relation: exact.
- Language: Russian.
- Player-generated: yes.
- Form: concrete review body on aggregate/list page.
- Theme: negative 4/10-style assessment; strong idea but weak implementation, short run through RNG, too little content/replay motivation for a roguelike.

#### Other discovery surfaces

- Steam Community exact-product discussion index exists:
  https://steamcommunity.com/app/1000010/discussions/
- Exact-product community thread inspected:
  https://steamcommunity.com/app/1000010/discussions/0/5739253211802736576/?l=russian
  It is player-generated and exact-product, but the surfaced discussion text was English, so it is not counted as Russian-language feedback.
- A Steambase aggregate exists:
  https://steambase.io/games/crown-trick/reviews
  It summarizes Steam review totals but is not itself player-generated feedback and is not counted as a player-feedback surface.

**Control conclusion for Crown Trick:** concrete Russian player review bodies are easy to find on the exact Steam Store appid surface. In the bounded search, no second clearly Russian player-generated surface class outside Steam Store reviews surfaced.

### C. appid 1000360 — Hellish Quart

#### Russian player-feedback leads

**HQ-RU-01 — exact Steam Store Russian review aggregate**
- Surface: Steam Store user reviews.
- URL: https://store.steampowered.com/app/1000360/Hellish_Quart/?l=russian
- Relation: exact.
- Language: Russian.
- Player-generated: yes.
- Form: aggregate/list with concrete user-review layer.
- Observation: the exact page showed roughly 558–566 Russian reviews across observed crawl snapshots, with about 89% positive.

**HQ-RU-02 — concrete positive review**
- Surface: Steam Store user review on indexed curator-query variant.
- URL: https://store.steampowered.com/app/1000360/Hellish_Quart/?curator_clanid=34861613&l=russian
- Relation: exact.
- Language: Russian.
- Player-generated: yes.
- Form: concrete review body exposed on aggregate/list page; no item-level locator surfaced.
- Theme: very strong concise praise ("best game" sentiment).

**HQ-RU-03 — concrete long negative review**
- Surface: Steam Store user review on the same indexed curator-query variant.
- URL: https://store.steampowered.com/app/1000360/Hellish_Quart/?curator_clanid=34861613&l=russian
- Relation: exact.
- Language: Russian.
- Player-generated: yes.
- Form: concrete review body exposed on aggregate/list page.
- Theme: long-time player says later updates worsened animation quality and combat feel; complaints include jerky/jelly-like arms, weapons snagging, and low impact on attacks.

#### Other discovery surfaces

Steam Community exact-product discussions are abundant:
- https://steamcommunity.com/app/1000360/discussions/
- Examples inspected:
  - https://steamcommunity.com/app/1000360/discussions/0/603017112894573595/
  - https://steamcommunity.com/app/1000360/discussions/0/603031430877955466/
  - https://steamcommunity.com/app/1000360/discussions/0/809098168003310582/

They are concrete player-generated exact-product posts, but the surfaced feedback bodies in this run were English; therefore they are not counted as Russian-language leads.

**Control conclusion for Hellish Quart:** a large Russian review corpus and concrete Russian review bodies exist on the exact Steam Store appid surface. No second clearly Russian player-generated surface class surfaced within the 15-query control budget.

## 4. Surface diversity per game

Counting only surfaces that actually yielded Russian-language player-generated feedback in this bounded run:

| Game | Russian player-feedback surface classes found | Classes |
|---|---:|---|
| BG3 Digital Deluxe DLC (2378500) | 1 | Steam Store user reviews |
| Crown Trick (1000010) | 1 | Steam Store user reviews |
| Hellish Quart (1000360) | 1 | Steam Store user reviews |

Additional exact/likely-exact player-generated community discussion was found on Steam Community for all three products, but the concrete discussion bodies surfaced by the search tool were English or Ukrainian rather than Russian, so they are not counted as Russian surface classes.

The diversified non-Steam queries (Reddit, Pikabu, DTF, GoHa, IXBT and generic forum searches) did not surface clearly Russian player-generated leads for these exact targets within the 15-query-per-game ceiling.

## 5. Exact vs likely/adjacent identity observations

### Crown Trick and Hellish Quart

- Exact-product identity is straightforward on the Steam Store because appid `1000010` and `1000360` are present directly in the review-bearing store URLs.
- Search indexing can expose concrete review text on an aggregate/list page without exposing an individual item/post URL.
- Indexed variants may add curator/query parameters while still clearly resolving to the exact appid.

### BG3 Digital Deluxe DLC

- The exact appid `2378500` clearly has its own large Russian user-review corpus.
- Concrete player discussion about Deluxe entitlement, files, dice skin, artbook, soundtrack and bonus items is naturally organized under the base-game community appid `1086940`.
- Therefore URL/appid identity and semantic product identity can diverge in normal public discussion: a base-game community URL can still be likely exact to the Deluxe DLC by content.
- The available web reader hit Steam's age-check surface for the exact DLC page on direct open, while search indexing still exposed the exact DLC's Russian review aggregate. That is a retrieval/tooling issue, not an absence signal.

## 6. What Russian player feedback clearly exists in the wild regardless of current production contract

1. **BG3 Digital Deluxe DLC:** hundreds of Russian Steam user reviews exist on exact appid `2378500` (roughly 516–523 in observed indexed snapshots). Separately, real players discuss Digital Deluxe content inside the base-game Steam Community.
2. **Crown Trick:** multiple concrete Russian Steam reviews were directly exposed, including both strong positives and detailed negatives about balance, content depth, replayability, buildcrafting, relics and QoL.
3. **Hellish Quart:** hundreds of Russian Steam reviews exist on exact appid `1000360` (roughly 558–566 in observed snapshots), and concrete Russian review bodies include both strong praise and detailed long-term criticism of update/animation/combat feel.

This is sufficient to reject any hypothesis that these targets simply lack Russian player-generated feedback on the public internet.

## 7. Patterns that current production representation may have difficulty capturing

Descriptive only; no fix is recommended here.

- **Aggregate/list review pages can contain real concrete review bodies without an exposed stable item-level locator** in the search result.
- **Search snippets can expose player-review text even when direct page reading is blocked or redirected** (for example by Steam age-check behavior).
- **DLC discussion can live on the base-game community surface**, so exact semantic relation may be visible in post content while the URL contains the base-game appid.
- **Indexed Steam URLs may include curator/query parameters** rather than a minimal canonical store URL.
- **A single exact store page can expose multiple player reviews as one retrieved document**, while item-level provenance remains unavailable to the retrieval tool.
- **Language evidence can be present at the review-content layer even when the destination page/UI behavior differs by locale/age gate.**
- **Aggregate counts vary across crawl snapshots**, so existence is stable while the exact count/date observed by a search index may not be.
- **Public search can reveal an existence signal even where the current tool cannot open a direct review endpoint**, as happened with Steam `/appreviews/<appid>`.

## 8. Unresolved

- No clearly Russian non-Steam UGC surface was found for these exact targets within the fixed 15-query-per-game ceiling. This remains unresolved rather than being treated as evidence of non-existence.
- For BG3 Digital Deluxe DLC, this run did not recover an individually locatable Russian review item/body from appid `2378500`; it recovered the exact Russian review aggregate plus concrete Deluxe-specific base-game community discussions in other languages.
- Steam's public `/appreviews/<appid>` JSON URLs were inaccessible through the available web tool in this run, so they could not be used to enumerate additional exact Russian review bodies.
- Some highly relevant base-game community discussions for BG3 Deluxe were Ukrainian or English, not Russian; they prove the identity/surface-organization pattern but are not counted as Russian feedback.

## 9. Status

**complete**

The bounded control research was completed under the specified ceiling, no production filters were used to reject leads during discovery, no production state/contracts/settings were changed, and only this report is written.

## 10. Recommended next step

**Director compares with strict diagnostic report.**

## 11. Efficiency / reusable lesson

For this class of control-research, the fastest high-yield route is:

- query the exact Steam appid/title with Russian review language first;
- treat the store review surface as existence evidence even when the tool exposes only aggregate/list form;
- for DLC/edition targets, additionally query the base-game community by exact DLC/edition wording because real player discussion may naturally live there;
- then spend the remaining bounded queries on materially different Russian UGC surfaces rather than repeating Steam variants.

This run also shows why control research must record what exists before applying serialization/provenance constraints: concrete Russian review content was easy to surface for Crown Trick and Hellish Quart even when the retrieval representation did not provide an item-level locator.
