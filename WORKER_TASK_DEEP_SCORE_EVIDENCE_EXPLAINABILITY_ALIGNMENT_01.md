# WORKER TASK — DEEP SCORE EVIDENCE / EXPLAINABILITY ALIGNMENT 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Task ID: `deep-score-evidence-explainability-alignment-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/deep-score-evidence-explainability-alignment-01.md`

## User authorization and product requirement

The user explicitly rejects a presentation-only fix.

The required invariant is:

> A Deep personal score must be based on the same grounded, specific reasons that can be shown to the user. The site must explain the actual reasons that produced the rating, not hide weak reasons while still letting them affect the score.

This task must align the full chain:

`Deep semantic findings -> grounded factor evidence -> accepted taste_factors -> deterministic score contribution -> visible explanation`

Do NOT merely add more lexical templates to `scripts/card_explanation_policy.py`.

## Accepted diagnosis

Read and reuse:
`reviews/worker_reports/kof-xv-missing-positive-reasons-diagnostic-01.md`

Accepted facts:
- KOF XV / AppID 1498570 currently has authoritative completed Deep;
- current Deep has specific positive evidence and taste factors;
- current visual ranks it highly;
- current positive explanation is lost because `scripts/card_explanation_policy.py::_positive_reason()` recognizes only a narrow set of hard-coded textual forms;
- current snapshot showed 34 visible Deep analyzed-fit cards, only 7 with non-empty `why_fit` and 27 with empty `why_fit`;
- this is broader than KOF XV;
- ranking and explanation are currently separate enough that a card may receive a strong personal score while visible reasons are filtered independently.

## Core correctness rule

After this task, for authoritative Deep results:

1. Every material personal score contribution must be traceable to explicit grounded semantic findings.
2. Each score-bearing finding must identify:
   - which Taste factor(s) it supports or lowers;
   - the exact candidate/game evidence;
   - the exact personal/profile evidence or preference it is being matched against when the claim is personalized;
   - the current immutable semantic/Deep binding.
3. Generic praise, broad genre labels, popularity, review score, price, discount, ranking position, purchase verdict or other commercial signals must not be allowed to masquerade as a personal positive reason.
4. A material Taste factor must not receive a positive contribution merely because the semantic worker emitted a number. The accepted result must carry sufficient grounded support for that contribution.
5. The visible explanation must be a faithful projection of those same accepted score-bearing findings.
6. A reason that is not valid enough to show as part of the score explanation must not silently remain valid enough to raise the personal score.
7. Conversely, a valid specific score-bearing reason must not disappear merely because its wording does not match a hard-coded phrase list.
8. Negative/caution findings that materially lower or qualify the personal assessment must remain visible through the existing grounded negative/caution path, so the user can see the important reasons for both the high and low parts of the rating.
9. Ranking weights/formula remain GitHub-owned and deterministic; this task does not invent a second scoring system.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and fully execute its START gate.

Then read this task fully and create the required checklist.

Read minimally:
1. `CHAT_CONTEXT.md`;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. accepted KOF XV diagnostic report;
4. `PROJECT_DECISIONS.md` current Taste/Deep/ranking/explanation decisions;
5. relevant routes in `PROJECT_ROUTES.md`;
6. `config/execution_ownership_contract.json`;
7. current Deep/PASS2 result schema and worker prompt;
8. current Deep ingest/validation/state materialization;
9. `scripts/progressive_pass2.py`;
10. `scripts/progressive_personalization.py`;
11. `scripts/refine_visual_ranking.py` and current score path;
12. `config/final_ranking_policy.json`;
13. `scripts/card_explanation_policy.py`;
14. base/final visual producers and card explanation validators;
15. focused current KOF XV Deep/Dossier/Fast records;
16. only the tests needed for this alignment.

Do not reconstruct unrelated history.

## Architecture preflight — mandatory before writes

Record and prove:

1. Which exact semantic fields currently determine each Deep Taste factor and how they feed the deterministic personal score.
2. Whether current Deep result schema already contains enough structured evidence-to-factor linkage to enforce the user invariant.
3. Which layer must own semantic judgment of whether a positive is specific/personal/grounded. This must remain the Deep semantic worker + GitHub validation boundary, not browser heuristics.
4. Which parts can be validated deterministically by GitHub (identity, evidence refs, factor bindings, completeness, provenance) and which semantic assertions are produced by Deep.
5. How visible explanation can be projected from the accepted structured findings without a brittle lexical whitelist.
6. How to handle existing authoritative Deep results that predate the new explainability binding:
   - reuse them only if exact sufficient linkage can be proven deterministically from already accepted structured data;
   - otherwise mark them for a bounded existing-Deep-worker migration/reanalysis path rather than inventing bindings or silently grandfathering hidden score reasons.
7. Why this introduces no second semantic worker, scheduler, queue, retry owner or browser authority.

If the current architecture cannot support this invariant without a material product-policy choice, stop with `needs_user_decision` and state the exact choice.

## Required implementation behavior

### A. Structured score-bearing findings

Replace the current loose relationship between free-text `positive_evidence` and numeric `taste_factors` with an explicit accepted structure sufficient to trace score reasons.

The exact schema design is the worker's bounded implementation decision, but it must provide stable linkage among:
- a specific semantic finding/reason;
- one or more Taste factors;
- candidate/Dossier evidence refs;
- personal/profile evidence or preference binding where personalization is claimed;
- exact Deep result identity/binding;
- whether the finding supports, lowers, or qualifies the factor.

Do not create per-AppID special cases.

### B. Deep semantic quality gate

Update the canonical Deep worker/result contract so completed Deep cannot claim a materially positive personalized factor from only generic or commercial language.

The semantic worker must produce specific grounded reasons as part of the same result that carries the factor assessment.

GitHub ingest/validation must fail closed on structurally missing, stale, wrong-product, wrong-profile, unbound or internally inconsistent score evidence.

Do not pretend deterministic code can semantically judge arbitrary prose beyond what can actually be validated. Semantic specificity remains a Deep responsibility; structural/provenance consistency is GitHub's responsibility.

### C. One truth for score and explanation

The visual explanation path must consume the accepted structured score-bearing findings.

Do not use a small lexical/template whitelist as the authority deciding whether a valid Deep reason exists.

A deterministic renderer may:
- select the most material accepted reasons;
- use worker-provided display-safe text or a generic deterministic formatting layer;
- deduplicate and limit rows;
- preserve exact provenance.

But it must not:
- invent a reason not present in accepted semantic findings;
- convert commercial/rank signals into personal praise;
- drop a valid finding only because its vocabulary is unfamiliar.

### D. Full rating picture

The card must make the personal rating intelligible.

At minimum, the final payload must allow the user to see:
- the main grounded positive reasons responsible for the strongest positive personal contributions;
- the important grounded negative/caution reasons that lower or qualify the assessment;
- the existing score/component information needed to understand that purchase value is separate from personal fit.

Do not redesign the whole card unnecessarily. Reuse existing `Почему может зайти`, cautions/risks and score breakdown where possible.

The visible reasons do not need to enumerate every tiny contribution, but **no material hidden positive contribution may exist with no accepted user-visible reason behind it**.

### E. Historical/current Deep compatibility

Do not silently declare old Deep results compliant.

Build a deterministic compatibility audit for current authoritative Deep results.

For each current result:
- compliant if the required score-evidence linkage is already provable;
- otherwise noncompliant/current-migration-needed.

If semantic reanalysis is required:
- use only the existing Progressive Deep semantic worker architecture;
- prepare a finite exact GitHub-owned migration/recovery authority;
- preserve old accepted result/history until a new result is successfully accepted according to current canonical migration rules;
- do not execute semantic reanalysis in this developer chat;
- do not create or modify a Scheduled Task.

The implementation must make the migration state visible/accounted for rather than silently hiding affected games.

### F. KOF XV pinned acceptance

KOF XV / AppID 1498570 is the pinned regression.

Acceptance must prove:
- its accepted Deep score-bearing positives are either structurally migrated from exact existing proof or queued for exact semantic reanalysis under the new contract;
- after a compliant result exists, the card displays grounded reasons tied to the same factor evidence that contributes to its personal score;
- roster/team experimentation and fighting/mastery evidence are not rejected merely because they do not contain old whitelist words such as `parry` or `dodge`;
- if the new semantic assessment changes its factor values/score, the site reflects the new accepted truth rather than pinning the historical 68.9.

## Required regressions

At minimum:

1. **KOF XV positive linkage**
   - specific fighting/mastery + roster/team evidence;
   - valid factor linkage;
   - visible reason generated from same accepted finding;
   - exact provenance preserved.

2. **Generic praise rejected at semantic/result boundary**
   - examples such as “great fighting game”, “popular”, “highly rated”, “75% off”, “ranked #3” cannot support a personal factor.

3. **Hidden-score prevention**
   - a material positive factor with no valid linked user-visible reason fails validation / cannot become authoritative compliant Deep.

4. **Vocabulary independence**
   - a valid grounded reason with previously unseen but legitimate game mechanics is not rejected merely because a renderer lacks a keyword template.

5. **Wrong-product/profile/evidence refs**
   - remain fail-closed.

6. **Negative/caution integrity**
   - grounded negative/caution reasons remain linked and visible; no new double penalty.

7. **Ranking formula stability**
   - weights/formula and Deep-first stage order remain unchanged unless the accepted semantic factor values themselves change.

8. **Purchase separation**
   - price/history/purchase verdict cannot create or erase personal-fit reasons.

9. **Historical compatibility audit**
   - old result without required linkage is explicitly noncompliant/migration-needed rather than silently treated as fully explainable.

10. **No browser semantic inference**
   - browser renders producer-owned explanation; it does not decide whether a reason is valid.

11. Existing relevant Progressive PASS2, Dossier, ranking, card explanation, translation and visual freshness suites remain green.

12. No new scheduler/queue/retry owner and no Scheduled Task change.

## Production / migration acceptance

Implementation PR may merge only after required validations.

If the new contract requires semantic migration:
- implementation acceptance must prove the finite migration authority/state is correctly prepared;
- do not claim all current cards fixed until the existing Deep semantic worker has actually produced and GitHub has accepted compliant results;
- report exact count of current authoritative Deep results that are already compliant vs require migration;
- identify KOF XV exact migration state.

After compliant KOF XV data exists and normal visual publication runs, verify the canonical visual and Pages staging show the score-linked reasons.

Preserve concurrent Dossier/Deep/translation production writes. Never reset current semantic state to task fixtures.

## Hard prohibitions

Do not:
- solve this by only adding more phrases to `_positive_reason()`;
- display raw unvalidated free text merely to make cards non-empty;
- let a hidden/invalid reason still raise the score;
- weaken exact Deep/Dossier/profile provenance;
- infer personal reasons from price, discount, review score, popularity, rank or purchase verdict;
- invent factor-to-evidence linkage in deterministic code when it requires semantic judgment;
- manually rewrite current Deep results;
- rerun semantic Deep work from this developer chat;
- change RANK-013 stage ordering;
- create a new semantic worker, scheduler, recurring queue or retry daemon;
- create/change/pause/resume Scheduled Tasks.

## Delivery

Implement on a dedicated branch/PR under current worker protocol.

Before merge:
- reconcile with fresh `main`;
- preserve all concurrent production writes;
- run focused + existing validations;
- merge only if clean and current protocol permits.

Write:
`reviews/worker_reports/deep-score-evidence-explainability-alignment-01.md`

Required report sections:
1. `Task`
2. `Architecture preflight`
3. `Previous mismatch`
4. `Canonical score-evidence model`
5. `Deep contract / semantic quality gate`
6. `GitHub deterministic validation`
7. `Explanation projection`
8. `Historical compatibility / migration`
9. `KOF XV pinned regression`
10. `Validation`
11. `Production / migration acceptance`
12. `Unresolved`
13. `Status`
14. exact PR/commit/run/artifact refs
15. `Recommended next step` — exactly one bounded next step
16. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `migration_prepared_needs_semantic_execution`
- `needs_fix`
- `needs_user_decision`
- `blocked`

Do not start another task after this one.
