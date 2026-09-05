# Director Orchestration Phase 2A Security Boundary — IMPLEMENT 01

## 1. Status

`complete`

Phase 2A security/state/cloud-worker boundary is implemented and GitHub-hosted validation passed. Real worker dispatch remains disabled. No OpenAI/Codex call, API-key use, product mutation, deploy, or automated IMPLEMENT execution was enabled by this task.

Validated implementation head: `bd0b8ad88f8c1f6b8ba4f8ac7da628df2e51be6c`.

## 2. Files/contracts changed

Phase 2A infrastructure/control-plane paths:

- `config/director_orchestration_phase2a_contract.json`
- `orchestration/state.json`
- `orchestration/state_writer_manifest.json`
- `orchestration/codex_action_pin.json`
- `orchestration/intake/intake-20260905-0001-play-role-r1.json`
- `orchestration/intake/intake-20260905-0002-wishlist-recon-r1.json`
- `orchestration/intake/intake-20260905-0003-epic-recon-r1.json`
- `orchestration/intake/intake-20260905-0004-top-summary-implement-r1.json`
- `orchestration/schemas/read_only_worker_request.schema.json`
- `orchestration/schemas/read_only_worker_result.schema.json`
- `orchestration/templates/future-read-only-codex-worker.yml.disabled`
- `scripts/director_orchestration_controller.py`
- `scripts/director_report_publisher.py`
- `scripts/test_director_orchestration_phase2a.py`
- `scripts/test_director_orchestration_shadow.py`
- `.github/workflows/director-orchestration-phase2a-validation.yml`

The retained Phase 1 shadow planner implementation remains in place. Its focused tests were updated only to reflect the current manual Chat 1 task occupancy.

## 3. Single-writer model

Authoritative state remains `orchestration/state.json`.

Exactly one repository code path is designated as its future writer:

`scripts/director_orchestration_controller.py`

`orchestration/state_writer_manifest.json` declares that writer and forbids other writers. The Phase 2A contract additionally sets `state_persistence_enabled: false`, so even the authoritative controller's `persist_state(...)` path fails closed in Phase 2A. Lease acquisition/reconciliation used by tests is therefore an in-memory deterministic transition only. No second scheduler/state writer was introduced.

The initial Phase 2A state migration was committed as implementation bootstrap. After this boundary, future persistent state changes require the sole controller and an explicit later contract enablement.

At the validated snapshot there are exactly two logical slots: `slot_1` is reserved as `external_manual` occupancy for Chat 1 task `play-role-and-start-priority-implement-01`; `slot_2` is free. Manual product work therefore continues to consume capacity without being automated.

## 4. Intake/revision/attempt/lease semantics

Committed task intake is represented by immutable `orchestration/intake/*.json` events with unique event IDs. State stores the SHA-256 digest of every applied event and fails closed if an applied event changes or an unapplied/unknown event appears.

Each task is bound to:

- task revision;
- exact task-file Git blob SHA;
- exact base/input commit SHA;
- expected report path;
- mode, gates, dependencies/conflict keys;
- retry state and evidence refs.

Current intake base is the immutable pre-Phase2A snapshot `65aa6668e1009885450103e9cde6b6b0f43008d3`. Controller validation also resolves `<base_sha>:<task_file>` with Git and requires that blob to equal the bound task-file SHA.

Stable cloud attempt identity is `<task_id>:r<revision>:a<attempt_number>`. Cloud lease identity binds slot + exact attempt; cloud leases require expiry and use a 1800-second lease window. External/manual occupancy is separately represented and may have no automatic expiry. Stale revision, stale attempt, wrong lease binding, expired lease, malformed state, unknown schema, or more than two slots fail closed.

## 5. Worker request/result schema

Machine-readable strict schemas are:

- `orchestration/schemas/read_only_worker_request.schema.json`
- `orchestration/schemas/read_only_worker_result.schema.json`

The future cloud-worker contract permits only `READ_ONLY_RECON` and `AUDIT`. `IMPLEMENT` is rejected before lease acquisition.

Requests/results carry exact task/revision/attempt/lease/task-file/blob/base/report bindings. Request authority flags require repository write, GitHub write credential, state write, product write, and next-task selection to all be false. Secret-value arrays must be empty. Result mutation arrays/flags must also be empty.

## 6. Trusted publisher boundary

`scripts/director_report_publisher.py` is deterministic and separate from the future LLM worker.

Before publication it validates:

- current task revision and attempt;
- active cloud lease and non-expired lease time;
- exact lease ID;
- exact task file, task-file blob SHA, and base SHA;
- exact expected report path;
- task-revision-specific allowed result status;
- empty repository/product/state mutation requests;
- empty explicit secret values;
- deterministically detectable credential material in report content;
- path confinement to one direct file under `reviews/worker_reports/`.

`publish_exact_report(...)` can write only the validated expected report file. Phase 2A does not enable a real publisher commit; the write boundary is unit-tested in a temporary repository tree.

The disabled future template uses a separate trusted `publisher` job for repository write permission. The Codex/LLM job itself has no write permission. Before any future commit, the publisher job additionally asserts that `git diff --name-only` contains exactly the expected report path and stages only that path.

## 7. Exact future Codex Action pin/provenance and permissions

Official future action repository: `openai/codex-action`.

Exact immutable pin:

`openai/codex-action@86365089eb2b84e0a8fb0717b304f8bdcb13b20e`

GitHub commit verification observed for that commit: `verified=true`, reason `valid`, verified at `2026-08-20T23:39:07Z`. Provenance is recorded in `orchestration/codex_action_pin.json` together with the official repository/commit/security-document references.

The future definition is deliberately non-executable in Phase 2A at `orchestration/templates/future-read-only-codex-worker.yml.disabled`, outside `.github/workflows`.

Future worker-job boundary:

- GitHub-hosted `ubuntu-latest`;
- `permissions: contents: read` only;
- checkout exact request `base_sha`;
- `persist-credentials: false`;
- exact task revision/blob/base/report prompt bindings;
- structured result schema;
- `permission-profile: ":read-only"`;
- `safety-strategy: drop-sudo`;
- only `OPENAI_API_KEY` is declared for the future Codex step;
- no Steam/provider secret is declared;
- no GitHub write credential is exposed to the LLM job;
- automatic bot allowance is narrowed to `github-actions[bot]`, not all bots;
- worker cannot choose another task.

## 8. Security test results

GitHub-hosted Phase 2A suite: **19/19 passed**.

Covered explicitly:

- current external/manual occupancy + maximum two slots;
- single-writer manifest and Phase 2A persistence disabled;
- stale revision cannot acquire a lease;
- stale revision cannot retain a lease;
- IMPLEMENT cannot acquire a cloud lease;
- read-only bound worker request;
- stale result after attempt advance rejected;
- expired result rejected;
- wrong report path rejected;
- wrong base/task SHA rejected;
- repository/product/state mutation request rejected;
- detectable secret material rejected;
- publisher writes only the exact report in fixture;
- changed immutable intake event rejected;
- malformed/unknown state rejected;
- dispatch-disabled staging candidate is non-executable;
- future Codex template has minimum worker permissions and exact pin;
- validation workflow has no OpenAI secret, Codex invocation, worker dispatch, or contents-write permission.

Retained Phase 1 shadow suite also passed: **10/10**.

## 9. Validation workflow run/job/artifact refs

Workflow: `.github/workflows/director-orchestration-phase2a-validation.yml`

- Run: `33964008655` — `success`
- Run head: `bd0b8ad88f8c1f6b8ba4f8ac7da628df2e51be6c`
- Job: `101300745779` (`security-boundary`) — `success`
- Artifact: `9968832310`
- Artifact name: `director-orchestration-phase2a-staging-request`
- Artifact size: `611` bytes
- Artifact digest: `sha256:d1d3e7bcc35e5809bb2862f5472e6e5b6f119afd2a26624540007b70df2d8660`

All job steps completed successfully, including retained Phase 1 tests, Phase 2A security tests, staging request generation, explicit no-dispatch/no-mutation assertions, and artifact upload.

## 10. Proof no OpenAI/Codex or real worker dispatch occurred

The validation runner token had only `Contents: read` (plus metadata read). Checkout used `persist-credentials: false`.

The job downloaded/ran `actions/checkout` and `actions/upload-artifact`; it did not invoke `openai/codex-action` or any OpenAI client.

The generated staging evidence recorded exactly:

- `dispatch_enabled: false`
- `dispatch_performed: false`
- `openai_or_codex_invoked: false`
- `product_mutation_performed: false`
- `state_mutation_performed: false`
- candidate mode `READ_ONLY_RECON`
- candidate `executable: false`

The staging candidate was `epic-ru-availability-source-probe-01` revision 1 for proposed `slot_2`, but it was not leased, dispatched, or executed.

The validation workflow contains no `OPENAI_API_KEY`, no Codex action, no repository/workflow dispatch, and no `contents: write` permission.

## 11. Exact one-time user setup still required for Phase 2B

No API key is required or inspected for Phase 2A.

Only after Phase 2A is independently accepted, the one-time credential setup for Phase 2B is: in repository `kentrap2011-hub/steam-kz-deals-2`, open **Settings -> Secrets and variables -> Actions -> New repository secret**, create the secret named exactly `OPENAI_API_KEY`, paste the key there, and save it. The key must never be pasted into chat, a task file, a report, or Git.

No Steam/provider secret is required for the READ-ONLY Codex worker definition.

## 12. Whether Phase 2B live READ-ONLY worker pilot can safely start after secret provisioning

**Yes, with one gate:** the Phase 2A implementation and the successful validation evidence are technically ready for a separately enabled Phase 2B READ-ONLY pilot, but live dispatch should not be enabled until this Phase 2A implementation receives independent security/system acceptance. After that acceptance and direct GitHub Actions secret provisioning, Phase 2B may explicitly enable state persistence/dispatch for READ-ONLY RECON/AUDIT only.

IMPLEMENT must remain manual and outside the cloud-worker path.

## 13. One bounded next step only

Run one independent Phase 2A security/system audit against validated head `bd0b8ad88f8c1f6b8ba4f8ac7da628df2e51be6c` and validation run `33964008655`. Do not enable Phase 2B dispatch or add the API key until that audit accepts the boundary.
