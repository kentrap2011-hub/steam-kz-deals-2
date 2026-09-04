# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины, но эта board новее и выигрывает при расхождении статусов.

## Ключевые правила

1. По умолчанию держать два worker-чата занятыми параллельно, если задачи независимы и не конфликтуют.
2. Неясная проблема сначала `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
3. Worker-чат удалять только после durable report + Director decision + ближайших user checks.
4. В каждой копируемой worker-команде первая строка явно начинается с `=== ЧАТ N ===`.
5. Номер принадлежит worker-слоту.
6. Не запускать параллельно конфликтующие Taste/ranking IMPLEMENT.
7. Taste Reviewer recommendations have VERY HIGH USER PRIORITY.

## Review checkpoint

Latest System Audit: `reviews/system_audits/giveaway-cache-post-incident-audit-01.md`
Result: accepted.
`system_audit_due: false`.

## Latest completed reports

### ЧАТ 1 — Taste recommendations gap recon

Report:
`reviews/worker_reports/taste-review-recommendations-gap-recon-01.md`
Status: `complete`.

Three real ordered implementation gaps remain:
1. evidence state / confidence / reconsideration semantics;
2. play role + relative start priority;
3. reconsideration commercial bridge + wishlist-good-deal override.

Important sequencing: step 1 must precede the wishlist override because current reason codes are too coarse to distinguish insufficient/reconsiderable from confirmed weak/direct conflict safely.

### ЧАТ 2 — DLC + personalized bundle economics recon

Report:
`reviews/worker_reports/dlc-personalized-bundle-economics-recon-01.md`
Status: `needs_user_decision`.

Findings:
- DLC->base dependency is already source-proven; missing piece is authoritative ownership.
- Base-game ownership can likely use Valve `IPlayerService/GetOwnedGames` if an approved Steam Web API key is provisioned and library visibility permits it.
- Current fixed `Sub_` package economics already exist and must remain unchanged.
- Personalized Steam Complete The Set payable price is account-specific and cannot be proven by current unauthenticated GitHub pipeline.
- No local subtraction/reconstruction is allowed.
- Authenticated Steam Store account/session integration is a new security boundary and requires explicit user/Director approval before design/implementation.

Recommended split:
A. DLC ownership eligibility first.
B. package/bundle expansion / Complete The Set second, with personalized CTS price blocked until account-context policy is approved.

## Active / next

### ЧАТ 1 — VERY HIGH PRIORITY IMPLEMENT 1

Task:
`WORKER_TASK_TASTE_EVIDENCE_STATE_AND_CONFIDENCE_IMPLEMENT_01.md`
Task ID: `taste-evidence-state-and-confidence-implement-01`
Mode: `IMPLEMENT`
Expected report:
`reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`
Status: `ready_continue_existing_chat_1`.

Goal:
- explicit insufficient / reconsiderable / confirmed-negative evidence state;
- stronger evidence provenance/strength rules;
- old shallow historical negatives can be weaker/reconsiderable;
- candidate-quality complaints separate from personal dislike;
- preserve price-blind Taste and no-discount-rescue.

Do not implement play-role or wishlist override yet.

### ЧАТ 2 — hold for user decision

Status: `keep_existing_chat_2_needs_user_decision`.

Need user decision on two separate access boundaries:
1. approve or reject using a Steam Web API key for a read-only canonical owned-games snapshot (`GetOwnedGames`) to support DLC eligibility;
2. separately approve or reject future authenticated Steam Store account/session integration needed to obtain actual personalized Complete The Set payable prices.

Do not ask user to paste any secret/API key/session cookie into ordinary chat. Credential provisioning must use an approved secret path if implementation proceeds.

## Other queued

- `WORKER_TASK_TASTE_REVIEW_RECOMMENDATIONS_GAP_RECON_01.md` complete.
- `WORKER_TASK_WISHLIST_GOOD_DEAL_OVERRIDE_RECON_01.md` complete; implementation waits for Taste evidence-state foundation.
- `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md` queued blocker-resolution recon.
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md` ready.
- `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md` ready.
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` queued larger integration.
- Russian-language availability ranking factor planned.
- YouTube review selection planned.
- modern Windows compatibility evidence planned.
- semantic/Russian-description completion remains blocked on existing scheduled semantic runtime evidence; do not create another scheduler.

## Next decision

1. Continue existing Chat 1 with Taste IMPLEMENT 1.
2. Keep existing Chat 2 until user chooses Steam access policy.
3. After Taste step 1 report, decide whether step 2 can safely start.
4. Do not accept/deploy the complete Taste semantic sequence without required independent Taste Review at the chosen acceptance boundary.
