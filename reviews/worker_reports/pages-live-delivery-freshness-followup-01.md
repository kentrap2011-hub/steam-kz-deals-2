# Pages live delivery / freshness follow-up — independent ЧАТ 4

**Task:** `pages-live-delivery-freshness-followup-01`  
**Final status:** `LIVE_HTTP_UNVERIFIED` (neither live parity nor a delivery fault proved).  
**Mode:** read-only QA; this file is the sole report-only PR change. No Deploy or production mutation.  
**Pinned main:** `c3aac2c7dcf862e5d9c36efe2a00e5d60a14f6f6` (2026-10-23T17:20:59Z).

## START / narrow architecture preflight

Read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, the registered `WORKER_TASK_PAGES_LIVE_DELIVERY_FRESHNESS_FOLLOWUP_01.md`, relevant `PROJECT_ROUTES.md` route, top `DIRECTOR_TASK_BOARD.md`, registered item `pages-live-delivery-freshness-followup-01` in `config/director_task_plan.json`, `config/execution_ownership_contract.json`, `config/site_publication_resilience_contract.json`, and the complete previous report from draft [PR #245](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/245). Registration exists in current main; previous report is historical evidence, not a new live HTTP result.

Four preflight answers: (1) GitHub owns source status, build, staging, and publication; browser only presents prepared data. (2) The existing site resilience contract permits independently fresh optional status/tasks while preserving mandatory source/integrity fail-closed checks and historical semantic payload. (3) This QA does not relocate control-plane responsibility to ChatGPT. (4) No new schedule, queue, retry/checkpoint, CI, validator, workflow or ownership is proposed.

## Independent live URL attempts (2026-10-23T17:22:40Z)

Requested host: `https://kentrap2011-hub.github.io/steam-kz-deals-2/`. Six uncached HTTP targets:
- `/`
- `/app.js`
- `/data/current.json`
- `/data/status.json`
- `/data/tasks.json`
- `/data/publication-disposition.json`

For **each** URL, independent web retrieval returned “URL ... is not accessible via this tool.” Python HTTPS requests from the runtime failed at DNS lookup for `kentrap2011-hub.github.io` (`NameResolutionError`); no HTTP response was received. Thus public **HTTP status, response bytes, body SHA-256, response body length, ETag, Last-Modified, Cache-Control, Age, CDN/browser cache and actual user-visible cards remain UNKNOWN**. Neither a 404 nor a 200 nor a cache hit was observed. These failures describe the two verification environments; they **do not demonstrate site outage, stale CDN, or delivery mismatch**.

## Newest observed Pages run and independent artifact inspection

- At checked run listing (2026-10-23 ~17:22Z), newest `Deploy visual mailing`: [run 39994326860](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39994326860), **success**, event `push`, main SHA `c3aac2c7dcf862e5d9c36efe2a00e5d60a14f6f6`, created `17:21:02Z`, completed/updated `17:21:31Z`. Jobs confirm successful staging, staged paid-data validation, Pages upload and `Deploy to GitHub Pages`.
- Downloaded the **actual newest uploaded** [Pages artifact 12518173663](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39994326860/artifacts/12518173663): GitHub metadata 443,580 ZIP bytes; independently computed ZIP SHA-256 `b7509410ad3236c23ed0a4328d65e36cb9e983c4a1b15cceeeeec2dec3dae2ed`, matching upload job log; inner `artifact.tar` contains 44 files. This is staged deployment material, **not** public HTTP.
- Job log states `VISUAL_FRESHNESS=unbound/non_workflow_run event=push`. The triggering build receipt step was skipped for this push; **neither `fresh` nor a newly failed build can be inferred**. The historical build [39920764346](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39920764346) documented in PR #245 had `degraded/no_fresh_build` and preserved semantic history; it is not a new failure observed today.
- Deployment manifest explicitly records `published_verification=unverified_until_live_pages_readback`, `published_visual_sha256=null`, with staged source/current SHA matching. That label is intentional evidence separation, not a failed delivery receipt.

Exact **uncompressed** bytes of the latest artifact (NOT publicly served bytes):

| Path | Bytes | SHA-256 |
|---|---:|---|
| `index.html` | 11,128 | `80a9b2e5bbc6071773c24ffadc25215886738a9e7749be741a497fb983630c13` |
| `app.js` | 34,539 | `66ac02473dc3f3e2d44a9e1be5f44b684411a30a512a86cdec23e5f53df8de25` |
| `data/current.json` | 3,305,951 | `061641c13f072c6dd2be89b677276701a20375deacc87f02d8b250a98759e992` |
| `data/status.json` | 3,777 | `90276955f265191f6d9cac66b84fe47e5514bae894988f5f43feb03f48ae418b` |
| `data/tasks.json` | 41,023 | `d0774765c2bcbcb1645db694ee7eb7f59da74626120323e8580acb001eedcc39` |
| `data/publication-disposition.json` | 733 | `a5503b11e9c2c10214de6fa3d99472933e6e22aabe113f78b61e47cbd31a53e7` |

The first four SHA-256 values **exactly match** those independently archived in PR #245's prior Pages artifact `12504359614`. Current artifact's `current.json` git-blob SHA-1 `679fb741f0bc53ca241c9212e080ff1e02119347`, `status.json` `4f8cad0508dc98995474256b74e0f3a0064f75c3`, `app.js` `56c77178ecd437fa11f4e2078beac9617e2f12c4`, and `index.html` `ccda136a24f327c184cb4e27e6bbe00d2db11f05` match their exact blob SHAs at pinned main. The latest artifact refreshes **tasks** (97 task titles, `generated_at_utc=2026-10-23T17:21:20Z`; PR #245 artifact had 89 titles) and deployment disposition, **not the underlying deal/status/UI bytes**.

## Data freshness and what remains unproved

- Artifact `current.json`: schema 5, `status=complete`, 388 distinct game IDs and 388 staged item records; `generated_at_utc=2026-10-23T07:53:57.802212Z`. Original mailing data observed `2026-10-22T23:26:22.787817Z`; storefront commercial observation `2026-10-22T23:27:23.468675Z`. These are stored-source timestamps, **not** current live Steam prices or browser-side freshness proof.
- At **fixed audit clock 2026-10-23T17:25:50Z**, 29 of those staged offers had `sale_end_utc <= clock`. Existing frontend source includes client-side expired-sale filtering (as PR #245 noted), but **how many cards the public browser actually showed was not measured**. Do not infer 388 visible/live sale cards or a publication break from expired entries inside the immutable snapshot.
- Staged `status.json` timestamp `2026-10-23T07:54:02Z`: Dossier 87 accepted / 311 pending (398 current scope); Deep 26 authoritative completed / 373 remaining (399 target), Deep last write `2026-10-14T19:03:44Z`; Fast 0 attempts. Age of semantic analysis differs from current commercial data and from technical deploy timestamp. No semantic rerun was performed.
- Staged section disposition says `status=fresh`, `tasks=fresh`, `giveaways=fresh` as to their **staged section validation**. This is not an attestation of an uncached public HTTP response or actual giveaway content.
- First established boundary: source Git → newest staged Pages artifact **consistent** for required core bytes; Pages upload + deploy step **success**. Next boundary artifact → Pages CDN → actual browser **unverified**. No demonstrated `CONFIRMED_DELIVERY_PROBLEM` predicate. Historical `degraded/no_fresh_build` cannot by itself be relabelled a CDN or website outage.

## Verdict / one recommended next Director action

**`LIVE_HTTP_UNVERIFIED`** — proven Git-to-staged-byte consistency and successful upload/deployment; *no independent live-host status/body/cache readback*. No source, data, UI/currency, Reviews, Dossier/Deep/Fast, workflow, GitHub setting, production or deploy change in this PR.

**One action:** arrange a **bounded independent external-network browser + raw HTTP readback** of the six exact public targets above, with UTC, HTTP statuses, uncompressed body SHA-256/length, ETag/Age/Cache-Control (if present), plus an uncached browser rendering check; compare with artifact `12518173663` or the then-current latest artifact. Only if observed bytes/status differ should the Director commission separately scoped delivery diagnosis. **Do not rerun Deploy merely because this runtime cannot reach Pages.**
