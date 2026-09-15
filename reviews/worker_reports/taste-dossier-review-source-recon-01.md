# Steam Review Source Recon 01

- Task ID: `taste-dossier-review-source-recon-01`
- Mode: `READ-ONLY / RECON`
- Date: `2026-09-15`
- Final status: `recon_complete_source_selected`
- Repository: `kentrap2011-hub/steam-kz-deals-2`

## 1. Scope and non-actions

This recon evaluated how the Steam review dossier Scheduled Task can obtain **individual Steam review bodies**, including a dedicated Russian lane, repeatable pagination, provenance and bounded adaptive sampling.

No runtime/config/code fix was made. No Scheduled Task UI was opened or changed. No `Run now` was pressed. No workflow was manually dispatched. No production inbox/cache artifact was mutated. Taste Semantic Producer was not changed.

The only project write performed by this task is this explicitly authorized durable report.

## 2. Architecture preflight

Canonical ownership remains unchanged.

Relevant sources read before recommendation:

- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `PROJECT_DECISIONS.md` (`TASTE-004`, `TASTE-005`, `TASTE-006`)
- `reviews/worker_reports/taste-dossier-full-defect-sweep-01.md`
- `reviews/worker_reports/taste-dossier-live-compact-acceptance-01.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/execution_ownership_contract.json`
- current `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- representative current group descriptor `.../g000003.json`

Preflight result:

1. **Current control-plane owner:** GitHub/GitHub Actions.
2. **Scheduled ChatGPT owner:** constrained external/semantic data-plane worker only.
3. Direct acquisition of review evidence by the Scheduled Task is already an allowed data-plane responsibility if a reliable source/tool exists; this would not itself transfer control-plane ownership.
4. GitHub-side deterministic source collection is also explicitly compatible with `config/execution_ownership_contract.json`, which assigns GitHub responsibility to collect sources GitHub can access directly. GitHub may prepare evidence, while Scheduled ChatGPT remains responsible for neutral semantic synthesis.
5. No new queue, retry authority, completeness authority, dossier scope, or independent scheduler is required for the recommended path.

The current dossier contract requires adaptive review sampling in batches of 20, Russian plus non-Russian lanes, up to 80 per lane / 160 total per game. The worker prompt requires actual Steam user-review inspection and records counts/batches/stop reason, while forbidding a raw-review archive in the dossier output.

## 3. Current group-3 test set

The current compact worker index has snapshot:

`c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`

Current group 3 (`g000003.json`) includes the required representative appids tested in this recon:

| appid | title |
|---|---|
| `1158890` | White Shadows |
| `1164940` | Trepang2 |
| `1169040` | Necesse |
| `1172380` | STAR WARS Jedi: Fallen Order™ |

## 4. Source candidates evaluated

### Candidate A — official Steam `appreviews` JSON endpoint

Valve documents this endpoint in Steamworks:

`GET https://store.steampowered.com/appreviews/<appid>?json=1`

Official documentation:

`https://partner.steamgames.com/doc/store/getreviews?l=english`

Valve documents these production-relevant fields and parameters:

- `filter=recent|updated|all`
- `language=<Steam API language code>|all`
- `cursor=*` for first page, then response `cursor` for the next page
- default batch up to 20; `num_per_page` up to 100
- `review_type=all|positive|negative`
- `purchase_type=all|steam|non_steam_purchase`
- response `reviews[]`
- `reviews[].recommendationid` — stable review identifier
- `reviews[].language`
- `reviews[].review` — actual written review body
- `reviews[].timestamp_created`
- `reviews[].timestamp_updated`
- `reviews[].voted_up` — polarity
- response `cursor` — next-page token

Valve explicitly says that when paging, `recent` or `updated` should be used so traversal can eventually reach an empty result set. Cursor values must be URL-encoded when reused.

This is materially better than store-page scraping because it provides the exact fields the dossier pipeline needs and a defined cursor mechanism.

### Candidate B — Steam Store product pages

Live store-page checks reliably expose store descriptions and review aggregates/language counts, but they do **not** consistently expose individual review bodies in the text surface available to the Scheduled Task.

Examples observed during recon:

- White Shadows store page: current aggregate review information was visible, but no dependable body pagination surface.
- Trepang2 store page: Russian review aggregate visible (hundreds of Russian reviews).
- Necesse store page: Russian review aggregate visible (thousands of Russian reviews).
- Fallen Order store page: Russian review aggregate visible (thousands of Russian reviews), and some crawled variants sometimes surfaced individual reviews.

The body visibility is crawler/page-state dependent, not a stable data interface.

Result: useful corroborating source, **not production review-body transport**.

### Candidate C — Steam Community review pages through normal web/search

Live Steam Community pages did expose actual review bodies for all four representative appids, proving that real individual bodies exist and are public.

Bounded examples (short snippets only; no usernames retained):

- `1158890` White Shadows: a negative body described the story/gameplay as “meh” despite good art; the page also exposed positive bodies, playtime and posting date.
- `1164940` Trepang2: bodies discussed intense combat, mission/base downtime and campaign quality; polarity and posting dates were visible.
- `1169040` Necesse: bodies discussed Steam Deck control failure, Terraria-like progression, colony management and late-game grind; positive/negative polarity and dates were visible.
- `1172380` Fallen Order: bodies included both English and an actual Russian negative review body discussing deliberately prolonged traversal; polarity and dates were visible.

However this surface is not adequate for production adaptive sampling:

- search/crawl decides which page snapshot is exposed;
- the web surface does not expose Steam `recommendationid` reliably with each body;
- there is no dependable cursor token tied to the returned body set;
- “See More Content” / dynamic loading is not a deterministic bounded API;
- language filtering is not reliable enough through search results (one Fallen Order page labelled its language display as English while exposing a Russian body);
- a worker cannot prove it sampled the next 20 independent reviews rather than a different search-engine/crawler snapshot;
- arbitrary `p=` or filter traversal is not a stable contract for hundreds of appids.

Result: useful live proof that bodies are public; **not suitable as the production sampler**.

### Candidate D — generic web search snippets

Search can occasionally expose snippets/bodies, but it has the same or worse problems as Candidate C: ranking/indexing dependence, incomplete bodies, no review ID contract, no deterministic language lane, and no cursor-based continuation.

Result: rejected for production.

### Candidate E — direct Scheduled Task access to Steam `appreviews`

The endpoint itself is valid, but the current Scheduled Task web-access shape is the blocker.

During this recon, direct attempts to open concrete group-3 URLs such as:

`https://store.steampowered.com/appreviews/1169040?json=1&filter=recent&language=russian&num_per_page=3&cursor=*`

were rejected by the current web tool as an unsafe arbitrary URL because it was not the exact URL surfaced by a prior search result/user message. Search did not surface the concrete `appreviews/<appid>` JSON URL as a fetchable result. A separate local container HTTP attempt also had no external DNS, so it cannot serve as a production substitute.

This reproduces the practical boundary seen in `taste-dossier-live-compact-acceptance-01`: the Scheduled Task could see Steam/web aggregate surfaces and some web content, but could not reliably obtain a paginated stream of individual review bodies for group 3.

There is no currently proven arbitrary-HTTP connector in the active worker contract/tool path that bypasses this restriction. The connected GitHub action is proven for repository reads/writes, not as a generic Steam HTTP proxy.

Result: **the direct Scheduled Task source is not proven production-usable in the current runtime**.

### Candidate F — GitHub-prepared review evidence from official `appreviews`

This path has a much stronger factual basis.

A historical GitHub Actions workflow in the connected repository `kentrap2011-hub/stopgame-ratings-data` proves that a GitHub-hosted runner can access the exact Valve endpoint without Steam credentials, cookies or browser state.

Relevant historical commit:

`1e21628f05dd600daf4a2ed045e210e4c6c1f643` — `Add one-shot Steam review threshold calibration`

That workflow used Python `urllib.request` with ordinary HTTP headers and called:

`https://store.steampowered.com/appreviews/{appid}?json=1&filter=all&language={language}&day_range=365&review_type=all&purchase_type=all&num_per_page=20&filter_offtopic_activity=1`

for both `language=all` and `language=russian`, with retries and a 20-second timeout. It successfully produced and committed the calibration artifact (`814ecce82fd097be59e8d6d403d50389ad0400ae`) and summary (`cb912b19df046ce4fac5d36c5244abeb2772e3c8`). This is direct evidence that GitHub Actions networking can reach and parse `store.steampowered.com/appreviews` unauthenticated.

That old calibration intentionally consumed only `query_summary`; it was not designed to retain review bodies. For the present dossier problem, Valve's current official schema confirms that the same response contains `reviews[].review`, IDs, language, timestamps, polarity and cursor.

Result: the source and GitHub network path are both proven. The remaining work is deterministic evidence shaping/delivery, not discovery of a new source.

## 5. Exact representative appid results

| appid | Actual body observed live | Positive/negative observable | Russian evidence | Deterministic pagination through current Scheduled web | Assessment |
|---|---|---|---|---|---|
| `1158890` White Shadows | yes, multiple Steam Community bodies | yes | store supports Russian localization; current normal crawled review page exposed English bodies; RU body availability through direct web was not deterministic | no | direct web unsuitable |
| `1164940` Trepang2 | yes, multiple bodies | yes | Steam store exposed ~600+ Russian reviews in current crawled snapshots | no | direct web unsuitable; API source viable |
| `1169040` Necesse | yes, multiple bodies | yes | Steam store exposed ~2.3k Russian reviews in current crawled snapshots | no | direct web unsuitable; API source viable |
| `1172380` Fallen Order | yes, multiple bodies | yes | thousands of RU reviews shown; an actual Russian body was observed live | no | direct web unsuitable; API source viable |

The exact aggregate counts vary as Steam receives new reviews; that is expected and is not used as dossier identity.

## 6. Russian lane conclusion

Russian review acquisition is technically first-class in the official endpoint:

`language=russian`

The response review objects include their own `language` field, so the preparer can verify that the Russian lane really contains Russian-tagged reviews rather than relying on page locale.

For the non-Russian lane, the deterministic recipe should use `language=all` and exclude any object where `review.language == "russian"`, deduplicating by `recommendationid`. This keeps the contract's lane meaning as “non-Russian,” rather than silently narrowing it to English only.

If the Russian lane returns zero reviews while the non-Russian lane has reviews:

- record Russian lane attempt explicitly;
- record `reviewed_count=0` and `source_exhausted_or_sparse` for that lane;
- do not fabricate localization evidence;
- continue the non-Russian lane normally.

## 7. Pagination and bounded sampling recipe

For GitHub evidence preparation, use the official JSON endpoint rather than HTML scraping.

Per appid / per lane:

1. Use `filter=recent` (or `updated`; choose one canonically and keep it fixed). `recent` is recommended because it is creation-time ordered and Valve explicitly supports cursor exhaustion for pagination.
2. First request uses `cursor=*`.
3. Use `num_per_page=20`, matching the canonical dossier `review_batch_size=20`.
4. Persist/use the exact returned cursor for the next request; URL-encode it.
5. Stop when:
   - the lane reaches the contract ceiling (`80` accepted review objects), or
   - the endpoint returns no reviews / no new unique recommendation IDs.
6. Deduplicate by `recommendationid` defensively.
7. For `language=all`, exclude Russian objects before filling the non-Russian lane.
8. Preserve only the fields needed by the semantic worker:
   - `recommendationid`
   - `language`
   - `review` body
   - `voted_up`
   - `timestamp_created`
   - `timestamp_updated`
   - optionally bounded playtime/helpfulness metadata if the contract explicitly needs it
9. Do not include SteamID/user profile/name in the evidence projection.

The Scheduled Task can then execute the existing adaptive semantic logic over the ordered 20-review batches and may stop early after the existing “two consecutive batches add no material change” rule. GitHub prepares evidence; GitHub does **not** decide semantic stability.

This preserves the current hard ceilings of 80 Russian + 80 non-Russian / 160 total per game.

## 8. Provenance model

The resulting dossier should continue to store compact provenance rather than raw review text.

Recommended provenance inputs from prepared evidence:

- Steam endpoint base URL / query policy, not a user profile URL
- `appid`
- capture timestamp
- lane (`russian` / `non_russian`)
- filter (`recent`)
- requested page size (`20`)
- number of pages/batches actually semantically reviewed
- actual reviewed count
- stop reason
- SHA-256 over the ordered list of sampled `recommendationid` values per lane
- optional evidence artifact content hash/binding

The final dossier must not copy full review bodies or usernames into the canonical dossier cache.

## 9. Auth, cookies, scraping state and operational constraints

### Auth/cookies

No Steam Web API key was required by the historical GitHub Actions fetch. No Steam login cookie or browser session was used. Valve's documented endpoint is a normal JSON GET endpoint.

### Browser state

None is required for the API path. This is a major advantage over store/community HTML.

### Rate/load behavior

No official per-client numeric rate limit was established by this recon. Therefore implementation should be conservative:

- bounded concurrency;
- retry only transient network/5xx failures with backoff;
- fail closed on malformed JSON/schema mismatch;
- no unbounded crawling;
- exact contract ceilings;
- cache/reuse evidence only within the prepared snapshot/evidence freshness boundary.

The prior GitHub calibration workflow already used bounded retries and a small delay between requests, which is a useful precedent but not a canonical rate-limit guarantee.

## 10. Direct Scheduled Task vs GitHub-prepared evidence

### Direct Scheduled Task

**Rejected for current production runtime.**

Why:

- current live acceptance already failed at group 3 due body-access insufficiency;
- this recon reproduced inability to open concrete `appreviews/<appid>` URLs through the current web tool;
- Steam Community/search can expose bodies but not a reliable cursor, stable ID stream or deterministic Russian filter;
- search-engine/page crawl behavior is not a production data contract;
- no already-proven generic HTTP connector is in the active worker path.

A future runtime that exposes a safe arbitrary unauthenticated GET tool could make direct access preferable, but that capability is not proven now and must not be assumed.

### GitHub-prepared evidence

**Selected.**

Why:

- GitHub is already the control plane and is explicitly allowed/required to collect directly accessible sources;
- GitHub Actions access to the exact Steam `appreviews` endpoint is already empirically proven in the user's connected repositories;
- Valve documents individual bodies, stable IDs, language, polarity, timestamps and cursor on that endpoint;
- body existence was live-verified on all four required group-3 appids, including a live Russian body on Fallen Order and large Russian populations on Trepang2/Necesse/Fallen Order;
- no Steam key, cookie or manual browser session is needed;
- it can produce deterministic ordered batches matching the contract's 20-review batch size;
- Scheduled ChatGPT still owns semantic theme/conflict synthesis only; GitHub does not take over semantic judgment.

## 11. Smallest production architecture change

Do **not** add a second scheduler and do **not** turn ChatGPT into an HTTP retry/control-plane owner.

The smallest safe architecture is to extend the existing GitHub pre-AI preparation so it also prepares a **bounded, snapshot-bound review evidence projection** from the official Steam `appreviews` endpoint for the exact dossier work already selected by GitHub.

Important storage constraint: review bodies should not be committed as a permanent raw-review archive in Git history. Prefer a short-retention GitHub Actions artifact (or equivalently ephemeral GitHub-owned object already readable through the connected GitHub tool) whose locator and content hash are bound from the compact worker projection. The connected GitHub capability includes workflow-artifact download support, so this delivery shape is architecturally consistent; the IMPLEMENT task must prove that the Scheduled Task can consume that artifact in its real runtime before activation.

The evidence projection should contain only bounded review fields, no usernames/SteamIDs, and at most the current contract ceiling. The canonical dossier cache continues to store only neutral synthesis + compact provenance/hashes.

This is a data-source/delivery extension to the existing GitHub pre-AI path, not a new queue/retry/completeness system.

## 12. Remaining proof boundary

One fact could not be directly live-tested without violating this task's restrictions: a **new GitHub Actions run** against the four exact group-3 appids was not dispatched. Therefore this recon does not claim that a newly written fetcher has already run in the target repository.

What is nevertheless proven separately and jointly:

- Valve currently documents the endpoint and individual review fields/cursor.
- Current live Steam pages expose real review bodies for all four required appids.
- Current live Steam pages expose substantial Russian review populations for the representative titles where expected, and a real Russian body was observed for Fallen Order.
- GitHub Actions in the user's connected environment has already successfully called and parsed this exact `store.steampowered.com/appreviews` endpoint without auth.
- Current Scheduled Task/web access does not provide deterministic direct endpoint access.

That is sufficient to select the source architecture, while leaving bounded end-to-end implementation acceptance for the next task.

## 13. Exact next IMPLEMENT scope

One implementation task only:

Implement and acceptance-test a GitHub-owned, bounded Steam `appreviews` evidence projection in the existing pre-AI path, using `filter=recent`, `num_per_page=20`, `cursor` pagination, explicit `language=russian` plus `language=all` filtered to non-Russian, `recommendationid` dedupe, current 80/80 ceilings, no user identity fields, short-retention non-Git-history body storage, and a compact hash/locator binding readable by the Scheduled Task. Its acceptance must use the four appids `1158890`, `1164940`, `1169040`, `1172380` and prove page 1 + page 2 bodies, Russian handling, sparse-RU behavior, deterministic evidence hashes and successful Scheduled Task read **without** pressing dossier `Run now` until that source acceptance passes.

## 14. One next step

Create the single IMPLEMENT/ACCEPTANCE task described in section 13; do not run the dossier Scheduled Task again before that task passes.

github_prepared_review_evidence_recommended
