# Taste Dossier worker prompt V2 alignment fix 01

**Task:** `WORKER_TASK_TASTE_DOSSIER_WORKER_PROMPT_V2_ALIGNMENT_FIX_01.md`  
**Date:** 2026-09-23  
**Status:** `complete_ready_for_director_acceptance`

## Result

The canonical semantic worker prompt is aligned to the already-active non-blocking V2 Dossier worker index/runtime. The stale V1/`canonical_expected_sequence` traversal and contiguous-prefix blocking text was removed without changing evidence, privacy, exact-app, source, validation, create-only, or ownership semantics.

Architecture ownership remains unchanged: GitHub owns group state/order/validation/persistence/recovery/completeness and Scheduled ChatGPT remains the bounded create-only semantic candidate producer. No new queue, retry owner, scheduler, or recurring stage was created.

## FIX-01 — primary prompt V2 alignment

Implementation commit: `17eba7f5ba616e53d45ef63ec835d35a4eb60913`.

`config/taste_steam_review_dossier_worker_prompt.md` now:
- requires `TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2`;
- uses `normal_first_pass_complete`, `next_pending_sequence`, and `pending_group_sequences`;
- starts from the exact GitHub-projected next pending sequence;
- preserves exact snapshot/plan/descriptor/evidence-binding checks and fail-closed behavior;
- traverses only forward through still-pending sequences in the immutable plan during the same invocation;
- excludes accepted and `failed_or_invalid_pending_recovery` groups from normal first-pass work;
- preserves separate GitHub-owned failed-group recovery;
- contains no `canonical_expected_sequence` and no active V1 index requirement;
- describes independent per-group GitHub classification rather than the superseded global contiguous-prefix blocker.

No other semantic evidence/retrieval/privacy/exact-app sections were changed.

## FIX-02 — live anti-drift regression

Regression commit: `5e068f5ed4c97e6b9372b4d0b9fd6f2f6836b2d0`.

Added `test_gap08_live_worker_prompt_runtime_and_projection_are_v2_aligned` to `scripts/test_taste_steam_review_dossier_contract_gaps.py`, which is already executed by the production `Build pre-AI deterministic payload` validation surface.

The regression reads the live primary prompt, runtime prompt, canonical manifest, worker index, and current next-pending descriptor. It fails if the prompt/runtime regress away from V2 traversal, if `canonical_expected_sequence` returns, if live index/manifest progress disagree, or if runtime/evidence/descriptor bindings drift.

Validation:
- GitHub Actions run: `35875165680` (#184), event `push`, conclusion `success`;
- job: `107229124431`, conclusion `success`;
- step `Regression test fixed daily dossier snapshot control plane`: `success`;
- downstream existing step `Recompute Progressive PASS 2 eligibility from current canonical truth`: `success`;
- run #184's own post-validation atomic commit was `f454d364edff1854b45367477b7f40f610eb401e`; it contained no Dossier index/manifest delta because the overlapping prompt-triggered build had already refreshed that projection.

## FIX-03 — canonical binding/projection refresh

The worker prompt content hash is part of the canonical web-evidence compatibility binding and Dossier snapshot identity. Therefore the existing GitHub-owned build path canonically rebuilt the current Dossier projection; no snapshot/index/hash/progress file was hand-edited.

The prompt-change push triggered canonical build run `35875102006` (#183), job `107228855031`, conclusion `success`. Its job log proves the final rebased push `5e068f5e..2ba1ef1a  HEAD -> main`.

Canonical Dossier binding/projection refresh commit:
`2ba1ef1aa197c7ab0076b302df32ba6e55b22e57`
(parent: regression commit `5e068f5ed4c97e6b9372b4d0b9fd6f2f6836b2d0` after the workflow rebased onto concurrent fresh `main`).

A second overlapping push-triggered build, run `35875165680` (#184), then executed the newly added live anti-drift regression successfully. Its own atomic commit `f454d364edff1854b45367477b7f40f610eb401e` did not modify the Dossier worker index or manifest, confirming the projection was already current.

Current binding:
- worker prompt SHA-256: `c5773cc9aebe7fc4fb7a2bb9444bab4c35c5b2c63102f995b183def102b59ed7`;
- runtime prompt SHA-256: `bfa4a7b5fac60eceefab5ce7f6cb8a01f0dc31fe39e998f45e80c8ae3515fe35`.

The canonical build also refreshed ordinary deterministic pre-AI derived surfaces from then-current source truth. Its existing PASS 2 eligibility recomputation updated only the derived `progressive_pass2_work.json` projection in response to the new Dossier compatibility binding. No Fast/Deep source, contract, semantic state, attempt/result/receipt history, or execution behavior was modified, and no Fast/Deep execution was launched.

## FIX-04 — fresh-main proof

Fresh `main` after the canonical rebuild:

- primary prompt blob: `49d6a7e19e6b6f52aa75a0db96f30721db0e1895`;
- runtime prompt blob: `3ab7946cc5cc9241d8433155b85559a68226a4c9`;
- both prompts require V2 traversal fields and contain no `canonical_expected_sequence`;
- worker index blob: `9609b51181d4f97da89899f93bdb7b4b86849a8c`;
- manifest blob: `02bd3ba76fb29f5b8721d87e493ffe57c3b9fe7f`;
- index schema/version: `TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2` / `2`;
- snapshot: `bae494b435e752f23beea70ee238d7f480f45cf94d9d27e8827525bb4b67fc09`;
- prepared required: `560`;
- group count: `187`;
- accepted / failed / pending groups: `0 / 0 / 187`;
- `next_pending_sequence=1`;
- `normal_first_pass_complete=false`;
- `all_groups_accepted=false`;
- prepared-required SHA-256: `395257c5b5c730e02c6926b40e3f943fe25395732bc2fc40cd4a39dfb0d7d3a5`;
- group-plan SHA-256: `c350fb01f6a4f1dda90baf48e378de8dd13ac1d61711fcc73ae04518f4ee2a01`.

Current next descriptor is readable:
`data/production/pre_ai/taste_steam_review_dossier_worker_groups/bae494b435e752f23beea70ee238d7f480f45cf94d9d27e8827525bb4b67fc09/g000001.json`
(blob `833294fb749a59ca40a1fb3dad790080c24c9c62`), sequence `1`, appids `1000010, 1007040, 1018800`.

Index, manifest, and descriptor have equal current web-evidence bindings and matching snapshot/prepared/plan identities. The live regression also recomputes and verifies the worker-prompt binding and runtime-prompt hash.

The tracked current Dossier inbox contains no candidate artifacts. Accepted and failed group counts remained zero; no group was manually advanced. The canonical rebuild commit changed no canonical Dossier cache file and no Fast/Deep source/contract/state/attempt/result/receipt path.

## Prohibitions / non-actions

- Dossier Scheduled Task was not run by this worker.
- Dossier Scheduled Task settings were not changed.
- No external Scheduled Task API/action was invoked.
- No Dossier candidate was created manually or fabricated.
- No Dossier canonical progress/state/count was manually edited.
- No failed group was reopened/retried.
- No Fast/PASS 1 or Deep/PASS 2 behavior was changed.
- No V1 contiguous-prefix ownership was restored.

## Exact refs

- task handoff state start: `d40ff48439c048e227d805813a430c3b9f3a5590`
- prompt implementation: `17eba7f5ba616e53d45ef63ec835d35a4eb60913`
- anti-drift regression: `5e068f5ed4c97e6b9372b4d0b9fd6f2f6836b2d0`
- canonical binding/projection rebuild run: `35875102006`
- canonical binding/projection rebuild job: `107228855031`
- atomic canonical projection/binding refresh: `2ba1ef1aa197c7ab0076b302df32ba6e55b22e57`
- live anti-drift validation run: `35875165680`
- live anti-drift validation job: `107229124431`
- post-validation atomic commit with no Dossier projection delta: `f454d364edff1854b45367477b7f40f610eb401e`
- task closure state: `b7682da8f928425dac9c9e0d512f0c03edf66b80`
- CURRENT_TASK provenance correction: `087a07509ce89c4584df15c04df5fe1c65b8bd7e`

All FIX-01..FIX-06 acceptance gates are satisfied once this durable report is committed and reread from `main`.
