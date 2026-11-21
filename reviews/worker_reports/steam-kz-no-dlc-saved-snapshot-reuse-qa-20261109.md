# Steam KZ — no-DLC replay of saved Nov 9 snapshot: OFFLINE QA

**Verdict: OFFLINE_SNAPSHOT_REPLAY_PASS. Production cutover not tested or authorized.**

Scope: only kentrap2011-hub/steam-kz-deals-2; pinned main SHA d99ce24fce32ecab076f02c6039353d3be1de343. Source timestamp 2026-11-09T11:20:25.250256+00:00. Authorization: explicit "Тестируй" after checking whether the full current day's Steam games could be obtained without rerunning a GitHub Steam collection.

## Execution

- Isolated draft [PR #427](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/427).
- [Actions run 42677902095](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42677902095) on exact original test head e28c77fbb4eb28b5a90711b8bc75793f696d7e03: PR-only regression SUCCESS; collector job explicitly SKIPPED.
- Executed source: scripts/test_steam_kz_no_dlc_saved_snapshot.py, integrated into existing deterministic scripts/test_steam_targeted_paid_lanes.py regression. No new recurring workflow or production collector run. Existing targeted paid-lane regression 18/18 PASS; all other existing regression steps passed.
- Exact test log:
  NO_DLC_SAVED_SNAPSHOT_PASS source=907 source_dlc_excluded=528 games=365 packages=14 retained=379 simulated_mailing_chunks=3 store_active_retained=375 family_allowed=368 family_count=365 allowed_packages=14 source_mailing_projection=exact retained_price_discount=unchanged family_assignment=complete network=0 production_writes=0 downstream_rebinding_required=true

## Source correctness

Verified the current manifest and the complete 19 source chunks and seven mailing chunks against the same 2026-11-09 source stamp. Projection from all 907 full source TSV records to the existing mailing columns was an exact 907/907 match in original order.

A token-exact exclusion on the persisted verified_relevant_dlc reason:
- 907 original sale offers;
- 528 DLC App_ offers removed;
- 365 non-DLC App_ identities retained;
- all 14 independent Sub_ package identities retained;
- 379 total remaining, 379 distinct IDs, no unexpected removals;
- KZT, price, discount, names, product identity and other source/mailing fields unchanged for every retained row;
- new hypothetical mailing chunks (150 rows each) contain 150 + 150 + 79 records.

Using only the persisted same-source Store, metadata, content eligibility rules and family contract, the test ran the **unmodified real** build_pre_ai_family_graph.resolve on a reduced in-memory 379-item feed:
- 375 of the 379 are currently active in the saved Store snapshot;
- 368 satisfy the saved canonical mechanical eligibility actions and current Store-active gate;
- 368/368 were assigned once across **365 complete purchase families**;
- no addon child from the excluded DLC scope leaked into these families;
- all 14 Sub_ package offers remain represented in allowed family membership.

Scope denominator explanation: the 365 non-DLC source App_ identifiers are not all automatically semantically valid full games; the saved content rules classify some as obvious non-game addons, so 368 family-eligible inputs is correct. Four of the 379 also have inactive Store offers. Existing independent package content catalog contains 36 available candidate package routes, and is not deleted or interpreted as a reason to suppress any Sub_ product; individual package member DLC remains permitted inside purchased package metadata.

No Steam HTTP was made, no new full collector run, and no production output, cache, schedule, website or main source changed.

## Safety limits and required later work

This is an **offline snapshot and real family-resolver test**, not an end-to-end rebuilt live visual. Current canonical mailing policy still requires complete eligible-base targeted-DLC discovery (scope eligible_base_targeted_dlc_and_independent_sub_v3). Merely bypassing the DLC function without changing source completeness and downstream compatibility contracts is not safe. Existing Store/metadata/rules/families/semantic progress/visual references were originally published against all 907 keys; a future 379-offer production artifact requires a canonical new scope/generation and correct source timestamp/provenance, refreshed matching keysets, complete downstream publication checks, and no legacy DLC in the current UI. The old semantic evidence/cache must remain available for future ownership-based DLC search.

Standalone DLC offers disappear by definition under the proposed rule, including playable story DLC; bundle contents may still include addons and must remain intact. The free/giveaway lane is separate, unchanged and was not exercised by the test.

A future implementation must rerun offline full pipeline acceptance on the saved source snapshot through current content, package, family, scoring and publication logic with no Steam discovery; only then may a new production rule be safely accepted. Approximate observed potential speed saving is the previous 2,817.441 seconds DLC-stage timing, not a measured 4-minute production run.

**Disposition:** TEST_PASS_OFFLINE; NO_COLLECTOR_RERUN; NO_MAIN_CHANGE; IMPLEMENT_NOT_PERFORMED. This is an isolated test-only draft PR and should not be merged as a permanent day-pinned test.
