# Trine 4 missing diagnosis 01

## Task
Traced the exact current canonical path for `Trine 4: The Nightmare Prince` from the Steam KZ live-sale snapshot through shortlist/pre-AI semantic context into the final visual/user-visible feed. This was RECON only: no manual app insertion, no Taste/ranking/price/business-rule change, no publish/deploy, and no production backlog processing was performed.

## Canonical identity
- canonical offer key: `App_690640`
- Steam app id: `690640`
- canonical title: `Trine 4: The Nightmare Prince`
- production family: `game:690640`
- Taste subject key: `App_690640`

## Live sale state
Canonical source: `data/production/pre_ai/store_snapshot.json`.

Captured while the sale is active:
- Steam Kazakhstan availability: `true`
- current price: `1,520 KZT`
- reference/original price: `7,600 KZT`
- discount: `80%`
- canonical source observation timestamp: `2026-09-02T06:42:05.485251Z`
- recorded sale end: `2026-09-15T17:00:00+00:00`

The current canonical source therefore proves that the exact app is available in KZ and on a live paid discount.

## Trace
| Stage | Artifact / exact identity | State | Relevant evidence |
|---|---|---|---|
| Steam KZ canonical source | `data/production/pre_ai/store_snapshot.json` / `App_690640` | PRESENT | KZ available, 1,520 KZT, -80%, observed `2026-09-02T06:42:05.485251Z` |
| production shortlist | `data/production/shortlist/chunk_001.tsv` / `App_690640` | PRESENT | row contains app `690640`, title, 80% discount, 1520.0 KZT and discovery flags `mainstream_quality|strong_fit|strong_niche_fit|exceptional_discount|very_high_rating` |
| purchase/deal context | `data/production/pre_ai/chatgpt_purchase_context.jsonl` / `game:690640` | PRESENT | purchase key `App_690640`; current `288 RUB` display equivalent; both `deal_if_strong` and `deal_if_moderate` are `INCLUDE`; `price_gate_reason=within_normal_budget_target`; wishlist false; history `unverified` but not excluding |
| semantic work input | `data/production/pre_ai/chatgpt_taste_queue.jsonl` / `App_690640` | PRESENT BUT UNRESOLVED | `ai_required_reason=taste_cache_key_missing`; no `resolved_taste_fit`; `work_required=[evaluate_taste_fit,evaluate_normalized_taste_factors,resolve_grounded_negative_analysis]` |
| final visual producer input gate | `scripts/build_visual_feed_v2.py::get_fit()` / `App_690640` | EXCLUDED | without row `resolved_taste_fit` and without a valid cache entry whose verdict is `INCLUDE`, `get_fit()` returns `None`; `main()` immediately skips rows whose fit is not `strong`/`moderate` |
| canonical final visual / bounded ranking lookup | `data/production/visual/current.json`; `data/production/visual/ranking_lookup/t.json` | ABSENT | bounded `t.json` ordering contains `Train Valley 2` and then later `Troublemaker`; no Trine 4 entry/rank exists, consistent with the upstream `get_fit` skip before ranking |
| user-visible web list | `web/app.js` -> `DATA_URL='data/current.json'` | ABSENT | UI consumes producer-owned current payload; it does not discover or re-add missing games, so a game skipped before visual assembly cannot render as a card |

Current payload-wide bounded context: `data/production/pre_ai/chatgpt_payload.json` reports `source_family_count=696`, `ai_queue_count=599`, `ready_without_ai_count=0`, `negative_full_evaluation_queue_count=23`, and `complete_family_partition=true`. Trine 4 is one of the current full semantic-evaluation shapes because its row requires Taste fit + normalized factors + grounded negative analysis.

## First disappearance point
The first canonical present-before / absent-after transition is:

`chatgpt_purchase_context.jsonl` + `chatgpt_taste_queue.jsonl` -> `scripts/build_visual_feed_v2.py::get_fit()` -> visual item preparation.

Trine 4 is still a valid commercial candidate immediately before this transition. It is not admitted to `prepared`/visual items because the canonical Taste key `App_690640` has no usable current cache verdict and the queue row has no `resolved_taste_fit`.

This is earlier than final ranking. Ranking never receives Trine 4, so ranking/cutoff cannot be the cause of the current absence.

## Classification
`stale_or_incomplete_data`

The commercial/product route is not excluding Trine 4: identity, KZ availability, live discount, price gate and both strong/moderate deal branches are valid. The missing prerequisite is current canonical semantic data for `App_690640` (`taste_cache_key_missing`). The producer is behaving fail-closed as designed when required semantic input is incomplete.

## Scope of impact
This is not isolated to app `690640`, but no catalog-wide manual scan was performed.

Bounded existing counts show the current pre-AI scope has 599 semantic work rows and 23 rows requiring full semantic evaluation. Therefore the failure shape can affect other currently valid commercial candidates whose Taste cache key/fingerprint is unresolved; it is not evidence of a Trine-specific identity, region, price, ranking, or package defect.

No evidence was found that the generic visual gate itself is defective: `get_fit()` matches the canonical fail-closed requirement that normal paid recommendations need resolved semantic prerequisites.

## Efficiency / reusable lesson
`none`

## Status
`complete`

## Recommended next step
Use the existing scheduled ChatGPT semantic data-plane to resolve the current GitHub-prepared Taste work for `App_690640` (including normalized factors and grounded negative analysis), then let the existing GitHub-owned ingest/completeness/rebuild route validate, persist and rebuild downstream visual artifacts. Do not manually evaluate/insert Trine 4 in this interactive chat and do not create another queue or scheduler.

Ownership remains per `config/execution_ownership_contract.json`: GitHub owns scope/queue/validation/persistence/downstream rebuild; scheduled ChatGPT owns the constrained semantic judgment.

Trine 4 сейчас есть в canonical live-sale source, исчезает впервые на слое semantic Taste readiness -> visual item preparation, потому что `App_690640` имеет `taste_cache_key_missing` и поэтому `get_fit()` не выдаёт допустимый `strong/moderate` fit, и безопасный fix должен затрагивать существующий semantic Taste runtime/ingest/rebuild path, а не Trine 4, цену или ranking.