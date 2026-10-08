# DIRECTOR HANDOFF — CURRENT

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

This is the compact transfer point for the next Director chat.

## MANDATORY FIRST RESPONSE IN THE NEW DIRECTOR CHAT

The user's first expected response is **NOT** a new repository audit.

Before doing anything else, answer the user's three unresolved questions from the previous Director chat:

1. Give concrete examples of games that the shortlist-reduction diagnostic would move out of the first semantic wave, and explain the exact reason for each. Be precise that these games are **deferred to reserve, not permanently deleted/excluded**. Use current known examples/signals already summarized below; do not start a broad code/data investigation just to answer.
2. Explain why PR #157 was created at all, and why PR #157 now differs/conflicts with `main`.
3. Explain why the previous Chat 2 continuation message was unnecessarily long, and provide a shorter normal worker continuation message style going forward.

Only after answering those three questions should the new Director continue project management.

## CONTEXT-BUDGET / DEPTH RULE — VERY IMPORTANT

The Director must stay shallow and conserve context.

- Do **not** broadly inspect code, scripts, old PRs, workflows, historical reports, or repository trees just to "understand the project".
- Start from this handoff and only the **top/current** Board state.
- For a concrete question, inspect only the exact artifact needed.
- If answering correctly would require deep implementation/code analysis, **do not perform that analysis in the Director chat**. Create/assign a bounded worker task instead.
- Do not duplicate analysis already completed by a worker report.
- Do not re-open accepted PR #156 architecture freeze unless there is direct contradictory evidence.
- Keep Director responses concise and decision-oriented.

## THREE-QUESTION FACTS ALREADY ESTABLISHED

### CURRENT USER DECISION — SUPERSEDES FIRST-WAVE/RESERVE IMPLEMENTATION

The user rejected semantic first-wave/deferred-reserve gating as the production direction.

Current approved and implemented direction:
- keep the full canonically eligible semantic pool;
- do not defer ordinary eligible candidates merely to shrink semantic work;
- GitHub-owned ordering prioritizes never-Deep-analyzed subjects first;
- within comparable cohort, priority uses Steam positive rating + logarithmic review-count confidence + current price + current discount;
- no hard top-N and no eligibility reduction;
- implementation task: `WORKER_TASK_STEAM_SEMANTIC_QUEUE_PRIORITY_IMPLEMENT_01.md`;
- PR #158 accepted and merged as `9c9d79194fba3ff22ad491d80257277a87fdcfaf`;
- validations on PR head were green;
- no Stage 1/Stage 2 scoring logic changed;
- ЧАТ 1 task-page work is fully accepted and published: PR #165 fixed the closeout regression and merged as `b9ad7aed7bcc76237fb3402a291cb632ac730598`; real Pages deploys 37768728895 and 37769122260 succeeded. ЧАТ 1 is complete and free.
- PR #157 remains closed without merge as superseded.

The older ~581 + ~1,720 reserve analysis below remains historical diagnostic evidence only and must not be turned into production gating unless the user explicitly reopens that decision.

### A. Shortlist reduction: what happens to the ~1,700

Current corrected main report:
`reviews/worker_reports/steam-shortlist-scope-reduction-diagnostic-02.md`

Current funnel:
`2,522 shortlist offers -> 2,385 purchase families -> 2,301 semantic families`.

Corrected recommendation currently in `main`:
- first semantic wave: about **581** families;
- roughly **1,720** remain as `deferred_reserve`;
- reserve is **not** `not_fit`, not deleted, and not removed from canonical source truth;
- after the new 60/40 Deep model is production-active, GitHub may keep promoting reserve items that can still mathematically beat the current top-100 boundary.

Why reserve rather than permanent exclusion:
- when the same deterministic gates are tested on 112 current known Deep-fit games *without* protecting them because they are already known fit, only **23/112 (20.5%)** naturally pass the balanced ~581 gate;
- therefore Steam metadata/reviews/tags are too weak to safely make permanent taste decisions.

Concrete current examples of the type of rows likely to be deferred unless another protected lane applies:
- **Superliminal** — current discovery reasons are generic quality only (`mainstream_quality`, `very_high_rating`, `high_confidence_adjacent`), 92.5% / ~14.5k reviews, 60% discount; moderate purchase scenario says `ЛУЧШЕ ЖДАТЬ`. Under the balanced first-wave design, standalone generic routes do not qualify.
- **Seen** — `mainstream_quality` + `very_high_rating`, 90.5% / ~9.3k reviews, 50% discount; moderate scenario `ЛУЧШЕ ЖДАТЬ`. No stronger personal-fit route is visible in the current deterministic reasons.
- **Russian Life Simulator** — `mainstream_quality` only, 88.5% / ~7.1k reviews, 50% discount; moderate scenario `ЛУЧШЕ ЖДАТЬ`.
- **Sayonara Wild Hearts** — `very_high_rating` only, 94.5% / ~3.7k reviews, 50% discount; moderate scenario `ЛУЧШЕ ЖДАТЬ`.

Use these as examples of **why an item is deferred from the first wave**, not proof it can never be good. If a protected lane (Wishlist, already authoritative Deep-fit, direct user reference, package/bundle lane, current DLC lane, or protected strong-commercial lane) applies, that protection overrides ordinary defer logic.

### B. PR #157: why it exists and why it diverged

PR #157:
`Steam shortlist scope reduction diagnostic 02`

Exact chronology:
- PR branch `diagnostic-steam-shortlist-scope-reduction-02` contains two commits:
  - `c9aa423...` — add diagnostic report;
  - `3abeb5e...` — record diagnostic completion.
- That PR's report is the **older recommendation**, around **784** families in a conservative first wave.
- After the PR was created, the worker performed a stronger Deep-fit recall backtest and wrote corrected report commits into **main**:
  - `6b79acb...` — report;
  - `9f3c879...` — corrected recommendation with Deep-fit recall backtest.
- The corrected `main` report recommends ~**581 first-wave + reserve**, not the older 784 permanent-style recommendation.
- `CURRENT_TASK.md` also moved independently in main.
- Therefore PR #157 is now `dirty`/conflicting: its branch contains an older version of files that were later changed directly in main.

Why PR #157 was created: the worker used a normal task branch/PR path for the report and CURRENT_TASK update. The later corrections were not applied back to that branch; they landed in main. Do not merge PR #157 blindly. First decide whether it contains any unique useful content not already superseded by main; likely outcome is close it as superseded after a bounded comparison.

### C. Why the previous Chat 2 message was too long

The Director over-packed the continuation prompt with state the worker can read from GitHub. Going forward, continuation prompts should contain only:
- repo/source of truth;
- exact task filename;
- one or two critical known blockers/state facts;
- explicit "continue, do not restart";
- explicit boundaries if necessary.

Do not restate the entire task specification in the chat message when the canonical task file already contains it.

- ЧАТ 1 historical backlog audit is accepted via PR #167. Five strong restoration candidates and three Director-decision cases were found; none are yet auto-restored. Physical slot is free.

- ЧАТ 1 active: `WORKER_TASK_DOSSIER_THROUGHPUT_QUALITY_PRESERVING_DIAGNOSTIC_01.md`. Diagnostic only; quantify Dossier bottlenecks/rejections and recommend speedups without lowering evidence/provenance/validation quality. No implementation or Scheduled Task changes.

## CURRENT PHYSICAL WORKER SLOTS

### ЧАТ 1 — DIAGNOSTIC COMPLETE

Task:
`WORKER_TASK_STEAM_SHORTLIST_SCOPE_REDUCTION_DIAGNOSTIC_02.md`

Status:
`diagnostic_complete_recommendation_ready`

Authoritative corrected report is already in `main`:
`reviews/worker_reports/steam-shortlist-scope-reduction-diagnostic-02.md`

Recommendation:
- ~581 first semantic wave;
- ~1,720 deferred reserve;
- do not permanently exclude reserve;
- do not implement until Director/user accepts semantics;
- future bounded implementation task proposed by report:
  `WORKER_TASK_STEAM_SEMANTIC_FIRST_WAVE_AND_RESERVE_IMPLEMENT_01.md`.

PR #157 remains open but conflicts with main and contains an older report variant. Do not merge it blindly.

ЧАТ 1 physical slot is available after the Director resolves/records the PR #157 disposition.

### ЧАТ 2 — STAGE 2 ACCEPTED / CONTINUE STAGE 1

Accepted task:
`WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md`

Accepted PR:
`#159` merged as `06aeeda19bf550899fd690f08f413e58d6f33b1d`

Deep Stage 1 is accepted and merged via PR #163 as `e410ee6183e29ec595f2c1fce1336751ceea9585`.

Deep Fast-removal/ranking migration preparation is accepted via clean replacement PR #166 (`4d1cfb4745989994051f6233a3810759f1f1a305`). Old #164 is closed superseded. The new scorer remains non-active until cutover; remaining Deep prerequisite is the separate mirror UI/Statistics implementation. Physical ЧАТ 2 is free.

Branch:
`implement/deep-stage2-calibration-worker-01`

Known work already present on branch:
- Stage 2 manual worker prompt;
- Stage 2 work manifest;
- state file;
- validation workflow;
- partial implementation start.

Latest known branch head:
`8e674ea33ecc2710acc2bb1946ab741a0971e06d`

Known failed validation:
`Validate Deep Stage 2 calibration` run `37509068199`

Immediate failure:
workflow compile step references missing `scripts/deep_stage2.py`.

No Stage 2 PR or final worker report existed at the last Director check.

Correct continuation style for ЧАТ 2 should be short, e.g.:

```
Продолжай текущую задачу:
WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md

Рабочая ветка уже есть:
implement/deep-stage2-calibration-worker-01

Не начинай заново. Последняя проверка 37509068199 упала на отсутствующем scripts/deep_stage2.py.
Продолжи реализацию, добей проверки, создай PR и worker report.

Не переходи к следующей задаче.
```

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
`WORKER_TASK_STEAM_SHORTLIST_SCOPE_REDUCTION_DIAGNOSTIC_02.md`

Mode:
`READ-ONLY / DIAGNOSTIC / OFFLINE SIMULATION`

Current fresh funnel is roughly 60,632 paid eligible -> 7,972 broad -> 2,522 paid shortlist -> ~2.3k Dossier/Deep semantic target. The user wants ЧАТ 1 to analyze how to reduce this much further without restoring the old accidental shrinkage caused by broken review enrichment.

The task must quantify which admission rules create the current explosion, simulate safer stronger gates, protect Wishlist/packages/known-good candidates, and compare conservative/balanced/aggressive semantic-pool sizes. No implementation.

### ЧАТ 2 — ASSIGNED / SOLE DEEP LOGIC OWNER

Current task:
`WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md`

The user explicitly wants one physical worker chat to carry the Deep logic changes forward to avoid split logic ownership.

Sequence in this same physical chat, with separate task boundaries/reports/PRs:
1. finish `WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md`;
2. then implement `WORKER_TASK_DEEP_STAGE1_WORKER_IMPLEMENT_01.md`;
3. then implement `WORKER_TASK_DEEP_FAST_REMOVAL_RANKING_MIGRATION_01.md`.

Do not merge these into one uncontrolled PR. Close/validate each task cleanly before the next.

ЧАТ 1 must not touch Deep logic while this assignment stands. Site/UI remains a later separate implementation task. Production authority remains unchanged until final integration/cutover.

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
