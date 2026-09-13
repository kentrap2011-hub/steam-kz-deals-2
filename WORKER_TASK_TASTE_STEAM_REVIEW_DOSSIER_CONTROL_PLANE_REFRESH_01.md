# WORKER TASK — Taste Steam review dossier control-plane refresh 01

Task ID: `taste-steam-review-dossier-control-plane-refresh-01`

Status: `authorized_ready_for_worker`

Mode: `IMPLEMENT`

## Goal
Close the production orchestration gap exposed by the first real `Run now` validation after the full-backlog dossier implementation.

The existing Scheduled Task `Taste Steam Review Dossier` must be able to obtain a current GitHub-prepared dossier work manifest without inventing scope itself and without requiring the user to manually run a separate preparatory GitHub step before every `Run now`.

GitHub/control-plane remains owner of scope derivation, queue construction, checkpoint state, retry/completeness and manifest persistence. Scheduled ChatGPT may only consume the exact GitHub-prepared `required_items[]`, collect Steam evidence and submit results through the canonical path.

## Background
Full-backlog implementation is already on `main`; durable report:
`reviews/worker_reports/taste-steam-review-dossier-full-backlog-01.md`

Accepted refs:
- PR `#16`
- merge `ecde503c6b74aa964e7b331da009f87af8d0b3cd`
- closeout `49819d0e18404c1279abc41f06c03ab27eea33c2`
- `CURRENT_TASK.md` closeout `88a9107562bb3a9e3f1852ac076d8b4c4c28361f`

Subsequent real Scheduled Task `Run now` processed 0 new dossiers because `taste_steam_review_dossier_work.json` still had `status="ready_from_fresh_cache"` and `required_items=[]`, generated before the full-backlog merge. The scheduled worker correctly stopped fail-closed instead of deriving its own scope.

This is a confirmed orchestration defect: the full-backlog builder exists, but the production control plane does not reliably rebuild/publish the current dossier manifest before the collector needs it.

## Mandatory preflight
Follow `CHAT_PROTOCOL.md` START gate first. Before writes, verify the minimal relevant route using:
- `config/execution_ownership_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- relevant `PROJECT_ROUTES.md` entry if present
- exact existing GitHub workflow/control-plane path that creates or refreshes `data/production/pre_ai/chatgpt_taste_queue.jsonl`
- `scripts/build_taste_steam_review_dossier_work.py`
- current dossier ingest/rebuild path

Do not perform a broad repository re-audit.

## Required behavior
Implement the minimal GitHub-owned orchestration so the canonical dossier work manifest cannot remain silently stale after source Taste backlog changes or dossier-backlog implementation changes.

Required production semantics:
1. GitHub deterministically prepares dossier work from the current canonical eligible Taste backlog.
2. `taste_steam_review_dossier_work.json` is bound to current source/provenance strongly enough that stale preparation is detected fail-closed.
3. Scheduled ChatGPT consumes only the exact current GitHub-prepared checkpoint.
4. After a checkpoint is ingested, GitHub-owned logic prepares the next exact checkpoint automatically.
5. Daily schedule and user `Run now` use the same logical production path.
6. The user must not have to run a separate preparatory GitHub Action before every `Run now`.

## Route preference
Prefer wiring dossier manifest preparation into an existing canonical GitHub control-plane path that already owns Taste queue/pre-AI refresh, rather than creating an unrelated new recurring workflow.

For arbitrary manual `Run now`, first determine whether an existing safe GitHub-owned prepare/refresh handshake can be reused. If not, implement only the minimal GitHub-owned trigger/handshake needed so Scheduled ChatGPT can request deterministic preparation while GitHub still derives and publishes scope. ChatGPT must never construct the manifest itself.

Do not create a second recurring ChatGPT task.

If the manual `Run now` requirement would require materially new architecture not authorized by canonical contracts, stop before that architecture and return `needs_user_decision` with the exact conflict.

## Stale-manifest guard
Add a durable guard proving at least:
- source Taste backlog changes => old dossier manifest is not accepted as current READY;
- current builder run => manifest reflects current full eligible dossier scope;
- fresh existing dossiers remain reusable;
- READY is valid only when current-source remaining required work is actually zero.

Do not weaken fail-closed behavior.

## Prohibitions
Do not:
- change `Taste Semantic Producer`;
- change Taste production limits;
- resume Taste throughput measurement;
- perform age-priority work;
- redesign review semantics/TTL unless directly required;
- create a second dossier Scheduled Task;
- let Scheduled ChatGPT derive scope from `chatgpt_taste_queue.jsonl`;
- manually construct production manifest as a substitute for fixing orchestration;
- run the full Steam review backlog in the worker chat.

Existing 10 fresh production dossiers must remain reusable.

## Acceptance
Prove:
1. stale pre-merge/pre-source-change manifest cannot yield false `ready_from_fresh_cache`;
2. GitHub-owned preparation rebuilds from current full eligible Taste backlog;
3. `>10` missing/stale eligible dossiers produce first exact checkpoint with correct total completeness state;
4. ingest of checkpoint 1 automatically yields next GitHub-prepared checkpoint;
5. fresh reuse remains correct;
6. base-support-only/non-Taste rows remain excluded;
7. exact Taste semantic pin behavior remains unchanged;
8. Scheduled ChatGPT cannot bypass absent/stale control-plane state;
9. daily and `Run now` use the same logical path;
10. no separate recurring ChatGPT task/backlog manager is introduced;
11. `Taste Semantic Producer` remains unchanged.

Run focused deterministic regressions plus the smallest safe control-plane smoke. Do not execute the actual Steam review backlog; the user performs the next real `Run now` after Director acceptance.

## CURRENT_TASK.md
Update only for truthful handoff/status bookkeeping; do not erase unrelated active work.

## Durable report
Write:
`reviews/worker_reports/taste-steam-review-dossier-control-plane-refresh-01.md`

Include root cause, exact GitHub-owned route, any reused or added trigger/handshake, stale-manifest binding/guard, changed files, focused tests, proof ChatGPT does not own scope, Scheduled Task invariance, and one next step.

Allowed final statuses:
- `complete_ready_for_user_run_now_validation`
- `needs_user_decision`
- `blocked`

Do not report `blocked` without a concrete verified blocker.

## Expected next step
Director reviews the report. If accepted, user presses `Run now / Выполнить сейчас` on the existing `Taste Steam Review Dossier` once more. Success: the same invocation receives current GitHub-prepared work and continues through checkpoints until backlog exhaustion or a genuine runtime/tool limit, with prior checkpoints durable.
