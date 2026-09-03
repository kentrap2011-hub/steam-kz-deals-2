# TASTE REVIEW — LOGIC CHANGE HANDOFF 01

Status: ready_for_director_review
Role: Taste Reviewer
Scope: advisory only; no production code/config/weight changes performed here

## Purpose

This handoff converts direct user calibration into bounded changes for the Director to evaluate in the current discount/recommendation logic.

The central finding is that the current Taste layer risks treating **structural game features as negatives before there is evidence that their implementation is actually bad for Dmitry**. Dmitry explicitly corrected the review method: every game has drawbacks, and it is not valid to invent likely negatives from a store description/feature list alone. For candidate-specific quality risks, recurring player-review evidence is more useful than speculative feature-level penalties.

## Required logic change direction

### 1. Do not treat feature presence as a demonstrated personal negative

These labels must not receive a strong direct penalty merely because the feature exists:
- `directionlessness`
- `unchanged_repetition`
- `management_routine`
- `puzzle_pacing`
- resource scarcity / inventory pressure
- persistent threat / pursuit
- crafting / progression / open areas / stealth as generic structural features

Direct calibration shows why:
- `RDR2`: open world is a strong confirmed positive when exploration is dense, atmospheric and rewarding.
- `Silent Hill (1999)`: mystery, puzzles and searching are positive; the negative is opaque objectives / irritating lostness.
- `Hogwarts Legacy`: puzzle rooms are enjoyable; the negative would be excessive density, not puzzles themselves.
- repetition: Dmitry explicitly says repetition is not a problem if the activity remains interesting.
- management/progression: can be interesting when optional; forced upkeep is the risk.
- `Resident Evil 4`: resource control did not irritate Dmitry.
- `Amnesia: The Bunker`: limited resources did not reduce interest, and persistent threat increased interest.

Recommendation: convert coarse feature penalties into **context/implementation hypotheses**, or sharply reduce their weight unless supported by stronger evidence.

### 2. Use player-review evidence to establish real implementation risks before taste penalties

For a candidate-specific negative, prefer this evidence chain:
1. identify a recurring complaint from actual players/reviews;
2. confirm it is a meaningful pattern rather than one isolated complaint;
3. map that complaint to an experiential issue (e.g. boring missions, weak combat feel, confusing navigation, mandatory grind, poor AI, technical friction);
4. only then test whether that issue conflicts with Dmitry's known preferences.

Do not infer a candidate's negative merely from its store description or list of mechanics.

Important separation:
- **player reviews = evidence that a quality/implementation issue is real**;
- **Dmitry's profile/direct answers = evidence that the issue matters to him personally**.

Review sentiment by itself must not become a taste score, and popularity/review percentage must not be treated as personal preference proof.

### 3. Separate personal fit, role and queue priority from sale urgency

Current calibration shows at least three distinct outputs are needed conceptually:
- is this game suitable for Dmitry at all?
- in what role: main/full game, secondary/palate-cleanser, family/co-op?
- how strong is its relative play priority among other suitable games?

Sale urgency should remain a commercial/ranking factor, but must not visually imply that a game is one of Dmitry's strongest taste matches when the high rank is primarily deadline-driven.

Controls:
- `Sifu`: strong current pre-play priority.
- `High On Life`: valid full/main-game candidate, moderate queue priority.
- `Amnesia: The Bunker`: valid full/main-game candidate, moderate ordinary-queue priority; not a special-mood game despite horror tension.
- `Terminator: Resistance`: moderate ordinary-queue interest, boosted by liking the `Terminator` film universe; not a drop-everything title.
- `Tails of Iron 2`: secondary/palate-cleanser role, not main-game priority.
- `Trine 4`: confirmed family-play positive.

## Candidate-specific findings relevant to current ranking

### `Terminator: Resistance`

Current production ranking previously placed it very high while Taste risk reduced its personal score substantially.

Direct user calibration:
- Dmitry was unfamiliar with the game itself;
- liking the `Terminator` films created immediate positive interest from the title/universe;
- a neutral gameplay description preserved interest and made him want to learn more;
- it did **not** create urgency to abandon his current queue.

Interpretation: moderate positive ordinary-queue candidate, not top taste priority. A strong generic Taste penalty is not currently justified by direct preference evidence.

### `Amnesia: The Bunker`

Direct calibration:
- previously unknown title;
- description created desire to try it;
- resource control was not a concern; Dmitry explicitly referenced `Resident Evil 4` as a positive/neutral resource-management control;
- persistent threat was attractive, not a negative;
- if already owned, it would sit in the normal queue rather than become immediate priority or a special-mood-only title.

Interpretation: useful regression control against generic penalties for scarcity, pressure and pursuit.

### `HighFleet`

Strong negative pre-play control remains valid, but the reason must stay narrow:
- dry/technical/tedious felt presentation;
- "more like studying an instruction manual than playing a game".

Do not generalize this into anti-complexity, anti-strategy, anti-management or anti-simulation rules.

### `Trine 4: The Nightmare Prince`

Confirmed positive family-play title that was omitted when semantic Taste state was unresolved. Keep as a regression control for unknown-vs-negative handling.

## Director acceptance tests recommended

1. **Feature-vs-flaw test**
   - A game must not receive a strong negative merely because it contains puzzles, repetition, resource pressure, management, open exploration or pursuit.
   - Strong negative should require either direct user evidence or a well-grounded implementation problem that maps to known user dislike.

2. **Review-grounded risk test**
   - For a bounded current sample, compare current Taste risk reasons against recurring player complaints.
   - Flag risks that exist only as speculative structural assumptions.
   - Do not use aggregate review score as personal fit evidence.

3. **Role/priority/urgency separation test**
   - Verify `Sifu`, `High On Life`, `Amnesia: The Bunker`, `Terminator: Resistance`, `Tails of Iron 2`, and `Trine 4` can be represented without collapsing suitability, role, queue priority and commercial urgency into one signal.

## Expected product effect

The goal is **not to loosen all filtering**. `HighFleet` proves false positives remain possible.

The desired effect is:
- fewer false negatives caused by speculative/coarse risk penalties;
- fewer false positives caused by generic feature matching;
- clearer distinction between "fits Dmitry", "fits a particular play role", "should be played soon", and "sale is urgent";
- candidate-specific negatives grounded in real implementation evidence rather than feature-list stereotypes.

## Canonical evidence refs

- `USER_TASTE_PROFILE.md`
- `reviews/taste_reviews/baseline-01.md`
- direct calibration controls: `Trine 4`, `HighFleet`, `Tails of Iron 2`, `High On Life`, `Sifu`, `Batman: Arkham`, `RDR2`, `Silent Hill (1999)`, `Silent Hill f`, `Alan Wake`, `Amnesia: The Bunker`, `Terminator: Resistance`

## Handoff

Director should decide implementation, weights, contracts and technical architecture. Taste Reviewer should continue calibrating concrete current candidates and update this handoff only when new evidence materially changes the recommended logic.