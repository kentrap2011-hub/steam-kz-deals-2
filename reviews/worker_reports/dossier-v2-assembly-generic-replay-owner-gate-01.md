# ЧАТ 1 — Universal GitHub owner-requested Notes V2 Assembly replay

**Task:** `dossier-v2-assembly-generic-replay-owner-gate-01` (supersedes fixed rerun3 implementation).
**Repository ONLY:** `kentrap2011-hub/steam-kz-deals-2`.
**Date:** 2026-11-23.
**Source PR:** [#476](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/476), branch `implement/dossier-v2-assembly-generic-replay-owner-gate-20261123`, based on `main@6d2edbf8cb86d9c73ce8bbd922907775dd8f6101`. PR remains **DRAFT / UNMERGED**. Final head SHA and exact CI results must be refreshed by Director after all source report/registry commits.
**Previous specific trial:** [PR #475](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/475) remains distinct, open/unmerged, **not activated, not automatically reusable**; no cherry-pick or merge of that PR was performed.
**Current stage:** source implementation and PR CI; NO real generic user request or issuance, NO Research or Assembly semantic execution, NO sandbox writer, production, Deep, scheduled task or canonical Lean activation.

## User goal and architecture

The user should be able to request “Повтори второй этап Dossier для этих игр; используй тот же Research” for a previously owner-authorized Notes V2 Research source and then, after the one new GitHub owner run, separately launch a new semantic Assembly chat. **No repeated developer code, new task or per-run source PR** is needed for rerun4, rerun5, etc. The original Research assignment and old Assembly outputs remain immutable; GitHub deterministically copies the Research semantic data with a fresh manifest assignment and separate one-add typed receipts rather than forging old Research Git ancestry.

Four-point ownership preflight was completed from `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `config/execution_ownership_contract.json`, original Notes V2/Lean/Batch policies and `PROJECT_DECISIONS.md`:
1. **GitHub** controls request consent-proof, exact source/research eligibility, AppID/edition and order, authority/uniqueness, grant/marker/manifest, new Research copies/typed receipts, later strict writer/Deep acceptance and any separate recovery.
2. Existing owner-only V2 batch and independent receipt contracts authorize isolated sandbox evidence; new versioned `config/dossier_notes_v2_generic_replay_policy.json` authorizes the narrow new explicit manual owner-request workflow only, not an automatic production stage.
3. This implementation chat is a developer; a later **separately launched** semantic Assembly chat creates only bounded Assembly JSON and candidate+receipt transport. It never owns scope, grant, retry, queue or writer.
4. No schedule, recurring trigger, new persistent queue, global retry/recovery loop, semantic Research stage, fixed quota, Fast/Deep production or duplicate canonical writer.

## Exact implementation

- New versioned request policy: `config/dossier_notes_v2_generic_replay_policy.json`, explicit one user request each time, all production/canonical/scheduler/automatic semantic retry flags **false**. Global `config/dossier_lean_canonical_dual_format_contract.json` three Lean switches remain **false**.
- New reusable owner branch trigger: `.github/workflows/issue-dossier-notes-v2-generic-assembly-replay.yml` listens only to `dossier-assembly-requests/**` pushed request JSON paths; no main merge/recurrence/dispatch trigger. GitHub first-attempt owner actor/event/ref/source-main direct parent/first one-add and absent destination sandbox are mandatory.
- `scripts/dossier_notes_v2_generic_replay.py` validates request schema `DOSSIER-NOTES-V2-GENERIC-ASSEMBLY-REPLAY-REQUEST-V1`, 32-hex nonce, safe existing non-generic source trial, 1–24 unique decimal AppIDs and frozen source ordering; independently verifies genuine **already accepted owner** source authorization via real completed GitHub Action, original Git Research one-add candidate+typed receipt exact SHA and immutable bytes. A source Research record lacking its typed receipt, with wrong product/edition, rejected/edited source, missing owner run, or stale source HEAD cannot issue a new trial. It constructs unique `dossier-notes-v2-assembly-replay-<nonce>`, owner grant/frozen manifest/nonce marker/direct-child authorization, deterministic new assignment IDs and one independent Research candidate/typed receipt per game. A single nonforce final push and readback; no automatic rerun after ambiguous transport. Generated generic trials cannot be recursively used as sources.
- Existing `scripts/dossier_notes_v2_batch_route.py`, `scripts/dossier_research_notes_v2.py::_manifest`, `scripts/dossier_notes_v2_per_item_receipts.py`, `scripts/dossier_notes_v2_batch_pilot.py`, `scripts/taste_steam_review_dossier_buffered.py` and `scripts/dossier_notes_v2_connector_transport.mjs` add **typed generic-owner** path while preserving old non-generic/original18 issuer, strict V2, isolated writer and canonical/non-production enforcement. Immutable new grant replaces the need for another developer `main` cohort contract on each repeat. The tokenless Assembly preflight checks the actual newly issued request commit, request one-add/parent/hash/body, grant/manifest derived Research assignments, real completed first-attempt owner GitHub Action and exact sandbox HEAD. Its separate typed Assembly receipts bind the full Python authority source pins.
- Generic operator instructions: `config/dossier_notes_v2_generic_assembly_replay_runbook.md`. Generic separate semantic chat launcher: `config/dossier_notes_v2_generic_assembly_replay_manual_one_shot_prompt.md`; Lean `DOSSIER-NOTES-V2-LEAN-FINAL-V1` only in the new expressly owner-authorized isolated generic sandbox. Legacy strict cohorts still obey strict format. No mandatory blanket new source discovery or 12-field review ledger. Honest insufficient-evidence terminal remains available without invented claims.

## Actual connected GitHub request interface

The installed GitHub connector exposed `mcp__GitHub__create_branch`, `mcp__GitHub__create_file`, `mcp__GitHub__fetch` and `mcp__GitHub__fetch_file`, but **no tool for workflow_dispatch**. No direct workflow dispatch was demonstrated or claimed.

After **separate source PR acceptance and merge**, for each explicitly approved real request an operator chat can perform:
1. Read fresh `main`, select exactly one **existing legitimate source Research cohort** and a correct manifest-ordered subset of AppIDs; create one never-used 32hex nonce.
2. `mcp__GitHub__create_branch(repository_full_name="kentrap2011-hub/steam-kz-deals-2",branch_name="dossier-assembly-requests/<nonce>",sha=<exact-fresh-main-sha>)`.
3. `mcp__GitHub__create_file(...,branch="dossier-assembly-requests/<nonce>",path="data/control/dossier_notes_v2/replay_requests/<nonce>.json",content=<exact-versioned-request>)`.
4. Read actual resulting GitHub Actions and new sandbox. Do not infer success from the create-file return. If first-attempt owner Action failed, owner identity/permission does not match, event did not trigger, or source is malformed, status is **BLOCKED_AUTHORITY** / **BLOCKED_SOURCE**, not a fabricated authorization. Workflow job retry does not grant another semantic attempt.
5. Only after real owner run success and new Research item+receipt commits are confirmed give generic launcher to an **independent fresh physical Assembly chat**; one candidate+typed receipt per item with exact new Research commit through CAS. No source/old Research SHA substituted.

### First intended six-game request (NOT ISSUED)

Source: `dossier-notes-v2-fresh6-20261114-rerun1`, old immutable sandbox HEAD `c4232fb579fa88c4ed01afd5c45c57792c309984`; rerun2 `dossier-notes-v2-fresh6-assembly-rerun2-20261117` contains previously copied Research and completed Assembly, all immutable. Frozen requested order:

| AppID | exact edition/title |
|---|---|
| 1000010 | Crown Trick |
| 102600 | Orcs Must Die! |
| 1029690 | Sniper Elite 5 |
| 49520 | Borderlands 2 |
| 499180 | Braid, Anniversary Edition |
| 501590 | Bulletstorm: Full Clip Edition |

This first live future invocation is the intended end-to-end acceptance test only after source is approved. There is deliberately **no preissued nonce, grant, marker, sandbox or semantic result** in the source PR.

### Other supported scopes

Any bounded **1–24 AppID subset** of an already genuine non-generic owner-issued Notes V2 batch Research source if every requested item has original immutable Research intro and safe typed receipt, the original source owner GitHub run is independently proven, titles/editions exactly match source manifest, and ordering matches the source manifest. No generic-source chaining, original18 migration, arbitrary Steam AppIDs, self-assigned source batch, silent retry of failed Research, or new Research semantic stage.

## CI and limits

- Existing `.github/workflows/validate-dossier-research-notes-v2.yml` runs `scripts/test_dossier_notes_v2_generic_replay.py` (two distinct accepted requests without code changes; owner event/run/first-attempt guards, subsets, source receipt missing/mutated in disposable Git, immutable one-add receipt+Research) and existing Node `scripts/test_dossier_notes_v2_connector_transport.mjs` (real-shape generic request/manifest/authenticated Action, forged request/provenance/owner/edition/Research guards, published CAS remains unchanged), together with historical strict and Lean/Deep offline regressions.
- The test runner's disposable mock REST owner Action is **not** proof of a live requester. No real GitHub request-branch event, owner token ability, Actions source fetch, sample semantic quality, writer acceptance or downstream normal Deep/canonical cutover is claimed in this worker. Independent QA is required by the new task; old PR #475 waiver is unrelated.
- Documentation `PROJECT_ROUTES.md` and `PROJECT_DECISIONS.md#DOSSIER-GENERIC-REPLAY-005` record the reusable route and why avoiding per-run source PRs changes the owner control boundary.
- The critical operator limitation is connecting the explicit real user request to the two create-only GitHub calls; if unavailable, use truthful `BLOCKED_AUTHORITY` and bounded owner-operated request, not silent recurring automation.

**Source status at report-writing:** `SOURCE_PR_476_DRAFT_CI_IN_PROGRESS; NO_LIVE_OWNER_REQUEST; NO_SEMANTIC_ASSEMBLY; NO_CANONICAL_OR_PRODUCTION`. Reverify exact FINAL PR HEAD and all mandatory tests before declaring implementation ready; do not self-merge.
