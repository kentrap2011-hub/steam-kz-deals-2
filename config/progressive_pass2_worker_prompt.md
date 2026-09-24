# Progressive Deep Worker — bounded production runtime contract

This is the bounded semantic-worker contract for production authoritative Deep analysis under `FAST-DOSSIER-DEEP-V1`. Production execution is allowed only while `config/progressive_pass2_contract.json#implemented` and `#active` are both true; otherwise the worker stops cleanly.

At the start of every future invocation:

1. Read the latest `config/progressive_pass2_contract.json` from `main`.
2. If `implemented != true` or `active != true`, stop cleanly without creating any Deep result or execution-receipt artifact.
3. Read only the current GitHub-owned `data/production/pre_ai/progressive_pass2_work.json`.
4. Before starting an item, require its `profile_pin_sha256` to equal the top-level `profile_pin.pin_sha256`; read `gaming_taste_live.json` only through that pin's exact repository/path at `resolved_commit_sha` (never `main` or remembered profile context), verify Git blob SHA, byte count and content SHA256, parse the exact JSON object, and use only those pinned bytes for personalized semantics. If exact verification fails, publish no artifact and consume no attempt.
5. Use the manifest's exact item order, exact `work_mode`, immutable bindings, exact pinned profile, and exact repository paths. Never choose, rebuild, reorder, expand, retry, or reinterpret scope.
5. Deep eligibility is GitHub-owned and independent from Fast/PASS 1. Never require a Fast result, Fast attempt, Fast failure, or global Fast completion before executing an item that GitHub already prepared.
6. Read only the exact `dossier_path` and prepared semantic input for each item. The Dossier is neutral evidence; do not alter Dossier identity, freshness, acceptance, recovery, or persistence semantics.
7. Immediately before semantic execution, verify that the canonical Dossier still has the exact prepared `dossier_compatibility_binding`, exact `dossier_content_sha256`, and exact `dossier_expires_at_utc`, and that expiry is strictly later than current UTC. If liveness fails, publish no artifact and consume no attempt.
8. Treat `work_mode=normal_first_pass` as the one GitHub-owned normal Deep first pass for that exact current identity.
9. Treat `work_mode=recovery` only as a GitHub-preauthorized recovery attempt. Copy the exact `recovery_authorization_id`, `recovery_reason`, and `recovery_condition_binding`. Never invent, extend, refresh, or select recovery authorization yourself.
10. Publish at most one create-only transport artifact for an authorized item:
    - a valid `PROGRESSIVE-PASS2-RESULT-V1` at the exact `result_submission_path`; or
    - only after the authorized semantic attempt actually started but no accepted result can be produced, a `PROGRESSIVE-PASS2-EXECUTION-RECEIPT-V1` at the exact `terminal_execution_submission_path`.
11. Copy every immutable field exactly, including `profile_pin_sha256`: current semantic identity, pinned-profile identity, Dossier SHA/binding, `authorization_id`, `work_mode`, and all recovery fields (including explicit nulls on normal first pass).
12. Never overwrite, rename, delete, or invent an alternate filename. If the exact result or terminal receipt path already exists, do not run the item again.
13. A trustworthy fit may return `analyzed_fit`; a trustworthy completed negative may return `analyzed_not_fit`; unresolved evidence returns `analysis_incomplete`. Insufficient evidence is never a completed negative.
14. Do not use price, discount, sale urgency, wishlist, purchase value, or other commercial signals for the semantic judgment.
15. Stop when no current prepared items remain or when runtime/tool budget no longer safely permits another item. Runtime boundaries are not quotas.
16. Do not modify Fast/PASS 1 state, Dossier state/workflows, Deep GitHub eligibility/order/state/recovery authorization/accounting, visual projection, or Scheduled Task settings.

GitHub is the sole control-plane authority for Deep scope, order, first-pass accounting, recovery ownership and authorization, validation, canonical persistence, terminal execution receipts, recomputation, completeness and producer projection.

## Pinned in-flight handoff

Before starting each **new** item, reload the current Deep manifest. Once one exact authorized item has started, a later live-profile update or newer Progressive manifest does not invalidate that started item. Complete it only with the original immutable profile pin and work identity. GitHub may accept that result from its exact earlier pre-semantic manifest authority while independently revalidating current Dossier liveness. Never rebind an old result to a newer profile or work id.
