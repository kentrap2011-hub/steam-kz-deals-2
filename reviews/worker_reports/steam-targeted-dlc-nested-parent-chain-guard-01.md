# Worker report — steam-targeted-dlc-nested-parent-chain-guard-01

- Role: NEW Chat 1; one bounded implementation, self-review and existing CI; no parallel QA or production.
- Source PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/404
- Base: main @ 7776434bf827dc4f533527f809af976b81b6836f
- Status: IMPLEMENTED_WAITING_DIRECTOR (conditional on final exact-HEAD CI verification recorded below).

## Root cause / known evidence / limits

The 2026-11-05 main collector run 42012646983 stopped at `targeted_dlc_relations_failed`: `DLC App_235960 contradicts verified parent relation`, 449 HTTP 200 appdetails and no initial 429. In the previous code, `discover_dlc_for_bases()` required every returned DLC `fullgame.appid` to equal **one of the admitted base AppIDs whose `dlc` list named that child**. That assumption fails for a nested DLC.

Public Steam product pages explicitly describe App_201310 (X3: Albion Prelude) as requiring App_2820 (X3: Terran Conflict), and App_235960 (X3: Albion Prelude Bonus Package) as requiring App_201310. Exact source pages: https://store.steampowered.com/app/201310/ and https://store.steampowered.com/app/235960/. SteamDB independently shows App_201310's DLC list with App_235960: https://steamdb.info/app/201310/dlc/ and parent metadata for App_235960: https://steamdb.info/app/235960/ .

**Unverified**: original live `cc=kz` appdetails JSON for App_2820, App_201310 and App_235960 was not persisted, including precise `type`, `dlc` and `fullgame` values. In fact, SteamDB's App_201310 metadata uses Game type while the Steam Store presents it as DLC. This PR does not hardcode the example, infer the response, or claim a confirmed live collector recovery.

## Implemented model and scope

1. Only KZ appdetails for the **existing complete set of quality-admitted base games**; the original Steam Search discovery, independent Sub offers and source proof are untouched.
2. Validate each root AppID, `type=game`, and exact set of positive canonical member IDs; fetch each direct member **once**. Source-list duplicates do not multiply requests.
3. An exact root-listed member with a valid DLC membership list may be a bounded intermediate (`type=dlc` or `type=game`, because Store labels and type metadata may differ). Its `fullgame`, if present, must equal its root; its own `dlc` IDs are read only **one** further level. No catalog scan, name matching, arbitrary ancestry, recursive walk or new scheduler. A direct root-list entry alone is never accepted as a nested child with an unrelated `fullgame`.
4. To accept a nested child's `fullgame.appid=P`, verify `base.dlc` contains P; P's own `dlc` contains the exact child; and the child's `fullgame` identifies P. Missing intermediate, cross-base parent, contradictory link, self-reference, two-node cycle and unsupported third hop fail closed. Non-DLC intermediate game records are never emitted as DLC purchases.
5. Strict paid gate preserved: parent/identity proof runs before absent/null/empty `price_overview` skip; any nonempty malformed price, non-KZT currency or incomplete integer KZT price fails closed; genuine paid DLC must still satisfy KZT <=4500 and discount >=50%, and existing paid-source rejection. Free and unpriced DLC remain absent from paid candidates.
6. The existing 180 physical starts per rolling 300 seconds shared pacing, 429 retry limits, 900-second lookup deadline, GitHub 60-minute production job, all-core source completeness and one read-only UI remain unchanged. More necessary exact child lookups are counted honestly; timeout/error blocks publication instead of treating partial traversal as complete.
7. Verified chains on admitted paid candidates are recorded deterministically in `verified_parent_chains` alongside existing `verified_base_appids`; stats expose distinct first-hop/nested identities and honest request counts.

## Deterministic negative/positive regression and self-review

- `scripts/test_steam_targeted_paid_lanes.py::check_nested_dlc_exact_parent_proof` uses **synthetic**, clearly marked `2820 -> 201310 -> 235960` KZ-shaped fixtures and a paid nested sibling. Tests direct and nested-only membership, repeated IDs, one GET per exact child, optional game-type intermediate, no-price variants, unrelated/missing intermediates and source lists, child AppID spoofing, root/intermediate type or AppID corruption, cross-base parent, self/two-node cycles, malformed nested list, price/currency/int violations and zero implicit third-hop truncation. No live Steam requests in unit tests.
- Existing direct, no-price, shared multi-base and physical 180/300s test paths are preserved.
- Self-review: no `235960` exception in implementation; no weakened direct parent gate; missing live JSON is explicitly not treated as evidence. A production run on main after Director merge and separate user authorization remains required for live acceptance.
- Files: `scripts/steam_targeted_paid_lanes.py`, `scripts/test_steam_targeted_paid_lanes.py`, this report.

## Verification / gates

- Local isolated execution in this chat: unavailable (repository not network-mountable in local container). Instead, the canonical GitHub PR runner executes the deterministic full regression with Python 3.12 and its existing dependencies.
- `steam-test.yml / regression`: pending final exact-HEAD verification.
- Existing `validate` and `backlog-disposition` checks: pending final exact-HEAD verification.
- Exact final CI head: pending.
- Runtime main collector to mailing/pre-AI: **NOT RUN**, **NOT VERIFIED** (explicitly forbidden in this worker task).

## Director handoff

The Director owns CI/HEAD/risk acceptance and merge. No self-merge. If the actual KZ intermediate membership or type does not meet the two exact link proofs, the correct outcome remains a fail-closed collector; capture bounded exact runtime evidence and request a separate risk/contract decision rather than silently weakening the guard. No Dossier V1/V2 before a full current main collector -> mailing -> pre-AI chain.
