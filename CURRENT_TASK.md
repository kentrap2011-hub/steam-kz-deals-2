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
- первый recovery run дал 400 current-bound результатов; после fail-closed repair они canonically ingested;
- canonical bot commit первого recovery: `35c4670699d6266cc498848e8b663d4f0530818d`;
- после него queue стала `234`;
- второй scheduled run оценил ещё `100`; первые `80` были canonically ingested и queue стала `154`;
- pending checkpoint `2026-08-31T1250Z-005.json` на 20 результатов сначала падал на `App_461620`;
- permanent fail-closed diagnostics commit: `c0201333b86f0efad6a1ee57b35b022b48698031`;
- диагностика доказала механическую identity-copy опечатку: input fingerprint оканчивался `...fc91d`, canonical current fingerprint `...fc91`, при полностью совпадающих appid и candidate_context_sha256;
- narrow one-shot repair commit: `09a45fa08ccce130789dc5fe8f349cb2d4d4a31d`;
- repair workflow run `33400223095` завершён `success`: repair, canonical dry-run, transactional ingest и commit прошли;
- active Taste inbox после этого пуст (directory absent);
- canonical `data/production/pre_ai/chatgpt_payload.json` сейчас: `ai_queue_count=134`, `ready_without_ai_count=450`, `purchase_context_line_count=584`, `complete_family_partition=true`, `sale_end_coverage=1.0`.

Следующий шаг:
1. Пользователь вручную запускает ТУ ЖЕ существующую scheduled Taste task ещё один раз, без изменения prompt.
2. Worker обязан читать current GitHub queue и увидеть `134`.
3. После run проверить опубликованные checkpoints / exact bindings / canonical ingestion.
4. Taste считается закрытым только когда canonical queue = `0` и downstream production validation доказан.

Важно:
- не создавать replacement queue и не пропускать pending rows вручную;
- canonical `ingest_taste_results.py` остаётся строгим; identity-copy repair допускается только при доказанном совпадении current appid/context и recomputed canonical context;
- SteamDB `App_901735` остаётся отдельно blocked/retryable и Taste completion не блокирует.

## 2. Steam fixed-package purchase options

Статус: `implementation_ready_on_feature_branch`.
Feature branch: `purchase-options-fixed-packages-20260831`.

Цель: если fixed Steam Store Package (`Sub_`) содержит несколько фактически видимых игровых families и объективно дешевле их отдельных current prices, producer передаёт готовый `better_purchase_option`; UI только отображает его. Taste/ranking не меняются.

Подтверждено:
- discovery fixed `Sub_` через StoreBrowse реализован;
- comparison/enrichment producer-side реализован;
- dynamic `/bundle/` / personalized Complete-the-Set остаются fail-closed;
- unknown extra content получает calculated value 0;
- package требует минимум 2 distinct visible base-game families и строгую экономию;
- edition-equivalence не угадывается: package coverage только по фактическим included appids / canonical family membership;
- BioShock current package membership для regression: `409710`, `409720`, `8870`;
- read-only live test после исправления original/remaster assumption завершён зелёным;
- package implementation пока НЕ вливать в `main`, пока Taste V3 queue не закрыта.

После Taste completion:
1. Обновить/recreate package integration branch от свежего `main`.
2. Интегрировать package feature.
3. Запустить normal pre-AI build и проверить реальный `fixed_package_options.json`.
4. Запустить downstream visual build и проверить реальные `better_purchase_option` / offers.
5. После production validation синхронизировать `PROJECT_ROUTES.md` и `PROJECT_DECISIONS.md`.

## Definition of done

Taste:
- current GitHub-owned Taste queue = `0`;
- только current-bound V3 результаты canonically persisted;
- downstream producer использует normalized Taste factors по ranking contract.

Purchase options:
- fixed `Sub_` discovery/comparison работает в production;
- package advice producer-owned, UI display-only;
- no original/remaster guessing;
- production artifact и visual field проверены.

`CURRENT_TASK.md` удалить только когда обе активные части фактически завершены.
