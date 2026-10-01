# WORKER TASK — personal taste scoring targeted offline backtest 02

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `personal-taste-scoring-targeted-offline-backtest-02`
Mode: `READ-ONLY / OFFLINE EXPERIMENT`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/personal-taste-scoring-targeted-offline-backtest-02.md`

## Goal

Run one focused follow-up experiment to answer the unresolved question from backtest 01:

Can Architecture A materially outperform the current production five-factor baseline specifically on the user's hardest preference cases — games that look externally strong but were personally disappointing, and games with conventional flaws that were nevertheless personally memorable or highly rated?

This is an offline experiment only.

Do NOT modify production scoring, ranking, Deep/Dossier contracts, visual payload, canonical Taste profile, or Scheduled Tasks.

## Mandatory START gate

1. Read current `CHAT_PROTOCOL.md` from `main` fully and execute START gate.
2. Read current `DIRECTOR_TASK_BOARD.md` current-state section.
3. Read:
   - `WORKER_TASK_PERSONAL_TASTE_SCORING_ARCHITECTURE_RESEARCH_01.md`;
   - `reviews/worker_reports/personal-taste-scoring-architecture-research-01.md`;
   - `WORKER_TASK_PERSONAL_TASTE_SCORING_OFFLINE_BACKTEST_01.md`;
   - `reviews/worker_reports/personal-taste-scoring-offline-backtest-01.md`.
4. Reuse prior experiment artifacts only where methodologically valid.
5. Freeze all new experiment inputs before scoring held-out truth.

Do not start another task.

## Scope

Compare only:

### Baseline
The current production five-factor personal-taste model under its actual current semantics.

### Architecture A
Holistic calibrated semantic personal-fit evaluation with:
- one overall 0–100 personal-fit prediction;
- explicit positive and negative evidence;
- calibration anchors;
- no fixed category caps;
- no final score justified merely by superficial similarity;
- explicit uncertainty;
- explicit treatment of decisive negatives and context-dependent positives.

Do not test Architecture C or D again in this task.

## Dataset target

Create a fresh deterministic set of **20 newly explained historical games**, if the available data supports 20 usable cases.

The set must be deliberately balanced between two hard families:

### Family 1 — externally strong but personally disliked / underwhelming
Target about 10 cases.

Examples of qualifying patterns:
- objectively rich or polished;
- many apparent positive features;
- popular or highly regarded;
- superficially similar to games the user liked;
- but the user gave a low or middling rating due to one or more personal reasons.

Prioritize cases where the direct explanation mentions:
- onboarding friction;
- information overload;
- pacing friction;
- weak novelty relative to earlier franchise experience;
- combat/control feel mismatch;
- excessive reading or system density;
- repetition/filler;
- weak emotional hook;
- disappointing ending;
- one strong deal-breaker overwhelming many positives.

### Family 2 — conventionally flawed but personally memorable / liked
Target about 10 cases.

Examples:
- technically rough;
- shallow by conventional design criteria;
- repetitive;
- dated;
- low production values;
- narrow;
- yet personally rated well because of novelty, freedom, atmosphere, identity, nostalgia/context, unusual mechanics, fantasy fulfilment, first-contact effect, or another personally decisive hook.

The split must be deterministic and versioned.

Do not manually cherry-pick cases after seeing model predictions.

## Freshness / independence from backtest 01

Prefer games not used as primary held-out cases in backtest 01.

If the dataset cannot provide 20 fully independent suitable examples:
- maximize independence;
- disclose overlap;
- never reuse a prior held-out result as model evidence;
- do not count duplicated evidence twice.

## Leakage prevention

For every held-out game:
- hide its direct user rating;
- hide its direct reason/explanation;
- remove any profile statement derived solely from that exact held-out rating/reason when that would leak the answer;
- do not use its current production score or rank as semantic evidence;
- do not use prior backtest predictions for that game as evidence.

Freeze evaluator input first.

Persist a leakage audit.

## Pre-registration before scoring

Before any held-out predictions are generated, persist a pre-registration artifact containing:

- exact 20-game split;
- family assignment;
- baseline protocol;
- Architecture A protocol;
- calibration anchors;
- metrics;
- thresholds for deciding whether A clearly wins;
- rules for deal-breaker detection;
- rules for “personally meaningful contextual hook” detection;
- stability protocol;
- no post-hoc metric substitution.

This pre-registration must be committed before prediction artifacts.

## Decision thresholds

Set defensible thresholds before scoring.

At minimum require Architecture A to show improvement over baseline in the dimensions that mattered most in backtest 01:

1. materially lower absolute error;
2. no material degradation in pairwise ordering;
3. lower false-high rate on Family 1;
4. lower false-low rate on Family 2;
5. lower severe deal-breaker miss rate;
6. acceptable rerun stability;
7. explanations that expose the decisive personal reason rather than generic feature richness.

Do not declare A production-ready based on MAE alone.

The exact numeric thresholds must be pre-registered and justified before predictions.

## Architecture A protocol refinement

Backtest 01 showed that a generic holistic score still missed decisive personal context.

Therefore Architecture A in this task must explicitly test a refined protocol:

Before assigning a score, the semantic evaluator must separately answer:

1. What are the strongest reasons this user might like the game?
2. What are the strongest reasons this user might dislike the game?
3. Is there any single personally decisive negative that should cap the score?
4. Is there any single personally decisive positive/contextual hook that should outweigh conventional weaknesses?
5. Is any apparent similarity to a liked game superficial rather than causal?
6. Is novelty relative to the user's own prior franchise/history important here?
7. Is onboarding/first-hours friction likely to dominate actual enjoyment?
8. What evidence is missing or uncertain?

Only then produce the calibrated 0–100 prediction.

The score must be justified against fixed calibration anchors from training examples.

## Baseline fairness

Evaluate the current five-factor model exactly as production would.

Do not retrofit new information into it.

If a case is legacy/coarse or otherwise not comparable, disclose and handle it according to a pre-registered rule.

## Metrics

At minimum:

- MAE;
- RMSE;
- Spearman rank correlation;
- pairwise ordering accuracy;
- calibration error by score band;
- false-high rate on Family 1;
- false-low rate on Family 2;
- severe deal-breaker miss rate;
- decisive-positive miss rate;
- high-score precision;
- low-score precision;
- rerun score variance;
- explanation drift;
- explanation auditability.

Also report results separately by Family 1 and Family 2.

## Stability test

Repeat Architecture A scoring at least twice with identical frozen inputs for a representative subset spanning both families.

Measure:
- absolute score variance;
- band changes;
- whether decisive negative/positive detection changes;
- explanation drift.

Pre-register what variance is acceptable.

## Explanation audit

For every held-out case, after unblinding compare the predicted explanation to the actual user explanation.

Classify errors such as:
- missed decisive negative;
- overweighted generic richness;
- superficial similarity;
- missed novelty/context;
- missed first-contact effect;
- missed franchise-relative novelty expectation;
- invented importance;
- correct decisive factor but wrong magnitude;
- correct reasoning and score band.

Create a compact confusion/error taxonomy.

## User-facing sample

Produce a small blinded sample showing what the future card would say under Architecture A:

- personal fit 0–100;
- strongest reason up;
- strongest reason down;
- decisive factor if one exists;
- calibration anchor comparison;
- uncertainty;
- why the model did NOT overvalue superficial similarity or conventional quality.

This is experimental output only.

## Decision rule

At the end, return one of:

### A clearly wins
Only if pre-registered thresholds are met broadly enough to justify moving to implementation design.

### Baseline remains better supported
If A does not materially improve the hard cases or damages ordering/stability.

### Evidence remains inconclusive
If sample size/noise prevents a responsible choice.

Do not force a winner.

## Experiment artifacts

Use:
`experiments/personal_taste_scoring/backtest_02/`

Allowed:
- preregistration;
- frozen split;
- evaluator inputs;
- baseline outputs;
- Architecture A predictions;
- repeated stability runs;
- metrics;
- unblinded evaluation;
- explanation audit;
- blinded UI sample;
- deterministic analysis scripts.

Do not write production data.

## Hard boundaries

Do NOT:
- change production scoring/ranking;
- change Deep/Dossier contracts;
- write production semantic results;
- run production Deep or Dossier;
- alter canonical Taste profile data;
- publish visual/site changes;
- create Scheduled Tasks;
- change scheduler/queue/retry behavior;
- implement Architecture A after the experiment.

## Delivery

Write:
`reviews/worker_reports/personal-taste-scoring-targeted-offline-backtest-02.md`

Required sections:

1. Task
2. Why this follow-up exists
3. Pre-registration
4. Frozen dataset and family balance
5. Leakage prevention
6. Baseline protocol
7. Refined Architecture A protocol
8. Metrics and decision thresholds
9. Family 1 results
10. Family 2 results
11. Overall results
12. Stability
13. Deal-breaker / decisive-positive analysis
14. Explanation error taxonomy
15. User-facing blinded sample
16. Does A clearly win?
17. Is production implementation justified?
18. Exact experiment artifacts
19. Status
20. Recommended next step — exactly one bounded next action

Allowed statuses:
- `experiment_complete_ready_for_director_review`
- `evidence_inconclusive`
- `baseline_better_supported`
- `architecture_a_ready_for_implementation_design`
- `needs_more_data`
- `blocked`

Do not implement after producing the report.
