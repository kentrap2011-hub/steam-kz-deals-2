# TASTE REVIEW — BASELINE 01

Status: complete baseline review; user calibration still required
Role: dedicated Taste Reviewer
Mode: advisory only; no production code/config/weight changes

## Profile confidence

**LOW**.

The repository currently does not contain enough confirmed game-level positive and negative controls to claim that the Taste system reliably models Dmitry's preferences. `USER_TASTE_PROFILE.md` was previously only a scaffold. The baseline therefore separates explicit-interest evidence, model hypotheses and actual confirmed taste rather than treating current output as ground truth.

## Sample reviewed

Bounded evidence only:

1. Current production ranking diagnostics: `data/production/visual/ranking_lookup/*`.
   - manifest: 442 current ranked items;
   - current examples reviewed: `Afterimage`, `American Arcadia`, `Alan Wake`, `Amnesia: The Bunker`, `High On Life`, `HighFleet`, `Haven Moon`, `Tails of Iron`, `Tails of Iron 2: Whiskers of Winter`, `Tangle Tower`, `Terminator: Resistance`, `Teenage Mutant Ninja Turtles: Splintered Fate`.
2. Current unresolved expected-candidate control: `Trine 4: The Nightmare Prince`, using `reviews/worker_reports/trine4-missing-diagnosis-01.md`.
3. Historical canonical Taste-v2 projection: `data/cache/taste_fit.index.json` and `data/cache/taste_reason_codes.report.json`.
4. Historical downstream content eligibility: `data/cache/content_eligibility.validation.json`.
5. Current direct-conflict report: `data/cache/taste_direct_conflicts.report.json`.

The full `data/production/visual/ranking_review.jsonl` artifact is empty in current `main`, so it was not used as evidence.

## What the system currently gets right

### 1. Explicit wishlist interest is not ignored

Current ranking diagnostics give wishlist points to at least:
- `American Arcadia`: wishlist=true, wishlist_points=4.0, personal_score=47.5;
- `High On Life`: wishlist=true, wishlist_points=4.0, personal_score=47.0.

This is directionally correct: explicit interest contributes to personal priority rather than being discarded.

However, baseline evidence is insufficient to determine whether +4 is the right strength.

### 2. Serious modeled risks actually reduce personal score

Examples:
- `Terminator: Resistance`: taste_points=40.2 but risk_points=-10.0 and personal_score=33.0;
- `Teenage Mutant Ninja Turtles: Splintered Fate`: taste_points=44.1 but risk_points=-10.0 and personal_score=36.1;
- `Haven Moon`: risk_points=-10.0 for `directionlessness`, leaving personal_score=22.6 near the bottom of the current list.

So the ranking is not simply accumulating positive fit while ignoring negative hypotheses.

Whether these particular risk concepts match Dmitry is **not yet confirmed**; they remain model hypotheses.

### 3. Historical downstream content eligibility did not add a second exclusion layer after Taste include

The Taste-v2 content eligibility validation received 101 Taste-included candidates and marked all 101 eligible (`excluded_count=0`). This is useful negative evidence against a duplicated downstream content filter for that historical checkpoint.

## Strongest taste mismatches / concerns

### 1. Production top rank can look like strong personal recommendation when it is actually urgency-driven

`Terminator: Resistance` is production rank 4 and `TMNT: Splintered Fate` rank 7 even though both have serious -10 Taste-risk penalties and comparatively weak personal scores (33.0 and 36.1). Their sale urgency is `today`.

This does not prove the underlying Taste scores are wrong. It does show that the production rank is **not a pure personal-fit ordering** and can place weaker personal matches above much stronger ones because urgency is applied first.

For taste review, production rank must therefore never be treated as evidence that the system believes a game is one of Dmitry's strongest matches.

### 2. Unknown semantic state can compress the user-visible selection exactly like a negative verdict

`Trine 4: The Nightmare Prince` is a strong calibration case.

Canonical diagnosis shows:
- valid Steam KZ availability and active -80% sale;
- valid commercial/deal path;
- no negative Taste verdict;
- unresolved Taste semantic work because `App_690640` has `taste_cache_key_missing`;
- the visual producer fail-closes the unresolved row before ranking.

Therefore Trine 4 disappears from the user-visible choice even though the system has **not actually concluded that Dmitry would dislike it**.

From a user-facing taste perspective this matters: `unknown` and `negative` currently have the same visible result — absence. That can make the selection feel more certain and narrower than the available taste evidence justifies.

### 3. Historical Taste-v2 evidence shows very strong exclusion pressure, much of it based on insufficient evidence

The verified Taste-v2 reason-code report contains 583 entries:
- 36 `include_strong`;
- 65 `include_moderate`;
- 135 `exclude_audited_below`;
- 3 `exclude_direct_conflict`;
- 344 `exclude_insufficient`.

Thus the historical model excluded a very large number of candidates for insufficient evidence rather than a demonstrated negative preference.

This is a meaningful warning for recall/selection breadth, but it must **not** be projected mechanically onto the current normalized ranking: the current bounded ranking lookup has 442 items and represents a materially different/newer state.

The current direct-conflict report also has count=0, so baseline cannot use it as a reliable set of present-day negative controls.

## Selection-pressure assessment

**`cannot_determine`** for the current system, with a clear historical warning toward **too tight**.

Why not `too_tight` yet:
- current normalized ranking contains 442 items, much broader than the historical 101 Taste-included checkpoint;
- we do not yet have enough confirmed positive false negatives or negative false positives from Dmitry himself;
- model-generated fit/risk cannot be used to validate itself.

Why this is still concerning:
- historical Taste-v2 excluded many candidates for insufficient evidence;
- unresolved current semantic candidates such as Trine 4 are invisible rather than represented as unknown;
- production urgency can obscure the distinction between personal fit and time-sensitive purchase priority.

The next calibration should therefore optimize **recall measurement**, not immediately loosen or tighten weights.

## Recommended tests / changes for Director review

Maximum three, advisory only:

1. **User-calibrated pair test before any Taste threshold/weight change.** Compare explicit-interest/wishlist games against high model-fit non-wishlist games and record which Dmitry actually prefers. Use the results as positive/negative controls for future Taste reviews.

2. **Unknown-vs-negative recall test.** On a bounded current sample, count commercially valid candidates omitted only because Taste semantic state is unresolved/missing, and review several with Dmitry. Do not score `unknown` as a negative preference when measuring Taste precision/recall.

3. **Separate personal-fit QA from urgency/purchase ordering.** For Taste acceptance, evaluate personal_score/taste ordering independently of production urgency rank so a sale ending today cannot make a weak personal match look like a top Taste success.

## Unresolved taste questions

Use concrete comparisons rather than generic genre questions:

1. `American Arcadia` vs `Afterimage`: which one would Dmitry rather start/play, ignoring current price? (`American Arcadia` is wishlist=true; `Afterimage` has a slightly stronger current total result.)
2. `High On Life` vs `HighFleet`: which is the stronger personal fit? (Both have personal_score=47.0 in the current diagnostics; `High On Life` has explicit wishlist interest while `HighFleet` has the stronger model-only taste score.)
3. `Trine 4: The Nightmare Prince` vs `Tails of Iron 2: Whiskers of Winter`: which is more appealing to actually play? This tests an unresolved explicit-attention candidate against a current strong-fit recommendation.

For each answer, capture *why* — mechanics/structure/pacing/feel matters more than a bare winner.

## Profile update

`USER_TASTE_PROFILE.md` was updated during this baseline to:
- mark profile confidence LOW;
- keep strong positives/negatives unconfirmed rather than invent them;
- record `American Arcadia` and `High On Life` as explicit-interest signals, not confirmed likes;
- record Trine 4 as an unresolved calibration case, not a negative;
- preserve model risk labels as hypotheses until user-confirmed;
- add the three concrete comparison anchors above.

## Bottom line

The current system may already be less restrictive than the historical Taste-v2 gate, so the evidence does **not** justify blindly loosening it. But it also does not justify trusting current selection as a complete picture of Dmitry's taste.

The largest baseline risk is **false certainty**: unknown/unresolved candidates can disappear like dislikes, and urgent deals can appear near the top like strong personal matches. The next useful evidence is direct pairwise user calibration, not another round of self-validation against the model's own scores.