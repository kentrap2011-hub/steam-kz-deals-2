# Personal taste scoring targeted offline backtest 02 — pre-registration

Experiment: `personal-taste-scoring-targeted-offline-backtest-02`
Pre-registration version: `v1`
Selection seed: `personal-taste-scoring-targeted-offline-backtest-02-final-v2`

## Frozen sources
- Source profile: `kentrap2011-hub/stopgame-ratings-data/gaming_taste_live.json` blob `9b9926031889dbd98ba6585c57836d52c739a0bb`.
- Backtest 01 split: `experiments/personal_taste_scoring/backtest_01/frozen_split_manifest_v4.json` blob `dfeac6173545eb6aa22162ffd14135c5c9e1ab77`.
- Backtest 01 public candidate evidence: `experiments/personal_taste_scoring/backtest_01/candidate_evidence_v4.json` blob `92730d68fc49fcf90d9520d84aade03ecb3c9cfa`.
- Baseline policy blob: `f472b74ef36abb15ac8bbdd1a21d8eac802c130c`.
- Baseline implementation blob: `317bd06d4b5f45540816a952bd553e4476e0dd6b`.
- Deep worker semantics reference blob: `df5ac13d2cf47f42a5ec24aaec7e786f226c33a6`.
- Experiment base main commit: `94bec36a02513a4cb319cbbdd45d3c6f42a3bcd5`.

## Frozen split
Family assignment is truth-derived only for hard-case sampling and MUST remain hidden from the evaluator until blind predictions and stability reruns are frozen.

| Blind ID | Game | Family |
|---|---|---|
| B01 | Tekken 3 | family_2_conventionally_flawed_personally_memorable |
| B02 | Cyberpunk 2077 | family_1_externally_strong_personally_underwhelming |
| B03 | Prototype | family_1_externally_strong_personally_underwhelming |
| B04 | Perfect World | family_2_conventionally_flawed_personally_memorable |
| B05 | The Suffering | family_2_conventionally_flawed_personally_memorable |
| B06 | The Witcher 3: Wild Hunt - Blood and Wine | family_2_conventionally_flawed_personally_memorable |
| B07 | Prince of Persia: Warrior Within | family_2_conventionally_flawed_personally_memorable |
| B08 | Sanitarium | family_2_conventionally_flawed_personally_memorable |
| B09 | Grand Theft Auto III | family_1_externally_strong_personally_underwhelming |
| B10 | The Banner Saga 2 | family_1_externally_strong_personally_underwhelming |
| B11 | Resident Evil 4 | family_1_externally_strong_personally_underwhelming |
| B12 | The Elder Scrolls IV: Oblivion | family_1_externally_strong_personally_underwhelming |
| B13 | Marvel's Spider-Man | family_2_conventionally_flawed_personally_memorable |
| B14 | Borderlands | family_1_externally_strong_personally_underwhelming |
| B15 | Mafia II | family_1_externally_strong_personally_underwhelming |
| B16 | WarCraft 3: The Frozen Throne | family_2_conventionally_flawed_personally_memorable |
| B17 | The Witcher 3: Wild Hunt - Hearts of Stone | family_2_conventionally_flawed_personally_memorable |
| B18 | Red Dead Redemption | family_1_externally_strong_personally_underwhelming |
| B19 | Hogwarts Legacy | family_1_externally_strong_personally_underwhelming |
| B20 | Need for Speed: Most Wanted | family_2_conventionally_flawed_personally_memorable |

Balance: exactly 10 Family 1 / 10 Family 2.

### Deterministic selection
1. Start from backtest-01 final blind-v4 held-outs only.
2. Exclude titles whose direct truth/direction was explicitly disclosed by the backtest-01 report: Mirror's Edge, Castlevania: Lords of Shadow, Mass Effect, Grand Theft Auto V, Postal 2, Assassin's Creed, Half-Life: Blue Shift, Lucius II, The Exit 8.
3. Family 1 eligibility: direct rating <=3.5 plus at least one direct dislike or predeclared strong-negative token. This covers low or middling/underwhelming cases.
4. Family 2 eligibility: direct rating >=3.5, at least one direct like, plus a conventional weakness evidenced either by direct dislike, public candidate-fact weakness token, or a separate contextual remark. No requirement is imposed that the weakness lowered the user's rating.
5. Eligible cases receive deterministic family-strength scores from rating distance + frozen token counts. Choose the maximum-total non-overlapping 10/10 assignment; FNV-1a seed resolves ties. Predictions play no role.

Frozen strong-negative tokens:
`скуч, неинтерес, не зацеп, брос, хуже, непонят, однообраз, повтор, затянут, управлен, финал, концов, разочар, рутин, слаб`.

Frozen public conventional-weakness tokens:
`repet, dated, rough, simple, limited, short, technical, clunky, linear, shallow, old, weak, filler, grind, same, uneven, friction, bugs`.

## Leakage audit / fail-closed history
- Backtest 01 preliminary contaminated splits remain forbidden; only final blind-v4 inputs may be reused.
- Attempt 02-A was rejected before scoring because family direction leaked through sequential family-coded IDs.
- Attempt 02-B was rejected before scoring because inspection of the old training deck exposed direct truth for fresh candidate titles.
- Every title from both rejected attempts is therefore barred from the final held-out set.
- Final strategy intentionally accepts 20/20 title overlap with backtest-01 blind-v4 held-outs to preserve genuine current blindness. Prior backtest predictions/results for these titles are forbidden evaluator evidence and must not be opened before unblinding.
- The old blind-v4 90-card training input had zero exact/alias held-out references and remains the only allowed personal-history deck.
- Global derived `taste_profile` and `contextual_preferences` remain withheld.
- Held-out direct rating, reason, likes/dislikes/remarks and family are forbidden evaluator input until blind prediction + stability artifacts are frozen.

## Scale and bands
`score_0_100 = 25 * (rating_1_to_5 - 1)`.
- low <=37.5
- middle >37.5 and <75
- high >=75
- Family 1 false-high: prediction >=60
- Family 2 false-low: prediction <=50

## Baseline protocol
Use exact current five-factor geometry with no retrofit:
- gameplay_mastery 18
- development_variety 12
- structure_pacing_direction 8
- identity_hooks 8
- breadth_of_match 4
Predict each normalized factor 0..100 from only frozen training deck + public candidate evidence, then calculate `sum(factor/100*max_points)` on 0..50 and rescale x2 for experiment comparison.
The hidden direct-rating production override is prohibited because it is unavailable for a genuinely unseen candidate.
Baseline rationales may explain its five factor judgments, but baseline does not receive Architecture A's decisive-negative/positive checklist or family label.

## Refined Architecture A protocol
Before scoring, A MUST separately record:
1. strongest reasons the user might like the game;
2. strongest reasons the user might dislike it;
3. whether a single personally decisive negative should cap the score;
4. whether a single personally decisive positive/contextual hook should outweigh conventional weaknesses;
5. whether similarity to a liked game is superficial rather than causal;
6. whether novelty relative to own franchise/history matters;
7. whether onboarding/first-hours friction is likely to dominate;
8. missing/uncertain evidence.
Then assign one calibrated holistic 0..100 score, strongest reason up/down, decisive factor if any, calibration comparison and uncertainty. Generic feature richness is never sufficient by itself.

## Fixed calibration anchors
- Half-Life — 1.5/5 => 12.5
- Fallout 4 — 2.0/5 => 25
- Deus Ex: Human Revolution — 2.5/5 => 37.5
- Stray — 3.0/5 => 50
- Tomb Raider (2013) — 3.5/5 => 62.5
- Batman: Arkham Asylum — 4.0/5 => 75
- Red Dead Redemption II — 4.5/5 => 87.5

## Metrics
MAE; RMSE; Spearman; unequal-truth pairwise ordering accuracy (predicted tie = 0.5); band ECE on [0,25), [25,50), [50,75), [75,100]; Family 1 false-high; Family 2 false-low; severe deal-breaker miss; decisive-positive miss; high-score precision; low-score precision; rerun variance; explanation drift; explanation auditability; all major metrics separately by family.

No post-hoc metric substitution.

## Truth-side rules after unblinding
**Severe deal-breaker truth:** rating <=3.0, discussion confidence not low, and direct explanation identifies one primary negative/coherent root cluster explaining low enjoyment or abandonment. Root clusters may be onboarding/information overload, control/combat feel, pacing/repetition/filler, franchise-relative novelty, emotional/story hook, ending, or implementation quality. Score miss = prediction >=60.

**Decisive-positive truth:** rating >=3.5, discussion confidence not low, and direct explanation identifies a primary positive/contextual hook explaining why enjoyment stays positive despite conventional weakness. Hooks may be novelty/first-contact, freedom/identity/fantasy, atmosphere, unusual mechanic, co-op/social context, nostalgia/era, resonant character/story, mastery satisfaction. Score miss = prediction <=50.

Semantic explanation-match is audited separately from score miss.

## Stability protocol
Before truth unblinding, select 8 cases by deterministic hash within the hidden family assignments: 4 Family 1 + 4 Family 2. Run Architecture A two additional times with identical frozen evaluator inputs and no truth/prior-rationale access.
Acceptable:
- mean absolute rerun delta <=3;
- max delta <=7;
- <=12.5% repeat observations change low/middle/high band;
- decisive-factor polarity/class agreement >=87.5%;
- material explanation drift <=12.5%;
- zero positive<->negative reversals of the same claimed decisive factor.

## Explanation taxonomy
missed decisive negative; overweighted generic richness; superficial similarity; missed novelty/context; missed first-contact effect; missed franchise-relative novelty expectation; invented importance; correct decisive factor but wrong magnitude; correct reasoning and score band.

## Decision thresholds
**A clearly wins** only if every core gate passes:
1. A MAE improves by >=3.0 points AND >=15% relative.
2. A RMSE <= baseline RMSE.
3. A pairwise accuracy >= baseline -0.03 AND Spearman >= baseline -0.05.
4. Family 1 false-high improves by >=0.20 and is <=0.40.
5. Family 2 false-low improves by >=0.20 and is <=0.30.
6. Severe deal-breaker miss improves by >=0.20 and is <=0.40.
7. Decisive-positive miss improves by >=0.20 and is <=0.30.
8. Every stability threshold passes.
9. A correct decisive-factor explanation rate >=0.70 AND >= baseline +0.15; generic-richness/superficial-similarity explanation errors <=0.20.
10. ECE <= baseline +2 points; high/low precision, when defined for both, does not worsen by >0.10.

**Baseline remains better supported** only if A fails clear-win gates and at least one is true:
- baseline MAE is >=3 points lower than A; or
- baseline pairwise accuracy is >0.05 higher AND A fails to improve either family error rate by >=0.10; or
- A materially worsens both hard-family score error and decisive-factor explanation accuracy.

Otherwise: **Evidence remains inconclusive**.

Status mapping:
- A clearly wins => `architecture_a_ready_for_implementation_design`
- Baseline remains better supported => `baseline_better_supported`
- Evidence remains inconclusive => `evidence_inconclusive`

No implementation follows any outcome.
