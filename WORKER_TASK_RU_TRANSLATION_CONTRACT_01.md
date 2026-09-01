# WORKER TASK — CHAT 1

Task ID: `ru-translation-contract-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/ru-translation-contract-01.md`
Previous report: `reviews/worker_reports/ru-description-implement-01.md`

## Goal

Добавить bounded canonical contract для автоматического перевода проблемных описаний игр на русский так, чтобы interactive worker НЕ переводил каталог вручную, а полный scope и orchestration оставались у GitHub.

## Architecture decision to encode

Использовать существующую ownership-модель проекта:

- GitHub/GitHub Actions владеет определением полного текущего scope, exact unresolved keys, ordering, retries, completeness, validation, persistence и downstream rebuild.
- Scheduled ChatGPT data-plane разрешается использовать **только как constrained semantic translation worker** для exact immutable work input, подготовленного GitHub.
- Interactive ChatGPT worker не переводит production catalog item-by-item и не становится scheduler/backlog manager.
- Не создавать отдельный независимый recurring schedule, если translation может быть встроен в уже существующий canonical nightly ChatGPT data-plane contract. Сначала сверить `config/daily_execution_contract.json` и текущий scheduled payload pattern; новый recurring stage допустим только если canonical contracts явно требуют и авторизуют это.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- текущие scheduled ChatGPT payload/result contracts и ingestion patterns
- `reviews/worker_reports/ru-description-audit-01.md`
- `reviews/worker_reports/ru-description-implement-01.md`
- новые description quality/resolver/validator files из предыдущей реализации

## Contract requirements

Добавить canonical contract/config artifacts, достаточные для последующего IMPLEMENT, которые фиксируют минимум:

1. **Scope owner:** GitHub строит точный список только unresolved description records (`needs_translation` / `needs_ru_rewrite` или эквивалентные canonical states).
2. **Immutable identity:** каждая работа keyed by stable game/app identity + source-text hash/version so stale translation cannot attach to changed source.
3. **Input schema:** source text, source language/state, stable key/hash, минимально нужный контекст для качественного перевода; без лишних production fields.
4. **Worker role:** scheduled ChatGPT возвращает только Russian translation/result metadata по точным keys из input. Не выбирает новые игры, не расширяет scope, не управляет очередью.
5. **Output schema:** exact key/hash echo, translated Russian text, status/error, optional concise quality/provenance fields only if required.
6. **GitHub validation:** key/hash correspondence, nonempty/meaningful Russian quality gate, rejection of placeholder/technical garbage, no unknown output keys.
7. **Persistence:** validated translations сохраняются в GitHub-owned canonical cache/artifact with source hash and provenance; cache merge logic принадлежит GitHub.
8. **Freshness:** translation remains valid while source hash unchanged; changed source invalidates/requeues through GitHub-owned scope generation. No arbitrary daily retranslations.
9. **Retry/completeness:** only GitHub tracks unresolved/retry/completeness. ChatGPT does not invent retry loops or batch quotas.
10. **Downstream:** after validated cache ingestion GitHub rebuilds visual payload and existing full Russian-description validator remains final gate.
11. **Fail closed:** unresolved/invalid translation cannot silently become normal final Russian summary.
12. **No manual production fill:** interactive worker must not populate 132 current failures by hand.

## Existing runtime reuse

Prefer contractually extending/reusing the current GitHub-prepared scheduled ChatGPT data-plane interface if its ownership model supports multiple semantic work types cleanly.

Do NOT silently overload Taste-specific result schemas if their contracts are intentionally domain-specific. If a separate translation-specific input/result schema is required, define it, but still keep orchestration under the same GitHub-owned nightly production control-plane where feasible rather than inventing a separate chat-owned scheduler.

## What may change

Allowed:
- new description-translation contract/config schema files;
- minimal route/decision documentation needed to make ownership explicit;
- minimal updates to daily/execution contract only if required for explicit authorization and consistent with existing ownership;
- tests/schema validation for the contract itself.

Not in this task:
- translation producer/runtime implementation;
- mass translation;
- current production cache population;
- UI/ranking/Taste/package/duration changes;
- new independent recurring automation/schedule.

## Done when

- canonical contract explicitly authorizes the translation data-plane and preserves GitHub control-plane ownership;
- exact input/output/cache identity and validation semantics are defined;
- it is unambiguous whether existing nightly scheduled ChatGPT runtime is reused and how;
- no production descriptions are manually translated;
- contract/schema tests pass.

## Report format

Save:
`reviews/worker_reports/ru-translation-contract-01.md`

### Task
What contract was added.

### Verified facts
Ownership/runtime reuse decisions.

### Changes
Exact contract/schema/route files changed.

### Validation
Schema/tests/contract consistency checks.

### Unresolved
Any real implementation/provisioning gap.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded IMPLEMENT task for GitHub-owned translation scope + scheduled ChatGPT result ingestion.

Final response must include report path and commit refs.