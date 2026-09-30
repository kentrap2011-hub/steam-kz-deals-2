# Deep score evidence / explainability alignment 01 — worker report

## 1. Task

Task: `deep-score-evidence-explainability-alignment-01`.

Implementation PR: #128 — `Align Deep score evidence with card explanations`.

Branch: `fix/deep-score-evidence-explainability-alignment-01`.

Required invariant: Deep personal score contributions must be grounded in the same specific accepted semantic findings that can be projected as honest player-facing explanations. A reason that is too weak/unbound to support the visible explanation must not silently raise the score, and a valid grounded reason must not disappear because a renderer does not recognize its vocabulary.

Status: `migration_prepared_needs_semantic_execution`.

## 2. Architecture preflight

Ownership remains unchanged:

- Deep semantic worker owns semantic judgment: candidate-specific meaning, profile match, factor values, finding text and whether evidence supports/lowers/qualifies a factor.
- GitHub remains control-plane owner: work scope/order, immutable profile/Dossier bindings, run-start confirmation, structural validation, persistence, migration accounting and publication.
- deterministic producer/renderer only projects already accepted structured findings; browser is not a semantic authority.
- no new semantic worker, scheduler, recurring queue, retry daemon or Scheduled Task was created.
- RANK-013/final ranking formula and weights were not changed. `config/final_ranking_policy.json` blob is identical on main and the implementation branch: `f472b74ef36abb15ac8bbdd1a21d8eac802c130c`.

The existing schema was insufficient before this task because numeric `taste_factors` and free-text `positive_evidence` had no exact factor-to-evidence/profile linkage. The card path independently applied a lexical whitelist, so scoring and explanation could disagree.

## 3. Previous mismatch

Accepted diagnosis reproduced the KOF XV failure mode:

- authoritative Deep could persist high `taste_factors`;
- `priority_ranking` consumed those normalized factors deterministically;
- `card_explanation_policy._positive_reason()` independently recognized only a small set of textual patterns;
- therefore a score-bearing positive could affect personal score while producing no visible `why_fit`.

This was not presentation-only: the canonical result contract allowed factor numbers without structured proof linking each score-bearing factor to exact candidate and personal evidence.

During PR validation an additional regression was found in `Progressive async traversal + invalid transport regression`. Exact root causes were:

1. the new object-valued `score_evidence_contract` had been placed in `IMMUTABLE_RESULT_FIELDS`, whose scalar identity loop compares through `str(...)`; JSON round-tripping can reorder object keys, so equal objects were falsely rejected as identity mismatches;
2. `normalize_score_findings()` called existing `_bound_dossier()` as if it returned a record wrapper, although that helper returns the Dossier document directly;
3. test fixtures initially omitted a positive observation and did not faithfully echo the new score-evidence binding;
4. legacy/invariant test helpers initially assumed only the older PPD-010 migration could pause ordinary Deep work.

The final implementation keeps invalid-transport protection strict: structured `score_evidence_contract` equality is validated directly, while scalar immutable identity remains in the scalar comparison path.

## 4. Canonical score-evidence model

New contract: `DEEP-SCORE-EVIDENCE-V1`.

For newly authorized Deep `analyzed_fit` work, `score_findings[]` is required. Each finding carries:

- `finding_id`;
- Russian display-safe `text_ru`;
- exact Dossier `candidate_evidence_refs`;
- exact pinned-profile `profile_evidence_refs` with JSON pointer/value hash and match explanation;
- `factor_impacts[]` binding the finding to one or more of the five normalized Taste factors, with `supports|lowers|qualifies` and exact normalized value.

All five score-bearing factors must be covered. At least one supporting finding is required for `analyzed_fit`. Generic praise and commercial/ranking language are rejected by the result boundary.

The same accepted `score_findings` are persisted into canonical Deep state and projected into the semantic Taste entry.

## 5. Deep contract / semantic quality gate

`config/progressive_pass2_worker_prompt.md` now requires the existing Deep semantic worker to produce specific, grounded score findings whenever the frozen work item contains the score-evidence contract.

If a factor cannot be responsibly connected to exact candidate evidence and pinned-profile evidence, the worker must not invent a number/reason; it must return a truthful incomplete result.

For the finite historical migration, prior factor values and the old fit verdict are historical context only, not values to preserve. A completed replacement may lower factors or change the overall outcome if the frozen evidence supports that result.

No semantic Deep execution was performed in this developer chat.

## 6. GitHub deterministic validation

GitHub validation now fail-closes on:

- missing/empty score findings for score-bound `analyzed_fit`;
- missing factor coverage;
- factor/value mismatch;
- out-of-range Dossier refs;
- missing/malformed pinned-profile refs;
- duplicate refs/findings;
- generic praise;
- commercial/ranking-only explanation text;
- support claims without positive/mixed Dossier evidence;
- lowering/qualifying claims without negative/mixed/conflict evidence;
- wrong score-evidence/migration identity.

The async invalid-transport regression remains strict. Final validated behavior accepts the exact confirmed frozen run result while still rejecting stale/wrong-authority transport, and sibling traversal remains asynchronous.

## 7. Explanation projection

For authoritative Deep results with linked score evidence:

- positive card reasons come directly from accepted supporting `deep_score_findings`;
- score qualifiers can be shown through the existing caution surface;
- existing grounded negative assessment remains independent;
- confirmed negative risks still use the existing canonical risk-code scoring path;
- cautions and score qualifiers do not create a second penalty.

The Deep path no longer relies on the legacy lexical positive whitelist to decide whether a valid reason exists. Non-Deep/legacy paths retain their existing compatibility behavior.

## 8. Historical compatibility / migration

Historical current Deep-fit results were not silently grandfathered.

Finite migration manifest:

- path: `data/control/progressive_pass2_score_explainability_migration_manifest.json`;
- blob SHA: `6ce88bf7ff569eb948b19c424ba0a7314e9fb0d2`;
- migration ID: `deep-score-evidence-explainability-alignment-01`;
- frozen authority commit: `7beb2624e8a659f4bdb311f64c4534a7af844263`;
- frozen at: `2026-09-30T03:35:38Z`;
- target count: 43 prior authoritative fit results;
- already-linked fit count: 0;
- prior authoritative not-fit results outside positive-score migration: 4.

Migration uses the same existing Progressive Deep worker and the same `progressive_pass2_work.json` control-plane path. Ordinary Deep work is paused without consuming its attempts while this finite migration is active, then resumes. Incomplete migration attempts do not displace the prior completed revision. No second queue/retry owner was created.

## 9. KOF XV pinned regression

KOF XV / AppID `1498570` is migration sequence 34.

Exact migration target:

- target ID: `deep-score-explainability-01:game:1498570:14dbe354ac94de42`;
- prior authorization: `14dbe354ac94de42af2204527b3733f41ea9a1d5a856b79383673da18eaba117`;
- prior accepted at: `2026-09-29T11:32:43+00:00`.

Regression coverage proves that:

- fighting/mastery evidence using hops, meter management, cancels and chained supers can become a visible accepted score reason without requiring old whitelist words such as `parry` or `dodge`;
- roster/team experimentation and identity evidence can be linked to their factors and displayed;
- the single-player limitation remains a qualifier/caution rather than an invented second risk penalty;
- all five factor contributions require linked findings;
- generic praise and invalid Dossier refs fail closed.

The migration has been prepared but not semantically executed, so this report does not claim KOF XV's production card is already repaired.

## 10. Validation

Validated implementation head before report-only commit: `d67d6603a73dc9f627a4f370f1108e9e7d225500`.

Required GitHub Actions on that head:

- Validate Progressive PASS 2 core — run `36676280595` / #490 — **success**;
- Validate execution ownership — run `36676280614` / #249 — **success**;
- Validate backlog dispositions — run `36676280585` / #1485 — **success**;
- Validate package purchase value — run `36676280584` / #66 — **success**.

PASS 2 core run includes successful:

- Visual material freshness regressions;
- Progressive async traversal + invalid transport regression;
- Deep parallel frozen-start regression;
- Progressive profile semantic identity stability regression;
- PASS 2 core regression;
- PASS 2 Dossier integration regression;
- Dossier/Deep release-year identity compatibility;
- Deep balanced negative assessment regression;
- Deep legacy full reanalysis regression;
- Deep score evidence explainability regression;
- PASS 2 canonical-writer staging regression;
- PASS 1 regressions/staging;
- Progressive personalization;
- Deep-first final-score ordering;
- staged projection accounting;
- unresolved-row preservation;
- visual activation routing;
- UI provenance;
- active production eligibility recompute without consuming attempts.

## 11. Production / migration acceptance

Implementation is ready to merge, but semantic migration remains outstanding by design.

After merge, the existing GitHub-owned Deep work projection can expose the finite `score_explainability_migration` to the existing Progressive Deep semantic worker. This developer chat did not submit semantic results, alter scheduler settings, or process the 43-item semantic backlog.

No claim is made that current production cards already contain linked reasons. That becomes true per game only after the existing semantic worker produces a compliant result, GitHub accepts it, and normal visual publication projects it.

## 12. Unresolved

One intentional unresolved item remains: the 43 historical fit targets have not yet been semantically migrated. KOF XV is among them.

This is not an implementation defect and does not require a new architecture. It requires execution of the already-prepared finite work by the existing Progressive Deep semantic worker after the implementation is merged.

## 13. Status

`migration_prepared_needs_semantic_execution`

## 14. Exact PR / commit / run / artifact refs

- PR: `#128` — `Align Deep score evidence with card explanations`;
- branch: `fix/deep-score-evidence-explainability-alignment-01`;
- validated implementation head: `d67d6603a73dc9f627a4f370f1108e9e7d225500`;
- async transport production fix: `fc5e358f60c4e845ab417bdd737cc52c5f2c1826`;
- bound-Dossier score finding fix: `85aa9fa495d465880e8e88881109f8489af9f053`;
- legacy migration regression compatibility: `f2ded0930b58a13644173169c2d5336e0fbe867a`;
- KOF caution-only assertion correction: `589c373f9fd1aedd18860d8553b5509adffa32d5`;
- final projection invariant correction: `d67d6603a73dc9f627a4f370f1108e9e7d225500`;
- PASS 2 validation run: `36676280595`;
- execution ownership run: `36676280614`;
- backlog dispositions run: `36676280585`;
- package purchase value run: `36676280584`;
- migration manifest: `data/control/progressive_pass2_score_explainability_migration_manifest.json`;
- migration manifest blob: `6ce88bf7ff569eb948b19c424ba0a7314e9fb0d2`;
- migration authority: `7beb2624e8a659f4bdb311f64c4534a7af844263`;
- KOF XV target: `deep-score-explainability-01:game:1498570:14dbe354ac94de42`.

## 15. Recommended next step

After PR #128 is merged, run the existing Progressive Deep semantic worker against the GitHub-prepared finite `score_explainability_migration` manifest; do not create or modify any Scheduled Task, queue, retry mechanism or semantic worker.

## 16. Efficiency / reusable lesson

Structured immutable objects must not be routed through scalar/string identity comparison. Compare structured bindings canonically/structurally and keep scalar identity tuples scalar-only. Regression assertions that depend on transport acceptance should include the rejection receipt in their failure message so the exact fail-closed reason is visible immediately.
