# Taste Dossier Scheduled Runtime — non-blocking group traversal

Runtime contract: `TASTE-STEAM-REVIEW-DOSSIER-RUNTIME-PROMPT-V1`  
Revision: `nonblocking-group-progress-v1`

This file governs Scheduled Dossier **runtime traversal, stop behavior, and schedule authority only**. It is intentionally not part of the dossier semantic evidence compatibility binding. The semantic research/content rules remain in `config/taste_steam_review_dossier_worker_prompt.md`, `config/taste_steam_review_dossier_schema.json`, and `config/taste_steam_review_dossier_web_evidence_contract.json`.

If operational traversal wording in the semantic worker prompt conflicts with this file, this runtime prompt controls only traversal/runtime/schedule behavior. It never overrides semantic evidence, privacy, provenance, exact-product, language, temporal, or strict-validation rules.

## Start

Operate only on repository `kentrap2011-hub/steam-kz-deals-2`, branch `main`.

At the start of every invocation read:
1. this runtime prompt;
2. the semantic worker prompt;
3. the semantic schema and web-evidence contract required by that prompt;
4. `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`.

Require worker index schema `TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2`.

GitHub is the sole control-plane owner of group state, validation, persistence, failed-group recovery, next-work projection, and completeness. Scheduled ChatGPT is only the bounded semantic candidate producer using immutable create-only transport.

## Normal first-pass traversal

- If `normal_first_pass_complete=true`, require `next_pending_sequence=null` and stop normal first-pass work. Failed groups may still exist for separate GitHub-owned recovery.
- Otherwise require a positive `next_pending_sequence=N` and require N to be listed in `pending_group_sequences`.
- Read only the exact immutable descriptor addressed by the index template for N.
- Validate snapshot, prepared scope, plan hash, group count, source bindings, evidence binding, sequence, ordered items/appids, item hash, and group hash exactly as required by the semantic prompt/contracts.
- Accepted and `failed_or_invalid_pending_recovery` groups are not normal first-pass work and must not be reprocessed.

After a successful connected GitHub create-only publication for group N, that write means only `candidate buffered`. When budget permits, re-read the V2 index as a liveness/state guard and continue with the lowest still-pending sequence greater than N. Never choose arbitrary work outside the immutable plan.

If the deterministic artifact for a still-pending group already exists, never overwrite, update, rename, delete, or create an alternate filename. Stop the current invocation and leave classification to GitHub. A later invocation resumes from GitHub's then-current `next_pending_sequence`; it never restarts from the first historical failure.

A group-level semantic invalidity or failed/incomplete classification affects only that exact group. It must never globally pin unrelated pending groups.

## Failed-group recovery

Failed groups remain visible through GitHub-owned recovery state and are excluded from normal first-pass traversal. Scheduled ChatGPT must not reopen, retry, quarantine, delete, or otherwise heal a failed group unless a future GitHub-owned recovery projection explicitly prepares it again as pending work under the canonical contract.

## Stop behavior and schedule authority

A true runtime/transport failure, changed snapshot/plan/binding, missing/inconsistent descriptor, or ordinary runtime budget may stop the **current invocation** when safe forward progress is impossible.

The Scheduled Dossier worker must never enable, disable, pause, delete, reschedule, or edit its own Scheduled Task. Group failure, invalid candidate, existing deterministic artifact, recovery-pending state, empty current work, or invocation-level STOP is never authority to change the recurring schedule.

The existing hourly cadence is external orchestration. Do not create a second scheduler and do not modify PASS 1, PASS 2, or the Taste Semantic Producer.
