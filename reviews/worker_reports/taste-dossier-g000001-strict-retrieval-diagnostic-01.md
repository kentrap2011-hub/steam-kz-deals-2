# Taste dossier g000001 strict retrieval diagnostic 01

## 1. Task / exact scope / snapshot

- Task: `taste-dossier-g000001-strict-retrieval-diagnostic-01`
- Mode: **READ-ONLY / RECON**; the only permitted write is this durable report.
- Repository/source of truth: `kentrap2011-hub/steam-kz-deals-2` / `main`.
- Scheduled Task `Run now`: **not launched**.
- Scheduled Task settings, schema, evidence contract, worker prompt, validator, production state, dossier cache, queue/progress and `CURRENT_TASK.md`: **unchanged**.
- No other repository was read, searched, changed, or used.

Canonical live identity was re-checked before web research against the current worker index, exact `g000001` descriptor, and canonical work manifest:

- snapshot: `cc99c7e33c2094de955c14c2fdfcf8a39eb9836f22afb9313ac01ff2fc4ecc86`;
- canonical expected sequence: `1` / `g000001`;
- progress: `0/732`;
- group size: `3`;
- group SHA-256: `e19dffa09728f444f266625fa829e8572343e8a44705e636330011172a517a9e`;
- active evidence revision: `russian-multi-source-retrieval-2026-09-18`;
- active prompt revision: `web-evidence-v2-russian-multi-source-retrieval-v1`.

Exact ordered scope still is:

1. `2378500` — **Baldur's Gate 3 - Digital Deluxe Edition DLC**;
2. `1000010` — **Crown Trick**;
3. `1000360` — **Hellish Quart**.

Therefore the task's stop-on-snapshot-change condition did not trigger.

## 2. Search budget actually used

The diagnostic task explicitly allowed a wider ceiling than production: at most 12 web-search queries and 30 opened/read pages per game. Production remains unchanged at 8/16.

| Game | Diagnostic search queries | Distinct readable source pages inspected | Failed page/endpoint retrievals | Diagnostic ceiling respected |
|---|---:|---:|---:|---|
| BG3 Digital Deluxe DLC / 2378500 | 12 | 2 | 1 Steam `appreviews` endpoint | yes |
| Crown Trick / 1000010 | 12 | 1 | 1 Steam `appreviews` endpoint + 1 forum decode failure | yes |
| Hellish Quart / 1000360 | 12 | 3 | 1 Steam `appreviews` endpoint | yes |

Repeated opens of the same physical page for line inspection are not counted as additional distinct source pages. Search-result excerpts were used only as discovery evidence, not persisted as feedback records.

The wider 12-query diagnostic budget does **not** change or reinterpret the production 8-query bound. Candidate-validity findings below are contract diagnostics; they do not imply that production may spend 12 queries.

## 3. Canonical rules applied

The candidate ledger was evaluated against the active V2 schema/evidence contract and worker prompt. The rules that materially determined outcomes were:

- `identity.steam_player_feedback_url_appid_must_match_exact_dossier_appid_when_exposed=true`;
- `identity.base_game_feedback_may_satisfy_dlc_gate=false`;
- `feedback_item_identity.collection_surfaces_forbidden_as_feedback_records=true`;
- `feedback_item_identity.public_ref_rule`: an item needs a stable machine-like/explicit item locator; date/playtime descriptions alone are not identities;
- `evidence_invariants.player_feedback_record_requires_item_level_stable_locator=true`;
- `source_policy.steam_store_app_page_is_player_feedback_record=false`;
- `source_policy.aggregate_storefront_statistics_are_player_feedback_mentions=false`;
- `mention_binding.aggregate_count_rule`: aggregate review totals/language counts never create feedback records or mentions;
- `compact_provenance.author_identity_allowed=false`;
- `compact_provenance.profile_scoped_urls_allowed=false`;
- `compact_provenance.forbidden_profile_url_path_regexes`, including `^/(?:id|profiles?|users?|u|authors?)/...`;
- `compact_provenance.rule`: persist only non-identifying locator metadata;
- `russian_evidence.found_and_used_rule`: at least one attributable Russian/mixed item-level player-feedback record must be persisted and bound;
- `russian_evidence.retrieval_unresolved_rule`: exact-product Russian existence + no contract-usable item within bounds => `existence_established_retrieval_unresolved`, no complete dossier;
- `recency.current_state_requires_recent_support=true`; older feedback remains usable for durable gameplay/structure/friction topics but not by itself for current-state claims.

## 4. Compact candidate ledger

No usernames, display names, author attribution, profile URL, raw review/post bodies, or quotations are retained here. Diagnostic IDs below are local report labels, not canonical feedback IDs.

### 4.1 appid 2378500 — Baldur's Gate 3 - Digital Deluxe Edition DLC

Exact-product Russian player-feedback existence was established. The exact DLC review surface and an exact-product mirror expose a non-zero Russian review population. Base-game BG3 material was deliberately excluded by the exact-DLC identity rule.

| ID | Source / surface | Safe locator | Exact product | Player-generated | Russian/mixed | Item-level attributable locator | Verdict | FIRST rejection reason | Canonical rule/field | Classification / remediation |
|---|---|---|---|---|---|---|---|---|---|---|
| BG3-E0 | Steam Store exact app review population | `https://store.steampowered.com/app/2378500/` | yes | aggregate of player reviews | yes existence signal | no | rejected as feedback record; valid existence signal only | Steam Store/aggregate is not an individual player-feedback record | `source_policy.steam_store_app_page_is_player_feedback_record=false`; `mention_binding.aggregate_count_rule` | evidence-contract; no contract change needed |
| BG3-K1 | Kupikod exact-product mirrored review list | `https://steam.kupikod.com/ru-ru/games/baldurs-gate-3-digital-deluxe-edition-dlc/reviews` | yes | yes | yes | **no** | rejected | collection/list surface exposes the review body/date but no stable non-identifying item locator | `feedback_item_identity.collection_surfaces_forbidden_as_feedback_records=true`; `evidence_invariants.player_feedback_record_requires_item_level_stable_locator=true` | retrieval limitation against a strict evidence requirement; better item-ID retrieval can solve |
| BG3-K2 | same physical surface; distinct Russian review card | same collection URL | yes | yes | yes | **no** | rejected | same as BG3-K1 | same as BG3-K1 | retrieval limitation; better retrieval |
| BG3-K3 | same physical surface; distinct Russian review card | same collection URL | yes | yes | yes | **no** | rejected | same as BG3-K1 | same as BG3-K1 | retrieval limitation; better retrieval |
| BG3-K4 | same physical surface; distinct Russian review card | same collection URL | yes | yes | yes | **no** | rejected | same as BG3-K1 | same as BG3-K1 | retrieval limitation; better retrieval |

The four distinct Russian cards were visibly present on the exact DLC collection page, but the page provides no review-specific safe URL or neutral machine token. A human date/card position is explicitly insufficient as item identity. No base-game review was counted.

**Per-game classification:** Russian feedback exists; concrete Russian review cards were found; **zero contract-usable Russian/mixed item records were recovered**. Under the active contract this remains `existence_established_retrieval_unresolved`.

### 4.2 appid 1000010 — Crown Trick

Exact-product Russian player-feedback existence was established by the Steam exact-app review language breakdown; one historical Steam render reports 116 Russian-language reviews.

| ID | Source / surface | Safe locator | Exact product | Player-generated | Russian/mixed | Item-level attributable locator | Verdict | FIRST rejection reason | Canonical rule/field | Classification / remediation |
|---|---|---|---|---|---|---|---|---|---|---|
| CT-E0 | Steam Store exact app Russian review population | `https://store.steampowered.com/app/1000010/Crown_Trick/` | yes | aggregate of player reviews | yes existence signal | no | rejected as feedback record; valid existence signal only | aggregate/store page is not an attributable item | `source_policy.steam_store_app_page_is_player_feedback_record=false`; `mention_binding.aggregate_count_rule` | evidence-contract; no contract change needed |
| CT-S1 | Steam exact-app review card exposed by indexed/rendered review section | same exact-app collection URL | yes | yes | yes | **no stable item token recovered** | rejected | the visible card is reachable only through collection/search rendering, not a stable item-level locator | `feedback_item_identity.collection_surfaces_forbidden_as_feedback_records=true`; `evidence_invariants.player_feedback_record_requires_item_level_stable_locator=true` | retrieval limitation; better retrieval |
| CT-F1 | Russian public forum thread discovered for exact title | `https://tapochek.net/viewtopic.php?t=249685` | yes | yes UGC | yes | thread-level only / no inspected attributable player-feedback item | rejected | discovered material is a discussion/question lead, not an inspected attributable feedback item supporting an observation/conflict | `mention_binding.definition`; worker prompt individual-feedback-item requirement | other semantic/retrieval limitation; no contract change justified |

The forum page itself could not be decoded by the web reader, so it was not promoted into an item-level record and no content from it is persisted here.

**Per-game classification:** Russian feedback exists; a concrete Russian Steam review card was surfaced, but **no stable item-level locator was recovered**. Under the active contract this remains `existence_established_retrieval_unresolved`.

### 4.3 appid 1000360 — Hellish Quart

Exact-product Russian player-feedback existence was established by exact-app Steam review activity. This game produced the clearest distinction between factual sufficiency and contract usability.

| ID | Source / surface | Safe locator | Exact product | Player-generated | Russian/mixed | Item-level attributable locator | Verdict | FIRST rejection reason | Canonical rule/field | Classification / remediation |
|---|---|---|---|---|---|---|---|---|---|---|
| HQ-E0 | Steam Store exact app review population | `https://store.steampowered.com/app/1000360/Hellish_Quart/` | yes | aggregate of player reviews | yes existence signal | no | rejected as feedback record; valid existence signal only | aggregate/store page is not a feedback item | `source_policy.steam_store_app_page_is_player_feedback_record=false`; `mention_binding.aggregate_count_rule` | evidence-contract; no contract change needed |
| HQ-SC1 | direct Steam Community recommendation/review page | direct URL intentionally not persisted because it contains `/id/<profile>/recommended/1000360/` | yes; URL exposes exact appid 1000360 | yes | yes | physically item-level, but locator is profile-scoped | **rejected** | persisted locator would expose profile identity | `compact_provenance.profile_scoped_urls_allowed=false`; forbidden profile path regex; `author_identity_allowed=false` | **privacy/provenance contract limitation**; a neutral recommendation token would solve by retrieval |
| HQ-SS1 | SteamStat exact-game user-review collection | `https://steamstat.io/ru/app/1000360` | yes | yes, mirrored Steam review | yes | **no** review-specific safe locator | rejected | collection page/card has no stable item-level locator | `feedback_item_identity.collection_surfaces_forbidden_as_feedback_records=true`; `evidence_invariants.player_feedback_record_requires_item_level_stable_locator=true` | retrieval limitation; better retrieval |
| HQ-SS2 | same physical SteamStat collection; distinct Russian review card | same collection URL | yes | yes | yes | **no** | rejected | same as HQ-SS1 | same as HQ-SS1 | retrieval limitation; better retrieval |
| HQ-SS3 | same physical SteamStat collection; distinct Russian review card | same collection URL | yes | yes | yes | **no** | rejected | same as HQ-SS1 | same as HQ-SS1 | retrieval limitation; better retrieval |

The three SteamStat cards are dated 2026-08-31, 2026-08-30 and 2026-08-14 and are therefore recent under the 365-day rule, but date alone is not a feedback-item identity.

HQ-SC1 is a direct Russian player review of the exact app and contains enough player experience to support at least anecdotal durable observations. Its 2022 date makes it old, so it cannot by itself support current localization/technical-state claims. Its **first** production rejection is nevertheless privacy/provenance, not age: the only recovered direct locator is profile-scoped and the active contract forbids persisting it. The page did not expose a neutral `steam-recommendation:<id>` token to this diagnostic.

**Per-game classification:** Russian feedback exists; concrete item-level Russian feedback was directly opened; **the only directly attributable Steam item failed compact provenance**, while recent mirrored cards failed item identity. Under the active contract this remains `existence_established_retrieval_unresolved`.

## 5. Important comparison questions

### Baldur's Gate 3 - Digital Deluxe Edition DLC

1. **Russian player feedback found at all?** Yes, for the exact DLC/appid.
2. **Concrete item-level messages/reviews found?** Yes as visible individual review cards, but no contract-usable stable item locator was recovered.
3. **Most common usability blocker?** Collection/list surface without an item-level stable locator.
4. **Factually sufficient but forbidden by contract?** No clean contract-only case was proven. The mirror cards are evidence-rich enough to be promising, but the missing stable locator is a retrieval/provenance gap that normal retrieval can potentially solve.
5. **One-rule change that should be made?** None. Relaxing item identity would unlock cards mechanically but would destroy the attributable-record/count model; better retrieval is the correct route.

### Crown Trick

1. **Russian player feedback found at all?** Yes; Steam exposes a non-zero exact-product Russian review population.
2. **Concrete item-level messages/reviews found?** A Russian Steam review card was surfaced, but no stable item token was recovered; the forum hit did not become an inspected feedback item.
3. **Most common usability blocker?** Item-level stable locator missing.
4. **Factually sufficient but forbidden by contract?** No clean contract-only case was proven.
5. **One-rule change that should be made?** None. This remains a retrieval problem before it is a contract-design problem.

### Hellish Quart

1. **Russian player feedback found at all?** Yes.
2. **Concrete item-level messages/reviews found?** Yes: one direct Steam Community review plus three recent mirrored review cards.
3. **Most common usability blocker?** For the mirrored recent cards, missing item-level locator; for the direct Steam item, profile-scoped provenance.
4. **Factually sufficient but forbidden by contract?** **Yes. HQ-SC1.** It is exact-product, Russian, player-generated and directly inspectable, but the recovered direct URL contains profile identity and is forbidden from compact provenance.
5. **If exactly one rule were changed, what would unlock the proven contract-only lead?** A narrowly scoped exception to `compact_provenance.profile_scoped_urls_allowed=false` for Steam recommendation pages would make HQ-SC1 representable, but it would weaken a deliberate privacy guarantee and is not necessary if retrieval can obtain the neutral recommendation ID. This is a diagnostic contract-change candidate, not an implementation recommendation.

## 6. Top blocking production constraints

Ranking below counts **actual distinct Russian player-feedback item leads** in the ledger, excluding aggregate existence-signal rows.

1. **Missing stable item-level locator / collection surface forbidden — 8 rejected item leads**
   - BG3-K1..K4: 4;
   - CT-S1: 1;
   - HQ-SS1..SS3: 3.
   - Rules: `feedback_item_identity.collection_surfaces_forbidden_as_feedback_records=true`; `evidence_invariants.player_feedback_record_requires_item_level_stable_locator=true`.
   - Diagnosis: the contract rejection is real, but for these leads the practical blocker is **retrieval-only** because the intended evidence model already accepts neutral item IDs/URLs.

2. **Profile-scoped URL forbidden — 1 rejected item lead**
   - HQ-SC1: 1.
   - Rules: `compact_provenance.profile_scoped_urls_allowed=false`, `author_identity_allowed=false`, forbidden profile-path regex.
   - Diagnosis: **contract-caused for the locator actually recovered**. Better retrieval of a neutral recommendation token would avoid needing a contract change.

3. **Discovered Russian UGC did not become an attributable feedback item — 1 lead**
   - CT-F1.
   - Rule: `mention_binding.definition` plus worker prompt item requirement.
   - Diagnosis: semantic/retrieval limitation, not evidence that the contract should change.

Aggregate exact-app Steam signals for all three games were intentionally excluded from this item-lead ranking because the active contract explicitly treats them only as discovery/existence signals, never as mentions.

## 7. Retrieval-only blockers vs contract-caused blockers

### Retrieval-only / retrieval-first

- BG3 exact-product mirror: bodies/cards exist, but no stable item token was exposed.
- Crown Trick Steam review rendering: Russian review existence and a visible card exist, but no stable item token was recovered.
- Hellish Quart SteamStat: recent concrete Russian cards exist, but the aggregator exposes no review-specific neutral locator.
- Neutral Steam `appreviews` retrieval was attempted for all three appids but was inaccessible in this diagnostic environment. After two failed access routes to the same endpoint family, the diagnostic did not keep repeating that route.

For these cases, weakening `player_feedback_record_requires_item_level_stable_locator` is **not justified**. The rule is the basis for physical-item dedupe, exact mention counts and auditability; normal retrieval of stable IDs is the proper remedy.

### Contract-caused

- HQ-SC1 is the single proven case where the retrieved item is direct, exact-product, Russian, player-generated and semantically useful, but its only recovered direct locator is profile-scoped. The current privacy contract itself makes that locator unusable.

This does not prove the privacy guard is wrong: the contract already documents a privacy-preserving preferred representation such as `steam-recommendation:<id>`. The diagnostic could not recover that neutral ID for HQ-SC1.

## 8. Minimal contract-change candidate

Evidence proves one narrow contract blocker, so the task requires a candidate to be named.

**Candidate only; do not implement:** permit a narrowly scoped Steam-recommendation exception to `compact_provenance.profile_scoped_urls_allowed=false` for an exact-app recommendation page when author/display identity is not copied into any other persisted field.

Observed impact: it would unlock **one** real lead in this audit, HQ-SC1.

Risk: it weakens the existing deliberate privacy rule by persisting a URL whose path itself contains profile identity. Because the active contract already supports neutral non-identifying recommendation IDs, **better retrieval of the neutral item token is preferable**. No change to the stable-item-locator requirement is supported by this evidence.

## 9. Unresolved

- The diagnostic web tooling could not retrieve Steam `appreviews` JSON for any of the three appids, so it could not test whether neutral `recommendationid` values are obtainable for the exact visible Steam review items.
- For HQ-SC1, the direct page exposed no neutral recommendation token in the parsed HTML. Therefore the diagnostic cannot determine whether the same physical review is representable under the current contract through another public Steam surface.
- The 12-query diagnostic budget is wider than production's 8-query bound. This report diagnoses candidate usability; it does not claim that every diagnostic lead is discoverable by the production worker before its normal eighth query.
- No live Scheduled Task trace was available beyond the user's stated result, so this report does not attribute the prior worker miss to a specific internal query ordering.

## 10. Status

`complete`

The strict diagnostic is complete. All three exact products have Russian player-feedback existence evidence, but **no Russian/mixed candidate found in this audit is currently usable end-to-end under the active production contract**. The dominant reason is failure to recover a stable non-identifying item locator, with one separately proven Hellish Quart privacy/provenance rejection.

No dossier candidate was published.

## 11. Recommended next step

**Exactly one next step:** compare this strict-retrieval report with the open-discovery control report and identify which leads are found only when contract checks are removed; do **not** implement any rule change yet.

## 12. Efficiency / reusable lesson

The useful diagnostic split is:

1. exact-product Russian **existence**;
2. concrete player-feedback **content found**;
3. stable non-identifying **item identity recovered**;
4. compact provenance/privacy **representable**;
5. temporal/language rules **support the intended claim**.

The first two can look successful while production still correctly rejects the evidence at steps 3 or 4. Future retrieval diagnostics should record those five gates per lead immediately rather than treating “review text visible” as equivalent to “usable feedback record”.

The largest reusable retrieval improvement is not another website quota: once a collection page visibly exposes suitable reviews, search effort should switch to recovering each item's neutral stable locator before spending more queries on additional collection pages. That remains compatible with the existing source-agnostic diversification rule and does not require a production contract change.
