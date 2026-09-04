# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины, но эта board новее и выигрывает при расхождении статусов.

## Ключевые правила

1. По умолчанию держать два worker-чата занятыми параллельно, если задачи независимы и не конфликтуют.
2. Неясная проблема сначала `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
3. UI-инциденты закрывать только после real-device/site проверки пользователя.
4. Worker-чат удалять только после сохранённого report, решения директора и ближайших проверок.
5. В каждой копируемой worker-команде первая строка должна явно начинаться с `=== ЧАТ N ===`.
6. Номер принадлежит worker-слоту: замена удалённого ЧАТА 1 остаётся ЧАТОМ 1; замена удалённого ЧАТА 2 остаётся ЧАТОМ 2.
7. Не запускать параллельно конфликтующие IMPLEMENT-задачи в одном production/deploy контуре.

## Giveaway live-site incident — CLOSED

Technical report:
`reviews/worker_reports/giveaway-cache-identity-production-shape-fix-01.md`
Status: `complete`.

Final implementation commit:
`024f81937942987c96bb5db1b0e1d7b66dd67587`

Deploy:
- workflow run `33841356092` — success;
- deploy job `100924142727` — success;
- Pages artifact `9925017623`;
- deployed build/version `024f81937942987c96bb5db1b0e1d7b66dd67587`.

User verification on the real mobile site succeeded on 2026-09-04 without clearing site data.

The incident is user-visible and stabilized after the previous System Audit, so the recurring audit trigger fired again.

Prepared mandatory short audit:
`WORKER_TASK_GIVEAWAY_CACHE_POST_INCIDENT_AUDIT_01.md`
Expected report:
`reviews/system_audits/giveaway-cache-post-incident-audit-01.md`.

## Recommended next parallel pair

### ЧАТ 1 — highest priority

`giveaway-cache-post-incident-audit-01`
Mode: `READ-ONLY / AUDIT`.

Why now:
- mandatory recurring checkpoint after stabilized user-visible incident;
- short and pinned to exact incident refs;
- should close before ordinary backlog grows further.

### ЧАТ 2 — fastest safe implementation

`mobile-feed-regression-gate-01`
Task: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
Mode: `IMPLEMENT`.

Why now:
- only proven remaining gap is that existing passing `tests/feed-bootstrap.test.js` is not in the canonical Pages deploy gate;
- expected product-code change is zero;
- only wire the already-existing test into the existing deploy regression step and prove one passing Pages run;
- safe in parallel with the read-only audit because the audit is pinned to the earlier stabilized incident refs and must ignore unrelated later deploy-gate-only wiring.

## Ready / queued after this pair

### Top summary buttons

Recon complete:
`reviews/worker_reports/top-summary-filter-buttons-recon-01.md`.
Implementation ready:
`WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.

User-visible UI implementation:
- top `Новые / Не смотрел / Интересно / Видел` become clickable;
- reuse one existing view/filter state;
- remove lower duplicate `Интересно` only after replacement works;
- production deploy + mobile user verification required.

### Epic RU giveaway availability

Prepared future recon:
`WORKER_TASK_EPIC_RU_GIVEAWAY_AVAILABILITY_RECON_01.md`.

Requirement:
- Epic Games only: accept giveaways only when available/redeemable for RU;
- Steam unchanged;
- GOG unchanged.

Recon first because authoritative Epic RU availability semantics must be proven before implementation.

### Giveaway ITAD provider-neutral identity

Prepared larger implementation:
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.

Purpose:
- exact Epic/GOG provider ID -> ITAD -> exact Steam appid;
- one switchable provider-neutral identity interface;
- no fuzzy/title fallback;
- IGDB reserved for later provider switch.

Larger/riskier than current recommended quick pair.

## Blocked / waiting / low priority

### Semantic / Russian-description runtime

Current semantic production remains blocked on authoritative external scheduled-task evidence / execution. Do not create a parallel scheduler and do not weaken completeness.

### Twitch/IGDB

Waiting for Twitch Support / provider readiness; do not start dependent work as if credentials/provider route were available.

### SteamDB tail

`App_901735` remains low-priority blocked/retryable; exact KZ historical minimum is unproven and must not be fabricated.

## Older roadmap requiring status refresh before being promoted

`CURRENT_TASK.md` is older (2026-09-01) and still lists:
- ranking/card explanation quality work;
- Russian language availability as ranking factor;
- YouTube reviews for games;
- Russian game-description guarantee/runtime acceptance.

The card explanation implementation is not fully accepted: its durable report shows behavioral tests pass but a real generated top-30 sample still had one exact positive-explanation violation (`Middle-earth: Shadow of Mordor`). Before promoting those older roadmap items above the newer board, Director should perform a bounded status refresh rather than assume the old `in_progress/planned` labels are current.

## Review checkpoint

`system_audit_due: true` after successful real-device closure of the giveaway cache incident.
Prepared audit: `WORKER_TASK_GIVEAWAY_CACHE_POST_INCIDENT_AUDIT_01.md`.

## Suggested order

1. Run mandatory giveaway-cache System Audit in ЧАТ 1.
2. In parallel run mobile-feed regression gate wiring in ЧАТ 2.
3. After both reports, close audit checkpoint and confirm deploy gate.
4. Then likely start top-summary-buttons implementation as the next user-visible feature.
5. Epic RU recon remains a good independent backend/recon companion for a later slot.
