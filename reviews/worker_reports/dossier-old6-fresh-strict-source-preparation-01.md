# Fresh old Dossier strict-six control — source preparation (2026-11-27)

**Scope:** user-requested repeat of the **original complete one-stage** `TASTE-STEAM-REVIEW-DOSSIER-V2` for exactly six already Lean-tested games. Repository `kentrap2011-hub/steam-kz-deals-2` only. Source base `main@993d7ff317892e05bab96117adbccea414824f61`. Related: [issue #501](https://github.com/kentrap2011-hub/steam-kz-deals-2/issues/501), [quality comparison PR #500](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/500), earlier three-only reconnaissance [PR #502](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/502) superseded in scope by this **six-item** task.

**Source status:** `SOURCE_PREPARED_PENDING_CI_AND_INDEPENDENT_AUTHORITY_QA` when written. **No semantic Research performed, no new strict Dossier generated, no real sandbox acceptance, no production or Deep touched.**

## Scope and evidence source

Immutable product/work evidence is taken from original source `main@665f5d0202859a6bac20566671f10158538e4764`, original snapshot `25c227d782188699f56b5702b3f0cfa63b101d890f09620b7b59893fab93c1af`, two existing original groups 1 and 70 (each 3). The six exact AppIDs / editions:

| Legacy comparison group | AppID | Exact game |
|---|---|---|
| 1 | 1000010 | Crown Trick |
| 1 | 102600 | Orcs Must Die! |
| 1 | 1029690 | Sniper Elite 5 |
| 70 | 49520 | Borderlands 2 |
| 70 | 499180 | Braid, Anniversary Edition |
| 70 | 501590 | Bulletstorm: Full Clip Edition |

This is **not** permission to reuse three existing old V2 cache files, nor to copy the fresh6/rerun1 Notes V2 Research. All six must be researched again with the **original Dossier worker's complete and current strict source/evidence coverage standards**. Distinguish original release/work-year from storefront/remaster edition-year, especially Braid and Bulletstorm. The outputs are `PROSPECTIVE_OLD_FORMAT_CONTROL`, not historical September/October files. Exact Lean acceptance comparison commit remains `372efa1e7e1f95905a3d16dd95f531f12bed2d9c`.

## Architecture preflight

1. **Owner:** existing `config/execution_ownership_contract.json` and `config/taste_steam_review_dossier_contract.json` assign scheduling, business rules, scope/order, validator and canonical state to GitHub. Semantic ChatGPT only receives exact scoped tasks.
2. **Allowed bounded extension:** an explicit owner request for an **isolated 6-item one-time comparison**, frozen into GitHub config before the separate semantic start. It uses unchanged original `config/taste_steam_review_dossier_worker_prompt.md`, `config/taste_steam_review_dossier_schema.json`, `config/taste_steam_review_dossier_web_evidence_contract.json`, `scripts/taste_steam_review_dossier_strict.py`, and does not change their semantics or the original production writer.
3. **No unauthorized control-plane transfer:** GitHub stores fixed six IDs and review authority in reviewed `main` config, immutable sandbox Git parent/one-add files, and runs its PR-only strict validation; the semantic worker cannot choose scope, accept results, change production, issue fake receipts or invent a new execution grant. A GitHub read-only CI PASS is not a factual-quality or canonical acceptance.
4. **No new recurring stage/queue/retry:** a single fixed trial `dossier-old6-20261127-exact-six-01`, branch `sandbox/dossier-old6-20261127-exact-six-01` only after source acceptance + fresh new-chat launch. The active 493-item V1 queue (groups 125/126/127 for last three) is not traversed, reordered, rewritten, retried or skipped by this trial. No Scheduled Task or workflow_dispatch producer is added.

## Implemented source files

- `config/dossier_old6_fresh_strict_control_v1.json`: frozen exact six, exact titles/edition, original source, two groups, strict V2 target, TTL20, min generation date, old cache + Notes V2/Lean reuse forbidden, sandbox-only.
- `config/execution_ownership_contract.json#explicit_manual_semantic_worker_chats.dossier_old6_fresh_strict_control_one_shot`: isolated fresh user-launched role. The ordinary interactive developer chat and normal scheduled Dossier are unchanged. Independent authority QA is necessary before activating this new exception.
- `config/dossier_old6_fresh_strict_control_worker_prompt.md`: complete reusable execution steps, new GitHub-created branch, marker bound to exact actual Git-parent, true fresh web research by game, one-add files, strict candidate PR. No manual token/JSON entry by the user.
- `scripts/validate_dossier_old6_control.py`: read-only `--check-config` and `--check-outputs`; real Git one-add marker+six files, frozen source-commit ancestry and manifest, exact ID/edition/order, actual generated-date floor, current **original strict validator**, TTL20, forbidden extra files. Does not publish any result.
- `scripts/test_validate_dossier_old6_control.py`: negative source-authority/edition/cache/Lean/production/scheduler tests, no-marker refusal and disposable Git one-add vs multi-add regression.
- `.github/workflows/validate-dossier-old6-control.yml`: PR-only read-only tests and strict `--check-outputs` if and only if a trial directory exists. A source-only PR deliberately reports no semantic work; a future candidate PR with even one incomplete result fails rather than receiving false 6/6 status.
- This worker report.

## Execution and acceptance gates

1. Exact source branch PR checks, including new strict-six CI and existing execution-ownership CI. Reviewer independently checks the new one-time semantic authorization (scope takeover, marker-parent authenticity, PR approval, GitHub privileges and candidate trust) before any source merge. **Source worker does not self-merge.**
2. After source accepted and merged, user explicitly opens a new *semantic* chat using the canonical worker prompt. The source merge alone never starts Research. This trial does not use a Scheduled Task or an owner Action secretly activated by workflow paths.
3. Semantic chat creates exactly one sandbox branch + start marker through connected GitHub owner identity, obtains fresh player feedback and publishes six strict one-add files in order. **No old cache or Lean reuse.** If external evidence is incomplete, report incomplete, not invented.
4. Completed six go through a **separate draft candidate PR**, strict GitHub test on its exact HEAD, then substantive independent quality review of actual public sources and old-vs-new buyer-useful coverage. No direct canonical acceptance or Deep.
5. The comparison worker may compare historical old (3 matched), **fresh prospective old strict (6 new)** and Lean (6) with matched edition/identity; data must be labeled by kind. End-to-end speed is `UNMEASURED` unless actual compatible stage timing is recorded; do not treat Git publication delay as model runtime or extrapolate artificial `N×`.

### Safety and limitations

The narrow source extension intentionally creates a **one-shot sandbox semantic data plane** rather than pretending the existing V1 normal queue accepts arbitrary group selection. New authority is security-sensitive and must be independently reviewed. A candidate may pass shape/one-add CI while source content remains weak; only a separate semantic quality review can support `QUALITY_GOOD`. The user must not be told that all six were processed merely because the source PR is green.

**Sensible terminal statuses:** `SOURCE_READY_AWAITING_DIRECTOR_ACCEPTANCE` after exact-HEAD CI, or a specific `BLOCKED_CI_OR_AUTHORITY`; `SANDBOX_STRICT_VALIDATED_PENDING_QUALITY` only after actual six-file semantic follow-up; `COMPARISON_COMPLETE` only after real source-grounded study.
