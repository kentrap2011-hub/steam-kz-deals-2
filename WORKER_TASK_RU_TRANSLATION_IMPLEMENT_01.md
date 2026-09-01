# WORKER TASK — CHAT 1

Task ID: `ru-translation-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/ru-translation-implement-01.md`
Previous report: `reviews/worker_reports/ru-translation-contract-01.md`

## Goal

Implement the canonical Russian-description translation path defined by the translation contracts, while preserving GitHub as control plane and reusing the existing nightly scheduled ChatGPT semantic worker.

Do not manually translate the production catalog item-by-item.

## Start condition / concurrency guard

Before changing any shared producer or workflow file, re-read current `main` and confirm whether `duration-igdb-implement-01` has finished.

If `ЧАТ 2` still has an active implementation touching the same shared files/workflows (especially final visual builder / daily visual workflow), do **not** race it. Stop before overlapping edits and report the exact overlap so the director can sequence the tasks.

Once `duration-igdb-implement-01` is durably complete or shared-file overlap is absent, continue.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `config/russian_description_translation_contract.json`
- `config/russian_description_translation_result_contract.json`
- `config/russian_description_translation_cache_entry_contract.json`
- `reviews/worker_reports/ru-description-implement-01.md`
- `reviews/worker_reports/ru-translation-contract-01.md`
- relevant current producer/resolver/workflow files only after route check

## Architecture invariants

- GitHub owns full exact unresolved scope, ordering, retry state, completeness, validation, persistence/cache merge and downstream rebuild.
- Scheduled ChatGPT is only a constrained semantic translation worker for exact immutable GitHub-prepared records.
- Interactive ChatGPT must not translate the catalog or manage a production backlog.
- Reuse the existing nightly scheduled ChatGPT data-plane; do not create a separate recurring translation scheduler.
- Translation checkpoint/batch sizes are transport details, not daily quotas.
- Existing deterministic Russian-description quality gate remains final fail-closed validation.

## What to implement

1. **Exact unresolved translation scope producer**
   - Build GitHub-owned `data/production/pre_ai/chatgpt_ru_description_queue.jsonl` (or exact contract path) from current producer/resolver states.
   - Include only contract-approved `needs_translation` / `needs_ru_rewrite` records.
   - Stable identity and request hash/version exactly per contract.
   - `ready_ru`, missing source, technical source and other non-translatable states must not be silently queued.

2. **Status/completeness artifact**
   - GitHub-owned translation status artifact per contract.
   - Exact pending/resolved/retryable/unresolved counts/keys sufficient for control-plane completeness.
   - No chat-owned queue state.

3. **Existing nightly ChatGPT payload integration**
   - Extend the canonical GitHub-prepared scheduled ChatGPT input so translation work is available as a distinct semantic work type.
   - Do not overload Taste-specific schemas in a way that weakens their contract.
   - Preserve exact GitHub-selected scope; scheduled worker must not discover or add items.

4. **Translation result submission / ingestion**
   - Strictly validate request_id/source_key/appid/hash/version echo.
   - Reject unknown keys, stale source binding, invalid statuses and malformed output.
   - Require translated text to pass existing `good_ru` quality classification before cache acceptance.
   - Worker errors/weak/non-RU/placeholder/technical output remain unresolved and do not count as completion.

5. **Canonical translation cache**
   - Create/use `data/cache/russian_description_translations.json` per contract.
   - GitHub-owned deterministic merge.
   - Exact source hash/version provenance.
   - Valid cached translation reusable while source binding remains unchanged and quality still passes.
   - Source change invalidates old binding naturally via request identity/hash.

6. **Description resolver integration**
   - Precedence must remain:
     1. meaningful direct Russian source;
     2. validated translation cache for otherwise translatable source;
     3. explicit unresolved state.
   - Never allow translation cache to overwrite a valid current direct RU source.
   - Keep placeholder/technical-source protections.

7. **Nightly orchestration / downstream rebuild**
   - Wire producer -> exact translation work input -> scheduled ChatGPT result interface -> GitHub ingestion/cache -> visual rebuild through the existing canonical nightly control-plane.
   - No new independent recurring workflow/schedule unless an existing canonical contract explicitly requires one.
   - If the current scheduled ChatGPT runtime executes separately from the GitHub workflow, implement only the repo-defined handoff artifacts/interface that the existing runtime already consumes; do not invent a second scheduler.

8. **Validation**
   - Contract validator remains green.
   - Queue identity changes when source text changes.
   - Non-translatable states excluded.
   - Unknown/stale result rejected.
   - Good Russian result accepted into cache.
   - Placeholder/English/weak result rejected.
   - Cache reuse works for unchanged source.
   - Valid direct RU source wins over translation cache.
   - Existing full Russian-description validator remains fail-closed.

## Production processing rule

The worker may run bounded synthetic/spot validation only.

Do **not** manually translate or fill the current 132 unresolved descriptions.

After implementation, GitHub/GitHub Actions must build the real current production scope automatically. If the scheduled ChatGPT runtime needs to process real translations, it must receive the GitHub-prepared exact work artifact through the canonical runtime path; the interactive worker must not substitute itself.

## Shared-file conflict rule

Because `duration-igdb-implement-01` may touch the final visual builder and daily workflow, do not overwrite or revert its changes.

Before every write to a shared file:
- re-read current `main` version;
- preserve already-merged duration implementation;
- if changes cannot be cleanly composed, stop and return `blocked` with exact overlapping files rather than guessing.

## Hard boundaries

Do not change:
- Taste semantics or Taste queue logic except minimal generic payload envelope compatibility explicitly required by existing contracts;
- duration provider/scoring/cache logic;
- package economics;
- ranking weights;
- UI except strictly necessary compatibility for existing producer fields;
- commercialization guard.

Do not add generic external machine translation providers.
Do not create a separate recurring translation automation.
Do not manually process the catalog.

## Done when

- GitHub can automatically build exact translation work for current unresolved translatable descriptions;
- the existing scheduled ChatGPT data-plane has a contract-valid translation work interface;
- GitHub can strictly ingest/validate/cache matching translation results;
- resolver reuses validated cache correctly;
- control-plane completeness remains GitHub-owned;
- tests/contract checks pass;
- no production descriptions were manually translated by the interactive worker;
- any shared duration changes already on main remain intact.

If the repo-side implementation is complete but the scheduled runtime cannot yet consume/return the new translation work because a runtime-side canonical update is separately required, report that exact gap as the next bounded step rather than inventing a new scheduler.

## Report format

Save:
`reviews/worker_reports/ru-translation-implement-01.md`

### Task
What was implemented.

### Verified facts
Ownership, runtime reuse, scope generation and shared-file concurrency status.

### Changes
Exact files and commits.

### Validation
Tests/workflow refs and bounded fixtures.

### Production handling
State explicitly that no interactive manual catalog translation was performed; explain what GitHub now owns/produces and what existing scheduled ChatGPT runtime consumes.

### Unresolved
`none` or exact runtime/integration/blocking gap.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only.

Final response must include report path and commit refs.