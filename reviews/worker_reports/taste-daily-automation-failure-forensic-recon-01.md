# Taste Daily Automation Failure Forensic Recon 01

## Task
Forensic READ-ONLY recon of why automatic ChatGPT Taste analysis stopped producing accepted results after 2026-09-01, why the failure remained unnoticed, and whether it is related to the paid-list publication incident.

Worker task: `WORKER_TASK_TASTE_DAILY_AUTOMATION_FAILURE_FORENSIC_RECON_01.md`

## Status
`complete_root_cause_bounded`

No repair, scheduler mutation, Taste-row processing, canary inference, workflow dispatch, or production-data mutation was performed. The only repository mutation in this task is this required report.

## Executive conclusion

The last proven accepted automatic Taste semantic progress occurred at **2026-09-01T21:03:08Z** (Europe/Samara: **2026-09-02 01:03**). Canonical receipt `data/cache/taste_ingest_receipts/4f99eff1753a8ac9480e.json` records batch `4f99eff1753a8ac9480e`, input `chatgpt-20260902-0100-001.json`, **11 accepted results**, and queue movement **37 -> 26**.

The next required daily semantic cycle was the **2026-09-03 01:00 Europe/Samara** cycle (approximately `2026-09-02T21:00Z`). GitHub-side preparation succeeded before that boundary: historical `data/production/pre_ai/chatgpt_payload.json` at commit `093543079e3c078de5ad479026f0c6360ace01d9` is bound to fresh source `2026-09-02T20:36:22.419743Z`, has `status=complete`, and contains **644** unresolved Taste queue entries. No normal Taste semantic inbox submission or accepted receipt followed. The next commit touching `data/ai_inbox/taste` after the successful Sep-1/Sep-2 cycle is the separately authorized singleton canary on **2026-09-06T17:05:09Z** (`392903cf720dde1de4936436f235e9489d659ddd`).

Therefore the first missed cycle is **not a deterministic preparation failure and not an ingest failure after a produced result**. The failure boundary is the external semantic-producer stage: a fresh GitHub-prepared scope existed, but no normal semantic output reached the canonical inbox/ingest path. This is a **stage-level semantic execution failure classification**. It does **not** prove that the ChatGPT task actually launched and crashed; the repository cannot distinguish `ran_and_failed`, `did_not_run`, `disabled`, `deleted`, `owner/workspace inaccessible`, or another scheduler-platform state.

The exact reason the historical scheduled task stopped working or disappeared **cannot be proven from retained repository evidence and current scheduler visibility**. Durable later recon identifies the historical canonical producer as `Taste Semantic Producer`, historical task/jawbone id `0a51664a-af13-5b98-8c25-d589f0d247c9`, but explicitly classifies its current platform state as ambiguous. A later control-plane check of a separately established singleton task also demonstrates the same visibility limitation: enabled/disabled state could not be reliably read. Neither later artifact is proof of the old task's deletion time, disable time, or cause.

The system did not alarm after the first missed day because the required liveness invariant did not yet exist in durable production form. Before the Sep-3 observability work, GitHub had queue/preparation evidence and ingest receipts when work arrived, but **queue presence was not a heartbeat** and there was no automatically enforced condition equivalent to: `fresh prepared semantic scope exists AND no accepted semantic progress for that scope by the daily deadline/grace => alert/degraded runtime`. The durable `latest_runtime_status.json` / current-scope progress mechanism was introduced only on **2026-09-03 around 03:38Z**, after the first expected semantic cycle had already been missed. The ingest workflow itself is event-driven by Taste inbox writes/manual dispatch; it has no daily schedule that would fail noisily when the external producer emits nothing. Silence therefore looked like “nothing to ingest,” not like a failing GitHub job.

The paid-list publication incident and Taste automation outage are **separate primary failures with downstream coupling** (`partially_coupled`), not one root cause. The paid-list forensic recon proves the published paid commercial lineage was already stale from source `2026-08-30T20:37:11Z`, while a newer mailing source existed on `2026-08-31T20:36:53Z`. Taste still produced a successful accepted batch on `2026-09-01T21:03:08Z`, so the Taste outage cannot be the initiating cause of the paid-list staleness. The paid-list primary cause was a missing/inactive deterministic `commercial_only` production-orchestration handoff. However, after Taste stopped producing current-scope completion, the full visual route correctly failed closed on `chatgpt_completion_missing`; that semantic outage became a contributing blocker that prevented the full rebuild from catching up. Thus the two faults overlapped and reinforced the visible stale-list symptom.

## 1. Last proven accepted automatic semantic progress

### Canonical receipt

`data/cache/taste_ingest_receipts/4f99eff1753a8ac9480e.json`

Proven fields:

- `processed_at_utc = 2026-09-01T21:03:08+00:00`
- Europe/Samara local time = `2026-09-02 01:03`
- `batch_id = 4f99eff1753a8ac9480e`
- `input_files = ["chatgpt-20260902-0100-001.json"]`
- `result_count = 11`
- baseline `ai_queue_count = 37`
- after `ai_queue_count = 26`
- exact queue delta = `11`
- all receipt validation checks are true.

This is accepted semantic progress, not merely prepared work.

### Corroborating runtime status

The later durable runtime observability layer bootstrapped from the same accepted receipt and records:

- last accepted progress: `2026-09-01T21:03:08Z`
- 11 accepted results
- queue `37 -> 26`
- current newer scope had no accepted overlap/progress.

## 2. Next expected daily cycle

`config/daily_execution_contract.json` is canonical and defines:

- timezone: `Europe/Samara`
- night preparation local time: `01:00`
- external semantic worker: `ChatGPT scheduled task`
- GitHub owns the control plane and exact prepared scope.

The successful Sep-2-local semantic result arrived at 01:03 local. The next required cycle was therefore Sep 3 local, with its semantic window centered on **2026-09-03 01:00 Europe/Samara / 2026-09-02 21:00 UTC**.

### Preparation evidence

Historical payload at commit `093543079e3c078de5ad479026f0c6360ace01d9`, committed `2026-09-02T20:37:14Z`, proves:

- `status = complete`
- `source_mailing_updated_at_utc = 2026-09-02T20:36:22.419743Z`
- `source_family_count = 743`
- `ai_queue_count = 644`
- `purchase_context_line_count = 644`
- `complete_family_partition = true`
- Taste `semantic_work.queue_count = 644`.

So the next cycle had a fresh, complete deterministic input and substantial unresolved semantic work.

### Semantic output / ingest evidence

Git history for `data/ai_inbox/taste` from immediately after the successful receipt through Sep 6 shows:

- successful ingest commit `2e7405e6b36faf4e9f2758d80366b05c47f25a79` at `2026-09-01T21:03:09Z`;
- then no normal Taste producer submission;
- next inbox-changing commit is special singleton canary `392903cf720dde1de4936436f235e9489d659ddd` at `2026-09-06T17:05:09Z`.

The receipt history over the corresponding pre-canary window has no new accepted semantic batch; the Sep-3 receipt-directory mutation is the observability implementation bootstrapping status from the already existing Sep-1 accepted receipt, not new semantic work.

### Classification

`next_expected_cycle_classification = semantic_execution_failure_at_external_producer_boundary`

Meaning: preparation succeeded; no normal semantic output was delivered to the canonical inbox; therefore ingest had nothing new to process. This classification locates the broken stage but **does not assert whether the external scheduler attempted execution**.

Not supported:

- `prepare failure` — disproven by fresh complete 644-row payload;
- `ingest failure` — no produced normal inbox artifact exists for ingest to reject/process;
- “ChatGPT definitely launched and crashed” — not observable;
- “task definitely disappeared that night” — not observable.

## 3. What can be said about subsequent daily launches

The phrase “subsequent launches” must be evidence-qualified.

### Proven

- No accepted normal automatic Taste progress occurred after `2026-09-01T21:03:08Z` before later recovery/canary work.
- No normal `data/ai_inbox/taste` producer submission is retained between the successful cycle and the Sep-6 canary.
- GitHub continued to create newer deterministic/pre-AI state after the last success; the first next scope alone already contained 644 unresolved semantic entries.
- Later production artifacts explicitly reached `DEGRADED / chatgpt_completion_missing` when semantic completion was absent.

### Not proven

For each missed calendar day the repository cannot say whether the external ChatGPT scheduled task:

- fired and failed internally;
- fired but could not access/emit the result;
- was disabled;
- was deleted/lost;
- was owner/workspace-scoped away from the current session;
- remained enabled but the platform did not execute it.

There is no retained authoritative scheduler execution log for those dates in GitHub, and later scheduler inspection does not reconstruct historical lifecycle events.

## 4. Can the old task's disappearance/failure cause be proven?

`historical_scheduler_failure_provable = false`

Durable recovery recon proves the historical identity:

- title: `Taste Semantic Producer`
- historical task/jawbone id: `0a51664a-af13-5b98-8c25-d589f0d247c9`
- runtime owner: ChatGPT scheduled-task service, external to GitHub Actions.

But that recon could not surface an authoritative current record for the historical task and explicitly listed multiple mutually compatible possibilities: disabled, another owner/workspace scope, deleted/lost, or enabled but invisible to the session. Therefore current absence from a visible task surface is not proof of deletion.

A later report checking the separately established singleton task instance `6a9d6fdddc00819193ed670d782045c4` likewise could not reliably bind exact task ID to current enabled flag. That later task must not be confused with the historical producer, and its unreadable state does not establish why the historical task stopped.

### Maximum defensible statement

The historical producer **ceased producing repository-visible normal Taste outputs after the accepted Sep-1/Sep-2-local cycle**. Its exact scheduler-platform lifecycle transition and exact cause are **not reconstructible from retained evidence**.

## 5. Why unresolved/new work accumulated without alarm

There were two independent properties that together created a silent backlog:

1. **Producer/output silence did not create a failing ingest run.** `.github/workflows/ingest-taste-batch.yml` is triggered by a write to `data/ai_inbox/taste/*.json` (and manual dispatch), not by a daily clock. If the external producer emits nothing, the ingest workflow has no failed daily run to surface.
2. **Prepared queue was not liveness proof.** GitHub could continue preparing/rebuilding unresolved semantic scope. Presence or growth of the queue means “work exists,” not “the external worker is alive.” Before the later runtime-observability fix, there was no durable current-scope progress check turning “fresh work exists but no accepted result arrived” into a specific runtime failure.

The 644-row Sep-2 payload should be understood as **unresolved semantic work**, not as proof that all 644 rows were newly discovered games. It nevertheless proves the backlog could be large while the semantic producer contributed zero new accepted progress.

## 6. Why the system did not notice after the first missed day

### What was missing at the time

The missing invariant was effectively:

```text
IF current GitHub-prepared Taste scope is fresh
AND current scope contains unresolved semantic work
AND no accepted semantic progress/heartbeat for that scope arrives by the expected daily completion window
THEN runtime health must become degraded/failed and an operator-visible alarm must be raised.
```

Before Sep 3, the repository had receipts only when accepted work happened. It did not yet persist one canonical runtime health artifact that correlated the latest accepted progress with the **current prepared scope** and explicitly rejected queue presence as a heartbeat.

### When the gap became durably visible

Commit `61d11ee463cba39ff9e904bb6912b3a46e21b5fc` (`Fix semantic runtime completion observability`) landed at approximately `2026-09-03T03:38:46Z` and introduced the durable `latest_runtime_status.json` / current-scope progress mechanism. The implementation report records that the latest accepted receipt was still Sep 1 21:03Z while the current prepared scope was Sep 2 20:36Z, producing `no_current_scope_progress_observed` / degraded state.

Therefore:

- **logical earliest failure boundary:** after the Sep-3 01:00 Europe/Samara semantic cycle failed to produce current-scope accepted progress;
- **first durable repository-side health proof found in this recon:** Sep 3 around `03:38Z` (`07:38` Europe/Samara), when observability was added/bootstrapped;
- **why no first-day automatic alarm:** the watcher/invariant capable of making that distinction was not yet durably implemented/wired before the miss.

Later code uses cadence/grace/staleness concepts, but this recon does not retroactively claim that such an alert was actively scheduled before the incident.

`earliest_detectable_failure_point = next_expected_cycle_no_current_scope_progress; durable_repo_detection_available_by_2026-09-03T03:38Z`

`missing_alert_invariant = fresh_current_scope_with_unresolved_work + no_current_scope_accepted_progress_by_daily_window => degraded_and_operator_alert`

## 7. Relation to the stale paid-list publication incident

`relation_to_paid_list_incident = partially_coupled_separate_primary_failures`

### Evidence that they are not one initiating failure

The publication forensic report establishes:

- last proven published paid commercial source lineage: `2026-08-30T20:37:11Z` (rendered locally as 31 Aug 00:37);
- first proven newer mailing source: `2026-08-31T20:36:53Z`;
- fresh commercial data continued above visual publication;
- primary paid-list cause: missing/inactive production-orchestration handoff for deterministic `commercial_only` refresh.

Taste, meanwhile, still produced accepted semantic progress at `2026-09-01T21:03:08Z`, more than a day after the first proven newer commercial source existed while the published paid lineage remained old.

Therefore the Taste outage did **not** initiate the paid-list stale lineage.

### Where they became coupled

The full visual rebuild is intentionally fail-closed on semantic completeness. Once Taste stopped producing current-scope completion, later pre-AI state reached `DEGRADED / chatgpt_completion_missing`; the full visual route could not legally absorb new commercial truth. Because the independent `commercial_only` orchestration branch was missing, there was also no scoped deterministic bypass that could safely refresh paid price/discount fields while preserving semantic labels.

So:

- paid publication had its own primary orchestration defect;
- Taste had its own external semantic-producer liveness failure;
- semantic incompleteness then **amplified/prolonged** the paid-list symptom by blocking full rebuild;
- both shared a broader observability weakness: strong fail-closed integrity behavior existed without equally strong per-subdomain liveness/freshness alarms.

## Final required classifications

| Field | Classification |
|---|---|
| `last_proven_accepted_semantic_progress` | `2026-09-01T21:03:08Z`, batch `4f99eff1753a8ac9480e`, 11 accepted, queue `37 -> 26` |
| `next_expected_cycle_classification` | `semantic_execution_failure_at_external_producer_boundary` — fresh preparation existed; no normal output reached inbox; scheduler attempt itself unproven |
| `historical_scheduler_failure_provable` | `false` |
| `earliest_detectable_failure_point` | after the Sep-3 01:00 Europe/Samara expected semantic cycle had no current-scope progress; durable repo-side proof available by ~`2026-09-03T03:38Z` |
| `missing_alert_invariant` | fresh unresolved current scope + no accepted current-scope progress by daily window => degraded/failure + operator-visible alert |
| `relation_to_paid_list_incident` | `partially_coupled_separate_primary_failures` |

## Evidence inspected

Required control/protocol inputs:

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `WORKER_TASK_TASTE_DAILY_AUTOMATION_FAILURE_FORENSIC_RECON_01.md`
- `PROJECT_ROUTES.md`
- `config/daily_execution_contract.json`
- `config/execution_ownership_contract.json`
- `config/taste_result_contract.json`

Required/prior runtime reports:

- `reviews/worker_reports/taste-zero-cost-runtime-migration-recon-01.md`
- `reviews/worker_reports/semantic-runtime-task-health-recon-01.md`
- `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md`
- `reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`

Additional durable forensic/recovery evidence:

- `reviews/worker_reports/taste-semantic-runtime-recovery-recon-01.md`
- `reviews/worker_reports/taste-singleton-disabled-state-confirm-01.md`
- `reviews/worker_reports/taste-runtime-trigger-status-01.md`
- `reviews/worker_reports/semantic-runtime-completion-fix-01.md`
- `reviews/worker_reports/publication-freshness-pre-fix-forensic-recon-01.md`
- `data/cache/taste_ingest_receipts/4f99eff1753a8ac9480e.json`
- `data/cache/taste_ingest_receipts/latest_runtime_status.json`
- historical `data/production/pre_ai/chatgpt_payload.json@093543079e3c078de5ad479026f0c6360ace01d9`
- `.github/workflows/ingest-taste-batch.yml`
- commit history for `data/ai_inbox/taste`, `data/cache/taste_ingest_receipts`, and `data/production/pre_ai/chatgpt_payload.json`.

## Changes

- Created this report first, before forensic investigation, as required by `WORKER_REPORT_DURABILITY_PROTOCOL.md`.
- Finalized this same report with evidence and classifications.
- No other repository state changed by this task.

## Validation / safety

- No scheduler/task was created, modified, enabled, disabled, deleted, or run.
- No workflow was dispatched.
- No Taste game was analyzed.
- No Taste queue row was processed.
- No canary was run or inferred as production success.
- No receipt, queue, cache, production payload, ranking, or visual artifact was modified.
- Historical task deletion/disable timing was not invented.
- Paid-list correlation was classified from retained chronology, not temporal coincidence alone.

## Recommended next step

No repair is authorized by this task. Director should use this report as the forensic boundary for a separate future task if recovery/monitoring work is authorized. Any future scheduler action must first distinguish the exact existing task state without assuming deletion, and any future alerting work should enforce current-scope accepted-progress liveness independently of queue preparation.

Do not begin the next task from this worker report.

## Efficiency / reusable lesson

For external semantic workers, a queue and a fail-closed consumer are insufficient observability. Persist an execution/progress receipt tied to the exact current scope and separately alarm on absence of progress after the expected window. Event-driven ingest cannot detect a producer that emits nothing.