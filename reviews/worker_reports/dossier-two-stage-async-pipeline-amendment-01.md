# ЧАТ 1 — Dossier two-stage async Research → Assembly amendment 01

Task: `WORKER_TASK_DOSSIER_TWO_STAGE_ASYNC_PIPELINE_AMENDMENT_01.md`.
Source: `main`; implementation branch: `implement/dossier-two-stage-async-buffer-amendment-01`.
Status: **implemented inactive; PR #177 validation passed; not merged or active**.

## 1. Previously implicit blocking risk

- P1 interfaces exposed per-game Research acceptance receipts and Assembly assignments, but did not define a multi-item immutable **preauthorized buffer** for either semantic stage. A future worker could interpret a receipt as permission to move to the next item.
- P2 `receive_research()` already accepts independently submitted items; it validates the Research marker/assignment and returns GitHub-owned proposed receipt/state. However, the P2 API was single-item and did not prescribe a multi-item run-start order or bounded in-flight capacity.
- P2 `prepare_assembly()` validated one frozen GitHub plan and Research receipt at a time. Its **upstream** Research acceptance is a legitimate barrier *for that game only*, not a reason for a worker to wait after producing the prior Assembly candidate. There was no frozen batched Assembly handoff for the next already-accepted sibling.
- The existing strict **three-game final canonical Dossier group** remains a genuinely different boundary. The task does not remove it or reinterpret unaccepted Research as final Dossier/Deep truth.

## 2. Asynchronous lifecycle and immutable preauthorization

GitHub derives the canonical ordered eligible paths and occupies bounded slots, then prepares an immutable, content-addressed Research buffer listing exact assignment paths, Git blob SHA, game, group, item index, snapshot and assignment IDs. The run-start nonce-only marker's **actual Git parent** freezes the manifest and every assignment. Research runs its exact manifest items in order. After item A's create-only transport is emitted, Research may immediately execute B without seeing A's ingest receipt. Existing transport means only `do not recreate`; it never proves acceptance. GitHub independently validates and commits each Research accepted/rejected receipt/state.

Each **accepted Research** receipt can independently make that exact item eligible for GitHub Assembly planning, without an all-Research-group barrier. GitHub predeclares accepted-only Assembly plans and freezes a second immutable, content-addressed Assembly manifest at its run-start marker. The deterministic stage planner produces one atomic create-only proposal containing the exact assignment + state files for all buffer members. Assembly can run B after A's create-only transport, without any final A acceptance. The offline result checker verifies immutable stage and result Git provenance and P1 output schema/binding but does **not** mark a canonical Dossier accepted.

The Research and Assembly stages need not share a semantic invocation or wait for each other's acknowledgements. Their relation is exact-item `Research accepted → GitHub stages Assembly`; Research on later authorized games, Assembly on earlier accepted games, and both GitHub ingests can overlap. Stage 1 rejection only impacts that stage's exact item; it does not revoke sibling frozen manifests. Later `main` movement does not change an already-frozen marker-parent authorization. The strict final V2 Dossier group validator and existing canonical-writer lock remain the only eventual Dossier/group/Deep authority.

## 3. Bounded deterministic backpressure

Contract `DOSSIER-TWO-STAGE-ASYNC-BUFFER-CONTRACT-V1`: 8 **open item slots per phase** (not a daily quota). GitHub counts prior reserved unresolved slots, **including submitted results not yet ingested**, and selects the canonical earliest still-eligible and unreserved assignments up to `max(0, 8 - open_slots)`. Buffer selection validates the entire candidate list's order and exact Git bindings before capacity truncation. A full buffer only stops GitHub from issuing **new** authorization; already-authorized workers continue regardless of sibling acceptance timing. Slots free on GitHub-owned terminal reconciliation, never merely on worker submission or receipt timeout. Failed/stale/malformed items do not grant a worker retries; any replay needs an explicit new GitHub authorization.

Important integration boundary: this is an offline pure planner with the counts and eligible path list **supplied by future GitHub control plane**, not a new production queue scanner/reconciler. Future shared-writer integration must derive occupancy from authoritative state, commit buffers and complete stage proposals with an atomic create-only collision recheck, and release slots by GitHub reconciliation. No current production execution is activated.

## 4. Changes

- `config/dossier_two_stage_interfaces_contract.json`: explicit per-item non-blocking lifecycle and no premature canonical acceptance.
- `config/dossier_two_stage_staging_contract.json`: buffered paths, bounded open slots, frozen marker-parent authority.
- `config/dossier_two_stage_async_buffer_contract.json`: versioned inactive async authority, backpressure, retry/recovery and strict final boundary.
- `scripts/dossier_two_stage_async_buffer.py`: deterministic preauthorization allocation, frozen work/blob verification, independently buffered Research ingest planning, multi-Assembly staging and result provenance checks.
- `scripts/dossier_two_stage_staging.py`: optional **read-only** revalidation of an already-prepared Assembly assignment, without replaying the create-only collision check; default write-planner collision behavior stays strict.
- `scripts/test_dossier_two_stage_async_buffer.py`: disposable actual Git commit history regression with a real three-game descriptor and independent manifests.
- `.github/workflows/validate-dossier-two-stage-contract-interfaces.yml`: existing read-only PR CI now includes async tests and retains P1/P2/one-stage regressions.

## 5. Required tests (offline)

1. Research A submitted but unaccepted; B and C remain authorized and can submit.
2. Rejected Research A does not revoke B and C.
3. Assembly A submitted without final receipt; B and C remain authorized and may submit.
4. Invalid/mismatched Assembly A does not revoke valid B.
5. Assembly uses canonically accepted Research A while Research B/C proceed.
6. Existing final strict authority remains disabled for the new path.
7. Invalid/stale/tampered/duplicate result/manifest/work fails closed, including forged scope and no worker-issued retries.
8. Open-slot arithmetic is stable; 8 occupied slots issue no new buffer while existing authorization remains valid.
9. Later Research C can complete and be accepted before A/B, and Assembly C can submit before A/B, without losing frozen order/authority.
10. Existing P1/P2 schema, Git history, one-stage date, and Dossier/Deep release-year checks remain in the existing CI job.

**Verified GitHub PR checks:** `Validate inactive Dossier two-stage interfaces` run `37918769747` — success: 12/12 asynchronous Git-history tests, 25/25 previous P2 staging tests, 15/15 P1 contract schema tests, 9/9 current one-stage factual date tests, and the Dossier/Deep identity compatibility regression. `Validate backlog dispositions` run `37918769764` — success. No production invocation or semantic execution was performed.

## 6. Production noninterference and deferred work

Both interface and staging contracts remain `active=false`; async contract is `active=false, authoritative=false, executable_in_production=false`. No new Research/Assembly semantic prompts or workers were created. No current Dossier worker prompt/transport/validator/cache/progress, Deep/Fast, UI, ranking, translation, commercial refresh or production workflow is changed. No Scheduled Task, automation or second scheduler is created.

Later tasks must implement two bounded separate semantic workers **only after explicit authorization**; perform final strict per-group Assembly ingest integration, shared canonical-writer atomic commits, durable slot occupancy/release reconciliation, permitted retry/recovery authorizations and end-to-end real-evidence/parity/shadow validation before a separately approved cutover. The current one-stage Dossier remains the sole production authority.
