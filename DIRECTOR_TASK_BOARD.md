# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины, но эта board новее и выигрывает при расхождении статусов.

## Ключевые правила

1. По умолчанию держать два worker-чата занятыми параллельно, если задачи независимы и не конфликтуют.
2. Неясная проблема сначала `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
3. UI-инциденты закрывать только после real-device/site проверки пользователя.
4. Worker-чат удалять только после сохранённого report, решения директора и ближайших проверок.
5. В каждой копируемой worker-команде первая строка должна явно начинаться с `=== ЧАТ N ===`.
6. Номер принадлежит worker-слоту.
7. Не запускать параллельно конфликтующие IMPLEMENT-задачи.
8. Возраст задачи не понижает её приоритет автоматически.

## Review checkpoint

Latest System Audit:
`reviews/system_audits/giveaway-cache-post-incident-audit-01.md`

Status: `complete`
Result: `Giveaway cache incident systemic closure: accepted`

`system_audit_due: false`.

## Активная пара

### ЧАТ 1 — Wishlist + хорошая скидка против слабого Taste

Task:
`WORKER_TASK_WISHLIST_GOOD_DEAL_OVERRIDE_RECON_01.md`

Task ID:
`wishlist-good-deal-override-recon-01`

Mode: `READ-ONLY / RECON`
Expected report:
`reviews/worker_reports/wishlist-good-deal-override-recon-01.md`

Goal:
- найти точный ordinary Taste eligibility gate, который сейчас может выбросить wishlist-игру до ranking;
- определить существующий канонический сигнал `genuinely good deal`;
- спроектировать минимальный wishlist override только ordinary Taste gate;
- не скрывать confirmed risks / плохую ценность покупки;
- не менять код в recon;
- финальный IMPLEMENT acceptance потребует независимый Taste Review, потому что меняется wishlist-vs-Taste eligibility semantics.

Status: `user_approved_start_now`.

### ЧАТ 2 — Epic RU giveaway availability

Task:
`WORKER_TASK_EPIC_RU_GIVEAWAY_AVAILABILITY_RECON_01.md`

Task ID:
`epic-ru-giveaway-availability-recon-01`

Mode: `READ-ONLY / RECON`
Expected report:
`reviews/worker_reports/epic-ru-giveaway-availability-recon-01.md`

Goal:
- доказать authoritative способ определить, доступна ли Epic giveaway для RU;
- Epic only;
- Steam unchanged;
- GOG unchanged;
- не менять production code/data в recon.

Status: `user_approved_start_now`.

These two tasks are safely parallel: Chat 1 is paid-feed ranking/Taste policy recon; Chat 2 is Epic giveaway source/region recon.

## Ready / queued after current pair

### Top summary buttons

Recon complete:
`reviews/worker_reports/top-summary-filter-buttons-recon-01.md`.
IMPLEMENT ready:
`WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.

### Mobile bootstrap deploy regression gate

Task:
`WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
Existing mobile bootstrap regression is passing but not mandatory in canonical Pages deploy gate.

### ITAD provider-neutral giveaway identity

Task:
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
Larger integration; exact Epic/GOG provider ID -> Steam identity through provider-neutral interface.

## Older unfinished / blocked work

- Grounded negative V4 architecture implemented, but semantic completion waits on existing scheduled Taste runtime; do not create second scheduler/manual processing.
- Card positive-explanation fix implemented; production acceptance waits on Russian-description/semantic runtime prerequisite.
- Russian-description translation contracts/ingest exist; runtime production completion waits on existing scheduled semantic runtime.
- Russian language availability as ranking factor remains planned.
- YouTube Russian-language game review selection remains deferred/planned.
- Modern Windows compatibility evidence source remains deferred.
- SteamDB tail: only `App_901735` unresolved/retryable; low priority/external.
- Detailed score UI implementation/fixes are deployed; no new implementation without fresh user evidence.
- Twitch/IGDB route remains externally blocked/waiting.

## Next decision

Read the two exact reports when workers finish. Do not auto-implement either recon result until Director checks conflicts/review requirements.
