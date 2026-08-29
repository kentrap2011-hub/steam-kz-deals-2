# GAME-DEALS-MAILING v1.9

`config/mailing_policy.json` — канонический источник правил отбора и production. `config/daily_execution_contract.json` — канонический источник расписания и способа получения результата. Этот файл — только краткое человекочитаемое описание.

## Текущая модель выполнения

- Суточный смысловой production выполняется по ночному регламенту в **01:00 Europe/Samara**.
- После завершения текущего production и закрытия AI taste queue формируется готовый `data/production/visual/current.json`.
- Отдельная рассылка/доставка в **08:00 отменена** и не должна создаваться заново.
- Пользователь открывает визуализацию сам в любое удобное время в течение дня; она показывает уже подготовленный замороженный суточный snapshot.
- Открытие/refresh витрины не запускает Steam/Store/SteamDB/web lookup и не пересчитывает taste, deal, eligibility/family, risk, reasons или `priority_rank`.

## Что исправляет v1.9

### 1. Taste fit стал строже

В v1.8 цена и скидка уже были отделены от вкуса, но semantic threshold оказался слишком мягким: generic tags позволяли получить слишком много положительных «аналогий».

В v1.9 действует `taste-v2`:

- цена, скидка, reviews, popularity, SteamDB и историческая цена полностью запрещены в taste verdict;
- `strong_fit`, `strong_niche_fit`, `recent_fit`, `high_confidence_adjacent` — только recall/audit flags, не taste evidence;
- `core_fit_count` — recall context, не положительный taste evidence;
- generic tags (`Action`, `Adventure`, `RPG`, `Singleplayer`, `Story Rich`, `Open World`, `Horror`, `Exploration` и т.п.) сами по себе не считаются содержательными сигналами;
- каждое положительное evidence должно связывать **конкретное свойство игры** с **конкретным якорем/устойчивым паттерном канонического профиля**;
- для `moderate+` нужен либо минимум один high-specificity механический/структурный якорь + независимый второй содержательный плюс, либо минимум три независимых specific signal из разных факторов профиля;
- хотя бы один плюс обязательно должен относиться к gameplay/mechanics/structure, а не только к теме, сюжету или визуалу;
- неизвестные свойства игры нельзя придумывать;
- audit использует тот же порог и не может его снижать.

Никаких whitelist конкретных игр и control-game names в policy нет.

### 2. Taste-cache теперь имеет ранний обязательный checkpoint

Файл: `data/cache/taste_fit.json`.

Cache hit возможен только при совпадении:

- exact production key;
- Git blob SHA `gaming_taste_live.json`;
- `taste_model_version` (`taste-v2`);
- price-blind fingerprint.

Главное новое правило: после того как все taste-cache misses получили окончательные post-audit verdict, pipeline **обязан сразу записать изменённый taste-cache одним GitHub write** — ещё до content eligibility, family resolution, Store, SteamDB, deal-quality и sorting.

Это сделано специально, чтобы длинный внешний этап больше не мог уничтожить уже выполненную работу по 597 кандидатам при timeout.

### 3. Остальные правила сохранены

- полный daily snapshot, не delta и не TOP-N;
- весь production-feed Steam Kazakhstan читается полностью;
- completed не является auto-exclude;
- wishlist не discovery, не taste proof и не ownership proof;
- DLC/chapter не рекомендуется самостоятельно по умолчанию;
- одна итоговая строка на purchase family с лучшим App/Sub/edition/bundle вариантом;
- свежий production snapshot подтверждает current price/discount;
- Store live только условно;
- SteamDB только history после персонального отбора;
- SteamDB legacy cache v1 читается, writer v2 поддерживает `confirmed_min`, `previously_free`, `unavailable_exact_history`;
- negative history cache TTL — 14 дней только для реально подтверждённо отсутствующей exact history;
- blocked/timeout/tool failure не записываются как negative-cache;
- runtime SteamDB cache count всегда `len(entries)`;
- historical 0 = `previously_free`, не платный минимум;
- единый provider+exact-key registry запрещает повторные Store/SteamDB lookup;
- исключённые позиции пользователю не показываются;
- upcoming — максимум одно ближайшее релевантное событие;
- финальная сортировка: `БРАТЬ СЕЙЧАС` → `МОЖНО БРАТЬ` → `ЛУЧШЕ ЖДАТЬ`.
