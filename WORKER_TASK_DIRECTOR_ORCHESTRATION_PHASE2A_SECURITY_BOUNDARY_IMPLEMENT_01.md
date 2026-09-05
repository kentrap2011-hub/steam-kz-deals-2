# WORKER TASK — DIRECTOR ORCHESTRATION PHASE 2A SECURITY BOUNDARY IMPLEMENT 01

Task ID: `director-orchestration-phase2a-security-boundary-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/director-orchestration-phase2a-security-boundary-implement-01.md`
Priority: `VERY_HIGH_INFRASTRUCTURE_PRIORITY`

## Context

Phase 1 shadow observer is implemented and independently accepted:
- implementation: `reviews/worker_reports/director-orchestration-shadow-observer-implement-01.md`
- audit: `reviews/system_audits/director-orchestration-phase1-audit-01.md`
- closure: accepted.

Phase 2 goal from the orchestration recon is eventual automatic READ-ONLY / RECON and AUDIT cloud workers using GitHub-hosted execution + official OpenAI Codex Action / `codex exec`, while keeping IMPLEMENT manual.

This task is **Phase 2A only**: build and validate the security/state/dispatch boundary with real dispatch still disabled. It must not require an OpenAI API key yet.

## Goal

Prepare the exact deterministic control plane required before any real cloud worker can run:

1. one authoritative orchestration state writer/controller;
2. immutable intake events / versioned task revisions;
3. fail-closed slot leasing and stale-result rejection;
4. exact READ-ONLY worker request/result schema;
5. trusted report-publisher boundary separated from any future LLM job;
6. disabled-by-default cloud-worker workflow/template pinned to verified official Codex Action provenance;
7. security tests proving no credential or write authority reaches a future worker job;
8. no real OpenAI/Codex invocation in this Phase 2A task.

## Required implementation

### A. Orchestration contract/state evolution

Extend the Phase 1 contract/state minimally so Phase 2A can represent:
- `schema_version` / `state_revision`;
- immutable intake event IDs;
- task revision;
- attempt ID (`task_id + revision + attempt_number` or equivalent stable identity);
- slot lease owner/status/expiry;
- exact task-file blob SHA;
- base/input SHA;
- expected report path;
- review/user gates;
- retry state;
- evidence refs;
- explicit `dispatch_enabled: false` for Phase 2A.

The current manual Chat 1 product work must remain representable as external/manual occupancy until it actually finishes.

### B. Single deterministic state writer/controller

Add one bounded deterministic controller script/workflow that is the **only** future writer of `orchestration/state.json`.

It may in Phase 2A:
- ingest explicitly committed immutable intake events;
- validate allowed state transitions;
- reconcile leases in dry-run/staging mode;
- compute dispatch requests;
- persist state only in a dedicated test/staging workflow if the task explicitly validates that path safely.

It must NOT dispatch a real worker in Phase 2A.

No second state writer is allowed.

### C. Read-only cloud worker request/result contracts

Create machine-readable schemas/contracts for a future READ-ONLY RECON/AUDIT worker containing at minimum:
- task ID/revision/attempt;
- task file + exact blob SHA;
- base SHA;
- allowed mode (`READ_ONLY_RECON` / `AUDIT` only);
- allowed input refs;
- expected report path;
- forbidden product/repository write authority;
- result status;
- exact attempt/task/base bindings;
- report content or trusted handoff payload;
- no secret values.

### D. Trusted publisher separation

Implement or specify deterministic trusted publisher validation so future LLM output cannot write arbitrary repository paths.

The publisher must enforce at minimum:
- expected report path only;
- exact task/revision/attempt match;
- exact task-file blob SHA/base SHA match;
- allowed report schema/status;
- stale lease/result rejection;
- sanitized content/no secret material where deterministically detectable;
- no product file mutation;
- no state mutation by the worker itself.

If actual report commit is not enabled in Phase 2A, unit-test the publisher boundary with fixtures.

### E. Codex worker definition — disabled / non-executing in Phase 2A

Verify the official `openai/codex-action` source and current security guidance from authoritative OpenAI/GitHub sources.

Prepare the future worker definition as either:
- a non-executable template under an orchestration/template path; or
- a workflow that is structurally impossible to invoke unless a later explicit Phase 2B enable flag/contract change is made.

Requirements for the future worker job:
- GitHub-hosted runner;
- `actions/checkout` with `persist-credentials: false`;
- repository `contents: read` only;
- no GitHub write credential in the LLM job;
- only future `OPENAI_API_KEY` secret exposed to the Codex step;
- no Steam/provider secrets;
- action dependency pinned to an immutable verified commit SHA, not floating tag;
- prompt bound to exact task revision/blob/base SHA;
- READ-ONLY mode only in Phase 2;
- structured result schema;
- no worker ability to choose next task.

Do **not** call Codex/OpenAI during this task.

### F. Security / deterministic tests

At minimum prove:
1. max two logical slots and manual occupancy remain respected;
2. only one state writer exists;
3. stale task revision cannot acquire/retain a lease;
4. stale worker result is rejected;
5. result for wrong report path is rejected;
6. worker result cannot mutate product/state files;
7. unknown/malformed state fails closed;
8. task mode other than READ_ONLY_RECON/AUDIT is rejected by Phase 2 worker contract;
9. future worker job has no GitHub write credential path;
10. `dispatch_enabled=false` prevents real worker invocation;
11. no OpenAI/API secret is required for Phase 2A validation.

## GitHub workflow validation

Create/run a safe Phase 2A validation workflow that:
- uses no OpenAI/Codex/API key;
- tests controller/request/result/publisher contracts;
- may produce a staging dispatch-request artifact only;
- does not call a worker;
- does not mutate product code/data;
- does not merge/deploy.

Run it at least once and capture exact run/job/artifact refs.

## Security / secret boundary

The eventual `OPENAI_API_KEY` is a user credential gate for Phase 2B, not Phase 2A.

Never ask for or store the key in chat/task/report/Git.
After Phase 2A is accepted, Director will tell the user how to add the key directly to GitHub Actions Secrets from the phone/browser.

## Boundaries

Do NOT:
- invoke OpenAI/Codex;
- require or inspect `OPENAI_API_KEY`;
- dispatch any real worker;
- automate IMPLEMENT;
- alter product/Taste/ranking behavior;
- alter deploy/production authority;
- create GitHub Projects/Issues as a second canonical queue;
- create a second state writer;
- grant an LLM job GitHub write credentials;
- create more than two logical worker slots.

## Done when

Save:
`reviews/worker_reports/director-orchestration-phase2a-security-boundary-implement-01.md`

Include:
1. Status
2. Files/contracts changed
3. Single-writer model
4. Intake/revision/attempt/lease semantics
5. Worker request/result schema
6. Trusted publisher boundary
7. Exact future Codex Action pin/provenance and permissions
8. Security test results
9. Validation workflow run/job/artifact refs
10. Proof no OpenAI/Codex or real worker dispatch occurred
11. Exact one-time user setup still required for Phase 2B
12. Whether Phase 2B live READ-ONLY worker pilot can safely start after secret provisioning
13. One bounded next step only

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`
