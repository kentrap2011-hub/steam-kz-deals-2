# ЧАТ 1 — typed director fast path + anti-aging

**Task ID:** `director-typed-fastpath-anti-aging-implement-01`  
**Source:** current `main` at work start; repository `kentrap2011-hub/steam-kz-deals-2`  
**Scope:** `DIRECTOR_PROTOCOL.md` + this report only  
**Status:** `complete_for_independent_qa` (not accepted / not merged)

## Verified facts and architecture preflight

The named task is registered in the current Board top section and in the addressed `config/director_task_plan.json` record (worker slot ЧАТ 1). Independent QA is separately planned for ЧАТ 2. Existing `CHAT_PROTOCOL.md` START and `CHAT_CONTEXT.md` govern worker actions. Inputs reviewed: draft report PRs #248 (ЧАТ 5), #251 (ЧАТ 6), #253 (ЧАТ 7). They identify missing typed STATUS stop-condition; they do not prove the actual tool-call cause of Director latency.

**Owner:** GitHub remains the governance source of truth and production control plane; Director orchestrates; worker implements/reviews. **Authorization:** registered limited user-approved governance change. **Boundary:** no production ownership transfer, schedules, queues, retries, checkpoints, scripts, CI, validators or automations added/changed. No Dossier/Deep/Research/Assembly/deploy changes.

## Changes

Replaced the old generic seven-part gate in `DIRECTOR_PROTOCOL.md` §1 with one visible typed table and retained common safety preflight; added **one** human PR review rule to retire/reconcile old governance requirements and limit future mandatory-reading growth. Did not remove existing registration, slot identity, exact-HEAD QA, required CI, fail-closed merge or role restrictions. Existing §2/§3/§8/§10/§12 remain untouched.

**Static size check:** prior 268 lines, updated 271 lines, net **+3** (limit +45); typed entry starts at line **28** (limit 120). Source code/workflows untouched.

## Bounded route walkthroughs (text-level only)

| Case | Expected route; explicit stop |
| --- | --- |
| **STATUS: «Проверь ЧАТ 1»** | Current Board slot → addressed registry record if needed → exact report/PR HEAD and relevant CI/QA. Once submission/QA status is established, **STOP**: no whole-registry, Board history, source patch or Director technical audit. Without chat visibility, inactivity is **UNKNOWN**. |
| **DECIDE: «Что дальше?»** | Board current top → affected IDs/dependencies and exact PR/report only if needed; recommend one justified next actor/action. **STOP** before unsolicited task creation, production action or treating observations as defects. |
| **REGISTER: «Назначь задачу»** | Verify authorization/duplication/ownership/slot → one named task + synchronized registry/Board in registered PR → existing CI on exact HEAD → merge to `main` → user may launch. Before those gates, **BLOCKED_AUTHORITY**. |
| **MERGE: «Принимай PR»** | Exact live HEAD + independent QA on same HEAD + required successful checks + authority/merge gates. **BLOCKED** for stale QA, failed/pending/skipped/missing required checks or absent authorization. No implicit deploy. |
| **Stale handoff** | Prior handoff conflicts with current Board/registry/PR: use canonical current targeted facts; refuse inferred live state, mark discrepancy UNKNOWN until reconciled. |
| **Unsafe PR** | Report says PASS but PR gained a new HEAD or has missing required CI: **BLOCKED** and new exact-HEAD QA/CI; do not bypass. |
| **Future rule creep** | Governance PR adds ten «mandatory» rules: reviewer identifies owner, replaced rules or genuinely novel risks, change to required read volume and why targeted retrieval is insufficient, and runs STATUS + unsafe-MERGE walkthrough. No recurring Director check or new automated test. |

## Comparison to six ЧАТ 7 acceptance points

1. **PASS (static):** only protocol + own report; no second registry, Board, scripts, workflow or scheduler.
2. **PASS (static):** role remains at top, typed map line 28 of first 120, net +3 lines (≤45).
3. **PASS (text contract only):** STATUS stop after sufficient evidence, zero unjustified full-fetch / worker-level audit required; real model behavior **not proven**.
4. **PASS (text contract only):** REGISTER preserves main/CI; MERGE preserves exact-head independent QA and fail-closed conditions.
5. **PASS (static):** one compact human governance PR review rule, not new documents, standing requirements or CI.
6. **PENDING independent QA:** six walkthroughs above (four routes + stale handoff/unsafe PR), plus future rule creep, are **static reasoning examples**. Independent QA of final PR HEAD and five observed/replayed Director requests have **not** been performed here and cannot be claimed by this implementer.

## Validation / unresolved / next

**Performed:** in-memory bounded replacement assertion; route keywords present; entry line and net line limits; retained merge safety and unchanged following sections. **Not performed:** independent QA, observed model tool-call replay, real main-branch merge, production validation. Existing required CI status to be read from draft PR exact HEAD; this report does not claim it succeeded.

**Next:** ЧАТ 2 performs independent exact-HEAD QA of this draft PR and checks actual changed-file list / existing CI; Director subsequently decides whether to merge. No automatic acceptance or future CI project.

**Efficiency / reusable lesson:** none (this protocol contains the durable route).
