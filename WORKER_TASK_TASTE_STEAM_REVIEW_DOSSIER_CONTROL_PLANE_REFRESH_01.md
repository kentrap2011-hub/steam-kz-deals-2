# WORKER TASK — Taste Steam review dossier daily full-backlog control plane 01

Task ID: `taste-steam-review-dossier-control-plane-refresh-01`

Status: `authorized_revised_ready_for_worker`

Mode: `IMPLEMENT`

## User-approved architecture

Use a simple daily two-stage model:

1. **GitHub once per day prepares one complete canonical dossier backlog for that day** from the current eligible Taste queue.
2. The existing ChatGPT Scheduled Task `Taste Steam Review Dossier` reads that complete GitHub-prepared backlog and processes it from start to finish.
3. The worker may save progress in small durable checkpoints (10 is acceptable), but checkpoint size is only a persistence/runtime boundary. It must not determine what work GitHub exposes and must not become a per-run or daily quota.
4. If the prepared daily backlog is empty, dossier work for that prepared day is complete.
5. If the ChatGPT run hits a genuine runtime/tool limit, already completed checkpoints stay durable and the next invocation resumes the same prepared daily backlog from the remaining items.
6. A manual `Run now / Выполнить сейчас` is allowed to use the most recently prepared daily GitHub backlog. It does **not** need to force an on-demand GitHub refresh. New source changes that appear after the daily preparation may wait until the next daily GitHub preparation.

This decision intentionally replaces the more complicated design where GitHub exposes only the next 10 items and must rebuild a new manifest after every checkpoint.

## Goal

Implement this daily full-backlog architecture with GitHub remaining the production control-plane owner and ChatGPT remaining only the bounded semantic/evidence worker.

The user must not need to manually run a GitHub Action before the normal daily dossier task.

## Background

The prior full-backlog implementation is already on `main`:
- report: `reviews/worker_reports/taste-steam-review-dossier-full-backlog-01.md`;
- PR `#16`;
- merge `ecde503c6b74aa964e7b331da009f87af8d0b3cd`.

A real `Run now` after that merge processed 0 new dossiers because the canonical `taste_steam_review_dossier_work.json` was still an older `ready_from_fresh_cache` manifest prepared before the merge. The Scheduled Task correctly refused to derive scope by itself.

Root architectural simplification now authorized by the user:
- GitHub should not expose only one 10-item work checkpoint;
- GitHub should prepare the **entire daily eligible dossier backlog** in one canonical manifest/snapshot;
- ChatGPT should process that fixed prepared backlog sequentially, checkpointing persistence internally as needed.

## Mandatory START / architecture preflight

Follow `CHAT_PROTOCOL.md` START gate first.

Before writes, verify the minimal current route and reconcile the canonical contracts. At minimum inspect only what is needed from:
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- relevant `PROJECT_ROUTES.md` entry if present;
- `PROJECT_DECISIONS.md` relevant Taste dossier rationale;
- current GitHub path that creates/refreshes `data/production/pre_ai/chatgpt_taste_queue.jsonl`;
- current dossier manifest/build/ingest/persistence scripts;
- existing daily production workflow that can own the once-daily preparation step.

Do not perform a broad repository re-audit.

If current canonical wording still encodes a next-10 manifest as the production scope, update the contract/rationale first, then implementation.

## Ownership invariants

GitHub/control-plane owns:
- the exact eligible daily dossier scope;
- source snapshot/provenance binding;
- fresh/stale/missing determination at preparation time;
- deterministic order/dedupe;
- retry/completeness state;
- validation and canonical persistence;
- deciding when the prepared daily backlog is fully complete.

Scheduled ChatGPT owns only:
- reading the exact prepared daily backlog;
- collecting Steam store/review evidence for those exact prepared items;
- producing neutral compact dossiers;
- submitting/persisting results through the canonical repository-defined interface;
- proceeding through that already-prepared list until complete or a genuine runtime/tool limit.

ChatGPT must not add games that are not present in the prepared daily backlog and must not derive scope directly from `chatgpt_taste_queue.jsonl`.

## Required daily preparation behavior

Integrate dossier backlog preparation into the appropriate existing GitHub-owned daily control-plane path whenever possible. Prefer adding a deterministic step to the existing daily/pre-AI production workflow rather than creating an unrelated new recurring workflow.

Each daily preparation must:
1. read the current canonical eligible Taste queue;
2. exclude non-Taste/base-support-only rows;
3. deduplicate deterministically by Steam `appid` while preserving canonical queue order;
4. reuse fresh valid dossiers;
5. include every currently missing or stale eligible dossier in the **same prepared daily backlog**;
6. persist source/provenance identity and preparation timestamp strongly enough to identify which daily source state the manifest represents;
7. publish the complete prepared backlog before the ChatGPT dossier task's normal daily execution time.

If zero items require work, publish a valid current empty daily backlog/READY state.

## Daily backlog semantics

The canonical daily manifest/snapshot must represent the full prepared workset for that day, not merely the first checkpoint.

Example:
- 37 items need dossiers at daily preparation time;
- GitHub publishes all 37 as the prepared backlog;
- ChatGPT processes items 1–10 and durably persists;
- then 11–20;
- then 21–30;
- then 31–37;
- only then is that prepared backlog complete.

There is no GitHub scope rebuild between those checkpoints merely to reveal the next 10 items.

If a run stops after 20 because of a real runtime/tool limit:
- the first 20 remain durable;
- the same prepared backlog records/derives 17 remaining;
- the next daily or manual invocation resumes those 17 without redoing the first 20.

## Manual Run now semantics

A user-triggered `Run now` consumes the latest valid prepared daily backlog.

It does not need to trigger an immediate GitHub rebuild first.

Therefore:
- if today's prepared backlog still has remaining items, `Run now` continues them;
- if today's prepared backlog is complete/empty, `Run now` may correctly do nothing;
- if the underlying Taste queue changed after today's preparation, those new changes may wait until the next daily GitHub preparation.

This is intentional and should be documented in the durable report.

## Scheduling integration

Ensure the GitHub-owned daily preparation happens before the existing `Taste Steam Review Dossier` Scheduled Task with a safe margin.

Do not change `Taste Semantic Producer`.

Do not change the existing dossier Scheduled Task unless its prompt must be minimally updated to consume the new full daily manifest semantics. If such a prompt change is required, change only that existing dossier task, never create a duplicate, and document the exact change.

If the current GitHub daily workflow timing already guarantees preparation before the dossier task, reuse it.

## Persistence / checkpoint behavior

Preserve durable incremental persistence.

Checkpoint size may remain 10, but:
- it must not limit the prepared backlog;
- it must not require a new GitHub scope build after each checkpoint;
- it must not be interpreted as a daily quota;
- completed items must not be regenerated on resume;
- one bad item must not destroy prior successful progress;
- completion is based on zero remaining items from the prepared daily backlog.

Use the minimal repository-native state representation needed to support resume idempotently.

## Freshness / TTL

Keep existing dossier TTL behavior unless a small compatibility adjustment is required:
- default TTL 20 days;
- fresh dossiers reused;
- stale/missing eligible dossiers included in next daily preparation;
- existing 10 fresh production dossiers remain reusable.

Do not redesign review semantics.

## Prohibitions

Do not:
- change `Taste Semantic Producer`;
- change Taste production limits;
- resume Taste throughput measurement;
- perform age-priority work;
- create a second dossier Scheduled Task;
- create a second Taste producer;
- let ChatGPT choose or expand daily scope;
- require an on-demand GitHub refresh before every manual `Run now`;
- keep the old next-10-as-manifest architecture merely for compatibility if it conflicts with this approved design;
- execute the real full Steam review backlog in the worker chat.

## Required validation

Acceptance must prove at least:

1. Daily preparation with 25 missing/stale eligible games publishes one prepared backlog containing all 25, not only 10.
2. ChatGPT-side/runtime simulation can progress `25 -> save 10 -> save 10 -> save 5 -> complete` without GitHub rebuilding scope between checkpoints.
3. A runtime stop after the first 10 or 20 resumes the same prepared backlog without redoing completed dossiers.
4. READY/complete occurs only when zero items remain from that prepared daily backlog.
5. A current empty daily backlog is a legitimate no-work state.
6. Fresh dossiers are excluded/reused; stale and missing eligible dossiers are included.
7. Base-support-only/non-Taste rows are excluded.
8. Deduplication/order remain deterministic.
9. Exact downstream Taste semantic pin behavior remains unchanged.
10. A source queue change after daily preparation does not mutate the already-prepared daily backlog; it is picked up by the next daily preparation.
11. A manual `Run now` uses the latest prepared daily backlog and does not require an on-demand GitHub rebuild.
12. GitHub preparation is wired into an actual daily control-plane path that runs before the dossier Scheduled Task.
13. No new recurring ChatGPT task/backlog manager is introduced.
14. `Taste Semantic Producer` remains unchanged.

Run focused deterministic regressions and the smallest safe workflow/control-plane smoke needed to prove the daily preparation route.

Do not execute the real Steam review backlog. The user will run the existing Scheduled Task after Director accepts the report.

## Durable decision / routes

Because this is a durable architecture simplification, update the appropriate canonical rationale/route (`PROJECT_DECISIONS.md` and/or `PROJECT_ROUTES.md`) if existing entries would otherwise direct future workers back to the old next-checkpoint manifest design.

## CURRENT_TASK.md

Update only for truthful task handoff/status bookkeeping. Do not erase unrelated active work.

## Durable report

Write:
`reviews/worker_reports/taste-steam-review-dossier-control-plane-refresh-01.md`

Keep it compact and include:
- exact old defect;
- exact daily GitHub preparation route chosen;
- full-daily-backlog manifest/state semantics;
- checkpoint/resume semantics;
- manual `Run now` semantics;
- any Scheduled Task prompt change, if actually required;
- changed files;
- focused tests/workflow smoke;
- confirmation that GitHub still owns scope and ChatGPT cannot add work;
- confirmation that `Taste Semantic Producer` remains unchanged;
- one next step.

## Allowed final statuses

- `complete_ready_for_user_run_now_validation`
- `needs_user_decision`
- `blocked`

Do not report `blocked` without a concrete verified blocker.

## Expected next step

Director reviews the durable report. If accepted, the user presses `Run now / Выполнить сейчас` on the existing `Taste Steam Review Dossier` task. Success means it consumes the latest prepared daily backlog, processes more than 10 when more than 10 remain, persists checkpoints durably, and either exhausts that prepared backlog or stops only on a genuine runtime/tool limit with completed progress preserved.
