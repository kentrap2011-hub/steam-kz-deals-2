# Personal Taste Scoring Offline Backtest 01

## 1. Task

Task: `WORKER_TASK_PERSONAL_TASTE_SCORING_OFFLINE_BACKTEST_01.md`

Mode: `READ-ONLY / OFFLINE EXPERIMENT`

Objective: compare the current fixed five-factor baseline against Architecture A (calibrated holistic 0–100 semantic scoring), Architecture C (pure pairwise latent preference), and Architecture D (evidence-grounded pairwise hybrid with deterministic final score mapping), without changing production scoring, ranking, Deep, Dossier, UI, publication, or Scheduled Tasks.

This report evaluates the exact frozen experiment artifacts listed in section 18. It does not implement any candidate architecture.

## 2. Frozen inputs and leakage controls

Canonical input versions frozen for the experiment:

- `kentrap2011-hub/stopgame-ratings-data/gaming_taste_live.json` blob: `9b9926031889dbd98ba6585c57836d52c739a0bb`
- `ratings.json` blob: `1317bf7add5d279c95992f97c3970b29ccaa3056`
- current ranking policy blob: `f472b74ef36abb15ac8bbdd1a21d8eac802c130c`
- current ranking implementation blob: `317bd06d4b5f45540816a952bd553e4476e0dd6b`
- current Deep semantic worker prompt blob: `df5ac13d2cf47f42a5ec24aaec7e786f226c33a6`

Leakage handling was fail-closed and is part of the experiment record:

1. A first diagnostic split was rejected because low/mid/high band labels were accidentally surfaced before prediction. All 36 affected titles were quarantined from future held-out selection.
2. Blind-v2 was then superseded because four held-out titles were directly referenced inside training-card explanation text.
3. Blind-v3 was superseded before scoring because its four replacement titles had already had their direct rating/reason exposed while they were training records.
4. Blind-v4 is the only split used for reported metrics. It excludes every title whose direct truth was exposed before freeze and has zero exact/alias held-out references in the 90 training-card text fields under the documented alias rules.
5. Global derived `taste_profile` and `contextual_preferences` summaries were withheld from the evaluator because they may contain information derived from held-out examples.
6. Blind predictions were frozen in commit `72b8e23ac0e05e2f8e3898c5150ac97e3ebfd7c9`.
7. Only after that freeze, held-out truth was unblinded and persisted in commit `fb2d9a020c9a87a24214602c4b4f6f7dd51d5082`.

The final blind-v4 split therefore preserves the core requirement: the direct held-out rating, direct explanation, likes/dislikes, and any explicit cross-reference derived from them were unavailable when predictions were authored.

## 3. Dataset and deterministic split

The canonical profile contains 120 historical rated games.

Final blind-v4:

- 30 held-out cases;
- 90 training cases;
- hidden strata: 10 low (`rating <= 2.5`), 10 mid (`3.0–3.5`), 10 high (`>= 4.0`);
- multiple experience families represented, including traversal/action, open-world action/RPG, linear action, narrative adventure/RPG, tactical/strategy, racing, fighting, MMO, sandbox/indie, and short-form observation.

The final split is stored in `frozen_split_manifest_v4.json`. The manifest intentionally does not publish title-to-band mapping before unblinding.

Candidate evidence was frozen separately from user truth. Public evidence records concrete game properties only; critic numeric verdicts were not used as prediction targets.

## 4. Current baseline implementation

The baseline uses the current five-factor contract exactly:

| Factor | Max points |
|---|---:|
| gameplay_mastery | 18 |
| development_variety | 12 |
| structure_pacing_direction | 8 |
| identity_hooks | 8 |
| breadth_of_match | 4 |
| Total | 50 |

For fair comparison, each held-out candidate received blind semantic factor values from 0–100 based on the same frozen candidate evidence and the leakage-safe training history. The actual production formula was then applied unchanged and the resulting taste score was rescaled from 0–50 to 0–100.

The hidden direct user rating override was not used because it is unavailable for a real unseen candidate and prohibited by the held-out protocol.

This is a fair test of the existing additive taste geometry, but not a claim that the experiment reproduced the complete production Deep/Dossier evidence pipeline.

## 5. Architecture A — calibrated holistic semantic 0–100

A interprets the score as a rating-equivalent expected-enjoyment value:

`score = 25 * (rating - 1)`

Frozen calibration anchors covered the observed user scale from 1.5 to 4.5, including:

- Half-Life — 1.5;
- Fallout 4 — 2.0;
- Deus Ex: Human Revolution — 2.5;
- Stray — 3.0;
- Tomb Raider (2013) — 3.5;
- Batman: Arkham Asylum — 4.0;
- Red Dead Redemption II — 4.5.

For each held-out game, A produced one holistic 0–100 score plus a dominant positive, dominant negative, and uncertainty label.

A was the best experimental candidate on absolute point calibration:

- MAE: **19.43**
- RMSE: **24.92**
- calibration ECE: **13.97**
- stability subset mean absolute rerun change: **1.56 points**
- maximum rerun change: **2 points**

However, A did not improve preference ordering:

- Spearman: **0.2939** vs baseline **0.3651**
- pairwise ordering accuracy: **0.6243** vs baseline **0.6483**

A also severely missed 7 of 10 explicit low-rating/deal-breaker cases, exactly the same severe miss count as baseline, C, and D.

## 6. Architecture C — pure pairwise latent preference

C persisted only candidate-vs-anchor pairwise relations and did not use a separate rich finding layer.

Each candidate was compared with seven common anchors. Final numeric score was produced deterministically.

Primary model:

- Bradley–Terry probability: `sigmoid(u_candidate - u_anchor)`
- anchor utility: `u = (score - 50) / 20`
- ties encoded as half-win/half-loss;
- candidate utility fitted on a fixed grid;
- final score: `clamp(50 + 20*u_MLE, 0, 100)`.

Sensitivity model:

- Thurstone/probit using the same fixed anchors.

Graph properties:

- every candidate is connected to the same seven anchors;
- the global graph is therefore connected to the rating scale;
- there are no candidate-to-candidate edges, so candidate-cycle non-transitivity is not identifiable in this design;
- the common-anchor star design is easy to fit but too coarse near the top and bottom.

Results:

- C/BT MAE: **24.95**
- C/BT Spearman: **0.1109**
- C/BT pairwise accuracy: **0.5480**
- C/BT ECE: **20.94**
- Thurstone MAE: **23.83**
- Thurstone ECE: **19.69**

The alternative link function slightly reduces point error but does not fix ranking or high-end saturation. Eighteen of 30 games were predicted in the high band by C, while only ten were truly high.

Explainability is also weaker than A/D because pairwise edge rationales were not persisted per comparison.

## 7. Architecture D — evidence-grounded anchor hybrid

D used:

1. one explicit positive finding;
2. one explicit negative finding;
3. seven pairwise anchor relations;
4. deterministic Bradley–Terry mapping identical in mechanics to the experiment C mapping.

The semantic worker did **not** author the final D numeric score.

The intended advantage was that the evidence layer would stop superficial similarity from dominating pairwise comparison. It helped on some obvious negative cases such as Half-Life: Blue Shift, Lucius II, and The Exit 8, but did not solve the main false-positive class.

D results:

- MAE: **27.41**
- RMSE: **32.90**
- Spearman: **0.2870**
- pairwise accuracy: **0.6201**
- ECE: **25.51**
- high-band precision: **0.40**
- low-band precision: **0.75**
- low-band recall: **0.30**
- severe deal-breaker miss rate: **0.70**

The deterministic mapping also saturates too aggressively. Twenty of 30 cases landed in the predicted high band, and several pairwise relation patterns map to 96–100 even when hidden truth is low or mid.

## 8. Metric definitions and headline results

Truth scale: `25 * (rating - 1)`.

High band: truth/prediction >= 75.

Low band: truth/prediction <= 37.5.

Severe deal-breaker miss: hidden rating <= 2.5, explicit negative evidence present, non-low discussion confidence, but predicted score >= 60.

Pairwise accuracy: all held-out pairs with unequal true ratings; a predicted tie receives 0.5 credit.

Calibration ECE: weighted absolute prediction-vs-truth gap in predicted score bins 0–25, 25–50, 50–75, and 75–100.

Headline table:

| Method | Spearman | Pairwise acc. | MAE | RMSE | ECE | High precision | Low precision | Low recall | Severe deal-breaker miss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Current baseline | **0.3651** | **0.6483** | 20.55 | 25.50 | 18.22 | 0.471 | n/a (0 predicted low) | 0.00 | 0.70 |
| A | 0.2939 | 0.6243 | **19.43** | **24.92** | **13.97** | 0.467 | **1.00** | 0.20 | 0.70 |
| C / Bradley–Terry | 0.1109 | 0.5480 | 24.95 | 31.80 | 20.94 | 0.389 | 1.00 | 0.20 | 0.70 |
| C / Thurstone | 0.1109 | 0.5480 | 23.83 | 30.79 | 19.69 | 0.389 | 1.00 | 0.20 | 0.70 |
| D | 0.2870 | 0.6201 | 27.41 | 32.90 | 25.51 | 0.400 | 0.75 | **0.30** | 0.70 |

No architecture dominates the baseline across the required metrics.

## 9. Stability / repeatability

Eight representative held-out cases were rerun twice with identical frozen inputs, for three total semantic passes per case.

| Method | Mean abs. change vs primary | Max abs. change | Mean within-case range | Max within-case range |
|---|---:|---:|---:|---:|
| A | 1.56 | 2.0 | 3.13 | 4.0 |
| C | 0.79 | 8.6 | 1.58 | 8.6 |
| D | 1.11 | 9.6 | 2.23 | 9.6 |

A is the smoothest and easiest to interpret.

C/D appear stable on average mainly because coarse pairwise relation patterns quantize many cases to the same score. A single relation boundary can still create an 8–10 point deterministic jump.

## 10. Real historical stress cases

### Mass Effect — polished/rich game with decisive personal onboarding friction

Hidden truth: 2/5 (25).

The user repeatedly failed to get through the opening because of information overload, too much reading, unengaging early mechanics, slow-feeling controls, and combat that did not feel exciting.

Predictions:

- baseline 82.1;
- A 85;
- C 100;
- D 100.

All methods confused externally rich RPG properties with personal fit. This is the strongest false-positive stress case.

### Grand Theft Auto V — surface richness does not imply novelty-relative-to-history

Hidden truth: 2.5/5 (37.5).

The user liked heists, but expected far more novelty and variety after earlier GTA entries, found too few new mechanics, and disliked the ending.

Predictions:

- baseline 86.2;
- A 83;
- C 96;
- D 96.

All architectures missed the importance of **relative novelty against the user's own franchise history**.

### Postal 2 — objective shallowness can coexist with personal novelty value

Hidden truth: 3.5/5 (62.5).

The strong remembered value came from childhood novelty, absurd freedom, and taboo interactions, not from technical depth.

Predictions:

- baseline 53.4;
- A 42;
- C 50;
- D 34.

D's negative evidence layer over-penalized conventional weaknesses and erased the personal contextual hook.

### Assassin's Creed — repetition did not dominate the first-series experience

Hidden truth: 4/5 (75).

Parkour, the assassin fantasy, and first-contact novelty outweighed the repetitive mission structure.

Predictions:

- baseline 63;
- A 55;
- C 66;
- D 50.

This is another case where a generally valid negative finding should not automatically dominate expected enjoyment.

## 11. Explanation and evidence audit

Manual content-level audit of frozen prediction artifacts found no plainly invented positive/negative finding among the 60 A rationale statements or 60 D findings.

However, production-grade traceability was **not** proven:

- A stored rationale text but no exact evidence pointers.
- C stored 210 pairwise relations but no exact rationale/evidence record for each edge.
- D stored record-level candidate/profile provenance labels, not exact fact-index/profile-card pointers.
- therefore content support looked acceptable in manual review, but exact machine-auditable evidence lineage remains below the current production evidence-contract standard.

The blinded UI sample itself was compact and readable: score, uncertainty interval, one positive, one negative.

That readability is not sufficient proof of reliability. In the sample, Mass Effect displayed a D score of 100 while hidden truth was 25. A plausible explanation can therefore make a badly wrong score look more trustworthy, which is a deployment risk.

No human UI preference study was conducted; this was a structural audit only.

## 12. Results table by experience family

MAE:

| Family group | n | Baseline | A | C/BT | D |
|---|---:|---:|---:|---:|---:|
| Action / traversal / linear / fighting / racing | 11 | 12.07 | **10.86** | 14.35 | 19.06 |
| Open-world / MMO | 9 | 28.31 | **28.11** | 34.98 | 37.84 |
| Narrative / tactical / strategy | 6 | 24.90 | **24.67** | 34.13 | 33.73 |
| Experimental / sandbox / loot / short-form | 4 | 19.88 | **15.63** | 17.77 | 17.43 |

A lowers MAE in every broad family group, but the improvement over baseline is tiny in open-world and narrative groups, where all approaches remain weak.

The most important cross-genre result is not a winner; it is the shared failure mode. Open-world candidates are systematically overpredicted because feature breadth, production quality, story potential, and activity count are poor proxies for this user's actual long-term engagement.

## 13. Failure modes

### Baseline

- additive positive factors accumulate too easily;
- it produced zero low-band predictions;
- it over-rewards breadth/identity/mastery even when a single personal deal-breaker dominates;
- nevertheless it retained the best rank correlation and pairwise ordering accuracy of the tested methods.

### A

- better numeric calibration than baseline;
- stable and easy to explain;
- still vulnerable to halo effects from polished/rich games;
- still missed 7/10 severe low-rating cases;
- ordering quality did not improve.

### C

- coarse anchor relations produce score quantization;
- star graph cannot test candidate-candidate non-transitivity;
- high relation patterns saturate at 96–100;
- weakest ranking performance;
- explanation surface is thin.

### D

- rich findings did not prevent halo effects;
- deterministic pairwise mapping amplified semantic overestimation;
- negative findings can also over-penalize personally meaningful novelty/context (Postal 2, Assassin's Creed);
- worst MAE and calibration of the primary tested methods;
- record-level evidence labels are not yet exact production-grade provenance.

## 14. Best-supported architecture

**Best-supported experimental candidate: Architecture A.**

Reason:

- lowest MAE;
- lowest RMSE;
- lowest calibration error;
- smoothest repeatability;
- simplest semantic/runtime shape among the alternatives;
- explanations are straightforward.

This is a narrow statement about the tested candidate architectures. It is **not** evidence that A should replace production scoring now.

A failed to beat the current baseline on rank correlation and pairwise ordering, and it did not reduce the severe deal-breaker miss count.

## 15. Runner-up

**Runner-up: current five-factor baseline.**

It has:

- the strongest Spearman correlation;
- the strongest pairwise ordering accuracy;
- materially better performance than C/D on overall error;
- the lowest migration risk because it is already production-canonical.

Its main defect remains serious: additive scoring never predicted the low band in this held-out set.

Among the new alternatives only, no stable second-place conclusion is justified: C is weaker in ranking and D is weaker in calibration/error.

## 16. Is the evidence strong enough to implement a replacement?

**No.**

The experiment disproves the stronger claim that the research-preferred D architecture is already demonstrably superior to the current baseline.

It also does not establish A as a safe replacement. A's absolute-score improvement is modest:

- MAE improves from 20.55 to 19.43 (1.12 points);
- ECE improves from 18.22 to 13.97;

but:

- Spearman drops from 0.3651 to 0.2939;
- pairwise accuracy drops from 0.6483 to 0.6243;
- severe deal-breaker miss rate stays at 70%.

Those tradeoffs are not strong enough to justify production migration.

## 17. Migration implications

No production migration is recommended from this task.

Specifically, do not change:

- `config/final_ranking_policy.json`;
- `scripts/priority_ranking.py`;
- Deep contracts/prompts;
- Dossier contracts/prompts;
- publication/ranking order;
- visual state;
- Scheduled Tasks.

If future work revisits A, it should not simply replace five factors with a free-form scalar. The new evidence says the missing information is more specific:

- onboarding friction;
- novelty relative to the user's own franchise history;
- whether mechanics continue developing after the opening;
- context/era effects that can make an otherwise shallow game personally memorable;
- explicit single-factor deal-breakers that should sometimes veto broad positive feature coverage.

These are research findings only, not implementation instructions.

## 18. Exact experiment artifacts

Final artifacts used for decision:

- `experiments/personal_taste_scoring/backtest_01/frozen_split_manifest_v4.json`
- `experiments/personal_taste_scoring/backtest_01/evaluator_training_input_v4.json`
- `experiments/personal_taste_scoring/backtest_01/candidate_evidence_v4.json`
- `experiments/personal_taste_scoring/backtest_01/blind_predictions_v4.json`
- `experiments/personal_taste_scoring/backtest_01/backtest_model.py`
- `experiments/personal_taste_scoring/backtest_01/stability_runs_v4.json`
- `experiments/personal_taste_scoring/backtest_01/blinded_ui_sample_v4.json`
- `experiments/personal_taste_scoring/backtest_01/heldout_truth_v4.json`
- `experiments/personal_taste_scoring/backtest_01/metrics_v4.json`
- `experiments/personal_taste_scoring/backtest_01/evaluation_records_v4.json`
- `experiments/personal_taste_scoring/backtest_01/stress_cases_v4.json`
- `experiments/personal_taste_scoring/backtest_01/explanation_and_cost_audit_v4.json`

Superseded/audit-only artifacts retained to preserve the leakage history:

- `frozen_split_manifest.json`
- `evaluator_training_input.json`
- `frozen_split_manifest_v3.json`
- `evaluator_training_input_v3.json`
- `candidate_evidence.json`

Semantic/runtime cost note:

- exact per-candidate LLM latency/token telemetry was not available from the connector execution environment and was not fabricated;
- reproducible semantic decision proxy per candidate:
  - baseline: 5 factor judgments;
  - A: 1 holistic score + 2 dominant rationale judgments;
  - C: 7 pairwise judgments + deterministic fit;
  - D: 2 evidence findings + 7 pairwise judgments + deterministic fit.

## 19. Status

`evidence_inconclusive`

Interpretation:

- experiment execution is complete;
- D did not validate as a replacement;
- C did not validate;
- A is the strongest new candidate on point calibration but did not demonstrate clear overall superiority to the current baseline;
- production implementation is not justified by this evidence.

## 20. Recommended next step

Run **one new pre-registered offline backtest using only the current baseline versus Architecture A on a fresh set of 20 newly explained games deliberately balanced between “externally strong but personally disliked” and “conventionally flawed but personally memorable” cases**, with the split and metric thresholds frozen before any new ratings are exposed.
