# WORKER TASK — Taste Dossier Direct Appreviews Work Acceptance 01

Task ID: `taste-dossier-direct-appreviews-work-acceptance-01`
Mode: `ACCEPTANCE`

## Goal
Prove or disprove the cheapest direct architecture before building any custom Steam Reviews tool:

`isolated Work Scheduled Task -> Cloud Browser -> Steam appreviews -> review bodies -> cursor -> second page in same invocation`

The target is direct fresh review access with **no GitHub-prefetched review-body storage** and no custom MCP/app implementation unless this acceptance fails.

## START gate
Read fully:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- this task
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-direct-review-access-recon-01.md`
- `reviews/worker_reports/taste-dossier-review-source-recon-01.md`
- `reviews/worker_reports/taste-dossier-non-review-defect-repair-01.md`
- current `config/taste_steam_review_dossier_worker_prompt.md`
- current `config/taste_steam_review_dossier_schema.json`
- `config/execution_ownership_contract.json`.

Architecture preflight before any recommendation.

## Critical MANUAL-UI rule
Do **not** spend time trying to inspect or control the user's Scheduled Task UI.

The live UI is user-controlled and may be inaccessible to the worker.

After repository/product baseline is understood, ask the user to perform the exact minimal UI steps needed for this isolated acceptance. Treat the user's verbatim confirmation as authoritative.

Do not touch the production `Taste Steam Review Dossier` task.

## Acceptance object
Create/use a completely separate test Scheduled Task in **ChatGPT Work** with Cloud Browser capability.

Suggested task name:
`Steam Review Direct Access Test`

This test task must not read/write the production repository and must not produce dossier artifacts.

## Exact test behavior
The isolated test Scheduled Task must, in one invocation, use the Cloud Browser to directly access the official Steam endpoint:

`https://store.steampowered.com/appreviews/<appid>?json=1`

Use at least these representative cases:

### Primary appid
`1169040` — Necesse

Russian lane first page:
- `filter=recent`
- `language=russian`
- `review_type=all`
- `purchase_type=all`
- `num_per_page=20`
- `cursor=*`

It must inspect the returned JSON and record:
- at least 3 `recommendationid` values;
- actual `review` body presence;
- `language`;
- `voted_up`;
- `timestamp_created`;
- returned `cursor`.

Then, **in the same invocation**, URL-encode/use that returned cursor to fetch the second Russian page and prove it is a different page by observing at least one new `recommendationid`.

Then fetch a non-Russian page using:
- `language=all`
- same fixed filters;
- exclude objects with `language == "russian"` conceptually in the analysis;
- prove actual non-Russian review bodies are visible.

### Secondary appid
`1172380` — STAR WARS Jedi: Fallen Order™

Fetch at least one Russian page and prove review bodies/IDs are available, to show the result is not a one-game accident.

## Test task prompt
When ready for the manual UI step, give the user this exact prompt to install in the isolated Work Scheduled Task:

---
Use ChatGPT Work with Cloud Browser only. This is an isolated read-only acceptance test. Do not use GitHub, do not modify any account data, and do not save review bodies anywhere.

Test whether the cloud browser can directly read Steam's public appreviews JSON endpoint and follow its cursor in one scheduled invocation.

1. Open this exact URL for Necesse:
https://store.steampowered.com/appreviews/1169040?json=1&filter=recent&language=russian&review_type=all&purchase_type=all&num_per_page=20&cursor=*

2. From the returned JSON, confirm that reviews[].review contains actual review text. Record only a compact acceptance summary: the first 3 recommendationid values, their language, voted_up, timestamp_created, and whether non-empty review text was present. Do not reproduce full review bodies in the final answer.

3. Capture the response cursor. URL-encode it if necessary, open the same endpoint again using that cursor, and prove that the second page contains at least one recommendationid not present on page 1.

4. In the same invocation, fetch:
https://store.steampowered.com/appreviews/1169040?json=1&filter=recent&language=all&review_type=all&purchase_type=all&num_per_page=20&cursor=*
Confirm that non-Russian review bodies are available. Treat reviews tagged language=russian as excluded for this non-Russian check.

5. Also fetch one Russian first page for appid 1172380 using the same parameters and confirm actual review bodies and recommendationid values are present.

6. Report only:
- direct Steam appreviews access: PASS/FAIL;
- Necesse RU page 1 bodies: PASS/FAIL;
- Necesse RU cursor page 2 in same invocation: PASS/FAIL;
- different recommendationid observed on page 2: PASS/FAIL;
- Necesse non-Russian bodies: PASS/FAIL;
- Fallen Order RU bodies: PASS/FAIL;
- any browser/blocking/error details;
- whether any user interaction was required after the run started.

Do not fall back to search-engine snippets, Steam Community HTML, or store review aggregates. If the exact JSON endpoint cannot be opened/read, report FAIL rather than substituting another source.
---

## Manual UI sequence
After baseline read, instruct the user only as needed:

1. Open ChatGPT Work.
2. Create a new isolated Scheduled Task named `Steam Review Direct Access Test` using the exact prompt above.
3. Keep production `Taste Steam Review Dossier` unchanged.
4. Press `Run now` exactly once on the isolated test task.
5. Return to the worker chat with `Запустил`.

Do not ask the user to modify plans, install custom plugins, or create MCP infrastructure during this acceptance.

## What counts as PASS
Overall PASS only if one isolated Scheduled Task invocation proves all of:

- exact `store.steampowered.com/appreviews/...` JSON URL is directly accessible through Work Cloud Browser;
- actual `reviews[].review` text is present;
- `recommendationid`, language, polarity and timestamp fields can be read;
- returned cursor can be reused for a second page **in the same scheduled invocation**;
- second page is demonstrably not the same page;
- Russian access works;
- non-Russian access works;
- at least two appids work;
- no user interaction is required after invocation starts;
- no GitHub/raw-review storage is created;
- no fallback scraping/search source is used.

## What counts as FAIL/BLOCKED
FAIL if Work/Cloud Browser cannot directly open/read the endpoint, cannot reuse cursor, Steam blocks automation, or the Scheduled Task surface cannot use Work/Cloud Browser as required.

BLOCKED only if the user cannot create/run an isolated Work Scheduled Task because the needed product surface is absent or unavailable on the current account.

Do not reinterpret a product-surface absence as a Steam failure.

## After PASS
Do **not** modify production yet.

Report that the next task should align the production worker prompt/evidence contract to direct Work/Cloud Browser `appreviews` access, then coordinate g1/g2 recovery and a separate live production acceptance.

## After FAIL
Do **not** silently revert to GitHub-prefetched evidence.

Report the exact blocker. The next architecture candidate is the narrow stateless `get_steam_reviews` app/tool from `taste-dossier-direct-review-access-recon-01`.

## Prohibitions
- No production `Taste Steam Review Dossier` Run now.
- No production Scheduled Task UI change.
- No production g1/g2 mutation/recovery.
- No GitHub workflow dispatch.
- No runtime/config/code implementation.
- No custom MCP/app deployment.
- No raw-review storage.
- No Taste Semantic Producer change.

## Durable report
Write to `main`:
`reviews/worker_reports/taste-dossier-direct-appreviews-work-acceptance-01.md`

Report must include:
- architecture preflight;
- user manual UI action requested/confirmed;
- exact isolated task prompt used;
- single-run evidence/results;
- whether exact JSON endpoint was read;
- page-1/page-2 cursor proof;
- RU/non-RU proof;
- second-appid proof;
- whether post-start user interaction was required;
- no-storage confirmation;
- overall verdict;
- one next step only.

Allowed final statuses:
- `accepted_direct_work_appreviews_path`
- `rejected_direct_work_appreviews_path`
- `blocked_product_surface_unavailable`

Stop after durable report.