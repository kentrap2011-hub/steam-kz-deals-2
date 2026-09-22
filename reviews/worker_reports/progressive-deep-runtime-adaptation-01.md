# Progressive Deep Runtime Adaptation 01

Task: `progressive-deep-runtime-adaptation-01`  
Accepted model: `FAST-DOSSIER-DEEP-V1`  
Status: `complete_ready_for_director_acceptance`

## Runtime changes

- Deep/PASS 2 normal work now covers every current exact Progressive identity with a current exact-compatible, canonically accepted, non-expired Dossier and no current authoritative Deep completion. Fast/PASS 1 is not an eligibility prerequisite.
- `scripts/progressive_pass2.py` now separates `normal_first_pass` from `recovery`, keeps exact immutable authorization bindings, records authoritative completion separately from attempted work, and never normal-reemits recovery-owned identities.
- Recovery is GitHub-owned. `scripts/authorize_progressive_pass2_recovery.py` plus manual-only `.github/workflows/authorize-progressive-pass2-recovery.yml` create one exact fresh recovery authorization for one recovery-owned identity. No recurring recovery worker, time retry, blind loop, or hidden quota was added.
- Result/terminal-receipt schemas and the inactive worker prompt now carry `work_mode`, `recovery_authorization_id`, `recovery_reason`, and `recovery_condition_binding`; the semantic worker never chooses recovery.
- Fast projection now suppresses future Fast only after current authoritative Deep fit/not-fit. Deep incomplete/error/recovery-owned and stale/non-current Deep do not suppress Fast.
- Producer precedence is authoritative Deep fit/not-fit > trustworthy current Fast fit/not-fit > unresolved/not-analyzed. Deep incomplete/error does not erase a valid Fast provisional result. Ranking weights are unchanged.
- Dossier statistics are presentation-only observability; unreadable Dossier progress yields explicit unavailable/null metrics and does not block the normal deal payload.

## Old vs new Deep predicate

Old runtime predicate: current Fast/PASS 1 had to exist and be `analysis_incomplete`, then an accepted compatible Dossier could make that identity PASS 2 eligible.

New normal-first-pass predicate: current Progressive identity + exact current semantic/work binding + exact-compatible accepted non-expired Dossier + no authoritative current Deep + normal first pass unconsumed + not recovery-owned + current liveness. Fast may be `fit`, `not_fit`, `incomplete`, `error`, or `not_started`; none of those states suppress normal Deep.

## State/schema migration and accounting

`data/cache/progressive_pass2_state.json` migrated deterministically from empty `PROGRESSIVE-PASS2-STATE-V1` to empty `PROGRESSIVE-PASS2-STATE-V2`. Non-empty V1 state is explicitly rejected by the runtime migration guard. No historical attempt was fabricated.

For each exact current Deep identity:
- normal first pass has exactly one automatic attempt budget;
- an unresolved consumed first pass sets `normal_first_pass_attempted=true`, `authoritative_completed=false`, and `recovery_owned=true`;
- normal first-pass recomputation cannot emit that identity again;
- every recovery attempt requires a fresh GitHub authorization with exact current identity, exact Dossier/evidence or defect-fix binding, canonical reason, and immutable authorization ID;
- recovery history is separate from the normal first-pass budget; there is no fixed recovery-attempt quota.

Current durable Deep state remains exactly zero-entry V2.

## Producer-owned stage fields

Every producer-built current game carries:
- `fast_stage_state`: `not_started | completed | incomplete | error`
- `fast_stage_outcome`: `fit | not_fit | null`
- `dossier_stage_state`: `not_ready | accepted | failed_or_recovery`
- `deep_stage_state`: `not_started | waiting_for_dossier | eligible_or_pending | completed | incomplete_or_recovery`
- `deep_stage_outcome`: `fit | not_fit | null`
- `deep_recovery_state`: `none | recovery_owned | recovery_eligible | recovery_pending`
- `effective_analysis_source`: `deep | fast | none`

These are producer-owned fields; no browser-side stage reconstruction or final pixel-icon/Statistics-page UI was implemented.

## Producer statistics and current inactive projection

Fast fields: `fast_total_current_scope`, `fast_attempted_count`, `fast_completed_fit_count`, `fast_completed_not_fit_count`, `fast_incomplete_count`, `fast_error_count`, `fast_skipped_due_to_authoritative_deep_count`, `fast_remaining_count`.

Current Fast projection: total **540**; attempted **60** = fit **0** + not-fit **0** + incomplete **57** + error **3**; skipped due to authoritative Deep **0**; remaining **480**.

Dossier fields: `dossier_total_current_scope`, `dossier_accepted_count`, `dossier_pending_count`, `dossier_failed_or_recovery_count`, `dossier_normal_first_pass_complete`, `dossier_all_accepted_or_recovered_complete`, plus `dossier_observability`.

Current Dossier projection: total **556**; accepted **18**; pending **532**; failed/recovery **6**; normal-first-pass complete **false**; all accepted/recovered complete **false**; observability `available`.

Deep fields: `deep_total_current_coverage_target`, `deep_first_pass_attempted_count`, `deep_authoritative_completed_count`, `deep_completed_fit_count`, `deep_completed_not_fit_count`, `deep_incomplete_or_recovery_count`, `deep_waiting_for_dossier_count`, `deep_ready_or_pending_count`, `deep_normal_first_pass_remaining_count`, `deep_remaining_until_all_authoritative_count`, `deep_normal_first_pass_complete`, `deep_all_current_authoritative_complete`.

Current regenerated inactive Deep projection: target **540**; first-pass attempted **0**; authoritative completed **0**; completed fit **0**; completed not-fit **0**; incomplete/recovery **0**; waiting for Dossier **523**; ready/pending **17**; normal first-pass remaining **540**; remaining until all authoritative **540**; both completion flags **false**. Recovery-owned/eligible/pending attempt counts are all **0**. The 17 ready items are inactive work projection only; no semantic execution occurred.

## Recompute trigger graph

All current eligibility writers stay under GitHub control and the existing `taste-steam-review-dossier-canonical-writer` concurrency boundary with `cancel-in-progress:false`:
1. canonical Dossier acceptance/recovery persistence;
2. Fast/PASS 1 persistence;
3. daily/current semantic generation/work/binding/freshness preparation;
4. future Deep result/terminal-receipt persistence;
5. explicit bounded Deep recovery authorization.

Recompute is idempotent, zero-attempt, exact-bound, and sibling-nonblocking.

## Validation DEEP-01..22

- DEEP-01..04: normal Deep is proven eligible with Fast not-started, fit, not-fit, incomplete/error; Fast never gates Deep.
- DEEP-05..08: authoritative current Deep suppresses future Fast and supersedes Fast; stale/non-current or unresolved Deep does not suppress/erase valid current Fast.
- DEEP-09..12: unresolved first pass moves only that identity to recovery ownership; normal work does not reemit it; recovery requires fresh explicit GitHub authorization; repeated/time-based recomputation cannot create a blind retry or hidden quota.
- DEEP-13: normal first-pass completeness and all-authoritative completeness reconcile separately.
- DEEP-14..16: exact producer stage fields and independent stage denominators reconcile; Dossier observability failure is non-blocking.
- DEEP-17: canonical builder regenerated `data/production/pre_ai/progressive_pass2_work.json` under the new predicate with 17 ready/pending items and zero attempts.
- DEEP-18..19: Fast/Dossier semantic histories remain untouched; exact binding, ingest-time recomputation, and existing serialized GitHub ownership remain intact.
- DEEP-20: every Deep/PASS 2 activation mirror remains false and durable Deep attempt count remains zero.
- DEEP-21: GitHub Actions run `35771238162` at head `57bb59c63cef69632154861efb988658dd0e08c1` passed compile, Deep core/integration, PASS 1, personalization, unresolved-row, visual-routing, UI provenance, real Fast/Dossier accounting, and inactive Deep recomputation checks.
- DEEP-22: completion gate is to commit this report to `main` and reread this exact path from `main` before the final chat response; the final reread is performed after integration.

## Activation proof

`config/progressive_pass2_contract.json#active=false`; `activation_guard.deep_active=false`; `production_execution_authorized=false`; `real_backlog_processing_allowed=false`; Progressive mirrors keep `pass2_active=false`. Durable V2 Deep state has `entries={}`; regenerated work has `pass2_active=false`, `deep_first_pass_attempted_count=0`, `deep_authoritative_completed_count=0`, `deep_incomplete_or_recovery_count=0`, and `recovery_pending_count=0`.

No Deep Scheduled Task was created, edited, enabled, or run. No production Deep result or terminal receipt was created. No production Deep backlog was processed. No final pixel-icon or Statistics-page UI was implemented.

## Exact refs

- Repository: `kentrap2011-hub/steam-kz-deals-2`
- START/source branch: `main`
- START task-state commit: `21b749e3d4d427c28cd02474695183fc359e1595`
- Implementation validation head: `57bb59c63cef69632154861efb988658dd0e08c1`
- Validation workflow run: `35771238162`
- Semantic generation in regenerated Deep manifest: `334bee04617cc4a43fe300a26d62a3ef3af4e1469eb313c352e37fb39fc0213d`
- Deep state contract: `PROGRESSIVE-PASS2-STATE-V2`
- Deep work contract: `PROGRESSIVE-PASS2-WORK-V1` schema version 2
- Recovery authorization contract: `PROGRESSIVE-PASS2-RECOVERY-AUTHORIZATION-V1`
- Main integration commit and DEEP-22 reread: recorded after integration in the final completion gate.

## Recommended next step

Exactly one next step: Director reviews/accepts this runtime adaptation and, only in a separate follow-up task, explicitly authorizes Deep/PASS 2 activation.
