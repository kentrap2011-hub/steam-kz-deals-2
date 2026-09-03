# USER TASTE PROFILE

Canonical durable profile for game-selection taste review.

This file is maintained by the dedicated Taste Reviewer from explicit user feedback and canonical project evidence. It is not a technical project log and must not contain secrets.

## Profile confidence

- **Low, improving** as of baseline-01 calibration. Direct user calibration now contains confirmed played positives (`Trine 4: The Nightmare Prince`, `Batman: Arkham` series as a replay-positive anchor, `Red Dead Redemption 2` as a strong open-world positive), one strong negative pre-play/start-priority control (`HighFleet`), one lower-priority/secondary-game control (`Tails of Iron 2: Whiskers of Winter`), a clearer relative-priority calibration for `High On Life`, a multi-factor strong pre-play interest profile for `Sifu`, and a moderate pre-play interest control for `Alan Wake`. This is still too small a set to claim the current Taste model reliably represents Dmitry's preferences across genres.
- Current ranking position, price/deal quality and model-produced fit are not treated as evidence that Dmitry personally likes a game.

## Strong positive signals

- `Trine 4: The Nightmare Prince` — **confirmed played positive in a family-play context**. Dmitry bought it specifically to play with his family, played it with them the next day, and explicitly said he liked it. This is genuine positive evidence, but its context matters: it was selected for family play, so do not automatically treat it as proof that the same game would be equally strong as a solo/main-game choice.
- `Batman: Arkham` series — **confirmed strong replay-positive anchor**. Dmitry is willing to replay an Arkham game even ahead of starting a new game such as `High On Life`. He explicitly names atmosphere, story, combat and achievements as the reasons that make him want to return. Treat the series as strong positive evidence for those factors working together, while avoiding unsupported assumptions about a specific Arkham entry.
- `Red Dead Redemption 2` — **strong confirmed open-world positive**. Dmitry calls it the best open world. What specifically worked: a strong atmosphere; many activities; hunting; finding unusual people, criminals and mysteries; bounty hunting from notice boards; Arthur's observations/notes that deepened immersion; and a satisfying loop where exploration/hunting produced money that he then enjoyed spending. Organic discovery is itself part of the appeal: not knowing in advance where interesting content is gives unexplored space value. This is important because open-world structure otherwise creates an initial negative expectation for him; `RDR2` proves that a sufficiently rich and rewarding world can make open world a major positive rather than a liability.

## Strong negative signals

- `HighFleet` — **strong negative pre-play / start-priority signal**. After watching a trailer specifically for calibration, Dmitry said it did not appeal to him at all and that he would likely postpone it until there was little else left to play. He described the trailer impression as **tedious and overly technical**: the atmosphere felt less like starting a game and more like having to study an instruction manual. He compared this feeling to the game he called "Танки", but said `HighFleet` creates that impression much more strongly. This is valid evidence that `HighFleet` should currently rank low for personal start/play priority. It is not evidence that he has played the game or that every individual mechanic/genre element in it is disliked.

## Explicit-interest signals

These are useful calibration evidence, but are **not equivalent to confirmed liking** unless separately confirmed below:

- `American Arcadia` — current canonical production ranking marks the game as wishlist=true. Dmitry has watched a review and knows more about it than the comparison candidate `Afterimage`; he explicitly says the game's "Truman Show"-like concept appeals to him. This is a positive concept/interest signal, but not evidence that he prefers it to `Afterimage` on equal familiarity.
- `High On Life` — **moderate main-game interest / queue-worthy, but not top-priority**. Dmitry has watched a review and says he would not put it ahead of everything after purchase. In his current queue, `Sifu` interests him more, and he may even replay a `Batman: Arkham` game before starting `High On Life`. Crucially, he does **not** view `High On Life` as a lightweight/palate-cleanser game; it remains a normal/full main-game candidate, just below stronger alternatives.
- `Sifu` — **strong current pre-play interest signal with multiple explicit reasons**. Dmitry associates its fantasy/atmosphere with the film `The Raid`, which he loves. He is attracted by the game's minimalism, wants to try its combat system, finds the aging concept intriguing, and is additionally motivated by a very difficult achievement for completing the challenge without aging because he wants to test himself. This is strong start-priority evidence, but not yet a confirmed played positive.
- `Alan Wake` — **moderate positive pre-play interest, but not queue-reordering priority**. Dmitry has only minimal retained knowledge of the game, although he likely saw a review in the past. After a spoiler-light description, he said it reminded him of `Silent Hill`, that he would play something like this, and that he feels he currently has relatively little of this kind of experience. However, he would not rearrange his current queue for it. Treat this as a valid full-game candidate with novelty/variety appeal, not as a strong near-term priority or confirmed horror-genre preference.
- `Batman: Arkham` series — also functions as a **current replay-priority anchor**: a familiar positive experience can outrank a moderately interesting new game (`High On Life`) when atmosphere, story, combat and achievements are all strong draws.
- `Trine 4: The Nightmare Prince` — was an explicit current-attention case while discounted and is now additionally a confirmed played positive in its intended family-play context.

## Mechanics / structure preferences

- **Durable positive signal: achievements can materially increase both start motivation and replay value.** This now repeats across independent examples: the difficult no-aging achievement is one reason `Sifu` interests Dmitry, and achievements are one of the explicit reasons he would replay `Batman: Arkham`. Dmitry does **not** currently distinguish mastery-style repetition from counter/grind-style repetition as inherently better or worse: if the underlying activity remains interesting, either form can be acceptable or motivating. Do not assume collectible/count achievements are negative merely because they require repetition.
- **Repetition itself is not a confirmed negative.** Dmitry explicitly says there is no important difference between repeatedly mastering a hard fight and repeating simpler actions for a counter **if the activity is interesting**. The relevant risk is therefore boredom/tedium, not repetition as a structural property. `unchanged_repetition` should not be treated as a strong standalone dislike without evidence that the repeated activity becomes uninteresting.
- **Management/progression systems are conditionally positive when optional.** Dmitry says inventory, crafting, equipment selection, upgrades/base progression or resource management can be interesting, especially at first, but he is glad when they are **not mandatory**. This suggests that such systems can add engagement as an optional layer, while required ongoing upkeep risks turning into routine. `management_routine` should therefore focus on **forced maintenance burden / loss of optionality**, not on the mere presence of management mechanics.
- **Puzzles are conditionally positive as variety, but density matters.** Dmitry cites the separate block-moving puzzle rooms in `Hogwarts Legacy` as enjoyable. However, he says that if there were too many of them they would start to feel oppressive/overbearing. `puzzle_pacing` should therefore model **overconcentration and interruption of the broader game rhythm**, not treat the existence of puzzles as a negative. Puzzles can be a welcome side activity or pace change when they remain proportionate.
- **Positive signal: engaging combat is an important attraction.** `Batman: Arkham` combat is one of the reasons Dmitry wants to replay the series, while curiosity about `Sifu`'s combat is a major reason it sits high in his current queue. This supports combat quality/feel as a meaningful ranking factor, but not a blanket preference for action games.
- **Open world is a default skepticism signal, not a hard dislike.** When Dmitry sees that a game has an open world, he says he is more likely to expect a negative than a positive. However, `Red Dead Redemption 2` is his strongest counterexample and is explicitly described as the best open world. Therefore open-world structure should slightly raise scrutiny rather than trigger a blanket penalty or exclusion.
- **What makes open-world freedom work for Dmitry is becoming clearer.** `RDR2` works because the world supports varied activities, atmospheric immersion, organic discovery and rewarding side loops rather than merely offering space. Dmitry liked hunting, bounty hunting, spending money earned from activities, discovering unusual NPCs and criminals, and finding side details that deepened the world. This suggests that **world density + authored discoveries + meaningful activities + usable rewards** can overcome his default skepticism toward open worlds.
- **Organic discovery is positive, but it needs reasonable progress feedback.** Dmitry enjoys finding things by chance and says unexplored space loses value if all interesting content is revealed in advance. However, the opposite extreme is also negative: if the game gives no indication that an area has already been exhausted, repeated wandering through the same cleared places becomes frustrating. The preferred pattern is therefore **hidden/organic discovery plus enough state/progress feedback to know when an area is effectively done**, not either a fully pre-marked checklist or total informational opacity.
- **Directionlessness cannot be scored in isolation.** Dmitry explicitly rejected an abstract "guided game vs open world" comparison because the appeal depends on the rest of the design. The project's `directionlessness` concept must therefore be tested contextually: freedom can work extremely well when the world, story, atmosphere and activities justify it, as in `RDR2`, but lack of feedback about completed/exhausted spaces can still become irritating.
- Tentative positive hypothesis: a distinctive, easily understandable high-concept premise can increase interest. Current explicit examples: `American Arcadia`, whose "Truman Show"-like concept appeals to Dmitry, and `Sifu`, whose aging mechanic he finds intriguing. Confidence is increasing but still insufficient for a broad rule.
- **Tentative positive signal: focused/minimalist presentation can raise interest when the core activity itself is appealing.** `Sifu` is the current explicit example: Dmitry specifically cites minimalism together with wanting to try the combat. Do not interpret this as a blanket preference for short or mechanically simple games.
- **Positive challenge signal:** demanding mastery challenges can increase motivation when they feel like a personal skill test. `Sifu`'s no-aging achievement is attractive specifically because Dmitry wants to test himself. However, this is **one positive form of engagement, not a requirement**: repetitive counter/grind tasks are not automatically worse if the repeated activity itself stays interesting.
- **Tentative negative structural signal:** games can lose substantial appeal when their presentation makes the experience feel dry, technical, tedious, or dominated by learning systems/instructions before the fun is apparent. `HighFleet` is the current strong example. This should be treated as aversion to the **felt burden / presentation of technicality**, not as a blanket dislike of complexity, strategy, management, simulation, or deep systems.
- **Context-sensitive positive:** a game can be a strong fit when it works well as an accessible shared/family experience. `Trine 4` is the first confirmed example. Do not generalize this to all co-op/family games without more examples.
- `Tails of Iron 2: Whiskers of Winter` currently reads to Dmitry as a **secondary / palate-cleanser game** rather than a main game: something he could start when he wants something lighter or needs a break from the main game, but not something he would currently choose as his primary game.
- `High On Life` is an important counterexample showing that **lower queue priority does not imply palate-cleanser status**. Dmitry sees it as a normal/full game that simply loses to stronger current choices. The Taste model should distinguish absolute role/context from relative queue priority.
- Four current risk concepts now have direct user calibration and should not be treated as coarse binary dislikes: `directionlessness` is contextual and especially sensitive to progress feedback; `unchanged_repetition` is not negative if the repeated activity stays interesting; `management_routine` becomes risky mainly when upkeep is mandatory; `puzzle_pacing` becomes risky mainly when puzzles are too dominant or frequent.
- Do **not** infer a dislike of strategy, management, simulation, fleet mechanics, retro presentation, or any other `HighFleet` component from this case alone. More targeted comparisons are required to determine which kinds of complexity feel engaging versus instructional/tedious.

## Story / atmosphere preferences

- **Atmosphere is a confirmed important positive factor.** Dmitry explicitly names atmosphere as one of the main reasons he wants to replay `Batman: Arkham`; `Sifu` also gains substantial pre-play appeal because it evokes the feeling/fantasy of `The Raid`, a film he loves; and `RDR2`'s atmosphere is one of the main reasons its open world works for him. `Alan Wake` also received a moderate positive pre-play reaction partly through its dark atmospheric resemblance to `Silent Hill`, although this remains weaker evidence than the played anchors. Atmosphere should therefore be treated as a genuine personal-fit signal rather than decorative metadata.
- **Story can be a major positive when the title otherwise fits.** Dmitry explicitly names story among the reasons he wants to replay `Batman: Arkham`. Evidence is currently strong for Arkham but not broad enough to claim he always prioritizes narrative-heavy games.
- **Small authored discoveries can deepen immersion strongly.** In `RDR2`, Dmitry specifically liked finding unusual NPCs/criminals and details that generated Arthur's observations/notes and made him feel more immersed in the world. This is stronger evidence for curiosity-driven worldbuilding than for passive lore dumps.
- `American Arcadia` gains interest from a recognizable high-concept setup reminiscent of `The Truman Show`; this is concept attraction rather than confirmed story-quality preference.

## Visual preferences

- `American Arcadia` and `Afterimage` were both described as visually attractive. This is too weak and too small a sample to infer a durable art-style preference.
- `HighFleet` produced a strong negative trailer-level reaction, but the user described the cause primarily as an overall sense of tedious technicality rather than a specific art-style rejection. Do not convert this into an art-style rule.
- `Tails of Iron 2: Whiskers of Winter` — explicit visual downgrade: Dmitry described the trailer as looking like a **cheap indie game with angular/rough graphics**. This lowers perceived main-game priority for him. Treat this as a title-level visual signal until repeated across more games; do not infer a blanket dislike of indie or stylized 2D games.

## Genre preferences and exceptions

- Open-world games start with **mild negative prior expectation** for Dmitry, but this is not a genre-level rejection. `Red Dead Redemption 2` is a major positive exception and demonstrates that execution/context dominates the structural label.
- Horror / psychological-thriller preference is **not yet established**, but `Alan Wake` produced a moderate positive pre-play reaction and its resemblance to `Silent Hill` was perceived positively. More played or familiar controls are needed before treating horror as a genre preference.
- Other genre preferences are not yet established. Do not infer them from current INCLUDE/EXCLUDE output, isolated wishlist entries, or the current small set of controls.

## Known comparison anchors

- `American Arcadia` vs `Afterimage` — **not a valid preference winner yet**. Dmitry chose `American Arcadia`, but explicitly identified familiarity asymmetry: he has seen a review of `American Arcadia` and knows essentially nothing about `Afterimage`. The comparison may be reused only after giving comparable spoiler-light information about both games. What is valid from this test: both look attractive to him, and the `American Arcadia` concept appeals to him.
- `High On Life` vs `HighFleet` — produces one reliable result despite familiarity asymmetry: `HighFleet` itself is a strong negative start-priority control after Dmitry watched its trailer and found it unappealing. The reason he gave is the sense of tedious, dry technicality — "more like studying an instruction manual than playing a game." `High On Life` was later calibrated independently as a moderate full-game candidate, not a top-priority or palate-cleanser title.
- `Trine 4: The Nightmare Prince` vs `Tails of Iron 2: Whiskers of Winter` — **not a clean pairwise winner test**, because `Trine 4` had already been purchased and played with the family while `Tails of Iron 2` was only inspected through a trailer. Nevertheless, both sides independently produced useful evidence: `Trine 4` is a confirmed positive in family play; `Tails of Iron 2` is currently a lower-priority, secondary-game candidate with a visual-quality concern.
- Current relative queue anchor: `Sifu` > possible `Batman: Arkham` replay > `High On Life` for near-term start priority. This is a priority relation only; it does not mean `High On Life` is disliked or secondary/lightweight.
- `Alan Wake` is a moderate-interest full-game control: attractive enough to play and useful as variety because Dmitry feels he has little of this type of experience, but not strong enough to reorder the current queue.
- `Sifu` priority is supported by multiple explicit attractions rather than familiarity alone: `The Raid` association, minimalism, curiosity about combat, the aging concept, and a difficult achievement that functions as a personal skill challenge.
- `Batman: Arkham` is a useful positive decomposition anchor: atmosphere + story + combat + achievements are all independently named reasons for replay value.
- `Red Dead Redemption 2` is the primary open-world exception anchor: open world normally creates skepticism, but this game is explicitly judged the best open world because its atmosphere, activities, discoveries and reward loops make the world feel worth inhabiting. Its organic discovery matters, but so does feedback that prevents already-cleared space from becoming an annoying uncertainty sink.
- `Hogwarts Legacy` puzzle rooms are a useful positive-but-density-sensitive control: the block-moving puzzle rooms are enjoyable in their current role, but too many similar puzzle segments would begin to dominate the experience negatively.

## Calibration methodology learned from user feedback

- Pairwise taste tests must control for **familiarity / information asymmetry**. A game Dmitry already knows from a review should not be treated as a clean preference winner over an unfamiliar game.
- A game already purchased/played cannot be used as a clean A/B comparator against a trailer-only game without explicitly separating **experienced fit** from **pre-play appeal**.
- When familiarity differs, first provide comparable spoiler-light descriptions or let Dmitry inspect a trailer, then ask which is more appealing and why.
- Abstract structural questions without the rest of the game context can be misleading. Dmitry explicitly rejected a context-free guided-vs-open-world binary because real preference depends on the total design. Prefer concrete titles or multi-factor scenarios.
- Exploration questions also need to distinguish **discovery uncertainty** from **completion/progress uncertainty**. Dmitry likes not knowing exactly what he may discover, but dislikes being unable to tell whether he has already exhausted an area.
- Repetition questions must distinguish **repetition itself** from **whether the repeated activity stays interesting**. Dmitry does not currently prefer mastery repetition over counter/grind repetition in principle; boredom/tedium is the relevant failure mode.
- Management questions must distinguish **optional engagement** from **mandatory upkeep**. Dmitry can enjoy management/progression systems, especially initially, but values being able to ignore them when they stop being interesting.
- Puzzle questions must distinguish **puzzles as welcome variety** from **puzzles dominating the pacing**. `Hogwarts Legacy` provides a concrete positive example of optional/contained puzzle rooms, with an explicit warning that excessive density would become oppressive.
- A strong negative reaction to an unfamiliar game's trailer can still be a valid **pre-play interest/start-priority** signal even when the opposite member of the pair is better known.
- When capturing a negative control, prefer the user's stated experiential reason (for example, "feels like studying an instruction manual") over broad genre labels such as strategy or simulation.
- Distinguish **main-game priority**, **secondary/palate-cleanser suitability**, and **family-play suitability**. A game can fit one role well without being a strong candidate for another.
- Also distinguish **role** from **relative queue priority**: a full/main-game candidate can still sit behind other stronger main-game choices without becoming a palate-cleanser.
- For positive controls, capture the independent reasons that create desire to start or replay a game; several aligned reasons are more informative than a bare winner label.
- Repeated factors across independent games should be promoted from title-level observations to durable preference signals only when the user's statements support that promotion. `Achievements` now qualifies; broad genre preferences still do not.
- Unknown/unfamiliar must remain distinct from dislike or weak fit.

## Uncertainty / questions

- Which current high-scoring games are genuine positives rather than plausible model guesses?
- What forms of **area-completion/progress feedback** work best for Dmitry without spoiling discovery: subtle completion state, fog/map clearing, discovered-vs-undiscovered counters, post-discovery markers, or something else?
- What makes a repeated activity stay interesting for Dmitry over time: mechanical depth, changing context, rewards/progression, intrinsic feel, achievement goals, or some combination? Repetition itself is no longer treated as the suspected problem.
- At what point does optional management become annoying for Dmitry: frequency of interruption, amount of inventory clutter, weak rewards, mandatory optimization, or simply long-term repetition? Current evidence establishes that **optionality matters**, not the exact threshold.
- How much puzzle density is comfortable before puzzles begin to crowd out the rest of the experience? Current evidence establishes the direction but not a numerical threshold.
- Does the `HighFleet` aversion generalize to other games whose systems/UX feel technical or instructional, and what kinds of complexity avoid that reaction?
- How broad is the visual-quality sensitivity seen with `Tails of Iron 2`, and which stylized/indie-looking games are exceptions?
- How much should the system model **play context** separately: solo main game, family/co-op game, and lighter secondary game?
- How should the system represent **relative queue strength** among games that are all valid main-game candidates?
- How broadly does the `Batman: Arkham` combination of atmosphere + story + combat predict other strong positives?
- Does `Alan Wake`'s positive resemblance to `Silent Hill` reflect a broader attraction to psychological horror/unease, or only interest in this specific presentation?
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