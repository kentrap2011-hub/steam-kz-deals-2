# Taste Dossier Contract Contradictions Fix 01

## 1. Task / repo / mode

- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- Base/source of truth: `main`.
- Task: `WORKER_TASK_TASTE_DOSSIER_CONTRACT_CONTRADICTIONS_FIX_01.md`.
- Mode: IMPLEMENT / ACTIVATE / VALIDATE.
- Scope was limited to the three confirmed audit findings CONTRA-01, CONTRA-02 and CONTRA-03.
- No other repository was read or modified.

## 2. Architecture preflight

Preflight result: no execution-ownership transfer and no new runtime architecture were required.

- GitHub remains the control plane for rules, canonical scope/work preparation, strict validation, buffered acceptance/persistence, recovery and completeness.
- Scheduled ChatGPT remains the bounded dossier data-plane worker.
- Interactive chat acted only as the allowed developer/operator for contract, validator, fixture, regression and report changes.
- No new queue, recurring worker, reviewer-identity store, cross-run author mapping, retry loop or manual progress path was created.
- `scripts/validate_execution_ownership.py` returned `ARCHITECTURE_OWNERSHIP_VALID` in PR CI run #85.

## 3. Baseline accepted behavior preserved

The implementation deliberately preserved the already accepted semantics:

- Steam Store exact-app page may remain a parent collection only for actually inspected concrete review-card fallback children.
- The Store page itself, aggregate counts/ratings and language totals do not become feedback records or mentions.
- Neutral stable locator remains preferred over transient-author fallback.
- `transient_author_deduped` persists no author/profile identity and no child item URL/public_ref.
- Fallback recurrence remains reduced-strength and capped as before.
- Russian discovery remains source-agnostic.
- Story-DLC policy remains `story-dlc-positive-evidence-v1`.
- Group size remains 3; publication remains atomic full-group plus maximal contiguous prefix.
- Package/pricing/ranking/giveaway/UI and retry/recovery architecture were not changed.

## 4. CONTRA-01 exact fix

Root cause: the active semantic contract required exact-product and physical-parent binding, but strict validation previously enforced exact Steam appid only on parent source URLs and, for stable children, only broad host/surface compatibility.

Fix:

- stable Steam child URL/public-ref locators that deterministically expose an appid are now checked against the exact dossier appid;
- Steam parent sources whose deterministic public reference exposes an appid are checked as well;
- when both parent and stable child expose deterministic Steam discussion/container identity, every commonly resolved appid/forum/thread component must match;
- same host or broad `steam_review` / `steam_discussion` class alone is no longer sufficient;
- unknown/unresolvable identity is not guessed.

Canonical semantic owner remains the active web-evidence contract and GitHub strict validator. The schema and worker prompt expose the same worker-facing invariant.

## 5. CONTRA-02 exact fix

Root cause: stable `source_id` / `feedback_id` fields were structurally arbitrary short strings. URL/public-ref privacy rules were strong, but an author-derived SteamID/profile token or direct hash could still leak through those internal join keys.

Fix:

- every serialized source uses sequential dossier-local `source-NNN`;
- every stable-locator feedback record uses sequential dossier-local `feedback-NNN`;
- fallback keeps its existing independent sequential `fallback-NNN` namespace;
- IDs are author-independent local join keys only;
- stable physical item identity remains in the validated safe item URL/`public_ref`;
- compact-provenance validation and strict validation both reject non-local ID shapes;
- no compatibility exception was added for stale arbitrary IDs.

This closes the username/SteamID/profile/direct-hash/predictable-pseudonym leakage path through internal IDs without changing fallback privacy or recurrence behavior.

## 6. CONTRA-03 exact fix

Root cause: the generation contract already described deterministic observation-language derivation, but strict validation only checked that individually claimed Russian/non-Russian tokens had some support. It did not require exact equality and schema still permitted `mixed` as a summary token.

Fix:

- strict validation derives the expected observation language list from the final bound `player_feedback_ids`;
- record `russian` projects to `russian`;
- record `non_russian` projects to `non_russian`;
- record `mixed` projects to both `russian` and `non_russian`;
- record `unknown` projects to `unknown`;
- output is ordered exactly `russian`, `non_russian`, `unknown`;
- serialized `evidence_languages` must equal that projection exactly;
- `mixed` was removed from the observation-summary enum while remaining legal at feedback-record/source language level.

## 7. Schema / contract / prompt / validator alignment

The existing canonical surfaces were aligned without adding a parallel policy layer:

- `config/taste_steam_review_dossier_schema.json`
  - revision: `contract-contradictions-fix-2026-09-18`;
  - observation language enum excludes `mixed`;
  - local internal-ID and stable Steam child/container invariants are explicit.
- `config/taste_steam_review_dossier_web_evidence_contract.json`
  - revision: `contract-contradictions-fix-2026-09-18`;
  - worker prompt revision: `web-evidence-v2-contract-contradictions-fix-v1`;
  - exact stable-child product/container rules, internal join-ID semantics and strict language equality are explicit.
- `config/taste_steam_review_dossier_worker_prompt.md`
  - generation instructions match all three acceptance rules.
- `scripts/taste_steam_review_dossier_strict.py`
  - canonical acceptance enforces all three fixes.
- `scripts/taste_steam_review_dossier_compact_provenance.py`
  - compact privacy validation also enforces the local ID namespaces.
- synthetic fixtures were migrated coherently to the new local-ID format instead of preserving stale aliases.

## 8. Privacy implications

Privacy is stricter, not weaker.

Persisted IDs can no longer carry usernames, display names, SteamIDs/account IDs, profile identifiers, direct hashes or predictable author-derived pseudonyms. A stable record may still persist an accepted neutral item locator in URL/`public_ref`; a transient-author fallback still persists neither author identity nor child item locator. No reviewer identity survives as a cross-run mapping key.

## 9. Exact-product / physical-parent implications

A stable Steam child must now prove the exact product whenever its locator exposes appid, and a deterministically resolvable Steam discussion/container relationship must physically agree with its parent. This closes the prior silent path where a child from a different app/thread could pass solely because both records lived on Steam and shared a broad surface class.

The narrow Steam Store exact-app concrete-card parent fallback is unaffected because fallback children intentionally have no stable child locator to over-bind.

## 10. Exact language projection semantics

Observation language summary is no longer a free-form subset.

For the final bound record set, the validator computes the ordered distinct union:

1. `russian`
2. `non_russian`
3. `unknown`

Record-level `mixed` contributes both first and second tokens and is never serialized as an observation-summary token. Missing supported tokens, unsupported extras and non-canonical order all fail.

## 11. CONTRA-FIX-01..14 results

PR CI run #85 (`Validate buffered Steam review dossier runtime`) completed successfully.

- CONTRA-FIX-01: PASS — wrong Steam child appid rejected.
- CONTRA-FIX-02: PASS — matching exact-product/matching-parent stable child accepted.
- CONTRA-FIX-03: PASS — deterministic Steam physical-container mismatch rejected.
- CONTRA-FIX-04: PASS — valid transient-author fallback remains accepted without child URL/ref.
- CONTRA-FIX-05: PASS — author-derived/non-local stable `feedback_id` rejected.
- CONTRA-FIX-06: PASS — author-derived/non-local `source_id` rejected.
- CONTRA-FIX-07: PASS — neutral sequential local IDs with valid stable locator accepted.
- CONTRA-FIX-08: PASS — bound `mixed` record projects exactly to `["russian","non_russian"]`.
- CONTRA-FIX-09: PASS — `unknown` support is preserved in canonical order.
- CONTRA-FIX-10: PASS — incomplete Russian/non-Russian summary rejected.
- CONTRA-FIX-11: PASS — observation-summary `mixed` token rejected while record-level `mixed` remains valid.
- CONTRA-FIX-12: PASS — correct tokens in wrong order rejected.
- CONTRA-FIX-13: PASS — complete three-game current-g000001 candidate fixture validates.
- CONTRA-FIX-14: PASS — all required prior guard suites remained green.

The dedicated contradiction suite ran 14 tests and passed.

The first PR attempt, run #84, intentionally remained blocked because one pre-existing Store-parent negative fixture switched a fallback record to `stable_locator` but retained the now-invalid `fallback-001` ID, so the new local-ID guard fired before the intended Store-parent guard. The fixture was corrected to use `feedback-001`; no production rule was weakened. Run #85 then passed completely.

## 12. Current g000001 fixture result

The focused regression validates a deterministic complete candidate for the current three-game group under all three fixes:

- Crown Trick — appid `1000010`, using the accepted Steam Store concrete-card transient-author fallback path.
- Hellish Quart — appid `1000360`, using a valid stable-locator fixture path.
- Tetris® Effect: Connected — appid `1003590`, using a valid stable-locator fixture path.

The current canonical descriptor after activation remains exactly those three appids/titles in that order.

## 13. Prior guard confirmation

Run #85 kept the required prior suites green:

- daily snapshot regression: 9 tests;
- buffered submission regression: 8 tests;
- same-day preservation regression: 5 tests;
- strict recovery/content-complete binding regression: 16 tests;
- prepublication parity regression: 8 tests;
- contract-gap regression: 10 tests;
- language binding regression: 7 tests;
- semantic consistency regression: 20 tests, including Russian existence/retrieval and multi-source semantics;
- transient-author fallback regression: 12 tests;
- Steam Store review-card parent regression: 11 tests;
- contradiction closeout regression: 14 tests;
- package identity regression: 6 tests;
- Story-DLC regression: 8 tests;
- parallel/maximal-contiguous-prefix regression: 3 tests.

Execution ownership validation was also green. Backlog-disposition PR run #763 completed successfully.

## 14. PR / CI / merge refs

- Implementation branch: `worker/taste-dossier-contract-contradictions-fix-01`.
- PR: #62 — `Fix Taste dossier contract contradictions`.
- Failed diagnostic PR CI: `Validate buffered Steam review dossier runtime` run #84.
- Final green PR CI: `Validate buffered Steam review dossier runtime` run #85.
- Final green PR backlog dispositions: run #763.
- Merge commit: `46acb0aad3606c0bcf84a9a9798f5a5b6854d950`.

## 15. Activation / binding / snapshot

Normal GitHub-owned activation ran automatically from the merge-triggered push.

- Activation workflow: `Build pre-AI deterministic payload`, run #137 — SUCCESS.
- Atomic activation commit: `c87e35b1fbbbb8fadd563acfd4f8e1473af7eaf9`.
- Snapshot id: `d253b195701e74c9c00fc8b669f84655341601faf11e09a7edfb353a8b7f2bbb`.
- Prepared / completed / remaining: `702 / 0 / 702`.
- Expected sequence: `1` (`g000001`).
- Group count: `234`.
- Group size: `3`.
- Exact g000001:
  - `1000010` — Crown Trick — `missing_dossier`;
  - `1000360` — Hellish Quart — `refresh_required`;
  - `1003590` — Tetris® Effect: Connected — `refresh_required`.
- g000001 group SHA256: `ebe4fe17ea90ffb8ddf70993a24850c6d406602abe09cd007d332247fac6869b`.

Active content-complete binding:

- evidence contract revision: `contract-contradictions-fix-2026-09-18`;
- evidence contract SHA256: `97c24bdfb8a249167cf9395b4aa91f59b1035ce25301dea5f60426b0a6ef1c02`;
- worker schema revision: `contract-contradictions-fix-2026-09-18`;
- worker schema SHA256: `d04a8463ec17e0971fa54a851258247163af4e4ceb2861f1b202907e359d362e`;
- worker prompt revision: `web-evidence-v2-contract-contradictions-fix-v1`;
- worker prompt SHA256: `22d702f30d3b021e2115cb3caf4e5798a703c7775471d891b1b574d891de39cf`.

Pre-task baseline snapshot was `2db923b8171bcf30caa2a6a0b2e36f4bc21c63143265a92648969d3748f79319` with `702 / 0 / 702`. Post-activation scope is also `702 / 0 / 702`; scope delta is exactly zero, so there are no removed or added dossier objects to explain.

Story-DLC policy and scope binding remained unchanged:
- policy revision: `story-dlc-positive-evidence-v1`;
- scope SHA256: `71acd585e2b86d17187db0dae6668f0b7fa9e5da3d206ac982d5fa6bbff41a7a`.

No manual rebind or progress repair was performed.

## 16. PROJECT_DECISIONS ref

`PROJECT_DECISIONS.md#TASTE-011` records the durable decision:

- validator-enforced exact-product/physical-parent stable Steam child binding;
- author-independent dossier-local join IDs;
- stable item identity remains in safe URL/`public_ref`;
- exact deterministic observation language projection;
- no weakening of privacy or recurrence guards.

## 17. Scheduled Task confirmation

Scheduled Task `Run now` was not invoked.

Scheduled Task settings were not read-modified-write or otherwise changed by this task.

## 18. Unresolved

None.

## 19. Status

`complete_ready_for_live_acceptance`

The implementation is merged, canonical activation is complete, the fresh binding/snapshot is present, required regressions and prior guards are green, and current g000001 remains deterministic.

## 20. Exactly one recommended next step

Return to Director.

## 21. Efficiency / reusable lesson

When a privacy hardening changes internal ID semantics, regression fixtures that intentionally switch an object between identity modes must also switch to the target mode's valid local-ID namespace; otherwise an earlier local-ID guard can mask the downstream behavior the fixture was designed to test. Keeping local join identity separate from physical evidence identity also makes future privacy audits materially simpler because URL/`public_ref` is the only stable-item identity surface that needs item-specific scrutiny.
