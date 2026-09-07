# WORKER TASK — Taste Pre-AI Deal Contract Guard Fix Implement 01

## Task ID
`taste-pre-ai-deal-contract-guard-fix-implement-01`

## Mode
`IMPLEMENT / ACCEPTANCE`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/taste-pre-ai-deal-contract-guard-fix-implement-01.md`

## Direct predecessor
Read first:
`reviews/worker_reports/taste-canary-atomic-ingest-failure-recon-01.md`

Accepted predecessor conclusion:
- Prototype canary did not fail because of its semantic result;
- current committed pre-AI state is stale versus the newer mailing feed;
- the upstream atomic pre-AI refresh failed because `scripts/build_pre_ai_deal_scenarios.py` still accepts only `DEAL-QUALITY-AND-SORT-V1` version `1.3` while canonical `config/deal_quality_contract.json` is version `1.5`;
- this obsolete exact-version guard caused `Build pre-AI deterministic payload` run `33991072184` to abort before its atomic commit;
- the existing Prototype result is bound to the old snapshot and MUST NOT be reused after repair;
- a new one-row canary will be a later separate task only after fresh pre-AI state is successfully committed.

## Goal
Apply the smallest safe fix to align the deal-scenario builder with the current canonical deal-quality contract v1.5, then prove the normal atomic pre-AI refresh completes successfully and commits fresh state.

## Required implementation
1. Start from current `main`.
2. Read:
   - `CHAT_PROTOCOL.md`
   - `CHAT_CONTEXT.md`
   - `DIRECTOR_PROTOCOL.md`
   - predecessor report above;
   - `scripts/build_pre_ai_deal_scenarios.py`;
   - `config/deal_quality_contract.json`;
   - focused tests/validators for deal scenarios and pre-AI atomic refresh.
3. Change only the obsolete compatibility guard needed for the builder to accept the repository's current canonical `DEAL-QUALITY-AND-SORT-V1` version `1.5`.
4. Preserve fail-closed behavior for genuinely incompatible contract id/version/shape.
5. Add/update focused regression proving:
   - current canonical v1.5 is accepted;
   - incompatible/unexpected contract still fails closed.
6. Run the existing normal `Build pre-AI deterministic payload` route and prove it reaches the atomic commit successfully.
7. Prove committed pre-AI content metadata aligns with the then-current mailing source timestamp/current source state.

## Hard boundaries
Do NOT:
- run a new Taste semantic canary;
- enable the `Taste Semantic Producer`;
- create another Scheduled Task/producer/generation;
- reuse, relabel, patch or force-ingest the old Prototype result;
- manually edit generated pre-AI payload/queue/cache/receipt artifacts;
- weaken Taste exact binding checks;
- weaken atomic/fail-closed behavior;
- accept arbitrary future deal-quality contract versions;
- change Taste recommendation semantics/ranking;
- use paid OpenAI API or Copilot;
- work on UI/giveaways/other backlog.

Existing singleton must remain disabled/fail-closed:
`6a9d6fdddc00819193ed670d782045c4`

## Acceptance
Status `complete_ready_for_fresh_canary` only if:
1. canonical v1.5 contract is accepted by the deal-scenario builder;
2. incompatible contract regression still fails closed;
3. existing `Build pre-AI deterministic payload` workflow completes successfully;
4. atomic pre-AI commit occurs;
5. committed `content_metadata.source_updated_at_utc` aligns with the current mailing source;
6. fresh canonical Taste queue/bindings are committed;
7. old Prototype inbox/result has NOT been reused or accepted;
8. existing Taste Scheduled Task remains disabled;
9. no second producer/task/generation was created.

## Final status — exactly one
- `complete_ready_for_fresh_canary`
- `blocked`
- `needs_followup_fix`

## Required report
Save exactly:
`reviews/worker_reports/taste-pre-ai-deal-contract-guard-fix-implement-01.md`

Include:
- final status;
- exact code change;
- commit(s);
- focused regression evidence;
- exact pre-AI workflow run and result;
- proof atomic commit occurred;
- mailing timestamp vs committed content metadata timestamp;
- fresh queue/binding state summary;
- explicit confirmation old Prototype result was not reused;
- explicit confirmation existing producer stayed disabled and no second producer was created;
- whether Director may now schedule exactly one new fresh canary.

Do not start the fresh canary in this task.
