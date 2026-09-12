# DIRECTOR TASK BOARD

## Current rules
- Keep at most two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots, not historical chat identities.
- No autonomous IMPLEMENT without separate user approval.
- Reconcile Board -> exact task -> exact durable report before assigning follow-up work.
- Proactive gap detection follows `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`; the user is not the project's monitoring layer.
- Current priority is operational speed with GitHub-owned production control-plane boundaries preserved.

## ACTIVE — full Steam review dossier backlog
Task:
`WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_FULL_BACKLOG_01.md`

Task ID:
`taste-steam-review-dossier-full-backlog-01`

Status:
`authorized_ready_for_worker`

Mode:
`IMPLEMENT`

Worker slot:
`ЧАТ 2` — use a NEW chat because the previous Chat 2 session exhausted context before making repository changes.

Goal:
- correct dossier scope so one existing `Taste Steam Review Dossier` invocation can continue through the whole current eligible dossier backlog rather than only the current 10-item Taste active pin;
- keep GitHub as scope/queue/checkpoint/completeness owner;
- first reconcile `config/taste_steam_review_dossier_contract.json`, whose current `exact_pinned_game_scope` wording is too narrow for the already-authorized full-backlog scheduler behavior;
- preserve the existing 10 fresh production dossiers;
- allow small durable checkpoints (10 is acceptable) without treating checkpoint size as a per-run or daily quota;
- validate with backlog >10 and checkpoint continuation;
- do not run the real mass backfill in the worker; user validates later with `Run now` on the existing Scheduled Task.

Expected report:
`reviews/worker_reports/taste-steam-review-dossier-full-backlog-01.md`

Allowed final statuses:
- `complete_ready_for_user_run_now_full_backlog_validation`
- `blocked_contract_or_scope_ambiguity`
- `needs_fix`

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
- downstream Taste input remains fail-closed;
- current implementation originally scoped dossier work to the current Taste active pin, which is the specific issue now being corrected by the active full-backlog task.

## LIVE — existing dossier Scheduled Task
Title:
`Taste Steam Review Dossier`

State:
- task exists and the user successfully executed `Run now` once;
- first real run generated/persisted 10/10 required dossiers and reached `ready_from_fresh_cache` for the then-visible scope;
- durable checkpoint reported by the run: `0e3a1e425a03466ee841d19e0d9446a04157b4da`;
- those 10 dossiers must be reused, not discarded;
- the observed defect is that control-plane scope ended at the current 10-item active pin instead of continuing through the full eligible backlog;
- do not run it again until the active full-backlog implementation/report is accepted.

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
`paused_until_dossier_full_backlog_path_is_ready_and_user_validated`

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
- keep unchanged during dossier backlog correction.

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
