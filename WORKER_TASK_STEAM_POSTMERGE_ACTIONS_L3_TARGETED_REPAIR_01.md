# ЧАТ 4 — исправить три конкретных замечания Steam QA

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: steam-postmerge-actions-l3-targeted-repair-01
Worker: НОВЫЙ физический ЧАТ 4; прежний ЧАТ 4 завершил отдельную работу.
Role: narrow source repair IN EXISTING PR #346 only; no new implementation PR.
QA: report-only PR #349, reviews/worker_reports/steam-postmerge-actions-failures-final-l3-qa-01.md.
Source: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/346 ; source branch fix/steam-postmerge-actions-failures-01; prior SHA 8df383752da1b119742702767d780a00580a18a5. Read actual current PR HEAD.

FIRST read full CHAT_PROTOCOL.md from current main, perform START gate and read this named task plus canonical relevant Steam mailing/metadata/content-eligibility/family contracts. Work only in specified repo. Pass architecture preflight before source/workflow edit.

Implement ONLY independent QA #349 CR-1/CR-2/CR-3:
CR-1 verify reused cached metadata identity and every metadata entity key, type and steam_id against current App_ or Sub_ key before current eligibility classification/family consumption. Regress fail-closed for App_2 metadata steam_id=999. For Sub_456 metadata steam_id must represent package 456; mailing representative appid may differ.
CR-2 additionally compare BOTH persisted metadata and eligibility taste_index_blob_sha to CURRENT GitHub HEAD blob SHA for data/cache/taste_fit.index.json at family read boundary, not just to each other. Negative regression for mutually stale A when current HEAD is B.
CR-3 in config/content_eligibility_contract.json diagnostic stage 12 replace hardcoded eligible+excluded == 101 with eligible+excluded == current-feed INCLUDE count. Historical 101, current 34, out-of-feed 67 are observation, not invariant. Preserve completeness and zero unresolved.

Add scoped fail-closed negative tests in EXISTING Steam PR regression; preserve full active mailing feed, historic 67 out-of-feed records, no invented price or silent omission, exact policy/profile/current source SHA checks. Do not change pricing, stage owners, schedulers, retries, Deep/Dossier, production, collector or deployment; do not manually trigger GitHub production Actions.

Commit directly on EXISTING PR #346, avoid new source PR. Save brief repair report reviews/worker_reports/steam-postmerge-actions-l3-targeted-repair-01.md in same PR with exact final HEAD, passing applicable exact-HEAD CI, known boundaries and verdict FIX_READY_FOR_NARROW_L3_DELTA_QA or BLOCKED_CONCRETE. No self-merge. Director organizes bounded independent recheck of ONLY the three changed safety deltas, then decides merge.