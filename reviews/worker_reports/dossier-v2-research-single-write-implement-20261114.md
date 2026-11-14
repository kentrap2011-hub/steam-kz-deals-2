# Dossier V2 Research single-write implementation report (2026-11-14)

## User-approved objective

Research should search and summarize actual public opinions with minimal technical metadata and no mandatory proof that individual pages were opened. ChatGPT should not manage Git history, SHA handoffs or receipt construction. Move correctness/authority handling into GitHub; retain existing immutable frozen scope and Assembly readiness.

## Implementation in source PR #450

- `config/dossier_notes_v2_batch_research_manual_one_shot_prompt.md`: one manifest read and one GitHub create-only file write for each frozen game; no manual preflight/hash/handoff/receipt. The new workflow is manual only.
- `config/dossier_research_notes_v2.schema.json` and `scripts/dossier_research_notes_v2.py`: accept absent source_log (optional). Existing source-log records and safe locators still validate.
- `scripts/dossier_notes_v2_research_receipt_ingest.py`: owner-confirmed batch issuer, exact candidate Git lineage, generate typed Research receipts through unchanged strict receipt blueprint, one per item, with immutable original blob/one-add, independent sibling processing, no overwrites, no automatic retries, no main or canonical writes. Print processing duration/counts.
- `.github/workflows/ingest-dossier-notes-v2-research.yml`: manually dispatched on main by the repository owner, runs trusted merged-main Python code against isolated, separately issued sandbox Git worktree. Existing authenticated GitHub Actions owner authorizer remains mandatory.
- `config/dossier_research_notes_v2_contract.json` and legacy connector runbook: Research-specific route recorded, previous connector remains for Assembly and older cohorts.
- `scripts/test_dossier_notes_v2_research_receipt_ingest.py`: synthetic authorized six items, no source log, prior source-log compatibility, missing/partial, invalid binding, broken JSON, altered candidate, extra-file candidate, unsafe locator, idempotent receipt, Assembly consumption, and wrong/manual-owner refusal.
- Existing V2 validation PR workflow updated to run new regressions.

## Architecture and scope

GitHub remains the only source of scope/order/authorization/strict acceptance. There is **no new automatic watcher, worker schedule, retry queue or production activation**. One create_file commit is not an accepted result; accepted Research requires later GitHub-owned typed receipt and independent Assembly. Previously submitted fresh6/original18 files and receipts are not modified or replayed.

## Verification

Source and offline tests are in PR #450. Final exact HEAD PR checks and independent source review are required before merge. New owner-issued real six-game live run and actual elapsed performance were **not** performed in this source implementation; only a fresh explicitly authorized cohort may test them.

## Operational difference

Old interactive path: 14 GitHub preflight calls then ~11 per game and manual handoffs. New interactive Research: one frozen manifest read for the batch plus **one create-only GitHub write per game**. GitHub performs immutable checks and receipts in a single separate owner-manual workflow dispatch for all ready items; no claim of measured end-to-end speed until a live run.

## Status

`implemented_in_draft_pr; CI_RUNNING; no_live_ingest_or_merge`.
