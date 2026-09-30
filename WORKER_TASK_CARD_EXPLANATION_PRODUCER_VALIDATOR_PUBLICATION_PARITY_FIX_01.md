# WORKER TASK — card explanation producer / validator publication parity fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Task ID: `card-explanation-producer-validator-publication-parity-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/card-explanation-producer-validator-publication-parity-fix-01.md`

## User requirement

Fresh Dossier and Deep truth must be able to reach the live site without weakening the protection that prevents invented or ungrounded personalized reasons.

Do **not** fix the defect by inserting the literal word `тебе` into every explanation or by disabling the explanation validator.

The validator must trust the canonical structured Deep provenance introduced by PR #128 rather than a vocabulary heuristic.

## Mandatory START gate

Before implementation:

1. Read current `CHAT_PROTOCOL.md` from `main` fully and execute its START gate.
2. Read this task fully.
3. Read current `DIRECTOR_TASK_BOARD.md` current-state section.
4. Read the accepted reports:
   - `reviews/worker_reports/deep-score-evidence-explainability-alignment-01.md`
   - `reviews/worker_reports/stale-live-statistics-publication-diagnostic-01.md`
5. Refresh from current `main` immediately before writes.
6. Preserve all concurrent Dossier, Deep, translation, production and publication state.

Do not start any other task.

## Confirmed defect

The stale live Statistics diagnosis proved:

- current Dossier/Deep canonical truth is newer than the live site;
- routing correctly detects that a full progressive visual rebuild is required;
- fresh visual candidate generation succeeds;
- publication then fails at `scripts/validate_card_explanations.py`;
- canonical visual persistence is skipped;
- Pages therefore keeps deploying/staging the last successful old canonical visual.

The failing validator rule currently contains:

`if 'теб' not in reason.casefold(): positive lacks explicit personal-taste link`

This is incompatible with the structured Deep explainability architecture merged in PR #128.

PR #128 established `DEEP-SCORE-EVIDENCE-V1`:
- accepted Deep score findings;
- exact candidate/Dossier evidence refs;
- exact pinned-profile evidence refs;
- exact factor impacts;
- exact semantic/accepted-state binding;
- visible Deep reasons are projected from those accepted score findings rather than lexical reinterpretation.

Therefore a Deep reason can be genuinely personalized and score-linked without containing the literal substring `теб`.

## Confirmed publication evidence

Last successful canonical visual:

- build run `36678188514` (#1007);
- canonical visual commit `2aca7915028057a9e8a7f0126c2d9d3d1744f7a2`;
- persisted visual blob `19925553e0fe9e090a012f982552e1bb8891b416`;
- generated at `2026-09-30T06:26:28.370489+00:00`.

First observed failing full build after that:

- run `36678293360` (#1012);
- candidate build succeeded;
- `Validate generated card explanations` failed;
- `CARD_EXPLANATION_VALIDATION=FAIL count=8`.

Latest diagnostic failing full build:

- run `36713360722` (#1094);
- fresh visual candidate build succeeded;
- card explanation validation failed with `count=60`;
- later material-binding and persistence steps were skipped.

Representative error:

`positive lacks explicit personal-taste link`

The current browser/Pages path is not the root cause.

## Architecture rule to preserve

For authoritative Deep linked-v1 explanations, the real personalization proof is structured provenance, not the wording of the Russian sentence.

A visible Deep positive is valid only when all required canonical structure proves:

1. source is an accepted `deep_score_finding`;
2. finding has a stable `finding_id`;
3. finding has score-factor impacts;
4. candidate/Dossier evidence refs are present and valid;
5. pinned-profile evidence refs are present and valid;
6. semantic binding is complete and exact;
7. binding belongs to the current card identity/generation;
8. score/explanation status permits the reason;
9. reason is not generic fallback;
10. reason is not commercial/ranking-only language.

The display sentence itself must not need a magic substring such as `теб` to prove personalization.

## Required implementation

### A. Split validation semantics by provenance source

Update card explanation validation so authoritative linked Deep positives are validated by their structured provenance.

For `effective_analysis_source=deep` with accepted linked `deep_score_finding` provenance:
- do NOT require literal `теб` in the display text;
- require the full structured accepted-state proof already defined by PR #128;
- retain generic-positive rejection;
- retain commercial/ranking-only rejection;
- retain exact family/generation/binding checks;
- retain evidence/profile refs;
- retain factor linkage.

For legacy/non-Deep paths:
- preserve existing compatibility/safety behavior unless a narrowly necessary change is proven;
- do not accidentally weaken older unstructured Taste explanation validation.

Do not convert every reason into Deep semantics.

### B. Producer / validator parity

Inspect the producer path that creates:
- `why_fit`;
- `why_fit_status`;
- `why_fit_provenance`.

Ensure the validator checks exactly the invariants the producer guarantees for accepted Deep score findings.

Do not create a second independent semantic interpretation layer.

If a producer bug is found in addition to the validator mismatch, fix it only when required for parity and document it.

### C. Fail closed on invalid provenance

A Deep positive with:
- missing profile evidence refs;
- missing candidate evidence refs;
- missing factor impacts;
- wrong family;
- wrong semantic generation;
- incomplete accepted-state binding;
- wrong provenance source;
- migration-required/unlinked status;

must still fail or remain hidden according to the canonical architecture.

Removing the lexical `теб` requirement must not make these cases pass.

### D. No text rewriting hack

Do not:
- prepend `Тебе понравится...`;
- inject `тебе` into worker text;
- rewrite all Deep findings to satisfy a regex;
- add a second list of accepted vocabulary.

The user explicitly wants semantic/provenance correctness, not phrase matching.

### E. Current production recovery

After implementation and merge, allow the **normal existing publication path** to rebuild/persist/deploy the visual.

Do NOT manually:
- trigger Build daily visual payload;
- trigger Pages deploy;
- replace canonical visual;
- edit `web/data/current.json`;
- bypass the validator.

The implementation merge/push and existing normal trigger graph may run automatically. Observing those automatic runs is allowed and required for acceptance.

If the normal existing trigger graph does not produce a build after merge, report that exact fact rather than manually triggering one.

### F. Freshness acceptance

After a successful normal post-merge publication, verify:

1. a fresh full visual candidate is built;
2. card explanation validation passes;
3. exact visual material binding passes;
4. a new canonical `data/production/visual/current.json` is persisted;
5. its material bindings reflect current Dossier/Deep inputs;
6. normal Pages deploy stages that canonical visual;
7. live/deployed Statistics are no longer the old screenshot snapshot.

Do not pin acceptance to historical counts because Dossier/Deep may advance concurrently.

Instead prove the published counts/timestamps correspond to the exact canonical material bindings used by the successful visual.

At minimum, prove they are not still the known stale snapshot:
- Dossier `60 / 200 / 6`, last record `2026-09-30T06:25:51Z`;
- Deep `41 / 37 / 4 / 7 / 206 / 8 / 221`, last record `2026-09-30T02:07:06Z`.

### G. Top-page “Скидки: обновлено” remains out of scope

Do not change the meaning or wording of:
`Скидки: обновлено 24 сент., 03:12`

The diagnostic proved it represents `source_mailing_updated_at_utc`, not visual/site freshness.

If UX wording should change later, that is a separate task.

## Required regression coverage

At minimum:

1. Linked Deep positive with valid candidate/profile/factor/semantic provenance and text WITHOUT `теб` -> PASS.
2. Same Deep text with missing profile refs -> FAIL.
3. Same Deep text with missing candidate refs -> FAIL.
4. Same Deep text with missing factor impacts -> FAIL.
5. Wrong family binding -> FAIL.
6. Wrong semantic generation -> FAIL.
7. Wrong/partial accepted-state binding -> FAIL.
8. Generic positive fallback -> FAIL.
9. Commercial/ranking-only positive -> FAIL.
10. Legacy unlinked Deep result cannot expose positive before migration/compliance.
11. Non-Deep legacy path retains its intended validation behavior.
12. KOF XV linked Deep reasons remain visible/valid independent of vocabulary.
13. Full visual build with current real canonical state passes card explanation validation.
14. Exact material freshness/binding regression remains green.
15. RANK-013 behavior unchanged.
16. Deep score-evidence explainability regression remains green.
17. Progressive PASS 2 core, backlog dispositions, execution ownership and package purchase value remain green.
18. No new scheduler, queue, retry loop or semantic worker.
19. No Scheduled Task changes.

## Concurrency / source-of-truth constraints

Dossier and Deep are actively advancing.

Immediately before merge:
- refresh/reconcile with current `main`;
- preserve newer production records;
- never restore an old visual/data snapshot over newer canonical truth;
- never pin tests to counts that are legitimately changing.

If merge reconciliation changes current production inputs, rerun the relevant deterministic validations on the reconciled head.

## Hard boundaries

Do NOT:
- run semantic Deep;
- run semantic Dossier;
- alter Deep/Dossier results;
- change Deep score semantics;
- change RANK-013;
- weaken structured provenance checks;
- bypass card explanation validation;
- manually run/redeploy publication workflows;
- change Service Worker/cache behavior;
- change translation semantics;
- change the top mailing-source timestamp semantics;
- create or modify Scheduled Tasks.

## Delivery

Use a dedicated implementation branch and PR.

Write:
`reviews/worker_reports/card-explanation-producer-validator-publication-parity-fix-01.md`

Required report sections:

1. Task
2. START / fresh-main reconciliation
3. Confirmed root cause
4. Deep linked-v1 validation rule
5. Legacy/non-Deep compatibility
6. Producer/validator parity
7. Regression coverage
8. Fresh-main merge reconciliation
9. Automatic post-merge visual build
10. Canonical visual persistence
11. Automatic Pages deployment
12. Published Statistics freshness
13. Unresolved
14. Exact PR/commit/run/artifact refs
15. Status
16. Recommended next step — exactly one bounded next action
17. Efficiency / reusable lesson

Allowed statuses:
- `complete_ready_for_director_acceptance`
- `implementation_complete_publication_pending`
- `needs_fix`
- `needs_user_decision`
- `blocked`

Do not start another task after this one.
