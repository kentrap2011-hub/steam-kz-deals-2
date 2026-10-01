# Personal Taste Scoring Targeted Offline Backtest 02

## 1. Task

Task: `WORKER_TASK_PERSONAL_TASTE_SCORING_TARGETED_OFFLINE_BACKTEST_02.md`

Mode: `READ-ONLY / OFFLINE EXPERIMENT`

Comparison:
- current production five-factor personal-taste baseline under its frozen current semantics;
- refined Architecture A only.

No Architecture C/D retest was performed. No production scoring, ranking, Deep/Dossier contract, canonical Taste profile, visual publication, scheduler, queue, retry owner, or Scheduled Task was changed.

Experiment base: `main@94bec36a02513a4cb319cbbdd45d3c6f42a3bcd5`.

## 2. Why this follow-up exists

Backtest 01 found a mixed result:
- Architecture A improved point calibration modestly;
- the five-factor baseline remained stronger on ordering;
- both still missed 7/10 severe low-rating cases;
- the dominant unresolved failures were polished/feature-rich games that the user personally disliked and conventionally flawed games whose personal context made them memorable.

This follow-up therefore deliberately concentrates on those hard cases rather than another broad architecture search.

## 3. Pre-registration

The preregistration was committed before any held-out prediction artifact:

- preregistration commit: `e26eba6409f8284bfc464c0e68a7faabf28bbccc`;
- blind primary predictions commit: `1f03b783fb7d41c50a74c9f95dd5e0eb7d510e35`;
- blind stability runs commit: `82a470a37801cbf147dcebc3b97c17eb3aca6a95`;
- truth was unblinded only afterward in commit `a6b9d32cb6018c753a15213e8de4826a0497174f`.

The preregistration froze:
- exact 20 cases and family assignment;
- baseline protocol;
- refined A protocol;
- seven calibration anchors;
- truth scale and bands;
- metrics;
- Family 1 / Family 2 error definitions;
- severe deal-breaker and decisive-positive rules;
- stability protocol;
- explanation taxonomy;
- numeric decision gates;
- final status mapping.

No decision threshold was changed after predictions.

## 4. Frozen dataset and family balance

Final set: 20 games.

- Family 1 — externally strong / feature-rich but personally underwhelming: **10**.
- Family 2 — conventionally imperfect but personally memorable/liked: **10**.

The final set is intentionally a subset of the prior final blind-v4 held-out pool. This is not ideal for between-experiment independence, but it became the strongest remaining leakage-safe option after two new-split attempts were rejected before scoring.

Identity overlap with backtest 01: **20/20**.

Prior backtest predictions/results for those titles were explicitly forbidden evaluator evidence and were not opened before the new blind predictions were frozen. This experiment therefore provides new semantic predictions on old hidden-truth cases rather than a statistically independent second sample.

Frozen profile blob:
`9b9926031889dbd98ba6585c57836d52c739a0bb`.

Frozen candidate-evidence blob:
`92730d68fc49fcf90d9520d84aade03ecb3c9cfa`.

Frozen safe training input blob:
`47b7aa3e1e9148b547ddd2c08fb34bb0830b6923`.

## 5. Leakage prevention

Two setup attempts were rejected fail-closed before any prediction:

1. **02-A** — sequential family-coded IDs leaked family direction. The split was discarded.
2. **02-B** — inspection of the old training deck exposed direct truth for proposed fresh held-outs. The replacement split was discarded.

The final design then used only backtest-01 final blind-v4 held-outs whose truth:
- was absent from the safe 90-card training input;
- had zero exact/alias cross-reference in that input under the prior final-v4 audit;
- was not explicitly disclosed by the previous report;
- was not read from old prediction artifacts.

The evaluator received only:
- title;
- public candidate facts;
- safe training-deck reference;
- fixed calibration anchors;
- baseline factor contract;
- A's preregistered question protocol.

Withheld until after primary + stability freeze:
- rating;
- why-this-rating;
- likes/dislikes;
- remarks;
- family;
- prior backtest prediction;
- production score/rank;
- global derived `taste_profile` / `contextual_preferences` summaries.

This fail-closed history is itself a limitation: the final experiment is methodologically cleaner than the rejected attempts, but less independent from backtest 01 than originally intended.

## 6. Baseline protocol

Frozen production factor geometry:

| Factor | Max |
|---|---:|
| gameplay_mastery | 18 |
| development_variety | 12 |
| structure_pacing_direction | 8 |
| identity_hooks | 8 |
| breadth_of_match | 4 |
| **Total** | **50** |

For each blind candidate the semantic evaluator produced five normalized 0–100 values from the frozen training deck + candidate facts.

The exact current arithmetic was then applied:

`sum(normalized_factor / 100 * factor_max)`

on the 0–50 taste scale, then multiplied by 2 solely to compare with the experiment's 0–100 rating-equivalent truth scale.

The direct-rating production override was prohibited because a genuinely unseen candidate would not have it.

No Architecture-A checklist was fed into baseline factor judgments.

## 7. Refined Architecture A protocol

A was required to answer before assigning a score:

1. strongest reasons the user might like the game;
2. strongest reasons the user might dislike it;
3. whether one decisive personal negative should cap the score;
4. whether one decisive positive/context hook should outweigh ordinary weaknesses;
5. whether similarity to a liked game is superficial;
6. whether franchise/history-relative novelty matters;
7. whether onboarding/first-hours friction is likely to dominate;
8. what evidence is missing or uncertain.

Only then could it assign a holistic 0–100 expected-enjoyment score.

Fixed anchors:
- Half-Life — 12.5;
- Fallout 4 — 25;
- Deus Ex: Human Revolution — 37.5;
- Stray — 50;
- Tomb Raider (2013) — 62.5;
- Batman: Arkham Asylum — 75;
- Red Dead Redemption II — 87.5.

A had no fixed category caps.

## 8. Metrics and decision thresholds

Truth mapping:
`score = 25 * (rating - 1)`.

Bands:
- low <=37.5;
- middle >37.5 and <75;
- high >=75.

Key preregistered hard-case definitions:
- Family 1 false-high: predicted score >=60;
- Family 2 false-low: predicted score <=50;
- severe deal-breaker miss: qualifying truth-side severe case predicted >=60;
- decisive-positive miss: qualifying truth-side positive/context case predicted <=50.

A could be called **A clearly wins** only if all ten preregistered gates passed, including:
- MAE improvement >=3 points and >=15%;
- no RMSE degradation;
- no material ordering degradation;
- large reductions in both family error rates;
- severe-deal-breaker and decisive-positive improvements;
- stability;
- decisive-reason explanation accuracy;
- no material calibration/precision regression.

## 9. Family 1 results

| Metric | Baseline | A |
|---|---:|---:|
| n | 10 | 10 |
| MAE | 32.68 | **22.65** |
| RMSE | 34.43 | **25.45** |
| Spearman | **0.509** | 0.258 |
| Pairwise accuracy | **0.714** | 0.586 |
| Calibration ECE | 32.68 | **21.75** |
| False-high rate (>=60) | 1.00 | **0.80** |

A materially reduced absolute error in Family 1 by **10.03 points**, which is an important positive signal.

However, it still predicted **8 of 10** underwhelming cases at 60 or above. The preregistered acceptance cap was <=0.40, so Family 1 gate 4 failed despite the 20-point improvement versus baseline.

A also lost within-family ordering quality: pairwise accuracy dropped from 0.714 to 0.586 and Spearman from 0.509 to 0.258.

Most revealing misses:
- Cyberpunk 2077 — A 68 vs truth 37.5;
- Grand Theft Auto III — A 72 vs truth 25;
- Mafia II — A 66 vs truth 37.5;
- Red Dead Redemption — A 82 vs truth 50.

The pattern is consistent: A now notices generic risks more often, but still often misses the **specific personal reason** why a rich game failed.

## 10. Family 2 results

| Metric | Baseline | A |
|---|---:|---:|
| n | 10 | 10 |
| MAE | **8.26** | 8.50 |
| RMSE | **10.03** | 11.18 |
| Spearman | 0.687 | **0.754** |
| Pairwise accuracy | 0.889 | **0.926** |
| Calibration ECE | **7.26** | 8.50 |
| False-low rate (<=50) | **0.00** | 0.20 |

On these personally liked/memorable cases, the baseline was already well calibrated. A did not improve absolute error and introduced two false-low cases:
- Perfect World — A 45 vs truth 62.5;
- Sanitarium — A 50 vs truth 75.

Both are important because they illustrate the opposite failure from Family 1:
- Perfect World was personally valuable for social role, co-op dungeons and flight; A over-penalized conventional MMO grind;
- Sanitarium was valuable for atmosphere, puzzles and emotionally affecting stories; A over-penalized conventional point-and-click friction.

A did improve Family 2 ordering, but that does not compensate for the preregistered requirement to reduce false-low errors.

## 11. Overall results

| Metric | Baseline | Architecture A |
|---|---:|---:|
| MAE | 20.47 | **15.58** |
| RMSE | 25.36 | **19.65** |
| Spearman | 0.330 | **0.442** |
| Pairwise accuracy | 0.634 | **0.676** |
| Calibration ECE | 18.46 | **12.18** |
| High-score precision | 0.429 | **0.600** |
| Low-score precision | n/a (0 predictions) | n/a (0 predictions) |

Overall, A is clearly better than baseline on point error, global ordering, calibration and high-score precision in this targeted sample.

MAE improvement:
- absolute: **4.895 points**;
- relative: **23.9%**.

Therefore gates 1–3 and the calibration/secondary gate passed.

But the task explicitly forbade declaring production readiness from MAE alone. The hard-case gates are the reason this experiment exists, and those did not validate A.

## 12. Stability

Representative subset: 8 blind cases, four from each hidden family.

Two additional A runs were frozen before truth unblinding.

Results over 16 repeat observations:
- mean absolute score delta: **1.625**;
- maximum delta: **2**;
- band-change rate: **0%**;
- decisive-factor class+polarity agreement: **100%**;
- positive/negative polarity reversals: **0**;
- material explanation drift under the stored root-class audit: **0%**.

All preregistered stability thresholds passed.

Important limitation: these are two additional passes by the same bounded semantic worker, not independent judges. This supports within-worker repeatability but does not measure cross-model/judge variance.

## 13. Deal-breaker / decisive-positive analysis

Truth-side severe deal-breaker cases: **7**.

| Method | Severe miss rate |
|---|---:|
| Baseline | 1.000 (7/7) |
| A | 0.857 (6/7) |

A caught one more severe case, but the preregistered gate required:
- at least 0.20 absolute improvement;
- final miss rate <=0.40.

A improved only ~0.143 and remained far above the cap. Gate 6 failed.

Truth-side decisive-positive/context cases: **7**.

| Method | Decisive-positive miss rate |
|---|---:|
| Baseline | 0.000 |
| A | 0.286 (2/7) |

A created false negatives where conventional flaws were less important than the user's personal context. Gate 7 failed.

The post-unblind evidence points to three recurring missing context channels:

1. **Franchise/history-relative comparison**
   - GTA III was judged after Vice City;
   - RDR was judged after RDR2;
   - Banner Saga 2 lost novelty relative to the first game.

2. **Social/contextual experience**
   - Perfect World was valued for helping newcomers and group dungeons, not generic MMO systems.

3. **Sustained development trajectory**
   - Cyberpunk lost the user after the sense of discovering new possibilities stopped;
   - Hogwarts Legacy similarly weakened after its strong first half.

A's refined checklist asks about these themes, but candidate/public evidence often cannot answer them. The model then fills the gap with plausible but wrong generic assumptions.

## 14. Explanation error taxonomy

Audit-eligible direct explanations: **17/20**.

Three cases were excluded from strict decisive-reason correctness because the canonical truth itself did not provide a sufficiently specific direct reason:
- The Suffering;
- Marvel's Spider-Man;
- WarCraft 3: The Frozen Throne.

Architecture A strict decisive-reason matches: **6/17 = 35.3%**.

Baseline factor-alignment proxy: **7/17 = 41.2%**.

The baseline number is only a proxy because its blind artifact stored normalized factors plus generic factor notes rather than an Architecture-A-style concrete decisive-reason narrative. Therefore this is not strong evidence that baseline explanations are superior; it is strong evidence that A did **not** reach its preregistered >=70% decisive-reason requirement.

Observed A error classes:
- missed decisive negative;
- overweighted generic richness;
- missed social/contextual hook;
- overweighted conventional friction;
- missed franchise-relative novelty expectation;
- superficial similarity to a favourite/formula;
- invented importance when direct truth was weak;
- correct decisive factor but wrong magnitude;
- correct reasoning and score band.

Concrete examples:
- **GTA III:** A hypothesized first-contact novelty; truth was the reverse — it was judged as a crude regression after Vice City.
- **RDR:** A treated shared underlying strengths with RDR2 as strong evidence; truth explicitly compared it unfavourably after RDR2.
- **Perfect World:** A centered grind/repetition; truth centered social status, helping newcomers, group dungeons and flight.
- **Sanitarium:** A made interaction friction decisive; truth centered atmosphere, puzzles and emotionally affecting stories.
- **Cyberpunk:** A noticed generic open-world/system risk but missed the actual decisive combination of weak story hook + stalled sense of mechanical discovery.

Gate 9 failed.

## 15. User-facing blinded sample

Artifact:
`experiments/personal_taste_scoring/backtest_02/blinded_user_audit_sample.json`.

Six cases were selected by a blind-ID hash independent of truth.

Each card contains exactly:
- personal fit 0–100;
- strongest reason up;
- strongest reason down;
- decisive factor;
- anchor comparison;
- uncertainty;
- why the score is not based merely on superficial similarity or conventional quality.

The sample is readable and substantially more useful than a naked five-factor number.

However, post-unblind review shows a deployment risk: a polished, coherent explanation can make a wrong assumption look especially credible. For example, the blind RDR card explicitly warned that play order could matter, but still assigned 82 because it lacked the actual play-order fact that drove the user's 50 truth score.

So explanation quality and prediction correctness must remain separate acceptance dimensions.

## 16. Does A clearly win?

**No.**

Passed preregistered gates:
- gate 1 — MAE improvement;
- gate 2 — RMSE;
- gate 3 — overall ordering;
- gate 8 — stability;
- gate 10 — calibration/secondary metrics.

Failed preregistered gates:
- gate 4 — Family 1 false-high;
- gate 5 — Family 2 false-low;
- gate 6 — severe deal-breaker misses;
- gate 7 — decisive-positive misses;
- gate 9 — decisive-reason explanation accuracy.

The numeric improvement is real but does not solve the exact hard cases the task was designed to validate.

## 17. Is production implementation justified?

**No.**

The preregistered rule does not permit implementation design when five core gates fail.

A would improve average point prediction on this sample, but production migration today would still:
- overrate many rich/polished games whose personal failure depends on hidden historical context;
- sometimes underrate liked games whose social/emotional/contextual hook beats conventional flaws;
- produce explanations that are stable and plausible but often identify the wrong decisive personal reason.

No production file was changed and no Architecture A implementation was started.

## 18. Exact experiment artifacts

All experiment artifacts are under:
`experiments/personal_taste_scoring/backtest_02/`.

- `preregistration.md` — commit `e26eba6409f8284bfc464c0e68a7faabf28bbccc`
- `frozen_split_manifest.json` — `e59cacfb66eaa3e8d1d43496628b8df2c30947a1`
- `leakage_audit_preblind.json` — `016de2b4a74c995cb4ceb7e10c4dd425ab2a0c51`
- `evaluator_input.json` — `1c0979006dc66b0587412935399145c10cb09ecc`
- `blind_predictions.json` — `1f03b783fb7d41c50a74c9f95dd5e0eb7d510e35`
- `stability_input.json` — `5252d3db372c659045c97ac8ecda252c30b4fe5d`
- `stability_runs.json` — `82a470a37801cbf147dcebc3b97c17eb3aca6a95`
- `heldout_truth.json` — `a6b9d32cb6018c753a15213e8de4826a0497174f`
- `truth_classifications.json` — `492103a8b3c533a674b208504f4ab67fdf0f4262`
- `explanation_audit.json` — `b449bd104eb72ca88771146130fb9f4989e46b07`
- `metrics.json` — `d00d2ff01e5e80a146ee2010407e850cbd7605fb`
- `evaluation_records.json` — `8a74c119ae37fcf05b7171b87cd1aa0c6d46b407`
- `blinded_user_audit_sample.json` — `864f606c3b1498dc0d9ef26e004b11d8188cdf05`

Durable worker report:
`reviews/worker_reports/personal-taste-scoring-targeted-offline-backtest-02.md`.

## 19. Status

`evidence_inconclusive`

Semantic conclusion:

**Evidence remains inconclusive.**

More precisely:
- Architecture A now has a meaningful overall numerical advantage over the five-factor baseline on this hard sample;
- it does **not** meet the preregistered hard-case acceptance criteria;
- the current baseline is also not better supported overall, because A substantially improved MAE/RMSE/calibration and global ordering;
- neither result justifies production implementation.

## 20. Recommended next step — exactly one bounded next action

**Collect 20 newly explained historical game ratings that are not currently in the canonical 120-card profile, deliberately covering franchise/play-order context, social-context value, and sustained-development drop-off, then run the same frozen baseline-vs-A protocol once on that genuinely new blind set without changing the preregistered thresholds.**

Do not implement A before that new independent evidence exists.
