# ЧАТ 1 — Lean writer auto-ready gate: BLOCKED authorization boundary

**Task:** `WORKER_TASK_DOSSIER_LEAN_WRITER_AUTO_READY_GATE_01.md`  
**Checked:** 2026-11-25, `main@bf5a017392f5ffa491d10ef513d7232b5229d643`.  
**Status:** `BLOCKED_AUTHORIZATION_CONFLICT` — HARD STOP before implementation. This is a report-only PR, **not** a functioning source implementation and **not** activation.

## START / authoritative inputs

Read in order from live `main`: `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, complete worker task; relevant `PROJECT_ROUTES.md` and `PROJECT_DECISIONS.md`; `config/execution_ownership_contract.json`; `config/dossier_notes_v2_generic_replay_policy.json`; `config/dossier_lean_canonical_dual_format_contract.json`; `config/dossier_notes_v2_isolated_lean_acceptance.json`; original shared writer workflow and its preflight/Lean readback implementations.

Ownership preflight: GitHub alone owns scope, grant, immutable receipt validation, writer serialization, once-only state, retry state, and persistence. No ChatGPT scheduler/worker or PR run can issue a new grant. The current generic replay policy has `allow_automatic_writer=false`, `allow_automatic_semantic_retry=false`, `automatic_launch_on_source_merge=false`. Global Lean writer/reader/Deep switches are false.

## Confirmed real first writer failure, not an unspent grant

- The **actual authenticated owner manual** `workflow_dispatch` run [#45540222575](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/45540222575) is `completed/failure`, `run_attempt=1`, actor and triggering actor `kentrap2011-hub`, branch `main`, run source SHA `147be762d217dc1e7dc53a6fbd896f323f6af08c`; job `138956661141`.
- Job step **Persist strictly checked reusable V2 batch in isolated sandbox only** failed with `DOSSIER_V2_BATCH_BLOCKED: [Errno 2] ... config/dossier_notes_v2_batches/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4.json`. This was old-cohort routing before any writer output, commit or push. It is nevertheless a **failed real first writer attempt**, not an unattempted owner grant.
- Source routing fix [PR #482](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/482) has been merged at `7e0d575373e4daf39bb184005dad031b7e85eea1`; correcting the code path does **not** erase or reauthorize the failed attempt.
- The real Git ref `refs/heads/sandbox/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4` still points to `d1b9a9e78dcde879a03370682ade4969763fd9d1`. This is the exact frozen pre-acceptance HEAD in the original grant; 0/6 sandbox acceptance, no new writer commit observed.
- Existing isolated six grant states `single_owner_first_attempt_only=true` and `automatic_retry=false`. In code, the current owner actor/attempt-1 gate is per dispatch invocation; a **new** run ID with attempt 1 must not be misinterpreted as a never-used **per-trial** grant. The worker task explicitly prohibits any automatic retry after failure, **including zero-write** failure.

**Decision:** Catch-up/bootstrap of these existing six under the unchanged grant would turn a known terminal failed writer attempt into an unapproved second execution. Requirement E expressly says STOP if this conflict exists. Do not hide it behind `github-actions[bot]`, a new nonce, workflow change, approval by PR merge, or an artificial “first auto attempt” counter.

## Authorization boundary requiring Director/owner resolution

Two independent grants are absent:

1. **Existing exact six:** a fresh, explicitly owner-approved and canonically recorded recovery/exception decision *for the already failed writer attempt*, with its own immutable per-trial single-use identity and previous-run linkage. It must say whether a second execution is permitted at all. A policy update or user request to build automation is not retrospectively a recovery grant. Without this, the original six must remain terminal-suppressed.
2. **Future batches:** a versioned, trial-scoped `sandbox-auto-writer` eligibility mechanism issued by the genuine existing GitHub owner request/issuer, distinct from global `allow_automatic_writer=false`; only narrowly approved Lean-format trials qualify. No blanket generic batch enablement or automatic semantic retry.

For both: source review and independent L3 authorization review must approve the exact proposed code HEAD; live activation requires a separate explicit owner decision. No source merge or PR CI can implicitly execute the first real write.

## Bounded implementation design once authorization is settled (NOT implemented)

- Reuse the existing locked writer `taste-steam-review-dossier-canonical-writer` and original strict validator/transaction/readback; preserve V1/V2, original18/manual paths and canonical/Deep/production flags.
- Exact ready-wakeup should observe only authenticated, eligible owner-issued trial and terminal typed Assembly receipts, and freeze the current sandbox HEAD and immutable request, grant, marker, six-pair Git SHA map (derive from Git, never owner-pasted fields); fail-closed on non-Lean, stale, malformed, expired, mismatched, wrong-edition/title/year, or partially ready items.
- Catch-up for historical six cannot start unless separately approved. If newly authorized, bound it to **exactly one** named trial/recovery ID and exact frozen HEAD, with explicit previous failed run link and no unbounded scan or rerun.
- A GitHub-owned once-only guard must classify `not_ready / running / accepted / terminal_failed / suppressed`; lock and immutable state must prevent duplicate dispatches, replays, race wakeups, double commit/push, and retries after a failed push. Validate actual actor/ref/repo/workflow and prevent untrusted PR/branch/fork events from escalating permissions.
- Prove that the chosen event mechanism actually fires for **real** trusted GitHub writes (including GitHub-token-generated events where relevant); don't infer event delivery from synthetic tests alone.
- Offline tests must run real event → authenticated ready preflight → **existing** writer → exact 12-file staged/committed readback in disposable Git and adversarial negative matrix. Any PR checks would be synthetic and are not owner credential proof.

## Files changed / verification / activation

- **Report-only:** this file and a closed blocked handoff entry in `CURRENT_TASK.md`. No executable code, workflow, grant, consent, schema, queue, sandbox, receipt or canonical data modified.
- **Read-only evidence:** actual run metadata, job steps and log; real sandbox ref; merged source PR #482; live main and machine contracts.
- **Tests executed:** none; execution cannot enter writer without the missing authorization decision. **GitHub CI:** a report-only PR may have ordinary PR checks, but no end-to-end automation tests exist on this head. Do not mark the requested acceptance tests PASS.
- **Actual writer/Research/Assembly/Deep/production:** not launched. No Actions manual dispatch or retry performed; no semantic replay.
- **Director next decision:** first decide whether the previously failed original six may receive a *new explicit one-use recovery authority*, or remain terminal-suppressed. Only then register a scoped implementation of a trial-specific auto-writer grant/wakeup with independent L3 and exact-HEAD CI; no direct activation on source merge.

**Definition of done not met:** automatic six-item and future-trial writer behavior is NOT implemented, NOT tested end-to-end and NOT activated.
