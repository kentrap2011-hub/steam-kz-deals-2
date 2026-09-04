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
| `НОВЫЙ ЧАТ 1` | Обязательный Epic post-incident System Audit | `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md` | `reviews/system_audits/epic-post-incident-audit-01.md` | `prepared_start_after_old_chat1_delete` |
| `СУЩЕСТВУЮЩИЙ ЧАТ 2` | Исправить collision stale LKG vs giveaway-only refresh | `WORKER_TASK_GIVEAWAY_CACHE_IDENTITY_FIX_01.md` | `reviews/worker_reports/giveaway-cache-identity-fix-01.md` | `prepared_direct_continuation` |

## ЧАТ 1 — завершённый semantic recon

Report:
`reviews/worker_reports/semantic-runtime-task-health-recon-01.md`
Status: `needs_user_evidence`.

Worker не получил authoritative scheduler/task record и поэтому честно классифицировал producer как `cannot_determine`.
Durable report сохранён, полезного продолжения в этом worker-чате сейчас нет.

**Старый ЧАТ 1 можно удалить.**

Следующий новый ЧАТ 1 получает обязательный независимый System Audit `epic-post-incident-audit-01`.

## ЧАТ 2 — giveaway live-site incident

Recon report:
`reviews/worker_reports/giveaway-live-site-mismatch-recon-01.md`
Status: `needs_followup_fix`.

Доказано:
- exact deployed Pages artifact содержит `Alone With You`;
- fresh payload корректно рендерится, если доходит до application;
- browser-side LKG cache может выдать старый payload;
- `web/feed-bootstrap.js::payloadIdentity()` использует только top-level `generated_at_utc`;
- giveaway-only update может сохранить тот же `generated_at_utc`, но изменить `source_giveaway_snapshot_blob_sha`;
- stale cached payload и fresh payload тогда ошибочно считаются `refresh-identical`, и fresh payload не применяется.

Prepared bounded IMPLEMENT:
`WORKER_TASK_GIVEAWAY_CACHE_IDENTITY_FIX_01.md`
Task ID `giveaway-cache-identity-fix-01`.

Использовать **существующий ЧАТ 2** как прямое продолжение. Его пока не удалять.
После deploy обязательна новая real-device/site проверка пользователя.

Если пользователь сознательно хочет очистить ЧАТ 2, допустима замена на **НОВЫЙ ЧАТ 2** с тем же task file; никогда не переносить слот 2 в номер 1.

## Review checkpoint

`system_audit_due: true`.
Prepared: `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md`.
Этот READ-ONLY / AUDIT независим от bounded frontend cache fix и может идти параллельно в новом ЧАТЕ 1.
Обычный backlog/ITAD остаётся заблокирован до завершения audit.

## Queued user UI request

`WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`
Task ID `top-summary-filter-buttons-01`.

После текущего cache fix + audit:
- верхние `Новые / Не смотрел / Интересно / Видел` сделать кликабельными;
- удалить нижний дубликат `Интересно` после полной замены его функции;
- real-device verification required.

## Следующий порядок

1. Удалить старый завершённый ЧАТ 1.
2. Создать НОВЫЙ ЧАТ 1 и запустить `epic-post-incident-audit-01`.
3. Существующий ЧАТ 2 запускает `giveaway-cache-identity-fix-01` как прямое продолжение своего recon.
4. Когда ЧАТ 2 закончит technical deploy, пользователь повторно проверяет реальные раздачи на телефоне.
5. После audit + успешной проверки раздач перейти к queued UI/mobile tasks по checkpoint.
