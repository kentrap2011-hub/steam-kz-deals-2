# WORKER TASK — Taste Dossier Live Compact Acceptance 01

Task ID: `taste-dossier-live-compact-acceptance-01`
Mode: `ACCEPTANCE`

## Goal
Run one controlled live acceptance after compact worker index + immutable per-group descriptors have landed and been accepted.

The user has already manually installed the live Scheduled Task prompt that instructs each invocation to read the authoritative repository worker prompt from `main`. Treat that manual fact as authoritative. Do not inspect Scheduled Task UI.

This acceptance must prove the live Scheduled Task actually uses the new compact read path and can publish at least two consecutive buffered groups in one invocation without waiting for canonical acceptance of the first.

## START gate
Read fully:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- this task
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-worker-view-recon-01.md`
- `reviews/worker_reports/taste-dossier-worker-view-implement-01.md`
- `reviews/worker_reports/taste-dossier-live-buffered-acceptance-02.md`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/execution_ownership_contract.json`
- current compact worker index
- current descriptors for canonical expected sequence N and N+1
- current canonical work manifest only as observer/control-plane reference; do not require the live worker to read the full manifest.

Perform architecture preflight.

## Manual UI boundary
Do NOT inspect or search Scheduled Task UI.
Do NOT edit the Scheduled Task prompt/UI.

When the GitHub baseline is captured and start condition is safe, ask the user in this chat to manually press `Run now` exactly once on the existing `Taste Steam Review Dossier` Scheduled Task and reply `Запустил`.

Do not substitute any other trigger.
Do not manually dispatch any GitHub workflow.

## Required pre-run baseline
Record from current durable `main`:
- latest main commit;
- current canonical snapshot_id;
- prepared/completed/remaining counts;
- compact worker index blob/path and its canonical_expected_sequence N;
- exact descriptor N path/hash/appids;
- exact descriptor N+1 path/hash/appids;
- current relevant inbox state for N and N+1;
- current canonical manifest identity/hash bindings;
- proof contract + persistence bridge + repository worker prompt agree that compact worker projection is the active live descriptor read surface;
- latest relevant workflow/commit refs.

If deterministic artifact N already exists while canonical progress has not resolved it, do not request Run now until classified safe under contract.

## PASS criteria
One user-triggered Scheduled Task invocation must prove all of the following:

1. The live worker starts from the compact worker index, not from reconstructing a group out of the oversized full manifest.
2. It reads exact immutable descriptor N and publishes the deterministic create-only buffered artifact for N.
3. After successful publication of N, it proceeds to descriptor N+1 in the same invocation without waiting for canonical ingest/acceptance of N.
4. It publishes at least descriptor N+1's exact deterministic buffered artifact in that same invocation.
5. Exact descriptor/group identities/order match the GitHub-owned compact projection and canonical plan.
6. GitHub state-based drain accepts the correct maximal contiguous valid prefix in order and validates against the full canonical manifest.
7. Canonical progress advances by exactly the accepted item count; no skip, reorder, duplicate, replay, alternate filename, stale-snapshot application, or scope drift.
8. Accepted buffered artifacts are cleaned up according to contract.
9. Compact worker index advances consistently with canonical progress; same-snapshot descriptor files remain immutable.
10. Taste Semantic Producer remains unchanged.

One published 10-item group alone is NOT sufficient for PASS.

## Same-invocation proof
The important evidence is not merely that two groups eventually exist.

Use durable/tool trace evidence available from the live invocation and GitHub ordering to prove that the worker did not wait for canonical progress/ingest of N before starting/acquiring/publishing N+1.

If GitHub happens to ingest N very quickly due to a race, PASS is still possible only if evidence shows worker traversal to N+1 was independent of that canonical advancement.

Do not guess if ordering evidence is insufficient.

## Async observation
GitHub Actions may be queued/running while the worker continues publishing later groups. That is expected.

Use bounded rechecks. Do not spin indefinitely. If the single invocation clearly published >=2 groups but canonical drain is still unresolved after a reasonable bounded window, write `acceptance_pending_async_completion` with exact evidence rather than guessing.

## Failure classification
- Worker again attempts full-manifest reconstruction/read instead of compact projection -> `rejected` or `blocked` depending on exact cause.
- Compact index/descriptor unreadable/missing/inconsistent -> `blocked` if fail-closed and no writes.
- Only one group published with no real tool/platform blocker -> `rejected`.
- Real create/write/safety/platform failure on N+1 -> classify exact blocker; do not invent an architecture cause.
- Out-of-order/skip/alternate retry/overwrite/direct canonical mutation -> `rejected`.
- GitHub drain wrong advancement/duplicate/stale snapshot application -> `rejected`.
- Unobservable interruption -> apply PITFALL-004; exact cause unknown unless evidenced.

## Safety constraints
- Exactly one user-triggered Scheduled Task `Run now` for this acceptance.
- No second run.
- No manual GitHub workflow dispatch.
- No runtime/config/code changes.
- No synthetic production data.
- No Scheduled Task UI changes.
- No Taste Semantic Producer changes.

## Durable report
Write to `main`:
`reviews/worker_reports/taste-dossier-live-compact-acceptance-01.md`

Report must include:
- architecture preflight;
- exact pre-run baseline;
- user manual-run confirmation;
- compact index + descriptor N/N+1 identities;
- evidence the live worker used compact projection rather than full-manifest descriptor reconstruction;
- published artifact identities/commit ordering/timestamps;
- proof or non-proof that N+1 traversal/publication did not wait for canonical acceptance of N;
- relevant GitHub Actions runs/jobs/outcomes;
- canonical before/after counts and expected sequence;
- compact index before/after state;
- accepted-buffer cleanup state;
- no-duplicate/no-reorder/no-scope-drift assessment;
- Taste Semantic Producer unchanged assessment;
- exact verdict;
- explicit statement whether the multi-group same-invocation compact-read behavior was proven.

Allowed statuses:
- `accepted`
- `rejected`
- `blocked`
- `acceptance_pending_async_completion`

Stop after durable report. Do not start another Scheduled Task run.