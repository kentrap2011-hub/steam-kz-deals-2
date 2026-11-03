# Steam targeted DLC identity blocker — worker report

Task: `steam-targeted-dlc-identity-blocker-restore-auto-dossier-01`  
Worker: physical ЧАТ 2  
Date: 2026-11-03  
Status: **IMPLEMENTED_IN_PR; final exact-head CI and Director L3 acceptance required**  
Source PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/388  
Source branch: `fix/steam-targeted-dlc-identity-blocker-01`  
Source of truth: `main` (starting base `cc04dab1094d85e4b8c55a0b936dc5cbf35f689e`).

## START, ownership and scope

Read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, task file, relevant `CURRENT_TASK.md`, `PROJECT_ROUTES.md`, `config/execution_ownership_contract.json`, `config/daily_execution_contract.json`, `config/mailing_policy.json#paid_discovery`, existing `steam-test.yml` and pre-AI Dossier chain. Preflight: collector source, daily scope and queue are GitHub control-plane responsibilities; existing parent-targeted DLC and KZT gating are authorized by paid discovery contract; no ownership transfer, new scheduler, queue, quota, retry or manual preparation is needed.

## Actual cause and evidence

- Main GitHub run [41362591621](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41362591621) on 2026-11-01 aborted stage `targeted_dlc_relations` after 1028.5s with `DLC relationship contains duplicates/invalid identities: 239140`. Publisher kept the previous stable payload.
- Old predicate `len(sorted({str(value) for value in raw if str(value).isdigit()})) != len(raw)` conflated two independent conditions: benign repeated AppID membership and malformed/non-canonical raw identities.
- Source run logs show **no raw parent `dlc` payload**, so we cannot establish whether AppID 239140 specifically contained repeats or malformed identities. No claimed replay or fabricated live proof. The changed behavior is conservative: only validated same-ID membership is deduplicated, all malformed inputs still reject the parent.
- The separately observed pre-AI failure [41498105517](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41498105517) rejected stale discovery, skipping automatic Dossier preparation as designed. At source check, `taste_steam_review_dossier_worker_index.json` still had `prepared_for_date=2026-10-27`; after 2026-11-02 worker-prompt change, old binding is not sufficient for a manual one-shot.

## Source correction

`scripts/steam_targeted_paid_lanes.py`:
- Canonical positive AppID parser rejects booleans, fractional numbers, zero, negatives, padded/non-ASCII/ambiguous textual IDs and invalid types instead of silently filtering entries.
- Parent `dlc` list treated as deterministic set membership; duplicate valid IDs deduplicated before DLC price lookups; explicitly invalid `dlc` representation remains a fatal parent error.
- Where appdetails returns a `steam_appid` it must match the requested parent/DLC AppID. Contradictory or ill-typed `fullgame` relations fail closed.
- Missing parent, wrong base type, inaccessible appdetails, cross-parent relationship validation, non-DLC exclusion, complete suitable-base scope, existing three-worker bounded request path and KZT price/discount paid gates preserved.

`scripts/test_steam_targeted_paid_lanes.py`: new deterministic fixtures for repeated valid IDs in one parent, cross-parent shared DLC membership, single unique price lookup per AppID, bad/negative/zero/fractional/boolean/padded/non-ASCII identity, malformed relation container, bad parent/embedded ID/fullgame, HTTP-access failure (parent and DLC), invalid parent type and non-DLC exclusion. Existing package, price, 100-visible limit, and conservative review-gate regressions remain in suite.

`PROJECT_ROUTES.md`: added date-stamped direct route to this failure, test and non-manual auto-regeneration path.
`CURRENT_TASK.md`: preserves other workers' ongoing handoffs while recording this scoped task.
`reviews/worker_reports/steam-targeted-dlc-identity-blocker-restore-auto-dossier-01.md`: this handoff.

## Verification and limitations

The existing PR-specific `.github/workflows/steam-test.yml` invokes `python -m py_compile` on touched modules and the complete deterministic discovery/collector regression list, including `scripts/test_steam_targeted_paid_lanes.py`, `scripts/test_steam_discovery_scope_reduction.py`, `scripts/test_steam_partial_publish.py`, fresh-discovery freshness guards, commercial and execution-ownership validations. **Final exact-head GitHub CI status must be read from PR #388; this report must not be interpreted as a PASS until GitHub confirms it.**

Local repository checkout is not possible in this execution environment (`git ls-remote` failed DNS resolution for github.com). No live Steam collection or semantic processing attempted. PR `collect` job is intentionally disabled on `pull_request`. Targeted source/test paths trigger PR regression, but are **not** a main-push production trigger; the existing `schedule` at 20:10 UTC is the authoritative next collector cycle after merge.

No generated index, canonical cache, Dossier V1/V2, PASS2 or freshness cutoff modified; no workflow dispatch, production rerun, manual semantic one-shot, separate scheduler or self-merge performed.

## Acceptance gate / next actor

Production-facing **L3 risk**. **Director**: independently review the exact PR #388 head, CI and fail-closed identity invariants; approve and merge only after acceptable QA. Then observe an **ordinary scheduled successful** GitHub collector → mailing → pre-AI chain and verify a fresh Dossier worker index plus the **current exact worker-prompt binding**. Until this happens Dossier semantic invocation remains blocked; source PR approval alone is not proof that queue auto-regeneration succeeded.

No additional worker or manual queue preparation is proposed.
