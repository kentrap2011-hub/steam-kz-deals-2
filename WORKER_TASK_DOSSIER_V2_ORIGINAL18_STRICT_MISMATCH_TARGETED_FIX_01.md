# ЧАТ 12 — точечно исправить подтверждённые несоответствия Dossier V2 original18

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: dossier-v2-original18-strict-mismatch-targeted-fix-01
Worker: НОВЫЙ физический ЧАТ 12
Mode: bounded diagnosis + minimal IMPLEMENT only for proven reusable defects; one PR, no semantic rerun or production.
Worker report: reviews/worker_reports/dossier-v2-original18-strict-mismatch-targeted-fix-01.md

## Start and evidence

Read current CHAT_PROTOCOL.md, pass START, and read CHAT_CONTEXT.md, relevant PROJECT_ROUTES.md and this task. Source of truth is main; read accepted independent audit reviews/worker_reports/dossier-v2-real-original18-quality-audit-01.md (merged PR #324), not just worker's stage receipt. Real isolated pilot is branch sandbox/dossier-notes-v2-original18-first, marker 19a22d17ca31b219ec317042f60de6a4655a1cab, authorization c11177e1896fbf9379c4cf12266f188ee5dd754d, writer run https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40568733539 and writer commit bf691923ab9be95a7fc81bcc1a357bdfb4276c56.

## Narrow diagnosis and correction

1. For AppID 206420 (*Saints Row IV: Re-Elected*) reconstruct read-only immutable original Research/Assembly Git pair (research d10b8efc84847a35bbe53e474ec8757678e84c0e; assembly 911d869268118f0b145c3c7d5baf59811a82b933) and exact current `inspect_assembly` / `individual_final_readiness` result with diagnostic if technically possible. Explain why pre-writer receipt claimed `strict_item_valid_pending_existing_atomic_group_ingest` but writer later reported `invalid`; audit identified historical observations without required historical evidence role/current-state check. Distinguish *invalid source data* from *actual validator inconsistency*. Do not assert latter without proof.
2. For AppID 1607130 (*Lust Theory – Season 1*) investigate Assembly `access_blocked` enum outside schema, the immutable candidate's original validation path and whether parser/workflow or only a rejected insufficient-evidence result is affected. Fix a true cross-contract or validation inconsistency at its source only if independently reproduced, preserving strict fail-closed enforcement.
3. For *SULFUR* (2124120), evaluate recent 1.0 release transition and existing Dossier time-boundedness rules. Recommend safe handling for stale assertions and source evidence; no invented fresh player reviews, rewriting accepted pilot data or unauthorized re-Assembly.
4. Determine whether common code-level defects can be corrected **without** changing source semantic/evidence policy. If confirmed: minimal bounded changes in V2-only guardrails/tests to ensure all draft stages and writer agree and invalid input fails predictably. If the issue is purely immutable input/insufficient evidence, **do not fake a fix**: produce a precise correction/research authorization proposal instead of code. Don't weaken strict V1/Deep validation to make the game pass.
5. Existing 14 persisted sandbox dossiers, all Research/Assembly trial commits, receipts, production V1 and Deep must remain untouched. No second one-shot, retry, pipeline dispatch, new scheduler, live writer, ranking/recovery or global V2 activation. Any future semantic replacement is separately owner authorized, create-only and not this task.

Deliver one developer PR with code and focused tests only if a proven bug warrants it; otherwise **one report-only draft PR**. Report confirmed cause, exact reproduction or limits, minimal necessary next step, accepted 14 unchanged and original18 non-production status. No self-merge or automatic production promotion. Flag independent L3 QA if any actual production/authorization/publisher code would be changed. Status FIX_READY_FOR_DIRECTOR_REVIEW / DIAGNOSIS_COMPLETE_NO_SAFE_CODE_FIX / BLOCKED_EVIDENCE.
