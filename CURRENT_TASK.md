# CURRENT TASK

## Taste V3 migration: recover interrupted scheduled run

Статус: in_progress
Дата исходной задачи: 2026-08-30
Последнее обновление handoff: 2026-08-31

Цель:
- завершить миграцию active production scope с `legacy_coarse_fit` на пять нормализованных price-blind taste factors `0..100`;
- использовать только существующий GitHub-owned queue/ingest/downstream pipeline;
- не превращать interactive chat в массовый semantic worker.

Architecture preflight:
1. GitHub владеет scope, queue, exact binding validation, persistence, completeness и downstream rebuild.
2. Existing scheduled ChatGPT taste worker остаётся semantic data-plane.
3. Новая recurring stage/queue/quota/retry-loop не создаётся.
4. Stale/noncanonical semantic results нельзя relabel/rebind без доказанной semantic equivalence.

Подтверждённый provenance вывод:
- `config/taste_result_contract.json` создан commit `e0e687968eacd7f2994a33a6c942ba639e7ec8da` и с тех пор не менялся; именно он задаёт пять normalized factor semantics.
- До canonical V3 cutover projection была `taste-v2` с semantic digest `28177637756ffc4cf51ea8cb7a37b6e3d1173dd11f852deb56966d29261ec13b`.
- Bounded normalized-factor canary commit `9d9e4e4aa044c125048c1922d583a9726e40e4da` тоже был привязан к `taste-v2` / `281776…`, хотя уже содержал `taste_factors`.
- Canonical V3 cutover commit `89b0376b820926369714b748d2404c87dcd88405` перевёл model binding на `taste-v3` и semantic digest `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`; cutover прямо добавил `taste_factor_semantics` из canonical result contract в semantic digest.
- Пять interrupted-run submissions `2026-08-31T0630Z-001..005.json` использовали `price_blind_taste_v3` + digest `fc0e4846…` + stale source binding. Такой canonical binding не найден ни до, ни после V3 cutover.
- Текущий scheduled-task prompt требует копировать exact bindings из текущего `taste_projection.json`; усилен fail-closed запретом придумывать/alias-ить binding strings.
- Поэтому provenance старых 500 результатов недостаточен для безопасного rebind; они переоцениваются штатным worker.

Recovery decision:
- старые 500 результатов переоценивает существующий scheduled semantic worker по текущей GitHub-owned queue;
- пять невалидных submission-файлов удалены только из active inbox; Git history остаётся аудитом;
- canonical cache/projection/payload/queue/ranking вручную не редактируются.

Текущий Taste progress:
- пользователь вручную запустил существующую scheduled-задачу с усиленным prompt;
- на `main` уже появились current-bound Taste V3 semantic checkpoints; не polling-ить run и не вмешиваться параллельной обработкой игр;
- после завершения проверить exact bindings, штатный ingest, остаток queue, downstream build и `score_precision=normalized_taste_factors`.

---

## Parallel subtask: Steam fixed-package purchase options

Статус: in_progress_research_and_implementation
Выбрано пользователем: 2026-08-31
Исходная backlog-оценка: `L5 / T4 / I4`

Цель:
- если Steam Store Package (`Sub_`) содержит одну или несколько игр текущего результата и является объективно более выгодным фиксированным вариантом покупки, producer должен это вычислить и передать готовым полем в visual payload;
- UI только отображает готовую рекомендацию покупки;
- текущий Taste scope/model/queue не менять.

Architecture preflight:
1. Purchase-option discovery/comparison — deterministic GitHub responsibility по `config/execution_ownership_contract.json`.
2. Новая scheduled ChatGPT stage не нужна.
3. Новую recurring queue/quota/retry-loop не создавать.
4. Использовать уже существующие Steam KZ commercial snapshot + official Steam app/package metadata route.
5. Разработка идёт на отдельной branch, пока scheduled Taste-run пишет checkpoints в `main`; до окончания Taste не запускать намеренно production rebuild на main этой подзадачей.

Уже подтверждено:
- `scripts/steam_production.py` получает текущие KZ цены и скидки App/Sub из Steam Search и сохраняет их в mailing feed;
- `.github/workflows/build-content-metadata.yml` уже вызывает official `appdetails` для `App_` и `packagedetails` для `Sub_`; для `Sub_` сохраняет `package_apps`;
- `.github/workflows/build-offer-family-resolution.yml` уже сравнивает base app с package, если package содержит ровно одну base game;
- multi-game package сейчас намеренно становится отдельной `franchise_bundle` family и не прикрепляется как purchase alternative к входящим играм;
- это объясняет текущий пробел: BioShock, BioShock 2 и BioShock Infinite есть как отдельные строки, но `BioShock: The Collection` (`Sub_127633`) отсутствует в mailing feed и поэтому current offer-family stage его не видит;
- fixed `Sub_` package можно обрабатывать неперсонализированно; dynamic Steam `/bundle/` / Complete-the-Set нельзя считать фиксированной ценой без отдельной доказанной price semantics — для них пока fail closed.

Проверенный regression-кейс:
- current snapshot: `BioShock` 662 KZT, `BioShock 2` 397 KZT, `BioShock Infinite` 975 KZT; сумма трёх отдельных base titles = 2034 KZT;
- `BioShock: The Collection` = Steam Store Package `Sub_127633`; текущая KZ цена подтверждена как 1420 KZT, то есть на 614 KZT дешевле уже только этих трёх отдельных покупок и дополнительно содержит другой контент;
- current `offer_family.validation.json` для BioShock families не содержит package alternative.

Предпочтительный implementation direction:
1. Расширить existing app metadata: сохранять package IDs, которые Steam `appdetails` связывает с app, как discovery seeds purchase-only options.
2. Для уникальных discovered `Sub_` fetch-ить через existing official `packagedetails?cc=kz` состав и fixed KZ price/discount.
3. Не добавлять discovered packages в Taste queue/candidate semantic scope; это purchase-only entities.
4. В offer-family/purchase layer построить reverse membership `appid -> fixed packages` и сравнивать package с replaceable standalone purchase cost входящих текущих игр.
5. Не считать неизвестную ценность/неизвестные standalone prices экономией; дополнительный контент можно отображать как bonus.
6. Dynamic/personalized `Bundle_` не сравнивать с fixed Sub до отдельного canonical contract extension.
7. Producer должен передать selected/better purchase option и объяснение в final visual payload; UI ничего не пересчитывает.

Definition of done для подзадачи:
- fixed package discovery не зависит только от того, появился ли `Sub_` отдельной строкой Steam Search;
- BioShock regression на `Sub_127633` проходит детерминированно на fixture/test;
- package recommendation считается producer-side и не влияет на Taste verdict/factors;
- personalized/dynamic bundle path остаётся fail-closed;
- `PROJECT_ROUTES.md` и, если появляется новое архитектурное правило, `PROJECT_DECISIONS.md` обновлены;
- после окончания Taste изменение можно безопасно интегрировать в main и проверить обычным downstream rebuild.

---

## Общий Definition of done текущей работы

Taste:
- current GitHub-owned taste queue закрыта только current-bound V3 submissions;
- downstream production validation проходит;
- final producer использует normalized taste factors там, где предусмотрено ranking precedence.

Purchase options:
- fixed Steam Store Packages могут быть обнаружены через app relationships даже при отсутствии package row в search feed;
- выгодный fixed package доходит до карточки как готовый producer-owned purchase option;
- BioShock regression подтверждён.

После фактического завершения обеих активных частей синхронизировать `PROJECT_ROUTES.md` / `PROJECT_DECISIONS.md`; `CURRENT_TASK.md` удалить только когда нет активной незакрытой части.

Коммуникационные инварианты:
- если ответ занимает >1 минуты, в том же ответе объяснить задержку и сделать долговечное ускорение;
- diagnostic prompt/log/config, который ассистент сам попросил прислать, не исполнять без отдельной явной команды пользователя;
- простые UI-проверки по возможности просить пользователя, сложную contract/diff диагностику выполнять инструментами.
