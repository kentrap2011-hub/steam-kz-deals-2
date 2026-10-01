# WORKER TASK — personal taste scoring architecture research 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `personal-taste-scoring-architecture-research-01`
Mode: `READ-ONLY / RESEARCH / DESIGN`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/personal-taste-scoring-architecture-research-01.md`

## User goal

The user wants the personal taste score to be trustworthy, understandable and controllable.

The current fixed weighted buckets are NOT an architectural constraint. Do not assume the present five taste factors, their weights, the 50-point taste subscore, current Deep result shape, current score findings format, or current ranking score formula must survive.

If a materially better design requires replacing them, say so explicitly and describe the migration.

The user specifically wants to avoid hidden arbitrary weighting such as:
- one predefined category having too much or too little maximum influence;
- a factor receiving a very high score without a clear reason;
- similarity to a liked game being treated as valuable merely because it is superficially similar;
- a model outputting a final score that cannot be audited.

A useful system should let the user inspect why a game received, for example, 87/100 personal fit and understand which concrete game properties and which proven personal preferences moved that score up or down.

## Mandatory START gate

1. Read current `CHAT_PROTOCOL.md` from `main` fully and execute its START gate.
2. Read this task fully.
3. Read the current Director Board only for ownership/concurrency.
4. Inspect the current scoring, Deep evidence, Taste profile, ranking and UI architecture only to understand what exists and what migration would be required.
5. Do NOT treat current architecture as the starting assumption for the recommended design.

Do not start another task.

## Research requirement

This is not only repository analysis. Perform substantial current web research.

Use high-quality sources where possible:
- recommender-system literature and production practices;
- preference-learning / ranking literature;
- explainable recommendation;
- calibrated scoring and uncertainty;
- pairwise comparison methods;
- human preference modelling;
- LLM-as-judge / model-based evaluation calibration;
- multi-attribute utility approaches;
- industrial or academic systems that learn from positive/negative examples rather than fixed hand-authored buckets.

Prefer primary papers, official research blogs/docs, conference papers, books/lecture materials from credible institutions, and first-party engineering material over SEO summaries.

The report must contain source links/citations and clearly distinguish:
- established practice;
- promising research idea;
- worker's own architectural proposal.

Do not copy long passages.

## Do not anchor on the current design

Explicitly consider architectures that may require deleting or replacing:
- the five fixed normalized taste factors;
- fixed per-category maxima such as 18/12/8/8/4;
- the current 50/60 personal-score structure;
- the current `taste_factors` schema;
- current Deep score-finding semantics;
- current deterministic score assembly;
- current migration compatibility assumptions.

Existing architecture matters only when estimating migration cost, safety and rollout.

Do not reject a better design merely because it would be a large refactor.

## Required design space

Produce at least FOUR materially different scoring architectures.

At minimum investigate these families, but do not limit yourself to them:

1. **Holistic calibrated semantic score**
   - Deep evaluates the complete fit from 0–100;
   - no fixed category caps;
   - requires explicit evidence-backed positive/negative contributions and calibration anchors.

2. **Dynamic evidence contribution model**
   - Deep discovers candidate-specific factors itself;
   - each factor can contribute variable positive/negative weight;
   - contributions sum or otherwise compose into a final fit score;
   - no permanent global buckets.

3. **Pairwise / preference-learning model**
   - estimate fit by comparing a candidate to games or experiences the user liked/disliked;
   - investigate Bradley–Terry, Thurstone, Plackett–Luce, Elo-like or modern preference-learning variants;
   - explain how absolute 0–100 output could be calibrated from pairwise evidence.

4. **Hybrid model**
   - e.g. learned/pairwise preference prior + semantic Deep evidence + uncertainty/calibration layer;
   - candidate-specific explanations remain auditable.

Also consider whether nearest-neighbour / embedding similarity, collaborative-filtering style ideas, or learned latent preference representations help or hurt in this personal single-user setting.

## Questions the report must answer

### A. What should 0–100 actually mean?

Define a stable interpretation of ranges.

For example, decide whether 90 means:
- very high predicted enjoyment;
- very high match to established taste;
- high confidence of purchase satisfaction;
- relative rank percentile;
- or something else.

Avoid mixing incompatible meanings.

Explain how the score stays comparable across genres and across time.

### B. How should one very strong factor behave?

The user's concern is central:

If one property of a game is extraordinarily important to this user and strongly evidenced, should it be able to account for a very large portion of the fit score?

Compare designs where it can vs cannot.

Explain safeguards against one superficial feature dominating the score incorrectly.

### C. How should examples from liked/disliked games be used?

Use a Last-of-Us-style example:
- do not reward superficial similarity;
- identify WHAT the user liked in the reference game;
- match those underlying properties against the candidate;
- allow a very different genre to score highly if it reproduces the personally important experience;
- allow a superficially similar game to score poorly if it misses the actual reasons.

### D. How should negatives work?

A score must not be a pile of positives only.

Explain:
- strong deal-breakers;
- moderate friction;
- uncertainty;
- conflicting evidence;
- one severe negative vs many positives;
- whether penalties should be additive, multiplicative, gating, probabilistic or semantic.

### E. How do we prevent arbitrary model scoring?

For every architecture, explain how to stop the semantic worker from simply saying:
`87 because it feels like 87`.

Evaluate mechanisms such as:
- calibration anchors;
- score bands with explicit criteria;
- pairwise reference games;
- evidence contribution accounting;
- consistency checks;
- counterfactual checks;
- repeated judge agreement;
- deterministic validation;
- uncertainty/confidence;
- score-change limits absent new evidence.

### F. What should the user see on the card?

Design an audit UI for the score.

The user should be able to answer:
- why this score is high/low;
- which factors mattered most;
- how much each factor mattered, if numeric contributions are used;
- which known personal preference each reason came from;
- what evidence about the game supports it;
- what lowered the score;
- what is uncertain;
- whether the score is coarse/legacy/migrated.

Do not overload the default card. Propose collapsed and expanded views.

### G. How should user corrections work?

Explore a future feedback loop such as:
- “this factor matters much less to me”;
- “this factor matters much more”;
- “you misunderstood why I liked this game”;
- “this negative is not a problem for me”;
- “87 feels too high; compare against these known games.”

Explain whether corrections should update:
- the Taste profile;
- pairwise preferences;
- calibration anchors;
- model evidence weights;
- or some combination.

Do not implement this feature in this task.

### H. What remains deterministic GitHub-owned?

For each architecture identify:
- semantic responsibilities of Deep;
- deterministic validation responsibilities of GitHub;
- what data must be persisted;
- what may never be silently recomputed by the browser;
- how reproducibility and auditability are preserved.

### I. Migration

For every serious option explain:
- what current data can be reused;
- what must be discarded or recomputed;
- whether existing Deep results need finite migration/reanalysis;
- how to avoid mixing old and new incomparable scores;
- rollout strategy;
- rollback strategy.

## Evaluation criteria

Compare every proposed architecture against the same criteria:

- faithfulness to the user's real taste;
- freedom from arbitrary fixed category caps;
- explainability;
- auditability;
- resistance to hallucinated/arbitrary scores;
- ability to learn from liked/disliked examples;
- handling of strong single factors;
- handling of negatives/deal-breakers;
- uncertainty handling;
- cross-genre comparability;
- score stability over time;
- user-correction support;
- implementation complexity;
- migration cost;
- runtime/semantic cost;
- deterministic validation strength.

Do NOT reduce the result to a fake numeric scorecard unless the numbers have a defensible meaning. A qualitative comparison table is preferred.

## Required recommendation structure

Do not stop at one idea.

The report must provide:
- at least four real alternatives;
- strengths and failure modes of each;
- which two are the strongest candidates for this project and why;
- one recommended architecture;
- one serious runner-up;
- what evidence/experiment would change the recommendation.

The recommendation may be a full rewrite of the current scoring architecture.

## Concrete examples

Run at least three worked examples using hypothetical but realistic user-preference situations:

1. one dominant factor should legitimately drive a very high score;
2. superficial similarity to a favorite game should NOT create a high score;
3. many moderate positives are offset by one meaningful deal-breaker.

Show how each leading architecture would treat them.

Do not use invented claims about the user's actual preferences as facts. Clearly label hypothetical examples.

## Current repository assessment

After the independent design work, map the recommended architectures back to the repo:

- current files/contracts that would likely change;
- current data that can be reused;
- current fields that should be retired;
- migration boundaries;
- whether RANK-013 should remain separate or eventually consume a new personal-fit output;
- whether commercial purchase scoring should remain separate from personal taste.

Do not implement any changes.

## Hard boundaries

Do NOT:
- modify production code;
- modify scoring/ranking contracts;
- change Deep/Dossier state;
- run semantic Deep or Dossier;
- change current visual payload;
- create implementation PR;
- change Scheduled Tasks;
- create automation/scheduler/queue/retry machinery;
- make production migrations.

Only the task report and minimal task-tracking metadata may be written.

## Delivery

Write:

`reviews/worker_reports/personal-taste-scoring-architecture-research-01.md`

Required report sections:

1. Task and research method
2. User problem restated
3. Current architecture — only as baseline
4. External practices researched
5. What a 0–100 score should mean
6. Architecture A
7. Architecture B
8. Architecture C
9. Architecture D
10. Additional variants worth noting
11. Common safeguards against arbitrary scoring
12. Worked examples
13. User-facing audit UI
14. Correction/feedback loop
15. GitHub/Deep ownership model
16. Comparative analysis
17. Two strongest candidates
18. Recommended architecture
19. Serious runner-up
20. What would change the recommendation
21. Migration impact
22. Proposed validation/experiment before implementation
23. Unresolved questions
24. Exact external sources
25. Status
26. Recommended next step — exactly one bounded next action

Allowed statuses:
- `research_complete_ready_for_director_review`
- `needs_more_research`
- `needs_user_decision`
- `blocked`

Do not implement after producing the report.
