# WORKER TASK — TASTE EVIDENCE STATE AND CONFIDENCE IMPLEMENT 01

Task ID: `taste-evidence-state-and-confidence-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`
Priority: `VERY_HIGH_USER_PRIORITY`

## Context

Implement only the first ordered gap from:
`reviews/worker_reports/taste-review-recommendations-gap-recon-01.md`

Authoritative product handoff:
`reviews/taste_reviews/DIRECTOR_IMPLEMENTATION_HANDOFF_01.md`

Do not implement play-role/start-priority or wishlist-good-deal yet. They depend on this semantic foundation.

## Goal

Introduce one canonical evidence-state layer so the system can distinguish:
- insufficient evidence;
- reconsiderable evidence/history;
- confirmed negative evidence;

without pretending that all three are the same `below_moderate` rejection.

Also add the minimum evidence-strength/history semantics needed so:
- generic feature presence cannot become a strong Dmitry-specific dislike without adequate personal/title-specific evidence;
- old shallow historical abandonment can be weaker/reconsiderable rather than a permanent veto;
- recurring/public quality complaints can exist as candidate-quality risk evidence without automatically becoming personal dislike.

Preserve price-blind Taste and the existing rule that paid discount cannot rescue confirmed weak/uninteresting fit.

## Required controls

Use the calibrated controls already named by the recon; do not expand the questionnaire:
- `Haven Moon` -> insufficient, not confirmed personal directionlessness negative;
- `BioShock` -> old shallow negative can become reconsiderable when later evidence justifies reopening;
- `HighFleet` -> informed/direct dry/technical/tedious negative remains strong;
- `Trine 4` -> unresolved/insufficient must not behave as dislike;
- `RDR2`, `Silent Hill (1999)`, `Hogwarts Legacy` puzzle-room controls -> no blanket structural negatives;
- `Amnesia: The Bunker` -> scarcity/threat are not generic negatives.

## Scope

Expected semantic surfaces are those identified in the recon, including relevant current Taste contracts/cache/ledger/producers and bounded tests.

If a candidate-quality evidence contract/artifact is needed, it must reuse the existing GitHub-owned semantic execution ownership. Do not create another scheduler/ranking authority.

## Must preserve

- Taste remains price/discount/wishlist blind.
- Commercial urgency remains separate.
- Giveaways remain separate.
- Existing grounded-negative readiness/fail-closed behavior remains useful and must not be replaced by invented fallback negatives.
- Confirmed direct negative remains non-overridable.
- No wishlist-good-deal implementation in this step.
- No play-role/start-priority implementation in this step.
- No broad Taste questionnaire.

## Validation

Add/extend focused deterministic regressions proving at minimum:
1. insufficient != confirmed negative;
2. reconsiderable != confirmed negative;
3. old/shallow negative is weaker than recent informed rejection;
4. generic feature hypothesis cannot produce strong personal-negative without adequate evidence strength/provenance;
5. candidate-quality risk can exist without personal dislike;
6. HighFleet control remains strongly negative;
7. paid discount/wishlist cannot alter the evidence state or rescue confirmed negative;
8. existing grounded-negative and card explanation regressions stay green.

Regenerate only the bounded current control output necessary to prove semantics.

## Acceptance boundary

This is internal IMPLEMENT step 1 of a three-step Taste sequence.
Do not claim final product acceptance of the whole Taste handoff yet.

Technical validation is required now.
Independent Taste Review is required before accepting/deploying this step as a completed material product semantic boundary. If this step remains an internal unaccepted precursor to steps 2 and 3, Director may instead run one combined Taste Review after all three steps, per the recon.

## Boundaries

Do NOT:
- implement wishlist override;
- implement play-role/start-priority;
- change final ranking weights unless mechanically necessary to prevent an invalid strong penalty and fully justified in report;
- change giveaway/Epic/GOG logic;
- create a second semantic scheduler;
- manually process semantic queues;
- broaden into DLC/package work.

## Done when

Save:
`reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`

Include:
1. Status
2. Exact semantic changes
3. Exact files/contracts
4. Cache/ledger migration/invalidation behavior
5. Regression/control results
6. Any production/runtime dependency
7. Whether step 2 can safely start
8. Exact commits/runs/artifacts if any
9. One bounded next step only

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`
