# Taste dossier identity provenance generation fix 01

## 1. Task / repo / mode
- Task: `WORKER_TASK_TASTE_DOSSIER_IDENTITY_PROVENANCE_GENERATION_FIX_01.md`.
- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- Base/source of truth: `main`.
- Mode: IMPLEMENT / ACTIVATE / VALIDATE.

## 2. Architecture preflight
- Scheduled ChatGPT remains the constrained semantic dossier-generation worker.
- GitHub remains control plane for scope, group planning, strict validation, persistence, progress, recovery and activation.
- The task/canonical contracts authorize worker-facing prompt/schema/content-binding alignment.
- No scheduler, queue, retry, checkpoint, persistence, recovery or progress ownership was moved or duplicated.

## 3. Accepted production diagnosis
Affected canonical snapshot `533abb9b4328efec3b80a61caddb142ffe0ff7fb9438482d5159b2ed9878378d` was at expected sequence 1 with zero completed work. Its buffered `g000001` and `g000002` were both rejected by the existing strict validator with `game identity requires an identity-role provenance source`.

## 4. Exact worker-generation gap
The strict validator already required at least one `game_identity.identity_source_ids` entry to resolve to a provenance source whose `evidence_role` is `identity`. The active worker prompt only said to record compact identity provenance, and the worker schema only required non-empty identity source IDs. That allowed generation to serialize ordinary player-feedback source IDs (for example `durable_trait`) as identity provenance before GitHub strict validation rejected the artifact.

## 5. Canonical prompt/schema/contract alignment change
- `config/taste_steam_review_dossier_worker_prompt.md` now explicitly requires every resolved identity to reference at least one exact-product provenance source with `evidence_role:"identity"`.
- It explicitly forbids relabeling ordinary player-feedback evidence as identity just to pass validation and says identity-only metadata cannot count as feedback, Russian usage, recurrence or source diversity.
- `config/taste_steam_review_dossier_schema.json` revision is now `identity-provenance-generation-fix-2026-09-20` and encodes matching machine-facing identity invariants.
- `config/taste_steam_review_dossier_web_evidence_contract.json` keeps evidence semantics/revision unchanged and advances only the worker prompt content binding to `web-evidence-v2-identity-provenance-generation-v1`.

## 6. Validator boundary
`scripts/taste_steam_review_dossier_strict.py` was not weakened or changed. The pre-existing fail-closed identity-role check remains authoritative, as do exact appid/title, privacy, language, recurrence, Russian, parent/child and buffered validation rules.

## 7. Before/after identity provenance shape in plain language
Before: the worker could point `game_identity.identity_source_ids` only at review/discussion sources used for feedback, even though none was classified as identity provenance; GitHub then rejected the dossier.

After: the worker must persist a separate source that establishes the exact intended product (title/release identity and exact appid when exposed), mark that source `evidence_role:"identity"`, reference it from `game_identity.identity_source_ids`, and keep player-feedback sources/records separate.

## 8. ID-PROV-01..10 results
- ID-PROV-01: PASS — non-identity-only identity source lists remain rejected by strict validation.
- ID-PROV-02: PASS — worker prompt/schema now explicitly require identity-role provenance.
- ID-PROV-03: PASS — valid identity source + exact appid + separate feedback passes strict, prepublication and buffered validation.
- ID-PROV-04: PASS — identity-only source cannot be used as a player-feedback source/record and cannot manufacture feedback support.
- ID-PROV-05: PASS — exact title/appid identity remains fail-closed and aligned to the intended product.
- ID-PROV-06: PASS — sequential dossier-local IDs and privacy guards remain intact; identity/profile/hash-derived IDs are rejected.
- ID-PROV-07: PASS — evidence semantics remain unchanged.
- ID-PROV-08: PASS — required prior focused suites and ownership validation are green.
- ID-PROV-09: PASS — content-complete binding change produced a fresh compatible snapshot; old candidates became stale and were quarantined without rebind.
- ID-PROV-10: PASS — production Scheduled Task was not run and its settings were not changed.

## 9. Existing guard suites
Final dossier CI run #98 (`35493176865`) passed compile plus:
- execution ownership;
- daily snapshot;
- buffered submission;
- same-day preservation;
- strict recovery;
- prepublication parity;
- contract gaps;
- language binding;
- semantic consistency;
- transient-author fallback;
- Steam Store review-card parent;
- contract contradictions;
- identity provenance generation;
- package identity;
- story-DLC scope;
- parallel candidate validation / contiguous-prefix behavior.

Backlog disposition PR run #805 (`35493176864`) also passed.

Two stale live-fixture assertions encountered during validation were corrected to validate the current canonical `g000001` descriptor generically instead of hardcoding historical appids. No runtime logic was weakened for those fixes.

## 10. PR / CI / merge refs
- Implementation branch: `worker/taste-dossier-identity-provenance-generation-fix-01`.
- PR: #67 — `Fix Taste dossier identity provenance generation contract`.
- Final implementation head: `2be80ef65e4cde536d99412fc1d5025e90c6ce7f`.
- Final dossier CI: run #98 / `35493176865` — success.
- Final backlog CI: run #805 / `35493176864` — success.
- Merge commit: `f0a42cd2c870bbc013c07901b86ae21bfef4bc98`.

## 11. Activation refs
Normal GitHub-owned push activation ran automatically because the merged prompt/schema paths are watched by `.github/workflows/build-pre-ai-store-snapshot.yml`.
- Build pre-AI deterministic payload: run #143 / `35493204897` — success.
- Atomic activation commit: `d174f1652581b3ef0c633fc9da22d0533b5abdd6`.
- Push ownership validation: run #175 / `35493204894` — success.
- Push backlog validation: run #806 / `35493204926` — success.
- Activation log reported `stale_inbox_quarantined_count: 2` and no contiguous current work persisted during reconciliation.

## 12. Active snapshot/binding state
- Active snapshot: `905bddbce50fc8fd319465e3e68450e9cd7f0b2edc53c8a1a687466372f4d384`.
- Prepared date: `2026-09-20` (`prepared_at_utc: 2026-09-20T06:03:14+00:00`).
- Prepared / completed / remaining: `733 / 0 / 733`.
- Canonical expected sequence: `1`.
- Group count: `245`; normal group size: `3`.
- Worker prompt: `web-evidence-v2-identity-provenance-generation-v1`; SHA-256 `247d3ab7ad6c208cbf209f4df0aea63dab443b62997f067305abf9d1ceec4a98`.
- Worker schema: `identity-provenance-generation-fix-2026-09-20`; SHA-256 `3f163b41449232c5fc73532e87147c101d48fe42ffcb0081b64569a4e36f4a9e`.
- Evidence contract revision remains `contract-contradictions-fix-2026-09-18`; content SHA-256 `2adc57a346067a438a009f8503bb07c66f207f4c2b299581e96e9e8921b7d61e`.
- Exact expected descriptor: `data/production/pre_ai/taste_steam_review_dossier_worker_groups/905bddbce50fc8fd319465e3e68450e9cd7f0b2edc53c8a1a687466372f4d384/g000001.json`.
- Descriptor: sequence `1`, start `0`, end-exclusive `3`, appids `1000010, 1000360, 1003590`, items SHA-256 `f9b5c5c44fb43a240955911b7299e70ecd059b51027e2280d5d758e526ef7254`, group SHA-256 `97f13bd595318de51632dadc1e9e1781223547c1b4a3529cafa82febf6279ac8`.

## 13. Old invalid artifact compatibility/recovery result
Old snapshot `533abb9b4328efec3b80a61caddb142ffe0ff7fb9438482d5159b2ed9878378d` is no longer the active worker snapshot. Its historical validation status remains non-authoritative (`canonical_progress_authority:false`).

The normal GitHub-owned activation moved both invalid candidate files from the active inbox into:
`data/quarantine/taste_steam_review_dossier_inbox/stale/533abb9b.../`.

They were 100% renames with zero content changes. Git blob identities were preserved exactly:
- old `g000001`: `6ff475dcf123481fb08112f16ebff4f2861d6c97` before and after quarantine;
- old `g000002`: `9ab1b9aec3080aabf3690231771227697ff13382` before and after quarantine.

No manual edit, overwrite, delete, alternate filename replacement, rebind, cache repair or progress surgery was performed. No explicit recovery request was necessary; the existing normal activation/recovery path handled stale artifacts.

## 14. Scheduled Task confirmation
Production Scheduled Task `Run now` was not invoked and Scheduled Task settings were not changed.

## 15. Unresolved
None within this task scope. Live production acceptance is intentionally deferred to the Director-required next step.

## 16. Status
`complete_ready_for_live_acceptance`

## 17. Exactly one recommended next step
Return to Director for one clean production `Run now` acceptance on active snapshot `905bddbce50fc8fd319465e3e68450e9cd7f0b2edc53c8a1a687466372f4d384`.

## 18. Efficiency / reusable lesson
Content-complete worker bindings should be asserted from one canonical revision source where possible; multiple tests had duplicated historical prompt/group literals. Keeping live-fixture regressions descriptor-driven avoids false failures when the canonical daily snapshot legitimately changes, while strict semantic invariants remain fixed and fail-closed.
