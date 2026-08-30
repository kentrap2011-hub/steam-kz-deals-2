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

**Граница:** срочность не спасает игру ниже taste threshold, символическую скидку, превышение бюджета или уже закончившуюся акцию. Неизвестная дата не штрафуется — просто не получает подтверждённого срочного приоритета.

**Основные места:** `PROJECT_RULES.md`, `config/final_ranking_policy.json`, `scripts/priority_ranking.py`, `scripts/validate_priority_ranking.py`.

---

## RANK-003 — `priority_bucket` остаётся главным качественным слоем после срочности

**Дата:** 2026-08-30  
**Статус:** implemented and regression verified

**Решение:** после expiry urgency идёт качественный `priority_bucket`, реализующий согласованную матрицу примерно 60% taste / 40% deal.

**Почему:** скидка, wishlist, ачивки и другие признаки не должны превращать слабое вкусовое попадание в более важную покупку, чем существенно более подходящая игра. Срочность — исключение только потому, что она отвечает за риск физически потерять предложение.

**Не делать:** не заменять bucket скрытым числовым score без отдельного согласования.

**Основные места:** `PROJECT_RULES.md`, `config/final_ranking_policy.json`, `config/mailing_policy.json -> sorting.qualitative_priority_buckets`.

---

## RANK-004 — Прямую оценку пользователя не учитывать второй раз после `priority_bucket`

**Дата:** 2026-08-30  
**Статус:** implemented and regression verified

**Решение:** direct user evidence может корректировать `fit`, после чего пересчитывается коммерческая ветка и `priority_bucket`; отдельного следующего слоя `direct_user_evidence` в final sort быть не должно.

**Почему:** иначе один и тот же вкусовой сигнал учитывается дважды: сначала меняет fit/bucket, затем ещё раз двигает игру внутри bucket.

**Основные места:** `scripts/refine_visual_ranking.py` (`apply_fit_adjustment`, `apply_commercial_branch`), final sort в `scripts/priority_ranking.py`, contract `config/final_ranking_policy.json`.

---

## RANK-005 — Подтверждённые персональные/Windows-риски раньше wishlist и цены

**Дата:** 2026-08-30  
**Статус:** partially implemented; ranking behavior verified, confirmed Windows fact acquisition still missing

**Решение:** внутри одинаковой expiry urgency и `priority_bucket` сначала учитывать **серьёзные подтверждённые** персональные и практические риски, включая реальные проблемы запуска на современной Windows. Средние/слабые эвристические риски остаются описательными и сами по себе не должны обгонять wishlist/коммерческую выгоду.

**Почему:** хорошая скидка мало полезна, если у игры есть подтверждённая проблема, которая существенно ухудшит сам опыт или потребует заметных ручных исправлений.

**Windows-уточнение:** строка Steam с XP/7/8 сама по себе не является доказательством проблемы — у старых игр требования часто просто не обновлялись. Такая строка только запускает/мотивирует дополнительную проверку. Понижение допустимо лишь при подтверждённой фактической ориентации ниже Windows 10, необходимости патчей/compatibility mode/ручных fixes или известных проблемах современной Windows.

**Текущая техническая граница:** production ranking уже нейтрализует одну только legacy Steam label и умеет понизить `known_fix_required`, `confirmed_pre_windows_10_target`, `serious_problem`. Но на 2026-08-30 отдельный канонический автоматический источник, который надёжно получает эти подтверждённые Windows-факты, ещё не реализован. Старый `build_visual_feed_v2.py` умеет только классифицировать строку Steam system requirements, чего недостаточно по этому решению.

**Основные места:** `PROJECT_RULES.md -> Практическая пригодность покупки`, `config/final_ranking_policy.json`, `scripts/refine_visual_ranking.py`, `scripts/priority_ranking.py`, `scripts/validate_priority_ranking.py`.

---

## RANK-006 — Wishlist важен, но ограничен

**Дата:** 2026-08-30  
**Статус:** implemented and regression verified

**Решение:** после bucket и серьёзных рисков wishlist даёт заметный приоритет уже допустимому кандидату.

**Почему:** wishlist — прямой сигнал предварительного интереса пользователя, но не доказательство вкусового соответствия и не повод обходить eligibility/budget/deal gates.

**Не делать:** wishlist не должен сам включать игру в список и не должен вытягивать существенно худший taste+deal вариант выше более сильного кандидата из другой группы.

**Основные места:** `PROJECT_RULES.md -> Wishlist Steam при финальной сортировке`, `config/final_ranking_policy.json`, `scripts/priority_ranking.py`.

---

## RANK-007 — Размер скидки важнее качества относительно исторического минимума

**Дата:** 2026-08-30  
**Статус:** implemented and regression verified

**Решение:** внутри одинаковых expiry/bucket/risk/wishlist условий сначала сравнивать `discount_percent`, и только потом `price_quality_vs_history`.

**Почему:** у новой игры даже обычные −20% часто автоматически являются историческим минимумом просто потому, что история цены короткая. Если history quality поставить раньше процента скидки, такой технический `record` получает слишком сильное преимущество над старой игрой с действительно крупной скидкой, например −70%.

**Сознательно отвергнуто:** порядок `history_quality → discount_percent`.

**Основные места:** `config/final_ranking_policy.json`, `scripts/priority_ranking.py`, `scripts/validate_priority_ranking.py`.

---

## RANK-008 — Достижения и длительность только поздние различители близких кандидатов

**Дата:** 2026-08-30  
**Статус:** implemented and regression verified

**Решение:** после скидки, истории и текущей цены учитывать achievement quality; duration — ещё позже как самый слабый tie-break перед title.

**Почему:** наличие/качество Steam Achievements важно пользователю, но не должно обгонять существенно более выгодную покупку. Длительность ещё менее фундаментальна и нужна только для очень близких вариантов.

**Основные места:** `PROJECT_RULES.md -> Практическая пригодность покупки`, `config/final_ranking_policy.json`, `scripts/priority_ranking.py`.

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
