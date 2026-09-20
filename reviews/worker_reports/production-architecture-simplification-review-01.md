# Production architecture simplification review 01

## 1. Task / repo / mode

- Task: production-architecture-simplification-review-01.
- Authoritative task: WORKER_TASK_PRODUCTION_ARCHITECTURE_SIMPLIFICATION_REVIEW_01.md.
- Repository: kentrap2011-hub/steam-kz-deals-2.
- Branch / source of truth: main.
- Mode: READ-ONLY / ARCHITECTURE REVIEW.
- No other repository was read, searched, changed, or used.
- No production run or Scheduled Task was triggered.
- No source, workflow, contract, configuration, production artifact, queue, cache, progress state, or UI file was changed.
- The only repository write in this task is this durable review report.

Architecture preflight conclusion:

1. GitHub currently owns business/execution contracts, source collection it can perform directly, deterministic transforms, exact work scope/order, manifests/pins, retry/completeness state, validation, canonical persistence, downstream rebuild and publication orchestration.
2. Scheduled ChatGPT currently owns bounded external/semantic data-plane work: Taste judgments and Steam-review-dossier web research for exact GitHub-prepared work, returning structured results through repository-defined handoff paths.
3. A fresh normal paid visual currently requires Scheduled ChatGPT semantic success indirectly because current readiness requires ai_queue_count == 0. On the 2026-09-20 snapshot ai_queue_count is 734 and ready_without_ai_count is 0.
4. Source integrity, exact identity, current offer validity, budget/content gates and acceptance of returned semantic facts are correctness-sensitive. Dossier freshness, Russian review retrieval, temporal player-feedback completeness, detailed personalized risks and other enrichment are currently over-scoped when they become prerequisites for any fresh paid output.
5. The proposed target does not transfer GitHub control-plane responsibility to ChatGPT. It reduces the set of user-facing publication states that are allowed to depend on ChatGPT.

## 2. User-facing product objective

The canonical product goal is not “complete every enrichment pipeline.” The user-facing purpose is to help the user find roughly one paid game per month that is genuinely worth buying now, while separately surfacing relevant permanent giveaways.

The important product constraints remain unchanged:

- taste is the main filter for a personalized recommendation;
- price/deal quality cannot manufacture taste fit;
- symbolic discounts of 5% or less are excluded;
- the ordinary target price is around 500 RUB and the absolute paid-recommendation ceiling is 750 RUB;
- sale urgency affects ordering only after eligibility;
- missing secondary information must not make a potentially useful purchase disappear merely because enrichment could not be fetched;
- the UI must remain a read-only consumer of producer-owned results.

The architecture should therefore distinguish two claims that are currently conflated:

- “this is a current valid discounted offer worth showing as a deal candidate”; and
- “this is a fully personalized recommendation whose Taste/risk evidence is current enough to support personalized claims.”

The first claim can be made deterministically from current commercial and product facts. The second needs Taste/enrichment. The system should never present the first as the second when personalization is pending.

## 3. Current architecture / critical path

### Current end-to-end path

| Stage | Current owner | Deterministic / LLM | Needed for basic current deal facts? | Current failure effect |
| --- | --- | --- | --- | --- |
| Steam KZ discovery / manifest / shortlist | GitHub | Deterministic/network collector | Yes | Correctly global if the source manifest is incomplete or wrong-region |
| Store snapshot, FX, family graph, content/deal gates | GitHub | Deterministic | Yes | Mostly correct core dependency |
| History classification / purchase context | GitHub plus bounded external history where needed | Mostly deterministic, external facts for misses | Useful but exact history is not required to know that a current discount exists | Current visual workflow waits for complete classification coverage |
| Pre-AI consumer bundle | GitHub | Deterministic | Yes as current normalized input | Produces current queue/state |
| Steam Review Dossier daily full backlog | GitHub scope + Scheduled ChatGPT evidence worker | LLM/web | No for basic deal availability | Currently upstream of Taste semantic readiness |
| Dossier validation / persistence / group progress | GitHub | Deterministic validation | No for basic deal availability | First invalid/missing expected group can halt canonical dossier progress |
| Taste semantic evaluation | Scheduled ChatGPT, exact GitHub pin | LLM | Needed for fully personalized recommendation, not for raw current deal facts | Any unresolved queue item prevents normal fresh visual build |
| Taste ingest/cache | GitHub | Deterministic validation/persistence | Needed to persist personalized semantics | Exact binding mismatch rejects, correctly for semantic correctness |
| Final personalized ranking / visual build | GitHub | Deterministic over semantic + commercial inputs | Yes for fully personalized UI | Current readiness returns WAIT until ai_queue_count == 0 |
| Pages/UI | GitHub Pages/browser | Read-only rendering | Yes | Can only render prepared payload |

### Current concrete state on 2026-09-20

- data/production/pre_ai/chatgpt_payload.json:
  - status = degraded;
  - source_mailing_updated_at_utc = 2026-09-19T22:47:44.410194+00:00;
  - source_family_count = 794;
  - ai_queue_count = 734;
  - ready_without_ai_count = 0;
  - deterministically_excluded_without_ai_count = 60;
  - all 734 queue rows require a new evaluate_taste_fit + evaluate_normalized_taste_factors + resolve_grounded_negative_analysis; one additionally requires base-support resolution.
- data/production/pre_ai/taste_steam_review_dossier_work.json:
  - snapshot = ad93a4484f1c6ceba4ba3d4ef0de681f65fe670ec1ee600e2abc0822b0eec54a;
  - prepared/remaining/completed = 733 / 733 / 0;
  - checkpoint size = 3;
  - group count = 245;
  - first group = Crown Trick / Hellish Quart / Tetris Effect: Connected.
- data/production/visual/current.json:
  - status = degraded;
  - semantic source is still 2026-08-30T20:37:43.818127+00:00;
  - only 3 paid items remain in the payload;
  - semantic completeness reports 608 unresolved / 1 resolved for its tracked scope and sufficiently_complete_for_publication = false;
  - nevertheless paid_list_freshness is current commercial-only, with commercial source 2026-09-19T22:47:44.410194+00:00 and Store observation 2026-09-20T12:31:41.608391+00:00.

This proves an important architectural fact: GitHub can still obtain and publish fresh commercial facts while fresh semantic publication is blocked. The existing commercial-only visual refresh already preserves semantic fields and updates current prices/offers without Taste recalculation; it simply cannot introduce the current 734-item candidate population because the normal builder waits for the AI queue to close.

## 4. Current blocking dependencies

### Legitimate core blockers

These should remain fail-closed for a new “current” core snapshot:

- source manifest/discovery incompleteness or wrong region;
- unparseable/missing source timestamp or source older than the existing 18-hour preparation freshness gate;
- current product/offer identity that cannot be safely bound to the right game/family;
- missing current price/discount where the item cannot be classified safely;
- known ended sale;
- deterministic content ineligibility;
- symbolic discount <= 5%;
- paid offer above the absolute 750 RUB ceiling for the personalized paid-recommendation lane;
- malformed deterministic family partition that prevents trustworthy per-item classification.

A failure in one item’s deterministic identity/offer can quarantine that item if the global discovery manifest itself is complete. It should not automatically invalidate unrelated correctly classified items.

### Currently blocking but should become non-blocking for core availability

- Steam Review Dossier completeness;
- Russian-review existence/retrieval gates;
- temporal current-state review coverage;
- multi-source player-feedback provenance completeness;
- Scheduled ChatGPT prompt compliance;
- Dossier content-complete prompt binding;
- Dossier group progress / maximal contiguous prefix;
- full Taste queue closure;
- grounded-negative completion for every current candidate;
- play-role/start-priority enrichment;
- duration/achievement-quality enrichment;
- exact fresh external-review evidence;
- exact SteamDB/history lookup success when history can be explicitly marked unverified.

Those signals can remain strict for the claims they support. They should not be allowed to prevent the system from saying “this current KZ deal exists and personalization is pending.”

## 5. Failure-class blast-radius review

| Failure class | Current blast radius | Correct target blast radius |
| --- | --- | --- |
| Scheduled prompt noncompliance | Can stop expected dossier group, then semantic progress, then all fresh paid personalized output | Enrichment worker only; affected items stay pending/stale; core deals publish |
| Stale binding / snapshot mismatch | Correctly rejects old result but can leave entire new semantic generation blocked | Reject only incompatible enrichment result; requeue affected item; core unaffected |
| Semantic/Taste backlog or stale result | ai_queue_count > 0 makes normal builder WAIT | Personalized status degrades per item; compatible cached Taste may be reused; unknown item stays personalization_pending |
| Dossier evidence/retrieval failure | One item can fail an atomic group and hold canonical prefix | Quarantine/retry that item; unrelated dossier items and all core deals continue |
| External-site variability | Can exhaust one dossier route and stop group | Only current-state/risk confidence for that item degrades |
| Fail-closed whole-group behavior | One bad game blocks two good games in the same group and later canonical prefix | Batching may remain transport-only, but canonical enrichment outcome must be item-level |
| Validator/generator mismatch | Structurally valid-looking worker output can be rejected, blocking group progress | Reject/quarantine the one result; producer contract tests protect future items; no core effect |
| Runtime artifact/persistence handoff failure | Previously prevented canonical checkpoint advancement | Background result remains unaccepted/retryable; no core effect |
| Long repair cycle | User can go weeks seeing stale/minimal paid output while engineers repair enrichment | User sees current core daily; repair cycle affects only personalization depth |
| History/SteamDB miss | Can contribute to history-stage waiting depending on classification state | Item history = unverified; do not call it a record/near-record; current deal still eligible if other core gates pass |

The current behavior converts “cannot prove enrichment is complete” into “cannot publish current paid product.” That blast radius is not justified by the user-facing business rules.

## 6. Design A — current architecture, hardened

Keep current coupling and global fail-closed semantics; add better Scheduled Task entrypoint attestation, prompt compliance proof, retries, generator/validator parity tests and richer runtime receipts.

Advantages:

- minimal conceptual change to current contracts;
- highest assurance that every published personalized card has passed the full current semantic stack;
- much of the existing implementation can be retained.

Disadvantages:

- core daily availability still depends on Scheduled ChatGPT and external web behavior;
- any new semantic contract/binding revision can recreate a near-full backlog;
- group/head-of-line semantics still turn item failures into broad outages;
- observability helps diagnose failure but does not reduce failure blast radius;
- operator burden remains high because recovery requires coordinated prompt/contract/runtime work;
- the probability of another long repair cycle remains structurally high even if the currently known defects are fixed.

Conclusion: suitable only if “no output until all enrichment is complete” is itself a business requirement. The canonical product rules do not require that.

## 7. Design B — split core deals from enrichment

Daily GitHub production publishes a deterministic current deal surface from current commercial/product data. Personalization is an overlay with explicit per-item status.

Core characteristics:

- source/discovery/commercial correctness remains strict;
- current deterministic deal candidates can publish without Scheduled ChatGPT;
- exact-compatible Taste cache is used when available;
- incompatible/missing Taste does not get silently reused as personalized truth;
- unknown items are explicitly personalization_pending rather than falsely recommended;
- Dossier and external review evidence update independently;
- a failed enrichment item cannot block unrelated items;
- one canonical UI payload can still contain both current core facts and optional personalized fields.

Advantages:

- high daily availability;
- preserves strong personalized recommendations whenever evidence exists;
- clean failure isolation;
- reuses much of the deterministic pipeline already proven by commercial-only refresh;
- makes GitHub, not LLM narration, the source of visible production state.

Disadvantages:

- requires a clear degraded-card/product-state contract;
- UI must distinguish “current deal candidate” from “personalized recommendation”;
- final ranking policy needs an explicit deterministic fallback mode rather than pretending a missing personal score is complete.

Conclusion: best fit for the stated product goal and failure history.

## 8. Design C — cache-first personalization

Treat Taste and dossier knowledge as long-lived per-game caches. Daily commercial production consumes whatever exact-compatible cache exists and queues misses separately.

Advantages:

- avoids repeated semantic work for unchanged games;
- good steady-state personalization with low LLM load;
- natural handling of large catalogs;
- Dossier can be maintained opportunistically.

Disadvantages:

- cache invalidation after profile/model changes still matters;
- a whole-profile invalidation, as in the current snapshot, can leave no current Taste hits at all;
- without an explicit core/nonpersonalized surface, this design can still produce either an empty product or pressure to reuse incompatible stale taste;
- more cache-state semantics are needed to distinguish compatible, stale, incompatible and unknown.

Conclusion: valuable as an implementation pattern inside Design B, but not sufficient by itself as the product availability contract.

## 9. Design D — minimal product recovery architecture

Reduce the product temporarily or permanently to:

- fresh current deal facts;
- deterministic content/price/sale gates;
- history when available, otherwise unverified;
- compatible existing Taste cache if any;
- deterministic fallback ranking;
- UI output.

Everything else is background.

Advantages:

- fastest service restoration;
- lowest runtime complexity;
- essentially removes Scheduled ChatGPT from availability.

Disadvantages:

- today’s current profile has no resolved current Taste rows, so most initial output would be explicitly unpersonalized;
- rich why-fit, grounded personal risk, review-localization detail, play role, duration and some practical nuance are absent;
- as a permanent end-state it underserves the original goal of helping choose the best game for this user.

Conclusion: correct Phase 0 recovery shape, not the long-term target.

## 10. Comparison table

| Criterion | A — Harden current | B — Split core/enrichment | C — Cache-first | D — Minimal recovery |
| --- | --- | --- | --- | --- |
| Core daily availability | Low to medium; still tied to semantic completion | High if deterministic source is healthy | High after cache model is mature; unknown generation still needs fallback | Highest |
| Core dependence on Scheduled ChatGPT | High | None | None for core, medium for cache growth | None |
| One bad game blast radius | Potentially global via group/queue closure | Item-level | Item-level if cache queue is designed correctly | Item-level deterministic quarantine |
| Operational complexity | Very high | Medium | Medium to high | Low |
| Recovery difficulty | High | Low to medium | Medium | Low |
| Personalization quality | Highest only when complete | High where enriched, explicit pending elsewhere | High in steady state, weaker after invalidation | Low to medium |
| Stale-data tolerance | Low | Explicit and bounded | High but requires careful compatibility semantics | High for optional fields |
| Migration effort | Low code churn, high continuing operational cost | Medium | Medium to high | Low |
| Risk of month-long enrichment repair blocking user | High | Low | Low if fallback is explicit | Very low |

## 11. Explicit answers to the seven challenged assumptions

1. Does Taste Steam Review Dossier need to be on the daily critical path at all?  
   No. It is valuable background knowledge for evidence quality, risk/localization/current-state confidence and semantic grounding. It is not required to prove that a current Steam KZ discount exists.

2. Does Russian-review retrieval need to block a deal from appearing?  
   No. It may block a claim that depends specifically on Russian player feedback. It should not block the deterministic deal card or an explicitly pending personalization state.

3. Does exact fresh semantic evidence need to exist before every daily recommendation?  
   Not every day. An exact-compatible accepted Taste verdict can be reused without a wall-clock expiry while profile/model/fingerprint bindings remain unchanged. After a binding change, incompatible stale Taste must not be called current personalization; the offer can still appear as personalization_pending.

4. Should a group of three fail as one atomic unit for user-facing publication?  
   No. Grouping can remain a transport optimization during migration, but user-facing publication and canonical enrichment availability must be item-level. One bad game must not suppress two unrelated valid games or the rest of the catalog.

5. Is current content-complete binding protecting real correctness on the daily path, or only background knowledge updates?  
   It protects real correctness for accepting and interpreting enrichment results. The same binding is over-scoped when used as a prerequisite for current deal publication. Keep it at enrichment ingress; remove it from core availability.

6. Are “cannot prove enrichment is perfect” and “cannot safely show a discounted game” currently mixed?  
   Yes. Current ai_queue_count == 0 readiness and global sufficiently_complete_for_publication explicitly make those two concepts one gate.

7. Which invariants are essential user-safety/business invariants versus engineering-process invariants?  
   Essential product invariants: current source integrity, correct region/identity, active offer, deterministic content gates, symbolic-discount and budget rules, no false personalized claim from incompatible Taste, exact validation of any semantic fact that is actually published, and one explicit ranking authority per publication mode.  
   Engineering/process invariants: fixed daily dossier snapshot, group size 3, maximal contiguous prefix, content-complete prompt binding, fail-closed execution ledger, full backlog completion before semantic advancement, and exact retrieval route ordering. Those may be useful for background worker correctness but are not product-availability requirements.

## 12. Recommended target architecture — exactly one

Recommended target: DESIGN B — SPLIT CORE DEALS FROM ENRICHMENT.

Design C’s cache-first semantics should be used inside the enrichment side of Design B. Design D should be used only as the Phase 0 recovery posture. Design A should not remain the target.

The target has one user-facing artifact but two independent completeness dimensions:

- core_deals: deterministic, current, publishable without any LLM;
- personalization_enrichment: per-item, cached/async, never a global prerequisite for core_deals.

A fully personalized card remains subject to the existing Taste threshold and exact semantic binding. A nonpersonalized card must be visibly labelled pending/stale and must not invent why-fit/risk claims.

## 13. Core synchronous path

The target daily critical path should be:

1. GitHub collects/validates the complete Steam KZ discovery snapshot.
2. GitHub validates source freshness using the existing <=18-hour preparation gate.
3. GitHub builds Store/current offer facts, FX, family identity and deterministic content/price gates.
4. GitHub classifies history:
   - current exact history when available;
   - exact cached historical fact when still valid;
   - otherwise unverified, never fabricated.
5. GitHub constructs one core row per safe purchase family.
6. GitHub applies deterministic current-offer exclusions:
   - non-game/ineligible content;
   - known inactive sale;
   - symbolic discount <=5%;
   - absolute paid ceiling and other existing deterministic business gates.
7. GitHub overlays exact-compatible Taste cache if present.
8. GitHub assigns publication state per item:
   - personalized_current;
   - personalized_cached_compatible;
   - personalization_pending;
   - personalization_stale_not_authoritative;
   - item_quarantined.
9. GitHub ranks:
   - personalized items by the existing personalized policy;
   - pending items by one explicitly canonical deterministic fallback mode, using only current deal/purchase signals and sale urgency, not fake personal points.
10. GitHub writes data/production/visual/current.json and Pages serves it read-only.

No Scheduled ChatGPT invocation, Dossier completion, Russian review retrieval, semantic group progress or conversational retry may be required to reach step 10.

Initial availability SLO recommendation: publish the current core payload within 60 minutes of the existing 01:00 Europe/Samara production start, i.e. by 02:00, on days when the current source snapshot passes the existing freshness/integrity gates. This is a proposed operational SLO, not a claimed measured runtime guarantee. Its rationale is that the target core contains only existing deterministic transformations and explicitly removes unbounded web/LLM work. Measure real runs before promoting it to a contractual hard SLA.

## 14. Non-blocking enrichment path

Move these off the core critical path:

- Steam Review Dossier web research;
- Russian player-feedback retrieval;
- multi-source evidence diversification;
- temporal current-state evidence checks;
- grounded personal-negative enrichment;
- candidate-quality findings;
- play_role and relative_start_priority;
- duration enrichment when not already deterministic/cached;
- achievement quality interpretation;
- external compatibility/current technical evidence;
- any semantic explanation that needs the Dossier.

GitHub still owns the enrichment queue, exact item identity, retry state, binding/version, validation and canonical persistence.

Scheduled ChatGPT should receive a small immutable item-level work unit. It returns a bounded result. GitHub either:

- accepts that one item;
- rejects/quarantines that one item with a typed reason;
- marks it retryable.

A valid accepted enrichment result can trigger a deterministic visual rebuild/overlay or wait until the next daily build. Neither path may delay core publication.

Long-term semantic simplification: base price-blind Taste fit should not require a fresh full player-feedback dossier for every candidate. Intrinsic game metadata + the canonical profile can support base fit; dossier evidence should primarily refine confidence, negative/risk/current-state claims. Any future change here requires its own semantic contract review and must not silently weaken the definition of a fully personalized card.

## 15. Fallback hierarchy

### Taste verdict

- Fresh: exact current profile_blob_sha + taste_model_version + candidate fingerprint/binding.
- Last-known-good: an already accepted verdict with the same exact current binding. No wall-clock TTL is needed for the intrinsic Taste verdict because current rules already make profile/model/fingerprint change the invalidation event.
- Stale-but-allowed: incompatible old Taste may be retained for diagnostics/history only, not used to include/exclude or rank as current personalization.
- Unknown/default: personalization_pending; deterministic deal can still publish.
- Hard stop: only the personalized claim for that item. No hard stop for core deal availability.

### Steam Review Dossier / external player-feedback evidence

- Fresh: current accepted Dossier within the existing 20-day dossier TTL and compatible schema/binding.
- Last-known-good: same accepted dossier while within that TTL.
- Stale-but-allowed: after 20 days, durable traits may be retained as clearly stale background context; current-state-sensitive bugs/performance/localization/service claims become unknown unless supported by a fresh accepted source.
- Unknown/default: no dossier; personalization evidence/risk confidence pending.
- Hard stop: only claims that specifically require dossier evidence. Never the core deal.

### Current-state external review claim

- Fresh: must satisfy current temporal evidence policy; the existing recent-source rule remains strict for current-state claims.
- Last-known-good/stale: durable gameplay/structure observations may survive; “current bug/performance/localization state” may not.
- Unknown/default: omit the claim or mark unknown.
- Hard stop: that claim only.

### SteamDB / historical price

- Fresh: exact current-cycle history classification.
- Last-known-good: exact-key previously confirmed historical facts may remain known facts.
- Stale-but-allowed: if the commercial cycle advances without a successful history recheck, retain the old fact only as stale context and do not award “record/near-record” certainty from it.
- Unknown/default: history_quality = unverified, which the existing ranking model already knows how to represent.
- Hard stop: identity/key mismatch for that item, not the whole daily core.
- TTL: event-based rather than arbitrary wall clock — the comparison becomes stale when a new commercial source cycle cannot reconfirm it.

### Commercial/current offer facts

- Fresh: source accepted within the existing 18-hour preparation freshness gate.
- Last-known-good: prior complete core payload may remain visible as a stale fallback for at most one missed daily cycle.
- Stale-but-allowed: explicitly labelled stale; known sale_end is applied locally and expired rows are removed.
- Hard stop for “current” label: source older than the normal 18-hour gate.
- Proposed absolute LKG display ceiling: source age 42 hours, derived from the existing 18-hour maximum accepted source age plus one missed 24-hour daily cycle. After that the UI may show “data unavailable/stale” but must not imply current deals.

### Ranking inputs

- Fresh personalized rank: current commercial inputs + exact-compatible Taste + accepted optional inputs.
- Last-known-good personal factors: same exact compatible Taste binding.
- Pending fallback rank: deterministic sale urgency + purchase/deal components only, defined in the same canonical ranking authority as an explicit degraded mode.
- Unknown inputs: neutral/unverified, never invented.
- Hard stop: malformed core offer identity/current commercial input; missing optional personalization never hard-stops core.

## 16. Publication / partial-success semantics

Partial daily output should publish when the global source snapshot is trustworthy but individual items fail isolated deterministic/enrichment checks.

Rules:

- If the discovery/source manifest itself is incomplete, wrong-region, stale beyond the source gate, or internally inconsistent, do not publish a new “current” core. Keep LKG with explicit stale status.
- If one item has a bad identity, malformed current offer or another item-local deterministic blocker, quarantine that item and publish the rest with an omission reason/count.
- If one item lacks Taste/Dossier, publish it only in the nonpersonalized pending state.
- If one item has exact-compatible Taste below the personalized threshold or confirmed negative, do not present it as a personalized recommendation.
- No pending card may contain invented why_fit or personalized risk text.
- A daily payload with zero eligible items is valid if the complete current source was processed and omission/classification counts prove why.

Minimum valid daily payload:

- exact current source lineage/timestamp;
- core publication status;
- complete deterministic source partition;
- item-level current offer identity/price/discount/active-state facts for every shown item;
- core deterministic eligibility applied;
- per-item personalization status;
- omission/quarantine counts by reason;
- explicit core freshness and enrichment freshness;
- one canonical order for each declared publication mode.

## 17. Availability vs enrichment completeness

Replace the current single global publication concept with at least two independent machine concepts.

### Core availability completeness

Questions:

- Did the complete current Steam KZ source ingest?
- Was it within freshness limits?
- Were all source families deterministically classified as published, excluded, pending-personalization or item-quarantined?
- Was current.json written for that source?

Suggested states:

- current_complete;
- current_partial_with_item_quarantine;
- stale_lkg;
- blocked_source_integrity.

### Enrichment completeness

Questions:

- How many current core items have exact-compatible Taste?
- How many have fresh Dossier?
- How many are pending, stale, retryable or quarantined?
- What is the oldest pending enrichment age?

Suggested states:

- complete;
- partial;
- stale;
- unavailable.

Core publication never requires enrichment_complete = complete.

The current semantic_completeness.sufficiently_complete_for_publication = ai_queue_count == 0 is therefore the main coupling to retire for core publication.

## 18. Retry / recovery ownership

GitHub remains the retry/recovery authority.

Core:

- deterministic source/workflow failures use bounded GitHub Actions retry/re-run semantics;
- item-local deterministic failures are recorded as quarantined/omitted and retried on the next normal source cycle or a repository-defined bounded retry;
- no interactive chat loops.

Enrichment:

- GitHub owns per-item state: pending, leased/prepared, accepted, retryable, quarantined;
- Scheduled ChatGPT receives only an immutable exact item work unit and cannot choose queue order, invent retry filenames, declare completeness or repair canonical state;
- invalid result is rejected for that item only;
- binding change invalidates/requeues affected enrichment items only;
- a Scheduled Task that never runs simply causes pending count/age to grow;
- no user-facing core outage follows from enrichment backlog growth.

The existing create-only GitHub submission pattern can remain as a transport primitive, but canonical completion should be item-level rather than maximal-contiguous-prefix across groups.

## 19. Minimal observability model

The production system should expose a small GitHub-owned machine-readable status, not depend on verbose LLM final text.

Minimum aggregate fields:

- production_date / source_mailing_updated_at_utc;
- core_build_status;
- core_published_at_utc;
- core_source_age;
- core_item_count;
- core_omitted_count_by_reason;
- core_quarantined_count;
- core_payload_freshness = current / stale_lkg / unavailable;
- personalization_counts = current / compatible_cache / pending / stale / quarantined;
- dossier_counts = fresh / stale / pending / retryable / quarantined;
- enrichment_oldest_pending_age;
- last_valid_semantic_result_at_utc;
- last_valid_dossier_result_at_utc;
- last_enrichment_submission_at_utc if observable;
- Scheduled worker health = healthy / no_recent_accepted_result / unknown, explicitly distinguishing unknown platform state from failure.

This answers:

- did deterministic build run?;
- did a payload publish?;
- how many items were omitted and why?;
- how stale is personalization?;
- is Scheduled ChatGPT producing accepted results?;
- is backlog growing?

The fail-closed execution ledger can remain a debugging aid if the parallel observability review finds it useful, but it must not be the primary production health model and must not gate core deals.

## 20. Components to remove / demote / keep

### Remove from core publication

1. ai_queue_count == 0 as a prerequisite for building current paid deal output.
   - Correctness risk: without replacement semantics, unknown games might look personalized.
   - Mitigation: explicit personalization_pending card/state; no personal claims.

2. One global sufficiently_complete_for_publication bit that combines current deals and semantic enrichment.
   - Risk: partial semantic state may be misread as full success.
   - Mitigation: two explicit completeness dimensions.

3. Dossier full-backlog completion as an implicit prerequisite for current user output.
   - Risk: detailed risk/evidence confidence may lag.
   - Mitigation: show pending/stale enrichment state and restrict claims.

### Demote to background enrichment

- Russian-review retrieval;
- multi-source evidence;
- temporal review checks;
- exact current-state technical/localization evidence;
- grounded-negative Dossier pass;
- duration/play-role/start-priority/achievement-quality semantic enrichment;
- full Dossier content-complete binding.

Correctness risk: personalized explanations become less complete. Mitigation: those fields are omitted/pending until validated; they are never synthesized from missing data.

### Change from group-level to item-level

- Dossier canonical acceptance/progress;
- semantic failure/quarantine;
- retry accounting.

Risk: more per-item state and possibility of duplicate processing. Mitigation: GitHub-owned exact appid/work-key identity, idempotent accepted-result keys and deterministic validation.

### Cache

- exact-compatible Taste verdicts;
- Dossier with current 20-day freshness plus durable-trait stale semantics;
- exact historical facts;
- translations/media/practical facts where already safely cached.

### Replace with deterministic validation where possible

- core current deal eligibility;
- deal/purchase score components;
- sale expiry;
- source freshness;
- family/offer identity;
- fallback ordering;
- payload/completeness states.

### Keep strict and unchanged in principle

- GitHub control-plane ownership;
- exact source/region/identity correctness;
- price-blind Taste semantics for personalized fit;
- minimum Taste threshold for a personalized recommendation;
- symbolic-discount and absolute-budget rules;
- no commercial signal rewriting Taste;
- exact binding validation for AI results;
- privacy/provenance rules for persisted evidence;
- no stale incompatible Taste masquerading as current;
- UI as a read-only consumer;
- one canonical ranking authority, extended with an explicit degraded mode rather than duplicated hidden sorters.

## 21. Phase 0 — restore service

Objective: restore useful current discounted-game output without waiting for Dossier/Taste completion.

Exact architecture change class for a later IMPLEMENT:

- add a core fallback publication mode to the existing daily visual producer;
- allow fresh deterministic core rows to be built while ai_queue_count > 0;
- consume no incompatible old Taste as current personalization;
- mark every unresolved item personalization_pending;
- use one explicit deterministic fallback ranking mode;
- show a visible “personalization pending/degraded” state;
- preserve the existing source integrity gate and LKG behavior.

Use the existing commercial-only refresh implementation as proof that deterministic commercial updates can already be isolated from Taste mutation, but Phase 0 must build current core rows rather than merely refresh the three old semantic rows.

Acceptance:

- with a synthetic/current state equivalent to ai_queue_count=734 and Dossier progress 0/733, a current core payload is produced from the fresh commercial source;
- no Scheduled ChatGPT call is needed;
- no pending item receives fabricated why_fit/personalized risk;
- expired offers are removed;
- deterministic exclusions remain enforced;
- source-integrity failure still prevents a falsely current payload;
- the existing complete-personalized path remains valid when semantic work is actually complete.

Rollback:

- revert the bounded publication-mode change and continue serving the previous LKG payload; no data migration should be required for rollback.

What the user sees:

- current deals again;
- personalization status is explicit;
- personalized recommendations appear where valid cache exists;
- no old profile semantics are presented as current.

## 22. Phase 1 — isolate enrichment

Objective: make LLM/Dossier failures incapable of blocking unrelated enrichment and core publication.

Architecture change class:

- move Dossier/Taste work to a persistent background enrichment queue derived by GitHub;
- switch canonical Dossier/Taste result acceptance and retry accounting to item-level;
- keep immutable item work units and create-only handoff;
- remove global contiguous-prefix/head-of-line semantics from enrichment availability;
- allow accepted item results to overlay current core independently.

Acceptance:

- one invalid Dossier result, one retrieval failure, one binding mismatch and a completely absent Scheduled Task are separately injected/observed;
- current core still publishes;
- unrelated valid enrichment items are accepted;
- only failed items become pending/retryable/quarantined;
- no interactive recovery is needed.

Rollback:

- keep the old background group worker available but not as a core gate; item overlay can be disabled without losing core output.

What the user sees:

- same reliable current deal surface;
- increasing share of cards become personalized as background work catches up;
- failures affect only individual cards’ enrichment badges/fields.

## 23. Phase 2 — simplify / delete

Objective: remove machinery that existed primarily to make the globally coupled pipeline recoverable.

Candidate retirements after Phase 1 is proven:

- daily fixed full Dossier snapshot as a product-completeness concept;
- maximal-contiguous-prefix Dossier acceptance;
- group-level all-or-none canonical progress;
- duplicated prompt/validator guard layers that only compensate for group atomicity;
- global semantic publication bit;
- legacy readiness paths that wait solely for queue closure;
- verbose per-invocation fail-closed narration as an operational dependency.

Preserve evidence schema/validation rules that are still needed for the enrichment claims themselves.

Acceptance:

- one authoritative background item-state model;
- no old workflow can reintroduce a global enrichment gate;
- repository tests prove only one canonical core publication path and one canonical enrichment item-state path;
- no production behavior depends on obsolete group-completeness fields.

Rollback:

- do not delete old paths until Phase 1 has run successfully for multiple production cycles; retirement is by staged disable then removal.

What the user sees:

- no intended UX change from Phase 1; the benefit is lower maintenance and fewer failure modes.

## 24. Phase 3 — quality

Objective: improve personalization only after availability is stable.

Possible quality work:

- lightweight base Taste evaluation for new games from intrinsic metadata/profile without requiring a fresh full Dossier first;
- Dossier as selective risk/current-state confidence enrichment;
- background priority for sale-urgent or otherwise high-value pending items, with GitHub remaining queue owner;
- better compatibility/localization evidence;
- stronger explanation quality;
- tuning cache freshness based on observed drift;
- ranking UX improvements without moving analysis into the client.

Acceptance:

- core availability SLO remains satisfied during enrichment experiments;
- no new enrichment rule can change core publication status;
- personalized cards retain current Taste/business thresholds and exact provenance;
- measured user-facing improvement exists before adding more complexity.

Rollback:

- disable the new enrichment feature; cached/core deal output remains intact.

What the user sees:

- progressively more cards move from pending to high-quality personalized recommendations without losing daily availability.

## 25. Required later canonical changes

No changes are made by this review. If the Director/user approves the target, later IMPLEMENT work should be bounded to these canonical surfaces.

Likely Phase 0 surfaces:

- PROJECT_RULES.md: clarify that a degraded “current deal candidate / personalization pending” is not a personalized recommendation; do not change taste threshold or budget preferences.
- config/daily_execution_contract.json: split core availability from enrichment completeness; define proposed core SLO/LKG semantics.
- config/mailing_policy.json: define core publication state and pending personalization semantics.
- config/final_ranking_policy.json: add one explicit deterministic fallback/degraded ranking mode under the same ranking authority.
- scripts/semantic_runtime_completion.py: replace global semantic publication gate with separate core/enrichment status.
- scripts/build_daily_visual_payload.py: stop returning WAIT solely because ai_queue_count > 0 for core mode.
- scripts/build_final_visual_payload.py and/or scripts/build_visual_feed_v2.py: build current core rows, not merely refresh old semantic rows; do not emit invented personal explanations for pending cards.
- .github/workflows/build-daily-visual-payload.yml: run core build from successful deterministic pre-AI source regardless of semantic queue closure.
- web/app.js / paid freshness UI surfaces: render current/pending/stale states without recalculating semantics client-side.

Likely Phase 1/2 surfaces:

- config/execution_ownership_contract.json: ownership stays GitHub-first, but completion wording should distinguish core versus enrichment.
- config/taste_result_contract.json and taste cache contract: item-level background result lifecycle.
- config/taste_steam_review_dossier_contract.json and persistence bridge: background cache semantics, item-level acceptance/quarantine, no daily core dependency.
- Dossier worker/persistence workflows and validators: preserve exact validation but remove head-of-line group coupling after migration.
- PROJECT_DECISIONS.md: record the architectural reason for decoupling so future fixes do not recreate the global gate.

The parallel Scheduled-entrypoint observability preflight may still recommend a bounded worker-health mechanism. It should be integrated only as enrichment observability, not as a prerequisite for Phase 0 core publication.

## 26. REVIEW-01..15

- REVIEW-01 — PASS. User-facing purpose identified from canonical rules: taste-first purchase help, current deal value, budget constraints, and “do not lose games solely because secondary data is incomplete.”
- REVIEW-02 — PASS. Current path mapped from source through deterministic pre-AI, Dossier/Taste, ranking, visual/current and UI.
- REVIEW-03 — PASS. Legitimate core blockers separated from enrichment dependencies that should be non-blocking.
- REVIEW-04 — PASS. Scheduled prompt, binding mismatch, Taste backlog, Dossier retrieval, external variability, group fail-close, validator/generator parity, persistence handoff and long repair-cycle blast radii reviewed.
- REVIEW-05 — PASS. Designs A-D compared.
- REVIEW-06 — PASS. Exactly one target selected: Design B.
- REVIEW-07 — PASS. Dossier/Taste removed from daily core critical path; retained as background personalization/enrichment.
- REVIEW-08 — PASS. User publication and canonical enrichment outcomes should be item-level; batching may exist only as transport.
- REVIEW-09 — PASS. Fallback/LKG hierarchy defined for Taste, Dossier/reviews, history, current offers and ranking.
- REVIEW-10 — PASS. Core availability completeness separated from enrichment completeness.
- REVIEW-11 — PASS. Small GitHub-owned machine-observable status model defined; LLM prose is debugging-only.
- REVIEW-12 — PASS. Phase 0..3 plan includes objective, change class, acceptance, rollback and user-visible effect.
- REVIEW-13 — PASS. Later canonical change surfaces are explicitly bounded.
- REVIEW-14 — PASS. No implementation, production run, Scheduled Task trigger or production mutation occurred.
- REVIEW-15 — PASS. Exactly one next step is recorded below.

## 27. Changes: report only

Created only:

- reviews/worker_reports/production-architecture-simplification-review-01.md

No other repository or runtime state was intentionally changed.

## 28. Unresolved

These do not block the architecture recommendation:

- the exact UI placement/wording for personalization_pending versus personalized recommendations;
- whether all pending core candidates should be visible in one queue or a separate section, while retaining the current “full snapshot, not fixed TOP-N” principle;
- the exact implementation shape of a future lightweight base Taste step that no longer requires a fresh Dossier;
- actual deterministic runtime distribution, so the proposed 02:00 core SLO must be measured during implementation/acceptance;
- the parallel Scheduled-entrypoint observability preflight result, which may improve background worker diagnosis but does not change the core decoupling conclusion.

## 29. Status

complete_architecture_recommendation

The review has one target architecture, a Phase 0 that can restore useful output without advanced enrichment, explicit ownership and failure-isolation semantics, a cache/fallback model and no implementation.

## 30. Exactly one recommended next step

Return this report to the Director for comparison with the parallel Scheduled-entrypoint observability preflight, then obtain the user’s decision on the Design B migration direction before authorizing any IMPLEMENT task.

## 31. Exact refs

Primary task/protocol:

- CHAT_PROTOCOL.md — START/DURING/PRE-SEND gates and architecture-preflight requirement.
- WORKER_TASK_PRODUCTION_ARCHITECTURE_SIMPLIFICATION_REVIEW_01.md lines 121-155 — P2..P7 fallback/SLA principles.
- WORKER_TASK_PRODUCTION_ARCHITECTURE_SIMPLIFICATION_REVIEW_01.md lines 157-260 — Designs A-D and required recommendation dimensions.
- WORKER_TASK_PRODUCTION_ARCHITECTURE_SIMPLIFICATION_REVIEW_01.md lines 262-348 — simplification, phases, comparison, challenged assumptions and exclusions.
- WORKER_TASK_PRODUCTION_ARCHITECTURE_SIMPLIFICATION_REVIEW_01.md lines 352-445 — REVIEW-01..15 and durable report/status requirements.

Canonical product/execution:

- PROJECT_RULES.md — “Главная цель”, “Нельзя терять игры из-за неполных данных”, Taste/deal separation, budget and UI requirements.
- config/daily_execution_contract.json — execution_invariants, night_input_freshness, night_preparation, visualization_consumption.
- config/execution_ownership_contract.json — github_control_plane, scheduled_chatgpt_runtime_data_plane, architecture_change_gate.
- config/mailing_policy.json — delivery, ingest_qa, personal_filter, taste_cache, content_eligibility, pricing.
- config/final_ranking_policy.json — eligibility_boundary, automatic_final_priority_order, score_model, ui_override.

Current coupling implementation:

- scripts/semantic_runtime_completion.py lines 20-27: sufficiently_complete = partition_complete and unresolved == 0.
- scripts/semantic_runtime_completion.py lines 39-49: sufficiently_complete_for_publication and unresolved/resolved counters.
- scripts/semantic_runtime_completion.py lines 147-158: visual status becomes complete only when semantic completeness is sufficient.
- scripts/build_daily_visual_payload.py lines 308-341: current_production_readiness validates partition and returns None when ai_queue_count != 0.
- scripts/build_daily_visual_payload.py lines 388-392: normal visual build reports WAIT when source_key is absent due open AI queue.
- scripts/build_final_visual_payload.py lines 202-210: deterministic purchase refresh explicitly operates on an already accepted visual snapshot while semantic work is queued.
- scripts/build_final_visual_payload.py lines 333-364: commercial-only refresh preserves existing semantic fields.
- scripts/build_final_visual_payload.py lines 510-551: FORCE build with unresolved AI queue only refreshes the existing visual instead of rebuilding the current candidate population.
- .github/workflows/build-daily-visual-payload.yml lines 109-166: commercial freshness is intentionally classified independently of semantic completeness.
- .github/workflows/build-daily-visual-payload.yml lines 433-508: commercial-only refresh validates current source lineage and removes expired rows.
- .github/workflows/build-daily-visual-payload.yml lines 790-849: complete history classification gate then full visual builder.
- scripts/build_taste_semantic_dossier_input.py lines 11-22: downstream Taste semantic input is explicitly fail-closed on fresh V2 dossier input.

Dossier architecture:

- config/taste_steam_review_dossier_contract.json lines 6-18: complete fixed daily neutral dossier backlog before Taste semantic analysis and GitHub-owned scope/group plan.
- config/taste_steam_review_dossier_contract.json lines 55-60: worker cannot declare readiness before remaining snapshot scope reaches zero.
- config/taste_steam_review_dossier_contract.json lines 157-174: checkpoint size 3 is a durability boundary across the entire prepared snapshot.
- config/taste_steam_review_dossier_contract.json lines 219-235: worker progression follows predeclared groups and cannot declare completeness.
- config/taste_steam_review_dossier_contract.json lines 252-260: GitHub drain accepts only maximal valid contiguous prefix and stops at first invalid/missing expected group.
- PROJECT_DECISIONS.md TASTE-004..TASTE-012 — evolution of full backlog, fixed snapshot, buffered groups, multi-source/Russian/temporal/provenance gates.
- PROJECT_DECISIONS.md STEAMDB-001 — explicit distinction between stage completeness and persistence of already verified partial facts; directly relevant precedent against over-broad blocking.

Current production evidence:

- data/production/pre_ai/chatgpt_payload.json — source_family_count 794, ai_queue_count 734, ready_without_ai_count 0, deterministic excluded 60, current commercial source 2026-09-19T22:47:44.410194+00:00.
- data/production/pre_ai/chatgpt_taste_queue.jsonl — 734 rows; 733 require evaluate_taste_fit + evaluate_normalized_taste_factors + resolve_grounded_negative_analysis and one additionally requires base-support resolution; no current resolved Taste fields in the queue.
- data/production/pre_ai/taste_steam_review_dossier_work.json — snapshot ad93a448…, prepared/remaining/completed 733/733/0, 245 groups, checkpoint 3.
- data/production/visual/current.json — semantic source 2026-08-30, 3 visible items, degraded semantic completeness, but commercial-only freshness published from 2026-09-19/20 source data.

Repeated-failure evidence:

- DIRECTOR_TASK_BOARD.md — active architecture review, paused Run now, accepted entrypoint-ledger diagnostic and sequence of recent Dossier repair tasks.
- reviews/worker_reports/taste-dossier-scheduled-entrypoint-ledger-diagnostic-01.md — canonical prompt aligned but live Scheduled Task entrypoint not exposed; current live omission remains insufficiently observable to classify.
- reviews/worker_reports/taste-steam-review-dossier-persistence-bridge-01.md — prior real persistence/handoff defect and hosted bridge acceptance.
- reviews/worker_reports/taste-dossier-validator-generator-parity-audit-01.md — concrete generator/strict-validator mismatches capable of blocking Dossier candidates.
- reviews/worker_reports/taste-dossier-fail-closed-execution-ledger-implement-01.md — additional observability/route accounting implemented without solving the structural daily-availability dependency.

## 32. Efficiency / reusable lesson

The review took longer than a narrow code check because the decision required reconciling user-facing rules, ownership contracts, actual current queue/dossier/visual state, the exact readiness code path, and a bounded sample of repeated failure reports.

The shortest reusable architecture-debug route for this project is now clear:

1. read CHAT_PROTOCOL + task + PROJECT_ROUTES;
2. inspect current chatgpt_payload counters;
3. inspect current Dossier manifest counters;
4. inspect visual/current freshness/completeness;
5. read scripts/semantic_runtime_completion.py and current_production_readiness;
6. only then inspect the few failure reports needed to classify blast radius.

That sequence reaches the structural diagnosis without replaying the project’s full history. The durable simplification lesson is equally direct: correctness gates should be scoped to the claim they protect. Exact evidence/binding checks are valuable for personalized enrichment, but they should not become availability gates for deterministic current deal facts.
