# USER TASTE PROFILE

Canonical durable profile for game-selection taste review.

This file is maintained by the dedicated Taste Reviewer from explicit user feedback and canonical project evidence. It is not a technical project log and must not contain secrets.

## Profile confidence

- **Low, improving** as of baseline-01 calibration. There are still too few confirmed game-level controls to claim that the current Taste model reliably represents Dmitry's preferences, but direct user calibration has started producing usable controls.
- Current ranking position, price/deal quality and model-produced fit are not treated as evidence that Dmitry personally likes a game.

## Strong positive signals

- No game-level strong positive has yet been confirmed strongly enough for durable use.

## Strong negative signals

- `HighFleet` — **strong negative pre-play / start-priority signal**. After watching a trailer specifically for calibration, Dmitry said it did not appeal to him at all and that he would likely postpone it until there was little else left to play. He described the trailer impression as **tedious and overly technical**: the atmosphere felt less like starting a game and more like having to study an instruction manual. He compared this feeling to the game he called "Танки", but said `HighFleet` creates that impression much more strongly. This is valid evidence that `HighFleet` should currently rank low for personal start/play priority. It is not evidence that he has played the game or that every individual mechanic/genre element in it is disliked.

## Explicit-interest signals

These are useful calibration evidence, but are **not equivalent to confirmed liking**:

- `American Arcadia` — current canonical production ranking marks the game as wishlist=true. Dmitry has watched a review and knows more about it than the comparison candidate `Afterimage`; he explicitly says the game's "Truman Show"-like concept appeals to him. This is a positive concept/interest signal, but not evidence that he prefers it to `Afterimage` on equal familiarity.
- `High On Life` — current canonical production ranking marks the game as wishlist=true. Dmitry has watched a review, so comparisons against unfamiliar games must control for familiarity.
- `Trine 4: The Nightmare Prince` — explicit current user attention/expectation case while discounted; its current absence is caused by unresolved Taste semantic data (`taste_cache_key_missing`), not by a canonical negative Taste verdict. Treat it as an unresolved calibration case, not a dislike.

## Mechanics / structure preferences

- Tentative positive hypothesis: a distinctive, easily understandable high-concept premise can increase interest. Current explicit example: `American Arcadia`, whose "Truman Show"-like concept Dmitry finds appealing. Confidence remains low until repeated across games.
- **Tentative negative structural signal:** games can lose substantial appeal when their presentation makes the experience feel dry, technical, tedious, or dominated by learning systems/instructions before the fun is apparent. `HighFleet` is the current strong example. This should be treated as aversion to the **felt burden / presentation of technicality**, not as a blanket dislike of complexity, strategy, management, simulation, or deep systems.
- Current risk labels such as `directionlessness`, `unchanged_repetition`, `management_routine`, `puzzle_pacing` and similar model outputs remain hypotheses until checked against concrete user comparisons. Do not promote them to durable preferences solely because the current model applies penalties for them.
- Do **not** infer a dislike of strategy, management, simulation, fleet mechanics, retro presentation, or any other `HighFleet` component from this case alone. More targeted comparisons are required to determine which kinds of complexity feel engaging versus instructional/tedious.

## Visual preferences

- `American Arcadia` and `Afterimage` were both described as visually attractive. This is too weak and too small a sample to infer a durable art-style preference.
- `HighFleet` produced a strong negative trailer-level reaction, but the user described the cause primarily as an overall sense of tedious technicality rather than a specific art-style rejection. Do not convert this into an art-style rule.

## Genre preferences and exceptions

- Not yet established. Do not infer genre preferences from current INCLUDE/EXCLUDE output, isolated wishlist entries, or the single `HighFleet` negative control.

## Known comparison anchors

- `American Arcadia` vs `Afterimage` — **not a valid preference winner yet**. Dmitry chose `American Arcadia`, but explicitly identified familiarity asymmetry: he has seen a review of `American Arcadia` and knows essentially nothing about `Afterimage`. The comparison may be reused only after giving comparable spoiler-light information about both games. What is valid from this test: both look attractive to him, and the `American Arcadia` concept appeals to him.
- `High On Life` vs `HighFleet` — produces one reliable result despite familiarity asymmetry: `HighFleet` itself is a strong negative start-priority control after Dmitry watched its trailer and found it unappealing. The reason he gave is the sense of tedious, dry technicality — "more like studying an instruction manual than playing a game." Do not use the pair to quantify how strongly `High On Life` is liked until that is asked directly.
- `Trine 4: The Nightmare Prince` vs `Tails of Iron 2: Whiskers of Winter` — unresolved-but-explicitly-noticed candidate vs a current strong-fit recommendation; pending calibration.

## Calibration methodology learned from user feedback

- Pairwise taste tests must control for **familiarity / information asymmetry**. A game Dmitry already knows from a review should not be treated as a clean preference winner over an unfamiliar game.
- When familiarity differs, first provide comparable spoiler-light descriptions or let Dmitry inspect a trailer, then ask which is more appealing and why.
- A strong negative reaction to an unfamiliar game's trailer can still be a valid **pre-play interest/start-priority** signal even when the opposite member of the pair is better known.
- When capturing a negative control, prefer the user's stated experiential reason (for example, "feels like studying an instruction manual") over broad genre labels such as strategy or simulation.
- Unknown/unfamiliar must remain distinct from dislike or weak fit.

## Uncertainty / questions

- Which current high-scoring games are genuine positives rather than plausible model guesses?
- Does the `HighFleet` aversion generalize to other games whose systems/UX feel technical or instructional, and what kinds of complexity avoid that reaction?
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