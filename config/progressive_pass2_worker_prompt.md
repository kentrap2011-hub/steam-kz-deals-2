# Progressive PASS 2 Worker — inactive future runtime contract

This file is the bounded semantic-worker contract for future PASS 2 execution. It is implemented in the repository but MUST NOT execute production work while `config/progressive_pass2_contract.json#active` is false.

At the start of every future invocation:

1. Read the latest `config/progressive_pass2_contract.json` from `main`.
2. If `implemented != true` or `active != true`, stop cleanly without creating any result or execution-receipt artifact.
3. Read only the current GitHub-owned `data/production/pre_ai/progressive_pass2_work.json`.
4. Use its exact item order, exact immutable bindings and exact repository paths. Never choose, rebuild, reorder, expand, retry, or reinterpret scope.
5. For each item, read only its exact `dossier_path` plus the prepared semantic input. The dossier is neutral evidence; do not alter Dossier evidence, identity, freshness, or acceptance semantics.
6. Immediately before starting semantic execution for an item, verify that the canonical dossier still has the exact prepared `dossier_compatibility_binding`, that its exact `expires_at_utc` equals the prepared `dossier_expires_at_utc`, and that this expiry is strictly later than current UTC. If any liveness check fails, publish no result or terminal receipt for that item, consume no attempt, and do not rebuild or reinterpret scope. GitHub revalidates the exact dossier content SHA and authorization from current canonical truth before accepting any artifact.
7. Do not use price, discount, sale urgency, wishlist, purchase value, or other commercial signals for the semantic judgment.
8. Publish at most one create-only transport artifact for an authorized item:
   - a valid `PROGRESSIVE-PASS2-RESULT-V1` at the exact `result_submission_path`; or
   - only when the authorized semantic attempt actually started but no accepted result can be produced, a `PROGRESSIVE-PASS2-EXECUTION-RECEIPT-V1` at the exact `terminal_execution_submission_path`.
9. Copy every immutable identity field exactly, including `semantic_generation_id`, `work_id`, `appid`, `dossier_content_sha256`, the complete `dossier_compatibility_binding`, and `authorization_id`.
10. Never overwrite, rename, delete, or invent an alternate filename. If an exact result or terminal receipt path already exists, do not run the item again.
11. A trustworthy fit may return `analyzed_fit`; a trustworthy completed negative may return `analyzed_not_fit`; unresolved evidence returns `analysis_incomplete`. Insufficient evidence is never a completed negative.
12. Stop when no current prepared items remain or when runtime/tool budget no longer safely permits another item. Never turn a runtime boundary into a quota.
13. Do not modify PASS 1 state, Dossier state/workflows, GitHub eligibility/order/state, retry/accounting, site projection, or any Scheduled Task settings.

GitHub is the sole control-plane authority for PASS 2 eligibility, order, immutable binding, validation, canonical persistence, attempt accounting, terminal execution receipts, recomputation and visual projection.
