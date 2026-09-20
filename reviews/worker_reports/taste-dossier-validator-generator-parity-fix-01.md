# Taste dossier validator ↔ generator parity fix 01

## 1. Task / repo / mode

- Task: `taste-dossier-validator-generator-parity-fix-01`.
- Worker task: `WORKER_TASK_TASTE_DOSSIER_VALIDATOR_GENERATOR_PARITY_FIX_01.md`.
- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- Base/source of truth: `main`.
- Mode: `IMPLEMENT / ACTIVATE / VALIDATE`.
- Scope was limited to accepted PARITY-01..03 only.

## 2. Architecture preflight

Preflight from `CHAT_CONTEXT.md` was completed before the first implementation write.

1. Ownership: GitHub remains the control-plane owner for contracts, snapshot/group-plan preparation, compatibility binding, validation, persistence, progress and activation. The existing Scheduled ChatGPT dossier worker remains the constrained web/semantic data plane.
2. Canonical authorization: `config/taste_steam_review_dossier_contract.json`, `config/taste_steam_review_dossier_web_evidence_contract.json`, `config/taste_steam_review_dossier_schema.json` and the task authorize generator-facing contract/schema/prompt alignment with existing strict acceptance semantics.
3. No responsibility transfer: the change does not move queue, retry, checkpoint, progress, binding or recovery authority to Scheduled ChatGPT or the interactive chat.
4. No new architecture: no new recurring stage, quota, queue, retry loop, scheduler or backlog manager was created.

## 3. Accepted PARITY-01..03 findings

- PARITY-01: strict already required each provenance source to carry exactly one of `url` / `public_ref`; URL must be public HTTPS; `domain` must equal the normalized URL hostname. Generator-facing layers did not completely encode this.
- PARITY-02: strict already required `multi_source` to have at least two distinct physical used player-feedback sources and `single_source_reason:null`. Generator-facing layers described the single-source positive case but omitted the converse null invariant.
- PARITY-03: strict already allowed an exact Steam Store concrete-item fallback parent only with `source_type:"steam_reviews"` or `"store_user_reviews"`. The worker prompt's former “normally” wording left other player-feedback source types semantically possible.

No fourth finding was added.

## 4. Exact changes for PARITY-01

`config/taste_steam_review_dossier_schema.json` now exposes machine-facing provenance-source invariants for:

- exactly one locator: `url` XOR `public_ref`;
- both locators forbidden;
- neither locator forbidden;
- URL requires public `https://`;
- source `domain` must equal the normalized URL hostname;
- normalization is explicitly aligned with strict: trim, lowercase, strip trailing dots, then remove one leading `www.`.

The embedded JSON schema now also declares source items, locator `oneOf`, HTTPS URL shape and the Store-parent conditional.

`config/taste_steam_review_dossier_web_evidence_contract.json` carries the same source-locator policy, and the worker prompt now tells the generator to serialize exactly one locator and the exact HTTPS/domain rule.

## 5. Exact changes for PARITY-02

Generator-facing schema/evidence/prompt now make the existing two-way rule explicit:

- `single_source_only` retains the existing compact non-empty reason behavior;
- `multi_source` requires at least two distinct physical used player-feedback sources under the existing identity rule and requires `single_source_reason:null`.

Physical source diversity computation was not changed.

## 6. Exact changes for PARITY-03

The generator-facing schema and evidence contract now expose the exact exclusive Store fallback-parent source-type set:

- `steam_reviews`;
- `store_user_reviews`.

The worker prompt no longer says “normally”; it says no other player-feedback source type is legal for that exact Steam Store fallback-parent role. `other_player_feedback` remains available elsewhere where already legal; it is only invalid for this specific parent shape.

## 7. Validator boundary confirmation

`scripts/taste_steam_review_dossier_strict.py` was not changed.

Its Git blob SHA before implementation and after merge/activation is the same:

`81126b87db7542512221a82f1ece4b846abe1af7`.

Strict acceptance semantics therefore remain authoritative and unchanged.

## 8. PARITY-FIX-01..12 results

- PARITY-FIX-01 PASS — both/neither locator rejected generator-side/parity fixture; exact-one valid.
- PARITY-FIX-02 PASS — HTTP rejected; HTTPS valid.
- PARITY-FIX-03 PASS — host/domain mismatch rejected; exact normalized match valid, including normalization control.
- PARITY-FIX-04 PASS — `multi_source + non-null single_source_reason` rejected; null with two legal physical used sources valid.
- PARITY-FIX-05 PASS — existing valid `single_source_only` reason semantics preserved.
- PARITY-FIX-06 PASS — exact-app Store fallback parent is valid for both `steam_reviews` and `store_user_reviews`.
- PARITY-FIX-07 PASS — same Store-parent shape with `other_player_feedback` rejected by generator parity fixture and strict validator.
- PARITY-FIX-08 PASS — focused regression pins the unchanged strict-validator Git blob SHA.
- PARITY-FIX-09 PASS — identity-provenance generation rules and focused suite remain green.
- PARITY-FIX-10 PASS — required prior dossier/ownership suites remain green.
- PARITY-FIX-11 PASS — normal GitHub activation produced fresh compatible snapshot `3bd2085e…`; no old binding was rebound.
- PARITY-FIX-12 PASS — production Scheduled Task was not run and its settings were not changed.

## 9. Existing guard suites

Final PR dossier CI run `35500617436` / run #103 passed all steps, including:

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
- new validator-generator parity regression;
- package identity;
- Story-DLC semantic scope;
- parallel candidate validation / maximal contiguous prefix.

Backlog disposition PR run `35500617438` / #820 also passed.

The immediately preceding dossier run #102 failed only on a stale expected `worker_prompt_revision` string in the existing strict-recovery regression after the intentional binding revision change. The expectation was updated; no runtime/strict semantic change was made.

## 10. PR / CI / merge refs

- Implementation branch: `worker/taste-dossier-validator-generator-parity-fix-01`.
- PR: #70 — `Align Taste dossier generator contract with strict validator`.
- Final PR head: `883e8578c1ab1d3c34487b3a5484712fc1e4b65f`.
- Final dossier CI: run `35500617436` / #103 — success.
- Final backlog CI: run `35500617438` / #820 — success.
- Merge commit: `505c1adbd48eeaa2100148947cbe56bd881f4f76`.

## 11. Activation refs

Normal GitHub-owned activation was triggered automatically by the merged binding/config changes.

- Workflow: `Build pre-AI deterministic payload`.
- Run: `35500644784` / #144 — success.
- Atomic pre-AI activation commit: `cf8467d65691312efe55efd76979cc74ff50c50d`.
- Post-merge execution ownership run: `35500644843` / #176 — success.
- Post-merge backlog disposition run: `35500644818` / #821 — success.

No manual production artifact mutation was used.

## 12. Active snapshot/binding state

Active canonical state after activation:

- snapshot id: `3bd2085e4a4a157aa0edadfeabbdcc36786228787016f373189d71d12da8d99b`;
- prepared date: `2026-09-20`;
- canonical expected sequence: `1` / `g000001`;
- completed / remaining: `0 / 733`;
- prepared: `733`;
- group count: `245`;
- normal group size: `3`;
- exact current expected group:
  - Crown Trick — appid `1000010`;
  - Hellish Quart — appid `1000360`;
  - Tetris® Effect: Connected — appid `1003590`;
- current `g000001` group SHA-256: `53cf1ce2cc36a580a99528a7d4495e4ac789308178fb4bec742415beffc92e3f`;
- prompt revision: `web-evidence-v2-validator-generator-parity-fix-v1`;
- prompt SHA-256: `35163c3da9c04419d6182402746788949e90e2c2280cc282fe951624e4a8033c`;
- worker schema revision: `validator-generator-parity-fix-2026-09-20`;
- worker schema SHA-256: `d3d02d5060b5a978c827ebaddacac67b9cf4e1fa5369e5921a0762fce940da98`;
- evidence contract revision: `validator-generator-parity-fix-2026-09-20`;
- evidence contract SHA-256: `88cbca02bf91f71bff99225572c6e6f91a2dbd716aef77edc7661815f94ac3ce`.

Activation did create a fresh snapshot.

## 13. Compatibility effect on prior snapshot/candidates

Immediately before activation, the active snapshot was:

`905bddbce50fc8fd319465e3e68450e9cd7f0b2edc53c8a1a687466372f4d384`

with `0 / 733` completed/remaining progress and the prior binding:

- evidence revision/hash: `contract-contradictions-fix-2026-09-18` / `2adc57a346067a438a009f8503bb07c66f207f4c2b299581e96e9e8921b7d61e`;
- schema revision/hash: `identity-provenance-generation-fix-2026-09-20` / `3f163b41449232c5fc73532e87147c101d48fe42ffcb0081b64569a4e36f4a9e`;
- prompt revision/hash: `web-evidence-v2-identity-provenance-generation-v1` / `247d3ab7ad6c208cbf209f4df0aea63dab443b62997f067305abf9d1ceec4a98`.

The normal activation replaced the active work/index projection with the new snapshot/binding and regenerated the worker group descriptors under the new snapshot id. The prior snapshot therefore became stale/inert under the existing exact content-binding rule; nothing was manually rebound. No Git-tracked active submission inbox directory/candidate was present to migrate or repair, so no pre-fix candidate was rebound.

## 14. Scheduled Task confirmation

The production Scheduled Task `Taste Steam Review Dossier` was not run. Its settings were not changed. No production dossier candidate was created by this interactive implementation chat.

## 15. Unresolved

None within the accepted PARITY-01..03 implementation scope.

Live production behavior is intentionally not claimed here because the task explicitly forbids running the Scheduled Task during implementation/activation validation.

## 16. Status

`complete_ready_for_live_acceptance`

All accepted parity gaps are aligned generator-side, strict semantics are unchanged, focused and prior guards are green, normal activation completed, the active snapshot carries the new exact binding, no manual progress/recovery surgery occurred, and the Scheduled Task was not run.

## 17. Exactly one recommended next step

Return to Director for one clean production `Run now` acceptance of the existing `Taste Steam Review Dossier` Scheduled Task against active snapshot `3bd2085e4a4a157aa0edadfeabbdcc36786228787016f373189d71d12da8d99b`.

## 18. Efficiency / reusable lesson

Content-complete binding revisions predictably invalidate hard-coded revision expectations in regression controls even when semantics are intentionally unchanged. A reusable implementation rule is to scan the focused dossier suites for exact binding-revision assertions before opening the final PR, update only those stale expectations, and keep semantic guards unchanged. The new parity suite also pins the strict-validator blob SHA so future generator-facing fixes cannot silently alter strict acceptance behavior.
