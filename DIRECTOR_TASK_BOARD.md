# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины. Эта board хранит только директорские метаданные.

## Ключевые правила

1. По умолчанию держать два worker-чата занятыми параллельно, если задачи независимы и не конфликтуют.
2. Неясная проблема сначала `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
3. UI-инциденты закрывать только после real-device/site проверки пользователя.
4. Worker-чат удалять только после сохранённого report, решения директора и ближайших проверок.
5. В каждой копируемой worker-команде первая строка должна явно начинаться с `=== ЧАТ N ===`.
6. Номер принадлежит worker-слоту: замена удалённого ЧАТА 1 остаётся ЧАТОМ 1; замена удалённого ЧАТА 2 остаётся ЧАТОМ 2.
7. Не запускать параллельно два frontend IMPLEMENT, если они делят production/deploy контур.

## Текущее состояние

### ЧАТ 1 — top summary recon complete

Report:
`reviews/worker_reports/top-summary-filter-buttons-recon-01.md`
Status: `complete`.

Доказано:
- верхние `Новые / Не смотрел / Интересно / Видел` сейчас не controls;
- единый существующий UI state — `currentTab` + existing local state;
- готовый view/action существует только для `Интересно`;
- `Новые / Не смотрел / Видел` должны быть добавлены как режимы того же `currentTab`, без второго filter state;
- нижний дубликат для удаления — `.tab[data-tab="liked"]`, но `#likeBtn` и `likedView` должны остаться;
- implementation затрагивает `web/app.js`, `web/index.html`, `web/styles.css`, новый focused test и возможно deploy UI gate;
- recon рекомендует начинать implementation только после giveaway fix acceptance из-за общего frontend/deploy окна.

**Текущий ЧАТ 1 можно удалить.**

Implementation `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md` остаётся queued и не запускается параллельно с текущим giveaway frontend fix.

### ЧАТ 2 — recovery acceptance failed

Report:
`reviews/worker_reports/giveaway-cache-identity-recovery-acceptance-01.md`
Status: `needs_followup_fix`.
Classification: `deployed_but_fix_insufficient`.

Принятый ранее commit `6282619c65c134459a4e85c80b9355fe3174e8ae` действительно был успешно задеплоен, но fix неверен для production schema:
- использует отсутствующие flat `giveaway_generated_at_utc` / `giveaway_status`;
- ожидает `giveaways` array, тогда как production uses object;
- реальный provenance: `production_contract.source_giveaway_snapshot_blob_sha`;
- production-shaped acceptance probe воспроизводит `refresh-identical` и отсутствие app update.

Prepared exact bounded follow-up IMPLEMENT:
`WORKER_TASK_GIVEAWAY_CACHE_IDENTITY_PRODUCTION_SHAPE_FIX_01.md`
Report:
`reviews/worker_reports/giveaway-cache-identity-production-shape-fix-01.md`.

Use **existing ЧАТ 2** as direct continuation if context remains available.
Do not ask user to retest until this correction is deployed successfully.

## Review checkpoint

Epic post-incident audit complete and accepted.
`system_audit_due: false`.
No ordinary-backlog audit block remains.

## Semantic runtime unresolved evidence

`reviews/worker_reports/semantic-runtime-task-health-recon-01.md` remains `needs_user_evidence` because worker cannot inspect authoritative external scheduler/task record for 701 unresolved semantic rows.

## Следующий порядок

1. Existing ЧАТ 2 implements `giveaway-cache-identity-production-shape-fix-01` and owns tests + deploy wait.
2. ЧАТ 1 is not assigned a conflicting frontend IMPLEMENT while ЧАТ 2 is in this production window; its completed recon chat may be deleted.
3. After ЧАТ 2 technical `complete`, user re-checks giveaways on real mobile site.
4. Only after giveaway verification succeeds, start top-summary-buttons IMPLEMENT in a fresh ЧАТ 1.
