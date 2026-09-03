# DIRECTOR TASK — APPLY TASTE LOGIC V1

Status: ready_for_director
Source role: Taste Reviewer

## Goal

Apply the first calibrated batch of Dmitry's real gaming-taste evidence to the discount/recommendation logic, then regenerate the current recommendation output for before/after validation.

This is the point where calibration should stop expanding by default and move into implementation + acceptance testing. Further taste questions should be driven by concrete disagreements in the new output, not by an open-ended questionnaire.

## Canonical inputs

Read first:
- `USER_TASTE_PROFILE.md`
- `reviews/taste_reviews/baseline-01.md`
- `reviews/taste_reviews/current-ranking-audit-01.md`
- `reviews/taste_reviews/logic-change-handoff-01.md`

## Required behavioral changes

1. Preserve `unknown / insufficient evidence` separately from negative fit.
2. Do not turn structural features (`directionlessness`, repetition, management, puzzles, scarcity, threat, etc.) into strong negatives without implementation-level evidence and personal relevance.
3. Use recurring player-review complaints as evidence that an implementation issue exists, not as automatic proof Dmitry dislikes the game.
4. Weight historical negative evidence by depth, recency and explicitness. A shallow old abandon is not a permanent veto (`BioShock`).
5. Separate:
   - personal fit;
   - evidence confidence;
   - play role;
   - queue priority;
   - sale urgency;
   - discount magnitude;
   - bundle value;
   - free-giveaway acquisition threshold.
6. Do not let an extreme paid discount rescue a game already judged weak/uninteresting with good confidence.
7. Allow a strong bundle/price to improve purchase value when a game/series is already a credible fit or credible reconsideration candidate.
8. Treat free giveaways separately: free can lower claim/sample friction without creating stronger Taste fit.
9. Do not turn historical franchise expectations into hard role rules (`TMNT`).

## Acceptance controls

Use at minimum these controls when validating the new logic:

- `Sifu` — strong current near-term main-game interest.
- `Batman: Arkham` — confirmed replay-positive anchor: atmosphere + story + combat + achievements.
- `High On Life` — valid full/main candidate, moderate queue priority.
- `Amnesia: The Bunker` — valid full/main candidate, moderate priority; scarcity not negative; active threat positively attractive.
- `Terminator: Resistance` — moderate ordinary-queue candidate with franchise boost; not top taste priority.
- `Haven Moon` — insufficient evidence; text description sounded dull but no negative-fit verdict is justified yet.
- `BioShock` — old shallow failed attempt; legitimately reconsiderable because external quality evidence reopened interest; discounted full-series bundle can become a serious purchase candidate.
- `Tails of Iron 2` — title-specific secondary/palate-cleanser impression.
- `TMNT: Splintered Fate` — franchise-positive; old TMNT history creates only a weak prior, not a hard secondary-role cap.
- `Trine 4: The Nightmare Prince` — confirmed family-play positive; regression control for unknown-vs-negative omission.
- `HighFleet` — strong negative pre-play/start-priority control after trailer inspection; negative reason is dry/technical/tedious felt presentation, not generic complexity.
- `RDR2` — strong open-world positive; regression control against coarse directionlessness/open-world penalties.
- `Silent Hill (1999)` — mystery/puzzles positive, opaque objectives/lostness negative.
- `Hogwarts Legacy` puzzle rooms — puzzles can be positive; over-density is the risk.

## Validation output required from Director

After implementation, produce a bounded before/after report showing for the control games:
- old fit / new fit;
- old risk reasons / new risk reasons;
- evidence confidence;
- role;
- queue priority;
- commercial urgency contribution;
- whether discount/bundle/free status changed purchase value without changing Taste fit.

Also regenerate the current user-facing recommendation list and flag:
- false negatives removed;
- false positives newly exposed;
- items that remain `insufficient evidence`;
- cases where urgency still distorts apparent personal priority.

## Stop condition for Taste Reviewer

Do not keep expanding general taste calibration before this implementation pass. Resume calibration only when the new output exposes a concrete ambiguity or disagreement that the existing profile cannot resolve.
