# Worker report — Dossier async Research semantic worker implementation 01

- Task: `WORKER_TASK_DOSSIER_ASYNC_RESEARCH_SEMANTIC_WORKER_IMPLEMENT_01.md`
- Physical worker: **ЧАТ 1 — new conversation**
- Source: `main` at implementation branch origin `17ddd004e031ea9ded8464774fb25e7e10f0c07c`
- PR: [#181 — inactive Research semantic worker](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/181)
- Branch: `implement/dossier-async-research-semantic-worker-01`
- Mode: **INACTIVE; PR-only/offline validation; no production authorization**

## Changed paths

1. `config/dossier_two_stage_research_semantic_worker_prompt.md` — versioned Research entry prompt with frozen parent/manifest/assignment bindings, exact neutral research semantics, twelve dimensions, strict public/privacy provenance, per-item failure isolation, and no acknowledgment/slot/ingest waits.
2. `scripts/dossier_two_stage_research_worker.py` — pure Python Git-history frozen work enumerator; binds approved prompt bytes and Git blob to the *actual* marker parent, retrieves original assignment and exact create-only transport path; prevalidates a Research result and inspects the unchanged original Git transport without claiming GitHub acceptance.
3. `scripts/test_dossier_two_stage_research_worker.py` — isolated disposable Git fixtures; global gate and prompt-parent checks, schema and provenance, no-sibling-ack independent submissions, replay/collision/tamper/failure, stale/missing prompt, exact scope, 12 frozen items beyond old eight-slot gate.
4. `.github/workflows/validate-dossier-two-stage-research-worker.yml` — pull-request-only Python regression for Research plus existing P1/P2/fully-async, one-stage factual dates, and Dossier/Deep release-year compatibility.
5. This worker report.

No edit to Assembly worker files, shared staging/contracts, `CURRENT_TASK.md` (large shared multi-worker handoff), production inbox/cache/queue, scheduled automation, or the existing one-stage Dossier strict validator.

## Authority and invariant proof

- **Canonical authority:** GitHub alone owns finite work authorization, exact order, original group bindings, source worker index, immutable single-parent marker, item acceptance/rejection, retry/recovery, and final atomic original three-game Dossier ingest.
- **Scope and original Git provenance:** `frozen_research_batch` delegates to existing strict `frozen_buffer(... phase=research)` and `research_authority`. It reads the marker's *actual* single parent, not the moving HEAD or an untrusted caller-provided assignment. The only caller input is the exact GitHub-provided marker commit and buffered manifest path. Work path/assignment, Research schema hash, descriptor/index bindings, Git blob and original marker are checked before providing a work item. Frozen prompt bytes and blob are required in the same immutable marker parent.
- **Full asynchronous traversal:** returns all frozen `items`, in original manifest order; there is no Research accepted-receipt check, sibling checkpoint, eight-slot gate, daily quota, worker-chosen scope/recovery or polling. A local item exception leaves separately frozen siblings available.
- **Result invariants:** one exact-package JSON under `DOSSIER-RESEARCH-PACKAGE-V1` with the original assignment, verified 12-dimension survey, privacy/provenance/source validation, and factual dates. The pure helper computes exact canonical JSON SHA, raw bytes SHA and Git blob identity; it never supplies an acceptance receipt.
- **Transport invariants:** result path is derived from `receipt_paths`, not supplied by the semantic worker. Existing exact candidate requires one create-only Git introduction on the marker's first-parent lineage, original blob/raw bytes still intact, and schema/binding validation. An identical candidate is only `submitted_unaccepted`. A different candidate, rewritten blob, added extra path, or unknown provenance fails closed.
- **Execution boundaries:** helper has no CLI/HTTP/Git-write/real semantic code. New workflow triggers on PR only; the inactive gates remain unchanged (`active=false`, `authorized_for_semantic_execution=false`, `executable_in_production=false`, global `semantic_workers_implemented=false`). The sole production Dossier remains one-stage.

## Checks

- Research fixture test file includes 12 passing tests, including twelve GitHub-prepared Research games across four original three-game groups (above the deprecated eight-slot gating model). The final optimized guard caches only immutable marker-parent proof within an invocation, returning defensive copies and rechecking inactive gates; this avoids quadratic repeat Git scans without introducing any sibling ack/worker-owned queue.
- **Authoritative GitHub Actions success:** `Validate inactive Dossier Research semantic worker`, run [37955966206](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/37955966206), validated Research implementation head `98f4e3385e9f49e9c1df4fe491061a6a73359c3d`. All job steps passed: Research **12/12** (7.933 s), P1 strict schemas **15/15**, P2 staging Git history **25/25**, async Research/Assembly buffers **12/12**, one-stage GitHub factual date regression **9/9**, Dossier/Deep release-year identity compatibility **PASS**. Total: **73 Python unit tests and 1 compatibility regression**. `Validate backlog dispositions` run [37955966152](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/37955966152) also **success**.
- No real Steam/web semantic work or current production data used in fixtures.

## Remaining blockers and strict stop

- PR #181 has **successful offline CI** and remains unmerged; Director review and separate integration authorization are still required. This report is not a claim of production readiness or final acceptance.
- Research-only implementation **does not** make `semantic_workers_implemented=true`. Independently owned Assembly semantic worker, future GitHub-owned live integration/writer and item acceptance, real-evidence parity, shadow quality and explicit Director-authorized cutover remain required.
- Existing GitHub P2 provenance validator and the original atomic three-game final Dossier acceptance remain the eventual authoritative path. Newly submitted Research is never itself a validated/canonical Dossier.
- No Scheduled Tasks created/edited/toggled or executed, no real Research run, no production activation, no PR auto-merge.
- `CURRENT_TASK.md` was intentionally left untouched to avoid overwriting parallel worker handoff; this report is the bounded Research completion reference for Director.
