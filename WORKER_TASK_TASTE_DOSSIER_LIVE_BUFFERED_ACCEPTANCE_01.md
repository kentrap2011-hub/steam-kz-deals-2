# WORKER TASK — Taste Dossier Live Buffered Acceptance 01

Task ID: `taste-dossier-live-buffered-acceptance-01`
Mode: `ACCEPTANCE`

## Goal
Validate the newly installed live buffered prompt for the existing ChatGPT Scheduled Task `Taste Steam Review Dossier` against real GitHub production behavior, without giving the worker any responsibility for Scheduled Task UI state.

The user has manually confirmed that the prepared buffered replacement prompt was saved in the existing Scheduled Task. Treat that manual confirmation as authoritative. Do NOT attempt to read or verify Scheduled Task UI state.

## START gate
Read fully before doing anything:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- this task
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-buffered-submission-implement-01.md`
- `reviews/worker_reports/taste-dossier-live-buffered-prompt-prep-01.md`
- `reviews/worker_reports/taste-dossier-live-prompt-acceptance-01.md`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/execution_ownership_contract.json`
- current canonical dossier work manifest.

Perform architecture preflight.

## Manual UI boundary
Worker chats do not have reliable access to Scheduled Task UI.

Therefore:
- do NOT try to inspect the live task prompt, title, schedule, state or Run button;
- do NOT spend time looking for Scheduled Task UI through tools;
- when ready for the real run, explicitly ask the user in this worker chat to manually press `Run now` once on the existing `Taste Steam Review Dossier` task and then reply `Запустил`;
- do not substitute another trigger for that user action.

## Baseline before user Run now
Before asking the user to run it, record from durable GitHub state at minimum:
- current `snapshot_id`;
- prepared/completed/remaining counts;
- immutable group count;
- canonical expected sequence/group;
- exact expected first group appids and `group_sha256`;
- current relevant inbox artifacts for this snapshot, if any;
- current dossier cache state necessary to prove new persistence later;
- current latest relevant workflow/run/commit refs as baseline.

If the current expected deterministic group artifact already exists while canonical progress has not advanced, do not ask the user to Run now until you classify that condition under the canonical contract. Report blocked if a safe live acceptance cannot start from a clean expected-group state.

## Controlled real acceptance run
After baseline is captured, ask the user to manually press `Run now` exactly once on the existing `Taste Steam Review Dossier` Scheduled Task and reply `Запустил`.

After that user confirmation, observe durable GitHub state only. Do not inspect Scheduled Task UI.

The acceptance must determine whether the live worker actually exercises buffered behavior.

### Minimum PASS evidence
A strong PASS requires evidence from one controlled Scheduled Task invocation that:

1. At least **two successive immutable groups** from the same snapshot were published create-only by the worker without waiting for canonical acceptance of the first before publication of the second.
2. Published group identities/order exactly match the predeclared canonical group plan.
3. GitHub drain handles repository state, not only one triggering file, and canonically accepts the available valid contiguous prefix in order.
4. Canonical progress advances by the exact accepted item count with no reorder, skip, duplicate or replay.
5. Accepted buffer artifacts are cleaned up according to contract; later/gapped artifacts, if any, remain correctly pending.
6. Same snapshot remains in force during the controlled sequence unless a genuine daily boundary/new canonical snapshot occurs; if superseded, classify according to contract rather than forcing PASS.
7. Local publication is not falsely reported as canonical completion.
8. No Taste Semantic Producer changes occur.

The key proof is **multiple-group same-invocation publication**. Merely proving one 10-item group persisted is not sufficient to accept the buffered live behavior.

## Timing / asynchronous GitHub Actions
GitHub Actions may still be queued/running while the Scheduled Task continues publishing later groups. This is expected in the buffered design.

Do not treat temporary ingest invisibility as a failure by itself.

Observe enough durable repository history/state to determine publication order and later canonical drain outcome. Use bounded waiting/rechecks; do not spin indefinitely. If GitHub Actions are still unresolved after a reasonable bounded observation window, report `acceptance_pending_async_completion` with exact durable evidence and stop rather than guessing.

## Fail / partial classifications
Use precise status and evidence:

- If only one group is published and the Scheduled Task ends/stops without a real create/write/platform blocker, buffered live behavior is NOT accepted.
- If publication of group N succeeds but N+1 create fails for a real tool/safety/platform reason, report that exact blocker; do not call architecture failed automatically.
- If worker publishes out of order, skips, changes scope, writes alternate retry artifacts, overwrites, or directly edits canonical state: fail acceptance.
- If GitHub drain misorders, skips a gap, duplicates persistence, advances wrong count, or stale snapshot mutates current state: fail acceptance.
- If the run is interrupted for an unobservable platform reason, apply PITFALL-004: state exact observable last step and `причина неизвестна` unless evidence proves more.

## Production safety
- Exactly one user-triggered Scheduled Task `Run now` for this acceptance.
- No manual GitHub workflow dispatch.
- No runtime/config/code changes during acceptance.
- No synthetic production data.
- Do not modify Taste Semantic Producer.
- Do not alter schedule/cadence/limits.

## Durable report
Write to `main`:
`reviews/worker_reports/taste-dossier-live-buffered-acceptance-01.md`

The report must contain:
- architecture preflight;
- exact pre-run baseline;
- user manual-run confirmation noted as authoritative UI action;
- published group artifact identities/commits/timestamps/order;
- evidence showing whether group 2+ was published before group 1 canonical acceptance became visible, to the extent durable ordering permits;
- relevant GitHub Actions runs/jobs and outcomes;
- canonical before/after counts and expected sequence;
- cleanup/pending state;
- no-duplicate/no-reorder/no-scope-change assessment;
- Taste Semantic Producer unchanged assessment;
- exact acceptance verdict;
- explicit statement whether multiple-group same-invocation buffered behavior was proven.

Allowed final statuses:
- `accepted`
- `rejected`
- `blocked`
- `acceptance_pending_async_completion`

Stop after durable report. Do not start another Scheduled Task run.
