# Director Orchestration Phase 2A — Independent System/Security Audit 01

Status: `PASS`

Closure decision: `accepted`

Validated implementation head: `bd0b8ad88f8c1f6b8ba4f8ac7da628df2e51be6c`

This was an independent READ-ONLY system/security audit of the Phase 2A security/state/cloud-worker boundary. The implementation report was treated as a claim set, not as authoritative proof. No code, config, state, workflow, dispatch setting, product/Taste/ranking logic, secret, OpenAI/Codex call, or worker execution was changed or enabled by this audit. The only repository write performed by the audit is this required audit report.

## 1. Scope

Audited against the exact Phase 2A implementation snapshot and its validation evidence:

- task: `WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2A_SYSTEM_AUDIT_01.md`
- implementation report: `reviews/worker_reports/director-orchestration-phase2a-security-boundary-implement-01.md`
- validated head: `bd0b8ad88f8c1f6b8ba4f8ac7da628df2e51be6c`
- validation run: `33964008655`
- validation job: `101300745779`
- validation artifact: `9968832310`
- artifact name: `director-orchestration-phase2a-staging-request`
- artifact digest: `sha256:d1d3e7bcc35e5809bb2862f5472e6e5b6f119afd2a26624540007b70df2d8660`

I also compared validated head `bd0b8ad88f8c1f6b8ba4f8ac7da628df2e51be6c` to the then-current `main` head `bc65d5f6c189e5f7f7b98074dd780fb3f4752469`. The 13 later commits do not modify the Phase 2A controller, contract, state, schemas, publisher, disabled Codex worker template, or Phase 2A validation workflow. The audited boundary therefore remains the same implementation on current `main` at audit time.

## 2. Verified security/state invariants

### Single authoritative state writer and Phase 2A write-off state

`orchestration/state_writer_manifest.json` names exactly one future authoritative writer for `orchestration/state.json`:

`scripts/director_orchestration_controller.py`

It also declares `other_writers_allowed: false` and `state_persistence_enabled_in_phase2a: false`. The Phase 2A contract independently requires `state_persistence_enabled: false`, and the controller fails closed if the contract tries to enable persistence in Phase 2A.

The independent repository review found no second Director state writer. The retained Phase 1 shadow planner is side-effect-free with respect to state/dispatch. An unrelated one-shot IMPLEMENT workflow present in the implementation commit range has repository write permission for separate Taste/product work, but its explicit write set and helper scripts do not target `orchestration/state.json`; it is not a second Director state writer or a cloud-worker path.

Result: **PASS**.

### Immutable intake, revision, attempt and lease binding

The controller loads immutable `orchestration/intake/*.json` events, rejects duplicate event IDs, and verifies each applied event against a canonical SHA-256 digest stored in state. It also rejects unapplied intake events and changed applied events.

For the validated staging candidate `epic-ru-availability-source-probe-01`, independent recomputation of the canonical intake digest produced:

`7d1b509ed87f9cb1017f5e58b4a32e1754ef45a791143c92cad2fd7821863c39`

This exactly matches `orchestration/state.json` for event `intake-20260905-0003-epic-recon-r1`.

Task state is revision-bound; attempts are deterministically identified as `<task_id>:r<revision>:a<attempt_number>`; cloud leases bind task, revision, attempt, slot, lease ID, acquisition state revision and expiry. Stale revision cannot acquire or retain a cloud lease. Publisher validation rejects advanced task revision, advanced attempt, changed lease ID/binding, missing lease, non-cloud occupancy, and expired lease.

Result: **PASS**.

### Exact task-file/base/report binding

The controller verifies repository binding both ways: the current task file must hash to the bound Git blob SHA, and `<base_sha>:<task_file>` resolved through Git must equal that same blob SHA.

The actual validation artifact was independently reopened and inspected. Its staging candidate binds:

- task: `epic-ru-availability-source-probe-01`
- revision: `1`
- role/mode: `READ_ONLY_RECON`
- proposed slot: `slot_2`
- base SHA: `65aa6668e1009885450103e9cde6b6b0f43008d3`
- task file: `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`
- task-file blob SHA: `fdefa23f6aa9d2689f98adcc4af4fd019a7bcb04`
- expected report: `reviews/worker_reports/epic-ru-availability-source-probe-01.md`
- executable: `false`

GitHub independently reports the same blob SHA `fdefa23f6aa9d2689f98adcc4af4fd019a7bcb04` for that exact task file at base `65aa6668e1009885450103e9cde6b6b0f43008d3`. The task itself declares `READ-ONLY / RECON` and the same expected report path.

The publisher requires exact equality for task ID, task revision, attempt number, attempt ID, lease ID, mode, task file, task-file blob SHA, base SHA and expected report path before publication.

Result: **PASS**.

### Maximum two slots and manual occupancy preservation

The contract requires exactly two logical slots; state validation requires exactly `slot_1` and `slot_2` and rejects a third slot. At the validated head, `slot_1` is occupied as `external_manual` by `play-role-and-start-priority-implement-01`; `slot_2` is free. Cloud lease acquisition therefore cannot erase or ignore the external/manual occupancy and cannot exceed total capacity two.

Result: **PASS**.

### READ-ONLY cloud roles only; IMPLEMENT structurally excluded

The controller hard-codes allowed cloud modes to exactly:

- `READ_ONLY_RECON`
- `AUDIT`

The Phase 2A contract requires that exact set. Cloud eligibility excludes every other mode, and lease acquisition independently rejects forbidden modes. Existing `IMPLEMENT` tasks may remain in Director state for manual/external work, but cannot acquire a cloud-worker lease. Request/result schemas and runtime validation also restrict cloud mode to the same two values.

The worker request explicitly carries false authority flags for GitHub write credentials, repository writes, state writes, product writes and next-task selection. The worker result must carry no requested repository mutations, no state/product mutation request, and no secret values.

Result: **PASS**.

### LLM worker privilege boundary and trusted publisher separation

The future worker definition is stored at:

`orchestration/templates/future-read-only-codex-worker.yml.disabled`

It is outside `.github/workflows`, is explicitly marked non-executable for Phase 2A, and Phase 2A has `dispatch_enabled: false`. The worker job has `permissions: contents: read`, checks out the exact request `base_sha`, uses `persist-credentials: false`, gives Codex `permission-profile: ":read-only"` and `safety-strategy: drop-sudo`, and declares only future `OPENAI_API_KEY` as the worker secret. It has no `contents: write`, no `git push`, and no GitHub write credential exposed to the LLM job.

The separate trusted publisher job is the only future job with `contents: write`. `scripts/director_report_publisher.py` validates the trusted request/current state/result binding and can materialize only one exact direct path under `reviews/worker_reports/`. The future workflow additionally checks that the Git diff contains exactly the expected report path, stages only that path, and then commits/pushes it. The LLM cannot select the next task and cannot directly mutate state, product files or repository content.

Result: **PASS**.

### Exact immutable verified `openai/codex-action` pin

The future template pins:

`openai/codex-action@86365089eb2b84e0a8fb0717b304f8bdcb13b20e`

The pin is a full immutable 40-hex commit SHA. Independent lookup in the authoritative official repository `openai/codex-action` resolves that exact commit. GitHub reports commit verification `verified: true`, reason `valid`, verified at `2026-08-20T23:39:07Z`. The action at that exact commit exposes the permission-profile/safety inputs used by the disabled template.

Result: **PASS**.

### Real dispatch remains off

At the validated implementation:

- contract `dispatch_enabled` is false;
- state `dispatch_enabled` is false;
- state persistence is false;
- the future worker YAML is `.disabled` and outside `.github/workflows`;
- the validation workflow has `contents: read`, `persist-credentials: false`, no `OPENAI_API_KEY`, no Codex action, no repository/workflow dispatch and no `contents: write`.

The staging artifact itself records:

- `dispatch_enabled: false`
- `dispatch_performed: false`
- `openai_or_codex_invoked: false`
- `state_mutation_performed: false`
- `product_mutation_performed: false`
- candidate `executable: false`

Result: **PASS**.

## 3. Findings

### Finding 1 — No critical Phase 2A invariant failure found

Severity: `none/blocking: no`.

All critical closure invariants required by the audit task are independently supported: one state writer, no LLM GitHub write credential, no worker state/product/repository mutation authority, stale-result validation, max two slots, dispatch disabled, IMPLEMENT excluded from cloud leases, exact publisher path confinement, and exact task/revision/attempt/lease/base/blob/report binding.

### Finding 2 — Validation run proves the audited snapshot, not merely a self-report

Severity: `informational`.

Run `33964008655` and job `101300745779` completed successfully at exact head `bd0b8ad88f8c1f6b8ba4f8ac7da628df2e51be6c`. Logs show checkout of that exact revision, read-only token permissions, removal/non-persistence of checkout credentials, Phase 1 tests `10/10` passing and Phase 2A tests `19/19` passing. The single artifact `9968832310` belongs to that run/head and its downloaded ZIP SHA-256 exactly matches GitHub artifact metadata: `d1d3e7bcc35e5809bb2862f5472e6e5b6f119afd2a26624540007b70df2d8660`.

The artifact was independently inspected and its exact base/task/blob/report/mode/non-executable staging bindings match the repository snapshot. This closes the provenance question for the validation evidence.

### Finding 3 — Secret detection is deliberately bounded, not general DLP

Severity: `low / accepted limitation for bounded pilot`.

The publisher rejects explicit `secret_values`, known OpenAI/GitHub token forms, named API-key assignments and Bearer credentials. Test coverage proves at least detectable OpenAI-key material is rejected. This is deterministic pattern detection, not a proof that arbitrary encoded, transformed, fragmented or previously unknown secret formats can never appear in model output.

That limitation is acceptable for the proposed single bounded READ-ONLY pilot only because the LLM job receives no GitHub write credential, no Steam/provider secret, repository access is read-only, checkout credentials are not persisted, the result schema forbids secret values/mutation requests, and publication goes through the separate deterministic publisher. Phase 2B must not broaden exposed secrets or worker authority under this acceptance.

### Finding 4 — Live Phase 2B must preserve a current-state/optimistic-concurrency stale barrier

Severity: `Phase 2B gate; not a Phase 2A closure blocker`.

The stale-result logic is real and unit-tested, but Phase 2A has no live dispatcher/publisher path to runtime-prove concurrency behavior. The disabled future template's publisher checks out a trusted repository snapshot and calls the deterministic validator; Phase 2B must ensure that publication is validated against the then-current authoritative state and/or fails closed on a concurrent repository/state advance before a report commit can land.

This does not violate Phase 2A because the template is currently non-executable, persistence and dispatch are disabled, and no report can be live-published by this path today. It is an explicit acceptance condition for activating the Phase 2B pilot rather than evidence against Phase 2A closure.

## 4. Phase 2B readiness

**Phase 2A is accepted and the project may proceed to Phase 2B.**

The accepted scope is deliberately narrow: Phase 2B may separately implement/enable exactly one bounded live `READ_ONLY_RECON` or `AUDIT` cloud-worker pilot, while preserving the two-slot model, external/manual occupancy, exact revision/attempt/lease/base/blob/report bindings, current-state stale-result rejection, trusted report-only publication, and no autonomous `IMPLEMENT` path.

This audit does **not** authorize live dispatch by itself. `IMPLEMENT` must remain outside the cloud-worker path.

## 5. User secret provisioning

**Yes. After this audit acceptance, the user may now provision `OPENAI_API_KEY` directly in GitHub Actions Secrets for `kentrap2011-hub/steam-kz-deals-2`.**

Provisioning the secret alone does not enable dispatch: the Phase 2A contract still has dispatch/persistence disabled and the Codex worker definition is still structurally non-executable. The secret value must not be pasted into chat, Git, task files, reports or logs.

## 6. One next step max

Add the repository Actions secret named exactly `OPENAI_API_KEY` directly in GitHub; do not enable dispatch yet.

## 7. Exact refs

- Audit target: `reviews/system_audits/director-orchestration-phase2a-audit-01.md`
- Validated implementation head: `bd0b8ad88f8c1f6b8ba4f8ac7da628df2e51be6c`
- Phase 2A base/input SHA used by the staging candidate: `65aa6668e1009885450103e9cde6b6b0f43008d3`
- Staging task: `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`
- Staging task blob SHA: `fdefa23f6aa9d2689f98adcc4af4fd019a7bcb04`
- Staging report path: `reviews/worker_reports/epic-ru-availability-source-probe-01.md`
- Validation run: `33964008655`
- Validation job: `101300745779`
- Validation artifact: `9968832310`
- Artifact digest: `sha256:d1d3e7bcc35e5809bb2862f5472e6e5b6f119afd2a26624540007b70df2d8660`
- Future Codex pin: `openai/codex-action@86365089eb2b84e0a8fb0717b304f8bdcb13b20e`
- Official Codex commit verification: `verified=true`, `reason=valid`, `verified_at=2026-08-20T23:39:07Z`

Director orchestration Phase 2A systemic closure: accepted | needs_followup