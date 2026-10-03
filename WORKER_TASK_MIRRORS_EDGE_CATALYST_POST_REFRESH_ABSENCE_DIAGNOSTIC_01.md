# WORKER TASK — Mirror's Edge Catalyst post-refresh absence diagnostic 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `mirrors-edge-catalyst-post-refresh-absence-diagnostic-01`
Mode: `DIAGNOSTIC / READ-ONLY PRODUCTION TRACE`
Worker slot: `ЧАТ 1`

Durable report:
`reviews/worker_reports/mirrors-edge-catalyst-post-refresh-absence-diagnostic-01.md`

## User-observed problem

After the accepted fresh deal discovery refresh fix (PR #140), Mirror's Edge Catalyst still does not appear in the user-visible result.

Known probe identity:
- title: `Mirror's Edge Catalyst`
- Steam AppID: `1233570`

The Director must NOT diagnose the cause in advance. This worker owns the root-cause trace.

## Goal

Determine exactly why AppID `1233570` is absent now, using current repository truth and current production artifacts/runs.

Find the first deterministic stage where the game is absent, excluded, stale, blocked, or not published.

Do not assume the old pre-PR #140 diagnosis still applies.

## START gate

1. Read current `CHAT_PROTOCOL.md` and fully execute START gate.
2. Read current `DIRECTOR_TASK_BOARD.md`.
3. Read this task fully.
4. Read the accepted fresh-discovery task/report for PR #140 and the current production ownership contracts relevant to discovery -> shortlist -> mailing -> pre-AI -> semantic work -> visual publication.
5. Reconcile against current `main` before drawing conclusions.

Do not start another task.

## Scope

Trace AppID `1233570` through the current live/canonical pipeline in order.

At minimum inspect:

1. current production discovery/catalog output;
2. current shortlist and shortlist index/manifest;
3. current mailing projection;
4. current Store state/cache and pre-AI Store snapshot;
5. current content/family/deal/taste candidate projections as applicable;
6. current semantic work queues/results needed for publication;
7. current final ranking/visual payload;
8. current Pages/publication artifact if repository truth says the game reached visual production;
9. the exact GitHub Actions runs that most recently refreshed the relevant stages after PR #140 merged.

For each stage record one of:
- present and valid;
- absent;
- explicitly filtered, with exact deterministic rule;
- stale / not refreshed;
- blocked on semantic state;
- publication-only mismatch;
- cannot be proven from current evidence.

Stop the root-cause trace at the FIRST stage that explains downstream absence, but inspect enough downstream metadata to prove there is not a second independent publication mismatch masking the primary issue.

## Required questions

Answer explicitly:

1. Did a true post-PR-#140 fresh production discovery run actually execute on `main`?
2. If yes, did that run discover AppID `1233570`?
3. If discovered, what was the first later stage that removed or blocked it?
4. If not discovered, why did the current discovery owner fail to include it?
5. Is the current absence caused by:
   - discovery not running;
   - discovery coverage/input defect;
   - deterministic eligibility/filtering;
   - stale handoff;
   - current sale/region state;
   - semantic-work incompleteness;
   - ranking/publication gating;
   - Pages artifact lag;
   - or another precisely identified cause?
6. Is PR #140 itself defective, or did its live acceptance simply never occur / fail for an external or downstream reason?
7. What is the smallest correct next action?

## Evidence requirements

Use repository/GitHub truth first.

For current public Steam/KZ sale facts, use the existing repository-owned source/provenance when available. If external verification is necessary, use only the normal evidence route allowed by current project contracts and record the source/time precisely.

Do not infer from the visible website alone.

Cite exact:
- commit SHAs;
- workflow run IDs;
- artifact paths;
- timestamps;
- relevant AppID rows/keys;
- exact filtering/status reason when one exists.

## Important boundaries

This is DIAGNOSTIC ONLY.

Do NOT:
- implement a fix;
- special-case AppID `1233570`;
- manually insert the game into shortlist/mailing/pre-AI/visual data;
- rerun or dispatch production merely to make the symptom disappear;
- change ranking/scoring;
- change Dossier/Deep/Fast semantics;
- run semantic workers;
- create or modify ChatGPT Scheduled Tasks;
- modify production state;
- open an implementation PR.

You may create only the durable diagnostic report and any report-only metadata required by `CHAT_PROTOCOL.md`.

## Historical context to verify, not trust blindly

PR #140 `Fix stale deal discovery freshness handoff` was merged as:
`7df5ed0cbe9dd9217c56344e0caab47dd366915f`.

Its accepted report stated implementation was complete but live KZ production acceptance was still pending at that time.

Subsequent unrelated work includes:
- PR #141 production-trigger isolation;
- PR #143 Dossier frozen invocation rollover safety.

Do not attribute the current absence to any of these without current evidence.

## Durable report

Write:
`reviews/worker_reports/mirrors-edge-catalyst-post-refresh-absence-diagnostic-01.md`

Required sections:

1. Task
2. Current user symptom
3. Current-main baseline
4. Post-PR-#140 production run chronology
5. AppID 1233570 stage-by-stage trace
6. First failing/absent stage
7. Root cause
8. Why downstream stages behave as observed
9. Whether PR #140 is defective or simply not live-accepted
10. Evidence refs
11. Smallest correct next action
12. Status

Allowed final statuses:
- `diagnosis_complete_root_cause_identified`
- `diagnosis_complete_no_current_defect_found`
- `blocked_missing_evidence`
- `needs_user_decision`

## Completion rule

Do not stop at “game is absent”.

The task is complete only when the report identifies the first causal stage and explains why, or proves exactly what evidence is unavailable.

Do not implement the fix in this task.
