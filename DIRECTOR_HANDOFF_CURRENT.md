# DIRECTOR HANDOFF — CURRENT

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

This is the compact transfer point for the next Director chat.

## CRITICAL START RULE FOR THE NEXT DIRECTOR

Do **not** reconstruct the project by roaming through the entire repository.

Do **not** enumerate all PRs, branches, workflow history, old worker reports, or old Board sections just to rebuild context.

Preserve context and token budget.

Start in this order only:

1. Read current `DIRECTOR_PROTOCOL.md` and `CHAT_PROTOCOL.md`; perform only the required Director START gate.
2. Read this file fully.
3. Read only the top/current section of `DIRECTOR_TASK_BOARD.md`.
4. For a concrete user request, open only the exact task/report/config/artifact referenced here or by that request.
5. Inspect wider GitHub history only when there is a specific contradiction, missing fact, failed check, or explicit user request.

Treat old Board sections as historical unless this handoff explicitly points to them.

## CURRENT PHYSICAL WORKER SLOTS

### ЧАТ 1 — ASSIGNED / NEW PHYSICAL CHAT

Task:
`WORKER_TASK_STEAM_REVIEWS_PUBLICATION_BLOCKER_FIX_01.md`

Mode:
`DIAGNOSE / IMPLEMENT / VALIDATE / LIVE ACCEPTANCE`

Previous Steam discovery task is accepted. Normal main run `37357943696` completed successfully in ~39 minutes with complete games+DLC discovery (97,998 rows), Search 429 reduced to 1, canonical persistence successful and downstream refresh dispatched.

New exact blocker begins after discovery: AppReviews enrichment opened its circuit after ~310 physical review requests, only 147 AppIDs completed both global/Russian review calls, logical failure rate reached ~99.75%, and immediate mailing/visual downstream runs failed. The new task must diagnose the exact review/circuit cause and the exact downstream failure chain, then apply the smallest correction without reopening accepted discovery scope.

### ЧАТ 2 — ASSIGNED / ARCHITECTURE FREEZE

Task:
`WORKER_TASK_DEEP_TWO_STAGE_ARCHITECTURE_FREEZE_01.md`

Mode:
`ARCHITECT / CONTRACT-FREEZE / NO PRODUCTION CUTOVER`

The former monolithic `WORKER_TASK_DEEP_TWO_STAGE_COMPARATIVE_CALIBRATION_IMPLEMENT_01.md` is now an umbrella requirements source only. Do not implement the whole redesign in one chat.

Freeze the Stage-1, Stage-2, score, migration and site interfaces first. After acceptance, implementation is intentionally distributed across separate new physical chats:

Wave 2, parallel when both slots are free:
- `WORKER_TASK_DEEP_STAGE1_WORKER_IMPLEMENT_01.md`
- `WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md`

Wave 3, parallel:
- `WORKER_TASK_DEEP_FAST_REMOVAL_RANKING_MIGRATION_01.md`
- `WORKER_TASK_DEEP_SITE_MIRROR_UI_STATISTICS_IMPLEMENT_01.md`

Wave 4:
- `WORKER_TASK_DEEP_TWO_STAGE_INTEGRATION_CUTOVER_01.md`

Current approved product semantics remain:
- two separate semantic worker chats for Stage 1 and Stage 2;
- Stage-1 dynamic point explanation + provisional score;
- Stage-2 neighbor comparison + final calibrated score;
- calibrated Deep 0–56 + deterministic Wishlist +4 = personal /60;
- purchase/deal /40; total /100;
- distinct calibrated positions need distinct displayed decimal personal scores;
- compact card shows only final Stage-2 authority;
- details expose both scores, delta, positives, negatives, nuances and why above/below;
- Statistics shows Stage 1 and Stage 2 as separate blocks;
- Fast removed from current semantic authority;
- no Scheduled Task changes without separate user authorization.

## CURRENTLY WORKING / RECENT SEMANTIC CHATS

These do **not** occupy physical ЧАТ 1/2 slots.

### Russian-description manual semantic worker — STOPPED AFTER INGEST FAILURE

Canonical prompt:
`config/russian_description_manual_semantic_worker_prompt.md`

A one-shot run was authorized and submitted checkpoint 1, but canonical ingest rejected the checkpoint. Do not retry or retranslate it in the semantic worker.

Relevant commits:
- authorization: `30f59b693cdef3eca520ddc78334850fdf850948`;
- checkpoint 1 submission: `32caa3b35fb750cd31da7198f28e34855928edd6`.

Current confirmed result after checking ingest:
- ingest run `37138503097` failed at `Validate and ingest current submissions`;
- exact failing item observed: AppID `1237980`, request `2aeac6b...`, translated result failed the `good_ru` gate;
- canonical cache/status did not persist checkpoint 1;
- current queue remains 82 and the last successful translation timestamp remains 2026-10-01 at the Director check.

Do **not** tell the semantic worker to redo checkpoint 1. ЧАТ 2 now owns the user-authorized implementation that will isolate bad items, accept valid siblings, create translation diagnostics, and reconcile the existing checkpoint without retranslation.

No Scheduled Task action is authorized.

### Progressive Deep semantic worker — ACTIVE / RECENT

A current Deep invocation started and has begun submitting results.

Relevant commits:
- run start: `0b47a0fe3830dfbcec37fa5a2395d6be08169067`;
- result AppID 1577120: `7005c0f0901e33e087494c92617bbe1e71b2bf0c`;
- result AppID 1237980: `0622b86499dab789711b07ab7f08270eb0bda0e3`.

Current PASS 2 manifest observed at handoff had 23 items.

Do not rebuild, reorder, or restart Deep scope. If the user asks for status, inspect the current canonical PASS 2 work and the latest exact worker/result commits only.

### Dossier semantic worker — ACTIVE / RECENT

The frozen-authority behavior is already on `main` and recent Dossier work is progressing.

Canonical snapshot at handoff:
`a9a1390c7821fcc69c06f83e57c0297df0016e0d90e637ddccd7185d53bd8b19`

Observed current progress:
- next_pending_sequence: 5;
- accepted_group_count: 4;
- pending_group_count: 127;
- accepted_dossier_count: 12;
- pending_dossier_count: 379;
- failed_group_count: 0.

Recent commits:
- group 3 buffered: `391afad22736b6dd3ca0990eff480fecd3af228d`;
- group 3 ingested/reconciled: `1782812ec194cd8d78cd30c83d1a588008177bed` / `79f5e476774d122ba802655407d57ad54f3e3957`;
- group 4 buffered: `98f10a2c2f5c934b7c1ae3d890d8c490c7544d2c`;
- group 4 ingested: `1ae9bc6e55304ca5d773fb3a8b0b3f8e688003a1`.

Do not assume these counts remain current; if asked, read only the current worker index.

## MIRROR'S EDGE CATALYST — DIAGNOSIS COMPLETE

User-visible symptom:
Mirror's Edge Catalyst (AppID `1233570`) still did not appear after PR #140.

Do not re-diagnose.

Worker conclusion:
`diagnosis_complete_root_cause_identified`.

First causal stage:
**fresh Steam KZ discovery does not complete/persist**.

Key result:
- a real post-PR-#140 production discovery run did execute on `main`;
- run `37120664964` was cancelled at the 60-minute collector timeout;
- live Steam still exposed about `100307` rows despite the PR #140 `category1=998,21,996` bounding attempt;
- canonical discovery therefore remained the stale 2026-09-23 universe;
- Catalyst never reached shortlist, mailing, pre-AI, semantic work, ranking, or Pages.

Important split conclusion:
- PR #140 freshness/fail-closed guards are working;
- PR #140's live discovery-input bounding is not sufficient against current Steam behavior;
- live acceptance was attempted and failed in discovery itself;
- this is not a Dossier/Deep/ranking/Pages problem.

Smallest next action from the worker:
a bounded implementation task on the **existing Steam KZ production shortlist owner only** to make live discovery input/traversal actually bounded enough to finish inside the existing production cycle, with no Catalyst special case and no second scheduler/collector.

**Do not create that implementation task until the user authorizes fixing it.**

## RECENT ACCEPTED IMPLEMENTATIONS — DO NOT REOPEN WITHOUT NEW EVIDENCE

- PR #140 — fresh deal discovery freshness handoff:
  merge `7df5ed0cbe9dd9217c56344e0caab47dd366915f`.
  Freshness guards accepted; live discovery bounding remains the newly diagnosed unresolved part above.

- PR #141 — isolate PR validation from production `workflow_run` triggers:
  merge `da71fb7578c5fe467da0ce8e3decfbc62a6465a4`.
  PR validation can no longer masquerade as production authority.

- PR #143 — Dossier frozen invocation rollover safety:
  merge `a354500fc83d20fff89d19c0752aa2810898861e`.
  Already-started legitimate Dossier work no longer dies merely because a later daily snapshot replaces the current projection.

- PR #125 — Russian translations nonblocking + Statistics observability remains accepted.

- RANK-013 and accepted score/ranking architecture remain closed unless the user explicitly reopens them.

## IMPORTANT USER OPERATING RULES

- Director delegates implementation/diagnostics to worker chats; do not directly implement when user says “исправляем/делаем”.
- Max two physical developer worker slots: ЧАТ 1 and ЧАТ 2.
- Semantic workers (Dossier, Deep, manual translation) do not consume those physical slots.
- User remains operator of semantic runs/Scheduled Task UI.
- Never create/modify Scheduled Tasks unless explicitly requested.
- GitHub is source of truth.
- Explain simply in Russian.
- When checking a chat, prefer a narrow status check: branch/PR/report/latest checks. Do not inspect raw logs unless needed.
- Bootstrap for a physical worker must say `ЧАТ N`, point to the exact `WORKER_TASK_*.md`, and tell it not to start other tasks.
- Full task instructions belong in GitHub task files, not in the bootstrap.
- Concurrent GitHub writes are normal; never overwrite newer canonical production state.

## IMMEDIATE DIRECTOR PRIORITIES

1. Preserve and monitor the currently active semantic translation / Deep / Dossier work without restarting it.
2. If user asks about Catalyst, report the completed diagnosis above; do not redo it.
3. If user says to fix Catalyst/discovery, create a new bounded implementation task for a free physical slot, based on the completed diagnostic report.
4. If user asks about translation status, first check whether checkpoint 1 was ingested and then use the fresh canonical queue/status.
5. If user asks about Dossier or Deep status, inspect only their current exact canonical index/work/results.

## HANDOFF SNAPSHOT

Final observed recent `main` activity included:
- Deep result AppID 1237980: `0622b86499dab789711b07ab7f08270eb0bda0e3`;
- Catalyst diagnostic closeout: `62cf27a2ef7fd4c3312fe9b4a629bc4f539434d8`;
- Dossier/PASS2 reconciliation: `fb9bf4efa3445cbd27fc148035bd1b32e369e0d0`;
- Russian translation checkpoint 1 submission: `32caa3b35fb750cd31da7198f28e34855928edd6`.

This snapshot is descriptive only. Always trust newer exact canonical state if it has advanced.

## CONTEXT-CONSERVATION RULE

The next Director should assume this handoff is correct unless a **specific** current check contradicts it.

Do not spend context proving settled history again.

Do not fetch dozens of files “for completeness”.

Read the one exact file needed for the user's current question, answer it, and preserve the rest of the context window for actual decisions.
