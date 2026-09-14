# TRANSIENT PLATFORM ISSUES

Purpose: keep a lightweight durable log of platform/tool problems that appear, later disappear, and are not yet reproducibly explained. This file is for recurrence tracking, not for speculative root-cause claims.

## Operating rule

For each occurrence record: date/time when known, affected surface/action, exact visible symptom, whether it reproduced, impact, durable evidence/ref, and current status.

Do not infer hidden causes such as timeout, context exhaustion, rate limit, tool limit, or safety classifier unless explicit evidence exists.

Escalate from simple logging to a dedicated bounded diagnostic when either:
- the same issue class is observed at least 3 times within 7 days; or
- it blocks production/acceptance twice; or
- one occurrence causes data loss, unsafe state, or an unrecoverable production block.

If a dedicated diagnostic already exists, link it rather than duplicating investigation here.

---

## TPI-001 — Intermittent OpenAI safety-layer block on GitHub write actions

First recorded: 2026-09-14
Last seen: 2026-09-14
Status: `reproducible_needs_diagnostic`

Observed behavior:
- one neutral GitHub `create-file` succeeded;
- later neutral `create-file` calls in the Director session were blocked before connector execution with the OpenAI safety-layer message;
- an independent worker session then completed six harmless `create-file` calls successfully;
- that worker later saw the same safety-layer presentation on a harmless `delete-file` call, after which another `create-file` succeeded;
- the exact Director-blocked `create-file` operation for `WORKER_TASK_TASTE_DOSSIER_RUN_STOP_RECON_01.md` was then repeated in the worker session with the same repository, branch, path, commit message, content, and action, and was blocked with the same safety-layer message before execution;
- reads continued to work;
- no structured classification id, HTTP status, policy reason, or stable numeric threshold was exposed.

Current conclusion:
- the earlier hypothesis that the block was specific to the Director session is no longer supported for the exact reproduced operation;
- an exact create-file request can reproduce the block across Director and worker sessions;
- the precise triggering field or safety rule remains unobservable;
- not proven to be repository-wide or permanently create-file-wide because other harmless create-file calls have succeeded;
- do not vary requests with the purpose of bypassing the safety layer.

Evidence:
- `reviews/worker_reports/github-create-file-safety-block-recon-01.md`
- report commit `2700dc5c676c73b48c4549d9526755381ce1a3d8`
- exact worker reproduction reported in chat on 2026-09-14; no GitHub commit exists because the operation was blocked before execution.

Occurrence count tracked here: 3 on 2026-09-14 (Director create-file block; worker delete-file block; exact worker reproduction of the Director-blocked create-file request).

Escalation state:
- recurrence threshold reached (3 occurrences within 7 days);
- dedicated bounded diagnostic is warranted only if further isolation can be done without probing for a safety bypass; until then, preserve evidence and continue project work through permitted paths.

---

## TPI-002 — Worker session interruption with no exposed termination telemetry

First recorded: 2026-09-14
Status: `intermittent_cause_unobservable`

Observed behavior:
- prior worker sessions stopped unexpectedly at different stages;
- no explicit system/tool error established the termination cause;
- the same chats later accepted user input;
- controlled replay of the proven operations did not reproduce the interruption;
- platform/session termination reason, wall-clock budget, context/budget state, and authoritative last-dispatched/last-delivered tool marker were not exposed.

Current conclusion:
- exact cause remains unobservable;
- do not relabel as context exhaustion, timeout, or tool limit without future explicit evidence;
- keep PITFALL-004 reproducibility trace for any recurrence.

Evidence:
- `reviews/worker_reports/worker-interruption-diagnostic-01.md`
- `KNOWN_WORKER_PITFALLS.md -> PITFALL-004`

Occurrence count tracked here: 2 historical incidents covered by the diagnostic report.

---

## New occurrence template

### TPI-XXX — Short issue name
First recorded: YYYY-MM-DD
Last seen: YYYY-MM-DD
Status: `observed | intermittent_cause_unobservable | reproducible_needs_diagnostic | resolved_with_cause`
Occurrence count: N

Observed behavior:
- exact symptom;
- affected action/surface;
- whether retry/replay reproduced it;
- user/production impact.

Evidence:
- exact report/commit/run/error reference when available.

Current conclusion:
- narrowest supported classification only.
