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

## Активно сейчас

### ЧАТ 1 — mandatory giveaway cache post-incident audit

Task:
`WORKER_TASK_GIVEAWAY_CACHE_POST_INCIDENT_AUDIT_01.md`

Mode: `READ-ONLY / AUDIT`
Expected report:
`reviews/system_audits/giveaway-cache-post-incident-audit-01.md`

Status: `user_approved_start_now`.

Reason: user-visible giveaway live-site incident was technically fixed and then verified working on the real mobile site. Recurring System Audit trigger is due.

### ЧАТ 2 — intentionally unassigned pending user choice

User explicitly paused the previously suggested mobile deploy regression-gate task and requested a complete plain-language comparison of all current and older unfinished work before selecting the second parallel task.

Do not auto-start Chat 2 until user chooses after that comparison.

## Current user-visible / ready work

- Top summary buttons: recon complete; IMPLEMENT ready in `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.
- Epic RU giveaway availability: future recon ready in `WORKER_TASK_EPIC_RU_GIVEAWAY_AVAILABILITY_RECON_01.md`; Epic only, Steam/GOG unchanged.
- Mobile feed regression gate: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`; existing passing mobile bootstrap test is not yet a mandatory Pages deploy gate.
- ITAD provider-neutral giveaway identity: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`; larger integration.

## Older unfinished work — current factual status

### Grounded negative / card-analysis completeness

The original diagnosis is complete and the V4 grounded-negative architecture is already implemented.
Report: `reviews/worker_reports/grounded-negative-implement-01.md`.
Current implementation status: `blocked` on the existing scheduled Taste semantic runtime.
At that report's acceptance point, 599 semantic rows remained (576 targeted negative backfills + 23 full evaluations). No second scheduler/manual processing is allowed.

### Card positive explanations / production acceptance

Explanation policy fix is implemented and a real generated top-30 candidate passed the explanation validator after the focused fix. Final production acceptance remains blocked by the independent Russian-description mandatory gate / semantic runtime.
Report: `reviews/worker_reports/card-explanation-production-acceptance-01.md`.

### Russian descriptions

Repo-side translation contracts/implementation exist. Runtime acceptance remains blocked waiting for the already-existing scheduled semantic runtime to produce canonical translation submissions. Do not create another scheduler or manually translate the queue.

### Russian language availability as ranking factor

Still a planned product feature: detect Russian interface availability as yes/no/unknown with evidence; confirmed lack of Russian should strongly reduce practical/final priority and be visible as a downside; unknown must not equal no.

### Wishlist good discount overrides weak Taste

Still an explicit high-importance backlog product rule: a Steam-wishlist game with a genuinely good deal should be allowed into the final feed even with weak automatic Taste fit, while retaining price/risk warnings. Needs design/implementation.

### YouTube game review on card

Still deferred/planned: automatically select a useful Russian-language review (or reliably Russian-audio option), avoid random/spoiler-heavy videos, persist choice in production payload and show a compact link/button.

### Windows compatibility evidence

Still deferred: add a reliable evidence source for actual modern-Windows friction and propagate confirmed problems into visible risk/scoring. Do not infer risk merely from legacy system-requirements text.

### SteamDB historical-minimum tail

One remaining retry `App_901735`; low priority and externally dependent. Exact KZ historical minimum remains unproven and must not be fabricated.

### Detailed score breakdown UI

Old CURRENT_TASK label is stale. Durable reports show the redesign and user-requested fixes were technically implemented and deployed. Remaining report-level item is only real-phone spot-check/acceptance if not already recorded separately. Do not treat it as a fresh implementation task without new user evidence.

### Twitch/IGDB route

Still waiting external/provider readiness per newer board. Do not treat it as immediately executable.

## Stale backlog record

The old BACKLOG entry saying the separate cross-platform giveaway block does not exist is obsolete: the feature exists, the recent live-site incident was fixed, and user mobile verification succeeded. It must not be counted as unfinished product work.

## Review checkpoint

`system_audit_due: true` until Chat 1 audit completes.

## Next decision

User will choose Chat 2 only after reviewing a complete plain-language task list. Do not privilege newer tasks solely because they are newer.
