# WORKER TASK — RECONSIDERATION COMMERCIAL BRIDGE + WISHLIST IMPLEMENT 01

Task ID: `reconsideration-commercial-bridge-and-wishlist-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`
Priority: `VERY_HIGH_USER_PRIORITY`

## Context

This is internal Taste IMPLEMENT step 3 of the ordered three-step sequence.

Step 1 complete:
`reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`

Step 2 complete:
`reviews/worker_reports/play-role-and-start-priority-implement-01.md`

Authoritative design sources:
- `reviews/worker_reports/taste-review-recommendations-gap-recon-01.md`
- `reviews/worker_reports/wishlist-good-deal-override-recon-01.md`
- `reviews/taste_reviews/DIRECTOR_IMPLEMENTATION_HANDOFF_01.md`

## Goal

Implement one bounded commercial bridge that consumes the already-explicit Taste evidence state without mutating Taste or play-role semantics.

Required outcomes:

1. `confirmed_negative` / direct confirmed conflict stays non-overridable by paid commercial signals.
2. Explicit `reconsiderable` may become commercially purchase-worthy when credible package/bundle value exists.
3. Wishlist + canonical genuinely good current deal may bypass the ordinary weak/insufficient eligibility gate only when the Taste evidence state is explicitly non-confirmed-negative and the existing commercial condition says the deal is genuinely good.
4. Preserve the original Taste/evidence state, play role/start priority, risks, warnings and provenance in output.
5. Do not invent a new discount threshold or hidden constant.

## Canonical good-deal signal

Reuse the already identified existing commercial signal from the wishlist recon:
- moderate scenario would be `INCLUDE`;
- current commercial purchase decision is `БРАТЬ СЕЙЧАС`.

If exact current field names evolved, bind to the same authoritative deal-quality semantics rather than creating a replacement threshold.

## Eligibility semantics

Allowed bounded exception only for explicit non-confirmed-negative evidence states defined by current V5 evidence contract.

At minimum:
- `confirmed_negative` -> never overridden;
- direct confirmed conflict -> never overridden;
- `insufficient` + wishlist + canonical good deal -> may bypass ordinary Taste eligibility only under this bounded rule;
- `reconsiderable` + credible current commercial value -> may become purchase-eligible without changing fit/evidence state;
- weak/ordinary deal -> no guaranteed wishlist bypass;
- non-wishlist weak-Taste behavior otherwise unchanged.

Do not rewrite a below-threshold fit to fake `moderate` or `strong`.

## Package/bundle bridge

Existing fixed-package economics may affect purchase value for an already explicit `reconsiderable` candidate.

Do not:
- alter purchase-equivalence semantics;
- fabricate personalized Complete-the-Set prices;
- use unauthoritative bundle arithmetic;
- let package value itself create `reconsiderable` or positive fit.

The bridge is strictly:
`Taste already says reconsiderable` -> commercial/package value may justify buying now.

## Must preserve

- Step 1 evidence-state semantics unchanged.
- Step 2 role/start-priority semantics unchanged.
- Taste remains price/discount/wishlist blind.
- Wishlist is an explicit user-interest/commercial context signal, not Taste proof.
- Paid discount cannot rescue confirmed weak/negative fit.
- Existing serious risk/poor-value/content/store/budget exclusions remain authoritative.
- Giveaways unchanged and separate.
- Final ranking weights unchanged unless a regression proves a mechanical necessity and report justifies it explicitly.
- No second ranker/sorter.
- No new semantic scheduler/runtime.

## Required regressions

At minimum prove:
1. wishlist + canonical good deal + `insufficient` -> bounded eligibility exception can pass;
2. wishlist + ordinary/weak deal + `insufficient` -> no guaranteed override;
3. wishlist + `confirmed_negative` + huge discount -> blocked;
4. non-wishlist + weak Taste -> unchanged;
5. `reconsiderable` + credible fixed-package value -> may become purchase-worthy without changing evidence state;
6. package value cannot turn `confirmed_negative` into eligible;
7. package/bundle route preserves risk/warning provenance;
8. strong Taste-positive candidate unchanged;
9. step-2 play role/start priority are not modified by commercial bridge;
10. giveaway path unchanged;
11. existing fixed-package tests remain green;
12. existing V5 evidence-state and role/start-priority tests remain green.

## Controls

Use the bounded controls already established; do not expand the questionnaire.

Especially:
- `BioShock` as reconsiderable/package-value control if current production evidence permits exact binding;
- `HighFleet` as confirmed-negative non-rescue control;
- wishlist good-deal synthetic/current bounded controls;
- strong positive controls remain unchanged.

## Production/regeneration requirement

After implementation:
- run bounded deterministic regressions;
- regenerate the current production output through the normal canonical producer path as far as current runtime dependencies permit;
- produce a bounded comparison against the current ranking/Taste controls;
- do not manually process semantic queues or fabricate missing V5 backfill.

If production regeneration is blocked by an unrelated existing semantic/runtime prerequisite, report it explicitly while preserving repository-side technical completion.

## Taste Review gate

This step completes the bounded three-step implementation sequence.

**Do not claim final material Taste acceptance.**

After this report is complete, Director must run one independent current Taste Review over steps 1–3 and regenerated controls before accepting the new Taste/wishlist semantics as final product behavior.

Reviewer advice remains advisory and must not auto-write policy.

## Likely files

Only touch exact current owners as needed, likely among:
- `config/mailing_policy.json`;
- `config/deal_quality_contract.json`;
- `scripts/build_pre_ai_chatgpt_payload.py`;
- `scripts/build_visual_feed_v2.py`;
- `scripts/apply_fixed_package_purchase_options.py` only for the bounded reconsiderable bridge;
- `scripts/build_final_visual_payload.py` / `build_ranking_lookup.py` for provenance/diagnostics if needed;
- `PROJECT_RULES.md` / `PROJECT_DECISIONS.md`;
- focused tests such as `scripts/test_wishlist_good_deal_override.py`.

Do not broaden beyond the bounded bridge.

## Done when

Save:
`reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`

Include:
1. Status
2. Exact eligibility/commercial bridge semantics
3. Files changed
4. Canonical good-deal signal used
5. Confirmed-negative protections
6. Package/reconsideration behavior
7. Regression/control results
8. Production regeneration/comparison result
9. Proof Taste/role states were not rewritten by commercial signals
10. Exact commits/runs/artifacts
11. Exact independent Taste Review requirement
12. One bounded next step only

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`
