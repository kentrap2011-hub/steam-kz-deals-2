# WORKER TASK — Taste Zero-Cost Runtime Migration Recon 01

## Task ID
`taste-zero-cost-runtime-migration-recon-01`

## Mode
`READ-ONLY / RECON`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Required report
`reviews/worker_reports/taste-zero-cost-runtime-migration-recon-01.md`

## Context
This is the direct continuation of Taste semantic runtime recovery.

Durable prior report:
`reviews/worker_reports/taste-semantic-runtime-recovery-recon-01.md`

Recovered historical canonical producer:
- name: `Taste Semantic Producer`
- historical task/jawbone ID: `0a51664a-af13-5b98-8c25-d589f0d247c9`
- historical owner: ChatGPT scheduled-task service
- canonical semantic result contract: `TASTE-SEMANTIC-RESULT-V5`
- GitHub remains canonical owner of queue/scope/retry/completeness/validation/persistence/final ranking.

New owner-scope user evidence on 2026-09-06:
- current ChatGPT Tasks view `Активно` contains no user-created active task;
- current `Приостановленные` view does not contain `Taste Semantic Producer`;
- therefore the historical producer is absent from the current runnable scheduler surface and must not be assumed recoverable by simple re-enable.

Provider evidence:
- `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md` closed `blocked` before successful Copilot semantic inference;
- therefore Copilot CLI is NOT a proven zero-extra-cost production replacement;
- absence of `reviews/worker_reports/epic-ru-availability-source-probe-02.md` is intentional for that blocked pilot and must not be fabricated.

User policy:
- no additional paid inference/API cost;
- paid OpenAI API fallback is forbidden;
- no duplicate semantic producer or second queue.

## Goal
Determine the safest currently realistic **zero-extra-cost canonical migration/recovery path** for exactly one Taste semantic producer, without implementing it.

The answer must preserve the existing GitHub control plane and `TASTE-SEMANTIC-RESULT-V5` contract unless a separately authorized contract migration is strictly necessary.

## Required investigation
1. Reconcile all current durable Taste/runtime/provider evidence from repository truth.
2. Treat the historical ChatGPT producer as absent from the current runnable scheduler surface; do not spend the task trying to prove a simple disabled-state recovery already contradicted by owner evidence.
3. Identify only realistic zero-extra-cost runtime/provider routes available under the user's current product/account/tool constraints.
4. Explicitly evaluate whether a new canonical ChatGPT scheduled task can safely fulfill the existing semantic-producer role without separately billed API inference, including any hard product/tool limitations that would prevent durable GitHub queue/result integration.
5. Re-evaluate Copilot only from durable evidence; do not promote the blocked Rev02 pilot into a successful provider.
6. If another built-in or zero-cost provider/runtime is a candidate, distinguish:
   - proven available now;
   - requires a bounded pilot;
   - unavailable/blocked.
7. Preserve singleton guarantees. Specify how migration would prevent the old historical producer and any replacement from running in parallel if the old task later reappears.
8. Preserve GitHub-owned queue, validation, persistence and current V5 result contract.
9. Produce exactly one recommended bounded next action.

## Forbidden
- No IMPLEMENT.
- Do not create, enable, disable or clone any scheduler/task.
- Do not execute semantic backlog rows.
- Do not manually process the current semantic queue.
- Do not create a second semantic queue or producer.
- Do not use or recommend paid OpenAI API fallback as the project path.
- Do not weaken validation, fail-closed behavior or singleton protections.
- Do not modify ranking/product logic.
- Do not claim any provider is production-ready without durable successful evidence.
- Do not start another major task.

## Required report structure
The report must include:
- evidence consumed;
- current runtime/provider classification;
- candidate zero-extra-cost routes and why each is viable/not viable;
- exact singleton/duplicate-prevention boundary;
- exact GitHub queue/result contract that remains canonical;
- one final classification, exactly one of:
  - `ready_for_bounded_implement`
  - `needs_user_gate`
  - `blocked_external`
- exactly one next bounded action;
- any user action required, stated minimally and without asking for secrets in chat.

Do not implement the recommended action in this task.
