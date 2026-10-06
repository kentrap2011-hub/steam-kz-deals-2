# Steam shortlist scope reduction diagnostic 02

Status: `diagnostic_complete_recommendation_ready`

Task: `WORKER_TASK_STEAM_SHORTLIST_SCOPE_REDUCTION_DIAGNOSTIC_02.md`

Mode: `READ-ONLY / DIAGNOSTIC / OFFLINE SIMULATION`

## 1. Executive conclusion

The current paid shortlist is not large because the Steam review thresholds were relaxed. The current review threshold map is materially the same as the historical 609-row snapshot. The dominant change is that the current complete paid discovery universe is much larger and the Reviews path now resolves that universe correctly instead of collapsing after the circuit breaker.

The comparison "609 -> 2522" is therefore not an apples-to-apples single-threshold regression:

- historical 2026-09-23 snapshot at commit `099c9c15fc8e08b78e167f5a8c8062d35ff73f3e`: 12,977 source rows -> 9,923 review candidates -> 1,615 broad -> 609 shortlist; global/russian review success was 9,895 AppIDs and only 8 review requests failed;
- broken modern 2026-10-05 snapshot at commit `7ad4b0196feb871cc11d25fe33e8538e478b569c`: ~97,998 source rows -> 60,624 unique paid candidates, but only 147 AppIDs had complete global+russian review data; broad collapsed to 28 and shortlist to 504, of which 497 were preserved last-known-good rows;
- fixed modern 2026-10-05/06 snapshots: ~98,015-98,023 source rows -> 60,631-60,632 unique paid candidates -> 7,972 broad -> 2,522 shortlist, with all 60,484-60,485 AppIDs resolved for both review components and no open circuit.

So the direct effect of repairing Reviews on the current large source is approximately 504 -> 2522, while the older 609 state was mainly a much smaller discovery universe. Returning to 609 by breaking or withholding reviews would recreate a correctness defect.

The strongest low-risk reduction found in this diagnostic is a **deterministic protected-lane + evidence-strength gate** before new semantic work. On the current 2,301-family Deep coverage target, the conservative simulation yields **784 families** and **670 unresolved semantic families**, while retaining:

- 112 / 112 current authoritative Deep-fit families;
- 39 / 39 current Wishlist families;
- 25 / 25 exact normalized title matches to directly user-rated StopGame cards;
- 181 / 181 families whose deterministic moderate-fit commercial scenario already says `БРАТЬ СЕЙЧАС`;
- 33 / 33 semantic families carrying a package/bundle purchase lane;
- 10 / 10 current semantic DLC/addon families.

This is a 65.9% reduction in the current Deep coverage target without using a blind top-N. The final visible ~100 remains a downstream ranking/publication target; it must not become a raw or semantic `take first 100`.

Recommendation: implement only the **conservative ~700-1000 band**, using the 784-family simulation as the concrete starting contract, then validate recall against known Deep/Wishlist/reference cases before activating it. Do not adopt the balanced 463 or aggressive 242 variants as the first production cut because their false-negative risk for unresolved niche titles is materially higher.

## 2. Architecture / ownership preflight

Current owner remains GitHub.

- discovery scope and deterministic transformations: GitHub control plane;
- semantic scope/order: GitHub control plane;
- Dossier/Deep workers: constrained semantic data plane only;
- interactive chat: diagnostic/developer session, not production backlog manager.

This diagnostic creates no new scheduler, queue, retry owner, recurring stage, Scheduled Task, or ChatGPT-owned scope selection.

A future implementation would change product semantics because it would make current recall flags insufficient by themselves for semantic admission. Therefore the follow-up must first encode the approved gate in a canonical GitHub-owned policy/contract and then modify the existing GitHub producer. It must not be implemented only in a worker prompt.

## 3. Exact current funnel

Current canonical `data/production/manifest.json`:

| Stage | Count |
|---|---:|
| Steam source reported / rows seen / parsed | 98,023 |
| removed non-paid or missing price | 51 |
| removed discount below 50% | 33,976 |
| removed price above 4500 KZT | 0 |
| removed obvious extras | 2,264 |
| removed software-only | 1,019 |
| eligible rows before partition dedupe | 60,713 |
| unique eligible after partition dedupe | 60,632 |
| review candidate items | 60,632 |
| review candidate AppIDs | 60,485 |
| broad shortlist | 7,972 |
| paid shortlist | 2,522 |

Reviews are now healthy:

- `global_review_appids_ok = 60485`;
- `russian_review_appids_ok = 60485`;
- `review_rate_limit_circuit_open = false`;
- all 2,522 shortlist items were publishable without AppReviews fallback under the current Search/cache/StoreBrowse strategy.

Current content/family decomposition:

| Stage | Count |
|---|---:|
| shortlist source items | 2,522 |
| metadata type: game | 2,407 |
| metadata type: package | 55 |
| metadata type: DLC | 60 |
| mechanically excluded before family resolution | 53 |
| family candidate items | 2,469 |
| purchase families / taste subjects | 2,385 |
| current Deep coverage target | 2,301 |
| current Dossier prepared/pending required items | 2,134 |

Current Deep scope document reports:

- first-pass attempted: 143;
- authoritative completed: 125;
- authoritative fit: 112;
- authoritative not-fit: 13;
- incomplete/recovery: 18;
- waiting for Dossier: 2,141;
- ready/pending: 17;
- remaining until all authoritative: 2,176.

The exact reason why 84 of the 2,385 taste subjects are outside the current 2,301 Deep coverage document is not reinterpreted here; this task uses the canonical current Deep target as the semantic baseline rather than inventing a new explanation for that delta.

## 4. Why 609 became 2522

### 4.1 Historical 609 was not a Reviews-failure snapshot

The 2026-09-23 609-row snapshot had:

- source total 12,977;
- review candidates 9,923;
- global+russian review success 9,895;
- only 8 review failures;
- broad shortlist 1,615;
- shortlist 609.

Its review threshold map matches the current threshold profile for the relevant refined reasons.

Therefore it is incorrect to say that the historical 609 itself was mainly produced by the broken Reviews path.

### 4.2 The actual Reviews-failure shrinkage was 2522 -> 504

On 2026-10-05 before PR #155 repaired the Reviews/publication path:

- source rows: 97,998;
- unique eligible: 60,624;
- complete global+russian review AppIDs: 147;
- broad shortlist: 28;
- shortlist: 504;
- 497 shortlist rows were carried by last-known-good preservation;
- logical review failure count was dominated by circuit-skipped work.

After the fix, with essentially the same source size:

- source rows: 98,015;
- unique eligible: 60,631;
- complete global+russian review AppIDs: 60,484;
- broad shortlist: 7,972;
- shortlist: 2,522.

This is the accidental shrinkage that must not be recreated.

### 4.3 Long-term growth is primarily source-universe growth

Comparing the healthy historical 2026-09-23 snapshot to current:

- source: 12,977 -> 98,023 (~7.55x);
- review-capable candidate universe: 9,923 -> 60,632 (~6.11x);
- broad shortlist: 1,615 -> 7,972 (~4.94x);
- refined shortlist: 609 -> 2,522 (~4.14x).

The source universe expanded much faster than the final shortlist. The current filters are still removing most source rows; there are simply far more valid sale rows reaching them.

## 5. Current admission-rule contribution

Counts below are **marginal reason presence**, so rows can appear in multiple reason counts. "Sole admit" means the row has exactly that one refined reason; removing only that rule would remove that row immediately.

| Refined reason | Current 2522 | Historical 609 | Delta | Current sole admits |
|---|---:|---:|---:|---:|
| `strong_fit` | 1,323 | 272 | +1,051 | 307 |
| `strong_niche_fit` | 955 | 155 | +800 | 414 |
| `mainstream_quality` | 1,059 | 295 | +764 | 62 |
| `exceptional_discount` | 973 | 259 | +714 | 142 |
| `very_high_rating` | 779 | 221 | +558 | 61 |
| `high_confidence_adjacent` | 159 | 48 | +111 | 0 |
| `recent_fit` | 108 | 65 | +43 | 32 |
| `substantive_content` | 54 | 4 | +50 | 36 |

Current largest exact reason combinations include:

- `strong_niche_fit` alone: 414;
- `strong_fit` alone: 307;
- `strong_fit + strong_niche_fit`: 153;
- `exceptional_discount` alone: 142;
- `exceptional_discount + mainstream_quality + strong_fit`: 115;
- five-way `exceptional_discount + mainstream_quality + strong_fit + strong_niche_fit + very_high_rating`: 107.

There are **1,054 / 2,522 (41.8%)** rows admitted by exactly one refined reason.

There are **685 / 2,522 (27.2%)** rows whose entire refined-reason set is only from the generic commercial/quality group:

- `mainstream_quality`;
- `exceptional_discount`;
- `very_high_rating`;
- `high_confidence_adjacent`.

That 685-row block is the safest large reduction target because current canonical policy already says reviews, discount, popularity and generic feed flags are recall/quality signals, not personal taste evidence.

However, the other major source of growth is also important: `strong_fit` and `strong_niche_fit` are themselves recall flags, not authoritative taste proof. In the current shortlist, 307 rows enter only through `strong_fit` and 414 only through `strong_niche_fit`. Treating these labels as if they were already semantic fit would leave the pool unnecessarily large.

## 6. Current distribution diagnostics

### Review-count bands, 2,522 shortlist rows

| Global review count | Count |
|---|---:|
| <300 | 14 |
| 300-999 | 376 |
| 1,000-2,999 | 555 |
| 3,000-4,999 | 431 |
| 5,000-9,999 | 450 |
| 10,000-19,999 | 317 |
| 20,000+ | 379 |

A flat popularity floor is unsafe: a substantial part of `strong_niche_fit` intentionally lives below mass-market review counts. The gate must allow a niche escape lane when core-fit structure is stronger.

### Global positive-rating bands

| Rating | Count |
|---|---:|
| <75 | 44 |
| 75-77.9 | 86 |
| 78-79.9 | 158 |
| 80-84.9 | 519 |
| 85-89.9 | 686 |
| 90+ | 1,029 |

### Current price bands, KZT

| Price | Count |
|---|---:|
| <=500 | 455 |
| 501-1000 | 741 |
| 1001-2000 | 843 |
| 2001-3000 | 329 |
| 3001-3500 | 74 |
| 3501-4000 | 60 |
| 4001-4500 | 20 |

Price is therefore not a useful primary semantic reducer: most candidates are already inexpensive, and using price as taste evidence would violate the current separation of taste and deal quality.

### Discount bands

| Discount | Count |
|---|---:|
| 50-59 | 517 |
| 60-69 | 414 |
| 70-74 | 224 |
| 75-79 | 485 |
| 80-89 | 618 |
| 90+ | 264 |

Discount alone also cannot safely select future top-100 candidates; it is useful only as a strengthened escape path when combined with strong quality evidence.

### Core-fit tag count

| Core tags | Count |
|---|---:|
| 0 | 654 |
| 1 | 788 |
| 2 | 755 |
| 3 | 253 |
| 4+ | 72 |

This is the strongest deterministic discriminator available before semantics, but it must not be used alone because canonical policy explicitly warns that generic tags are not taste proof.

## 7. Protected current semantic lanes

The current 2,301-family semantic baseline contains:

- Wishlist: 39 families;
- authoritative Deep fit: 112;
- authoritative Deep not-fit: 13;
- exact normalized-title matches to directly user-rated StopGame cards: 25;
- semantic families with package/bundle purchase lane: 33;
- semantic DLC/addon families: 10;
- deterministic moderate-fit deal scenario `БРАТЬ СЕЙЧАС`: 181.

The direct-user-rated count is a bounded exact normalized-title match against the canonical StopGame card titles. It is used only as a conservative diagnostic protection lane; it is not claimed to be a stronger AppID identity mapping.

Wishlist remains protected only as an admission-preservation lane in these simulations. It is still not taste evidence and cannot alter the later taste score.

Packages/bundles are also a distinct protected lane; no simulation silently deletes them.

## 8. Offline reduction simulations

All simulations are deterministic and run against the current canonical 2,301-family semantic context. None uses `take first N`.

The current project review predicate is preserved: the global review-count minimum must pass, and the rating threshold can be satisfied by global rating or by the Russian rating with the existing bounded Russian sample requirement.

### Strategy A — conservative, recommended

Target band: ~700-1000.

Always protect:
- current Wishlist;
- authoritative Deep fit;
- directly user-rated exact-title matches;
- package/bundle purchase lane;
- all current semantic DLC/addon families;
- current deterministic moderate-fit `БРАТЬ СЕЙЧАС` commercial opportunities.

Additional admission:

- `strong_niche_fit`:
  - core >=3 and reviews >=500 and rating >=82; or
  - core >=2, global reviews <5000, reviews >=1000 and rating >=86; or
  - core >=2, global reviews >=5000, reviews >=3000 and rating >=88;
- `strong_fit`:
  - core >=3, reviews >=3000 and rating >=86; or
  - core >=2, reviews >=10000 and rating >=90;
- `recent_fit`: core >=2, reviews >=1500, rating >=84;
- `substantive_content`: core >=2, reviews >=750, rating >=84;
- `exceptional_discount`: discount >=90%, reviews >=20000, rating >=90;
- no standalone admission from `mainstream_quality`, `very_high_rating`, or `high_confidence_adjacent`.

Result:

| Metric | Current | Kept | Dropped |
|---|---:|---:|---:|
| semantic families | 2,301 | **784** | 1,517 |
| unresolved semantic families after known Deep outcomes | — | **670** | — |
| Wishlist | 39 | 39 | 0 |
| Deep fit | 112 | 112 | 0 |
| Deep not-fit | 13 | 2 | 11 |
| directly user-rated exact matches | 25 | 25 | 0 |
| moderate-fit `БРАТЬ СЕЙЧАС` | 181 | 181 | 0 |
| package/bundle lane | 33 | 33 | 0 |
| DLC/addon lane | 10 | 10 | 0 |
| `strong_niche_fit` | 905 | 518 | 387 |
| low-volume `strong_niche_fit` (<5000 reviews) | 648 | 306 | 342 |
| generic commercial/quality-only | 638 | 109 | 529 |

The two retained Deep-not-fit families are not protected by their not-fit status; they independently satisfy another protected/gate condition. Authoritative Deep not-fit remains authoritative downstream and would still prevent them from becoming a visible positive recommendation.

Risk: moderate-low. The largest unresolved risk is still the 342 low-volume `strong_niche_fit` families rejected by the stronger gate. However, every currently known high-value protection class stays intact, and 306 low-volume niche candidates remain.

### Strategy B — balanced

Target band: ~300-600.

Use the same protected lanes as Strategy A.

Additional admission:

- `strong_niche_fit`: core >=3, reviews >=1500, rating >=88;
- `strong_fit`: core >=3, reviews >=7000, rating >=90;
- `recent_fit`: core >=3, reviews >=3000, rating >=88;
- `substantive_content`: core >=3, reviews >=1500, rating >=88;
- `exceptional_discount`: discount >=90%, reviews >=30000, rating >=92;
- no standalone `mainstream_quality`, `very_high_rating`, or `high_confidence_adjacent`.

Result:

| Metric | Current | Kept | Dropped |
|---|---:|---:|---:|
| semantic families | 2,301 | **463** | 1,838 |
| unresolved semantic families | — | **351** | — |
| Wishlist | 39 | 39 | 0 |
| Deep fit | 112 | 112 | 0 |
| Deep not-fit | 13 | 0 | 13 |
| directly user-rated exact matches | 25 | 25 | 0 |
| moderate-fit `БРАТЬ СЕЙЧАС` | 181 | 181 | 0 |
| package/bundle lane | 33 | 33 | 0 |
| DLC/addon lane | 10 | 10 | 0 |
| `strong_niche_fit` | 905 | 216 | 689 |
| low-volume `strong_niche_fit` | 648 | 105 | 543 |
| generic commercial/quality-only | 638 | 107 | 531 |

Risk: medium/high. The count is attractive, but only 105 of 648 low-volume niche candidates survive. That is too much unresolved niche recall loss to recommend as the first production cut when the final visible target is ~100.

### Strategy C — aggressive

Target band: ~150-300.

Always protect only:
- current Wishlist;
- authoritative Deep fit;
- directly user-rated exact-title matches;
- package/bundle lane.

Do not automatically protect all DLC or all commercial `БРАТЬ СЕЙЧАС` families.

Additional admission:

- `strong_niche_fit`: core >=3, reviews >=5000, rating >=90;
- `strong_fit`: core >=4, reviews >=10000, rating >=92;
- `exceptional_discount`: discount >=90%, reviews >=50000, rating >=94.

Result:

| Metric | Current | Kept | Dropped |
|---|---:|---:|---:|
| semantic families | 2,301 | **242** | 2,059 |
| unresolved semantic families | — | **130** | — |
| Wishlist | 39 | 39 | 0 |
| Deep fit | 112 | 112 | 0 |
| Deep not-fit | 13 | 0 | 13 |
| directly user-rated exact matches | 25 | 25 | 0 |
| moderate-fit `БРАТЬ СЕЙЧАС` | 181 | 19 | 162 |
| package/bundle lane | 33 | 33 | 0 |
| DLC/addon lane | 10 | 1 | 9 |
| `strong_niche_fit` | 905 | 112 | 793 |
| low-volume `strong_niche_fit` | 648 | 26 | 622 |
| generic commercial/quality-only | 638 | 55 | 583 |

Risk: high. This band materially sacrifices current strong commercial opportunities, most DLC, and most unresolved niche candidates. It should not be used without a separate explicit product decision accepting that loss.

## 9. What the simulations say about individual rule families

### Minimum review count

A single global popularity floor is not recommended.

The current shortlist contains 945 rows below 3,000 global reviews and 390 below 1,000. A flat 3k/5k floor would erase a large share of the niche lane.

Use review count only in a joint gate with core-fit strength and rating. Lower review-count requirements should remain possible when core structure is stronger.

### Rating threshold

The current low thresholds 78/80 are appropriate as recall guards but too weak as semantic-pool admission by themselves.

For pre-semantic narrowing, the simulations support moving most unresolved paths into the 84-90 range, while preserving known-good lanes independently.

### Core taste tags

Core count is useful as a deterministic pre-semantic discriminator:

- 1,442 / 2,522 shortlist rows have only 0-1 core tags;
- only 325 have 3+.

But core tags cannot become taste proof. The recommended gate always pairs them with review-quality evidence or a protected lane.

### Generic commercial reasons

Rows admitted only by `mainstream_quality / exceptional_discount / very_high_rating / high_confidence_adjacent` are the cleanest large cut.

Recommendation:
- `mainstream_quality`, `very_high_rating`, `high_confidence_adjacent` should not independently create semantic work;
- `exceptional_discount` can remain an escape path only when the discount is truly exceptional and quality confidence is high.

### `strong_niche_fit`

This is the largest sole-admission rule: 414 offer rows enter only through this flag.

Do not delete it. Instead split it into:
- strong-structure niche lane with lower popularity requirement;
- weaker-structure lane with stronger rating/review requirements.

That preserves the project goal of finding niche games without treating 2 generic/core tags + 300 reviews + 78% as enough to justify expensive semantics for every candidate.

## 10. DLC and package/bundle effects

### Packages/bundles

Current shortlist metadata contains 55 package rows. After family resolution, 33 current semantic families carry a package/bundle purchase lane.

All three simulations explicitly protect those 33 semantic package/bundle lanes. No recommendation silently removes package discovery.

### DLC/addons

Current shortlist metadata contains 60 DLC rows, but only 10 current semantic families are DLC/addon families requiring semantic handling.

Conservative and balanced simulations keep all 10.

The aggressive simulation keeps only 1 and drops 9. That is one reason aggressive is not recommended.

No simulation assumes an owned-library signal exists. Any future DLC narrowing must use only current deterministic base-family/semantic conditions until the separate owned-library support task actually provides canonical ownership data.

## 11. No blind top-N

The recommendation does not sort 2,301 rows and take the first 784.

Admission is explainable per family:

1. protected lane, or
2. named recall route,
3. minimum core-structure requirement,
4. minimum review-count confidence,
5. minimum rating confidence,
6. exceptional-discount escape only under explicit stronger conditions.

A future deterministic pre-ranking may order the admitted semantic pool for processing efficiency, but a hard cap is unnecessary for the recommended conservative gate. If a cap is later added, protected lanes must be admitted before the cap and the cap must operate only after these quality/fit gates.

## 12. Recommendation

Adopt the **conservative band**, not the balanced/aggressive bands.

Concrete starting rule: Strategy A above, currently yielding **784 / 2,301** semantic families.

Why this is the best balance:

- cuts current semantic coverage by 1,517 families (~65.9%);
- keeps every currently known Deep-fit case;
- keeps every current Wishlist family;
- keeps every directly user-rated exact match found in the current pool;
- keeps every current package/bundle semantic lane;
- keeps every current DLC semantic family;
- keeps every deterministic moderate-fit `БРАТЬ СЕЙЧАС` opportunity;
- removes 529 / 638 generic-commercial-only semantic families;
- still leaves 306 low-volume strong-niche families, so it does not turn popularity into a hard veto;
- leaves 670 unresolved semantic families, a much more realistic analysis backlog for a final visible target of roughly 100.

The balanced 463 pool is useful as a sensitivity bound, not as the first implementation target. The aggressive 242 pool is too close to the final visible size and therefore asks deterministic prefilters to make semantic decisions they cannot safely make.

## 13. Product tradeoffs requiring Director/user approval

Before implementation, one product choice must be explicit:

**Approve or reject the conservative semantic admission contract in Strategy A.**

Approving it means accepting that current recall flags are no longer sufficient alone:
- some `strong_fit` and `strong_niche_fit` rows will not receive new semantic analysis unless they meet stronger quality/core conditions or enter a protected lane;
- generic `mainstream_quality` / `very_high_rating` / `high_confidence_adjacent` no longer independently generate semantic work;
- `exceptional_discount` alone becomes a much narrower escape path.

No additional choice is needed about Wishlist, packages/bundles, current DLC, direct user-rated titles, current Deep fit, or current moderate-fit `БРАТЬ СЕЙЧАС` in the recommended variant: they are all explicitly protected.

## 14. Smallest follow-up implementation task

After Director/user acceptance only:

1. add one canonical GitHub-owned pre-semantic admission policy/contract defining the protected lanes and Strategy-A deterministic gates;
2. apply it in the existing GitHub producer that converts current family/candidate context into semantic scope;
3. preserve current Dossier/Deep ownership, retry, ordering and transport architecture;
4. add deterministic offline regression fixtures proving:
   - all current 112 Deep-fit families remain admitted;
   - all current 39 Wishlist families remain admitted;
   - all current 33 package/bundle lanes remain admitted;
   - all current 25 exact direct-rating matches remain admitted;
   - all current 181 moderate-fit `БРАТЬ СЕЙЧАС` families remain admitted;
   - current DLC handling does not use invented ownership;
   - no generic commercial reason can independently bypass the new gate;
5. run one fresh offline simulation against current production data and require the resulting band to remain approximately 700-1000 without a hard top-N;
6. only after those checks change the generated semantic scope.

Do not modify the Deep worker prompts to implement this filter. GitHub remains the scope owner.

Architecture preflight for this follow-up:
- changing responsibility: none; GitHub remains semantic-scope owner;
- canonical authorization: a new/updated GitHub policy is required before code activation;
- no control-plane transfer to ChatGPT;
- no new scheduler, queue, retry loop, backlog manager or recurring stage.

## 15. What was not changed

This task did not:

- change production code;
- change review thresholds;
- write a new shortlist;
- change current Dossier/Deep queues;
- change ranking;
- rerun semantic workers;
- change Scheduled Tasks;
- introduce a hard top-N;
- remove packages/bundles;
- assume Steam ownership data exists.

Only offline analysis and this diagnostic report are intended writes.

## 16. Final status

`diagnostic_complete_recommendation_ready`

Recommended semantic-pool band: **conservative ~700-1000**, concrete current simulation **784**.
