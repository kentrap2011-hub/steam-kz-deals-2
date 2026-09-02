# USER TASTE PROFILE

Canonical durable profile for game-selection taste review.

This file is maintained by the dedicated Taste Reviewer from explicit user feedback and canonical project evidence. It is not a technical project log and must not contain secrets.

## Profile confidence

- **Low** as of baseline-01. There are not yet enough confirmed game-level positive and negative controls to claim that the current Taste model reliably represents Dmitry's preferences.
- Current ranking position, price/deal quality and model-produced fit are not treated as evidence that Dmitry personally likes a game.

## Strong positive signals

- No game-level strong positive has yet been confirmed strongly enough for durable use.

## Strong negative signals

- No game-level strong negative has yet been confirmed strongly enough for durable use.

## Explicit-interest signals

These are useful calibration evidence, but are **not equivalent to confirmed liking**:

- `American Arcadia` — current canonical production ranking marks the game as wishlist=true. Dmitry has watched a review and knows more about it than the comparison candidate `Afterimage`; he explicitly says the game's "Truman Show"-like concept appeals to him. This is a positive concept/interest signal, but not evidence that he prefers it to `Afterimage` on equal familiarity.
- `High On Life` — current canonical production ranking marks the game as wishlist=true.
- `Trine 4: The Nightmare Prince` — explicit current user attention/expectation case while discounted; its current absence is caused by unresolved Taste semantic data (`taste_cache_key_missing`), not by a canonical negative Taste verdict. Treat it as an unresolved calibration case, not a dislike.

## Mechanics / structure preferences

- Tentative positive hypothesis: a distinctive, easily understandable high-concept premise can increase interest. Current explicit example: `American Arcadia`, whose "Truman Show"-like concept Dmitry finds appealing. Confidence remains low until repeated across games.
- Not otherwise established from sufficiently direct game-level evidence.
- Current risk labels such as `directionlessness`, `unchanged_repetition`, `management_routine`, `puzzle_pacing` and similar model outputs remain hypotheses until checked against concrete user comparisons. Do not promote them to durable preferences solely because the current model applies penalties for them.

## Visual preferences

- `American Arcadia` and `Afterimage` were both described as visually attractive. This is too weak and too small a sample to infer a durable art-style preference.

## Genre preferences and exceptions

- Not yet established. Do not infer genre preferences from current INCLUDE/EXCLUDE output or from isolated wishlist entries.

## Known comparison anchors

- `American Arcadia` vs `Afterimage` — **not a valid preference winner yet**. Dmitry chose `American Arcadia`, but explicitly identified familiarity asymmetry: he has seen a review of `American Arcadia` and knows essentially nothing about `Afterimage`. The comparison may be reused only after giving comparable spoiler-light information about both games. What is valid from this test: both look attractive to him, and the `American Arcadia` concept appeals to him.
- `High On Life` vs `HighFleet` — explicit wishlist interest vs stronger model-only taste fit; pending calibration.
- `Trine 4: The Nightmare Prince` vs `Tails of Iron 2: Whiskers of Winter` — unresolved-but-explicitly-noticed candidate vs a current strong-fit recommendation; pending calibration.

## Calibration methodology learned from user feedback

- Pairwise taste tests must control for **familiarity / information asymmetry**. A game Dmitry already knows from a review should not be treated as a clean preference winner over an unfamiliar game.
- When familiarity differs, first provide comparable spoiler-light descriptions of both candidates, then ask which is more appealing and why.
- Unknown/unfamiliar must remain distinct from dislike or weak fit.

## Uncertainty / questions

- Which current high-scoring games are genuine positives rather than plausible model guesses?
- Which current risk concepts are real user turn-offs, and which are over-generalized proxies?
- How much should explicit wishlist/current interest outweigh a model-only predicted fit when the two disagree?
- Does attraction to distinctive high-concept premises repeat across other games strongly enough to become a durable preference?
- Unknown/unresolved Taste state must remain distinct from negative preference evidence.

## Update rule

Record only durable preference evidence. Distinguish:
- explicit user statement;
- repeated observed behavior;
- tentative inference.

Do not infer personal taste from price, discount, popularity, review score, technical compatibility or ranking position alone.