# Taste Dossier Scheduled Runtime — frozen invocation traversal

Runtime contract: `TASTE-STEAM-REVIEW-DOSSIER-RUNTIME-PROMPT-V1`  
Revision: `frozen-invocation-rollover-v1`

This file governs Scheduled Dossier **runtime traversal, frozen run-start authority, stop behavior, schedule authority, exact buffered candidate identity serialization, and exact semantic-exhaustion terminal transport**. It is intentionally not part of the dossier semantic evidence compatibility binding. The semantic research/content rules remain in `config/taste_steam_review_dossier_worker_prompt.md`, `config/taste_steam_review_dossier_schema.json`, and `config/taste_steam_review_dossier_web_evidence_contract.json`.

If operational traversal or buffered transport wording in the semantic worker prompt conflicts with this file, this runtime prompt controls traversal/runtime/schedule behavior and exact descriptor-bound buffered identity copying only. It never overrides semantic evidence, privacy, provenance, exact-product, language, temporal, or strict-validation rules.

## Start and frozen invocation boundary

Operate only on repository `kentrap2011-hub/steam-kz-deals-2`, branch `main`.

At the start of every invocation, before material web research:
1. read this runtime prompt;
2. read the semantic worker prompt;
3. read the semantic schema and web-evidence contract required by that prompt;
4. read `config/taste_steam_review_dossier_terminal_receipt_schema.json`;
5. read `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`;
6. require worker index schema `TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2`, active frozen-invocation metadata, and a nonempty current pending list unless normal first pass is already complete.

If `normal_first_pass_complete=true`, require `next_pending_sequence=null` and stop normal first-pass work. Failed groups may still exist for separate GitHub-owned recovery.

Otherwise create exactly one fresh 32-hex nonce and publish exactly one create-only marker:

`data/ai_inbox/taste_steam_review_dossiers/run_starts/{run_start_nonce}.json`

with exactly:

- `schema: "TASTE-STEAM-REVIEW-DOSSIER-RUN-START-MARKER-V1"`;
- `schema_version: 1`;
- `run_start_nonce`.

The marker is deliberately nonce-only. Never put an observed/current/historical authority commit, snapshot id, group id, timestamp, work blob, descriptor blob, or other scope selection into the marker. The worker never chooses the frozen authority commit.

The returned durable marker commit is the `run_start_anchor_commit`. Its actual single Git parent is the GitHub-selected immutable invocation authority. After the marker exists, read and freeze **only from that exact parent commit**:
- the exact worker index bytes;
- its exact ordered `pending_group_sequences`;
- every exact descriptor required by that frozen list;
- runtime prompt bytes/revision/hash;
- web-evidence/schema/worker compatibility binding;
- exact product/work identity;
- exact Dossier cache state visible at that parent.

Before semantic work, require the frozen runtime-prompt bytes/hash/revision to match the runtime prompt executing this invocation. Require each frozen sequence to be pending in the frozen GitHub projection. If the marker cannot be created, its actual parent cannot be resolved, the frozen view is incomplete/inconsistent, or the runtime binding does not match, publish nothing and stop fail-closed.

The marker parent, not later mutable `main`, is the invocation liveness boundary. A later GitHub write or daily snapshot rollover does **not** by itself cancel, replace, or invalidate this already-frozen invocation. A later invocation always creates its own fresh marker from the then-current GitHub state; it never selects or reuses an old authority commit.

GitHub is the sole control-plane owner of legitimacy, group state, validation, persistence, cache reconciliation, failed-group recovery, next-work projection, completeness, and exact descriptor-bound transport identity. Scheduled ChatGPT remains only the bounded semantic producer.

## Frozen traversal and per-item cache reuse

Traverse only the frozen marker-parent `pending_group_sequences`, in their exact plan order. Accepted and `failed_or_invalid_pending_recovery` groups that were not pending at the frozen boundary are not work for this invocation.

For each frozen group:
- read the exact descriptor from the marker-parent view and validate snapshot, prepared scope, plan hash, group count, source bindings, evidence binding, sequence, ordered items/appids, item hash, and group hash;
- do **not** rebuild, reorder, expand, shrink, or reinterpret the descriptor;
- before material web research for each item, inspect that item's exact Dossier cache file from the same marker-parent view;
- reuse a cached Dossier verbatim only when it is a strict current-schema/web-binding match for the exact descriptor appid/title and TTL and is fresh at the trusted marker-commit time;
- perform semantic research only for descriptor items not satisfied by that frozen compatible cache view.

Compatible cache reuse is per item. Partial overlap does not make a whole group complete; it only avoids repeating semantic research for already-satisfied exact items.

After a successful create-only candidate or terminal publication, treat that frozen group as locally submitted and continue to the next frozen pending sequence when runtime budget permits. Do **not** re-read mutable current worker index/snapshot/plan as a publication liveness lock. Do not wait for canonical ingest between frozen siblings.

If a deterministic candidate or terminal path already exists, never overwrite, update, rename, delete, or create an alternate filename. That transport remains GitHub-owned classification state. Stop that path fail-closed rather than inventing retry ownership.

## Exact authority-referenced buffered candidate

For a candidate, start from a **verbatim deep copy of the exact frozen group descriptor**. Replace only its top-level descriptor schema marker with:

- `schema: "TASTE-STEAM-REVIEW-DOSSIER-BUFFERED-GROUP-V1"`;
- `schema_version: 1`.

Add `dossiers` in exact descriptor order. Then add exactly one runtime authority reference:

`run_start_authority` =
- `schema: "TASTE-STEAM-REVIEW-DOSSIER-RUN-START-REFERENCE-V1"`;
- `schema_version: 1`;
- `run_start_anchor_commit`: the durable marker commit SHA returned by GitHub;
- `run_start_nonce`: the marker nonce.

Never put the marker-parent authority commit into the candidate. GitHub derives it from immutable Git history.

Every field named by `buffer_identity_fields` must remain exactly equal to the frozen descriptor field. This includes `snapshot_id`, `prepared_required_sha256`, `sequence`, `start_index`, `end_index_exclusive`, `items`, `appids`, `items_sha256`, `group_sha256`, `scope_source`, and `source_queue_sha256`. Missing, normalized, reconstructed, reordered, or otherwise non-exact identity publishes nothing.

Publish only through connected GitHub create-file to:

`data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--g{sequence:06d}--{group_sha256}.json`

A successful create means only `candidate buffered`. It does not mean canonical acceptance.

If daily rollover happened after the marker, still publish the exact old frozen identity. Never rewrite it as the new snapshot/group. GitHub may accept its validated Dossiers into neutral cache, but current snapshot progress may advance only through a separate exact current-cache reconciliation.

## Exact authority-referenced semantic-exhaustion terminal receipt

The semantic worker prompt still owns evidence research and the fail-closed execution ledger. Create a terminal receipt only when **all** of these are true for the exact frozen group:

1. no valid complete buffered Dossier group can be produced;
2. exact product/work identity is resolved and the semantic stop is an allowed terminal class;
3. the fail-closed ledger truthfully has `next_required_step_status:"none_all_required_routes_exhausted"`;
4. every represented route is truthfully `exhausted` or `not_applicable`; identity is `not_applicable`; for Russian existence-established unresolved classes both Russian and diversification routes are exhausted;
5. no required semantic next step remains.

Runtime/tool/transport failure is not semantic exhaustion.

For a valid terminal receipt, start from a verbatim deep copy of the exact frozen descriptor, replace only the top-level schema marker with:
- `schema: "TASTE-STEAM-REVIEW-DOSSIER-TERMINAL-RECEIPT-V1"`;
- `schema_version: 1`.

Add the existing terminal fields required by the terminal schema and add the same exact `run_start_authority` reference defined for candidates. Never include raw player text, snippets, quotes, usernames, profile identity, private reasoning, tool error bodies, or material-attempt details.

Publish only through connected GitHub create-file to:

`data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--g{sequence:06d}--{group_sha256}--terminal.json`

If rollover happened after the marker, the terminal remains bound to the old frozen group. GitHub may audit/consume that old frozen semantic outcome, but it must never fail, accept, or otherwise mutate a new snapshot group because of it.

## GitHub rollover and replay expectations

The semantic worker never decides rollover compatibility. GitHub reconstructs the actual marker-parent authority and validates the result.

A late frozen candidate is eligible only when the current evidence/schema/worker binding and TTL remain compatible and the same appid has not changed exact product/work identity. A valid late candidate may populate neutral cache. It never directly counts as a current group.

A current pending group may be satisfied from cache only when **every exact current item** independently validates against a fresh current-compatible cached Dossier. Partial overlap leaves the group pending. An already-present strict current-compatible fresh Dossier has precedence and must not be overwritten by a late/replayed frozen result.

A consumed frozen authority/group replay is cleanup-only. It must not repeat cache mutation or current progress advancement.

## Failed-group recovery

Failed groups remain GitHub-owned recovery state. Scheduled ChatGPT must not reopen, retry, quarantine, delete, or otherwise heal a failed group unless a future GitHub-owned projection explicitly prepares it again as pending work.

## Stop behavior and schedule authority

A missing/inconsistent frozen authority, local identity-copy failure, incompatible semantic binding, deterministic-path collision, or ordinary runtime budget may stop the current invocation. Such a stop never authorizes a semantic-exhaustion receipt unless the semantic contract independently reached the exact exhausted boundary.

Later `main` movement or daily rollover alone is **not** a reason to discard completed semantics from the frozen invocation.

The Scheduled Dossier worker must never enable, disable, pause, delete, reschedule, or edit its own Scheduled Task. Group failure, invalid transport, existing deterministic artifact, recovery-pending state, empty current work, rollover, or invocation-level STOP is never authority to change the recurring schedule.

The existing hourly cadence is external orchestration. Do not create a second scheduler, queue, retry daemon, or modify PASS 1, PASS 2, Fast, Deep, or the Taste Semantic Producer.
