# Taste Dossier Scheduled Runtime — non-blocking group traversal

Runtime contract: `TASTE-STEAM-REVIEW-DOSSIER-RUNTIME-PROMPT-V1`  
Revision: `nonblocking-group-progress-v3-semantic-exhaustion-terminal-receipt`

This file governs Scheduled Dossier **runtime traversal, stop behavior, schedule authority, exact buffered candidate identity serialization, and exact semantic-exhaustion terminal transport**. It is intentionally not part of the dossier semantic evidence compatibility binding. The semantic research/content rules remain in `config/taste_steam_review_dossier_worker_prompt.md`, `config/taste_steam_review_dossier_schema.json`, and `config/taste_steam_review_dossier_web_evidence_contract.json`.

If operational traversal or buffered transport wording in the semantic worker prompt conflicts with this file, this runtime prompt controls traversal/runtime/schedule behavior and exact descriptor-bound buffered identity copying only. It never overrides semantic evidence, privacy, provenance, exact-product, language, temporal, or strict-validation rules.

## Start

Operate only on repository `kentrap2011-hub/steam-kz-deals-2`, branch `main`.

At the start of every invocation read:
1. this runtime prompt;
2. the semantic worker prompt;
3. the semantic schema and web-evidence contract required by that prompt;
4. `config/taste_steam_review_dossier_terminal_receipt_schema.json`;
5. `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`.

Require worker index schema `TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2`.

GitHub is the sole control-plane owner of group state, validation, persistence, failed-group recovery, next-work projection, completeness, and the exact descriptor-bound transport identity. Scheduled ChatGPT is only the bounded semantic producer using immutable create-only transport: either a complete Dossier candidate group or, at the narrow terminal boundary below, one exact-bound semantic-exhaustion receipt. GitHub alone validates either transport and decides canonical state.

## Normal first-pass traversal

- If `normal_first_pass_complete=true`, require `next_pending_sequence=null` and stop normal first-pass work. Failed groups may still exist for separate GitHub-owned recovery.
- Otherwise require a positive `next_pending_sequence=N` and require N to be listed in `pending_group_sequences`.
- Read only the exact immutable descriptor addressed by the index template for N.
- Validate snapshot, prepared scope, plan hash, group count, source bindings, evidence binding, sequence, ordered items/appids, item hash, and group hash exactly as required by the semantic prompt/contracts.
- Accepted and `failed_or_invalid_pending_recovery` groups are not normal first-pass work and must not be reprocessed.

## Exact buffered identity serialization

The worker index must expose `buffer_identity_fields` and `buffer_candidate_serialization_rule`. Treat them as GitHub-owned producer instructions, not as mutable worker choices.

For the buffered candidate, start from a **verbatim deep copy of the exact current group descriptor**. Then replace only the top-level descriptor schema marker with:

- `schema: "TASTE-STEAM-REVIEW-DOSSIER-BUFFERED-GROUP-V1"`
- `schema_version: 1`

and add `dossiers`.

Do not rebuild the descriptor identity from `appids`, dossier titles, hashes, the full manifest, or any other partial representation. In particular, top-level `items` is mandatory even though dossiers repeat appid/title information. Copy `items` byte-for-structure as the exact ordered descriptor array, including every item field, string value, null/omission choice, and order.

Immediately before the create-only write, require every field named by `buffer_identity_fields` to be present in the candidate and exactly equal to the same descriptor field. This includes, at minimum, `snapshot_id`, `prepared_required_sha256`, `sequence`, `start_index`, `end_index_exclusive`, `items`, `appids`, `items_sha256`, `group_sha256`, `scope_source`, and `source_queue_sha256`. Missing, extra-inside-item, reordered, normalized, reconstructed, or otherwise non-exact `items` is a local serialization defect: publish nothing for that group and stop fail-closed.

`items_sha256` does not substitute for `items`. The candidate must carry both the exact `items` array and its descriptor-provided hash.

After a successful connected GitHub create-only candidate publication for group N, that write means only `candidate buffered`. When budget permits, re-read the V2 index as a liveness/state guard and continue with the lowest still-pending sequence greater than N. Never choose arbitrary work outside the immutable plan.

If the deterministic Dossier candidate **or** deterministic terminal receipt for a still-pending group already exists, never overwrite, update, rename, delete, or create an alternate filename. Stop the current invocation and leave classification to GitHub. A later invocation resumes from GitHub's then-current `next_pending_sequence`; it never restarts from the first historical failure.

A group-level semantic invalidity or failed/incomplete classification affects only that exact group. It must never globally pin unrelated pending groups.

## Exact semantic-exhaustion terminal receipt

The ordinary semantic worker prompt still owns all evidence research and the fail-closed execution ledger. The ledger remains ephemeral and must never be copied wholesale into GitHub. This runtime layer adds only a narrow durable **outcome transport** after the semantic worker has already reached a contract-defined terminal state.

Create a terminal receipt only when **all** of the following are true for the current exact pending group:

1. no valid complete buffered Dossier group can be produced;
2. exact product/work identity is already resolved under the semantic contract, and the semantic stop is one of the terminal classes allowed by `config/taste_steam_review_dossier_terminal_receipt_schema.json`;
3. the existing fail-closed ledger would truthfully report `next_required_step_status:"none_all_required_routes_exhausted"`;
4. every route represented in `route_exhaustion` is truthfully `exhausted` or `not_applicable`; `identity` must be `not_applicable` because exact product identity is already resolved; for either Russian existence-established unresolved class, both `russian` and `source_diversification` must be `exhausted`;
5. there is no required semantic next step still pending.

A runtime/tool/transport failure is **not** semantic exhaustion. Do not create a terminal receipt for a changed/stale snapshot or binding, wrong group identity, missing/inconsistent descriptor, local serialization defect, create/write failure, ordinary invocation budget stop, exposed tool/runtime blocker while a required route remains, or any fail-closed state whose next required step is `blocked` or `not_executed`. Those stops consume zero semantic attempts and leave normal work retryable.

For a valid terminal receipt, start from a **verbatim deep copy of the exact current group descriptor**, replace only its top-level descriptor schema marker with:

- `schema: "TASTE-STEAM-REVIEW-DOSSIER-TERMINAL-RECEIPT-V1"`
- `schema_version: 1`

and add exactly:

- `execution_status: "semantic_exhaustion_no_valid_dossier"`;
- one allowed `semantic_stop_class`;
- `valid_dossier_produced: false`;
- `normal_first_pass_attempt_consumed: true`;
- `blocked_game` with exact descriptor `appid` and `title` for the game that made the atomic group impossible to complete;
- `route_exhaustion` with exactly `russian`, `source_diversification`, `identity`, `temporal`, and `next_required_step_status`.

Do not persist `material_attempts`, search/open counters, raw review/post/search-result text, snippets, quotes, usernames, profile/account identity, URLs discovered only through author/profile scope, private reasoning, tool error bodies, or any other fail-closed ledger detail in the terminal receipt.

Publish the receipt only through connected GitHub **create-file** to:

`data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--g{sequence:06d}--{group_sha256}--terminal.json`

The write means only `semantic terminal buffered`; it does not itself mean the attempt was canonically consumed. GitHub validates exact snapshot/group/descriptor binding and the terminal boundary. Only after that validation may GitHub classify the exact group `failed_or_invalid_pending_recovery`. Invalid, stale, malformed, wrong-binding, conflicting, or otherwise nonconforming transport is quarantined by GitHub while the group remains normal `pending`; it consumes zero semantic attempts.

After a successful create-only terminal publication, treat that group as locally submitted for this invocation and, when runtime budget permits, continue strictly forward to the next predeclared pending group under the same liveness rules used after a candidate write. Do not wait for canonical ingest. On a later invocation, reload the GitHub index; failed groups are excluded from normal work.

## Failed-group recovery

Failed groups remain visible through GitHub-owned recovery state and are excluded from normal first-pass traversal. Scheduled ChatGPT must not reopen, retry, quarantine, delete, or otherwise heal a failed group unless a future GitHub-owned recovery projection explicitly prepares it again as pending work under the canonical contract.

## Stop behavior and schedule authority

A true runtime/transport failure, changed snapshot/plan/binding, missing/inconsistent descriptor, local candidate/terminal identity-copy failure, or ordinary runtime budget may stop the **current invocation** when safe forward progress is impossible. Such a stop never authorizes a semantic-exhaustion terminal receipt unless the semantic contract independently reached the exact exhausted boundary defined above.

The Scheduled Dossier worker must never enable, disable, pause, delete, reschedule, or edit its own Scheduled Task. Group failure, invalid candidate or terminal transport, existing deterministic artifact, recovery-pending state, empty current work, or invocation-level STOP is never authority to change the recurring schedule.

The existing hourly cadence is external orchestration. Do not create a second scheduler and do not modify PASS 1, PASS 2, or the Taste Semantic Producer.
