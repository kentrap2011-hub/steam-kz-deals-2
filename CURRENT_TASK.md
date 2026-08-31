# CURRENT TASK

Последнее обновление: 2026-08-31

## 1. Taste V3 migration

Статус: `in_progress`.

Цель: закрыть current production scope normalized price-blind Taste V3 результатами через существующий GitHub-owned queue/ingest pipeline. Interactive chat не является массовым semantic worker.

Canonical binding:
- profile_blob_sha: `c478cda9bb7a9b024a30ca188dce4b98a2de24ea`
- taste_model_version: `taste-v3`
- taste_semantics_sha256: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`
- source_mailing_updated_at_utc: `2026-08-30T20:37:43.818127+00:00`

Подтверждённый прогресс:
- первый recovery run: 400 current-bound результатов canonically ingested после fail-closed repair;
- второй scheduled run: ещё 100 результатов; после repair/ingest canonical queue стала `134`;
- permanent fail-closed mismatch diagnostics: commit `c0201333b86f0efad6a1ee57b35b022b48698031`;
- prior pending identity typo `App_461620` safely repaired; repair run `33400223095` завершён `success`;
- следующий scheduled run стартовал с queue `134`, оценил/опубликовал `10` результатов в `data/ai_inbox/taste/2026-08-31T1407Z-001.json` и правильно остановился fail-closed до canonical ingestion;
- ingest run #40 (`33400822370`) упал не на semantics/identity, а на envelope serialization: `Ingest bindings must be an object`;
- checkpoint содержит exact canonical binding values, но они ошибочно записаны top-level вместо nested `bindings` object;
- четыре EXCLUDE-строки также используют noncanonical aliases `fit_level=weak`, `reason_code=exclude_weak`; canonical ledger requires below-threshold serialization `exclude_insufficient` + `below_moderate`;
- identity diagnostics для run #40 показывают `mismatch_count=0`;
- narrow one-shot repair commit `a6ea0b4efc79505ed623eae3d43f18696639af99` разрешает только: (1) перенос exact four top-level binding values в `bindings`; (2) explicit alias normalization для известных 4 EXCLUDE rows; (3) exact current queue appid/fingerprint/context proof; verdict/evidence/taste_factors менять запрещено;
- repair workflow run #4: `33401630279`, на последней проверке `queued`.

Следующий шаг:
1. НЕ запускать scheduled Taste task повторно, пока checkpoint `2026-08-31T1407Z-001.json` остаётся pending.
2. После конкретного сигнала проверить repair run #4 один раз.
3. Если repair зелёный: доказать inbox cleanup и canonical queue `124`; затем запускать ту же scheduled task на current queue.
4. Если repair красный: диагностировать точный canonical dry-run/transactional failure; не переоценивать 10 результатов без необходимости.
5. Taste закрыт только при canonical queue=`0` и downstream production validation.

SteamDB:
- `App_901735` остаётся blocked/retryable; exact KZ historical minimum не установлен и не выдумывается;
- SteamDB не блокирует Taste completion.

## 2. Steam fixed-package purchase options

Статус: `integration_ready_but_not_for_main_until_taste_complete`.

Старая feature branch: `purchase-options-fixed-packages-20260831`.
Свежая integration branch от current main: `purchase-options-fixed-packages-integration-20260831`.

Цель: fixed Steam Store Package (`Sub_`) становится готовым producer-owned `better_purchase_option`, когда реально покрывает >=2 visible base-game families и строго дешевле суммы их standalone current prices. UI display-only; Taste/ranking не меняются.

Подтверждено:
- StoreBrowse discovery fixed `Sub_` реализован;
- producer-side comparison/enrichment реализован;
- dynamic `/bundle/` / personalized Complete-the-Set excluded fail-closed;
- unknown extra content value=0;
- no original/remaster guessing; coverage только по фактическим included appids / canonical family membership;
- BioShock regression current members: `409710`, `409720`, `8870`;
- corrected read-only live package test прошёл зелёным;
- свежая integration branch создана от current `main` и содержит package contract, discovery producer, visual enrichment, regressions и минимальные workflow integrations;
- временный live-test workflow не переносится в production integration branch.

После Taste completion:
1. Обновить integration branch относительно свежего `main` (если появились новые commits).
2. Проверить final diff: только package files + минимальные два workflow changes.
3. Интегрировать в `main`.
4. Запустить normal pre-AI build и проверить real `fixed_package_options.json`.
5. Запустить downstream visual build и проверить real `better_purchase_option` / offers.
6. Синхронизировать `PROJECT_ROUTES.md` / `PROJECT_DECISIONS.md` после production validation.

## Definition of done

Taste:
- current GitHub-owned Taste queue=`0`;
- только current-bound V3 results canonically persisted;
- downstream producer uses normalized Taste factors per ranking contract.

Purchase options:
- fixed `Sub_` discovery/comparison works in production;
- package advice producer-owned, UI display-only;
- no edition guessing;
- production artifact and visual field validated.

`CURRENT_TASK.md` удалить только когда обе части завершены.
