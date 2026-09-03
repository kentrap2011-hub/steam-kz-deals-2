# DIRECTOR TASK — APPLY CALIBRATED TASTE LOGIC 01

Status: ready_for_director
Owner: Director
Source: Taste Reviewer

## Goal

Stop further broad taste calibration for this cycle and apply the accumulated evidence to the live recommendation/discount logic. Then regenerate the current output and return it to Taste Reviewer for acceptance testing.

## Canonical inputs

Read first:
- `USER_TASTE_PROFILE.md`
- `reviews/taste_reviews/baseline-01.md`
- `reviews/taste_reviews/current-ranking-audit-01.md`
- `reviews/taste_reviews/logic-change-handoff-01.md`

## Required implementation direction

Director should choose the technical design, weights and contracts, but the resulting behavior must satisfy these product/taste constraints:

1. Do not turn structural features (`directionlessness`, repetition, puzzles, management, scarcity, pursuit, crafting, open areas, etc.) into strong personal negatives merely because the feature exists.
2. Use recurring player-review evidence to establish real implementation issues; treat those issues as hypotheses about Dmitry until his profile/history or richer title-specific evidence connects them to his taste.
3. Preserve an explicit insufficient-evidence state. Description + review summaries alone must not force an unfamiliar game into positive or negative fit.
4. Weight historical negative evidence by exposure depth, recency and confidence. A brief failed attempt years ago is weaker than a recent, well-informed rejection. `BioShock` is the regression control.
5. Separate personal fit, play role, relative queue priority and commercial urgency.
6. Do not let extreme paid discount percentage rescue a game already judged weak/uninteresting with adequate evidence. Good games also receive deep discounts, so opportunity cost matters.
7. Treat free giveaways as a distinct low-friction acquisition state rather than strong Taste evidence.
8. Model bundle/series value separately from single-title discount magnitude. A bundle can legitimately improve purchase value for a credibly reconsiderable series (`BioShock`) without manufacturing Taste fit.
9. Do not hard-code franchise history into role. `TMNT` past experience is a prior expectation only; a new title must be able to override it.
10. Unknown/unresolved must remain distinct from negative.

## Regression / acceptance controls

Use at least these current controls after implementation:
- `Sifu` — strong near-term main-game interest.
- `High On Life` — valid full/main candidate, moderate queue priority.
- `Amnesia: The Bunker` — valid full/main candidate, moderate ordinary-queue priority; scarcity and active threat are not generic negatives.
- `Terminator: Resistance` — moderate ordinary-queue candidate with franchise boost; not a drop-everything priority.
- `Haven Moon` — insufficient title-specific evidence; initial description sounded dull, but no negative-fit verdict is justified yet.
- `BioShock` — old/shallow failed attempt, but legitimate reconsideration based on reputation/reviews; deeply discounted full-series bundle can be a rational purchase opportunity.
- `Tails of Iron 2` — current title-specific secondary/palate-cleanser impression, not a broad indie rule.
- `TMNT: Splintered Fate` — franchise-positive; historical secondary-game expectation is not a role cap.
- `Trine 4` — confirmed family-play positive and regression control for unknown-vs-negative handling.
- `HighFleet` — strong negative pre-play/start-priority control after direct trailer inspection; reason is dry/technical/tedious felt presentation, not generic complexity.

## Required execution sequence

1. Implement the bounded logic changes chosen by Director.
2. Re-run the current recommendation/discount pipeline on current data.
3. Produce a before/after comparison for the controls above plus the current top recommendations and near-cutoff/omitted candidates.
4. Explicitly show for each sampled game:
   - personal fit/status;
   - evidence confidence/depth;
   - play role if known;
   - relative queue priority if known;
   - sale urgency / commercial contribution separately;
   - discount/bundle/free status separately from Taste.
5. Return the regenerated output and comparison to Taste Reviewer for acceptance review.

## Acceptance condition

This task is not complete merely because code/tests pass. It is complete only when the regenerated current output can be reviewed against the calibrated controls and no longer exhibits the known semantic failures:
- feature-as-flaw;
- unknown-as-negative;
- shallow-old-abandon-as-permanent-veto;
- role/priority/urgency collapse;
- discount-rescues-weak-game;
- franchise-history-as-hard-role;
- bundle value collapsed into raw discount percentage.

## Taste Reviewer next phase

After Director applies the changes, Taste Reviewer should stop broad questioning and move into **post-change acceptance testing** on the regenerated real recommendations. New taste questions should be asked only when a specific post-change ambiguity requires them.