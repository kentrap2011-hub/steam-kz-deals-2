# CURRENT_TASK

status: in_progress
started_at: 2026-08-30 07:18 Europe/Berlin
current_task: Закрыть 5 оставшихся SteamDB history retry через GitHub-owned production pipeline без ручной обработки в interactive chat.
last_progress: GitHub-derived `data/cache/steamdb_runtime_work.json` содержит 5 retry из 534; 529 уже resolved. Архитектурный ownership подтверждён: GitHub владеет scope/retry/validation/persistence/downstream, interactive chat не обрабатывает backlog вручную. Для этого участка создан и проверен быстрый маршрут в `PROJECT_ROUTES.md`; `CHAT_CONTEXT.md` теперь обязывает будущие чаты сначала проверять карту маршрутов перед широким поиском. Выяснено также, что 529 результатов были перенесены через recovery migration, поэтому их наличие не подтверждает работоспособность текущего GitHub → runtime handoff.
next_step: По маршруту `PROJECT_ROUTES.md` найти точный штатный триггер GitHub → external runtime для 5 GitHub-derived retry, запустить/починить именно этот handoff, затем проверить `unresolved_count == 0`, validation/checkpoint `steamdb_history` и успешный downstream rebuild.