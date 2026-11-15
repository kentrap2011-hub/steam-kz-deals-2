# ЧАТ 2 — Dossier V2 no-UI owner launch / Research fresh6 rerun

- Task: `WORKER_TASK_DOSSIER_V2_NO_UI_OWNER_LAUNCH_RERUN_FRESH6_01.md`
- Status: **SOURCE PR IMPLEMENTED, LIVE RERUN NOT EXECUTED**.
- Source: [PR #452](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/452), `implement/dossier-v2-owner-push-rerun-fresh6-01`, base `main@268abd13816fac0866a677103ef75be82cc26a56`.
- Scope: one authorized `dossier-notes-v2-fresh6-20261114-rerun1` source cohort only; excludes original18 and `fresh6-20261111-first`.

## Implementation

1. Prepared new exact six-game cohort under `config/dossier_notes_v2_batches/` with **historically pinned 2026-11-11 GitHub source**, not a 2026-11-14 re-snapshot. AppIDs in order: 1000010 Crown Trick, 102600 Orcs Must Die!, 1029690 Sniper Elite 5, 49520 Borderlands 2, 499180 Braid, Anniversary Edition, 501590 Bulletstorm: Full Clip Edition. Existing deterministic `batch.rows/manifest_blueprint` calculates new assignment IDs.
2. New `issue-dossier-notes-v2-on-owner-push.yml` is restricted to first owner-ID authenticated `main` push **adding** only this previously absent cohort source file. `guard_owner_push` validates real GitHub event payload (`sender`, `before/after`, `head_commit`, exact repo/branch), first-parent introduction, remote `main` SHA, immutable historical provenance, policy and absent sandbox. `owner_push_launch` creates separate Git commits for grant, deterministic manifest, new nonce marker and direct-child authorization with non-force GitHub readback and no copy-pasted SHA. Explicit authorization includes actual main SHA, owner run ID and origin; later `authenticated_owner_run` checks completed successful authentic first-attempt GitHub Actions via REST API. Old manual dispatch authority and exact old auth structure remain unchanged.
3. Owner-connected GitHub `create_file` at each frozen Research candidate path triggers only `ingest-dossier-notes-v2-research-on-owner-push.yml` on exact sandbox branch. `_owner_push_candidate_gate` validates genuine first-attempt owner GitHub push event and a one-add commit for a frozen assignment. Trusted-main `run_authorized` authenticates previously completed source issuer, independently creates strict typed Research receipt commits by existing `prepare_receipt/inspect_receipt_commit` and non-force CAS, only if source still current. Dispositions of invalid/missing items remain truthful and independent; existing manual ingest remains fallback and shares the same GitHub concurrency group. No semantic retry, no raw user-review storage, no Assembly or strict final acceptance.
4. Canonical inactive policies and Research launcher amended. New adversarial synthetic regressions in `scripts/test_dossier_notes_v2_owner_push.py` and CI step in `validate-dossier-research-notes-v2.yml`; unchanged V1, original18, Deep, strict final and production flags.

## Real disposable connector capability proof (NOT a semantic trial)

- Disposable branch only: `test/dossier-v2-connector-owner-push-20261115`. Separate branch workflow `disposable-dossier-v2-owner-push-smoke-20261115.yml` and `data/control/dossier_notes_v2/_smoke_20261115/*` are **not in PR #452**, not production and not Research.
- A single authenticated connected `mcp__GitHub__create_file` wrote harmless `owner_input.txt`; GitHub created actual owner-authenticated `push` [run 43682622350](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43682622350) with `actor.id=315790060`, `event=push`, `run_attempt=1`, `status=completed`, `conclusion=success` and exact source commit `d22398e06d8ef7e7ef3a020ab89ec270ead4c5b7`.
- That GitHub Actions run used only `permissions: contents: write` and successfully created a **new** bot commit `eb3ccc1d352e25955652f1e53fc43738735d82f9` on the disposable branch; `action_output.txt` independently read back with the exact owner actor ID and originating push SHA. Confirms actual connected push and Actions write capability, **not** that a real rerun has been authorized or receipts accepted.

## Test and acceptance contract

- New synthetic tests: old/new cohort isolation, exact AppIDs/titles/edition, frozen source date, original18 exclusion, no stale/ref/actor/run substitutions, real event and immutable one-use owner run requirements, typed strict receipt and subsequent Assembly-ready technical state, idempotent multiple candidate receipts and sibling independence. Existing strict branch/first-parent/one-add/schema/privacy/source checks remain.
- PR CI expected: Dossier V2 offline, Dossier eventual-chain, site task registry, backlog dispositions; verify each on **final PR HEAD**. Synthetic green is not owner run issuance, real browser research quality or canonical final writer acceptance.
- Source PR must be **accepted/merged by the project Director**, not by this developer chat. After merge, inspect actual first-attempt owner main-push issuer run, new sandbox marker/authorization, authenticated Actions readback; if missing or failed, report `BLOCKED_INTERFACE` and do not start semantic Research. Only a distinct explicitly user-launched Research worker then writes six create-only candidates, after which actual GitHub sandbox event/receipt readbacks are checked. No user actions in GitHub UI.

## Explicit non-actions and residual risks

- No new trial sandbox created in this PR; no new semantic notes, receipt, Assembly or strict final writer run. Previous six and original18 untouched. No new recurring automation and no change to V1/Deep/canonical production.
- GitHub can reject source PR merge or scheduled event due branch protection, permissions, source drift, commit shape or GitHub platform rules: fail closed. A successful disposable owner push is capability evidence, not issuance evidence for the actual trial.
- A candidate GitHub commit alone is not a typed receipt or a quality audit. Ingest may record a technical incomplete/rejected outcome; Assembly requires the actual accepted typed Research receipt.

## Time / simplification

The work required reading the actual issuer, owner proof, receipt validator, Actions and test fixtures to avoid issuing false authority. The resulting interactive Research route uses exactly **one GitHub `create_file` per item** and no hand-pasted SHA, issuer tokens, manual Actions UI steps or separate receipt publication by ChatGPT. The one-time source authorization and typed receipts remain strictly GitHub-owned.
