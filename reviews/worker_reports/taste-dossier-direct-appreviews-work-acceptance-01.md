# Taste Dossier Direct Appreviews Work Acceptance 01

- Task ID: `taste-dossier-direct-appreviews-work-acceptance-01`
- Mode: `ACCEPTANCE`
- Date: `2026-09-15`
- Final status: `rejected_direct_work_appreviews_path`
- Repository: `kentrap2011-hub/steam-kz-deals-2`

## 1. Architecture preflight

- GitHub remains the production control plane.
- The acceptance test used a separate isolated ChatGPT Work Scheduled Task only to probe direct external review access through Work Cloud Browser.
- The test did not transfer queue, scope, retry, progress, checkpoint, validation, persistence, or completeness authority away from GitHub.
- No production runtime/config/code changes were authorized or made.
- Production `Taste Steam Review Dossier` was not modified or run.
- Existing g1/g2 artifacts/state were not touched.
- No GitHub-prefetched review bodies were used.
- No custom MCP/plugin/app was built.
- Ordinary web search, Steam Community HTML, and store aggregates were not accepted as substitutes.

Relevant baseline read before the test:
- `WORKER_TASK_TASTE_DOSSIER_DIRECT_APPREVIEWS_WORK_ACCEPTANCE_01.md` from task commit `ee61b0a05ff5f2230c77959ff7fbf6e48f67356c`
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-direct-review-access-recon-01.md`
- `reviews/worker_reports/taste-dossier-review-source-recon-01.md`
- `reviews/worker_reports/taste-dossier-non-review-defect-repair-01.md`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_schema.json`
- `config/execution_ownership_contract.json`

Preflight verdict: an isolated read-only Work Scheduled Task was architecturally safe to attempt because it exercised only the data-plane read path and did not alter production ownership.

## 2. User manual UI action requested and confirmed

The user manually created a separate Work Scheduled Task named `Steam Review Direct Access Test`, visible independently from both `Taste Semantic Producer` and the paused production `Taste Steam Review Dossier` task.

The user then manually invoked `Run now` exactly once on the isolated test task. This manual confirmation is treated as authoritative per the task protocol.

After the invocation started, the user did not take over the cloud browser or supply any additional Steam interaction. Approximately one hour after launch, the Work UI was still in `Thinking` and displayed `Подключение к облачному браузеру` (`Connecting to cloud browser`).

## 3. Exact isolated task prompt used

```text
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
```

## 4. Single-run evidence/results

Observed result from the single invocation:

- Work task started: **YES**.
- Work remained in `Thinking`: **YES**.
- Cloud Browser connection completed: **NO evidence; after approximately one hour the UI still showed `Connecting to cloud browser`**.
- Exact Steam `appreviews` JSON read: **FAIL / not reached**.
- Necesse RU page 1 review bodies: **FAIL / not proven**.
- Necesse RU first 3 `recommendationid` values and metadata: **not obtained**.
- Necesse RU response cursor: **not obtained**.
- Necesse RU cursor page 2 in the same invocation: **FAIL / not reached**.
- Different `recommendationid` observed on page 2: **FAIL / not proven**.
- Necesse non-Russian review bodies: **FAIL / not reached**.
- Fallen Order (`appid=1172380`) RU review bodies / IDs: **FAIL / not reached**.
- Search-engine snippets / Steam Community HTML / store aggregates used as fallback: **NO**.
- User interaction required after start to make progress: the run had not completed autonomously after approximately one hour; no takeover was performed because any such intervention would invalidate the acceptance condition.

No second invocation was requested or used. The failed/hung single invocation is the acceptance result.

## 5. Exact endpoint and pagination proof

Required direct endpoint:

`https://store.steampowered.com/appreviews/1169040?json=1&filter=recent&language=russian&review_type=all&purchase_type=all&num_per_page=20&cursor=*`

Acceptance required successful Cloud Browser access to this exact JSON, extraction of real body-bearing review records, reuse of the returned cursor, and proof of a different second page in the same invocation.

That proof was **not obtained**. The run did not progress past Cloud Browser connection during the observed approximately one-hour interval, so there is no valid page-1 response, no cursor, and no page-2 response to record.

Because the task explicitly requires FAIL when Work/Cloud Browser cannot directly open/read the exact endpoint, substituting any other source is prohibited.

## 6. Russian / non-Russian / second-app proof

- Necesse Russian lane: **not proven**.
- Necesse non-Russian lane via `language=all` with Russian-tagged reviews excluded: **not proven**.
- Fallen Order (`appid=1172380`) Russian first page: **not proven**.

The failure occurred before any of these endpoint-level checks could be completed.

## 7. No-storage confirmation

- The isolated task explicitly prohibited GitHub use and prohibited saving review bodies anywhere.
- No review bodies were obtained during the observed run, so no raw review body could have been persisted by this acceptance flow.
- No GitHub-prefetch artifact containing review bodies was created or used.
- No production dossier artifact was written by this test.
- This durable acceptance report contains no review bodies.
- The only repository write performed by this task is this final worker report.

## 8. Verdict

`rejected_direct_work_appreviews_path`

Reason: the isolated Work Scheduled Task did not establish a usable Cloud Browser session during the single observed invocation and remained stuck at `Connecting to cloud browser` for approximately one hour. Therefore the exact Steam `appreviews` JSON endpoint was not directly read, cursor reuse was not demonstrated, RU/non-RU review-body access was not demonstrated, and the second appid was not demonstrated. The acceptance contract requires rejection rather than fallback when the exact direct path cannot be proven.

## 9. One next step

Create the bounded follow-up for the narrow stateless `get_steam_reviews` app/tool described in `reviews/worker_reports/taste-dossier-direct-review-access-recon-01.md`; do not fall back to GitHub-prefetched review bodies.
