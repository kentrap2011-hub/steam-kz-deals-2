# DIRECTOR TASK BOARD

## Current rules
- Keep at most two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots, not historical chat identities.
- No autonomous IMPLEMENT without separate user approval.
- Reconcile Board -> exact task -> exact durable report before assigning follow-up work.
- Every nontrivial worker task must finish with its compact durable report committed to `main` at the task-declared `reviews/worker_reports/...` path before the worker presents the task as complete/ready for Director acceptance.
- When the user says `Проверь`, `Готово, читай` or equivalent after worker completion, Director reads the expected durable worker-report directly from GitHub. Director may also read `DIRECTOR_TASK_BOARD.md`, `CURRENT_TASK.md`, `CHAT_PROTOCOL.md`, `DIRECTOR_PROTOCOL.md` and other compact operating rules needed for orchestration.
- Director must not inspect source code, diffs, workflow implementation, logs, production artifacts or other deep project state to compensate for an incomplete worker-report. If the report is insufficient or internally inconsistent, Director asks the worker to investigate and update the durable report.
- The user should not need to relay normal worker results between chats; GitHub worker-reports are the normal handoff channel.
- Proactive gap detection follows `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`; the user is not the project's monitoring layer.
- Current priority is operational speed with GitHub-owned production control-plane boundaries preserved.

## ACCEPTED — Taste dossier validator ↔ generator parity fix

Task:
`WORKER_TASK_TASTE_DOSSIER_VALIDATOR_GENERATOR_PARITY_FIX_01.md`

Report:
`reviews/worker_reports/taste-dossier-validator-generator-parity-fix-01.md`

Final status:
`complete_ready_for_live_acceptance`

Accepted facts:
- PARITY-01..03 are now explicitly aligned generator-side;
- source locator exact-one / HTTPS / normalized host equality is machine-encoded;
- `multi_source` now explicitly requires `single_source_reason:null`;
- exact-app Steam Store fallback parent now allows only `steam_reviews` or `store_user_reviews`;
- strict validator semantics were unchanged;
- PARITY-FIX-01..12 and prior focused dossier suites passed;
- PR #70 merged as `505c1adbd48eeaa2100148947cbe56bd881f4f76`;
- normal activation succeeded via run `35500644784`, commit `cf8467d65691312efe55efd76979cc74ff50c50d`;
- fresh active snapshot is `3bd2085e4a4a157aa0edadfeabbdcc36786228787016f373189d71d12da8d99b`, expected `g000001`;
- previous snapshot became stale/inert through normal binding compatibility;
- no manual progress/recovery surgery occurred;
- Scheduled Task was not run during implementation.

Next step:
- one clean production `Run now` acceptance on the active snapshot;
- keep the worker chat until live acceptance is observed.

## ACCEPTED — Taste dossier validator ↔ generator parity audit

Task:
`WORKER_TASK_TASTE_DOSSIER_VALIDATOR_GENERATOR_PARITY_AUDIT_01.md`

Report:
`reviews/worker_reports/taste-dossier-validator-generator-parity-audit-01.md`

Final status:
`complete_confirmed_parity_gaps`

Accepted findings:
- PARITY-01: source locator serialization is under-specified generator-side; strict requires exactly one of `url/public_ref`, HTTPS for URL, and exact normalized URL host equality in `domain`;
- PARITY-02: for `source_mix_status:"multi_source"`, strict requires `single_source_reason:null`, but generator-facing layers do not state the converse-null invariant;
- PARITY-03: exact-app Steam Store fallback parent is accepted only with `source_type:"steam_reviews"` or `"store_user_reviews"`; current generator-facing wording leaves other player-feedback source types seemingly legal;
- identity-provenance control case is now aligned and was not reopened;
- GitHub-only transport/progress defensive checks were correctly excluded;
- no speculative future/retrieval findings were promoted.

Recommended next step:
- one bounded IMPLEMENT covering only PARITY-01..03, aligning generator-facing contracts/tests to existing strict validator semantics;
- do not change validator semantics, ownership, queue/retry/checkpoint architecture or production state;
- keep production `Run now` paused until that bounded fix is accepted.

## ACCEPTED — Taste dossier identity provenance generation fix

Task:
`WORKER_TASK_TASTE_DOSSIER_IDENTITY_PROVENANCE_GENERATION_FIX_01.md`

Report:
`reviews/worker_reports/taste-dossier-identity-provenance-generation-fix-01.md`

Final status:
`complete_ready_for_live_acceptance`

Accepted facts:
- worker prompt/schema now explicitly require at least one exact-product identity provenance source with `evidence_role:"identity"`;
- strict validator was not weakened and remains authoritative;
- focused and prior dossier guard suites passed;
- implementation PR #67 merged as `f0a42cd2c870bbc013c07901b86ae21bfef4bc98`;
- normal activation succeeded via run `35493204897`, commit `d174f1652581b3ef0c633fc9da22d0533b5abdd6`;
- fresh active snapshot is `905bddbce50fc8fd319465e3e68450e9cd7f0b2edc53c8a1a687466372f4d384`, expected `g000001`;
- old invalid snapshot `533abb9b...8378d` candidates were quarantined unchanged by GitHub-owned activation/recovery;
- Scheduled Task was not run during implementation.

Next step:
- one clean production `Run now` acceptance on the active snapshot;
- keep the worker chat until that live acceptance is observed.

## ACTIVE — Steam review dossier persistence bridge
Task:
`WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PERSISTENCE_BRIDGE_01.md`

Task ID:
`taste-steam-review-dossier-persistence-bridge-01`

Status:
`authorized_ready_for_worker`

Mode:
`IMPLEMENT`

Worker slot:
`ЧАТ 2` — continue in the existing dossier chat because this is the direct follow-up to the failed production validation.

User authorization:
- user explicitly approved sending the discovered persistence/write-back defect for repair.

Verified production-validation facts:
- fixed daily full snapshot is now real and contains 591 required dossier items;
- current durability checkpoint contains 10 items;
- `full_backlog_complete=false`;
- scheduled ChatGPT can read/prepare the checkpoint but cannot execute the canonical dossier ingest script through its current GitHub action surface;
- no partial write occurred, so the same snapshot/checkpoint remains authoritative;
- `ingest-taste-batch.yml` belongs to Taste Semantic Producer and must remain untouched.

Goal:
- add the smallest repository-defined submission bridge that the existing scheduled ChatGPT task can actually call;
- keep validation, canonical dossier persistence, snapshot advancement and completeness GitHub-owned;
- reuse canonical dossier ingest logic rather than duplicating it;
- prove the real bridge shape in GitHub-hosted acceptance before another production `Run now`;
- do not process the real 591-item backlog in the worker task.

Expected report:
`reviews/worker_reports/taste-steam-review-dossier-persistence-bridge-01.md`

Allowed final statuses:
- `complete_ready_for_user_run_now_validation`
- `needs_user_decision`
- `blocked`

## IMPLEMENTED, PRODUCTION VALIDATION EXPOSED NEXT GAP — daily full-backlog Steam review dossier control plane
Task:
`WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_CONTROL_PLANE_REFRESH_01.md`

Report:
`reviews/worker_reports/taste-steam-review-dossier-control-plane-refresh-01.md`

Implementation status:
`complete_ready_for_user_run_now_validation`

Accepted implementation facts:
- one fixed daily GitHub-prepared full backlog replaces checkpoint-as-scope behavior;
- checkpoint size 10 is durability only, never quota;
- same-snapshot checkpoint/resume is implemented;
- daily preparation is wired into the existing pre-AI control-plane path;
- implementation PR #18 / merge `efc754a094199a8c41ae686494c8f2a5e4741cef`;
- durable report closeout PR #19 / merge `e64a77f3804832c9b7e16fc642293c5b33b33847`.

Real `Run now` then proved the snapshot/scope layer works but exposed a separate missing write-back bridge: scheduled ChatGPT had no available action to invoke canonical dossier ingest/persistence. The active persistence-bridge task owns that defect.

## ACCEPTED — full Steam review dossier backlog scope implementation
Task:
`WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_FULL_BACKLOG_01.md`

Report:
`reviews/worker_reports/taste-steam-review-dossier-full-backlog-01.md`

Final status:
`complete_ready_for_user_run_now_validation`

Accepted facts:
- full eligible Taste dossier scope is no longer limited to the 10-item active Taste semantic pin;
- semantic pin remains downstream-only;
- fresh dossiers are reusable;
- non-Taste/base-support-only rows are excluded;
- regression coverage proved >10 scope and durable checkpoint continuation;
- implementation reached `main` via PR #16 / merge `ecde503c6b74aa964e7b331da009f87af8d0b3cd`.

## ACCEPTED — Steam review dossier preparer mechanism
Task:
`WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PREPARER_01.md`

Report:
`reviews/worker_reports/taste-steam-review-dossier-preparer-01.md`

Final status:
`complete_ready_for_separate_scheduler_and_clean_throughput_measurement`

Accepted facts:
- compact neutral Steam dossier schema implemented;
- Russian + non-Russian review lanes implemented;
- default TTL 20 days, configurable;
- GitHub owns validation/persistence/cleanup;
- downstream Taste input remains fail-closed.

## LIVE — existing dossier Scheduled Task
Title:
`Taste Steam Review Dossier`

State:
- task exists;
- first historical real run generated/persisted 10 dossiers under the older route;
- the latest validation now sees the correct fixed full snapshot: 591 required items, 10-item current checkpoint;
- latest run did not persist/advance because no callable repository ingest bridge was exposed to the scheduled ChatGPT runtime;
- no partial write occurred and the same checkpoint remains authoritative;
- do not press `Run now` again until the active persistence-bridge implementation is accepted by Director.

## PAUSED — normal ChatGPT/Taste mechanism + clean throughput measurement
Task:
`WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md`

Task ID:
`taste-normal-semantic-producer-01`

Previous measurement evidence:
- 50 durably accepted semantic work-items total;
- only 30 were full game fit evaluations and 20 were negative-analysis follow-ups;
- therefore that historical run is not the final clean full-game capacity benchmark.

Status:
`paused_until_dossier_end_to_end_production_path_is_user_validated`

Worker slot:
`ЧАТ 1` may be reused later with a fresh chat if the old context is no longer useful.

When resumed:
- run a NEW clean throughput benchmark using fresh dossier-backed inputs;
- checkpoint size 10 is measurement/durability only, never a production limit;
- record exact timing/checkpoints/stop reason;
- do not choose the final production limit automatically;
- age-priority remains separate.

Expected report remains:
`reviews/worker_reports/taste-normal-semantic-producer-01.md`

## NORMAL TASTE SCHEDULED TASK — still old canary
Existing task:
- title `Taste Semantic Producer`;
- id `6aa032f37e688191a5c9a1a83f91c5d9`;
- current UI prompt is still the old one-game Chernobylite canary;
- user screenshot shows daily schedule at 23:00 Samara time;
- keep unchanged during dossier repair.

Do not reconfigure it until dossier production is validated and a later clean throughput measurement plus separate user production-limit decision are complete.

## DEFERRED — Taste queue age-priority ordering
Task:
`WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md`

Status:
`deferred_separate_do_not_block_throughput_measurement`

Required ordering when separately authorized later:
1. never successfully canonically Taste-checked;
2. then previously checked from oldest successful canonical Taste evaluation to newest.

## ACCEPTED — real Steam partial-publish production refresh
Task:
`WORKER_TASK_STEAM_PARTIAL_PUBLISH_PRODUCTION_REFRESH_01.md`

Report:
`reviews/worker_reports/steam-partial-publish-production-refresh-01.md`

Final status:
`complete_with_problem_entries_for_separate_review`

Verified production result:
- workflow run `34643249267` success;
- 17,299 observed / 17,299 reported;
- 17,287 processed successfully;
- shortlist 676;
- 12 isolated review-enrichment problems;
- 0 segment/system failures.

Do not investigate those 12 now unless the user changes priority.

## ACCEPTED — read-only architecture review
Task:
`WORKER_TASK_CODE_ARCHITECT_SYSTEM_REVIEW_01.md`

Report:
`reviews/worker_reports/code-architect-system-review-01.md`

Final status:
`review_complete_recommendations_ready`

No blocking structural issue was found. Architecture cleanup recommendations remain non-blocking/deferred while operational Taste/dossier work is priority.

## QUEUED LATER
- `WORKER_TASK_STEAM_SERVER_SIDE_PREFILTER_OPTIMIZATION_01.md`
- `WORKER_TASK_STEAM_ERROR_NOTIFICATION_WATCH_01.md`
- `WORKER_TASK_GIVEAWAY_DECOUPLE_FROM_STEAM_CRAWL_01.md`
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
- `WORKER_TASK_ARCHITECTURE_RECOMMENDATIONS_FOLLOWUP_01.md`

`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Proactive Project Auditor — standing role
Protocol:
`PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`
