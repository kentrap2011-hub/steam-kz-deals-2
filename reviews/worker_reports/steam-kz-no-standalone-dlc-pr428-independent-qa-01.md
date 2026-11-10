# Independent L3 QA — PR #428: no standalone DLC (Chat 3)

**Task:** `steam-kz-no-standalone-dlc-pr428-independent-qa-01`  
**Review date:** 2026-11-10  
**Scope:** `kentrap2011-hub/steam-kz-deals-2` ONLY; read-only source/production review and report-only PR  
**Reassessed verdict (after user clarification, 2026-11-10):** **PASS_FOR_DIRECTOR_MERGE, WITH DISCLOSED/ACCEPTED RESIDUAL RISKS** — QA does not merge or authorize unrelated production actions.  
**Source PR:** [#428](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/428), draft, not merged  
**Verified exact source HEAD:** `8d9394dd418cac6f127c69df15eeec5383820202`  
**PR original BASE:** `d99ce24fce32ecab076f02c6039353d3be1de343`  
**Main observed at QA/report branch creation:** `407087fd97413e1a4b95b423c8a4eb8a79ab1b82`  
**Saved 2026-11-09 snapshot ref:** `d99ce24fce32ecab076f02c6039353d3be1de343`.

## 1. START, authority and architecture preflight

Read the complete `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, assigned `WORKER_TASK_STEAM_KZ_NO_STANDALONE_DLC_PR428_INDEPENDENT_QA_01.md`, relevant `PROJECT_ROUTES.md`, `PROJECT_DECISIONS.md#STEAM-DLC-SCOPE-002` **on the PR head** (not merged into main), `config/execution_ownership_contract.json`, `config/daily_execution_contract.json`, `config/mailing_policy.json` (main and PR head), `config/feed_integrity_contract.json`, relevant workflow paths and `config/site_publication_resilience_contract.json`.

Architecture preflight: **(1)** GitHub Actions owns source scope, collector, retry, completeness, queue, downstream generation, persistence; **(2)** the user-approved product scope is expressed by PR-head `mailing_policy.json` and `STEAM-DLC-SCOPE-002`; **(3)** QA does not transfer control plane to ChatGPT; **(4)** no new recurring workflow/queue/quota is authorized. Source activation's auto-collector was initially considered a consent blocker; the user subsequently confirmed that an additional merge-triggered rebuild is acceptable. The updated, scoped assessment is in §7. No external repositories, Steam API, live HTTP probes, `workflow_dispatch`, production mutations or source merge were used.

## 2. Exact PR delta and source behavior — CHECKED

The exact PR HEAD is unchanged from the task binding. PR #428 changes eleven files: `CURRENT_TASK.md`, `PROJECT_DECISIONS.md`, `PROJECT_ROUTES.md`, `config/mailing_policy.json`, `config/mailing_policy.md`, implementation report, `scripts/steam_partial_publish_runner.py`, `scripts/steam_production.py`, `scripts/steam_targeted_paid_lanes.py`, `scripts/test_steam_targeted_paid_lanes.py`, `scripts/validate_mailing_policy.py`. No source workflow, cache or output artifact is changed by this PR.

- **CHECKED**: new source scope `game_and_independent_sub_without_standalone_dlc_v1`; `dlc_discovery.mode=disabled_until_owned_library`; `standalone_offers_enabled=false`; `requires_complete_verified_relations=false`; `global_category1_21_traversal=false`; `owned_base_expansion=separate_future_task`. Exact import-time and call-time mismatched-mode guards fail closed.
- **CHECKED**: active runner still obtains suitable base IDs and independently classified on-sale `Sub_` package offers from the bounded `category1=998` Games Search. It calls only `targeted.current_standalone_dlc_offers`, which returns no standalone DLC, performs no parent/child KZ `appdetails` GET, reports zero relation/price lookups, `relation_complete=null` (not falsely certified), and `scope_complete=true` for the **disabled lane under the newly approved scope**, not the legacy DLC graph. Overall manifest completeness still depends on Search segment state.
- **CHECKED**: dormant `discover_dlc_for_bases` remains for historical deterministic tests but has no invocation from the current production runner. No new `category1=21` or broad `996` partition; single `998` traversal remains, with no raw Top-N and existing Search total/price-bound checks.
- **CHECKED**: unchanged rules: `cc=kz`, paid `discount >=50%`, `0<KZT<=4500`, local price rejection, review/quality/suitability checks, independent `Sub_` gate, separate free/giveaway lane, existing downstream Deep/visible top-100 semantics. The existing final output expression **`len(selected) > 800`** remains in the manifest and shortlist index; at 800 it is false, at 801 true. No threshold bypass or removal.
- **NOT TESTED live**: actual new no-DLC collection/network runtime/Steam availability, true elapsed time, and network-source completeness under current Steam conditions.

Source PR test adds a patched GET-forbidden check, disabled-policy fail-closed negatives and Sub retention. These are CI-backed checks, but are not a full production run.

## 3. Independent saved-snapshot replay evidence — CHECKED directly from full persisted data

I separately read the **complete 19 source TSV files and all 7 mailing TSV files** at the immutable saved 2026-11-09 ref, plus source manifest, both indexes and the mailing integrity attestation. In two bounded retrieval batches I checked the actual rows/columns and compared each of the 26 chunk blob SHAs against the attested blob identity. **26/26 matched**, 907/907 original source/mailing rows were aligned in original order, with **zero column-projection mismatches**. The attestation is against manifest blob `feff5fa3e7c2de551cbc5032865e08d28ff5c76f`, source index blob `ffc75202e32a536919b42919c663e47d79be22ad`; source timestamp `2026-11-09T11:20:25.250256+00:00`, source contract `eligible_base_targeted_dlc_and_independent_sub_v3`.

An independently applied exact-token test for `verified_relevant_dlc` in the persisted `reasons` field yields:

| Category | Count |
|---|---:|
| All saved paid source offers | 907 |
| Excluded standalone App DLC | 528 |
| Retained ordinary `App_` offers | 365 |
| Retained independent `Sub_` offers | 14 |
| **Total retained** | **379** |

Across all retained rows, existing source/mailing identity, AppID, name, KZT price, displayed discount and every mailing-projected column match exactly. I found **zero** malformed retained offer IDs, non-positive/missing/over-4500 KZT final prices, discounts under 50%, or excluded non-App identities. Retained keys were unique within each verified chunk batch; the original test-only PR #427 independently asserts 907 unique source identities and 379 unique retained identities. Nothing was written to production.

**Package nuance independently verified:** all fourteen `Sub_` source/mailing identities are present. Thirteen have exact matching prices/discounts and complete member content in the saved `fixed_package_options.json` (a **separate, scoped purchase-options catalog**, not the authoritative list of all source `Sub_` offers). The fourteenth, **`Sub_28005`**, is **not** in that scoped purchase-options document but *is* present with exact package ID, 90%/330 KZT Store purchase route in saved `store_snapshot.json`, complete `content_metadata.json` with member AppID 230820 and a package content rule `keep_for_ai_then_resolve_condition`. Thus **not an absent Sub source offer**. Six of the saved independent Sub packages have DLC members in their verified package content; those members are not independently removed by PR #428. The separate saved fixed-package document resolves 36 purchase routes overall; contents do not imply member Taste fitness.

**Earlier independent-work caveat:** PR [#427](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/427), CI [42678253183](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42678253183), contains a genuine offline call of the real `build_pre_ai_family_graph.resolve` with 379 filtered source entries, yielding 375 Store-active, 368 rule-allowed inputs assigned to 365 families, with all 14 Sub keys assigned. I read its test/report and independently checked the whole persisted source/mailing inputs and package evidence above. I **did not independently re-execute** its actual Python resolver or full pre-AI scoring; classify that part as **PRIOR CI EVIDENCE / NOT INDEPENDENTLY EXECUTED**. The family resolver code was separately inspected for package membership and exact coverage assertions.

## 4. CI — exact source HEAD

Verified GitHub check-runs and actual regression job steps/log at **`8d9394dd418cac6f127c69df15eeec5383820202`**:

- [Steam KZ production shortlist run **42682164573**](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42682164573): **regression SUCCESS** (job `129379311840`); **collect SKIPPED** (job `129379314741`, expected on PR).
- Discovery scope regression **20/20 PASS**; targeted DLC + independent-package regression **19/19 PASS**; other scheduled PR regressions in the job successful.
- [Backlog dispositions **42682164493**](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42682164493): SUCCESS.
- [Site task registry validation **42682164408**](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42682164408): SUCCESS.

**These checks establish only PR-only deterministic regression, not new collector completion, downstream matching-generation build, visual publication, or live DLC removal.**

## 5. Downstream binding and current state — CHECKED code; NEW GENERATION UNVERIFIED

Actual route inspected: `steam_partial_publish_runner.py` source manifest and shortlist → `build-mailing-feed.yml` direct lossless mailing projection and blob attestation → `build-feed-ingest-validation.yml` compact validation with exact blob/tree identities, policy blob and needs_tuning gates → `build-pre-ai-store-snapshot.yml` / Store/metadata / package-content path → content rules, historical-taste/current-feed scoping and family resolver → history, commercial/semantic generation → `build-daily-visual-payload.yml` → `data/production/visual/current.json` → read-only `deploy-visual.yml` / site.

- Source/manifest/mailing timestamp, counts and Git blob bindings are required; `legacy_offer_scope.py` intersects historical INCLUDE decisions with exact current offer identities, records out-of-feed keys and fails stale family metadata/eligibility bindings. No semantic/Dossier/Deep cache is deleted by the PR. **Actual post-cutover semantic rebinding NOT TESTED.**
- **Old proof is not new proof**: saved Nov 9 index has 907 and `needs_tuning=true`; old compact feed validation at the saved ref is for **703** with outdated blob hashes, and the saved 100-card visual is old-generation. None proves a new 379-item production generation.
- **Important later main movement (2026-11-10):** current `main=407087fd...` now holds a *different, successful normal legacy-scope* commercial snapshot at `2026-11-10T03:17:43.909846+00:00`: **687 offers, including 391 standalone DLC, 12 Sub offers, 284 other App offers**, `needs_tuning=false`, `eligible_base_targeted_dlc_and_independent_sub_v3`. The current 100-card visual was regenerated `2026-11-10T03:20:17.488226+00:00` against the same Nov 10 old-scope source. Neither 907 nor 703 is the **current** snapshot. PR #428 is still unmerged; DLC-off production cutover **has not happened**.
- **ACCEPTED TRANSITIONAL RISK: possible mixed-generation race.** New-policy push also activates `build-pre-ai-store-snapshot.yml`, `build-content-eligibility-validation.yml` and `build-offer-family-resolution.yml`. `scripts/discovery_freshness.py::assess_discovery_freshness` checks timestamps, complete/coverage, candidate counts and cycle age, but **does not compare `source_scope_contract` in the manifest/shortlist to newly loaded policy**. Today's old 687-source snapshot is fresh and below 800. Thus the inspected freshness predicate **cannot itself prevent** a new-policy downstream branch from consuming old-scope DLC while the new collector is pending. Other later guards may reject some paths; the complete concurrent scheduling/rebind behavior has **not been independently proven safe**. Do not claim a production leak was observed, but do not certify its absence. The user expressly accepts temporary legacy DLC visibility during the transition; this is not a source-PR merge blocker under the clarified goal.
- Historical keys should remain historical semantics only; current commercial cards must derive only from new authoritative current-scope generation. No fresh end-to-end compact proof, package/family graph, pre-AI candidate binding, or visual/site proof exists for the DLC-off source.

## 6. Adversarial negatives — checked vs unverified

| Negative/guard | Result |
|---|---|
| Threshold **800/801** | **CHECKED code/policy**: strictly `>800`, unchanged; separate independent execution of the boundary NOT TESTED. |
| Missing, malformed or non-KZT price, discount <50%, price >4500 KZT | **CHECKED** source local KZT/discount gates, strict dormant DLC price parser and 20/20 scope CI; all retained Nov 9 saved rows valid. No live failure injection. |
| Incomplete Search page/segment | **CHECKED code**: segment failures recorded; source coverage marked incomplete if failed segment exists and feed ingest demands complete. Network scenarios NOT TESTED. |
| Independent `Sub_` and DLC inside package | **CHECKED persisted**: 14 saved Sub identities and package-member paths, six packages with DLC members; one-package-route `Sub_28005` explicitly accounted for. Future fresh end-to-end package acquisition UNVERIFIED. |
| Wrong source/manifest/mailing SHA/timestamp | **CHECKED validator code**: fail-closed attestation, exact source blob and tree identity, count/timestamp/freshness checks; stale compact 703 cannot substitute. Dedicated new-scope negative E2E NOT TESTED. |
| Disabled DLC mode / legacy relation parentage | **CHECKED source + exact HEAD 19/19 CI**: strict mode guard, zero-GET disabled function, historical parentage code retained but not called in active source. |
| Historic semantic caches | **CHECKED PR file list + scoping code**: no deletion, current-feed intersection; post-cutover effective semantic/history behavior NOT TESTED. |
| `last-known-good` stale DLC leakage | **UNVERIFIED edge**: `preserve_last_known_good` in `steam_partial_publish.py` re-adds prior rows for exact `failed_keys`; runner's post-preservation `row_meets_current_paid_gate` checks **price/discount only**, not the newly disabled DLC scope or `verified_relevant_dlc` reason. A prior DLC could be reused **conditionally if its exact App key becomes a current failed game/search key**. No such leakage observed in saved historical queue (its 4 unresolved App entries had no prior site data), but a deterministic negative regression should prove rejection under an exceptional failure. This remains an untested recovery-path edge. Under the clarified acceptance of temporary old DLC rows it is a documented non-blocking residual risk; it does not demonstrate continued standalone-DLC Steam GETs. |

## 7. Reassessment after explicit user clarification — PASS_FOR_DIRECTOR_MERGE with accepted residual risks

**Assessment update (2026-11-10; supersedes the earlier BLOCKED_SAFETY recommendation):** the user clarified the actual priority: avoid unnecessary Steam requests and failure exposure from standalone DLC that the project does not currently use. The user explicitly accepts (a) an automatic full collector run after PR #428 is merged and (b) old standalone DLC temporarily remaining in existing outputs. These are product/operational risk-acceptance changes, **not new technical test results**. QA retains its original checked/untested distinctions.

1. **Auto-collector on merge — CONFIRMED, NOW ACCEPTED (NOT A BLOCKER).** The existing main-push workflow matches PR #428 source/config changes and starts a full collector. This is expected and the user has said it is acceptable. QA itself still launches no run; the Director owns any merge decision and subsequent normal GitHub run.
2. **Old-scope generation may temporarily feed downstream — UNVERIFIED TRANSIENT, NOW ACCEPTED (NOT A BLOCKER).** A new-policy downstream workflow may initially see the prior complete 687-row generation because existing freshness checks do not test the new source-scope marker. The user has said old DLC remaining temporarily is acceptable. We do **not** certify an atomic new-generation cutover or an immediate DLC-free visual; the next accepted normal collection should establish the new canonical source scope.
3. **Legacy last-known-good DLC carryover after a failure — UNVERIFIED EDGE, NON-BLOCKING WITH DISCLOSURE.** Old DLC rows could conditionally reappear if the recovery mechanism encounters a previously DLC-labeled App key as a failed key. This is an inherited-row recovery path, **not evidence of fresh DLC parent/child KZ appdetails requests**. It merits an offline negative test later if DLC residue provably causes downstream failures, but QA has no evidence that this conditional edge blocks current ordinary game collection.

**Central requirement — CHECKED in source + exact-HEAD CI:** the active PR #428 production source path disables standalone DLC discovery and performs **zero** targeted standalone DLC parent/child KZ appdetails GETs; dormant legacy traversal is not called. Games Search remains bounded and complete under its existing gate; ordinary App_ and independent Sub_ offers are kept, DLC members inside packages are not stripped. Price/discount gates and the **800** threshold are unchanged. Saved full 907→379 snapshot replay and 19/19 + 20/20 CI checks support no loss of eligible ordinary App_/Sub_ from that saved dataset.

**Verdict: `PASS_FOR_DIRECTOR_MERGE` (scope-limited).** This supersedes the prior `BLOCKED_SAFETY` **for the three disclosed activation/residue risks only** after the user's clarification. It means the **independent QA does not object to Director acceptance of PR #428 on those grounds**; it is not an assertion of already successful live no-DLC collection, new-generation downstream completeness, faster elapsed time, or zero transitional DLC on site. The Director still needs to verify current exact source HEAD/CI, appropriate merge authority and no material drift under the project's normal gates. No QA grant to merge #428 directly is implied.

**One bounded Director next step:** consider accepting **source PR #428** through existing Director merge gates without creating an additional scope-gating work package solely for the accepted risks; let the **existing** merge-triggered GitHub collector run normally. Inspect the resulting source manifest and collector outcome for the new source-scope marker, zero standalone DLC GETs and continued ordinary App_/independent Sub_ eligibility. If an actual DLC-caused error still blocks ordinary games, treat that as a new evidenced defect rather than as a presumed QA blocker.

## 8. STOP and disclosure

**Final after user clarification:** `PASS_FOR_DIRECTOR_MERGE` with the above disclosed and accepted risks; no QA objection to Director processing source PR #428 under normal gates. This is a report-only review; no source/main changes, semantic worker writes, production artifacts, Steam network probes, GitHub collector dispatch or new test workflow run were performed. Independent whole-snapshot checking was completed; live/offline full downstream generation and the listed failure-injection cases are explicitly **NOT TESTED**. The verification required multiple read-only chunk fetches and contract/workflow checks; a compact permanent QA report plus exact immutable refs avoids repeating these expensive exploratory reads.
