# Pages live publication readback audit — ЧАТ 4

**Task:** pages-live-publication-readback-audit-01  
**Mode:** READ-ONLY / RECON, report-only draft PR  
**Pinned main at audit:** e9d9fd64986ada2e26a5ea1dea95298f98b1ae3e (merged PR [#242](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/242))  
**Result:** RECON_COMPLETE_WITH_LIVE_HTTP_UNVERIFIED. Actual Pages deployment job and its uploaded artifact are verified; public HTTP response and browser/CDN cache are **UNVERIFIED**. No source/data/workflow/deploy settings changes.

## START, registry and architecture preflight

- Read current main CHAT_PROTOCOL.md, CHAT_CONTEXT.md, relevant PROJECT_ROUTES.md publication path, DIRECTOR_PROTOCOL.md, DIRECTOR_TASK_BOARD.md, config/director_task_plan.json and the exact registered WORKER_TASK_PAGES_LIVE_PUBLICATION_READBACK_AUDIT_01.md. Task, plan and Board align on task ID, worker ЧАТ 4, report-only mode, own branch and no Deploy.
- Registration authority: PR [#242](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/242) merged as e9d9fd64986ada2e26a5ea1dea95298f98b1ae3e; PR-head CI [39961762153](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39961762153) (site task registry) **success** and [39961762208](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39961762208) (backlog dispositions) **success**.
- Preflight 1: config/execution_ownership_contract.json assigns source, source freshness, payload build, status, validation and publish to **GitHub control plane**; browser is read-only presentation. Preflight 2: config/site_publication_resilience_contract.json permits independently omitted optional sections, but global identity/prices/material/receipts are fail-closed. Preflight 3: audit performs no transfer to interactive or scheduled ChatGPT. Preflight 4: no schedule, recurring job, queue, retry loop, production or semantic ownership added.
- Relevant path: .github/workflows/build-daily-visual-payload.yml → scripts/build_final_visual_payload.py → data/production/visual/current.json → .github/workflows/deploy-visual.yml → staged web/data/current.json and optional sections → Pages artifact → GitHub Pages. Historical report-only [#236](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/236) documented failed pre-fix Deploy; accepted code [#238](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/238), merge bb0d8bb7426c0e0afd277f7a3d7f5c808c2ca981, changed fault isolation. Neither code merge nor workflow success alone proves publicly served bytes.

## Actions chronology (all UTC, selected consequential runs)

| Event | Evidence | Verified meaning |
|---|---|---|
| 2026-10-21 17:49, pre-fix Deploy | [39647198011](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39647198011) | **Failure** at UI regression, Upload/Deploy Pages **skipped**; NOT a release. Earlier PR #236 investigation also cites failed runs 39479228940 / 39456363674. |
| 2026-10-22 23:27, upstream visual Build | [39871956044](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39871956044) | **Success**; historical build alone is not Pages deployment. |
| 2026-10-23 07:53, PR #238 merge push | [39920764326](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39920764326) | Pages upload + deploy steps **success** before subsequent fresh build receipt, event push/unbound. Artifact 12486049688. |
| 2026-10-23 07:53–07:54, Build after #238 | [39920764346](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39920764346) | Workflow and build job **success**, 388-item JSON persisted, but actual [receipt artifact 12486588567](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39920764346/artifacts/12486588567) says fresh_build=false, full_visual_freshness=false, outcome=degraded/no_fresh_build, reason=deterministic_refresh_preserved_semantic_history; produced_visual=null; observed visual commit=4cadd6dd6b8f0105bea5c3ce236831371926e1b4. |
| 2026-10-23 07:54–07:55, triggered Deploy | [39920891539](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39920891539) | Triggering receipt download, exact verify, Pages artifact 12486244005 and Pages deployment **success**, but classified **degraded/no_fresh_build**. |
| 2026-10-23 13:31, after PR #242 | [39961882854](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39961882854) | **Latest observed successful** Deploy, from main e9d9fd64986ada2e26a5ea1dea95298f98b1ae3e; Pages upload/deploy jobs **success**; no triggering build receipt (push) and classification **unbound/non_workflow_run**, NOT an attested fresh cycle. Artifact [12504359614](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39961882854/artifacts/12504359614). |

The 13:31 deploy job logs directly identify Pages environment URL: https://kentrap2011-hub.github.io/steam-kz-deals-2/. The artifact and deployment step completed successfully; this is stronger than merely a green workflow badge, but not a live URL byte readback.

## Exact source-to-staged artifact readback

Read the actual archived ZIP → artifact.tar of the latest Deploy 39961882854. Independently computed SHA-256 and git-blob SHA-1 on **uncompressed archived file bytes**; matched source Git blob identities and staging manifest. Current main remained e9d9fd64986ada2e26a5ea1dea95298f98b1ae3e when the audit branch was opened.

| File | Archived bytes | SHA-256 | Git blob SHA / finding |
|---|---:|---|---|
| data/current.json | 3,305,951 | 061641c13f072c6dd2be89b677276701a20375deacc87f02d8b250a98759e992 | 679fb741f0bc53ca241c9212e080ff1e02119347 = main data/production/visual/current.json |
| data/status.json | 3,777 | 90276955f265191f6d9cac66b84fe47e5514bae894988f5f43feb03f48ae418b | 4f8cad0508dc98995474256b74e0f3a0064f75c3 = main data/production/site/current_status.json |
| app.js | 34,539 | 66ac02473dc3f3e2d44a9e1be5f44b684411a30a512a86cdec23e5f53df8de25 | 56c77178ecd437fa11f4e2078beac9617e2f12c4 = main web/app.js |
| index.html | 11,128 | 80a9b2e5bbc6071773c24ffadc25215886738a9e7749be741a497fb983630c13 | ccda136a24f327c184cb4e27e6bbe00d2db11f05 = main web/index.html |
| data/tasks.json | 37,518 | 4399580c5f1d2ea320f66b857f93715fac4f7393774843ee6b01caf04fdaf9e7 | Generated at deploy, 4 groups, 89 titles; staged optional tasks=fresh. |
| data/publication-disposition.json | 733 | ee55c9d72c7f4b908013ce9dcc26e718dee18d96b6908dec2230f4b8816fbe6c | Manifest: scope=general, status/tasks/giveaways disposition=fresh, published_visual_sha256=null, published_verification=unverified_until_live_pages_readback. |

The manifest source_visual_git_blob_sha and source_visual_sha256 equal the independent computed values, and staged_visual_sha256 equals 061641c13f072c6dd2be89b677276701a20375deacc87f02d8b250a98759e992. Mandatory core bytes are **identical** in Git and the last uploaded artifact; no verified payload-byte discrepancy.

Compared the previous successful artifact 12486244005 with latest 12504359614: data/current.json, data/status.json, app.js, index.html are **byte-identical**. Only the publication-disposition manifest and generated data/tasks.json differ among archived files: task titles 86 → 89 with PR #242 registry changes. Thus latest deployment updated task metadata, **not** deal or semantic data.

## What the verified latest artifact contains (not a claim about HTTP readback)

- Source current.json: schema_version=5, status=complete, generated_at_utc=2026-10-23T07:53:57.802212+00:00, source_mailing_updated_at_utc=2026-10-22T23:26:22.787817+00:00, commercial store observation=2026-10-22T23:27:23.468675+00:00. item_count=388, exact 388 distinct game IDs and matching priority order. Every one of 388 has numerical current_price_kzt and current_price_rub.
- Examples in stored order: rank 1 Blue Fire game:1220150, **530 KZT**, 80%, end Oct 27 17:00Z; rank 2 Dome Keeper game:1637320, **1,200 KZT**, 75%, end Oct 24 17:00Z; rank 3 Saviorless game:1438480, **780 KZT**, 85%, end Oct 24 17:00Z; rank 4 Blasphemous 2 game:2114740, **1,900 KZT**, 75%, end Oct 26 18:00Z. These are **stored snapshot prices**, not freshly validated Steam live prices.
- At fixed audit clock 2026-10-23 14:41Z, **one of 388 stored offers already ended**: Green Hell game:815370, end 2026-10-23T08:00:00Z. It remains in immutable daily JSON; scripts in the staged frontend route web/app.js::syncActiveSaleItems to web/progressive-personalization-ui.js::filterActiveSaleItems and hide known-expired sales at render. Expected eligible UI count at that clock is 387, subject to live client verification and user interface state. No undocumented correction to JSON was made.
- **Currency presentation discrepancy in verified source:** data has current_price_kzt for every offer, but shipped app.js::fmtRub and card/list/search render paths read current_price_rub and append **₽**. E.g. rank 1 Blue Fire is stored as 530 KZT and 97 RUB; this UI code will display 97 ₽, not 530 ₸. This is a confirmed code-to-data presentation choice, not proof of a new defect caused by PR #238, and not permission for a currency fix in this task. Requires product/Director decision if KZT is intended for users.
- Giveaway section is structurally valid and marked fresh in the stage manifest, but **state=unavailable, games=[]**, zero accepted offers. Do not equate structural acceptance to actual giveaway availability.
- Status JSON generated at 2026-10-23T07:54:02Z; Fast 0 attempted / 373 remaining (26 skipped by authoritative Deep), Dossier 87 accepted / 311 pending of 398, Deep 26 current authoritative completed / 373 remaining of 399, last Deep write 2026-10-14T19:03:44Z. The visual JSON separately records last accepted analysis 2026-10-14T19:02:30Z. These are different producer/status projections, not a fresh Deep run. Untranslated games=8, last translation success 2026-10-11T23:43:50Z.
- Latest frontend fetches data/current.json and data/status.json with cache:no-store, does not compute prices/scores. This describes source code behavior only; CDN/browser cache and actual HTTP payload remain unobserved.

## First proven divergence, limits and next decision

1. **No source→staged artifact byte divergence found** (core and associated source/staged hashes match).
2. First verified **freshness qualification** failure occurs at [Build 39920764346](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39920764346): workflow success but receipt fresh_build=false / degraded/no_fresh_build because deterministic refresh preserved semantic history. Following 39920891539 deploy is operationally successful but explicitly degraded. Last 39961882854 Deploy is successful and uses correct current Git bytes but remains **unbound/non_workflow_run**.
3. **Live HTTP readback UNVERIFIED:** attempted GET for site /, data/current.json, data/status.json and data/publication-disposition.json through web retrieval: URL not accessible via tool. Independent container network had DNS resolution failure for kentrap2011-hub.github.io. Those access limits **do not prove Pages is down or stale**. No independently observed ETag, HTTP status/body, CDN age, tasks HTML, browser state or service-worker/cache behavior. GitHub Pages job success + extracted artifact cannot be silently relabelled as verified public browser bytes.
4. No direct current Steam/API price checks; no external expiry refresh or semantic verification. Confirmed stored fields and UI behavior must not be represented as present-time storefront truth.

**Recommended single next Director decision:** authorize a **separate bounded live Pages readback/QA** from an environment that can access the Pages hostname; save HTTP status/headers/body SHA-256 for /, index.html, app.js, data/current.json, data/status.json, data/tasks.json and data/publication-disposition.json and compare with archived artifact 12504359614, including uncached and real-browser views (387 eligible as of fixed audit time). If hashes differ, first isolate CDN/browser/deploy provenance; do not automatically rerun Deploy or rewrite producer. Separately decide whether KZT display and the degraded semantic freshness warrant their **own** authorized code/production tasks. No Deploy, workflow_dispatch, production write, semantic run, Scheduled Task, or PR merge is authorized by this report.

## Change set and validation

Only this new report file under reviews/worker_reports/ on an isolated audit branch; no CURRENT_TASK.md overwrite, source, workflow, canonical data, config, UI, GitHub settings, Pages deploy or scheduled automation changes. Independently extracted two real Pages artifacts and one original visual freshness receipt; recomputed archived SHA-256 and Git blob SHA; compared exact source blobs, IDs, dates, selected KZT values, section disposition, build/deploy steps and PR #242 registration CI. Last main pin is e9d9fd64986ada2e26a5ea1dea95298f98b1ae3e; report-only draft awaits Director review.