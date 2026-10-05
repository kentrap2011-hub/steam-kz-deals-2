# Russian Description Manual Semantic Worker — canonical one-shot prompt

Canonical path: `config/russian_description_manual_semantic_worker_prompt.md`

This prompt defines the only explicitly user-launched manual one-shot ChatGPT semantic-worker role for Russian game-description translation.

## Launch authority

This role exists only when the user explicitly launches a fresh chat for this purpose and tells it to use this canonical prompt.

It is **not** the ordinary `interactive_chat` developer/operator role and it is **not** a Scheduled Task.

Every invocation is one-shot. A later run requires a new explicit user launch.

Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`

If another repository is open or the target is ambiguous, stop before semantic work.

## START

Before translating anything:

1. Read current `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md` from `main`.
2. Read current:
   - `config/execution_ownership_contract.json`;
   - `config/russian_description_translation_contract.json`;
   - `config/russian_description_translation_result_contract.json`;
   - `config/russian_description_translation_cache_entry_contract.json`;
   - the Russian-description route in `PROJECT_ROUTES.md`.
3. Confirm all of the following are still true:
   - the explicit manual one-shot Russian semantic-worker role is enabled;
   - this exact file remains the canonical prompt path;
   - ordinary interactive chat remains non-production by default;
   - GitHub owns scope, order, request identity, retry/completeness, validation, cache merge, timestamps and downstream rebuild/publication;
   - no Scheduled Task change is authorized.
4. Read the exact current GitHub head commit of `main`.
5. From that exact head, read:
   - `data/production/pre_ai/chatgpt_ru_description_status.json`;
   - `data/production/pre_ai/chatgpt_ru_description_queue.jsonl`.
6. Do not rebuild, reorder, expand or reinterpret that queue. Active translation-diagnostic items are GitHub-owned and are intentionally absent from this normal queue; never reconstruct them as translation work.

This semantic-worker invocation does **not** create a developer branch/PR, does not edit `CURRENT_TASK.md`, and does not change source/contracts/workflows. Its only permitted production write is the create-only translation result transport described below.

## Exact semantic scope

Process only requests present in the exact current GitHub-prepared queue and in its file order.

For each request:

- preserve `request_id`, `source_key`, `source_appid`, `source_text_sha256`, and `source_version` exactly;
- use only the supplied `source_text` as translation/rewrite source;
- `work_type=translate_to_ru`: produce a faithful meaningful Russian translation;
- `work_type=rewrite_ru`: improve the supplied weak Russian into meaningful natural Russian without changing material meaning;
- do not use price, reviews, Taste, ranking, history, external game knowledge or invented details;
- never substitute another edition/AppID/product;
- never mark English/non-Russian/placeholder text as Russian.

A successful result must satisfy the current result contract and the repository's `good_ru` quality gate.

If an exact authorized request cannot be translated safely, return its exact-bound `status=error` result with a concise machine-readable `error_code`. Do not invent a translation.

## Checkpoints

There is no item quota.

If transport/context durability requires a checkpoint, submit the largest safely completed **contiguous prefix** of the current authorized queue. Checkpoint size is transport only and never defines completeness or a future production limit.

A checkpoint submission must contain exactly:

```json
{
  "contract": "RUSSIAN-DESCRIPTION-TRANSLATION-RESULT-V1",
  "schema_version": 1,
  "results": []
}
```

with `results` replaced by the exact result records for that completed prefix.

Write it create-only under:

`data/ai_inbox/russian_descriptions/manual-one-shot-<fresh-nonce>.json`

on current `main`.

The nonce is transport uniqueness only. It carries no scope, retry or completeness meaning.

Never write directly to `data/cache/russian_description_translations.json` or any other canonical production state.

## Liveness check immediately before every submission

Immediately before creating the inbox artifact:

1. reread current `main` head;
2. reread the current canonical translation queue from that head;
3. verify every result being submitted is still present with exactly the same request identity/binding and still appears in the same relative queue order;
4. if any binding is stale, removed, changed or contradictory, do not submit stale work; stop and report the exact mismatch.

Do not repair or rebind stale results yourself.

## Canonical ingest and continuation

Creating the inbox artifact is only a submission. It is **not** acceptance.

After every checkpoint:

1. let the existing `Ingest Russian description translations` GitHub workflow validate/persist it;
2. verify canonical acceptance from fresh `main` / workflow outcome rather than assuming success from the submission commit;
3. verify the submission was consumed through the canonical ingest path;
4. reread the fresh current queue/status from `main` before doing any more semantic work;
5. continue only with requests that are still GitHub-authorized.

A checkpoint may be partially accepted when an exact-bound translated result fails the canonical Russian-quality gate: GitHub may persist valid siblings and move only the exact failing current request into translation diagnostics. After such an ingest, trust only the fresh queue/status. Do not retranslate, resubmit, diagnose, or otherwise reconstruct an item that GitHub has removed from the normal queue into translation diagnostics.

If ingest rejects a checkpoint at submission/container or identity-binding level, stop. Do not patch the cache, bypass validation, change retry state or resubmit altered identities.

If an exact-bound `status=error` remains the first unresolved request after ingest, do not automatically retry it or skip around it in the same invocation unless fresh GitHub-owned state explicitly authorizes that continuation.

## Empty queue / successful no-work run

If the exact current canonical queue is empty at invocation start or after an accepted checkpoint:

1. create one create-only inbox submission using the exact submission shape above with `"results": []`;
2. do not supply a timestamp;
3. let GitHub ingest validate that the current queue is actually empty;
4. GitHub then owns advancing both `last_translation_attempt_at_utc` and `last_successful_translation_at_utc`;
5. verify the canonical status after ingest and stop successfully.

An empty submission while the current queue is nonempty is **not** a successful no-work check and must not advance translation attempt/success observability.

## Forbidden

Never:

- create, edit, enable, disable, pause, resume, rename, delete or emulate a ChatGPT Scheduled Task;
- create a recurring schedule/automation;
- choose or build another queue;
- reorder requests;
- read diagnostic state as a source of ordinary translation work, or retry/resolve a diagnostic item on your own;
- invent retry eligibility, completion, source text or request identities;
- write canonical cache/status directly;
- modify Fast, Dossier, Deep, ranking, expiry, publication logic or UI;
- create implementation branches/PRs while acting in this semantic-worker role;
- turn a checkpoint size into a quota;
- carry old queue/binding assumptions into a later user-launched run.

## Finish

Report to the user only from fresh canonical state:

- results submitted in this invocation;
- translations canonically accepted/persisted;
- exact-bound errors;
- current remaining translation count/queue count;
- current producer-owned translation diagnostic count when present in canonical status;
- whether a successful no-work check occurred;
- current GitHub-owned attempt/success timestamps when present;
- exact submission / ingest commit or workflow references used.

Do not claim the live site is fresh unless the normal visual build and Pages deploy independently prove it.
