# Dossier V2 — individual final readiness (ЧАТ 1)

Task: `dossier-v2-individual-final-acceptance-implement-01`  
Status: **BLOCKED_CANONICAL_WRITER_AUTHORITY** for actual independent canonical publication.  
Scope: **inactive offline per-item readiness only**, one draft PR. Nothing merged.

## Evidence and decision

- `config/dossier_research_notes_v2_contract.json` has `active=false`, `authorized_for_canonical_ingest=false`, `assembly.group_acceptance=existing_atomic_three_game_writer_only`. `scripts/dossier_research_notes_v2.py::inspect_assembly` already uses the existing `validate_dossier_strict` independently per immutable research/assembly Git chain and returns `strict_item_valid_pending_existing_atomic_group_ingest`; this is **not** canonical acceptance.
- `config/dossier_two_stage_interfaces_contract.json` requires `original_three_game_group_final_acceptance_atomic=true`; `config/dossier_two_stage_async_buffer_contract.json` specifies existing atomic three-game ingest; `config/dossier_two_stage_final_acceptance_bridge_contract.json` has `required_size=3`. `scripts/dossier_two_stage_final_acceptance.py::inspect_original_groups` builds a group artifact only if **all three** pass; only `scripts/taste_steam_review_dossier_buffered.py::drain_buffered_groups` through the shared existing writer can persist it.
- GitHub remains owner of authorization, immutable scope, validation and canonical writes under `config/execution_ownership_contract.json`. This task does **not** authorize changing the V1 shared writer or the V2 publication authority. Accordingly the full requested independent **canonical** acceptance is not yet supported; a V2 claim of individual canonical acceptance would be false.

## Minimal isolated implementation

- Added only `scripts/dossier_research_notes_v2.py::individual_final_readiness`: read-only inspection of the exact immutable 18-item manifest, each item's existing original Git Research/Assembly commits and **existing** strict final validator via `inspect_assembly`; no extra validator, durable receipt, queue, workflow, publish or authority. Five item-local statuses: `ready`, `invalid`, `missing`, `waiting`, `error`. Unknown AppID fails the frozen scope. Invalid item cannot block already valid siblings.
- Every response, including `ready`, explicitly sets `canonical_acceptance=false`, `deep_ready=false` and `requires_separately_authorized_canonical_writer=true`; no production or stage flags changed.
- Existing offline regression file `scripts/test_dossier_two_stage_final_acceptance.py` extended with 4 synthetic Git/strict cases: A valid/B strict-invalid/C valid, B missing, B runtime-error, B still waiting, malformed/foreign or false Git binding, complete original 18 order and zero cross-item acceptance. Existing V1 group-writer regression remains unchanged. Existing PR-only CI workflows already cover this file and source; **none added or edited**.
- No overlap with PR #266 changed files (`config/dossier_research_notes_v2_contract.json`, V2 main tests, issuer workflows/scripts) or PR #270 (`scripts/dossier_notes_v2_per_item_receipts.py`, receipt tests); this implementation does not assume either PR is merged.

## Architecture preflight

1. Owner: existing GitHub control plane / shared canonical writer.
2. Authorization: currently inactive Notes V2 permits only synthetic/offline computation; no canonical writes.
3. Interactive chat does not gain semantic-worker or publication responsibilities.
4. No new recurring job, quota, queue, retry, source of truth, or CI gate.

## Verification and limits

- New tests added to the *existing* `validate-dossier-async-final-acceptance-integration.yml` and `validate-dossier-research-notes-v2.yml` pull-request trigger paths **without modifying those workflows**. Existing tests must be observed at the final PR HEAD. No real Research, Assembly, workflow dispatch, canonical ingest, Deep, production or Deploy was run.
- Direct local full-suite execution is unavailable in this worker environment because this repository is accessible via the GitHub connector rather than an authenticated local checkout. GitHub PR check status, not an assumption, decides whether these tests passed.
- Remaining blocker: independent **canonical** single-game persistence under a separately approved writer authority, preserving original V1 atomic group publication. Future authority/contract change requires a separate user/Director decision and independently reviewed writer integration. Offline `ready` must never be treated as published or Deep-ready.

Outcome: **BLOCKED_CANONICAL_WRITER_AUTHORITY** (bounded offline implementation offered for independent QA; no final publication).
