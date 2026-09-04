# Taste Review recommendations gap recon 01

## 1. Task

Task ID: `taste-review-recommendations-gap-recon-01`.

Mode: **READ-ONLY / RECON**.
Priority: **VERY_HIGH_USER_PRIORITY**.

This task did not change ranking/Taste code, weights, thresholds, semantic queues, giveaway logic, wishlist behavior, or production data. The only repository write is this required worker report. `CURRENT_TASK.md` / routes were not modified because this worker task explicitly requires READ-ONLY recon/report-only behavior.

Status: `complete`.

## 2. Authoritative Taste Reviewer handoff

Primary authority inspected:

- `reviews/taste_reviews/DIRECTOR_IMPLEMENTATION_HANDOFF_01.md` — `READY_FOR_IMPLEMENTATION`;
- supporting review state only as needed: `reviews/taste_reviews/baseline-01.md`, `reviews/taste_reviews/current-ranking-audit-01.md`, `reviews/taste_reviews/logic-change-handoff-01.md`, `USER_TASTE_PROFILE.md`;
- concurrent/recent reconciliation source: `reviews/worker_reports/wishlist-good-deal-override-recon-01.md`.

The handoff explicitly says **do not resume broad taste questioning** before implementing/regression-testing the already learned rules. This recon therefore inspected current production contracts/code and a bounded set of current controls rather than reopening preference calibration.

The repository has materially evolved since the original review. Several Reviewer recommendations are already implemented partially or fully by later Taste V4 negative-grounding, transparent V2 ranking, package-value, card-explanation, giveaway, and mobile queue-mode work. The remaining implementation should target only the actual current gaps below.

## 3. Recommendation-by-recommendation current-state matrix

| # | Taste Reviewer objective | Current state | Current evidence / exact gap |
|---|---|---|---|
| 1 | Preserve `unknown / insufficient evidence` separately from negative fit | **STILL MISSING — material** | `config/mailing_policy.json` still maps `if_candidate_properties_are_unknown_and_no_direct_or_same_series_anchor` to `below_moderate_fit`. Final decision ledger allows only `INCLUDE/EXCLUDE`; `exclude_insufficient`, `exclude_audited_below`, and `exclude_direct_conflict` all collapse to canonical `below_moderate_fit` in `config/taste_ledger_contract.json`. `build_pre_ai_chatgpt_payload.py` then drops cached `EXCLUDE` rows before purchase context, and `build_visual_feed_v2.py` only prepares `strong/moderate`. Negative-analysis readiness is a separate useful state, but it is **not** a fit-uncertainty/reconsideration state. |
| 2 | Generic feature presence must not automatically become a strong personal-negative | **PARTIALLY SATISFIED** | Later ranking/card work did improve this: derived structural heuristics are mostly low/medium (`management` 3, generic open-world direction 3, puzzle/platform 1), and `card_explanation_policy` hides heuristic-only risks from the player-facing negative block. However Taste-owned V4 findings can still label `directionlessness` or `unchanged_repetition` score 4 with only `{category, code, evidence, risk_text_ru}` and no provenance/depth field proving implementation-specific evidence. `Haven Moon` is a current counterexample: visible diagnostics still show high `directionlessness` and `-10`, although Reviewer calibration says evidence is insufficient for a personal-negative verdict. |
| 3 | Recurring player complaints may establish game-quality risk without automatically becoming Dmitry dislike | **STILL MISSING — representation/plumbing only partial** | The system now has structured grounded-risk plumbing and player-facing provenance, but there is no canonical `game_quality_risk` evidence state distinct from personal Taste risk. Current Taste AI input intentionally forbids review evidence; purchase context contains review percentages, not recurring complaint themes. No current producer/contract was found that validates recurring complaint patterns as candidate-quality evidence while leaving `personal_relevance` unresolved by default. |
| 4 | Historical negative evidence weighted by depth, recency, confidence; old shallow abandon not permanent veto | **PARTIALLY SATISFIED, material gap** | Current direct evidence can use numeric rating and `discussion_confidence`, and a sub-3.5 direct rating can cap a strong modeled fit to moderate. But the current ranking path has no explicit exposure depth, age/recency, `old_shallow`, or `reconsiderable` metadata. `false_negative_audit` also treats direct strong negative as stable unless newer contradictory user evidence exists. Therefore an old short attempt is not literally guaranteed to hard-EXCLUDE forever, but it can remain a durable negative/cap with **no formal decay or reconsideration mechanism**. `BioShock` cannot be represented faithfully as “old shallow negative, credibly reopened.” |
| 5 | Separate personal fit, play role, relative queue priority and commercial urgency | **PARTIALLY SATISFIED — role/queue still missing** | Major later progress exists: V2 score explicitly separates `personal_score` (60) and `purchase_score` (40); urgency is outside the score; mobile UI defaults to `urgency_first=false`, sorting its local automatic queue by `total_score`, and explicitly labels urgency as “сейчас не влияет на порядок”. Users can opt into an urgency-first mode. However there is still **no canonical play-role field** (`main/full`, `secondary/palate-cleanser`, `family/co-op`) and no separate **play/start queue priority**. Production `priority_rank` itself remains `urgency -> total_score -> title`, so when urgency mode is enabled it is purchase-attention priority, not play priority. Role-aware suitability is still collapsed into fit/score. |
| 6 | Paid discount is timing/value evidence and must not rescue confirmed weak/uninteresting fit | **SATISFIED CURRENTLY — preserve** | Taste is explicitly price-blind; price/discount/reviews/wishlist/history are forbidden as positive Taste evidence. `build_pre_ai_chatgpt_payload.py` drops Taste `EXCLUDE` rows; V2 `eligibility_boundary` states score and urgency cannot rescue an ineligible candidate; `deal_quality_contract.json` says deal quality never raises Taste fit. **Do not reimplement or loosen this globally.** |
| 7 | Free giveaways separate from paid purchase recommendation | **SATISFIED — preserve** | Giveaway data is a separate visual sibling/path and does not run through paid purchase ranking. Current giveaway code handles Steam/Epic/GOG acquisition separately. No work from this Taste handoff is needed here. |
| 8 | Bundle value separate; credible bundle may reopen a genuinely reconsiderable/inconclusive series case without overwriting fit | **PARTIALLY SATISFIED** | Package economics are now well separated from Taste: fixed-package scoring is purchase-only; purchase-equivalence explicitly says `affects_taste=false`; excluded package extras are `verified_included_not_personalized`; BioShock original/remaster equivalence is explicit and directional. But the package system operates on **already visible/eligible** games. It cannot reopen an excluded `reconsiderable` candidate because no such eligibility/evidence state exists. Thus “bundle does not manufacture Taste” is implemented; “bundle can close a legitimately reopened BioShock-type case” is not. |
| 9 | Franchise history is weak prior, not hard role cap | **LARGELY SATISFIED at fit/family layer; remaining role behavior belongs to #5** | Current policy requires candidate-specific resolution for mixed same-series evidence and only allows same-series anchors with clear continuity. Family resolution forbids merging only because of a shared franchise word. There is no current hard franchise-to-role cap — mainly because there is no role model yet. Do **not** create a separate franchise implementation task. When role/queue is added, franchise history must remain a prior only, with `TMNT` as regression. |

## 4. Already satisfied items — do not duplicate

The following Reviewer recommendations already work sufficiently and should be treated as invariants during implementation:

1. **Price-blind Taste / no paid-discount rescue of confirmed weak fit.**
   - `config/mailing_policy.json -> taste_deal_separation`;
   - `scripts/ingest_taste_results.py` rejects price/discount/wishlist/review/history evidence in Taste result text;
   - `scripts/build_pre_ai_chatgpt_payload.py` applies commercial context only after Taste and drops cached EXCLUDE;
   - `config/final_ranking_policy.json -> eligibility_boundary` prevents score/urgency rescue.

2. **Personal and purchase score components are explicitly separated.**
   - `scripts/priority_ranking.py` builds separate `personal_score` and `purchase_score` and exposes all components.
   - This is useful and should stay; the missing concepts are role/start-priority, not another hidden 0–100 formula.

3. **Commercial urgency is already visibly disentangled better than in the original audit.**
   - Production `priority_rank` remains urgency-first, but `web/app.js` defaults `urgency_first=false` and sorts the local queue by `total_score`;
   - UI explicitly says urgency “сейчас не влияет на порядок” when off.
   - Therefore the original “Terminator rank 4 looks like top personal recommendation” problem is **partially mitigated in the default current mobile experience**. Do not redo this as if no work happened.

4. **Generic derived risk hypotheses were softened and player-facing risk is grounded.**
   - `scripts/refine_visual_ranking.py` keeps most generic structural hypotheses low/medium;
   - `scripts/card_explanation_policy.py` does not show heuristic-only risks as confirmed negatives;
   - `scripts/build_final_visual_payload.py` preserves a distinction between scoring candidates and grounded visible explanation.
   - Remaining work is to strengthen **semantic evidence provenance**, not to delete all hypothesis/risk plumbing.

5. **Structured negative readiness exists.**
   - V4 negative findings and `negative_analysis_ready` fail closed rather than fabricating a negative.
   - This should be reused, not replaced. It solves “is a grounded negative analysis complete?”, but not “is personal fit unknown vs negative?”.

6. **Free giveaways are separate.** No implementation work from this handoff.

7. **Fixed-package commercial value is separated from Taste.**
   - `scripts/apply_fixed_package_purchase_options.py`, `config/purchase_equivalence_overrides.json`, `scripts/priority_ranking.py` already enforce purchase-only package semantics.
   - Do not rewrite package scoring just to implement BioShock reconsideration.

8. **Franchise identity is not guessed into family/Taste equivalence.**
   - Keep exact/candidate-specific same-series logic and explicit purchase-equivalence rules.

## 5. Still-missing items

The nine Reviewer objectives reduce to **three real implementation gaps**, not nine separate projects.

### Gap A — Evidence state, evidence strength and reconsideration semantics

This is the prerequisite gap and should be implemented first.

Current problem:
- “not enough evidence” is ultimately an `EXCLUDE/below_moderate` result;
- “confirmed direct conflict” is also an `EXCLUDE/below_moderate` result at canonical ledger level;
- negative findings do not record enough evidence provenance to distinguish a store-description hypothesis, recurring implementation complaint, direct user reaction, rich title inspection, or old shallow historical experience;
- old historical negative evidence has no formal depth/recency/reopen semantics.

Required product state, without creating a second ranking authority:

```text
personal_fit: strong | moderate | below_moderate (when actually known)
fit_evidence_state: sufficient | insufficient | reconsiderable | confirmed_negative
```

Names are implementation choices, but the distinction is mandatory. A third state must be able to survive downstream without pretending to be positive or negative.

Also needed:
- historical evidence metadata: exposure depth, recency/age, explicitness/confidence, and reopened-interest/reconsideration state;
- candidate-quality issue evidence distinct from personal dislike;
- strong personal-negative scores allowed only when the evidence contract proves adequate personal relevance / title-specific depth.

`Haven Moon` is the primary control for `insufficient`; `BioShock` for `reconsiderable`; `HighFleet` for a real direct/richer negative that must **remain** strong.

### Gap B — Play role and relative start/queue priority

Current final deal score is useful but cannot represent:
- `Trine 4` = family/co-op positive;
- `Tails of Iron 2` = secondary/palate-cleanser;
- `High On Life` = full/main candidate but only moderate start priority;
- `Sifu` = strong near-term main-game priority.

The existing current UI urgency toggle already separates commercial deadline attention reasonably well; therefore the missing implementation should **not** be “another global sort formula.” It should add producer-owned semantic fields for:

```text
play_role: main_full | secondary_palate_cleanser | family_coop | unresolved
relative_start_priority: high | ordinary | low | unresolved
role_confidence / provenance
```

Exact enum names may differ, but role must not be inferred from the final purchase score or franchise name. The existing canonical deal `priority_rank` may remain purchase-attention order, provided UI/diagnostics do not present it as play/start priority and the new role/start fields are visible/usable separately.

### Gap C — Commercial bridge for explicitly reconsiderable cases, then wishlist-good-deal

Only after Gap A exists should commercial value be allowed to affect an **eligibility exception/reconsideration outcome**.

Two cases need the same boundary:

1. **BioShock-style bundle:** later quality evidence has already moved an old shallow negative to `reconsiderable`; then credible bundle value may make purchase worthwhile. Bundle value must not itself create that reconsideration state.
2. **Wishlist + genuinely good deal:** explicit wishlist interest plus a genuinely good current deal may bypass the ordinary weak/insufficient Taste gate, but only when the underlying state is **non-confirmed-negative**.

The existing commercial `good deal` signal from `wishlist-good-deal-override-recon-01.md` remains a good bounded reuse point:

```text
decision_if_moderate.final_disposition == INCLUDE
AND decision_if_moderate.purchase_decision == "БРАТЬ СЕЙЧАС"
```

No new hidden discount threshold is needed.

However, the prior report's provisional reason-code predicate must be **refined before IMPLEMENT**. Current raw reason codes are too coarse for the new Reviewer semantics:
- `exclude_direct_conflict` is always non-overridable;
- `exclude_audited_below` must not be assumed automatically safe to override until the evidence-state implementation says whether it is merely inconclusive or actually confirmed weak;
- `exclude_insufficient` should become an explicit non-negative insufficiency state rather than being used as a proxy forever.

The future override should therefore key on the new evidence state (`insufficient` / genuinely `reconsiderable`, or equivalent) plus the existing good-deal signal, **not simply on all current below-moderate reason codes**.

## 6. Current-list / user-impact assessment

Current ranking lookup manifest contains **442 visible paid items**.

The remaining gaps have real current effects, but later UI changes alter how some original audit examples should be interpreted:

### `Haven Moon` — current material mismatch remains

Current diagnostics:
- total score `40.6`;
- personal score `22.6`;
- `fit=moderate`;
- high `directionlessness` risk;
- risk penalty `-10`.

Reviewer calibration says the correct state is **insufficient evidence / needs richer inspection**, not confirmed negative fit. This is the clearest current-list example that Gap A is still material.

### `Terminator: Resistance` — production urgency issue is partially mitigated in UI

Production diagnostics still show:
- `priority_rank=4`;
- total `65.0`;
- personal `33.0`;
- `sale_expiry_urgency=today`.

But current mobile default has `urgency_first=false`; its normal automatic queue sorts by `total_score`, and the UI labels urgency as not affecting current order. Therefore production rank 4 should **not** be described as the default current mobile queue position anymore.

The remaining Reviewer gap is that `Terminator` has no explicit “ordinary queue” / main-game-role semantic field; its purchase urgency and play priority are still different concepts with no shared canonical representation.

### `High On Life`

Current diagnostics show personal `47.0`, total `68.0`, wishlist present, strong fit, ordinary/later urgency. In default score-first mobile mode it can naturally sit above lower-score urgent items. This is evidence that the urgency display problem has already been partially corrected.

Still missing: a canonical `full/main + moderate queue priority` state rather than inferring role from score.

### `Tails of Iron 2`

Current diagnostics show a strong personal/taste score and a good purchase verdict, but there is no `secondary/palate-cleanser` role field. The current scalar score cannot preserve the Reviewer's calibrated role distinction.

### `TMNT: Splintered Fate`

Production urgency mode can place it very high (`priority_rank=7`) while its personal score is much lower and it carries a serious risk. Default mobile score mode reduces this distortion. Remaining work is not another franchise penalty: it is explicit unresolved-role / cautious-prior semantics so old TMNT history cannot silently become a role cap.

### `BioShock`

Current package implementation is commercially sophisticated and includes explicit original/remastered purchase equivalence, but only already-visible games can drive personalized package value. The system still lacks “old shallow negative -> reconsiderable -> bundle can matter” as an eligibility/evidence path.

### Historical old-attempt impact

Current code does **not** prove that every old short failure becomes a hard veto. The narrower confirmed issue is:
- rating/history can remain a durable direct negative or strong->moderate cap;
- there is no age/depth attenuation;
- no `reconsiderable` state exists;
- direct strong negative audit has a stable-skip rule unless newer contradictory user evidence exists.

That is enough to require Gap A without overstating the defect.

## 7. Wishlist interaction / conflict assessment

The wishlist-good-deal user rule and Taste Reviewer rules are compatible **only if the order is explicit**:

```text
1. determine price-blind personal fit + evidence state;
2. preserve confirmed negative/direct conflict as non-overridable;
3. identify explicit non-negative insufficiency/reconsideration;
4. evaluate existing commercial deal quality;
5. allow a bounded wishlist-good-deal eligibility exception only for that non-negative state;
6. preserve original Taste/evidence/risk provenance in ranking/card output.
```

This avoids the contradiction “discount cannot rescue confirmed weak fit” vs “wishlist + good deal may bypass ordinary Taste eligibility.”

Wishlist is an explicit **interest/context signal**, not Taste proof. The good deal is a **commercial trigger**, not a fit upgrade. The override must never mutate `below_moderate` to fake `moderate`, erase risks, or bypass content/store/budget/commercial gates.

Important reconciliation with `wishlist-good-deal-override-recon-01.md`:
- keep its existing `good deal` signal (`moderate scenario INCLUDE + БРАТЬ СЕЙЧАС`);
- keep `exclude_direct_conflict` non-overridable;
- **do not implement its provisional `{exclude_insufficient, exclude_audited_below}` predicate first**. Gap A should first make insufficient/reconsiderable vs confirmed-negative explicit. Then the wishlist override can consume that stable semantic state safely.

Therefore implementation order should be **Taste evidence-state first, wishlist override later**, even though wishlist recon completed first.

## 8. Exact implementation files / contracts

The current gap should be split into three ordered bounded IMPLEMENT tasks. No parallel ranker and no broad rewrite is required.

### IMPLEMENT 1 — evidence state + evidence strength / historical confidence

Existing canonical files likely requiring semantic changes:

- `config/mailing_policy.json`
  - stop mapping unknown/insufficient directly to a final negative semantic state;
  - define the relationship between personal fit and evidence state;
  - add old/shallow/reconsideration rules.
- `config/taste_result_contract.json`
  - carry the distinct evidence state and stronger negative-evidence provenance/strength requirements.
- `config/taste_cache_entry_contract.json`
  - persist the new semantic fields with exact binding; this is a material Taste-semantic change and should invalidate/re-evaluate affected cache generation deliberately rather than being silently bolted on.
- `config/taste_ledger_contract.json`
  - stop forcing every insufficient/reconsiderable result into an indistinguishable final `below_moderate_fit` exclusion ledger state.
- `scripts/taste_cache_common.py`
- `scripts/taste_negative_contract.py`
- `scripts/ingest_taste_results.py`
- `scripts/build_taste_cache_index.py`
- `scripts/build_pre_ai_taste_projection.py`
- `scripts/build_pre_ai_chatgpt_payload.py`
- `scripts/process_taste_inbox.py`
- `scripts/refine_visual_ranking.py`
- `scripts/card_explanation_policy.py`
- `scripts/build_final_visual_payload.py`

For Reviewer objective #3, add one bounded **candidate-quality evidence** contract/artifact rather than overloading price-blind Taste or review percentage:

- proposed new canonical contract: `config/game_quality_evidence_contract.json`;
- proposed helper/validator: `scripts/game_quality_evidence.py`;
- proposed canonical cache/artifact: `data/cache/game_quality_evidence.json`.

Architecture constraint: this must **not** become a second recurring scheduler or ranking authority. `config/execution_ownership_contract.json` and `config/daily_execution_contract.json` already require GitHub to own exact scope/queue/validation and allow the existing scheduled ChatGPT semantic data plane to obtain external facts only for GitHub-prepared work. An IMPLEMENT must amend/authorize the exact semantic work contract first and reuse the existing nightly cycle. Interactive chat must not collect complaint evidence candidate-by-candidate.

Minimum tests to extend/add:

- `scripts/validate_taste_v3_contract.py`;
- `scripts/test_grounded_negative_contract.py`;
- `scripts/test_card_explanation_policy.py`;
- proposed bounded new regression: `scripts/test_taste_review_evidence_states.py`.

### IMPLEMENT 2 — role + relative start/queue semantics

Files:

- `config/final_ranking_policy.json` — only if the new fields affect canonical scoring/order; do not create a second sort authority;
- preferably a dedicated semantic context contract outside the stable Taste-fit cache, proposed `config/play_priority_context_contract.json`;
- proposed producer/helper `scripts/play_priority_context.py` or equivalent producer-owned enrichment;
- `scripts/build_visual_feed_v2.py`;
- `scripts/build_final_visual_payload.py`;
- `scripts/priority_ranking.py` only if canonical ordering must consume the new field; otherwise leave score weights unchanged and expose role/start priority separately;
- `scripts/build_ranking_lookup.py` so bounded diagnostics expose role/start-priority provenance;
- `web/app.js` to display role/start priority distinctly from sale urgency and purchase score;
- `PROJECT_RULES.md` / `PROJECT_DECISIONS.md` to record the durable distinction if accepted.

Tests:

- `scripts/validate_priority_ranking.py`;
- proposed `scripts/test_taste_review_role_controls.py`;
- existing UI regression for urgency mode must remain green (`urgency_first=false` default, urgency label truthful, manual-end invariant preserved).

### IMPLEMENT 3 — reconsideration commercial bridge + wishlist-good-deal override

Only after IMPLEMENT 1 establishes stable evidence-state semantics.

Files:

- `config/mailing_policy.json`;
- `config/deal_quality_contract.json`;
- `PROJECT_RULES.md` and relevant `PROJECT_DECISIONS.md` entry because current durable wishlist rule explicitly says wishlist never bypasses Taste;
- `scripts/build_pre_ai_chatgpt_payload.py`;
- `scripts/build_visual_feed_v2.py`;
- `scripts/apply_fixed_package_purchase_options.py` only to permit package value to attach to an explicitly reconsiderable case; do not alter purchase equivalence or let package economics create fit;
- `config/purchase_equivalence_overrides.json` should remain purchase-only; semantic rule need not change unless a concrete new explicit equivalence is required;
- no giveaway changes;
- no new final-ranking weights are required merely for wishlist override.

Tests:

- existing `scripts/test_fixed_package_purchase_options.py`;
- proposed `scripts/test_wishlist_good_deal_override.py`;
- combined controls: confirmed weak + huge paid discount remains non-rescuable; reconsiderable + credible bundle may become purchase-worthy; wishlist + good deal only bypasses non-negative insufficient/reconsiderable state.

## 9. Regression / calibrated control plan

Use the existing handoff controls; do not expand the questionnaire.

1. **`Trine 4: The Nightmare Prince`**
   - unresolved/insufficient state must not equal negative fit;
   - confirmed family-play positive must be representable as role context.

2. **`Haven Moon`**
   - description + recurring complaints can create `game_quality_risk` / inspection questions;
   - must remain `insufficient` rather than a confirmed personal `directionlessness` penalty without richer evidence.

3. **`HighFleet`**
   - direct trailer-based dry/technical/tedious reaction remains a strong personal-negative/start-priority control;
   - no generic anti-complexity rule;
   - wishlist/paid discount cannot rescue it merely on price.

4. **`BioShock`**
   - old brief failed attempt carries weaker historical confidence than recent informed rejection;
   - strong later quality/reputation evidence can set `reconsiderable`;
   - bundle value matters only **after** reconsideration; Taste is not rewritten by bundle price.

5. **`Sifu`**
   - strong near-term main-game interest remains high play/start priority independent of sale urgency.

6. **`High On Life`**
   - full/main candidate + moderate play queue is representable;
   - wishlist remains a bounded interest bonus/context, not “play next”.

7. **`Amnesia: The Bunker`**
   - scarcity/resources/threat do not become generic negative feature penalties;
   - main/full + ordinary queue is representable.

8. **`Terminator: Resistance`**
   - moderate ordinary queue with franchise interest;
   - sale urgency can still be shown as commercial urgency without being labeled top personal/play priority.

9. **`Tails of Iron 2`**
   - secondary/palate-cleanser role survives downstream visual output even if raw fit is strong.

10. **`TMNT: Splintered Fate`**
    - franchise positive/cautious history is a prior only;
    - new title remains free to resolve main/secondary based on title-specific evidence.

11. **`RDR2`, `Silent Hill (1999)`, `Hogwarts Legacy` puzzle rooms**
    - anti-monotonic structural controls: open world, puzzles, repetition/management-style structures cannot become blanket negatives.

12. **Commercial invariants**
    - non-wishlist + confirmed weak unchanged;
    - wishlist + ordinary deal + insufficient has no guaranteed override;
    - wishlist + canonical good deal + explicit non-negative insufficiency/reconsideration may pass the bounded eligibility exception;
    - `exclude_direct_conflict` / confirmed negative never bypassed;
    - fixed package remains purchase-only;
    - free giveaway path unchanged and separate.

## 10. Taste Review acceptance requirement

**Independent Taste Review is mandatory before final acceptance.**

`DIRECTOR_REVIEW_CHECKPOINTS.md` requires current Taste Review before acceptance of material changes to:
- Taste eligibility;
- personal-fit scores/weights/order;
- personal-preference thresholds;
- wishlist-vs-Taste semantics.

Recommended cadence:

- run technical/unit/regression validation **after each internal IMPLEMENT step**;
- do **one independent Taste Review after the complete bounded three-step implementation has been regenerated and compared against the calibrated controls**, before final product acceptance;
- do not require a separate Reviewer round after every internal commit if those commits are not independently accepted/deployed as completed product semantics;
- if the Director chooses to accept/deploy one material step independently, then that step becomes its own acceptance boundary and therefore requires its own current Taste Review before that acceptance.

This single post-bounded-implementation review is preferable because Gap A, role semantics, and wishlist/bundle reconsideration interact; reviewing them in isolation would risk approving contradictory intermediate states.

Reviewer output remains advisory. It must not be auto-converted into policy without Director/product acceptance.

## 11. One bounded implementation sequence

Minimal ordered sequence for only the missing work:

### 1. `taste-evidence-state-and-confidence-implement-01`

Implement objectives 1–4 together as one evidence-semantics change:
- explicit `insufficient` / `reconsiderable` vs `confirmed_negative` evidence state;
- negative evidence provenance/strength sufficient to prevent generic feature presence from becoming a strong personal dislike;
- candidate-quality complaint evidence separate from personal dislike;
- historical negative depth/recency/confidence/reopen semantics;
- regress `Haven Moon`, `BioShock`, `HighFleet`, `Trine 4`, `RDR2`, `Silent Hill`, `Hogwarts`, `Amnesia`.

Do not change final ranking weights in this step unless mechanically required to stop an invalid strong penalty. Preserve price-blind Taste and no-discount-rescue.

### 2. `play-role-and-start-priority-implement-01`

Add producer-owned play role + relative start/queue priority separately from fit and commercial purchase urgency:
- main/full vs secondary/palate-cleanser vs family/co-op vs unresolved;
- high/ordinary/low start priority (or equivalent);
- provenance/confidence;
- keep the existing mobile urgency toggle behavior and truthful urgency label;
- do not create a second automatic scorer/sorter.

Controls: `Sifu`, `High On Life`, `Amnesia`, `Terminator`, `Tails of Iron 2`, `Trine 4`, `TMNT`.

### 3. `reconsideration-commercial-bridge-and-wishlist-implement-01`

Reconcile this report with `wishlist-good-deal-override-recon-01.md`:
- bundle value may raise purchase value only for an already explicit `reconsiderable` case;
- wishlist + existing canonical good deal may bypass ordinary weak/insufficient eligibility only for explicit **non-confirmed-negative** state;
- preserve original Taste/evidence state and all risks;
- direct conflict / confirmed weak remains non-overridable;
- reuse `decision_if_moderate INCLUDE + БРАТЬ СЕЙЧАС`; add no new discount threshold;
- leave giveaway and final ranking weights untouched unless a regression proves otherwise.

After step 3: regenerate current production output, run the bounded control suite, compare with baseline/current-ranking audit, then obtain **one independent current Taste Review** before final acceptance.

No separate IMPLEMENT is needed for objectives already satisfied (#6 paid-discount separation, #7 giveaway separation) or for franchise history by itself (#9 is a regression requirement of role semantics).

## 12. Status

`complete`

## 13. Exact refs

Primary/authoritative refs:

- `WORKER_TASK_TASTE_REVIEW_RECOMMENDATIONS_GAP_RECON_01.md`
- `reviews/taste_reviews/DIRECTOR_IMPLEMENTATION_HANDOFF_01.md`
- `reviews/taste_reviews/baseline-01.md`
- `reviews/taste_reviews/current-ranking-audit-01.md`
- `reviews/taste_reviews/logic-change-handoff-01.md`
- `reviews/worker_reports/wishlist-good-deal-override-recon-01.md`
- `USER_TASTE_PROFILE.md`
- `DIRECTOR_REVIEW_CHECKPOINTS.md`

Operational/architecture refs:

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `PROJECT_ROUTES.md`
- `CURRENT_TASK.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`

Current policy/contracts:

- `config/mailing_policy.json`
  - `taste_deal_separation`
  - `personal_filter.structured_taste_evaluation`
  - `decision_ledger`
  - `false_negative_audit`
  - `offer_family_resolution`
- `config/taste_result_contract.json`
- `config/taste_cache_entry_contract.json`
- `config/taste_ledger_contract.json`
- `config/final_ranking_policy.json`
  - `eligibility_boundary`
  - `automatic_final_priority_order`
  - `score_model.personal`
  - `score_model.purchase`
- `config/deal_quality_contract.json`
- `config/purchase_equivalence_overrides.json`
- `PROJECT_RULES.md`
- `PROJECT_DECISIONS.md`

Current producers/consumers/tests:

- `scripts/taste_cache_common.py`
- `scripts/taste_negative_contract.py`
- `scripts/ingest_taste_results.py`
- `scripts/build_taste_cache_index.py`
- `scripts/build_pre_ai_taste_projection.py`
- `scripts/build_pre_ai_chatgpt_payload.py`
- `scripts/process_taste_inbox.py`
- `scripts/build_pre_ai_deal_scenarios.py`
- `scripts/build_visual_feed_v2.py`
- `scripts/refine_visual_ranking.py`
- `scripts/card_explanation_policy.py`
- `scripts/build_final_visual_payload.py`
- `scripts/priority_ranking.py`
- `scripts/apply_fixed_package_purchase_options.py`
- `scripts/build_ranking_lookup.py`
- `scripts/validate_taste_v3_contract.py`
- `scripts/test_grounded_negative_contract.py`
- `scripts/test_card_explanation_policy.py`
- `scripts/validate_priority_ranking.py`
- `scripts/test_fixed_package_purchase_options.py`
- `web/app.js`

Bounded current diagnostics inspected:

- `data/production/visual/ranking_lookup/_manifest.json` — 442 visible items;
- `data/production/visual/ranking_lookup/h.json` — `Haven Moon`, `High On Life`, `HighFleet` vicinity;
- `data/production/visual/ranking_lookup/t.json` — `Tails of Iron 2`, `TMNT: Splintered Fate`, `Terminator: Resistance`.

No broad Git-history archaeology or new Taste questionnaire was performed.
