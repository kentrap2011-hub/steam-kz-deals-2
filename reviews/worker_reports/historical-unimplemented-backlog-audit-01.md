# Historical unimplemented backlog audit 01

**Дата:** 2026-10-08  
**Режим:** DIAGNOSTIC / HISTORY AUDIT / NO IMPLEMENTATION  
**Репозиторий:** kentrap2011-hub/steam-kz-deals-2  
**Источник истины:** main, проверенное состояние планов и исходников: 3ddc83fcf6646fccc6fc5bc72e5259bd11da54d4; перед ветвлением main продвинулся до a6b1ced33916f82dcd9030b027015cd24b5bc77c исключительно по четырём путям состояния Progressive PASS 2 и не менял проверяемые планы/функции.  
**Статус:** diagnostic_complete_ready_for_director_review.

## 1. Итог и границы достоверности

Восстановлены **пять практически подтверждённых незакрытых направлений**, отсутствующих в каноническом реестре задач для сайта; ещё **три направления требуют решения Director** прежде, чем их можно объявить самостоятельными будущими задачами. YouTube — только один из найденных случаев.

Главный системный разрыв: старый [BACKLOG.md](../../BACKLOG.md) по-прежнему содержит отложенные продуктовые требования, но новый [config/director_task_plan.json](../../config/director_task_plan.json) используется как единственный источник списка задач сайта. Старые записи не были автоматически сверены с новым реестром. **Нельзя** переносить всё содержимое BACKLOG без проверки: значительная часть уже реализована, заменена новой политикой или существует в виде внешней runtime-очереди, а не новой продуктовой задачи.

Это **проверка доступных долговечных свидетельств**, а не доказательство отсутствия любой мысли в устных/несохранённых чатах. Просмотрены страницы истории коммитов Director Board (475 изменений, с 2026-09-01 по 2026-10-08), история BACKLOG (28 изменений), контрольные старые снимки Board/BACKLOG, текущий Board и реестр, связанные worker task/report, продуктовые решения и точечные актуальные source/runtime-файлы. Проверялись недавние PR/commit-пути для разграничения законченного и отложенного. Это не означает построчного чтения каждого diff всех 475 коммитов: связанные ветви истории проходились по конкретным следам. Отсутствие PR с подходящим названием **не использовано как единственное доказательство отсутствия реализации**.

## 2. Текущий перечень и система классификации

На проверенном main в реестре 25 позиций, включая сам этот аудит. Уже зарегистрированы: semantic translation, Dossier, текущий Deep, Steam reviews, Steam 50%/top-100, owned DLC, Deep ranking, Deep site, Deep cutover, taste-profile update, 20 explained taste ratings, Taste throughput/age queue, Steam prefilter/incident watch, giveaway decouple/ITAD и architecture cleanup. Сам факт существования старого task-файла не делает его незавершённым.

Для каждого кандидата ниже применяется одна из пяти категорий из задания: **(1) восстановить**, **(2) реализовано**, **(3) отменено/замещено**, **(4) дубликат текущего**, **(5) неясно — решение Director/пользователя**.

Ссылки на важные исходные документы:
- [BACKLOG на main](../../BACKLOG.md) и [BACKLOG, старый снимок 2026-08-30](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/874891eb4/BACKLOG.md).
- [Board, снимок 2026-09-10](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/9b21f6268/DIRECTOR_TASK_BOARD.md), [Board, 2026-09-11](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/cf4f0d395/DIRECTOR_TASK_BOARD.md), [актуальный Board](../../DIRECTOR_TASK_BOARD.md).
- [CURRENT_TASK](../../CURRENT_TASK.md) — архив принятых worker-итогов, **не** самостоятельный будущий backlog.
- [PROJECT_DECISIONS](../../PROJECT_DECISIONS.md) — приоритетнее старой формулировки, если продуктовая модель впоследствии изменилась.

## 3. Категория 1 — отсутствуют в forward registry, целесообразно вернуть на рассмотрение

### R1. YouTube: русскоязычный обзор на карточке игры

- **Первичное свидетельство:** [BACKLOG.md, запись 2026-08-30](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/874891eb4/BACKLOG.md); запись всё ещё есть в [текущем BACKLOG](../../BACKLOG.md), но отсутствует среди ID [текущего forward plan](../../config/director_task_plan.json).
- **Восстановимый обязательный scope:** автоматически находить подходящий **русскоязычный обзор конкретной игры**; сохранять выбранный URL/видео-ID и минимум метаданных в producer-owned production payload; выводить компактную кнопку/блок перехода на карточке; предусмотреть корректное отсутствие подходящего обзора; **не** искать YouTube из read-only браузера при открытии карточки.
- **Почему не признано реализованным:** текущий [web/app.js](../../web/app.js) не имеет consumer-пути YouTube или видео-обзора; соответствующий payload/UI contract и task-ID в forward plan не обнаружены при точечной проверке. Нельзя трактовать наличие Steam review Dossier как реализацию видео-обзоров: это другой тип evidence и UX.
- **Не восстановлено однозначно:** каналы/белый список, допустимые источники, качество, язык речи против языка названия, recency, разрешение неоднозначности изданий/DLC, квоты/provider, embed против внешнего перехода. **Не выдумывать** эти решения.
- **Рекомендация:** вернуть **CONTRACT/RECON → IMPLEMENT**, где GitHub выбирает/сохраняет точный видео-идентификатор и источник, сайт только показывает. **Трудоёмкость L4/T4/I3 (историческая), средняя срочность**. Зависимость: стабильная схема текущей/будущей карточки и отдельный разрешённый механизм получения видео.

### R2. Windows: фактический автоматический источник совместимости

- **Первичное свидетельство:** [BACKLOG.md, запись 2026-08-30](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/874891eb4/BACKLOG.md); каноническое решение [PROJECT_DECISIONS — RANK-005](../../PROJECT_DECISIONS.md), прямо говорит, что автоматический надёжный источник подтверждённых Windows-фактов **ещё не реализован**.
- **Восстановимый scope:** автоматический grounded evidence-source проблем современных Windows; нельзя превращать устаревшую строку Steam «Windows XP/7/8» в доказанную несовместимость. Признаки подтверждённых ручных fixes, проблем запуска/режима совместимости, значимых текущих проблем должны попадать через canonical ownership и проверенный evidence/риск-путь.
- **Почему не признано реализованным:** [scripts/priority_ranking.py](../../scripts/priority_ranking.py) уже **потребляет** practical.modern_windows_friction, но потребительский скоринг не доказывает наличие автоматического producer для этих фактов. Прямое указание о недостающем automatic source в RANK-005 остаётся неотменённым; отдельная активная задача по сбору таких данных в реестре отсутствует.
- **Не восстановлено:** конкретный провайдер, лицензия, identity/provenance/cache/TTL, допустимый уровень уверенности. Нельзя переносить старый штраф V2 буквально в будущий Deep Stage 1/2.
- **Рекомендация:** **CONTRACT/RECON → IMPLEMENT**, сначала определить факт-источник и ownership, затем интеграцию с актуальной, а не устаревшей балльной архитектурой. **L4/T4/I3 (историческая), обычная срочность; зависимость от Deep ranking/cutover и evidence-path.**

### R3. Четыре верхние карточки статистики как фильтры

- **Первичное свидетельство:** [WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md](../../WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md), затем [готовый диагностический отчёт](top-summary-filter-buttons-recon-01.md), статус RECON = complete, но **IMPLEMENT оставлен отдельным последующим шагом**.
- **Восстановимый scope:** сделать кликабельными верхние «Новые», «Не смотрел», «Интересно», «Видел» как фильтры текущей ленты; убрать дублирующую нижнюю вкладку «Интересно» **после** работоспособности верхней; сохранить кнопку на карточке, которой игра помечается интересной. Использовать существующий единый currentTab и исходный порядок producer-owned очереди, не создавать вторую модель состояния.
- **Почему не признано реализованным:** в текущем [web/index.html](../../web/index.html) сохраняется нижняя вкладка data-tab="liked"; в [web/app.js](../../web/app.js) нет переходов data-summary-filter, то есть описанная worker recon реализация не попала на main. Нет готового implementation report; текущий forward plan не содержит задачу.
- **Уточнения/зависимости:** требуется аккуратно сохранить cursor, локальное «В конец», пустые фильтры и возврат из giveaway; у «Новые» и «Не смотрел» изменение seen сразу меняет состав фильтра. Принципиальная постановка полностью восстановлена, продуктового доопределения почти не требуется. Начать после принятого состояния параллельных site/Deep UI файлов.
- **Рекомендация:** **IMPLEMENT с ранее готовым recon**, средняя трудоёмкость / обычная срочность, UI acceptance на телефоне.

### R4. Оценка качества конкретного издания, ремастера или набора — отдельно от игр внутри

- **Первичное свидетельство:** [WORKER_TASK_TASTE_PACKAGE_EDITION_QUALITY_RECON_01.md](../../WORKER_TASK_TASTE_PACKAGE_EDITION_QUALITY_RECON_01.md) и [его завершённый отчёт](taste-package-edition-quality-recon-01.md). [Отчёт по активации состава пакета](taste-package-member-activation-01.md) многократно фиксирует **package/edition quality not implemented**.
- **Восстановимый пользовательский смысл:** члены набора оцениваются по Taste отдельно; одна подходящая игра позволяет не исключать весь набор сразу. Но **качество конкретного издания** — ошибки ремастера, техническое состояние, урезанный контент и подобное — отдельный доказательный сигнал, способный дать значимый видимый минус и снизить итоговый приоритет. Не объявлять пакет непригодным для Taste только потому, что Definitive Edition плохого качества. Проверочный пример: GTA: The Trilogy – Definitive Edition.
- **Почему не реализовано:** package member identity/aggregation принято PR #31 и activation PR #32/#33, но эти задачи **явно исключили** сбор/скоринг качества издания. В текущей схеме не найден завершённый offer_edition_quality producer, а forward registry этого follow-up не содержит.
- **Не все детали финальны:** recon предложил отдельный offer/version identity и grounded provenance; контракт/политика штрафа ещё должны быть одобрены, нельзя механически применять старые V2 компоненты после нового Deep 60/40.
- **Рекомендация:** разделить на **(i) CONTRACT + сбор точных edition-evidence, (ii) score/warning integration**; вторая зависит от первой и текущей Deep ranking/cutover. Высокая трудоёмкость, обычная срочность, возможна высокая пользовательская ценность при проблемных сборниках.

### R5. IGDB duration: завершить включение уже подготовленного production enrichment

- **Первичное свидетельство:** [WORKER_TASK_DURATION_IGDB_IMPLEMENT_01.md](../../WORKER_TASK_DURATION_IGDB_IMPLEMENT_01.md) и [отчёт implementation](duration-igdb-implement-01.md), конечный статус **blocked**, не complete live.
- **Что осталось:** технический Github-owned collector/cache/валидаторы уже написаны, но требуется **добровольное предоставление владельцем GitHub Actions Secrets** IGDB_CLIENT_ID и IGDB_CLIENT_SECRET (не передавать в чат), положительная OAuth/IGDB connectivity проверка, отдельное bounded включение и заполнение реального кэша по обычному GitHub-owned маршруту.
- **Подтверждённое отсутствие live результата:** [config/duration_enrichment_contract.json](../../config/duration_enrichment_contract.json) содержит production_collection_enabled: false; [data/cache/duration_estimates.json](../../data/cache/duration_estimates.json) имеет пустые entries. Текущий forward plan не выделяет completion/provisioning dependency. **Нельзя объявлять весь IGDB feature «не реализованным»**: проблема в activation, а не в отсутствующем коде.
- **Зависимости:** user-provisioned provider account/secrets и приемлемость условий доступа, затем bounded connectivity validation, затем текущая политика использования duration в новой Deep architecture. Никакого использования личных credentials через чат.
- **Рекомендация:** вернуть как **BLOCKED ACTIVATION / USER INPUT**, не запускать новый implementation. Оставшаяся инженерная работа небольшая/средняя, срочность низкая–обычная до подключения провайдера.

## 4. Категория 5 — неясно, восстановление только после решения Director

### U1. Точечная переоценка после изменения вкусового профиля

- **Свидетельство:** исторические [Board 2026-09-10](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/9b21f6268/DIRECTOR_TASK_BOARD.md) и [Board 2026-09-11](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/cf4f0d395/DIRECTOR_TASK_BOARD.md), самостоятельный незавершённый пункт taste-selective-profile-reevaluation-01, queued_after_current_backlog_is_usable.
- **Историческое требование:** небольшая правка live-profile не должна без необходимости отправлять сотни не затронутых игр на повторную оценку; только доказуемо затронутые, с immutable provenance, conservative fallback, неизменённым pinned in-flight scope. В старом плане указывалась **почасовая обработка только текущих затронутых items**, не повторный обход всех игр и не разрешение создавать Scheduled Task.
- **Почему не считать выполненным:** [PROJECT_DECISIONS — PPD-012](../../PROJECT_DECISIONS.md) решает **commit-only churn при неизменном содержимом профиля** и строгое reuse для эквивалентной семантики, но не доказывает безопасный selective invalidation при **реальной смене** предпочтений. В текущем реестре задачи нет.
- **Почему не безусловная категория 1:** Taste/Deep модель изменилась, существует новый Deep Stage1/Stage2 и отдельный запланированный profile-update; старый обещанный hourly cadence может конфликтовать с актуальным ownership/daily contract. **Director должен решить**, сохраняется ли требование и каким компонентом; первым шагом может быть новый bounded RECON/CONTRACT, не runtime implementation. Трудоёмкость высокая; отложить после стабилизации нового Deep.

### U2. Live-верификация Taste Steps 1–3 на текущем production

- **Свидетельство:** [WORKER_TASK_TASTE_STEPS_1_3_PRODUCTION_MATERIALIZATION_ACCEPTANCE_01.md](../../WORKER_TASK_TASTE_STEPS_1_3_PRODUCTION_MATERIALIZATION_ACCEPTANCE_01.md), [завершённый report](taste-steps-1-3-production-materialization-acceptance-01.md), статус blocked_semantic_runtime, и [DIRECTOR_REVIEW_CHECKPOINTS.md](../../DIRECTOR_REVIEW_CHECKPOINTS.md): taste_integrated_production_verification_pending: true.
- **Чего не произошло:** после реализации/independent Taste review ожидалось показать доказанный новый live snapshot и десять контрольных игр пользователю. Старый отчёт имел 701 unresolved semantic rows; **этот счёт исторический, не текущий**. Код поддерживающих reviewer рекомендаций был внедрён, но фактический end-to-end acceptance не доказан этим report.
- **Решение Director:** либо сохранить как явный **blocked acceptance checkpoint**, либо объединить с новой Stage1/Stage2 production acceptance, без повторения устаревшего Taste V5 route как отдельного producer. Не создавать вторую semantic queue/worker.

### U3. Старый SteamDB single retry против нового batch scope

- **Свидетельство:** [BACKLOG.md](../../BACKLOG.md), старый остаток App_901735; [steamdb_lookup.validation.json](../../data/cache/steamdb_lookup.validation.json) фиксирует старое 8/9 и 1 unresolved. Однако свежий [steamdb_runtime_work.json](../../data/cache/steamdb_runtime_work.json) и [steamdb_runtime_state.json](../../data/cache/steamdb_runtime_state.json) на проверенном main показывают **555 current unresolved** и не включают App_901735 в текущий runtime-work scope.
- **Классификация:** старую задачу «разобрать именно App_901735» **нельзя автоматически восстановить** как текущую: прежний subset сдвинулся; новый runtime-work уже представляет актуальные обязательства GitHub. Не считать новые 555 отдельной запланированной product implementation задачей только по числу ожидающих.
- **Решение Director:** нужен короткий read-only scope reconciliation, если пользователь хочет отдельно вернуться к историческому retry; не назначать самостоятельную операционную задачу по устаревшему ключу без доказательства его текущей применимости.

## 5. Категория 2 — следы старых задач, уже реализованные или закрытые

| Историческое требование | Доказательство завершения / корректная граница |
|---|---|
| Wishlist + действительно хорошая скидка преодолевают слабый Taste | [reconsideration-commercial-bridge-and-wishlist-implement-01.md](reconsideration-commercial-bridge-and-wishlist-implement-01.md) — Step 3 complete; [Taste Review Steps 1–3](../taste_reviews/taste-steps-1-3-current-review-01.md) подтверждает принятую семантику. **Live materialization** отдельно U2. |
| Подтверждённые минусы на карточке; отсутствие минуса — incomplete | [grounded-negative-implement-01.md](grounded-negative-implement-01.md): V4 evidence/readiness/negative-only backfill route реализованы, но последующее canonical semantic filling было blocked. Старый пункт «реализовать такую модель» не восстановлять как новую задачу. |
| Кроссплатформенные раздачи claim-to-keep отдельным видом | [cross-platform-giveaway-separate-view-fix-01.md](cross-platform-giveaway-separate-view-fix-01.md) и файлы [web/giveaway-ui.js](../../web/giveaway-ui.js); **улучшение идентичности ITAD и декуплинг** — существующие отдельные задачи категории 4. |
| Сворачиваемая детальная оценка, убрать misleading wishlist 0/4 | [web/score-details-ui.js](../../web/score-details-ui.js) с раскрытием деталей, прежние worker reports [detailed-score-ui-01.md](detailed-score-ui-01.md), [detailed-score-user-fixes-01.md](detailed-score-user-fixes-01.md). |
| Ярлык Chrome/manifest | [web/index.html](../../web/index.html) подключает icon.svg и manifest; старый BACKLOG очищен после implementation. |
| Пропадающие скриншоты | Старое изменение BACKLOG «Close media screenshots after user confirmation» (2026-09-01, e90627540). Это исторически закрытая user-verified работа, не новый тикет без свежего регресса. |
| Особая ценность Steam Achievements для уже сыгранных игр | [PROJECT_DECISIONS — RANK-012](../../PROJECT_DECISIONS.md), [scripts/priority_ranking.py](../../scripts/priority_ranking.py); новая Deep architecture может перенести смысл в Stage 1, но старое требование не означает отсутствующую старую реализацию. |
| Покупка bundle/package вместо отдельных игр, member-game Taste | [reconsideration-commercial-bridge-and-wishlist-implement-01.md](reconsideration-commercial-bridge-and-wishlist-implement-01.md), [taste-package-member-activation-01.md](taste-package-member-activation-01.md); отдельная проблема качества конкретного издания — **R4**, не смешивать. |
| Страница задач проекта и публикация | PR #162 / #165 и текущие [web/tasks.js](../../web/tasks.js), [forward plan](../../config/director_task_plan.json); задача реализована, **полноту миграции старых идей этот аудит только диагностирует**. |
| Deep Stage 1 / Stage 2 architecture, foundation и semantic queue priority | Текущий forward registry помечает freeze, Stage1, Stage2, queue priority complete. Не оживлять принятые записи CURRENT_TASK. |

## 6. Категория 3 — замещённые / неавторизованные старые планы

- **Фиксированная нормализация старого strong/moderate Taste через арифметику пяти факторов.** В старом BACKLOG это была отдельная задача; новая авторизованная [two-stage Deep архитектура](../../WORKER_TASK_DEEP_TWO_STAGE_COMPARATIVE_CALIBRATION_IMPLEMENT_01.md) заменяет жёсткий fixed-five additive scoring на Stage1 findings + Stage2 comparative calibration. Не восстанавливать старую форму задачи; требуемый новый ranking/site/cutover уже в forward registry.
- **Отдельный Publication Freshness Sentinel.** Исторический [Board, «Other queued work»](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/cf4f0d395/DIRECTOR_TASK_BOARD.md) прямо помечает WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md как **superseded by user decision**; не включать.
- **Progressive site progress header compaction** в текущей Board — **DRAFT / NOT AUTHORIZED** (не пропавшее утверждённое обязательство). Для восстановления нужно новое продуктовое согласование, а не автоматическая миграция.

## 7. Категория 4 — старые пункты, уже отражённые в текущем forward plan

Не создавать дубликаты следующих исторических намерений: Steam server-side prefilter; Steam 50% / rolling top-100 discovery; Steam error notification watch; giveaways decoupled from Steam crawl; giveaway ITAD identity; architecture review recommendations follow-up; DLC для принадлежащих базовых игр; уточнение Taste profile по 14 вопросам; дополнительные объяснённые оценки для backtest; Deep Stage 1/2/ranking/site/cutover; Taste throughput benchmark и age-ordering. Все эти направления уже имеют соответствующие ID в [config/director_task_plan.json](../../config/director_task_plan.json) (часть planned/blocked/active). Их отсутствие в каком-либо частном старом разделе Board — не основание для восстановления.

## 8. Предупреждения для Director и контроль исполнения

1. **Не восстанавливать старые записи механически.** BACKLOG не синхронизирован с новым forward plan и одновременно содержит реально забытое, технически закрытое и stale runtime. Новые задачи вносить только Director-решением вместе с Board + canonical JSON registry (одним согласованным изменением).
2. **Новая семантическая архитектура может менять место реализации.** YouTube и фильтры относятся к producer/consumer и UI; Windows/edition/duration связаны с текущим Deep score и его cutover. Не внедрять старые V2 веса во время миграции 60/40.
3. **Никакого нового scheduler/queue.** Даже если в историческом задании selective profile reruns описаны как hourly, это не разрешение создавать Scheduled Task. Вначале сверить текущие execution_ownership/daily contracts и актуальные источники фактов.
4. **Степень отрицательного доказательства различна:** для R3 и R5 есть положительная source-проверка, что нужные UI controls/activation отсутствуют; для R4 прямо написано not implemented в принятом worker report; для R2 — каноническое решение о недостающем automatic source; для R1 — BACKLOG + отсутствие соответствующего route в проверенных producer/consumer/registry. Их нельзя ошибочно объявлять «100% нигде не существует» без runtime acceptance.
5. **Контекст/маршрут для следующего аудита:** краткий воспроизводимый путь — BACKLOG snapshots → historical Board queued sections → точный worker report → актуальные contracts/source → forward JSON registry → PR/commit/validation по сомнительным случаям. Не начинать с 144 KB CURRENT_TASK или полного dump всех PR. Этот маршрут сохранён здесь; отдельное изменение PROJECT_ROUTES.md не делалось из-за строгого report-only delivery.

## 9. Что изменено этим worker

**Только данный диагностический report в отдельной ветке/PR.** Не изменены BACKLOG.md, DIRECTOR_TASK_BOARD.md, config/director_task_plan.json, CURRENT_TASK.md, canonical decision/contracts, исходный код, production data, semantic work, GitHub Actions или ChatGPT Scheduled Tasks. Не выполнялась реализация ни одной найденной задачи.

## 10. Компактный proposed restoration list — ТОЛЬКО на решение Director

| № | Направление | Рекомендуемый статус | Очередность / зависимость |
|---|---|---|---|
| **R1** | Русскоязычный YouTube-обзор на карточке | **RESTORE, planned CONTRACT/RECON → IMPLEMENT**, L4/T4/I3 | После согласования источника/selection и стабильной карточки; обычная срочность |
| **R2** | Автоматический grounded Windows compatibility source | **RESTORE, planned CONTRACT/RECON**, L4/T4/I3 | Согласовать с текущим Deep score/cutover |
| **R3** | Верхние «Новые / Не смотрел / Интересно / Видел» = фильтры | **RESTORE, planned IMPLEMENT** | Предыдущий recon готов; после параллельных site/UI изменений; мобильная проверка |
| **R4** | Edition/remaster/package quality evidence + warning/rank | **RESTORE, planned split CONTRACT → evidence → integration** | После принятой Deep ranking/identity модели; две связанные задачи |
| **R5** | Включение IGDB duration collector | **RESTORE, blocked on user-provisioned GitHub Secrets** | Connectivity gate → bounded enablement, без нового collector |
| **U1** | Selective re-evaluation после изменения profile | **DIRECTOR DECISION / возможный новый RECON** | После Deep cutover; проверить relevance и canonical cadence |
| **U2** | Подтверждение Taste Steps 1–3 на живом site | **DIRECTOR DECISION / blocked acceptance**, не новый worker | Объединить с текущим Deep integration/live acceptance либо сохранить отдельный checkpoint |
| **U3** | SteamDB старый App_901735 single retry | **DIRECTOR DECISION / bounded scope reconciliation** | Не восстанавливать старый key без current-scope доказательства; текущий GitHub runtime уже ведёт 555 work items |
