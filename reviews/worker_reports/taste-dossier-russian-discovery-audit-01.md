# Taste dossier Russian discovery audit 01

## Task / repository / mode

- Task: `taste-dossier-russian-discovery-audit-01`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Base/source of truth: `main`
- Mode: READ / VALIDATE / BOUNDED WEB EVIDENCE AUDIT
- Changes to production prompt/schema/contract/validator/runtime: none
- Scheduled Task `Run now`: not launched
- Production candidate publication: none

## Exact snapshot / group identity audited

- Snapshot: `00072072b0b382e6b973f448ce00b4aaaeccb2dbe355ca323de1785ccc0bd34c`
- Prepared for: `2026-09-18`
- Canonical expected sequence: `1`
- Group: `g000001`
- Group plan SHA-256: `084433d7b0b69595ef3638a328ba81feb58edc205a37ed620e2f6a43f811695c`
- Group SHA-256: `aa3bfb88365fcdd0ed54e55920bb3a52afc9d07ab1c0a5cceafb36aef2852158`
- Exact ordered appids:
  1. `2378500` — `Baldur's Gate 3 - Digital Deluxe Edition DLC`
  2. `1000360` — `Hellish Quart`
  3. `1003590` — `Tetris® Effect: Connected`
- Active evidence binding: `TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2`, revision `semantic-consistency-gaps-2026-09-17`; worker prompt revision `web-evidence-v2-language-binding-v1`.

Canonical identity and binding were checked against:
- `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- `data/production/pre_ai/taste_steam_review_dossier_worker_groups/00072072b0b382e6b973f448ce00b4aaaeccb2dbe355ca323de1785ccc0bd34c/g000001.json`
- `data/production/pre_ai/taste_steam_review_dossier_work.json`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- `config/taste_steam_review_dossier_schema.json`
- `config/taste_steam_review_dossier_worker_prompt.md`

## Search methodology and bounded counts

Method:
- resolved exact appid/title identity and release year from exact-product public Steam metadata where accessible;
- used exact title + year/appid and Russian-language terms;
- used site-specific Steam Community/discussion discovery where useful;
- inspected only public player-feedback surfaces and exact-product metadata needed to classify discovery;
- treated Russian-rendered store/community UI, aggregate review counts, collection/index pages and professional context as non-record evidence only;
- did not persist raw player text, quotes, usernames, display names or profile URLs;
- did not broaden beyond the three exact `g000001` products.

Counts below count the 8 web-search queries separately from material source documents/pages inspected or access-attempted; search-result clutter/aliases not used for the decision are not counted as additional source-page reads.

| Exact product | Web-search queries | Material source pages/documents inspected or access-attempted | Bound respected |
|---|---:|---:|---|
| Baldur's Gate 3 - Digital Deluxe Edition DLC | 8 | 5 | yes, <=8 / <=16 |
| Hellish Quart | 8 | 8 | yes, <=8 / <=16 |
| Tetris® Effect: Connected | 8 | 4 | yes, <=8 / <=16 |

Minimal effective discovery pattern for the usable Tetris item was an ordinary exact-appid/exact-title Steam Community search with a Russian-language term (equivalent to `site:steamcommunity.com/app/1003590/discussions "рус"` / `"русский"`). No exotic source or backlog-wide crawling was required.

## Per-game classification

| Appid | Exact product | Classification | Result |
|---|---|---|---|
| `2378500` | Baldur's Gate 3 - Digital Deluxe Edition DLC | `russian_feedback_found_but_not_contract_usable` | Exact DLC Steam storefront exposed a substantial Russian-language review population, but the bounded audit did not surface an attributable item-level Russian/mixed record with a stable non-profile item URL or neutral public_ref. Russian store/aggregate evidence is explicitly insufficient under V2. Base-game BG3 feedback was not substituted for the DLC. |
| `1000360` | Hellish Quart | `russian_feedback_found_but_not_contract_usable` | Exact Steam storefront exposed hundreds of Russian-language reviews, but the bounded audit did not surface a V2-usable item-level Russian record. A Russian-rendered Steam discussion page that was discoverable contained non-Russian player content; page locale therefore correctly does not count as Russian evidence. |
| `1003590` | Tetris® Effect: Connected | `usable_russian_feedback_found` | Exact-appid Steam Community thread contains attributable Russian-language player contributions with a stable non-profile item/thread URL and enough substantive content to support a neutral localization/language-friction observation. |

## Minimal compact provenance for usable proof items

### Tetris® Effect: Connected — contract-usable Russian feedback

- Source type: `steam_community` / community discussion
- Domain: `steamcommunity.com`
- Exact product surface: appid `1003590`
- Non-profile item URL: `https://steamcommunity.com/app/1003590/discussions/0/603016087419883875/`
- Approximate first-post date: `2024-12-10`
- Language: Russian; the same thread also contains later Russian-language individual contributions
- Contract-usable support type: neutral `localization` / language-availability observation and language-related comprehension/friction observation
- Raw player text and author identity intentionally omitted.

The exact Steam product metadata independently resolves Tetris® Effect: Connected to release date `2021-08-17` and appid `1003590`.

## Discoverable vs contract-usable

### Baldur's Gate 3 - Digital Deluxe Edition DLC

`discoverable_but_not_contract_usable`:
- exact appid `2378500` Steam DLC surface;
- Russian-rendered exact DLC store page / Russian review aggregate demonstrating that Russian-language review activity exists;
- access/search surfaces that did not yield a stable V2 item-level Russian record within bounds.

`contract_usable_russian_feedback`:
- none proven within bounds.

Important identity result: no base-game Baldur's Gate 3 review/thread was promoted to DLC evidence merely because it discussed Deluxe content or was Russian-language.

### Hellish Quart

`discoverable_but_not_contract_usable`:
- exact appid `1000360` Steam storefront exposes hundreds of Russian-language reviews;
- exact-product Russian-rendered Steam discussion surface was discoverable, but at least one such item contained non-Russian player content, demonstrating why UI locale cannot be used as language evidence;
- review collection/index surfaces are not attributable item records.

`contract_usable_russian_feedback`:
- none proven within bounds.

### Tetris® Effect: Connected

`discoverable_but_not_contract_usable`:
- exact Steam storefront Russian review aggregate and Russian-rendered product page are context only.

`contract_usable_russian_feedback`:
- at least one exact-product Russian Steam Community discussion contribution was readily discoverable and meets the item-level provenance requirement for audit proof.

## Overall classification

`mixed_discovery_failure_and_scarcity`

Meaning in this audit:
- one exact product, Tetris® Effect: Connected, had contract-usable Russian player feedback discoverable by a simple bounded search pattern;
- for BG3 Digital Deluxe DLC and Hellish Quart, Russian player activity is visibly present at exact-product aggregate level, but the bounded audit did not prove a contract-usable item-level locator;
- therefore this is not evidence that Russian-language players were absent for those two products. The proven scarcity is specifically scarcity of contract-usable item-level provenance discoverable within the bounded audit.

## Human-readable conclusion

The live worker's blanket inability to obtain usable Russian records cannot be treated as evidence that the whole `g000001` lacked discoverable Russian player feedback. Tetris has a direct exact-appid Russian player-feedback thread that an ordinary site-specific Russian query exposes.

At the same time, the audit does not establish that BG3 DLC or Hellish Quart had easily discoverable V2-usable Russian item records. Their exact Steam pages show substantial Russian review populations, but aggregate/list evidence is deliberately insufficient under the active contract, and no stable item-level non-profile record was proven within the hard bounds.

Without the live runtime search trace, this report does not claim the internal reason the Scheduled worker missed the Tetris evidence. It proves only that such evidence was independently discoverable by a reasonable bounded method.

## Is a Russian discovery-method gap proven?

Yes, but narrowly.

A practical discovery gap is proven because a contract-usable exact-product Russian item for Tetris was reachable through a minimal pattern that should be considered normal bounded discovery:
- exact title/appid;
- Russian-language term;
- site-specific Steam Community/discussion surface.

The report does **not** justify a fixed website quota, a new search engine, extra retry architecture, or a requirement that every game must yield Russian records.

## Is the previous contract-misread fix still needed?

Yes.

The independent audit does not change the canonical V2 rule:
- Russian search is mandatory;
- Russian evidence is not mandatory;
- when useful attributable Russian feedback is absent or insufficient, `searched_not_found_or_insufficient` is a valid completed Russian-attempt state;
- lack of Russian feedback alone cannot make an otherwise complete V2 dossier/group impossible.

Therefore the already proven contract-interpretation defect remains independently actionable. The new discovery finding means the next fix should address **both**:
1. correct interpretation of the allowed Russian-attempt states; and
2. the minimal Russian discovery guidance that would have exposed the Tetris item.

## Architecture preflight for the recommended next task

- Current owner of bounded player-feedback discovery: Scheduled ChatGPT semantic data-plane.
- Canonical authorization already exists in `config/taste_steam_review_dossier_contract.json` and `config/taste_steam_review_dossier_web_evidence_contract.json`.
- No control-plane responsibility needs to move from GitHub.
- No new recurring stage, queue, retry loop, checkpoint mechanism or backlog manager is justified.
- The next implementation should remain a bounded worker-prompt/runtime-interpretation correction under the existing ownership and hard bounds.

## Unresolved

- No live worker search trace is available, so the exact runtime cause of the missed Tetris evidence is unknown.
- This audit does not prove a V2-usable Russian item for appid `2378500` or `1000360`; it also does not prove that such items do not exist.
- Exact per-review Russian content behind Steam aggregate review counts was not treated as usable without item-level provenance.
- No conclusion is made about any backlog item outside `g000001`.

## Status

`mixed_discovery_failure_and_scarcity`

## Recommended next bounded IMPLEMENT task

Exactly one next task for Director:

`TASTE_DOSSIER_RUSSIAN_DISCOVERY_AND_CONTRACT_INTERPRETATION_FIX_IMPLEMENT_01`

Bounded scope:
- correct the active Scheduled worker prompt/runtime interpretation so `searched_not_found_or_insufficient` and `source_access_unavailable` are explicitly non-blocking Russian-attempt outcomes when the rest of the dossier is sufficient;
- add minimal adaptive discovery guidance: when the Russian attempt is unresolved and budget remains, try an exact-title/appid Russian-language query and a relevant site-specific player-feedback/community surface where available;
- preserve the current <=8 search-query / <=16 source-page hard bounds;
- do not require a Russian item, do not add fixed source quotas, retries, new queues/stages, group splitting, group-size changes, or control-plane changes;
- validate against a bounded regression fixture/sample that includes the Tetris exact-appid discovery pattern plus a no-usable-Russian case.

No part of that IMPLEMENT task is started by this audit.

## Efficiency / reusable lesson

`none`
