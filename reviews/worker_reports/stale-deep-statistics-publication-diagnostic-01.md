# stale-deep-statistics-publication-diagnostic-01

## 1. Task

- Task ID: `stale-deep-statistics-publication-diagnostic-01`.
- Mode: `READ-ONLY / RECON`.
- Repository / authority: `kentrap2011-hub/steam-kz-deals-2`, branch `main`.
- User symptom: the public Statistics view still showed old Deep counters after canonical Deep/PASS 2 had advanced.
- This task did not run Fast, Dossier, Deep, rebuild, deploy, scheduler changes, state repair, or ranking changes. The only durable change from this worker is this report.

## 2. Pinned user-visible stale snapshot

The exact user-visible values were recovered from the actual GitHub Pages artifact deployed by Deploy visual mailing run **#926** / run ID **36459102720**:

- Pages artifact ID: **10986847860**
- staged path: `web/data/current.json`
- source path: `data/production/visual/current.json`
- visual source commit selected by deploy: **2202a668cad11f67f0659aa6bcfe5e6cf34bb9ab**
- payload `generated_at_utc`: **2026-09-28T16:49:10.166499+00:00**
- payload `item_count`: **381**
- Deep total: **387**
- authoritative completed: **30**
- completed fit: **24**
- completed not-fit: **6**
- incomplete/recovery: **10**
- waiting for Dossier: **338**
- ready/pending: **9**
- remaining until all authoritative: **357**
- `deep_last_write_at_utc`: **2026-09-28T16:47:46+00:00**

These are byte-for-byte the same statistics reported in the user screenshot. Therefore the screenshot was not merely an old DOM rendering of newer published data: the deployed Pages payload itself contained the old counters.

Run #926 log proves the exact deploy path:

1. checkout current `main`;
2. identify `data/production/visual/current.json` last mutation as commit `2202a668...`;
3. `cp data/production/visual/current.json web/data/current.json`;
4. upload `web` as Pages artifact **10986847860**;
5. deploy it successfully.

## 3. Canonical Deep truth

The Deep control plane had advanced independently of the public visual snapshot.

### Snapshot that still had nine ready items

At both commit **23e39f8ee4e0380515cc6c5bbc35ae91345a9abc** and the later transport commit **53767218c890c9bdb5698d039a5651fa416c4963**, `data/production/pre_ai/progressive_pass2_work.json` reported:

- `deep_total_current_coverage_target = 399`
- `deep_first_pass_attempted_count = 46`
- `deep_authoritative_completed_count = 36`
- fit = 30
- not-fit = 6
- incomplete/recovery = 10
- waiting Dossier = 344
- ready/pending = 9
- remaining authoritative = 363

The PASS 2 state blob at `53767218...` was:

- **4435430a967f94474c41aa77ea97374f7d276cf1**

### First accepted Deep advance after that snapshot

Commit **dede9ea264b834819642b6e23f778cabd85a4fdd** reconciled Dossier/PASS 2 state and advanced canonical Deep to:

- total = 399
- first-pass attempted = 47
- authoritative = 37
- fit = 31
- not-fit = 6
- incomplete/recovery = 10
- waiting Dossier = 344
- ready/pending = 8
- remaining authoritative = 362

Its PASS 2 state blob was newer:

- **b1967e420ef55cc3c2368f25f71ef99df8041aec**

### Frozen authority used by the later Deep invocation

At **97012741145611e481858f0e3bc981992ef869bd**:

- total = 399
- first-pass attempted = 54
- authoritative = 44
- fit = 38
- not-fit = 6
- incomplete/recovery = 10
- waiting Dossier = 344
- ready/pending = 1
- remaining authoritative = 355

Its PASS 2 state blob was:

- **642a5d64971aac81998fa59801d41ecd36cf18ed**

Thus the one-item frozen Deep queue was correct. The public `ready/pending = 9` was already stale relative to accepted GitHub state.

The later worker transport commit **40e0ba34808314634582770886a1829a7254ab91** submitted the STAR WARS Battlefront result. The subsequent reconciliation commit **b09b179010cfaafdd740f2b773d05b3193cd78f8** did not increase the authoritative-completed count beyond 44, so this diagnostic does not treat the transport commit itself as proof of a newly accepted canonical Deep completion.

Later Dossier reconciliation at **85f55df8ee542ebfc47f82d9f7c15dbef2b46141** changed the current ready/waiting split to ready 5 / waiting 340 while Deep completed counts stayed 44. This is further evidence that control-plane state continued to move while the visual snapshot remained fixed.

## 4. Exact Statistics data source

There is no separate public Statistics API and no browser-side Deep recount.

### Browser

`web/app.js` defines:

- `DATA_URL = 'data/current.json'`
- `init()` fetches that URL with `cache: 'no-store'`
- the Statistics view passes `data.processing_status` to `ProgressivePersonalizationUI.statisticsSections(...)`

`web/progressive-personalization-ui.js` maps the Deep rows directly to producer-owned fields:

- `deep_total_current_coverage_target`
- `deep_authoritative_completed_count`
- `deep_completed_fit_count`
- `deep_completed_not_fit_count`
- `deep_incomplete_or_recovery_count`
- `deep_waiting_for_dossier_count`
- `deep_ready_or_pending_count`
- `deep_remaining_until_all_authoritative_count`
- `deep_last_write_at_utc`

The browser only formats the values; it does not infer Deep state.

### Producer

`scripts/progressive_personalization.py::stamp_processing_status()` rebuilds `processing_status` from the GitHub-owned progressive state and the final visible item set. `build_processing_status()` explicitly skips hard/business-excluded families and computes Deep stage counts from producer-owned stage fields.

The final visual producer is `scripts/build_final_visual_payload.py`, which writes:

- `data/production/visual/current.json`

### Deploy

`.github/workflows/deploy-visual.yml` copies that exact file to:

- `web/data/current.json`

and uploads the `web` directory to GitHub Pages.

Therefore the authoritative publication chain for Statistics is:

`GitHub Deep state -> progressive projection -> data/production/visual/current.json.processing_status -> web/data/current.json -> Pages artifact -> app.js -> Statistics UI`.

## 5. Publication timeline

### Before the divergence

- **23e39f8...** — canonical reconcile: Deep ready/pending 9.
- **53767218...** — Deep result transport; canonical accepted Deep state still ready/pending 9.
- Build daily visual payload run **#869**, run ID **36453699478**, started while this was the checkout state.
- Its freshness receipt artifact **10984680877** records:
  - `captured_checkout_commit_sha = 53767218c890c9bdb5698d039a5651fa416c4963`
  - semantic payload status `degraded`
  - `ai_queue_count = 399`

The produced visual embedded:

- `progressive_pass2_state_blob_sha = 4435430a967f94474c41aa77ea97374f7d276cf1`

which is exactly the PASS 2 state blob from `53767218...`.

### Concurrent canonical advance

While run #869 was building, GitHub accepted the next Deep state transition:

- **dede9ea264b834819642b6e23f778cabd85a4fdd**
- ready/pending became 8
- authoritative became 37
- PASS 2 state blob became **b1967e420ef55cc3c2368f25f71ef99df8041aec**

### Stale visual persisted after rebase

Run #869 created a local visual commit, then its first push failed:

- local commit initially `90b08875`
- remote rejection: main was already at **dede9ea...**, while the build expected **53767218...**

The workflow then:

1. fetched the advanced `main`;
2. rebased the already-generated visual commit;
3. **did not rebuild the visual from the new parent**;
4. pushed final commit **2202a668cad11f67f0659aa6bcfe5e6cf34bb9ab**.

GitHub proves:

- parent of `2202a668...` = **dede9ea...**
- `2202a668...` changes only `data/production/visual/current.json`
- that visual still embeds old PASS 2 blob **4435430...** from **53767218...**, not parent state blob **b1967e42...**

This is the first proven publication divergence.

### After the divergence

Fresh visual runs did attempt to follow later accepted Deep changes, but the full-build path repeatedly failed before a replacement visual could be persisted.

Examples:

- run **36453797991**: Russian description validation failed, 1/26 personalized cards invalid;
- run **36453933968**: failed, 2/28;
- run **36454341915**: failed, 4/32;
- run **36454921288**: failed, 4/32;
- run **36457892914**: failed, 1/18.

Therefore the stale visual commit **2202a668...** remained the last canonical `data/production/visual/current.json`.

### Later pre-AI / build / deploy sequence

At head **9cb123765884440d37632740d51695a371338483**:

- pre-AI deterministic run **#221 / 36458961528** failed in `test_progressive_profile_semantic_identity_stability.py` with:
  - `AssertionError: migration target missing current binding: game:1143810`
- visual run **#884** was cancelled by concurrency;
- visual run **#885 / 36459026993** ended workflow-success, but its actual `build` job was **skipped**;
- its `no_build_receipt` job succeeded and produced freshness receipt artifact **10986348538** with:
  - `fresh_build = false`
  - `outcome = degraded/no_fresh_build`
  - `reason = upstream_prerequisite_not_ready`
- deploy run **#926 / 36459102720** then successfully staged the existing visual commit **2202a668...**, explicitly classified publication as:
  - `VISUAL_FRESHNESS=degraded/no_fresh_build`
  - `VISUAL_PUBLICATION_OUTCOME=degraded/no_fresh_build`
- nevertheless the Pages upload/deploy itself succeeded, producing artifact **10986847860**.

## 6. First divergence

The first proven divergence in the required chain is:

**Build daily visual payload run #869 persisted a visual calculated from checkout `53767218...` after rebasing that already-calculated file onto newer parent `dede9ea...`, without recomputing the visual against the new parent.**

Concrete binding proof:

- build checkout: `53767218...`
- old PASS 2 state blob used in visual: `4435430...`
- newer accepted parent: `dede9ea...`
- newer parent PASS 2 state blob: `b1967e42...`
- final visual commit after rebase: `2202a668...`
- final visual commit parent: `dede9ea...`
- final visual still bound to: `4435430...`

So the defect is a **stale-snapshot persistence race in the GitHub visual publication path**, specifically the rebase/push path after concurrent `main` advancement.

It is not a Deep accounting error: canonical Deep state advanced correctly.

## 7. Why successful build/deploy stayed stale

There are two different meanings of “success” in the observed runs.

### Run #869

The builder did generate and persist a visual, but its own freshness receipt classified it:

- `fresh_build = false`
- `outcome = degraded/no_fresh_build`
- `reason = deterministic_refresh_preserved_semantic_history`

The visual commit still advanced in Git despite that degraded semantic freshness classification.

### Run #885

The workflow-level conclusion was `success`, but:

- `build` job = **skipped**
- `no_build_receipt` job = **success**

That success only means the workflow correctly emitted a degraded receipt for an upstream prerequisite failure. It did not mean that a new visual payload was built.

### Run #926

The deploy workflow succeeded because it successfully uploaded and deployed the staged files. It did **not** claim they were fresh. Its log explicitly says:

- `degraded/no_fresh_build`

The deploy contract currently permits publishing the existing canonical visual even when the triggering receipt says no fresh build. Therefore a green deploy is not proof that Deep statistics were refreshed.

## 8. 399 vs 387 vs 381

These three numbers belong to different layers.

### 399 — canonical Deep coverage target

At the relevant Deep control-plane snapshots, `progressive_pass2_work.json` had:

- `deep_total_current_coverage_target = 399`

The progressive candidate context at build checkout `53767218...` also contained 399 unique families, and `chatgpt_payload.json` reported `progressive_candidate_count = 399`.

### 387 — published Statistics scope

The visual producer intentionally removes families that are not part of the currently publishable business/deal catalogue.

In run #869:

1. the base visual producer started from 399 progressive families;
2. one analyzed-fit family failed the existing hard business/deal INCLUDE gate, so the base processing scope became 398;
3. the final build log reports `expired_removed = 10`;
4. it also reports `removed = 1` from the later fit/commercial recheck;
5. final `stamp_processing_status()` treats visible-state families absent from the final catalogue as hard excluded.

Arithmetic:

`399 - 1 initial business/deal exclusion - 10 expired - 1 later commercial removal = 387`.

Therefore 387 is a legitimate publication-filtered denominator for that snapshot. It is not supposed to equal the unfiltered Deep control-plane target 399.

### 381 — visible feed cards

Within the published 387-family scope, the stale snapshot had:

- 6 authoritative `analyzed_not_fit` Deep outcomes.

Those are counted in Statistics but are intentionally not shown as normal feed cards.

Arithmetic:

`387 - 6 analyzed_not_fit = 381`.

This exactly matches the deployed `item_count = 381`.

So:

- **399** = control-plane Deep coverage target;
- **387** = publication-filtered Statistics scope for that old visual snapshot;
- **381** = actually visible cards after hiding not-fit results.

The defect is not the existence of these three different denominators. The defect is that the 387/381 snapshot was never replaced as accepted Deep state continued to advance.

## 9. Browser/service-worker role

No repository Service Worker owns or freezes the Statistics payload:

- no Service Worker registration was found in the web entrypoint;
- no Service Worker file is present in the current `web` publication set.

There is, however, an intentional last-known-good browser cache in `web/feed-bootstrap.js`:

- Cache Storage name: `steam-deals-feed-lkg-v1`
- requests to `/data/current.json` may initially render cached data;
- a background network refresh then fetches the current Pages payload;
- when network identity differs, the fresh payload is reapplied through `init()`.

Separately, `app.js` requests `data/current.json` with `cache: 'no-store'`.

This cache can cause a temporary old-first render or preserve the last good payload if network fetch fails. It is **not the root cause here**, because Pages artifact **10986847860** itself contains the exact stale values from the screenshot. Clearing browser cache would only fetch the same stale network payload from that deployment.

## 10. User-facing explanation

Простыми словами:

Deep действительно продвинулся. GitHub уже знал, что игр в очереди осталось меньше.

Но сайт берёт статистику не прямо из Deep, а из заранее собранного файла для сайта. Один такой файл начали собирать, когда в Deep ещё было 9 готовых игр. Пока файл собирался, GitHub уже принял следующий результат и стало 8. При сохранении файла система увидела, что `main` изменился, сделала rebase, но **не пересобрала сам файл заново**. В итоге новый commit содержал старую статистику.

После этого следующие попытки пересобрать сайт падали на другой проверке русских описаний. Позже зелёный build #885 вообще не выполнял настоящий build: он только зафиксировал, что свежая сборка невозможна. А зелёный deploy #926 честно развернул старый файл и прямо пометил это как `degraded/no_fresh_build`.

Поэтому:

- Deep-счётчики в GitHub были правильные;
- публикационный файл сайта был старый;
- Pages успешно опубликовал именно этот старый файл;
- браузер показал то, что реально лежало на Pages;
- очистка браузерного кэша причину не устранит.

## 11. Changes — report only

Changed:

- added only this diagnostic report.

Not changed:

- Deep/PASS 2 state;
- Fast/PASS 1 state;
- Dossier state;
- visual payload;
- GitHub workflows;
- Pages deployment;
- browser cache logic;
- ranking;
- scheduler / Scheduled Task settings;
- production contracts.

## 12. Unresolved

No material uncertainty remains about the cause of the stale Statistics snapshot.

Not required for root-cause proof and therefore not expanded into a second task here:

- the exact family IDs of the 12 publication exclusions;
- whether the existing degraded-deploy behavior should later receive a separate user-visible freshness indicator.

Neither affects the demonstrated first divergence.

## 13. Status

**needs_fix**

Canonical Deep accounting is healthy, but the visual publication path can persist a pre-rebase semantic snapshot onto a newer `main` parent and later keep deploying that stale payload.

## 14. Recommended next step

Exactly one bounded IMPLEMENT task:

**Fix the full-visual stale-snapshot rebase race.**

Required scope:

1. In the GitHub-owned `Build daily visual payload` persistence path, bind the generated visual to the exact semantic/control-plane source blobs used to build it.
2. If `main` advances before push/rebase and any relevant progressive source blob changes — at minimum PASS 2 state plus the other inputs already represented by the visual production contract — do not rebase and persist the old generated JSON unchanged.
3. After such drift, either:
   - rebuild from the new `main` before persistence, or
   - fail closed without changing `data/production/visual/current.json`.
4. Add a focused regression reproducing the proven race:
   - build against `53767218...` / PASS 2 blob `4435430...`;
   - advance parent to `dede9ea...` / PASS 2 blob `b1967e42...`;
   - assert that a final visual commit may not have the new parent while retaining the old PASS 2 source binding/statistics.
5. Do not change Deep worker semantics, Dossier semantics, browser caching, scheduler ownership, or introduce a new queue/retry architecture.

Architecture preflight supports this location: `config/execution_ownership_contract.json` assigns deterministic transformations, downstream visual rebuild, aggregate processing counts, persistence and publication to the GitHub control plane; `config/progressive_personalization_contract.json` likewise assigns aggregate counts/publication to GitHub and the browser is read-only presentation.

## 15. Exact commit / run / artifact references

### Canonical Deep / result timeline

- `23e39f8ee4e0380515cc6c5bbc35ae91345a9abc` — reconcile; ready 9.
- `53767218c890c9bdb5698d039a5651fa416c4963` — result transport; visual-build captured checkout; PASS 2 state blob `4435430a967f94474c41aa77ea97374f7d276cf1`.
- `dede9ea264b834819642b6e23f778cabd85a4fdd` — next accepted reconcile; ready 8; PASS 2 state blob `b1967e420ef55cc3c2368f25f71ef99df8041aec`.
- `2202a668cad11f67f0659aa6bcfe5e6cf34bb9ab` — stale visual commit after rebase; parent is `dede9ea...`; visual still binds `4435430...`.
- `97012741145611e481858f0e3bc981992ef869bd` — frozen authority with ready 1 / authoritative 44; PASS 2 state blob `642a5d64971aac81998fa59801d41ecd36cf18ed`.
- `2aa42b36850039e106dca26d4b7a2ff31a8cd070` — later Deep run-start marker.
- `40e0ba34808314634582770886a1829a7254ab91` — submitted STAR WARS Battlefront Deep result.
- `b09b179010cfaafdd740f2b773d05b3193cd78f8` — subsequent reconcile.
- `85f55df8ee542ebfc47f82d9f7c15dbef2b46141` — later Dossier reconcile; ready 5 / waiting 340.
- `9cb123765884440d37632740d51695a371338483` — later head that triggered the observed pre-AI/build/deploy sequence.

### Workflow / publication

- Build daily visual payload #869:
  - run ID **36453699478**
  - freshness receipt artifact **10984680877**
  - captured checkout `53767218...`
  - final persisted visual commit `2202a668...`
  - receipt: degraded/no_fresh_build, deterministic_refresh_preserved_semantic_history.
- First subsequent failed full visual run:
  - run ID **36453797991**
  - Russian-description validation failure.
- Pre-AI deterministic #221:
  - run ID **36458961528**
  - failure at semantic-identity regression, missing current binding `game:1143810`.
- Build daily visual payload #884:
  - run ID **36458961848**
  - cancelled.
- Build daily visual payload #885:
  - run ID **36459026993**
  - workflow conclusion success;
  - actual `build` job skipped;
  - `no_build_receipt` succeeded;
  - freshness receipt artifact **10986348538**;
  - reason `upstream_prerequisite_not_ready`.
- Deploy visual mailing #926:
  - run ID **36459102720**
  - deployment success;
  - explicit classification `degraded/no_fresh_build`;
  - selected visual commit `2202a668...`;
  - Pages artifact **10986847860**;
  - artifact `data/current.json` exactly matches the user-visible stale Statistics values.

## 16. Efficiency / reusable lesson

Reusable diagnostic rule for this repository:

**A green workflow/deploy is not enough to prove visual freshness.**

For a stale-site report, check in this order:

1. inspect the deployed Pages `data/current.json` bytes;
2. pin its `data/production/visual/current.json` mutation commit;
3. inspect `production_contract` source blob bindings;
4. compare those bindings with the visual commit's actual parent source blobs;
5. only then inspect browser cache.

Also distinguish:

- workflow-level `success`;
- whether the actual `build` job ran;
- freshness receipt `fresh_build`;
- deploy classification;
- successful Pages upload.

Run #885/#926 demonstrates why these cannot be treated as synonyms.

This route is not currently captured as a dedicated publication-freshness pitfall in `KNOWN_WORKER_PITFALLS.md`. Because this task is report-only, that file was not edited; the next implementation task should consider adding a concise reusable pitfall after the fix is accepted.
