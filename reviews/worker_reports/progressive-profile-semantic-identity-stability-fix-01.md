# Progressive profile semantic identity stability fix 01 — worker report

## 1. Task

Task: `WORKER_TASK_PROGRESSIVE_PROFILE_SEMANTIC_IDENTITY_STABILITY_FIX_01.md`.

Repository/source of truth: `kentrap2011-hub/steam-kz-deals-2@main`.

Final status: `complete_ready_for_director_acceptance`.

The task separated semantic Taste-profile identity from exact execution provenance, reconciled already accepted Fast/Deep state without semantic reruns, restored the completed PPD-010 migration as current where equivalence was proven, preserved PPD-010/PPD-011, and completed normal visual/Pages publication.

No Dossier, Fast, or Deep semantic worker was manually run. Scheduled Task configuration was not changed.

## 2. Architecture preflight

The implementation keeps the existing ownership model intact:

- GitHub remains sole owner of profile resolution/pinning, semantic generation, work identity, eligibility, attempt/recovery accounting, result acceptance, persistence, current-result selection, deterministic recomputation, and publication.
- Scheduled ChatGPT remains bounded semantic execution against one exact prepared immutable work item.
- No new scheduler, recurring stage, retry loop, queue owner, backlog manager, or checkpoint authority was introduced.
- Exact execution provenance remains strict: `PROGRESSIVE-PROFILE-PIN-V1` still includes the exact repository/path/resolved commit/blob/content SHA/byte count and remains required for prepared invocation/run-start/result transport validation.
- Dossier remains independent.
- PPD-010 migration history/results remain immutable.
- PPD-011 release-year compatibility remains unchanged.
- No whole-`main` stability requirement was reintroduced.

## 3. Canonical semantic/provenance decision

PPD-012 was added before runtime changes.

It defines two separate identities:

1. **Semantic profile identity** — `PROGRESSIVE-PROFILE-SEMANTIC-IDENTITY-V1`.
   - canonical repository/path;
   - Git blob identity;
   - profile content SHA-256;
   - profile byte count;
   - plus existing global semantic bindings: Taste model version, Taste semantics binding, and candidate-context contract binding.
   - `resolved_commit_sha` is explicitly not a semantic invalidation key when the semantic bytes/bindings are identical.

2. **Execution provenance identity** — existing exact `PROGRESSIVE-PROFILE-PIN-V1`.
   - exact repository/path;
   - exact resolved commit;
   - exact blob/content hash/bytes;
   - immutable preparation provenance.
   - still strict for run-start/work/result audit and validation.

Historical compatibility is a GitHub-owned selection rule, not a result rewrite: an accepted older result can remain current only when its exact immutable historical work manifest proves the same profile content, model/semantics/context bindings, and item identity.

## 4. Accepted root cause

The accepted diagnosis was confirmed by implementation behavior and regression coverage:

- the PPD-010 30-result migration had completed successfully;
- profile blob/content bytes were unchanged;
- only the profile provenance commit changed;
- the old contract included that commit-derived `profile_pin_sha256` in global semantic identity;
- therefore the global semantic generation/work IDs changed even though Taste semantics did not;
- current-result matching rejected the 30 valid accepted revisions and ordinary Deep work was emitted again.

PPD-012 removes only this provenance-only invalidation. It does not make title/path matching sufficient and does not weaken exact worker provenance.

## 5. Changes

Primary implementation merged in PR #113:

- `PROJECT_DECISIONS.md`: PPD-012;
- `config/progressive_personalization_contract.json`;
- `config/progressive_pass1_contract.json`;
- `config/progressive_pass2_contract.json`;
- `scripts/progressive_pass1.py`;
- `scripts/progressive_pass2.py`;
- `scripts/test_progressive_profile_semantic_identity_stability.py`;
- Progressive validation/pre-AI workflow coverage;
- `PROJECT_ROUTES.md`.

Core implementation details:

- new content-based `profile_semantic_sha256`;
- global semantic generation no longer depends on provenance-only commit churn;
- new PASS 1/2 state writes persist semantic profile identity while keeping the exact provenance pin;
- current-result matching order is:
  1. exact frozen historical identity match;
  2. direct new semantic identity match;
  3. fail-closed historical semantic-equivalence proof from exact `work_authority_commit` manifest;
- original accepted entries are reused in place as immutable history; no fake result/new attempt is created.

PR #114 added production-history visual provenance regression after reconciliation.

PR #115 fixed one downstream deterministic publication defect exposed only after Deep results became current again:

- `grounded_negative_visual.py` had reprojected Deep negative findings through the legacy compatibility shape and dropped exact `semantic_binding` and Dossier `evidence_refs`;
- Deep finalization now uses the exact Deep projection and preserves `evidence_refs`, `semantic_binding`, and `disposition`;
- Fast/cache structured-negative behavior remains unchanged;
- ranking weights/policy are unchanged;
- changing this finalizer now triggers canonical visual publication.

## 6. Semantic identity regressions

Focused PPD-012 regression proves:

- same profile bytes + different provenance commit => different exact provenance pin but same semantic profile identity;
- same profile bytes + different provenance commit => same global semantic generation;
- same profile bytes + different provenance commit => same per-item work ID when item semantics are unchanged;
- otherwise-current Fast state remains current across provenance-only commit churn;
- real profile byte/content change => new semantic generation/work identity;
- Taste model change => new semantic generation;
- Taste semantics binding change => new semantic generation;
- candidate-context contract change => new semantic generation;
- item taste fingerprint change => only the affected item work identity changes;
- unchanged sibling item work identity stays unchanged.

Current post-merge regression output in run `36431916442`:

- `profile_semantic_sha256=f0852fd520755bedafb764da25d3aa391fd0706eae4878d6f89ef10894fd915e`;
- current semantic generation `d21e7d0b38be9d16dbd931900610ff8603715150eec3d0e666f5c84a93e52408`.

## 7. Provenance / fail-closed regressions

The regressions prove:

- missing profile content SHA fails closed;
- invalid/missing Git blob identity fails closed;
- an arbitrary old result with different semantic content cannot be revived;
- exact result transport remains strict: an old exact provenance pin is rejected against a newly prepared exact provenance pin even when semantic identity is equivalent;
- exact frozen migration/recovery work still matches its own historical accepted state before compatibility reconciliation is considered;
- historical reconciliation requires exact immutable `work_authority_commit` material and exact historical work item/profile pin;
- insufficient or inconsistent historical proof returns no match.

The final visual regression additionally proves all visible reconciled Deep risk rows keep exact accepted-state binding plus Dossier evidence references.

Post-merge PPD-012 output in run `36431916442`:
- `fit_count=26`;
- `cards_with_visible_risk=19`;
- `bound_visible_risk_rows=23`.

## 8. Deep historical reconciliation

Fresh current reconciliation proves:

- PPD-010 migration targets checked: 30;
- semantically equivalent and restored as current: 30/30;
- re-emitted as ordinary Deep work: 0;
- new semantic attempts consumed by reconciliation: 0;
- recovery authorizations created by reconciliation: 0.

The two durable non-migration Deep completions from the accepted diagnostic are handled by the same generic rule rather than a migration-specific hard code:

- `game:1161590` / AppID 1161590 — current after PPD-012;
- `game:1118240` / AppID 1118240 — current after PPD-012.

Thus current canonical Deep authority is 32 accepted authoritative results: the reconciled 30 migration results plus the two non-migration completions.

## 9. Fast compatibility

Fast uses the same semantic profile identity split.

Validated behavior:

- provenance-only profile commit churn does not invalidate an otherwise-current Fast result;
- exact Fast worker/result provenance remains strict;
- no Fast completion was invented retroactively;
- existing Fast attempt/history semantics are unchanged.

Post-merge current Fast arithmetic from run `36431916442`:
- total current scope: 399;
- attempted: 5;
- completed fit: 2;
- completed not-fit: 0;
- incomplete: 3;
- skipped due to authoritative Deep: 31;
- remaining: 363.

## 10. PPD-010 migration preservation

PPD-010 remains finite and complete:

- migration ID: `deep-legacy-full-reanalysis-with-preserved-positives-01`;
- frozen migration authority: `97d7798dfbf113ff0c3c4e71a75c7d50b39f3b3a`;
- total: 30;
- accepted: 30;
- accepted completed: 30;
- fit: 26;
- not-fit: 4;
- incomplete: 0;
- confirmed-risk count: 23;
- caution count: 7;
- pending: 0;
- complete: true;
- last accepted: `2026-09-28T10:36:02+00:00`.

No migration manifest/result was rebuilt or rewritten. No migration item was rerun. Original generation/work/profile pin/run-start/acceptance fields remain historical truth.

## 11. PPD-011 preservation

PPD-011 remains unchanged.

The dedicated Dossier/Deep release-year compatibility regression passed in the final PR and post-merge core runs. The eight known repaired release-year false rejects remain covered by their existing regression, while strict AppID/title/product identity, current evidence binding, expiry, exact AppID corroboration, and identity provenance remain fail-closed.

Dossier was never paused or manually rebuilt.

## 12. Production concurrency reconciliation

Fresh-`main` reconciliation was performed before each merge.

No branch state/cache/work snapshot was used to overwrite concurrent production progress.

Observed production state was preserved:

- Dossier current total scope: 399;
- accepted: 46;
- pending: 353;
- failed/recovery: 0.

PR #113, #114, and #115 contained implementation/tests/contracts/workflow changes only; no accepted production Deep/Fast/Dossier state was manually rewritten.

Normal automation serialized publication safely:

- PR #115 merge: `e864f882d74d26512d1430ab1632d7c93654f058`;
- full visual commit: `5ad0966f57f593aab94588b6b28b487185b63a6e`;
- atomic pre-AI follow-up: `e4170cd29586fb7a1bf25a1c4f6e54b3aacf8cbf`, parented on the visual commit;
- bounded commercial refresh: `d6d1b6a0ca15a243459b4007df6edaccfb78e39a`, preserving semantic fields.

## 13. Validation

Key green validations:

- PR #113 final PASS 2 core: run `36427891905`;
- PR #113 post-merge PASS 2 core: run `36428012132`;
- PR #114 PASS 2 core: run `36429794783`;
- PR #115 PASS 2 core: run `36431826189`;
- PR #115 package/ranking validation: run `36431826163`;
- PR #115 post-merge PASS 2 core: run `36431916442`;
- post-merge pre-AI: run `36431916031` — success;
- full canonical visual: run `36431916004` — success;
- follow-up bounded commercial visual refresh: run `36432000795` — success;
- full Pages deploy: run `36431998231` — success;
- final commercial-preserving Pages deploy: run `36432075275` — success.

Critical production validation in visual run `36431916004`:
- `VISUAL_FINAL_BUILD=BUILT`;
- item count 391;
- `CARD_EXPLANATION_VALIDATION=PASS`;
- normal card explanation, giveaway, Russian-description, ranking review/lookup and canonical commit steps all succeeded.

Final Pages environment:
`https://kentrap2011-hub.github.io/steam-kz-deals-2/`.

## 14. Current Deep counters

Canonical GitHub Deep projection on final `main`:

- total current coverage target: 399;
- normal first-pass attempted: 42;
- authoritative completed: 32;
- completed fit: 26;
- completed not-fit: 6;
- incomplete/recovery: 10;
- waiting for Dossier: 344;
- ready/pending: 13;
- normal first-pass remaining: 357;
- remaining until all authoritative: 367;
- recovery owned: 10;
- recovery eligible: 0;
- recovery pending: 0;
- ordinary emitted work items: 13;
- PPD-010 migration complete: 30/30.

The 13 ready/pending items are genuinely not-yet-current ordinary Deep work. None of the 30 reconciled migration targets is among them.

## 15. Published card/statistics result

Final deployed canonical payload is based on `d6d1b6a0ca15a243459b4007df6edaccfb78e39a`.

Published Progressive statistics are no longer zero. The published commercial-filtered processing scope reports:

- total current candidates: 397;
- analyzed success: 31;
- analyzed fit: 25;
- analyzed not-fit: 6;
- effective Deep results: 30;
- effective Fast results: 1;
- Deep first-pass attempted: 40;
- Deep authoritative completed: 30;
- Deep completed fit: 24;
- Deep completed not-fit: 6;
- Deep incomplete/recovery: 10;
- waiting for Dossier: 344;
- ready/pending: 13;
- Deep last write: `2026-09-28T10:36:02+00:00`;
- PPD-010 observability remains complete 30/30 with 23 confirmed-risk / 7 caution.

The difference from canonical Deep `32` is normal downstream publication filtering, not lost Deep state. Two current Deep-fit candidates are not in the final paid-card scope:
- `STAR WARS Jedi: Fallen Order™` / 1172380;
- `EARTH DEFENSE FORCE 5` / 1007040.

For Jedi, the immutable migration result is current and remains `analyzed_fit` with original preserved positives and its completed negative assessment. Its confirmed `unchanged_repetition` risk triggers the existing serious-risk fit cap; the resulting moderate branch fails the current price gate, so no final paid card is published. This is normal current Deep/business behavior, not semantic identity loss.

Published bounded sample:

**Black Skylands / 1143810**
- current source: `progressive_pass2`;
- effective source: `deep`;
- Deep stage: completed / fit;
- published rank: 9;
- fit: moderate;
- total score: 43.6;
- personal score: 19.6;
- preserved positive reason is present;
- confirmed risks are present;
- risk provenance includes exact Deep accepted-state binding and exact Dossier `evidence_refs`;
- caution is present with exact Deep/Dossier provenance.

**The Complex / 1107790**
- current PPD-010 result: `analyzed_not_fit`;
- it is counted in published Deep not-fit statistics;
- it is correctly absent from visible paid cards under normal Deep rules.

Therefore cards, ranking, risk/caution projection, and Statistics now consume current reconciled Deep authority instead of showing zero because of provenance-only profile commit churn.

## 16. Unresolved

No task-blocking unresolved issue remains.

The external Pages URL itself is not directly readable through this worker's web-fetch surface, but the exact canonical payload was inspected from final `main`, both Pages deploy workflows succeeded, UI regressions succeeded, and final Pages artifact/deployment IDs are recorded below. This does not block acceptance.

## 17. Status

`complete_ready_for_director_acceptance`

## 18. Recommended next step

Director reviews and accepts this report; keep existing Dossier/Fast/Deep workers and Scheduled Task configuration unchanged.

## 19. Exact PR / commit / run / artifact refs

Implementation and validation:
- PR #113 — semantic/provenance split and reconciliation; merge commit `bf4061d3b46f53b3dfcf0fe2a6eee83e770e1896`.
- PR #114 — production-history/visual provenance regression; merge commit `32f3354d1e43647271e8f1aac8884cec4ec92f77`.
- PR #115 — final grounded-negative Deep provenance publication fix; merge commit `e864f882d74d26512d1430ab1632d7c93654f058`.
- PR #114 core: `36429794783` — success.
- PR #115 core: `36431826189` — success.
- PR #115 package/ranking: `36431826163` — success.
- post-merge core: `36431916442` — success.
- post-merge pre-AI: `36431916031` — success.
- full visual run: `36431916004` — success; visual commit `5ad0966f57f593aab94588b6b28b487185b63a6e`; freshness artifact `10973782545`.
- post-pre-AI commercial visual run: `36432000795` — success; commercial visual commit `d6d1b6a0ca15a243459b4007df6edaccfb78e39a`; freshness artifact `10973149504`.
- full Pages deploy: `36431998231` — success; Pages artifact `10974106989`.
- final Pages deploy: `36432075275` — success; Pages artifact `10974421321`; deployed commit `d6d1b6a0ca15a243459b4007df6edaccfb78e39a`.

Canonical production commits:
- full visual: `5ad0966f57f593aab94588b6b28b487185b63a6e`;
- atomic pre-AI: `e4170cd29586fb7a1bf25a1c4f6e54b3aacf8cbf`;
- final commercial visual: `d6d1b6a0ca15a243459b4007df6edaccfb78e39a`.

## 20. Efficiency / reusable lesson

Do not use an exact provenance wrapper as the semantic cache/current-result key. Keep content semantics and execution provenance as separate first-class identities: semantic changes invalidate analysis, provenance changes remain auditable without forcing semantic reruns.

When historical results are reused, prove equivalence from immutable historical Git authority rather than copying/relabeling results.

When a state fix restores previously hidden semantic data, regress the entire deterministic publication chain, including post-processors. The final visual defect here was not in Deep reconciliation; it was a later compatibility finalizer that discarded provenance after the correct Deep projection had already been built.
