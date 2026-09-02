# TASTE REVIEW — BASELINE 01

Status: complete baseline review; initial user calibration recorded
Role: dedicated Taste Reviewer
Mode: advisory only; no production code/config/weight changes

## Profile confidence

**LOW, improving**.

The repository alone did not contain enough confirmed game-level positive and negative controls to claim that the Taste system reliably models Dmitry's preferences. Initial direct calibration now adds:
- one confirmed played positive: `Trine 4: The Nightmare Prince` in its intended family-play context;
- one strong negative pre-play/start-priority control: `HighFleet`;
- one lower-priority/secondary-game control: `Tails of Iron 2: Whiskers of Winter`;
- one positive concept/interest signal for `American Arcadia`.

This is enough to identify concrete ranking/model mismatches, but not enough to infer broad genre rules or to classify the overall current selection pressure with high confidence.

## Sample reviewed

Bounded evidence only:

1. Current production ranking diagnostics: `data/production/visual/ranking_lookup/*`.
   - manifest: 442 current ranked items;
   - current examples reviewed: `Afterimage`, `American Arcadia`, `Alan Wake`, `Amnesia: The Bunker`, `High On Life`, `HighFleet`, `Haven Moon`, `Tails of Iron`, `Tails of Iron 2: Whiskers of Winter`, `Tangle Tower`, `Terminator: Resistance`, `Teenage Mutant Ninja Turtles: Splintered Fate`.
2. Current unresolved expected-candidate control: `Trine 4: The Nightmare Prince`, using `reviews/worker_reports/trine4-missing-diagnosis-01.md`.
3. Historical canonical Taste-v2 projection: `data/cache/taste_fit.index.json` and `data/cache/taste_reason_codes.report.json`.
4. Historical downstream content eligibility: `data/cache/content_eligibility.validation.json`.
5. Current direct-conflict report: `data/cache/taste_direct_conflicts.report.json`.
6. Initial direct user calibration:
   - `American Arcadia` vs `Afterimage` — invalid as a clean A/B winner because of familiarity asymmetry, but produced a positive concept signal for `American Arcadia`;
   - `High On Life` vs `HighFleet` — invalid for relative strength because familiarity differs, but `HighFleet` independently became a strong negative start-priority control after trailer inspection;
   - `Trine 4` vs `Tails of Iron 2` — invalid as a clean A/B winner because `Trine 4` was already bought and played while `Tails of Iron 2` was trailer-only, but both produced useful independent evidence.

The full `data/production/visual/ranking_review.jsonl` artifact is empty in current `main`, so it was not used as evidence.

## What the system currently gets right

### 1. Explicit wishlist interest is not ignored

Current ranking diagnostics give wishlist points to at least:
- `American Arcadia`: wishlist=true, wishlist_points=4.0, personal_score=47.5;
- `High On Life`: wishlist=true, wishlist_points=4.0, personal_score=47.0.

This is directionally correct: explicit interest contributes to personal priority rather than being discarded.

However, calibration is still insufficient to determine whether +4 is the right strength.

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

### 1. `HighFleet` is a concrete model false-positive for personal priority

Current diagnostics treated `HighFleet` as a very strong model-only Taste candidate; in the baseline pair it sat level with wishlist game `High On Life` on personal_score.

Direct user calibration contradicts that strongly. After watching the `HighFleet` trailer, Dmitry said it did not appeal to him and that he would postpone it until there was little else left to play. The stated reason was the feeling of **tedious, dry technicality** — more like studying an instruction manual than starting a game.

This is now a real negative control. The mismatch is not evidence that strategy/management/deep systems are generically bad for Dmitry; it is evidence that the current model can mistake a technically rich-looking game for a strong personal fit when its felt burden/presentation is actually a major turn-off.

### 2. `Tails of Iron 2` appears over-prioritized as a main-game recommendation

The baseline selected `Tails of Iron 2: Whiskers of Winter` as a current strong-fit comparison candidate.

After watching its trailer, Dmitry did not reject it, but described it as visually resembling a cheap indie game with angular/rough graphics and said he could imagine using it as a **light secondary/palate-cleanser game**, not as his main game.

This suggests a second ranking blind spot: the system may conflate **acceptable/fit enough to play** with **high priority to start as the main game**. A game can be a valid secondary recommendation while still being materially over-ranked for primary-play intent.

### 3. `Trine 4` demonstrates a real false-negative user-visible omission

Canonical diagnosis showed `Trine 4: The Nightmare Prince` had:
- valid Steam KZ availability and active sale;
- valid commercial/deal path;
- no negative Taste verdict;
- unresolved Taste semantic work because `App_690640` had `taste_cache_key_missing`;
- fail-closed visual omission before ranking.

Direct calibration now adds the missing user-side evidence: Dmitry bought `Trine 4` specifically to play with his family, played it with them the next day, and explicitly said he liked it.

Therefore this is no longer merely an abstract unknown-vs-negative concern. It is a **confirmed positive that was absent from the user-visible selection because semantic state was unresolved**, demonstrating that unknown-as-absence can hide a genuinely suitable game.

The context matters: the positive is confirmed for family play, not automatically for solo/main-game priority.

### 4. Production top rank can look like strong personal recommendation when it is actually urgency-driven

`Terminator: Resistance` is production rank 4 and `TMNT: Splintered Fate` rank 7 even though both have serious -10 Taste-risk penalties and comparatively weak personal scores (33.0 and 36.1). Their sale urgency is `today`.

This does not prove the underlying Taste scores are wrong. It does show that the production rank is **not a pure personal-fit ordering** and can place weaker personal matches above much stronger ones because urgency is applied first.

For taste review, production rank must therefore never be treated as evidence that the system believes a game is one of Dmitry's strongest matches.

### 5. Historical Taste-v2 evidence shows very strong exclusion pressure, much of it based on insufficient evidence

The verified Taste-v2 reason-code report contains 583 entries:
- 36 `include_strong`;
- 65 `include_moderate`;
- 135 `exclude_audited_below`;
- 3 `exclude_direct_conflict`;
- 344 `exclude_insufficient`.

Thus the historical model excluded a very large number of candidates for insufficient evidence rather than a demonstrated negative preference.

This is a meaningful warning for recall/selection breadth, but it must **not** be projected mechanically onto the current normalized ranking: the current bounded ranking lookup has 442 items and represents a materially different/newer state.

The current direct-conflict report also has count=0, so it cannot provide present-day negative controls.

## Selection-pressure assessment

**`cannot_determine`** for the current system overall, but confidence has increased that there are **both false-negative and over-prioritization problems**.

Evidence toward excessive tightening / lost recall:
- historical Taste-v2 excluded many candidates for insufficient evidence;
- unresolved semantic state can remove candidates without a negative preference verdict;
- `Trine 4` is now a confirmed positive family-play example that was hidden by exactly this unresolved-state path.

Evidence against simply loosening everything:
- `HighFleet` is a strong current false-positive for personal start priority;
- `Tails of Iron 2` appears suitable only as a lower-priority secondary game despite being selected as a strong-fit calibration candidate;
- current normalized ranking already contains 442 items.

Therefore the emerging problem is **not well described by one global threshold being simply too strict or too loose**. The evidence instead points toward poor calibration of *what kind of fit* a game has, plus unsafe treatment of unknowns.

## Recommended tests / changes for Director review

Maximum three, advisory only:

1. **Add role/context calibration to Taste QA.** Test games separately for at least `main/primary game`, `secondary/palate-cleanser`, and `family/co-op` suitability instead of treating all positive fit as one scalar priority. Use `Trine 4` (family positive) and `Tails of Iron 2` (secondary-only current fit) as initial controls.

2. **Unknown-vs-negative recall test with confirmed-positive control.** On a bounded current sample, count commercially valid candidates omitted only because Taste semantic state is unresolved/missing. `Trine 4` should be retained as a regression control showing that unknown-state omission can hide a real positive.

3. **False-positive test for dry/technical burden.** Compare current high model-fit games against direct user reaction to games whose presentation feels technical/instructional. `HighFleet` should be a negative control. The test must not collapse this into a generic anti-strategy or anti-complexity rule.

## Unresolved taste questions

Further calibration should avoid forced pairwise comparisons where familiarity differs. Prefer already-familiar titles or independently rate one title at a time.

Current questions:
- How strong is `High On Life` itself as a start/play candidate, independent of `HighFleet`?
- Which familiar games demonstrate **complex/deep but still inviting**, to distinguish enjoyable complexity from `HighFleet`-style technical burden?
- How often does visual perceived production value change whether a game feels like a main-game candidate versus a secondary game?
- How strongly should family/co-op suitability influence purchase recommendations compared with solo/main-game fit?
- Does attraction to distinctive high-concept premises repeat beyond `American Arcadia`?

## Profile update

`USER_TASTE_PROFILE.md` now records:
- `Trine 4` as the first confirmed played positive, specifically in family-play context;
- `HighFleet` as a strong negative start-priority control and its explicit "instruction manual / tedious technicality" reason;
- `Tails of Iron 2` as a current secondary/palate-cleanser candidate rather than a main-game priority, with an explicit visual-quality concern;
- `American Arcadia` as a positive concept/interest signal without pretending it cleanly defeated an unfamiliar `Afterimage`;
- a calibration rule separating familiarity, experienced fit, pre-play appeal and play context.

## Bottom line

The baseline now has enough direct user evidence to reject the idea that current Taste output is reliably calibrated simply because it is internally consistent.

Three different failure modes are already visible:
1. a **confirmed positive can disappear as unknown** (`Trine 4`);
2. a **strong model fit can be a strong user negative** (`HighFleet`);
3. a **plausible game can be assigned the wrong role/priority** (`Tails of Iron 2`: secondary rather than main).

This argues against a simple global loosen/tighten change. The next useful work is to calibrate personal priority and play context with familiar games, while keeping unknown separate from negative.