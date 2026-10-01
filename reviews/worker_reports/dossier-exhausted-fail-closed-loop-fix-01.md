# Dossier exhausted fail-closed loop fix 01

## 1. Task

Task: `WORKER_TASK_DOSSIER_EXHAUSTED_FAIL_CLOSED_LOOP_FIX_01.md`.

Mode: `IMPLEMENT / VALIDATE`.

Goal: stop exact normal-first-pass Dossier work from repeating forever after genuine semantic route exhaustion, while preserving zero-attempt retryability for transport/runtime defects and keeping GitHub as the sole owner of attempt accounting, classification, recovery, next-work projection, persistence and idempotency.

## 2. START / fresh-main reconciliation

The worker read the current `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, task file, current-state task board, Dossier runtime/semantic contracts, schemas, persistence bridge, execution ownership contract, worker index/work manifest/validation status, and buffer/drain/recovery implementation before changing source.

Initial implementation started from then-current `main@05a92ac2af0c346b039d99c15caa3e93834f9165`. Parallel unrelated work advanced main during implementation. The branch was reconciled twice and the final implementation was rebased onto `main@94bec36a02513a4cb319cbbdd45d3c6f42a3bcd5`. The intervening main changes were unrelated personal-taste experiment/director-task files and did not overlap Dossier source.

Architecture preflight confirmed that the change belongs to the existing GitHub-owned Dossier control plane and must not add a second queue, scheduler, retry daemon or ChatGPT-owned state machine.

## 3. Root cause

The semantic worker already emitted a truthful user-visible `FAIL_CLOSED_EXECUTION_LEDGER_V1`, but that ledger was intentionally ephemeral and not a repository transport.

When the worker exhausted all required routes and correctly produced no valid Dossier candidate, GitHub therefore received no durable exact-bound outcome. The canonical group remained indistinguishable from “worker has not finished yet”, so `next_pending_sequence` continued to select the same exact group on every later normal invocation.

The defect was therefore not the semantic stop rule itself. The missing boundary was a durable, GitHub-validated representation of “this exact normal-first-pass semantic attempt executed to terminal exhaustion and produced no valid dossier”.

## 4. Attempt-consumption boundary

A normal-first-pass attempt is now consumed only by one exact-bound terminal outcome that satisfies all of these conditions:

- exact snapshot/group/descriptor identity matches the immutable GitHub group;
- exact product/work identity is already resolved;
- no valid complete atomic Dossier group was produced;
- `execution_status=semantic_exhaustion_no_valid_dossier`;
- stop class is an allowed semantic-exhaustion class;
- every required route is `exhausted` or `not_applicable`;
- `identity=not_applicable`, because exact identity must already be established;
- `next_required_step_status=none_all_required_routes_exhausted`;
- `normal_first_pass_attempt_consumed=true`.

The consuming stop classes are:

- `existence_established_retrieval_unresolved`;
- `existence_established_access_unresolved`;
- `critical_evidence_insufficient_after_required_routes_exhausted`.

Transport/runtime failures do not cross this boundary. Malformed candidate/receipt data, stale snapshot, wrong group identity/hash, conflicting transports, missing/inconsistent descriptor, write failure, ordinary runtime cutoff, blocked/not-executed required routes, and unresolved exact-product identity consume zero semantic attempts and leave the exact group normal `pending`.

## 5. Terminal artifact/receipt design

New schema: `config/taste_steam_review_dossier_terminal_receipt_schema.json`.

Runtime validator/path helper: `scripts/taste_steam_review_dossier_terminal.py`.

Schema: `TASTE-STEAM-REVIEW-DOSSIER-TERMINAL-RECEIPT-V1`.

Deterministic create-only path:

`data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--g{sequence:06d}--{group_sha256}--terminal.json`

The receipt is built from a verbatim copy of the exact current immutable group descriptor plus only compact terminal fields. It contains no raw review/post/search-result bodies, snippets, quotes, usernames, author/profile/account identity, profile URLs, material-attempt bodies or private reasoning.

Candidate and terminal filenames are separate deterministic namespaces inside the existing Dossier inbox; the candidate scanner explicitly excludes terminal filenames.

## 6. GitHub ingest/classification

The existing state-based Dossier drain now handles two exact outcome transports:

- a valid Dossier candidate: strict validation and canonical Dossier persistence remain unchanged;
- a valid semantic-exhaustion terminal receipt: GitHub archives the receipt and moves exactly that pending group to existing `failed_or_invalid_pending_recovery`.

Malformed/stale/wrong-binding/conflicting candidate or terminal transport is quarantined as retryable transport, audited, and leaves the canonical group `pending` with zero attempt consumption.

Later unrelated pending groups continue to validate/persist independently. A valid semantic terminal does not become a head-of-line blocker.

Exact replay of an already-consumed terminal receipt is cleanup-only and cannot consume a second attempt.

## 7. Recovery semantics

No new recovery owner or retry loop was added.

Consumed semantic exhaustion uses the existing GitHub-owned `failed_or_invalid_pending_recovery` state and remains excluded from normal first-pass traversal.

Only the existing explicit GitHub recovery request can reopen a failed group, and only after normal first pass is complete. Recovery now additionally requires both deterministic active outcome paths (candidate and terminal) to be empty, preventing a stale terminal replay from immediately re-consuming an explicitly reopened group.

Scheduled ChatGPT cannot authorize, select or execute recovery on its own.

## 8. Regression coverage

The final Dossier runtime suite proves the requested boundaries:

1. unresolved semantic exhaustion consumes one normal first pass;
2. the valid Dossier candidate path remains accepted/persisted;
3. malformed terminal receipt consumes zero attempts;
4. stale-snapshot terminal receipt consumes zero attempts;
5. wrong group hash/path consumes zero attempts;
6. blocked/unexhausted required-route stop consumes zero attempts;
7. deterministic consumed-terminal replay is idempotent cleanup-only;
8. accepted/failed canonical states remain outside ordinary normal traversal;
9. later unrelated groups continue despite a consumed failed/recovery group;
10. failed semantic terminal state requires explicit GitHub recovery authorization, and stale terminal replay blocks reopen;
11. the strict Dossier evidence validator remains fail-closed;
12. current Russian evidence semantics remain unchanged;
13. privacy/provenance restrictions remain unchanged and terminal extras such as ledger/raw body/username are rejected;
14. the existing shared `taste-steam-review-dossier-canonical-writer` serialization remains intact;
15. Scheduled Task configuration remains unchanged.

The suite also verifies the new resolved-identity precondition and preserves existing Dossier/Deep integration regressions.

## 9. Current production state after merge

Implementation PR #138 merged as `4b9e34e273ccb42ecb643cd4a8064e75d654bc3c`.

At post-merge read, current main had advanced only by one unrelated SteamDB runtime-state commit to `345c319035f6d47e5121c026512dd48bd969a994`; no Dossier semantic state had been manually changed.

Current Dossier projection:

- snapshot: `f26a7466dfe1a534a4c7ab506df29725d4ed5fe4fdef1633af6c1fc751771d1b`;
- runtime revision: `nonblocking-group-progress-v3-semantic-exhaustion-terminal-receipt`;
- runtime prompt SHA-256: `aa47dfd4aa9df488326d8f78ac82e4421587e5002eb19e582b43fe9a4608cd36`;
- accepted / failed / pending groups: `4 / 0 / 51`;
- accepted / pending dossiers: `12 / 152`;
- `next_pending_sequence=5`;
- group 5 SHA: `04fa628954e081c590b4de0f907599f64b51504bd353be17a4e84434029652c7`;
- group 5 state: `pending`;
- validation `candidate_count=0`;
- `normal_first_pass_complete=false`.

This is intentional. The task explicitly forbids fabricating a receipt from the pasted historical ledger or manually editing current group 5. The next real Dossier semantic invocation must re-read current GitHub truth and submit a terminal receipt only if the same exact exhaustion is still true.

## 10. Boundaries preserved

Preserved unchanged:

- GitHub owns normal-first-pass accounting, canonical classification, next work, recovery eligibility/authorization, persistence, idempotency and completeness;
- Scheduled ChatGPT remains a bounded semantic data-plane producer using create-only transport;
- no second queue, retry daemon, scheduler, checkpoint owner or backlog manager was added;
- no AppID-specific exception was added;
- no browser logic was added;
- Dossier V2 evidence semantics, temporal derivation, Russian evidence requirements and privacy/provenance rules were not weakened;
- no Dossier or Deep semantic work was executed by this developer chat;
- no Scheduled Task was created, edited, enabled, disabled, paused, resumed, rescheduled or manually run;
- current production group 5 was not manually reclassified.

## 11. Exact PR/commit/run refs

- implementation PR: #138 — `Fix Dossier exhausted fail-closed retry loop`;
- final PR head: `78ce397bab6742dce553a094f8c4d92ea6cb0fd1`;
- merge commit: `4b9e34e273ccb42ecb643cd4a8064e75d654bc3c`;
- Dossier runtime validation: run `36905347096`, workflow run #225 — success;
- execution ownership validation: run `36905346841`, workflow run #269 — success;
- backlog dispositions validation: run `36905347241`, workflow run #1569 — success;
- Progressive PASS 2 core validation: run `36905347238`, workflow run #569 — success.

The Dossier runtime run passed the full existing Dossier suite plus the new exhausted semantic terminal receipt regression.

## 12. Status

`implementation_complete_needs_next_semantic_invocation`

The architecture defect is fixed and merged. The current production group intentionally remains pending until the existing semantic worker performs a fresh exact-bound invocation under the new runtime contract.

## 13. Recommended next step — exactly one bounded next action

Allow the existing Taste Steam Review Dossier Scheduled Task to perform its next normal invocation against current `main`; do not alter its schedule or manually fabricate group-5 state. If the exact current group still reaches the same fully exhausted semantic condition, that worker can now submit the canonical terminal receipt and GitHub will move the group into failed/recovery while allowing later groups to continue.

## 14. Efficiency / reusable lesson

A semantic worker’s user-visible fail-closed explanation is observability, not durable attempt state. When a control plane must distinguish “not run yet” from “ran to a legitimate no-result terminal outcome”, use a minimal exact-bound create-only terminal receipt validated by the existing canonical writer.

Keep semantic terminal outcomes and transport/runtime failures as separate classes: the former may consume the exact attempt; the latter must stay retryable. When multiple outcome types share one inbox, give them disjoint deterministic namespaces and regression-test scanners so one transport cannot be mistaken for another.
