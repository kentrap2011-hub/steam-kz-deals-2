# WORKER TASK — Russian translation partial acceptance and diagnostic quarantine fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Do not search, read, modify, or use another repository for this task. If GitHub/tool opens another repository by default or the repository target is ambiguous, stop and switch to `kentrap2011-hub/steam-kz-deals-2`.

Task ID: `RUSSIAN_TRANSLATION_PARTIAL_ACCEPT_DIAGNOSTIC_QUARANTINE_FIX_01`
Worker slot: `ЧАТ 2`
Mode: `IMPLEMENT / VALIDATE`

## User requirement

Change the Russian-description translation system so that **one problematic game can never block valid translations for unrelated games**.

When one exact translation result fails semantic Russian-quality validation:
- do not automatically send that game for another translation;
- route that exact current request into a separate **translation diagnostic** state;
- continue accepting and persisting valid sibling translations;
- continue normal translation work for the remaining normal queue;
- show on the site/Statistics how many games are currently in this translation-diagnostic state.

The diagnostic state is not a new automatic translation retry and not a new Scheduled Task.

## Known current incident

Manual translation checkpoint 1:
- submission commit: `32caa3b35fb750cd31da7198f28e34855928edd6`;
- workflow: `Ingest Russian description translations`;
- run: `37138503097`;
- job: `111247856419`;
- checkpoint contains 20 translated result records;
- ingest stopped on exact request `2aeac6b30b8bea9fcecd9be3269154b2bb4b84fefc3345986929ee9f4e23b76e`, AppID `1237980`, because the translated result failed the `good_ru` quality gate;
- no canonical cache/status update was persisted from that checkpoint;
- current queue therefore remained at 82 at Director check time.

Do not ask the semantic worker to retranslate this failed item as part of this task.

## START / required reads

1. Read current `CHAT_PROTOCOL.md` and perform START gate.
2. Read current `CHAT_CONTEXT.md`.
3. Read this task fully.
4. Read the Russian-description route in `PROJECT_ROUTES.md`.
5. Read current:
   - `config/execution_ownership_contract.json`;
   - `config/russian_description_translation_contract.json`;
   - `config/russian_description_translation_result_contract.json`;
   - `config/russian_description_translation_cache_entry_contract.json`;
   - `config/russian_description_manual_semantic_worker_prompt.md`.
6. Inspect only the exact current ingest/runtime/workflow/status/statistics/UI files required for this change.
7. Use the failed run/job above as the pinned regression incident. Do not broadly inspect unrelated workflow history.

## Mandatory architecture preflight

This change modifies validation, unresolved-state routing and observability, so reconcile canonical contracts **before** implementation.

Required ownership:
- GitHub remains owner of scope, queue construction, result validation, diagnostic-state classification, persistence, completeness and downstream rebuild;
- semantic translation workers still only translate exact GitHub-prepared requests and submit exact-bound results;
- no ChatGPT worker chooses retry/diagnostic eligibility;
- no second recurring scheduler or automatic diagnostic semantic worker is created;
- no Scheduled Task is created/edited;
- the browser remains read-only presentation for producer-owned counts.

If the current contracts conflict with the user requirement, update the relevant canonical contract(s) first, then implement to them.

## Required behavior

### 1. Partial acceptance

A submission containing multiple exact-bound results must no longer lose all good sibling results merely because one exact item fails a per-item semantic quality check.

At minimum the pinned regression must prove:
- result A valid -> accepted/persisted;
- result B has exact valid identity but translated text fails `good_ru` -> not cached, routed to translation diagnostics;
- result C valid -> accepted/persisted;
- B does not prevent A/C from being accepted.

Preserve fail-closed identity safety.

The implementation must explicitly distinguish:
- submission/container-level corruption where partial interpretation is unsafe;
- item-level exact-bound failures that can be isolated safely.

Do not weaken AppID/request/hash/source-version checks merely to achieve partial success.

### 2. Translation diagnostic state

Introduce the smallest GitHub-owned durable/canonical state needed to represent exact translation requests that require **diagnosis rather than another translation attempt**.

For each diagnostic item preserve enough exact information to answer:
- which request/source/AppID failed;
- current exact source binding;
- why it entered diagnostics;
- when/current generation if canonically appropriate;
- what evidence/result triggered diagnostics.

Rules:
- an exact current item in translation diagnostics must not remain in the normal translation semantic queue;
- it must not be automatically retried by the normal translation worker;
- no automatic diagnostic worker is added in this task;
- a later dedicated diagnostic task may inspect it;
- define deterministic behavior when source text/binding changes, the source becomes direct ready_ru, or a diagnostic is explicitly resolved;
- stale historical diagnostic state must not poison a new current request identity.

Choose the minimal artifact/state shape consistent with existing architecture; do not create an unnecessary second backlog-management subsystem.

### 3. Current checkpoint recovery without retranslation

After the implementation is validated, process the already-submitted checkpoint 1 through the corrected canonical ingest path if its exact current bindings are still valid.

Do **not** regenerate its translations merely to make the test pass.

Expected principle:
- every valid exact-bound translation from that checkpoint is accepted;
- every exact-bound semantic-quality failure is routed to diagnostics;
- the exact number is determined by the corrected validation, not assumed in advance;
- current canonical queue/status are rebuilt honestly afterward.

If current binding movement makes any old result stale, handle it under canonical rules and report it; do not rebind it manually.

### 4. Statistics / site observability

Expose a producer-owned count for current translation diagnostics.

The site Statistics must display a clear Russian label, preferably equivalent to:

`На диагностике перевода: N`

The exact wording may be adjusted for consistency, but the meaning must be obvious.

Also preserve current translation observability:
- unresolved/translation queue counts remain honest;
- diagnostic items are distinguishable from ordinary items waiting for translation;
- timestamps must not falsely claim successful translation for a quarantined item;
- accepted valid siblings must advance success observability according to the canonical contract.

The browser must render the producer-owned value, not infer it from cards or client state.

### 5. Semantic-worker behavior

Update the canonical manual/scheduled translation contract/prompt only as needed so future workers:
- process only the normal current translation queue;
- do not see diagnostic items as ordinary translation work;
- stop/reconcile from fresh canonical state after checkpoint ingest as before;
- never self-retry a diagnostic item.

Do not modify Dossier, Deep, Fast, ranking, expiry logic, or unrelated publication behavior.

## Required regressions

Add deterministic coverage for at least:

1. 3-result checkpoint with a bad `good_ru` item in the middle; valid siblings persist.
2. Bad exact-bound item enters diagnostics and leaves normal translation queue.
3. Diagnostic item is not automatically retried by normal translation queue generation.
4. Source/binding change does not incorrectly carry stale diagnostic state onto a new request identity.
5. A later explicit/canonical resolution can clear diagnostic state safely.
6. Re-ingest/idempotency does not duplicate cache entries or diagnostic items.
7. Statistics receives and renders the current diagnostic count.
8. Existing nonblocking Russian-publication behavior remains intact.
9. Existing identity/AppID/hash fail-closed guarantees remain intact.

## Branch / PR / report

Use a dedicated implementation branch and PR. Do not write implementation directly to `main`.

Save durable report at:

`reviews/worker_reports/russian-translation-partial-accept-diagnostic-quarantine-fix-01.md`

The report must include:
- contract changes;
- exact new diagnostic-state semantics;
- pinned mixed-success regression result;
- what happened to existing checkpoint 1;
- fresh accepted/diagnostic/normal-queue counts after canonical ingest if live acceptance is reached;
- Statistics proof;
- tests/checks;
- PR number/head and remaining acceptance steps.

Do not merge the PR unless the current project protocol explicitly authorizes the worker to do so; otherwise stop ready for Director acceptance.

## CURRENT_TASK.md

You may update only your own clearly delimited task entry. Re-read immediately before every write and do not overwrite another active worker's entry. If a safe merge is not possible because of concurrent movement, skip the write and explain it in the report.

## Done when

One exact bad translation can no longer block unrelated valid translations, that item is removed from normal translation retry flow into a GitHub-owned diagnostic state, the site shows the diagnostic count, and the existing failed checkpoint can be reconciled through the canonical path without retranslation.
