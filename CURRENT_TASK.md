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
- первый run остановился по hard runtime/tool limit после публикации `400` результатов в четырёх checkpoint-файлах по `100`;
- exact bindings этих checkpoint: profile `c478cda9bb7a9b024a30ca188dce4b98a2de24ea`, model `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`, source snapshot `2026-08-30T20:37:43.818127+00:00`;
- штатный ingest сначала отклонил checkpoints из-за worker serialization aliases (`include_*_fit`, `weak`) и доказанных identity-copy ошибок отдельных `taste_fingerprint`;
- one-shot fail-closed repair менял только canonical serialization aliases и fingerprint только при доказанном полном совпадении key/appid/current candidate context; verdict/evidence/taste_factors не менялись;
- repair run #2 успешно завершён;
- canonical bot commit: `35c4670699d6266cc498848e8b663d4f0530818d` — `Repair and ingest current Taste V3 checkpoints`;
- после первого восстановительного run canonical payload показывал `ai_queue_count=234`, `ready_without_ai_count=366`, `purchase_context_line_count=600`;
- второй scheduled run прочитал current queue `234`, оценил `100` результатов и опубликовал пять checkpoint-файлов суммарно на `100` результатов;
- первые четыре checkpoint второго run (`80` результатов) доказанно canonically ingested; authoritative queue пересобралась с `234` до `154`;
- пятый checkpoint `data/ai_inbox/taste/2026-08-31T1250Z-005.json` содержит следующие `20` строк в canonical queue order и на момент последней проверки всё ещё находится в active inbox; его ingestion пока не доказан;
- exact bindings второго run снова корректны и скопированы verbatim из current projection: profile `c478cda9bb7a9b024a30ca188dce4b98a2de24ea`, model `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`, source snapshot `2026-08-30T20:37:43.818127+00:00`;
- второй run правильно остановился fail-closed на GitHub-ingestion synchronization barrier и не создавал replacement remaining queue;
- НЕ запускать scheduled worker ещё раз, пока checkpoint `2026-08-31T1250Z-005.json` остаётся в canonical inbox: новый run упрётся в тот же барьер;
- следующий шаг: после конкретного сигнала об ingestion проверить один раз, что пятый checkpoint исчез из inbox и authoritative queue стала `134`; если checkpoint вместо этого застрял/упал, сначала диагностировать ingest, не пропуская его;
- только после доказанного ingestion пятого checkpoint один раз вручную запустить ту же scheduled task для оставшейся current GitHub-owned queue;
- SteamDB остаётся отдельно unresolved: prepared `1`, resolved `0`, blocked/retryable `App_901735`; это не блокирует Taste completion.

---

## Parallel subtask: Steam fixed-package purchase options

Статус: implementation_ready_on_feature_branch
Выбрано пользователем: 2026-08-31
Исходная backlog-оценка: `L5 / T4 / I4`
Feature branch: `purchase-options-fixed-packages-20260831`

Цель:
- если Steam Store Package (`Sub_`) содержит несколько игр текущего результата и является объективно более выгодным фиксированным вариантом покупки, producer должен это вычислить и передать готовым полем в visual payload;
- UI только отображает готовую рекомендацию покупки;
- текущий Taste scope/model/queue не менять.

Architecture preflight:
1. Purchase-option discovery/comparison — deterministic GitHub responsibility по `config/execution_ownership_contract.json`.
2. Новая scheduled ChatGPT stage не нужна.
3. Новую recurring queue/quota/retry-loop не создавать.
4. Использовать уже существующий Steam KZ StoreBrowse route.
5. Реализация изолирована на feature branch; до окончания Taste не запускать намеренно production rebuild на `main` этой подзадачей.

Подтверждённые факты:
- `scripts/build_pre_ai_store_snapshot.py` уже использует StoreBrowse `include_all_purchase_options=True`; Steam storefront для BioShock одновременно предлагает `BioShock: The Collection`, то есть purchase alternative существует на самой app-page и не требует отдельного поискового feed;
- StoreBrowse package-object предоставляет `included_appids`, а purchase option — `packageid`, current fixed KZ price и discount;
- multi-game package сейчас не прикрепляется как purchase alternative к входящим game families, поэтому этот слой действительно отсутствовал;
- fixed `Sub_` package можно сравнивать неперсонализированно; dynamic Steam `/bundle/` / Complete-the-Set остаются исключены fail-closed.

Проверенный regression-кейс и live nuance:
- исходный deterministic fixture: `BioShock` 662 KZT + `BioShock 2` 397 KZT + `BioShock Infinite` 975 KZT = 2034 KZT; `BioShock: The Collection` fixture price 1420 KZT; fixture savings 614 KZT;
- read-only live StoreBrowse test обнаружил `Sub_127633`, но current Steam membership возвращает remastered appids `409710`, `409720` и `8870`, а не старые original appids `7670`, `8850`;
- current `family_graph` считает originals и remasters отдельными game families, поэтому production logic не должна угадывать edition-equivalence (`original == remaster`);
- durable rule: package coverage подтверждается только фактическими included appids / canonical family mapping; никаких heuristic substitution между оригиналом и ремастером.

Что уже реализовано на feature branch:
- `config/fixed_package_purchase_option_contract.json` — явный контракт `FIXED-PACKAGE-PURCHASE-OPTION-V1`;
- `scripts/build_fixed_package_purchase_options.py` — discovery fixed `Sub_` через StoreBrowse, current KZ price + membership, purchase-only artifact `data/production/pre_ai/fixed_package_options.json`;
- unavailable/старые optional package IDs не блокируют production: классифицируются как `package_not_returned_by_storebrowse`;
- `scripts/apply_fixed_package_purchase_options.py` — producer-side сравнение только по currently visible base-game families;
- package рекомендуется только при покрытии минимум двух distinct visible game families и строгой экономии относительно суммы их standalone current prices;
- неизвестный дополнительный контент получает расчётную ценность 0 и не может искусственно создать экономию;
- лучший package выбирается по большей абсолютной экономии, затем меньшей цене, затем packageid;
- результат пишется в `better_purchase_option` и одновременно добавляется как дополнительный `offers` entry с готовым русским объяснением;
- dynamic `/bundle/` / Complete-the-Set не поддерживаются и не сравниваются;
- `.github/workflows/build-pre-ai-store-snapshot.yml` строит purchase-only artifact и запускает regression test;
- `.github/workflows/build-daily-visual-payload.yml` применяет готовое package enrichment после final visual build и до commit;
- `scripts/test_fixed_package_purchase_options.py` содержит BioShock regression и negative-path проверки; локально базовая версия тестового набора прошла `6/6`, затем добавлены ещё discovery safety regressions;
- compare `main...purchase-options-fixed-packages-20260831` подтверждает, что branch не меняет Taste/cache/semantic файлы: только два existing workflow, новый contract и три package scripts.

Что осталось перед production:
1. Исправить deterministic/live BioShock regression так, чтобы он проверял фактические package members и не подменял remaster original-appid'ом.
2. Повторить read-only live test; если он зелёный, package implementation технически готова к интеграции.
3. Дождаться полного закрытия Taste V3 queue, чтобы не смешивать две production-миграции.
4. Обновить feature branch относительно актуального `main`.
5. Запустить штатный pre-AI build уже после интеграции и проверить реальный `fixed_package_options.json`.
6. Запустить обычный downstream visual build и проверить реальные `better_purchase_option` только для фактически покрытых current families.
7. После production-validation синхронизировать `PROJECT_ROUTES.md` / `PROJECT_DECISIONS.md`.

Definition of done для подзадачи:
- fixed package discovery не зависит только от того, появился ли `Sub_` отдельной строкой Steam Search;
- BioShock regression соответствует фактическому Steam membership и проходит детерминированно/live без edition guessing;
- package recommendation считается producer-side и не влияет на Taste verdict/factors/ranking;
- personalized/dynamic bundle path остаётся fail-closed;
- production build подтверждает реальный artifact и visual field;
- `PROJECT_ROUTES.md` / `PROJECT_DECISIONS.md` обновлены после production-validation.

---

## Общий Definition of done текущей работы

Taste:
- current GitHub-owned taste queue закрыта только current-bound V3 submissions;
- downstream production validation проходит;
- final producer использует normalized taste factors там, где предусмотрено ranking precedence.

Purchase options:
- fixed Steam Store Packages могут быть обнаружены через app relationships даже при отсутствии package row в search feed;
- выгодный fixed package доходит до карточки как готовый producer-owned purchase option;
- BioShock regression подтверждён в production.

После фактического завершения обеих активных частей синхронизировать `PROJECT_ROUTES.md` / `PROJECT_DECISIONS.md`; `CURRENT_TASK.md` удалить только когда нет активной незакрытой части.

Коммуникационные инварианты:
- если ответ занимает >1 минуты, в том же ответе объяснить задержку и сделать долговечное ускорение;
- diagnostic prompt/log/config, который ассистент сам попросил прислать, не исполнять без отдельной явной команды пользователя;
- простые UI-проверки по возможности просить пользователя, сложную contract/diff диагностику выполнять инструментами.
