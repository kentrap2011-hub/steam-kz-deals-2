# WORKER TASK — Progressive Deep Runtime Adaptation 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repo by default or the repo target is ambiguous, stop and switch to kentrap2011-hub/steam-kz-deals-2 before doing any work.

Task ID: progressive-deep-runtime-adaptation-01
Mode: IMPLEMENT / VALIDATE
Worker slot: НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1

## START

First open the current `CHAT_PROTOCOL.md` from main and complete its START gate.
Then read and obey the current canonical architecture and accepted report:

- `config/progressive_personalization_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass2_contract.json`
- `config/execution_ownership_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- `reviews/worker_reports/progressive-fast-dossier-deep-architecture-amendment-01.md`
- `reviews/worker_reports/progressive-pass2-dossier-integration-activation-prep-01.md`
- `DIRECTOR_TASK_BOARD.md`

The accepted user model is `FAST-DOSSIER-DEEP-V1`.

## Confirmed starting state

- Fast/PASS 1 is provisional early analysis.
- Dossier is independent neutral evidence preparation.
- Deep/technical PASS 2 is eventual authoritative analysis for every current eligible game.
- Deep no longer requires prior Fast attempt or Fast `analysis_incomplete`.
- A current exact-compatible canonically accepted Dossier is the evidence gate for normal Deep work.
- Authoritative completed Deep suppresses future Fast for the same current identity.
- Fast success never suppresses eventual Deep coverage.
- Deep incomplete/error must not erase a valid current Fast provisional result.
- Deep first-pass failure moves into separate non-blocking GitHub-owned recovery.
- Existing GitHub recomputation wiring from the prior inactive PASS 2 implementation is reusable.
- Deep remains inactive and has consumed zero production attempts.

## Goal

Adapt the existing inactive PASS 2 runtime implementation to the accepted Deep architecture without activating production execution.

At completion, all runtime code, work projection, state/accounting, ingest/validation, Fast suppression rules, producer-owned stage observability, and statistics projection must match the accepted canonical architecture and be ready for a later separate activation task.

## 1. Deep normal-work eligibility

Replace the superseded Fast-incomplete-only runtime predicate.

Normal Deep first-pass work is eligible only when all current canonical conditions hold, including:

- item is in the current Progressive eligible scope;
- current semantic/work identity is exact and current;
- exact-compatible canonically accepted non-expired Dossier exists;
- no current authoritative completed Deep result exists for that Deep identity;
- the normal Deep first-pass attempt for that Deep identity has not already been consumed;
- the item is not recovery-owned from an already-consumed unresolved first pass;
- all current exact binding/liveness checks pass.

Explicitly prove:
- prior Fast attempt is not required;
- Fast outcome may be fit, not-fit, incomplete, error, or not-started without suppressing normal Deep work;
- Deep may therefore appear in the manifest before Fast is attempted.

## 2. Fast suppression after authoritative Deep

Adapt GitHub-owned Fast work projection so that:

- a current authoritative Deep completed fit/not-fit result suppresses future Fast work for that same current identity;
- existing Fast history is preserved;
- stale/non-current Deep results do not suppress current Fast;
- Deep incomplete/error/recovery-owned state does not suppress Fast if Fast has not yet consumed its own current attempt;
- no browser-side inference is used.

Do not otherwise change Fast semantic policy.

## 3. Deep state/accounting model

Adapt `data/cache/progressive_pass2_state.json` schema/runtime semantics from the old one-shot recovery model into explicit Deep first-pass + recovery accounting.

Required concepts:

### Normal first pass
For each current Deep identity, represent enough canonical state to distinguish:
- not started / waiting for Dossier;
- eligible/pending;
- first-pass consumed;
- authoritative completed;
- unresolved and moved to recovery-owned.

A consumed unresolved first pass must:
- count as normal first-pass attempted/accounted;
- not count as authoritative completion;
- leave the item visible as needing Deep recovery;
- stop normal first-pass re-emission for that identity.

### Recovery
Implement a separate GitHub-owned recovery authorization/accounting path sufficient to represent:
- `recovery_owned`
- `recovery_eligible`
- `recovery_pending`

Every recovery attempt must carry:
- exact current semantic/work identity;
- exact current Dossier/evidence or defect-fix binding;
- `recovery_authorization_id`;
- explicit canonical `recovery_reason`;
- immutable result/receipt binding.

No blind retry loop.
No time-based implicit retry.
No hidden fixed retry quota.
A recovery attempt may be emitted only from an explicit current GitHub-owned authorization satisfying the canonical contract.

If the current repository has no operator-facing recovery-authorize entrypoint, implement the smallest GitHub-owned bounded entrypoint/schema needed to create a recovery authorization without creating a recurring worker, queue owner, or autonomous retry system.

## 4. Effective-result precedence

Adapt the final producer/projection logic so that:

- current authoritative completed Deep fit/not-fit is the effective personalized result;
- otherwise current trustworthy Fast fit/not-fit remains provisional effective truth;
- Deep incomplete/error/recovery-owned does not erase a valid Fast fit/not-fit;
- if neither has a trustworthy completed result, existing unresolved/not-analyzed semantics apply;
- Fast and Deep histories/provenance remain distinct.

Do not alter ranking weights. Only ensure the current effective result source is correct.

## 5. Producer-owned per-game stage fields

Emit explicit presentation fields for each current game so the browser never reconstructs stage state.

At minimum expose:

### Fast
- `fast_stage_state`: `not_started | completed | incomplete | error`
- `fast_stage_outcome`: `fit | not_fit | null`

### Dossier
- `dossier_stage_state`: `not_ready | accepted | failed_or_recovery`

### Deep
- `deep_stage_state`: `not_started | waiting_for_dossier | eligible_or_pending | completed | incomplete_or_recovery`
- `deep_stage_outcome`: `fit | not_fit | null`
- `deep_recovery_state`: `none | recovery_owned | recovery_eligible | recovery_pending`

### Effective source
- `effective_analysis_source`: `deep | fast | none`

Names may differ only if a stronger existing canonical naming convention already exists; document the exact final names in the report.

These are producer-owned presentation fields, not browser-derived logic.

## 6. Producer-owned statistics fields

Expose the accepted stage-specific statistics in the GitHub-produced visual payload or another canonical presentation object consumed by the site.

Required Fast metrics:
- total current scope;
- attempted;
- completed fit;
- completed not-fit;
- incomplete;
- error;
- skipped due to authoritative Deep;
- remaining.

Required Dossier metrics:
- total current scope;
- accepted;
- pending;
- failed/recovery-owned;
- normal-first-pass complete;
- all-accepted-or-recovered complete.

Required Deep metrics:
- total current coverage target;
- first-pass attempted;
- authoritative completed;
- completed fit;
- completed not-fit;
- incomplete/recovery;
- waiting for Dossier;
- ready/pending;
- normal first-pass remaining;
- remaining until all authoritative;
- normal first-pass complete;
- all-current authoritative complete.

Do not merge scopes/denominators.

Dossier observability must remain non-blocking for core site publication. If Dossier statistics cannot be read, preserve the normal site payload and emit an explicit unavailable/null observability state rather than failing core deal publication.

## 7. Recompute trigger graph

Preserve and adapt the already-landed GitHub-owned recomputation triggers:

- canonical Dossier acceptance/recovery persistence;
- Fast/PASS 1 persistence;
- daily/current semantic generation/work/binding refresh;
- Deep result/receipt persistence;
- Deep recovery authorization changes if a new bounded authorization artifact is introduced.

Recompute remains:
- idempotent;
- zero-attempt;
- GitHub-owned;
- exact-bound;
- non-blocking across siblings.

## 8. Inactive-state migration

The currently generated inactive Deep work manifest may still contain items produced under the obsolete Fast-incomplete-only runtime predicate.

Regenerate/rewrite only through the canonical GitHub-owned builder after runtime adaptation so the inactive projection reflects the new architecture.

This projection must consume zero Deep attempts.

Any existing zero-entry Deep durable state remains valid only if schema-compatible; migrate deterministically if needed.

Do not fabricate historical Deep attempts.

## 9. Worker prompt / schemas / ingest

Update the inactive Deep worker prompt/result/receipt/state/work schemas as needed so that future activation is unambiguous.

Worker behavior after future activation must distinguish:
- normal first-pass Deep work;
- explicitly authorized recovery Deep work.

The worker must never:
- choose recovery itself;
- infer a retry reason;
- reconstruct queue scope;
- modify Fast/Dossier state;
- edit its Scheduled Task.

GitHub owns validation, persistence, current liveness, recovery authorization, and accounting.

## Activation guard

Throughout this task keep every Deep/PASS 2 activation mirror false.

Do NOT:
- create/edit/enable/run a Deep Scheduled Task;
- run production Deep semantic execution;
- create a real production Deep result;
- create a real production Deep terminal receipt;
- consume a normal Deep or recovery attempt;
- process a production Deep backlog;
- implement the final pixel icon design or Statistics page UI.

Inactive work projection and visual/statistics projection from real canonical state are allowed because they consume zero attempts.

## Validation

Prove at minimum:

- DEEP-01: a current eligible game with accepted compatible Dossier and no Fast attempt can enter normal Deep work.
- DEEP-02: Fast fit does not suppress Deep work.
- DEEP-03: Fast not-fit does not suppress Deep work.
- DEEP-04: Fast incomplete/error does not block Deep work.
- DEEP-05: authoritative completed current Deep suppresses future Fast work.
- DEEP-06: stale/non-current Deep does not suppress current Fast.
- DEEP-07: Deep fit/not-fit supersedes Fast as effective result.
- DEEP-08: Deep incomplete/error preserves a valid Fast provisional effective result.
- DEEP-09: one normal unresolved Deep attempt moves only that item to recovery-owned and does not block siblings.
- DEEP-10: normal first-pass work does not automatically re-emit recovery-owned identities.
- DEEP-11: recovery work requires explicit GitHub-owned recovery authorization with reason/binding.
- DEEP-12: no blind retry loop / time retry / hidden fixed recovery quota exists.
- DEEP-13: first-pass completeness and all-authoritative completeness are distinct and reconcile.
- DEEP-14: per-game Fast/Dossier/Deep stage fields are producer-owned and exact.
- DEEP-15: stage statistics reconcile independently without false shared denominators.
- DEEP-16: Dossier statistics failure cannot block core visual publication.
- DEEP-17: current inactive Deep manifest is regenerated under the new predicate with zero attempt consumption.
- DEEP-18: Fast/Dossier canonical semantic histories are not rewritten.
- DEEP-19: existing recomputation/concurrency/exact-binding safeguards remain intact.
- DEEP-20: Deep remains inactive; production Deep attempts remain zero.
- DEEP-21: relevant focused/canonical regressions pass.
- DEEP-22: durable report is committed and reread from main before completion.

## Durable report

Create and commit:

`reviews/worker_reports/progressive-deep-runtime-adaptation-01.md`

Keep it compact and include:
- exact runtime changes;
- old vs new Deep eligibility predicate;
- state/schema migration;
- exact first-pass vs recovery accounting;
- Fast suppression behavior;
- effective-result precedence proof;
- exact producer-owned stage field names;
- exact statistics field names and current inactive projected counts;
- recomputation trigger graph;
- validation DEEP-01..22;
- proof all activation flags remain false and attempts remain zero;
- exact refs;
- final status;
- exactly one recommended next step.

Allowed statuses:
- complete_runtime_ready_for_activation
- complete_ready_for_director_acceptance
- needs_fix
- blocked_external_operator_action
- needs_user_decision

Before final response, commit the report and reread the exact report from main.
