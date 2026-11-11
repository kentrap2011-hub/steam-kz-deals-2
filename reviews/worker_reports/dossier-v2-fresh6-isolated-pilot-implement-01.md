# Dossier Notes V2 — isolated fresh-six executable route (IMPLEMENT, source PR)

**Status:** IMPLEMENTED_IN_DRAFT_PR, **QA PENDING**, **NO LIVE SEMANTIC OR SANDBOX ACTIONS AUTHORIZED BY THIS PR**.

**Dependency:** stacked on [PR #439](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/439) source-only fresh6 preflight. The source of truth remains `main`; #439 and this PR are not merged. Candidate provenance source is historical `main@665f5d0202859a6bac20566671f10158538e4764`. User separately said “Реализовывай” to implement missing mechanism, **not** to dispatch pilot, authorize semantic workers or promote production.

## Exactly what was implemented

- Dedicated `scripts/dossier_notes_v2_fresh6_route.py` validates the six GitHub-prepared AppID/edition/source identities; derives six unique immutable assignment hashes and a distinct pinned manifest, separate from `_original_rows()`. Strict one-add grant → manifest → marker → authorization, exact Git parent/unchanged bytes/first-parent checks and actual GitHub Actions owner-run readback before semantic transport.
- Dedicated `scripts/dossier_notes_v2_fresh6_issuer.py` with two distinct first-attempt manual GitHub-owner Actions dispatches: `.github/workflows/issue-dossier-notes-v2-fresh6.yml` freeze/grant/manifest/marker **once** on a new `sandbox/dossier-notes-v2-fresh6-20261111-first`; then `authorize-dossier-notes-v2-fresh6.yml` creates exactly one authorization direct child of marker, with actual authenticated owner identity/run evidence. No scheduled/push trigger and no automation, semantic generation, batch retries or direct main write.
- Inactive `scripts/dossier_research_notes_v2.py` manifest validation and `scripts/dossier_notes_v2_per_item_receipts.py` Research/Assembly transport have **exact-trial** dispatch to the fresh6 source/issuer checks. Old original18 behavior remains the unchanged default branch. `scripts/dossier_notes_v2_fresh6_pilot.py` only submits one worker-provided preexisting JSON item after checking exact sandbox branch, AppID, edition, GitHub authorizer run and remote SHA. No semantic or polling loop inside this program.
- `scripts/taste_steam_review_dossier_buffered.py` has a separate `trial_id == fresh6` authenticated manual owner dispatch guard using existing strict per-item Assembly validation and immutable issuer; fresh6 writes only to `data/control/dossier_notes_v2/fresh6_pilot_store/` and `fresh6_pilot_accepted/`, never original18 pilot store, canonical Dossier, V1, Deep or site.
- The preexisting `ingest-taste-steam-review-dossier-checkpoint.yml` existing **shared writer concurrency** now supports explicit `notes_v2_fresh6_pilot_writer=true`, mutually exclusive with original18 sandbox and canonical modes. It checks owner GitHub workflow, frozen evidence, only add-only exact fresh6 sandbox paths and non-force verified push. It never enters the normal main canonical writer branch.
- Tests in `scripts/test_dossier_notes_v2_fresh6_route.py` build an offline disposable Git issuer chain from real historical source pins and adversarially check original18 SHA substitution, wrong edition, missing authority, fake actor/run/path/attempt, and read-only source flags. Existing V2 Research/Assembly and receipt regressions remain. CI added to existing PR-only `validate-dossier-research-notes-v2.yml`.

## Actual execution / constraints

**No real fresh6 owner GitHub workflow has been dispatched; no new frozen remote branch exists because of this PR; Research/Assembly 0/6; strict sandbox writer 0/6; production/canonical acceptance 0.** New source code is conditional on exact owner manual action after both source PRs merge; dispatch is a separately approved human action. The helper's local test uses synthetic grants and mocked GitHub REST evidence, never real-player-feedback quality.

**Required next:** get code HEAD CI all green and independent security/source L3 QA; accept dependency #439 then this PR (in that order) only after correct approval gates and check that main-triggered side effects are within scope. **Only then** separate explicit user authorization can initiate first owner manual freeze/authorize, and separate authorized one-shot Research/Assembly prompt jobs. Evaluate actual six-item evidence quality, semantic time and final strict writer receipts before any future canonical design. Do not run any live pilot from this draft PR.

## Architecture preflight

1. Owner: `config/execution_ownership_contract.json` GitHub Action control-plane owns scope, manifest, authorization, progress, validation, persistence.
2. Authority: `config/dossier_research_notes_v2_contract.json` inactive V2 original18 remains immutable; separate preflight contract #439 pins six. This PR adds a separate owner/manual **runtime issuance path**, not a global V2 authorizer or production activation.
3. Interactive chat does not issue manifests, assign work, decide retries, process bulk research or impersonate workflow actor.
4. No recurring schedule, queue, retry manager, backlog or new production stage.

## Scope, test reporting

Six (original source groups g000001 and g000070): Crown Trick (1000010); Orcs Must Die! (102600); Sniper Elite 5 (1029690); Borderlands 2 (49520); Braid, Anniversary Edition (499180); Bulletstorm: Full Clip Edition (501590).

CI: **PENDING exact PR HEAD**. Any static green result is not live semantic or GitHub-owner workflow attestation. Record failure details and fix before acceptance.
