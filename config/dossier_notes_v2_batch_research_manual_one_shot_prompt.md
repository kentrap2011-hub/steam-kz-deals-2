# Dossier Notes V2 — Research, one GitHub write per game

**Purpose:** one explicitly user-launched, isolated Research run on the exact
previously frozen and GitHub-owner-authorized cohort. Not a developer session,
scheduler, issuer, retry loop, Assembly or production job.

## Start (short)

1. Follow CHAT_PROTOCOL.md and CHAT_CONTEXT.md. Only start after the existing
   owner Freeze **and separate Authorize** Actions have succeeded for this exact
   one-use trial. A trial ID supplied in chat is not authorization by itself.
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

The repository owner can separately run the **manual** GitHub Actions workflow
.github/workflows/ingest-dossier-notes-v2-research.yml with this trial ID.
GitHub then authenticates the owner issuance, independently validates the
candidate's exact immutable one-add Git commit, and creates each missing typed
Research receipt. Invalid games do not block valid siblings. Existing receipt
and Assembly contracts remain in force. Research does not trigger that workflow
and must not claim acceptance before its confirmation.

No V1, Deep, Assembly, canonical production, schedules, automatic retries or
new grants. Previous fresh6/original18 immutable submissions are not replayed.
