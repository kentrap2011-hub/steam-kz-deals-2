# WORKER TASK — personal taste scoring offline backtest 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `personal-taste-scoring-offline-backtest-01`
Mode: `READ-ONLY / OFFLINE EXPERIMENT`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/personal-taste-scoring-offline-backtest-01.md`

## Goal

Test whether the proposed replacement personal-taste architectures actually predict the user's known game preferences better and explain them more faithfully than the current fixed five-factor system.

This is an offline experiment only.

Do NOT change production scoring, ranking, Deep/Dossier contracts, visual payload, or Scheduled Tasks.

## Mandatory START gate

1. Read current `CHAT_PROTOCOL.md` from `main` fully and execute START gate.
2. Read current `DIRECTOR_TASK_BOARD.md` current-state section.
3. Read:
   - `WORKER_TASK_PERSONAL_TASTE_SCORING_ARCHITECTURE_RESEARCH_01.md`;
   - `reviews/worker_reports/personal-taste-scoring-architecture-research-01.md`.
4. Read current Taste/profile inputs and the historical rating+reason dataset referenced by the research report.
5. Read current five-factor scoring implementation only as the baseline comparator.
6. Freeze all experiment inputs before scoring held-out cases.

Do not start another task.

## Architectures to compare

At minimum compare:

### Baseline
Current fixed five-factor personal-taste model.

### Architecture A
Holistic calibrated semantic 0–100 evaluation with explicit evidence-backed positives/negatives and calibration anchors.

### Architecture C
Pure pairwise latent-preference model using candidate-vs-known-anchor comparisons; fit at least one principled pairwise model such as Bradley–Terry and, if practical, one alternative such as Thurstone/tie-aware variant.

### Architecture D
Anchor-calibrated evidence-grounded hybrid recommended by the research report:
- Deep/semantic evaluator produces grounded findings and pairwise anchor relations;
- semantic evaluator does NOT directly author final 0–100;
- deterministic offline code derives latent utility and maps it to the user's rating-equivalent score.

Do not favor Architecture D merely because the research report recommended it.

## Data leakage rule

Held-out evaluation must be genuinely blind.

For every held-out game:
- hide its direct user rating;
- hide its `why_this_rating` or equivalent explanation;
- hide any derived profile statement that was created solely from that same held-out rating/reason if it would leak the answer;
- do not use the current final score/rank for the held-out game as evidence.

Training/calibration examples may use their known ratings/reasons.

Document exactly how leakage was prevented.

## Split

Create a deterministic, versioned split of the available historical rating+reason examples.

Target:
- at least 30 held-out games if the dataset permits;
- stratify across low/mid/high ratings and materially different game/experience types;
- keep enough calibration/training examples to provide anchors at multiple preference levels.

Use a deterministic rule (for example stable hash + strata), not hand-picking cases to make one architecture look good.

Persist the split manifest as an experiment artifact if needed.

## Semantic evaluation protocol

For each held-out candidate, use only evidence that would have been available without knowing its hidden rating.

The evaluator must reason about:
- concrete properties of the game;
- evidence-backed user preferences from non-held-out/profile sources;
- positive fit;
- negative fit/deal-breakers;
- uncertainty/conflicting evidence.

For anchor-based models:
- use a versioned anchor-selection rule;
- include anchors across rating levels;
- prefer meaningful contrast anchors rather than only nearest-similarity matches;
- do not reward superficial genre/franchise similarity by itself;
- comparison rationale must identify the underlying property that matters to the user.

## Worked semantic records

Persist enough per-case experiment data to audit results, but do not expose private/raw profile material unnecessarily.

Each held-out case should record at minimum:
- hidden truth only in evaluation output, not evaluator input;
- predicted score/band by each architecture;
- pairwise relations used by C/D;
- major positive findings;
- major negative findings;
- uncertainty;
- whether one dominant factor drove the conclusion;
- whether any superficial-similarity trap was detected;
- provenance/input version.

## Metrics

Evaluate at minimum:

- rank correlation against held-out user ratings;
- pairwise ordering accuracy;
- absolute error after mapping to a common rating-equivalent scale;
- calibration by score band;
- high-score precision (how often very high predicted fit is actually high-rated);
- low-score precision;
- deal-breaker miss rate;
- cross-genre consistency;
- unsupported/hallucinated finding rate by manual audit;
- rerun stability on a representative subset;
- semantic/runtime cost per candidate;
- explanation auditability.

Do not collapse the decision to one metric.

## Stability test

For a representative subset of held-out games, repeat the semantic evaluation at least twice with identical frozen inputs.

Measure:
- score/band variance;
- pairwise relation changes;
- explanation drift;
- whether winner architecture is robust to rerun noise.

If architecture output is too unstable to compare meaningfully, report that as a failure mode.

## Three mandatory stress cases

Ensure the held-out or supplemental audit set contains examples for:

1. one dominant property legitimately should drive a very high fit;
2. superficial similarity to a favorite game should not create a high fit;
3. many moderate positives are offset by one meaningful negative/deal-breaker.

If the historical dataset lacks a clean real example, use a clearly labelled supplemental hypothetical audit case, but do not mix it into prediction metrics.

## Current baseline fairness

The current five-factor baseline must be evaluated honestly under its actual production semantics.

Do not deliberately cripple it.

If some held-out cases only have legacy/coarse baseline state, report that limitation separately rather than treating missing precision as a zero.

## Architecture D calibration

Do not allow the semantic evaluator to directly type the final 0–100.

Use pairwise/anchor outputs plus deterministic offline mapping.

Document:
- pairwise model;
- anchor selection;
- mapping from latent utility to rating-equivalent 0–100;
- uncertainty method;
- handling of ties/conflicts.

## Architecture A calibration

If Architecture A directly returns a holistic score, require explicit score-band anchors and perform calibration against training examples.

Measure rerun variance carefully because direct model-authored scalar scoring is a known risk.

## Architecture C

Test whether pairwise-only structure is sufficient without the richer evidence-finding layer.

Specifically inspect:
- explainability;
- deal-breaker handling;
- contextual/non-transitive preferences;
- graph connectivity/model fit.

## User-facing auditability

For a small blinded sample, produce the exact kind of explanation a user would see:
- final personal-fit score;
- strongest reasons up;
- strongest reasons down;
- anchor comparisons;
- uncertainty;
- evidence/profile linkage.

Judge whether the explanation makes it possible to notice a mistaken assumption such as “visual style mattered far more than it actually does.”

## Decision rule

Do not preselect a winner.

At the end:
- identify the best-supported architecture;
- identify the runner-up;
- state where evidence is inconclusive;
- state what result would justify keeping the current model;
- state whether evidence is strong enough to authorize implementation now.

If none is clearly better, recommend another bounded experiment rather than forcing a redesign.

## Experiment artifacts

You may add deterministic experiment-only artifacts under:

`experiments/personal_taste_scoring/backtest_01/`

Allowed:
- frozen split manifest;
- derived non-production comparison tables;
- experiment-only scripts;
- experiment result JSON/CSV;
- methodology notes.

Do not modify production source/config/data.

## Hard boundaries

Do NOT:
- change production scoring/ranking;
- change Deep/Dossier contracts;
- write production semantic results;
- run production Deep or Dossier;
- alter Taste canonical profile data;
- publish visual/site changes;
- create Scheduled Tasks;
- change scheduler/queue/retry behavior.

## Delivery

Write:
`reviews/worker_reports/personal-taste-scoring-offline-backtest-01.md`

Required report sections:
1. Task
2. Frozen inputs and leakage prevention
3. Dataset and deterministic split
4. Baseline protocol
5. Architecture A protocol
6. Architecture C protocol
7. Architecture D protocol
8. Metrics
9. Stability results
10. Stress cases
11. Explanation audit
12. Results table
13. Failure modes
14. Best-supported architecture
15. Runner-up
16. Is evidence strong enough to implement?
17. Migration implications
18. Exact experiment artifacts
19. Status
20. Recommended next step — exactly one bounded next action

Allowed statuses:
- `experiment_complete_ready_for_director_review`
- `evidence_inconclusive`
- `needs_more_data`
- `blocked`

Do not implement the winning architecture after the experiment.
