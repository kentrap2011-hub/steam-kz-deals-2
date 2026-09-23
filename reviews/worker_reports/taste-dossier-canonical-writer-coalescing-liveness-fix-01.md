# Taste Dossier Canonical-Writer Coalescing Liveness Fix 01

**Task:** `taste-dossier-canonical-writer-coalescing-liveness-fix-01`  
**Repository / source of truth:** `kentrap2011-hub/steam-kz-deals-2` / `main`  
**Final status:** `complete_ready_for_director_acceptance`

## Result

The cancelled/coalesced Dossier wake-up hole is closed inside the existing single GitHub-owned `taste-steam-review-dossier-canonical-writer` boundary.

The durable authority is repository state, not the original workflow event. Every surviving workflow in that shared writer domain now runs the existing state-based Dossier inbox reconcile and validation projection before any dependent Deep projection/write that can use Dossier truth. No second scheduler, concurrency domain, polling loop, retry daemon, queue owner, or ChatGPT-side inbox interpretation was added.

## Exact shared-writer inventory

A bounded scan of all 63 `.github/workflows/*.yml` files found exactly five workflows using the exact shared concurrency group:

1. `.github/workflows/build-pre-ai-store-snapshot.yml`
2. `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
3. `.github/workflows/ingest-progressive-pass1.yml`
4. `.github/workflows/ingest-progressive-pass2.yml`
5. `.github/workflows/authorize-progressive-pass2-recovery.yml`

The first two already reconciled Dossier inbox state. The fix added the same existing GitHub-owned reconcile/validation path to PASS 1, PASS 2, and explicit Deep recovery authorization.

## Implementation and ordering

For each of the three previously missing writer paths:

- run `python scripts/ingest_taste_steam_review_dossier_inbox.py --reconcile-nonfatal`;
- run `python scripts/taste_steam_review_dossier_parallel_validation.py`;
- stage the canonical Dossier cache/work/index/validation/inbox plus existing quarantine/audit outputs in the writer commit;
- preserve `cancel-in-progress: false` and the same shared concurrency group.

Ordering is explicit:

- pre-AI: prepare current Dossier backlog → Dossier reconcile → validation projection → Deep work recomputation;
- Dossier ingest: recovery request handling → Dossier reconcile → validation projection → Deep work recomputation;
- PASS 1: Dossier reconcile → validation projection → PASS 1 ingest → Deep work recomputation;
- PASS 2: Dossier reconcile → validation projection → Deep work recomputation → PASS 2 ingest/revalidation;
- Deep recovery authorization: Dossier reconcile → validation projection → exact recovery authorization, whose existing script recomputes Deep work from canonical state.

PASS 2's final commit is no longer gated by the PASS 2 activation guard, so a surviving PASS 2 writer can persist Dossier reconciliation even when no PASS 2 semantic ingest is authorized.

No Dossier validator, deterministic candidate pathname, snapshot/group identity, create-only rule, overwrite/rename/skip rule, per-group progress model, Fast semantics, Deep semantics/recovery model, or ranking weight changed.

## Regression

Added `scripts/test_taste_dossier_canonical_writer_coalescing_liveness.py` and wired it into the existing read-only `Validate buffered Steam review dossier runtime` PR gate.

The regression reproduces the required causal state generically, without historical sequence/snapshot special-casing:

1. an exact current candidate exists durably while canonical group state is still `pending` (the state after an original zero-job wake-up is lost);
2. a surviving shared writer reconciles from repository state;
3. a valid candidate is accepted/persisted once and removed from normal pending traversal;
4. a repeated surviving-writer reconcile performs zero additional classifications/persistence;
5. an invalid candidate is failed/quarantined/recovery-owned once and a repeated reconcile does not fail it again;
6. before canonical persistence, transport alone unlocks no Deep work;
7. after canonical persistence, Deep recomputation sees the accepted Dossier store;
8. a static inventory/order assertion proves exactly the five shared writers all contain the state-based reconcile/validation path and no `schedule:` owner was introduced.

The first PR Dossier run `35814891568` failed only inside the new test because its generic Deep fixture had a release-year mismatch and an anti-hardcode assertion contained the historical literal it was checking for. The test fixture was corrected without weakening the semantic assertions. The next run `35814982291` (#142) passed the full pre-existing Dossier suite and the new coalescing regression.

## Idempotence and liveness closure

The original Dossier workflow event is now advisory only. If its pending run is cancelled before job start, the next surviving shared writer checks the current inbox and classifies any exact current candidate through the same strict GitHub-owned drain.

After valid classification, canonical `group_progress` is accepted, `next_pending_sequence` no longer points to that group, the transport candidate is consumed, and repeated reconcile reports zero accepted/failed groups for that candidate. After invalid classification, the group enters the existing `failed_or_invalid_pending_recovery` state once and is not reclassified by a later normal reconcile.

Therefore the semantic worker cannot remain falsely authorized solely because the original wake-up disappeared, and the same exact deterministic candidate path is not recreated from stale canonical `pending` state.

## Files changed in implementation PR #90

- `.github/workflows/ingest-progressive-pass1.yml`
- `.github/workflows/ingest-progressive-pass2.yml`
- `.github/workflows/authorize-progressive-pass2-recovery.yml`
- `.github/workflows/validate-taste-dossier-buffered.yml`
- `scripts/test_taste_dossier_canonical_writer_coalescing_liveness.py`
- `PROJECT_ROUTES.md`
- `KNOWN_WORKER_PITFALLS.md`
- `CURRENT_TASK.md`

Task bookkeeping was subsequently closed on `main` in commit `bbce21515267aa2280eaff65c924852fb9506e77`.

## Validation gates

- **LIV-01 PASS:** exact shared-writer set enumerated as the five workflows above; all 63 workflow files were checked.
- **LIV-02 PASS:** every shared writer uses the existing state-based `--reconcile-nonfatal`; classification does not depend on event type.
- **LIV-03 PASS:** generic lost-zero-job-wake-up state is reconciled by the surviving writer and no longer remains falsely pending.
- **LIV-04 PASS:** valid current candidate is accepted/persisted exactly once; second reconcile is a no-op.
- **LIV-05 PASS:** invalid current candidate enters existing failed/quarantine/recovery state exactly once; second reconcile is a no-op.
- **LIV-06 PASS:** repeated reconciliation is explicitly covered for both valid and invalid outcomes.
- **LIV-07 PASS:** stale/current snapshot logic was not modified; existing daily snapshot/strict recovery regressions passed in Dossier run `35814982291`.
- **LIV-08 PASS:** deterministic pathname/create-only/snapshot/group rules were not modified.
- **LIV-09 PASS:** Scheduled semantic worker ownership is unchanged; no inbox interpretation moved into ChatGPT.
- **LIV-10 PASS:** regression proves transport alone gives no Deep authorization, while post-reconcile canonical Dossier truth is visible to Deep; workflow ordering requires reconcile before dependent recomputation.
- **LIV-11 PASS:** no second concurrency domain, scheduler, polling loop, retry daemon, queue owner, or hidden retry was introduced.
- **LIV-12 PASS:** required coalescing/lost-wake-up regression passed in run `35814982291`.
- **LIV-13 PASS:** the full existing buffered Dossier regression suite passed in run `35814982291`.
- **LIV-14 PASS:** no production Fast/PASS 1 or Deep/PASS 2 semantic state file was changed by implementation PR #90; Deep core/integration gate `35814982336` (#105) passed.
- **LIV-15 PASS:** historical `g000012` was not restored, recovered, rewritten, renamed, rebound, or special-cased.
- **LIV-16 PASS:** no Scheduled Task setting/action occurred; this task did not create/edit/enable/disable/pause/resume/reschedule/run the Taste Steam Review Dossier task.
- **LIV-17 PASS:** Dossier gate `35814982291`, Progressive PASS 2 core gate `35814982336`, and backlog disposition gate `35814982293` all completed successfully on the final PR head.
- **LIV-18 PASS:** this durable report is committed on `main` and is reread from exact `main` bytes before completion.

## Historical / scheduler / Deep guards

The superseded historical `g000012` incident remains diagnostic history only; no historical artifact or state was recovered.

No Dossier Scheduled Task prompt, cadence, enabled state, or execution action was changed or invoked by this task. Any automatic repository workflows observed after merge were normal GitHub-triggered repository activity, not a manual Dossier `Run now` or scheduler mutation.

The separate ЧАТ 2 Deep activation task/branch/report/scheduler ownership was not modified by this implementation. Its independently merged Deep fix remains separate from PR #90.

The stale-cleanup observability discrepancy from the earlier diagnostic remains out of scope and was not redesigned.

## Exact refs

- START protocol blob: `38e4891059d71fd16da39bae8e7bbeec684fc56a`
- task blob: `4024ff4fe3ae04200d698484470ba71c1c6a6c36`
- accepted root-cause diagnostic report blob: `1d56caf85e54eeb7791cb6a9a91f6b893656ff68`
- implementation PR: #90
- final implementation PR head: `4f2ff99c44adf098230c90735ac787cda3902b3b`
- implementation merge: `e69eb97a678636ea78b2aaac52ff07785c119f0d`
- task bookkeeping close: `bbce21515267aa2280eaff65c924852fb9506e77`
- successful Dossier validation: run `35814982291` (#142)
- successful Progressive PASS 2 validation: run `35814982336` (#105)
- successful backlog validation: run `35814982293` (#1029)

## Recommended next step

Director accepts this fix; after acceptance, if the existing Taste Steam Review Dossier Scheduled Task is externally disabled, its owning operator may restore that existing task separately.
