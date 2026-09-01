# WORKER TASK — CHAT 1

Task ID: `ru-description-source-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/ru-description-source-recon-01.md`
Previous reports:
- `reviews/worker_reports/ru-description-audit-01.md`
- `reviews/worker_reports/ru-description-implement-01.md`

## Goal

До проектирования ChatGPT-перевода проверить, можно ли закрывать unresolved descriptions уже готовыми русскими описаниями из внешних структурированных источников.

Перевод считается последним fallback, а не default path.

## Context

Current deterministic gate found 132/442 visible cards invalid under Russian-description quality rules. Existing Steam Russian StoreBrowse path already supplies good Russian descriptions for many cards, but unresolved cases remain.

The previous proposal to immediately add a translation contract is intentionally deferred pending this source recon.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- relevant description source/producer files
- `reviews/worker_reports/ru-description-audit-01.md`
- `reviews/worker_reports/ru-description-implement-01.md`

## What to investigate

Compare a small set of realistic external sources that may already expose ready Russian game descriptions. Prefer official/structured/API-accessible sources.

For each candidate establish:
1. Does it actually provide Russian-localized description text, not merely English text or UI labels?
2. Coverage likely relevant to Steam PC catalog.
3. Reliable mapping from Steam appid or another stable identity.
4. Official API / structured endpoint / stable server-side access path.
5. Can GitHub Actions fetch it directly without browser automation, anti-bot scraping, or manual chat work?
6. Auth/rate limits/pricing/licensing/caching/redistribution constraints from public documentation where available.
7. Description quality: real game summary vs package/edition/store marketing blurb.
8. Maintenance/stability risk.
9. Whether the source can be canonical primary/secondary source or only weak fallback.

## Candidate direction

Do not assume these are good; verify them:
- Steam Russian Store data remains primary existing source;
- other official storefront/catalog APIs with Russian localization if they expose reusable descriptions and stable identity mapping;
- structured game databases/APIs only if they actually provide Russian-localized descriptions;
- do not use search-engine snippets or arbitrary copied web text as canonical description data.

## Decision rule

Preferred future precedence should be evidence-based, roughly:
1. meaningful official Steam Russian description;
2. meaningful ready-Russian text from another approved structured source with reliable identity mapping;
3. only if no acceptable ready-Russian source exists: translation fallback.

Do not encode this precedence into production code yet; RECON only.

## Hard boundaries

Do NOT:
- translate any game description;
- manually inspect/process all 132 unresolved games;
- build a catalog queue;
- change code/contracts/workflows;
- scrape websites in violation of documented terms;
- use interactive ChatGPT as a production description collector;
- change ranking/Taste/duration/package/UI.

A tiny source-level sanity check may be used only if needed to prove that an API/source genuinely returns Russian-localized description fields; do not turn that into catalog sampling.

## Done when

- viable ready-Russian source options are compared;
- one recommended source precedence is proposed;
- it is clear which sources are GitHub-direct and which are unsuitable;
- estimated architectural benefit is clear: whether translation can likely be eliminated, reduced to rare fallback, or remains necessary;
- no production descriptions were manually populated.

## Report format

Save:
`reviews/worker_reports/ru-description-source-recon-01.md`

### Task
What source classes/providers were checked.

### Verified facts
Compact comparison table.

### Recommendation
Recommended source precedence.

### Translation impact
One of:
- `translation_not_needed`
- `translation_rare_fallback`
- `translation_still_required`
- `undecided`
with concise reason.

### Executor
Which parts can be `GitHub-direct`.

### Changes
`none` except report.

### Validation
Public docs/source references + canonical repo evidence.

### Unresolved
Real remaining uncertainties only.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded contract/implement step based on evidence.

Final response must include report path and commit ref.