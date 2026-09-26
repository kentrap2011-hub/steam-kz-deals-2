# PROJECT_DECISIONS

Долговечный журнал **почему** в проекте приняты неочевидные продуктовые и архитектурные решения.

`PROJECT_RULES.md` отвечает на вопрос **что должно быть**.
`config/*.json` отвечает на вопрос **как это формально задано машине**.
`PROJECT_ROUTES.md` отвечает на вопрос **где это реализовано и как быстро туда попасть**.
`PROJECT_DECISIONS.md` отвечает на вопрос **почему правило именно такое, какую проблему оно решает и какие альтернативы были сознательно отвергнуты**.

## Как вести журнал

- Добавлять сюда каждое подтверждённое пользователем решение, если его смысл не очевиден из самого правила или если будущий разработчик/чат вполне может решить, что это ошибка.
- Не писать сюда каждую мелкую техническую правку. Нужны именно решения, понимание причины которых важно для будущих изменений.
- Для каждого решения фиксировать: дату, статус, правило, причину, сознательно отвергнутую альтернативу/ловушку и основные места реализации.
- Если решение меняется, старую запись не удалять молча: пометить `superseded` и сослаться на новое решение. Так можно понять эволюцию логики без чтения истории чатов и коммитов.
- При вопросе «почему код/сортировка устроены именно так?» сначала проверить релевантное решение здесь, а уже потом исследовать историю Git.

---

## RANK-001 — Только одна финальная формула `priority_rank`

**Дата:** 2026-08-30
**Статус:** implemented in production path; regression verified, full payload rebuild pending external history gate

**Решение:** pipeline может иметь несколько стадий enrichment/refinement, но итоговый `priority_rank` должен вычисляться одной канонической policy-driven формулой только после завершения всех refinement-факторов.

**Почему:** исторически `build_daily_visual_payload.py` уже сортировал игры, после чего добавленный позднее `refine_visual_ranking.py` уточнял fit/риски/практические признаки и сортировал второй раз другой формулой. Сам путь `builder → refiner` был намеренным, потому что после refinement порядок действительно нужно пересчитать. Ошибка состояла не в двух стадиях, а в двух независимых источниках правил сортировки, которые со временем разошлись.

**Не делать:** не удалять полезный refinement только ради «одной сортировки» и не оставлять две полные sort-key функции в production path.

**Основные места:** `config/final_ranking_policy.json`, `scripts/build_final_visual_payload.py`, `scripts/priority_ranking.py`, `.github/workflows/build-daily-visual-payload.yml`.

---

## RANK-002 — Срочность окончания скидки выше автоматического качества рекомендации

**Дата:** 2026-08-30
**Статус:** implemented and regression verified

**Решение:** среди уже прошедших taste/commercial eligibility игр самый верхний автоматический слой сортировки: `скидка заканчивается сегодня → завтра → позже/срок неизвестен`.

**Почему:** даже не самая сильная игра из текущего списка может стать практически более важной для просмотра, если пользователь иначе не успеет дойти до неё до окончания акции. Задача очереди — не только абстрактно назвать лучшую игру, но и не дать пропустить исчезающее предложение.

**Граница:** срочность не спасает игру ниже taste threshold, символическую скидку, превышение бюджета или уже закончившуюся акцию. Неизвестная дата не штрафуется — просто не получает подтверждённый срочный приоритет.

**Основные места:** `PROJECT_RULES.md`, `config/final_ranking_policy.json`, `scripts/priority_ranking.py`, `scripts/validate_priority_ranking.py`.

---

## RANK-003 — Смешанная группа «вкус + выгодность» остаётся главным обычным качественным слоем

**Дата:** 2026-08-30
**Статус:** superseded by RANK-010 for final ordering

**Решение:** качественный `priority_bucket` по-прежнему реализует согласованную матрицу примерно 60% taste / 40% deal и остаётся главным обычным качественным слоем, но после срочности и серьёзного подтверждённого риска согласно RANK-009.

**Почему:** скидка, wishlist, ачивки и другие признаки не должны превращать слабое вкусовое попадание в более важную покупку, чем существенно более подходящая игра. Срочность отвечает за риск физически потерять предложение, а серьёзный подтверждённый риск — за ситуацию, когда формально выгодная покупка с высокой вероятностью даст плохой пользовательский опыт.

**Не делать:** не заменять качественную матрицу скрытым числовым score без отдельного согласования.

**Замена:** RANK-010 вводит отдельно согласованный **прозрачный** числовой score, который пользователь видит целиком и который реально определяет финальный порядок. `priority_bucket` остаётся eligibility/explanation context, но больше не является скрытым final-sort слоем.

**Основные места:** `PROJECT_RULES.md`, `config/final_ranking_policy.json`, `config/mailing_policy.json -> sorting.qualitative_priority_buckets`.

---

## RANK-004 — Прямую оценку пользователя не учитывать второй раз после `priority_bucket`

**Дата:** 2026-08-30
**Статус:** principle retained; final mechanism superseded by RANK-010

**Решение:** direct user evidence может корректировать `fit`, после чего пересчитывается коммерческая ветка и `priority_bucket`; отдельного следующего слоя `direct_user_evidence` в final sort быть не должно.

**Почему:** иначе один и тот же вкусовой сигнал учитывается дважды: сначала меняет fit/bucket, затем ещё раз двигает игру внутри bucket.

**После RANK-010:** принцип «один сигнал — один вклад» сохраняется. Если есть точная прямая пользовательская оценка, она становится источником taste-score и не получает отдельного дополнительного бонуса поверх него.

**Основные места:** `scripts/refine_visual_ranking.py`, `scripts/priority_ranking.py`, `config/final_ranking_policy.json`.

---

## RANK-005 — Подтверждённые персональные/Windows-риски раньше wishlist и цены

**Дата:** 2026-08-30
**Статус:** risk principle retained; precedence mechanism superseded by RANK-010; confirmed Windows fact acquisition still missing

**Решение:** учитывать **серьёзные подтверждённые** персональные и практические риски, включая реальные проблемы запуска на современной Windows. По RANK-009 этот слой теперь стоит даже раньше смешанной группы «вкус + выгодность». Средние/слабые эвристические риски остаются описательными и сами по себе не должны обгонять группу приоритета, wishlist или коммерческую выгоду.

**Почему:** хорошая скидка мало полезна, если у игры есть подтверждённая проблема, которая существенно ухудшит сам опыт или потребует заметных ручных исправлений.

**После RANK-010:** риск не является отдельным скрытым lexicographic слоем; он видимым штрафом входит в персональную часть score. Базовые ориентиры: серьёзный персональный риск `−10`, подтверждённая серьёзная Windows-проблема `−12`, конкретные числа живут только в policy-конфиге.

**Windows-уточнение:** строка Steam с XP/7/8 сама по себе не является доказательством проблемы — у старых игр требования часто просто не обновлялись. Такая строка только запускает/мотивирует дополнительную проверку. Понижение допустимо лишь при подтверждённой фактической ориентации ниже Windows 10, необходимости патчей/compatibility mode/ручных fixes или известных проблемах современной Windows.

**Текущая техническая граница:** production ranking нейтрализует одну только legacy Steam label и умеет понизить `known_fix_required`, `confirmed_pre_windows_10_target`, `serious_problem`. Но отдельный канонический автоматический источник, который надёжно получает эти подтверждённые Windows-факты, ещё не реализован.

**Основные места:** `PROJECT_RULES.md`, `config/final_ranking_policy.json`, `scripts/refine_visual_ranking.py`, `scripts/priority_ranking.py`, `scripts/validate_priority_ranking.py`.

---
## RANK-006 — Wishlist важен, но ограничен

**Дата:** 2026-08-30
**Статус:** principle retained; final mechanism superseded by RANK-010

**Решение:** после серьёзных рисков и группы приоритета wishlist даёт заметный приоритет уже допустимому кандидату.

**Почему:** wishlist — прямой сигнал предварительного интереса пользователя, но не доказательство вкусового соответствия и не повод обходить eligibility/budget/deal gates.

**После RANK-010:** wishlist — ограниченный видимый бонус внутри персональной части score; стартовое значение `+4/4` задаётся только в `config/final_ranking_policy.json`.

**Не делать:** wishlist не должен сам включать игру в список и не должен обходить eligibility/budget/deal gates.

**Основные места:** `PROJECT_RULES.md`, `config/final_ranking_policy.json`, `scripts/priority_ranking.py`.

---

## RANK-007 — Размер скидки важнее качества относительно исторического минимума

**Дата:** 2026-08-30
**Статус:** superseded by RANK-011

**Решение:** внутри одинаковых expiry/risk/bucket/wishlist условий сначала сравнивать `discount_percent`, и только потом `price_quality_vs_history`.

**Почему:** у новой игры даже обычные −20% часто автоматически являются историческим минимумом просто потому, что история цены короткая. Если history quality поставить раньше процента скидки, такой технический `record` получает слишком сильное преимущество над старой игрой с действительно крупной скидкой, например −70%.

**Сознательно отвергнуто:** порядок `history_quality → discount_percent`.

**Замена:** по RANK-011 процент скидки вообще не даёт баллов. Коммерческий score использует абсолютную экономию в рублях, текущую цену и историю цены как три отдельные видимые компоненты.

**Основные места:** `config/final_ranking_policy.json`, `scripts/priority_ranking.py`, `scripts/validate_priority_ranking.py`.

---

## RANK-008 — Достижения и длительность только поздние различители близких кандидатов

**Дата:** 2026-08-30
**Статус:** principle retained; lexicographic mechanism superseded by RANK-010; achievement strength refined by RANK-012

**Решение:** после скидки, истории и текущей цены учитывать achievement quality; duration — ещё позже как самый слабый дополнительный критерий перед title.

**Почему:** наличие/качество Steam Achievements важно пользователю, но не должно обгонять существенно более выгодную покупку. Длительность ещё менее фундаментальна и нужна только для очень близких вариантов.

**После RANK-010:** достижения и длительность становятся небольшими видимыми компонентами персональной части score вместо отдельных скрытых tie-break слоёв.

**Основные места:** `PROJECT_RULES.md`, `config/final_ranking_policy.json`, `scripts/priority_ranking.py`.

---

## RANK-009 — Серьёзный подтверждённый риск важнее смешанной группы «вкус + выгодность»

**Дата:** 2026-08-30
**Статус:** superseded in final mechanism by RANK-010; rationale preserved

**Решение:** после срочности окончания скидки сравнивать серьёзный подтверждённый персональный/практический риск и только затем `priority_bucket`. Средние и слабые риски на этом раннем слое остаются нейтральными.

**Почему:** `priority_bucket` смешивает вкусовое соответствие с коммерческим вердиктом. На реальном примере `Seraph's Last Stand` против `High On Life` очень дешёвая Seraph получила более сильную группу покупки (`МОЖНО БРАТЬ`), хотя у неё подтверждён высокий персональный риск однообразного повторения; High On Life находится в wishlist, имеет лучший вкусовой порядок и не имеет серьёзного подтверждённого риска, но была ниже из-за более слабого коммерческого вердикта (`ЛУЧШЕ ЖДАТЬ`). Это означает, что выгодность покупки могла перекрыть важный сигнал о том, насколько сама игра вероятно понравится.

**После RANK-010:** исходная проблема решается не перестановкой скрытых слоёв, а прозрачным score: taste, wishlist, риск, цена, экономия и история видны отдельно и складываются в тот же итоговый балл, по которому реально сортируется очередь.

**Основные места:** `config/final_ranking_policy.json`, `scripts/priority_ranking.py`, `scripts/validate_priority_ranking.py`, `PROJECT_RULES.md`.

---

## RANK-010 — Финальный рейтинг 0–100 должен быть прозрачным и настраиваемым из одного конфига

**Дата:** 2026-08-30
**Статус:** implementation in progress

**Решение:** после eligibility финальный обычный приоритет определяется числовым `total_score` 0–100. Стартовое распределение: до 60 баллов за персональную ценность и до 40 за выгодность покупки. Срочность окончания акции остаётся отдельным верхним слоем вне 100 баллов; `manual_end_at` остаётся UI override поверх всего автоматического порядка.

**Почему:** lexicographic сортировка делала реальный вклад факторов непрозрачным: было трудно понять, почему игра выше другой, и трудно безопасно скорректировать относительную силу скидки, риска, wishlist и других сигналов. Пользователь должен видеть на карточке тот же score и те же компоненты, которые реально определяют порядок.

**Настраиваемость:** все веса, штрафы, пороги и таблицы начисления должны жить только в `config/final_ranking_policy.json`. Python читает конфиг и не содержит независимой копии чисел. Изменение веса/порогов должно менять score без переписывания scorer-кода.

**Taste-архитектура:** semantic layer по мере обновления должен сохранять нормализованные price-blind taste factors 0–100, не зависящие от текущих весов. GitHub применяет веса. Поэтому изменение, например, `gameplay_mastery 18 → 15`, не требует повторной AI-оценки уже детализированной игры. Старые записи без factor vector временно используют явно видимый `legacy_coarse_fit`, чтобы не изображать точность, которой в старом cache нет.

**Не делать:** не добавлять декоративный score поверх другой скрытой сортировки; не дублировать веса в Python/JS; не пересчитывать semantic taste только из-за изменения веса.

**Основные места:** `config/final_ranking_policy.json`, `scripts/priority_ranking.py`, `scripts/validate_priority_ranking.py`, `web/app.js`.

---

## RANK-011 — Скидочную выгоду считать по рублям экономии, а не по проценту скидки

**Дата:** 2026-08-30
**Статус:** implemented in scorer/config; regression added, production rebuild pending

**Решение:** компонент выгодности акции считает `savings_rub = max(0, original_price_rub - current_price_rub)`. `discount_percent` остаётся только отображением/контекстом и сам по себе не добавляет score. Стартовый максимум компонента экономии — 20 баллов; все рублёвые диапазоны задаются только в policy-конфиге.

**Почему:** одинаковый процент не означает одинаковую экономическую выгоду. Скидка 50% на игру 60 ₽ экономит всего 30 ₽, а 50% на игру 6000 ₽ экономит 3000 ₽. Давать им одинаковый вклад в рейтинг искажает ценность акции.

**Граница:** текущая цена остаётся отдельным компонентом (`до 12`), поэтому абсолютная экономия не означает, что дорогая после скидки игра автоматически становится хорошей покупкой. Eligibility/budget gates применяются до score и не обходятся большой экономией.

**Регрессия:** 60→30 ₽ при 50% получает 0/20 по текущей стартовой таблице, 6000→3000 ₽ при тех же 50% — 19/20; изменение одного только `discount_percent` при одинаковых старой/новой ценах не меняет V2 score.

**Основные места:** `config/final_ranking_policy.json -> score_model.purchase.savings`, `scripts/priority_ranking.py`, `scripts/validate_priority_ranking.py`, `web/app.js`.

---
## RANK-012 — Достижения значительно важнее для уже сыгранной игры

**Дата:** 2026-08-31
**Статус:** implemented in scorer/config; regression verified; production payload rebuilt

**Решение:** achievement-компонент зависит от подтверждённого предыдущего опыта с игрой. Текущий канонический сигнал `played confirmed` — наличие числовой `direct_user_evidence.rating`, то есть точной пользовательской оценки из привязанного игрового профиля. Для новой или не подтверждённо сыгранной игры достижения остаются небольшим бонусом: максимум `+1.5`. Для уже сыгранной игры качественный набор может дать до `+3`, но слабый набор становится причиной не возвращаться: качество `2/5 → −2`, `1/5 → −4`, отсутствие Steam Achievements → `−6`. Если статус/качество достижений неизвестны, неизвестность сама по себе не штрафуется.

**Почему:** у новой игры достижения — дополнительная приятная причина купить её, но сама игра ещё даёт основную ценность. У уже пройденной/сыгранной игры ачивки могут стать отдельной причиной вернуться и перепройти иначе. Если такой причины нет или набор почти полностью автоматический/неинтересный, ценность повторной покупки заметно ниже.

**Граница:** отсутствие ачивок не становится отдельным risk-штрафом поверх achievement-компонента; `no_steam_achievements` по-прежнему исключён из общего risk-score, чтобы не считать один и тот же минус дважды. Неизвестные achievement-данные не приравниваются к отсутствию.

**Почему числовая прямая оценка используется как played-signal:** это уже канонический привязанный пользовательский факт, который production получает до финального score. Он не создаёт нового источника состояния и не требует отдельного «played cache». Если позже появится более прямой канонический completed/played state, policy может перейти на него без изменения самой идеи правила.

**Регрессия:** новая игра с лучшим набором ачивок получает `+1.5`, новая без ачивок — `0`; уже сыгранная с качеством `5/5` получает `+3`, с `2/5` — `−2`, с `1/5` — `−4`, без Steam Achievements — `−6`. Разница между уже сыгранной игрой с лучшим набором и без ачивок составляет 9 баллов при одинаковых остальных условиях.

**Основные места:** `config/final_ranking_policy.json -> score_model.personal.achievements`, `scripts/priority_ranking.py`, `scripts/validate_priority_ranking.py`.

---

## UI-001 — «В конец очереди» абсолютнее любой автоматической сортировки

**Дата:** 2026-08-30
**Статус:** implemented; existing behavior regression protected

**Решение:** явное локальное действие пользователя `В конец очереди` всегда накладывается поверх production `priority_rank`. Даже игра со скидкой, заканчивающейся сегодня, остаётся в конце, если пользователь её туда отправил.

**Почему:** явное пользовательское решение важнее любой автоматической эвристики. Production должен сохранять чистый канонический исходный порядок, а локальное состояние интерфейса — персональное управление уже этой очередью.

**Не делать:** не записывать `manual_end_at` в production ranking и не позволять новому суточному payload автоматически отменять локальное перемещение.

**Основные места:** `web/app.js` (`manual_end_at`, `canonicalQueueIds`, `sendCurrentToEnd`), `PROJECT_RULES.md`, `scripts/validate_priority_ranking.py`.

---

## STEAMDB-001 — Полный scope должен завершаться целиком, но это не то же самое, что запрещать partial persistence

**Дата:** 2026-08-30
**Статус:** rationale recovered; current implementation over-blocking confirmed; replacement behavior not yet approved

**Исходное решение:** весь GitHub-подготовленный набор SteamDB true misses для текущего production cycle должен считаться одной стадией. Размер внешнего batch/checkpoint — только техническая деталь и никогда не означает суточную квоту или завершение стадии. Partial subset нельзя объявлять готовым completed artifact.

**Почему это было введено:** прежняя архитектура рисковала превратить ограниченный runtime batch в фактическое правило «сегодня обработали N, остальное завтра». Это противоречило требованию пользователя, что один суточный production должен пытаться закрыть весь актуальный scope, а GitHub — владеть scope, retry-state и completeness. Поэтому `config/steamdb_lookup_contract.json` намеренно требует `must_complete_all_required_stage_15_items_for_the_current_prepared_artifact` и запрещает считать partial subset завершённым.

**Что произошло при реализации:** `scripts/ingest_steamdb_runtime_submissions.py` выпускает `data/cache/steamdb_web_resolutions.json` только при `status == complete`, а checkpoint в `steamdb_history.json` требует полный stage-16 validation. В результате правильное правило «529/534 не означает, что стадия завершена» фактически превратилось в более сильное правило «529 уже подтверждённых результатов нельзя persist/checkpoint до завершения оставшихся 5».

**Почему это важно различать:** завершённость стадии и сохранение уже проверенных фактов — разные свойства. Можно сохранить 529 подтверждённых фактов, продолжать считать stage incomplete и держать 5 ключей в retry. Запрет partial persistence не был исходной целью правила против daily quota.

**Текущее проявление:** current runtime state содержит 529 resolved из 534 и ровно 5 unresolved (`App_1282200`, `App_225320`, `App_399670`, `App_630060`, `App_901735`). Все пять имеют по одному сохранённому transient failure `runtime_web_internal_error`, пришедшему из one-time recovery migration старого `steamdb_runtime_progress.json`. Это классифицированные transport/tool failures, а не подтверждение отсутствия исторической цены SteamDB. Нет сохранённого доказательства, что эти пять являются постоянными semantic/data failures или имеют одну общую проблему SteamDB.

**Важная граница доказательств:** 529 resolved тоже были перенесены recovery migration. Наличие этих данных доказывает сохранённый прогресс прежнего runtime, но само по себе не доказывает, что новый GitHub → external runtime → GitHub handoff уже успешно выполнял свежий retry. Поэтому перед архитектурным изменением или ручными выводами про пять ключей нужно проверить именно текущий runtime handoff; интерактивный чат не должен заменять его ручным lookup backlog.

**Сознательно не решено пока:** менять ли контракт на verified partial checkpoint + incomplete retry state. Это отдельное архитектурное решение пользователя. До согласования не ослаблять completeness молча.

**Основные места:** `config/steamdb_lookup_contract.json`, `scripts/ingest_steamdb_runtime_submissions.py`, `scripts/validate_steamdb_runtime_resolutions.py`, `config/steamdb_checkpoint_contract.json`, `data/cache/steamdb_runtime_state.json`, `data/cache/steamdb_runtime_work.json`, `data/inbox/steamdb_runtime/recovery-migration-11ac4563c927.json`.

---

## CHAT-001 — Процедурные правила чата должны работать как короткий обязательный gate

**Дата:** 2026-09-01
**Статус:** implemented; cold-start verification pending

**Решение:** обязательные правила поведения интерактивного чата вынесены в отдельный корневой `CHAT_PROTOCOL.md` с тремя явными gates: `START`, `DURING`, `PRE-SEND`. Новый чат обязан читать его **до** `CHAT_CONTEXT.md`, а перед каждым пользовательским ответом проходить релевантный `PRE-SEND`; перед финальным ответом по подзадаче — весь gate.

**Почему:** существовавшее правило «если ответ занял больше минуты — объяснить задержку и способ ускорения» было найдено и прочитано ассистентом в `README.md`/`CHAT_CONTEXT.md`, но затем всё равно не было применено в ответе. Это показало, что простое наличие и даже дублирование правила в длинных документах не гарантирует его попадание в рабочее внимание непосредственно перед отправкой ответа.

**Сознательно отвергнуто:** просто продублировать правило ещё раз в README/CHAT_CONTEXT или создать фиктивный JSON/CI-validator, который создавал бы впечатление технической гарантии. GitHub не может фактически заблокировать отправку ChatGPT-ответа, поэтому правильная модель — короткий явный procedural gate с честно указанной границей гарантии.

**Структурное следствие:** `CHAT_CONTEXT.md` остаётся картой источников истины, ownership и context budget; `README.md` является короткой точкой входа; процедурные правила не должны независимо размножаться между ними. Если обязательная процедура меняется — править `CHAT_PROTOCOL.md`, а не добавлять ещё одну расходящуюся копию.

**Проверка:** основная acceptance-проверка должна выполняться из нового чата/cold start, чтобы исключить помощь памяти текущей сессии. Новый чат получает только указание найти репозиторий и выполнить небольшую задачу; успешным считается самостоятельное чтение `CHAT_PROTOCOL.md`, соблюдение стартового маршрута и проявление соответствующего PRE-SEND поведения при специально созданном trigger-case.

**Основные места:** `CHAT_PROTOCOL.md`, `README.md`, `CHAT_CONTEXT.md`, `PROJECT_DECISIONS.md`.

---

## TASTE-001 — Evidence confidence is not the fit verdict

**Дата:** 2026-09-05
**Статус:** implemented as internal Taste step 1; independent Taste Review required before material product acceptance.

**Решение:** binary `INCLUDE/EXCLUDE` and `strong/moderate/below_moderate` remain compatibility fit/eligibility semantics, while a separately bound price-blind evidence layer distinguishes `sufficient`, `insufficient`, `reconsiderable`, and `confirmed_negative`.

**Почему:** lack of evidence, an old shallow failed attempt, and a current informed rejection have different meaning. Collapsing them into `below_moderate` made uncertainty look like dislike and could turn old non-engagement into a permanent veto.

**Граница:** price, discount, wishlist and bundle value never manufacture or change evidence state. Recurring public complaints may establish candidate-quality risk but stay `personal_relevance=unresolved`; a strong personal-negative finding requires candidate-specific personal/title evidence. `confirmed_negative` remains non-overridable by paid commercial value.

**Миграция:** existing exact fit bindings remain reusable. Safe legacy cases receive compatibility evidence states; ambiguous legacy direct-conflict/audited-below and risk-bearing include rows are backfilled through the existing `resolve_grounded_negative_analysis` work path. Until exact V5 backfill, legacy personal-risk scoring remains fail-safe so real negatives are not silently erased.

**Не делать:** не use evidence state as wishlist override, play-role/start-priority, discount boost, second ranking formula, or new semantic scheduler.

**Основные места:** `config/taste_result_contract.json`, `config/taste_cache_entry_contract.json`, `scripts/taste_evidence_contract.py`, `scripts/ingest_taste_results.py`, `scripts/build_pre_ai_chatgpt_payload.py`, `scripts/refine_visual_ranking.py`.

---

## TASTE-002 — Play role and start priority are not purchase urgency

**Дата:** 2026-09-05
**Статус:** implemented as internal Taste step 2; combined independent Taste Review remains pending after step 3.
**Решение:** хранить `play_role` и `relative_start_priority` как отдельный producer-owned semantic/context layer поверх price-blind Taste evidence, но вне commercial urgency/value и вне канонического ranker.

**Почему:** scalar fit/score не умеет одновременно выразить `Sifu = main/high`, `High On Life = main/ordinary`, `Tails of Iron 2 = secondary`, `Trine 4 = family/co-op`. Sale deadline отвечает на вопрос «не пропустить ли покупку», а start priority — «насколько скоро запускать среди подходящих игр».

**Граница:** wishlist, цена, скидка, history quality, purchase verdict и sale expiry не разрешают role/start state. Franchise history — только слабый prior; без title-specific evidence состояние остаётся `unresolved`. Step-1 `confirmed_negative` не может получить `high`. `priority_ranking.py` и `config/final_ranking_policy.json` остаются единственной автоматической ranking authority и этой задачей не меняются.

**Основные места:** `config/play_priority_context_contract.json`, `scripts/play_priority_context.py`, `scripts/build_final_visual_payload.py`, `scripts/build_ranking_lookup.py`, `scripts/test_play_priority_context.py`.

---

## TASTE-003 — Commercial signals can reopen eligibility, not Taste

**Дата:** 2026-09-05
**Статус:** implemented as internal Taste step 3; independent combined Taste Review required before final material acceptance.

**Решение:** разрешить только два explicit post-Taste commercial eligibility bridges: `insufficient + Steam wishlist + canonical good deal`, а также `reconsiderable + existing fixed-package strict current-price savings`.

**Инвариант:** bridge не повышает `fit_level`, не меняет `fit_evidence_state`, не переписывает `play_role`/`relative_start_priority`, не стирает риски и не создаёт новый ranking score. Exact V5 `confirmed_negative` / direct confirmed conflict fail closed и не спасаются коммерческими сигналами. Сам по себе legacy `reason_code=exclude_direct_conflict` не равен V5-confirmation: без V5 binding он остаётся fail-closed, а при exact V5 `reconsiderable` не блокирует bounded package bridge.

**Good deal:** только существующий `decision_if_moderate.final_disposition=INCLUDE` + `purchase_decision=БРАТЬ СЕЙЧАС`; новый discount threshold не вводится.

**Package:** используется существующий fixed-Sub deterministic economics / exact-or-verified purchase equivalence / `strict_current_price_savings`; personalized Complete-the-Set и fuzzy equivalence по-прежнему запрещены. Package value может использовать уже `reconsiderable`, но не создаёт это состояние.

**Основные места:** `config/mailing_policy.json`, `config/deal_quality_contract.json`, `scripts/commercial_reconsideration_bridge.py`, `scripts/build_pre_ai_chatgpt_payload.py`, `scripts/build_visual_feed_v2.py`, `scripts/test_reconsideration_commercial_bridge.py`.

---

## TASTE-004 — Steam review dossier backlog is broader than the active Taste pin; checkpoint size is not a quota

**Дата:** 2026-09-13
**Статус:** implementation in progress; ownership boundary approved by task contract

**Решение:** canonical Steam review dossier preparation scope is the full current eligible Taste backlog derived by GitHub from `data/production/pre_ai/chatgpt_taste_queue.jsonl`, deduplicated by Steam `appid` in canonical queue order. The bounded active Taste pin remains downstream semantic-work authority only and must not define total dossier-preparation scope. A checkpoint of 10 dossiers is only a bounded submission/persistence unit: after a successful checkpoint GitHub must rebuild remaining work and the same scheduled invocation continues to the next checkpoint until the full eligible dossier backlog is exhausted or a real platform/tool/runtime limit interrupts the run.

**Почему:** the first production population proved that reusing the active exact-10 Taste pin as dossier scope can make the preparer stop after 10 even when more eligible games still need dossiers. Conversely, removing the bound entirely would force one large all-or-nothing submission and would lose durable progress if a later part of a long run fails. Full-scope completeness and bounded durable checkpoints are separate concerns: GitHub owns both the total remaining backlog and each exact checkpoint; the checkpoint exists to preserve verified progress, not to create a daily quota.

**Граница:** fresh dossiers remain reusable; missing/stale in-scope dossiers remain work; stale out-of-scope cleanup uses the full eligible dossier scope; base-support-only/non-Taste rows do not enter dossier scope; exact checkpoint submission validation remains fail-closed. `build_taste_semantic_dossier_input.py` continues to bind only the exact active Taste pin and holds if any pinned dossier is missing/stale/invalid. ChatGPT/Scheduled Task may process only GitHub-prepared checkpoints and may not invent queue order, retry/completeness state, or a production batch limit.

**Сознательно отвергнуто:** active pin as total dossier scope; `10` as per-run/daily quota; a single unbounded all-or-nothing submission for the entire backlog; ChatGPT-owned queue/retry/completeness; changing the existing Taste Semantic Producer or its pin authority.

**Основные места:** `config/taste_steam_review_dossier_contract.json`, `scripts/taste_steam_review_dossier.py`, `scripts/build_taste_steam_review_dossier_work.py`, `scripts/ingest_taste_steam_review_dossiers.py`, `scripts/taste_steam_review_dossier_cleanup.py`, `config/taste_steam_review_dossier_worker_prompt.md`.


---

## TASTE-005 — Fixed daily full Steam-review-dossier snapshot

**Дата:** 2026-09-13
**Статус:** implemented by `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_CONTROL_PLANE_REFRESH_01`; supersedes only the checkpoint-rebuild portion of TASTE-004

**Решение:** GitHub один раз в штатном daily/pre-AI path готовит полный фиксированный Steam-review-dossier backlog snapshot из текущей canonical Taste queue. В snapshot входят все missing/stale eligible appids после deterministic dedupe; fresh dossiers переиспользуются. `checkpoint_size=10` — только внутренняя граница durable persistence. После accepted checkpoint GitHub продвигает `remaining_required_items` внутри того же `snapshot_id` и не перечитывает queue/store для перестроения scope.

**Почему:** прежняя модель `persist checkpoint -> rebuild current scope from current queue/store` позволяла scope меняться посреди одного запуска и делала manual Run now зависимым от свежести/момента rebuild. Это противоречит требованию иметь один полный дневной production scope и делает checkpoint технической квотой вместо durability boundary.

**Resume / Run now:** interruption сохраняет принятые checkpoints; следующий invocation продолжает только remaining того же последнего prepared daily snapshot. Manual `Run now` читает последний опубликованный daily snapshot и не запускает on-demand refresh. Изменения canonical queue после daily preparation попадают только в следующий daily snapshot. Empty snapshot является валидным complete state.

**Граница:** TASTE-004 сохраняется в части `full eligible Taste backlog > active semantic pin` и `10 is not a quota`, но его фраза о rebuild после checkpoint считается superseded этим решением. Downstream `taste_active_work_unit.json` и существующий Taste Semantic Producer этой задачей не меняются.

**Основные места:** `config/taste_steam_review_dossier_contract.json`, `scripts/taste_steam_review_dossier_daily.py`, `scripts/build_taste_steam_review_dossier_work.py`, `scripts/ingest_taste_steam_review_dossiers.py`, `config/taste_steam_review_dossier_worker_prompt.md`, `.github/workflows/build-pre-ai-store-snapshot.yml`.

---

## TASTE-006 — Buffered dossier transport preserves GitHub canonical ownership

**Дата:** 2026-09-14
**Статус:** contract approved; runtime not activated

**Решение:** для уже фиксированного daily Steam-review-dossier snapshot GitHub заранее определяет неизменяемый ordered group plan поверх `prepared_required_items[]`, обычно группами по `checkpoint_size=10`. Каждая группа получает стабильную identity, включающую `snapshot_id`, `prepared_required_sha256`, `sequence`, диапазон индексов, точные ordered items/appids, `items_sha256`, `group_sha256` и provenance bindings. После успешного create-only сохранения группы N scheduled ChatGPT в будущем buffered mode может сразу обработать только следующую заранее объявленную группу N+1, не ожидая canonical ingest N.

**Почему:** текущий fixed-snapshot contract уже математически определяет весь дневной порядок, но current-checkpoint transport заставляет worker ждать GitHub ingest и manifest advancement после каждой десятки. Immutable per-group transport снимает этот round-trip, не передавая worker-у контроль над scope, retry или canonical progress.

**Buffer / drain:** каждая группа сохраняется отдельным immutable create-only transport artifact; несколько групп одного snapshot могут одновременно ожидать ingest. Buffer не является canonical progress, retry state, очередью ChatGPT или completeness authority. GitHub drain начинает с canonical `expected_sequence`, принимает только maximal valid contiguous prefix и не перескакивает gap. Missing, malformed, stale/wrong-snapshot, reordered, out-of-scope или иначе invalid expected group блокирует последующие группы; replay уже принятой группы не может повторно двигать canonical state. Cleanup принадлежит только GitHub.

**Canonical writer:** все GitHub-процессы, способные менять dossier canonical manifest, обязаны участвовать в одном serialized canonical-writer boundary. Buffer push — только wake-up signal; конкретная workflow/concurrency реализация относится к отдельному IMPLEMENT task.

**Transition:** решение contract-first и не активирует ещё не реализованный путь. Текущие `TASTE-STEAM-REVIEW-DOSSIER-WORK-V2`, current-checkpoint submission path и действующий worker prompt остаются допустимыми и обязательными до отдельного buffered runtime implementation и Director acceptance. `config/execution_ownership_contract.json` не меняется: GitHub по-прежнему control plane, scheduled ChatGPT — constrained semantic/data worker. `checkpoint_size=10` остаётся durability boundary, а не run/day/production quota.

**Миграция текущего snapshot:** будущий IMPLEMENT может сохранить существующий `snapshot_id` и уже принятый progress без rebuild scope, только если group plan строго выводится из существующего `prepared_required_items[]`, а `remaining_required_items[]` доказан как точный suffix после accepted prefix. Уже принятые группы не создаются и не ingest повторно; продолжение начинается с первой непринятой группы. Если точный prefix/suffix или group-boundary proof невозможен — migration fail closed.

**Сознательно отвергнуто:** mutable shared buffer, alternate retry filenames, ChatGPT-owned queue/retry/backlog/completeness, gap skipping, applying stale old-snapshot artifacts to a new snapshot, prompt-only activation before runtime support, изменение Taste Semantic Producer.

**Основные места:** `config/taste_steam_review_dossier_contract.json`, `config/taste_steam_review_dossier_persistence_bridge.json`, `reviews/worker_reports/taste-dossier-buffered-submission-recon-01.md`.

---

## TASTE-007 — Production dossier evidence uses multi-source player-feedback web research

**Дата:** 2026-09-15
**Статус:** approved architecture; implementation prepared and CI-green in PR #30; production activation blocked by current task scope

**Решение:** production Taste dossier evidence больше не требует Steam `appreviews` как обязательного корпуса, cursor continuation или фиксированных review-count lanes. Semantic worker выполняет обычный bounded multi-source web research по отзывам и обсуждениям игроков. Идентичность игры сначала связывается с точным work-item title + release year; при неоднозначности добавляются developer/publisher/platform/version/Steam appid или другой канонический corroborator. Нельзя смешивать оригинал, remake, remaster, re-release или одноимённые разные игры.

**Временная семантика:** свежие player-feedback источники имеют приоритет для bugs/performance/compatibility/technical/localization/regional current-state claims. Launch-era проблема, которую свежие данные показывают исправленной или существенно ослабленной, должна сохраняться как `historical`, а не как текущий recurring defect. Старые отзывы остаются допустимыми для durable traits: gameplay, story, pacing, structure, progression, repetition, difficulty и persistent friction. При неразрешённом временном конфликте состояние остаётся `uncertain`.

**Русский evidence:** для каждой игры обязателен отдельный добросовестный поиск русскоязычных мнений, особенно по localization/translation/voice/font/encoding/regional-service проблемам. Допустимы состояния `found_and_used`, `searched_not_found_or_insufficient`, `source_access_unavailable`; отсутствие русского evidence нельзя компенсировать выдуманными данными.

**Storage / ownership:** raw review/post bodies, quotes, usernames и corpus archive в GitHub не сохраняются; хранится только компактный dossier и компактная provenance metadata. GitHub остаётся control plane для scope/order/progress/validation/persistence/recovery/completeness/buffered drain; Scheduled ChatGPT владеет только semantic web research + synthesis. Buffered group size остаётся transport/durability boundary, не semantic quota. Taste Semantic Producer не меняется.

**Versioning / migration:** новый semantic contract и dossier shape версионируются отдельно; legacy V1/empty/store-only placeholders не считаются удовлетворяющими новой evidence policy. Fresh legacy dossiers должны быть rebuilt при следующей canonical freshness evaluation, если они не соответствуют новой версии. Текущие invalid buffered g1/g2 не изменяются этой задачей и остаются для отдельной coordinated recovery + acceptance.

**Сознательно отвергнуто:** обязательный direct Steam appreviews transport; fixed 20/40/80 review sampling quotas; GitHub-prefetched raw review bodies; ChatGPT-owned queue/retry/backlog manager; перенос personal recommendation в neutral dossier; изменение Taste Semantic Producer.

**Текущий blocker:** PR #30 не мержится в этой задаче, потому что merge путей dossier runtime/config автоматически запускает production pre-AI workflow, а текущая task production run не разрешает.

**Основные места:** `config/taste_steam_review_dossier_web_evidence_contract.json`, `config/taste_steam_review_dossier_schema.json`, `config/taste_steam_review_dossier_worker_prompt.md`, `scripts/taste_steam_review_dossier_strict.py`, `scripts/taste_steam_review_dossier_web.py`, PR #30, `reviews/worker_reports/taste-dossier-web-evidence-redesign-01.md`.

---

## TASTE-008 — Russian existence proof creates an item-level retrieval gate

**Дата:** 2026-09-18
**Статус:** implemented by `WORKER_TASK_TASTE_DOSSIER_RUSSIAN_EXISTENCE_RETRIEVAL_GATE_IMPLEMENT_01.md`.

**Решение:** отдельный поиск русскоязычного player feedback остаётся обязательным, потому что релевантность для русскоязычного пользователя является частью evidence-задачи. При этом exact-product **existence proof** и contract-usable attributable item-level feedback — разные уровни доказательства. `evidence.russian_attempt` является единственным machine-readable состоянием gate: `found_and_used`, `searched_no_existence_signal`, `existence_established_retrieval_unresolved`, `existence_established_access_unresolved`.

**Почему:** bounded audit показал два разных случая, которые прежний `searched_not_found_or_insufficient` смешивал. Для Tetris® Effect: Connected usable Russian item был нормально discoverable через exact appid/title + Russian term + Steam Community; для BG3 Digital Deluxe DLC и Hellish Quart exact-product surfaces доказывали Russian review activity, но usable item-level provenance в bounds не был получен. Поэтому доказанное существование + неудача item retrieval — discovery/retrieval defect и должно fail closed, а не изображать отсутствие русских отзывов.

**Граница:** `searched_no_existence_signal` допустим только когда bounded good-faith search не установил надёжный exact-product player-activity existence signal. Existence aggregate/list/community signal сам не является player-feedback record, не поддерживает observation/conflict, не создаёт mention_count/recurrence и не удовлетворяет `found_and_used`. Russian-rendered UI без player activity не является existence proof. Профессиональный/журналистский русский материал может быть context/relevance evidence, но не заменяет player feedback и не закрывает retrieval gate.

**Discovery:** fixed website quota и Steam-only requirement не вводятся. Используются exact title + release year/appid, Russian-language variants и, если attempt ещё не разрешён и budget остаётся, релевантный site-specific player-feedback/community search. После existence signal оставшийся bounded search направляется на attributable item-level retrieval. Hard bounds остаются <=8 search queries и <=16 opened/read pages на игру и являются safety ceilings, не targets.

**Identity / architecture:** base game, DLC, edition, sequel/remaster и другой appid не смешиваются; когда Steam feedback URL явно содержит `/app/{appid}/`, он должен совпадать с exact dossier appid. GitHub остаётся control plane и единственным strict validation authority; Scheduled ChatGPT остаётся bounded evidence worker. Новые queue/retry/healing/recurring stages не создаются; group size 3 и buffered maximal-contiguous-prefix architecture не меняются.

**Дополнение — source-agnostic retrieval diversification (2026-09-18):** existence proof создаёт не Steam-обязанность, а source-agnostic obligation получить contract-usable item-level Russian/mixed player feedback в пределах уже существующего bounded budget. Steam aggregate/store/community signal может доказать existence и Steam может быть одним retrieval surface, но usable record разрешено и требуется искать на materially different public player-feedback surface classes, когда первый разумный surface не дал item и budget ещё есть. После первого diversified шага worker продолжает adaptive diversification по наиболее перспективным reasonably discoverable distinct classes до usable item, hard bound или отсутствия иных разумно discoverable distinct classes. Fixed website quota, обязательный обход всех классов и Steam-only retrieval запрещены. Exact-product identity остаётся строгой; professional/editorial material остаётся context-only и не закрывает gate.



**Дополнение — early multi-source ordering (2026-09-19):** после exact-product Russian existence proof Steam остаётся предпочтительным дешёвым item-level путём, если usable concrete Russian/mixed item уже доступен или непосредственно достижим. Но aggregate/count-only, недоступный language-filter representation, profile-scoped hit, только non-Russian concrete cards либо collection/index row без concrete child считаются семантическими stop-shape для приоритета Steam: при оставшемся budget worker должен рано перейти к generic non-site-constrained cross-source discovery по exact title + release year (когда полезно) + русским player-review/discussion формулировкам, а site-specific follow-up делать только после того, как discovery показал перспективный источник. Фиксированного числа Steam queries/pages нет; это ordering/prioritization, а не изменение evidence semantics. Причина — MO:Astray доказал, что usable exact-product Russian player-feedback может быть дешёво доступен вне Steam, тогда как последовательные equivalent Steam retrieval attempts способны израсходовать bounded budget до этого pivot.

**Основные места:** `config/taste_steam_review_dossier_schema.json`, `config/taste_steam_review_dossier_web_evidence_contract.json`, `config/taste_steam_review_dossier_worker_prompt.md`, `scripts/taste_steam_review_dossier_strict.py`, `scripts/test_taste_steam_review_dossier_semantic_consistency.py`.



---

## TASTE-009 — Story DLC only in independent Taste/dossier scope

**Дата:** 2026-09-18  
**Статус:** implemented by `WORKER_TASK_TASTE_STORY_DLC_SCOPE_POLICY_IMPLEMENT_01.md`

**Решение:** independent Taste/Steam-review-dossier scope включает add-on/DLC только при положительном подтверждении существенного playable narrative content из уже канонически полученной Steam product metadata. Non-story bonus content и DLC с недоказанной сюжетностью исключяются до dossier identity projection; неоднозначность fail-closed. Machine states: `story_dlc_eligible`, `non_story_dlc_excluded`, `story_content_unproven_excluded`.

**Почему:** Taste model оценивает meaningful playable products, а не merchandising/digital bonus packs. Dossier research на Digital Deluxe/OST/artbook/cosmetic add-ons расходует evidence budget и создаёт ложную semantic obligation. Для пользовательского recommendation workflow independently meaningful DLC — только сюжетное.

**Граница:** base games не меняются; mixed story+cosmetics остаётся допустимым только при отдельном положительном story evidence; season pass/container не наследует semantic identity дочерних story DLC; package/member aggregation, exact appid identity, pricing/package economics, Russian retrieval/provenance, group size 3 и GitHub control-plane ownership не меняются.

**Regression control:** appid `2378500` (`Baldur's Gate 3 - Digital Deluxe Edition DLC`) должен классифицироваться `non_story_dlc_excluded` и отсутствовать в required dossier group plan.

**Основные места:** `config/taste_steam_review_dossier_contract.json`, `scripts/taste_steam_review_dossier_web.py`, `scripts/build_taste_steam_review_dossier_work.py`, `scripts/test_taste_story_dlc_scope.py`, `.github/workflows/validate-taste-dossier-buffered.yml`, `.github/workflows/build-pre-ai-store-snapshot.yml`.

---

## TASTE-010 — Transient author identity may dedupe concrete feedback when neutral item identity is unavailable

**Дата:** 2026-09-18  
**Статус:** implemented by `WORKER_TASK_TASTE_DOSSIER_TRANSIENT_AUTHOR_DEDUPE_FALLBACK_IMPLEMENT_01.md`.

**Решение:** neutral stable item locator остаётся предпочтительной и более сильной identity. Если конкретный exact-product player-feedback item реально виден и инспектирован, но acceptable neutral item locator получить нельзя, Scheduled worker может временно прочитать stable author/account/profile identity только в памяти текущего запуска для dedupe. После dedupe сохраняется только dossier-local `transient_author_deduped` record без item/profile URL, username, SteamID/account/vanity id, profile identity, прямого hash или предсказуемого pseudonym. Author identity не получает persistent registry и не заявляется как cross-run identity.

**Почему:** strict/open diagnostics для Crown Trick и Hellish Quart показали реальные конкретные русскоязычные review cards, которые прежняя модель выбрасывала только из-за отсутствия доступного neutral recommendation/item id. Сохранение profile URL решало бы locator-проблему ценой ухудшения privacy, а прямой hash публичного SteamID/username не является надёжной анонимизацией из-за enumerability/re-identification. Transient dedupe использует достаточный сигнал для разделения видимых карточек, но не переносит reviewer identity в GitHub.

**Evidence strength:** fallback records считаются реальными player-feedback mentions, но из-за отсутствия независимо переоткрываемого item locator имеют сниженный auditability. `limited` может опираться на >=2 total bound records; `moderate` требует >=3 bound `stable_locator` records; `strong` требует >=5 bound `stable_locator` records. Поэтому fallback-only evidence всегда максимум `limited`; в mixed set fallback увеличивает `mention_count` и может помочь только до `limited`, но не входит в stable threshold для `moderate/strong`.

**Граница:** aggregate/list/count surface без конкретно инспектированного item по-прежнему не является feedback record. Exact appid/product identity остаётся fail-closed. Story-DLC policy `story-dlc-positive-evidence-v1`, group size 3, buffered maximal-contiguous-prefix architecture, GitHub control-plane ownership, source-agnostic Russian discovery и hard 8/16 bounds не меняются. Валидный Russian/mixed fallback может закрыть `russian_attempt=found_and_used`.

**Дополнение — Steam Store parent collection (2026-09-18):** exact-app Steam Store page остаётся storefront/aggregate provenance и сама не является feedback item, mention или stable item locator. Но если на ней реально видны и инспектированы конкретные individual review cards, страница может быть parent collection surface для `transient_author_deduped` child records через `feedback_surface_mode:"concrete_item_collection"`. Aggregate counts, percent positive, rating, language totals и review-summary block остаются non-evidence/non-mention metadata и сами не закрывают `found_and_used`. Source-level `player_feedback:true` для такого parent означает наличие инспектированных player-feedback children, а не превращает Store URL в отзыв. Stable neutral locator по-прежнему предпочтителен; privacy, no-direct-hash и recurrence caps TASTE-010 не меняются.

**Основные места:** `config/taste_steam_review_dossier_schema.json`, `config/taste_steam_review_dossier_web_evidence_contract.json`, `config/taste_steam_review_dossier_worker_prompt.md`, `scripts/taste_steam_review_dossier_strict.py`, `scripts/test_taste_dossier_transient_author_fallback.py`.


---

## TASTE-011 — Dossier stable-child binding, local join IDs and exact language projection are strict acceptance invariants

**Дата:** 2026-09-18  
**Статус:** implemented by `WORKER_TASK_TASTE_DOSSIER_CONTRACT_CONTRADICTIONS_FIX_01.md`.

**Решение:** canonical strict acceptance enforces three previously worker-facing invariants end to end. First, a stable Steam child whose URL/public reference deterministically exposes an appid must match the exact dossier appid; when both Steam parent and child expose a deterministic discussion/container/thread identity, the shared resolvable identity components must match physically, not merely by host or broad surface class. Second, every persisted `source_id` and stable `feedback_id` is an author-independent dossier-local sequence key (`source-NNN`, `feedback-NNN`); fallback retains its independent `fallback-NNN` sequence. Stable physical item identity remains only in the validated safe URL/`public_ref`, never in an internal join key. Third, observation `evidence_languages` must exactly equal the canonical ordered distinct projection of its final bound feedback-record languages: `russian`, then `non_russian`, then `unknown`; record-level `mixed` expands to `russian + non_russian` and is never an observation-summary token.

**Почему:** the prior contracts already required exact-product/physical-parent binding, no persisted reviewer identity, and deterministic language derivation, but strict acceptance enforced only weaker subsets. That left silent wrong-product/container evidence, a privacy leak through arbitrary internal IDs, and stale/non-canonical language summaries structurally acceptable.

**Граница:** the accepted Steam Store exact-app concrete-card parent exception remains fallback-only and unchanged; `transient_author_deduped` records still persist no child item/profile locator or author identity and retain the same reduced recurrence semantics. Unknown/unresolvable Steam identity is not guessed. Story-DLC, source-agnostic Russian discovery, group size 3, buffered maximal-contiguous-prefix publication, retry/recovery, ranking/pricing/package/UI and GitHub control-plane ownership do not change.

**Основные места:** `config/taste_steam_review_dossier_schema.json`, `config/taste_steam_review_dossier_web_evidence_contract.json`, `config/taste_steam_review_dossier_worker_prompt.md`, `scripts/taste_steam_review_dossier_strict.py`, `scripts/taste_steam_review_dossier_compact_provenance.py`, `scripts/test_taste_dossier_contract_contradictions_fix.py`.


---

## TASTE-012 — Temporal completeness is a pre-stop retrieval gate

**Дата:** 2026-09-19  
**Статус:** implementation governed by `WORKER_TASK_TASTE_DOSSIER_TEMPORAL_PRESTOP_RETRIEVAL_GATE_IMPLEMENT_01.md`; final activation status is recorded in its durable worker report.

**Решение:** для current-state-sensitive dossier observations (bugs, performance, compatibility, technical state, localization, regional/service state) уже существующая temporal evidence semantics проверяется **до** решения `research_state:sufficient` / `stop_reason:evidence_stable`. Draft `historical` observation без bound `historical` evidence + <=365-day `current_state/recent` source не может остановить research, пока остаётся bounded budget. Worker продолжает exact-product recent retrieval с уже активной early multi-source diversification, затем заново выбирает существующий `historical/current/uncertain` state. Durable traits не затягиваются этим gate.

**Почему:** immutable `593378be…/g000002` по `60 Seconds! Reatomized` показал не validator gap, а более раннюю stopping ошибку: worker нашёл 2019 technical complaint, пометил её `historical` и остановился до обязательного recent current-state check. Strict validator уже корректно отверг candidate. Bounded diagnostic/live retrieval показывает, что recent exact-product technical player feedback доступен внутри существующего 8-search / 16-page ceiling, поэтому исправлять нужно pre-stop retrieval ordering, а не evidence meanings или validator strictness.

**Граница:** meanings `historical/current/durable/uncertain`, <=365-day recency, source admissibility, privacy/provenance/language, exact-product identity, strict validator, 8/16 bounds, group size, buffered transport и GitHub ownership не меняются. Не создаются queue, scheduler, retry daemon, fixed website quota или Steam-only lane. Старый immutable `g000002` не ремонтируется и не переиздаётся; prompt binding change активируется только normal GitHub-owned compatible snapshot rebuild.

**Основные места:** `config/taste_steam_review_dossier_worker_prompt.md`, `config/taste_steam_review_dossier_web_evidence_contract.json#worker_prompt_revision`, `scripts/test_taste_steam_review_dossier_semantic_consistency.py`, `scripts/taste_steam_review_dossier_strict.py` (authority unchanged).
---

## PPD-001 — Progressive personalized publication is tier-first and no longer waits for semantic closure

**Дата:** 2026-09-20  
**Статус:** approved for Phase A implementation

**Решение:** текущий deterministic-eligible каталог публикуется до закрытия semantic queue. GitHub канонически проецирует четыре состояния: `analyzed_fit`, `analysis_incomplete`, `not_analyzed`, `analyzed_not_fit`. Видимый автоматический порядок строго tier-first: fit → incomplete/error → not analyzed; not-fit скрывается из обычного списка, но учитывается в processing counts. `analysis_in_progress` не является durable state.

**Почему:** глобальное ожидание Taste/Dossier делало одну незавершённую semantic цепочку блокером всего продукта. При этом показ неразобранной игры не требует притворяться, что она персонально рекомендована. Явный analysis tier сохраняет персонализированную природу продукта и честность данных одновременно.

**Не делать:** не присваивать Tier 2/3 фиктивный `total_score`; не скрывать игру из-за отсутствия evidence; не превращать `insufficient` из-за нехватки информации в завершённый not-fit; не переносить state/count/retry ownership из GitHub в browser или ChatGPT.

**Граница Phase A:** PASS 1/PASS 2 execution, retry/recovery и изменение Scheduled ChatGPT не входят в это решение. Для Phase A активируется только state projection, publication, ordering и site progress visibility.

**Основные места:** `config/progressive_personalization_contract.json`, `config/daily_execution_contract.json`, `config/mailing_policy.json`, `config/final_ranking_policy.json`, visual producer и read-only UI.


---

## PPD-002 — PASS 1 is item-level, one-shot per semantic binding, and coverage-first

**Дата:** 2026-09-21  
**Статус:** approved for Phase B implementation

**Решение:** Phase B использует GitHub-owned item-level PASS 1 поверх Phase A progressive publication. Каждый current `not_analyzed` item получает не более одной PASS 1 попытки для текущей semantic/item binding. Валидный результат независимо переходит в `analyzed_fit`, `analyzed_not_fit` или `analysis_incomplete`. Недостаток evidence, invalid exact-bound semantic result и caught per-item worker failure не превращаются в not-fit и не блокируют следующие items.

**Почему:** group/maximal-prefix acceptance превращает один сложный item в head-of-line blocker и противоречит цели coverage-first. Phase A уже доказала, что unresolved каталог можно честно публиковать, поэтому semantic progress должен быть incremental и независимым от полного закрытия backlog.

**Transport:** canonical PASS 1 progress — item-level. Worker может обработать несколько последовательных items за invocation, но каждый результат создаётся отдельным immutable create-only artifact с exact GitHub work identity. Batch atomicity и maximal contiguous prefix не являются authority PASS 1.

**Evidence:** compatible-cache — fast path. Новый PASS 1 использует lightweight candidate-specific evidence; Dossier, Russian Steam review, exhaustive multi-source research и deep recovery не являются обязательными. `insufficient_evidence` => `analysis_incomplete`. Retry/deep recovery принадлежит будущему PASS 2.

**Generation:** commercial price/source timestamp не входит в semantic generation identity и сам по себе не сбрасывает attempt. Profile/model/semantics/context-contract change создаёт новый global generation; fingerprint/context change создаёт новый item work identity только для затронутого item.

**Граница:** GitHub остаётся control plane; Scheduled ChatGPT — bounded semantic data plane; browser — read-only. PASS 2 не активирован. Phase A current catalogue остаётся fallback и публикация не ждёт PASS 1 completion.

**Основные места:** `config/progressive_pass1_contract.json`, `config/progressive_personalization_contract.json`, `scripts/progressive_pass1.py`, `scripts/build_progressive_pass1_work.py`, `scripts/ingest_progressive_pass1.py`, `.github/workflows/ingest-progressive-pass1.yml`.


---

## PPD-003 — PASS 2 is dossier-ready per item and independent from global PASS 1 completion

**Дата:** 2026-09-21  
**Статус:** superseded before production activation by PPD-004; retained as historical rationale for the dossier-ready and no-global-wait parts only

**Решение:** глобальный барьер `not_analyzed_count == 0` для старта PASS 2 отменён. PASS 1 и будущий PASS 2 являются независимыми GitHub-owned потоками: PASS 1 продолжает брать только текущие `not_analyzed` items, а PASS 2 может рассматривать только уже текущие `analysis_incomplete` items. Ни один pass не ждёт завершения другого и не блокирует его.

Конкретный `analysis_incomplete` item становится PASS 2 eligible только после того, как GitHub канонически принял и сохранил **current exact-compatible** Taste Steam Review Dossier для того же app/work identity. Буферный candidate, stale/expired dossier, wrong-app/wrong-work/cross-release dossier или dossier со старой/mismatched content-complete evidence binding не открывает PASS 2.

**Attempt budget:** ожидание Dossier, сама eligibility projection и нахождение в будущей recovery queue расходуют **0** PASS 2 attempts. Для одного текущего `semantic_generation_id + work_id` разрешена максимум одна автоматическая PASS 2 recovery attempt. Новый/обновлённый dossier сам по себе не сбрасывает этот budget. После израсходованной неуспешной попытки item остаётся видимым `analysis_incomplete` Tier 2 и выходит из automatic recovery до смены semantic generation/work identity по существующим правилам.

**Ownership:** GitHub владеет dossier acceptance truth, PASS 2 eligibility, scope/order, immutable binding, state и attempt accounting. Scheduled ChatGPT может получить только уже подготовленную eligible work unit. Dossier worker не может напрямую поставить item в PASS 2 queue. Canonical Dossier acceptance должна автоматически стать входом для GitHub eligibility recomputation без interactive intervention.

**Почему:** глубокая recovery без принятого exact-compatible Dossier повторяет лёгкую/случайную оценку и не даёт PASS 2 нового подтверждённого основания. Одновременно ожидание полного PASS 1 искусственно задерживает recovery уже готовых incomplete items. Per-item dossier-ready gate сохраняет bounded recovery и позволяет обоим pass идти параллельно без starvation и без retry loop.

**Не изменено:** PASS 1 остаётся one-shot coverage path без обязательного Dossier; Dossier evidence/identity/freshness semantics остаются в своих canonical contracts; PASS 2 runtime/scheduler/worker/processor этим решением не активируются.

**Основные места:** `config/progressive_personalization_contract.json#phase_c_pass2_design`, `config/progressive_pass1_contract.json` (PASS 1 unchanged), `config/taste_steam_review_dossier_contract.json`, `config/taste_steam_review_dossier_persistence_bridge.json`.

---

## TASTE-013 — Dossier progress is per-group and non-blocking

**Дата:** 2026-09-22  
**Статус:** implementation governed by `WORKER_TASK_TASTE_DOSSIER_NONBLOCKING_GROUP_PROGRESS_IMPLEMENT_01.md`.

**Решение:** maximal-contiguous-prefix promotion is superseded for normal Taste Dossier progress. GitHub owns one canonical state for every immutable predeclared group: `pending`, `accepted`, or `failed_or_invalid_pending_recovery`. A valid group persists independently even if an earlier different group failed. An invalid group is fail-closed only for its own identity, is quarantined/recorded for separate recovery, and is removed from normal first-pass traversal. Scheduled ChatGPT receives only GitHub's next pending projection and never owns retry, ordering, recovery, completeness, or schedule mutation.

**Completeness:** `normal_first_pass_complete=true` means no `pending` groups remain and may coexist with unresolved failed groups. Existing `full_backlog_complete` is not silently redefined: it retains the stricter all-required/all-accepted meaning. Downstream evidence consumers may use only canonically accepted dossiers; a failed group never counts as accepted evidence.

**Recovery:** failed groups remain visible through a separate GitHub-owned recovery projection. Normal first pass never automatically retries them. Explicit recovery may later reopen an exact same-snapshot failed group only under canonical recovery rules; create-only deterministic transport, exact plan/binding and strict validation remain mandatory.

**Почему:** a single semantically bad group must not become a head-of-line blocker for hundreds of unrelated dossiers. The g000005 incident proved that immutable create-only transport plus contiguous-prefix acceptance could leave canonical progress pinned forever after a correctly rejected artifact, even though later groups were independent work.

**Граница:** group size 3, strict dossier semantic validation, evidence/schema rules, snapshot/plan exactness, stale-snapshot isolation, GitHub control-plane ownership and hourly Scheduled Dossier cadence remain unchanged. No new queue, retry daemon, scheduler, PASS 1/PASS 2 behavior or Taste Semantic Producer behavior is introduced. The Scheduled Dossier worker is explicitly forbidden from enabling, disabling, pausing, deleting, rescheduling or editing its own task.

**Основные места:** `config/taste_steam_review_dossier_contract.json`, `config/taste_steam_review_dossier_persistence_bridge.json`, `config/taste_steam_review_dossier_recovery_contract.json`, `config/execution_ownership_contract.json`, `scripts/taste_steam_review_dossier_group_progress.py`, `scripts/taste_steam_review_dossier_buffered.py`, `scripts/taste_steam_review_dossier_worker_projection.py`, `scripts/taste_steam_review_dossier_recovery.py`, `config/taste_steam_review_dossier_worker_prompt.md`.



## PPD-005 — Deep eligibility recomputation wiring is reusable; old recovery-only predicate is superseded

**Дата:** 2026-09-22  
**Статус:** historical pre-activation record; eligibility premise superseded by PPD-004. The old inactive/runtime-adaptation status is superseded in current production by active `FAST-DOSSIER-DEEP-V1` contracts.

**Решение:** Progressive PASS 2 eligibility is a GitHub-owned derived projection, not a queue owned by a Scheduled Task. The same existing `scripts/build_progressive_pass2_work.py` / `scripts/progressive_pass2.py::recompute_eligibility` entrypoint is invoked after every canonical write class that can change current eligibility: accepted/recovered Dossier persistence, PASS 1 durable state persistence, daily pre-AI generation/binding/freshness rebuild, and future PASS 2 attempt persistence. These writers share the existing serialized `taste-steam-review-dossier-canonical-writer` GitHub Actions boundary so a later rebase cannot overwrite the PASS 2 projection with eligibility derived from older canonical inputs.

**Почему:** Deep eligibility now depends on current semantic generation/work identity, exact canonically accepted Dossier content/binding/freshness, Deep first-pass/recovery state and current authorization. The previously landed hooks after Dossier persistence, Fast/PASS 1 persistence, daily/current identity-freshness preparation and Deep/PASS 2 attempt persistence remain the correct recomputation boundaries. The old requirement that eligibility also depend on current Fast/PASS 1 `analysis_incomplete` is superseded by PPD-004 and must be removed by the next runtime-adaptation task. Separate concurrency domains would still permit stale projection overwrite after concurrent writers rebase.

**Freshness boundary:** daily preparation recomputes normal freshness/binding changes. Wall-clock expiry between GitHub writes does not create a new scheduler: prepared work carries the exact Dossier expiry, the future semantic worker checks expiry/binding immediately before starting an item, and GitHub recomputes authorization from current canonical truth immediately before accepting a PASS 2 result/terminal receipt. Expired or rebound work therefore cannot consume an attempt or become canonical.

**Граница (historical pre-activation, superseded):** at the time of this decision PASS 2 remained inactive until a separate accepted activation. Current production has since activated `FAST-DOSSIER-DEEP-V1`; the preserved invariants remain that projection consumes zero attempts, buffered/unaccepted/failed Dossier artifacts are non-authoritative, and no polling daemon, second queue owner, retry loop or additional recurring producer is created.

**Сознательно отвергнуто:** Dossier-only hook; PASS1-only hook; daily-only reconciliation; ChatGPT-owned queue/retry state; a new expiry polling scheduler; separate unsynchronized PASS 2 projection writers.

**Основные места:** `config/progressive_pass2_contract.json`, `scripts/build_progressive_pass2_work.py`, `scripts/ingest_progressive_pass2.py`, `.github/workflows/ingest-progressive-pass1.yml`, `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`, `.github/workflows/build-pre-ai-store-snapshot.yml`, `.github/workflows/ingest-progressive-pass2.yml`.


---

## PPD-004 — Fast / Dossier / Deep are independent stages with Deep as eventual authority

**Дата:** 2026-09-22  
**Статус:** canonical architecture; the former pre-activation note that Deep runtime adaptation was still required and production Deep was inactive is superseded. Current production runs active `FAST-DOSSIER-DEEP-V1` under the canonical Progressive contracts.

**Решение:** Progressive personalization uses three related but independent stages. PASS 1 is user-facing **Быстрый разбор** and provides provisional early fit/not-fit/incomplete coverage. Taste Steam Review Dossier is user-facing **Подготовка досье**, remains neutral evidence preparation, and never decides fit/not-fit. PASS 2 is user-facing **Глубокий разбор** and is the eventual authoritative personalized analysis for every current eligible game.

Deep eligibility does **not** require a prior Fast attempt, Fast completion, or Fast `analysis_incomplete`. A current game becomes normal Deep work when its Progressive semantic/work identity is current, an exact-compatible canonically accepted current Dossier exists, and no authoritative current Deep completion exists. Therefore Deep may run before Fast. If authoritative Deep completes first, future Fast work for that identity is suppressed; if Fast completes first, Deep remains required.

**Effective result precedence:** trustworthy current completed Deep fit/not-fit is authoritative. Otherwise a trustworthy current completed Fast fit/not-fit may remain the provisional effective result. Deep incomplete/error never erases a still-valid Fast provisional result. Stage history stays separate and Deep never rewrites Fast provenance.

**First pass / recovery:** every current Deep identity gets one normal first-pass attempt once its accepted compatible Dossier is ready. A normal unresolved/technical failure does not count as authoritative completion and moves only that identity into GitHub-owned non-blocking recovery state. Recovery is not a blind retry loop and has no hidden arbitrary quota: every recovery attempt requires a fresh GitHub-owned authorization tied to a concrete condition such as materially changed accepted Dossier/evidence, a corrected runtime/validation defect material to the prior failure, or an explicit canonical recovery action with recorded reason. Recovery attempt history is separate from normal first-pass accounting.

**Completeness:** `deep_normal_first_pass_complete` and `deep_all_current_authoritative_complete` are different canonical metrics. Recovery-owned items may count as normal-first-pass-accounted but never as authoritative completion. Dossier normal-first-pass completeness and all-accepted/recovered completeness remain separate under the Dossier contract.

**Presentation:** GitHub must emit explicit per-game Fast/Dossier/Deep stage states for the browser; browser inference from history/files/timestamps is forbidden. The future UI may render three small pixel-style card indicators and one compact `Статистика` control leading to a dedicated three-section statistics page. Each section uses its own named denominator; scope counts are never merged when Fast, Dossier and Deep scopes differ.

**Preserved implementation:** existing GitHub-owned recomputation hooks after canonical Dossier persistence, Fast/PASS 1 persistence, daily/current identity/freshness preparation and future Deep/PASS 2 persistence are reusable, as are exact binding, liveness, zero-attempt projection and serialized ownership safeguards. The old recovery-only eligibility predicate and its activation plan are superseded and must not be activated.

**Граница (historical pre-activation, superseded):** at approval time Deep/PASS 2 stayed inactive and this decision itself did not create/enable/run a Scheduled Deep worker or consume backlog attempts. Current production has since activated Deep under `FAST-DOSSIER-DEEP-V1`; Dossier evidence semantics and site ranking weights remain unchanged, and activation did not transfer scheduler ownership into this decision record.

**Основные места:** `config/progressive_personalization_contract.json`, `config/progressive_pass1_contract.json`, `config/progressive_pass2_contract.json`, `config/execution_ownership_contract.json`, `PROJECT_ROUTES.md`.


---

## TASTE-014 — Dossier retrieval boundedness is semantic/adaptive, not a fixed search/page count

**Дата:** 2026-09-23  
**Статус:** implemented by `WORKER_TASK_TASTE_DOSSIER_SEMANTIC_BOUNDED_RETRIEVAL_01.md`.

**Решение:** hard per-game ceilings of 8 web-search queries and 16 opened/read source pages are removed from the active Dossier worker and machine evidence contract. Boundedness is now defined by semantic progress: stop early when evidence is sufficient; otherwise continue only through mandatory or materially promising distinct retrieval routes while the current snapshot/plan/binding is live and ordinary invocation runtime/tooling safely permits progress. Materially equivalent query, locale, endpoint, list/index or already-proven unusable surface variants are not new routes and must not be retried without a materially new factual lead. When all reasonably discoverable mandatory materially distinct routes are exhausted and critical evidence remains insufficient, fail closed and publish nothing.

**Ledger / observability:** query and opened-page counters remain diagnostic execution facts only. Their corresponding limit fields are explicitly `null`; count ordinals are not semantic stop gates and cannot by themselves justify route exhaustion, `stop_gate`, or `why_not_executed`. Runtime/tool/transport blockers and binding/liveness changes remain valid invocation-level stop conditions only when directly observed.

**Почему:** a fixed 8/16 ceiling can terminate a legitimately progressing exact-product/Russian retrieval solely because an arbitrary ordinal was reached, even when a materially distinct required route remains. Removing that ceiling must not turn the worker into an unlimited crawler, so anti-loop control is route-semantic rather than numeric: equivalence suppression, distinct-route exhaustion, evidence sufficiency, exact identity, and ordinary invocation runtime remain the bounding mechanisms.

**Граница:** this decision supersedes only the numeric 8/16-bound portions of TASTE-008, TASTE-010, TASTE-012 and earlier implementation reports. Russian-attempt semantics, exact-product/appid identity, temporal pre-stop rules, privacy/provenance, source diversification, create-only buffered transport, group size, GitHub-owned recovery/completeness, and scheduler ownership remain unchanged. No replacement numeric ceiling, website quota, scheduler, queue, retry loop, checkpoint authority, persistence owner, or production Dossier run is introduced.

**Основные места:** `config/taste_steam_review_dossier_worker_prompt.md`, `config/taste_steam_review_dossier_web_evidence_contract.json`, `scripts/test_taste_dossier_semantic_bounded_retrieval.py`, `scripts/test_taste_steam_review_dossier_semantic_consistency.py`, `.github/workflows/validate-taste-dossier-buffered.yml`.

---

## TASTE-015 — Dossier sufficiency means downstream-ready neutral coverage

**Дата:** 2026-09-25  
**Статус:** implemented by `WORKER_TASK_TASTE_DOSSIER_PURPOSE_AND_COVERAGE_SUFFICIENCY_FIX_01.md`.

**Решение:** Taste Dossier is a neutral, profile-agnostic evidence package for a later personalized Deep analysis. The Dossier worker must not use the user's Taste profile to choose favorable/unfavorable evidence or to decide when research is complete. Its semantic objective is a sufficiently complete, balanced, evidence-grounded picture of the actual game experience so downstream Deep can later judge fit.

**Sufficiency / speed:** semantic coverage and downstream usefulness outrank throughput, ordinary latency and minimizing tool calls. One valid observation, one usable source, one Russian item, one generic positive or one complaint is evidence, not completion. `research_state:"sufficient"` / `stop_reason:"evidence_stable"` requires a structured neutral coverage attestation over the final serialized observations. A material unresolved dimension forbids persisted sufficient/stable output. Narrow slices such as localization-only, generic social enjoyment, one isolated mechanic/complaint, or aggregate sentiment cannot close research while broader materially distinct exact-product player-feedback routes remain reasonably discoverable.

**Compact dossiers remain valid:** there is no minimum review/source/search/page/observation count and no numeric completeness score. A compact dossier may close when it directly and credibly characterizes the central experience, or when remaining applicable material dimensions are genuinely unavailable after required materially distinct routes are exhausted and no critical material gap remains. Balanced investigation means checking meaningful strengths and weaknesses/trade-offs where reasonably discoverable; it does not require fabricated one-pro/one-con symmetry.

**Boundedness / ownership:** this does not authorize unbounded crawling. TASTE-014 semantic/adaptive boundedness, equivalent-route suppression, exact identity, Russian evidence, temporal checks, privacy/provenance, create-only transport, ordinary invocation runtime/tool/liveness boundaries, GitHub-owned scope/validation/persistence/recovery/completeness and Scheduled Task ownership remain unchanged. No recovery authorization or Scheduled Task action is introduced.

**Основные места:** `config/taste_steam_review_dossier_worker_prompt.md`, `config/taste_steam_review_dossier_web_evidence_contract.json`, `config/taste_steam_review_dossier_schema.json`, `scripts/taste_steam_review_dossier_strict.py`, `scripts/test_taste_dossier_purpose_coverage_sufficiency.py`, `.github/workflows/validate-taste-dossier-buffered.yml`.


---

## PPD-006 — Progressive semantic invocations traverse a frozen run-start authority asynchronously

**Дата:** 2026-09-24  
**Статус:** canonical; supersedes only the per-item mutable-latest freshness timing in PPD-005 and earlier worker prompts.

**Решение:** Fast/PASS 1 and Deep/PASS 2 no longer serialize already-predeclared sibling semantic work on GitHub ingest/manifest advancement. A Fast invocation freezes the current prepared manifest/profile pin once and traverses its ordered items without waiting for prior sibling ingest. Exact Fast transport existence means only “already submitted; do not recreate”; it never means accepted or attempted.

Deep establishes one GitHub-confirmed invocation boundary before semantic execution. The worker first creates one create-only `PROGRESSIVE-PASS2-RUN-START-MARKER-V1`; the existing GitHub PASS 2 ingest path confirms it. The marker commit's actual first parent—not a worker-supplied timestamp—defines `run_start_authority_commit`, and that marker commit's Git committer time defines `run_started_at_utc`. The confirmed authority freezes ordered work, immutable profile pin, exact Dossier SHA/binding/expiry state and recovery authorization identity/reason/condition. Dossier/profile/recovery/work changes after that boundary belong to the next invocation and do not trigger per-item rereads or retroactive invalidation. Every Deep result/terminal transport binds to the marker commit plus the GitHub-confirmed authority/time, and GitHub ingest requires that confirmation to have been durable before the result transport.

**Invalid Deep transport:** malformed/invalid exact authorized Deep result or terminal receipt remains zero-attempt. GitHub durably writes the existing ingest rejection receipt, removes the bad candidate from the active deterministic inbox path in the same canonical-writer transaction, keeps no separate raw rejected-payload archive and adds no rejected-payload fingerprint field. A freed path is not worker-owned retry authority: only a later GitHub-prepared run-start view can authorize another submission, and there is no same-invocation retry loop.

**Почему:** immutable predeclared siblings are independent semantic work, so waiting for canonical ingest between games creates avoidable head-of-line blocking. Conversely, checking mutable Dossier/recovery state between Deep games can invalidate work after it was legitimately authorized. Director review DRG-01 additionally proved that a worker-written `run_started_at_utc` cannot itself prove which `main` state was current at the real invocation boundary: an older authority plus a forged earlier time could otherwise masquerade as current. The one-time GitHub marker confirmation closes that gap without restoring per-item checks. Invalid zero-attempt transport must not permanently occupy a create-only deterministic path.

**Сохранено:** GitHub alone owns scope/order, canonical acceptance, attempts, recovery authorization, completeness and persistence; exact profile pin and exact work/Dossier/recovery identity remain strict; valid execution still consumes attempts exactly once; stale/unprepared work remains fail-closed; Fast and Deep remain independent; Dossier worker/progression behavior is unchanged; no scheduler/queue/retry daemon or Scheduled Task setting is added or changed.

**Основные места:** `config/progressive_pass1_contract.json`, `config/progressive_pass1_worker_prompt.md`, `config/progressive_pass2_contract.json`, `config/progressive_pass2_worker_prompt.md`, `config/execution_ownership_contract.json`, `scripts/progressive_work_authority.py`, `scripts/ingest_progressive_pass2.py`, `scripts/progressive_pass2.py`.


---

## PPD-007 — Deep run-start confirmation is a publication guard, not a semantic-computation barrier

**Дата:** 2026-09-24  
**Статус:** canonical; supersedes only the “confirmation before semantic execution” timing clause of PPD-006. The GitHub-owned confirmation guard itself remains mandatory.

**Решение:** Deep reads one exact `observed_main_commit`, reads and freezes the PASS 2 contract/work plus the exact profile/Dossier/recovery inputs from that immutable commit, and creates the existing create-only run-start marker before any semantic execution. Semantic computation may then begin immediately, but it is strictly provisional: it may use only that exact observed immutable view and has no attempt, persistence, or transport effect by itself.

Before the **first** Deep result or terminal execution receipt from the invocation is serialized/published, the worker must obtain the durable GitHub-owned `PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1`. Publication is authorized only when the receipt is exact, `status:"confirmed"`, its marker path/nonce lineage matches the marker, and its `run_start_authority_commit` equals the exact `observed_main_commit` used for provisional semantics. The trusted `run_started_at_utc` still comes only from the marker commit's Git committer time through that receipt. A rejected, inconsistent, unsafe, or different-authority receipt invalidates all provisional work from the invocation and authorizes no result, terminal receipt, or semantic attempt.

**Delayed confirmation:** if the first provisional outcome is ready before the receipt exists, absence is not a failure authorization and never permits transport. The worker may perform only the bounded contract-defined wait/recheck sequence: one read when the first outcome is ready, then at most two delayed rereads after about 5 and 10 additional seconds (15 seconds total additional wait), while runtime/tool budget safely permits. If confirmation is still absent, the invocation stops without publishing or consuming an attempt. This tolerates the observed ~13-second GitHub confirmation latency without creating an unbounded poller, retry loop, queue manager, or second marker.

**Почему:** production anchor `202a0517b61d3462049afad503e57f2610c1eb05` was valid and later confirmed, but the scheduled worker stopped before semantics because the receipt had not yet appeared; this turned normal asynchronous GitHub persistence latency into zero-work invocations. Conversely, earlier anchor `90e8f5cc93c19950d5a4f4f016ce262f854c4eeb` was correctly rejected because observed main had been superseded. Therefore the confirmation remains the anti-race **publication** guard, while semantic computation before confirmation is speculative only.

**Сохранено:** GitHub remains sole control-plane authority for scope/order, marker confirmation, canonical acceptance, attempts, recovery authorization, completeness and persistence. Ingest must still prove that the confirmed receipt was durable before result transport and must reject missing/rejected/wrong-authority confirmation. No per-item mutable-current reread is restored; after one confirmation, frozen siblings continue without sibling-ingest waits. Fast prerequisites, Dossier acceptance/evidence semantics, Scheduled Task configuration, scheduler ownership and recovery ownership are unchanged.

**Основные места:** `config/progressive_pass2_contract.json`, `config/progressive_pass2_worker_prompt.md`, `config/execution_ownership_contract.json`, `scripts/ingest_progressive_pass2.py`, `scripts/progressive_work_authority.py`, `scripts/test_progressive_async_traversal.py`, `PROJECT_ROUTES.md`.

---

## TASTE-016 — Directly observed exact-product player feedback is usable without permanent per-review identity

**Дата:** 2026-09-26  
**Статус:** implemented by `WORKER_TASK_TASTE_DOSSIER_PRAGMATIC_EVIDENCE_MODEL_FIX_01.md`.

**Решение:** Taste Dossier may use concrete player-authored/player-feedback content that the worker directly observes in one of three acquisition modes: `stable_item`, `inspected_collection_item`, or `search_result_observation`. A neutral stable item URL/`public_ref` remains preferred auditability metadata when already available, but a permanent item locator and transient author/account identity are no longer evidence-validity, Russian-gate, recurrence-strength, or Dossier-completion prerequisites. Locatorless collection/search observations require strict safe source-level exact-product binding and persist only a neutral synthesis, source provenance, acquisition mode, language/recency metadata and dossier-local join ids.

**Search/discovery representations:** a search/discovery result is usable evidence only when its returned representation itself exposes concrete player-feedback content, the result can be bound fail-closed to the exact intended product, and the content materially supports the serialized observation/conflict. Query wording, a domain hit, locale, aggregate review count/rating, or a result with no concrete player-authored content is discovery metadata only. Once usable exact-product feedback was visibly observed in the result representation, a later target-page open/read failure does not invalidate that observation merely because no per-item locator can be recovered.

**Russian gate:** `found_and_used` requires actually observed and used Russian/mixed player feedback, but that feedback may use any allowed acquisition mode. The retained `existence_established_retrieval_unresolved` / `existence_established_access_unresolved` states are limited to genuine inability to observe usable concrete Russian/mixed content; missing locator, missing author identity, or later target-page failure after usable result observation is not such an unresolved state. Aggregate-only Russian activity still cannot satisfy `found_and_used`.

**Dedupe / recurrence:** `feedback_id` and `mention_count` remain dossier-local compatibility/bookkeeping fields, not globally stable review identity or review-population truth. One observed support item can establish only anecdotal support. Stronger recurrence is qualitative and evidence-grounded from materially independent observations/sources; no semantic level requires N stable locators or transient-author identities. Obvious aliases/equivalent resurfacing must not be duplicated to inflate support.

**Supersession boundary:** this decision supersedes **only** the conflicting item-level permanent-locator, transient-author fallback requirement, and stable-locator numeric recurrence/count prerequisites in TASTE-008 and TASTE-010. It does **not** relax exact AppID/product/release/DLC identity, safe provenance/privacy, language truth, TASTE-012 temporal completeness, TASTE-014 semantic/adaptive boundedness, TASTE-015 downstream-ready 12-dimension coverage sufficiency, create-only buffered transport, immutable group planning, or GitHub ownership of scope/validation/persistence/recovery/completeness.

**Privacy:** raw review/post/search-result text, snippets, quotes, usernames/display names, Steam/account/profile identity, profile URLs and reversible/direct author-derived hashes remain forbidden in persisted Dossier artifacts. No persistent author registry is introduced.

**Architecture:** no scheduler, second queue, retry daemon, crawler, manual backlog replay, Dossier recovery authorization, Deep recovery authorization, or Scheduled Task setting/change is introduced. Historical accepted Dossiers are not rewritten in place; binding changes flow through normal GitHub-owned projection/refresh semantics.

**Основные места:** `config/taste_steam_review_dossier_contract.json`, `config/taste_steam_review_dossier_web_evidence_contract.json`, `config/taste_steam_review_dossier_schema.json`, `config/taste_steam_review_dossier_worker_prompt.md`, `scripts/taste_steam_review_dossier_strict.py`, `scripts/taste_steam_review_dossier_compact_provenance.py`, `scripts/test_taste_dossier_pragmatic_evidence_model.py`, `.github/workflows/validate-taste-dossier-buffered.yml`.

