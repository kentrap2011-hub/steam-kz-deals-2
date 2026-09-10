# DIRECTOR TASK BOARD

## Current rules
- Keep at most two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots, not monotonically increasing task numbers.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, reconcile Board -> exact task file -> exact durable report from the immediately preceding step.
- Worker completion means exact durable report is final, not merely that the chat response ended.
- All non-trivial workers obey `WORKER_REPORT_DURABILITY_PROTOCOL.md` and `WORKER_ANTI_STALL_PROTOCOL.md`.
- All user-facing closeouts obey `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`.
- Proactive operational gap detection follows `PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`; the user must not be the project's monitoring layer.

## Current user priority — PROCESS REAL GAMES FIRST
The user explicitly does not want to pause backlog processing for another optimization cycle.

Primary goal now:
1. finish acceptance of the already-produced 10-result Taste package;
2. apply the narrow required queue-order policy before starting new semantic backlog batches;
3. resume real Taste backlog processing in bounded batches;
4. get enough canonically processed games that the user can actually inspect/use the output;
5. defer smarter profile-change reevaluation architecture until later.

Do not interrupt backlog drain merely to optimize reevaluation invalidation unless a real correctness blocker requires it.

## Current active worker — existing 10-result pinned ingest
Task:
`WORKER_TASK_TASTE_EXISTING_BATCH_PINNED_INGEST_01.md`

Report:
`reviews/worker_reports/taste-existing-batch-pinned-ingest-01.md`

Target package:
`data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json`

State at latest Director checkpoint:
- package preflight passed and remained byte-identical;
- worker could not create a fresh `workflow_dispatch` through its connected GitHub API;
- user manually launched exactly one `Ingest context-bound taste batch` workflow on `main`;
- same worker was instructed to resolve the exact new run/job IDs, verify success/failure, finalize the existing report, and not dispatch again;
- no next games may start inside this task.

## IMMEDIATE REQUIRED NEXT — Taste queue age-priority ordering
Task:
`WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md`

Report:
`reviews/worker_reports/taste-queue-age-priority-order-01.md`

Status:
`queued_after_existing_10_terminal_state_before_next_new_semantic_batch`

User-required ordering for newly constructed Taste work:
1. items that have never had a canonically accepted successful Taste semantic result;
2. then previously checked items from oldest successful canonical Taste evaluation to newest.

Rules:
- an already pinned/in-flight work-unit is never reordered mid-flight;
- failed/rejected/unaccepted attempts do not count as a successful check;
- equal times use deterministic stable canonical identity as tie-breaker;
- do not substitute source/queue/profile/Git commit time for semantic successful-evaluation time;
- if no reliable canonical successful-evaluation timestamp exists, worker must stop and report the smallest explicit state addition needed rather than invent an approximation.

This is a narrow ordering requirement, not a new commercial ranking system.

## Immediate after ordering — resume real backlog drain
After the exact existing-10 ingest reaches a terminal verified state and the age-priority ordering task is complete, resume the throughput-drain experiment from the then-current canonical Taste queue/work-unit.

Operational intent:
- process real games, not architecture work;
- bounded semantic batches, checkpoint after every accepted batch;
- continue in the same authorized worker session until a genuine blocker, safe stop, or practical execution limit;
- do not interpret infrastructure/system defects as semantic capacity;
- do not count stale-profile historical acceptance as current-profile backlog reduction when A→B rules keep work pending.

The observed result should later inform a practical per-invocation capacity, but must not silently become a business quota.

## Proactive Project Auditor — standing role
Protocol:
`PROACTIVE_PROJECT_AUDITOR_PROTOCOL.md`

Status:
`standing_operational_role`

Purpose:
Detect operational/architecture mismatches without waiting for the user to notice them.

Examples this role is expected to catch proactively:
- stale one-game/canary prompt still active after production architecture is ready;
- old cadence surviving after a newer user cadence requirement;
- queue ordering that does not match current product priority;
- a design report whose assumptions were superseded by later changes;
- implementation that passed local tests but is not wired into the real production path;
- recurring unnecessary reprocessing that should become a later architecture task;
- a production/system defect being mistaken for normal throughput/capacity.

The auditor is read-only by default and uses a free reusable worker slot when safe. It does not become a permanent third worker and cannot repair findings without separate authorization.

Mandatory gates include production failure, producer/scheduler/queue lifecycle changes, user operating-policy changes, before declaring automated production fully enabled, and after multi-step architecture repair acceptance.

## Normal Scheduled Task — IMPORTANT CURRENT STATE
Existing task:
- title: `Taste Semantic Producer`
- id: `6aa032f37e688191a5c9a1a83f91c5d9`
- producer identity remains generation 2.

Director rechecked the actual task instruction on 2026-09-10 and found that it is still the old one-game Chernobylite canary instruction, not the normal backlog-processing instruction.

Therefore:
- do NOT claim that the existing Scheduled Task currently drains the queue automatically;
- do NOT simply increase its cadence and assume that real backlog processing occurs;
- its old canary fail-closed checks make it unsuitable as the normal producer prompt.

The user wants the eventual normal Taste reevaluation/producer cadence to be **HOURLY, not DAILY**.

Until the normal producer binding is actually implemented and verified, keep the stale canary task on its previous safe DAILY 01:00 Europe/Samara schedule rather than causing useless hourly canary executions.

When the normal producer is enabled, update this SAME task rather than creating a second Taste producer. Target cadence: `RRULE:FREQ=HOURLY`. Preserve single-producer ownership and all pinned-work-unit/fail-closed rules.

## Ready design — normal bounded producer binding
Design report:
`reviews/worker_reports/taste-normal-daily-binding-design-01.md`

Design status:
`complete_design_ready_for_implementation`

Existing recommendation:
- `MAX_TASTE_ITEMS_PER_INVOCATION = 10`
- `MAX_TASTE_WORK_UNITS_PER_INVOCATION = 1`
- exact deterministic contiguous head work-unit;
- exact pinned profile/work identity;
- strict ingest/post-ingest verification;
- deterministic suffix resume;
- one existing Scheduled Task only.

The design originally preserved a daily cadence. User requirement has now superseded that cadence detail: when implementation is authorized/enabled, normal producer cadence should be hourly. The execution-safety cap remains separate from cadence and from business completeness.

The deterministic head must be built from the user-required age-priority queue, once `taste-queue-age-priority-order-01` is implemented.

Do not implement the broader normal producer merely because it is on the board; current priority is current real-game processing first.

## QUEUED LATER — selective profile-change reevaluation
Task ID / backlog item:
`taste-selective-profile-reevaluation-01`

Status:
`queued_after_current_backlog_is_usable`

User requirement:
A small edit to the live Taste profile should not automatically force hundreds of otherwise unaffected cached games through semantic reevaluation merely because the whole-profile blob SHA changed.

Goal for later design/implementation:
- preserve exact provenance of every accepted Taste result;
- determine which prior results are materially affected by a profile change;
- invalidate/requeue only affected results where safely provable;
- fail conservatively when impact cannot be determined;
- never reuse an old result under changed relevant preference evidence without proof;
- preserve pinned in-flight work-unit behavior;
- no ChatGPT-selected arbitrary candidates;
- no hidden second cache/queue;
- GitHub remains authoritative.

Cadence requirement for the eventual reevaluation mechanism:
- check/process reevaluation work **once per hour**, not once per day;
- this must mean processing the current affected queue, NOT reanalyzing the whole database every hour.

Do not start this optimization now. Current priority is to process the existing Taste backlog so usable results exist.

## Closed / accepted foundations relevant to current work
### Real Chernobylite canary
Report:
`reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`
Final status: accepted.

### Live-profile binding fix
Report:
`reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`
Final status: complete.

### Pinned profile batch lifecycle
Task:
`WORKER_TASK_TASTE_PINNED_PROFILE_BATCH_LIFECYCLE_FIX_01.md`
Report:
`reviews/worker_reports/taste-pinned-profile-batch-lifecycle-fix-01.md`
Final status:
`complete_pinned_profile_lifecycle_fix_ready_for_acceptance`

Production implementation commit:
`fc355295eb0c473a9d0d73ad33e4cfa9d621cc0b`

Key accepted behavior:
- exact profile/work-unit pin exists before semantics;
- live profile may advance while in-flight batch completes against its pinned profile;
- old-profile result can be persisted without being falsely promoted to a current-profile cache hit;
- next current work remains pending when required;
- active pin retirement/creation is transactional with successful ingest.

### Transactional proof repair
Report:
`reviews/worker_reports/taste-transactional-proof-repair-01.md`
Final status: complete.

### Manual throughput drain
Task:
`WORKER_TASK_TASTE_MANUAL_THROUGHPUT_DRAIN_01.md`
Report:
`reviews/worker_reports/taste-manual-throughput-drain-01.md`

First 10 semantic results were produced successfully, but their original ingest path failed before canonical acceptance. They are the exact package currently being recovered through the pinned lifecycle task above.

## Other queued work
### Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Remains queued after the current Taste priority.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.
