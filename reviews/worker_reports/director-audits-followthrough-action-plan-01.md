# ЧАТ 6 — выполнение рекомендаций аудитов директора

**Task:** `director-audits-followthrough-action-plan-01` · **Scope:** только report; `main` @ `e1376e23fdcc169a92723eafc80cc685035c84e5`. [Регистрация #250](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/250) merged; CI [registry](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39980472503) / [backlog](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39980472442) green.

**Вердикт: `BOUNDED_IMPLEMENT_TASK_REQUIRED`.** Не нужен третий аудит, переписывание всех правил или сокращение архива. **Первым действием** директор сейчас применяет ограничения чтения; **единственное новое техническое поручение**, требующее отдельной регистрации и разрешения, — короткий типизированный маршрут действий в `DIRECTOR_PROTOCOL.md`. Независимый QA обязателен.

[Отчёт ЧАТА 4 / PR #241](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/reviews/worker_reports/director-governance-safe-fixes-chat4-01.md) уже предлагал компактное current-view как *Stage B design only*, но реализация [#241](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/241) исправила другое. [ЧАТ 5 / PR #248](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/7351bedca0888305acb65b49009766c5e9eb0af0/reviews/worker_reports/director-role-context-regression-diagnosis-01.md) повторил идею экономии чтений и выявил недостающий короткий путь для `STATUS`. **Основной наблюдаемый сбой — поведение директора:** при «Проверь чат 1» он, по описанию задания, пошёл в техническую проверку после достаточных report/PR/CI. Повторяемость подтверждена пользовательским сообщением, но полная последовательность tool calls и причинность PR #241 **не доказаны**.

## Что сделано и что осталось

| Рекомендация и источник | Статус / доказательство в main |
| --- | --- |
| Точные schema-ошибки, негативные regression tests; [#241](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/241) | **implemented** — `scripts/build_site_tasks.py`, `scripts/test_site_tasks.py` |
| Registry CI для любого PR; без искусственного лимита двух чатов; точные handoff/PR/CI; [#241](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/241) | **implemented** — `.github/workflows/validate-site-tasks-page.yml`, `DIRECTOR_PROTOCOL.md`, bootstrap/handoff, Proactive Auditor |
| Реальная защита `main` с обязательными approvals/checks; [отчёт #241](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/reviews/worker_reports/director-governance-safe-fixes-chat4-01.md), [#244](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/244) | **not done** — `main.protected=false` при проверке; настройки требуют administrator и отдельного решения, не чинить в этом задании |
| Компактное derived current-view без второго реестра; [#241 report, Stage B](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/reviews/worker_reports/director-governance-safe-fixes-chat4-01.md) | **not done / proposal**, не принятый implementation scope. Board ~280 КБ, registry ~93 КБ, handoff ~78 КБ; физически сокращать/архивировать их пока **не нужно**: сохранить truth, validator и историю, читать верх/точную запись |
| Директор не делает worker-level audit по status; [`DIRECTOR_PROTOCOL.md` §1/§8](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/DIRECTOR_PROTOCOL.md), [#248](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/248) | **partial** — запрет уже есть, фактическое соблюдение не подтверждено |
| Typed `STATUS`/stop-condition и различение `REGISTER`/`MERGE`; [#248](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/248) | **not done** — общий decision gate (§1) требует свежий Board/registry/PR/CI при любом решении, §8 говорит читать компактно, но не определяет пооперационный предел |
| Проверка поведения на пяти релевантных запросах; [#248](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/248) | **not proven** — нет достоверного «до/после» |

**Предел старого evidence:** отдельный исходный независимый audit-report *до* задания ЧАТА 4 не удалось однозначно идентифицировать по ограниченному маршруту. Не приписывать ему больше, чем подтверждают task этапа A, отчёт и merged PR #241. PR #248 — всё ещё draft и не меняет правила.

## Последовательность

1. **P0 — сразу, без правок:** директор классифицирует запрос `STATUS / DECIDE / REGISTER / MERGE`, читает только текущую Board/registry запись, exact worker report и PR/CI, останавливается при достаточном доказательстве. На 5 соответствующих запросах фиксирует количество/тип GitHub fetch и отклонения; критерий: **0 полных Board/registry/patch/source чтений без конкретного evidence gap, 0 самовольных worker-level аудитов**, QA/authority не ослаблены. Это проверка соблюдения, не доказанная экономия в процентах.
2. **P1 — одно следующее `IMPLEMENT`, отдельно авторизуемое:** только `DIRECTOR_PROTOCOL.md` (§1 decision gate, §2/§8 handoff): короткие режимы и условия остановки для четырёх команд ниже. Не вырезать universal safety checks, а задать *минимальный способ* их выполнить. **Acceptance:** небольшой diff, отсутствие параллельного статуса/реестра, корректность всех четырёх сценариев, draft PR/report; dependency — Director регистрирует task+Board+JSON в main с required CI **до** запуска worker. Затем **независимый QA финального HEAD**, и только Director рассматривает merge.
3. **P2 — после проверки поведения и P1:** если остаётся измеренный перерасход именно из-за навигации, отдельно решить, нужен ли Stage B: *производный* current-view без второй ручной базы, перестройки registry schema, архивирования источников, новой очереди/планировщика или влияния на production. Сейчас такой проект **не авторизован**.

**Одно готовое задание директору для регистрации:** `DIRECTOR_TYPED_DECISION_FASTPATH_IMPLEMENT_01` — **НОВЫЙ worker IMPLEMENT**, разрешено изменить только `DIRECTOR_PROTOCOL.md`; реализовать typed fast-path и явные stop-conditions, сохранить свежие Board/registry/task/report/PR/CI, независимый QA, authorization и unique physical `ЧАТ N`. Запретить код, скрипты, workflow, settings, bootstrap/handoff/Board/JSON, архивирование, Research/Assembly/Deploy/automation. Результат: один малый draft PR, worker-report, четыре сценария и отдельный QA. **Не запускать до самостоятельной директорской регистрации и проверки отсутствия дубликата.**

## Приёмочные сценарии

| Запрос | Минимум evidence и где остановиться |
| --- | --- |
| **«Проверь чат N»** | Точный slot→task из верха Board/registry, report, PR HEAD/state, релевантный exact-HEAD CI. Ответить `сдан / QA / заблокирован / неизвестно`; нет patch/code/history. Без доступа к переписке нельзя объявлять чат зависшим |
| **«Что дальше?»** | Текущая верхняя Board-секция + только релевантные registry IDs/dependencies и live PR/report при споре; предложить **одно** решение/actor, без нового незапрошенного task |
| **«Назначь задачу»** | Проверить необходимость, дубль, scope, authority, свободный слот; директор сам делает именованный task + JSON + актуальный Board, точный CI/merge в main; **до этого stop: `BLOCKED_AUTHORITY`** |
| **«Принимай PR»** | Live PR exact HEAD, independent QA на этот HEAD, required CI, permission/merge gates; если не доказано — **fail closed**. PASS QA не означает автоматический merge или разрешение на Deploy |

**Ограниченный architecture preflight:** GitHub остаётся владельцем canonical governance и production control plane; директор организует, worker реализует/проверяет. P1 изменит только навигационную процедуру, не source/runtime/ownership/queue/retry/schedule. Этот ЧАТ 6 **не изменял** protocol, registry, Board, code, CI или production. Причина реальных задержек без telemetry остаётся неизвестной.
