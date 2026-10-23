# Steam Reviews 429 and publication reliability — bounded worker report

**Task:** `steam-reviews-429-publication-reliability-01`  
**Worker:** ЧАТ 3 (developer, not Director)  
**Verdict:** `NO_CONFIRMED_BOUNDED_FIX` — report-only; no production or semantic worker run  
**Source of truth:** `main` at `c3aac2c7dcf862e5d9c36efe2a00e5d60a14f6f6` (2026-10-23 17:20:59 UTC)  
**Scope:** only Steam Reviews evidence, existing Steam collector's review-enrichment code, its bounded tests, and publication-failure boundary  
**Artifact:** `reviews/worker_reports/steam-reviews-429-publication-reliability-01.md`

## START and ownership / architecture preflight

Read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, this task, relevant `PROJECT_ROUTES.md` passages, task's entry in `config/director_task_plan.json`, and current top `DIRECTOR_TASK_BOARD.md`. The registration is present in merged main commit `c3aac2c7`. No new task is inferred from historical incident records.

1. **Owner:** `config/execution_ownership_contract.json` assigns deterministic collection, queue/retry, persistence, validation, and production orchestration to **GitHub**, not ordinary chat; `config/daily_execution_contract.json` keeps collection in the existing daily GitHub cycle.
2. **Authorization:** `WORKER_TASK_STEAM_REVIEWS_429_PUBLICATION_RELIABILITY_01.md` allows one proven isolated Reviews code fix or report-only draft PR; it does not authorize global deployment/source policy edits.
3. **No ownership transfer:** all observations here were obtained read-only from the repository and persisted receipts. Interactive chat performed no production calls.
4. **No new mechanism:** no new retry loop, external rate-limit workaround, scheduler, queue, workflow, CI or validation proposed. `config/site_publication_resilience_contract.json` and already merged PR #238 own the separate Pages presentation-failure boundary.

## Evidence: latest **persisted** daily collector runs

Source: versioned GitHub `data/production/manifest.json` at `main` and at commit `b91a41416c52a4f69987f01851c9052de1fd52b0`; current persisted collector commit `a6d4f07e2544a869b2a94ed5a467bc734f9cd3f6`. Both records have UTC run start/end; no claim of external live Pages readback.

| Completed UTC | Steam Search HTTP 429 | StoreBrowse review HTTP 429 | AppReviews HTTP 429 | Review failures | AppReviews physical calls | StoreBrowse batches | Review candidate appids | Published paid shortlist |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-10-21 23:23:24 | 2 | 0 | 0 | 0 | 0 | not checked separately | 13,324 | 593 |
| 2026-10-22 23:26:22 | 1 | 0 | 0 | 0 | 0 | 75 successful, 0 failed | 11,562 | 443 |

The 2026-10-22 collector manifest records `review_search_surface_reused_appids=4143`, `review_storebrowse_fallback_appids=7419`, `review_exact_cache_reused_appids=0`, `review_appreviews_logical_components_attempted=0`, `review_storebrowse_retry_events=0`, `review_api_failed_requests=0`, `review_rate_limit_circuit_open=false`, `coverage_ratio=1.0`, `source_status=complete`, `game_failures_this_run=0`. All 11,562 candidate appids resolved without live AppReviews. The observed 429 events are **Search**, not Reviews. Historic route notes cite 204 Search 429s in an earlier run, likewise not proof of current Reviews failures.

The durable unresolved failure queue at `data/cache/steam_partial_publish_failures.json` still lists four game entries with stage `review_enrichment`, first/last observations on **2026-09-13** (one) and **2026-09-23** (three). They have not been observed failing anew according to their `last_seen_at_utc` and latest `game_failures_this_run=0`. Its `problematic_games=4` count represents durable **unresolved state**, not four fresh failures on 2026-10-22. No blind cleanup is authorized: current relevance/eligible source identity would have to be demonstrated separately.

The available GitHub code search index returned no matching hits; bounded direct file reads and versioned GitHub manifests/commit timestamps provided this evidence. A complete recent collection job transcript was not independently retrieved. No assertions about undisclosed live endpoint responses are made.

## Existing local handling (read-only code inspection)

- `scripts/steam_partial_publish_runner.py`: eligible rows use decisive Search evidence, then fresh exact cache, then paced batched StoreBrowse, then serialized AppReviews. StoreBrowse 429 respects positive `Retry-After` or bounded exponential wait and retries an individual batch; exhaustion falls through to AppReviews. A failed per-app review result records the exact game key as failed while other appids continue.
- `scripts/steam_production.py`: AppReviews allows one network worker, 5 attempts, `Retry-After`/bounded backoff and a circuit after 4 **consecutive** HTTP 429 events. The circuit's synthetic result is explicitly `ok=false`; successful/non-429 responses reset streak. A circuit-open outcome does not masquerade as a good rating.
- `scripts/steam_production_cached.py`: review cache TTL varies with review volume, affects **reviews only**, not current Steam discount or price; uncached AppReviews requests are paced at >=1-second intervals. The daily source is still live.
- `scripts/steam_partial_publish.py`: on an isolated failed game, `preserve_last_known_good` can carry forward an existing validated shortlist row. The runner rechecks the current paid gate on preserved rows; missing prior rows are not manufactured. Global source-price validation, catalog end, coverage and nonempty shortlist are intentionally stricter safeguards and can block a **new collector write** if source completeness is unproven.

The existing regression scripts `scripts/test_steam_review_fallback.py` (11 cases) and `scripts/test_steam_partial_publish.py` (6 cases) cover respective mocked 429, circuit/retry/fallback, and isolated game-preservation semantics. Tests were **inspected**, not executed by this report-only worker; these cases are not proof of a live Steam API health check.

## Independence of Reviews and Pages publication

PR [#238](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/238) is **merged** at `bb0d8bb7426c0e0afd277f7a3d7f5c808c2ca981` and isolates optional Pages sections while retaining strict material/receipt/global integrity. That protection is distinct from the collector: an individual Reviews failure may quarantine its own item and preserve last-known-good shortlist data, whereas truly invalid global source/completeness blocks a new canonical build as intended. Previously validated paid visual bytes are not automatically rewritten because one optional Pages section fails. None of these facts establishes **public HTTP freshness**, which is assigned to ЧАТ 4. Shared deploy/workflow edits would conflict with that lane and are prohibited here.

## Decision / next action

**`NO_CONFIRMED_BOUNDED_FIX`**: no present Steam Reviews 429 issue, local corruption, or Reviews-originated paid publication blocker is demonstrated by the latest two persisted runs. Do **not** patch code, change rate limits, rerun production, change global publishing or remove historical failure records merely to make counters zero.

If a subsequent **ordinary scheduled, GitHub-owned** collection records nonzero `review_storebrowse_429_events` or `review_appreviews_429_events`, `review_api_failed_requests`, `game_failures_this_run`, or surprising loss of preserved previously-valid games, Director may assign one new narrow RECON with the exact **run ID, UTC timestamp, manifest commit, per-app failure key and bounded job-log excerpt** to distinguish external rate-limits from a deterministic Reviews regression. Otherwise no implementation follow-up is justified. If public Pages delivery appears stale, address independently under ЧАТ 4 without treating it as Reviews failure.

## Writes and QA

- **Changed files:** this report only. No source, tests, CI, Actions, queues, site workflow, UI, currency, Dossier, Deep or global publication changed.
- **CI:** existing `.github/workflows/steam-test.yml` contains `test_steam_review_fallback.py` and `test_steam_partial_publish.py`; no new checks were created. This report-only PR's actual check outcomes are to be recorded from exact PR HEAD after creation.
- **Independent QA:** not required for code (no code PR); Director review of this report-only PR is appropriate. Any future code fix needs separate independent QA at its exact HEAD.
- **Execution:** no production/Deploy/workflow_dispatch, live Steam ingestion, semantic worker or merge was initiated.
