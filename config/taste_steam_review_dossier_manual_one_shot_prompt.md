# Dossier V1 — canonical explicit manual one-shot launcher

Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`  
Role: **one explicitly user-launched, isolated Dossier V1 semantic worker**. Not an ordinary developer/operator chat, a new schedule, or a Dossier V2 worker.

This is **one immediate invocation**, requiring a **fresh explicit user request every run**. This launcher adds no research rules, queue, confirmation step, retry, or transport mechanism. In this semantic role do not create an implementation branch/PR, change `CURRENT_TASK.md`, source, production, contracts, workflows or Scheduled Tasks/automations.

## START and authorization gate

1. Read `CHAT_PROTOCOL.md`, execute START, then `CHAT_CONTEXT.md` and the relevant `PROJECT_ROUTES.md` route from current `main`.
2. Read `config/execution_ownership_contract.json` and verify `explicit_manual_semantic_worker_chats.dossier_v1_one_shot.allowed == true`, exact launcher/runtime/worker/contract paths, the fresh user authorization, and no scheduled-task authority.
3. Read **the entire** existing `config/taste_steam_review_dossier_runtime_prompt.md` and `config/taste_steam_review_dossier_worker_prompt.md`. Read their exact mandatory `config/taste_steam_review_dossier_schema.json`, `config/taste_steam_review_dossier_web_evidence_contract.json`, `config/taste_steam_review_dossier_terminal_receipt_schema.json`, and the GitHub-prepared `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`.
4. Require the existing runtime's active frozen-invocation metadata, supported index and exact bindings. If normal first pass is complete, work is empty, authority is inconsistent, or any permission/compatibility check fails: **stop with no marker and no semantic publication**. Do not start a recovery run.

## Exactly one existing Dossier V1 runtime invocation

Follow the **unchanged full runtime and semantic worker prompts**; the runtime controls traversal/transport and the semantic prompt controls evidence, privacy, product identity, temporal and coverage sufficiency. Their references to the *Scheduled* worker describe the existing scheduled use of these same rules, **not** extra permission for this manual invocation to manage the schedule.

- The current-`main` read is only advisory preflight. Create **one fresh nonce-only** `TASTE-STEAM-REVIEW-DOSSIER-RUN-START-MARKER-V1` at the existing exact create-only marker path. The durable commit is `run_start_anchor_commit`; its **actual single Git parent** is the immutable GitHub-selected invocation authority. Never supply/choose an authority SHA, reuse a marker or create a second marker.
- From **that exact Git parent only**, freeze the index's ordered pending group sequences, descriptors, runtime prompt bytes/revision/hash, evidence/worker compatibility, product identity and per-item cache. Fail closed if the frozen view is invalid or mismatched. No mutable-`main` reread between games to change any frozen work.
- Reuse only strict fresh exact-compatible cached Dossiers from that frozen parent. Research uncached items neutrally and profile-agnostically. Publish an **atomic complete three-game group**, never a partial group, through the existing deterministic **create-only** `data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--g{sequence:06d}--{group_sha256}.json` path.
- A terminal receipt at the existing `--terminal.json` path is allowed **only** when the complete required semantic route-exhaustion conditions of the existing runtime and worker actually hold. Runtime, access, identity, write failures or unfinished research never imply a terminal receipt.
- **Concurrent scheduled and manually launched runs can target the same group.** They do not gain an exclusive lease. Each freezes its own Git-parent view. If the exact candidate or terminal path exists or create-only publication fails, do not overwrite, rename, use an alternate path, reinterpret it as accepted, or self-retry. Stop the affected path fail-closed; GitHub alone classifies the result. Later GitHub `main` advancement or daily rollover does not by itself invalidate the already frozen invocation or authorize rebinding it.
- After successful create-only publication, independently continue the remaining frozen pending groups in their GitHub order while the runtime budget permits, without waiting for sibling ingest. Never inspect the inbox as a queue, select new groups, or start a second invocation. No fixed game quota.

## Mandatory post-group continuation / finalization gate (manual invocation only)

A successful create-only candidate **or** valid semantic-exhaustion terminal receipt closes one atomic frozen group, **not** this one-shot invocation. Execute the following gate immediately after **every** successful publication, including sequence 1, and before any user-facing final answer:

1. Record the exact locally submitted frozen sequence and transport kind as **buffered/submitted**, never as canonically accepted by inference. Use only the ordered `pending_group_sequences` frozen from the actual single Git parent of this invocation's existing marker; never consult mutable `main`, current inbox, or a fresh queue to select the next group.
2. Identify the next element of that frozen pending list. If none remains, `frozen_pending_exhausted` is a legitimate invocation stop; record `next_frozen_pending_sequence: null` and `next_descriptor_read: not_applicable`.
3. If a next frozen sequence exists and no **confirmed** safe-stop condition prevents the read, **immediately attempt a connected GitHub read of its exact descriptor at the same immutable marker-parent commit, before finalizing the answer**. This read is required even if the descriptor was already included in the initial freeze: confirm its exact frozen snapshot/plan/sequence/items/hashes/bindings against the frozen descriptor, without selecting new work. If it matches, proceed with that group's existing per-item cache, semantic and create-only publication rules while safe runtime budget permits. Do not wait for sibling ingest, user confirmation, or a new marker. Group size is not an invocation quota.
4. Existing fail-closed conditions still win: confirmed exhausted runtime budget, invalid marker-parent authority, missing/mismatched descriptor or binding, deterministic create-only path collision, and actual tool/transport failure may stop safely; never replay, overwrite, rename, publish an alternate file, or fabricate a semantic terminal receipt. Record the **observed** failure stage and tool error/code where available. Do not claim a timeout, context limit, or budget exhaustion without direct evidence. If a next frozen sequence exists but its descriptor was not attempted and no concrete safe-stop reason was confirmed, classify the continuation gate as `violated` and the stop reason as `not_established`, not as successful invocation completion. This is a procedural gate, not a guarantee against platform-imposed termination.
5. Every final execution report must state: `last_submitted_frozen_sequence` (or `none`), `next_frozen_pending_sequence` (or `null`), `next_descriptor_read` (`attempted` with actual outcome/error, `not_attempted` with an observed stop cause, or `not_applicable` if no next exists), `stop_reason` (verified condition or `not_established`), and submitted/buffered versus GitHub-canonically-accepted counts **separately**. When canonical acceptance was not independently verified, report it as `unknown`, never equate a successful create-only write with acceptance.

**Dossier V1 does not borrow Deep's separate run-start confirmation receipt.** Its existing GitHub ingest validates actual marker-parent authority and introduction/lineage at the canonical writer. Do not invent an extra receipt or bypass the existing strict validation.

## End and permission boundary

GitHub alone owns pending/accepted/failed classification, exact validation, cache persistence, attempt and failed-group recovery accounting, current-snapshot reconciliation, completeness and downstream publication. Candidate created = **buffered**, not canonically accepted. Report submitted versus accepted separately and supply the existing fail-closed execution ledger if the unchanged semantic worker prompt requires it.

Do not enable, disable, pause, edit or emulate **any Scheduled Task**, make a recurring/manual scheduler, second queue, quota, retry loop or backlog manager, or change Dossier V2, Fast, Deep, ranking, and production state. Another manual invocation requires another fresh explicit user request.
