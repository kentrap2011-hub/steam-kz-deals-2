# WORKER TASK — AUTONOMOUS DIRECTOR ORCHESTRATION RECON 01

Task ID: `autonomous-director-orchestration-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/autonomous-director-orchestration-recon-01.md`
Priority: `VERY_HIGH_INFRASTRUCTURE_PRIORITY`

## User goal

The user works primarily from an Android phone and wants to stop manually relaying work between Director and worker chats.

Desired end state:
- user adds/changes/cancels tasks only by messaging the Director in natural language from the phone;
- GitHub stores durable task/state truth;
- two worker slots are filled automatically when safe;
- workers detect/execute assigned bounded tasks without the user sending prompts manually;
- Director automatically notices durable reports/CI/deploy outcomes, closes or advances tasks, and selects the next safe task;
- required System Audit / Taste Review checkpoints are triggered automatically;
- user receives a notification only when a real user action/decision is needed (real-device check, product-policy choice, credential/access decision, unresolved blocker);
- no always-on home PC is required;
- cloud-first execution is strongly preferred;
- maximum two parallel worker slots and current conflict rules remain.

## Current architecture to preserve

Read only the compact operational sources first:
- `DIRECTOR_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `DIRECTOR_REVIEW_CHECKPOINTS.md`
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- representative current `WORKER_TASK_*.md` files and reports only as needed.

The current manual protocol already has useful durable primitives:
- task files;
- worker reports;
- Director task board;
- review checkpoints;
- GitHub Actions/CI/deploy;
- two-worker parallelism and conflict rules.

Do not redesign the product pipeline itself.

## Goal of this recon

Produce the smallest viable **cloud-first autonomous orchestration design** that can be introduced gradually while existing product work continues.

The design must explicitly separate:
1. task intake from the user's Director chat;
2. durable machine-readable task queue/state;
3. worker dispatch/execution;
4. report/CI/deploy observation;
5. Director decision loop;
6. review/audit gates;
7. user-notification gates;
8. failure/retry/stop behavior.

## Required questions

1. What current ChatGPT/OpenAI/GitHub mechanisms available to this project can realistically provide:
   - background/cloud task execution;
   - GitHub event or scheduled observation;
   - Codex/cloud coding work;
   - push/user notification;
   without a permanently running user PC?
2. Which parts can be automated entirely from GitHub state and which still require a ChatGPT/OpenAI control-plane capability outside the repository?
3. Can the current ordinary worker-chat pattern itself be automated, or must those chats be replaced by cloud agents/jobs? State this clearly.
4. Define the smallest machine-readable state model. At minimum consider:
   - task_id;
   - mode;
   - priority;
   - domain/conflict_key;
   - status;
   - assigned_slot;
   - task_file;
   - expected_report;
   - dependencies;
   - user_gate;
   - review_gate;
   - retry/failure state.
5. Define exact safe lifecycle, e.g. conceptually:
   `queued -> assigned -> running -> report_ready -> director_review -> review_gate/user_gate -> accepted/blocked -> next assignment`.
6. Define conflict/parallelism rules so two agents cannot simultaneously perform incompatible Taste/ranking/frontend/deploy work.
7. Define how the Director detects a finished worker without user message.
8. Define how the Director knows CI/deploy succeeded and how exact deployed artifact evidence is attached where needed.
9. Define how mandatory `SYSTEM AUDITOR` / `TASTE REVIEWER` gates become automatic scheduled/conditional steps without auto-converting reviewer advice into product policy.
10. Define notification policy: only real user decisions/checks should surface to Android.
11. Define secret handling: no API key/session cookie in task files/reports/chat; approved secrets remain in proper secret stores.
12. Define crash/retry/idempotency so duplicate runs cannot double-assign tasks or accept a stale report.
13. Determine whether GitHub Issues/Projects are needed or whether repository files are sufficient. Prefer the smallest reliable control plane.
14. Determine what must remain manually approved initially.
15. Produce a staged rollout that can start **now without waiting for existing product backlog to finish**.

## Required rollout phases

The recommendation must include at least these safety phases:

### Phase 0 — current system continues
Existing Chat 1 product IMPLEMENT may keep running. Automation work must not interrupt it.

### Phase 1 — shadow observer
Automation reads GitHub task/report/checkpoint state and proposes what it would do, but does not dispatch/change product tasks automatically.

### Phase 2 — autonomous RECON/AUDIT dispatch
Allow safe READ-ONLY / RECON and AUDIT work to be dispatched/advanced automatically.

### Phase 3 — bounded IMPLEMENT with approval gates
Allow only predefined low-risk/bounded IMPLEMENT categories automatically; material Taste/ranking, credential/security, new external-provider authority, and user-visible acceptance remain gated as defined by project rules.

### Phase 4 — mature autopilot
User interacts only with the Director chat and receives notifications only at explicit user gates.

Do not recommend jumping directly to Phase 4.

## Phone-first requirement

The user must not need:
- desktop Codex UI;
- an always-on laptop/desktop;
- local cron/daemon;
- manual GitHub editing;
- manual creation/deletion of worker chats as the steady-state workflow.

A one-time setup step on desktop is acceptable only if absolutely unavoidable; identify it explicitly and minimize it.

## Boundaries

READ-ONLY / RECON only.

Do NOT:
- implement orchestration code yet;
- change current product task assignments;
- stop the active Taste IMPLEMENT;
- modify product pipelines;
- create a third active product worker;
- provision or expose secrets;
- assume unsupported OpenAI product capabilities without verifying current authoritative documentation;
- depend on a permanently running user PC.

If fresh OpenAI capability details are needed, use authoritative OpenAI documentation only and cite exact refs in the report.

## Done when

Save:
`reviews/worker_reports/autonomous-director-orchestration-recon-01.md`

Include:
1. Status
2. Feasibility verdict
3. What can/cannot be automated with ordinary chats
4. Recommended cloud-first architecture
5. Machine-readable state model
6. Dispatch/finish/review state machine
7. Conflict/idempotency rules
8. Notification/user-gate model
9. Secret/security model
10. Exact current OpenAI/GitHub mechanisms and limits
11. Staged rollout Phase 1-4
12. One smallest bounded IMPLEMENT task to start migration
13. Any one-time setup required from the user
14. Exact refs

Status exactly one:
- `complete`
- `blocked`
- `needs_user_decision`
