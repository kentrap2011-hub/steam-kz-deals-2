# WORKER TASK — Taste Dossier Live Web Evidence Acceptance 02

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If a tool opens another repository by default or the repo target is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-live-web-evidence-acceptance-02`
Mode: `READ / VALIDATE / ACCEPTANCE`

## Authoritative manual UI input from user
Treat the following as confirmed authoritative Scheduled Task output from one manual `Run now` invocation:

> Published transport artifact for canonical group 1 of snapshot 6e4f851c… via create-only GitHub transport; commit 15b386859c945ce159ebb7fd35cfed6d00c3fb72.
>
> After publication, the liveness guard still showed the same snapshot/plan and canonical expected sequence 1, so processing continued to predeclared group 2 as permitted. Group 2 descriptor was loaded and evidence research started, but no group-2 artifact was published in this invocation.
>
> This is transport publication progress only, not canonical acceptance or task completion.

Do not attempt to re-read Scheduled Task UI state. The above manual text is sufficient UI evidence.

## Goal
Determine whether the newly published group-1 web-evidence artifact for the fresh activated snapshot is canonically valid and accepted by the GitHub-owned ingestion/control plane, and whether the live V2 web-evidence acceptance can now be considered successful for group 1.

Do not run the Scheduled Task again.

## Read first / START gate
Follow `CHAT_PROTOCOL.md` START gate fully, then read at minimum:
- `DIRECTOR_PROTOCOL.md` as applicable;
- `CHAT_CONTEXT.md`;
- relevant `PROJECT_ROUTES.md`;
- relevant `PROJECT_DECISIONS.md`, especially active Taste dossier/web-evidence decisions;
- `config/execution_ownership_contract.json`;
- `reviews/worker_reports/taste-package-member-activation-01.md`;
- prior rejected live acceptance report `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-01.md`;
- relevant active dossier web-evidence contract/schema/validator docs only as needed for acceptance validation.

Run architecture preflight before any action beyond reading.

## Acceptance target
Snapshot:
`6e4f851cd4c9e6d6f5a6c265ba30b80ee0d338b6477401453111be06109c8f53`

Published transport commit:
`15b386859c945ce159ebb7fd35cfed6d00c3fb72`

Expected canonical group sequence at invocation start: `1`.

## Validate
Use repository/GitHub evidence to determine:

1. The transport artifact corresponds exactly to snapshot `6e4f...`, group sequence `1`, and the canonical group-1 descriptor/hash.
2. The artifact satisfies the strict V2 web-evidence schema/contract and identity binding for all ten items.
3. Evidence is not a store-only placeholder and contains genuine ordinary-web player-feedback synthesis with compact provenance, including the required Russian-language search attempt semantics.
4. No raw review bodies, prohibited quotes/usernames, or malformed provenance were persisted.
5. Technical/current-state claims respect recency/temporal status rules; historical fixed launch issues are not presented as current without support.
6. The DLC item `App_2378500 / Baldur's Gate 3 - Digital Deluxe Edition DLC` is treated as its own exact dossier subject at this stage, without being remapped to base game `1086940` and without being rejected merely because it is DLC.
7. The prior hybrid package identity failure is absent from this group/snapshot.
8. GitHub-owned canonical ingestion/reconciliation either:
   - accepted group 1 and advanced canonical progress/expected sequence coherently, or
   - rejected/has not accepted it, in which case identify the exact machine-readable reason/state.
9. No group-2 transport artifact was published by the same Scheduled Task invocation. If a later independent publication exists, distinguish it by commit/time and do not misattribute it.
10. No manual rewriting of canonical progress/cache/receipt occurred.

## Interpretation rules
- Transport publication alone is NOT acceptance.
- Do not declare success until canonical GitHub state proves group-1 acceptance.
- If ingestion is automatic and still legitimately pending, observe the bounded repository-defined workflow/state. Do not invent a retry or manually force progress.
- If a direct ordinary deterministic ingestion defect is exposed, do not implement a fix in this acceptance task unless existing protocol explicitly authorizes it. Prefer `blocked` with exact defect and a bounded next task.
- Do not inspect or modify Scheduled Task UI.
- Do not press `Run now`.

## Success criteria
A successful live acceptance requires at minimum:
- exact group-1 artifact valid under strict V2;
- all ten identities/evidence objects valid;
- canonical ingestion accepted the contiguous group-1 result;
- canonical completed count advanced from `0` to `10` and remaining count/expected sequence updated consistently (normally expected sequence `2`, subject to canonical contract);
- no stale/invalid artifact accepted;
- no group-2 artifact falsely credited to this invocation;
- package-member activation invariants remain intact.

If group 1 is accepted but evidence quality reveals a substantive contract gap that strict validation does not catch, mark acceptance as rejected/blocked and explain the gap rather than rubber-stamping it.

## Restrictions
- READ/VALIDATE only except durable report publication.
- Do not change code, schemas, workflows, prompts, ranking, production artifacts, queue, progress, receipts, or Scheduled Tasks.
- Do not run production workflows manually unless the repository explicitly defines a read-only validation workflow and protocol allows it; ordinary observation is preferred.
- Do not use any other repository.

## Durable report
Publish to `main`:
`reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-02.md`

Report must include:
- architecture preflight;
- exact transport artifact path/hash/commit;
- validation outcome for all ten group-1 items;
- concise evidence-quality assessment, especially current-vs-historical technical claims and RU search attempt;
- canonical ingestion/progress outcome;
- whether group 2 was published or only researched;
- exact acceptance verdict;
- production side effects (should be none except prior external transport publication and automatic canonical ingestion already owned by GitHub);
- exactly one next step.

Allowed final statuses:
- `accepted_live_web_evidence_group1`
- `rejected_live_web_evidence_group1`
- `blocked`

Ensure final durable report is in `main` before completion. Stop after report publication.