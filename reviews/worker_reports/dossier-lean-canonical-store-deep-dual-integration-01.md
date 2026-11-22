# Lean Dossier → canonical store → Deep dual-format integration — worker report

**Date:** 2026-11-22  
**Task:** `dossier-lean-canonical-store-deep-dual-format-integration-01`  
**Repository:** `kentrap2011-hub/steam-kz-deals-2` only  
**Source PR:** [#471](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/471), **Draft**, branch `fix/dossier-assembly-no-routine-discovery-20261119`  
**Original PR code+report head:** `24b86e1253ca3d89d269046f686795d370d13253`  
**Implementation code HEAD (before this report):** `036b29d1ae4fcc7dfe2d0d1bbcef6567bfe06bab`  
**Production / Research / Assembly / Deep semantic launches:** **NONE**  
**Merge / owner grant / independent L3:** **NONE**  

## 1. Work performed and scope

START gate read from live `main`: `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, project routes, decisions, `config/execution_ownership_contract.json`, explicit worker task, source PR state/comments, and director handoff **from the source PR branch**. Existing source PR/branch continued in place. GitHub remains the sole owner of immutable Research/Assembly authorization, canonical writer/store, Deep work projection and accepted outcomes. No second source PR, new runtime, queue, scheduler, retry loop, live owner issuer or real worker invocation was created.

Added `config/dossier_lean_canonical_dual_format_contract.json`, explicitly three switches `lean_writer_enabled=false`, `lean_reader_enabled=false`, `lean_deep_enabled=false`. Live authorization requires this separate versioned contract *and* existing original Notes V2 source + writer + downstream approval. The synthetic offline gate uses only a disposable temporary Git fixture guarded by the pre-existing `offline_gate`, with all live switches **still false**.

Added `scripts/dossier_lean_canonical_dual.py` to verify exact Lean schema, frozen AppID/title/edition, non-null original release year, TTL/expiration, quality, privacy and source dates, exact canonical store path, **Git-committed** cache and acceptance receipt bytes, full original Research→Assembly immutable provenance, and final Assembly bytes. It constructs a **distinct Lean-only format/quality/receipt compatibility binding**; it never manufactures legacy source records, per-review provenance, mention counts, synthetic evidence or a 12-dimension ledger.

Extended the **existing shared** `scripts/taste_steam_review_dossier_buffered.py` Notes V2 per-item writer to route only an authorized Lean candidate through this inactive gate. The existing original strict V2 validator, original V1 group writer and strict V2 acceptance receipt are preserved. Lean acceptance uses the existing same-transaction cache + receipt publisher and an explicitly separate format/quality binding. Existing strict files cannot be overwritten by a different Lean SHA (collision remains fail-closed). Cache reuse and frozen recovery examine Lean only through exact canonical acceptance; strict rows keep their prior logic.

Extended `scripts/taste_steam_review_dossier_web.py` daily manifest reader and `build_semantic_input_strict` with a version discriminant. Strict V2 remains byte- and row-compatible; only admitted Lean semantic rows include a new `dossier_format` and `quality_binding`. Ordinary entrypoints do not set test-only flags.

Extended `scripts/progressive_pass2.py` ordinary `dossier_is_eligible`, `recompute_eligibility`, `_bound_dossier` and live binding checks to allow **only** an owner-accepted, version-authorized Lean file with the distinct exact quality+receipt binding. The old `lean_sandbox_preview` path remains isolated and never counts as normal Deep acceptance. Existing score and negative normalizers read Lean `observations` / `conflicts` without a fabricated strict `provenance`. Existing strict V2 path, historical Deep outputs and old work state are not modified.

Fixed a material hash distinction: the writer's historical `dossier_sha256` receipt binds canonical-json-object SHA256, while the existing ordinary Deep loader uses SHA256 of the **raw, indented JSON bytes**. Both values are checked and kept separate. Replacing one with the other would make correct Lean normal Deep fail despite passing the synthetic sandbox preview.

Tightened `scripts/dossier_notes_v2_lean_final.py` source validation to reject nonpublic/private/IP URLs, unsafe ports, private author/profile URL variants and hidden/private query keys. No URL is fetched or re-researched.

## 2. Test suite and acceptance boundaries

New `scripts/test_dossier_lean_canonical_dual.py` uses the **existing code** and separately marked disposable Git repository, not mock acceptance flags presented as live GitHub authority. It follows one frozen synthetic SULFUR AppID `2124120` Research/Assembly **fixture transport** through real `drain_buffered_groups` writer code, one atomic local Git commit of canonical cache+receipt, immutable original-lineage verification, canonical reader, `build_semantic_input_strict`, real `progressive_pass2.recompute_eligibility` normal work construction, `normalize_score_findings` and `normalize_negative_assessment`.

Synthetic offline Git success verifies *code-path integration*, not a real GitHub owner-issued canonical receipt, real Deep execution, an accepted game assessment, or truth of any player review. A true GitHub-approved owner-run remains a separate explicit authorization gate.

Coverage includes:
- old strict `web_dossier` positive reader and Deep eligibility without new format fields;
- original strict accepted bytes unchanged when an attempted Lean per-item write collides;
- raw-byte Deep loader digest versus distinct canonical writer receipt digest;
- uncommitted cache/receipt denied; duplicate identical write idempotent;
- wrong AppID, edition, unresolved/out-of-range year, stale expiry, unsupported time claim, missing pros/cons, invalid sources/privacy, bogus digest and sandbox path;
- missing/forged owner receipt and tampered **already committed** issuer SHA;
- disabled Lean reader/Deep denied on normal non-fixture paths, wrong Deep compatibility binding denied;
- existing strict V1 group atomicity and V2 individual-sibling tests remain in their pre-existing CI suites.

New tests are wired into existing `.github/workflows/validate-dossier-research-notes-v2.yml`. That workflow already runs Node-based connector tests, V2 Research/Assembly synthetic Git tests, legacy strict writer staging/atomicity tests, Deep preview and old Deep regression. Existing `Validate Progressive PASS 2 core`, buffered Dossier and final acceptance integration workflows also run via PR CI.

### Fixed same-game semantic comparison (NO new research)

Three fixed synthetic SULFUR views are compared in a local test: (1) existing strict `web_dossier(2124120)` with a mixed mechanics finding and neutral localization note, (2) lean `make_lean_final(2124120, "SULFUR")` with an explicit combat strength and repeatability trade-off, and (3) the same lean fixture with one bounded player-view dissent conflict. The normal Deep risk-candidate selector sees strict mixed-mechanics observation `observation/0`, lean repeatability `observation/1`, and extra lean dissent `conflict/0`. The accepted lean E2E test passes both score and negative normalization functions. This demonstrates retention of positive/negative structure and dissent support, **not** actual commercial fit improvement or a measured representative real-player truth result. No independent external review search was run.

## 3. CI evidence

The implementation code HEAD before this report is `036b29d1ae4fcc7dfe2d0d1bbcef6567bfe06bab`. GitHub Actions PR checks were triggered; **the exact final code-head complete green CI verdict is not claimed until the relevant runs reach terminal green**. Check:
- [Source PR checks](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/471/checks).
- [Existing Notes V2 synthetic tests](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/workflows/validate-dossier-research-notes-v2.yml).
- [GitHub Actions runs](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions).

All tests described above are **test cases added/selected**, not necessarily a verified green result at the time of this report commit. Individual test stdout and CI log are the evidence, not this narrative. Earlier green results for a prior SHA must not be misreported as this report-inclusive HEAD.

## 4. Rollback, historical migration, and acceptance

Keep all new Lean switches **false**. Rollback is to decline/revert PR #471 (or the add-on commits) without touching canonical `data/cache/taste_steam_review_dossiers`, prior accepted receipts, historical `data/cache/progressive_pass2_state.json` or work queues. Old strict SHA/provenance rules and old Deep results are not migrated, rewritten, reissued, or replaced. The existing writer's SHA collision guard explicitly **prevents** implicit replacement of any strict V2 Dossier by Lean; a future historical conversion would require a separately authorized migration design, not this PR.

Existing source contract `config/dossier_research_notes_v2_contract.json`, dedicated existing writer activation contract and Deep owner flags all remain unactivated. This branch performs no live GitHub issuer grant, writer dispatch, Research, Assembly, canonical ingest, normal Deep run, production or main merge. Passing offline Git fixtures does not satisfy the live owner proof.

## 5. Remaining blockers / independent L3 checklist

**State: SOURCE IMPLEMENTATION AVAILABLE; OWNER ACTIVATION DISABLED; INDEPENDENT QA AND FINAL CI REQUIRED.** The Director must enlist a *different physical QA chat*, not reuse this implementing chat, for an independent L3 review of the final delta and exact final HEAD. L3 must:
1. Re-read `CHAT_PROTOCOL.md`, the worker task, live PR HEAD/diff, exact GitHub CI and original director handoff on the PR branch.
2. Verify inherited strict V1/V2 byte structure, receipts, cached compatibility, current Deep generation, completed history, recovery and work identity cannot change under the default-off lean gate.
3. Independently check raw-byte versus canonical-JSON SHA and the unforgeable immutable Research/Assembly/receipt acceptance chain, including commit-based fraud, time/identity/edition errors and foreign sandbox promotion.
4. Verify positive disposable-Git writer → canonical versioned reader → Taste semantic input → normal Deep work projection → real score/negative normalization. Confirm no real semantic Research/Assembly, owner writer or normal Deep was executed.
5. Inspect false switches in code and contracts, CI exactly on final PR material HEAD, and GitHub control-plane ownership. Do not reinterpret CI of an older commit as latest.
6. Check the trade-off: source date/year/URL fields are structurally verified but the source's semantic truth and representative real-game sufficiency are **not** established by synthetic tests. Require explicit owner authorization and, if warranted, separately permitted real representative QA before future activation.

**Merge gate:** final exact-HEAD CI PASS, independent L3 QA PASS, and Director/owner explicit permission. **Live Lean activation gate:** separate GitHub owner-issued source + writer/Deep approval and its own bounded approved rollout. No automatic activation or merging from this worker.
