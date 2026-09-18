# Taste dossier semantic consistency gaps implement 01

## Task

- Task: `taste-dossier-semantic-consistency-gaps-implement-01`
- Mode: `IMPLEMENT / ACTIVATE / VALIDATE`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Source of truth: `main`

## Architecture preflight

Passed before implementation writes. GitHub remains the control plane for scope, immutable group plan, validation, persistence, recovery, stale quarantine, progress and completeness. Scheduled ChatGPT remains only the bounded semantic/data worker and immutable create-only candidate publisher. No second scheduler, retry/healing manager, queue, control-plane writer or validator authority was introduced.

## SCG reconciliation and final invariants

| Finding | Fresh-main status before change | Classification | Canonical invariant after task | Deterministic proof |
|---|---|---|---|---|
| SCG-01 parent source ↔ child feedback physical provenance | Open. Same-host Reddit child items could be bound to a different subreddit/thread parent; Steam discussion item could sit under an explicit reviews parent. | `implemented_now` | Every feedback item must belong to the physical surface represented by its parent source when that relationship is deterministically resolvable. Reddit subreddit/thread identity must contain the child; Steam review/recommendation and discussion surfaces cannot be cross-bound. Valid distinct items in one valid thread/surface remain allowed. | `scripts/test_taste_steam_review_dossier_semantic_consistency.py::test_scg01_wrong_parent_surface_rejected_and_same_thread_distinct_items_preserved` |
| SCG-02 source ↔ child temporal coherence | Open. A known old child item could inherit undated parent `recent/current_state` metadata. | `implemented_now` | A bound child with a known date older than the 365-day recent window cannot inherit `freshness=recent`/current-state support from an undated parent. A genuinely unknown child date preserves the pre-existing undated behavior; the dated-source `<=365 recent / >365 older` rule remains unchanged. | `scripts/test_taste_steam_review_dossier_semantic_consistency.py::test_scg02_old_known_child_cannot_be_laundered_by_undated_recent_parent_but_unknown_child_is_preserved` |
| SCG-03 top-level summary evidence binding | Open. `summary` was effectively free-form subject only to shape/privacy checks and could contradict structured evidence. | `implemented_now` | `summary` is a deterministic projection only: `Evidence summary: {observation_count} validated structured observations; consult observations and conflicts for supported findings.` It cannot add observation/conflict text or independent factual/evidence claims. | `scripts/test_taste_steam_review_dossier_semantic_consistency.py::test_scg03_summary_is_exact_structured_projection_and_cannot_add_claims` |
| SCG-04 exact duplicate conflicts | Open. A byte-equivalent valid conflict could be repeated and still pass individual checks. | `implemented_now` | Exact duplicate conflict objects are rejected deterministically, aligned with the existing exact duplicate observation guard. No semantic near-duplicate redesign was introduced. | `scripts/test_taste_steam_review_dossier_semantic_consistency.py::test_scg04_exact_duplicate_conflict_is_rejected` |
| SCG-05 worker-facing `overall_strength` semantics | Open as a generation-contract gap. Strict validation already derived `strong/moderate` from observations, but the active worker-facing schema/contract/prompt did not state that strong conflicts do not promote `overall_strength`. | `implemented_now` | Canonical derivation remains observation-based: `strong` requires at least one strong observation; `moderate` requires at least one moderate or strong observation. Conflict recurrence does not promote `overall_strength`. Strict validation was not weakened. | `scripts/test_taste_steam_review_dossier_semantic_consistency.py::test_scg05_strong_conflict_alone_does_not_promote_overall_strength` plus machine/prompt assertions in that test. |
| SCG-06 parent source language ↔ child feedback language | Partially closed by the prior language-binding fix: strict validator already rejected child `russian` under non-Russian-only parent and vice versa, but the exact parent↔child containment rule was still not fully worker-facing. | `implemented_now` | Child `russian` requires parent `russian|mixed`; child `non_russian` requires parent `non_russian|mixed`; `mixed`/`unknown` child adds no new containment rule. The existing strict meaning is unchanged and is now explicit in schema, evidence contract and worker prompt. | `scripts/test_taste_steam_review_dossier_semantic_consistency.py::test_scg06_parent_child_language_containment_is_worker_facing_and_strict` |

## Exact implementation changes

- Extended `config/taste_steam_review_dossier_schema.json` with summary, conflict-duplicate, overall-strength and provenance relationship invariants.
- Extended `config/taste_steam_review_dossier_web_evidence_contract.json` with canonical parent-item binding, temporal coherence, deterministic summary binding, conflict duplicate rule, observation-based overall-strength binding and parent-child language containment.
- Updated `config/taste_steam_review_dossier_worker_prompt.md` so Scheduled ChatGPT generation semantics match strict acceptance semantics.
- Extended the existing canonical `scripts/taste_steam_review_dossier_strict.py`; no second validator truth source was added.
- Added `scripts/test_taste_steam_review_dossier_semantic_consistency.py` covering SCG-01..SCG-06 exact audited counterexamples and positive controls.
- Updated shared/legacy test fixtures only where the new cross-object invariants made an old positive fixture internally contradictory.
- Added the semantic-consistency suite and execution-ownership validation to the existing focused dossier PR workflow.

## Strict validator / validator authority

The canonical strict validator was extended, not weakened. Existing rejection semantics for expired dossiers, physical source/item aliasing, item-level locator requirements, the 365-day freshness boundary, bidirectional `russian_attempt`, feedback-bound recurrence, aggregate Steam counts, Russian-rendered store metadata, compact-provenance privacy/content rules, compatibility binding, parallel buffering and maximal contiguous-prefix acceptance remain covered by the focused regression workflow.

There remains exactly one canonical strict validator truth source: the existing dossier strict/buffered validation path. The optional prepublication parity path continues to call the canonical buffered validator rather than maintaining a competing ruleset.

## Buffer architecture

Unchanged:

- canonical group size: `3`;
- groups remain atomic for acceptance/retry semantics;
- candidate publication remains immutable create-only;
- multiple pending sequential groups remain allowed;
- GitHub accepts only the maximal valid contiguous prefix from the expected sequence;
- an invalid expected group blocks promotion of later groups;
- no automatic semantic retry/healing manager was added.

## PR / CI / merge

- Implementation branch: `worker/taste-dossier-semantic-consistency-gaps-implement-01`.
- Implementation PR: `#44` — `Close Taste dossier semantic consistency gaps`.
- Final validated PR head: `47efdad6a7f43f47ca9f78c1513ac0d114480447`.
- Focused dossier CI: run `35269544646`, job `105365093134` — `success`.
- The successful job included: compile, execution ownership guard, daily snapshot, buffered submission, same-day preservation, strict recovery, prepublication parity, contract-gap, language-binding, semantic-consistency SCG-01..06, package identity, and parallel candidate/maximal-contiguous-prefix regressions.
- Merge: squash commit `80d6fc3adb9689f99ad5f30b729c6c1d36379d7d` on `main`.
- Post-merge execution ownership: run `35269588327` — `success`.

## Closeout guard and CURRENT_TASK finalization

- Durable closeout PR: `#45` — `Close Taste dossier semantic consistency task`.
- Closeout merge: squash commit `e8e5f3f65555f9b2ec14a8dfd85de1b1aafaeb41` on `main`.
- Required backlog-disposition / closeout guard: workflow `Validate backlog dispositions`, run `35272360456`, job `105374575676` (`backlog-disposition`) — `success`.
- The successful guard job explicitly completed both `Run backlog disposition regressions` and `Validate backlog deletion dispositions` with `success` before PR #45 was merged.
- `CURRENT_TASK.md` is in the required final state on `main`: it contains the task under `Worker closeout — 2026-09-18` with status `complete_ready_for_live_acceptance`, the implementation/activation refs, current snapshot/group-size state, the no-`Run now` statement, durable report path, and the separate live-acceptance boundary.
- Preservation of unrelated concurrent work was verified from the PR #45 diff: the PR changed exactly two files (this report and `CURRENT_TASK.md`); inside `CURRENT_TASK.md`, the only pre-existing line replaced was `Последнее обновление: 2026-09-17` → `2026-09-18`, and the task-specific closeout block was appended. No unrelated task block or concurrent work entry was deleted or rewritten.

## Post-merge compatibility / activation

A fresh snapshot was required because schema/contract/prompt content-complete compatibility hashes changed. Activation used only the normal GitHub-owned pre-AI path.

- Pre-merge active snapshot: `e2fe16341be5bdfdb314a668c2152703e2db7f20f0a4bf769f179818b090fc59` with evidence revision `language-binding-2026-09-17`.
- Post-merge pre-AI activation run: `35269588293` — `success`.
- GitHub-owned activation commit: `23fa46e0a07a3b1f0a8e7a53876ec93f49c9a235` (`Refresh atomic pre-AI payload`).
- Current snapshot: `00072072b0b382e6b973f448ce00b4aaaeccb2dbe355ca323de1785ccc0bd34c`.
- Current evidence contract revision: `semantic-consistency-gaps-2026-09-17`.
- Current worker schema revision: `semantic-consistency-gaps-2026-09-17`.
- Current `canonical_expected_sequence`: `1`.
- `prepared_required_count`: `564`.
- `completed_required_count`: `0`.
- `remaining_required_count`: `564`.
- `group_count`: `188`.
- Canonical group size remains `3`; `g000001` contains exactly three planned items and copies the current compatibility binding.

The old `e2fe1634…` worker descriptor path is absent from current `main`; it was not rebound to the new contract and no old candidate/progress artifact was manually patched, overwritten, renamed or advanced. Old snapshot/candidate state is therefore stale/inert only through the normal GitHub-owned compatibility lifecycle.

## Scheduled Task

Scheduled Task `Run now` was **not executed** during implementation, activation, validation or closeout preparation. Scheduled Task settings were not changed.

## Unresolved

No deterministic implementation/activation gap remains for SCG-01..SCG-06. Live behavior of the existing `Taste Steam Review Dossier` Scheduled Task against the fresh compatible snapshot is intentionally not proved by this task; the task contract requires that to be a separate later acceptance.

## Status

`complete_ready_for_live_acceptance`

## Recommended next step

Perform exactly one separate live acceptance of the existing `Taste Steam Review Dossier` Scheduled Task against the current compatible snapshot, then produce a separate READ / VALIDATE acceptance report. Do not fold that live run back into this implementation task.

## Efficiency / reusable lesson

Cross-object semantic invariants must be reflected in positive fixtures as well as negative cases: when a parent source is changed to `recent`, review child dates bound to that source must remain temporally coherent; when a feedback locator is changed for a privacy/content test, keep its parent surface physically valid so the intended guard is the first failing invariant. Keeping one shared canonical fixture plus focused invariant-specific mutations prevents CI from confusing stale synthetic controls with production defects. The focused dossier workflow now runs execution-ownership validation and the SCG suite in the same PR gate, reducing separate validation passes for future changes in this path.
