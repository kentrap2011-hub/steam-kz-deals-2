# ЧАТ 1 — Dossier V2 next safe component 01

**Status:** `CONTRACT_BLOCKED` (report-only, no implementation).
**Task:** `WORKER_TASK_DOSSIER_V2_NEXT_SAFE_COMPONENT_01.md`; registry ID `dossier-v2-next-safe-component-01` / Board slot **НОВЫЙ ЧАТ 1**.
**Repository/source:** `kentrap2011-hub/steam-kz-deals-2`, `main` at start and report-branch base `499d1d736131d2c22def234501d793a05d30a93a`.
**Report:** `reviews/worker_reports/dossier-v2-next-safe-component-01.md`.

## One selected next blocker: trusted prospective GitHub V2 run issuer

A **genuine one-time, GitHub-owned prospective V2 manifest/run-start issuer** is the first missing control-plane component on the path to safe Research → Assembly. It is a prerequisite to treating later item transports, receipts, reviewer appointments and strict group acceptance as belonging to a newly authorized V2 trial. No actual issuer exists in the current inactive runtime.

Bounded evidence (no general audit):
- Both [PR #239](../../pull/239) and [PR #243](../../pull/243) are merged. The [PR #243 worker report](research-assembly-v2-safe-use-readiness-01.md) and [independent PR #249 QA](../../pull/249) explicitly leave a genuine GitHub prospective issuer and one-time authority confirmation absent. PR #249's corrected-head QA is PASS only for **inactive** code.
- `config/dossier_research_notes_v2_contract.json`: `implemented=inactive_offline_pr_only`, `owner=github_control_plane`, and `active=false`, `authoritative=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`, `production_enabled=false`. Its namespace declares prospective manifest/marker paths, but it does not authorize an issuer to create them for a real run.
- `scripts/dossier_research_notes_v2.py::manifest_blueprint` returns future manifest bytes with `authorizes_semantic_execution=False` and writes nothing. `_manifest` / `_marker_nonce` check **already-created** manifest and marker Git history and exact original assignment; they cannot authenticate who approved or issued the marker. Synthetic disposable-Git tests construct those commits themselves; they do not constitute a trusted issuer.
- `config/execution_ownership_contract.json` gives GitHub, not the interactive/semantic worker, manifest, nonce/authority, scope, ordering, attempt/retry, validation and persistence responsibility. `config/dossier_two_stage_interfaces_contract.json` remains inactive, forbids staging/claims and canonical ingest, and reserves any eventual group writing to the existing shared writer.
- The original 18 are exactly six triples g3, g8, g13, g15, g18, g20, with exact original titles/edition/assignment digest pinned to `config/dossier_notes_v2_pinned_original_research_buffer_v1.json`. No authority exists to reassign, rebundle or overwrite original historical Research/Assembly.

**Consequence:** A local issuer helper, guessed approval flag, fake Git token or simulated marker would only manufacture authority and could incorrectly legitimize future receipts. Adding a working issuance/write path requires explicit rules for *who* records the once-only human grant, *which* GitHub-controlled actor issues, and *how* that grant and marker are atomically/immutably attested. Those rules are not presently granted by the inactive contract; this task forbids actual marker issuance and new/modified workflows/CI. Therefore no safe bounded implementation can close this selected blocker under the present permissions.

## Architecture preflight

1. **Owner:** existing GitHub control-plane; not this chat, not Research/Assembly, and not an additional scheduled process.
2. **Contract:** execution ownership authorizes GitHub as the *class of owner*, but inactive V2 contract does **not** authorize a concrete prospective issuer/approval protocol.
3. **No delegation:** proposing issuer under the existing GitHub ownership only; semantic workers must never set marker authority, choose scope or self-authorize.
4. **No new cadence:** no automatic, recurring or retrying issuer; one finite, explicitly authorized prospective trial only, and no implied ability to run semantics after marker preparation.

## ONE concrete decision requested from Director/user

Authorize a **separate, inactive-only contract design** specifying a GitHub-owned, create-once prospective V2 issuer for **exactly** the original frozen 18-item/six-group scope, while explicitly **withholding** permission to issue any real marker or execute any Research/Assembly.

The contract design must bind all of the following *before* an implementation PR can be approved:
1. **Explicit user grant:** immutable, scope-limited, one-use authorization recorded separately from ChatGPT's claims; its approval identity, GitHub-readable proof and revocation/consumption semantics defined. The current worker task/prompt does **not** count as permission for a semantic trial.
2. **Deterministic creation:** the existing GitHub-owned control-plane alone freezes the exact original 18 complete assignments (including titles/editions and original buffer blob/pins), creates exactly one manifest and one new nonce-only marker under the V2 namespace, and records their immutable Git ancestry and parent. No worker-supplied authority SHA; no historical V1 replay or overwrite, alternate destination, partial manifest, second issuance, or forged commit.
3. **Durable attestation:** GitHub verifies its own issuer identity, approval consumption, correct manifest parent and marker first-parent lineage, no mutate/restore, duplicate/collision/race refusal, and exposes a read-only, exact-bound confirmation before **any** worker transport is eligible. Confirmation alone never means Research or Assembly completed, an attempt was consumed, or Dossier accepted.
4. **Separate downstream gates:** actual Research/Assembly, authenticated independent A/B/C appointments, item receipt persistence, source-quality evidence, and strict same-original-three shared-writer ingest each remain **independently blocked** until their own contract/implementation/QA and user authorization. Historical PR #232 is not an activation path.

This is a request for a **contract decision and later separately assigned scope**, **not** a request to waive the existing task's prohibition on workflow/validator/CI changes.

## Performed / not performed

- **Performed:** protocol/START; exact task, registry and current Board match; limited architecture preflight; source and previous developer + independent QA evidence inspection; selected a single upstream blocker and proposed one owner-preserving decision.
- **Changed:** this report alone; **no source, tests, configs, contracts, workflows, branch-state/canonical data, Board/registry or `CURRENT_TASK.md`**. The shared `CURRENT_TASK.md` is historic/concurrent; task-specific handoff stays in this report to avoid overwriting others.
- **Not performed:** no semantic Research/Assembly, prospective marker/manifest issuance, receipt or authenticated reviewer appointment, group publication, real V2 transport, CI creation/modification, automation, production, Deep/Fast, historical PR #232, or merge.
- **Tests:** no runtime/code change exists to exercise, so no new tests were run. Existing GitHub checks for this report-only draft PR are to be read on its final exact HEAD; do not infer check success from prior PRs.

## Handoff / independent QA boundary

**Worker verdict:** `CONTRACT_BLOCKED`. **Single next action:** Director/user resolves the above prospective GitHub issuer contract authority decision in a separately scoped task; only then may another worker consider implementation behind still-inactive flags. No real trial permission is conferred by this report, its branch, its draft PR or a CI green. For a future code PR, independent exact-HEAD QA remains mandatory.
