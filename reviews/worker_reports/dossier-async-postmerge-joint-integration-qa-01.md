# Worker report — Dossier fully async post-merge joint integration QA 01

- Physical worker: **НОВЫЙ ЧАТ — ЧАТ 1**.
- Task: `WORKER_TASK_DOSSIER_ASYNC_POSTMERGE_JOINT_INTEGRATION_QA_01.md`.
- Repository/base: `kentrap2011-hub/steam-kz-deals-2` / `main`.
- Starting verified main SHA: `ae94dd2fe3216ce4847ab84c60c2cd718b7a7f03`.
- Prerequisites: PR #187 merged as `aec7701dfb484bbe3d0165e3dc75875c4d2e2c23`; PR #188 merged as `0549dc00b4a96833f747707f92c000bf44f443fc`. Both were confirmed via current GitHub metadata.
- Worker branch: `qa/dossier-async-postmerge-joint-01`; PR: **#190** — https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/190 — **open, clean, not merged**.
- Mode: **offline, synthetic, disposable Git repositories only**. No semantic execution, production write, workflow dispatch, scheduled-task change or source-web query.

## START and scope

Read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, task definition, the two prerequisite worker reports, Dossier-specific route in `PROJECT_ROUTES.md`, actual current ownership contract and inactive two-stage interfaces/staging/async/final bridge contracts. Only this worker's new regression, PR-only workflow and report were modified. Shared `CURRENT_TASK.md` was not rewritten to avoid collision with concurrent Chat 2 work.

The existing `config/execution_ownership_contract.json` makes GitHub the sole control-plane owner; this PR installs no consumer, receipt, queue, retry or scheduler. The canonical one-stage Dossier writer stays authoritative. The offline bridge is permitted only with its disposable-Git marker, strict `offline_fixture=True`, disabled live gate and real existing strict `validate_buffer_artifact` + `drain_buffered_groups`.

## Joint proof added

New `scripts/test_dossier_two_stage_postmerge_joint.py` reuses merged `FinalAcceptanceOfflineTests.fixture` and thus executes the **actual merged** frozen Research/Assembly marker APIs, create-only Git transport, GitHub Research receipt validation, final chain inspection, original ordered immutable three-game group validator and existing V2 buffered canonical drain. No mocked acceptance authority or worker-created receipt.

1. **Former original-work year XFAIL**: source `rsource-002` explicitly asserts 2021 while Research identity and independent source describe original work as 2020. P1 strict validation rejects; the same immutable submitted Research A is rejected by P2 as `rejected_invalid / invalid_binding` even if Assembly A was already submitted using the exact Research Git bytes before GitHub receipt. A never enters canonical cache/Deep-ready and its original group remains pending.
2. **B/C and independent next group**: Research and strict Assembly B/C continue independently of failed A. The first original group cannot partially accept; the second unmodified, fully ready, original ordered three-game group is accepted by the existing writer and persists precisely three Dossiers. No per-sibling barrier or reordering is introduced.
3. **Legitimate Steam port**: original work year remains 2020 and a later Steam/port-related source may have `publication_date=2024-08-09`. P1/P2 accept these noncontradictory fields, Assembly submits before Research acceptance, and only complete exact original 3/3 strict V2 group becomes canonically accepted.
4. **Moving main / replay**: unrelated later HEAD commit does not rebind the frozen marker and immutable transports; exact strict 3/3 writer succeeds. Writer cannot replay accepted group against stale manifest.
5. **Adversarial final boundary**: a forged GitHub Research acceptance receipt after initial inspection cannot authorize acceptance; writer rechecks the complete original Git chain and fails closed. The existing final and eventual chain suites separately cover duplicate/foreign locators, stale/tampered Research and Assembly commit/path/blob/raw/hash/plan/prompt/marker/output, rewritten submissions, forged handoff, collision without overwrite and original group boundary.
6. **Activation and owner gate**: test checks interfaces/staging/async/final bridge active/authority/write booleans remain false, no new live workflow, unchanged existing shared `taste-steam-review-dossier-canonical-writer` boundary and preservation of one-stage authority.

New `.github/workflows/validate-dossier-async-postmerge-joint.yml` triggers **only on PR** for bounded paths, requests `contents: read`, and runs joint + merged Research/P1/P2/Assembly/async/final/one-stage tests and `scripts/validate_execution_ownership.py`. No dispatch, schedule, push or production data artifacts. The former XFAIL is asserted to have no `@unittest.expectedFailure` decoration and the CI log rejects an expected-failure summary.

## Important cross-PR proof metadata limitation

Current merged `scripts/dossier_two_stage_final_acceptance.py::offline_gate` requires `cross_pr_research_original_year_fix_verified is False` **in addition to** all three real activation gates being false. Thus flipping the requested proof-only flag true would disable even the inactive disposable-Git offline adapter and break the test suite. The flag is currently `false`. This is a **fail-closed proof-metadata coupling**, not evidence that production is active; no live bypass was found.

This worker does **not** edit the other chat's merged bridge implementation or claim production authority. Leave the proof flag **false** until the joint checks pass and a separate narrowly authorized fix makes the bridge gate depend only on real activation fields while allowing either boolean proof metadata value. Re-run joint CI after that bounded correction, then change proof flag only with verified evidence. In no case may the proof flag activate the canonical writer. No wider rewrite, new workflow consumer or scheduler is authorized.

## CI and final outcome

- CI workflow: `Validate Dossier async postmerge joint integration (offline)`.
- **SUCCESS** — dedicated joint Actions run **38121480191** on implementation/report head `c9459a9441935532c7970f4a261113138fd79e8a`. Every step succeeded: compilation; five newly added genuine joint disposable-Git tests; former-XFAIL now ordinary negative eventual chain suite; existing strict final bridge; strict P1 year/schema suite; P2 frozen marker/staging and full async buffer; one-stage strict buffered acceptance; GitHub execution ownership validation.\n- **SUCCESS** — independent PR backlog dispositions run **38121480201** on the same head.\n- GitHub raw pull request metadata: `mergeable=true`, `mergeable_state=clean`. Worker does **not** merge the PR.
- Joint P1/P2/Assembly/final three-game strict acceptance proof **passed offline**. No test-failure integrity defect was observed in this bounded fixture. The already documented proof-flag/offline-gate coupling is a separate narrow blocker: do not silently flip the flag or authorize production.
- All production acceptance, two-stage activation and semantic worker flags remain **false**.
