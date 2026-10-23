# ЧАТ 7 — устойчивость director governance к старению (6–12 месяцев)

**Task:** `director-governance-aging-resilience-review-01`  
**Source:** `main` @ `0ab87df303c26013e879003a7d2dea40c4645df9` (registration [PR #252](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/252) merged; exact registration HEAD `234f50914eea5f5e2afd29ab8314b2543f975f23`; registry/backlog CI SUCCESS).  
**Mode:** READ-ONLY follow-up; only this report in draft PR.  
**Verdict:** **`CHAT6_PLAN_NEEDS_AGING_GUARD`**.

## Результат простыми словами

Предложение [ЧАТА 6 / PR #251](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/251) — четыре коротких маршрута `STATUS / DECIDE / REGISTER / MERGE` и остановка после достаточных доказательств — **необходимо для сегодняшней проблемы**. Но оно не задаёт механизма для будущих governance PR: через год новые «обязательные» проверки могут снова накапливаться поверх старых, даже если текущий fast path работает. Нужны **одна компактная норма замены, а не добавления**, и маленький PR-only guard на размер/место оперативного маршрута; не новый реестр и не новый полный аудит.

**Уже существует, не переписывать:** [CHAT_PROTOCOL.md START/PRE-SEND](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/CHAT_PROTOCOL.md#L7-L25), [Director role / decision gate](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/DIRECTOR_PROTOCOL.md#L1-L53), [compact report path §8](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/DIRECTOR_PROTOCOL.md#L185-L203), [context budget](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/CHAT_CONTEXT.md#L10-L24), one [registry](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/director_task_plan.json#L1831-L1847) + top [Board](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/DIRECTOR_TASK_BOARD.md#L1-L42), current PR/CI authority, independent QA and fail-closed merge. [PR #241](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/241) уже исправил строгую регистрацию/негативные тесты/PR-wide registry CI и убрал старый лимит двух чатов. [ЧАТ 5 / PR #248](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/248) подтвердил нормативный пробел короткого STATUS, **не** доказал, что PR #241 вызвал поведение модели. Оба отчёта #248/#251 остаются draft.

## Матрица рисков

| Риск через время | Существующая защита | Пробел / статус доказательств | Точечная защита |
| --- | --- | --- | --- |
| +50 завершённых задач: Board/handoff становятся длиннее | JSON registry один machine source; Board хранит авторизации; §8 даёт точный report/PR | **Факт:** уже описаны крупные Board/registry/handoff ([#248, §1](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/248)); **не доказано**, что объём вынуждает читать весь файл | Только верх Board + адресная запись registry + exact PR/report, без второго writable current-view |
| +10 правил: каждое расширяет «обязательный» checklist | START, role boundary, compact reads и общие gates уже есть | **Факт:** общего `STATUS` fast path и PR-гейта замены правил нет ([#251](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/251)); будущий рост — сценарий | Новое требование обязано назвать старое, которое заменено/удалено, владельца и измеренное влияние на mandatory-read |
| Устаревший handoff/несогласованные статусы | [Handoff warning](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/DIRECTOR_HANDOFF_CURRENT.md#L1-L8), canonical registry, fresh PR HEAD/CI | **Факт:** handoff исторический; **гипотеза:** новый директор ошибочно примет его за current | Один канонический живой task ID, no manual second ledger; при конфликте fail-closed + точечная проверка |
| Новая обязательная процедура чтения | CHAT_CONTEXT требует bounded fetch | **Факт:** baseline возможного *полного* чтения ~556 КБ по [#248](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/248); это не фактические tool-траты | Статический budget только **оперативной входной секции**, не архивных документов; проверять будущее изменение обязательного набора в PR |
| Рост рабочих чатов/PR и ошибочная идентичность | Уникальные `ЧАТ N`, task IDs, PR/QA, физическая ротация | **Гипотеза:** много завершённых диалогов повышает риск ложного «активен/завис» | Slot→task→current PR; no status from historical Board, no inference from no commits |
| Модель снова делает worker-аудит или unsafe merge | Уже прямо запрещено; QA/CI exact HEAD | **Доказанное правило, но не детерминированное исполнение.** Нет tool telemetry/формальной гарантии; сейчас `main.protected=false` по актуальному GitHub branch metadata | 5 выборочных поведенческих проверок; отдельная admin branch protection, без заявления о CI-enforced merge, пока не включена |

## ОДНА поправка к предлагаемому ЧАТОМ 6 IMPLEMENT-заданию

К существующему `DIRECTOR_TYPED_DECISION_FASTPATH_IMPLEMENT_01` добавить **«anti-aging acceptance»**; *не* создавать новое большое переписывание, второй ledger или дополнительный обязательный документ. В **том же `DIRECTOR_PROTOCOL.md`** рядом с typed fast path установить, что будущие governance-изменения до merge обязаны: **(а)** указать canonical owner и существующее требование, которое заменяют/снимают, либо обосновать действительно новый риск; **(б)** показать изменение объёма обязательного оперативного чтения и почему нельзя обойтись адресным fetch; **(в)** сохранить STATUS stop-condition, authority/QA/CI/merge; **(г)** пройти ограниченный сценарий нового Director и статусного запроса. Это правило review, а не приглашение директору самостоятельно переписывать все документы.

**Шесть измеримых acceptance-критериев для amended IMPLEMENT:**
1. Правка только `DIRECTOR_PROTOCOL.md` + собственный worker-report; никакой новой registry/current-view, переписи Board/bootstrap, workflow или scheduler на фазе A.
2. Директорская роль и указатель `STATUS / DECIDE / REGISTER / MERGE` видны в первых **120 строках** протокола; реализация не добавляет более **45 net lines** в этот файл без удаления дублирующего текста и объяснения исключения.
3. `STATUS` при полной достаточности exact slot/task/report/PR/HEAD/CI требует **0** полных Board/registry, patch/source/history и **0** worker-level технических аудитов; отсутствие доказательств ведёт к `UNKNOWN`, не к выдуманному статусу.
4. `REGISTER` сохраняет task + JSON + top Board и PR-wide CI **до запуска**; `MERGE` без независимого QA на exact HEAD, требуемых успешных checks и разрешения — **blocked**, даже если отчёт готов.
5. Установлена ровно **одна** короткая процедура review governance PR «заменяет/обосновывает + owner + mandatory-read delta + сценарий»; никаких новых универсально обязательных полных документов и дублирующих live-статусов.
6. Независимый QA финального HEAD проверил четыре команды плюс `stale handoff` и `unsafe PR`; затем 5 реальных/воспроизведённых status/decision обращений проверены по фактическим категориям чтения. Цель: **0** неоправданных full-fetch и расширений scope; наличие rules само по себе не доказывает соблюдение.

## Две фазы и критерии остановки

**A — одно ограниченное исправление.** Принять только typed fast path ЧАТА 6 с вышеуказанным anti-aging acceptance в существующем `DIRECTOR_PROTOCOL.md`. STOP, если невозможно сохранить независимые QA/authority/merge и короткий front-entry без нового реестра; сначала предъявить конкретное противоречие. После A — exact-HEAD QA и 5 выборочных сценариев, никакой автоматической следующей работы.

**B — недорогая защита будущих PR, отдельно разрешаемая после A.** В существующий **PR-wide CI**, без ежедневного запуска, добавить маленькую статическую проверку marked operational fast-path (единственное расположение в первых 120 строках, фиксированный baseline-лимит UTF-8 байт после A с fail-closed при росте без явной ревизии лимита; проверка целостности упомянутых repo paths) и негативные fixtures `duplicate/missing/moved/over-budget`. Governance review вручную проверяет семантическое дублирование, статус authority и реальную стоимость чтения: статический скрипт **не умеет** надежно понимать смысл норм, отличать историю от live truth во всякой прозе или контролировать tool calls модели. Разрешать этот малый CI шаг только отдельным scope/QA, не включать в нынешний report PR. STOP: если guard потребует нового планировщика, новой writable current-view или переписывания архивов — отказаться от расширения. Условие успеха B: каждый изменяющий оперативную секцию PR проходит короткий статический тест, а отрицательные fixtures падают. GitHub `main` protection требует отдельной admin-настройки: один зелёный CI без неё не блокирует unsafe merge технически.

## Сценарии через 6 и 12 месяцев

| Когда / случай | Короткий путь и исполнитель | Что защищает / остаточный риск |
| --- | --- | --- |
| **6 месяцев, +50 закрытых task, запрос «проверь ЧАТ N»** | Director: top Board→одна registry запись→report/PR HEAD/CI; worker только при недостатке evidence | Не читает архив; если нет переписки, «чат завис» остаётся unknown |
| **6 месяцев, +10 новых норм** | Governance reviewer (worker QA) сравнивает diff обязательного front-entry и «что заменено»; Director лишь принимает/отклоняет | B тест ловит размер/перемещение, не семантическое противоречие |
| **6 месяцев, stale handoff** | Новый Director: START→canonical registry/Board/PR; historical handoff как справка | Предупреждение уже есть; ошибочное поведение модели всё ещё возможно |
| **12 месяцев, новый чистый Director** | START + role/typed entry, только current top Board и exact task; не весь старый протокол по каждому запросу | Начальная обязательная проверка остаётся; фиксируется выборочным поведением |
| **12 месяцев, «проверь ЧАТ N» на большом PR** | Director STATUS, worker отдельной независимой QA при конкретном дефиците | Нет права на self-audit под видом STATUS |
| **12 месяцев, unsafe PR с красным/отсутствующим CI** | Director MERGE: fail-closed; independent exact-HEAD QA; GitHub protection — отдельная admin-обязанность | Без фактически активной branch protection CI сам не блокирует админский/direct push |

## Ограничения и итог

Сквозной **architecture preflight пройден только для governance**: GitHub хранит durable state/control plane; Director принимает решения и делегирует; worker проверяет. Ни одного переноса production ownership, recurring stage, queue/retry, semantic execution или deployment. Из-за отсутствия полной director tool telemetry невозможно доказать, что P1 устранит модельные регрессии на 100% или гарантировать «никогда не повторится»; измерять поведение, не объявлять размеры документов причиной вызовов. Отчёты ЧАТОВ 5/6 и PR #241 изучены точечно, нового полного аудита нет.

**Changes:** только этот Markdown report. **Status:** `complete_for_director_review`. **Recommended next step:** директору при отдельной авторизации дополнить **один** будущий IMPLEMENT task ЧАТА 6 anti-aging acceptance из шести пунктов, затем независимый QA. B не запускать автоматически.
