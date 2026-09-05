# TASTE REVIEW — Steps 1–3 Current Review 01

Task: `taste-steps-1-3-current-review-01`  
Mode: `READ-ONLY / TASTE REVIEW`  
Reviewed main: `d30aff1b30514bf75eebccf765ef22c8e3afeefe`  
Conclusion: **`ACCEPT_WITH_ADVISORY_RECOMMENDATIONS`**

## Scope reviewed

Independent review of the combined current semantics after:
1. V5 evidence state / confidence / reconsideration;
2. play role + relative start priority;
3. commercial reconsideration + wishlist-good-deal bridge.

Primary evidence reviewed:
- `USER_TASTE_PROFILE.md` and `reviews/taste_reviews/baseline-01.md`;
- `reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`;
- `reviews/worker_reports/play-role-and-start-priority-implement-01.md`;
- `reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`;
- `reviews/worker_reports/taste-review-recommendations-gap-recon-01.md`;
- current V5 evidence, play-priority, bridge and final-producer contracts/helpers/tests on `main`;
- current pre-AI semantic status and current persisted ranking lookup;
- successful Step-3 closeout run `33979912267`.

No product/code/config/ranking changes were made by this review.

## Overall assessment

The three steps form a coherent semantic boundary and address the main problems identified in the baseline **without globally loosening Taste**.

The strongest improvement is that the system no longer has to treat every below-moderate compatibility result as the same kind of personal rejection. `insufficient`, `reconsiderable`, and `confirmed_negative` now mean materially different things. The later commercial bridge consumes those states rather than rewriting them, while play role/start priority adds a missing non-scalar dimension without becoming another ranker.

The resulting selection pressure looks **approximately balanced at the semantic-rule level**: weaker/unknown evidence is no longer falsely equivalent to dislike, but a real title-specific negative remains hard; commercially attractive cases can cross a narrow paid-eligibility boundary without being relabeled as positive Taste.

Current production materialization is not yet a clean post-Steps-1–3 acceptance sample: the current pre-AI payload is degraded with `701` unresolved semantic rows and `0` resolved rows for the current scope, while the persisted ranking lookup is still schema 3 / 442 items from the older accepted visual snapshot. Therefore the old lookup must not be read as evidence that the new semantics are already reflected in the live/current ranking. This is an acceptance-observability limitation, not evidence that the new rules themselves are wrong.

## Strongest correct behaviors

### 1. Evidence states now match the actual taste model much better

- `insufficient` is explicitly **not dislike**. It requires below-moderate compatibility eligibility but cannot contain a strong confirmed personal negative.
- `reconsiderable` is correctly narrow: old brief/partial exposure, old non-engagement/mixed reaction, plus later non-commercial reopening evidence. It remains `EXCLUDE / below_moderate`; it is not a hidden positive fit.
- `confirmed_negative` requires high confidence plus a strong confirmed personal finding. An old brief attempt alone cannot create it; historical-only confirmation needs substantial/complete exposure plus explicit dislike.
- recurring player complaints/candidate-quality findings remain separate with `personal_relevance=unresolved`; they do not automatically become Dmitry's dislike.
- strong personal risk cannot be inferred merely from a generic feature label. This is particularly important for the profile's contextual treatment of directionlessness, repetition, management, puzzles, scarcity and complexity.

This is a direct improvement over the baseline failure mode where unknown/coarse risk could squeeze the selection too hard.

### 2. `confirmed_negative` is genuinely protected from commercial rescue

The current bridge checks evidence readiness first and hard-blocks `confirmed_negative`. The Step-3 regression explicitly verifies that even a huge commercial signal cannot rescue the HighFleet-style control. Step 2 also gives a confirmed negative `play_role=unresolved` and `relative_start_priority=low` before any title calibration can raise it.

This is semantically correct for `HighFleet`: the negative is title-specific felt burden (dry/technical/tedious), not a generic anti-strategy or anti-complexity rule.

### 3. Role and relative start priority solve a real baseline blind spot without contaminating Taste

The new role/start layer does not read wishlist, price, discount, deal verdict, sale urgency, personal/purchase score or final rank. It also does not alter eligibility, fit, score or ranking.

That correctly separates examples which a single scalar fit could not express:
- a strong-fit game can still be a secondary/palate-cleanser game;
- a liked family game can remain a family/co-op recommendation rather than becoming a solo-main recommendation;
- a full/main game can be ordinary rather than near-term priority;
- sale urgency does not mean “play next.”

### 4. The commercial bridge stays commercial

`wishlist_good_deal` requires an `insufficient` evidence state, wishlist interest and the already-canonical moderate scenario `INCLUDE + БРАТЬ СЕЙЧАС`. It preserves the original `EXCLUDE / below_moderate / insufficient` Taste state and adds no new discount threshold or fake moderate/strong fit.

`reconsiderable_fixed_package_value` similarly requires an already-reconsiderable state plus existing fixed-package strict savings/source alignment. It may make the purchase commercially reasonable while preserving Taste, role/start and risk provenance.

This matches the user's actual model: explicit interest/value can justify buying an uncertain game, but money does not prove personal fit.

## Current control review

| Control | Current Steps 1–3 semantic result | Taste-review assessment |
|---|---|---|
| `Sifu` | `main_full / high` | Correct. Strong current pre-play interest and challenge/combat motivation justify high start priority without needing price. |
| `High On Life` | `main_full / ordinary` | Correct. Full game, real interest, but below stronger queue choices; not a palate cleanser. Wishlist does not raise start priority. |
| `Amnesia: The Bunker` | `main_full / ordinary` | Correct. Moderate full-game interest; scarcity/threat are not wrongly treated as generic negatives. |
| `Terminator: Resistance` | `main_full / ordinary` | Correct. Franchise/setting boost supports interest, but not queue-reordering priority; sale urgency is orthogonal. |
| `Tails of Iron 2` | `secondary_palate_cleanser / ordinary` | Correct and materially better than the baseline scalar interpretation. Strong/acceptable fit does not imply main-game role. |
| `Trine 4` | `family_coop / ordinary` | Correct. Preserves the confirmed positive in its actual family-play context instead of over-generalizing it to solo/main play. |
| `TMNT: Splintered Fate` | `unresolved / unresolved` | Correctly conservative. Franchise history remains a weak prior, not a hard role cap or invented title-specific conclusion. |
| `HighFleet` | V5 control: `confirmed_negative`; role `unresolved`; start `low`; commercial rescue blocked | Correct target behavior and one of the strongest improvements over baseline. |
| `Batman: Arkham` | Strong replay-positive profile anchor; no dedicated current role/start hardcoding | No contradiction found. It remains important positive evidence for atmosphere/story/combat/achievements, but the current bounded deterministic control set does not directly prove a regenerated current-output treatment. |
| `Red Dead Redemption 2` | Strong open-world positive profile anchor; no dedicated current role/start hardcoding | No contradiction found. Its main value is as a positive exception against coarse “open world/directionlessness = bad” reasoning; current integrated output proof remains pending. |

## Current ranking/output check

There is one **visible contradiction in the persisted old lookup**, but it is not a contradiction in the new Step-1–3 rules:

- current persisted `ranking_lookup/h.json` still shows `HighFleet` as `fit=strong`, `risk_points=0`, `risk_level=low`, rank `71`, decision `БРАТЬ СЕЙЧАС`;
- that lookup's manifest is still schema `3`, while the current lookup producer is schema `4` and now exposes evidence-state and role/start fields;
- current `chatgpt_payload.json` is `degraded`, with `ai_queue_count=701`, `resolved_semantic_count=0` and no current-scope semantic progress yet;
- the normal final producer correctly waits/fails closed rather than fabricating a complete post-change visual result.

Therefore the old HighFleet row is **stale pre-change output**, not a new promotion caused by Steps 1–3. It is still important operationally: nobody should cite that persisted lookup as proof that current Taste acceptance has materialized. A post-backfill regenerated control snapshot is still required before claiming the new semantics are visible in current production.

No deterministic Step-1–3 control showed a weird commercial promotion, fit rewrite, role rewrite or confirmed-negative rescue.

## Blocking findings

**None in the combined Steps 1–3 semantic contracts/implementation.**

I did not find a Taste-policy reason to reject the new evidence-state boundary, role/start separation, or the two bounded commercial bridge routes.

The lack of a current complete regenerated production snapshot is an **acceptance-verification dependency**, not a reason to redesign these semantics. The pipeline is currently failing closed, which is preferable to publishing fabricated new-state output.

## Advisory observations

One wording nuance should remain explicit: Step-3 prose often says the wishlist bridge requires an “exact ready V5” `insufficient` state, while `evidence_readiness()` intentionally also treats a valid legacy `exclude_insufficient` row as safe `insufficient` readiness. This is semantically acceptable because Step 1 explicitly defines that legacy mapping as non-negative/insufficient; it should simply be described as **canonical insufficient readiness (including the safe legacy mapping)** rather than implying every bridged row is already V5-bound.

The role/start title calibrations are intentionally conservative and currently match the profile, but they are static reviewer-derived title calibrations. They should be treated as durable user evidence that needs revalidation if the canonical taste profile later materially changes, not as timeless genre rules.

## Maximum 3 advisory recommendations / tests

1. **Post-backfill integrated control snapshot.** Once the current semantic queue is genuinely resolved and the final payload regenerates, run one bounded acceptance check over the ten controls above. HighFleet is the critical negative: the regenerated current output must no longer reproduce the stale strong/no-risk row, and the Step-2 role/start fields must appear for the calibrated controls.
2. **Add positive-exception regression coverage for `Batman: Arkham` and `RDR2`.** Use them to ensure future negative-risk work does not drift back toward “complexity/open world/directionlessness/repetition label = personal dislike” without implementation-specific evidence.
3. **Add a revalidation trigger/provenance check for static title role/start calibrations when `USER_TASTE_PROFILE.md` materially changes.** This is a maintenance guard, not a request to make role/start algorithmic or price-driven.

## Confidence / unresolved questions

Confidence in the **semantic design of Steps 1–3: medium-high**. It is grounded in direct user controls, explicit contracts, current implementation and focused regressions.

Confidence in the **currently materialized production ordering: low**, because the current semantic scope is degraded and the persisted ranking lookup predates the integrated semantics.

No new broad taste questions are required before accepting these semantic rules. The next useful evidence is a regenerated current control sample after legitimate semantic completion, not more abstract preference questioning.

## Final conclusion

**`ACCEPT_WITH_ADVISORY_RECOMMENDATIONS`**

The combined Steps 1–3 are semantically coherent with Dmitry's current taste profile and materially improve the baseline model without collapsing commercial value into personal fit. `confirmed_negative` remains hard, `reconsiderable` remains uncertainty/reopening rather than positive fit, role/start stays non-commercial, and both commercial rescue routes are bounded and preserve Taste/risk provenance.

Acceptance is for the **Steps 1–3 semantic boundary**. It does **not** assert that the current persisted 442-item ranking lookup is already a post-change production result; that artifact is demonstrably stale and should be replaced/verified only through the normal pipeline after current semantic completion.