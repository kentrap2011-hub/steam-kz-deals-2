# WORKER TASK — Deep two-stage comparative calibration implementation 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `DEEP_TWO_STAGE_COMPARATIVE_CALIBRATION_IMPLEMENT_01`
Worker slot: `ЧАТ 2`
Mode: `ARCHITECT / IMPLEMENT / VALIDATE / MIGRATION-PREP`

## User-authorized product decision

The Director explicitly approved a new scoring architecture.

### 1. Remove Fast semantic assessment from ranking decisions

The current "Fast" taste assessment no longer has product value when authoritative Deep analysis exists.

Target product model:

- Fast must not supply a taste score, fit conclusion, personal reasons, or ordering authority.
- Items without Deep may still be provisionally ordered by deterministic non-semantic facts such as price, discount, Steam review evidence, freshness or other already-approved GitHub-owned deterministic signals.
- Such provisional ordering must be visibly/non-ambiguously "not Deep-calibrated".
- Do not let legacy Fast output silently influence final ranking, Deep queue priority, card reasons, or score fallback.
- Historical Fast artifacts may remain temporarily for migration/audit compatibility if deleting them immediately would be unsafe, but production decision paths must stop consuming them.
- Do not introduce a replacement "quick semantic score" under another name.

### 2. Split Deep into two semantic stages

The new pipeline concept is:

`Dossier -> Deep Analysis (Stage 1) -> Comparative Calibration (Stage 2) -> final ranking`

#### Stage 1 — Deep Analysis

Purpose: understand the game on its own, without trying to place it precisely against the whole catalog.

Stage 1 must produce grounded semantic findings such as:

- concrete personal positives;
- concrete personal negatives;
- decisive positive hooks;
- decisive deal-breakers / purchase risks;
- uncertainty / missing evidence;
- fit / not-fit semantic conclusion where justified;
- confidence in the semantic conclusion;
- an **initial / provisional taste estimate** on a 0–100 scale.

The Stage-1 number is intentionally approximate / intuitive.

It answers roughly:

> "Ignoring exact placement among other games, how strongly does this game appear to fit the user's taste?"

It is **not ranking-authoritative**.

It must not be produced by the old fixed additive five-factor arithmetic.

The current five-factor fixed-weight aggregation must no longer be the authority for the overall score.

Stage 1 may preserve useful dimensions/findings if they help explanation, but:
- no fixed factor ceilings;
- no fixed additive formula as final taste authority;
- no fake numerical precision;
- holistic/non-additive interactions from the user profile must be preserved.

#### Stage 2 — Comparative Calibration

Purpose: convert the approximate Stage-1 estimate into a ranking-authoritative score by comparing the game with already analyzed/calibrated games.

Example user intent:

- Game A receives provisional 78.
- Game B also receives provisional 78.
- Comparative calibration determines A is materially better for this user than B.
- It then compares A/B to nearby calibrated games and adjusts one or both placements/scores so that final scores match their true relative order.

Stage 2 must answer:

> "Relative to the games we already know, where does this game actually belong?"

The Stage-2 output is the **authoritative final taste score / ordering result**.

## Core semantic rule

The system should mirror the user's natural process:

1. first decide whether / how much the game seems appealing;
2. then inspect what specifically makes it better or worse than known neighboring games;
3. only then assign the precise final score/place.

The final number must be justified comparatively, not by arithmetic decomposition.

## Stage-2 evidence boundary

Stage 2 must NOT redo web research or invent new facts merely to force an ordering.

Its semantic evidence is:

- immutable Stage-1 findings for the target game;
- immutable accepted Stage-1 / calibrated findings for comparison games;
- current pinned user taste profile;
- exact GitHub-provided comparison window / anchors.

It may reason about relative importance and interactions, but it must not:
- erase a Stage-1 negative;
- invent a new positive;
- change factual Dossier evidence;
- reinterpret missing evidence as evidence;
- silently change fit/not-fit semantics just to obtain a score.

If Stage 2 discovers a genuine contradiction in Stage-1 inputs, it must emit a diagnostic requiring reanalysis rather than patching facts.

## Comparative calibration mechanics

GitHub must own which comparison items are supplied.

Do not let the semantic worker browse the entire catalog and self-select anchors.

Implement a bounded calibration strategy along these lines unless current architecture proves a safer equivalent:

1. GitHub maps the provisional Stage-1 score to a local calibrated neighborhood.
2. Supply a small set of already calibrated anchors immediately below / near / above the expected placement.
3. Stage 2 compares the target to those anchors and returns:
   - relative ordering;
   - whether the target is clearly above/below/effectively tied with each relevant anchor;
   - a proposed final calibrated score;
   - a concise comparative explanation.
4. If the target belongs outside the supplied window, GitHub—not the semantic worker—expands/moves the window and issues another bounded comparison step.
5. Stop once the target is bracketed and an internally consistent placement is established.

Do not compare every new game against hundreds of games in one prompt.

## Score/order invariants

Design and implement an explicit invariant so final numbers actually correspond to final ordering.

Requirements:

- if A is judged materially better fit than B, final calibrated ordering must place A above B;
- score direction must agree with ordering;
- exact ties are allowed only when the semantic conclusion is genuinely indistinguishable at the system's supported precision;
- deterministic non-semantic tie-breakers may order equal-score display rows but must not pretend one has a higher taste score;
- one- or two-point changes are allowed only when comparative calibration supports them;
- final score must stay within 0–100;
- do not arbitrarily renumber unrelated distant games every time one new result arrives.

Assess whether integer score precision remains sufficient. If the current top population cannot faithfully encode comparative order with integers, propose and implement the smallest safe representation change (for example bounded decimal precision or score+rank separation), but document the tradeoff and preserve human-readable 0–100 semantics.

## Fit / not-fit

Do not force every game onto a positive comparative ladder.

Stage 1 remains responsible for whether evidence supports fit / not-fit.

Stage 2 must support:
- calibrated fit results;
- authoritative not-fit results;
- diagnostics / insufficient evidence.

If not-fit games require relative ordering for product purposes, design a clear separate rule rather than pretending they are directly comparable by the same positive-fit scale without evidence.

## Ranking authority

After cutover:

- Stage-2 calibrated result is the highest semantic ranking authority.
- Stage-1 provisional score is never final-ranking authority.
- legacy Deep final scores must not outrank calibrated Stage-2 results merely because they existed earlier.
- items with completed Stage 1 but pending Stage 2 are "analyzed, awaiting calibration".
- items without Stage 1 are "not Deep-analyzed".
- deterministic provisional ordering may exist below calibrated authority, but must not masquerade as taste certainty.

Define an explicit rank precedence for:
1. Stage-2 calibrated fit;
2. Stage-1 analyzed but not yet calibrated;
3. not-yet-Deep-analyzed deterministic candidates;
4. authoritative not-fit / excluded outcomes,
while preserving any current product rule that should still apply.

Do not assume the exact precedence details if current canonical contracts reveal a conflict; document and resolve them in favor of this user-authorized architecture.

## Existing Deep results / migration

Do not discard valuable existing Dossier or Deep evidence.

Design a bounded migration plan for current authoritative Deep results.

Required analysis:
- which existing Deep outputs contain enough grounded findings to serve as Stage-1 inputs without semantic re-research;
- which legacy outputs are missing required explanation/findings and therefore need a fresh Stage-1 semantic pass;
- how the known 23 current fit results lacking score findings are handled;
- how to prevent a mix of legacy fixed-formula scores and new calibrated scores from producing misleading ordering.

Preferred migration:
- preserve existing factual findings when valid;
- remove legacy numeric score from final authority;
- run Stage 2 only after Stage-1-compatible evidence exists;
- quarantine/queue incomplete legacy items rather than inventing missing reasoning.

Do not execute mass semantic migration in this developer task unless an existing test-only/offline path is explicitly safe. Prepare the GitHub-owned work manifests/contracts for later semantic execution.

## Fast removal migration

Trace every current production consumer of Fast semantic output.

At minimum check:
- ranking;
- site/card display;
- explanations / why-fit;
- Deep eligibility / queue ordering;
- publication;
- fallback score logic;
- statistics;
- recovery/migration scripts.

Implement a clean cutover so no hidden Fast fallback remains.

Do not delete historical state before proving no migration/recovery dependency needs it.

Statistics should distinguish:
- Stage 1 complete;
- Stage 2 calibrated;
- awaiting calibration;
- not analyzed;
- not-fit;
- diagnostic/incomplete,
instead of presenting Fast as an equivalent analysis stage.

## Explainability

Final calibrated result must make the number understandable.

Required Stage-2 explanation shape should capture:

- why the target sits above specific lower anchor(s);
- why it sits below specific higher anchor(s), when applicable;
- which Stage-1 positives/negatives drive those relative judgments;
- why the final score changed from the provisional Stage-1 estimate, if it changed materially;
- uncertainty where neighboring placements are close.

Example conceptual output:

> provisional 78 -> calibrated 80 because its movement/gameplay hook is materially stronger than current 78–79 anchors, while its repetition risk keeps it below the 82 anchor.

Do not use canned generic phrases.

## Control-plane ownership

Preserve existing architecture:

- GitHub owns exact scope, manifests, ordering, comparison windows, iteration, retries, persistence, validation and completion.
- Semantic workers only evaluate exact GitHub-prepared items.
- A bad calibration item must not block unrelated items.
- No worker may self-expand calibration scope.
- No browser-side scoring.
- No second independent queue owner.

## Semantic worker shape

Implement repository contracts/prompts needed for:
- revised Stage-1 Deep semantic output;
- separate Stage-2 comparative calibration semantic output;
- GitHub-owned calibration work manifest / exact anchor window;
- validation and persistence;
- diagnostics / retry-safe handling.

Do NOT create, modify, schedule, enable, disable, pause, resume, or run any ChatGPT Scheduled Task in this task.

If a new recurring semantic worker would eventually be useful, implement only the repository-owned contract/runtime prompt/manual invocation path and report that scheduler configuration remains a separate user decision.

## Rollout safety

This is a major ranking architecture change.

Do not directly switch production ranking to partially migrated results.

Use a staged cutover:

1. implement contracts/schema/control plane;
2. deterministic/offline validation;
3. prepare migration manifests;
4. prove no Fast dependency remains in the proposed new authority path;
5. only enable production authority when the state is internally coherent.

If full production cutover requires semantic Stage-2 results that do not yet exist, stop with the new path implemented and migration ready rather than publishing a mixed misleading ranking.

## Validation

Required tests should cover at least:

- Stage-1 score cannot become final authority;
- fixed five-factor sum is not the final scoring authority;
- Stage-2 cannot introduce new factual evidence;
- GitHub selects anchors / semantic worker cannot self-expand;
- target above/below anchors produces monotonic final ordering;
- tie handling;
- window expansion;
- one bad calibration item isolated;
- duplicate/replay safety;
- stale anchor-set rejection;
- profile/binding drift rejection;
- legacy Deep migration classification;
- Fast result no longer affects production ranking;
- no hidden Fast fallback;
- existing Dossier evidence remains authoritative factual input;
- site/statistics cannot confuse provisional vs calibrated score.

Run relevant:
- Progressive PASS 2 / Deep core tests;
- ranking tests;
- publication/card explanation tests;
- execution ownership;
- backlog dispositions;
- any new calibration-specific tests.

## Report

Create:

`reviews/worker_reports/deep-two-stage-comparative-calibration-implement-01.md`

Report:

- exact old scoring/ranking architecture found;
- all Fast consumers found and disposition;
- final Stage-1 schema/semantics;
- final Stage-2 schema/semantics;
- comparison-window algorithm;
- score/order invariant;
- migration classification of existing Deep results;
- handling of the 23 missing score-findings cases;
- production cutover state;
- files changed;
- PR/checks;
- exact remaining semantic execution required, if any;
- exact user/Director next action.

Allowed final statuses:

- `implementation_complete_migration_ready`
- `implementation_complete_cutover_ready_after_semantic_calibration`
- `complete_production_cutover_validated`
- `needs_director_decision`
- `blocked`


## Director correction — preserve site 60/40 scoring model

This section supersedes any earlier wording in this task that described the Deep Stage-1 or Stage-2 score as the site's full 0–100 final score.

### Existing site scoring model must be preserved

Current canonical `config/final_ranking_policy.json` defines:

- total displayed score: **0–100**;
- personal / game-quality side: **maximum 60**;
- purchase/deal side: **maximum 40**.

The new two-stage Deep architecture must preserve that product/UI split.

Therefore:

`final_total_score_0_100 = calibrated_quality_score_0_60 + deterministic_purchase_score_0_40`

Deep semantic calibration owns only the **0–60 quality/personal-fit component**.

The deterministic purchase component remains GitHub-owned and must not be semantically adjusted by Stage 2 merely to move a game in the ranking.

### Stage 1 corrected score semantics

Stage 1 outputs:

- grounded positives/negatives/hooks/risks;
- fit/not-fit/confidence;
- **provisional_quality_score_0_60**.

This is an approximate holistic estimate of how strong the game is for this user.

It is not a final site score and not final ranking authority.

Example replacing the earlier 78/78 illustration:

- Game A provisional quality: 47/60;
- Game B provisional quality: 47/60.

### Stage 2 corrected score semantics

Stage 2 compares the target against already calibrated **quality anchors** and produces:

- relative quality ordering;
- **calibrated_quality_score_0_60**;
- comparative explanation.

Example:

- A and B both start at 47/60;
- comparative calibration determines A is clearly stronger than B;
- after checking nearby anchors:
  - A becomes 49/60;
  - B remains 47/60 or is moved to 46/60 if the comparative evidence supports it.

Only this calibrated **0–60 quality score** is authoritative for the personal/quality component.

### Purchase/deal 0–40 stays separate

The existing deterministic purchase/deal logic remains separate and transparent.

Stage 2 must not:
- raise quality because the discount is larger;
- lower quality because the price is worse;
- alter price/history/package value facts;
- use the purchase component to fabricate a taste distinction.

After calibration, GitHub combines:

- calibrated quality 0–60;
- deterministic purchase value 0–40;

into the final site total 0–100.

Therefore two games can have:
- A: quality 50/60 + deal 20/40 = total 70/100;
- B: quality 47/60 + deal 30/40 = total 77/100.

B may appear higher in the **deal-ranking feed** even though A is the better personal game fit. This is correct and must remain explainable.

The UI must not imply that Stage 2 semantically judged B to be the better game merely because B has the higher 100-point purchase-ranked total.

### Existing 60-point subcomponents

Current canonical 60-point personal side is internally composed from legacy fixed components (taste/wishlist/achievements/duration/risk).

The worker must explicitly audit these consumers.

Target architecture:
- the **final 0–60 personal/game-quality result must be holistic and Stage-2 calibrated**;
- the old fixed additive taste-factor arithmetic must not remain hidden final authority;
- wishlist, achievements, duration, risks and similar personal context may remain evidence/context inputs where useful, but must not be double-counted after the calibrated 0–60 score is authoritative.

If preserving any current deterministic subcomponent inside the 60-point side is necessary for product semantics, document exactly why and prove that it does not reintroduce a hidden additive formula conflicting with the user-authorized holistic calibration.

### Required site/UI changes

The implementation must inspect and update the actual site presentation, not only backend contracts.

After cutover the site must clearly distinguish:

1. **Stage 1 only / awaiting calibration**
   - no Fast label or Fast score;
   - may show `предварительная оценка X/60` if the product currently exposes an interim score;
   - must not present it as final quality or final calibrated authority.

2. **Stage 2 calibrated**
   - show final personal/game-quality value as **X/60**;
   - show deterministic purchase/deal value as **Y/40**;
   - show final combined score as **Z/100** where the current site uses the combined score;
   - explanation must make clear that X/60 comes from comparative Deep calibration and Y/40 from deal economics.

3. **Not yet Deep-analyzed**
   - no semantic quality score fabricated from Fast;
   - deterministic provisional ordering only.

4. **Authoritative not-fit**
   - retain current visibility/exclusion semantics; do not create a fake calibrated positive score.

### Site progress / Statistics

Remove Fast as a current equivalent semantic stage from user-facing progress/statistics.

Replace relevant progress concepts with at least:

- Deep Stage 1 complete;
- awaiting comparative calibration;
- Deep Stage 2 calibrated;
- not analyzed;
- not-fit;
- diagnostic/incomplete.

If the current UI has stage icons/status badges/Statistics tied to Fast/Dossier/Deep, update them so the new two-stage Deep model is understandable.

### Ranking interpretation

Stage 2 calibrates **quality position**, not commercial deal value.

The final site feed may still use the combined 100-point score after GitHub adds the 0–40 purchase component.

The worker must make both orderings explicit enough that the system never confuses:

- "better game for this user" = higher calibrated quality score /60;
- "better offer right now" = higher final combined score /100, subject to the canonical ranking-stage rules.

Do not force semantic quality numbers to compensate for price/discount merely to make final commercial ordering line up.

### Regression additions

Add tests proving:

- Stage-2 semantic output cannot exceed 60 quality points;
- purchase component remains capped at 40 and unchanged by Stage 2;
- final displayed total is the transparent sum of calibrated quality + deterministic purchase;
- no legacy Fast score fills the 60-point quality component;
- provisional Stage-1 score is visually/contractually distinct from calibrated Stage-2 score;
- site/card/Statistics labels no longer imply Fast is an equivalent analysis stage;
- a game with higher quality but lower deal score can legitimately have a lower combined 100-point total without corrupting its quality score.
