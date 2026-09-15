# WORKER TASK — Taste Dossier Live Buffered Acceptance 02

Task ID: `taste-dossier-live-buffered-acceptance-02`
Mode: `ACCEPTANCE`

## Goal
Repeat the controlled live buffered acceptance after canonical activation-state alignment has been completed and accepted.

The user has already manually installed the buffered live prompt in the existing ChatGPT Scheduled Task `Taste Steam Review Dossier`. Treat that manual UI fact as authoritative. Worker chats must not attempt to inspect Scheduled Task UI state.

## START gate
Read fully:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- this task
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-buffered-submission-implement-01.md`
- `reviews/worker_reports/taste-dossier-live-buffered-prompt-prep-01.md`
- `reviews/worker_reports/taste-dossier-live-buffered-acceptance-01.md`
- `reviews/worker_reports/taste-dossier-buffered-activation-state-align-01.md`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/execution_ownership_contract.json`
- current canonical dossier work manifest.

Perform architecture preflight.

## Manual UI boundary
Do NOT inspect or search for Scheduled Task UI.

When GitHub baseline is captured and the start condition is clean/safe, ask the user in this chat to manually press `Run now` exactly once on the existing `Taste Steam Review Dossier` Scheduled Task and reply `Запустил`.

Do not substitute another trigger. Do not manually dispatch any GitHub workflow.

## Baseline before Run now
Record from current durable `main` at minimum:
- latest main commit;
- current `snapshot_id`;
- prepared/completed/remaining counts;
- immutable group count;
- canonical expected sequence;
- exact expected group 1 appids/group hash;
- exact group 2 identity too, because multi-group proof is required;
- current relevant dossier inbox artifacts for this snapshot;
- latest relevant workflow/run/commit refs;
- confirm contract, persistence bridge and repository worker prompt now agree that buffered transport/drain is active.

If the current expected deterministic group artifact already exists while canonical progress has not advanced, classify first and do not request Run now unless safe under the contract.

## Controlled real acceptance
After the user replies `Запустил`, observe durable GitHub state only.

A PASS requires one controlled Scheduled Task invocation to prove buffered behavior end-to-end:

1. At least two successive immutable groups from the same snapshot are published create-only by the worker.
2. Group identities/order exactly match the canonical predeclared group plan.
3. Evidence shows group 2 was published without waiting for canonical acceptance of group 1. Use durable commit/action ordering where available; do not guess.
4. GitHub state-based drain accepts the maximal valid contiguous prefix in order.
5. Canonical progress advances by exactly the accepted item count, with no reorder, skip, duplicate or replay.
6. Accepted buffer artifacts are cleaned up according to contract.
7. Same snapshot remains in force unless a genuine canonical snapshot rollover occurs.
8. Local publication is not falsely treated as canonical completion.
9. Taste Semantic Producer remains unchanged.

One successfully persisted 10-item group alone is NOT sufficient acceptance.

## Async observation
GitHub Actions may be queued or still running while the Scheduled Task publishes later groups. This is expected.

Use bounded observation/rechecks. Do not spin indefinitely. If publication evidence is sufficient but GitHub drain is still unresolved after a reasonable bounded window, write `acceptance_pending_async_completion` with exact evidence rather than guessing.

## Failure classifications
- Only one group published without real blocker -> `rejected` for buffered live behavior.
- Real create/write/safety/platform failure on N+1 -> report exact blocker; do not automatically blame architecture.
- Out-of-order, skipped scope, alternate retry, overwrite, direct canonical mutation -> `rejected`.
- GitHub drain gap-skip, wrong advancement, duplicate persistence, stale snapshot mutation -> `rejected`.
- Unobservable interruption -> apply PITFALL-004 and state `причина неизвестна` unless evidence proves otherwise.

## Safety constraints
- Exactly one user-triggered Scheduled Task `Run now` for this acceptance.
- No manual GitHub workflow dispatch.
- No runtime/config/code changes.
- No synthetic production data.
- Do not modify Taste Semantic Producer.
- Do not alter schedule/cadence/limits.

## Durable report
Write to main:
`reviews/worker_reports/taste-dossier-live-buffered-acceptance-02.md`

Report must include:
- architecture preflight;
- exact pre-run baseline;
- user manual-run confirmation;
- published group artifact identities/commits/timestamps/order;
- proof or non-proof that group 2 publication preceded group 1 canonical acceptance;
- relevant GitHub Actions runs/jobs/outcomes;
- canonical before/after counts and expected sequence;
- cleanup/pending state;
- no-duplicate/no-reorder/no-scope-change assessment;
- Taste Semantic Producer unchanged assessment;
- exact acceptance verdict;
- explicit statement whether multi-group same-invocation buffered behavior was proven.

Allowed statuses:
- `accepted`
- `rejected`
- `blocked`
- `acceptance_pending_async_completion`

Stop after durable report. Do not start another Scheduled Task run.