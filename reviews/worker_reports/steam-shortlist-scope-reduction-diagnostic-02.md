# Steam shortlist scope reduction diagnostic 02

Status: `diagnostic_complete_recommendation_ready`

Task: `WORKER_TASK_STEAM_SHORTLIST_SCOPE_REDUCTION_DIAGNOSTIC_02.md`

Mode: `READ-ONLY / DIAGNOSTIC / OFFLINE SIMULATION`

## 1. Executive conclusion

The Reviews/publication repair exposed the real shortlist; it did not make review thresholds looser.

The clean same-source comparison around the Reviews fix is:

| Metric | Broken Reviews | Healthy Reviews |
|---|---:|---:|
| Source rows | 97,998 | 98,015 |
| Unique paid eligible | 60,624 | 60,631 |
| Global review AppIDs OK | 147 | 60,484 |
| Russian review AppIDs OK | 147 | 60,484 |
| Broad shortlist | 28 | 7,972 |
| Paid shortlist | 504 | 2,522 |
| Review circuit open | yes | no |

The source universe changed by only +7 eligible identities, while the paid shortlist grew by +2,018. The pre/post shortlist indexes use the same `personal-calibrated-v1` review profile and the exact same threshold map. Therefore the growth is restored review evidence, not weakened review standards.

The historical ~609 state is not an apples-to-apples target. The older completed funnel was about:

`12,977 raw -> 9,923 review candidates -> 1,615 broad -> 609 shortlist/mailing`.

Current discovery is about 98k raw / 60.6k paid-eligible. Returning to ~609 by making Reviews unavailable again would recreate the defect.

The current expensive semantic scope is already smaller than 2,522:

`2,522 shortlist offers -> 2,469 after mechanical exclusions -> 2,385 purchase families -> 2,301 current semantic families`.

The 84 deterministic pre-AI exclusions are:
- 66 `deal_excludes_even_if_strong`;
- 18 `package_member_taste_pending`.

Current Deep target is 2,301. Canonical Deep state reports:
- 112 authoritative fit;
- 13 authoritative not-fit;
- 18 incomplete/recovery;
- 2,141 waiting for Dossier;
- 17 ready/pending.

The fresh Dossier snapshot prepares 2,134 required dossiers.

### Main finding

A permanent deterministic cut from 2,301 to 300–600 is **not low-risk**.

The current pool contains many genuine Deep-fit games whose Steam-side deterministic features are weak. To test future false-negative risk, the simulated gates were reapplied to the 112 current Deep-fit games **without** allowing “already known Deep-fit” to protect them:

- conservative ~1,000 first-wave gate: 33 / 112 naturally pass (29.5%);
- balanced ~581 first-wave gate: 23 / 112 naturally pass (20.5%);
- aggressive ~240 gate: 10 / 112 naturally pass (8.9%).

So the correct recommendation is **not** to turn ~581 into permanent eligibility.

Recommended architecture:

1. preserve the full canonical paid shortlist/family universe;
2. activate roughly **500–600 candidates as the first semantic wave** using transparent deterministic gates and protected lanes;
3. keep the remaining candidates as **deferred reserve**, not excluded/not-fit;
4. after the frozen 60/40 two-stage Deep architecture is actually production-active, let GitHub stop promoting reserve candidates only when a mathematically valid maximum possible total score proves they cannot beat the current top-100 cutoff.

This gives the largest immediate workload reduction with the smallest principled risk of losing a future top-100 offer.

## 2. Current canonical funnel

| Stage | Count |
|---|---:|
| Steam source rows seen | 98,023 |
| Removed non-paid/missing price | 51 |
| Removed discount below 50% | 33,976 |
| Removed price above 4500 KZT | 0 |
| Removed obvious extras | 2,264 |
| Removed software-only | 1,019 |
| Eligible before partition dedupe | 60,713 |
| Unique eligible after dedupe | 60,632 |
| Review candidate AppIDs | 60,485 |
| Global review AppIDs OK | 60,485 |
| Russian review AppIDs OK | 60,485 |
| Broad shortlist | 7,972 |
| Paid shortlist offers | 2,522 |
| Family candidates after mechanical exclusions | 2,469 |
| Purchase families / taste subjects | 2,385 |
| Deterministically excluded before AI | 84 |
| Current semantic / Deep coverage target | 2,301 |
| Current Dossier required | 2,134 |

Offer-level content metadata for the 2,522 shortlist:
- game: 2,407;
- package: 55;
- DLC: 60.

Family graph before the final pre-AI exclusions:
- base_game: 2,354;
- edition_family: 2;
- external_base_addon: 9;
- franchise_bundle: 19;
- package_without_candidate_base: 1.

Package preservation must not be inferred only from family type. In the 2,301 semantic contexts, **33 families contain a package/Sub purchase-value lane or package-family identity**.

Current semantic contexts contain **10 DLC/base-support families**. DLC is therefore not a material source of the 2.3k explosion.

## 3. Why the pool expanded

### 3.1 Review completeness was the direct trigger

Fresh pre-fix state:
- 60,624 unique paid eligible;
- only 147 global+Russian review-resolved AppIDs;
- 28 broad shortlist;
- 504 paid shortlist;
- 497 last-known-good rows preserved;
- review circuit open.

Fresh post-fix state:
- 60,631 unique paid eligible;
- 60,484 review-resolved AppIDs;
- 7,972 broad shortlist;
- 2,522 paid shortlist;
- no review failure/circuit problem.

This is the strongest causal evidence. Reviews repaired selection coverage rather than changing eligibility rules.

### 3.2 Current refined routes are individually broad

Offer-level marginal counts (overlap allowed):

| Refined reason | Shortlist offers |
|---|---:|
| strong_fit | 1,323 |
| mainstream_quality | 1,059 |
| exceptional_discount | 973 |
| strong_niche_fit | 955 |
| very_high_rating | 779 |
| high_confidence_adjacent | 159 |
| recent_fit | 108 |
| substantive_content | 54 |

At offer level, 1,054 / 2,522 have exactly one refined reason. The biggest single-reason groups are:
- strong_niche_fit only: 414;
- strong_fit only: 307;
- exceptional_discount only: 142;
- mainstream_quality only: 62;
- very_high_rating only: 61;
- substantive_content only: 36;
- recent_fit only: 32.

At semantic-family level (2,301), the corresponding single-reason total is 947:
- strong_niche_fit only: 396;
- strong_fit only: 260;
- exceptional_discount only: 128;
- mainstream_quality only: 54;
- very_high_rating only: 58;
- substantive_content only: 22;
- recent_fit only: 29.

Also at family level:
- 638 / 2,301 (27.7%) are admitted only through the generic quality/commercial set `mainstream_quality / exceptional_discount / very_high_rating / high_confidence_adjacent`;
- 1,663 / 2,301 have at least one fit-recall route (`strong_fit / strong_niche_fit / recent_fit / substantive_content`).

There is no single threshold whose correction would safely return the pool to ~600.

## 4. Current signal distributions

### Review count — semantic families

| Global reviews | Families |
|---|---:|
| <300 | 10 |
| 300–999 | 348 |
| 1,000–2,999 | 508 |
| 3,000–4,999 | 395 |
| 5,000–9,999 | 420 |
| 10,000–19,999 | 287 |
| 20,000+ | 333 |

A universal 5k floor would destroy a large part of the niche lane.

### Global rating — semantic families

| Rating | Families |
|---|---:|
| <78% | 116 |
| 78–79.9% | 138 |
| 80–84.9% | 477 |
| 85–89.9% | 613 |
| 90%+ | 957 |

The <78 group can still qualify through the canonical global-count + global-or-Russian rating rule. A global-only cutoff would silently break the Russian-rating rescue path.

### Price — semantic family primary offer

| Current price | Families |
|---|---:|
| <=100 RUB | 506 |
| 101–250 RUB | 1,011 |
| 251–500 RUB | 651 |
| 501–650 RUB | 119 |
| 651–750 RUB | 14 |

2,168 / 2,301 are already <=500 RUB. Price is not a useful primary discriminator after the current commercial gate.

### Discount — semantic families

| Discount | Families |
|---|---:|
| 50–59% | 449 |
| 60–69% | 384 |
| 70–74% | 205 |
| 75–79% | 448 |
| 80–89% | 572 |
| 90%+ | 243 |

1,263 / 2,301 are already >=75%. Discount alone cannot safely narrow to the desired band.

### Core-fit tags — semantic families

| core_fit_count | Families |
|---|---:|
| 0 | 611 |
| 1 | 704 |
| 2 | 693 |
| 3 | 227 |
| 4+ | 66 |

1,315 / 2,301 (57.1%) have <=1 core tag. Core count is a strong cost-control signal, but the Deep-fit backtest proves it is not safe as universal final eligibility.

## 5. Protected/current reference set

Within the 2,301 current semantic families:

- Wishlist: 39;
- authoritative current Deep-fit: 112;
- authoritative current Deep-not-fit: 13;
- exact direct-user-rated/reference title matches: 25;
- package/bundle lane: 33;
- DLC/base-support lane: 10;
- `deal_if_moderate.purchase_decision == БРАТЬ СЕЙЧАС`: 181;
- `deal_if_strong.purchase_decision == БРАТЬ СЕЙЧАС`: 189.

The strict “strong commercial opportunity” metric used for retention below is the **moderate-scenario `БРАТЬ СЕЙЧАС`** set of 181. If even moderate fit still produces `БРАТЬ СЕЙЧАС`, it is a strong deterministic purchase opportunity.

Wishlist protection means only: an already discovered/paid-shortlist candidate is not pre-semantic-deferred because of weak generic signals. It does not make Wishlist a discovery source, taste evidence, ownership proof, or final include.

Direct-rated/reference protection is an offline guardrail. It must not automatically convert a known negative user reference into a positive recommendation.

## 6. Offline simulation method

The simulations were run read-only over current canonical:
- `data/production/pre_ai/progressive_candidate_context.jsonl`;
- `data/production/pre_ai/chatgpt_taste_queue.jsonl`;
- `data/production/pre_ai/family_graph.json`;
- `data/cache/progressive_pass2_state.json`;
- current canonical taste-profile titles for direct-reference matching.

No production file, queue, result, ranking, worker, or Scheduled Task was changed.

Review gates preserve current review semantics:
- minimum count remains global review count;
- the rating condition remains global OR bounded Russian rating;
- no missing score is invented.

The strategy counts are observed outputs of transparent gates on the current snapshot. They are not quotas.

## 7. Strategy C — conservative first wave (~1,000)

Protected:
- Wishlist;
- existing authoritative Deep-fit;
- exact direct-rated/reference matches;
- package/bundle lane;
- all current DLC/base-support families;
- all 181 moderate `БРАТЬ СЕЙЧАС`.

Unprotected escape paths:
- strong_niche_fit: core>=2 + >=750 reviews + >=84%;
- strong_fit: core>=2 + >=3k + >=86%, or core>=1 + >=10k + >=88%;
- recent_fit: core>=2 + >=1k + >=84%;
- substantive_content: core>=2 + >=500 + >=82%;
- exceptional_discount: >=85% discount + >=10k + >=88%;
- very_high_rating: >=10k + >=92%;
- mainstream_quality: >=20k + >=90%;
- high_confidence_adjacent: >=20k + >=92%.

Observed result:
- **1,000** families;
- reduction: 56.5%;
- Wishlist: 39 / 39;
- current Deep-fit: 112 / 112;
- direct-rated/reference: 25 / 25;
- moderate `БРАТЬ СЕЙЧАС`: 181 / 181;
- package/bundle lane: 33 / 33;
- DLC: 10 / 10;
- strong_niche_fit: 550 / 905;
- low-volume (<5k reviews) strong_niche: 321 / 648;
- unresolved semantic work retained: ~885.

### Future-fit proxy

Remove “existing Deep-fit” from the protection rule and ask whether the same deterministic features would have admitted the current 112 Deep-fit games as if they were new:

- 33 / 112 retained = **29.5%**;
- Deep-not-fit retained: 3 / 13.

Conclusion: acceptable as a first wave, not safe as permanent eligibility.

## 8. Strategy B — balanced first wave (~581) — recommended

Protected:
- Wishlist;
- existing authoritative Deep-fit;
- exact direct-rated/reference matches;
- package/bundle lane;
- all 181 moderate `БРАТЬ СЕЙЧАС`;
- all 10 current DLC/base-support families.

Unprotected escape paths:
- strong_niche_fit:
  - core>=3 + >=300 reviews + >=86%; OR
  - core>=2 + >=5k + >=91%;
- strong_fit:
  - core>=3 + >=7k + >=92%;
- recent_fit:
  - core>=3 + >=1.5k + >=89%;
- substantive_content:
  - core>=2 + >=1k + >=87%;
- exceptional_discount:
  - >=90% discount + >=30k + >=94%.

No standalone `mainstream_quality`, `very_high_rating`, or `high_confidence_adjacent` escape remains. Those generic routes survive only through a protected lane or overlap with a stronger fit/niche route.

Observed result:
- **581** families;
- reduction: 74.8%;
- Wishlist: 39 / 39;
- current Deep-fit: 112 / 112;
- direct-rated/reference: 25 / 25;
- moderate `БРАТЬ СЕЙЧАС`: 181 / 181;
- package/bundle lane: 33 / 33;
- DLC: 10 / 10;
- strong_niche_fit: 335 / 905;
- low-volume strong-niche: 165 / 648;
- unresolved semantic work retained: ~468.

### Future-fit proxy

Without the historical Deep-fit protection:
- 23 / 112 current Deep-fit naturally pass = **20.5%**;
- Deep-not-fit naturally pass: 1 / 13.

Conclusion: **good first-wave size, unsafe permanent cutoff**.

The low-volume niche escape is intentional: core>=3 candidates can survive from only 300 reviews if rating quality is strong. This avoids turning popularity into the primary taste proxy.

## 9. Strategy A — aggressive stress test (~240)

Protected:
- Wishlist;
- existing authoritative Deep-fit;
- direct-rated/reference;
- package/bundle lane.

Unprotected:
- `БРАТЬ СЕЙЧАС`: only core>=3 + >=3k + >=90%;
- DLC: only core>=3 + >=1.5k + >=90%;
- strong_niche_fit: core>=4 + >=1k + >=90%, or core>=3 + >=5k + >=92%;
- strong_fit: core>=4 + >=5k + >=92%;
- recent_fit: core>=4 + >=2.5k + >=90%;
- exceptional_discount: >=90% + >=30k + >=94%.

Observed result:
- **240** families;
- reduction: 89.6%;
- Wishlist: 39 / 39;
- current Deep-fit: 112 / 112;
- direct-rated/reference: 25 / 25;
- package lane: 33 / 33;
- moderate `БРАТЬ СЕЙЧАС`: 19 / 181;
- DLC: 1 / 10;
- strong_niche_fit: 109 / 905;
- low-volume strong-niche: 29 / 648.

Future-fit proxy without historical Deep-fit protection:
- 10 / 112 = **8.9%**;
- Deep-not-fit: 0 / 13.

Conclusion: high recall loss. Reject as default.

## 10. What contributes most to the explosion

The dominant pattern is not “too many DLC” or “too many bundles”:
- only 10 semantic DLC/base-support families;
- only 33 semantic package/bundle-value families.

The main drivers are:
1. broad `strong_fit` and `strong_niche_fit` recall routes;
2. generic quality/commercial standalone routes;
3. low core-tag requirements;
4. restored review coverage that now allows those routes to evaluate correctly.

The pool also cannot be reduced safely by ordinary commercial tightening alone:
- 94.2% of semantic families are already <=500 RUB;
- 54.9% already have >=75% discount;
- 41.6% already have >=90% global rating.

This means the next reduction must change **semantic work admission**, not merely price/discount or Reviews.

## 11. Why permanent deterministic 300–600 is rejected

Canonical policy already says reviews, popularity, discount, generic tags, and shortlist flags are recall/quality signals rather than personal Taste evidence.

The Deep-fit proxy confirms that boundary empirically.

A permanent balanced 581 gate would preserve all **known** Deep-fit only because existing Deep-fit is explicitly protected. For a new future game with no prior Deep result, the deterministic rule naturally recalls only ~20.5% of the current Deep-fit reference set.

That is too weak to claim “minimal risk of losing future top 100.”

Therefore the first-wave/reserve distinction is essential.

## 12. Recommended design

### 12.1 Preserve full canonical source truth

Keep:
- the complete current paid shortlist;
- family resolution;
- current Reviews health;
- package identities;
- all reserve candidates.

Do not rewrite the Steam collector into a hard 581 source shortlist.

### 12.2 Build an active first semantic wave

Use the balanced gate to mark roughly 500–600 current families as `active_first_wave`.

The rest become `deferred_reserve`, not excluded.

Every row gets deterministic admission/defer reason codes.

### 12.3 Preserve protected lanes

The first wave must not crowd out:
- Wishlist already inside current paid candidates;
- current compatible authoritative Deep-fit;
- package/bundle lane;
- direct reference guardrails;
- strict `БРАТЬ СЕЙЧАС`;
- current tiny DLC/base-support lane.

Protected-lane membership never becomes taste proof.

### 12.4 Promote reserve rather than delete it

Reserve remains owned by GitHub.

No ChatGPT worker chooses the next candidate and no new independent scheduler/retry manager is introduced.

A later contract must define how the existing GitHub producer promotes reserve candidates.

### 12.5 Safe stopping after the two-stage 60/40 cutover

The frozen target architecture defines:
- Deep calibrated fit: 0–56;
- Wishlist: deterministic 0/+4;
- personal: 0–60;
- purchase: 0–40;
- total: 0–100.

Only after that model and its final-ranking authority are production-active can GitHub use a mathematically valid upper bound.

For an unprocessed reserve candidate:
- non-Wishlist maximum total = current deterministic purchase score + 56;
- Wishlist maximum total = purchase score + 60 (Wishlist should already be first-wave protected).

After there are at least 100 fully calibrated eligible candidates, a reserve candidate can be safely left unprocessed only when its maximum possible total cannot beat the current #100 cutoff under the active ranking contract.

This is not arbitrary top-N. It is branch-and-bound using the score ceiling.

If an item can still mathematically beat #100, it must remain promotable for semantic analysis.

### Activation boundary

Do not use this score-bound stopping against current legacy `FAST-DOSSIER-DEEP-V1` merely because the new architecture is frozen. Current production authority remains unchanged until the separate integration/cutover task activates the new model.

## 13. Product/Director choices

The diagnostic itself is complete. Before implementation, Director/user should explicitly accept:

1. **First-wave + reserve semantics** rather than permanent pre-semantic exclusion.  
   Recommended: yes.

2. **All 181 current moderate-scenario `БРАТЬ СЕЙЧАС` opportunities protected in the first wave.**  
   Recommended: yes. The aggressive alternative drops 162 / 181.

3. **All package/bundle lanes protected.**  
   Recommended: yes. Only 33 semantic families; not a meaningful cost driver.

4. **Current DLC lane retained until owned-library/base-game support is available.**  
   Recommended: yes. Only 10 semantic families; pruning them does not solve the scale problem.

5. **Low-volume niche escape retained.**  
   Recommended: yes. Do not impose a global 5k/10k popularity floor.

6. **Score-bound permanent stopping activated only after two-stage 60/40 cutover.**  
   Recommended: yes.

No product choice should restore the old small pool by damaging review coverage.

## 14. Smallest follow-up implementation task

After acceptance, create one bounded contract-first implementation task:

`WORKER_TASK_STEAM_SEMANTIC_FIRST_WAVE_AND_RESERVE_IMPLEMENT_01.md`

Scope:
1. define `active_first_wave` and `deferred_reserve` in a canonical GitHub-owned semantic-scope contract;
2. keep the full 2,522 paid shortlist/family graph as source/audit truth;
3. implement the balanced first-wave predicate with explicit admission/defer reason codes;
4. preserve protected-lane invariants;
5. do not mark reserve as not-fit;
6. add funnel counters for full semantic universe / active first wave / reserve and per-rule reasons;
7. run shadow-mode comparison before authoritative cutover;
8. add a regression that evaluates the gate both with and without existing-Deep protection so future-fit proxy recall remains visible;
9. do not activate score-bound stopping until the two-stage integration/cutover has made the 60/40 score/ranking authority active.

Architecture preflight:
- owner remains GitHub control plane;
- scope/order remain GitHub responsibilities;
- no ChatGPT-owned queue;
- no new scheduler/retry owner;
- canonical contract must be updated before the new active/reserve semantics become authoritative.

Do not combine this implementation with ЧАТ 2’s Deep-logic implementation.

## 15. What was not changed

This diagnostic did not:
- change Steam discovery;
- change review thresholds;
- change shortlist data;
- change Dossier/Deep queues or results;
- change ranking;
- run semantic workers;
- change Scheduled Tasks;
- implement hard top-N;
- remove packages/bundles;
- restore broken Reviews behavior.

## 16. Final status

`diagnostic_complete_recommendation_ready`

Concrete recommendation:

**Use ~581 only as the first semantic wave, not permanent eligibility. Keep the remaining ~1,720 families as reserve. After the new 60/40 Deep model is truly active, promote reserve candidates until a mathematical maximum-score bound proves they cannot enter the current top 100.**

This reduces immediate semantic work by about 75% while preserving every currently identifiable Wishlist, authoritative Deep-fit, strict strong-commercial, package/bundle, direct-reference, and current DLC lane—and avoids pretending Steam metadata can safely replace semantic taste analysis.
