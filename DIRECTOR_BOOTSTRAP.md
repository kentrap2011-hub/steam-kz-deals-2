# DIRECTOR BOOTSTRAP

Last refreshed: 2026-09-29

Purpose: compact restart context for a **NEW physical Director conversation** after the previous Director chat reached its context limit.

This file is a bootstrap snapshot, not a replacement for canonical project truth. The new Director must read current `CHAT_PROTOCOL.md`, `DIRECTOR_PROTOCOL.md`, fresh `DIRECTOR_TASK_BOARD.md`, and current `main` first. Newer canonical GitHub state always wins over this file.

## Repository scope

Repository: `kentrap2011-hub/steam-kz-deals-2`  
Base branch / source of truth: `main`

Use only this repository unless an exact task explicitly authorizes another repository.

## Director operating rules

- Director orchestrates; worker chats perform nontrivial diagnosis/implementation.
- Do not investigate implementation code deeply in the Director chat when a bounded worker task is appropriate.
- GitHub owns production control-plane state.
- Do not turn the Director into Dossier/Fast/Deep semantic worker.
- No nontrivial IMPLEMENT without explicit user authorization.
- Before decisions/handoffs reconcile fresh Board -> exact task -> exact durable report -> relevant PR/run metadata.
- For a new worker task, write full instructions into a `WORKER_TASK_*.md`; give user only the short launch prompt.
- Retired physical worker chats are not reused for unrelated work. Slot numbers ЧАТ 1/2 may be reused only as explicitly NEW physical chats.
- The user personally controls ChatGPT Scheduled Task UI. Do not create/edit/run Scheduled Tasks unless explicitly requested.
- Explain in simple Russian; minimize untranslated jargon.
- Default max parallel workers: 2.

## Current Director state

Current accepted Director-state commit before this bootstrap:
`3ff0a5041265851881499e18f87d8ece18eec450`.

Worker slots:
- ЧАТ 1: free.
- ЧАТ 2: free.
- Both latest physical worker chats are retired and may be deleted.
- No Scheduled Task action is authorized.

### Most important current user observation

After all recent merges, the user reports that the **live site still looks unchanged**:
- games whose discounts have ended are still visible;
- Statistics still shows the old/stale values.

Do not answer this by saying the fixes are already merged. The user is explicitly reporting the actual live site behavior.

The next Director must determine what is **actually deployed on GitHub Pages** now: both browser code and `web/data/current.json`/visual payload. Do not infer live state from `main` or from a green workflow name.

## Latest accepted implementations

### 1. Expired-sale immediate browser visibility — accepted, merged, but live publication not proven

Task:
`WORKER_TASK_EXPIRED_SALE_IMMEDIATE_VISIBILITY_FIX_01.md`

Report:
`reviews/worker_reports/expired-sale-immediate-visibility-fix-01.md`

PR #121 merged:
`9a500cefd3ec3bf460cf3c51afe92c35e55ab97b`

Behavior implemented in source:
- known valid `sale_end_utc <= now` hides the paid-sale card locally before queue/manual-end/urgency/cursor/count reconciliation;
- null/missing/malformed sale end remains visible;
- stale payload is intentionally supported: browser uses the stored end timestamp without a new Steam request;
- Titanfall® 2 / AppID 1237970 / `2026-09-28T17:00:00+00:00` is the pinned regression;
- Taste/Fast/Dossier/Deep state remains untouched.

PR and post-merge checks passed.

Important publication fact from worker report:
- post-merge full visual run `36518618313` reached the Russian-description gate and failed;
- deploy attempts `36518618351` cancelled, `36518623279` skipped, `36518660075` skipped;
- therefore no live Pages proof was established for the new browser source.

Since the user still sees expired cards, a high-priority hypothesis is that Pages is still serving older web code. This is plausible but must be verified from the actual deployed Pages artifact/source, not assumed.

### 2. Progressive migration current-scope regression — accepted, merged, pre-AI unblocked

Task:
`WORKER_TASK_PROGRESSIVE_MIGRATION_CURRENT_BINDING_REGRESSION_FIX_01.md`

Report:
`reviews/worker_reports/progressive-migration-current-binding-regression-fix-01.md`

PR #122 merged:
`1d8b54114d5aef09adb1c244a848f356987f3048`

Closeout PR #123 merged:
`0c9c343cdde12480d4ae631ba2f5f161d1e8b5d0`

Root cause:
- old regression wrongly assumed all 30 historical PPD-010 migration targets must remain in current Progressive scope forever;
- Black Skylands / `game:1143810` correctly left current scope after its sale ended;
- no missing semantic binding defect existed.

Fix:
- migration targets are now classified individually as current+equivalent, current+stale, or outside current scope;
- immutable Deep history preserved;
- no semantic reruns/rewrites.

Post-merge pre-AI run `36518529454` succeeded end-to-end.
Fresh atomic pre-AI commit:
`4836bea4c7c0822baa08c954cfbcfe6651ccb0d5`

Russian translation scope now persists:
- scope records: 283;
- translation queue: 71;
- direct Russian resolved: 212;
- nontranslatable blockers: 0;
- App_13500 and App_1155970 have exact-bound translation requests.

### 3. Current Russian-description source fallback — accepted implementation, translations still pending

Task:
`WORKER_TASK_CURRENT_RUSSIAN_DESCRIPTION_PUBLICATION_BLOCKER_FIX_02.md`

Report:
`reviews/worker_reports/current-russian-description-publication-blocker-fix-02.md`

PR #119 merged:
`c25762948500d6f64158047de01c7e4f5952911f`

Closeout PR #120 merged:
`cdbdfa721ced95a280fea7289330cae439150d0e`

Pinned game:
Prince of Persia: Warrior Within™ / AppID 13500.

Fix:
- meaningful exact-app non-Russian/weak-Russian appdetails text is retained only as translation input when direct Russian is unavailable;
- non-Russian text still cannot publish as `ready_ru`;
- meaningful-Russian gate remains strict.

After the current-scope regression fix, normal translation-scope persistence is restored. The remaining actual semantic translations for App_13500 and Roadwarden are still normal pending work; do not manually populate translation cache.

### 4. Deep-first final-score ranking — accepted, merged, live publication still unproven

Task:
`WORKER_TASK_DEEP_FIRST_FINAL_SCORE_ORDER_FIX_01.md`

Report:
`reviews/worker_reports/deep-first-final-score-order-fix-01.md`

PR #117 merged:
`9cb123765884440d37632740d51695a371338483`

Closeout PR #118:
`f200e809f169c7bd6b0ee74de3775bc8b6043614`

Canonical RANK-013:
`deep_fit -> fast_fit/provisional -> analysis_incomplete -> not_analyzed`.

Inside Deep/Fast:
`total_score DESC`.

Fast cannot outrank current Deep merely by higher score.
UI label changed to `Позиция в ленте: N из M`.

Do not reimplement this. Live publication is the missing proof.

## Accepted stale Statistics publication diagnosis — still relevant and not yet fixed

Task:
`WORKER_TASK_STALE_DEEP_STATISTICS_PUBLICATION_DIAGNOSTIC_01.md`

Report:
`reviews/worker_reports/stale-deep-statistics-publication-diagnostic-01.md`

The user's old/stale Statistics screenshot was proven to exist in the actual Pages artifact, not just browser cache.

Exact stale Pages payload:
- Pages artifact ID `10986847860`;
- visual source commit `2202a668cad11f67f0659aa6bcfe5e6cf34bb9ab`;
- old Deep values included total 387, completed 30, fit 24, not-fit 6, incomplete 10, waiting 338, ready 9, remaining 357;
- visible cards 381.

Root cause:
- Build daily visual payload built from an older source state;
- while build ran, `main` advanced;
- push failed;
- workflow rebased the already-generated old JSON onto newer `main` without rebuilding it;
- stale visual became canonical on a newer parent.

Required implementation from accepted diagnosis:
- bind generated full visual to exact source blobs;
- if relevant source state changes before persistence, do not rebase old generated JSON unchanged;
- rebuild from fresh main or fail closed;
- regression must reproduce old PASS2 blob being placed on newer parent.

This stale-snapshot rebase-race fix has **not** yet been implemented.

## Current live-site problem to handle next

The user now reports both:
1. expired sales still visible;
2. Statistics still stale.

These symptoms may have a common publication explanation:
- PR #121 browser fix is in `main` but may not have reached Pages;
- fresh visual/statistics payload has repeatedly failed to replace stale canonical visual;
- previous successful deploys were allowed to deploy `degraded/no_fresh_build` old artifacts.

However do not claim this as fully proven for the current moment until a worker checks the exact latest Pages artifact and deployment source.

### Recommended next task shape

Prefer one bounded **READ-ONLY / RECON** worker first:
`LIVE_SITE_POST_FIX_PUBLICATION_DIAGNOSTIC`

It should compare, for the current deployed Pages artifact:
- deployed `web/app.js` / browser-source commit against PR #121 merge;
- deployed `web/progressive-personalization-ui.js` against PR #121 merge;
- deployed `web/data/current.json` against canonical `data/production/visual/current.json`;
- visual source commit/freshness receipt;
- latest Build daily visual payload runs;
- latest Deploy visual mailing runs;
- whether Pages still serves stale visual `2202a668...`;
- whether the live artifact contains the expired-sale filtering code;
- whether cache/LKG is secondary or irrelevant.

The worker must identify the **first exact publication divergence** for both code and payload, and say whether one fix can solve both symptoms or there are two independent publication paths.

Do not immediately implement another browser expiry fix or another ranking/statistics fix; those are already merged.

## Known publication blockers / dependencies

1. Russian semantic translation work is now normally queued after pre-AI was unblocked.
2. Meaningful-Russian gate can still prevent a new canonical visual until required translations are accepted.
3. The stale-snapshot rebase race remains an accepted unfixed control-plane defect.
4. Even a source-code merge does not prove Pages deployed the new browser files.
5. Green deploy/workflow status is not freshness proof. Inspect actual selected visual/source commit and artifact.

## Other pending accepted diagnosis

Atelier Escha & Logy positive explanation:
- task: `WORKER_TASK_ATELIER_ESCHA_LOGY_DEEP_WITHOUT_POSITIVE_REASON_DIAGNOSTIC_01.md`;
- report: `reviews/worker_reports/atelier-escha-logy-deep-without-positive-reason-diagnostic-01.md`;
- issue: authoritative Deep has positive evidence, but shared positive explanation mapper does not map those sentence shapes, so `why_fit=[]`;
- implementation still pending;
- lower priority than current live-publication problem.

## Dossier / Deep notes

Do not reuse stale counts from old Board lower sections as current truth.
Production continues to advance independently.
When current counts are needed, read fresh canonical files/runs.

Do not equate Dossier accepted count directly with Deep ready count; scopes/identity differ.

## User preferences for this project

- Simple Russian explanations.
- Avoid unexplained English terms.
- User expects Director to delegate worker-level technical diagnosis rather than doing it itself.
- Fullness/correctness matters more than speed.
- User dislikes repetitive unnecessary checks after every item.
- User controls Scheduled Task UI.
- Do not ask for secrets in chat.

## Handoff rule

This physical Director chat is retired after this bootstrap update.
New project work must continue in a **NEW physical Director conversation**.
The old conversation remains only historical UI transcript, not current project truth.
