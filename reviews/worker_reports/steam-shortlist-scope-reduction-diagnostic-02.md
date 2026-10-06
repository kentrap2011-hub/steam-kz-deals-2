# Steam shortlist scope reduction diagnostic 02

Status: `diagnostic_complete_user_choice_required`

Task: `WORKER_TASK_STEAM_SHORTLIST_SCOPE_REDUCTION_DIAGNOSTIC_02.md`

Mode: `READ-ONLY / DIAGNOSTIC / OFFLINE SIMULATION`

## 1. Executive conclusion

The fresh current funnel is healthy and materially larger because Steam review coverage was restored rather than because the paid source universe suddenly grew:

- 98,023 source rows;
- 60,632 unique paid-eligible items after the existing 50% / 4500 KZT gates;
- 7,972 broad-shortlist items;
- 2,522 paid-shortlist rows;
- 2,385 purchase families after family construction, of which 2,301 are in the current semantic context / Deep coverage target;
- current Dossier snapshot prepares 2,134 required dossiers;
- current Deep state contains 112 authoritative current `analyzed_fit`, 13 authoritative current `analyzed_not_fit`, and the rest is unresolved/current work.

The old small state must not be restored. Immediately before PR #155 fixed Reviews, a fresh source run already had 60,624 eligible items but only 147 AppIDs had usable global+Russian review resolution. Its 504-row shortlist was mostly preservation fallback: 497 last-known-good rows were carried forward while 60,481 games were marked problematic. After the Reviews fix, the same-size source universe had 60,484 review-resolved AppIDs, broad shortlist jumped 28 -> 7,972 and paid shortlist 504 -> 2,522. Source eligibility changed by only +7. The expansion is therefore primarily recovery of missing review evidence, not discovery-scope inflation.

The main current shortlist inflation is caused by permissive recall rules that were useful when the pool was smaller:

- `strong_fit`: 1,323 / 2,522 rows;
- `mainstream_quality`: 1,059;
- `exceptional_discount`: 973;
- `strong_niche_fit`: 955;
- `very_high_rating`: 779.

These counts overlap. More diagnostic are the exclusive routes: **1,054 / 2,522 (41.8%) have exactly one refined reason**. Of these, 414 are only `strong_niche_fit`, 307 only `strong_fit`, 142 only `exceptional_discount`, 62 only `mainstream_quality`, 61 only `very_high_rating`, 36 only `substantive_content`, and 32 only `recent_fit`.

Also, **685 / 2,522 (27.2%) are admitted only by commercial/general-quality reasons** (`mainstream_quality`, `exceptional_discount`, `very_high_rating`, `high_confidence_adjacent`) with no stronger taste-oriented recall route, and **654 / 2,522 have core_fit_count = 0**.

The best offline balance is a **semantic pool around 450-500**, not ~100 and not a blind top-N. The tested balanced gate yielded **468 families** while retaining all 39 current Wishlist families, all 112 authoritative current Deep-fit families, all 25 exact direct-user-rated/reference title matches, all 33 package/bundle-value families, all 10 current DLC/addon semantic families, and all 181 families whose moderate deal scenario says `БРАТЬ СЕЙЧАС`.

The tradeoff is real: current `strong_niche_fit` is itself a broad deterministic recall flag, not semantic Taste proof. The balanced simulation keeps 217 / 905 current semantic families carrying that flag, including 105 / 648 low-volume (<5k global reviews) strong-niche families. This is the key recall risk and is why implementation requires explicit user/Director approval plus a shadow false-negative audit before cutover.

## 2. Architecture / ownership boundary

Confirmed owner remains GitHub. `config/execution_ownership_contract.json` assigns candidate scope, deterministic transformations, queues and completeness to the GitHub control plane.

Relevant canonical selection authority is `config/mailing_policy.json` plus the current Steam producer in `scripts/steam_production.py`.

No recommendation here creates:
- a ChatGPT-owned queue;
- a second scheduler;
- a new recurring stage;
- a semantic-worker retry owner;
- a raw top-N discovery cutoff;
- a Reviews failure shortcut.

Any future change to these deterministic admission thresholds is a product-policy change and must update the canonical contract before/with implementation.

## 3. Exact current funnel

Current canonical manifest (2026-10-06 snapshot):

| Stage | Count |
|---|---:|
| Steam source reported / seen | 98,023 |
| Parsed | 98,023 |
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
| Paid shortlist | 2,522 |
| Family candidates after mechanical exclusions | 2,469 |
| Purchase families | 2,385 |
| Current semantic / Deep coverage target | 2,301 |
| Current Dossier prepared required | 2,134 |

The current Reviews circuit is closed and the current 2,522 shortlist rows are publishable without AppReviews fallback. This task does not use missing Reviews as a reduction mechanism.

## 4. Why ~609 / 504 became 2,522

The historical ~609 value is not a valid same-input A/B baseline because it came from an earlier snapshot. The cleanest causal comparison is the fresh run immediately before the Reviews fix versus the first healthy run after it:

| Metric | Pre-fix fresh run | Post-fix healthy run | Change |
|---|---:|---:|---:|
| Source rows | 97,998 | 98,015 | +17 |
| Unique paid eligible | 60,624 | 60,631 | +7 |
| Global+Russian review OK AppIDs | 147 | 60,484 | +60,337 |
| Broad shortlist | 28 | 7,972 | +7,944 |
| Paid shortlist | 504 | 2,522 | +2,018 |
| Last-known-good preserved | 497 | 0 | fallback no longer needed |

Therefore the small pre-fix shortlist was primarily an artifact of review unavailability plus preservation fallback. Returning to it by requiring unavailable Reviews would recreate the bug.

## 5. Current admission-rule contribution

### Marginal refined reason counts

These overlap and therefore must not be summed:

| Refined reason | Current shortlist rows |
|---|---:|
| strong_fit | 1,323 |
| mainstream_quality | 1,059 |
| exceptional_discount | 973 |
| strong_niche_fit | 955 |
| very_high_rating | 779 |
| high_confidence_adjacent | 159 |
| recent_fit | 108 |
| substantive_content | 54 |

### Exclusive single-reason admissions

| Only refined reason | Rows |
|---|---:|
| strong_niche_fit only | 414 |
| strong_fit only | 307 |
| exceptional_discount only | 142 |
| mainstream_quality only | 62 |
| very_high_rating only | 61 |
| substantive_content only | 36 |
| recent_fit only | 32 |
| high_confidence_adjacent only | 0 |
| **Total single-reason** | **1,054** |

This is the most useful explanation of the explosion. The two biggest exclusive admission paths are not mainstream/popularity rules; they are the broad deterministic `strong_niche_fit` and `strong_fit` recall routes.

Current definitions are permissive for a 2.5k pool:
- `strong_fit`: one core tag, >=1,500 global reviews, rating >=78% (global or bounded Russian rescue);
- `strong_niche_fit`: two core tags, price <=2500 KZT, >=300 global reviews, rating >=78%;
- `mainstream_quality`: no taste tag requirement, >=5,000 reviews, >=80%;
- `exceptional_discount`: no taste tag requirement, discount >=75%, >=3,000 reviews, >=75%;
- `very_high_rating`: no taste tag requirement, >=3,000 reviews, >=90%.

Canonical policy already states that these feed flags are recall/audit context rather than semantic Taste evidence. Tightening them before expensive semantic work is therefore conceptually valid, but changes recall and needs explicit approval.

### Structure/type

At shortlist-row level:
- games: 2,407;
- packages: 55;
- DLC: 60.

After family construction/current semantic projection:
- current semantic families: 2,301;
- base-game families: 2,289;
- edition families: 2;
- external-base-addon families: 9;
- package-without-candidate-base family: 1;
- 33 semantic families contain a package/`Sub_` purchase-value lane;
- 10 current semantic families require DLC/addon base-support handling.

Packages are therefore a small, cheap lane to preserve explicitly rather than discard.

## 6. Distribution of current 2,522 shortlist rows

### Global review-count bands

| Reviews | Rows |
|---|---:|
| <300 | 14 |
| 300-999 | 376 |
| 1,000-2,999 | 555 |
| 3,000-4,999 | 431 |
| 5,000-9,999 | 450 |
| 10,000-19,999 | 317 |
| 20,000+ | 379 |

A flat popularity floor such as 5k would remove 1,376 rows but would also destroy a large share of the niche lane. It is not recommended.

### Global rating bands

| Positive rating | Rows |
|---|---:|
| <78% | 130 |
| 78-79.9% | 158 |
| 80-84.9% | 519 |
| 85-89.9% | 686 |
| 90%+ | 1,029 |

A rating-only cutoff is also insufficient: 1,029 rows already sit at 90%+.

### Price bands, KZT

| Price | Rows |
|---|---:|
| <=500 | 455 |
| 501-1000 | 741 |
| 1001-2000 | 843 |
| 2001-3000 | 329 |
| 3001-3500 | 74 |
| 3501-4000 | 60 |
| 4001-4500 | 20 |

Most of the pool is cheap. Lowering price alone would preferentially keep low-cost noise rather than future top-100 quality.

### Discount bands

| Discount | Rows |
|---|---:|
| 50-59% | 517 |
| 60-69% | 414 |
| 70-74% | 224 |
| 75-79% | 485 |
| 80-89% | 618 |
| 90%+ | 264 |

Again, discount alone cannot safely produce the target pool.

### Core fit count

| core_fit_count | Rows |
|---|---:|
| 0 | 654 |
| 1 | 788 |
| 2 | 755 |
| 3 | 253 |
| 4+ | 72 |

This is the strongest deterministic lever. 1,442 / 2,522 rows have at most one current core tag. But core tags are still recall metadata, not semantic proof, so they should be combined with rating/review/value lanes rather than used as a universal exclusion.

## 7. Protected evidence / current semantic reference set

Within the 2,301 current semantic families:

- Wishlist: 39;
- authoritative current Deep-fit: 112;
- authoritative current Deep-not-fit: 13;
- exact direct-user-rated/reference title matches: 25;
- package/bundle-value lane: 33 families;
- DLC/addon semantic lane: 10 families;
- moderate-deal `БРАТЬ СЕЙЧАС`: 181;
- strong-deal `БРАТЬ СЕЙЧАС`: 189.

The offline strategies below protect current Deep-fit, Wishlist, direct-rated/reference and package/bundle lanes by construction. Conservative and balanced also protect all current DLC and all 181 moderate `БРАТЬ СЕЙЧАС` opportunities.

This is deliberately stricter than simply asking whether the new rules would reproduce the current shortlist count.

## 8. Offline reduction strategies

These are diagnostic predicates over current canonical fields. They are **not** proposed as final numeric contract text and were not written to production.

### Strategy C — conservative: ~781 semantic families

Target band: 700-1000.

Protected unconditionally:
- all Wishlist;
- all current authoritative Deep-fit;
- all exact direct-user-rated/reference matches;
- all package/bundle-value families;
- all current DLC/addon semantic families;
- all moderate-scenario `БРАТЬ СЕЙЧАС`.

Remaining candidates need substantially stronger combinations than current rules, approximately:
- `strong_niche_fit`: core >=3 with >=500 reviews / >=82%, or core >=2 with >=2,000 / >=86%;
- `strong_fit`: core >=3 with >=2,500 / >=86%, or core >=2 with >=7,000 / >=88%;
- `recent_fit`: core >=3 and >=1,500 / >=84%;
- `substantive_content`: core >=2 and >=750 / >=84%;
- `exceptional_discount`: >=90% discount plus >=20k / >=90%.

Result:
- **781** families;
- unresolved semantic work: about **667**;
- Wishlist: **39/39 retained**;
- Deep-fit: **112/112 retained**;
- direct-rated/reference: **25/25 retained**;
- package lane: **33/33 retained**;
- DLC: **10/10 retained**;
- moderate `БРАТЬ СЕЙЧАС`: **181/181 retained**;
- current `strong_niche_fit`: **457/905 retained**;
- low-volume (<5k reviews) `strong_niche_fit`: **235/648 retained**.

Risk: moderate. It halves semantic cost versus 2,301 while keeping a broad niche escape path.

### Strategy B — balanced: ~468 semantic families

Target band: 300-600.

Uses the same protected lanes as Strategy C, but the non-protected escape paths are stricter:
- `strong_niche_fit`: primarily core >=3 with stronger review/rating proof;
- `strong_fit`: core >=3 with materially higher review/rating proof;
- pure commercial/general-quality routes do not survive unless they are exceptional enough to compete with protected value lanes.

Result:
- **468** families;
- unresolved semantic work: about **356**;
- Wishlist: **39/39 retained**;
- Deep-fit: **112/112 retained**;
- direct-rated/reference: **25/25 retained**;
- package lane: **33/33 retained**;
- DLC: **10/10 retained**;
- moderate `БРАТЬ СЕЙЧАС`: **181/181 retained**;
- current `strong_niche_fit`: **217/905 retained**;
- low-volume (<5k reviews) `strong_niche_fit`: **105/648 retained**.

Risk: meaningful but bounded and explainable. The dropped `strong_niche_fit` rows are not proven bad games; they are candidates that currently receive a broad deterministic recall flag but lack enough deterministic evidence to justify expensive semantics under the tighter budget.

### Strategy A — aggressive stress test: ~276 semantic families

Target band: 150-300.

Unconditional protection is reduced to:
- Wishlist;
- authoritative Deep-fit;
- direct-user-rated/reference matches;
- package/bundle-value lane;
- current DLC lane (added as a protected lane because it is only 10 families and ownership support is not yet available).

The remaining pool requires very strong deterministic combinations such as:
- `strong_niche_fit` with core >=3, >=2k reviews and >=90%;
- `strong_fit` with core >=3, >=10k and >=92%;
- moderate `БРАТЬ СЕЙЧАС` only with core >=2 plus >=10k / >=90%;
- `exceptional_discount` only at >=90% discount plus >=30k / >=94%.

Result:
- **~276** families;
- Wishlist: **39/39 retained**;
- Deep-fit: **112/112 retained**;
- direct-rated/reference: **25/25 retained**;
- packages: **33/33 retained**;
- DLC: **10/10 retained**;
- moderate `БРАТЬ СЕЙЧАС`: only **26/181** retained before the DLC-protection adjustment (DLC protection does not materially repair this loss);
- current `strong_niche_fit`: about **134/905** retained;
- low-volume strong-niche: about **43/648** retained.

Risk: high. This range can be reached without hard top-N, but only by discarding many currently strong commercial and niche recall candidates. It is not recommended as the production default.

## 9. Why generic commercial routes should be tightened first

A strong reduction should not begin by raising a global popularity floor, because that disproportionately kills niche titles. It should first require stronger evidence when the admission is taste-agnostic.

Recommended order of tightening:

1. remove ordinary `mainstream_quality` as a standalone semantic-admission route unless it clears a much higher quality/popularity bar;
2. require `exceptional_discount` without taste-oriented evidence to be genuinely exceptional (for example 90%+ plus strong quality), rather than 75% discount + 75% rating;
3. make `very_high_rating` / `high_confidence_adjacent` standalone admission rarer;
4. tighten `strong_fit` from one core tag to a stronger core+quality combination;
5. keep a dedicated niche escape path that allows lower review counts when core evidence is strong;
6. protect Wishlist / known Deep-fit / direct references / package-value lanes explicitly;
7. treat DLC separately until owned-library support exists; do not assume ownership.

This attacks the 685 commercial/general-quality-only rows and the 654 zero-core rows before relying on a popularity floor.

## 10. Recommendation

**Recommend the balanced ~450-500 semantic-pool design, with a temporary shadow-audit phase.**

Why this is the best balance for a final visible target around 100:
- 2,301 semantic families is about 23x the visible target and creates unnecessary Dossier/Deep cost;
- ~276 is achievable but loses too many current niche and `БРАТЬ СЕЙЧАС` candidates;
- ~781 is safe but still leaves roughly 6-8x the final visible target;
- ~468 preserves every currently identifiable high-confidence protected lane while still leaving roughly 4.7 candidates per final visible slot, enough room for Deep to reject or rerank.

The production rule should **not** be “take 468”. The 468 number is an observed result of transparent deterministic gates on the current snapshot. The canonical rule should be the gates + protected lanes, with funnel observability. No fixed candidate count and no arbitrary ordering cutoff are required.

Before cutover, run the new gate in shadow mode against at least the current snapshot and one later normal snapshot. Record what it would exclude, and fail acceptance if it excludes any current authoritative Deep-fit, Wishlist, protected package/bundle lane or direct reference. For the niche lane, sample/examine the dropped high-core/low-volume cases rather than treating review count alone as proof of irrelevance.

## 11. Exact product tradeoffs requiring user/Director choice

1. **Approve or reject tightening `strong_niche_fit` as a pre-semantic admission rule.**  
   Balanced keeps 217/905 current strong-niche families, including 105/648 low-volume strong-niche. This flag is not semantic Taste proof, but narrowing it is the largest recall-sensitive decision.

2. **Approve or reject protecting all moderate-scenario `БРАТЬ СЕЙЧАС` offers.**  
   Balanced/conservative protect all 181 and still reach 468/781. Aggressive cannot reach its band safely while doing so.

3. **Confirm package/bundle lane remains explicitly protected.**  
   Recommended answer: yes. It costs only 33 semantic families and avoids a known product regression.

4. **Keep current DLC lane protected until owned-library support exists.**  
   Recommended answer: yes for now. It costs only 10 families. After owned-library DLC support lands, the lane can be narrowed by relevant/owned base-game context rather than popularity.

No choice is required about Wishlist or current authoritative Deep-fit: both should remain protected.

## 12. Smallest follow-up implementation task after approval

One bounded implementation task in the existing GitHub shortlist/discovery owner:

**STEAM_SHORTLIST_BALANCED_PRESEMANTIC_GATE_IMPLEMENT_01**

Scope:
1. add a canonical deterministic pre-semantic admission contract/policy section;
2. implement the approved balanced gates in the existing GitHub producer path before Dossier/Deep scope construction;
3. preserve explicit lanes for Wishlist, current compatible authoritative Deep-fit, direct-user references, packages/bundles, and current DLC policy;
4. add per-rule funnel/rejection counters and reason codes;
5. run in shadow comparison first;
6. regression-test current protected identities;
7. prove Reviews remains healthy and no review failure is used as filtering;
8. only after acceptance make the gate authoritative.

Architecture preflight:
- owner: GitHub control plane;
- authority: current mailing/selection policy + execution ownership contract, with the new gate first made canonical;
- no control-plane transfer to ChatGPT;
- no new scheduler, queue, retry owner or recurring stage.

Do not combine this with the separate Deep two-stage implementation owned by ЧАТ 2.

## 13. What was not changed

This task did not:
- change production code or thresholds;
- write a new shortlist;
- mutate Dossier/Deep queues or state;
- run semantic workers;
- change ranking;
- change Scheduled Tasks;
- introduce hard top-N;
- weaken or break Reviews.

Only this diagnostic report and bounded task-status documentation are written.

## 14. Final status

`diagnostic_complete_user_choice_required`

Concrete recommendation: **use the balanced deterministic gate targeting roughly the observed 450-500 semantic-family range, preserve explicit protected lanes, and validate it in shadow mode before cutover.** The unresolved choice is the acceptable recall loss inside the current broad `strong_niche_fit` lane.
