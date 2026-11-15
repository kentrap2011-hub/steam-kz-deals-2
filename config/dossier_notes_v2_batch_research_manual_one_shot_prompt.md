# Dossier Notes V2 — Research, one GitHub write per game

**Purpose:** one explicitly user-launched, isolated Research run on the exact
previously frozen and GitHub-owner-authorized cohort. Not a developer session,
scheduler, issuer, retry loop, Assembly or production job.

## Start (short)

1. Follow CHAT_PROTOCOL.md and CHAT_CONTEXT.md. Only start after the existing one-use GitHub-owned Freeze and separate Authorize **commits** are
   present AND their real owner Actions run is completed successfully.
   For `dossier-notes-v2-fresh6-20261114-rerun1`, owner merge and authenticated
   first-attempt main push (not UI dispatch) is the only new issuer authority.
   For legacy cohorts, preserve their existing manual owner dispatch.
   A trial ID or a ChatGPT answer alone is never authorization.
2. Read the single frozen manifest at
   data/control/dossier_notes_v2/manifests/<trial_id>.json on
   sandbox/<trial_id> with GitHub connector fetch_file. Use the returned file
   SHA (manifest_blob_sha) and exact immutable items.
   Use the original owner-issued marker_commit, never an invented marker.
   Do not choose, replace or reorder games. If the manifest is inaccessible or
   inconsistent, STOP; do not reconstruct it from old messages.
3. For each item, research genuine public player opinion about exactly its
   game and edition. Summarize strengths, complaints and uncertainty
   neutrally. **No mandatory browser access log, proof-of-opening, timestamps
   or source-count quota.** Do not invent findings, personal review material
   or claims of accessing pages that were not accessed.

## One-call submission per game

Build a plain JSON document with:

- schema: "DOSSIER-RESEARCH-NOTES-V2"
- schema_version: 2
- assignment: the exact row from the manifest plus the same trial_id,
  original marker_commit and the GitHub-fetched manifest_blob_sha
  (as defined by frozen_assignment in the existing Python contract)
- notes_text: concise neutral Research notes, max 1200 characters
- research_status: notes_recorded, limited_evidence,
  no_verifiable_findings or tool_interrupted
- Optional unknowns_text, conflicts_text and source_log. Missing
  source_log is valid; if supplied, keep public safe locators only.

Use **one** mcp__GitHub__create_file for that game, on
sandbox/<trial_id>, at the exact create-only path:

data/ai_inbox/dossier_notes_v2/<trial_id>/g<group_sequence as six digits>/<appid>--<assignment_id>.json

Never update, overwrite, resend, pick a different path or retry an ambiguous
create. Continue independent games only when previous writes are confirmed.
A returned candidate commit is **not** an acceptance receipt.

## After the Research batch

Report which exact AppIDs produced GitHub candidate commits and which did not.
Do not write a typed receipt, manually calculate Git hashes, perform handoff
serialization, or run the old connectorPreflight/connectorPublishItem path.

For the exact rerun1 cohort, a real owner-authenticated sandbox `push`
from `create_file` triggers GitHub receipt ingestion automatically using
`.github/workflows/ingest-dossier-notes-v2-research-on-owner-push.yml`.
This is **not** an automatic semantic retry: the chat still selects no work,
and GitHub validates exact owner event / branch / immutable Git candidate
before adding one typed receipt per item. A GitHub candidate commit alone is
not evidence that a receipt exists; inspect GitHub receipts when finished.
Missing/invalid candidates remain explicitly incomplete or rejected.

The **manual** `.github/workflows/ingest-dossier-notes-v2-research.yml`
continues as legacy fallback for already authorized cohorts only.
Existing strict Assembly and writer contracts are unchanged. Research does
not manually run receipt workflows or claim strict acceptance.

No V1, Deep, Assembly, canonical production, schedules, automatic retries or
new grants. Previous fresh6/original18 immutable submissions are not replayed.
