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

Implementation `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md` remains queued until giveaway user verification closes the current frontend incident.

**Текущий завершённый ЧАТ 1 можно удалить.**

### ЧАТ 2 — production-shaped giveaway cache fix technically complete

Report:
`reviews/worker_reports/giveaway-cache-identity-production-shape-fix-01.md`
Status: `complete`.

Final implementation commit:
`024f81937942987c96bb5db1b0e1d7b66dd67587`

Canonical Pages deployment:
- workflow run `33841356092` — success;
- deploy job `100924142727` — success;
- Pages artifact `9925017623`;
- deployed build/version `024f81937942987c96bb5db1b0e1d7b66dd67587`.

Technical proof:
- `payloadIdentity()` now uses actual production provenance `production_contract.source_giveaway_snapshot_blob_sha`;
- production-shaped stale-cache -> fresh giveaway-only regression => `updated`;
- truly identical payload => `identical`;
- canonical UI regressions passed;
- exact deployed artifact contains corrected `feed-bootstrap.js` and active giveaway payload.

User-visible incident is **not closed yet**. Next required evidence is one normal real-mobile-session check by the user, with no cache/site-data clearing.

**ЧАТ 2 пока не удалять до результата этой проверки.**

If user verification succeeds:
- close giveaway live-site incident;
- ЧАТ 2 can be deleted;
- start queued top-summary-buttons IMPLEMENT in a fresh ЧАТ 1.

If user verification fails:
- keep/use existing ЧАТ 2 for one bounded follow-up based on the new real-device evidence.

## Review checkpoint

Epic post-incident audit complete and accepted.
`system_audit_due: false`.

## Semantic runtime unresolved evidence

`reviews/worker_reports/semantic-runtime-task-health-recon-01.md` remains `needs_user_evidence` because worker cannot inspect authoritative external scheduler/task record for 701 unresolved semantic rows.

## Следующий порядок

1. User checks giveaways on the real mobile site in the normal existing browser session; do not clear cache/site data.
2. Success -> close incident and delete ЧАТ 2.
3. Failure -> exact bounded follow-up in existing ЧАТ 2.
4. After giveaway incident closes, launch `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md` in a fresh ЧАТ 1.
