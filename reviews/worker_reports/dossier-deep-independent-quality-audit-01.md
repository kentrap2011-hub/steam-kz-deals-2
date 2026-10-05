# Dossier + Deep independent quality audit 01

Status: `audit_complete_systematic_quality_problems_found`

Task: `WORKER_TASK_DOSSIER_DEEP_INDEPENDENT_QUALITY_AUDIT_01.md`  
Mode: `READ-ONLY / INDEPENDENT AUDIT`  
Audited source of truth: `main` at `877933d7f4a3e9c9402dafcbc438697a7e971f6b`  
Audit date: 2026-10-06

## Executive verdict

The current Dossier + Deep pipeline is **substantively useful and much better than a schema-only system**, but it is not yet trustworthy as a precise numerical ranking engine.

The strongest part of the system is the evidence-to-verdict path:

- real Dossiers usually contain both meaningful positives and meaningful trade-offs;
- spot-checked claims were generally corroborated by the cited public surfaces;
- current Deep results usually consume the actual Dossier rather than ignoring inconvenient negatives;
- the current balanced-negative path is especially good: completed Deep results explicitly evaluate negative/mixed Dossier observations instead of producing only positive recommendation copy;
- `fit` / `not_fit` outcomes in the stratified sample were mostly believable and cross-game comparisons were usually directionally consistent.

The principal weakness is **score calibration, not basic semantic understanding**.

The current system requires exact evidence references for score-bearing findings, but it does not provide enough semantic calibration to explain why a factor is, for example, `92` instead of `86`. Those factor values are then combined by fixed weights (`18/12/8/8/4`) even though the current pinned taste profile explicitly says the user's evaluation is holistic and non-additive. The result is a score that looks more precise than the evidence and rules justify.

Therefore:

- **rough fit ranking / broad buckets:** trustworthy enough;
- **exact top-100 ordering by small score differences:** not trustworthy enough yet;
- **confident purchase recommendation:** trustworthy for strong, well-supported cases when reasons are read; not trustworthy from the numeric score alone, especially near a cutoff or for medium-confidence / thin-evidence cases.

This is why the final status is `audit_complete_systematic_quality_problems_found`, despite a generally good factual evidence layer.

## Overall score

**82 / 100**

This score describes the quality of the current semantic decision system as a whole, not contract validity.

## Nine component scores

| Dimension | Score | What 100/100 would require | Why points were lost | Defect type |
| --- | ---: | --- | --- | --- |
| Dossier completeness | **82** | Material gameplay/structure/progression/story/social/current-state dimensions covered when relevant, balanced positives/negatives, no material discoverable theme omitted, language/currentness attempts remain useful at purchase time. | Most sampled Dossiers were good, but several accepted broad/compact dossiers are thin; current language availability can outrun the frozen Dossier; some high-impact purchase-time currentness is only conditionally checked. | confirmed + judgment |
| Factual / evidence correctness | **88** | Every material claim reproducible from durable attributable evidence, with exact-product identity and independently re-auditable support. | Public spot-checks were strongly corroborative, but many `inspected_collection_item` records intentionally persist no stable child URL/public_ref or raw text, so an independent later auditor cannot always reproduce the exact support item. | rule-level auditability limitation |
| Balance / recurrence quality | **85** | Recurrence labels consistently proportional to materially independent evidence; strong themes not confused with anecdotes; source diversity reflects genuine independent support. | The sampled recurrence labeling was mostly sensible, but thresholds above anecdotal are intentionally qualitative and therefore not fully calibrated across games; some `moderate` rows rest on only two local records. | judgment + rule-level |
| Deep use of Dossier | **91** | Every completed Deep result evaluates all material favorable and unfavorable Dossier evidence and exposes the actual evidence-to-conclusion path. | New/current score-bearing results are strong here, but 23 current authoritative fit results still lack `score_findings`, so the evidence-to-number path is not uniform. | confirmed |
| Fit / not-fit correctness | **87** | Outcomes consistently plausible under the pinned profile; incomplete evidence never becomes negative; strong contrary evidence changes the verdict. | Sample verdicts were mostly good. A few moderate/high fits are debatable because meaningful profile-specific risks coexist with fairly high factors, but no sampled not-fit appeared to be merely “we lacked evidence.” | mostly judgment |
| Taste-score calibration | **62** | Stable semantic anchors for the 0–100 factor scale, meaningful uncertainty, comparable magnitudes across genres, holistic profile interactions preserved, small score differences defensible. | No adequate numeric anchor rubric; fixed additive weights conflict with the pinned holistic/non-additive preference rule; exact values carry false precision; not-fit results do not share the same numeric scale. | confirmed systematic rule-level problem |
| Explanation quality | **84** | The visible reasons are the exact reasons for the conclusion and score for every current result, with consistent positive and negative grounding. | Current `score_findings` are often excellent, but 23/135 current authoritative fit results (17.0%) still have no score findings; legacy explanation quality is therefore inconsistent. | confirmed |
| Cross-game consistency | **82** | Similar evidence and taste relationships produce comparable score differences and confidence; genre differences are handled by profile evidence rather than arbitrary numeric drift. | Broad ordering is good, but close numeric differences are not defensible from the current calibration rules; several factors absorb concepts outside their natural meaning. | confirmed + judgment |
| Overall usefulness | **80** | A user can safely use the output for exact purchase ordering without re-reading raw evidence except for unusual cases. | Strong for shortlist triage and reason-based evaluation; weaker for exact top-100 cutoff/order and medium-confidence purchasing because the score overstates precision. | product-level judgment |

## Canonical state at audit close

### Dossier

Current Dossier snapshot:

- snapshot: `a9a1390c7821fcc69c06f83e57c0297df0016e0d90e637ddccd7185d53bd8b19`;
- accepted groups: **22**;
- accepted Dossiers: **66**;
- failed groups: **0**;
- pending groups: **109**;
- pending Dossiers: **325**;
- current next pending sequence: **21**.

The previous retryable-transport blocker fixed by PR #153 was treated as closed context and was not re-diagnosed.

### Deep

Current Progressive Deep scope:

- current coverage target: **527**;
- first-pass attempted: **190**;
- authoritative completed: **159**;
- authoritative fit: **135**;
- authoritative not-fit: **24**;
- incomplete/recovery: **31**;
- waiting for Dossier: **325**;
- ready/pending normal Deep work: **12**.

Among current authoritative fit results:

- with non-empty `score_findings`: **112 / 135**;
- without `score_findings`: **23 / 135 = 17.0%**.

For audit comparison only, the stored five Deep factors were converted to an equivalent 0–100 taste scale using the current production ranking weights:

`(gameplay_mastery*18 + development_variety*12 + structure_pacing_direction*8 + identity_hooks*8 + breadth_of_match*4) / 50`

Current authoritative fit distribution on that equivalent scale:

- minimum: **52.9**;
- Q1: **68.9**;
- median: **76.8**;
- Q3: **84.8**;
- maximum: **92.4**.

This normalization is an audit convenience. The underlying production values remain the five stored 0–100 factors plus the current final-ranking policy.

## Sampling methodology

I used a stratified sample of **22 current authoritative Deep results**, paired with **22 exact accepted Dossiers**. That exceeds both task minimums (12 Dossiers, 20 Deep results).

For each Deep item, the Dossier was read from the exact Deep `work_authority_commit` when available rather than silently substituting the latest cache bytes.

Selection covered:

- `analyzed_fit` and `analyzed_not_fit`;
- strong / moderate fit;
- high / medium confidence;
- top / middle / bottom of the current fit-score range;
- recent results and older still-current results;
- normal first pass, recovery, legacy reanalysis, and score-explainability migration;
- large and small review populations;
- action / movement / shooter / metroidvania / puzzle / hidden-object / party / management / narrative-FMV / multiplayer cases;
- cases whose correct answer is reasonably debatable.

## Exact sample

| AppID | Title | Deep outcome | Fit/confidence | Audit taste 0–100 | Why sampled |
| --- | --- | --- | --- | ---: | --- |
| 1836730 | Echo Point Nova | fit | strong / high | **92.4** | top score; movement/mastery |
| 1237970 | Titanfall 2 | fit | strong / high | **91.6** | top score; older still-current; no score_findings |
| 1229490 | ULTRAKILL | fit | strong / medium | **91.5** | top score; mastery / high skill |
| 1369630 | ENDER LILIES: Quietus of the Knights | fit | strong / high | **90.3** | migrated score; compact evidence |
| 1928690 | Bionic Bay | fit | strong / high | **90.4** | movement; lower review population |
| 1282100 | REMNANT II | fit | strong / medium | **89.4** | rich current evidence; many negatives |
| 2100 | Dark Messiah of Might & Magic | fit | strong / high | **89.5** | old title; current compatibility |
| 1590910 | Forgive Me Father | fit | strong / medium | **86.2** | strong loop + late-campaign risks |
| 1586800 | Lil Gator Game | fit | moderate / medium | **75.9** | low challenge; movement / emotion |
| 1467920 | A Guidebook of Babel | fit | moderate / medium | **78.2** | directionlessness risk; Russian-coverage check |
| 1509510 | Settlement Survival | fit | moderate / medium | **76.2** | management depth vs micromanagement |
| 1608230 | Planet of Lana | fit | moderate / medium | **68.9** | beauty vs repetitive/simple loop |
| 1085510 | Garfield Kart - Furious Racing | fit | moderate / medium | **57.8** | social karting; legacy reanalysis |
| 1969080 | A Building Full of Cats | fit | moderate / high | **52.9** | minimum current fit score; compact game |
| 1206610 | Rubber Bandits | fit | moderate / medium | **54.3** | social value vs shallow repetition |
| 2366980 | Thank Goodness You're Here! | fit | moderate / medium | **55.6** | identity-heavy / minimal gameplay |
| 1353270 | Five Dates | not-fit | high | — | confirmed personal negative |
| 1158940 | Blazing Sails | not-fit | high | — | multiplayer population dependency |
| 1629520 | A Little to the Left | not-fit | high | — | confirmed personal negative / puzzle logic |
| 1577120 | The Quarry | not-fit | medium | — | narrative / low active gameplay |
| 1002560 | Tiny Snow | not-fit | medium | — | sparse route-exhausted evidence |
| 1593780 | Organs Please | not-fit | medium | — | management depth vs repetitive overload |

Review-population diversity was also checked from current canonical candidate context. Examples range from `Organs Please` (~334 global reviews) and `Bionic Bay` (~924) through `Titanfall 2` (~286k).

## What was done well

### 1. REMNANT II: unusually complete neutral Dossier

Artifact:

- Dossier: `data/cache/taste_steam_review_dossiers/App_1282100.json` at the Deep frozen authority;
- Deep: current authoritative `game:1282100`.

The Dossier contains eight substantive observations and ten feedback records across Steam and Reddit, including:

- build/gunplay strengths;
- procedural exploration and reroll friction;
- item/progression farming;
- boss-design trade-offs;
- co-op vs solo differences;
- story/art split;
- current 2026 stutter/frame-drop reports;
- current co-op communication friction.

Deep did **not** discard those negatives. Its balanced-negative assessment evaluated six negative/mixed issues while still concluding strong fit. This is exactly what the two-stage architecture is supposed to achieve.

External spot-check also corroborated the current no-communication/co-op friction: a 2026 Remnant community thread repeatedly discusses the lack of text/voice communication and public-lobby friction.

### 2. Planet of Lana: Dossier captures the central trade-off, not only the praise

Artifact:

- `data/cache/taste_steam_review_dossiers/App_1608230.json`.

Dossier correctly captures:

- strong art/music/landscape identity;
- companion-puzzle interaction;
- simple approachable puzzle flow;
- a material recurring complaint that mechanics stop evolving and become repetitive.

Deep then turns that exact repetition observation into a confirmed personal `unchanged_repetition` risk and lowers `development_variety`.

Independent current Steam pages show both sides: praise for the art/simplicity and explicit complaints that the loop is repetitive, simple, and reveals most of its ideas early.

This is a strong example of semantic balance.

### 3. Forgive Me Father: negative late-game structure is preserved despite a strong fit

Artifact:

- `data/cache/taste_steam_review_dossiers/App_1590910.json`;
- Deep current authoritative result.

Dossier identifies the fast FPS loop, upgrade progression, challenge, visual identity, and also:

- dark/confusing later layouts;
- late-game durability/arena frustration;
- the final act as rushed/padded/weaker.

Deep keeps the game strong-fit because the active FPS/mastery loop and art identity strongly match the profile, but it lowers structure/pacing and surfaces late-game risks.

Independent Steam review material explicitly corroborates the weak final act, progression slowdown and later-level readability complaints.

### 4. Blazing Sails: not-fit is based on access to the core loop, not genre prejudice

Artifact:

- `data/cache/taste_steam_review_dossiers/App_1158940.json`;
- Deep recovery result `analyzed_not_fit`, basis `confirmed_personal_negative`.

Dossier positively describes crew coordination, roles, looting, boarding and ship combat. Deep does not call the mechanics bad. It rejects the practical fit because the strongest mechanics depend on populated coordinated multiplayer and current feedback reports difficulty finding enough players.

This is independently plausible: public SteamCharts data around September 2026 shows only tens of average concurrent players.

This is good use of current-state evidence in a purchase-oriented system.

### 5. A Little to the Left: not-fit maps a Dossier complaint to an exact user preference

Artifact:

- `data/cache/taste_steam_review_dossiers/App_1629520.json`.

Dossier records:

- satisfying/calming sorting for players who like the format;
- under-explained or arbitrary rules;
- exact-position friction;
- repetitive Daily Tidy completion;
- hint-system limitations.

Deep does not merely say “puzzle game = bad”. It links opaque logic and precision friction to the pinned profile's dislike of lostness/unclear intended action and links repetition to the user's repetition sensitivity.

Public Reddit discussions independently contain the same two complaints: difficulty inferring some puzzle logic and correct conceptual solutions failing because placement is too exact.

### 6. Cross-game movement/mastery cluster is directionally coherent

Equivalent audit scores:

- Echo Point Nova — 92.4;
- Titanfall 2 — 91.6;
- ULTRAKILL — 91.5;
- Bionic Bay — 90.4.

All four have concrete evidence of movement / mechanical execution / skill expression and are matched to one of the strongest pinned user signals. Their relative closeness is itself reasonable.

The problem is not that this cluster is high; the problem is that the system cannot defend the exact one-point ordering inside the cluster.

### 7. Social-game distinction is useful

- Rubber Bandits: moderate fit, 54.3 equivalent score; social play helps, but mechanics are shallow and novelty fades.
- Blazing Sails: not-fit; the deeper coordinated multiplayer loop is appealing, but current population makes access unreliable.

This is a sensible distinction between “social play is a plus” and “the product requires a population state that may not exist.”

## Concrete weaknesses / errors

### Serious issue S1 — exact numeric score magnitude is not calibrated enough

**Classification: recurring systematic / rule-level.**

Relevant artifacts:

- `config/progressive_pass2_worker_prompt.md`;
- `config/progressive_pass2_result_schema.json`;
- `config/final_ranking_policy.json`;
- pinned profile `gaming_taste_live.json` at commit `f8e8ebffbf0f6a93ca04f727a707e88a633fde8d`.

What is good:

- current Deep score findings must cite exact Dossier evidence;
- they must cite exact pinned-profile evidence;
- all five factors must be covered;
- generic score filler is forbidden.

What is missing:

- there is no strong semantic rubric explaining what distinguishes `60`, `75`, `86`, `92`, or `98`;
- schema only enforces `0 <= normalized_value <= 100`;
- evidence grounding proves that a factor matters, but not the exact magnitude.

Concrete consequence:

- Echo Point Nova = 92.4;
- Titanfall 2 = 91.6;
- ULTRAKILL = 91.5;
- Bionic Bay = 90.4.

A reasonable auditor can defend “all are very strong fits”. The current artifacts do **not** provide enough calibration authority to defend the exact 0.1–2 point ordering.

This is false precision.

### Serious issue S2 — fixed additive scoring conflicts with the current pinned taste model

**Classification: systematic rule-level contradiction.**

Current final taste weighting:

- gameplay/mastery: 18;
- development/variety: 12;
- structure/pacing/direction: 8;
- identity/hooks: 8;
- breadth: 4.

Current pinned profile contains `contextual_preferences.holistic_non_additive_evaluation`, explicitly stating that the user evaluates games holistically and that a final rating should not be mechanically derived as a simple sum of independent components.

The current production ranking nevertheless mechanically converts the five factors into a fixed weighted taste component.

This does not make every result wrong. It does mean the **score architecture cannot fully represent its own current profile semantics**.

A visible symptom is factor overloading:

- Rubber Bandits' social/shared value is mapped into `structure_pacing_direction`, `identity_hooks`, and `breadth_of_match` because there is no direct social-role factor.
- Other newer profile dimensions (play role, start burden, long-campaign fatigue, active-loop filler, skill-stat transparency) must also be compressed into the same five factors.

The score can therefore be directionally useful while semantically lossy.

### Serious issue S3 — 17% of current authoritative fit results still lack score findings

**Classification: systematic historical-compatibility weakness.**

Current count:

- authoritative fit: 135;
- with score findings: 112;
- without score findings: **23 (17.0%)**.

Concrete example:

- state key: `game:1237970` — Titanfall 2;
- work id: `fb64b337169badf0905a2d55fde7b8c6e597b540b21dde4f08c8d9a77dea0a79`;
- frozen Dossier commit: `3d4915a2da67a3643f9a23c4a433b755ed2b07c0`;
- Dossier content SHA256: `735b78c9ae8839024696f6d1da346cd5e18412c4c0c2cfb7cc9a29a05b844e7a`;
- result: strong/high, equivalent audit score 91.6;
- `score_findings=[]`.

The result has sensible `positive_evidence` and negative assessment, but a score near the top of the ranking lacks the same explicit evidence-to-factor explanation required of newer items.

This creates two quality classes inside one current authoritative population.

### Serious issue S4 — Dossier provenance is valid but not always durably independently auditable

**Classification: systematic rule-level auditability limitation.**

The current evidence contract intentionally allows `inspected_collection_item` and other observed-feedback records without a stable child URL/public_ref, and raw review bodies are intentionally not persisted.

That is defensible for compactness/privacy, but it creates an independent-audit cost:

- the Dossier can say `feedback-002` supports an observation;
- `feedback-002` can point only to a changing Steam collection parent;
- later auditors cannot always retrieve the exact original review/card again.

Concrete example: `A Guidebook of Babel` Dossier at frozen commit `3e38cba20a88870e945850b22b3f55e11b58de99` has five feedback records, all without stable child URL/public_ref.

Independent spot-checking of the Steam collection corroborated the Dossier's main themes (getting stuck on small missed interactions, excessive guidance yet opaque triggers, dialogue/text pacing), but the artifact itself does not preserve enough information to reproduce every exact support item.

This reduces **auditability**, not necessarily factual correctness.

### Serious issue S5 — Russian-language attempt can become stale relative to the current purchase context

**Classification: confirmed current-state mismatch; original-research error not proven.**

Artifact:

- AppID 1467920 — A Guidebook of Babel;
- Deep state key: `game:1467920`;
- work id: `724d7f63494dcee88aa6e433229bba256e50d539ae8c6469fa0ab6c94740cec3`;
- frozen Dossier commit: `3e38cba20a88870e945850b22b3f55e11b58de99`;
- Dossier SHA256: `79a24bc8fdf300f654aa7f65545f07bb76a28eb4946199cbc5b502553d1cf58d`.

Frozen Dossier:

- `russian_attempt = searched_no_existence_signal`;
- all five persisted player-feedback records are non-Russian.

Current canonical candidate context now reports:

- global reviews: 1801;
- Russian reviews: **5**;
- Russian positive: 80%.

This proves the Dossier's Russian-language status is no longer an adequate description of the current purchase context.

Because the current candidate context may have been refreshed after the Dossier was generated, this audit does **not** claim the original search definitely failed at generation time. The product weakness is that accepted Dossier language-coverage state can become stale while the Dossier remains current enough for Deep/ranking.

### Weakness W6 — qualitative recurrence is sensible but not sufficiently cross-game calibrated

**Classification: rule-level + judgment.**

The evidence contract correctly forbids turning aggregate counts into mentions and correctly says one item can only be anecdotal.

Above one item, however, `limited / moderate / strong` are deliberately qualitative.

The sample mostly behaves sensibly:

- REMNANT II strong themes use four materially distinct support records;
- several moderate themes use three;
- some moderate themes use two materially independent records.

No obvious duplicate inflation was found.

Still, the same qualitative label can represent substantially different breadth. That matters because `overall_strength=moderate/strong` is partly derived from these labels, and Deep confidence can appear stronger than the actual evidence breadth suggests.

### Weakness W7 — some high-confidence outputs have relatively compact evidence bases

**Classification: judgment, not proven contract defect.**

Example: ENDER LILIES is strong/high at an equivalent 90.3, but its frozen Dossier contains four feedback records and no recent dated record.

For durable single-player mechanics this is not automatically wrong; recency is not always needed.

However, `confidence=high` currently does not communicate whether confidence comes from:

- broad independent evidence;
- a simple/stable central experience;
- strong profile match despite narrow sampling.

That makes confidence less interpretable across games.

### Weakness W8 — score effects are grounded but magnitude direction is not mechanically interpretable

**Classification: rule-level.**

In a score finding, `effect` can be `supports / lowers / qualifies`, but `normalized_value` simply echoes the final factor value.

Example: A Guidebook of Babel:

- directionlessness is a confirmed personal risk;
- `structure_pacing_direction=66`;
- the same factor value is attached to both lowering/qualifying findings;
- the artifact proves the reason for caution, but not how much that caution should numerically reduce the factor.

Thus score findings explain semantics better than they explain arithmetic.

### Weakness W9 — numeric comparability stops at not-fit

**Classification: product-model limitation.**

Current not-fit results correctly carry reason/basis/confidence, but do not share the same five factor values / 0–100 taste axis as fits.

This is acceptable if not-fit is a hard semantic exclusion.

It reduces usefulness for:

- comparing borderline low-fit vs not-fit games;
- calibrating the fit threshold;
- auditing whether a 52.9 fit and a completed-below-threshold result are actually separated by a meaningful difference.

### Weakness W10 — Dossier source breadth is good enough for semantics but not a census

**Classification: expected limitation, not defect by itself.**

The sample frequently uses 4–10 compact player-feedback records even for games with thousands or hundreds of thousands of Steam reviews.

The contract explicitly avoids fixed review quotas, which is correct.

The audit found no evidence that raw popularity is being treated as semantic truth, which is good.

But for highly polarized games, compact sampling can miss a material minority theme. The correct target should remain semantic coverage, not a fixed sample count.

## External public-evidence spot checks

These were used only to verify disputed/important themes, not as a replacement corpus.

### A Guidebook of Babel

Steam current/top-rated review surface corroborates:

- missed small interactions can block progression;
- overbearing tutorial can coexist with getting stuck;
- dialogue/text-heavy pacing can become tedious;
- attractive art/world can coexist with weak writing or frustrating puzzle flow.

Public references:

- https://steamcommunity.com/app/1467920/reviews/?browsefilter=toprated
- https://store.steampowered.com/app/1467920/

### Planet of Lana

Current Steam reviews corroborate both:

- art/music/simplicity praise;
- complaints of repetition, simplicity, and mechanics revealing most of their ideas early.

Reference:

- https://steamcommunity.com/app/1608230/reviews/

### Forgive Me Father

Steam review/discussion material corroborates:

- strong old-school FPS core and variety;
- late-level navigation/readability issues;
- final act/Act 5 being rushed or weaker;
- progression slowing late.

References:

- https://steamcommunity.com/app/1590910/reviews/?browsefilter=toprated
- https://steamcommunity.com/app/1590910/discussions/0/3717188244455606146/

### A Little to the Left

Public Reddit discussion corroborates:

- some puzzle rules feeling unintuitive;
- frustration when conceptually correct placement is not accepted until an exact spot is found.

References:

- https://www.reddit.com/r/CozyGamers/comments/1bnh31k
- https://www.reddit.com/r/CozyGamers/comments/1bxj35m

### Organs Please

Steam review material corroborates:

- confusing/opaque UI;
- management hassle;
- repetition;
- the management layer diluting rather than automatically deepening the Papers-Please-like premise.

Reference:

- https://steamcommunity.com/app/1593780/reviews/?browsefilter=toprated&l=english

### Blazing Sails

SteamCharts around September 2026 shows a low concurrent population (tens of average players), supporting the Dossier/Deep concern that a population-dependent PvP loop is not reliably accessible.

Reference:

- https://steamcharts.com/app/1158940

### REMNANT II

A current Reddit thread corroborates public-lobby friction and the lack of native communication.

Reference:

- https://www.reddit.com/r/remnantgame/comments/1v00hoj/i_tried_to_coop_for_4_hours_meaning_i_was_sent/

### Thank Goodness You're Here!

Current Steam reviews corroborate the exact trade-off used by Deep:

- excellent art/voice/humor;
- very short duration;
- intentionally minimal mechanical depth.

Reference:

- https://steamcommunity.com/app/2366980

## Product questions — direct answers

### 1. Does Dossier capture important recurring positives and negatives?

**Usually yes.**

The stronger Dossiers are genuinely neutral evidence packages, not recommendation copy. REMNANT II, Dark Messiah, Planet of Lana, Forgive Me Father and The Quarry all preserve material trade-offs.

Weakness: compact acceptance can still miss breadth, and language/current-state coverage can age while the artifact remains accepted.

### 2. Are review claims actually supported?

**Spot-check result: generally yes.**

The public checks reproduced the core disputed themes.

The limitation is durable reproducibility: many persisted feedback records have no stable child locator, so support is not always re-openable later from the artifact alone.

### 3. Does Dossier distinguish recurring patterns from anecdotes strongly enough?

**Mostly, but recurrence calibration is soft.**

One record is correctly constrained to anecdotal. Multiple records can produce stronger labels. No obvious duplicate inflation was found.

Above anecdotal, qualitative thresholds remain worker judgment.

### 4. Is source coverage broad enough?

**Broad enough for many semantic decisions; not uniformly broad enough for durable purchase confidence.**

Good:

- Steam plus Reddit / other player-feedback sources;
- Russian attempts;
- current technical/multiplayer evidence where material.

Weak:

- some accepted Dossiers remain compact;
- Russian/current-state availability can change after generation;
- some “multi-source” evidence still represents a small observed sample.

### 5. Does Deep use Dossier faithfully?

**Yes, strongly in current results.**

The balanced-negative requirement is working. In the sample Deep usually evaluated all negative/mixed Dossier rows.

This is one of the best parts of the current architecture.

### 6. Are fit/not-fit outcomes believable?

**Mostly yes.**

No sampled not-fit looked like a disguised “insufficient evidence” outcome.

Good distinctions include:

- movement/mastery cluster high-fit;
- Blazing Sails rejected for current multiplayer access, not because social play is bad;
- Five Dates / The Quarry penalized consistently for low-active narrative structure;
- A Little to the Left rejected for profile-specific opaque/repetitive puzzle friction.

### 7. Is the 0–100 taste score calibrated?

**No — not to the precision implied by the numbers.**

The scale is useful as a broad band, but exact values are under-calibrated.

The current system can responsibly say:

- ~90 cluster = very strong match;
- ~50–60 cluster = weak/moderate match.

It cannot responsibly claim, from current rules alone, that 91.6 is meaningfully better than 90.4.

### 8. Are pluses/minuses the real reasons?

**For new score-bearing results, usually yes.**

Current score findings are candidate-specific, profile-specific, and bound to exact Dossier evidence.

Legacy current fits without score findings remain a material exception.

### 9. Are similar games treated consistently?

**Broadly yes; exact point differences no.**

Good broad consistency:

- movement/mastery high cluster;
- low-mechanics/identity games lower;
- social games depend on whether the social loop is practically accessible;
- low-active narrative games face a high story-quality bar.

Main inconsistency is numerical precision, not categorical direction.

### 10. Confident scores despite weak/incomplete evidence?

**Some concern, but no catastrophic example in the sample.**

High confidence can appear with compact Dossiers when the central experience is stable. That may be valid, but confidence does not communicate evidence breadth clearly.

### 11. Enough information for final ranking / purchase?

**For rough ranking: yes. For exact ordering: no. For purchase: conditionally.**

A user can make a good purchase decision when reading:

- outcome;
- concrete positive findings;
- negative assessment;
- current technical/population cautions.

The numeric score alone should not be treated as a precise purchase probability or exact rank.

### 12. What is systematically missing?

Most important:

1. calibrated numerical anchors for the Deep factors / taste score;
2. a way to preserve holistic/non-additive profile interactions in the final score;
3. uniform score-findings coverage for all current authoritative fits;
4. durable auditability for locatorless observed-feedback support;
5. explicit freshness reconciliation between accepted Dossier language/current-state coverage and newer canonical store/review context;
6. clearer confidence semantics separating semantic certainty from evidence breadth.

### 13. Do any validation rules reduce semantic usefulness?

**Yes.**

The main example is not a strict validator being “too strict”; it is the combination of:

- very good exact evidence-binding validation;
- no equally strong numeric calibration semantics.

The system can prove that a reason is grounded while still being unable to prove that its score magnitude is well calibrated.

Also, the compact provenance model improves privacy/robust transport but reduces later independent auditability because raw text and stable child locators are often absent.

## Isolated vs systematic vs rule-level

### Isolated / local issues

- Current A Guidebook of Babel canonical context now exposes Russian review availability while its accepted Dossier still says `searched_no_existence_signal`. This is a concrete current mismatch; the audit cannot prove the signal already existed at original Dossier generation.

### Recurring systematic weaknesses

- 23 current authoritative fit results lack score findings.
- Confidence does not clearly encode evidence breadth.
- Exact score ordering is more precise than the evidence calibration.

### Rule-level limitations

- No sufficient numeric anchor rubric for 0–100 factor magnitudes.
- Fixed additive taste weights conflict with the pinned profile's explicit holistic/non-additive rule.
- Five-factor compression overloads factors with social/play-role/context signals.
- Locatorless compact provenance limits later independent reproduction of exact support.
- Not-fit results are not numerically comparable on the same taste scale.

## Trust assessment

### Rough ranking

**YES — trustworthy enough.**

Strong / moderate / not-fit separation and major relative differences are useful.

Suggested trust level: **high-moderate**.

### Exact top-100 ordering

**NO — not trustworthy enough as an exact ordinal list when differences are small.**

Use broad score bands / reason quality, not one-point ordering.

A practical current interpretation would be to treat close scores as ties rather than real ordering evidence.

### Confident purchase recommendation

**CONDITIONAL.**

Confident when:

- Dossier is rich/current for material concerns;
- Deep is high/medium confidence with grounded findings;
- negative assessment contains no unresolved purchase-critical concern;
- current multiplayer/technical dependencies are checked.

Not confident from the numeric score alone.

## Ranked improvement plan

No implementation is authorized or performed by this audit.

### 1. [Deep] Add real calibration semantics for factor values and the overall taste score

**Expected impact: very high.**

Define semantic anchor bands / calibration examples that make values meaningfully comparable across games.

The target should be to justify magnitude, not only evidence relevance.

Avoid pretending that 1–2 point differences are meaningful without such calibration.

### 2. [Deep] Align score aggregation with the pinned profile's holistic / non-additive rule

**Expected impact: very high.**

The current five fixed weights should not be the only authority for a user profile that explicitly says interactions matter.

Possible future design should preserve:

- decisive positive hooks;
- decisive deal-breakers;
- context-dependent compensation;
- play role;
- social/shared value;
- fatigue/start burden;
- interactions between factors.

This is a contract/design task, not an implementation action in this audit.

### 3. [no semantic-worker change required] Stop using tiny score deltas as decisive ordering evidence

**Expected impact: high, low semantic risk.**

Before changing Deep semantics, final ranking can treat nearby taste values as tied/banded rather than exact.

This does not require a new semantic worker; it would be a later deterministic ranking-policy task.

### 4. [no semantic-worker change required] Bring the 23 current fit results without score findings onto a uniform explainability standard

**Expected impact: high.**

The existing score-explainability architecture already exists. The quality goal is one explanation standard for all current authoritative fits.

This is not executed here.

### 5. [Dossier] Add freshness reconciliation for language/current-state evidence

**Expected impact: medium-high.**

When newer canonical context proves a materially relevant feedback surface now exists (for example Russian reviews or multiplayer/technical state), the system should know the accepted Dossier's evidence-coverage statement is older than current purchase context.

This should not become a broad refresh loop; only materially relevant freshness drift should matter.

### 6. [Dossier] Improve durable auditability without storing raw review bodies

**Expected impact: medium.**

Preserve a privacy-safe, stable evidence identity where possible:

- stable child URL/public_ref when available;
- otherwise a deterministic safe collection-item fingerprint or equivalent immutable audit token.

Goal: later independent auditors can establish that a specific persisted support item existed, without persisting raw review text or author identity.

### 7. [Deep] Make confidence semantics explicit

**Expected impact: medium.**

Separate at least conceptually:

- confidence in the semantic conclusion;
- breadth/robustness of the Dossier evidence;
- uncertainty in exact score magnitude.

A high-confidence fit from a compact but stable game can then be distinguished from a high-confidence conclusion backed by broad current multi-source evidence.

### 8. [Dossier] Keep semantic boundedness; do not replace it with fixed review quotas

**Expected impact: protective.**

The audit does **not** recommend “always read N reviews”.

The current no-fixed-quota principle is good. Improve material coverage and auditability, not brute-force count.

## Final conclusion

The pipeline's factual semantic core is **good enough to preserve and build on**.

The audit did **not** find evidence that Dossier routinely invents review themes or that Deep routinely ignores Dossier negatives. In fact, several sampled results are impressively well-grounded.

The systematic problem is narrower but product-critical: **the system currently turns good qualitative reasoning into a numerical score with more precision and additivity than its own evidence and current user profile justify**.

Until score calibration / aggregation is corrected or ranking explicitly treats close scores as tied bands:

- trust the reasons;
- trust broad fit bands;
- trust major not-fit conclusions with good evidence;
- do not trust one- or two-point taste differences as precise top-100 ordering authority.

Final status: `audit_complete_systematic_quality_problems_found`
