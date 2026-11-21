# RECON: Steam nested DLC 235960 — root cause and pre-merge GitHub live-smoke design

- **Task:** steam-nested-dlc-235960-root-cause-live-smoke-design-01
- **Mode:** RECON, report-only. No source, policy, workflow, tests, schedule, production or pricing modifications.
- **Final status:** **RECON_BLOCKED_UNVERIFIED** (precise failing origin root and historical Steam JSON are not evidenced).
- **Source of truth:** kentrap2011-hub/steam-kz-deals-2, main at start = 428b4ecb0cd62dd8df83911ab2fe39d801179461, incident source = b24a34027e4c96af40efca8554a954a635d27173.
- **Incident:** https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42315924316
- **Report-only PR:** draft; no self-merge.

## 1. Exact incident facts: confirmed

The 2026-11-07 UTC scheduled Steam KZ collect failed after 3246.2 seconds in the stage targeted_dlc_relations_failed with the exact error:

> DLC App_235960 contradicts verified parent relation

From the actual GitHub Actions job log (job 128228367673), 375 admitted base games, 16 preliminary independent Sub-package candidates, 1817 Steam appdetails request starts and **1817 HTTP 200 responses; zero appdetails 429**. The Store detail GET records are:

| Requested AppID | GET stage | Request index | HTTP | Timestamp UTC |
|---|---|---:|---:|---|
| 2820 | parent_relations | 3 | 200 | 2026-11-07 00:08:35 |
| 201310 | dlc_price | 390 | 200 | 2026-11-07 00:18:59 |
| 235960 | dlc_price | 404 | 200 | 2026-11-07 00:19:12 |
| 1697640 | dlc_price | 1117 | 200 | 2026-11-07 00:39:08 |

The log reports requested IDs, response status, stage and pacing, **not** the returned data.dlc, data.fullgame, data.type, data.steam_appid or per-child origin-root maps. The run has zero GitHub artifacts. HTTP 200 does **not** prove the relationship contents. The prior 2026-11-06 run 42262206049 ended at an unrelated 874344 HTTP 502; that incident does not establish this relationship.

Producer: scripts/steam_partial_publish_runner.py lines 1317–1339. It invokes targeted.discover_dlc_for_bases from the admitted root set and, on any relationship exception, stops, preserves the prior published paid data and does not advance mailing/pre-AI. This is not the earlier 1697640 game-alias identity mismatch and does not indicate an appdetails 429.

## 2. Exact failing branch: confirmed code consequence versus unknown payload

The implementation on main in scripts/steam_targeted_paid_lanes.py:

- Lines 389–411: get and validate all admitted roots as game; construct their exact direct DLC membership.
- Lines 413–426: retrieve root-listed AppIDs; allow only separately proven game aliases.
- Lines 428–467: optionally build only one further root→intermediate→child relationship using exact membership; no arbitrary recursion.
- Lines 489–529: for each DLC (type = dlc), inspect its fullgame parent, direct-bases map and nested-bases map.
- **Lines 514–518 are the only site emitting the incident's exact error.** It is raised in the else branch where the child has a valid non-null fullgame.appid that is not among direct_bases. For at least one base in the union of direct_bases and nested_bases, that declared fullgame parent is **not present in nested_bases[base]**.
- Lines 529–531 verify parent **before** any absent/null/empty price_overview skip. Consequently an unpriced/free child can still abort the collector; removing it merely because it is not paid would weaken source completeness.

This proves the failed **condition**, not which exact origin base or parent value caused it. The error text lacks the base and declared parent. Contrary examples would emit different errors: direct-base parent with nested overlap emits "has contradictory nested relation"; invalid intermediate fullgame emits "DLC intermediate ... contradicts base ..."; child with no fullgame and a nested claim emits "missing nested parent proof".

Potential *unproven* payload shapes:
1. App_235960 is directly listed by a root while its fullgame identifies an intermediate, but the same root lacks an exact listed intermediate→235960 path;
2. App_235960 is attributed to more than one admitted root and only some roots prove the chain;
3. App_201310 is missing from a relevant root list, or its own fullgame conflicts with that root;
4. the actual cc=kz fullgame.appid is not 201310, or another malformed/contradictory edge exists.

The existing synthetic test scripts/test_steam_targeted_paid_lanes.py lines 374–516 **already succeeds** for a **single** 2820 root listing both 201310 and 235960, with 201310 listing 235960 and child.fullgame.appid=201310. Therefore a simple assertion that the existing algorithm cannot handle any 2820→201310→235960 chain would be contradicted by its tests. The actual extra/missing edge must be established before changing the branch. No source patch is justified solely by the test fixture.

## 3. Field-level evidence matrix (do not conflate product pages with cc=kz JSON)

| Requested AppID | type | data.steam_appid | data.fullgame.appid | relevant data.dlc / origin |
|---|---|---|---|---|
| 2820 | **game implied**: reached later stage after root validation | if present, must equal 2820; raw value UNKNOWN | UNKNOWN | root's actual membership UNKNOWN; admitted root GET confirmed, not any child edge |
| 201310 | UNKNOWN (game or dlc may serve as intermediate) | UNKNOWN in raw log | UNKNOWN | membership of 235960 UNKNOWN |
| 235960 | **dlc implied**: exact error can occur only past type=dlc gate | if present, must equal requested ID under strict fetch; raw value UNKNOWN | positive canonical AppID, but exact value UNKNOWN and **not a directly admitted root for this candidate** | exact direct/nested origin roots and middle IDs UNKNOWN |
| 1697640 | UNKNOWN for this incident | UNKNOWN | UNKNOWN | successful HTTP 200, no causal evidence for this failure |

Public-facing product evidence, **not the same as returned KZ appdetails JSON**:
- https://store.steampowered.com/app/201310/ says X3: Albion Prelude requires X3: Terran Conflict (App_2820).
- https://store.steampowered.com/app/235960/ says X3: Albion Prelude Bonus Package requires X3: Albion Prelude (App_201310) and offers a Download action; it is not evidence of a current KZT paid sale.
- https://steamdb.info/app/201310/dlc/ lists App_235960 as a DLC of App_201310.
- Historical PR #404: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/404 documents this candidate path and expressly says original cc=kz JSON was absent. PR #408 game-alias rule has a distinct proven case: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/408 .

### Read-only API check attempted (bounded: 3 exact IDs)

Requested the public endpoint on 2026-11-07 for **only** AppIDs 2820, 201310, 235960 using exact query form:
- https://store.steampowered.com/api/appdetails?appids=2820&cc=kz&l=english
- https://store.steampowered.com/api/appdetails?appids=201310&cc=kz&l=english
- https://store.steampowered.com/api/appdetails?appids=235960&cc=kz&l=english

The web fetch did not permit API access; isolated runtime network DNS to store.steampowered.com also failed. No valid live JSON was returned. No retries, extra IDs, GitHub workflow, production or fan-out request was started. A future newly fetched JSON **cannot establish** the historical 2026-11-07 response byte-for-byte.

To unblock verification, obtain a short, sanitized excerpt of each exact requested entry containing success, data.type, data.steam_appid, data.fullgame.appid, data.dlc (complete membership for the three IDs), and for 235960 only the presence/absence and source-bounded validity of data.price_overview. Additionally require the **exact admitted origin roots for App_235960** from the production resolver (direct[235960] and nested[235960]) and, only if necessary, the relevant additional root/middle fields. A later enhanced diagnostic/smoke may produce these as bounded IDs and membership booleans without publishing bulk JSON. User-provided current JSON is useful current evidence, but cannot retroactively prove historical values.

## 4. One bounded conditional source fix (NOT authorized; root identity still unknown)

After the missing live origin-root proof is captured, **extract the existing per-candidate root/parent/chain validator into one production-shared pure function**. Use it to reconcile a redundant direct root→child listing with a true root→intermediate→child link **only** when all three AppIDs, both membership edges, the intermediate root's fullgame (if present), and the child's exact fullgame parent are positively verified for that **same origin root**. Preserve multiple provenance roots separately: an unrelated or unmatched root must **not** inherit another root's proof or silently become valid. Retain fail-closed on any still contradictory origin rather than suppressing an error just to restore the collector.

This is a **conditional candidate fix**, not a proven diagnosis of which edge is wrong. If raw evidence instead shows a foreign/missing root or a truly contradictory API response, stop and present that exact conflict for separate policy choice; do not auto-apply this reconciliation. Do not add an AppID-specific allowlist, drop the invalid-origin root without policy evidence, weaken _check_fetched_identity, let a product-page title replace Store relations, or skip parent validation for unpriced DLC. Existing KZT 4500 maximum, >=50% discount and zero/absent price handling remain unchanged. The existing test fixture (single root) must be extended for the **actual** conflicting shape rather than merely made green again.

## 5. DESIGN ONLY: short pre-merge GitHub Actions live smoke

**Trigger that actually works before merge:** one source PR to main extending the **existing** .github/workflows/steam-test.yml pull_request regression route with an explicitly gated, tiny PR-only smoke job/step. It checks out the PR HEAD and uses the proposed production-shared validator; it does not depend on a new workflow_dispatch existing on default main, and the existing collect job remains excluded for pull_request (workflow lines 3–27, 92–94 and 163–164). Run smoke only for the approved source PR, for example behind an explicit scoped PR label and a PR event including "labeled" (or an equally narrowly scoped PR-branch condition). Ensure enough permissions to read files only; never run a production writer/commit. A report-only PR does **not** trigger this smoke.

**Live input and physical request bound:** AppID 2820, 201310, 235960 initially, plus other root/middle IDs **only if per-origin diagnostic proof requires them**. Maximum **six unique IDs and six physical HTTP GET starts total**, including retries. Use scripts/steam_targeted_paid_lanes.py::get_appdetails (exact cc=kz/l=english, shared _SharedAppdetailsPacer, 180 physical starts in 300s and finite deadlines) with an additional smoke-only **hard physical-start budget of six** enforced at the actual GET wrapper; do not count just logical objects. No complete catalog, no uncontrolled additional children, no speculative root enumeration, no individual retries beyond that budget. Per HTTP timeout remains 25s, set a short job timeout (e.g. 5 min). On timeout, 429 exhaustion, 5xx, transport error, invalid JSON, inconsistent or insufficient origin roots, or cap exhaustion: emit **INCONCLUSIVE/nonzero** (or **FAIL** for a definitively invalid relationship), never PASS.

**Parity design:** a proposed extract must be called by the real production discover_dlc_for_bases candidate-processing branch **and** by the smoke runner. The smoke may read complete real parent data.dlc membership lists, but only fetch the preauthorized small ID set and pass real, unmodified membership arrays to the **same per-candidate** verification function. Include true direct and nested origin maps for the exact target; never synthesize or prune a contradictory root to force a PASS. If the current full root-admission universe cannot be reconstructed without collection, the smoke reports **subset PASS** only and explicitly marks **production-wide origin coverage INCONCLUSIVE**. Do not make a parallel simplified relationship checker or call the whole discover_dlc_for_bases with a fake truncated listing and claim equivalence.

**Runtime evidence summary (short and sanitized):** UTC timestamp, PR number and exact checkout SHA, actual requested AppID vs returned data.steam_appid, data.type, data.fullgame.appid, origin root IDs checked, relevant exact dlc membership booleans, chosen direct/two-hop path, reason for any rejection/skip, price_overview present/missing/null/empty or valid currency/discount/final only when appropriate, request/retry totals, and result PASS / FAIL / INCONCLUSIVE. Write bounded Actions step summary and small artifact; no whole raw JSON, response headers, secrets or massive output. Failure and inconclusive must make the CI status non-green; no automatic repeated polling.

**Meaning of PASS:** relationship evidence for App_235960 was accepted or correctly rejected under real current KZ data and the shared candidate validator; if its price is unavailable/zero/free, no paid candidate appears. Genuine unrelated/cross-root DLC identities, spoofed AppID, invalid price or missing necessary proof must still fail closed in deterministic negative tests; paid KZT <= 4500 and discount >= 50% are unchanged. PASS does **not** establish all 375 admitted roots, total collector completeness, deploy, mailing/pre-AI or site state.

**Offline + CI gates:** add deterministic positive/negative fixtures replicating the subsequently proven origin/root graph (not speculative single-root samples), canonical missing/contradictory cases, multi-origin, game-type intermediate, alias non-overlap, bad price, unpriced 235960 and request cap/timeout tests; run the existing complete PR steam-test.yml regression and relevant ownership/CI checks at exact source PR HEAD. A substantial workflow delta requires independent QA after Director acceptance. A successful targeted smoke precedes source merge but does not replace a separate, user-authorized full normal main collector→mailing→pre-AI acceptance run.

## 6. Architecture preflight and scope guard

1. Owner: GitHub Actions/GitHub repository own discovery, source scope, retries, validation, completeness, publishing, and daily execution under config/execution_ownership_contract.json.
2. Canonical authority: config/mailing_policy.json#paid_discovery (eligible-base targeted relations, 50% and KZT 4500) and config/daily_execution_contract.json (one GitHub-owned daily cycle); .github/workflows/steam-test.yml already has a PR-only regression path.
3. No control-plane logic moves into interactive ChatGPT; it performs report-only bounded developer RECON.
4. No new recurring automation, backlog, schedule, retry owner, quota or production writer. Proposed job is a narrowly gated pre-merge **test**; any future code/workflow change still needs explicit user authorization and separate source PR.

No files besides this report are modified; no production dispatch, source changes, site updates or self-merge. Existing pending work in CURRENT_TASK.md is left intact, as specifically required by this report-only task.

## 7. Acceptance state and decision gate

- **Done:** protocol/context/route/policy/decision review; exact failing source branch; actual GitHub run/job log and zero-artifact check; distinct public product evidence; attempted three constrained exact API reads; design of one conditional fix and PR-only bounded live smoke; one report-only draft PR.
- **Not established:** actual 2026-11-07 fullgame.appid for 235960, exact source membership arrays, all admitted origin roots and whether any are foreign or missing; precise data-dependent root cause and source patch correctness.
- **Status:** **RECON_BLOCKED_UNVERIFIED**. Maintain fail-closed. The next task, **only after an explicit new user approval**, should acquire the missing small raw relationships and origin-root evidence as a bounded gated live diagnostic/smoke before choosing and implementing the source correction. No automatic transition to IMPLEMENT or production.