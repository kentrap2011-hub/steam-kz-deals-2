# Dossier V2 Research — replace manual Git transport with one create-only submission

Status: CONTRACT/DESIGN approved in conversation 2026-11-14; **IMPLEMENT NOT YET DONE**. Scope: isolated manual Research V2 only. This document is the implementation checklist, not a semantic launcher or a new grant.

## User intent

- Research spends its effort finding and summarizing public player opinions about the exact game/edition.
- No mandatory evidence-of-browsing audit, per-page opening attestation, access-state log, or timestamps. Source inspection is a quality question for an optional separate audit, not a runtime transport gate. Never invent reviews or assert an inaccessible source was read.
- Remove the chat's manual preflight, handoff SHA256, Git blob/tree/commit/CAS, and typed receipt construction. Move deterministic checks and receipts to GitHub-owned ingest.
- Retain owner-issued immutable scope, no overwrite, exact assignment, isolated sandbox, independent validation and acceptance, no retry/production/scheduler/Deep/V1 changes.

## Proposed data flow

1. Existing GitHub Freeze/Authorize remains the sole authority for trial, marker, manifest, assignment, order, sandbox and eligibility. No new owner or automatic authorization.
2. The Research chat reads one small, GitHub-prepared **submission view** for its authorized trial (immutable assignment IDs, exact title/edition, appids, target paths; no need to reconstruct grant chains). The view is produced/validated by GitHub, not trusted merely because a user pasted it. Before implementation, establish how a read-only chat can obtain a GitHub-attested current authorized view with at most one connector read and without a fresh multi-call attestation.
3. For each authorized game the chat does semantic Research and calls `mcp__GitHub__create_file` **once** with a create-only JSON submission in a dedicated isolated intake path on the sandbox branch. The submission contains exact immutable assignment and notes; no worker-written receipt or worker-chosen queue/retry. `create_file` returns a commit SHA; never call it again after ambiguous failure. Confirm the actual GitHub tool contract's create-only behavior and branch semantics.
4. A GitHub-owned ingest validates the owner-issued authorization and frozen assignment, original Git blob/one-add/ancestry, privacy and schema; generates typed receipt and stores accepted/rejected per-item state. It must be idempotent on the exact candidate SHA and must not block unrelated games. On invalid or ambiguous transport, fail closed without pretending acceptance. **Do not use the current strict writer unchanged if it requires chat-created two-commit receipts**: adapt its input route while retaining independent acceptance authority.
5. Existing Assembly sees the same immutable Research identity and GitHub-generated typed receipt (or an explicitly versioned compatible projection); Assembly itself is not refactored in this task.
6. Existing sandbox and production remain separate. No implicit GitHub Actions dispatch or canonical ingest; run GitHub-owned ingest only through an explicitly authorized existing/manual trigger, or a new narrowly approved sandbox-only trigger if necessary. Do not silently activate scheduled workflows.

## Research payload simplification

- Keep `schema`, `schema_version`, exact `assignment`, `notes_text`, and `research_status`; optional `unknowns_text` and `conflicts_text`.
- Make `source_log` optional for the **new versioned intake contract** (or allow an empty array), with no minimum number of sources. Do not delete existing V2 schema in-place if existing accepted candidates depend on it. If links are useful, allow a small optional `sources` array, but no opening-state, observation-time, or proof requirements.
- Distinguish research quality from technical integrity: do not gate ingestion on an audit of whether a web page was actually opened. Validate safe public locators if provided, never private raw reviews.
- Preserve compatibility with all already submitted fresh6 Research candidates and receipts, without rewriting immutable files.

## Required implementation work

- Identify the exact current V2 issuer, frozen manifest, per-item writer, receipt validator and Assembly reader. Add the minimal versioned Research intake and GitHub-side receipt generation; update all direct consumers atomically.
- Replace the Research launcher with a short semantic instruction and one-call create-only submission path. The old connector/runbook can remain for Assembly or legacy pilots, but **must not** be required by new Research.
- Add deterministic offline tests: authorized six-game path; wrong AppID/title/edition; forged assignment; stale/missing owner authorization; duplicate/overwrite; unrelated sandbox path; interrupted submission; partial batch; exact SHA/blob/one-add; privacy; optional/empty sources; old fresh6 compatibility; Assembly read of GitHub receipt; no production mutation.
- Add timing instrumentation to report: Research time, GitHub calls per game, ingest latency, failures, total wall clock. Do not claim target speed as measured until a live run.
- Run source PR CI and independent review before merging. Live six-game test requires a **new explicit owner-authorized cohort**; never reuse an exhausted one-use grant, replay old submissions, or mutate original18/fresh6.

## Definition of done

A newly authorized isolated six-game Research run uses one create-only connector write per game (plus a bounded read of a trusted GitHub-prepared view), no manual handoff or chat-generated receipts; GitHub accepts/isolates each item independently and Assembly can consume accepted Research. Actual wall-clock and call counts are reported. This file alone is **not implementation**.

## Non-goals

No automatic source-quality attestation, mandatory review audit, second queue, retry daemon, schedule, canonical production activation, Dossier V1/Deep/ranking changes, or reissue of the prior six-game grant.
