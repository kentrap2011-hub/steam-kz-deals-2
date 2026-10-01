# Card explanation producer / validator publication parity fix 01 — worker report

## 1. Task

Task: `card-explanation-producer-validator-publication-parity-fix-01`.

Repository: `kentrap2011-hub/steam-kz-deals-2`.

Source of truth: `main`.

Implementation PR: #132 — `Validate linked Deep card reasons by provenance`.

Implementation branch: `fix/card-explanation-producer-validator-publication-parity-01`.

Current implementation head: `9b2c094aaa1c868162e2e6e269a92789b4dde131`.

Status: `implementation_complete_publication_pending`.

The implementation is complete on the dedicated branch and has been reconciled onto current `main`. The previously external PASS 2 blocker was fixed separately by PR #133. Fresh required PR validation is green; merge and normal post-merge publication verification are the remaining steps.

## 2. START / fresh-main reconciliation

The current `CHAT_PROTOCOL.md` START gate was completed before implementation.

Read before writes:

- `CHAT_PROTOCOL.md`;
- `CHAT_CONTEXT.md`;
- `WORKER_TASK_CARD_EXPLANATION_PRODUCER_VALIDATOR_PUBLICATION_PARITY_FIX_01.md`;
- current relevant state in `DIRECTOR_TASK_BOARD.md`;
- accepted report `reviews/worker_reports/deep-score-evidence-explainability-alignment-01.md`;
- accepted report `reviews/worker_reports/stale-live-statistics-publication-diagnostic-01.md`;
- `CURRENT_TASK.md`;
- relevant ownership contract and implementation routes.

The original fresh-main write anchor was:

`bf6e2b2288c745f5d2ed67ef73cdbfcec819e1cb`.

Before merge, PR #132 was reconciled with current `main@6b7076258713d5997d32a1868a37ac1ff7f89f9e` through merge commit `f2bfe892a157501cff69fac53e131ece0afadd85`. The compare then showed `behind_by=0`.

Immediately before the merge decision, `main` was refreshed again and remained exactly at the same commit. The implementation branch was six commits ahead and zero behind, with no concurrent main reconciliation required.

No Dossier, Deep, translation, visual, scheduler, retry or Scheduled Task production state was modified by this worker.

## 3. Confirmed root cause

The accepted stale-publication diagnostic was reproduced in code.

`scripts/validate_card_explanations.py` applied this legacy textual check to every visible positive reason:

`'теб' in reason.casefold()`.

PR #128 had already changed authoritative linked Deep explanations to use `DEEP-SCORE-EVIDENCE-V1`: the displayed text comes directly from an accepted `deep_score_finding` carrying structured candidate evidence, pinned-profile evidence, score-factor impacts and exact accepted-state provenance.

Therefore a semantically valid linked Deep finding could affect the accepted Deep score and be honestly projected to the card, yet fail the later publication validator only because its Russian display text did not contain the literal substring `теб`.

The failure was producer/validator incompatibility, not missing Dossier/Deep truth and not browser caching.

## 4. Deep linked-v1 validation rule

For a visible Deep positive with `score_explainability_status=linked_v1`, the implementation no longer treats a magic Russian substring as proof of personalization.

The canonical linked-Deep path now requires:

- `why_fit_status.has_described_fit=true`;
- `why_fit_status.grounding=grounded`;
- `score_explainability_status=linked_v1`;
- one provenance row per visible reason;
- provenance source `deep_score_finding`;
- non-empty `finding_id`;
- score-factor impacts containing at least one `supports` impact;
- exact candidate evidence refs;
- exact pinned-profile evidence refs;
- semantic source `progressive_pass2`;
- required accepted-state binding fields:
  - `semantic_generation_id`;
  - `profile_pin_sha256`;
  - `work_id`;
  - `family_id`;
  - `taste_subject_key`;
  - `appid`;
  - `taste_fingerprint`;
  - `candidate_context_sha256`;
  - `dossier_content_sha256`;
  - `authorization_id`;
  - `accepted_at_utc`;
- exact family match to the card;
- exact semantic-generation match to the card.

Generic fallback and commercial/ranking-only language checks remain fail-closed.

The implementation intentionally does not newly require `work_authority_commit` for this visible binding because the existing PR #128 linked-v1 producer does not guarantee that field for every accepted historical migration shape. The first CI attempt exposed that mismatch; the final implementation uses only the accepted-state fields already guaranteed by the current producer contract.

## 5. Legacy/non-Deep compatibility

Non-Deep/legacy explanation behavior is unchanged.

The old explicit textual compatibility guard still applies to non-linked-Deep reasons, including the existing `теб` requirement.

Legacy unlinked Deep with `migration_required` is still forbidden from exposing a positive reason.

No Fast/Taste lexical mapping, score semantics, ranking behavior, negative-risk behavior or migration eligibility was changed.

## 6. Producer/validator parity

The producer and validator now share the same linked-Deep required binding definition in `scripts/card_explanation_policy.py`:

`DEEP_SCORE_REQUIRED_BINDING_FIELDS`.

The producer uses `linked_deep_score_binding()` before emitting linked Deep reasons. If the required accepted-state binding is incomplete or has the wrong semantic source, the producer emits no linked Deep reason.

The validator checks the same required field set plus card-specific family/generation equality and visible reason/provenance parity.

This avoids a second semantic interpretation layer: the validator does not re-judge whether the Russian wording sounds personal. It validates the accepted structured proof that authorized the reason.

## 7. Regression coverage

Added to `scripts/test_deep_score_evidence_explainability.py`:

1. valid linked Deep positive with text containing no `теб` -> PASS;
2. missing profile refs -> FAIL;
3. missing candidate refs -> FAIL;
4. missing factor impacts -> FAIL;
5. no supporting factor impact -> FAIL;
6. wrong family binding -> FAIL;
7. wrong semantic generation -> FAIL;
8. partial accepted-state binding -> FAIL;
9. wrong provenance source -> FAIL;
10. generic positive fallback -> FAIL;
11. commercial/ranking-only positive -> FAIL;
12. `migration_required` linked Deep positive -> FAIL;
13. non-grounded Deep fit status -> FAIL;
14. incomplete producer binding -> reason hidden;
15. non-Deep legacy positive retaining the old textual rule -> PASS/FAIL as before;
16. KOF XV accepted linked Deep reasons remain valid without vocabulary dependence.

On PR head `9b2c094aaa1c868162e2e6e269a92789b4dde131`, Progressive PASS 2 run `36735554783` reached the changed regression and printed:

`DEEP_SCORE_EVIDENCE_EXPLAINABILITY=PASS migration_targets=43 kof_family=game:1498570 ...`.

The same workflow completed these preceding guards successfully:

- Visual material freshness regressions;
- Progressive async traversal + invalid transport;
- Deep parallel frozen-start;
- profile semantic identity stability;
- PASS 2 core regression;
- PASS 2 Dossier integration;
- Dossier/Deep release-year compatibility;
- Deep balanced negative assessment;
- Deep legacy full reanalysis;
- Deep score evidence explainability.

It then failed in the next, unrelated `Deep invalid not-fit contract loop regression`; see Unresolved.

Backlog dispositions on the same PR head passed in run `36735554878`.

RANK-013 and package/ranking files are absent from the PR diff.

No scheduler, queue, retry loop, semantic worker or Scheduled Task was added or changed.

## 8. Fresh-main merge reconciliation

Fresh-main reconciliation completed against:

- current `main`: `6b7076258713d5997d32a1868a37ac1ff7f89f9e`;
- prerequisite PR #133 merge: `b6019c11fa202c73e5470af3d2eb9a4b5900f476`;
- reconciled PR #132 head: `f2bfe892a157501cff69fac53e131ece0afadd85`;
- compare after reconciliation: `behind_by=0`;
- PR mergeability: true.

Only `CURRENT_TASK.md` overlapped with main changes since the old PR base; source implementation files did not. The reconciliation preserved current main and production records and added the PR implementation on top.

Fresh required validation on the reconciled head:

- Progressive PASS 2 core PR run `36855124640` / #542 — **success**;
- backlog dispositions PR run `36855124796` / #1528 — **success**;
- Visual material freshness regressions — **success**;
- Deep score evidence explainability regression — **success**;
- Deep invalid-not-fit contract loop regression — **success**.

Execution ownership and package-purchase validation scopes are unchanged by PR #132; the PR does not touch their watched contract/ranking/package paths.

## 9. Automatic post-merge visual build

Not applicable yet because PR #132 was not merged.

No Build daily visual payload workflow was manually triggered.

The task's required normal post-merge full visual candidate / card-validation acceptance therefore remains pending.

## 10. Canonical visual persistence

Not performed.

`data/production/visual/current.json` was not manually edited or replaced.

No claim is made that the stale canonical visual identified by the accepted diagnostic has been superseded.

## 11. Automatic Pages deployment

Not performed because there is no merged implementation and therefore no normal post-merge publication run to observe.

No Pages deployment was manually triggered.

## 12. Published Statistics freshness

Not yet accepted.

This worker does not claim the live/deployed Statistics have advanced beyond the known stale snapshot:

- Dossier `60 / 200 / 6`, last record `2026-09-30T06:25:51Z`;
- Deep `41 / 37 / 4 / 7 / 206 / 8 / 221`, last record `2026-09-30T02:07:06Z`.

The top-page `Скидки: обновлено 24 сент., 03:12` semantics were not changed.

## 13. Unresolved

No implementation/validation blocker remains before merge.

The prior unrelated PASS 2 blocker was repaired by PR #133, and the same current-state regression now passes on PR #132's reconciled validation run `36855124640`.

Remaining acceptance is runtime-only and must occur through the normal post-merge trigger graph:

- automatic full visual build;
- card explanation validation;
- exact material binding;
- canonical visual persistence;
- automatic Pages deployment;
- published Statistics freshness verification.

## 14. Exact PR/commit/run/artifact refs

Implementation:

- PR: #132 — `Validate linked Deep card reasons by provenance`;
- branch: `fix/card-explanation-producer-validator-publication-parity-01`;
- fresh-main anchor: `bf6e2b2288c745f5d2ed67ef73cdbfcec819e1cb`;
- pre-reconciliation implementation head: `9b2c094aaa1c868162e2e6e269a92789b4dde131`;
- reconciled validated head: `f2bfe892a157501cff69fac53e131ece0afadd85`;
- initial validator fix: `97f54a33fcf9e040ac243b7368477ab380b5d297`;
- task tracking: `a15c82bc753300ed562b4105cf0f82faf41d8d8b`;
- initial regression coverage: `7c9ccee8562f3981771e36767acc7267a847c6de`;
- producer binding parity: `486d3a2abf4831a53e5c0241e01ee92b27ecc03f`;
- validator binding parity: `04bc13f88c2155ac36c2334d9a2d4a6acbf600b7`;
- final regression correction: `9b2c094aaa1c868162e2e6e269a92789b4dde131`.

Validation:

- reconciled PASS 2 PR run: `36855124640` / #542 — success;
- reconciled backlog PR run: `36855124796` / #1528 — success;
- Deep score evidence explainability step — success;
- Deep invalid-not-fit current-state regression step — success;
- visual material freshness regression step — success;
- prior accepted ownership run: `36676280614` — success;
- prior accepted package purchase run: `36676280584` — success;
- last observed green main PASS 2 before current production-state advancement: `36697091309` / #524 — success.

No post-merge visual run, canonical visual commit, Pages run or Pages artifact exists for this unmerged task.

## 15. Status

`implementation_complete_publication_pending`

The implementation is reconciled with current main and required PR validation is green. Merge and normal automatic publication verification remain.

## 16. Recommended next step — exactly one bounded next action

Merge PR #132 at the validated reconciled head, then observe the existing automatic visual build and Pages deploy without manual workflow dispatch.

## 17. Efficiency / reusable lesson

For contract-backed semantic output, producer and validator should share one structural binding definition. Phrase-level heuristics such as requiring `теб` are appropriate only for legacy text-derived evidence; once an accepted structured provenance contract exists, duplicating personalization semantics as a later lexical rule creates false publication failures.

A second reusable lesson is that production-state regression tests must distinguish immutable historical facts from mutable current outcomes. Pinning a current entry forever to one workflow state makes unrelated PR validation fail as production legitimately advances.
