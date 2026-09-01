# Worker Report — ru-translation-implement-01

### Task
Implemented the repo-side canonical Russian-description translation path defined by the existing translation contracts without manually translating the production catalog.

The implementation adds:
- a GitHub-owned exact unresolved translation scope producer for contract-approved `needs_translation` / `needs_ru_rewrite` records;
- immutable request/source binding using `App_<appid>` plus normalized source-text SHA-256/version;
- a distinct `russian_description_translation` semantic work type in the existing canonical ChatGPT payload instead of reusing Taste result semantics;
- strict translation result validation/ingestion;
- a canonical GitHub-owned translation cache;
- cache-aware description resolution with direct valid Russian remaining higher priority than cached translation;
- event-driven GitHub ingestion and downstream visual rebuild handoff, without creating a second recurring translation scheduler;
- deterministic regression coverage for identity invalidation, translatable-scope selection, stale/unknown/duplicate result rejection, Russian quality validation, cache reuse, source-change invalidation, and direct-RU precedence.

### Verified facts
- GitHub remains the control-plane owner for prepared scope, request identity, validation, persistence/cache merge and downstream rebuild.
- Scheduled ChatGPT remains intended only as the constrained semantic data-plane worker for exact GitHub-prepared records. No separate recurring translation scheduler was created.
- Interactive ChatGPT did not discover or manage a production translation backlog and did not manually translate the catalog.
- `duration-igdb-implement-01` had durably completed its overlapping implementation before shared visual integration. The translation change was composed onto the then-current `main`; duration changes were not reverted.
- The final resolver priority implemented is: meaningful current direct Russian -> exact validated translation-cache hit for the current source binding -> explicit unresolved state.
- Translation cache identity is source-bound. A source-text change changes the hash/request identity, so the old cached translation does not attach to the new source.
- Current `main` does not contain `data/production/pre_ai/chatgpt_ru_description_queue.jsonl` or `data/production/pre_ai/chatgpt_ru_description_status.json` after the last producer dedupe fix. Therefore a successful current production scope publication is not yet proven.
- The repo exposes the new translation work through the canonical ChatGPT payload interface, but this implementation evidence does not prove that the already-existing scheduled ChatGPT runtime has been updated to consume and return the new translation work type end-to-end.

### Changes
Primary implementation files and commits:

- `scripts/russian_description_translation_runtime.py`
  - `5b6db647d934dec832ce6e9e3baa239a4e8ee6ac`
  - source/request binding, cache validation/reuse, direct-RU priority, Store Russian-source fetch helper.
- `scripts/build_russian_description_translation_queue.py`
  - initial producer: `b3616d32cc85f4298ea85fd0e9f465997c939f56`
  - immutable-identity dedupe correction: `2b9cdb470e89bb9798a3a3f93d8ac97ebc0cf374`.
- `scripts/ingest_russian_description_translations.py`
  - `361f14a899269154f80021b773810f4260418474`
  - strict request/source echo validation and deterministic cache merge.
- `scripts/test_russian_description_translation_runtime.py`
  - `bbb94925edb052ebccca65eff4a9c3768f1c0738`
  - 9 deterministic translation runtime regressions.
- `data/cache/russian_description_translations.json`
  - `7138262a9463a45833f2f92b19fe2bd9fac1d585`
  - canonical cache initialized empty; no production translations manually seeded.
- `.github/workflows/ingest-russian-description-translations.yml`
  - `c1d2b90ea0fb4ffd7ab2a9cb4dafa535c1814952`
  - event-driven submission ingestion and visual rebuild dispatch; not a recurring scheduler.
- `.github/workflows/build-pre-ai-store-snapshot.yml`
  - `adce5498442b08a750f662b379d9d6313bc98802`
  - translation scope generation attached to the existing pre-AI control-plane and translation work exposed as a distinct semantic payload type.
- `scripts/build_visual_feed_v2.py`
  - generated integration commit `e9faeac8c0574c4662122cd30e8b3e135e2a36df`
  - resolver now reuses only exact validated translation-cache entries and preserves direct-RU precedence. This integration also corrected an existing local variable-shadowing issue so description resolution metadata is not overwritten by the Taste short-description string.

Bounded implementation/validation helpers also landed during the work:
- `scripts/patch_russian_translation_visual_once.py` — `15a4405f15fe26f69079daca697819cf73ba540a`;
- `.github/workflows/patch-russian-translation-visual-once.yml` — `85f019add87196a516aeb0e07361ab13b237334d`;
- `.github/workflows/build-russian-translation-scope-once.yml` — `adbb02d0676cbf3bb4eef306c90dc34abd309b65`.

Director closeout marker before this report:
- `ab846c047dcd11f98c67728729a335bec09758bd` — implementation committed, required report missing.

### Validation
Successful bounded validation:

1. Translation visual integration workflow:
   - run `33516488010`;
   - job `99884696432`;
   - conclusion: `success`;
   - passed exact cache-aware visual patch, translation runtime regressions, translation contract validation and `py_compile` of the visual producer.

2. Translation scope validation workflow before real scope build:
   - run `33516656695`;
   - job `99885270763`;
   - validation stage passed:
     - `ARCHITECTURE_OWNERSHIP_VALID`;
     - `RUSSIAN_DESCRIPTION_TRANSLATION_CONTRACT_VALID`;
     - `Ran 9 tests ... OK`.
   - the subsequent real scope build correctly exposed a duplicate-context producer defect for one immutable request identity and stopped fail-closed rather than publishing ambiguous scope.
   - that defect was corrected in `2b9cdb470e89bb9798a3a3f93d8ac97ebc0cf374` by deduplicating on immutable identity while permitting only deterministic merge of non-identity context.

3. Synthetic end-to-end fixture coverage verifies:
   - only unresolved translatable states are queued;
   - request identity changes when source text changes;
   - good Russian translation is accepted into exact cache;
   - stale/unknown/duplicate submissions are rejected;
   - placeholder and English output are rejected by the Russian quality gate;
   - unchanged-source cache reuse works;
   - source change misses old cache naturally;
   - current valid direct Russian wins over cache.

Known unrelated workflow blocker:
- existing pre-AI workflow run `33516400092`, job `99884402596`, failed before the new translation stages on a pre-existing package/UI regression:
  `AssertionError: missing package UI override contract: window.renderPackageDeal=function(g)`.
- This was outside `ru-translation-implement-01` boundaries and was not modified here.
- Execution-ownership validation around the same implementation state remained green (`33516400201`).

No successful real production-scope build after the final dedupe correction is recorded in the implementation evidence, so production queue/status completeness is not claimed.

### Production handling
No interactive/manual production catalog translation was performed. In particular, the worker did not manually fill the previously identified unresolved production descriptions and did not seed placeholder Russian descriptions into the cache.

GitHub now owns the repo-side mechanics for:
- deriving exact translation candidates from canonical producer/resolver state;
- assigning immutable request identity/source provenance;
- exposing translation as a separate semantic work type in the canonical scheduled ChatGPT payload;
- validating matching results fail-closed;
- accepting only `good_ru` translated text;
- persisting exact-source-bound validated cache entries;
- reusing cache entries only while the source binding remains unchanged;
- rebuilding the visual payload after accepted translation ingestion.

The intended existing scheduled ChatGPT runtime input is the GitHub-prepared `russian_description_translation` work block/queue referenced by the canonical ChatGPT payload. The runtime must process only those exact records and return the translation result contract; it must not discover scope or own retry/completeness state.

However, an end-to-end production run proving that the existing scheduled runtime currently consumes and returns this newly added work type was not completed during this implementation. No second scheduler was created as a workaround.

### Unresolved
Two linked acceptance gaps remain:

1. After the final immutable-identity dedupe fix (`2b9cdb470e89bb9798a3a3f93d8ac97ebc0cf374`), a successful current production translation scope/status publication has not been recorded; both canonical generated files are absent on current `main`.
2. End-to-end consumption/return of the new translation work type by the already-existing scheduled ChatGPT runtime has not been demonstrated. If that runtime requires a separate canonical runtime-side binding update, that is the next bounded integration gap; a new scheduler must not be invented.

The unrelated pre-existing package/UI regression can also block the full canonical pre-AI workflow before translation stages, but it is not a translation implementation defect and remains outside this task's allowed scope.

### Status
`needs_fix`

### Recommended next step
Run one bounded scheduled-runtime acceptance after the existing pre-AI blocker is cleared: rebuild the current GitHub-owned translation scope with the final dedupe code and verify one exact GitHub-prepared translation record round-trips through the existing nightly ChatGPT worker -> strict GitHub ingestion/cache -> visual rebuild, implementing only a missing runtime-side binding if that acceptance proves it is required.
