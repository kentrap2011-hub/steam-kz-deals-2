# WORKER TASK — CHAT 1

Task ID: `ru-translation-provider-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/ru-translation-provider-recon-01.md`

## Goal

После source recon, который не нашёл широкого готового второго источника русских описаний, сравнить обычные machine-translation API/services, которые GitHub Actions может вызывать напрямую. Цель — по возможности не использовать ChatGPT для перевода описаний вообще.

Это НЕ задача на перевод текущих 132 карточек и НЕ задача на реализацию.

## Context

- Steam RU remains canonical primary source.
- Ready-Russian secondary sources do not provide broad low-friction coverage; Wikimedia is only a conditional subset and adds CC BY-SA attribution/share-alike complexity.
- Translation is still needed for some unresolved cards.
- User preference: prefer a direct automated source/service over using ChatGPT when feasible.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `reviews/worker_reports/ru-description-source-recon-01.md`
- `reviews/worker_reports/ru-description-implement-01.md`

## Providers to compare

Compare 3–5 realistic machine-translation options suitable for server-side GitHub Actions, prioritizing official APIs. Include at least:
- DeepL API
- Google Cloud Translation
- Yandex Cloud Translate

Optionally include one additional credible provider only if it materially improves the comparison (for example Microsoft Azure Translator). Do not pad the list.

## What to establish for each

1. Russian translation quality reputation/fit for short game descriptions.
2. Official API availability and server-side GitHub compatibility.
3. Auth model / secrets required.
4. Pricing/free tier and likely cost model for this project; do not translate the catalog to estimate cost, use provider pricing units and a bounded illustrative calculation only if useful.
5. Rate/size limits relevant to short descriptions.
6. Terms/licensing/data retention/confidentiality constraints that matter for sending Steam store text and storing translated output.
7. Whether translated output may be persistently cached/reused in our GitHub-owned cache.
8. Operational stability/maintenance risk.
9. Whether deterministic GitHub-owned request/response flow can satisfy current ownership contract without scheduled ChatGPT.
10. Quality-control implications: existing `russian_description_quality.py` gate remains final validation; identify whether provider confidence metadata is useful or not.

## Decision output

Recommend:
- one primary translation API;
- at most one fallback;
- executor class, expected to be `GitHub-direct` if feasible;
- whether ChatGPT translation can be removed from the planned architecture entirely or should remain only an exceptional manual/semantic fallback.

Prefer low operational complexity and predictable cost over marginal quality differences unless evidence strongly favors otherwise.

## Hard boundaries

Do NOT:
- translate any real production descriptions;
- process the 132 unresolved cards;
- create queues/caches/workflows/contracts;
- add secrets;
- modify production code;
- use ChatGPT as a translator in this task;
- change ranking/Taste/duration/package/UI.

Web/public documentation research is allowed. A provider sandbox/example may be inspected only if no production game text is submitted.

## Done when

- 3–5 providers compared with verified current public facts;
- one primary recommendation and optional fallback chosen;
- it is clear whether GitHub can call the provider directly;
- cost/auth/licensing implications are clear enough for a contract decision;
- no production data was translated.

## Report format

Save:
`reviews/worker_reports/ru-translation-provider-recon-01.md`

### Task
What was compared.

### Verified facts
Compact provider comparison table.

### Recommendation
Primary + optional fallback.

### Executor
`GitHub-direct` / other with reason.

### ChatGPT impact
One of:
- `chatgpt_not_needed`
- `chatgpt_exceptional_fallback_only`
- `chatgpt_still_required`

### Cost / provisioning
Keys, account/billing requirements, rough pricing model.

### Changes
`none` except report.

### Validation
Official provider docs + canonical repo evidence.

### Unresolved
Real unknowns only.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded contract task for the chosen GitHub-direct translation service.

Final response must include report path and commit ref.