# WORKER TASK

Task ID: `giveaway-publication-gap-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/giveaway-publication-gap-recon-01.md`

## Goal

Найти точную границу, из-за которой актуальная canonical бесплатная раздача уже есть в production data, но пользователь не видит бесплатные раздачи на опубликованном сайте.

Это только bounded recon. Не исправляй код и не запускай широкую переработку.

## Current verified facts

Пользователь на реальном сайте сейчас не видит бесплатные раздачи.

При этом актуальный `main` содержит:
- `data/production/giveaways/v1/current.json`;
- `snapshot_status = complete`;
- Epic `status = ok`, `complete = true`;
- `accepted_count = 1`;
- активную KZ-раздачу `Alone With You`, 100%, до `2026-09-10T15:00:00Z`.

Предыдущая Epic parser-задача закрыта как `complete`:
`reviews/worker_reports/epic-giveaway-schema-fix-01.md`.

Не переоткрывай parser defect без нового доказательства.

## Read first

1. Актуальный `main`.
2. `CHAT_PROTOCOL.md` и `CHAT_CONTEXT.md`.
3. `reviews/worker_reports/epic-giveaway-schema-fix-01.md`.
4. `data/production/giveaways/v1/current.json`.
5. Только минимально необходимые текущие файлы, которые реально связывают canonical giveaway data с опубликованным сайтом/рендерером.

Не восстанавливай историю проекта и не читай массово старые giveaway task/report файлы.

## What to establish

Проследи только текущую цепочку:

`canonical giveaway snapshot -> publication/deploy artifact -> browser-loaded data -> giveaway view/filter/render`

Установи первый точный слой, где `Alone With You` перестаёт быть доступной пользователю.

Проверь минимум:

1. Какой giveaway-файл или производный payload реально публикуется на Pages.
2. Содержит ли текущий опубликованный artifact/site payload `Alone With You`.
3. Если данные опубликованы — загружает ли frontend правильный путь/версию и не остаётся ли на старом payload/cache.
4. Если frontend получает запись — не отбрасывает ли её текущая view/filter/render логика.
5. Является ли проблема публикационной гонкой/непопавшим generated commit после run `33790442843`, stale deploy, неправильным data path или UI/filter defect.
6. Требуется ли пользовательский hard refresh только как временная проверка, а не как постоянное решение.

## Critical boundaries

Не делать в этой задаче:
- никаких исправлений production/frontend/workflow;
- никаких изменений Epic parser;
- никаких ITAD/IGDB изменений;
- никаких Taste/ranking/paid-deal изменений;
- никакого нового scheduler/queue/writer;
- никакого массового исследования Git history или старых Actions runs;
- не менять `CURRENT_TASK.md`.

Разрешено сохранить только этот report-файл.

## Validation standard

Вывод должен опираться на точные refs текущего `main`, опубликованного Pages/deploy artifact или минимально необходимого текущего workflow evidence.

Не писать `скорее всего`, если можно доказать точную границу. Если реальный deployed payload нельзя прочитать из worker-контекста, зафиксируй это как конкретный blocker и всё равно локализуй максимально узкий слой по доступным canonical данным.

## Done when

В report есть:

1. `Task` — что проверялось.
2. `Verified facts` — точная цепочка данных и где запись ещё присутствует/уже отсутствует.
3. `Changes` — `none`, кроме report.
4. `Validation` — exact refs/artifacts/site evidence.
5. `Unresolved` — только реально недоказанное.
6. `Status` — ровно одно: `complete`, `blocked`, `needs_fix`, `needs_user_decision`.
7. `Recommended next step` — один ограниченный следующий шаг.
8. `Efficiency / reusable lesson` — `none` либо одна короткая переносимая pitfall-ссылка.

## Expected next step

Если точный defect найден — рекомендовать один bounded `IMPLEMENT`, не выполнять его самому.

Если defect не найден и нужна только конкретная пользовательская проверка — назвать ровно эту проверку.

Сохрани итог в:
`reviews/worker_reports/giveaway-publication-gap-recon-01.md`

В финальном ответе обязательно назови этот путь и итоговый статус.