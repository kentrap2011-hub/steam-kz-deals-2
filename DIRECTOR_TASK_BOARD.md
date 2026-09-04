# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины. Эта board хранит только директорские метаданные.

## Ключевые правила

1. По умолчанию держать два worker-чата занятыми параллельно, если задачи независимы и не конфликтуют.
2. Неясная проблема сначала `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`; отдельная задача не обязательно требует нового чата.
3. Production queue/retry/completeness принадлежат GitHub/GitHub Actions по `config/execution_ownership_contract.json`.
4. UI-инциденты закрывать только после real-device/site проверки пользователя.
5. Worker-чат удалять только после сохранённого report, решения директора и ближайших проверок.
6. `prepared` не значит `next`.
7. Перед обычным backlog читать `DIRECTOR_REVIEW_CHECKPOINTS.md`.
8. `TASTE REVIEWER` и `SYSTEM AUDITOR` — отдельные независимые роли.
9. В каждой копируемой worker-команде первая строка должна явно начинаться с `=== ЧАТ N ===`.
10. Номер принадлежит worker-слоту: замена удалённого ЧАТА 1 остаётся ЧАТОМ 1; замена удалённого ЧАТА 2 остаётся ЧАТОМ 2.

## Активно сейчас

| Чат | Задача | Task file | Report | Статус |
|---|---|---|---|---|
| `НОВЫЙ ЧАТ 1` | Recon queued UX: верхние summary-карточки как фильтры | `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_RECON_01.md` | `reviews/worker_reports/top-summary-filter-buttons-recon-01.md` | `prepared_start_new_chat` |
| `НОВЫЙ ЧАТ 2` | Recovery/acceptance уже landed giveaway cache fix | `WORKER_TASK_GIVEAWAY_CACHE_IDENTITY_RECOVERY_ACCEPTANCE_01.md` | `reviews/worker_reports/giveaway-cache-identity-recovery-acceptance-01.md` | `prepared_start_new_chat_after_limit` |

## ЧАТ 1 — Epic post-incident audit завершён

Report:
`reviews/system_audits/epic-post-incident-audit-01.md`
Status: `complete`.
Decision: `Epic incident systemic closure: accepted`.

`DIRECTOR_REVIEW_CHECKPOINTS.md` обновлён:
- `system_audit_due: false`;
- `material_changes_since_last_system_audit: 0`;
- `last_system_audit_report: reviews/system_audits/epic-post-incident-audit-01.md`.

Старый ЧАТ 1 закончен и может быть удалён.

## ЧАТ 2 — worker достиг лимита после landing fix

Ожидаемый report `reviews/worker_reports/giveaway-cache-identity-fix-01.md` не был сохранён на `main` до достижения лимита.

Но implementation частично/полностью landed:
- commit `6282619c65c134459a4e85c80b9355fe3174e8ae`;
- message `Fix giveaway cache payload identity`;
- current `web/feed-bootstrap.js` уже содержит изменённый `payloadIdentity()`.

Нельзя считать user-visible incident закрытым без восстановления доказательств tests/deploy и новой проверки пользователя.

Старый ЧАТ 2 достиг лимита и может быть удалён.

Следующий **НОВЫЙ ЧАТ 2** выполняет только recovery/acceptance:
`WORKER_TASK_GIVEAWAY_CACHE_IDENTITY_RECOVERY_ACCEPTANCE_01.md`.
Он не должен переделывать fix с нуля.

Если technical acceptance = complete, Director просит пользователя проверить раздачи на реальном мобильном сайте. Если acceptance = needs_followup_fix, выдаётся один bounded IMPLEMENT в ЧАТ 2.

## Queued user UI request

Основная implementation-задача:
`WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.

Пока giveaway fix проходит recovery acceptance, новый ЧАТ 1 делает только безопасный READ-ONLY recon:
`WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_RECON_01.md`.

Цель recon:
- точно сопоставить `Новые / Не смотрел / Интересно / Видел` с существующим filter state;
- определить нижний дубликат `Интересно`;
- подготовить bounded implementation/test plan;
- не менять frontend до завершения giveaway acceptance window.

## Semantic runtime unresolved evidence

`reviews/worker_reports/semantic-runtime-task-health-recon-01.md` остаётся `needs_user_evidence`.
Worker не может authoritative определить состояние внешней scheduled semantic task для 701 unresolved rows. Не создавать параллельный scheduler и не ослаблять completeness.

## Следующий порядок

1. Удалить старые завершённые worker-чаты 1 и 2; ЧАТ 2 всё равно достиг лимита.
2. Создать НОВЫЙ ЧАТ 1 -> `top-summary-filter-buttons-recon-01`.
3. Создать НОВЫЙ ЧАТ 2 -> `giveaway-cache-identity-recovery-acceptance-01`.
4. Когда ЧАТ 2 завершит acceptance:
   - `complete` -> пользователь повторно проверяет реальные раздачи на телефоне;
   - `needs_followup_fix` -> один bounded IMPLEMENT в том же новом ЧАТЕ 2.
5. ЧАТ 1 после recon не начинает implementation, пока Director не проверит conflict/acceptance state ЧАТА 2.
