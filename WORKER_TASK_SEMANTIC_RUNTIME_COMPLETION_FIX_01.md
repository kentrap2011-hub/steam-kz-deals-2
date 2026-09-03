# WORKER TASK — SEMANTIC RUNTIME COMPLETION FIX 01

Task ID: `semantic-runtime-completion-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/semantic-runtime-completion-fix-01.md`

## Source decision

Direct continuation of:
- `reviews/system_audits/baseline-01.md`
- `reviews/worker_reports/semantic-runtime-completion-acceptance-01.md`

Acceptance result:
- `Semantic runtime observability`: `fail`
- `Feed semantic completeness visibility`: `fail`
- status: `needs_fix`

Do not repeat the acceptance or re-diagnose Trine 4.

## Goal

Fix exactly two system-level defects without changing Taste semantics or creating another runtime.

### A. Durable observability for the existing canonical Taste runtime

Add a durable operational signal for the **existing** scheduled semantic Taste owner that is sufficient to establish current liveness/progress independently of queue existence.

The canonical evidence must expose, directly or through an equivalent trustworthy proof:
- whether the existing semantic owner is operationally active/expected to run;
- expected cadence / next-run expectation when the platform exposes it, otherwise the nearest durable equivalent permitted by the existing architecture;
- last successful semantic execution or last accepted semantic progress;
- queue progress tied to the current prepared semantic scope, not merely queue presence.

If the scheduled-ChatGPT platform cannot expose enabled/schedule/next-run fields to the repository, do **not** invent them. Persist the smallest equivalent heartbeat/progress receipt that the existing runtime can truthfully produce through the current canonical interface.

### B. Truthful semantic completeness state

Remove the current ambiguity where partition/accounting completion can look like semantic-result completion.

The canonical publication/status path must distinguish at minimum:
- source/family partitioning completed;
- semantic work still materially unresolved / degraded;
- semantic result sufficiently complete/current for publication acceptance.

Expose at minimum:
- unresolved semantic count;
- total relevant semantic scope;
- unresolved age/staleness when it can be derived truthfully from existing canonical timestamps;
- a non-ambiguous semantic completeness/degraded state.

A state equivalent to `status=complete` must no longer be interpretable as full semantic completion when hundreds of required semantic rows remain unresolved.

## Ownership and boundaries

Preserve `config/execution_ownership_contract.json`:
- one existing scheduled ChatGPT semantic runtime only;
- GitHub owns queue preparation, validation, persistence, completeness and downstream rebuild;
- no interactive worker item-by-item processing.

Do NOT:
- create a second scheduler, queue, runtime or manual Taste path;
- manually judge Trine 4 or any other game;
- change Taste policy, weights, scores, ranking, exclusion thresholds or fail-closed semantic safety;
- weaken readiness gates merely to make more games appear;
- redesign the UI;
- broaden into unrelated stale-data/provider work.

Primary implementation surface should stay within the existing semantic runtime status/receipt interface, the canonical pre-AI/publication status path, and the smallest tests/contracts needed. `scripts/build_visual_feed_v2.py`, `data/production/pre_ai/chatgpt_payload.json` generation, and `config/execution_ownership_contract.json` are in scope only as needed for these two mechanisms.

If a required platform-side semantic-runtime change cannot be made from the available worker surface, implement all safe repo-side pieces, then stop with an exact blocker and the smallest user/platform action required. Do not substitute a new automation.

## Required validation

Prove at least:
1. A non-empty queue with no recent semantic progress cannot be reported as healthy semantic completion merely because partitioning finished.
2. Semantic progress/heartbeat evidence changes when the existing canonical runtime successfully advances accepted work.
3. The published/canonical status clearly reports unresolved semantic scope and degraded/incomplete state while work remains materially unresolved.
4. Existing Taste semantics and single-owner execution contract remain unchanged.
5. Existing tests plus new focused tests pass.

Use bounded validation; do not manually process the production queue.

## Required result

Report:
1. exact implementation performed;
2. exact durable runtime heartbeat/progress mechanism;
3. exact semantic completeness/degraded contract;
4. validation evidence;
5. any remaining external/platform blocker;
6. whether follow-up acceptance is ready now.

Status exactly one:
- `complete`
- `blocked`
- `needs_user_action`
- `needs_followup_fix`

## Completion

Save:
`reviews/worker_reports/semantic-runtime-completion-fix-01.md`

Final answer must state exact report path, status and exact refs.