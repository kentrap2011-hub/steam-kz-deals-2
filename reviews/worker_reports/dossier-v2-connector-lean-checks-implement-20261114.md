# Dossier V2 — lean GitHub Connector checks (2026-11-14)

## Authorization / scope
User instruction in current interactive session: remove **all thirteen groups** of repetitive/unjustified connector checks proposed by the prior diagnostic, while keeping compatibility and non-production boundaries. This is a **developer source change only**: not the earlier user-launched semantic worker and not a new Research authorization. The active production owner remains GitHub; sandbox publication/strict acceptance remains GitHub-only.

Base: `main@03a014caeceb7aba6e79b76c5f03e83ba8140b60`.
Source PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/446
Branch: `optimize/dossier-v2-connector-checks-20261114`.

Architecture preflight: `config/execution_ownership_contract.json` / scoped V2 batch policy authorize interactive developer modification of the tokenless transport, but not ownership transfer. No new backlog, retry owner, scheduler, grant, Freeze or Authorize. No V1/Deep/production or original18 modifications; original token-backed Python path untouched.

## Removed or reduced
- No `get_repo` push-permission query before a write; GitHub itself enforces permissions.
- No Git committer name/email/timestamp comparison as owner proof; actual owner GitHub Actions successful first-attempt proof remains.
- No extra `main` ancestry compare during an already authorized cohort invocation.
- No `v2ExactOneAdd` rereads for old grant, manifest, authorization or each created object in ChatGPT (GitHub-owned strict writer remains the final full provenance validator).
- No `v2Lineage` 2N multi-GET historical traversal on every fresh preflight. On noninitial branch use a single GitHub compare to detect unrelated/modified paths.
- No repeated branch HEAD queries before each write; `updateRef(expected_sha,force=false)` is the concurrency lease and one postwrite branch HEAD confirms commit publication.
- No preflight file-exists fetch before each new file, no repeated newly created commit metadata fetch, no repeated exact contents/blob readback in the ChatGPT loop. The strict writer rechecks full original bytes and one-add semantics.
- Research preflight loads only Research + receipt schema, Assembly loads Assembly + receipt schema.
- Local extra doc-schema field assertions removed when canonical schema already enforces them.
- Immutable grant/marker/manifest/run proof performed once per Code Mode invocation, not before each sibling item within that invocation.

**Preserved safeguards:** exact owner issuer/first-attempt Actions, fixed trial/manifest/assignment/edition, one-add-created blob/tree/commit per file, create-only path/phase, CAS lease, post-CAS branch HEAD readback, separate typed candidate and receipt Git commits, Research receipt required for Assembly, ambiguous write STOP/no automatic retry, independent GitHub Python strict accepted-only writer. In a restarted Code Mode invocation rerun preflight against current exact sandbox HEAD.

## Static call-cost and synthetic proof

- Original preflight on initial sandbox: approximately **24 GitHub tool calls**; new: **14** (no historical-sandbox compare for untouched initial head).
- Original `connectorPublishItem`: approximately **29 GitHub tool calls** for candidate + receipt. New: **10** (five calls per one-add CAS).
- A restarted preflight after previous commits performs one compare and one head-tree fetch instead of a growing per-commit walk.
- New synthetic regression asserts exactly 10 transport operations for *each* of six sequential Research items, no redundant byte/permission reads and resumed one-compare path discovery; existing adversarial tests keep stale-head, wrong edition/AppID, owner-run, duplicate path, missing receipt and ambiguous branch readback cases.
- No measured wall-clock speedup or live Research acceptance claim.

## GitHub CI at source HEAD `74fa118a25f088d056f543423d23185254f3de9f`

- [V2 Research/Assembly + Node connector + Python V2 + receipt/strict writer, run 43581237371](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43581237371): **SUCCESS**.
- [Eventual chain QA, run 43581237375](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43581237375): **SUCCESS**.
- [Backlog dispositions, run 43581237388](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43581237388): **SUCCESS**.
- [Site registry, run 43581237419](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43581237419): **SUCCESS**.

All four CI runs were verified complete/success at code-and-doc HEAD before this report-only commit. This report commit will advance the PR HEAD; recheck final status and code delta before acceptance. No semantic source web retrieval, real sandbox writes, owner writer dispatch, research or Assembly performed.

## Remaining gate

The source is **PR-only**, not merged. Reviewer/Director acceptance and exact final-head checks are required before the next **separately user-launched** six-game Research. Existing actual sandbox authorization SHA remains unchanged. Real connected GitHub publication with zero reissue and independent strict writer are not established by synthetic tests.


## 2026-11-14 self-QA correction — actual Code Mode cap

After the prior all-green CI result, a direct connected GitHub read-only execution showed that **20 GitHub calls succeed but an attempted 24-call invocation fails with `Code Mode exceeded the maximum number of tool calls`**. Thus earlier statement that the 14+10 single-invocation transport was sufficient was **wrong**. No semantic Git writes were attempted in that check.

Corrective changes in **the same PR #446**: pure `connectorHandoff` / `connectorResumeHandoff` preserve the verified one-time owner preflight within the same explicit user session, while an independent branch HEAD read rejects a changed sandbox. The next call publishes exactly one candidate+receipt pair under non-force CAS; 11 total connected GitHub calls per item-only invocation. Session JSON hash detects accidental edits but is not a cryptographic authentication of external input: handoffs from outside the immediately preceding verified call are forbidden. Added synthetic budget/continuation/recovery/Assembly tests; updated both manual worker prompts and runbook. Existing strict GitHub Python writer remains the acceptance authority. **New exact final commit SHA and all PR CI still need verification after this correction**.
