# CURRENT TASK

Последнее обновление: 2026-09-01

## Завершено

### Taste V3
Статус: `complete`.
- canonical `ai_queue_count=0`;
- final Taste ingest, downstream visual build и deploy подтверждены зелёными;
- model binding: `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`.

## Активная работа

### Steam fixed-package purchase options — verified purchase equivalence / BioShock
Статус: `reopened_in_progress`.

Причина переоткрытия:
- `BioShock: The Collection` содержит `BioShock Remastered` (`409710`), `BioShock 2 Remastered` (`409720`) и `BioShock Infinite` (`8870`);
- текущая лента содержит `BioShock® 2` (`8850`) и `BioShock Infinite`, поэтому старый exact-appid coverage видит только Infinite и скрывает набор;
- это не UI-баг, а отсутствие отдельной verified purchase-equivalence модели для случаев, когда fixed package содержит подтверждённую улучшенную версию видимой игры;
- дополнительно старый producer полностью скрывает пакет, если он не строго дешевле суммы только видимых standalone игр, хотя релевантная информация о fixed package всё равно нужна пользователю.

Архитектурное направление:
- НЕ сливать original/remaster в одну Taste/family сущность;
- НЕ угадывать equivalence по названию, словам `Remastered`, franchise или fuzzy similarity;
- добавить отдельный producer-owned directional purchase-equivalence contract: видимая игра -> явно подтверждённые package appids, которые могут закрыть её покупку;
- первая подтверждённая регрессия: `7670 -> 409710` (BioShock -> BioShock Remastered), `8850 -> 409720` (BioShock 2 -> BioShock 2 Remastered);
- exact included appid остаётся приоритетным; verified equivalence используется только как дополнительное доказуемое purchase coverage;
- package info показывать, когда fixed `Sub_` покрывает >=2 visible families по exact/verified coverage; наличие информации о наборе не должно требовать, чтобы пакет обязательно был дешевле суммы этих visible standalone цен;
- ranking boost по-прежнему fail-closed: package-route влияет на score только когда проходит коммерческие условия ranking policy; просто наличие набора не повышает балл автоматически;
- UI различает `Выгодный набор Steam` и просто `Набор Steam`, если strict standalone savings не подтверждены.

Definition of done:
- BioShock Collection появляется как package option минимум на текущих карточках `BioShock® 2` и `BioShock Infinite` при текущем production scope;
- coverage audit показывает, что `BioShock® 2` покрыт именно через explicit verified equivalence `8850 -> 409720`, а Infinite — exact `8870`;
- без equivalence-конфига старое угадывание original/remaster остаётся запрещено regression-тестом;
- package info может быть visible без ranking boost, если strict commercial route не прошёл;
- production build и deploy зелёные, конкретный BioShock regression проверен на deployed payload.

## Завершённые package-инварианты, которые сохраняются

- только fixed Steam Store Package (`Sub_`);
- dynamic/personalized Complete-the-Set `/bundle/` исключён fail-closed;
- unknown extra content не получает выдуманную денежную ценность;
- package не меняет Taste;
- scorer сравнивает standalone и eligible package purchase routes прозрачно и без двойного счёта;
- dedicated package UI и package-aware ranking уже production-validated до текущего reopening.

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
- раскрытая `Детальная оценка` визуально перегружена: слишком много pills/chips, слабая иерархия и лишняя высота на мобильном;
- сохранить всю прозрачность score, но сделать блок компактнее и визуально спокойнее;
- явно отделить `Подходит тебе` и `Выгодность покупки`, внутри перейти к более компактным строкам;
- package-driver встроить в коммерческую секцию, не превращая его в отдельную стену текста;
- технические подписи преобразовывать в пользовательские;
- ranking math не менять ради дизайна;
- regression/snapshot на mobile viewport.

## Текущий статус работ

Сейчас активна одна задача: verified purchase equivalence / BioShock для fixed packages. Остальной backlog остаётся `planned`.
