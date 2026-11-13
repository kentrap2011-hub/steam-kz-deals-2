# Dossier V2 connector-native transport without GH_TOKEN — worker report

Task: `dossier-v2-connector-transport-no-gh-token-implement-01`
Role: **developer IMPLEMENT**, not Research/Assembly.
Source: current `main` baseline `60641c5b5d4cf40dd0447316e7af0c186f542721`.
Branch: `implement/dossier-v2-connector-no-gh-token-01`.
PR: see the branch pull request; exact HEAD/CI to be recorded after final verification.

## Architecture preflight

1. Control plane remains GitHub; ordinary ChatGPT dev chat does not operate semantic backlog.
2. Existing `config/execution_ownership_contract.json`, `config/dossier_research_notes_v2_contract.json`, scoped owner-issued batch contract and unchanged strict V2 writer remain authority. This change is only a transport alternative, not new permission.
3. Connected GitHub tools perform authenticated Git data reads, owner-run verification and non-force CAS writes; ChatGPT remains only explicitly user-launched semantic data-plane in separate Research/Assembly conversations. No GitHub-owned schedule/queue/retry or acceptance logic is moved.
4. No additional scheduled task, recurring stage, daily quota, retry owner or new owner issue/authorize workflow is created.

## Changes

- `scripts/dossier_notes_v2_connector_transport.mjs`: a reusable direct GitHub-connector-only implementation with no injected token; immutable exact cohort identities, two real owner GitHub Actions run metadata, verified branch/git parent tree/one-add change sets, repo permission check, strict trial isolation, stage binding, exact one-blob tree/commit, `update_ref(expected_sha, force=false)`, remote content/blob readback, and separate typed Research/Assembly receipts. The immutable source route remains GitHub-owned.
- `config/dossier_notes_v2_connector_transport_manual_runbook.md`: a concrete interactive ChatGPT Code Mode adapter and manual invocation spec. This is **not** a standalone Python connector or a new scheduler.
- Both reusable manual one-shot prompts point at the connector route; legacy token-backed Python CLI remains functional and deliberately refuses missing token.
- Existing V2 PR CI adds synthetic Node connector adversarial coverage; Python V2 source and existing strict writer remain unchanged except explanatory docstrings.
- Tests are synthetic only, not evidence of live semantic Research or final Dossier quality. Strict accepted-only sandbox writer remains the final authority and may reject connector submissions that fail Python validation.

## Live evidence and bounds

Observed through connected GitHub in this developer chat:
- `freeze_run_id=43466039520`: first-attempt owner `workflow_dispatch` SUCCESS for `.github/workflows/issue-dossier-notes-v2-batch.yml`.
- `authorization_run_id=43467293841`: first-attempt owner `workflow_dispatch` SUCCESS for `.github/workflows/authorize-dossier-notes-v2-batch.yml`, correct fresh6 marker and run name.
- Owner login `kentrap2011-hub`, numeric ID `315790060`; actual sandbox ref at registration `87a8f4149a736ba797824c59698552766f71799b`.
- Correct original first six AppIDs: `1000010,102600,1029690,49520,499180,501590`.
- No live Research/Assembly/issuer/strict writer runs from this implementation chat. No canonical cache/production/V1/Deep mutation.

## STOP and remaining validation

- No actual semantic worker has yet executed this connector route, and **no real sandbox write was attempted**; GitHub API capability is observed, but end-to-end live runtime compatibility still requires a separately authorized one-shot invocation and owner strict writer validation.
- Standalone Python cannot call the ChatGPT GitHub connection; module and runbook execute within the ChatGPT GitHub-connected JavaScript orchestration tool. The connector tool cannot execute Python strict schema/semantic validation; this remains enforced by the existing GitHub writer. A candidate/typed receipt is only Git-transport evidence, never accepted final Dossier.
- Any insufficient permissions, owner-run provenance mismatch, missing tool, wrong trial/appid/edition, stale/parallel branch CAS rejection, duplicate file path, ambiguous create/commit/ref/read-back must STOP with no blind retry.
- Additional authorization, Freeze, strict writer dispatch, semantic Research/Assembly, production activation or PR merge are not performed.
