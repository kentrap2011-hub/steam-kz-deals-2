# Card explanation producer / validator publication parity fix 01 — worker report

## 1. Task

Task: `card-explanation-producer-validator-publication-parity-fix-01`.

Repository: `kentrap2011-hub/steam-kz-deals-2`.

Source of truth: `main`.

Implementation PR: #132 — `Validate linked Deep card reasons by provenance`.

Implementation branch: `fix/card-explanation-producer-validator-publication-parity-01`.

Current implementation head: `9b2c094aaa1c868162e2e6e269a92789b4dde131`.

Status: `complete_ready_for_director_acceptance`.

PR #132 was reconciled, validated and merged. Its first normal post-merge full visual build exposed a second producer/validator parity mismatch on the existing caution surface; bounded follow-up PR #136 fixed that mismatch. The following normal full visual build, canonical persistence and Pages deployment all succeeded.

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
16. KOF XV accepted linked Deep reasons remain valid without vocabulary dependence;
17. valid linked Deep score qualifier on the caution surface under `completed_no_relevant_negative` -> PASS;
18. score qualifier missing profile refs -> FAIL;
19. score qualifier carrying `supports` impact -> FAIL;
20. score qualifier with partial accepted-state binding -> FAIL.

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

PR #132 merged as `a225989b2a914e580114a5ec6212ae1486516af8`.

Its first normal push-triggered visual build `36855413554` / #1102 built a fresh candidate but exposed a second parity mismatch: four visible score qualifiers used producer-owned provenance `deep_score_finding_qualifier`, while the validator accepted only `deep_dossier_caution`.

That bounded mismatch was fixed in follow-up PR #136:

- PR: `#136` — `Accept linked Deep score qualifiers on caution surface`;
- branch: `fix/card-explanation-score-qualifier-validator-parity-01`;
- validator change: `015f264c84f60ee3c18f42b7f0a59dde89f378a9`;
- regression coverage: `600063f62d32c0e883ef24ebab702c027832199a`;
- validated head: `ddb3bd94448400a696c4dc876f0e6d2f5156ed23`;
- PASS 2 PR run `36855825768` / #547 — **success**;
- backlog PR run `36855825765` / #1532 — **success**;
- merge: `7a0b6d87b38c23afe3fee116c8425ff336eaf230`.

The follow-up did not reinterpret qualifiers as negative risks. It accepts `deep_score_finding_qualifier` only when the card is `linked_v1`, the finding has only lowering/qualifying score impacts, and candidate/profile/accepted-state provenance is complete. Existing `deep_dossier_caution` continues to require its own negative-assessment status.

The next normal push-triggered visual build:

- run `36855944330` / #1103 — **success**;
- fresh candidate generation — **success**;
- `CARD_EXPLANATION_VALIDATION=PASS`;
- `VISUAL_MATERIAL_BINDING=pass`;
- generated visual: 219 visible items, with the current progressive projection;
- no manual workflow dispatch was used.

## 10. Canonical visual persistence

Build #1103 persisted the fresh canonical visual through the normal workflow:

- canonical commit: `0cd51fb46182561c8cbd237bb630a870654db99b` — `Refresh daily visual payload`;
- canonical `data/production/visual/current.json` blob: `a18d12092fe6fe0aa9c22d8f2c927ea89549e0b3`;
- generated at: `2026-10-01T11:32:18.179861+00:00`;
- exact material binding validation passed before commit.

The published production contract binds the visual to current canonical sources, including:

- chatgpt payload blob `88102c2b1a7d22765e24303a2d41b5d499642566`;
- store snapshot blob `f7beff661139375f24604428737a6a6bfed673bd`;
- family graph blob `bf8a22c71cc9be50446c82d6949906cd9e586223`;
- history snapshot blob `f122832fa9d9223671d45c914a4464874f3c5d5e`;
- Dossier work blob `6a71928c4f62e4941656ebc1b8b0a0707b7eb027`;
- PASS 2 state blob `d90b004de91c4eaaf23225c1edf15f4919198071`.

Those blob IDs match the current files on `main`.

## 11. Automatic Pages deployment

The normal `workflow_run` trigger started Pages deployment automatically:

- Deploy visual mailing run `36856010448` / #1139 — **success**;
- Pages artifact ID: `11157892993`;
- Pages build version: `0cd51fb46182561c8cbd237bb630a870654db99b`;
- environment URL: `https://kentrap2011-hub.github.io/steam-kz-deals-2/`;
- GitHub Pages reported deployment success.

The uploaded Pages artifact contains `web/data/current.json`. Direct inspection of that exact artifact produced Git blob SHA:

`a18d12092fe6fe0aa9c22d8f2c927ea89549e0b3`.

That exactly equals the canonical `data/production/visual/current.json` blob, proving the deployed payload is the newly persisted canonical visual, not an older staging copy.

The existing freshness receipt remains truthful to its separate semantics and reports `degraded/no_fresh_build reason=deterministic_refresh_preserved_semantic_history` with `material_binding=exact`; this does not contradict the proven full visual rebuild/persistence/deploy above.

## 12. Published Statistics freshness

The deployed Pages artifact no longer contains the known stale Statistics snapshot.

Published Dossier values are now:

- total current scope: `228`;
- accepted: `64`;
- pending: `164`;
- failed/recovery: `0`;
- last write: `null` under the current snapshot semantics.

Published Deep values are now:

- total current coverage target: `222`;
- first-pass attempted: `60`;
- authoritative completed: `51`;
- fit: `48`;
- not-fit: `3`;
- incomplete/recovery: `9`;
- waiting for Dossier: `162`;
- ready/pending: `0`;
- normal first-pass remaining: `162`;
- remaining until all authoritative: `171`;
- last write: `2026-09-30T16:35:28+00:00`.

Therefore the deployed payload is not the old stale snapshot:

- old Dossier: `60 / 200 / 6`, last record `2026-09-30T06:25:51Z`;
- old Deep: `41 / 37 / 4 / 7 / 206 / 8 / 221`, last record `2026-09-30T02:07:06Z`.

The top-page `Скидки: обновлено 24 сент., 03:12` semantics remain unchanged as required. The deployed payload still carries `source_mailing_updated_at_utc=2026-09-23T23:12:47.031485+00:00`; that field is not the visual publication timestamp.

## 13. Unresolved

No blocker remains for this task.

The original positive-reason lexical mismatch and the follow-up score-qualifier caution mismatch are both fixed and regression-covered. The normal build/persist/deploy chain completed successfully.

## 14. Exact PR/commit/run/artifact refs

Primary implementation:

- PR #132 — `Validate linked Deep card reasons by provenance`;
- original branch: `fix/card-explanation-producer-validator-publication-parity-01`;
- reconciled main anchor: `6b7076258713d5997d32a1868a37ac1ff7f89f9e`;
- reconciled code head: `f2bfe892a157501cff69fac53e131ece0afadd85`;
- final PR #132 metadata head: `e7c7379d3fcc9f1bd64212dd71d0804ad91126a4`;
- PR #132 merge: `a225989b2a914e580114a5ec6212ae1486516af8`;
- final pre-merge PASS 2: `36855327276` / #544 — success;
- final pre-merge backlog: `36855327307` / #1530 — success.

Bounded post-merge parity follow-up:

- PR #136 — `Accept linked Deep score qualifiers on caution surface`;
- branch: `fix/card-explanation-score-qualifier-validator-parity-01`;
- validator commit: `015f264c84f60ee3c18f42b7f0a59dde89f378a9`;
- regression commit: `600063f62d32c0e883ef24ebab702c027832199a`;
- validated head: `ddb3bd94448400a696c4dc876f0e6d2f5156ed23`;
- PR PASS 2: `36855825768` / #547 — success;
- PR backlog: `36855825765` / #1532 — success;
- merge: `7a0b6d87b38c23afe3fee116c8425ff336eaf230`;
- post-merge PASS 2: `36855944331` / #548 — success;
- post-merge backlog: `36855944325` / #1533 — success.

Publication:

- first PR #132 post-merge build: `36855413554` / #1102 — failed on qualifier parity, no persistence;
- successful normal full visual build: `36855944330` / #1103;
- canonical visual commit: `0cd51fb46182561c8cbd237bb630a870654db99b`;
- canonical visual blob: `a18d12092fe6fe0aa9c22d8f2c927ea89549e0b3`;
- Pages deploy: `36856010448` / #1139 — success;
- Pages artifact: `11157892993`;
- Pages build version: `0cd51fb46182561c8cbd237bb630a870654db99b`;
- deployed `web/data/current.json` Git blob: `a18d12092fe6fe0aa9c22d8f2c927ea89549e0b3`.

No manual build/deploy, Deep/Dossier semantic execution, ranking change, scheduler/retry-owner change or Scheduled Task change was used for acceptance.

## 15. Status

`complete_ready_for_director_acceptance`

The producer/validator parity defect is fixed end to end. Both required PR validations and the normal post-merge visual publication chain succeeded, and the deployed Pages payload is byte-identical at Git-blob level to the newly persisted canonical visual.

## 16. Recommended next step — exactly one bounded next action

Director accepts this completed task and closes the card-explanation publication-parity work item.

## 17. Efficiency / reusable lesson

For contract-backed semantic output, producer and validator should share one structural binding definition. Phrase-level heuristics such as requiring `теб` are appropriate only for legacy text-derived evidence; once an accepted structured provenance contract exists, duplicating personalization semantics as a later lexical rule creates false publication failures.

A second reusable lesson is that a shared UI surface may carry more than one canonical provenance subtype. Validator logic must validate each producer-owned subtype by its own contract instead of assuming that every `cautions` row is a negative-assessment finding. Finally, production-state regression tests must distinguish immutable historical facts from mutable current outcomes.
