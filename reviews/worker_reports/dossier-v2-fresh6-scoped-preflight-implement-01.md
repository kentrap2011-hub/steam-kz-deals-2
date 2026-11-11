# Dossier V2 fresh6 — exact pinned GitHub scope preflight (ЧАТ 2)

**Status:** `BOUNDED_PREPARATION_IMPLEMENTED; FRESH6_ISSUER_NOT_IMPLEMENTED; NO_SEMANTIC_AUTHORITY`.  
**User instruction:** “Делай то что надо” after draft readiness RECON PR #438; interpreted as approval of the *bounded preparation path only*, not permission to dispatch new manual owner actions, launch Research/Assembly, replace V1, update original18 or promote V2 to production.

## Concrete implementation in this draft source PR

1. `config/dossier_notes_v2_fresh6_preparation_contract.json` — immutable-source candidate set of **exactly six** games, 2026-11-11 prepared snapshot, original GitHub worker-index and two descriptor Git blob SHA pins, exact per-item AppID/title/edition/order/status and existing or absent V1 baseline blobs. All authority flags **false**; explicitly `scoped_preparation_only_not_issuer` and no owner dispatch. This is NOT a V2 manifest or grant.
2. `scripts/dossier_notes_v2_fresh6_preflight.py` — a pure read-only Git and JSON check against source `main@665f5d0202859a6bac20566671f10158538e4764`; verifies actual prepared index and group descriptor blob SHAs, six exact independent identities, exclusion of all original18 AppIDs, exact present/absent per-AppID baseline from that commit, structural V2 global inactive gate, and all scoped execution flags off. CLI `--check` can return only `scope_verified_preparation_only` and explicit non-authorization flags; it never creates a branch/manifest/marker/grant/receipt or writes to the repository.
3. `scripts/test_dossier_notes_v2_fresh6_preflight.py` — one positive check against actual pinned historical Git objects plus offline negative mutations for original18 substitution, identity/title/edition/index/order, group/snapshot drift, authority toggles and wrong Git source SHA/path. Mutated JSON is **synthetic adversarial scope input**, not a substitute for real player reviews.
4. `.github/workflows/validate-dossier-research-notes-v2.yml` — existing pull-request-only inactive V2 CI now checks this preflight with full Git history (`fetch-depth:0`), then keeps all prior Notes V2, receipts and old strict writer regressions/activation guard. No scheduled or manual semantic execution event was added.
5. This report only. No `CURRENT_TASK.md` shared-handoff edit or original18 candidate/grant/receipt/data write.

## Exact six and source

All from existing `main` prepared `snapshot_id=25c227d782188699f56b5702b3f0cfa63b101d890f09620b7b59893fab93c1af`, not a new external catalog:

| V1 source descriptor | AppID | Exact title |
|---|---|---|
| g000001 index 0 | 1000010 | Crown Trick |
| g000001 index 1 | 102600 | Orcs Must Die! |
| g000001 index 2 | 1029690 | Sniper Elite 5 |
| g000070 index 0 | 49520 | Borderlands 2 |
| g000070 index 1 | 499180 | Braid, Anniversary Edition |
| g000070 index 2 | 501590 | Bulletstorm: Full Clip Edition |

Source grouping and index order are provenance, **not issued V2 authority**. Three one-stage baselines have exact original Git blobs; for three others `App_{appid}.json` was absent at the pinned source commit. Source details and intended experimental stratification remain in [RECON PR #438](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/438).

## Architecture preflight

1. **Owner:** GitHub alone owns immutable candidate identity, scoped issuer/grant, ordering, receipt, strict final validation and persistence, under `config/execution_ownership_contract.json`.
2. **Current contract:** `config/dossier_research_notes_v2_contract.json` still permits only original18 limited trial; `config/dossier_notes_v2_individual_writer_contract.json` and global V2 flags remain inactive. This PR introduces a separate preparation-only contract, **not semantic authority or a new writer**. That is the safe first contract stage before adjusting runtime ownership-sensitive entrypoints.
3. **No control-plane transfer:** current interactive chat does not choose live scope, retry errors, grant authorization, publish results or replace GitHub's issuer.
4. **No recurring addition:** no task, timer, owner action, scheduler, queue, retry loop, production stage or new event hook. Existing CI is PR-only.

**Proven limitations / further work required:** old `scripts/dossier_research_notes_v2.py::_original_rows/_manifest/manifest_blueprint`, issuer freeze/authorize, `scripts/dossier_notes_v2_original18_pilot.py`, authenticated transport and the optional shared sandbox writer all bind to original18. This PR does **not** generalize or bypass them. In a next bounded **separately reviewed** implementation, create exact fresh6-only GitHub owner-issued grant+marker+authorization and frozen six-item manifest/assignments, fresh two one-shot semantic entry and create-only per-item receipts, plus a new optional isolated sandbox writer using the same existing strict writer lock. Preserve all original18 and V1 behavior and reject wrong actor/main SHA/run attempt/trial/edition/receipt/collision. **No live launch until actual owner authorization and successful independent QA of implementation.**

## Measured vs unmeasured / final boundary

- Mechanical static source contract and code committed into this draft PR: **implemented**, but automated test result must be checked at exact final PR HEAD.
- GitHub Actions PR CI: **NOT YET ATTESTED** in the initial report text; verify the actual run/jobs against final HEAD before acceptance.
- Fresh6 Research 0/6, Assembly 0/6, GitHub-accepted sandbox dossiers 0/6, canonical V2 0/6: **NOT_TESTED** (no authority or execution).
- Research time, Assembly time, published GitHub transport time, source quality / V2 versus V1 cost and quality: **NOT_MEASURED**.
- Original18 immutable results and all present-day V1/Deep/site/production: **unchanged**.

**Why full authority is not included in this PR:** current old issuer is structurally hardcoded in multiple files to 18 and old unique original grant. Changing one count or using old `issuer_version=v2` with six games would break explicit provenance/consent gates and risk unauthorized publishing. The safe independently testable preparation source is kept separate from any runtime authorization. No user consent for actual owner dispatch or semantic pilot is inferred from approving this preparation.
