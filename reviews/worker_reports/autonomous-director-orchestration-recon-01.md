# Autonomous Director Orchestration Recon 01

Task: `autonomous-director-orchestration-recon-01`
Mode: `READ-ONLY / RECON`
Status: `complete`

## 1. Feasibility verdict

**Feasible without a permanently running home PC.**

The smallest reliable steady-state design is:

`Android Director chat -> immutable GitHub intake event -> GitHub-owned queue/state -> serialized dispatcher -> max 2 cloud workers -> report/PR -> CI/deploy observation -> Director evaluator -> mandatory review gates -> next task or explicit user gate`.

The existing protocol already has the right durable primitives: task files, worker reports, Director board, independent review checkpoints, GitHub Actions, CI/deploy evidence, and a two-worker conflict rule. The migration should therefore automate the handoff/execution loop rather than redesign the product pipeline.

The current ordinary worker-chat pattern itself should **not** be treated as an automatable execution substrate. No authoritative OpenAI mechanism was found that lets GitHub reliably wake an arbitrary existing ordinary ChatGPT worker chat, inject a task, wait for it, and collect a durable result. The supported programmatic cloud path verified in this recon is the official OpenAI Codex GitHub Action / `codex exec` path running on GitHub-hosted runners. Ordinary worker chats remain a manual fallback during rollout, then are replaced by cloud worker jobs.

This design preserves the core Director contract: the Director still accepts user intent, workers remain bounded, workers do not pick the next big task, reports remain durable, independent review stays advisory, and GitHub remains the durable control plane.

## 2. Existing project constraints verified

Current project refs:

- `WORKER_TASK_AUTONOMOUS_DIRECTOR_ORCHESTRATION_RECON_01.md` blob `4ed1d181bf1f892a5819afea2e05823f87ba9f6c`.
- `DIRECTOR_PROTOCOL.md` blob `93b02638ed7df64bcbe8371767831112cbc33ad6`.
- `DIRECTOR_TASK_BOARD.md` blob `4707433fcc4ab68baa3fb15bee3731e9c323477f`.
- `DIRECTOR_REVIEW_CHECKPOINTS.md` blob `f90585fc4f9647278cee0269e6a04d93f2a3da0f`.
- `CHAT_PROTOCOL.md` blob `f445a1890862ec49b2b9258a252837f7c8fe951a`.
- `config/execution_ownership_contract.json` blob `f0b5f48756489965ec223a42f3b234f62ac4bae1`.
- Active Taste task remains `WORKER_TASK_TASTE_EVIDENCE_STATE_AND_CONFIDENCE_IMPLEMENT_01.md`, blob `083e2e30bbf1dbc1ce3406a5f8ad741e4c3c0efc`; this recon does not stop, reassign, or modify it.

Important preserved rules:

- maximum two worker slots;
- do not run conflicting Taste/ranking implementations in parallel;
- unclear work starts with bounded RECON;
- worker results must be durable in GitHub;
- workers do not choose the next major task;
- Taste Reviewer advice is advisory and may not silently become product policy;
- System Audit / Taste Review checkpoints remain mandatory at their current triggers;
- GitHub remains owner of queue, retry, completeness and orchestration logic for automated processes;
- interactive chats are operator/developer sessions, not background production executors.

## 3. Exact current cloud mechanisms and limits

### OpenAI mechanisms verified

1. **Official Codex GitHub Action**
   - `https://github.com/openai/codex-action`
   - Runs `codex exec` inside a GitHub Actions workflow.
   - Uses an OpenAI API key supplied as a GitHub Actions secret.
   - Supports read-only/workspace permissions, model/effort selection, structured output schema, prompt files, and a final message output.
   - Security guidance: `https://github.com/openai/codex-action/blob/main/docs/security.md`.
   - This is the recommended cloud worker substrate because GitHub can dispatch it directly and no desktop Codex UI or home runner is needed.

2. **OpenAI Responses API background mode**
   - `https://developers.openai.com/api/reference/cli/resources/responses/methods/create`
   - `background=true` is supported, and a response can later be retrieved by response ID.
   - This can be useful later for long-running Director/reviewer reasoning without holding a runner open, but is not required for the minimum migration.

3. **ChatGPT Scheduled Tasks / monitoring**
   - `https://help.openai.com/en/articles/10291617-what-is-agent-mode`
   - Scheduled Tasks can run one-time/recurring tasks, monitor for changes, and send mobile push notifications when notifications are enabled.
   - Use this only as a user-notification/control-plane layer, not as the canonical queue owner.

4. **ChatGPT GitHub connection / event-triggered Work tasks**
   - `https://help.openai.com/en/articles/11145903`
   - Connected GitHub repositories can be accessed on demand.
   - Eligible Work users can create webhook-based tasks for supported GitHub pull-request activity, including PR open/ready/close and, depending on trigger, reviews/comments/commit updates/merges.
   - `https://help.openai.com/en/articles/20001275/` confirms Work can run on web/mobile and supports scheduled/event-triggered connected-app tasks.
   - Therefore ChatGPT-native Android push can be added later by mapping a user gate to supported PR activity. Do not assume arbitrary GitHub events can wake an ordinary Director chat.

5. **Codex cloud UI**
   - Cloud Codex tasks exist in OpenAI-managed environments, but this recon did **not** find an authoritative documented API that should be assumed to programmatically wake/control arbitrary existing Codex UI chats from GitHub.
   - Therefore the design intentionally does not depend on desktop/mobile Codex chat history as infrastructure.

### GitHub mechanisms verified

1. **GitHub Actions events**
   - `https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows`
   - Supports `push`, `schedule`, `workflow_dispatch`, `repository_dispatch`, `workflow_run`, PR events, deployment events, etc.
   - `workflow_run` chains are limited to three levels; do not build a deep A->B->C->D... chain.

2. **Dispatch from a workflow**
   - `https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow`
   - Events emitted with the repository `GITHUB_TOKEN` normally do not recursively create new workflow runs, except `workflow_dispatch` and `repository_dispatch`, which do.
   - Use `repository_dispatch` as the explicit event bus between dispatcher/worker/evaluator stages and keep a scheduled reconciliation workflow as a recovery path.

3. **Concurrency**
   - `https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax`
   - A concurrency group can serialize the dispatcher/control-state writer.
   - Current GitHub Actions supports queued concurrency groups; nevertheless state transitions must remain idempotent and version-bound.

4. **Exactly two workers**
   - `https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations`
   - Matrix strategy supports `max-parallel: 2`.
   - The recommended design additionally keeps two explicit logical slot leases, because conflict rules are semantic and cannot be expressed by `max-parallel` alone.

5. **Hosted-runner limit**
   - `https://docs.github.com/en/enterprise-cloud@latest/actions/reference/limits`
   - A GitHub-hosted Actions job has a 6-hour execution-time limit. Worker tasks must stay bounded; no worker may rely on an indefinitely alive job.

6. **GitHub secrets**
   - `https://docs.github.com/en/actions/concepts/security/secrets`
   - Store `OPENAI_API_KEY` and any future credential in repository/environment/organization secrets, never in task files, reports, chat messages or Git.
   - GitHub automatically redacts recognized secrets, but redaction is not a complete security boundary; minimize exposure and permissions.

7. **Environment/user approvals**
   - `https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments`
   - Environments can gate jobs with required reviewers and keep environment secrets unavailable until approval where plan/repository rules support it.
   - Use only for true credential/deploy authority gates; do not turn every task into a manual deployment approval.

## 4. Recommended cloud-first architecture

### 4.1 Director intake from Android

The user continues to talk only to the Director in natural language:

- add a task;
- raise/lower priority;
- postpone;
- cancel;
- resolve a user gate.

The Director converts that intent into a small **immutable intake event** committed to GitHub, rather than directly mutating the shared queue state.

Proposed path:

`orchestration/inbox/<timestamp>-<event-id>.json`

Example event types:

- `task_created`;
- `task_reprioritized`;
- `task_deferred`;
- `task_cancel_requested`;
- `user_gate_resolved`.

The event contains no secret. It references an existing/new human-readable `WORKER_TASK_*.md` when a full worker instruction is needed.

Why immutable intake events: the Director chat and background dispatcher must not race by both editing one `state.json` file. The Director writes events; only the GitHub dispatcher writes canonical orchestration state.

### 4.2 Durable GitHub state

Proposed canonical state:

`orchestration/state.json`

Only the serialized dispatcher/controller workflow may update it.

Human-readable task instructions remain in existing `WORKER_TASK_*.md` files. Existing worker reports remain in `reviews/worker_reports/`.

No GitHub Project is required for the initial system. Issues/PRs are transport/review/notification surfaces only; repository files remain canonical truth.

### 4.3 Serialized dispatcher

One workflow owns state mutation, with a dedicated concurrency group such as:

`director-orchestrator`

It:

1. ingests unconsumed intake events;
2. reconciles finished/cancelled/expired attempts;
3. validates review checkpoints;
4. computes eligible tasks;
5. applies dependency and conflict rules;
6. leases at most two logical slots;
7. dispatches cloud workers through `repository_dispatch`;
8. writes the new state in one commit;
9. emits no product change itself.

A periodic reconciliation run is a safety net for missed events/stale leases, not a second scheduler.

### 4.4 Cloud worker slots

Ordinary worker chats are replaced by **Cloud Worker Slot 1** and **Cloud Worker Slot 2**, each represented by a lease in state, not by a persistent conversation.

Worker implementation substrate:

`GitHub-hosted runner + openai/codex-action + current task file + exact task revision + current canonical repo state`.

For `READ-ONLY / RECON` and `AUDIT`:

- Codex job receives `contents: read` only;
- checkout uses `persist-credentials: false`;
- Codex runs with read-only permissions;
- Codex returns structured output/final report content;
- a separate trusted publish step/job writes only the allowed report path and task metadata.

For future bounded `IMPLEMENT`:

- Codex works against a per-attempt branch/worktree;
- agent job does **not** receive a GitHub write credential;
- agent output is transferred to a separate trusted publisher job;
- publisher verifies allowed paths, task revision, conflict lease and report schema before pushing a task branch/opening a PR;
- production/main is not changed until CI and required review/user gates pass.

This split prevents the LLM worker from owning dispatch, GitHub state, merge authority or broad repository credentials.

### 4.5 Report and completion observation

Every attempt has a stable identity:

`<task_id>:r<task_revision>:a<attempt_number>`.

The finished worker produces:

- expected report path;
- exact attempt ID;
- task revision;
- task-file blob SHA;
- input/base SHA;
- worker workflow run ID;
- candidate branch/head SHA if applicable.

Worker completion emits a trusted `repository_dispatch` event such as `worker_finished` even on failure (`if: always()` in the trusted wrapper). The dispatcher/evaluator accepts the result only if all version bindings match the current lease.

A scheduled reconciliation also scans active leases versus GitHub run state so a lost dispatch event cannot permanently occupy a slot.

### 4.6 Director evaluator

A cloud **Director Evaluator** replaces the manual `"Готово, читай."` handoff after Phase 1.

It is a bounded read-only OpenAI reasoning job launched by GitHub after report/CI evidence is ready. It receives only:

- current task entry;
- worker report;
- minimal canonical protocol/checkpoint files;
- exact CI/deploy evidence;
- relevant prior report if explicitly referenced.

It outputs a strict machine schema such as:

- `accept_report`;
- `retry_same_scope`;
- `request_followup_fix`;
- `enqueue_review`;
- `raise_user_gate`;
- `block_external`;
- `no_safe_decision`.

A deterministic GitHub controller validates that recommendation against allowed transitions. The LLM does **not** directly mutate queue state or pick arbitrary backlog work.

## 5. Minimal machine-readable state model

Recommended task entry:

```json
{
  "task_id": "example-01",
  "revision": 1,
  "mode": "READ_ONLY_RECON",
  "priority": {"class": "VERY_HIGH", "rank": 100},
  "domain": "orchestration",
  "conflict_keys": ["orchestration-control"],
  "status": "queued",
  "assigned_slot": null,
  "task_file": "WORKER_TASK_EXAMPLE_01.md",
  "task_file_blob_sha": "...",
  "expected_report": "reviews/worker_reports/example-01.md",
  "dependencies": [],
  "user_gate": {"required": false, "kind": null, "status": "none"},
  "review_gate": {"system_audit": "not_due", "taste_review": "not_applicable"},
  "attempt": {
    "number": 0,
    "attempt_id": null,
    "run_id": null,
    "base_sha": null,
    "branch": null,
    "lease_expires_at": null
  },
  "retry": {"count": 0, "max": 2, "last_failure_class": null},
  "evidence": {
    "report_blob_sha": null,
    "candidate_head_sha": null,
    "ci_runs": [],
    "deploy_run": null,
    "artifact_ids": []
  }
}
```

Global state additionally contains:

- `schema_version`;
- `state_revision`;
- `consumed_event_ids` or an event cursor;
- `slot_1` and `slot_2` lease summaries;
- review-checkpoint mirror refs, not duplicated policy;
- last reconciliation timestamp/run ID.

The existing `DIRECTOR_REVIEW_CHECKPOINTS.md` remains the review-policy source until a later explicit contract migration; orchestration state records only current gate execution/binding.

## 6. Safe lifecycle/state machine

Normal lifecycle:

`intake -> queued -> assigned -> running -> report_ready -> validation_pending -> director_review -> review_pending/user_gate(if required) -> accepted`

Alternative terminal/intermediate paths:

- `queued -> deferred`;
- `queued/assigned/running -> cancel_requested -> cancelled`;
- `running -> failed_transient -> queued` if retry budget allows;
- `running -> failed_permanent -> blocked`;
- `director_review -> needs_followup_fix -> queued` as a new revision/attempt;
- `director_review/review_pending -> user_gate -> queued/accepted/cancelled` after the user's Director message is durably recorded;
- any ambiguous/stale state -> `blocked_reconcile`, never guessed forward.

For IMPLEMENT, `accepted` means the exact required CI/review/deploy/user evidence for that task has passed. A worker saying `complete` is never sufficient by itself.

## 7. Priority, dependency, conflict and two-slot rules

### Eligibility

A task can be assigned only when:

1. `status == queued`;
2. every dependency is in the required accepted/complete state;
3. no unresolved user gate exists;
4. no mandatory pre-run review gate blocks it;
5. a logical slot is free;
6. its conflict keys do not conflict with any active lease;
7. task revision/blob SHA still matches the queued version.

### Priority

Sort eligible tasks by:

1. explicit user priority class;
2. infrastructure/user blocker severity;
3. dependency-unblocking value;
4. age/FIFO within equal class.

Do not let an LLM silently re-rank explicit user priority.

### Conflict keys

Use explicit semantic keys, not file-path overlap alone. Suggested initial families:

- `taste-write`;
- `ranking-write`;
- `taste-ranking-policy` (exclusive umbrella for material Taste/ranking changes);
- `frontend-feed`;
- `production-deploy`;
- `scheduler-runtime`;
- `provider-authority:<provider>`;
- `orchestration-control`.

Rules:

- two tasks sharing an exclusive conflict key cannot run simultaneously;
- two material Taste/ranking IMPLEMENT tasks never run together even if files differ;
- only one production deploy/merge gate at a time;
- a reviewer reads an immutable candidate SHA and cannot review a moving target;
- READ-ONLY RECON may coexist with unrelated IMPLEMENT work;
- a RECON depending on an unmerged candidate branch must bind to that exact branch SHA;
- the current manual Taste IMPLEMENT occupies one logical product slot until it completes or is explicitly migrated; automation must not treat both cloud slots as free while that work is active.

`max-parallel: 2` is a final mechanical cap, not the conflict scheduler itself.

## 8. Crash, retry, idempotency and stale-result rules

1. **Single state writer:** only serialized dispatcher updates `orchestration/state.json`.
2. **Immutable intake events:** event ID is processed once.
3. **Monotonic task revision:** reprioritize/cancel/scope change creates a new revision/event.
4. **Attempt identity:** report/result must match exact `task_id + revision + attempt_id`.
5. **Input binding:** accept only a report generated from the recorded task-file blob SHA and base/candidate SHA.
6. **Lease expiry:** crashed worker does not occupy a slot forever; reconciliation marks the attempt stale/failed after run evidence confirms it is no longer active.
7. **Retry budget:** default small cap (recommended 2 automatic retries) only for classified transient infrastructure/API failures.
8. **No automatic retry** for product-policy disagreement, credential denial, deterministic failing tests, reviewer policy concern, or real-device failure; those become fix/user/blocker states.
9. **Cancellation:** running task becomes `cancel_requested`; trusted controller cancels its workflow if possible, revokes the lease, and ignores any later stale report/PR from that attempt.
10. **Safe publish:** worker cannot write canonical state. Publisher rejects unauthorized file paths and stale task revisions.
11. **Safe merge:** candidate branch head SHA must still equal the reviewed/tested SHA.
12. **Fail closed:** unknown CI/deploy/review evidence means not accepted.

## 9. CI, deploy and artifact evidence

For each task define required validations by category, not by asking the worker to infer them.

The evaluator/controller must bind evidence to the exact candidate/merge SHA:

- required check/workflow names;
- workflow run IDs and URLs;
- result/conclusion;
- exact tested `head_sha`/merge SHA;
- deployment run ID/status if required;
- Pages/deploy artifact ID where applicable;
- real-device verification record if task requires it.

Never accept `latest successful deploy` without verifying it contains the relevant merge SHA.

For product IMPLEMENT:

1. worker creates candidate PR branch;
2. CI runs on candidate SHA;
3. mandatory Taste Review (if applicable) runs against that same frozen SHA;
4. Director evaluator decides whether merge is allowed;
5. merge occurs only after gates pass;
6. deploy observation waits for the exact merge SHA;
7. task becomes accepted only after required deploy evidence and any user real-device gate are complete.

## 10. Automatic System Audit / Taste Review gates

### System Auditor

GitHub deterministically evaluates current `DIRECTOR_REVIEW_CHECKPOINTS.md` triggers.

When due:

- enqueue a read-only `SYSTEM_AUDIT` task automatically;
- bind it to a precise accepted-main SHA/scope;
- run with Codex Action read-only permissions using `SYSTEM_AUDITOR_ROLE.md`;
- save its durable audit report;
- Director evaluator reads the report;
- trusted controller updates/reset checkpoint state only after the report is valid and accepted.

If audit discovers a concrete regression already inside an approved technical contract, Director may enqueue a bounded fix automatically in later phases. If it proposes new policy/authority, raise a user/product gate.

### Taste Reviewer

Before acceptance of any material Taste eligibility/weights/order/exclusion/wishlist-vs-Taste semantic change:

- freeze candidate SHA;
- enqueue read-only Taste Review automatically;
- reviewer uses `TASTE_REVIEWER_ROLE.md`, current taste profile and exact candidate diff/output;
- report is advisory evidence;
- reviewer output **must not directly modify ranking/Taste policy or create a new product rule**.

Automatic safe responses are limited to:

- block acceptance on an objective failed invariant;
- return the same task for a bounded fix that is already inside approved scope;
- request more evidence/recon.

Any recommendation requiring a new weight, threshold, exclusion rule, role semantics, provider authority, or other product-policy choice becomes `user_gate: product_policy`.

## 11. Notification / Android user-gate model

The durable source is a structured `user_gate` object in GitHub state. A notification is transport only.

Allowed notification kinds:

- `real_device_check`;
- `product_policy_decision`;
- `credential_or_access_boundary`;
- `external_blocker`;
- `no_safe_automatic_decision`.

Do **not** notify for ordinary worker start/finish, green CI, successful automatic review, normal retry, or next-task assignment.

### Baseline immediate Android transport

Use a GitHub-native notification surface only when a real gate is created, e.g. a dedicated labeled GitHub issue or task PR mention containing:

- task ID;
- one concise question/action;
- exact report/PR/run refs;
- no secrets.

GitHub Mobile can deliver that notification without a PC. The issue/PR is not canonical state; resolving the gate still happens by the user telling the Director in natural language, after which the Director writes a `user_gate_resolved` intake event.

### Preferred ChatGPT-native push later

OpenAI Scheduled Tasks can send mobile push notifications. Work also supports webhook-based tasks for supported GitHub PR activity. Therefore a later phase can encode user-gate creation as supported PR activity and have one Work task notify the Android ChatGPT app.

Do not assume arbitrary workflow/issue events can wake the Director chat. If the desired gate event cannot be represented by a documented supported Work trigger, keep GitHub Mobile as the reliable transport or use a scheduled conditional Work task only after verifying connected-GitHub access in that task surface.

## 12. Secret/security model

Rules:

- never place API keys, session cookies, tokens, credential values or secret-derived plaintext in `WORKER_TASK_*`, `orchestration/*`, reports, PR comments or chat;
- `OPENAI_API_KEY` belongs in GitHub Actions secret storage;
- Phase 1 shadow observer requires no OpenAI secret;
- agent job gets only the OpenAI credential required by `openai/codex-action`, never unrelated Steam/provider secrets;
- use `actions/checkout` with `persist-credentials: false` in agent jobs;
- give Codex agent job `contents: read` and no merge/write authority;
- keep GitHub write token in a separate trusted publish/controller job without the OpenAI secret;
- use minimal workflow permissions;
- pin third-party/actions dependencies to immutable commit SHAs after verification rather than floating tags in production orchestration;
- validate/report-sanitize agent output before publishing;
- do not run Codex on untrusted fork/user prompts with secrets available;
- provider credentials stay in their existing approved secret boundary and are exposed only to deterministic helper code or narrowly scoped tools if a future task explicitly authorizes that access.

## 13. GitHub Issues/Projects verdict

**GitHub Projects are not needed for the initial control plane.**

Repository files + Actions are sufficient and better aligned with the current project rule that GitHub files/contracts are canonical.

Issues/PRs are useful as:

- user-notification surfaces;
- candidate-code review surfaces;
- links to CI/deploy evidence.

They should not become a second task database.

## 14. Staged rollout

### Phase 0 — current system continues

- Current Chat 1 Taste IMPLEMENT continues untouched.
- Existing manual Director/worker protocol remains valid.
- No cloud worker is allowed to take over a currently running manual task.

### Phase 1 — shadow observer

Goal: prove state/priority/conflict logic with zero automatic product dispatch.

Automation may:

- read Director board/task files/review checkpoints;
- consume a shadow machine state/intake mirror;
- compute which tasks *would* be eligible;
- compute which two slots *would* be selected;
- report conflicts/dependencies/gates;
- publish only a workflow artifact or shadow report.

Automation may **not**:

- create worker dispatches;
- modify product tasks;
- merge PRs;
- alter current worker assignments;
- require `OPENAI_API_KEY`.

Exit criteria: repeated shadow decisions match Director decisions and never select the active Taste work/conflicting task incorrectly.

### Phase 2 — automatic RECON/AUDIT

Add:

- `openai/codex-action` worker workflow;
- `OPENAI_API_KEY` secret;
- two logical cloud slots with global `max-parallel: 2`;
- automatic read-only RECON/AUDIT dispatch;
- trusted report publisher;
- finished-run reconciliation;
- read-only Director evaluator;
- automatic System Audit / Taste Review dispatch when due.

Keep IMPLEMENT manual.

Exit criteria: bounded RECON/AUDIT tasks can enter queue from Director, run, save reports, be reviewed/advanced and free slots without user relaying messages.

### Phase 3 — bounded IMPLEMENT

Whitelist only pre-defined low-risk classes, for example:

- tests/regression guards;
- documentation/contracts that do not change product policy;
- deterministic tooling/refactors with unchanged behavior;
- narrowly scoped implementation already authorized by a completed recon/contract and with explicit allowed paths/tests.

Use branch/PR isolation, CI, exact-SHA review and trusted publisher/merger.

Still gated/manual:

- material Taste/ranking policy;
- new provider/data authority;
- credential/security boundary;
- deployment/production authority changes;
- new monetization/commercial policy;
- real-device acceptance when required;
- anything the evaluator cannot classify safely.

### Phase 4 — mature autopilot with user gates

User normally does only:

- natural-language task/prioritization/cancel/defer messages to Director;
- explicit user-gate decisions/checks when notified.

GitHub + OpenAI automatically handle intake persistence, safe scheduling, two worker slots, reports, CI/deploy observation, audit/review, retries, next-task assignment and normal closure.

Even Phase 4 is not unrestricted autonomy: product policy, credentials/access, external blockers and required real-world/user checks remain gates.

## 15. What is fully automatic vs what requires OpenAI/ChatGPT

### GitHub-only deterministic automation

Can be fully automatic without an LLM:

- intake event ingestion after Director has committed it;
- queue persistence;
- priority ordering from explicit fields;
- dependency checks;
- conflict-key checks;
- two-slot leases;
- run dispatch/cancel/reconciliation;
- retry counters and lease expiry;
- CI/workflow/deploy/status observation;
- exact SHA/run/artifact binding;
- review-trigger calculation from explicit project rules;
- state transition validation;
- stale report rejection;
- user-gate record creation;
- next eligible task selection after an approved decision.

### OpenAI API / Codex required

Required for semantic/coding work:

- RECON/AUDIT reasoning;
- code generation/modification;
- System Auditor and Taste Reviewer reasoning;
- Director evaluation of non-deterministic worker findings;
- classification of whether a report implies same-scope fix vs policy/user gate.

Recommended runtime: Codex Action invoked by GitHub Actions. This uses OpenAI API infrastructure but does not require a desktop Codex UI or persistent worker conversation.

### ChatGPT product control plane required only for the desired UX

- natural-language Director conversation on Android;
- translating user intent/decisions into GitHub intake events using the authorized repository connection;
- optional ChatGPT-native push notification through Scheduled/Work tasks.

The background queue/worker system itself should not depend on the Director chat staying open.

## 16. One-time user setup

### Phase 1

**None required** beyond the already authorized GitHub access used by the Director. The first shadow implementation should not require OpenAI API credentials.

### Before Phase 2

One credential setup is expected:

1. create/use an OpenAI API key suitable for Codex Action;
2. store it directly as a GitHub Actions secret such as `OPENAI_API_KEY` through GitHub's secret UI/approved secret-management path;
3. never paste the value into Director chat, worker task, report, issue or Git.

If repository policy prevents workflow write permissions needed by the trusted publisher, that becomes a one-time GitHub permission gate.

Optional Android setup:

- enable GitHub Mobile notifications for immediate gate notifications;
- later enable ChatGPT Scheduled Task push notifications if ChatGPT-native gate alerts are desired.

No always-on PC, local daemon, local cron, self-hosted runner or desktop Codex session is required.

## 17. Smallest first IMPLEMENT to start immediately

**Task recommendation: `director-orchestration-shadow-observer-implement-01`**.

Scope must be deliberately small and coexist with active product work.

Implement only:

1. `config/director_orchestration_contract.json`
   - declares Phase 1 shadow-only ownership;
   - max slots = 2;
   - status enum;
   - conflict/dependency semantics;
   - single state-writer rule;
   - explicitly states it does not replace current Director board/protocol yet.

2. `orchestration/state.json`
   - initial shadow state;
   - records the current manually occupied Taste slot as external/manual occupancy so automation cannot treat both slots as free;
   - contains no secrets.

3. `scripts/director_orchestration_shadow.py`
   - validates schema/invariants;
   - computes `would_assign` decisions only;
   - proves no dependency/conflict violation and no third worker;
   - makes no repository/product mutation.

4. `.github/workflows/director-orchestration-shadow.yml`
   - `workflow_dispatch` plus a low-frequency/safe reconciliation trigger;
   - serialized `concurrency` group;
   - runs deterministic validator/planner;
   - uploads `shadow-plan.json` artifact;
   - **does not** invoke OpenAI/Codex, dispatch workers, commit state or modify product files.

5. focused deterministic tests for:
   - max two slots;
   - current Taste slot occupancy;
   - conflicting Taste/ranking tasks rejected in parallel;
   - dependencies respected;
   - priority ordering deterministic;
   - stale/cancelled task not selected.

Why this is the correct first implementation:

- zero API key requirement;
- zero change to active Taste IMPLEMENT;
- zero automatic product write;
- validates the hardest safety invariant (scheduler/conflict/state correctness) before adding LLM execution;
- can be developed while ordinary product backlog continues;
- gives a clean Phase 2 attachment point for Codex Action workers.

Do **not** make the first implementation an autonomous worker dispatcher. First prove the shadow scheduler.

## 18. Recommended next step

Create one bounded IMPLEMENT task only:

`director-orchestration-shadow-observer-implement-01`

It should implement the Phase 1 files/workflow/tests described above and nothing from Phase 2.

## 19. Changes

Report only:

`reviews/worker_reports/autonomous-director-orchestration-recon-01.md`

No product pipeline, worker assignment, Taste implementation, current task, review checkpoint, secret, workflow or runtime behavior was changed by this recon.

## 20. Unresolved / gates

No blocker prevents Phase 1.

Before Phase 2, the project will need the `OPENAI_API_KEY` secret and a bounded security review of the exact Codex Action workflow/publisher permissions. This is an implementation prerequisite, not a reason to delay the shadow observer.

ChatGPT-native immediate push should be treated as a later notification enhancement unless the chosen user-gate representation is verified to map to a documented supported Work GitHub trigger. GitHub-native Android notification remains the safe baseline.

## 21. Recommended next step

`director-orchestration-shadow-observer-implement-01` — Phase 1 only, no Codex dispatch, no API secret, no product-task changes.
