# ЧАТ 2 — повторный независимый аудит Research V2 (fresh6 rerun1)

**Task:** dossier-v2-fresh6-rerun1-research-reaudit-evidence-01  
**Дата проверки:** 2026-11-16  
**Режим:** READ-ONLY / RECON, только этот report-only DRAFT PR; содержательная переоценка, не Research rerun и не Assembly.  
**Репозиторий и base:** kentrap2011-hub/steam-kz-deals-2, main.  
**Обязательные gates:** CHAT_PROTOCOL.md / CHAT_CONTEXT.md; WORKER_TASK_DOSSIER_V2_FRESH6_RERUN1_RESEARCH_REAUDIT_EVIDENCE_01.md; config/dossier_research_independent_quality_audit_protocol.md; маршрут Dossier V2 в PROJECT_ROUTES.md; PITFALL-009; config/dossier_research_notes_v2_contract.json, config/dossier_research_notes_v2.schema.json и config/dossier_notes_v2_item_receipt.schema.json.

## 1. Freeze / provenance

- Frozen trial: **dossier-notes-v2-fresh6-20261114-rerun1**.
- Frozen branch: **sandbox/dossier-notes-v2-fresh6-20261114-rerun1**.
- **Sandbox HEAD при начале:** cc36202c8e257a59a2bd463b0be821e572894ec7.
- Manifest: data/control/dossier_notes_v2/manifests/dossier-notes-v2-fresh6-20261114-rerun1.json; **blob SHA** 752d5689c3f7d055c94c1844877337eea13ebd79.
- Run-start marker commit: cdc8bcf79cef6d6e7c3c97ab91b5fb9416ab96d1.
- Snapshot ID: 25c227d782188699f56b5702b3f0cfa63b101d890f09620b7b59893fab93c1af; prepared_for_date 2026-11-11; source_main_sha 665f5d0202859a6bac20566671f10158538e4764.
- Main HEAD при подготовке отчётной ветки: 89608bb02e7b4afab36c18dfb85b6289c51b143a.
- Все ID, названия и порядок ниже взяты только из frozen manifest. Никаких замен продуктов или изданий.

| Порядок | g | AppID и издание | Assignment ID | Candidate blob SHA | Typed Research receipt blob SHA |
| --- | --- | --- | --- | --- | --- |
| 1 | 000001 | 1000010 Crown Trick | batch-bdda4764cb82820cc71565e1 | 1737afbff09b18dfd5f7fefb4a0d6e2fd9d7f32d | 75d7937d36a54138dcd5d573ef69acb96feca65e |
| 2 | 000001 | 102600 Orcs Must Die! | batch-c2cc7fa24858133403a944a3 | 2ed0600870442c76272b655688696add1fad19b2 | 28e53f7686af16adcfc349066187c4458a232f64 |
| 3 | 000001 | 1029690 Sniper Elite 5 | batch-bcc93e385d885f2c6046d2ec | 7cddb91dff2d5aa8f4ca0ebb75cf701006030c14 | e7375b885139b9259930e4d80609008a833687f7 |
| 4 | 000070 | 49520 Borderlands 2 | batch-4701e24f9a6e0e539d40de24 | 3872ebebdb41c233a410f87a3cb0d2f70e717f46 | 55dea0f04a6c228726e8280049fba086ef38f594 |
| 5 | 000070 | 499180 Braid, Anniversary Edition | batch-cb814fef210f7aed5dede611 | 6a41e6405cf5e5e60dd4c7739e60ecba628f41ff | 5d477a691e0631161a46ed66d6be9349fe20153e |
| 6 | 000070 | 501590 Bulletstorm: Full Clip Edition | batch-26a14ae3e2cdab2a3dfe369a | 1f66c942d21c7506b9b79ee22a1f7c4dc5540342 | bcd0f89f0a17778ea562dc2f8512a04553eaf682 |

Путь candidate каждой строки: data/ai_inbox/dossier_notes_v2/dossier-notes-v2-fresh6-20261114-rerun1/g{шесть цифр группы}/{appid}--{assignment_id}.json.  
Путь typed receipt: data/control/dossier_notes_v2/receipts/dossier-notes-v2-fresh6-20261114-rerun1/g{шесть цифр группы}/{appid}--{assignment_id}--research.json.

**Техническая граница:** шесть receipts содержат disposition=safe_incomplete_research, staged_only=true, canonical_acceptance=false, semantic_attempt_state=unknown; source.transport_technically_verified=true, но source.github_receipt_confirmed=false и issuer.github_run_authenticated=false. Это транспортная фиксация candidate и typed receipt, а **не** независимое доказательство фактов или canonical acceptance. Исходные candidate имеют research_status=notes_recorded. Не выдавать такое состояние за содержательно «готово».

## 2. Независимая методика и web-access trace

Сначала из manifest зафиксированы шесть точных Steam AppID/изданий. **До чтения всех шести Research candidate notes и прежнего QA #456** для каждого продукта выполнен самостоятельный веб-поиск, открыты точные публичные страницы, прочитаны релевантные разделы, составлены проверяемые факты и вопросы. Затем из GitHub прочитаны шесть оригинальных candidate JSON (notes_text, unknowns_text, необязательное conflicts_text, source_log, research_status) и шесть receipts. Подтверждение здесь означает только реально открытый и прочитанный аудитором внешний текст; найденный URL, чужой source_log, сниппет или GitHub receipt не повышает confidence. Старые выводы PR #456 **4 QUALITY_GOOD / 2 QUALITY_WEAK дезавуированы и не использованы** как исходная оценка.

**Реально открытые и прочитанные независимые материалы, 2026-11-16:**
- Crown Trick: [официальная Steam-страница AppID 1000010](https://store.steampowered.com/app/1000010/Crown%20Trick/) (функции/теги), [Prima Games — PC review от 2020-10-15](https://primagames.com/gaming/crown-trick-review-pc) (личная игра, random build, Blink, статус-эффекты), [RPGFan — PS5 review от 2021-10-10](https://www.rpgfan.com/review/crown-trick/) (soul shards/постоянные улучшения и геймплей). **Субъективные PS5 observations не переносятся автоматически на PC.**
- Orcs Must Die!: [Steam AppID 102600](https://store.steampowered.com/app/102600/Orcs_Must_Die/) (single-player, релиз 2011, DLC отдельно), [GameSpot PC/X360 review от 2011-10-11](https://www.gamespot.com/reviews/orcs-must-die-review/1900-6339433/) (ловушки, арсенал, skull upgrades, повторение планировок, нет мультиплеера), [Reddit — отзыв участника по первой игре и сравнение с серией](https://www.reddit.com/r/OrcsMustDie/comments/1qt3f62/my_feelings_about_orcs_must_die_1/) (враги/нагрузка на героя, Weavers). Reddit — **личные мнения в конкретной теме**, а не выборка частот.
- Sniper Elite 5: [Steam AppID 1029690](https://store.steampowered.com/app/1029690/Sniper_Elite_5/) (campaign/co-op, Axis Invasion, competitive PvP, Survival, DLC), [PC Gamer — PC review 2022](https://www.pcgamer.com/sniper-elite-5-review/) (ограниченность маршрутов, awkward ближний бой, история/AI и вторжения), [GameSpot — review 2022-05-26](https://www.gamespot.com/reviews/sniper-elite-5-review-longer-range/1900-6417884/) (кастомизация, ограничители, перемещение, AI). Оценки рецензентов — **мнения**, не измерение глобальной распространённости багов.
- Borderlands 2: [GameSpot — review от 2012-09-17](https://www.gamespot.com/reviews/borderlands-2-review/1900-6396650/) (луто-шутер, разнообразие классов, сюжет/юмор, онлайн до четырёх человек, отдельное console split-screen), [историческая Steam-hosted лента обновлений/патча с UVHM от 2013 года](https://store.steampowered.com/news/posts/?appids=49520&enddate=1364927213) (повышенный HP/regeneration, усиление действия slag в UVHM), [Reddit — обсуждение slag в UVHM](https://www.reddit.com/r/Borderlands2/comments/1qmg5l2/is_there_any_way_around_the_slag_necessity_in_uvhm/) (часть игроков считает slag очень полезным/нужным, другие указывают исключения по персонажам/билдам). **Steam store AppID 49520 перенаправил на age gate; страницу продукта не считать открытой/прочитанной.** Исторический игровой патч не переносится на базовую Normal campaign.
- Braid, Anniversary Edition: [Steam AppID 499180](https://store.steampowered.com/app/499180/Braid/) (издание 2024, time manipulation, new puzzles/world, commentary, single-player), [Push Square — PS5 review от 2024-05-13](https://www.pushsquare.com/reviews/ps5/braid-anniversary-edition) (переключаемый старый/новый вид, новые задачи, подробные комментарии, ценность повторной покупки), [Steam Community — developer news/patch notes для AppID 499180](https://steamcommunity.com/app/499180/allnews/) (различные новые commentary rooms и **датированные macOS-only** исправления), [Steam Community — original AppID 26800 developer news](https://steamcommunity.com/app/26800/allnews/) (отдельный Anniversary релиз, старый сохранён). PS5-рецензия не служит PC-тестом. Reddit-ссылки из чужого source_log отдельно открыть не удалось — см. ограничения.
- Bulletstorm: Full Clip Edition: [Steam AppID 501590](https://store.steampowered.com/app/501590/Bulletstorm_Full_Clip_Edition/) (2017 remaster, single-player и online co-op), [GameSpot — PC/PS4 review от 2017-04-06](https://www.gamespot.com/reviews/bulletstorm-full-clip-edition-review/1900-6416652/) (Skillshots, leash/kick, Echoes, Anarchy co-op, Overkill, remaster, Duke DLC, отдельные небольшие ragdoll-глюки), [Steam discussion от 2017-04-08](https://steamcommunity.com/app/501590/discussions/0/133261907132283472/) (первичные пользовательские утверждения: campaign co-op отсутствует, кооператив только в специальных режимах), [Steam discussion от 2021 года](https://steamcommunity.com/app/501590/discussions/0/3044979493849428827/) (то же о co-op Anarchy). Отдельные сообщения и наблюдения 2017 года не доказывают системных актуальных PC-сбоев в 2026 году.

**Недоступные / ограниченные чтения:** сторонняя страница SuperPhillip по Crown Trick вернула HTTP 429 (unavailable, не evidence); ссылки https://www.reddit.com/r/braid/comments/1ct3sjp и https://www.reddit.com/r/braid/comments/1cxaq13/appreciation_for_braid_anniversary_edition/ при попытке открытия вернули DisabledError (unavailable); Steam product AppID 49520 переадресовал на age-check (partial/blocked). По этим URL **нет статуса opened/read**. Не подтверждены чтением аудитора и оригинальные candidate source_log ссылки на Steam review *collection* как совокупности разнородных отзывов: ссылки и claimed access в Research не являются моими независимыми посещениями. Никаких численных квот на URL/отзывы не применялось.

## 3. Evidence Gate — шесть решений в порядке manifest

Статусы отдельных утверждений: **CONFIRMED** = сам открыл/прочитал релевантный материал по точному изданию, **UNCERTAIN** = доступный текст подтверждает лишь частный опыт/ограниченную часть тезиса, **UNKNOWN** = независимого подтверждения нет; заметка Research сама по себе не подтверждение. Каждый статус ниже применён *до* итогового QUALITY verdict.

### 1 / 1000010 — Crown Trick — **QUALITY_WEAK**

**Механика и режимы.** Research правильно описывает пошаговые срабатывания врагов, позиционирование, телепорт, элементальные сочетания, фамильяров, roguelite-случайность. Однако **не указывает явный single-player**, существенную комнатную боевую структуру и persistent upgrades (soul shards), влияющие на игровой цикл и отношение к сложности. Объяснение Blink/Break и мета-прогрессии добавляет конкретику для оценивания реиграбельности и порога входа.

| Research claim / пробел | Независимый URL, класс, действительно прочитанный фрагмент и контекст | Статус → влияние |
| --- | --- | --- |
| «враги действуют после хода героя», элементы и фамильяры | [Steam AppID 1000010](https://store.steampowered.com/app/1000010/Crown%20Trick/), официальный storefront: step-based rooms, elemental interactions, Familiar abilities; Steam feature single-player. | **CONFIRMED** → корректное ядро; missing solo/room structure заметный пробел. |
| телепортация/случайные сборки, баланс, повторения | [Prima PC review 2020](https://primagames.com/gaming/crown-trick-review-pc), firsthand PC test: ограниченный Blink, выбор оружия/фамильяров по RNG, многократные повторения комнат/ситуаций; это опыт автора, не статистика. | **CONFIRMED** как наличие механик, **UNCERTAIN** как распространённый дефект баланса → нужна аккуратная атрибуция. |
| отсутствие описания постоянного развития | [RPGFan PS5 review 2021](https://www.rpgfan.com/review/crown-trick/), firsthand PS5: soul shards покупают постоянные улучшения между забегами. | **CONFIRMED** наличие мета-прогрессии в обозреваемой версии → существенный недосказанный roguelite loop. |
| «UI перекрывает поле», «порча сохранения», «ограниченная глубина после десятков часов» | Не нашёл достаточно независимого подтверждения точного UI/сохранения/долгого тайминга в прочитанных страницах; оригинальный source_log предлагает Steam reviews collection, **не равен моему reading**. | **UNKNOWN** для технических жалоб/точной длительности; нельзя преподносить как частый или актуальный PC-баг. |

**Матрица:** механика частично сильная; solo omitted; версия Crown Trick 2020 без remaster-проблемы; отдельные обзоры показывают позитив за тактику и негатив RNG/повтор, но частоты неизвестны; PS5-обзор не подтверждает PC performance; save corruption unverified. **Существенный содержательный пробел + слабая датировка техники → QUALITY_WEAK.** Исправить полноту, разделить единичные complaint leads и подтверждённые свойства.

### 2 / 102600 — Orcs Must Die! — **QUALITY_GOOD** (с ограничениями)

**Механика/режимы/edition.** Research различает оригинал 2011 и продолжения, активный герой + тактика ловушек, одиночный режим, юмор, переигрывание, рост сложности; представлена и позитивная, и негативная сторона. Критического искажения основного продукта не выявлено. Добавление skull upgrades/Weavers и указание, что **две DLC — отдельные товары**, усилит сборку без необходимости объявлять Research слабым.

| Research claim / пробел | Независимый URL, класс, реально прочитанный фрагмент | Статус → влияние |
| --- | --- | --- |
| оригинальная игра 2011, single-player, ловушки + оружие/магия | [Steam AppID 102600](https://store.steampowered.com/app/102600/Orcs_Must_Die/), официальная страница: single-player и original title; [GameSpot 2011](https://www.gamespot.com/reviews/orcs-must-die-review/1900-6339433/), firsthand PC/X360 review: ловушки и прямые атаки, без multiplayer. | **CONFIRMED** → ключевой identity/mode верен; не путать с Orcs Must Die! 2. |
| удовольствие от связок, юмор, сложные волны, перераспределение ловушек | [GameSpot 2011](https://www.gamespot.com/reviews/orcs-must-die-review/1900-6339433/) — оригинальный обзор хвалит захватывающую расстановку и отмечает схожесть арен/шуток. | **CONFIRMED** как авторская оценка/описанные особенности, **UNCERTAIN** как универсальная частота отзывов. |
| «первая требует больше личного участия, особенно против быстрых и летающих» | [Reddit player thread](https://www.reddit.com/r/OrcsMustDie/comments/1qt3f62/my_feelings_about_orcs_must_die_1/): личное сопоставление 1 и 3 части, кобольды, летающие враги и огры, комментарии об улучшениях/Weavers. | **CONFIRMED** существование такой субъективной позиции; **UNCERTAIN** как общий консенсус игроков — так не утверждать. |
| не указаны skull upgrades/Weavers и отличие DLC | [GameSpot 2011](https://www.gamespot.com/reviews/orcs-must-die-review/1900-6339433/), механика skull upgrades; [Steam](https://store.steampowered.com/app/102600/Orcs_Must_Die/) предлагает Artifacts of Power и Lost Adventures отдельно от base. | **CONFIRMED** → полезная добавка для Assembly; не обнаружено критически неверного Research core. |

**Матрица:** core ловушки/hero defense покрыты; solo установлен и отражён; base/series edition отражены корректно, DLC можно уточнить; опыт игроков показан, но Reddit единичен; критичных временно-платформенных багов notes не обобщает. **QUALITY_GOOD** по существу с непроверенной частотой субъективных тезисов и добавлениями для возможной *отдельно разрешённой* стадии. Не означает acceptance.

### 3 / 1029690 — Sniper Elite 5 — **QUALITY_WEAK**

Research в целом корректно отражает снайперскую кампанию, вторжения Axis, два игрока в кооперативной кампании, кастомизацию и спорное ощущение свободы маршрутов. Но пропущены **существенные другие режимы**: конкурентный PvP до 16 игроков и режим Survival с кооперативом до 4. Нельзя сводить все мультиплеерные возможности к co-op campaign / Axis Invasion. Также не объяснена граница DLC / Complete Edition.

| Research claim / пробел | URL, класс и реально прочитанный контекст | Статус → влияние |
| --- | --- | --- |
| большая карта, снайпинг, настройка оружия, 2-player co-op campaign и optional Axis Invasion | [Steam AppID 1029690](https://store.steampowered.com/app/1029690/Sniper_Elite_5/), официальная страница описывает отдельные режимы и кастомизацию; [PC Gamer 2022](https://www.pcgamer.com/sniper-elite-5-review/) — firsthand прохождение с опциональными вторжениями. | **CONFIRMED** → корректный baseline. |
| missing 16-player competitive multiplayer и up-to-four co-op Survival | [Steam AppID 1029690](https://store.steampowered.com/app/1029690/Sniper_Elite_5/), явное описание competitive multiplayer до 16 и Survival co-op до 4. | **CONFIRMED** → **существенный omission**, меняет представление о социальных режимах; QUALITY_WEAK. |
| «невидимые барьеры», awkward movement, AI, повторяемость | [GameSpot review 2022-05-26](https://www.gamespot.com/reviews/sniper-elite-5-review-longer-range/1900-6417884/) и [PC Gamer PC review 2022](https://www.pcgamer.com/sniper-elite-5-review/), критики описывают такие ощущения на релизе. | **CONFIRMED** как конкретные first-hand критические мнения; **UNCERTAIN** как глобальные/актуальные для патчей 2026 проблемы. |
| отличие base от DLC/Complete Edition | [Steam AppID 1029690](https://store.steampowered.com/app/1029690/Sniper_Elite_5/) показывает DLC и отдельный Complete Edition purchase choice. | **CONFIRMED** → не переносить дополнения на базовую версию; отсутствует в Research. |

**Матрица:** кампания и механика покрыты, другие существенные modes отсутствуют; edition/DLC boundary отсутствует; игроки/рецензенты расходятся, время критики 2022 и PC, неизвестна нынешняя частота AI/movement; **QUALITY_WEAK** из-за неполноты modes, хотя основные положительные и отрицательные тезисы поддержаны.

### 4 / 49520 — Borderlands 2 — **QUALITY_WEAK**

Research правильно описывает co-op looter-shooter, классы, loot, юмор, реиграбельность и сложный UVHM. Но нет **уточнения онлайн кооператива до четырёх человек**, зависимости split-screen от платформы, базовой игры vs DLC/разных editions. Фраза о «фактической необходимости постоянно накладывать slag» слишком категорична: в UVHM это сильная обычная механика, но не абсолютная для каждой сборки/класса. Она не относится к основной кампании Normal/TVHM.

| Research claim / пробел | URL, класс, реально прочитанный контекст | Статус → влияние |
| --- | --- | --- |
| классы, яркий loot, quests/юмор, кооператив | [GameSpot 2012 original review](https://www.gamespot.com/reviews/borderlands-2-review/1900-6396650/): описаны разнообразные умения, совместное прохождение **до 4 онлайн**, console split-screen при обзоре консольной игры. | **CONFIRMED** → верные основные плюсы; **missing explicit party size and platform-specific split-screen**. Это не доказательство native PC split-screen. |
| UVHM: высокий HP, regeneration, усиленный slag | [Steam-hosted original patch/news 2013](https://store.steampowered.com/news/posts/?appids=49520&enddate=1364927213), конкретный контекст UVHM: HP примерно в 4 раза, regen, slag multiplier от 2x к 3x. | **CONFIRMED** для **UVHM/исторического обновления**, но не всех режимов и не современной бесперебойности. |
| «фактически обязательно постоянно накладывать slag» | [Reddit обсуждение игроков об UVHM](https://www.reddit.com/r/Borderlands2/comments/1qmg5l2/is_there_any_way_around_the_slag_necessity_in_uvhm/) показывает жалобу на зависимость от slag, *но также контрпримеры* с некоторыми билдом/персонажами и особым снаряжением. | **UNCERTAIN** для абсолютного «обязательно постоянно» → заменить на «часто очень полезно/ощущается обязательным у части игроков; есть исключения». |
| «недавние сетевые жалобы», частота и актуальные ошибки | Независимой репрезентативной, датированной текущей платформой оценки распространённости нет. Steam product AppID 49520 встретил age-check; доступ к его подробному содержимому **blocked/partial**. | **UNKNOWN** → нельзя повышать complaint до «системная проблема co-op». |
| base/DLC boundary и редакции | В прочитанных материалах различаются base game, отдельно расширяемые UVHM/DLC и консольные особенности; но нет достаточной независимой проверки полного списка изданий и включённого контента каждого. | **UNCERTAIN** для полного edition inventory; **значимый пробел** в notes, не выдумывать полный DLC pack перечень. |

**Матрица:** центральный loop + co-op покрыты, однако точное party/platform и DLC/edition отсутствуют; опыт игроков mixed, но Reddit личные мнения; UVHM/slag датируется историческим 2013 патчем и обсуждениями, одиночный случай сетевой проблемы не массовая авария. **QUALITY_WEAK** — избыточно категоричный gameplay claim и существенные ограничения mode/edition.

### 5 / 499180 — Braid, Anniversary Edition — **QUALITY_GOOD** (с ограничениями)

Research точно фиксирует именно отдельное **Anniversary Edition 2024**, а не старую Braid, рассказывает о puzzle time rewind, обновлённой графике, дополнительных заданиях, необычайно подробных интерактивных комментариях и спорной выгоде повторной покупки. Главное различие edition и core experience выдержано. Режим **single-player** и live-switch классического/современного визуала можно прямо дописать. Но **конкретное** утверждение «ветеранам новые задачи лёгкие, новичкам сложные» здесь не верифицировано собственным чтением первичных Reddit-тредов — не выдавать за общую тенденцию.

| Research claim / пробел | URL, класс и реально прочитанный контекст | Статус → влияние |
| --- | --- | --- |
| отдельный AppID 499180, 2024 remaster, time rewind puzzles, new world/puzzles, комментарии, solo | [Steam AppID 499180](https://store.steampowered.com/app/499180/Braid/), официальный storefront описывает новые уровни/комментарии и single-player. [Original Braid developer news](https://steamcommunity.com/app/26800/allnews/) уточняет сохранение оригинала и отдельный Anniversary release. | **CONFIRMED** → identity и основные механики/новый контент корректны. |
| новые puzzle rooms, старый/новый стиль, ценность комментариев для давних владельцев | [Push Square PS5 review 2024-05-13](https://www.pushsquare.com/reviews/ps5/braid-anniversary-edition), first-hand PS5 experience; [Anniversary developer news](https://steamcommunity.com/app/499180/allnews/) describes additional commentary rooms. | **CONFIRMED** как свойства версии и описанный опыт конкретного рецензента; не делать кросс-платформенных обещаний о performance. |
| мнения «ветеранам лёгкие, новичкам сложные» | Пытавшиеся открыть Reddit оригинальные два exact links вернули **DisabledError**; официальный магазин и обзор не дают надёжной картины распределения мнений по категориям игроков. | **UNKNOWN** для такой сравнительной закономерности; не преувеличивать, но это **не разрушает** основные верно проверенные notes. |
| технические жалобы, если понадобятся позднее | [Steam developer patch notes](https://steamcommunity.com/app/499180/allnews/) говорят о конкретных dated macOS 11/12 issue fixes (Dec 2024 и др.), а не о массовых Windows проблемах. | **CONFIRMED** только эти датированные macOS fixes → нельзя распространять на Windows/PS5/current build. |

**Матрица:** core time-puzzles, solo, точное издание и ключевые добавления, опыт рецензента/ценность double-dip covered; цены, распространённость новых отзывов и тезис veteran/newbie остаются unknown; нет обобщённых технических обвинений. **QUALITY_GOOD** с ограничением на непроверенный социальный тезис и enrichment solo/visual toggle. Не означает acceptance.

### 6 / 501590 — Bulletstorm: Full Clip Edition — **QUALITY_WEAK**

Research верно описывает Skillshots, leash/kick, окружающую среду, сюжетную кампанию, Echoes, грубоватый юмор и спорную реиграбельность. Но описание как «динамичного одиночного шутера» скрывает **онлайн co-op Anarchy (horde), при отсутствии кооперативной кампании**, и не раскрывает **Ultimate Echoes / Overkill** и отделённый Duke Nukem add-on. Это существенная недосказанность для конкретного remaster edition.

| Research claim / пробел | URL, класс и действительно прочитанный фрагмент/контекст | Статус → влияние |
| --- | --- | --- |
| Skillshots с whip/leash, kick, environment, solo campaign, vulgar humor | [Steam AppID 501590](https://store.steampowered.com/app/501590/Bulletstorm_Full_Clip_Edition/) — 2017 edition; [GameSpot PC/PS4 review 2017-04-06](https://www.gamespot.com/reviews/bulletstorm-full-clip-edition-review/1900-6416652/) — firsthand arcade kill-chain mechanics, сюжет и юмор. | **CONFIRMED** → главный игровой hook адекватен. |
| не указан кооперативный **Anarchy** и отсутствие кооперативной кампании | [Steam product](https://store.steampowered.com/app/501590/Bulletstorm_Full_Clip_Edition/) явно содержит Online Co-op; [GameSpot review 2017](https://www.gamespot.com/reviews/bulletstorm-full-clip-edition-review/1900-6416652/) описывает Anarchy cooperative horde; [Steam community first-hand 2017 discussion](https://steamcommunity.com/app/501590/discussions/0/133261907132283472/) указывает, что **campaign co-op нет**, co-op только в отдельном mode. | **CONFIRMED** для доступности кооператива Anarchy; отсутствие co-op campaign поддержано конкретными участниками и сопоставлением режима, но community source ограничен по авторитету — **UNCERTAIN** для исчерпывающей платформенной матрицы. Это **существенный** пропуск Research. |
| edition дополнения / Ultimate Echoes / Overkill / Duke | [GameSpot 2017 PC/PS4](https://www.gamespot.com/reviews/bulletstorm-full-clip-edition-review/1900-6416652/) описывает новые Echoes-related features и Overkill after completion, Duke Nukem add-on как отдельно приобретаемый/предзаказной content. | **CONFIRMED** для описанной Full Clip edition эпохи релиза → уточнить, что base edition включает, а что отдельно; старый оригинал 2011 не смешивать. |
| баги столкновений, вылеты, незачёт Skillshots | [GameSpot PC/PS4 review 2017](https://www.gamespot.com/reviews/bulletstorm-full-clip-edition-review/1900-6416652/) упоминает отдельные ragdoll glitches на релизе; ни он, ни прочитанные страницы не дают оценки частоты/современной версии вылетов и зачёта Skillshots. | **CONFIRMED** только частное наблюдение о ragdoll в 2017, **UNKNOWN** для массовых crashes/skillshot bugs на PC в 2026. |

**Матрица:** core gameplay и solo кампании covered, но co-op modes/ограничение co-op campaign пропущены; Full Clip 2017 vs original 2011 и добавки описаны недостаточно; достоинства/недостатки представлены, технические complaints без платформы/даты недоказаны. **QUALITY_WEAK** — конкретный материальный mode/edition omission и неатрибутированные tech claims.

## 4. Итоговая матрица и disposition

| Порядок, AppID | Evidence Gate | Основная причина | Что делать с содержанием |
| --- | --- | --- | --- |
| 1 — 1000010 Crown Trick | **QUALITY_WEAK** | отсутствие single-player и permanent progression/room loop; неподтверждённые UI/save claims | **Исправить** механику и отделить технические UNKNOWN от опыта критиков |
| 2 — 102600 Orcs Must Die! | **QUALITY_GOOD** | основные mechanics/mode/edition/опыт подтверждены, нет значимого искажения | Только **непроверенный lead** для возможной отдельно разрешённой Assembly; добавить skull/Weavers/DLC caveat, не делать Reddit opinion массовым |
| 3 — 1029690 Sniper Elite 5 | **QUALITY_WEAK** | пропущены PvP до 16, Survival co-op до 4; edition/DLC | **Исправить** полную матрицу режимов и base vs Complete |
| 4 — 49520 Borderlands 2 | **QUALITY_WEAK** | online party/platform/DLC scope нет, slag «обязательно постоянно» переобобщено | **Исправить** способы игры и смягчить UVHM claim |
| 5 — 499180 Braid, Anniversary Edition | **QUALITY_GOOD** | edition/новые пазлы/commentary/ценность проверены | Только **непроверенный lead** для возможной отдельно разрешённой Assembly; UNKNOWN тезис о сложности ветеранов и новичков, дописать solo/visual toggle |
| 6 — 501590 Bulletstorm: Full Clip Edition | **QUALITY_WEAK** | отсутствует Anarchy co-op и ограничение campaign co-op, remaster добавки, неатрибутированные баги | **Исправить** mode/edition и оставить техжалобы UNKNOWN без массовых формулировок |

**Один обоснованный общий вердикт:** **2 QUALITY_GOOD (Orcs Must Die!, Braid Anniversary), 4 QUALITY_WEAK (Crown Trick, Sniper Elite 5, Borderlands 2, Bulletstorm Full Clip), 0 BLOCKED_EVIDENCE**. Распределение следует из данного независимого чтения и конкретных пробелов, **не** из дезавуированных оценок PR #456. GOOD здесь означает лишь достаточную полноту исходного Research по независимо проверенным ключевым утверждениям; это **не** подтверждённый canonical Dossier, не технический «accepted» и не разрешение Assembly. Для WEAK исправление содержания необходимо до использования в дальнейшей semantic стадии; audited candidate/receipt остаются неизменны. Никакого нового Research rerun или Assembly этим PR не разрешается.

## 5. Контроль записи, блокеры и ровно один bounded next step

**Scope/write-set:** меняется **только этот Markdown-отчёт** на отдельной ветке в одном report-only DRAFT PR. В исходный sandbox/candidates/receipts, PR #456, протоколы, contract/schema, workflow, execution/registry/board/CURRENT_TASK, production, V1/Deep, Actions/owner grants и main **ничего не записано и не запускалось**. Настоящее внешнее чтение было выполнено отдельно от GitHub; CI проверяет лишь GitHub-техническое состояние и не может доказать посещение сайтов. Фиксированные доступ/ограничения и URL раскрыты выше.

**Блокеры/ограничения:** unavailable Reddit Braid source pages, age-gated Borderlands store, 429 отдельного Crown обзора, невозможность вывести частоту bugs/отзывов из единичных рассказов; эти UNKNOWN раскрыты и не превращены в CONFIRMED. Неожиданных блокеров публикации отчёта на момент составления текста нет; состояние GitHub CI/PR head нужно считать только по фактическому readback после создания PR.

**Единственный bounded next step для директора:** рассмотреть четыре указанных набора **точечных semantic исправлений** (1000010/1029690/49520/501590) и два GOOD как *unverified leads*, принять отдельное scoped решение о возможной коррекции/следующей semantic стадии **без автоматического разрешения Research/Assembly и без изменения исходных immutable candidates в рамках этого QA**. Любая такая стадия требует самостоятельного authorization и соблюдения GitHub-owned control plane.

**Примечание по эффективности:** больше всего времени заняли независимые чтения и проверка контекстов изданий/режимов/критики, а также один точный fetch по каждому original candidate и receipt. Следующий аудитор может использовать frozen manifest + candidate/receipt path pattern и этот trace как навигацию, **но не считать его заменой своим собственным независимым web-open/read**; отдельные route/pitfall правки запрещены write-set этого задания.
