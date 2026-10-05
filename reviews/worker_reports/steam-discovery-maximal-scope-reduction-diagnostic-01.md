# Steam discovery maximal scope reduction diagnostic 01

Status: `diagnostic_complete_pending_user_product_choices`

Task: `WORKER_TASK_STEAM_DISCOVERY_MAXIMAL_SCOPE_REDUCTION_DIAGNOSTIC_01.md`

Mode: `READ-ONLY / RECON`

## 1. Executive conclusion

The current bottleneck is confirmed and does not need another Catalyst trace: the existing GitHub-owned Steam Search collector must finish a complete 50-row pagination of the live `specials=1` result before it can persist a fresh canonical discovery universe. The current combined `category1=998,21,996` shape does not reliably bound that live result; the accepted post-PR-#140 run observed about **100,307 rows** and hit the existing **60-minute** owner timeout before persistence.

The strongest preservation-first reduction is **not** to turn the raw fetch into an arbitrary top-100 query. It is to push **necessary current eligibility conditions** as far toward Steam as live semantics allow, while keeping the same GitHub owner:

1. split paid discovery into explicit game / DLC / bundle query partitions instead of relying on the ineffective combined category string;
2. for paid partitions, verify and then use Steam's live price bound corresponding to the current hard shortlist ceiling (**4500 KZT**) plus paid-only/F2P exclusion;
3. merge/deduplicate inside the existing collector;
4. before any Reviews API enrichment, apply the already-necessary local gates: paid row, `discount >= 25%`, `price <= 4500 KZT`, obvious-extra/software rejection, then the existing structural union in `needs_review_enrichment`;
5. preserve a separate bounded free/giveaway lane if the existing free-output contract is retained.

The last successful canonical shortlist proves that all **609 / 609** selected paid rows satisfy `discount >= 25%` and `price <= 4500 KZT`; those are consequences of the current `refined_reasons()` rules, not new product thresholds.

A hard **~100 visible-card** limit is a separate downstream product decision. Current canonical policy explicitly says full snapshot / no artificial top-N. Therefore the safe design is: **shrink raw discovery to the complete current-eligible commercial universe first; rank later; only cap the visible site near 100 if the user explicitly changes that product rule.**

## 2. Architecture preflight

Confirmed owner: the existing GitHub Actions workflow `.github/workflows/steam-test.yml` / job `collect`, which runs `scripts/steam_partial_publish_runner.py`.

Canonical ownership: `config/execution_ownership_contract.json` keeps discovery scope, completeness, manifests, retry/failure state and downstream orchestration in GitHub.

Relevant current selection policy: `config/mailing_policy.json` / `config/mailing_policy.md`.

No recommended design requires:
- a new scheduler;
- a new recurring stage;
- a ChatGPT-owned collector;
- a browser-owned discovery path;
- a new retry/backlog manager;
- a Catalyst special case.

Any future implementation must remain in the existing GitHub discovery owner.

A source-scope change from “complete broad Steam specials feed” to “complete explicit current-eligible discovery scope” should be made explicit in the canonical policy/contract before implementation, even when the narrowed scope is mathematically equivalent to the current shortlist rules.

A hard visible top-N or any source preselection that can discard a currently valid candidate is a product-semantics change and requires explicit user/Director approval first.

## 3. Confirmed current bottleneck

Accepted prior diagnostic:
`reviews/worker_reports/mirrors-edge-catalyst-post-refresh-absence-diagnostic-01.md`.

Settled facts reused rather than reinvestigated:
- live KZ Steam Search reported about **100,307** rows;
- current `specials=1&category1=998,21,996` did not bound the live response as intended;
- pagination is 50 rows/page;
- repeated 429 backoff occurs;
- the GitHub collector timeout is 60 minutes;
- post-PR-#140 collection reached roughly `start=73850` and was cancelled before canonical persistence.

At ~100,307 rows, the collector is facing roughly **2,007 50-row pages** before considering retries/backoff. The current accelerator explicitly states that Steam Search itself is always fetched live; it only shortens the fixed courtesy delay and caches review summaries.

The collector therefore fails **before** downstream taste/ranking becomes the controlling cost.

## 4. Current measurable funnel

The last successfully persisted discovery snapshot is stale but remains the best exact completed funnel baseline:

| Stage | Measured count | Meaning |
|---|---:|---|
| Current failed live raw scope | ~100,307 | accepted post-PR-#140 live KZ search total; not persisted |
| Last successful raw Steam scope | 12,977 | complete 2026-09-23 source traversal |
| Review-enrichment candidates | 9,923 | structurally capable of entering broad shortlist before review quality |
| Unique AppIDs enriched | 9,903 | two language review summaries per AppID |
| Logical Reviews API requests | 19,806 | global + Russian |
| Broad shortlist | 1,615 | at least one broad reason |
| Refined/source shortlist | 609 | current collector-selected paid candidates |
| Mailing index | 609 | same stale source scope |
| Ranking lookup | 509 | latest measurable ranking-derived card universe; not proof of current live site freshness |
| Product target | ~100 | user target for final visible best offers, not a raw-fetch quota |

The old completed funnel already discarded ~95% of raw rows by the refined shortlist stage. The problem is that most of that rejection happens **after** the expensive broad traversal.

## 5. Existing deterministic invariants that can move earlier

### 5.1 Paid price and discount

Current `refined_reasons()` has no successful paid path below 25% discount or above 4500 KZT.

The current 609-row shortlist confirms:
- minimum discount: **25%**;
- maximum price: **4500 KZT**;
- 609 / 609 satisfy both.

Therefore:
- local `discount < 25%` rejection is semantics-preserving for the current paid shortlist;
- local `price > 4500 KZT` rejection is semantics-preserving for the current paid shortlist;
- a Steam-side price cap is potentially semantics-preserving, but only after exact KZ live semantics/rounding/package behavior are verified.

There is no verified Steam-side “minimum discount = 25%” query contract in the current path, so discount should be treated as a cheap per-row gate unless a live source parameter is separately proven.

### 5.2 Obvious extras / software-only

`base_item_info()` already rejects:
- obvious extras matched by `EXTRA_RE`;
- software-tagged rows without game tags.

Those are safe to apply immediately after each bounded page is parsed, before review enrichment.

### 5.3 Existing structural review gate

`needs_review_enrichment()` already computes whether price/discount/tags/release date could possibly satisfy one of the broad shortlist paths.

It is safe and should remain the union-of-current-paths gate before exact review enrichment.

The major missing optimization is not inventing a new review rule; it is reducing the source pages first and applying these cheap gates before expensive downstream work.

## 6. Verified Steam-side/query findings

### Strong / implementation-relevant findings

**`specials=1`**  
The current owner already uses it. It is necessary but currently far from sufficient: the accepted KZ run still returned ~100,307 rows.

**Combined `category1=998,21,996`**  
Rejected as an adequate live bound. The accepted production run proves this exact combined shape did not constrain the source enough to complete.

**Per-content category queries**  
Live/public Steam Search continues to recognize individual content-category filtering (games, DLC, bundles/package-style results). Therefore separate per-type queries are a viable replacement for the unreliable combined shape, but exact KZ totals must be measured in the implementation acceptance probe. Partitioning alone is unlikely to be sufficient because the games-only sale scope can itself be very large.

**`maxprice`**  
Live/public Steam Search supports price narrowing. A bounded public probe combining game category + specials + a low price ceiling reduced the result set by roughly an order of magnitude relative to a games-only specials page in the same current-sale period. This is a **proxy**, not an exact KZ count. The exact acceptance condition is a bounded `cc=kz` probe proving that `maxprice=4500` means the intended KZT ceiling for app/package rows and does not exclude boundary-valid offers.

**Paid/free separation / `hidef2p`**  
Live Steam Search supports hiding free-to-play rows. That is appropriate for the paid partitions because the paid shortlist already rejects `price <= 0`. If free/giveaway output remains required, it must be queried/preserved separately rather than silently dropped.

**Price sorting**  
Steam exposes price sorting. This gives a fallback design: if exact KZ `maxprice` semantics prove unreliable, a price-ascending partition can be paginated only through the verified <=4500 KZT boundary. This is acceptable only after bounded probes prove monotonic price ordering around the cutoff; otherwise early stop is unsafe.

### Source-side filters that are real but unsafe for current semantics

**Tags**  
Can shrink source scope heavily, but current valid paths include high-quality/adjacent bargains that do not require a fit tag. Making tags a primary source filter would create false negatives.

**Review score / review count**  
Steam Search exposes advanced review filters, but current canonical eligibility uses exact AppReviews global count plus a global-or-Russian rating rule. Search-display review filters could discard Russian-rescue or missing/stale-search-summary candidates. Do not use them as completeness gates without a deliberate product-rule change and empirical false-negative study.

**Top sellers / popularity filters**  
They can reduce the source sharply but are fundamentally subset/pre-ranking filters. They would miss niche deals and are incompatible with current exhaustive-recall semantics.

### Not verified / rejected as primary architecture

**Source-side minimum discount**  
No current reliable minimum-discount query parameter was established. Keep >=25% as a cheap parsed-row gate unless a future bounded live probe proves a stable source parameter.

**Incremental / changed-since discovery**  
No correctness-preserving Steam “changed offers since last snapshot” source was identified in the current owner. Treating yesterday’s catalog plus a partial refresh as authoritative risks missing newly discounted offers. It is not recommended as the primary discovery source.

**IStoreBrowseService/GetItems**  
Already useful in this repository for batch enrichment/fallback of known AppIDs. It is not currently a discovery-listing source and does not replace the need to identify the current sale universe.

**Disabling `ignore_preferences=1`**  
Not a valid optimization. Steam user/preferences filters could silently hide candidates and make source completeness account-specific.

**Removing `cc=kz`**  
Not a valid optimization. Kazakhstan availability/pricing is part of the product contract.

## 7. Implication of the ~100-card product target

The current system is discovering far more rows than the final UX needs, but the target should be applied at the right layer.

From the current 609 shortlist:
- `discount >= 70% AND price <= 3000 KZT` still leaves **346**;
- `discount >= 60% AND price <= 3000 KZT` leaves **411**;
- `discount >= 50% AND price <= 3500 KZT` leaves **494**.

So ordinary commercial tightening alone does not naturally produce ~100 without discarding many currently eligible offers.

The robust architecture is:

1. make raw discovery complete over a **much smaller but semantics-equivalent eligible commercial universe**;
2. run current family/taste/deal/ranking logic on that bounded universe;
3. if the user really wants about 100 visible cards, apply that as an explicit **post-eligibility/post-family/post-ranking publication rule**, not as “fetch only 100 Steam rows”.

This prevents a high-discount niche game from disappearing merely because Steam's source order placed it after an arbitrary raw cutoff.

## 8. Viable options

### Option 1 — Safest / least product loss: explicit content partitions, full completion

How it works:
- keep the same collector and schedule;
- replace the combined `category1=998,21,996` query with separate game / DLC / bundle partitions;
- keep `specials=1`, `cc=kz`, `ignore_preferences=1`;
- merge/deduplicate exact App/Sub identities;
- preserve full completion within every partition.

Owner/component changed:
- existing GitHub collector only.

Estimated raw scope:
- still potentially **tens of thousands** during large sale periods; games alone can be large.
- exact KZ totals must be measured.

Runtime/API pressure:
- lower ambiguity and easier per-partition diagnosis, but likely still too high by itself.

Risk of missing a strong deal:
- low if the union of partitions is proven equivalent and bundles/DLC are retained.

Product-rule change:
- none intended.

User choice required:
- none for the preservation-first form.

Implementation complexity:
- low/medium.

Acceptance:
- bounded first-page `total_count` probe per partition;
- known App and Sub examples land in the expected partition;
- merged scope has deterministic identity/deduplication;
- one normal owner run completes within timeout before acceptance.

### Option 2 — Best balance / recommended: necessary-condition pushdown

How it works:
- Option 1 partitions;
- paid partitions additionally use a verified KZ price ceiling for the current hard **4500 KZT** maximum;
- exclude free-to-play rows from paid partitions;
- preserve free/giveaway output in a separate bounded lane if required;
- immediately after parsing, reject `discount < 25%`, `price > 4500`, obvious extras/software-only;
- only then run `needs_review_enrichment()` and the existing exact review policy.

Owner/component changed:
- existing GitHub collector only; no new stage.

Estimated raw scope:
- exact KZ total unknown until bounded probe.
- public current-sale probes show that price narrowing can reduce a games+specials result by roughly an order of magnitude; this is directional evidence only, not a KZ acceptance number.
- target should be **low enough to finish one normal run**, not a hard raw-row quota.

Runtime/API pressure:
- expected large reduction in Steam pages and 429 exposure;
- also reduces review-candidate pressure because obviously impossible rows never reach review enrichment.

Risk of missing a strong deal:
- low **if** KZ max-price semantics are verified and free output is separately preserved;
- local >=25% / <=4500 gates are already required by every current refined paid path.

Product-rule change:
- intended to preserve current paid-shortlist semantics;
- the canonical definition of “complete source scope” should still be updated to make the narrowed explicit scope authoritative.

User choice required:
- none for the current-semantics version.

Implementation complexity:
- medium.

Acceptance:
1. exact bounded KZ source probe for each paid partition with `maxprice=4500`;
2. prove 4500-boundary rows are included and >4500 rows are excluded;
3. prove representative App/Sub rows survive;
4. deterministic test that no current `refined_reasons()` path can accept <25% or >4500;
5. one normal GitHub-owned collection completes within 60 minutes and persists;
6. compare known previous 609 shortlist identities against the new necessary-condition rules; any loss must be explained by current sale drift, not query-shape error.

### Option 3 — Alternative preservation-first fallback: price-ordered bounded traversal

How it works:
- explicit content partitions;
- `sort_by=Price_ASC`;
- keep paging only while returned rows are at/below the current 4500 KZT necessary boundary;
- stop once several bounded checks prove the partition has crossed that boundary;
- local >=25% discount gate remains.

Owner/component changed:
- existing GitHub collector.

Estimated raw scope:
- only the cheap prefix of each partition rather than every sale row;
- exact scope depends on current sale distribution.

Runtime/API pressure:
- potentially similar to Option 2 without relying on `maxprice`, but requires more pages and stronger ordering validation.

Risk of missing a strong deal:
- low only if exact KZ ordering is proven monotonic and stable; otherwise medium/high.

Product-rule change:
- none intended.

User choice required:
- none if equivalence is proven.

Implementation complexity:
- medium/high because early-stop correctness is harder than an explicit source price cap.

Acceptance:
- bounded multi-page probe around the 4500 KZT boundary for every partition;
- reject implementation if any later page contains a <=4500 row after the stop boundary;
- same old-shortlist invariant regression as Option 2.

### Option 4 — Most aggressive reduction: source pre-ranking / hard candidate budget

How it works:
- use one or more of Steam Search review filters, popularity/top-seller filtering, selected tags, stricter price/discount bands, content-type removal, and/or keep only a fixed oversampled top candidate set before full canonical analysis;
- optionally publish only top ~100 after ranking.

Owner/component changed:
- existing GitHub collector plus canonical product/ranking policy.

Estimated raw scope:
- can be reduced to low thousands or even hundreds, depending on filters/budget.

Runtime/API pressure:
- lowest.

Risk of missing a strong deal:
- material/high under current semantics:
  - niche low-volume games can disappear;
  - Russian-review rescue can disappear;
  - high-quality adjacent candidates can disappear;
  - bundle-only purchase opportunities can disappear;
  - substantive DLC can disappear;
  - source ordering becomes an implicit taste/deal rule.

Product-rule change:
- **yes**.

User choice required:
- **yes**.

Implementation complexity:
- medium technically, high product/validation complexity.

Acceptance:
- requires an approved new recall-loss contract first;
- retrospective false-negative audit against existing shortlist and known strong historical deals;
- explicit target recall metric;
- hard stop if excluded known-good cases exceed the approved loss budget.

## 9. Ranked recommendation

1. **Safest / least product loss:** Option 1 — explicit partitions. Good structural repair, but likely insufficient alone.
2. **Best balance:** **Option 2 — explicit partitions + verified KZ price ceiling + paid/free split + existing necessary local gates.**
3. **Fallback if maxprice cannot be trusted:** Option 3 — price-ordered bounded traversal with strong boundary validation.
4. **Most aggressive:** Option 4 — source pre-ranking / hard budgets. Only after explicit user product choices.

### Recommended combined design

Use **Option 2** as the primary design, with Option 3 only as a fallback mechanism if exact KZ `maxprice` semantics fail validation.

Do **not** add an arbitrary raw top-N.

After the reduced complete eligible universe is stable, treat “about 100 visible offers” as a separate ranking/publication decision. That downstream cap is much safer because every eligible candidate has already had the opportunity to compete under the project's own ranking.

## 10. Exact unresolved user choices

Further reduction beyond the preservation-first design requires answers to these product questions:

1. **Is “about 100 cards” a real hard/near-hard final-site cap, or only a UX target?**  
   Current canonical policy has `fixed_top_n=null` and explicitly forbids an artificial top-N. A hard cap therefore requires a policy change.

2. **May DLC discovery be narrowed to DLC attached to already-qualified base-game families, or must the system keep discovering substantive DLC independently as it can today?**  
   Dropping broad DLC discovery may save a large amount of source scope but changes current content semantics.

3. **May bundles/packages stop being discovery seeds and be looked up only as purchase variants after a base game/family is found?**  
   The last completed 609-row shortlist contained only 8 `Sub_` rows, so this may be attractive, but current policy allows bundles to be valuable purchase variants and a bundle-only bargain could otherwise be lost.

4. **If the goal is more aggressive than current semantics, which recall loss is acceptable: stricter discount/price bands, low-review/niche titles, non-tag matches, or none?**  
   Without such a sacrifice, the correct way to reach ~100 is downstream ranking, not source truncation.

No assumption has been made for these choices.

## 11. Smallest follow-up implementation tasks after approval only

### Implementation task A — source-scope contract + bounded live proof
- update the canonical discovery-scope definition to the approved explicit paid/free/content partitions;
- add bounded live acceptance probes for per-category total and KZ `maxprice=4500` semantics;
- no full 100k crawl.

### Implementation task B — existing collector pushdown
- modify only the existing GitHub collector to use the approved partitions/price bound;
- merge/dedupe App/Sub identities;
- move exact necessary local gates ahead of review enrichment;
- retain current review/taste/family/ranking semantics.

### Implementation task C — regressions + one normal live acceptance
- prove no current refined rule admits paid rows <25% or >4500 KZT;
- preserve representative App/Sub/bundle/DLC examples according to the approved content scope;
- run one ordinary GitHub-owned production collection;
- require completion/persistence inside the existing 60-minute job;
- then verify ordinary downstream discovery of current candidates, including Catalyst without any special case.

### Optional separate product task D — ~100 visible cards
Only if the user confirms a hard/near-hard final target:
- change the canonical final publication/ranking policy;
- cap after canonical eligibility/family resolution and final ranking;
- do not reinterpret that cap as a raw Steam-fetch quota.

## 12. What was not changed

This diagnostic did not:
- implement a collector change;
- modify production discovery data;
- run another full Steam crawl;
- change the GitHub Actions schedule;
- create or modify a Scheduled Task;
- create another discovery owner;
- change Fast/Dossier/Deep;
- change ranking;
- special-case Mirror's Edge Catalyst.

Only the required worker report and the task's bounded `CURRENT_TASK.md` status entry are operational writes.

## 13. Final status

`diagnostic_complete_pending_user_product_choices`

The Director can choose the preservation-first implementation path without another broad Steam investigation. More aggressive reduction is deliberately blocked on the explicit product choices in section 10.
