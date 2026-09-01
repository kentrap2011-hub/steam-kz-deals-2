# Taste ingest blocker diagnosis 01

### Task
Проверен текущий GitHub-owned Taste ingestion blocker для 9 файлов в `data/ai_inbox/taste/`: состав batch, уникальность `result.key`, canonical guards/contracts, фактический failed GitHub Actions run и минимальный безопасный recovery path. Submission-файлы, semantic state, cache, `CURRENT_TASK.md` и ingestion logic не изменялись.

### Verified facts

Текущие 9 неингестированных submission-файлов в `main`:

- `data/ai_inbox/taste/chatgpt-20260901-0059-001.json` — 10 results
- `data/ai_inbox/taste/chatgpt-20260901-0100-002.json` — 10 results
- `data/ai_inbox/taste/chatgpt-20260901-0101-003.json` — 10 results
- `data/ai_inbox/taste/chatgpt-20260901-0102-004.json` — 20 results
- `data/ai_inbox/taste/chatgpt-20260901-0104-005.json` — 20 results
- `data/ai_inbox/taste/chatgpt-20260901-0106-006.json` — 20 results
- `data/ai_inbox/taste/chatgpt-20260901-0108-007.json` — 20 results
- `data/ai_inbox/taste/chatgpt-20260901-0110-008.json` — 20 results
- `data/ai_inbox/taste/chatgpt-20260901-0112-009.json` — 17 results

Итого: 147 results, 147 уникальных `result.key`.

**Duplicate keys между текущими 9 inbox-файлами: none.** Следовательно, классификация `identical/conflicting` неприменима: дублирующихся `result.key` нет. Есть похожий, но контрактно другой случай: `Sub_4156` имеет `appid=6800`, а отдельно существует `App_6800`; это разные keys и guard `process_taste_inbox.py` сравнивает именно `result.key`, поэтому это не duplicate-key violation.

Все 9 файлов имеют одинаковые текущие bindings: profile blob `c478cda9bb7a9b024a30ca188dce4b98a2de24ea`, model `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`, source mailing timestamp `2026-08-31T20:36:53.491618+00:00`.

Canonical duplicate guard действительно существует в `scripts/process_taste_inbox.py`: после чтения всех inbox-файлов он проверяет `len(set(all_keys)) != len(all_keys)` и fail-closed завершает работу с `Duplicate taste key across inbox files`. На текущем batch этот guard не срабатывает.

Фактический последний ingest run — GitHub Actions run `33440037739` (`Ingest context-bound taste batch`, commit `172adbb826d0727906b37ff2b438a44c83692b7e`). `validate_taste_v3_contract.py` прошёл. Затем `process_taste_inbox.py` успешно провёл canonical per-file ingest всех 9 файлов во временной транзакции: 10+10+10+20+20+20+20+20+17 = 147 results. После rebuild `safe_cache_hit_count` вырос ровно с 492 до 639 (+147), а `ai_required_count` уменьшился с 181 до 34 (-147). Значит все 147 Taste results были приняты как валидные cache hits; повторная Taste semantic оценка этих 147 игр не нужна.

Run упал только на финальном transactional proof. До ingest manifest имел `ai_queue_count=147`; после ingest/rebuild — `ai_queue_count=3`. Failed checks были ровно:

- `ai_queue_decrement_exact`
- `queue_file_count_exact`
- `all_ingested_keys_removed_from_queue`

Причина оставшихся 3 строк canonical и ожидаема для payload builder: `scripts/build_pre_ai_chatgpt_payload.py` намеренно оставляет уже `cache_hit` Taste subject в AI queue, если family имеет `requires_ai_base_support=true`; для такой строки `work_required=["resolve_base_support_condition"]`. Текущий `data/production/pre_ai/family_graph.json` содержит ровно 3 `external_base_addon` family с этим флагом, и все три находятся в первом submission и имеют Taste `INCLUDE/moderate`:

- `App_1017030` — base appid `332950`
- `App_1019930` — base appid `332950`
- `App_1022850` — base appid `332950`

Таким образом, blocker — не duplicate-key hazard и не конфликт результатов. Это несовместимость transactional proof в `scripts/process_taste_inbox.py` с уже существующей двухэтапной семантикой queue builder: proof ошибочно предполагает, что каждый ingest key обязан полностью исчезнуть из queue после Taste ingest, хотя canonical payload builder разрешает тому же key остаться для отдельной `resolve_base_support_condition` работы.

Поведение fail-closed является безопасным и ожидаемым в том смысле, что workflow не коммитит runner-local partial writes, не удаляет inbox и не создаёт receipt при недоказанной транзакции. Но конкретное proof-условие сейчас слишком строго относительно canonical queue semantics.

### Changes
`none` (кроме этого report-файла).

### Validation

Вывод подтверждён следующими canonical источниками:

- `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `CURRENT_TASK.md`, `PROJECT_ROUTES.md` — ownership/route и зафиксированное состояние задачи.
- `config/execution_ownership_contract.json` — GitHub владеет ingestion/persistence/completeness; interactive worker не должен вручную подменять backlog/ingest.
- `config/taste_result_contract.json` и `config/taste_cache_entry_contract.json` — binding/result/cache-hit требования.
- `scripts/process_taste_inbox.py` — duplicate-key guard, canonical per-file ingest и transactional proof.
- `scripts/build_pre_ai_chatgpt_payload.py` — cache-hit family с `requires_ai_base_support=true` намеренно остаётся в AI queue с `work_required=["resolve_base_support_condition"]`.
- `data/production/pre_ai/family_graph.json` — ровно три `external_base_addon` family с `requires_ai_base_support=true`: `App_1017030`, `App_1019930`, `App_1022850`.
- `.github/workflows/ingest-taste-batch.yml` — canonical atomic ingestion workflow.
- GitHub Actions run `33440037739` — фактическая ошибка возникает после успешного ingest/rebuild именно на transactional proof; duplicate-key guard не срабатывает.

Отдельного уже готового canonical recovery workflow, который обходит эту proof-несовместимость без изменения guard/proof logic, не найдено. Существующий canonical ingestion path уже запускается, но останавливается на неверном ожидании `queue -> 0`.

### Unresolved
Не требуется выбирать между конфликтующими Taste payloads: конфликтующих duplicate keys нет. Отдельная семантическая работа по `resolve_base_support_condition` для трёх external-base addon family остаётся штатной downstream работой и не должна маскироваться как повторная Taste evaluation.

### Status
`needs_fix`

### Recommended next step
Исправить **только GitHub-side transactional proof** в `scripts/process_taste_inbox.py`, чтобы после успешного Taste ingest он разрешал ingest key оставаться в `chatgpt_taste_queue.jsonl` исключительно как доказанный `cache_hit` с `work_required=["resolve_base_support_condition"]` для family, где `requires_ai_base_support=true`, и рассчитывал ожидаемый `ai_queue_count` с учётом таких retained base-support rows; затем повторно запустить canonical `.github/workflows/ingest-taste-batch.yml`. Submission-файлы и их Taste results не менять и не переоценивать.