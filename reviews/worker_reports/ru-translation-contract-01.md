# Worker Report — `ru-translation-contract-01`

### Task

Добавлен bounded canonical contract для будущего автоматического перевода unresolved описаний игр на русский без ручного заполнения production catalog и без передачи control-plane scheduled ChatGPT.

Контракт разделён на три translation-specific части:

- `config/russian_description_translation_contract.json` — scope, ownership, immutable request identity, существующий nightly runtime reuse, retry/completeness, reserved artifact paths и downstream/fail-closed semantics;
- `config/russian_description_translation_result_contract.json` — точная форма результата semantic worker, strict identity/hash echo, status/error fields и Russian quality acceptance;
- `config/russian_description_translation_cache_entry_contract.json` — GitHub-owned reusable cache entry, exact source binding и invalidation rules.

Эта задача намеренно осталась contract-only: translation producer, runtime ingestion, resolver/cache wiring, массовый перевод и production cache population не реализовывались, потому что `WORKER_TASK_RU_TRANSLATION_CONTRACT_01.md` прямо исключает их из текущего scope.

### Verified facts

- Текущая canonical ownership-модель уже подходит для translation work: `config/execution_ownership_contract.json` оставляет exact scope/queue/order/retry/completeness/validation/persistence/downstream orchestration за GitHub, а scheduled ChatGPT разрешает только bounded semantic/external data-plane work.
- `config/daily_execution_contract.json` уже определяет один nightly production cycle и существующий scheduled ChatGPT semantic worker. Новый translation contract явно переиспользует этот runtime и запрещает отдельный recurring translation schedule.
- Taste-specific input/result schema намеренно не переиспользуется; translation имеет отдельный result/cache contract, но остаётся semantic work type внутри того же GitHub-owned nightly cycle.
- Semantic translation scope строго ограничен current records в состояниях `needs_translation` / `needs_ru_rewrite` с source quality `non_ru` / `weak_ru`.
- `ready_ru` не является translation work. `technical_source` / `missing_source` остаются отдельными GitHub-owned data-quality blockers и не маскируются как translatable source.
- Stable entity identity: `source_key = App_<steam_appid>`.
- Нормализация source text: `scripts/russian_description_quality.py::normalize_description`.
- Source version: `source_version = sha256:<source_text_sha256>`.
- Request identity: SHA-256 от LF-serialized `contract_id`, `source_key`, `source_text_sha256`. Таким образом, любое изменение нормализованного source text меняет request identity и не позволяет stale translation прикрепиться к новой версии текста.
- Worker result обязан дословно echo `request_id`, `source_key`, `source_appid`, `source_text_sha256`, `source_version`.
- GitHub acceptance требует exact current request match и `scripts/russian_description_quality.py::classify_description(translated_text_ru) == good_ru`.
- Unknown keys, stale/mismatched binding, placeholders/technical garbage, non-Russian/weak-Russian result и worker errors не cacheable и не считаются completion.
- Validated cache entry остаётся reusable без произвольной суточной ретрансляции, пока source entity/hash/version не изменились и cached Russian text продолжает проходить `good_ru`.
- Current direct deterministic `ready_ru` source имеет приоритет; translation cache предназначен только для otherwise unresolved translatable source.
- Partial worker submissions допустимы только как transport/checkpoint. Размер checkpoint не становится daily quota и не определяет completeness.
- Interactive ChatGPT не имеет права переводить production catalog item-by-item или заполнять canonical cache вручную.

### Changes

Contract/schema commit:
- `e46f4433f379ca4e7310f95afc323c70410ac5dd`

В нём добавлены/изменены:
- `config/russian_description_translation_contract.json`;
- `config/russian_description_translation_result_contract.json`;
- `config/russian_description_translation_cache_entry_contract.json`;
- `scripts/validate_russian_description_translation_contract.py`;
- `.github/workflows/validate-execution-ownership.yml` — translation contract validator добавлен в canonical ownership CI; workflow теперь также триггерится на translation contract/schema/validator changes.

Route documentation:
- `PROJECT_ROUTES.md` — добавлен маршрут `Русские описания / semantic translation contract` с canonical entry points, ownership invariants и reserved follow-up paths;
- route commit: `2727d0c5052a3a74a2a5c6df3a9855e0517d6425`.

Task state:
- `CURRENT_TASK.md` исправлен на `contract_complete_implementation_pending`, чтобы contract-only completion не выдавался за готовый producer/runtime;
- state commit: `fa4c5d7ed6a5a6b43cf9d9152bfae9fe144da7a3`.

Contractually reserved, но НЕ созданные/НЕ заполненные в этой задаче production artifacts:
- `data/production/pre_ai/chatgpt_ru_description_queue.jsonl`;
- `data/production/pre_ai/chatgpt_ru_description_status.json`;
- `data/ai_inbox/russian_descriptions/*.json`;
- `data/cache/russian_description_translations.json`.

Ни одного текущего production description вручную не переводилось.

### Validation

GitHub Actions:
- workflow: `Validate execution ownership`;
- run: `33512506228`;
- job: `99871394277`;
- head SHA: `e46f4433f379ca4e7310f95afc323c70410ac5dd`;
- conclusion: `success`.

Успешно прошли оба ключевых шага:
- `Validate component ownership boundaries` — success;
- `Validate Russian description translation contract` — success.

Translation contract validator проверяет минимум:
- canonical ids и cross-links request/result/cache contracts;
- binding к `PRODUCTION-EXECUTION-OWNERSHIP-V1` и `DAILY-VISUAL-EXECUTION-V2`;
- обязательный reuse existing nightly scheduled ChatGPT runtime;
- запрет отдельного recurring translation scheduler;
- запрет Taste-specific schema reuse;
- exact semantic scope `needs_translation` / `needs_ru_rewrite`;
- GitHub ownership scope/queue/retry/completeness/cache/downstream;
- interactive manual-fill prohibition;
- deterministic sample request identity;
- изменение source text или `App_<appid>` меняет request identity;
- request/result/cache unknown-field rejection semantics;
- exact worker echo fields;
- stale hash/version mismatch detectability;
- accepted fixture проходит `good_ru`;
- известный placeholder классифицируется `placeholder_or_technical` и не может пройти acceptance;
- English result не проходит `good_ru`;
- cache fixture сохраняет exact request/source binding.

Existing final Russian-description validator не ослаблялся и остаётся fail-closed downstream gate.

### Unresolved

Реальные implementation gaps остаются намеренно, потому что они были объявлены `Not in this task`:

- нет GitHub producer, который строит exact current `chatgpt_ru_description_queue.jsonl` из unresolved description records;
- существующий scheduled ChatGPT payload/runtime ещё не получает translation-specific work input;
- нет translation-specific GitHub ingestion/strict submission validator/cache merge implementation;
- `data/cache/russian_description_translations.json` ещё не существует как populated production cache;
- production resolver ещё не использует validated translation cache;
- текущие проблемные карточки не были массово переведены в interactive chat.

Это не blocker для contract task; это граница следующего IMPLEMENT.

### Status

`complete`

### Recommended next step

Один bounded IMPLEMENT task: реализовать GitHub-owned exact unresolved translation scope producer, подключить translation-specific work input к **существующему** nightly scheduled ChatGPT data-plane, добавить strict GitHub result ingestion/cache persistence и cache reuse в description resolver, затем rebuild через существующий downstream с неизменным `validate_russian_descriptions.py` fail-closed gate. Не создавать новый recurring scheduler и не заполнять каталог вручную.
