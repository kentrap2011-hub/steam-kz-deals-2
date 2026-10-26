# Dossier V2 PR #266 — remove extra freeze-run provenance gate

Task: `dossier-v2-pr266-remove-extra-freeze-provenance-gate-01`  
Status: **READY_FOR_DIRECTOR_DECISION** — code and synthetic GitHub CI validated; **no actual V2 launch authorized**.  
Target: existing [PR #266](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/266), `implement/dossier-v2-existing-issuer-adapt-01`, based on exact earlier PR head `e3c5de3ce0a1f7bbefa262af7b4faa87c5ab5443`. This is a continuation of the same PR; no competing implementation or merge.

## Minimal change

- `scripts/dossier_shadow_research_feasibility.py` — removed the unconditional `require(False, ... independently attested ...)` that rejected **every** structurally valid V2 authorization solely because an independent **original freeze GitHub Actions run → marker** attribution was absent. No replacement attestation, extra workflow, trust system, or retry path was introduced.
- Kept `v2_freeze_chain` checking exact one-add single-parent manifest and nonce marker, approved main first-parent ancestry, scoped grant ancestry and the unchanged full 18-item original title/edition/group/assignment bindings.
- Kept the existing GitHub workflow dispatch/actor checks, immutable scoped grant mechanism, exact contract/code blob checks, direct-child authorization, create-only remote old-SHA lease, re-fetch and replay rejection. The supplied original 18 and V1 flow are unchanged.
- `scripts/test_dossier_research_notes_v2.py` — replaced the now-obsolete negative test (valid freeze *must* fail for missing external attribution) with a full **positive native issuer test**.

Code commit `a4bbc90cf60c750190c566ea7b1b0d2714095aa4`; test commit `f10b3f1de6f4771d7e3263fdeca4c0cad582d086`.

## Normal authorized path proven offline

The positive test constructs an exact scoped immutable human grant on a disposable Git `main`, creates the real two-commit V2 manifest/marker from the original 18 rows, pushes that frozen marker to a local bare remote, resets `main` to the legitimate source/approved grant commit, models an exact first-attempt authorization dispatch, and calls the **real** `publish_v2_authorization` with the actual `v2_grant`, `v2_freeze_chain`, `local_v2_authorization`, `verify_v2_authorization` and remote re-fetch/lease logic. Only the canonical *GitHub remote URL identity* check is patched to permit a disposable local bare repository; the authorization checks are not mocked.

It succeeds with `issued_inactive_V2_authorization_not_semantics`, the authorization is a direct child of the frozen marker, the remote ref advances to that exact commit, semantic execution remains false, and an identical second authorization attempt is rejected before another write. No independent original freeze-run attestation is supplied or consulted.

Existing malicious-extra-path, merge-parent, foreign-source, modified grant, historic V1 SHA, race and replay checks remain negative.

## Verified GitHub CI at test commit

- [V2 / autonomous Assembly run 40322002190](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40322002190): **SUCCESS**, 50/50 Notes V2 synthetic tests (including the positive authorized issuer test) + 14/14 existing Git receipt tests; activation guard and syntax pass.
- [Original V1 publisher run 40322002193](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40322002193): **SUCCESS**, V1 feasibility 12/12, publisher 7/7, original Research trial 8/8, plus original six-group offline Git freeze.
- [Eventual chain 40322002266](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40322002266): SUCCESS.
- [Backlog 40322002191](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40322002191): SUCCESS.
- [Site task registry 40322002402](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40322002402): SUCCESS.

These runs validate the code/test commit; creation of this report adds a separate final PR commit without changing code. GitHub Actions PR checkout may be a synthetic merge ref rather than a detached raw PR head; the direct GitHub code/test commit is recorded above.

## Boundaries and decision

- `config/dossier_research_notes_v2_contract.json` still has `manual_v2_issuer.enabled=false`, null grant pins and `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`, `production_enabled=false`. The tested *prospective, explicitly approved* issuer works, but no actual live issuance is requested or performed here.
- A **separate concrete user authorization** is required before executing the real V2 freeze/authorization workflows or any Research/Assembly. This task authorizes only code simplification and synthetic checks. Real GitHub Actions freeze-run attribution was not claimed; it is intentionally *not* a new gate after the user's explicit decision.
- No new CI/workflow/validator/scheduler, no real freeze, no V2 Research/Assembly, no V1/production/ranking changes, no merge or force push.
- `CURRENT_TASK.md` in shared `main` has active concurrent worker records; it was not overwritten. This exact worker outcome and decision handoff are persisted here.

**Director decision:** review the existing PR #266 and decide whether to merge its inactive issuer adaptation. Do not request another general origin-attribution audit as a prerequisite; the explicit decision removes that additional gate. Any genuine live invocation still requires separate, concrete user permission.

**Efficiency note:** most elapsed work was mandatory START/task/provenance context reads, a narrow two-file edit, and real GitHub PR CI. Future similar changes can use the current short worker report, a targeted source range and the existing Notes V2 + V1 checks, without broad history or additional reviews.
