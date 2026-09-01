# WORKER TASK — CHAT 1

Task ID: `ru-translation-runtime-acceptance-01`
Mode: `ACCEPTANCE`
Report: `reviews/worker_reports/ru-translation-runtime-acceptance-01.md`

## Goal

Prove one real end-to-end Russian-description translation round-trip through the existing canonical architecture:

`GitHub-published exact request -> existing scheduled ChatGPT semantic worker -> strict GitHub ingestion/cache -> visual rebuild -> translated card output`.

This is acceptance of the already implemented path, not a catalog translation batch.

## Current proven state

The package/UI blocker is cleared. Canonical pre-AI workflow now publishes real translation scope successfully.

Latest proven scope from `package-ui-blocker-fix-01`:
- `status=translation_required`
- `translation_queue_count=155`
- `resolved_direct_ru_count=389`
- `resolved_translation_cache_count=0`
- `nontranslatable_blocker_count=26`

Use current `main` and current published queue/status, not these historical counts if they have changed.

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
- `reviews/worker_reports/ru-translation-implement-01.md`
- `reviews/worker_reports/package-ui-blocker-fix-01.md`
- current `data/production/pre_ai/chatgpt_payload.json`
- current `data/production/pre_ai/chatgpt_ru_description_queue.jsonl`
- current `data/production/pre_ai/chatgpt_ru_description_status.json`
- exact current scheduled-runtime instructions/contract if referenced by canonical payload or routes

## Architecture invariants

- GitHub owns scope, queue, ordering, retry/completeness, identity, result acceptance, cache merge and rebuild.
- Scheduled ChatGPT processes only exact GitHub-prepared work.
- Interactive worker must not choose an arbitrary game outside the published queue or manually process multiple catalog entries.
- No new recurring scheduler/automation.
- No daily translation quota.
- One record here is an acceptance probe only, not a production batch policy.

## Acceptance procedure

1. **Verify current scope publication**
   - Confirm current queue/status exist and are internally consistent.
   - Select exactly one record using a deterministic rule defined by GitHub state (for example first canonical pending record by existing queue order). Do not hand-pick a convenient title.
   - Record its immutable request identity/hash/version.

2. **Verify scheduled-runtime binding**
   - Determine whether the existing scheduled ChatGPT runtime currently recognizes the `russian_description_translation` semantic work type and can return the required result contract.
   - If the runtime-side binding is missing, implement only the minimal canonical runtime binding/update needed for this existing scheduled worker. Do not create a second schedule.
   - Preserve Taste and other existing work types.

3. **Run/observe one real semantic round-trip**
   - Process exactly that GitHub-prepared request through the existing scheduled ChatGPT data-plane.
   - The translation must be a natural Russian rendering of the supplied source description, preserving meaning and not inventing game facts.
   - Result must echo exact identity/hash/version fields per contract.
   - Do not process additional queue records as part of this acceptance.

4. **Strict GitHub ingestion**
   - Submit through the canonical result interface only.
   - Confirm stale/identity mismatch protection is active.
   - Confirm `good_ru` quality gate accepts the result.
   - Confirm one cache entry is persisted with exact source binding.

5. **Rebuild / visible propagation**
   - Run the canonical downstream path triggered by accepted ingestion.
   - Confirm the translated Russian description is used for the matching card only when no higher-priority direct Russian source exists.
   - Confirm direct-RU precedence remains intact.

6. **Completeness semantics**
   - After one accepted record, remaining pending items must remain pending under GitHub-owned status.
   - Do not mark the 155-record scope complete just because the acceptance record passed.
   - No ad hoc continuation in interactive chat.

## Important runtime constraint

If there is no supported way to trigger/run the existing scheduled ChatGPT runtime immediately from this worker context:
- do not simulate the semantic worker by manually translating in interactive chat and calling that end-to-end acceptance;
- instead verify/implement the runtime binding, leave the one exact acceptance record prepared, and report the exact remaining operational action needed to let the existing scheduled runtime execute it;
- status should then be `blocked` or `needs_user_decision`, not `complete`.

A synthetic fixture is not sufficient for `complete` because repo-side synthetic coverage already exists. `complete` requires one real scheduled-runtime semantic round-trip.

## Hard boundaries

Do NOT:
- translate multiple production descriptions;
- manually fill the cache outside canonical ingestion;
- invent a second recurring ChatGPT task;
- alter ranking/Taste/duration/package/UI semantics;
- change translation scope selection rules merely to make acceptance easier;
- weaken identity or Russian-quality validation;
- treat one accepted record as queue completeness.

## Done when

### Complete
- current production scope/status publication verified;
- existing scheduled ChatGPT runtime binding for translation confirmed or minimally fixed;
- one exact current queue request actually round-trips through the scheduled runtime;
- GitHub strict ingestion accepts it and persists one exact cache entry;
- canonical rebuild uses that cached translation in the matching visible output;
- remaining scope stays pending under GitHub control;
- no second scheduler and no manual catalog processing.

### Blocked
If real scheduled-runtime execution cannot be triggered/observed from this context, repo/runtime binding is still made as complete as safely possible and the exact external operational blocker/action is documented.

## Report format

Save:
`reviews/worker_reports/ru-translation-runtime-acceptance-01.md`

### Task
Exact acceptance performed.

### Verified facts
Current queue/status and selected immutable request identity.

### Runtime binding
Whether existing scheduled runtime already supported translation; exact changes if needed.

### Acceptance evidence
Runtime execution/task ref, result ref, ingestion workflow/run, cache entry identity, rebuild/deploy ref.

### Completeness
Remaining pending count/status after the single acceptance record; explicitly state one-record acceptance is not a quota/completeness rule.

### Changes
Exact files/commits, or `none` if no binding fix was needed.

### Unresolved
`none` or exact operational blocker.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only.

Final response must include report path and exact refs.