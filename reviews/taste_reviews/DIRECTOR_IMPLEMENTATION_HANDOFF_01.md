# DIRECTOR IMPLEMENTATION HANDOFF 01

Status: READY_FOR_IMPLEMENTATION
Owner after handoff: Director / implementation workflow
Source role: Taste Reviewer

## Decision

Taste calibration iteration 01 has reached a sufficient evidence threshold. Do **not** continue expanding the taste questionnaire before testing the learned rules in the product.

The next step is implementation and regression testing of the current discount/recommendation logic using the evidence already captured in:
- `USER_TASTE_PROFILE.md`
- `reviews/taste_reviews/baseline-01.md`
- `reviews/taste_reviews/current-ranking-audit-01.md`
- `reviews/taste_reviews/logic-change-handoff-01.md`

Additional taste calibration should resume only when implementation testing reveals a concrete ambiguity or new failure mode.

## Implementation objectives

1. Preserve `unknown / insufficient evidence` separately from negative fit.
2. Do not convert generic feature presence (`directionlessness`, repetition, puzzles, management, scarcity, threat, etc.) into strong personal-negative penalties without implementation-specific evidence.
3. Use recurring player complaints as evidence of real game-quality risks, but do not automatically convert them into Dmitry-specific dislikes.
4. Weight historical negative evidence by depth, recency and confidence; brief old abandonment must not become a permanent veto.
5. Separate personal fit, play role, relative queue priority and commercial urgency.
6. Treat paid discount as purchase-timing/value evidence, not as a way to rescue a confirmed weak/uninteresting game.
7. Treat free giveaways separately from paid purchase recommendations.
8. Model bundle value separately: a deeply discounted credible series bundle can justify re-evaluation when personal evidence is inconclusive, as in `BioShock`.
9. Historical franchise expectations may form a weak prior but must not become hard role caps (`TMNT` control).

## Regression controls

Use the existing calibrated titles as acceptance controls:

- `Trine 4: The Nightmare Prince` — confirmed family-play positive; unresolved semantic state must not behave like negative fit.
- `HighFleet` — strong negative pre-play/start-priority control after trailer inspection; reason is dry/technical/tedious felt burden, not generic complexity.
- `Sifu` — strong near-term main-game interest.
- `High On Life` — valid full/main candidate with moderate queue priority.
- `Amnesia: The Bunker` — moderate full-game candidate; scarcity is not a negative and persistent threat is attractive.
- `Terminator: Resistance` — moderate ordinary-queue candidate with franchise boost; high sale urgency must not masquerade as top personal priority.
- `Tails of Iron 2` — current specific-title secondary/palate-cleanser control.
- `TMNT: Splintered Fate` — franchise-positive, but previous TMNT history is only a cautious prior, not a mandatory secondary role.
- `Haven Moon` — description sounded dull, but evidence remains insufficient for a negative-fit verdict; needs richer inspection.
- `BioShock` — old shallow failed attempt, not permanent dislike; strong reputation/reviews can reopen evaluation and bundle value can then matter.
- `RDR2` — open-world positive exception proving open-world structure cannot be penalized monotonically.
- `Silent Hill (1999)` — mystery/puzzles positive while opaque objectives/lostness are negative; useful distinction for `directionlessness` and puzzle risks.
- `Hogwarts Legacy` puzzle rooms — puzzles can be positive when proportionate; excessive density is the risk.

## Acceptance criteria

Implementation iteration 01 is acceptable only if the updated output can represent all of the following without contradiction:

- `unknown` is not treated as `dislike`;
- a weak first impression is not treated as a confident negative;
- a brief old abandonment is weaker evidence than a recent informed rejection;
- recurring player complaints can flag risks without automatically assigning user dislike;
- a game can fit while still having moderate queue priority;
- a game can fit a family/secondary role without being promoted as the strongest main-game choice;
- sale urgency and discount magnitude do not overwrite personal priority;
- extreme paid discount does not rescue confirmed weak fit;
- free can lower the acquisition threshold without becoming a strong recommendation;
- a credible discounted bundle can raise purchase value for a genuinely reconsiderable series;
- franchise history can adjust expectations but cannot hard-code the new title's role.

## Workflow after implementation

After the Director/implementation workflow changes the logic:
1. regenerate the current recommendation/discount output;
2. run a bounded regression audit against the controls above;
3. compare new behavior with the current baseline and audit;
4. return only concrete mismatches to the Taste Reviewer for further calibration.

Do **not** resume broad preference questioning before this implementation/regression loop has been completed.
