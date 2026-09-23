# DIRECTOR BOOTSTRAP

Last refreshed: 2026-09-23

Purpose: compact restart context for a **NEW physical Director conversation**.

This file is a bootstrap snapshot, not a replacement for canonical project truth. After reading it, the Director must use the latest `CHAT_PROTOCOL.md`, `DIRECTOR_PROTOCOL.md`, `DIRECTOR_TASK_BOARD.md`, exact active task files, and durable worker reports as authoritative. If this file conflicts with newer canonical state, newer canonical state wins.

## Repository scope

Repository: `kentrap2011-hub/steam-kz-deals-2`  
Base branch / source of truth: `main`

Do not search, read, change, or use another repository for this project unless an exact task explicitly authorizes it.

## Director role

- Director orchestrates; worker chats execute nontrivial project work.
- GitHub owns production control-plane state.
- Interactive Director chat must not become a production semantic worker or backlog manager.
- No autonomous IMPLEMENT without explicit user authorization.
- Reconcile Board -> exact task -> exact durable report before any worker follow-up.
- When the user says a worker finished, read the expected durable worker report from GitHub directly; do not ask the user to paste it.
- Any copyable worker handoff must say outside the block where it goes (NEW or EXISTING physical chat + slot) and repeat the slot as the first line inside the block.
- `ЧАТ 1` / `ЧАТ 2` are reusable slots, not durable identities. Retired physical chats are not reused for unrelated tasks.
- At most two independent worker slots should be active when safe.

## Scheduled Task operator boundary

The user personally handles ChatGPT Scheduled Task UI/settings.

Do **not** create, edit, enable, disable, pause, delete, reschedule, rename, recreate, or run a Scheduled Task unless the user gives a direct explicit instruction for that exact action and the required tool is actually available.

Do not infer permission from phrases such as “делаем”, “запускаем”, or from a project task that only changes repository regulation.

## Current architecture

### Fast / Dossier / Deep

Accepted current model:

- Fast / PASS 1 = provisional early personalized analysis.
- Dossier = independent neutral evidence preparation; never decides fit/not-fit.
- Deep / PASS 2 = eventual authoritative personalized analysis for every current eligible game.
- Deep eligibility does **not** require prior Fast.
- A current exact-compatible canonically accepted Dossier is the Deep evidence gate.
- Deep may run before Fast.
- Successful authoritative Deep fit/not-fit supersedes Fast.
- Fast success never suppresses eventual Deep.
- Deep incomplete/error does not erase a still-valid Fast provisional result.
- Recovery is separate GitHub-owned authorization; no blind retry loop.

Both Fast and Deep production are active under their accepted contracts unless fresher Board state says otherwise.

### Dossier retrieval

The old hard per-game numeric ceilings are removed.

Current accepted Dossier boundedness:
- no hard 8-search ceiling;
- no hard 16-opened-page ceiling;
- no replacement arbitrary number;
- stop when evidence is sufficient, when all reasonably discoverable mandatory materially distinct routes are exhausted, on directly observed blocker/binding/liveness change, or ordinary invocation runtime;
- materially equivalent route repetition remains forbidden;
- query/page counts are diagnostics only, with null limit fields.

Canonical decision: `TASTE-014`.

## Immediate active worker state

Read the **fresh `DIRECTOR_TASK_BOARD.md` first**. At this bootstrap refresh, the active worker is:

### ACTIVE — ЧАТ 1 — Progressive PASS 2 optional Dossier inbox staging recovery fix

Task:
`WORKER_TASK_PROGRESSIVE_PASS2_OPTIONAL_DOSSIER_INBOX_STAGING_RECOVERY_FIX_01.md`

Report:
`reviews/worker_reports/progressive-pass2-optional-dossier-inbox-staging-recovery-fix-01.md`

Known confirmed blocker at assignment time:
- GitHub PASS 2 ingest accepted one current result in the working tree, then persistence failed because commit staging treated absent optional `data/ai_inbox/taste_steam_review_dossiers` as mandatory;
- current exact Shadow Warrior 3 result artifact already existed and must be canonically ingested without semantic rerun;
- the task is an IMPLEMENT fix inside the existing shared canonical-writer path;
- no Scheduled Task action and no Deep semantic rerun are authorized by that task.

When the user says this worker finished, read the exact durable report before deciding anything else.

## Dossier live result already observed

After the clean Scheduled Dossier experiment and semantic-bounded-retrieval change, GitHub canonically accepted three groups / nine dossiers in one observed run sequence with zero failed groups at that check. This proved that the clean Dossier entrypoint and new retrieval contract can progress canonical Dossier state.

Treat fresh Dossier index/progress as authoritative for any later count; do not reuse the old 3-group/9-dossier count as current progress.

## Site / UI product decision — accepted design, implementation not yet authorized

The user accepted this target presentation:

- remove the large always-visible statistics block from the main page;
- add a compact **“Статистика”** entry/button leading to a dedicated statistics page;
- do not show large textual card statuses such as “Подходит вам”, “Не подходит”, “Нужен дополнительный разбор”, or “Ещё не проверена”;
- a trustworthy analyzed **not-fit** game is excluded from the normal visible list rather than shown with a “not fit” badge;
- use three small visual stage icons on each card for:
  1. **Быстрый разбор** (Fast),
  2. **Подготовка досье** (Dossier),
  3. **Глубокий разбор** (Deep);
- icon state should communicate stage progress/result without duplicating a large textual status;
- after successful personalized analysis, show the existing personalized score and supported explanation/why-fit fields;
- analyzed-fit games use the existing personalized ranking authority / score ordering within their tier;
- unresolved / not-yet-analyzed games must not receive fake personalized scores;
- unresolved games remain lower tiers until resolved; trustworthy not-fit disappears from the normal list;
- the browser remains presentation-only and must not infer semantic fit/stage truth.

The old task `WORKER_TASK_PROGRESSIVE_SITE_PROGRESS_HEADER_COMPACTION_01.md` is stale/draft and must **not** be executed unchanged.

No new site IMPLEMENT task has yet been authorized solely by this product-design agreement. If the user asks to implement the site, create a fresh bounded UI task for a NEW physical worker chat.

## Director reliability gate

Before every decision or handoff:

1. Read/reconcile current `DIRECTOR_TASK_BOARD.md`.
2. Read the exact active task and exact durable report when available.
3. Separate confirmed facts from assumptions/unknowns.
4. Scan for contradiction with current ownership, runtime, scheduler, recovery, and user authorization.
5. Verify the proposed actor actually exists and owns the action.
6. Only then issue the next handoff or recommendation.

Do not reconstruct project truth from retired Director conversation history unless canonical compact state is genuinely insufficient.

## Rotation state

The Director conversation that produced this refresh is now being retired by user request.

Continue only in a **NEW physical Director conversation** using this bootstrap plus the fresh Board and protocols.
