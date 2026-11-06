# Steam KZ first-hop listed base alias — targeted fix, 2026-11-06

## Authorization and scope

User explicitly requested **"Исправь"** after reviewing the identity RECON and consenting in conversation to the proposed narrowly scoped GitHub-owned IMPLEMENT. Base: `main` SHA `5e4fd5c553dc8ec83515a3eebb909e352611b1b8`. This is a new implementation branch, **not** the RECON report-only PR #407. Related investigation: `reviews/worker_reports/steam-appdetails-1697640-identity-recon-01.md` on draft #407. The current real KZ Steam API response was supplied by the user: outer `"1697640"`, `success: true`, `data.type: "game"`, `data.name: "Dying Light"`, **integer `data.steam_appid: 239140`**, `data.dlc` includes `1697640`. The original 2026-11-05 HTTP 200 failure confirms the identity comparison failed but did not log the historical exact value.

## Architecture preflight

- **Owner:** GitHub and existing `scripts/steam_targeted_paid_lanes.py` KZ DLC discovery, per `config/execution_ownership_contract.json` and `config/daily_execution_contract.json`.
- **Canonical product rule:** `config/mailing_policy.json#paid_discovery.dlc_discovery` — only parent appdetails of quality-admitted base games, complete verified relationships, no global DLC traversal, no raw top-N shortcut.
- **No control-plane transfer:** no ChatGPT runtime, scheduler, queue, checkpoint, daily quota, retries, new network endpoints or independent production activity added.
- **Fail-closed:** any mismatched game not proven as a uniquely-listed validated root alias, any malformed fields, ambiguous parents or nested alias conflicts continue to stop publication. Current last-known-good preservation in `steam_partial_publish_runner.py` unchanged.

## Code changes

- `get_appdetails` remains strict by default. Only an explicit `verified_base_aliases` argument from the validated **first-hop root relationship** permits returning an alias response; unknown/foreign mismatch still raises the original exception.
- Helper `_is_verified_listed_base_alias` requires exactly one verified root listing this candidate, valid internal `steam_appid` equal to that root but **different** from requested child, `data.type="game"`, no foreign `fullgame`, and the returned canonical game's own valid `dlc` list must also contain the original requested ID. This matches the actual current 1697640 → 239140 case without adding a static whitelist or copying prices.
- In `discover_dlc_for_bases`, such a proven alias is recorded as **excluded from DLC**, never expanded as an intermediate and never made into an independent DLC offer. A nested relation targeting an excluded alias fails closed. Valid direct siblings continue as before; `dlc_price_lookups` still counts alias GETs, while `related_dlc_unique_ids`/rejections exclude proven non-DLC aliases and `verified_base_game_alias_exclusions` reports their count.
- No change to real DLC pricing, KZT price caps, quality gates, 180/300s request pacing, 4 attempts, shared 429 cooldown, parent discovery or default identity verification.

## Regression cases and acceptance

Existing `scripts/test_steam_targeted_paid_lanes.py` extended with **real-ID fixture** and explicit network-level `get_appdetails` request simulation:
- 1697640 → 239140 valid root alias, duplicate edges and alias-side price (which must **not** be used), plus a separately-priced genuine DLC requested after the alias and retained.
- Production caller passes verified roots to first-hop fetch, but not parent fetch; exact `cc=kz&l=english` params unchanged.
- No allowance at all on default GET; wrong or ambiguous root whitelists rejected; foreign internal game, child typed DLC, no reverse listing edge, malformed DLC list/member, foreign fullgame, multiple roots listing same alias, malformed internal IDs, and nested alias reintroduction all rejected.
- All previous 17 regression checks retained; suite expected **18/18**.

**Verification state:** pending GitHub PR-only `steam-test.yml` CI at exact final HEAD. This test workflow explicitly skips its production `collect` job for pull requests. Full real-nightly acceptance remains a later, separate main workflow gate following source review/merge. **No production/manual workflow dispatch, deployment, catalog rewrite or PR merge in this worker.**

**Task status:** IMPLEMENTED, AWAITING PR-ONLY CI AND INDEPENDENT REVIEW.
