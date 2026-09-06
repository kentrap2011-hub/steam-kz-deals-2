# Taste Semantic Runtime Recovery Recon 01

- Mode: `READ-ONLY / RECON`
- Priority: `VERY_HIGH_USER_PRIORITY`
- Scope: Taste semantic production runtime only
- Worker task: `WORKER_TASK_TASTE_SEMANTIC_RUNTIME_RECOVERY_RECON_01.md`
- Implementation performed: **none**
- New scheduler/task created: **no**
- New/parallel queue created: **no**
- Semantic rows manually processed: **0**
- Paid OpenAI API fallback used: **no**
- Current classification: **ambiguous scheduler ownership/state; canonical task existence is historically proven but current enabled/disabled/deleted state is not**
- Required next step: **`needs_user_evidence`**

## Executive finding

The repository contains sufficient durable evidence to recover the identity and production contract of the canonical Taste semantic producer, but it does **not** contain sufficient evidence to prove the producer's current scheduler-platform state.

The canonical producer is the historical scheduled ChatGPT task:

- name: **`Taste Semantic Producer`**
- task / `jawbone_id`: **`0a51664a-af13-5b98-8c25-d589f0d247c9`**
- runtime owner: ChatGPT scheduled-task service, external to GitHub Actions
- historical cadence: daily; older durable recon evidence places the run around `05:00 UTC`, but the exact current cadence/next-run state is not durably exported and must not be guessed

The producer was not merely theoretical. Durable repository receipts prove accepted semantic production as recently as **2026-09-01 21:03 UTC**, when **11 results** were accepted and the semantic queue moved **37 -> 26**. This proves that the canonical producer existed and was functioning recently; it does **not** prove whether it is enabled, disabled, inaccessible, owner-scoped elsewhere, or deleted now.

The repository's runtime heartbeat/progress artifact intentionally does not serve as a mirror of scheduler-platform `enabled`, `cadence`, or `next_run` state. Therefore an absent current heartbeat cannot be promoted into proof that the scheduled task was deleted.

The current scheduler surface available to this recon did not yield a usable record for the exact historical task. That observation is compatible with more than one state:

1. the task exists but is disabled;
2. the task exists but is visible only in another owner/account/workspace scope;
3. the task was deleted/lost;
4. the task exists and is enabled but is outside the visibility of this session.

Because these states have different safe remediations, replacement creation is forbidden until the ambiguity is resolved.

## Evidence inspected

Canonical control/context files inspected:

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `USER_TASTE_PROFILE.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `WORKER_TASK_TASTE_SEMANTIC_RUNTIME_RECOVERY_RECON_01.md`

Relevant durable runtime/acceptance evidence inspected:

- `reviews/worker_reports/taste-steps-1-3-production-materialization-acceptance-01.md`
- `reviews/worker_reports/semantic-runtime-task-health-recon-01.md`
- `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md`
- `reviews/worker_reports/taste-runtime-trigger-status-01.md`
- `reviews/worker_reports/semantic-runtime-completion-fix-01.md`
- `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`
- `data/cache/taste_ingest_receipts/latest_runtime_status.json`
- `data/production/pre_ai/chatgpt_payload.json`
- `config/execution_ownership_contract.json`
- `config/taste_result_contract.json`

Provider-pilot evidence inspected:

- `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-01.md`
- attempted lookup of `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md`

Historical paths referenced by older evidence but absent on current default branch were **not** treated as proof of scheduler deletion.

## Recovered canonical producer contract

### Identity

| Field | Recovered truth | Status |
|---|---|---|
| Scheduler name | `Taste Semantic Producer` | proven by durable historical recon |
| Scheduler/task ID | `0a51664a-af13-5b98-8c25-d589f0d247c9` | proven by durable historical recon |
| Runtime owner | scheduled ChatGPT task service | proven |
| Production role | exactly one constrained semantic data-plane worker | canonical |
| GitHub role | scope, queue, retry/completeness, validation/persistence/merge | canonical |
| Interactive chat role | must not become bulk semantic backlog processor | explicitly forbidden |
| Historical cadence | daily, historically approximately `05:00 UTC` | historical only; current platform cadence unverified |
| Current enabled state | unknown | not durably exported / not visible from current scope |
| Current next run | unknown | not durably exported / must not be guessed |
| Current owner/workspace visibility | unknown | requires external scheduler evidence |

### Queue and result interface

The current semantic architecture remains singleton and GitHub-controlled:

- GitHub owns canonical scope and queue construction.
- The existing scheduled ChatGPT worker owns semantic evaluation only.
- GitHub owns validation and persistence.
- Final ranking weights remain a downstream GitHub concern.

`config/taste_result_contract.json` identifies the canonical result contract as **`TASTE-SEMANTIC-RESULT-V5`** and explicitly assigns:

- `semantic_evaluation` -> `existing_scheduled_chatgpt_taste_worker`
- `queue_scope_and_bindings` -> `github`
- `validation_and_persistence` -> `github`
- `final_weight_application` -> `github_final_ranking_producer`

This is important for recovery: the scheduler is **not** the queue owner and must not create a replacement queue. A restored/reconnected/migrated producer must consume the existing GitHub-produced V5 payload and return results through the same canonical validation/persistence path.

The current Taste Step 3 production state contains **701 requestable `semantic_required` rows** plus static-triage-blocked rows. This recon deliberately processed none of them manually.

### Behavioral instructions recoverable from durable sources

The exact opaque scheduler-platform prompt text is not durably exported in the repository and therefore is not claimed verbatim. The production behavior is nevertheless recoverable from versioned contracts:

1. consume only the canonical GitHub-produced Taste semantic queue/payload;
2. evaluate only work that GitHub marked as requiring semantic evaluation;
3. remain price-blind for semantic fit and obey `TASTE-SEMANTIC-RESULT-V5`;
4. do not invent unknown candidate properties or semantic truth;
5. emit contract-valid structured results only;
6. leave scope, retry, completeness, validation, persistence and final ranking to GitHub;
7. never create a second queue or parallel semantic producer;
8. use the established ingest/progress receipt path as durable proof of accepted work.

### Writable/durable targets

The canonical architecture distinguishes worker output from GitHub persistence:

- worker input: existing GitHub-produced semantic queue/payload (`data/production/pre_ai/chatgpt_payload.json` is the current production payload surface inspected in this recon);
- worker result interface: structured `TASTE-SEMANTIC-RESULT-V5` output accepted by the existing GitHub ingest/validation path;
- durable canonical semantic store after GitHub acceptance: `data/steam-taste-semantics.json`;
- durable runtime acceptance/progress status: `data/cache/taste_ingest_receipts/latest_runtime_status.json`.

The worker must **not** bypass GitHub validation/persistence by inventing an alternate canonical store.

## Runtime state classification

The task required classification among exists/enabled, exists/disabled, inaccessible/owner mismatch, missing, or ambiguous.

### What is proven

- The canonical producer identity is proven.
- The producer existed and produced accepted work recently.
- GitHub-side queue/control-plane contracts still expect **one existing scheduled ChatGPT Taste worker**.
- The current V5 result contract is compatible with continuing the same singleton producer role.
- GitHub Actions/sync tooling is validator/compactor/control plane, not a semantic truth generator.

### What is not proven

- current `enabled=true/false` for task `0a51664a-af13-5b98-8c25-d589f0d247c9`;
- current task deletion/non-deletion at the scheduler-global owner scope;
- whether the task lives under another ChatGPT account/workspace/owner scope;
- current platform cadence or `next_run`;
- exact current scheduler prompt text.

### Classification

**`ambiguous`**.

A current-session inability to surface the exact task is **not sufficient evidence of deletion**. The correct fail-closed action is therefore **not** `canonical_migration_required` yet.

Likewise, the available evidence does not positively prove `disabled`, so `restore_existing_task` would be premature. It also does not positively prove an owner mismatch, so `reconnect_existing_task` cannot yet be asserted as fact.

## Copilot/provider pilot status

The Copilot/provider path is **not an accepted replacement basis in this recon**.

`reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-01.md` concluded **`blocked`** before any live Copilot inference/dispatch occurred. Therefore it does not prove that Copilot CLI can durably serve as the Taste semantic producer under the project's zero-cost constraint.

`reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md` was not present on the current default branch at recon time. Its outcome therefore cannot be assumed.

Per the worker task, a provider pilot may influence migration only when a **durable successful report already exists**. That requirement is not met.

## Exact evidence required from the user/owner scope

Only **one** external fact is needed to resolve the ambiguity:

> Open the scheduled Tasks view in the **same ChatGPT account/workspace that originally owned the Taste runtime** and provide the current task-state evidence for **`Taste Semantic Producer`**, preferably showing exact task ID **`0a51664a-af13-5b98-8c25-d589f0d247c9`** and whether it is enabled or disabled. A screenshot/export/task-detail view is sufficient. If the UI does not expose the ID, the task name plus its prompt/instructions and schedule from that owner scope is sufficient to disambiguate it.

No queue dump, no semantic-row content, no manual backlog work, and no paid API credential is required.

### How that single evidence item maps to the next safe action

- Same exact task exists and is **disabled** -> `restore_existing_task`.
  - Safe path: re-enable that exact task only; do not clone it.
- Same exact task exists but is **in another owner/workspace scope / inaccessible here** -> `reconnect_existing_task`.
  - Safe path: reconnect/access the existing owner-scoped task; do not create a duplicate.
- Owner-scope evidence proves the exact task is **deleted/absent** -> `canonical_migration_required`.
- Scheduler service itself becomes unavailable externally -> `blocked_external`.

Until one of those states is proven, the correct next step remains `needs_user_evidence`.

## Minimal canonical zero-cost migration path if deletion is later proven

This section is recon-only. **Do not execute it unless owner-scope evidence first proves that the historical task is truly gone.**

The minimal migration must preserve the existing architecture rather than redesign it:

1. Keep the existing GitHub control plane and current canonical Taste semantic queue/payload.
2. Keep `TASTE-SEMANTIC-RESULT-V5` unchanged unless a separately authorized contract migration is performed.
3. Replace the missing runtime with **exactly one** semantic producer; never create a second producer or parallel queue.
4. Use only a zero-cost runtime/provider that has first been proven by a durable project report under the project's provider-pilot rules.
5. Do not use paid OpenAI API fallback.
6. Bind the replacement producer to the same GitHub-owned queue/result/validation/persistence path.
7. Preserve singleton/duplicate-prevention guarantees.
8. Require a fresh accepted ingest/progress receipt before treating the runtime as recovered.
9. Only after that proof may normal semantic materialization continue.

At recon time there is **no already-proven Copilot provider report**, so this migration path does not nominate Copilot as the production runtime.

## Safety/invariant check

- No scheduler was created, cloned, enabled, disabled, or modified.
- No second semantic queue was created.
- No GitHub workflow was repurposed into a semantic producer.
- No semantic row was manually processed.
- No old ranking snapshot was used as proof of new semantic completion.
- No semantic backfill completion was fabricated.
- No paid OpenAI API fallback was used.
- No IMPLEMENT work was started.
- The only repository mutation from this recon is this required report.

## Decision

```text
next_step = needs_user_evidence
```

Reason: the canonical task's historical identity and recent production activity are proven, but its **current scheduler owner/state is not**. Deletion has not been proven, so creating a replacement would risk a duplicate semantic producer and violate the project's canonical singleton architecture.
