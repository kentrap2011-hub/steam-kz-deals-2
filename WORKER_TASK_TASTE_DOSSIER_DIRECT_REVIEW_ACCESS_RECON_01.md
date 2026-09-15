# WORKER TASK — Taste Dossier Direct Review Access Recon 01

Task ID: `taste-dossier-direct-review-access-recon-01`
Mode: `READ-ONLY / RECON`

## Goal
Determine whether the existing live Scheduled Task can be given a stateless direct way to fetch fresh Steam review bodies on demand, without prefetching or storing review-body batches in GitHub.

This task is a deliberate architecture alternative to the prior recommendation `github_prepared_review_evidence_recommended` from `taste-dossier-review-source-recon-01`.

The user preference is explicit: avoid storing temporary collections of review bodies. Prefer live pull at analysis time, where ChatGPT requests as many current reviews as it needs and discards raw bodies after synthesis.

## User intent to preserve
Target interaction:

`Scheduled Task -> direct Steam review-access tool -> fresh review bodies -> analyze -> fetch more if needed -> compact dossier`

No permanent raw-review archive. No waiting for GitHub to prefetch review pages. GitHub remains control plane for scope/order/validation/persistence.

## START gate
Read fully:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- this task
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-review-source-recon-01.md`
- `reviews/worker_reports/taste-dossier-non-review-defect-repair-01.md`
- `reviews/worker_reports/taste-dossier-full-defect-sweep-01.md`
- current `config/taste_steam_review_dossier_worker_prompt.md`
- current worker-readable dossier schema
- `config/execution_ownership_contract.json`.

Run architecture preflight.

## Core question
Can the Scheduled Task be given a small stateless callable capability that accepts Steam appid/language/cursor and returns current individual review bodies directly from Steam `appreviews`, so the model itself decides whether to fetch another page?

The answer must be about the actual current ChatGPT/Scheduled Task environment, not a theoretical HTTP client.

## Source baseline
The prior recon already established the official public endpoint as suitable source semantics:

`https://store.steampowered.com/appreviews/<appid>?json=1`

It returns review body, recommendation id, language, polarity, timestamps and cursor. Do not redo broad source discovery unless needed to verify a direct-access path.

This task is specifically about **delivery into Scheduled ChatGPT without pre-storage**.

## Paths to investigate
Investigate realistic stateless direct-access options in this order, without assuming availability:

1. Existing ChatGPT plugin/connector that can expose a safe HTTP/REST GET wrapper suitable for Steam `appreviews`.
2. A custom plugin/integration/action whose only job is a bounded stateless Steam review GET, callable by Scheduled Task.
3. A repository-hosted stateless proxy endpoint that returns live Steam review JSON on request without persisting bodies, only if the Scheduled Task can actually call it.
4. Any existing supported ChatGPT tool mechanism that can whitelist/fetch this exact Steam endpoint directly.

Do not recommend normal web-search/store-page scraping as equivalent to the structured API.

## Important distinction
A solution is acceptable only if the Scheduled Task itself can invoke it during one run.

It is NOT sufficient that:
- GitHub Actions can call Steam;
- interactive ChatGPT can theoretically browse Steam;
- a local script can call Steam;
- an endpoint exists but Scheduled Task cannot invoke it.

## Required proof
For any candidate deemed viable, prove as much of the actual call chain as current constraints permit using representative appids:
- `1158890`
- `1164940`
- `1169040`
- `1172380`

Need to demonstrate or tightly prove the intended callable interface can support:
- appid input;
- `language=russian`;
- non-Russian retrieval;
- page/cursor continuation;
- individual review bodies;
- `recommendationid`;
- polarity;
- timestamps;
- bounded page size;
- no persistence of raw bodies by the intermediary;
- no user interaction per request.

Do not press dossier Scheduled Task `Run now` during this recon unless a later separate ACCEPTANCE explicitly authorizes it.

## Plugin / integration investigation
If a suitable existing plugin is available, identify it precisely and determine whether Scheduled Tasks can use it.

If not, define the smallest custom plugin/integration needed. The design should expose a narrow operation such as:

`get_steam_reviews(appid, language, cursor?, page_size?)`

and return only bounded Steam review fields.

Prefer a narrow allowlisted Steam-specific tool over a generic arbitrary-URL browser if that is simpler/safer.

Determine:
- where the tool would run;
- whether it needs credentials (Steam itself should not);
- whether ChatGPT plugin/integration infrastructure requires any hosting/auth setup;
- whether Scheduled Tasks can invoke installed plugins/custom integrations in practice;
- whether the response can be consumed repeatedly in a single task invocation;
- whether invocation limits make adaptive paging practical.

Do not claim Scheduled Task plugin support without evidence from current product/tool contracts or a concrete testable path.

## Statelessness requirement
The intermediary may transiently hold request/response data in memory for the duration of the call, but must not intentionally persist review bodies to GitHub history, object storage, database, or long-lived cache.

Compact final dossier provenance/hashes remain allowed.

## Architecture requirements
Preserve:
- GitHub owns canonical work scope, order, progress, validation, persistence, recovery and completeness;
- Scheduled ChatGPT owns semantic evidence review/synthesis;
- direct review access is only a data-plane read capability;
- no new ChatGPT-owned queue/retry/backlog manager;
- no direct canonical write from the review access tool.

## Decision outcomes
Report must end with exactly one recommendation:

- `direct_stateless_review_tool_recommended`
- `direct_stateless_review_tool_possible_but_needs_product_setup`
- `direct_stateless_review_tool_not_viable_currently`

If recommended/possible, provide the exact next IMPLEMENT scope, including what the user would need to install/configure, if anything.

If not viable, explain the exact blocker and whether GitHub-prepared evidence remains the only proven production option.

## Prohibitions
- READ-ONLY / RECON only.
- No dossier `Run now`.
- No Scheduled Task UI changes.
- No repository runtime/config/code changes except this durable report.
- No manual GitHub workflow dispatch.
- No current g1/g2 recovery.
- No Taste Semantic Producer changes.
- No creation of permanent review-body storage.
- No custom integration deployment yet.

## Durable report
Write to `main`:
`reviews/worker_reports/taste-dossier-direct-review-access-recon-01.md`

Report must include:
- architecture preflight;
- why the prior GitHub-prefetch design is being reconsidered;
- candidate direct-access mechanisms investigated;
- evidence about Scheduled Task compatibility;
- exact stateless call shape if viable;
- RU + non-RU + cursor behavior;
- hosting/auth/setup requirements;
- whether raw reviews are persisted anywhere;
- operational limits/risks;
- comparison with GitHub-prefetch only where relevant;
- exact recommendation;
- one next step only.

Allowed final statuses:
- `recon_complete_direct_path_selected`
- `recon_complete_setup_required`
- `recon_complete_direct_path_not_viable`
- `blocked`

Stop after durable report.