# CURRENT TASK

Последнее обновление: 2026-09-01

## Завершено

### Taste V3
Статус: `complete`.
- canonical `ai_queue_count=0`;
- final Taste ingest, downstream visual build и deploy подтверждены зелёными;
- model binding: `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`.

### Steam fixed-package purchase options — visibility + ranking value
Статус: `complete_production_validated`.

Итоговое продуктовое правило:
- только fixed Steam Store Package (`Sub_`);
- package должен покрывать >=2 currently visible base-game families по actual included appids / canonical family membership;
- original/remaster equivalence не угадывается;
- package должен быть строго дешевле суммы current standalone prices; family считается один раз; unknown extra content value = 0;
- dynamic/personalized Complete-the-Set `/bundle/` исключён fail-closed;
- package не меняет Taste и влияет только на purchase/value часть финального score;
- scorer независимо считает standalone purchase route и eligible fixed-package route, затем берёт более высокий прозрачный purchase score; при равенстве остаётся standalone, поэтому одна и та же выгода не считается дважды;
- package route учитывает экономию против текущей покупки игр отдельно, эффективную цену за одну покрытую игру и количество покрытых visible games;
- package total price выше practical ceiling из ranking policy не получает package-score;
- карточка показывает отдельный заметный блок `🎁 Выгодный набор Steam` с названием, ценой, количеством/названиями игр, standalone total, экономией, ценой за игру и кнопкой открытия package в Steam.

Production proof после reopening:
- implementation merge: `a86b0e793b445c5d1af54ac08ba00528be946f6e` (`Make fixed Steam packages visible and ranking-aware`);
- visual run #111 / `33423352245` — success;
- `PRIORITY_RANKING_VALIDATION=PASS`;
- fixed-package regression: `12 passed`;
- `package_qualifying=7`, `package_touched=17`;
- `PACKAGE_VISIBLE_CARDS=17`, `PACKAGE_RANKING_DRIVERS=15`;
- production examples: `FlatOut 2` purchase score `22 -> 36` (+14) через `Flatout Complete Pack` за ~272 ₽ / 3 игры; `The Night of the Rabbit` `22 -> 40` (+18) через `The Daedalic Armageddon Bundle` за ~120 ₽ / 7 игр;
- package-aware visual commit: `66c00e9e389691be885123a9dd4e48663c41d5ad`;
- downstream deploy #151 / `33423389598` — success на package-aware payload;
- actual Pages artifact #151 (`9769779423`) проверен: в одном задеплоенном artifact одновременно присутствуют новый package UI и package-aware `data/current.json`;
- более поздний visual run #113 / `33437077173` также сохранил package regressions зелёными и диагностировал те же `17` visible package cards / `15` package ranking drivers.

Быстрый маршрут и rationale:
- `docs/fixed_package_purchase_options.md`;
- `docs/RANK-013-fixed-package-purchase-route.md`.

Задачу не переоткрывать только из-за того, что конкретная просмотренная карточка не имеет package: package block появляется только у игр, для которых текущий fixed `Sub_` реально проходит условия. Если пользователь сообщает, что package не виден на игре, которая точно должна иметь `better_purchase_option`, проверять deployed artifact/current payload для этой конкретной игры.

## Не активная основная работа

### SteamDB tail
Статус: `blocked_low_priority`.
- `App_901735` remains blocked/retryable;
- exact Kazakhstan historical minimum remains unproven and must not be fabricated.

## Запланировано, но ещё НЕ начато

### A. Ranking and card explanation quality audit
Статус: `planned`.
- audit минимум top-30 + boundary cases;
- trace `evidence -> Taste factors -> personal/purchase score -> rank -> card explanation`;
- высокий rank не должен необъяснимо получаться из одного слабого generic factor;
- служебная фраза вроде `Игра прошла строгий вкусовой отбор` не считается плюсом;
- каждая visible recommendation должна иметь минимум один конкретный содержательный плюс и минимум один доказуемый минус/ограничение/trade-off;
- `Подтверждённых персональных рисков не найдено` не считается минусом;
- если evidence недостаточно для содержательных плюса/минуса, карточка считается incomplete и требует enrichment, а не placeholder;
- добавить score/explanation regression guards.

### B. Russian language availability as a ranking factor
Статус: `planned`.
- проверять минимум русский интерфейс: `yes/no/unknown` + evidence;
- полного русского нет -> сильный practical/final-ranking penalty и видимый существенный минус;
- `unknown` не равно `no`;
- Taste semantics не менять.

### C. YouTube reviews for games
Статус: `planned`.
- полезный релевантный обзор перед покупкой;
- приоритет качественному русскоязычному ролику или подтверждённой русской аудиодорожке;
- не подставлять случайные/спойлерные видео ради ссылки;
- producer-owned choice, UI display-only.

### D. Fix stale/wrong game image when swiping cards
Статус: `planned`.
- при переходе на новую игру иногда остаётся изображение предыдущей до ручного refresh;
- text/price/image должны атомарно соответствовать текущей игре;
- проверить image state/key/cache и async race при быстрых переходах;
- добавить regression на несколько быстрых последовательных swipes.

### E. Guarantee Russian game descriptions
Статус: `planned`.
- 100% visible cards должны иметь содержательное русское описание;
- Steam Russian -> использовать/сокращать;
- Steam English/другой язык -> автоматически переводить на русский;
- английский fallback, скрытый блок и technical placeholder не допустимы;
- если у Steam действительно нет никакого source description, это отдельный exceptional data-quality case для разбора;
- добавить pre-deploy validation на nonempty Russian description и запрет placeholder strings.

### F. Redesign detailed score breakdown UI
Статус: `planned`.

Наблюдаемый дефект по мобильному интерфейсу:
- раскрытая `Детальная оценка` стала визуально перегруженной после появления package-aware ranking;
- слишком много отдельных pill/chip-строк подряд, из-за чего блок выглядит дробно и тяжело читается;
- важные уровни иерархии (`итоговый балл`, `насколько подходит тебе`, `выгодность покупки`, выбранный purchase route) визуально конкурируют между собой;
- длинные подписи факторов занимают много высоты и делают карточку чрезмерно длинной;
- package-driver (`Выгодный набор Steam · +N балла против покупки отдельно`) полезен, но сейчас плохо встроен в общую визуальную структуру оценки.

Требование:
- сохранить всю прозрачность score и возможность понять, откуда взялся итоговый балл;
- сделать раскрытую оценку заметно компактнее и визуально спокойнее на мобильном экране;
- явно отделить крупные секции `Подходит тебе` и `Выгодность покупки`, а внутри показывать факторы более компактным списком/табличной строкой вместо каскада больших pills;
- главный акцент — итог секции (`42,9/60`, `36/40`) и несколько реально значимых drivers; второстепенные детали не должны иметь такой же визуальный вес;
- выбранный purchase route (`игра отдельно` / `выгодный набор Steam`) показать компактно и понятно рядом с коммерческой частью;
- длинные технические подписи вроде `детальная нормализованная оценка`, `unknown`, внутренних source/status wording преобразовывать в понятные пользовательские формулировки;
- не убирать данные из producer payload и не менять ranking math ради дизайна: задача только presentation/interaction layer;
- проверить на реальной карточке с package driver (например `FlatOut 2`) и без package, а также на узком мобильном viewport;
- добавить UI regression/snapshot или DOM-проверку, чтобы детальная оценка не возвращалась к перегруженному виду после новых score-компонентов.

Definition of done:
- на мобильном экране пользователь за несколько секунд видит итог 0–100, вклад `Подходит тебе`, вклад `Выгодность покупки` и причину package-route, не разбирая длинную стену chips;
- все числовые составляющие по-прежнему доступны при раскрытии;
- блок занимает существенно меньше вертикального места и имеет понятную визуальную иерархию.

## Текущий статус работ

Сейчас незавершённой `in_progress` задачи нет. Следующую плановую задачу начинать только после явного выбора пользователя; наличие пункта в backlog не означает, что он активен.
