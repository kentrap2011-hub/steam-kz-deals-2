# DIRECTOR HANDOFF — CURRENT

Repository: `kentrap2011-hub/steam-kz-deals-2`
Branch: `main`
Purpose: compact handoff for a replacement Director chat without replaying prior conversation history.

## Start here

A replacement Director must read, in this order:
1. `DIRECTOR_PROTOCOL.md`
2. `DIRECTOR_HANDOFF_CURRENT.md` (this file)
3. `DIRECTOR_TASK_BOARD.md`
4. `DIRECTOR_REVIEW_CHECKPOINTS.md`

Do not broadly inspect Git history, workflow history, old task files, artifacts or source code just to rebuild context. Use exact saved worker reports and current management metadata first. The Director delegates investigation/implementation to worker chats rather than doing project work itself.

## User communication style

- Russian.
- Direct, practical, understandable language; explain technical conclusions in ordinary words.
- When giving a worker command, explicitly say `НОВЫЙ ЧАТ` or `СУЩЕСТВУЮЩИЙ ЧАТ`.
- Prefer copyable code blocks for commands.
- Do not claim a UI incident fixed before user verifies the actual site/device.

## Current urgent track — mobile feed latency

### Original incident

On the user's Android phone the discounts page shell and controls worked, but after fresh load/reload the game feed could be blank. Switching away to another app and returning could make the games appear.

Recon:
- task: `WORKER_TASK_MOBILE_PAGE_INTERACTION_FREEZE_RECON_01.md`
- report: `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`
- report blob: `48700dc77ac17fa031dd129996bef74075d86872`

Recon conclusion:
- canonical payload was non-empty;
- highest-confidence application boundary was the single unbounded initial `fetch('data/current.json', { cache: 'no-store' })` before first feed render;
- both feed result surfaces could remain hidden while that request was pending;
- exact Android/WebView transport-level cause was not runtime-proven.

### First fix — deployed, partial success

Task:
`WORKER_TASK_MOBILE_PAGE_BLANK_FEED_FIX_01.md`

Report:
`reviews/worker_reports/mobile-page-blank-feed-fix-01.md`

Report blob:
`61b23ffc479dff473310b1d7aed0d36d43a11c8f`

Production ref:
`af2c7362743b4fe3d80ea10caee7cb606acab3e5`

Successful Pages run:
`33766838776`

Implemented:
- immediate visible `Загружаю игры…` instead of silent blank;
- 9-second timeout;
- max 2 attempts total;
- guarded hidden->visible/BFCache recovery;
- explicit terminal error;
- focused regression tests pass.

Latest real-device user result:
- better, but not solved;
- sometimes refresh is effectively instant;
- sometimes `Загружаю игры…` remains for several seconds;
- games eventually appear;
- user asks whether the remaining delay can be eliminated.

This means the first fix solved silent blankness but repeat page load still blocks on network latency.

### Prepared direct continuation — NOT STARTED

Prepared task:
`WORKER_TASK_MOBILE_FEED_INSTANT_CACHE_FIX_01.md`

Creation commit:
`5756dfee952893a4336f321edd6c3d368da46f45`

Expected report:
`reviews/worker_reports/mobile-feed-instant-cache-fix-01.md`

Status:
`prepared_not_started`

Important: user has NOT yet been given/sent this worker command. Do not mark it started until user actually sends it to the worker chat.

Goal in plain language:
- after one successful load, keep one last-known-good feed payload locally on the phone;
- future open/reload should show that list immediately;
- fresh `data/current.json` loads in background and replaces the old list only when a valid new payload arrives;
- slow/failed network must not block or blank already available cards;
- canonical network payload remains source of truth; local copy is only presentation fallback.

Boundaries:
- no service worker;
- no polling/background scheduler;
- no second renderer;
- no Taste/ranking/filter changes;
- no unbounded historical cache;
- no merge of the separate visual-freshness branch inside this task.

If continuing this track, use **СУЩЕСТВУЮЩИЙ ЧАТ 1** and give only:

```text
=== ЧАТ 1 — УСКОРИТЬ ЗАГРУЗКУ ЛЕНТЫ ===

Открой `WORKER_TASK_MOBILE_FEED_INSTANT_CACHE_FIX_01.md`
в репозитории `kentrap2011-hub/steam-kz-deals-2`
и выполни поручение полностью.

Это прямое продолжение текущего мобильного инцидента.
Не повторяй диагностику и не переделывай интерфейс.
```

After worker completion: read exact report path first. If deployed successfully, require real-device verification again. The desired acceptance is that after one successful visit, repeated reloads normally show cards immediately from last-known-good data while refresh occurs in background.

## Visual freshness track — accepted, release deferred

Implementation report:
`reviews/worker_reports/visual-freshness-chain-fix-01.md`
blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`

Final acceptance:
`reviews/worker_reports/visual-freshness-chain-acceptance-02.md`
blob `6a691fb29d88b1785accf717752149e027265a2c`

Accepted branch:
`worker/visual-freshness-chain-fix-01`

Acceptance head:
`4080030e686d6b04fcc666069819aa46df18da7a`

All controls pass:
- Fresh-cycle build proof: pass
- Deploy-to-built-cycle binding: pass
- Stale-success visibility: pass
- Ownership/regression preserved: pass

Branch is ready for production merge/release, but release is intentionally deferred until the mobile incident is stabilized and overlap risk is reassessed.

Chat 2 is finished and can be deleted.

## Mandatory System Auditor — due

`DIRECTOR_REVIEW_CHECKPOINTS.md` currently has:
`system_audit_due: true`

The urgent mobile incident may pre-empt the audit until stabilized. After the incident is stable, run the due System Audit before ordinary backlog/ITAD work.

Do not forget this checkpoint.

## Taste Reviewer — baseline complete

Dedicated Taste Reviewer is established.

Report:
`reviews/taste_reviews/baseline-01.md`
blob `f243047d9bbb3d8515e7929e2962da66688243c4`

Overall conclusion is NOT simply `too strict` or `too loose`; current assessment is `cannot_determine`, with concrete evidence that role/context/risk semantics need better calibration.

Do not automatically change Taste/ranking weights from this advisory report. Material Taste/ranking-policy changes require the Taste Review checkpoint before acceptance.

## Giveaway identity — ITAD prepared with switchable provider

ITAD permission from provider is confirmed.

Prepared task:
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`

Expected report:
`reviews/worker_reports/giveaway-itad-identity-implement-01.md`

Architecture decision:
- one provider-neutral identity interface;
- active provider now: `itad`;
- future provider name reserved: `igdb`;
- no automatic fallback/dual lookup/provider voting;
- downstream Steam family/description/Taste path consumes one common resolved Steam identity and should not care whether it came from ITAD or IGDB.

Status:
`prepared_not_started`

Do not start before the urgent mobile incident is stabilized and due System Audit is handled, unless user explicitly reprioritizes.

Twitch/IGDB remains blocked/waiting for Twitch Support. If Twitch unblocks before ITAD starts, explicitly reconsider provider priority rather than blindly starting ITAD.

## Semantic runtime completion — closed

Final acceptance report:
`reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`
blob `5b4a25c89845ab258651a30608658e90d7d1840d`

System-level semantic observability/completeness fix is accepted and closed. Do not reopen Trine-specific investigation without a new defect.

## Parked blockers

- `grounded-negative-implement-01`: blocked on existing GitHub-owned Taste data-plane unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

Do not automatically reopen these after handoff.

## Priority order at handoff

Unless user explicitly changes priority:
1. Finish current mobile feed incident via prepared instant-cache follow-up and real-device verification.
2. Reassess/release accepted visual-freshness branch at the safest bounded point.
3. Run mandatory System Audit.
4. Then consider prepared switchable-provider ITAD implementation.
5. Ordinary backlog only after review checkpoints permit it.

## Context-protection rule

The previous Director was explicitly told not to consume context by broadly checking project history itself. Preserve that rule:
- exact report path first;
- minimum current evidence only;
- delegate code/log/history investigation to worker chats;
- do not rebuild project history in the Director chat.

## Worker deletion state

- Chat 2 visual freshness: finished; can be deleted.
- Chat 1 mobile incident: keep until the mobile incident is fully user-verified or explicitly handed to another worker.
- Taste Reviewer: dedicated advisory chat may be kept; it does not consume an implementation worker slot.

## Source of truth

If this file conflicts with a newer `DIRECTOR_TASK_BOARD.md` or exact newer worker report, prefer the newer durable evidence and update this handoff accordingly. Do not rely on chat memory over repository state.