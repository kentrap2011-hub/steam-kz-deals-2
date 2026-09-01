# CURRENT TASK

Последнее обновление: 2026-09-01

## Завершено

### Taste V3 migration
Статус: `complete`.
- исходная миграция Taste V3 была завершена и production-validated;
- model binding: `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`.

Важно: это не означает, что текущий новый source snapshot уже полностью переоценён. Последний scheduled Taste run увидел authoritative queue `147`, но опубликовал `0`, потому что в `main` уже лежат 9 неингестированных submission-файлов с duplicate-key transactional hazard. Это отдельный GitHub-owned ingest/rebuild blocker; вручную строить «остаточную очередь» в ChatGPT нельзя.

## Активная работа

### Steam fixed-package purchase options — verified complete-content valuation
Статус: `reopened_in_progress`.

Причина переоткрытия:
- production уже умеет показывать fixed `Sub_`, verified original/remaster purchase equivalence и пересчитывать коммерцию независимо от Taste;
- однако текущая package-value модель сравнивает цену набора почти только с currently visible base-game families и присваивает нулевую ценность всем nonvisible/extra content;
- для подтверждённого состава это слишком грубо: BioShock: The Collection включает не только BioShock Remastered, BioShock 2 Remastered и BioShock Infinite, но также BioShock 2: Minerva's Den Remastered, BioShock Infinite Season Pass и BioShock Infinite: Columbia's Finest;
- producer уже запрашивает StoreBrowse `include_included_items`, но `build_fixed_package_purchase_options.py` сохраняет только `included_appids` / базовое membership и теряет проверяемую структуру DLC/дополнительного контента;
- поэтому предыдущий production расчёт `256 ₽ standalone visible games vs 265 ₽ collection` не является полной оценкой ценности набора.

Отдельно установлена причина отсутствия первого BioShock в visible list:
- `App_7670` есть в текущем KZ Store snapshot: 662 KZT, скидка 75%;
- текущий Taste V3 entry имеет `EXCLUDE / below_moderate / exclude_direct_conflict`;
- сохранённое direct-conflict evidence утверждает, что BioShock ранее был начат и быстро брошен из-за отсутствия интереса;
- при этом normalized factors сами по себе не низкие: gameplay 78, development 76, pacing 59, identity 90, breadth 65;
- это semantic veto, а не коммерческое/Steam-исключение. Его корректность не менять молча в рамках package-value задачи; если direct-experience evidence неверно или больше не должно быть hard veto, это отдельная Taste-policy проверка.

Архитектурное направление:
- Taste/family identities остаются price-blind; набор не должен превращать Taste-excluded base game в standalone recommendation;
- producer должен сохранять полный проверенный top-level состав fixed package, включая DLC/content, с Steam provenance;
- `unknown/unverified` extra content по-прежнему имеет денежную ценность 0;
- `verified` included content можно учитывать денежно только если producer получил текущую KZ acquisition price / эквивалентный детерминированный purchase route;
- DLC/content, относящийся к visible/taste-qualified covered game, может увеличивать package commercial value;
- included base game, которое Taste исключает (сейчас BioShock 1), должно быть видно как included content, но не получать полный personalized game-value boost без изменения Taste policy;
- не считать одно entitlement дважды: direct top-level Season Pass и его внутренние DLC не суммировать рекурсивно; при неоднозначном overlap fail closed / use explicit entitlement evidence;
- package comparison и score остаются producer-owned; UI display-only;
- commercial refresh -> package complete-content valuation -> один canonical final ranking pass.

Definition of done:
- BioShock package artifact сохраняет все проверенные top-level included items, а не только три base-game appids;
- для Minerva's Den Remastered, Infinite Season Pass и Columbia's Finest хранится тип/parent/evidence и current KZ standalone acquisition price, если Steam её предоставляет;
- ranking comparison показывает отдельно: visible covered base-game value, verified incremental DLC/content value, nonpersonalized included game/content и total comparable value;
- никакой unknown/unpriced content не получает выдуманную цену;
- BioShock 1 отсутствие объясняется semantic veto, а не ошибочно трактуется как отсутствие товара;
- regression запрещает старое поведение, где verified DLC молча обнуляется;
- regression запрещает double count constituent DLC через Season Pass/recursive content;
- production pre-AI, visual build и deploy зелёные;
- BioShock acceptance проверен на deployed payload и пользовательская карточка показывает полный состав и честную экономику.

## Завершённые package-инварианты, которые сохраняются

- только fixed Steam Store Package (`Sub_`);
- dynamic/personalized Complete-the-Set `/bundle/` исключён fail-closed;
- exact included appid + explicit verified directional purchase equivalence; title/fuzzy remaster guessing запрещён;
- package info может быть visible без ranking boost;
- Taste не меняется от цены;
- fresh commercial refresh обновляет standalone commercial fields независимо от semantic queue;
- scorer сравнивает standalone и eligible package routes без stacking одного и того же commercial value.

## Не активная основная работа

### Current Taste source ingestion
Статус: `blocked_requires_github_ingestion_rebuild`, не выбран как текущая interactive-задача.
- authoritative prepared queue: 147;
- last scheduled run evaluated/published: 0/0;
- blocker: 9 existing non-ingested Taste submissions and duplicate keys across inbox files;
- canonical ingestion/downstream completion for this source is not proven;
- GitHub-owned ingest/rebuild must resolve this before the scheduled semantic worker continues.

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

Сейчас активна одна задача: verified complete-content valuation для fixed Steam packages. Current Taste ingestion остаётся отдельным GitHub-owned blocker и не должен тормозить коммерческий package refresh.