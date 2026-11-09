# Steam DLC fullgame parent authority — scoped IMPLEMENT

**Date:** 2026-11-07
**Repository/base:** kentrap2011-hub/steam-kz-deals-2 / main
**Branch:** `fix/steam-dlc-parent-fullgame-trust-01`
**Status:** IMPLEMENTED_AWAITING_PR_CI_AND_DIRECTOR_REVIEW
**User authorization:** «Убираем проверку. Верим что Стим корректно указывает родителя. ... Если родителем длс указана не сама игра а длс этой игры. Наша система понимает что оба длс относится к одной игре?»

## Confirmed source evidence

- [One-off live GitHub Actions run 42398758928](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42398758928), PR #415: **3 physical** HTTP 200 `appdetails?cc=kz&l=english` GETs for exactly 2820, 201310, 235960. `App_2820.dlc` contains 201310 and 235960, `App_201310.fullgame.appid=2820`, `App_201310.dlc` does NOT contain 235960, `App_235960.fullgame.appid=201310`. The old validator aborted on this missing reverse edge. Current live evidence, not exact historical response replay.
- Main `scripts/steam_targeted_paid_lanes.py::discover_dlc_for_bases` previously required both root-to-middle-to-child list membership and child's fullgame. This conflated discovery metadata with parent attribution.

## Authorized change

1. `fullgame.appid` on a DLC is now the primary source of its **immediate** parent; the parent's own `fullgame.appid` links a two-level DLC to its vetted root base. The root and middle `dlc` lists are kept for finite **discovery**, not reciprocal-identity veto.
2. Other root lists mentioning an unrelated DLC or intermediate cannot give it a fake root. Unresolvable parent lineage is excluded from the paid candidate set, not attached by guesswork.
3. Preserve strict requested-versus-returned `steam_appid`, canonical positive IDs, root game type, existing root-game alias safety, max two discovery hops, cycle guard, KZ physical-start/HTTP retry budgets, KZT price + >=50% discount and <=4500 KZT caps; no live source writes, no schedule/queue changes.
4. If `fullgame.appid` is absent, retain the existing direct-root listing fallback; no unproved nested lineage is accepted.

## Safety checks and limitations

Deterministic PR regression includes the concrete live shape: root 2820 lists child, middle 201310 omits it, child points at 201310; asserts `verified_base_appids=['2820']` and `verified_parent_chains=[['2820','201310','235960']]` for a **synthetic priced fixture**, with no fabrication of real pricing. Missing/null/empty real 235960 price remains excluded. Other tests cover second eligible root's conflicting listing, malformed AppIDs, foreign parent, cycles, third hop, paid price types/currency/threshold, alias, shared quota and collector ownership.

**CI acceptance required:** existing GitHub `steam-test.yml` PR `regression` must finish green on exact PR HEAD; production `collect` stays SKIPPED. Full production recovery is **not** proven by these deterministic tests, and still requires a separately authorized normal main cycle. **Do not merge source PR without Director review and appropriate independent QA.** The old diagnostic PR #415 must remain unmerged.

## Dependency/architecture preflight

Component and control plane are unchanged: GitHub-owned deterministic paid DLC discovery, scoped by `config/mailing_policy.json#paid_discovery`, `config/daily_execution_contract.json` and `config/execution_ownership_contract.json`. No ChatGPT-owned runtime or new producer introduced. The user changed only parentage semantics, not available root scope, price policy or dispatch semantics.
