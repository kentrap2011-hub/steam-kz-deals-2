# Dossier V2 — individual canonical publication finish (ЧАТ 1)

**Task:** `dossier-v2-individual-canonical-publish-finish-01`  
**Result:** **BLOCKED_WRITER_AUTHORITY** for real GitHub canonical activation; inactive shared-writer implementation and synthetic verification prepared.  
**PR:** [#274](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/274), `implement/dossier-v2-individual-final-readiness-01` (draft, not merged).

## Implemented in PR #274

- Reused the original `taste_steam_review_dossier_buffered.py::drain_buffered_groups` entrypoint with an **explicit, separately gated** `notes_v2` input. Default V1 code path, original 3-game buffer, group progress and strict validation are unchanged.
- V2 branch rechecks the **original frozen Git Research → Assembly lineage** and the existing final `validate_dossier_strict` **again at writer entry**; it never promotes a caller's `ready` assertion. Uses the existing canonical Dossier cache format, `atomic_write_json`, and the existing writer staging of `data/cache` + optional `data/control`.
- For each valid item independently, the temporary writer transaction prepares the existing cache entry and exact-bound individual acceptance receipt under `data/control/dossier_notes_v2/canonical_accepted/`. Rejects invalid, missing, waiting, wrong-Git, unauthorized, stale, contradictory receipts and cache collisions locally; never overwrites differing accepted bytes.
- Exact-bound replay is idempotent. Fatal I/O errors abort the **entire** writer transaction to avoid committing a cache without the matching receipt. Later original groups do not wait for the broken item in an earlier group.
- Added only a **disabled** Notes V2-specific writer contract `config/dossier_notes_v2_individual_writer_contract.json` and additional tests in existing `scripts/test_dossier_two_stage_final_acceptance.py`. No workflow, CI, semantic stage, new scheduler, production state or V1 group logic changed.
- Previous PR #274 per-game readiness remains in place; PR #266 issuer and PR #270 Research receipts were not modified.

## Synthetic acceptance demonstration

Using the project's existing disposable Git fixture and original frozen 18 items:

- Group 1: valid A, strict-invalid B, valid C → A and C are written into **disposable** canonical-format cache/receipts; B is not.
- A separately ready game in the next original group is also written, independent of B.
- Repeating the identical input keeps the original bytes and receipts; a divergent existing cache or receipt is rejected, while valid siblings continue.
- An invalid AppID is rejected by frozen-manifest authority. Storage I/O failure is fatal before the GitHub transaction can be called successful.
- Test results are **offline simulations**. There is no live GitHub canonical acceptance, no real Research/Assembly, and no Deep-ready publication.

## Why the final live authority is still blocked

1. The active source of truth for Notes V2 still explicitly specifies `assembly.group_acceptance=existing_atomic_three_game_writer_only`, `active=false` and `authorized_for_canonical_ingest=false`. PR #266 also edits this Notes contract. This worker did **not** rewrite the overlapping file or silently supersede its authority.
2. The existing locked GitHub writer workflow has **not** been authorized or wired to supply the V2 marker, trial, immutable per-item commit pairs, and this explicit `notes_v2` mode in a canonical Git transaction. The new source helper is not a live publisher by itself.
3. A later separate cutover must establish the V2-only contract precedence and the V1 cache-collision/downstream-Deep binding rules, then independently verify the actual existing-workflow transaction under the unchanged `taste-steam-review-dossier-canonical-writer` lock.

**Therefore do not label this task READY_FOR_FINAL_REVIEW as a completed live V2 publisher.** It is a bounded implementation for code review and the required next authority decision, not an activation. Do not merge without independent QA and an explicit owner decision resolving points 1–3.

## Verification

- Added 3 synthetic regressions to the **existing** offline final-acceptance test suite: A/C + later group vs bad B, same-binding replay + cache collision/foreign AppID + live gate, fatal receipt-write I/O.
- Existing PR-only GitHub CI is the authoritative test result; inspect checks on the **final PR HEAD**, not a historical green run.
- Latest source-change commit before this report: `71dfd3f6d9e52dff5d241116a83a9652f9546177`. Report commit advances the PR HEAD; read final exact HEAD from PR metadata.
- Full suite cannot be run against a local authenticated repository checkout in this session (GitHub connector only; the container cannot reach github.com). Do not represent the synthetic Git fixture as a real GitHub write.

No merge, production update, workflow dispatch, Research, Assembly, automation or scheduler changes.
