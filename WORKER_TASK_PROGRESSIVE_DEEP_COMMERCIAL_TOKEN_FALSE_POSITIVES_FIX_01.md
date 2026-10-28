# ЧАТ 8 — исправление ложного распознавания коммерческих терминов Deep

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch: main
Task ID: progressive-deep-commercial-token-false-positives-fix-01
Worker: НОВЫЙ физический ЧАТ 8
Mode: bounded IMPLEMENT, one PR.
Worker report: reviews/worker_reports/progressive-deep-commercial-token-false-positives-fix-01.md

Read current CHAT_PROTOCOL.md, pass START, then CHAT_CONTEXT.md and only relevant contracts/routes. Work only in this repository.

**Confirmed case:** Progressive Deep rejected Streamer Life Simulator (AppID 1261040) with receipt at data/cache/progressive_pass2_ingest_receipts/4a461de403abec199df0def7d3b659ca20cdbb3af71f577b44021b1d7af169f8.json. The reported reason was that evidence contained a three-letter Russian currency fragment inside a longer, unrelated ordinary word. The user's quoted example is “грубую” (valid non-price language). The consumed attempt is GitHub-owned recovery, not worker replay.

**Task:**
1. Trace the exact current validator and all related lexical commercial-evidence checks used in the active Deep ingest. Confirm the root cause against the source/receipt.
2. Inspect all adjacent tokens in the SAME validation family for equivalent substring false positives: Cyrillic/Latin word interiors, currency fragments and full names, case/Unicode, punctuation, boundaries, typography, genuine standalone monetary expressions, discount/store terms. Include any shared Fast/Deep consumer only if it uses the exact same check. Document the inspected inventory and confirmed near-neighbor defects.
3. Correct ALL verified analogous lexical false positives in this bounded family, not a single hardcoded word. Preserve meaningful detection of actual price, currency and purchasing context in taste evidence. No blanket bypass/disabled rejection and no irrelevant global refactor.
4. Add focused positive/negative tests for the reported harmless word, other embedded-fragment words, legitimate standalone prices/currencies/discounts, Unicode/punctuation variants and canonical validation path. Test existing contracts without changing scoring or semantic rules.
5. Do not alter the rejected work's consumed attempt, historical receipts, recovery state, queue, production data, retry logic, Dossier, scheduled tasks or run-start bindings. No manual Deep execution/retry.

Output one PR and worker report at the path above, with cause, tested analogues, focused CI and residual risks. Director performs acceptance; no self-merge. Status READY_FOR_DIRECTOR_REVIEW or BLOCKED_CONTRACT.
