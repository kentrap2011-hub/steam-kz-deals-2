# Steam KZ appdetails: AppID 1697640 identity RECON

- **Task:** `steam-appdetails-1697640-identity-recon-01`
- **Date checked:** 2026-11-06 UTC
- **Source of truth:** `main`, RECON base `5e4fd5c553dc8ec83515a3eebb909e352611b1b8`; failing live run code `61d29f95582d74f83cf897c3fbe67c3d0d31139d`
- **Status:** `RECON_BLOCKED_UNVERIFIED` — actual offending `data.steam_appid` value and the original parent JSON are not preserved/readable. A storefront alias is strongly indicated but historical API cause is not proven.
- **Scope:** read-only analysis of original incident, exact code path, existing logs and limited public evidence. **No IMPLEMENT, tests, workflow/production dispatch, replay, backfill, source changes or report merge.**

## 1. Original incident and exact facts

Source: [GitHub Actions run #42033530995](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42033530995), run attempt 1, `workflow_dispatch`, executed 2026-11-05 13:11:14–13:47:37 UTC on `61d29f95582d74f83cf897c3fbe67c3d0d31139d`. Job `collect`, step `Collect Steam KZ catalog with partial publish failure isolation` failed.

The original job log, [job 127265698616](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42033530995/job/127265698616), shows:
- `admitted_base_count=425`, `bundle_surviving_cheap_gate=16`;
- `2026-11-05T13:16:03.999Z`: `appid:"239140"`, `stage:"parent_relations"`, `request_index:39`, `status:200`;
- `2026-11-05T13:47:37.606Z`: `appid:"1697640"`, `stage:"dlc_price"`, `request_index:1223`, `attempt:1`, `status:200`, duration `140.7ms`;
- immediately afterward `stage:"targeted_dlc_relations_failed"`, `error:"KZ appdetails App_1697640 contradicts requested AppID 1697640"`;
- `appdetails_diagnostics={first_429_seen:false,request_starts:1223,response_status_counts:{"200":1223}}`. Thus the collector's 429 guard was not the cause.
- `Verified parent-targeted DLC discovery incomplete; prior paid publication kept unchanged`. Downstream persistence/mailing/pre-AI was not completed; no new production publication was claimed.

Artifact inventory: `fetch_workflow_run_artifacts` for this run returned `[]`, so no attached raw parent/child appdetails snapshot was available there. The log emits requested IDs, status and counts, **not the raw JSON `data.steam_appid` or the specific parent `dlc` array**.

## 2. Verified code mechanism

Exact run source [`scripts/steam_targeted_paid_lanes.py`](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/61d29f95582d74f83cf897c3fbe67c3d0d31139d/scripts/steam_targeted_paid_lanes.py), lines 212–299, 320–335, 361–389; and [`scripts/steam_partial_publish_runner.py`](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/61d29f95582d74f83cf897c3fbe67c3d0d31139d/scripts/steam_partial_publish_runner.py), lines 1316–1339.

1. `suitable_base_ids` (lines 302–317) selects the current eligible base **games** from paid/review rules. The runner passes that set into `discover_dlc_for_bases`.
2. `discover_dlc_for_bases` fetches all admitted bases, requires `type == "game"`, and derives `direct` from *positive canonical members of their returned `data.dlc` arrays*. It then requests each distinct listed member in sorted numerical order, `dlc_price` phase. A verified two-hop branch is possible but this error occurred in the direct first-hop fetch loop.
3. `get_appdetails("1697640")` sends one exact `GET https://store.steampowered.com/api/appdetails?appids=1697640&cc=kz&l=english`. The call must have received HTTP 200.
4. `body.get("1697640")` must have yielded a dict, with `entry.success is True` and `entry.data` a dict; otherwise different `missing identity` or `missing metadata` exceptions would have occurred.
5. `_check_fetched_identity` failed at lines 330–335 **inside `get_appdetails`** before returning. To produce the exact `contradicts requested AppID` exception, `data.steam_appid` **must be present**, and `_canonical_appid(data.steam_appid)` must be a positive canonical decimal ID **different from `"1697640"`**. A missing field would have been accepted; a Boolean, float, zero, negative or noncanonical string would have emitted `has invalid AppID identity` instead. The raw JSON type is **UNKNOWN**: accepted possibilities are positive Python `int` or canonical ASCII decimal `str`.
6. `"1697640"` as the top-level **response key** is NOT the problematic inner `data.steam_appid`. The exception message repeats the **requested** ID and **does not print** the inner value. `239140` must not be reported as the observed inner value without an actual body or equivalent evidence.

## 3. Why this ID was requested — observed evidence vs inference

- **CONFIRMED:** `239140` was fetched as one of the 425 admitted `parent_relations` bases in this exact run, before the `1697640` direct child query. The algorithm derives every direct child only from those validated parent `dlc` arrays.
- **EXTERNAL CURRENT EVIDENCE:** The [Dying Light 239140 DLC listing at GAME-LOG.jp](https://gamelog-jp.com/game/239140/) shows `1697640` among DLC members, even though [Steam Index](https://steamidx.com/app/dying-light-1697640) calls `1697640` a separate `game` named *Dying Light*, and [Steam Index publisher listing](https://steamidx.com/publisher/techland) separately lists `239140` and `1697640` as Dying Light apps. Steam's current official [Store page /app/1697640/](https://store.steampowered.com/app/1697640/) redirects to `/agecheck/app/239140/` (observed through public web fetch on 2026-11-06).
- **LIKELY:** Root `239140` listed `1697640` in `data.dlc` and Steam's storefront alias/canonicalization caused the inner identity mismatch on fetching that child. This neatly fits the observed direct-child stage, actual parent lookup and public alias evidence.
- **UNKNOWN:** Whether it was **this exact parent's raw `dlc` list in the 2026-11-05 run**, or another eligible parent, that contributed the child, because source `direct[1697640]` and the original parent lists were not persisted; whether the original `data.steam_appid` equaled `239140`; whether the Store API actually redirected (HTTP 200 alone is not proof of an HTTP redirect); or whether this is stable and region-specific.

Do not conflate independent identifiers, matching titles, current Store page redirects, actual HTTP redirect response, and the **historical JSON**.

## 4. Direct API probe / bounded verification

Target, without any retries, fans or secondary requests:
`https://store.steampowered.com/api/appdetails?appids=1697640&cc=kz&l=english`.

2026-11-06 UTC: both a public web fetch of this URL and one bounded `curl` access attempt failed **before a JSON response was available** (web fetch: endpoint inaccessible; container `curl`: DNS resolution failure `Could not resolve host: store.steampowered.com`, HTTP status `000`). Therefore **no verifiable current HTTP status, raw response-key, success Boolean, inner `steam_appid`, type, parent relation or raw JSON was acquired in this recon probe**. No automatic retries, alternative endpoint spraying or production execution were performed. The HTTP 200/success conditions described above come from the original GitHub log and program path, **not** from a new API observation.

A future successful single bounded request must record UTC timestamp, original URL/params, final URL and redirect chain if available, HTTP status, JSON outer keys, type and value of `success`, `type(data.steam_appid)` and its literal value if present, `type(data.type)` and value; a parent `dlc` membership can be evidenced by an existing immutable artifact if available. Even a successful **current** API result cannot reconstruct the 2026-11-05 response byte-for-byte.

## 5. Competing explanations

| Cause | Status | Reason |
| --- | --- | --- |
| Actual appdetails inner-vs-requested ID mismatch | **CONFIRMED** | Exact source condition and historical exception; raw inner value absent |
| Storefront alias/canonical app `1697640 → 239140` | **LIKELY** | Official current page redirect and external paired app records; raw API field unverified |
| `239140` originally listed `1697640` | **LIKELY, not historic-proof** | Original run queried `239140` as parent; present-day DLC listing contains `1697640`; original list not stored |
| Malformed input ID or missing inner identity | **EXCLUDED for this failure** | Different exact exception paths |
| HTTP 429, 5xx or transport failure | **EXCLUDED for this failure** | Original HTTP 200, no 429 |
| Validator false positive | **NOT PROVEN** | It intentionally detects a mismatching exact ID; no evidence that this check alone is faulty |
| Steam metadata mutation between 2026-11-05 and now | **UNKNOWN** | No immutable raw old/current snapshots |
| HTTP redirect on API endpoint | **UNKNOWN** | Store page redirect does not establish API redirect |

## 6. Options, control plane and recommendation — proposals only

**Recommended immediate step (diagnostic only, not IMPLEMENT):** obtain one read-only, *bounded* official KZ appdetails JSON observation for `1697640` from an environment with actual Steam access and preserve the exact relevant field values/types and final URL; cross-check the parent relationship only against already-available evidence if possible. The desired root-cause evidence is the actual `data.steam_appid` and its type — not a guessed number. If it resolves to `239140`, investigate the verified alias case, not generic loss of integrity.

**Proposed eventual IMPLEMENT option A (conditional on verified metadata and a separate user decision):** in GitHub-owned DLC discovery only, differentiate a publicly verifiable Store alias back to a validated base `game` from an actual `dlc`. Maintain exact cross-source verification of both IDs and parent link; do not create a paid `App_1697640` offer or borrow `239140` price/ownership. Keep every other contradictory or malformed identity fail-closed. Add strict deterministic tests for alias, true DLC, unrelated mismatches, absent/malformed fields, KZ price and relationship scope; no widening DLC traversal.

**Option B:** augment failure diagnostics with bounded non-sensitive outer-key/inner-ID/type evidence without relaxing validation, to make the *next naturally scheduled* failure explain itself. Risk: does not recover publication by itself; consider log retention/privacy and no unbounded metadata logging.

**Option C (not recommended):** blindly ignore the `steam_appid` mismatch or silently skip all contradicting children. Risk: aliasing of a genuinely unrelated game/price, broken parent attribution and false completeness; contradicts current fail-closed semantics.

**Architecture preflight:** `config/execution_ownership_contract.json` and `config/daily_execution_contract.json` assign paid scope, identity/validation, current-price computation, completeness and publishing to the **GitHub control plane**. Any eventual exception must be an explicitly approved, narrow GitHub-owned change in the existing producer, not a new ChatGPT queue, runtime retry, schedule, broader discovery or hidden quota. Since a canonical authority for an alias exception has not been established, proposed implementation remains blocked pending real evidence, contract reconciliation and **new user consent**.

## 7. Stop, deliverable and next approval gate

- The incident was traced to the exact strict comparison path; it was **not fixed**.
- The likely Dying Light alias chain is supported by multiple independent current sources, but the **literal historical second AppID remains `UNKNOWN`** and the original exact parent edge remains **`UNKNOWN`**.
- Status: **`RECON_BLOCKED_UNVERIFIED`** on raw identity field proof.
- Only this report file is proposed in a report-only PR, left open/unmerged. **No code, algorithms, tests, policy, CI, runtime, Registry, Board or production changed.**
- The user subsequently approved one separately scoped diagnostic Steam verification; see section 8. A future IMPLEMENT remains unauthorized. Exact raw response evidence from a network-enabled environment is required to confirm the second number.

## 8. User-authorized bounded verification, 2026-11-06

The user authorized a *separate* limited evidence probe after RECON; they did **not** authorize any source or production implementation.

- Exact intended request: `GET https://store.steampowered.com/api/appdetails?appids=1697640&cc=kz&l=english`; no credentials, no POST, no batch, no automatic retry. Public web opening of this exact URL returned the tool's own `not accessible` error, **not** a Steam HTTP response. A single container `curl` attempt with `--retry 0 --max-time 18` returned `curl: (6) Could not resolve host: store.steampowered.com`, `HTTP_STATUS=000`, redirect count 0. The endpoint was not successfully contacted, so `HTTP status`, response outer key, `success`, `data.steam_appid` type/value and `data.type` for **this diagnostic** remain **UNKNOWN**. No repeated live API request.
- Separate **official storefront evidence**: read-only GET of `https://store.steampowered.com/app/1697640/` was observed redirecting to `https://store.steampowered.com/app/239140/`, on 2026-11-06, with a region-unavailable error page afterwards. **This does not establish an API-level redirect or raw appdetails inner ID.** Public source: https://store.steampowered.com/app/1697640/.
- Separate **SteamDB metadata**: https://steamdb.info/app/1697640/ showed `App ID 1697640`, `App Type Unknown`, `Last Known Name Dying Light Standard Edition`, with missing access token/partial information. This is compatible with a legacy/limited listing, but does not independently demonstrate `data.steam_appid=239140`. Other aggregators classify the app differently; no forced conclusion from metadata type.
- Status remains **RECON_BLOCKED_UNVERIFIED**. **Recommended bounded follow-up for the user/operator**: open the exact URI above once from a network-accessible machine and provide only (a) requested appid and observed HTTP status/final URL/redirect count; (b) outer response keys; (c) exact `success` value/type; (d) `data.steam_appid` presence/value/type, `data.type`. Do not publish private tokens or cookies; do not treat a current result as the historical raw JSON. If those values independently prove the alias, propose a separately consented GitHub-owned surgical change preserving fail-closed.

**No source change, policy adjustment, CI/workflow change, production invocation or merge occurred during this diagnostic.**
