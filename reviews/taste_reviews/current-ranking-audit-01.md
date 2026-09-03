# TASTE REVIEW — CURRENT RANKING AUDIT 01

Status: in_progress
Role: Taste Reviewer
Scope: current user-visible recommendation/ranking calibration; advisory only

## Method

For candidate-specific downsides, do not invent negatives from store descriptions or feature lists. Use recurring player-review complaints to establish real implementation problems, then test whether those problems conflict with Dmitry's known taste.

Keep separate:
- personal fit;
- play role (`main/full`, `secondary/palate-cleanser`, `family/co-op`);
- relative queue priority;
- commercial urgency.

Also distinguish a **historically learned expectation** from a hard preference rule. If previous games in a franchise were usually secondary experiences, that can lower Dmitry's initial expectation for a new entry, but must not cap the new game's possible role before title-specific evidence is considered.

Also separate **weak personal interest** from **hard rejection**. A candidate can sound low-priority while still being worth sampling if the cost/friction of trying it is very low. Price/free access can change willingness to sample without becoming evidence of stronger personal fit.

## Calibrated current candidates

### `Amnesia: The Bunker`

User familiarity before calibration: essentially none.

Direct result:
- spoiler-light premise created desire to try the game;
- limited-resource management was not a negative; Dmitry explicitly noted resource control in `Resident Evil 4` did not bother him;
- an active persistent threat was attractive rather than off-putting;
- if already owned, it would sit in the ordinary queue (`B`), not become an immediate start and not be reserved only for a special mood.

Classification: **full/main-game candidate, moderate ordinary-queue priority**.

Use as regression control against generic penalties for scarcity, pressure and pursuit.

### `Terminator: Resistance`

User familiarity before calibration: none with the game itself.

Direct result:
- liking the `Terminator` films creates immediate franchise-driven interest from the title alone;
- neutral gameplay description preserved interest and created desire to learn more;
- did not create "drop everything and play" urgency.

Classification: **moderate positive ordinary-queue candidate with franchise boost; not top priority**.

Current ranking caution: a high production rank should not be presented as a correspondingly high personal-taste priority when urgency is doing much of the work.

### `Teenage Mutant Ninja Turtles: Splintered Fate`

User familiarity with this title: no confirmed prior experience in the full profile.

Franchise calibration:
- Dmitry likes `Teenage Mutant Ninja Turtles` because of childhood cartoons;
- past TMNT games have created a **learned expectation** that a TMNT game may end up as an additional/secondary game;
- Dmitry explicitly corrected that this is **not a rule or role cap**: a sufficiently strong new TMNT game can still become a main game.

Player-review context already identified for this title:
- overall reception is positive;
- recurring complaints focus on repetition / limited encounter-location variety, grind/progression friction and late-combat visual/AOE clutter rather than on the mere existence of a roguelite loop.

Classification for ranking QA: **franchise-positive with a cautious historical prior, but current play role remains unresolved until title-specific appeal/quality is evaluated**.

This is a useful anti-overgeneralization control: the system may use prior franchise experience as a prior expectation, but must allow a new entry to override that expectation rather than hard-coding it as secondary.

### `Haven Moon`

User familiarity before calibration: none found in the full gaming profile.

Player-review-grounded risk:
- the meaningful concern is not generic `directionlessness`;
- recurring complaints concern opaque puzzle communication, small/easy-to-miss details, unclear feedback after actions and repeated backtracking between locations.

Direct result:
- the premise sounds **somewhat boring / low-interest** to Dmitry;
- he would still be willing to give it a chance if the cost of trying were effectively zero (free) or after seeing more of the game visually;
- this is not a hard rejection.

Classification: **weak pre-play interest / low queue priority, but sampleable at very low entry cost; role unresolved**.

Ranking implication: the original strong `directionlessness` penalty is too coarse, but the candidate also should not be promoted merely because that penalty is removed. Its actual issue is weaker baseline appeal plus a real player-reported risk around opaque communication/backtracking. Free/very-low-price access may justify surfacing it as a low-risk trial without implying strong Taste fit.

## Current interpretation

The audit increasingly supports the distinction between **"would play / fits"**, **"would sample cheaply"**, and **"should rank as a main near-term recommendation"**, while also showing that role itself cannot be inferred too aggressively from franchise history.

Current controls:
- `Sifu` — strong near-term main-game interest;
- `High On Life` — full/main candidate, moderate queue priority;
- `Amnesia: The Bunker` — full/main candidate, moderate queue priority;
- `Terminator: Resistance` — moderate ordinary-queue candidate with franchise boost;
- `Haven Moon` — weak-interest candidate that Dmitry could sample if free/very cheap or after a stronger visual preview; not a hard reject;
- `Tails of Iron 2` — secondary/palate-cleanser candidate based on this specific title's trailer reaction;
- `TMNT: Splintered Fate` — franchise-positive; past TMNT games lower initial main-game expectation, but do not determine this title's role;
- `Trine 4` — confirmed family-play positive;
- `HighFleet` — strong negative pre-play/start-priority control.

## Director-facing implication

Taste/ranking QA should test role classification separately from raw fit, must not turn historical franchise patterns into hard role assignments, and should distinguish **low-cost trial value** from **strong personal fit**. `Haven Moon` is a direct control for the last distinction: removing an overbroad risk penalty does not mean the game becomes a high-priority recommendation, but an aggressive exclusion can still be wrong if a free/very-cheap trial would be acceptable.
