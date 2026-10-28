# ЧАТ 3 — доработать защиту коммерческих терминов Fast/Deep в существующем PR #323

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: progressive-deep-pr323-commercial-guard-targeted-repair-01
Worker: НОВЫЙ физический ЧАТ 3, НЕ прежняя завершённая QA-беседа и НЕ старый ЧАТ 8.
Mode: bounded IMPLEMENT on EXISTING PR #323 only.
Worker report: update existing reviews/worker_reports/progressive-deep-commercial-token-false-positives-fix-01.md **in PR #323**.

Read current CHAT_PROTOCOL.md, pass START, then this task and only relevant CHAT_CONTEXT.md / PROJECT_ROUTES.md, exact Fast/Deep validation contracts. Target original branch fix/progressive-deep-commercial-token-false-positives-01, PR #323; initially QA reviewed 7c60297d2936ee28c234dc5029efa2fe9e21f101, verify latest before edits. Director scoped direction: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/323#issuecomment-6464266084. Accepted independent QA in main: reviews/worker_reports/progressive-deep-pr323-commercial-guard-independent-qa-01.md (PR #329).

**Required:**
1. Preserve valid-word boundary fixes ('грубую', 'сцена', 'рубеж', 'scrub', 'Salem', etc.) while rejecting actual currency-before-amount with no whitespace (USD100, RUB100, EUR100, KZT100) as well as existing amount-before-code.
2. Detect bounded Latin/Cyrillic confusable substitutions *within candidate commercial terms* e.g. 'цeна', 'cкидка', 'prіce', 'diѕcount'; no global transliteration or aggressive safe-prose matches. Include anti-overblocking examples in focused Fast/Deep and score_findings tests and actual isolated ingest/receipt path.
3. Document and test a bounded explicit choice about 'рубл.', bare currency glyphs, spaced codes and contextual homonyms; do not expand the semantic policy without ownership.
4. Remove unnecessary manual workflow_dispatch from the new read-only CI; undo only PR #323's unrelated CURRENT_TASK.md change (preserve main and other workers' updates). Do not create a third workflow or unrelated CI.
5. Preserve all actual Steam/Deep canonical history, failed attempt and GitHub-owned recovery of AppID 1261040, marker/queue/production, scheduled tasks and Dossier. Do not trigger one-shot or retry.

Amend **the same PR #323**, record actual HEAD/mandatory relevant CI and update existing worker report. No new PR, no self-merge, no production. Status READY_FOR_NARROW_INDEPENDENT_DELTA_QA or BLOCKED; Director accepts only after material-delta QA.
