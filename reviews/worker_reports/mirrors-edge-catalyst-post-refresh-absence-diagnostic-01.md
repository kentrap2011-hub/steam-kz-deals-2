# Mirror's Edge Catalyst post-refresh absence diagnostic 01

## 1. Task

Task: `WORKER_TASK_MIRRORS_EDGE_CATALYST_POST_REFRESH_ABSENCE_DIAGNOSTIC_01.md`.

Mode: `DIAGNOSTIC / READ-ONLY PRODUCTION TRACE`.

Probe:
- title: `Mirror's Edge Catalyst`;
- Steam AppID: `1233570`.

The task was executed without production dispatch, semantic-worker execution, canonical production-state edits, ranking changes, Scheduled Task changes, or implementation changes. The only repository writes are this diagnostic report and the task-status metadata required by `CHAT_PROTOCOL.md`.

## 2. Current user symptom

After PR #140 (`Fix stale deal discovery freshness handoff`) merged, AppID `1233570` still does not appear in the user-visible result.

The symptom is reproducible from current repository truth: the game is absent before semantic analysis and before ranking/publication.

## 3. Current-main baseline

START gate was executed from current `main`: `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, the current-state section of `DIRECTOR_TASK_BOARD.md`, `PROJECT_ROUTES.md`, the relevant workflow-run production-authority pitfall, this task, the accepted PR #140 task/report, and the relevant ownership/execution contracts were read before conclusions were drawn.

The final pre-report reconciliation observed `main@30f59b693cdef3eca520ddc78334850fdf850948` (2026-10-03T16:49:26Z). Concurrent unrelated repository movement occurred during the diagnostic; the Steam discovery implementation on this final baseline is still the PR #140 implementation.

PR #140:
- merged at `2026-10-03T11:45:14Z`;
- merge commit: `7df5ed0cbe9dd9217c56344e0caab47dd366915f`.

Current canonical discovery chain remains old:
- `data/production/manifest.json`, blob `3c5c43dfec230db4699ccfcb49cd8e8afd7e31b8`, `updated_at_utc=2026-09-23T23:12:47.031485+00:00`;
- `data/production/shortlist/index.json`, blob `2459f1e3a47cea4506e71c79ec85c185ece4e357`, `source_updated_at_utc=2026-09-23T23:12:47.031485+00:00`;
- `data/production/mailing/index.json`, blob `445803536668059c94c2cf0734f59afb2b18a3f4`, `source_updated_at_utc=2026-09-23T23:12:47.031485+00:00`.

AppID `1233570` is absent from all three.

The current Store snapshot is newer only as a commercial observation:
- `data/production/pre_ai/store_snapshot.json`, blob `a2bbea0dbd459fb9dbfecb784328a306d99cb241`;
- `observed_at_utc=2026-10-03T11:44:34.173822+00:00`;
- `discovery_source_updated_at_utc=2026-09-23T23:12:47.031485+00:00`;
- AppID `1233570` absent.

Therefore current `main` still has no post-PR-#140 canonical fresh-discovery snapshot.

## 4. Post-PR-#140 production run chronology

### 4.1 PR merge and true production discovery start

PR #140 merged as `7df5ed0cbe9dd9217c56344e0caab47dd366915f` at `2026-10-03T11:45:14Z`.

Two seconds later, a real `main` production discovery run started:

- workflow: `Steam KZ production shortlist`;
- run ID: `37120664964`;
- run number: `80`;
- event: `push`;
- branch: `main`;
- head SHA: `7df5ed0cbe9dd9217c56344e0caab47dd366915f`;
- created: `2026-10-03T11:45:16Z`;
- completed: `2026-10-03T12:45:34Z`;
- conclusion: `cancelled`.

The production `collect` job was `111195963281`.

Its deterministic regressions passed. The real collection step, `Collect Steam KZ catalog with partial publish failure isolation`, was cancelled. All following ownership verification, canonical commit, and downstream dispatch steps were skipped.

### 4.2 Exact cancellation boundary

Current `.github/workflows/steam-test.yml` gives the production `collect` job `timeout-minutes: 60`.

The run continued catalog pagination until the timeout. The live Steam search reported:

- `total=100307`;
- page size: 50;
- repeated HTTP 429 throttling with 3/6/12/24-second waits;
- immediately before cancellation it had reached approximately `start=73850`, `unique=73831`.

At `2026-10-03T12:45:32.0293390Z` the job log records:

`##[error]The operation was canceled.`

The canonical commit step never ran. This is not a later shortlist/mailing failure; fresh discovery itself never completed/persisted.

### 4.3 Historical comparison

The last successful scheduled discovery was:

- run `35930927751`;
- created `2026-09-23T22:55:13Z`;
- completed `2026-09-23T23:12:59Z`;
- conclusion: `success`;
- source total during traversal: `12977`;
- resulting `shortlist_items=609`;
- canonical discovery timestamp: `2026-09-23T23:12:47.031485+00:00`.

Every scheduled `Steam KZ production shortlist` run from 2026-09-24 through the pre-PR-#140 schedule on 2026-10-02/03 was cancelled. The first such cancellation, run `36071409364`, already hit the same 60-minute execution ceiling, although its initial live total was only `13667`. Thus discovery-run completion had already become unhealthy before PR #140. The current post-merge failure is even more direct: it is still traversing a live `100307`-row result set when the 60-minute owner timeout fires.

### 4.4 PR #140 live input-bounding change did not work against live Steam

PR #140/current `scripts/steam_production.py` explicitly documents the late-September expansion from roughly 13k to over 100k rows and adds:

- `SEARCH_CATEGORY_TYPES = {"games": "998", "dlc": "21", "bundles": "996"}`;
- `SEARCH_CATEGORY1 = "998,21,996"`;
- `search_params(...)` sends both `specials=1` and `category1=998,21,996`.

The PR regression `test_11_canonical_search_is_bounded_to_supported_paid_content_types` verifies only that this parameter string is constructed and contains those three IDs.

The first real post-merge run nevertheless reports `total=100307`. Therefore the combined `category1` request shape did not bound the live Steam result set as intended. The regression proved local parameter construction, not live source behavior.

### 4.5 Downstream post-merge behavior

The PR #140 push also started pre-AI run `37120664975`. It failed exactly at the new freshness guard with:

`Fresh deal discovery prerequisite failed: discovery_source_older_than_allowed,candidate_universe_not_rebuilt_for_current_production_cycle; discovery=2026-09-23T23:12:47.031485+00:00; commercial=2026-10-03T11:45:30.564964+00:00`.

Visual run `37120682411` then failed the commercial-only refresh at the corresponding guard:

`Commercial publication requires a fresh current-cycle discovery universe`.

Its freshness receipt correctly classified the attempt as `degraded/no_fresh_build` / `commercial_only_refresh_not_persisted`.

When discovery run `37120664964` finally ended cancelled, its workflow-run successors were fail-closed:
- mailing run `37123911788`: skipped;
- feed-ingest validation run `37123914797`: skipped;
- pre-AI run `37123914757`: skipped.

This is the intended PR #141 production-source/conclusion behavior, not a new blocker.

## 5. AppID 1233570 stage-by-stage trace

| Stage | Current status for AppID 1233570 | Exact evidence |
|---|---|---|
| Fresh Steam KZ discovery/catalog | **stale / not refreshed** | Post-PR-#140 production run `37120664964` executed on `main` but was cancelled inside catalog collection at the 60-minute limit; canonical commit step skipped. |
| Canonical manifest | **absent** | `data/production/manifest.json` remains dated `2026-09-23T23:12:47.031485+00:00`; no AppID 1233570. |
| Shortlist | **absent** | `data/production/shortlist/index.json` still binds to 2026-09-23; no AppID 1233570. |
| Mailing projection | **absent** | `data/production/mailing/index.json` still binds to 2026-09-23; no AppID 1233570. Later mailing builds only reprojected the old shortlist. |
| Store state / pre-AI Store snapshot | **absent / stale discovery binding** | Current Store snapshot observed at `2026-10-03T11:44:34.173822+00:00` still binds discovery to 2026-09-23; PR #140 post-merge pre-AI run fails closed rather than producing a false-fresh snapshot. |
| Content rules | **absent** | `data/production/pre_ai/content_rules.json`, blob `68855192e6ff7f29ff90b514b8122382832fa481`, source 2026-09-23; no AppID. |
| Family graph | **absent** | `data/production/pre_ai/family_graph.json`, blob `cf1ccd1f81457f21d1084fe426d6d6a987f48370`, source 2026-09-23; no AppID. |
| Deal scenarios | **absent** | `data/production/pre_ai/deal_scenarios.json`, blob `51e793a569fc32ddc4c2c66c4ecb56c12d32f23b`; no AppID. |
| Taste projection / queue | **absent** | `taste_projection.json` blob `62894a48ee5112ae7f35ec9c5eb50a8dd122d88a`, `chatgpt_taste_queue.jsonl` blob `b28eee610a81552d17bce914076ca9ba65c33eb1`; no AppID. |
| Progressive candidate context | **absent** | `progressive_candidate_context.jsonl` blob `a72c564dcff361ca748ae46ab466d14f641ab728`; no AppID. |
| Fast / PASS 1 work | **absent, not semantic-incomplete** | `progressive_pass1_work.json` blob `7a262238820a98fd0c1fbbeb7eccdbed55109c2b`, source mailing 2026-09-23; no AppID. |
| Dossier work | **absent, not blocked on Dossier** | `taste_steam_review_dossier_work.json` blob `5c196f86bb0becf4ab826b546a4cc3e7cad593d5`; no AppID. |
| Deep / PASS 2 work | **absent, not blocked on Deep** | `progressive_pass2_work.json` blob `b0f7179924eb13d7f21b52fdc7856ca3609346aa`; no AppID. |
| Final ranking / visual lookup | **absent upstream, not ranking-filtered** | `data/production/visual/ranking_lookup/_manifest.json` blob `e35065b5f263f0f1423d8b933e0657e2fae165f9` has 509 items; `ranking_lookup/m.json` blob `26bc0dfdbf3e4e3a6888f70b8d55d3cf4ec58d69` contains neither AppID 1233570 nor the title. |
| Pages/publication | **not reached** | The game never reached canonical visual production, so Pages cannot be its first causal absence. Latest successful deploy before PR #140 was run `36998541896`, publishing visual commit `6e0d7a36e906fbb3e383d4f6252b7dd7846ca4bf`, artifact `11222941091`; post-PR-#140 deploy runs `37120687145` and `37120711123` were skipped. |

Public Steam was checked during this diagnostic only as a non-KZ-specific sanity check. Steam currently advertises an active `-95%` promotion for Mirror's Edge Catalyst ending October 8, 2026. That external page does **not** establish canonical Kazakhstan price/eligibility, because the GitHub-owned KZ collector never completed a fresh row. Therefore current sale/region state is not proven to be the exclusion cause; it is simply not reached by canonical discovery.

## 6. First failing/absent stage

The first deterministic causal stage is **fresh discovery completion/persistence**.

A true post-PR-#140 production discovery run did execute on `main`, but it did not complete. It timed out/cancelled inside the Steam catalog traversal before canonical output was committed.

Because no fresh discovery artifact exists, it cannot be proven from canonical evidence whether AppID `1233570` had already been encountered transiently inside the cancelled process. The collector log does not emit per-row AppIDs, and incomplete local runner state is not canonical. What is proven is that the run produced **no accepted fresh discovery universe at all**, so it could not publish Catalyst into manifest/shortlist/mailing.

This fully explains every downstream absence.

## 7. Root cause

Classification: **discovery coverage/input defect causing discovery execution timeout; fresh discovery never persists**.

The exact current causal chain is:

1. the existing GitHub-owned discovery owner runs correctly on `main`;
2. current PR #140 search parameters send `specials=1` plus the intended paid-content `category1=998,21,996` bound;
3. live Steam still reports `100307` rows, so that bound is ineffective against the real source;
4. the collector paginates 50 rows at a time and encounters repeated 429 backoff;
5. `.github/workflows/steam-test.yml` has a 60-minute `collect` timeout;
6. at roughly 73.8k / 100.3k rows, GitHub cancels the job;
7. canonical commit and downstream dispatch steps are skipped;
8. canonical discovery remains the last successful 2026-09-23 snapshot;
9. AppID `1233570` therefore never becomes a candidate.

This is not semantic-work incompleteness, ranking gating, Pages lag, or current stale-handoff masquerading. PR #140's new fail-closed handoff guards explicitly prevent those downstream stages from claiming freshness.

## 8. Why downstream stages behave as observed

The downstream behavior is internally consistent:

- shortlist/mailing cannot add an identity that discovery never persisted;
- Store/pre-AI cannot legally treat an old identity universe as current after PR #140, so it fails closed;
- content/family/deal/taste projections remain based on the old mailing universe;
- Fast/Dossier/Deep never receive AppID `1233570`, so there is no semantic verdict to block or publish;
- ranking lookup has no row to rank;
- Pages deploy has no new visual payload containing Catalyst and therefore cannot be the first cause.

A later mailing workflow can still succeed as a deterministic reprojection of the old shortlist. That does not mean discovery refreshed.

There is no evidence of a second independent publication mismatch masking Catalyst: the item is already absent from the canonical discovery-derived universe, and final ranking lookup is correspondingly absent. Pages only reflects an older already-Catalyst-free visual state.

## 9. Whether PR #140 is defective or simply not live-accepted

The answer is split by component:

- **PR #140's freshness handoff/guard is working correctly.** The post-merge pre-AI and visual attempts fail closed on stale discovery exactly as designed. A fresh Store timestamp can no longer masquerade as a fresh candidate universe.
- **PR #140 is not fully live-effective as an end-to-end fresh-discovery fix.** The same PR/current source contains an explicit live-input bounding change intended to prevent the late-September `specials` expansion from exceeding the 60-minute owner timeout, but its `category1=998,21,996` shape did not bound the real post-merge Steam response: the live run still reported `100307` rows and timed out.
- Therefore this is **not** merely “live acceptance was never attempted,” and it is **not** a downstream failure. Live acceptance was attempted immediately after merge and failed inside discovery itself.
- The underlying discovery completion problem predates PR #140; PR #140 correctly fixed stale-freshness semantics but did not successfully make the current live collector complete.

So the precise conclusion is: **PR #140 is correct on freshness fail-closed behavior, but incomplete/defective with respect to its live discovery-bounding path; live acceptance failed at the stage the PR was supposed to make safely refreshable.**

## 10. Evidence refs

Primary repository / code:
- PR #140 merge: `7df5ed0cbe9dd9217c56344e0caab47dd366915f`;
- current `main` pre-report baseline: `30f59b693cdef3eca520ddc78334850fdf850948`;
- `.github/workflows/steam-test.yml`: `collect.timeout-minutes=60`, canonical GitHub-owned production collector;
- `scripts/steam_production.py`: `SEARCH_CATEGORY_TYPES`, `SEARCH_CATEGORY1`, `search_params`, 50-row pagination and live collection;
- `scripts/test_fresh_deal_discovery_refresh.py::test_11_canonical_search_is_bounded_to_supported_paid_content_types`: structural parameter test only;
- accepted PR #140 report: `reviews/worker_reports/fresh-deal-discovery-refresh-fix-01.md`.

Production runs:
- last successful scheduled discovery: `35930927751`, 2026-09-23, source total 12977, 609 shortlist items;
- first subsequent scheduled cancellation sampled: `36071409364`, source total 13667, cancelled at owner timeout;
- post-PR-#140 discovery: `37120664964`, job `111195963281`, main @ `7df5ed0c...`, live total 100307, cancelled at `2026-10-03T12:45:32Z`;
- post-merge pre-AI fail-closed: `37120664975`, job `111195963506`;
- post-merge visual commercial fail-closed: `37120682411`, job `111196051157`;
- cancelled-discovery successors: mailing `37123911788` skipped, ingest-validation `37123914797` skipped, pre-AI `37123914757` skipped;
- latest successful Pages deploy before PR #140: `36998541896`, visual commit `6e0d7a36e906fbb3e383d4f6252b7dd7846ca4bf`, Pages artifact `11222941091`;
- post-PR-#140 deploy attempts: `37120687145`, `37120711123`, both skipped.

Canonical artifacts:
- manifest blob `3c5c43dfec230db4699ccfcb49cd8e8afd7e31b8`;
- shortlist index blob `2459f1e3a47cea4506e71c79ec85c185ece4e357`;
- mailing index blob `445803536668059c94c2cf0734f59afb2b18a3f4`;
- Store snapshot blob `a2bbea0dbd459fb9dbfecb784328a306d99cb241`;
- candidate context blob `a72c564dcff361ca748ae46ab466d14f641ab728`;
- PASS 1 work blob `7a262238820a98fd0c1fbbeb7eccdbed55109c2b`;
- Dossier work blob `5c196f86bb0becf4ab826b546a4cc3e7cad593d5`;
- PASS 2 work blob `b0f7179924eb13d7f21b52fdc7856ca3609346aa`;
- ranking lookup manifest blob `e35065b5f263f0f1423d8b933e0657e2fae165f9`;
- ranking lookup `m.json` blob `26bc0dfdbf3e4e3a6888f70b8d55d3cf4ec58d69`;
- current visual blob observed during trace: `24a1e97a1b1af553c0cae096dff6d6aadec43f8a`.

External sanity check:
- public Steam app page/search result for AppID `1233570`, checked 2026-10-03 during this diagnostic: active -95% promotion ending October 8, 2026;
- this was not used as Kazakhstan canonical eligibility evidence.

## 11. Smallest correct next action

Create one bounded follow-up **implementation task on the existing `Steam KZ production shortlist` owner only** to repair the live discovery input/traversal boundary so the supported paid-content universe is actually bounded against current Steam behavior and one normal GitHub-owned run can finish and commit within the existing production cycle.

The follow-up should:
- verify the real Steam parameter semantics rather than only the local `category1` string shape;
- keep the same single GitHub discovery owner and existing schedule;
- add a live-shaped deterministic regression/guard against implausible source-cardinality expansion;
- validate by one normal successful production discovery run, then confirm AppID `1233570`'s ordinary KZ eligibility/result;
- not special-case Catalyst;
- not create a second scheduler, queue, collector, semantic worker, or browser discovery path.

A blind rerun of the current workflow is not the smallest correct action: current evidence shows the same path reaches the 60-minute limit before completing.

## 12. Status

`diagnosis_complete_root_cause_identified`
