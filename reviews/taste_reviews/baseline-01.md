# TASTE REVIEW — BASELINE 01

Status: complete baseline review; direct user calibration expanded
Role: dedicated Taste Reviewer
Mode: advisory only; no production code/config/weight changes

## Profile confidence

**LOW, improving materially**.

The repository alone did not contain enough confirmed game-level positive and negative controls to claim that the Taste system reliably models Dmitry's preferences. Direct calibration now adds:
- confirmed played positives: `Trine 4: The Nightmare Prince` in family-play context, `Batman: Arkham` as a replay-positive anchor, and `Red Dead Redemption 2` as a strong open-world positive;
- one strong negative pre-play/start-priority control: `HighFleet`;
- one lower-priority/secondary-game control: `Tails of Iron 2: Whiskers of Winter`;
- `High On Life` as a moderate full/main-game candidate that is not top queue priority and not a palate-cleanser;
- `Sifu` as a strong current pre-play interest candidate;
- direct calibration of four model-risk concepts: `directionlessness`, `unchanged_repetition`, `management_routine`, and `puzzle_pacing`.

This is enough to identify concrete model mismatches and several places where coarse risk labels can overstate negatives, but not enough to infer broad genre rules or to classify the whole current selection pressure with high confidence.

## Sample reviewed

Bounded evidence only:

1. Current production ranking diagnostics: `data/production/visual/ranking_lookup/*`.
   - manifest: 442 current ranked items;
   - current examples reviewed: `Afterimage`, `American Arcadia`, `Alan Wake`, `Amnesia: The Bunker`, `High On Life`, `HighFleet`, `Haven Moon`, `Tails of Iron`, `Tails of Iron 2: Whiskers of Winter`, `Tangle Tower`, `Terminator: Resistance`, `Teenage Mutant Ninja Turtles: Splintered Fate`.
2. Current unresolved expected-candidate control: `Trine 4: The Nightmare Prince`, using `reviews/worker_reports/trine4-missing-diagnosis-01.md`.
3. Historical canonical Taste-v2 projection: `data/cache/taste_fit.index.json` and `data/cache/taste_reason_codes.report.json`.
4. Historical downstream content eligibility: `data/cache/content_eligibility.validation.json`.
5. Current direct-conflict report: `data/cache/taste_direct_conflicts.report.json`.
6. Direct user calibration:
   - `American Arcadia` / `Afterimage`: invalid clean A/B due familiarity asymmetry; valid positive concept signal for `American Arcadia`;
   - `HighFleet`: strong negative trailer/start-priority control;
   - `Trine 4`: confirmed liked in intended family context;
   - `Tails of Iron 2`: secondary/palate-cleanser candidate, not primary-game priority;
   - `High On Life`: moderate full-game interest, below stronger current choices;
   - `Sifu`: strong pre-play interest driven by `The Raid` association, minimalism, combat curiosity, aging concept and a difficult achievement challenge;
   - `Batman: Arkham`: confirmed replay-positive anchor driven by atmosphere, story, combat and achievements;
   - `Red Dead Redemption 2`: best-open-world anchor, with positive organic discovery, activities, atmosphere and reward loops;
   - `Hogwarts Legacy`: puzzle-room example showing puzzles can be enjoyable in moderation but oppressive if over-concentrated.

The full `data/production/visual/ranking_review.jsonl` artifact is empty in current `main`, so it was not used as evidence.

## What the system currently gets right

### 1. Explicit wishlist interest is not ignored

Current ranking diagnostics give wishlist points to at least:
- `American Arcadia`: wishlist=true, wishlist_points=4.0, personal_score=47.5;
- `High On Life`: wishlist=true, wishlist_points=4.0, personal_score=47.0.

This is directionally correct: explicit interest contributes to personal priority rather than being discarded.

Direct calibration adds an important constraint: wishlist/current interest does **not** imply "play next". `High On Life` remains a valid full/main-game candidate while sitting below `Sifu` and potentially a `Batman: Arkham` replay in near-term priority.

### 2. Serious modeled risks actually reduce personal score

Examples:
- `Terminator: Resistance`: taste_points=40.2 but risk_points=-10.0 and personal_score=33.0;
- `Teenage Mutant Ninja Turtles: Splintered Fate`: taste_points=44.1 but risk_points=-10.0 and personal_score=36.1;
- `Haven Moon`: risk_points=-10.0 for `directionlessness`, leaving personal_score=22.6 near the bottom of the current list.

So the ranking is not simply accumulating positive fit while ignoring negative hypotheses.

The problem is now clearer: several risk concepts are **too coarse if treated as direct dislikes**. Direct calibration shows they require context.

### 3. Historical downstream content eligibility did not add a second exclusion layer after Taste include

The Taste-v2 content eligibility validation received 101 Taste-included candidates and marked all 101 eligible (`excluded_count=0`). This is useful negative evidence against a duplicated downstream content filter for that historical checkpoint.

## Strongest taste mismatches / concerns

### 1. `HighFleet` is a concrete model false-positive for personal priority

Current diagnostics treated `HighFleet` as a very strong model-only Taste candidate; in the baseline pair it sat level with wishlist game `High On Life` on personal_score.

Direct user calibration contradicts that strongly. After watching the `HighFleet` trailer, Dmitry said it did not appeal to him and that he would postpone it until there was little else left to play. The stated reason was the feeling of **tedious, dry technicality** — more like studying an instruction manual than starting a game.

This is now a real negative control. The mismatch is not evidence that strategy/management/deep systems are generically bad for Dmitry; it is evidence that the current model can mistake a technically rich-looking game for a strong personal fit when its felt burden/presentation is actually a major turn-off.

### 2. `Tails of Iron 2` appears over-prioritized as a main-game recommendation

The baseline selected `Tails of Iron 2: Whiskers of Winter` as a current strong-fit comparison candidate.

After watching its trailer, Dmitry did not reject it, but described it as visually resembling a cheap indie game with angular/rough graphics and said he could imagine using it as a **light secondary/palate-cleanser game**, not as his main game.

This suggests a ranking blind spot: the system may conflate **acceptable/fit enough to play** with **high priority to start as the main game**.

`High On Life` adds the complementary control: lower queue priority does not automatically mean secondary/palate-cleanser role. The model should separate **role** from **relative queue strength**.

### 3. `Trine 4` demonstrates a real false-negative user-visible omission

Canonical diagnosis showed `Trine 4: The Nightmare Prince` had:
- valid Steam KZ availability and active sale;
- valid commercial/deal path;
- no negative Taste verdict;
- unresolved Taste semantic work because `App_690640` had `taste_cache_key_missing`;
- fail-closed visual omission before ranking.

Direct calibration adds the missing user-side evidence: Dmitry bought `Trine 4` specifically to play with his family, played it with them the next day, and explicitly said he liked it.

Therefore this is a **confirmed positive that was absent from the user-visible selection because semantic state was unresolved**, demonstrating that unknown-as-absence can hide a genuinely suitable game.

### 4. Coarse risk labels can over-penalize valid preferences

Four current risk concepts now have direct user calibration:

- **`directionlessness`**: not a blanket dislike. Open worlds initially create skepticism, but `RDR2` is Dmitry's best-open-world example. Organic discovery is positive when the world is dense, atmospheric and rewarding. The negative appears when freedom lacks useful feedback and the player cannot tell that an area is exhausted.
- **`unchanged_repetition`**: repetition itself is not a negative. Dmitry sees no important difference between repeatedly mastering a hard fight and repeating simpler actions for a counter if the underlying activity remains interesting. The real failure mode is boredom/tedium.
- **`management_routine`**: management/progression can be enjoyable, particularly at first, if it is optional. The risk is forced ongoing upkeep after the layer stops being interesting.
- **`puzzle_pacing`**: puzzles can be enjoyable as contained variety. `Hogwarts Legacy` block-moving puzzle rooms are a positive example, but too many would become oppressive. The relevant issue is puzzle density/dominance, not puzzles themselves.

This is strong evidence that binary or heavy penalties attached directly to these labels can squeeze selection incorrectly unless the system models **degree, optionality, density, feedback and context**.

### 5. Production top rank can look like strong personal recommendation when it is actually urgency-driven

`Terminator: Resistance` is production rank 4 and `TMNT: Splintered Fate` rank 7 even though both have serious -10 Taste-risk penalties and comparatively weak personal scores (33.0 and 36.1). Their sale urgency is `today`.

This does not prove the underlying Taste scores are wrong. It does show that production rank is **not a pure personal-fit ordering**.

### 6. Historical Taste-v2 evidence shows very strong exclusion pressure, much of it based on insufficient evidence

The verified Taste-v2 reason-code report contains 583 entries:
- 36 `include_strong`;
- 65 `include_moderate`;
- 135 `exclude_audited_below`;
- 3 `exclude_direct_conflict`;
- 344 `exclude_insufficient`.

Thus the historical model excluded a very large number of candidates for insufficient evidence rather than a demonstrated negative preference.

This remains a meaningful warning for recall/selection breadth, but must not be projected mechanically onto the current normalized ranking.

## Selection-pressure assessment

**`cannot_determine`** for the current system overall, but evidence now leans more strongly toward **over-compression caused by coarse risk semantics in addition to separate false-positive problems**.

Evidence toward excessive tightening / lost recall:
- historical Taste-v2 excluded many candidates for insufficient evidence;
- unresolved semantic state can remove candidates without a negative preference verdict;
- `Trine 4` is a confirmed positive family-play example hidden by unresolved-state handling;
- four calibrated risk labels are materially more conditional than their names suggest, creating a plausible path for valid candidates to be over-penalized.

Evidence against simply loosening everything:
- `HighFleet` is a strong current false-positive for personal start priority;
- `Tails of Iron 2` appears suitable mainly as a secondary game despite being selected as a strong-fit calibration candidate;
- current normalized ranking already contains 442 items.

Therefore the problem is **not one global threshold being simply too strict or too loose**. The evidence points toward poor calibration of *kind of fit*, risk-context loss, and unsafe unknown treatment.

## Recommended tests / changes for Director review

Maximum three, advisory only:

1. **Replace coarse risk-label QA with context-sensitive controls.** For `directionlessness`, `unchanged_repetition`, `management_routine`, and `puzzle_pacing`, test the actual negative condition instead of the structural feature itself: lack of progress feedback, boredom, mandatory upkeep, and puzzle over-density respectively. Use `RDR2` and `Hogwarts Legacy` as positive exception controls.

2. **Add role + relative-priority calibration to Taste QA.** Test at least `main/primary game`, `secondary/palate-cleanser`, and `family/co-op` suitability, while separately tracking queue strength within a role. Use `Trine 4` (family positive), `Tails of Iron 2` (secondary current fit), and `High On Life` (full-game but moderate queue priority) as controls.

3. **Unknown-vs-negative recall and false-positive burden test.** Keep `Trine 4` as a confirmed-positive regression control for unresolved-state omission, and `HighFleet` as the negative control for dry/technical felt burden. The test must not collapse `HighFleet` into a generic anti-complexity rule.

## Unresolved taste questions

Further calibration should prefer concrete familiar titles and avoid forced pairwise comparisons where familiarity differs.

Current questions:
- Which familiar games provide additional strong positive/negative controls across genres?
- Which kinds of complexity feel deep but inviting, versus technically burdensome like `HighFleet`?
- How broad is the visual-production-value sensitivity seen with `Tails of Iron 2`?
- How strong is the preference for atmosphere/story/combat combinations beyond `Batman: Arkham`?
- Which open-world games besides `RDR2` are positive or negative controls?
- How much puzzle density, management obligation and progress opacity is too much in concrete games?

## Profile update

`USER_TASTE_PROFILE.md` now records:
- `Trine 4` as a confirmed family-play positive;
- `HighFleet` as a strong negative start-priority control;
- `Tails of Iron 2` as secondary/palate-cleanser rather than main-game priority;
- `High On Life` as a moderate full/main-game candidate, not top priority and not a palate-cleanser;
- `Sifu` as strong current pre-play interest with multiple independent attractions;
- `Batman: Arkham` as a replay-positive anchor driven by atmosphere, story, combat and achievements;
- `RDR2` as the primary open-world positive and organic-discovery control;
- achievements as a durable motivator;
- direct contextual interpretations for `directionlessness`, `unchanged_repetition`, `management_routine`, and `puzzle_pacing`.

## Bottom line

The baseline now has enough direct user evidence to reject both simplistic interpretations:
- "the current Taste output is fine because it is internally consistent";
- "the fix is just to loosen the threshold".

Several distinct failure modes are visible:
1. a **confirmed positive can disappear as unknown** (`Trine 4`);
2. a **strong model fit can be a strong user negative** (`HighFleet`);
3. a **plausible game can be assigned the wrong role/priority** (`Tails of Iron 2`, contrasted with `High On Life`);
4. a **structural feature can be incorrectly treated as the negative itself** when the real dislike depends on context, density, optionality or boredom (`directionlessness`, `unchanged_repetition`, `management_routine`, `puzzle_pacing`).

This argues for a more conditional Taste model rather than a more aggressive one.