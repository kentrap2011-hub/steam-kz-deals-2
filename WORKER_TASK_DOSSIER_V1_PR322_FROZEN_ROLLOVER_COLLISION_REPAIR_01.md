# ЧАТ 1 — исправить L3 конфликт при ручном Dossier V1, продолжая PR #322

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: dossier-v1-pr322-frozen-rollover-collision-repair-01
Worker: НОВЫЙ физический ЧАТ 1, НЕ прежняя завершённая QA-беседа и НЕ старый ЧАТ 7.
Mode: narrowly bounded IMPLEMENT on EXISTING PR #322 only.
Worker report: update existing reviews/worker_reports/dossier-v1-explicit-manual-one-shot-authorization-01.md **in PR #322** (no new report-only PR).

Fully read CHAT_PROTOCOL.md and pass START, then current task file, relevant CHAT_CONTEXT.md / PROJECT_ROUTES.md and canonical Dossier V1 ownership/marker/transport contracts. Work ONLY in named repo and PR branch implement/dossier-v1-manual-one-shot-authorization-01. If PR has advanced since expected review HEAD f2f69b38144ac28e31463e0a22035565e5c88bb4, inspect the actual new diff before changing it. PR comment approved this exact bounded fix: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/322#issuecomment-6464264261

Read accepted independent L3 QA report in main: reviews/worker_reports/dossier-v1-pr322-manual-auth-l3-independent-qa-01.md (PR #330); that report, rather than developer assertions, defines blocking L3-01.

**Required change:** Correct the existing GitHub-owned frozen/rollover transport drain in scripts/taste_steam_review_dossier_buffered.py: if one immutable old-snapshot group has both a valid candidate and a valid semantic exhaustion terminal via separate markers, quarantine BOTH before any neutral-cache acceptance or contradictory terminal archive. Respect exact frozen marker parents and group identity, GitHub-owned work queue, strict validation, create-only immutable file paths, and later independent groups. No extra confirmation receipt, scheduling, recovery/retry authority, attempts, production data, evidence-policy change or live semantic work. Do not weaken existing positive rollover cache reuse or current-snapshot guard.

Add focused disposable-Git regression for two distinct markers, same old group, post-rollover dual outcome: no cache write, no terminal semantic archive, no consumed semantic attempt; verify ordinary one-sided rollover accepted and other groups unaffected. Existing PR tests and required exact-head Actions should pass. Keep all modifications in original PR #322; no new implementation PR and no self-merge. Update its worker report with evidence and new HEAD. Handoff status READY_FOR_NARROW_INDEPENDENT_DELTA_QA or BLOCKED, with precise blocker. Independent delta L3 review remains mandatory before Director merges.
