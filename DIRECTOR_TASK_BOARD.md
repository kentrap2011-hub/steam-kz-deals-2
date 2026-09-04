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

User verification on the real mobile site succeeded on 2026-09-04: giveaways are visible/working in the normal existing browser session.

Therefore the user-visible incident is closed.

**ЧАТ 2 можно удалить.**

## Top summary buttons

Recon:
`reviews/worker_reports/top-summary-filter-buttons-recon-01.md`
Status: `complete`.

Queued implementation:
`WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.

Now that the giveaway frontend incident is closed, this implementation may be scheduled in a fresh ЧАТ 1 when the Director chooses the next UI task.

## NEW queued future request — Epic RU giveaway availability

Prepared recon:
`WORKER_TASK_EPIC_RU_GIVEAWAY_AVAILABILITY_RECON_01.md`

Task ID: `epic-ru-giveaway-availability-recon-01`.
Status: `queued_user_requested_not_started`.

User requirement:
- Epic Games only: include free giveaways only when currently available/redeemable for Russian region `RU`;
- this means available in RU, not necessarily exclusive to RU;
- Steam giveaway behavior stays unchanged;
- GOG giveaway behavior stays unchanged.

Recon first because current Epic collector historically uses KZ-oriented region inputs and the exact authoritative RU-availability signal must be proven before implementation.

Do not start this task merely because it is prepared; it is a future queued request.

## Review checkpoint

Epic post-incident audit complete and accepted.
`system_audit_due: false`.

A future accepted change to Epic provider region semantics may itself require a fresh System Audit checkpoint under the existing recurring-trigger rules; recon must classify this before implementation acceptance.

## Semantic runtime unresolved evidence

`reviews/worker_reports/semantic-runtime-task-health-recon-01.md` remains `needs_user_evidence` because worker cannot inspect authoritative external scheduler/task record for 701 unresolved semantic rows.

## Следующий порядок

1. Current giveaway incident remains closed unless new user evidence appears.
2. Completed ЧАТ 2 may be deleted.
3. `top-summary-filter-buttons-01` is ready as the next previously queued UI implementation.
4. `epic-ru-giveaway-availability-recon-01` is added to future queue and must not change Steam/GOG behavior.
5. Preserve two-worker parallelism only when next chosen tasks are safely independent.
