# Wishlist good-deal override recon 01

## 1. Task

Task: `wishlist-good-deal-override-recon-01`.

Mode: **READ-ONLY / RECON**. No ranking code, Taste code, thresholds, giveaway/Epic/GOG logic, semantic queues, or production data were changed. The only repository write in this task is this required report.

Target user rule:

> A Steam-wishlist game may pass the ordinary weak/minimal Taste eligibility gate when the current paid deal is genuinely good, while preserving all authoritative commercial exclusions, confirmed direct conflicts, and truthful risk/value information.

Status: `complete`.

## 2. Current path

The relevant current paid path is:

1. canonical policy / profile / discovery feed;
2. pre-AI content/store/family/history/deal snapshots;
3. price-blind Taste projection/cache or AI Taste evaluation;
4. `scripts/build_pre_ai_chatgpt_payload.py` combines Taste + deal scenarios and loads Steam wishlist context;
5. accepted rows go to `data/production/pre_ai/chatgpt_purchase_context.jsonl`;
6. `scripts/build_visual_feed_v2.py` prepares visible paid rows and again requires a recognized eligible Taste fit plus an included deal scenario;
7. final visual producers enrich/refresh risks, practical facts and offers;
8. `scripts/priority_ranking.py` / `config/final_ranking_policy.json` rank **already eligible** visible items; wishlist currently contributes its existing score bonus there;
9. `data/production/visual/current.json` is the paid final feed sibling (giveaways are separate and out of scope).

Important separation already exists and should remain: Taste evaluation is price-blind; wishlist/price/discount/history are not valid Taste evidence. The requested behavior is therefore an **eligibility exception after a final Taste result**, not a mutation/promotion of the Taste verdict or fit.

## 3. Exact removal / gate point

### First current gate — pre-AI purchase-context producer

The first confirmed removal point for a wishlist item whose final cached Taste verdict is weak/below-moderate is in:

`script: scripts/build_pre_ai_chatgpt_payload.py`

Inside the `cache_hit` branch:

```python
if cached_taste['verdict'] != 'INCLUDE':
    excluded_keys.append(primary_key)
    exclusion_counts['valid_cached_taste_below_moderate'] += 1
    continue
```

At that point the script has already loaded the wishlist and the row can have `context_only.wishlist == true`, but wishlist is not consulted before the `continue`. Therefore the row never reaches `ready_context` / purchase context and cannot be rescued by final ranking.

Fresh AI Taste results do not create a bypass: `scripts/process_taste_inbox.py` ingests them, rebuilds Taste consumers, and reruns `scripts/build_pre_ai_chatgpt_payload.py`. The newly accepted cache entry then encounters the same branch.

There is an earlier **commercial** guard in the same producer:

```python
if not strong_ok and not moderate_ok:
    ...
    exclusion_counts['deal_excludes_even_if_strong'] += 1
    continue
```

That is not the Taste gate and must remain non-overridable.

### Second current gate — visual feed producer

Even if the first `continue` were simply removed, the row would still not become visible. `scripts/build_visual_feed_v2.py` currently has:

```python
fit = get_fit(row, taste_entries)
if fit not in {'strong', 'moderate'}:
    continue
scenario = row.get(f'deal_if_{fit}') or {}
if scenario.get('disposition') != 'INCLUDE':
    continue
```

`get_fit()` also returns only `strong`/`moderate` and falls back to an accepted Taste-cache verdict. A genuine override therefore needs an explicit eligibility marker/path here as well. **Do not fake `below_moderate` as `moderate`**, because that would corrupt the meaning of the Taste state.

### Ranking cannot currently rescue the row

`config/final_ranking_policy.json` explicitly applies after eligibility and says a score cannot rescue an ineligible candidate. The existing wishlist score bonus is therefore only a post-eligibility preference signal today.

## 4. Canonical good-deal signal

Do **not** invent a new discount-percent threshold.

The strongest already-existing canonical current-deal signal is the existing purchase-decision label:

`purchase_decision == "БРАТЬ СЕЙЧАС"`

In `config/deal_quality_contract.json` / `scripts/build_pre_ai_deal_scenarios.py`, that label is derived from the existing history classes:

- `record` -> `БРАТЬ СЕЙЧАС`;
- `near_record` -> `БРАТЬ СЕЙЧАС`.

`good_vs_history`, `previously_free`, and `unverified` map only to `МОЖНО БРАТЬ`; `well_above_history` maps to `ЛУЧШЕ ЖДАТЬ`.

For this override, the safe existing commercial route is specifically the already-built **moderate scenario**:

```text
decision_if_moderate.final_disposition == INCLUDE
AND
decision_if_moderate.purchase_decision == "БРАТЬ СЕЙЧАС"
```

Why `decision_if_moderate`: `moderate` is the current ordinary minimum eligible Taste band, so its commercial scenario is the least-permissive existing paid route that matches the boundary being overridden. Reusing it avoids borrowing strong-only exceptional price allowances and introduces no new hidden constant. It automatically preserves existing symbolic-discount and moderate price/value gates.

This means a historical `record/near_record` alone is **not** sufficient if the current moderate commercial scenario is excluded.

## 5. Proposed override semantics

Smallest explicit condition:

```text
wishlist_good_deal_override =
    steam_wishlist == true
    AND cached_taste.verdict == EXCLUDE
    AND cached_taste.fit_level == below_moderate
    AND cached_taste.reason_code IN {
        exclude_insufficient,
        exclude_audited_below
    }
    AND decision_if_moderate.final_disposition == INCLUDE
    AND decision_if_moderate.purchase_decision == "БРАТЬ СЕЙЧАС"
```

Effect:

- bypass **only** the ordinary below-moderate Taste eligibility rejection;
- keep the original Taste entry unchanged (`EXCLUDE`, `below_moderate`, original factors/evidence/reason code);
- select the already-existing `decision_if_moderate` only as the commercial route for this exception;
- attach an explicit provenance marker such as `eligibility_override = wishlist_good_deal` to purchase context / visual data so downstream code can distinguish “eligible by exception” from a genuine moderate Taste fit;
- do not create a second Taste state and do not write a promoted Taste cache entry.

`exclude_audited_below` is still an ordinary final below-threshold outcome and is eligible for the exception. `exclude_direct_conflict` is explicitly excluded from the override.

### Why the implementation must inspect the compact cache reason code

`config/taste_ledger_contract.json` maps all three implementation exclusions — `exclude_insufficient`, `exclude_audited_below`, and `exclude_direct_conflict` — to the canonical ledger reason `below_moderate_fit`. Therefore checking only the ledger reason is unsafe: it cannot distinguish an ordinary weak fit from a direct conflict. The override guard must retain/use the more precise cache `reason_code`.

## 6. Non-overridable protections

Wishlist must **not** override:

1. **Invalid/ineligible content or purchase identity** already rejected before the family reaches this point (including content/DLC ownership rules). Wishlist remains neither ownership proof nor content-eligibility proof.
2. **Inactive/unavailable/expired purchase**. Existing store/sale availability checks and final expired-offer removal remain authoritative.
3. **Symbolic/insufficient commercial attention** or other commercial exclusion. The proposed rule requires `decision_if_moderate.final_disposition == INCLUDE`; a moderate-scenario exclusion stays excluded.
4. **Clearly unreasonable price/value under the existing moderate commercial route**. No strong-only 650/750-style exception is borrowed for a below-moderate Taste item.
5. **Weak/ordinary value signal**. `МОЖНО БРАТЬ` and `ЛУЧШЕ ЖДАТЬ` do not trigger the override; only existing `БРАТЬ СЕЙЧАС` does.
6. **Confirmed direct Taste conflict**: `cached_taste.reason_code == exclude_direct_conflict` remains excluded even when wishlist + current deal are strong.
7. **Truthful risk/explanation visibility**. Existing grounded negative findings, practical risks and scoring penalties must remain present. Wishlist must never delete or soften them.
8. **Negative-analysis readiness**. Today the cache-hit EXCLUDE path exits before the INCLUDE branch can queue `resolve_grounded_negative_analysis`. If a weak item becomes eligible through this override and its grounded-negative analysis is not ready, it must enter the existing negative-backfill work path and must not be treated as fully ready merely because it is wishlisted.
9. Giveaway logic and Epic/GOG RU-availability logic are completely out of scope.

## 7. Eligibility vs ranking

The requested change should affect **eligibility only**.

No ranking redesign is required:

- keep the existing wishlist ranking bonus exactly as it is;
- keep normalized Taste factors / legacy fit scoring unchanged;
- keep risk penalties unchanged;
- keep final priority order unchanged.

Once an override row is legitimately eligible, it may naturally receive the same existing wishlist score bonus as any other wishlist row. No additional override-specific ranking points should be added.

`priority_ranking.py` already tolerates an unknown/non-listed coarse fit by giving no legacy coarse-fit points, and normalized factors remain available independently. There is no need to relabel the item as `moderate` merely to make ranking work.

## 8. Regression plan

Focused minimum cases for IMPLEMENT:

1. **wishlist + genuinely good deal + ordinary weak Taste**
   - wishlist `true`;
   - reason `exclude_insufficient` (also cover `exclude_audited_below`);
   - moderate scenario `INCLUDE` + `БРАТЬ СЕЙЧАС`;
   - expected: purchase-context row exists, explicit override provenance exists, visual row is present, original Taste remains `EXCLUDE/below_moderate`.

2. **wishlist + weak/ordinary deal + weak Taste**
   - wishlist `true`;
   - weak Taste;
   - moderate scenario is excluded **or** purchase decision is `МОЖНО БРАТЬ` / `ЛУЧШЕ ЖДАТЬ`;
   - expected: no guaranteed override; existing exclusion remains.

3. **non-wishlist + weak Taste**
   - identical good commercial scenario but wishlist `false`;
   - expected: existing weak-Taste exclusion unchanged.

4. **wishlist + good deal + direct conflict**
   - `reason_code == exclude_direct_conflict`;
   - expected: excluded; ledger flattening to `below_moderate_fit` must not accidentally permit it.

5. **wishlist override + confirmed non-hard risks**
   - eligible ordinary weak row with structured grounded negatives;
   - expected: risk codes/text/provenance and risk penalty remain; nothing is erased by override.

6. **wishlist override + negative analysis not ready**
   - expected: existing `resolve_grounded_negative_analysis` work is retained/queued; row is not silently treated as risk-ready.

7. **commercial protection**
   - record/near-record but `decision_if_moderate.final_disposition == EXCLUDE` (symbolic/price gate);
   - expected: excluded.

8. **expiry protection**
   - accepted override becomes expired before visual build;
   - expected: existing expired-family/offer removal still removes it.

9. **strong/moderate existing Taste-positive rows**
   - expected: byte/semantic behavior unchanged except any explicitly added neutral provenance field where applicable; no changed score/priority rules.

10. **ranking regression**
    - verify `config/final_ranking_policy.json` / `scripts/priority_ranking.py` unchanged and existing wishlist + risk scoring still applies after eligibility.

## 9. Exact implementation files

Minimum production/code/contract surface for a bounded IMPLEMENT:

1. `config/mailing_policy.json`
   - add the canonical explicit wishlist-good-deal eligibility exception **outside the price-blind Taste evaluation itself**;
   - keep wishlist non-evidence for Taste and ownership;
   - update the old rule that currently says wishlist never bypasses Taste.
   - Prefer a dedicated top-level eligibility field rather than changing `taste_profile`, `taste_deal_separation`, `personal_filter`, `false_negative_audit`, or `taste_factor_semantics`; those fields are part of the Taste semantic cache digest in `config/taste_cache_entry_contract.json`, while this override should not rewrite/invalidate price-blind Taste verdict semantics.

2. `config/deal_quality_contract.json`
   - remove/update only the implementation-contract assertions that currently state weak Taste can never be rescued by discount / below-moderate can never be promoted;
   - define the exception by reference to the existing moderate scenario + existing `БРАТЬ СЕЙЧАС`, without adding a new threshold.

3. `scripts/build_pre_ai_chatgpt_payload.py`
   - replace the unconditional cache-hit EXCLUDE `continue` with the bounded guard above;
   - emit explicit override provenance;
   - preserve original Taste verdict/fit/reason/factors;
   - route eligible override rows through the existing negative-analysis readiness/backfill path;
   - use `decision_if_moderate` as the commercial scenario for the override.

4. `scripts/build_visual_feed_v2.py`
   - stop treating `strong/moderate` as the only possible visibility proof when an explicitly validated `wishlist_good_deal` override marker is present;
   - for override rows use `deal_if_moderate` while rendering the real `below_moderate` Taste fit/provenance, not a fabricated moderate fit.

5. Focused regression coverage: add one bounded test/validator dedicated to this eligibility contract (recommended path: `scripts/test_wishlist_good_deal_override.py`) and wire it into the pre-AI/daily-visual validation path that owns these producers. Do not modify ranking implementation tests except to assert ranking code/policy remains unchanged semantically.

Documentation that should be updated in the same IMPLEMENT because it currently states the opposite user rule:

- `PROJECT_RULES.md` wishlist section.

Files that should **not** need semantic/code changes:

- `scripts/priority_ranking.py`;
- `config/final_ranking_policy.json`;
- Taste evaluator/ingest semantics (`scripts/ingest_taste_results.py`, Taste factor weights, Taste thresholds);
- giveaway/Epic/GOG paths.

## 10. Taste Review requirement

**Yes — mandatory before final acceptance.**

`DIRECTOR_REVIEW_CHECKPOINTS.md` explicitly requires independent Taste Review for material changes to Taste eligibility and wishlist-vs-Taste priority/eligibility semantics. Reviewer advice remains advisory; it must not be auto-converted into policy.

Acceptance sequence for IMPLEMENT should therefore be:

1. implement bounded eligibility exception + focused tests;
2. run technical regression/contract validation;
3. obtain independent current Taste Review specifically on the new wishlist-vs-weak-Taste eligibility semantics and the `exclude_direct_conflict` protection;
4. only then final acceptance if both technical checks and required review pass.

## 11. One bounded IMPLEMENT plan

1. Add one canonical `wishlist_good_deal_override` eligibility rule to `config/mailing_policy.json`, defined entirely from existing signals: wishlist membership + ordinary below-moderate cache reason + `decision_if_moderate == INCLUDE` + `БРАТЬ СЕЙЧАС`; update the conflicting implementation assertions in `config/deal_quality_contract.json` and the durable wishlist rule in `PROJECT_RULES.md`.
2. In `scripts/build_pre_ai_chatgpt_payload.py`, introduce one helper/guard for that rule at the current cache-hit Taste exclusion point. Keep original Taste state, emit explicit override provenance, select the moderate deal scenario, and reuse the existing grounded-negative readiness/backfill path.
3. In `scripts/build_visual_feed_v2.py`, accept that explicit override provenance as an alternate **eligibility proof only**, still require the moderate scenario to be included, and render/score with the genuine underlying Taste data rather than promoting it to moderate.
4. Add focused regression coverage for the ten cases above and wire it into the existing producer validation path. Do not touch final ranking semantics.
5. Run technical validation, then require independent Taste Review before final acceptance.

This is one bounded feature path; no parallel ranking implementation, second Taste state, new discount threshold, giveaway work, Epic/GOG work, or history archaeology is needed.

## 12. Exact refs

Primary refs inspected:

- `WORKER_TASK_WISHLIST_GOOD_DEAL_OVERRIDE_RECON_01.md`
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `PROJECT_ROUTES.md`
- `PROJECT_RULES.md`
- `USER_TASTE_PROFILE.md`
- `DIRECTOR_REVIEW_CHECKPOINTS.md`
- `config/mailing_policy.json`
  - `taste_profile`
  - `taste_deal_separation`
  - `personal_filter`
  - `pricing`
  - `pipeline`
- `config/content_eligibility_contract.json`
- `config/deal_quality_contract.json`
  - `commercial_visibility_gate`
  - `user_price_tolerance`
  - `history_quality`
  - `purchase_decision`
- `config/final_ranking_policy.json`
  - `eligibility_boundary`
  - existing wishlist score component
- `config/taste_cache_entry_contract.json`
  - `taste_semantics_policy_fields`
- `config/taste_ledger_contract.json`
  - `cache_reason_code_semantics`
- `scripts/build_pre_ai_deal_scenarios.py`
  - `build_gate()`
  - `decision_if_strong`
  - `decision_if_moderate`
- `scripts/build_pre_ai_chatgpt_payload.py`
  - `load_wishlist()`
  - `deal_excludes_even_if_strong`
  - cache-hit `cached_taste['verdict'] != 'INCLUDE'` removal
  - existing negative-readiness/backfill branch
- `scripts/process_taste_inbox.py`
  - `rebuild_taste_consumers()`
- `scripts/ingest_taste_results.py`
  - `validate_verdict_shape(...)`
  - direct-conflict evidence requirement
- `scripts/taste_cache_common.py`
  - `validate_verdict_shape(...)`
- `scripts/taste_negative_contract.py`
  - `negative_readiness(...)`
  - `structured_grounded_risks(...)`
- `scripts/build_visual_feed_v2.py`
  - `get_fit(...)`
  - prepared-row `fit in {'strong','moderate'}` gate
  - deal-scenario gate
- `scripts/build_daily_visual_payload.py`
  - expired-offer/family removal and risk enrichment
- `scripts/build_final_visual_payload.py`
  - card explanation/risk refresh and canonical final ranking handoff
- `scripts/priority_ranking.py`
  - existing scoring only; no proposed semantic change
- `.github/workflows/build-daily-visual-payload.yml`
  - final visual validation/producer path

No broad historical search was performed.

## Status

`complete`
