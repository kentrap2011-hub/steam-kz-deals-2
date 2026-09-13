# DIRECTOR TASK BOARD

## Current rules
- Keep at most two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots, not historical chat identities.
- No autonomous IMPLEMENT without separate user approval.
- Reconcile Board -> exact task -> exact durable report before assigning follow-up work.
- Proactive gap detection follows `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`; the user is not the project's monitoring layer.
- Current priority is operational speed with GitHub-owned production control-plane boundaries preserved.

## ACTIVE — daily full-backlog Steam review dossier control plane
Task:
`WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_CONTROL_PLANE_REFRESH_01.md`

Task ID:
`taste-steam-review-dossier-control-plane-refresh-01`

Status:
`authorized_revised_ready_for_worker`

Mode:
`IMPLEMENT`

Worker slot:
`ЧАТ 2` — continue in the current dossier implementation chat while its context remains useful.

User-approved architecture:
- GitHub once per day prepares one complete canonical dossier backlog from the current eligible Taste queue;
- the existing `Taste Steam Review Dossier` Scheduled Task processes that complete prepared backlog;
- checkpoint size 10 is only a durable persistence/runtime boundary, never the amount of work GitHub exposes and never a quota;
- no GitHub scope rebuild is required merely to reveal the next 10 items;
- if the prepared daily backlog is empty, dossier work for that prepared day is complete;
- if ChatGPT hits a genuine runtime/tool limit, completed checkpoints remain durable and a later invocation resumes the same prepared backlog;
- manual `Run now` may use the latest prepared daily backlog and does not require an on-demand GitHub refresh; source changes after preparation may wait until the next daily preparation.

Goal:
- replace the overly coupled next-10-manifest production design with one daily GitHub-prepared full backlog;
- wire preparation into the appropriate existing GitHub daily control-plane route before the dossier task runs;
- preserve GitHub ownership of scope/order/freshness/completeness and ChatGPT ownership only of evidence collection/synthesis for the prepared list;
- keep the existing 10 fresh production dossiers reusable;
- keep `Taste Semantic Producer` unchanged;
- validate full-list processing and resume semantics without running the real mass backlog in the worker chat.

Expected report:
`reviews/worker_reports/taste-steam-review-dossier-control-plane-refresh-01.md`

Allowed final statuses:
- `complete_ready_for_user_run_now_validation`
- `needs_user_decision`
- `blocked`

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

Production validation then exposed a separate orchestration defect: the real Scheduled Task saw a stale pre-merge empty manifest and processed 0. The current active task replaces the next-10-manifest coupling with the simpler daily full-backlog model.

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
- first real run generated/persisted 10 dossiers;
- those 10 dossiers remain reusable;
- later `Run now` after full-backlog merge processed 0 because the canonical work manifest was stale and still said `ready_from_fresh_cache`;
- the task correctly refused to invent scope;
- do not use the 0-result run as evidence that the eligible backlog is empty;
- next real user validation waits for the active daily full-backlog control-plane task to be accepted.

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
`paused_until_dossier_daily_full_backlog_path_is_ready_and_user_validated`

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
- keep unchanged during dossier control-plane correction.

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
