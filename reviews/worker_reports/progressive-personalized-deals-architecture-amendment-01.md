# Progressive Personalized Deals Architecture Amendment 01

## 1. Task / repo / mode

- Task ID: `progressive-personalized-deals-architecture-amendment-01`.
- Authoritative task: `WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_ARCHITECTURE_AMENDMENT_01.md`.
- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- Base/source of truth: `main`.
- Mode: `READ-ONLY / ARCHITECTURE AMENDMENT`.
- Direct continuation of `production-architecture-simplification-review-01`; the previous architecture audit was not restarted.
- No other repository was searched, read, changed, or used.
- No source, contract, workflow, UI, production payload, queue, cache, automation, Scheduled Task, or production state was changed.
- No game was processed manually.
- The only allowed and intended repository write is this amendment report.

This amendment preserves the previous review's main structural conclusion — daily current-deal publication must not be globally blocked by Taste/Dossier/Scheduled ChatGPT — but replaces the previous generic `personalization_pending` fallback ordering with the user's explicit progressive personalized ordering.

## 2. Accepted user correction

The product is still **personalized deal discovery**, not a neutral deal catalogue.

The automatic normal-list ordering must be:

1. **Successfully analysed + fits the user** — first.
2. **Analysis was attempted but could not be completed** — second.
3. **Not analysed yet** — last.
4. **Successfully analysed + does not fit** — excluded from the normal visible list.

All current deterministic-eligible candidates must remain visible before successful semantic analysis unless an existing hard deterministic source/business/identity rule excludes the item.

Therefore:

- lack of analysis is not exclusion;
- analysis failure is not exclusion;
- lack of Russian reviews is not exclusion;
- missing Dossier enrichment is not exclusion;
- only a successful semantic result that establishes “not fit” may remove a candidate for Taste reasons;
- a candidate that has not yet received a trustworthy fit/not-fit conclusion remains visible.

This explicitly amends the previous report's Phase-0 concept. Pending candidates remain a lower tier inside the same personalized product instead of competing on equal footing with successful personalized recommendations.

## 3. Architecture ownership preflight

### 3.1 Item analysis state owner

**GitHub control plane** owns the canonical per-item analysis state.

The state is derived from:

- the current deterministic-eligible candidate set;
- exact-compatible accepted Taste results/cache;
- accepted item-level semantic submissions;
- GitHub-owned validation outcomes;
- GitHub-owned retry/recovery decisions.

Scheduled ChatGPT may produce a semantic attempt result. It does not decide or persist the canonical state directly.

### 3.2 PASS 1 / PASS 2 queue and order owner

**GitHub control plane** owns:

- which candidates belong to the current candidate set;
- which candidates are already successfully analysed through compatible cache;
- the PASS 1 work set and deterministic order;
- the PASS 2 recovery set and deterministic order;
- whether an item has already consumed its allowed PASS 1/PASS 2 attempt for the current semantic generation.

Scheduled ChatGPT receives immutable GitHub-prepared work only.

### 3.3 Retry owner

**GitHub control plane** owns canonical retry decisions.

Scheduled ChatGPT may report a typed observable failure/result. It must not:

- create its own retry queue;
- skip ahead by inventing progress;
- choose alternate retry files;
- retry conversationally until success;
- declare a permanently difficult item resolved.

### 3.4 Site counts owner

**GitHub** computes and persists all processing counts in machine-readable production state and projects them into `data/production/visual/current.json`.

The browser only renders those counts. It does not infer hidden ChatGPT progress.

### 3.5 Does this add a new recurring stage/queue/retry owner?

It adds a **new explicit two-pass queue/state model inside the existing GitHub-owned semantic control plane**, but it does **not** require:

- a new queue owner;
- a new retry owner;
- a new interactive-chat responsibility;
- a second independent scheduler;
- a second independent Scheduled ChatGPT producer.

The existing semantic worker can consume work labelled by pass/purpose. The existing Dossier worker can be demoted/re-scoped rather than duplicated.

### 3.6 Required canonical contract change before implementation

Yes. This user correction conflicts with current canonical assumptions that:

- a current daily paid visual waits for the AI queue to close;
- current Dossier scope is prepared as one full backlog before Taste semantic analysis;
- Dossier canonical advancement uses group/maximal-contiguous-prefix progress;
- current V5 `insufficient` semantics are an `EXCLUDE` state even when the reason is inability to establish enough candidate evidence;
- normal paid-card semantics currently require grounded negative readiness;
- current visualization is described as a single fully prepared frozen semantic snapshot after production completion.

Before Phase A/B implementation, a canonical progressive-personalization contract must define the new state machine, tier order, two-pass semantics, counts and publication behavior. Existing daily execution, mailing/Taste and ranking contracts must then reference it.

### 3.7 Ownership transfer check

No control-plane responsibility moves into Scheduled ChatGPT or this interactive chat.

The design preserves the existing `config/execution_ownership_contract.json` principle:

- GitHub = scope/order/state/retry/validation/persistence/completeness/publication;
- Scheduled ChatGPT = bounded semantic/data-plane worker;
- interactive chat = architecture/development only.

## 4. Per-item state machine

Use exactly four durable user-relevant states.

`analysis_in_progress` should **not** be a durable canonical item state.

Reason: a worker attempt can disappear through timeout/tool/runtime interruption. Persisting “in progress” would require leases, expiry and crash-recovery semantics and would complicate the arithmetic without improving user correctness. Until GitHub accepts an outcome, the item remains in its previous durable state.

An optional operational field such as `active_attempt_count` may exist in runtime observability, but it is not part of the per-item state partition and is not needed for site correctness.

| Durable state | Visible normal list? | Automatic tier | Personal score/text? | Successfully analysed? | PASS 2? | Exit transition |
| --- | --- | --- | --- | --- | --- | --- |
| `not_analyzed` | Yes | Tier 3 | No personal score; no `why_fit`/personal risk claims | No | No; first goes to PASS 1 | accepted PASS 1 result -> `analyzed_fit`, `analyzed_not_fit`, or `analysis_incomplete` |
| `analyzed_fit` | Yes | Tier 1 | Yes, only from accepted exact-compatible fit result; optional enrichment fields may remain unknown | Yes | No for fit decision; optional background enrichment may continue | binding/fingerprint invalidation -> `not_analyzed`; later accepted semantic reevaluation may change outcome |
| `analyzed_not_fit` | No normal list | excluded | No recommendation score/card in normal list | Yes | No | binding/fingerprint invalidation -> `not_analyzed`; later accepted reevaluation may change outcome |
| `analysis_incomplete` | Yes | Tier 2 | No fake full personal score; show only deterministic deal facts and safe already-known fields | No | Yes if PASS 2 budget for this semantic generation remains | accepted recovery -> `analyzed_fit` or `analyzed_not_fit`; failed recovery -> remains `analysis_incomplete` |

### 4.1 Semantic generation identity

Automatic attempt budget must be tied to a semantic generation, not blindly to each daily commercial refresh.

A generation should be invalidated by material semantic input changes such as:

- canonical profile binding;
- Taste model/semantics version;
- candidate taste fingerprint/context binding;
- a relevant semantic contract change that requires reevaluation.

A mere new current price snapshot must not reset the semantic retry budget.

### 4.2 Important mapping rule: insufficient evidence is not successful “not fit”

The progressive state machine must distinguish:

- **trustworthy below-threshold/confirmed-negative conclusion** -> `analyzed_not_fit`;
- **cannot establish enough evidence to make a trustworthy fit/not-fit conclusion** -> `analysis_incomplete`.

This is necessary to satisfy the user's explicit rule that a game must remain visible until analysis actually resolves it.

The current V5 `fit_evidence_state=insufficient` + `EXCLUDE` semantics therefore cannot automatically mean `analyzed_not_fit` in the progressive product. When “insufficient” means candidate information is insufficient, the item belongs in Tier 2 and proceeds to recovery.

## 5. PASS 1 — coverage first

### 5.1 Purpose

PASS 1 maximizes breadth of trustworthy fit/not-fit coverage.

It must not perform deep recovery on a difficult candidate before moving to the next unresolved candidate.

### 5.2 Initial projection

For the current deterministic-eligible candidate set GitHub first applies compatible accepted semantic cache:

- exact-compatible complete fit result -> immediately project to `analyzed_fit` or `analyzed_not_fit`;
- incompatible old result -> does not classify the current item;
- “insufficient because evidence is missing” -> `analysis_incomplete`, not successful not-fit;
- no result -> `not_analyzed`.

Thus accepted cache reduces PASS 1 work without weakening bindings.

### 5.3 PASS 1 queue

PASS 1 contains only current items in `not_analyzed`.

Recommended deterministic order:

1. sale-expiry urgency, when known;
2. existing taste-independent purchase/deal value component;
3. stable source/candidate order as final tie-break.

This does not change visible tier semantics; it only makes the most time-sensitive/useful candidates become personalized sooner while still guaranteeing one first attempt for every unresolved candidate.

### 5.4 PASS 1 outcome rule

Each attempted item must end the first accepted attempt in exactly one durable outcome:

- `analyzed_fit`;
- `analyzed_not_fit`;
- `analysis_incomplete`.

A worker/runtime failure that produces no valid semantic result is recorded by GitHub as `analysis_incomplete` with a safe machine-readable issue code.

### 5.5 No item-level head-of-line blocking

After one item reaches any of those three outcome classes, GitHub moves PASS 1 forward.

A failure or invalid result for item N must not prevent item N+1 from being attempted.

### 5.6 PASS 1 completion

`pass1_complete = (not_analyzed_count == 0)`.

This is independent from:

- number of `analysis_incomplete` items;
- Dossier completeness;
- PASS 2 completeness;
- full background enrichment.

## 6. PASS 2 — recovery only

> **Superseded PASS 2 start rule — 2026-09-21:** Section 6.1 below records the earlier architecture choice and is no longer current. Canonical decision `PPD-003` and `config/progressive_personalization_contract.json#phase_c_pass2_design` replace the global `not_analyzed_count == 0` start barrier with a per-item Dossier-ready gate. PASS 1 and PASS 2 may operate independently in parallel; only a current `analysis_incomplete` item with a canonically accepted exact-compatible Dossier and unused one-shot PASS 2 budget is eligible. Waiting for Dossier consumes zero PASS 2 attempts. This report remains otherwise historical and is not a runtime activation.

### 6.1 Start rule

PASS 2 should start **only after PASS 1 has covered the entire current semantic candidate set**, i.e. `not_analyzed_count == 0`.

This is the simplest rule that guarantees recovery work cannot starve first-pass catalogue coverage.

An implementation may use otherwise-idle worker capacity only if GitHub can prove that no PASS 1 work is runnable, but this optimization is not required for the target architecture.

### 6.2 PASS 2 scope

PASS 2 contains only `analysis_incomplete` items that have not yet consumed their allowed recovery attempt for the same semantic generation.

### 6.3 Recovery depth

PASS 2 may use the heavier mechanisms intentionally avoided in PASS 1, including when relevant:

- fresh Dossier;
- Russian player-feedback retrieval;
- source diversification;
- temporal current-state retrieval;
- deeper candidate-specific evidence;
- any contract-approved recovery path needed to turn ambiguity into a trustworthy fit/not-fit result.

### 6.4 Retry state complexity

Do not introduce multiple durable retry states.

Keep one user/item state:

- `analysis_incomplete`.

Store separate machine metadata:

- `issue_code`;
- `pass1_attempted_at`;
- `pass2_attempted_at`;
- `pass2_attempted_generation_id`;
- optional last accepted/validation error class;
- whether another automatic PASS 2 attempt is currently eligible.

### 6.5 Infinite-loop prevention

For one semantic generation:

- PASS 1: at most one accepted/recorded attempt;
- PASS 2: at most one bounded automatic recovery attempt.

If PASS 2 still cannot resolve the item:

- it remains `analysis_incomplete`;
- it stays visible in Tier 2;
- it leaves the automatic retry queue for that semantic generation.

It is automatically eligible again only after a material semantic input/binding change or a separately canonical, bounded operator recovery decision.

This prevents a permanently difficult game from consuming the worker indefinitely.

### 6.6 Recovery success

A valid recovered fit result atomically changes the state to:

- `analyzed_fit`, or
- `analyzed_not_fit`.

GitHub then republishes the current progressive visual state. No global completion is required.

## 7. Sorting contract

The automatic queue must sort by **analysis tier first**. Scores from different tiers are never compared.

### Tier 1 — `analyzed_fit`

Sort using the existing personalized ranking authority.

When the user's existing “urgency first” mode is enabled:

1. analysis tier = 1;
2. existing `sale_expiry_urgency_asc`;
3. existing `total_score_desc`;
4. title.

When “urgency first” is disabled:

1. analysis tier = 1;
2. existing `total_score_desc`;
3. title.

No change to the 0–100 personalized score weights is proposed by this amendment.

### Tier 2 — `analysis_incomplete`

No `total_score` pretending to be comparable with Tier 1.

Within Tier 2:

- urgency-first ON:
  1. sale-expiry urgency;
  2. producer-owned taste-independent purchase score/value;
  3. title;
- urgency-first OFF:
  1. producer-owned taste-independent purchase score/value;
  2. title.

The purchase-only value may reuse the existing purchase component semantics from `FINAL-PRIORITY-RANKING-V2`, but must be surfaced as a separate intra-tier key, not as a 0–100 personal score.

### Tier 3 — `not_analyzed`

Same secondary ordering as Tier 2:

- urgency-first ON: urgency -> purchase-only value -> title;
- urgency-first OFF: purchase-only value -> title.

### `analyzed_not_fit`

Excluded from the normal visible list.

### Existing explicit user override

The existing `manual_end_at` rule remains absolute because it represents an explicit user action, not automatic ranking.

Therefore the tier contract governs **automatic order**. A user who explicitly sends an item “to the end of queue” may place it after lower automatic tiers until that local override is cleared.

### Smallest adjustment to current urgency UI

Current web ordering can let urgency/score choose order over the whole `items` array. Under the new contract, the UI must first respect producer-owned analysis tier, then apply the existing user urgency toggle only inside a tier.

The browser still does not calculate Taste or deal semantics; it only chooses between producer-provided sort fields inside already-defined tiers.

## 8. Site per-item labels

Use a small, explicit label set.

### `analyzed_fit`

Primary label:

- **“Разобрана · подходит вам”**

The card may show:

- existing personalized score;
- grounded `why_fit`;
- only those risks/explanations whose evidence is actually available.

If deeper Dossier-derived risk/current-state enrichment is still absent, do not invent it. The UI may say **“Дополнительные риски ещё уточняются”** only if the producer explicitly supplies that status.

### `analysis_incomplete`

Primary label:

- **“Разбор не завершён”**

Optional short reason category:

- “не хватило данных”;
- “ошибка источника”;
- “результат не прошёл проверку”.

Do not expose raw tool errors, private model reasoning, usernames or evidence bodies.

If PASS 2 is still eligible, an additional neutral note may say:

- **“Будет повторный разбор”**.

After the one bounded PASS 2 attempt is exhausted, omit that promise; the item remains “Разбор не завершён”.

### `not_analyzed`

Primary label:

- **“Ещё не разобрана”**

No personalized score, `why_fit` or personal-risk conclusion.

### `analyzed_not_fit`

No normal card because the item is excluded from the normal list.

Its count remains visible in aggregate progress.

## 9. Site aggregate counters + invariants

### 9.1 Minimal recommended visible set

Primary progress line:

- **Всего** — `total_current_candidates`.
- **Разобрано** — `analyzed_success_count`.
- **Ошибки / не завершено** — `analysis_incomplete_count`.
- **Ещё не разобрано** — `not_analyzed_count`.

Under “Разобрано”, show compact subcounts:

- **Подходит** — `analyzed_fit_count`.
- **Не подходит / исключено** — `analyzed_not_fit_count`.

Also show:

- `last_accepted_analysis_at_utc` — “Последний успешный разбор”.

This is the smallest useful set that lets the user distinguish:

- real progress;
- hidden-by-fit exclusions;
- errors;
- untouched work;
- whether progress has stopped.

### 9.2 PASS 2 count

Expose **“Повторный разбор: N”** only when `pass2_pending_count > 0`.

It need not be a permanent top-level metric when zero.

### 9.3 Arithmetic invariants

Because `analysis_in_progress` is not durable:

`total_current_candidates = analyzed_fit_count + analyzed_not_fit_count + analysis_incomplete_count + not_analyzed_count`

`analyzed_success_count = analyzed_fit_count + analyzed_not_fit_count`

`pass1_covered_count = analyzed_success_count + analysis_incomplete_count`

`pass1_covered_count + not_analyzed_count = total_current_candidates`

`normal_visible_count = analyzed_fit_count + analysis_incomplete_count + not_analyzed_count`

`pass1_complete = (not_analyzed_count == 0)`

`pass2_pending_count <= analysis_incomplete_count`

### 9.4 Site consistency while a worker is active

A currently running attempt does not move the item into a special partition.

Until GitHub accepts an outcome:

- PASS 1 item remains `not_analyzed`;
- PASS 2 item remains `analysis_incomplete`.

Therefore a browser refresh never sees a transient state that breaks the total arithmetic.

## 10. Publication semantics

### 10.1 Initial current catalogue

A fresh deterministic candidate set is publishable immediately with zero semantic results.

Valid example:

- total = 734;
- analyzed_fit = 0;
- analyzed_not_fit = 0;
- analysis_incomplete = 0;
- not_analyzed = 734;
- normal_visible = 734.

### 10.2 Progressive publication

As GitHub accepts each item outcome, it updates the canonical state and republishes the visual projection.

The same day's deterministic commercial catalogue remains frozen/current according to the existing daily source snapshot, while its **GitHub-owned semantic overlay progresses**.

The site remains read-only. Opening/refreshing the page:

- performs no Steam/API/web lookup;
- performs no Taste evaluation;
- performs no retry;
- only reads the latest canonical progressive payload.

### 10.3 What never blocks fresh catalogue publication

Publication does not wait for:

- all Taste results;
- all Dossiers;
- Russian review retrieval;
- PASS 1 completion;
- PASS 2 completion;
- zero analysis errors.

### 10.4 What still blocks or excludes

Global current-publication hard stops remain only for actual source-integrity failures where the whole current candidate set is untrustworthy.

Item-level deterministic failures such as unresolvable identity/current offer can quarantine/exclude that item without blocking unrelated items when the source manifest itself is trustworthy.

Existing hard current-offer/content/price/business rules remain authoritative.

### 10.5 Daily contract amendment required

The current `daily_execution_contract.json` describes one fully prepared semantic daily snapshot after AI closure.

The new contract should instead distinguish:

1. **daily deterministic catalogue snapshot** — fixed current commercial/source scope;
2. **progressive semantic overlay** — GitHub-owned accepted per-item state/results that may advance after initial catalogue publication.

This is not client-side live analysis. It is progressive server-side publication of canonical state.

## 11. Existing group/checkpoint treatment

### 11.1 Groups may remain transport-only

A group of three may remain as a worker input/read efficiency detail during migration.

It must no longer be a canonical atomic outcome.

### 11.2 Required acceptance change

Canonical validation/persistence must become per-item.

For a three-item transport group:

- valid item A persists and advances A;
- invalid/error item B becomes/retains `analysis_incomplete`;
- valid item C persists and advances C;
- PASS 1 then continues to later items.

A malformed group envelope may still be rejected if the envelope itself destroys item identity/binding trust. But one semantically bad child must not invalidate trustworthy siblings.

### 11.3 Exact item validation is preserved

Per item, keep strict:

- exact appid/key identity;
- candidate/profile/model/fingerprint binding;
- evidence/provenance/privacy rules for any evidence that is persisted;
- result schema;
- no author identity leakage;
- no wrong-product evidence;
- no guessed bindings.

Throughput does not justify weakening evidence correctness.

### 11.4 Maximal-contiguous-prefix

The current Dossier `accept maximal valid contiguous prefix; stop at first gap/invalid expected group` rule is incompatible with the new product requirement if it remains canonical progress authority.

It should be retired from **semantic completion/progress**.

It may temporarily remain in an old background transport compatibility path during migration, but it must not determine:

- whether later items can be accepted;
- whether PASS 1 can continue;
- whether the site can publish;
- whether unrelated semantic results become visible.

### 11.5 Group completion

`full_backlog_complete` may remain as an internal background Dossier metric while the old worker exists, but it is no longer a user-facing publication or Taste PASS 1 prerequisite.

## 12. Taste/Dossier relationship comparison A–C

### A — full Dossier before fit verdict

Advantages:

- strongest current evidence package before every fit outcome;
- minimal conceptual split from current Dossier-first path.

Problems:

- external web/Russian/temporal/source variability remains on PASS 1;
- a difficult player-feedback retrieval can turn a simple first-pass fit decision into an error;
- catalogue coverage remains slow;
- current evidence architecture was built for rich neutral player feedback, while current Taste positive fit rules explicitly do not treat public review sentiment as positive fit proof;
- poor match for “coverage first”.

Verdict: **not chosen**.

### B — lightweight fit first; Dossier only for richer explanation/risk/current-state evidence

Advantages:

- matches the existing price-blind intrinsic-fit model;
- removes web retrieval from most first-pass decisions;
- enables fast broad coverage;
- Dossier remains useful for risk/current-state/localization evidence.

Problems:

- ignores already accepted compatible semantic/Dossier knowledge if implemented literally;
- would redo work unnecessarily.

Verdict: strong base design, but not the best complete choice.

### C — hybrid: compatible cache fast path + lightweight fit fallback

Definition:

1. if an exact-compatible accepted Taste result already exists, project it immediately;
2. otherwise run lightweight PASS 1 from existing canonical candidate/profile inputs;
3. use compatible cached Dossier/evidence when already available, but never wait for fresh Dossier to start PASS 1;
4. when lightweight evidence cannot support a trustworthy fit/not-fit conclusion, return `analysis_incomplete`;
5. use PASS 2 Dossier/deeper retrieval only for those incomplete cases;
6. optional rich Dossier enrichment for already-fit games remains non-blocking background work.

Advantages:

- maximizes reuse;
- preserves strict bindings;
- gives broad coverage fastest;
- keeps Dossier value without making it universal critical path;
- naturally handles the “accepted cached Taste exists” case.

Verdict: **chosen**.

## 13. Exactly one chosen semantic path

Choose **C — compatible-cache fast path + lightweight PASS 1 fallback + Dossier/deep research only for recovery/background enrichment**.

### 13.1 Minimal successful PASS 1 fit result

A new `analyzed_fit` result must still satisfy the current Taste quality threshold; this amendment does not lower `moderate`.

At minimum it must have:

- exact candidate/profile/model/fingerprint binding;
- a valid `INCLUDE` / `moderate+` fit conclusion;
- current normalized Taste factors required by the ranking contract for a new evaluation;
- specific grounded positive evidence under the existing intrinsic gameplay/mechanics/structure rules;
- enough evidence to classify the fit decision as trustworthy rather than “candidate information insufficient”.

### 13.2 Successful not-fit

`analyzed_not_fit` requires a valid accepted semantic result that actually supports a below-threshold or confirmed-negative conclusion.

Examples:

- well-grounded specific structural conflict;
- confirmed strong personal negative;
- enough candidate-specific evidence to determine below-moderate fit.

A mere lack of candidate information is not enough.

### 13.3 Dossier not required for every PASS 1 success

PASS 1 does not require fresh:

- Russian player review;
- multi-source Dossier;
- temporal current-state evidence;
- exhaustive grounded risk analysis.

Those claims remain unavailable/unknown until supported.

### 13.4 Personal score honesty

Tier 1 may use the existing personalized ranking authority after successful fit analysis.

Unknown optional risk/current-state enrichment must remain visibly unknown and must not create fabricated negative or positive claims.

No Tier 2/3 item receives a fake `total_score`.

### 13.5 Current V5 contract conflict to resolve

Current `TASTE-SEMANTIC-RESULT-V5` bundles fit, grounded negatives and evidence state more tightly than this progressive state model requires, including:

- `normal_paid_card_requires_grounded_taste_negative_witness`;
- `insufficient_requires_exclude`.

A later canonical amendment must split:

- **fit decision completeness**;
- **rich negative/current-state enrichment completeness**.

Taste threshold and exact binding remain strict.

### 13.6 Commercial reconsideration conflict

Current canonical rules contain bounded post-Taste commercial bridges for:

- `insufficient + wishlist + canonical good deal`;
- `reconsiderable + strict package savings`.

The user's new direction says a successfully analysed true non-fit item is excluded from the normal list.

Therefore later canonical contract work must reconcile these cases explicitly:

- “insufficient because evidence is not enough” maps to `analysis_incomplete`, so it stays visible without pretending fit;
- a truly completed below-moderate/`reconsiderable` result maps to `analyzed_not_fit` and is excluded from the normal list under the new authoritative product direction.

This changes normal-list publication semantics, not the Taste threshold itself.

## 14. Failure scenarios

### Scheduled ChatGPT does not run

User sees:

- current deterministic candidate set;
- compatible-cache successes in Tier 1 or excluded not-fit;
- all other items in Tier 3 “Ещё не разобрана”;
- progress counts stop advancing;
- last successful analysis timestamp makes the stall visible.

What continues:

- current deal publication;
- deterministic commercial refresh;
- site availability.

### One item errors

User sees:

- that item moves from Tier 3 to Tier 2 “Разбор не завершён” after GitHub records the failed first attempt.

What continues:

- PASS 1 immediately advances to the next item;
- site publication;
- unrelated accepted results.

### One bad item inside a batch/group

User sees:

- valid siblings can become Tier 1 or disappear as not-fit;
- bad item becomes Tier 2.

What continues:

- later items/batches;
- no maximal-prefix head-of-line block.

### Russian review unavailable

PASS 1:

- does not fail solely because Russian review retrieval is unavailable if lightweight fit evidence is sufficient.

PASS 2/background:

- Russian-current/localization claim remains unavailable;
- if Dossier is genuinely required to resolve an ambiguous fit case and recovery still cannot establish enough evidence, item stays Tier 2.

### Dossier incomplete

User sees:

- no loss of the candidate solely for that reason.

If fit is already established:

- item may be Tier 1 with only supported personalized fields.

If fit itself cannot be established without deeper evidence:

- item is Tier 2.

### Binding changes

GitHub:

- rejects incompatible returned results;
- stops treating incompatible semantic cache as current;
- reprojects affected current candidates to `not_analyzed` unless another exact-compatible accepted result exists.

User sees:

- affected games move down to Tier 3 rather than disappearing.

### Accepted compatible Taste exists

GitHub:

- uses it immediately.

User sees:

- fit -> Tier 1;
- trustworthy not-fit -> absent from normal list and counted in analysed/not-fit.

No PASS 1 attempt is spent on that item.

### Analysis result invalid

GitHub:

- rejects the invalid semantic payload;
- records a safe typed attempt failure for that item;
- sets/keeps `analysis_incomplete`;
- does not persist untrusted semantic claims.

User sees:

- Tier 2 “Разбор не завершён”.

Other items continue.

### PASS 2 repeatedly cannot resolve item

There is no repeated automatic loop.

After the one PASS 2 recovery attempt for the semantic generation:

- item stays `analysis_incomplete`;
- remains visible Tier 2;
- leaves automatic retry queue;
- may be retried only after material semantic input change or a new bounded canonical recovery decision.

## 15. Target architecture

Target: **Progressive Personalized Deals**, an amendment of the prior Design B split-core architecture.

The architecture has three independent concepts:

1. **Current deterministic candidate catalogue**
   - GitHub-owned;
   - publishable immediately;
   - current offer/source/business correctness only.

2. **Progressive fit-analysis state**
   - GitHub-owned per item;
   - exact-compatible cache fast path;
   - PASS 1 coverage;
   - PASS 2 recovery;
   - drives Tier 1 / Tier 2 / Tier 3 / exclusion.

3. **Optional rich enrichment**
   - Dossier/current-state/localization/risk/detail;
   - may improve already-fit cards;
   - never global publication readiness.

The normal visible list is therefore always personalized in ordering intent:

- known fits first;
- unresolved errors next;
- untouched candidates last;
- known non-fits absent.

## 16. Phase A — progressive display + state/count model

### Objective

Restore useful visibility immediately and encode the user's ordering before changing the semantic worker.

### Smallest likely canonical/source/UI surfaces

Canonical:

- introduce a dedicated progressive-personalization contract (recommended rather than overloading unrelated contracts);
- reference it from:
  - `config/daily_execution_contract.json`;
  - `config/mailing_policy.json`;
  - `config/final_ranking_policy.json`;
  - relevant `PROJECT_RULES.md` / `PROJECT_DECISIONS.md`.

Producer/state:

- `scripts/semantic_runtime_completion.py`;
- `scripts/build_pre_ai_chatgpt_payload.py`;
- `scripts/build_daily_visual_payload.py`;
- `scripts/build_final_visual_payload.py`;
- visual payload schema/projection.

UI:

- `web/app.js`;
- `web/index.html` / relevant CSS/tests;
- current paid-freshness/progress rendering.

A GitHub-owned current candidate analysis-state manifest is likely needed because accepted Taste cache alone cannot represent `not_analyzed` and `analysis_incomplete`.

### Behavior

- project exact-compatible accepted results;
- all other deterministic-eligible candidates = `not_analyzed`;
- publish all visible states immediately;
- enforce tiers;
- emit counts/invariants;
- no semantic worker redesign yet.

### Acceptance

- zero-analysis current set publishes;
- all current deterministic-eligible candidates are visible except trusted analysed-not-fit/hard excludes;
- Tier 1 / Tier 2 / Tier 3 order is deterministic;
- no Tier 2/3 fake total score;
- counts reconcile exactly;
- site shows progress summary;
- current source-integrity guards remain.

### Rollback

Revert progressive projection/UI changes and continue serving the previous last-known-good visual payload. No semantic cache migration should be required.

### Useful personalized ordering after Phase A?

**Yes where compatible accepted Taste exists.**

For an all-invalidated generation, Phase A still gives useful current deal visibility/status but no new personalization until Phase B starts.

## 17. Phase B — item-level PASS 1

### Objective

Make successful personalization coverage advance item by item without global blocking.

### Smallest likely surfaces

Canonical:

- progressive-personalization contract;
- `config/taste_result_contract.json`;
- `config/execution_ownership_contract.json` wording only as needed to describe new queue semantics without changing ownership;
- `config/daily_execution_contract.json`.

Queue/pin/ingest:

- current Taste work preparation/pin builder;
- `chatgpt_taste_queue.jsonl` or its successor projection;
- `scripts/process_taste_inbox.py`;
- `scripts/ingest_taste_results.py`;
- cache/index/receipt logic;
- visual rebuild trigger after accepted per-item progress.

Scheduled semantic worker contract/prompt:

- item-level immutable work;
- coverage-first;
- no deep recovery in PASS 1.

### Acceptance

Synthetic/production-compatible checks prove:

- one item success persists independently;
- one item semantic failure -> incomplete;
- one invalid result -> incomplete;
- next item proceeds;
- no global queue-closure gate for publication;
- compatible cache skips work;
- every PASS 1 item gets at most one attempt;
- `not_analyzed_count` monotonically reaches zero for a stable current semantic generation when the worker is functioning;
- site updates reflect accepted progress.

### Rollback

Disable new PASS 1 producer/ingest while retaining Phase A current catalogue and state projection. Pending items remain visible Tier 3.

### Useful personalized ordering after Phase B?

**Yes — this is the first phase that progressively grows the personalized Tier 1 automatically.**

## 18. Phase C — PASS 2 recovery

### Objective

Recover only items that PASS 1 could not resolve.

### Smallest likely surfaces

Canonical:

- progressive-personalization recovery rules;
- Dossier contract scope;
- Taste semantic result/recovery reason rules.

Control plane:

- GitHub PASS 2 queue derivation from `analysis_incomplete`;
- one recovery attempt per semantic generation;
- typed issue/recovery metadata.

Dossier:

- re-scope current full-backlog Dossier requirement so fresh Dossier is not universal PASS 1 prerequisite;
- prepare/request Dossier/deeper evidence for incomplete candidates as needed;
- retain strict per-item evidence validation.

### Acceptance

- PASS 2 starts only when PASS 1 coverage is complete;
- only incomplete items enter;
- successful recovery changes state;
- failed recovery remains visible Tier 2;
- no infinite retry;
- no PASS 2 work can starve new PASS 1 work;
- Dossier/Russian retrieval failure cannot block other items.

### Rollback

Disable PASS 2 generation. Tier 2 items remain visible; PASS 1/core publication continues unaffected.

### Useful personalized ordering after Phase C?

**Yes, with higher coverage than Phase B.**

## 19. Phase D — cleanup

### Objective

Remove old machinery whose main purpose was protecting a globally coupled all-or-nothing semantic path.

### Candidate retirements after A–C are proven

- current “AI queue must be zero before normal visual build” gate;
- global semantic `sufficiently_complete_for_publication` meaning;
- Dossier full daily backlog as Taste PASS 1 prerequisite;
- canonical maximal-contiguous-prefix progress for semantic outcomes;
- group-level all-or-none acceptance;
- `full_backlog_complete` as any user-facing readiness gate;
- prompt-only fail-closed narration as primary runtime observability;
- duplicated group compatibility/recovery machinery that no longer protects a remaining production invariant.

Keep:

- strict item evidence schema;
- exact identity/binding checks;
- privacy/provenance validation;
- Dossier cache where still valuable;
- GitHub ownership.

### Acceptance

- no old workflow can reintroduce global semantic blocking;
- no current source of truth still treats group completion as site readiness;
- one canonical item-state/count model;
- one PASS 1 queue authority;
- one PASS 2 recovery authority;
- one personalized ranking authority for Tier 1.

### Rollback

Retire old paths only after A–C have run successfully over multiple real production cycles. Cleanup should be staged disable -> observe -> delete.

### Useful personalized ordering after Phase D?

**Yes; no intended user-visible regression from Phase C.**

## 20. Required later canonical changes

No canonical file is changed by this amendment. A future IMPLEMENT sequence will need bounded changes.

### New specialized contract recommended

Add one machine-readable canonical contract for:

- item states;
- tier precedence;
- count invariants;
- PASS 1/PASS 2 ownership/order;
- automatic attempt budget;
- semantic generation identity;
- site publication semantics.

Suggested responsibility, not mandated filename: `config/progressive_personalization_contract.json`.

### Existing canonical contracts requiring amendment/reference

`config/daily_execution_contract.json`:

- replace “publish only after closed AI queue” with immediate deterministic catalogue + progressive semantic overlay;
- keep UI read-only;
- keep GitHub orchestration.

`config/execution_ownership_contract.json`:

- ownership itself remains unchanged;
- describe item-level PASS 1/PASS 2 queue/retry/completeness explicitly.

`config/mailing_policy.json`:

- unresolved analysis is visible, not excluded;
- only successful not-fit becomes Taste exclusion;
- preserve hard deterministic business gates.

`config/taste_result_contract.json`:

- separate fit decision completeness from rich negative/current-state enrichment completeness;
- map information insufficiency to incomplete rather than successful not-fit in progressive publication;
- preserve exact binding and threshold.

`config/final_ranking_policy.json`:

- preserve existing Tier-1 score;
- add tier precedence and a named purchase-only intra-tier key for Tier 2/3;
- do not create a second 0–100 pseudo-score.

`config/taste_steam_review_dossier_contract.json`:

- remove universal Dossier prerequisite for PASS 1;
- replace canonical group-prefix completion with item-level result progress;
- retain strict evidence validation.

`PROJECT_RULES.md` / `PROJECT_DECISIONS.md`:

- persist the new authoritative product direction and rationale;
- reconcile the current bounded commercial reconsideration bridge with “successfully analysed not-fit is excluded”.

### Likely code/workflow/UI surfaces

- pre-AI queue/state builders;
- Taste pin/work preparation;
- Taste inbox processing/ingest;
- Dossier preparation/ingest;
- semantic runtime completion;
- final visual producer;
- daily visual workflow;
- site queue/status renderer and regressions.

## 21. AMEND-01..15

- **AMEND-01 — PASS.** Automatic order is exactly: analysed fit first, incomplete/error second, never-analysed last; analysed not-fit excluded.
- **AMEND-02 — PASS.** Every current deterministic-eligible candidate remains visible before successful analysis unless an existing hard deterministic rule excludes it.
- **AMEND-03 — PASS.** Minimal durable state machine uses exactly four states; `analysis_in_progress` remains ephemeral.
- **AMEND-04 — PASS.** PASS 1 performs one coverage attempt per unresolved item and never deep-recovers before advancing.
- **AMEND-05 — PASS.** PASS 2 is recovery-only, begins after PASS 1 coverage, and has one bounded automatic recovery attempt per semantic generation.
- **AMEND-06 — PASS.** Canonical acceptance/progress is item-level; one bad item cannot block siblings/later items/site publication.
- **AMEND-07 — PASS.** Tier precedes score. Tier 1 uses existing personalized ranking; Tier 2/3 use only a separate purchase-only intra-tier key.
- **AMEND-08 — PASS.** Site counts and exact arithmetic invariants are defined.
- **AMEND-09 — PASS.** User-facing item labels are defined for fit, incomplete and not-analysed.
- **AMEND-10 — PASS.** Exactly one Taste/Dossier path chosen: C, compatible-cache fast path + lightweight PASS 1 + Dossier/deep recovery only when needed.
- **AMEND-11 — PASS.** Group-of-three may remain transport-only; maximal-contiguous-prefix canonical progress is retired from semantic/user readiness.
- **AMEND-12 — PASS.** GitHub owns state/order/retry/counts/validation/persistence; no control-plane responsibility moves to ChatGPT.
- **AMEND-13 — PASS.** Phases A–D prioritize visible service first, then item-level coverage, recovery, cleanup.
- **AMEND-14 — PASS.** No implementation, production run, Scheduled Task trigger or production mutation occurred.
- **AMEND-15 — PASS.** One target architecture and one next step are stated.

## 22. Changes: report only

Created only:

- `reviews/worker_reports/progressive-personalized-deals-architecture-amendment-01.md`.

No other repository/runtime state was intentionally changed.

The task explicitly permits only this durable report, so no `CURRENT_TASK.md`, source, contract, route or decision file was modified in this read-only amendment.

## 23. Unresolved

These are implementation-detail decisions and do not block the architecture amendment:

1. Exact filename/schema version for the new progressive-personalization contract/state manifest.
2. Whether the item-level worker transport uses one create-only artifact per item or a group envelope whose children are independently accepted. The canonical outcome must be item-level either way.
3. Exact short user-facing wording for safe issue categories.
4. Exact producer field name for the Tier 2/3 purchase-only sort key.
5. Whether optional rich Dossier enrichment for already-fit items is processed after PASS 2 or by a lower-priority background cache refresh. It must remain non-blocking either way.
6. How the current commercial reconsideration bridge is retired/reframed for a trustworthy below-moderate result; the new user direction is clear, but canonical contract reconciliation belongs to the first bounded contract/IMPLEMENT phase.

## 24. Status

`complete_architecture_amendment`

The amendment exactly represents the user's corrected product direction, defines the progressive state/tier model, separates PASS 1 from PASS 2, preserves GitHub ownership, chooses one semantic path and requires no implementation to complete the architecture decision.

## 25. Exactly one recommended next step

Return this amendment report to the Director for acceptance. After Director acceptance, obtain explicit user approval for **Phase A only — progressive display + canonical state/count/tier model** before any IMPLEMENT work.

## 26. Exact refs

### Task / correction

- `WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_ARCHITECTURE_AMENDMENT_01.md` — authoritative user correction, required states, two-pass model, tier ordering, site counts, publication semantics, group treatment, Taste/Dossier alternatives, failure cases, phases and AMEND-01..15.

### Previous accepted architecture basis

- `reviews/worker_reports/production-architecture-simplification-review-01.md`:
  - failure blast-radius table: one item should not block unrelated items;
  - Design B recommendation;
  - unknown item = personalization pending rather than false personalization;
  - item-level enrichment acceptance;
  - Dossier/Russian evidence not required for basic current-deal visibility;
  - Phase 0 service restoration / later item-level isolation.

### Ownership

- `config/execution_ownership_contract.json`:
  - GitHub owns exact production scope/order, retry/unresolved state, checkpoint merge, validation, persistence, completeness and downstream orchestration;
  - Scheduled ChatGPT is constrained external/semantic data plane;
  - architecture change must not transfer control-plane responsibility.

### Current daily global-gate assumption to amend

- `config/daily_execution_contract.json`:
  - current nightly preparation expects required semantic work to close before the final prepared visual;
  - current visualization contract describes a prepared daily semantic snapshot;
  - UI remains read-only and must stay read-only.

### Existing personalized ranking

- `config/final_ranking_policy.json`:
  - `eligibility_boundary.apply_only_after_taste_and_commercial_eligibility=true`;
  - score cannot rescue ineligible candidate;
  - automatic personalized order uses sale urgency then `total_score` then title;
  - sale urgency is outside the 0–100 score;
  - explicit manual end-of-queue override has absolute precedence.

### Current Taste semantics

- `config/taste_result_contract.json`:
  - existing worker output includes fit verdict, normalized factors, grounded negative analysis and evidence state;
  - `fit_evidence_state` contains sufficient / insufficient / reconsiderable / confirmed_negative;
  - current rule `insufficient_requires_exclude_but_is_not_dislike`;
  - public review sentiment is not Taste proof;
  - unknown candidate properties must not be invented;
  - current consumer says normal paid card requires grounded Taste negative witness.

### Current intrinsic Taste rules

- `config/mailing_policy.json`:
  - full daily snapshot / no fixed TOP-N;
  - minimum Taste threshold remains moderate;
  - positive evidence must be candidate-specific and grounded;
  - gameplay/mechanics/structure evidence is required;
  - price/reviews/discount do not manufacture Taste fit;
  - unknown candidate properties are not automatic include.

### Current pre-AI work coupling

- `scripts/build_pre_ai_chatgpt_payload.py`:
  - new cache misses currently receive `evaluate_taste_fit`, `evaluate_normalized_taste_factors`, and `resolve_grounded_negative_analysis` together;
  - unresolved rows are written to `chatgpt_taste_queue.jsonl`;
  - current ready/AI/excluded partition is globally reconciled.

### Current Dossier-first path / group blocking

- `scripts/build_taste_semantic_dossier_input.py`:
  - downstream Taste semantic input is currently built fail-closed from fresh V2 Dossiers.

- `config/taste_steam_review_dossier_contract.json`:
  - purpose currently says one complete fixed daily Dossier backlog before Taste semantic analysis;
  - checkpoint size is 3;
  - worker processes immutable predeclared groups;
  - GitHub drain accepts only the maximal valid contiguous prefix;
  - first missing/invalid expected group stops later canonical advancement;
  - `full_backlog_complete` is current snapshot completion state.

### Existing UI ordering

- `web/app.js`:
  - current automatic queue applies urgency/score ordering across the entire item array;
  - `manual_end_at` is applied as an absolute local override;
  - personalized score/details are rendered when present.
  - Phase A must insert analysis tier before the current urgency/score ordering rather than calculating semantics in the browser.

### Relevant rationale

- `PROJECT_DECISIONS.md`:
  - RANK-010: one transparent canonical personalized score;
  - UI-001: explicit manual end-of-queue beats automatic ranking;
  - STEAMDB-001: stage completeness and persistence of already verified partial facts are different concepts;
  - TASTE-004/TASTE-005/TASTE-006: current full-scope/checkpoint/group architecture was designed for completeness/durability, not as a daily quota;
  - TASTE-007+: Dossier is neutral multi-source player-feedback evidence with strict provenance; this evidence correctness can remain strict even when Dossier is removed from universal PASS 1.

## 27. Efficiency / reusable lesson

This amendment was faster than the original architecture review because the prior report already established the structural decoupling and the repository route already identified the Taste/Dossier/ranking entry points. The only necessary recon was the current ownership/ranking/Taste/Dossier contract boundary.

The reusable design lesson is:

**“Visible before analysed” does not require “ranked as if analysed.”**

The correct progressive system keeps one personalized product by making analysis state an explicit first sort dimension:

- known fit;
- attempted but unresolved;
- untouched;
- known non-fit removed.

That preserves honesty, gives the user immediate catalogue visibility, and makes semantic progress observable without allowing incomplete evidence or one difficult game to block the rest of the product.
