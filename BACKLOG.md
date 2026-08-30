# BACKLOG

Постоянный список задач проекта, которые **нужно сделать, но не сейчас**.

Назначение:
- сюда переносить подтверждённые проблемы и улучшения, которые сознательно откладываются ради более приоритетной работы;
- `CURRENT_TASK.md` использовать только для задачи, которая выполняется прямо сейчас;
- при выборе следующей работы просматривать этот файл и поднимать нужную задачу обратно в `CURRENT_TASK.md`;
- завершённые пункты удалять или переносить в историю/коммит, чтобы backlog оставался коротким.

## Отложенные задачи

### SteamDB history: закрыть оставшиеся retry и проверить штатный handoff

**Статус:** deferred  
**Зафиксировано:** 2026-08-30  
**Причина откладывания:** исторический минимум уже присутствует у большинства игр; сейчас есть более приоритетные проблемы.

Что осталось:
- GitHub-derived runtime work содержит 534 SteamDB history ключа: 529 resolved, 5 unresolved;
- оставшиеся ключи: `App_1282200`, `App_225320`, `App_399670`, `App_630060`, `App_901735`;
- последний известный failure для них: `runtime_web_internal_error`;
- нужно не обрабатывать их вручную в interactive chat, а довести до рабочего состояния штатный GitHub → scheduled runtime handoff;
- после получения evidence GitHub должен сам выполнить ingestion/validation/checkpoint, обновить canonical history cache и downstream artifacts;
- задача считается закрытой только после `unresolved_count == 0` и успешного end-to-end downstream rebuild.

При возврате к задаче сначала сверяться с `config/execution_ownership_contract.json`, `config/steamdb_lookup_contract.json` и актуальным `data/cache/steamdb_runtime_work.json`.
