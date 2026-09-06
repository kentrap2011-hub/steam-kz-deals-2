# Taste Zero-Cost Runtime Migration Recon 01

## Task

- Task ID: `taste-zero-cost-runtime-migration-recon-01`
- Mode: `READ-ONLY / RECON`
- Priority: `VERY_HIGH_USER_PRIORITY`
- Scope: restore/migrate exactly one Taste semantic producer at zero additional inference/API cost without implementing it.
- Implementation performed: **none**.
- Scheduler/task created, enabled, disabled, cloned, or modified: **no**.
- Semantic backlog rows processed: **0**.
- Queue/result/ranking/product logic modified: **no**.
- Paid OpenAI API used or proposed as project fallback: **no**.

## Evidence consumed

### Canonical repository truth

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `WORKER_TASK_TASTE_ZERO_COST_RUNTIME_MIGRATION_RECON_01.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `config/taste_result_contract.json`
- `data/production/pre_ai/chatgpt_payload.json`
- `data/cache/taste_ingest_receipts/latest_runtime_status.json`
- `.github/workflows/ingest-taste-batch.yml`
- `scripts/process_taste_inbox.py`
- `scripts/ingest_taste_results.py`
- `reviews/worker_reports/taste-semantic-runtime-recovery-recon-01.md`
- `reviews/worker_reports/semantic-runtime-task-health-recon-01.md`
- `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md`
- `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md`

### New owner/account evidence accepted by this task

The historical ChatGPT task `Taste Semantic Producer` (`0a51664a-af13-5b98-8c25-d589f0d247c9`) is absent from the user's current runnable Scheduled/Tasks surface: it is neither a current user-created active task nor present among paused tasks. This task therefore treats the historical producer as unavailable for simple re-enable and does not request more enabled/disabled evidence.

### Current product/provider evidence

Current official product documentation checked on 2026-09-06:

- OpenAI, **Scheduled tasks in ChatGPT**: regular scheduled tasks can be recurring; plan usage limits apply; scheduled tasks can use supported connected apps including GitHub; connected apps may read or take actions according to granted permissions, and an approval-requiring action can pause a task. `https://help.openai.com/en/articles/10291617`
- OpenAI, **Connecting GitHub to ChatGPT**: ChatGPT can access authorized GitHub repositories, and scheduled tasks may use GitHub. `https://help.openai.com/en/articles/11145903`
- GitHub, **About using Copilot CLI in GitHub Actions**: with `GITHUB_TOKEN` in a personally owned repository, AI credits are billed to the repository owner's Copilot seat. `https://docs.github.com/en/copilot/concepts/agents/copilot-cli/copilot-cli-in-github-actions`
- GitHub, **GitHub Models**: GitHub Models was fully retired on 2026-07-30; its inference API is no longer available. `https://docs.github.com/en/github-models`
- GitHub Actions documentation: standard GitHub-hosted runners are free for public repositories. This establishes only compute availability, not a proven semantic model/provider. `https://docs.github.com/en/billing/concepts/product-billing/github-actions`

Live current-account/tool observation during this recon:

- the ChatGPT GitHub app is connected;
- its app-specific permission is `Allow all actions`, so the current permission layer does not require an approval prompt for ordinary supported GitHub reads/writes;
- the repository is currently accessible through that connection and is public;
- no task was created to test this capability in scheduled execution because this task is recon-only.

## Verified facts

### 1. The GitHub control plane and semantic contract remain canonical

`config/execution_ownership_contract.json` assigns GitHub all control-plane responsibility: exact scope, queue construction, retry/unresolved state, completeness, validation, persistence, checkpoint/merge behavior, downstream rebuild, and fail-closed behavior. A scheduled ChatGPT task is only the constrained semantic data plane.

`config/daily_execution_contract.json` already authorizes a single `ChatGPT scheduled task` as the external semantic worker in the existing nightly production stage. Replacing the missing scheduler instance does not require inventing a second recurring stage.

`config/taste_result_contract.json` remains canonical as `TASTE-SEMANTIC-RESULT-V5`. Its ownership split remains:

- semantic evaluation -> scheduled ChatGPT Taste worker;
- queue scope/bindings -> GitHub;
- validation/persistence -> GitHub;
- final weight application -> GitHub final ranking producer.

No semantic V5 migration is needed for the preferred recovery route.

### 2. Current production state is still blocked on semantic runtime

`data/production/pre_ai/chatgpt_payload.json` currently records:

- `ai_queue_count = 701`;
- `resolved_semantic_count = 0`;
- `unresolved_semantic_count = 701`;
- `sufficiently_complete_for_publication = false`;
- runtime owner expected by contract = scheduled ChatGPT production task;
- no accepted progress for the current source scope.

The latest durable accepted semantic execution remains 2026-09-01 21:03:08 UTC, with 11 accepted results and queue movement 37 -> 26. None of the current 701 rows were processed by this recon.

### 3. Copilot Rev02 is not a production replacement

`reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md` closed `blocked` before any Copilot semantic inference. `copilot_invocation_count = 0`; no semantic result was produced; the representative Epic report was correctly not published.

The adapter startup defect was fixed afterward, but the pilot was not rerun. Therefore current included Copilot quota, zero-overage state, semantic execution, output quality, and V5 compatibility remain unproven. Current GitHub documentation also confirms that a personal-repository `GITHUB_TOKEN` path consumes the owner's Copilot seat/AI credits rather than creating a provider-independent free inference path.

### 4. The existing GitHub ingest remains the only result path

The canonical producer input/output path remains:

1. GitHub builds `data/production/pre_ai/chatgpt_payload.json` and `data/production/pre_ai/chatgpt_taste_queue.jsonl` with current bindings.
2. The semantic producer evaluates only GitHub-prepared work.
3. It submits structured batches to the existing `data/ai_inbox/taste/*.json` interface.
4. `.github/workflows/ingest-taste-batch.yml` runs `scripts/process_taste_inbox.py` and `scripts/ingest_taste_results.py`.
5. GitHub validates exact current bindings/key/appid/fingerprint/context, rejects stale or invalid material, persists accepted state, rebuilds the queue/consumers, writes the receipt, and owns completeness.

No second queue, alternate canonical store, or direct cache writer is needed or permitted.

## Current runtime/provider classification

### Preferred route — one new regular ChatGPT Scheduled Task using the existing GitHub app

This is the only currently realistic zero-extra-cost route that is directly compatible with the canonical architecture.

Why it is viable now:

- the historical scheduler instance is absent from the current runnable surface, so recovery is now a migration to one replacement instance rather than a re-enable attempt;
- regular ChatGPT Scheduled Tasks are currently supported by the product;
- current OpenAI documentation explicitly states that scheduled tasks can use connected GitHub and can take actions according to app permissions;
- the current account already has the GitHub app connected with `Allow all actions` at the app-permission layer;
- the existing repository interface needs only repository reads plus creation of a bounded JSON submission under `data/ai_inbox/taste/`; GitHub continues to do all validation/persistence;
- this path uses ChatGPT plan task/model usage, not separately billed OpenAI API inference and does not require `OPENAI_API_KEY`;
- the same provider family previously produced accepted Taste results, so this is a runtime-instance migration rather than an untested semantic-provider replacement.

Hard limitation / remaining proof gap:

- product documentation proves the capability class, but this recon did not create a task, so a scheduled execution has not yet proved that this exact GitHub write action completes unattended without a surface-specific approval/safety pause;
- the exact sustainable throughput under the current ChatGPT plan/model task limits is not yet measured, so the 701-row scope must not be assumed drainable until a bounded canary succeeds;
- GitHub event-triggered Work tasks are not the canonical choice here: current GitHub webhook triggers are tied to supported pull-request activity rather than arbitrary queue-file changes. The replacement should be the existing architecture's regular time-scheduled semantic stage, not a second event-triggered queue architecture.

Therefore the route is sufficiently established to enter one bounded implementation/canary, but it is **not yet production-proven until that canary produces an accepted GitHub receipt**.

### Copilot CLI in GitHub Actions

Candidate only. The repository already has bounded orchestration work for it, but Rev02 never reached semantic inference and never proved usable included quota. The corrected adapter could support a future fresh pilot, but promoting it now would violate the explicit requirement not to treat an unproven provider as production-ready. It is not the selected migration path.

### GitHub Models

Unavailable. GitHub Models was fully retired on 2026-07-30, including its inference API, so it cannot be a current runtime option.

### Local open-source model on standard public GitHub Actions runners

The runner compute itself can be zero-extra-cost for this public repository, but no durable project evidence proves a local model/harness that satisfies the current Taste semantic quality, grounded-negative requirements, normalized factors, and V5 output contract. Building and validating such a provider would be a materially larger provider migration, not the safest recovery of the current production incident. It is not selected.

### Other external free-tier inference providers

No other provider is currently connected and durably proven in this project under the user's account, quota, terms, semantic-quality, and no-overage constraints. A nominal free tier is not sufficient evidence for a production producer, so none is promoted by this recon.

## Exact singleton / duplicate-prevention boundary

The owner evidence is enough to permit migration away from the missing historical scheduler, but a future unexpected reappearance of the historical task still needs a fail-closed boundary.

The existing ingest already rejects stale bindings, duplicate keys inside a batch, keys not in the current synchronized queue, appid/fingerprint/context mismatches, and invalid V5 shapes. That protects semantic state, but the inspected `scripts/ingest_taste_results.py` transport envelope currently has no required producer-instance identity. Therefore scheduler-surface absence alone is not a complete long-term duplicate-producer fence.

The bounded migration should add **one GitHub-owned accepted-producer generation/instance fence to the existing submission transport envelope**, without changing `TASTE-SEMANTIC-RESULT-V5` result semantics and without creating a new queue:

- GitHub has exactly one canonical active producer instance/generation at a time;
- the replacement Scheduled Task is configured with its fixed producer instance/generation identifier and must echo it in the top-level existing inbox submission envelope;
- GitHub ingest validates that identifier before accepting any `results[]` rows;
- a submission from the historical task, including a legacy submission with no active producer identifier, fails closed before semantic persistence;
- the V5 `results[]`, queue identity, current bindings, inbox directory, validation, persistence, retry/completeness, and downstream logic remain otherwise unchanged.

This is the exact singleton boundary: scheduler execution is external, but **only one producer generation is allowed to become an accepted production producer**. If the historical task unexpectedly becomes visible/runnable later, it is non-canonical and its legacy output remains rejected until it is explicitly decommissioned; it must never be accepted in parallel with the replacement.

## Architecture preflight for the recommended migration

1. Responsibility changing: only the missing scheduled semantic data-plane **instance** is replaced. GitHub ownership does not move.
2. Canonical authorization: `config/execution_ownership_contract.json`, `config/daily_execution_contract.json`, and `config/taste_result_contract.json` already authorize one scheduled ChatGPT semantic worker and the existing GitHub queue/result interface.
3. Control-plane transfer: none. Scope, queue, retry, completeness, validation, persistence, and ranking remain GitHub-owned.
4. New recurring stage/queue/retry manager: none. The replacement occupies the already canonical scheduled semantic stage and uses the existing queue/inbox. The producer-generation fence is an acceptance guard, not a second scheduler or queue.

Architecture preflight therefore permits a bounded migration implementation after this recon.

## Validation

- Historical producer treated as absent per the new user evidence; no further enabled/disabled proof requested.
- Current 701-row degraded state verified from canonical payload.
- V5 ownership and existing queue/result path verified from canonical contracts and ingest code.
- Copilot Rev02 verified as pre-inference blocked; no provider readiness inferred from the later adapter fix.
- Current OpenAI Scheduled Tasks + GitHub app capability checked against current official product documentation.
- Current ChatGPT GitHub app connection/permission checked live; no permission change performed.
- GitHub Models retirement checked against current official GitHub documentation.
- No scheduler/task, queue, workflow, semantic result, cache, ranking rule, or product rule was modified.

## Unresolved

- One live bounded Scheduled Task canary is still required to prove unattended GitHub write + semantic result + canonical ingest on the current account/task surface.
- Sustainable recurring throughput for the current 701-row scope is not yet proven and must not be extrapolated from product documentation alone.
- Copilot's corrected quota preflight and semantic inference remain untested, but Copilot is not required for the preferred route.

## User action required

None before the bounded migration canary. No API key, provider secret, billing enablement, or additional owner-state screenshot is required.

## Changes

Only this required recon report was added. No runtime implementation was performed.

## Efficiency / reusable lesson

`PROJECT_ROUTES.md#Taste V3 / normalized factors` now contains stale recovery wording that still points toward inspecting the historical scheduled worker. Because this task is read-only, the route was not edited; a future authorized bounded maintenance change should update that route to reference the durable migration report and the now-confirmed missing historical task.

## Final classification

`ready_for_bounded_implement`

## Recommended next step / next bounded action

Perform one bounded migration canary in the **same replacement producer instance**: add the GitHub-owned active-producer instance/generation check to the existing Taste inbox transport envelope, create exactly one regular ChatGPT Scheduled Task bound to that instance and the existing connected GitHub app, hard-limit its first execution to one current V5 queue row, and count the canary as successful only if the task writes one submission through `data/ai_inbox/taste/*.json` and the unchanged canonical ingest accepts it into a fresh receipt/queue delta; do not widen recurring throughput until that proof passes.
