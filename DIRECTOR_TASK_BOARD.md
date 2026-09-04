# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины, но эта board новее и выигрывает при расхождении статусов.

## Ключевые правила

1. По умолчанию держать два worker-чата занятыми параллельно, если задачи независимы и не конфликтуют.
2. Неясная проблема сначала `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
3. UI-инциденты закрывать только после real-device/site проверки пользователя.
4. Worker-чат удалять только после сохранённого report, решения директора и ближайших проверок.
5. В каждой копируемой worker-команде первая строка должна явно начинаться с `=== ЧАТ N ===`.
6. Номер принадлежит worker-слоту.
7. Не запускать параллельно конфликтующие IMPLEMENT-задачи.
8. Возраст задачи не понижает её приоритет автоматически; при выборе работы сравнивать текущий пользовательский эффект, системный риск, блокеры и полный цикл.

## Giveaway cache incident — systemically closed

System Audit:
`reviews/system_audits/giveaway-cache-post-incident-audit-01.md`

Status: `complete`
Result: `Giveaway cache incident systemic closure: accepted`

Audit found no incident-specific implementation follow-up required before ordinary backlog continues.
System checkpoint reconciled: `system_audit_due: false`, material change count reset to 0.

## Worker slots

### ЧАТ 1

Status: `free_pending_user_selection_after_audit`.

Previous audit task is complete and durably saved.
Do not auto-assign until Director/user select the next pair from the full current+older unfinished task set.

### ЧАТ 2

Status: `free_pending_user_selection_after_audit`.

Do not auto-assign until Director/user select the next pair from the full current+older unfinished task set.

## Current user-visible / ready work

- Top summary buttons: recon complete; IMPLEMENT ready in `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.
- Epic RU giveaway availability: recon ready in `WORKER_TASK_EPIC_RU_GIVEAWAY_AVAILABILITY_RECON_01.md`; Epic only, Steam/GOG unchanged.
- Mobile feed regression gate: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`; existing passing mobile bootstrap test is not yet a mandatory Pages deploy gate.
- ITAD provider-neutral giveaway identity: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`; larger integration.

## Older unfinished work — current factual status

### Grounded negative / card-analysis completeness

V4 grounded-negative architecture is implemented.
Report: `reviews/worker_reports/grounded-negative-implement-01.md`.
Current implementation remains blocked on the existing scheduled Taste semantic runtime. Do not create a second scheduler/manual processing path.

### Card positive explanations / production acceptance

Explanation policy fix is implemented. Final production acceptance remains blocked by the independent Russian-description mandatory gate / semantic runtime.
Report: `reviews/worker_reports/card-explanation-production-acceptance-01.md`.

### Russian descriptions

Repo-side translation contracts/implementation exist. Runtime acceptance remains blocked waiting for the already-existing scheduled semantic runtime to produce canonical translation submissions. Do not create another scheduler or manually translate the queue.

### Russian language availability as ranking factor

Still planned: detect Russian interface availability as yes/no/unknown with evidence; confirmed lack of Russian should strongly reduce practical/final priority and be visible as a downside; unknown must not equal no.

### Wishlist good discount overrides weak Taste

Still explicit high-importance product rule: a Steam-wishlist game with a genuinely good deal should be allowed into the final feed even with weak automatic Taste fit, while retaining price/risk warnings. Requires design/implementation and Taste Review before acceptance.

### YouTube game review on card

Still deferred/planned: automatically select a useful Russian-language review or reliably Russian-audio option, avoid random/spoiler-heavy videos, persist choice in production payload and show a compact link/button.

### Windows compatibility evidence

Still deferred: add a reliable evidence source for actual modern-Windows friction and propagate confirmed problems into visible risk/scoring.

### SteamDB historical-minimum tail

One remaining retry `App_901735`; low priority and externally dependent. Exact KZ historical minimum remains unproven and must not be fabricated.

### Detailed score breakdown UI

Implementation and user-requested fixes are technically complete/deployed. Do not promote as new implementation without fresh user evidence of a remaining problem.

### Twitch/IGDB route

Still waiting external/provider readiness.

## Stale backlog record

Old backlog text saying the separate cross-platform giveaway block does not exist is obsolete and must not be counted as unfinished work.

## Review checkpoint

`system_audit_due: false`.

## Next decision

Both worker slots are free. Select two safely independent tasks from the full current+older unfinished set; do not privilege newer tasks solely because they are newer.
