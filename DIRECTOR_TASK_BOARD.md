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
8. Возраст задачи не понижает её приоритет автоматически.
9. Taste Reviewer recommendations explicitly promoted by the user on 2026-09-04 are VERY HIGH PRIORITY and must not be displaced by ordinary UI/technical-debt work.

## Review checkpoint

Latest System Audit:
`reviews/system_audits/giveaway-cache-post-incident-audit-01.md`

Status: `complete`
Result: `Giveaway cache incident systemic closure: accepted`

`system_audit_due: false`.

## Just completed

### ЧАТ 1 — Wishlist + good deal vs weak Taste recon

Report:
`reviews/worker_reports/wishlist-good-deal-override-recon-01.md`
Status: `complete`.

Key result:
- exact pre-AI and visual eligibility gates identified;
- safe override can reuse existing wishlist membership + ordinary weak-Taste reason + existing `decision_if_moderate == INCLUDE` + existing `БРАТЬ СЕЙЧАС`;
- direct conflicts, commercial exclusions, risks and negative-analysis readiness remain non-overridable;
- ranking itself does not need redesign;
- independent Taste Review is mandatory after implementation.

Do not start this IMPLEMENT before reconciling it with the very-high-priority Taste Reviewer implementation handoff below.

### ЧАТ 2 — Epic RU giveaway availability recon

Report:
`reviews/worker_reports/epic-ru-giveaway-availability-recon-01.md`
Status: `blocked`.

Key result:
- simply changing Epic discovery `KZ -> RU` is not proven sufficient;
- Epic-owned docs establish account-country acquisition semantics and `Get` vs regional `Unavailable` as the relevant truth;
- no automation-ready Epic-owned machine-readable RU acquisition field/endpoint was proven;
- implementation must remain blocked rather than guessing.

Prepared bounded follow-up:
`WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`
Expected report:
`reviews/worker_reports/epic-ru-availability-source-probe-01.md`
Status: `queued_blocker_resolution_not_active`.

## Active next pair

### ЧАТ 1 — VERY HIGH PRIORITY Taste Reviewer recommendations gap recon

Task:
`WORKER_TASK_TASTE_REVIEW_RECOMMENDATIONS_GAP_RECON_01.md`

Task ID:
`taste-review-recommendations-gap-recon-01`
Mode: `READ-ONLY / RECON`
Expected report:
`reviews/worker_reports/taste-review-recommendations-gap-recon-01.md`
Priority: `VERY_HIGH_USER_PRIORITY_ACTIVE`.

Goal:
- map every recommendation in `reviews/taste_reviews/DIRECTOR_IMPLEMENTATION_HANDOFF_01.md` to already satisfied / partial / still missing in current code;
- reconcile later accepted work so nothing is duplicated or regressed;
- explicitly incorporate/conflict-check the just-completed wishlist-good-deal recon;
- produce the smallest ordered IMPLEMENT sequence for genuinely missing Taste/recommendation behavior;
- do not change code in this recon.

Status: `ready_continue_existing_chat_1`.

### ЧАТ 2 — DLC + personalized bundle economics recon

Task:
`WORKER_TASK_DLC_PERSONALIZED_BUNDLE_ECONOMICS_RECON_01.md`

Task ID:
`dlc-personalized-bundle-economics-recon-01`
Mode: `READ-ONLY / RECON`
Expected report:
`reviews/worker_reports/dlc-personalized-bundle-economics-recon-01.md`
Status: `ready_continue_existing_chat_2`.

Goal:
- if base game is confirmed owned, determine safe DLC/expansion eligibility rules;
- compare standalone target acquisition with package/bundle routes;
- support ownership-reduced personalized Complete-the-Set economics only from authoritative actual payable price;
- preserve current fixed-package behavior and never invent ownership subtraction;
- determine whether DLC and personalized bundle work should split into separate bounded IMPLEMENTs.

These two tasks are safely parallel because both are READ-ONLY: Chat 1 maps Taste/ranking semantics; Chat 2 maps ownership/commercial package economics. No implementation overlap is allowed yet.

## After active pair

1. Read exact Taste gap report and DLC/package report.
2. For Taste implementation order, reconcile:
   - `reviews/taste_reviews/DIRECTOR_IMPLEMENTATION_HANDOFF_01.md`;
   - `reviews/worker_reports/taste-review-recommendations-gap-recon-01.md`;
   - `reviews/worker_reports/wishlist-good-deal-override-recon-01.md`.
3. Do not run two conflicting Taste/ranking IMPLEMENT tasks in parallel.
4. Taste-semantic implementation acceptance requires an independent current Taste Review.
5. Epic RU follow-up remains `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`; it may use a later independent slot because current implementation is safely blocked rather than urgent production breakage.

## Other ready / queued work

### Top summary buttons

Recon complete:
`reviews/worker_reports/top-summary-filter-buttons-recon-01.md`.
IMPLEMENT ready:
`WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.

### Mobile bootstrap deploy regression gate

Task:
`WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
Existing mobile bootstrap regression is passing but not mandatory in canonical Pages deploy gate.

### ITAD provider-neutral giveaway identity

Task:
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
Larger integration; exact Epic/GOG provider ID -> Steam identity through provider-neutral interface.

## Older unfinished / blocked work

- Grounded negative V4 architecture implemented, but semantic completion waits on existing scheduled Taste runtime; do not create second scheduler/manual processing.
- Card positive-explanation fix implemented; production acceptance waits on Russian-description/semantic runtime prerequisite.
- Russian-description translation contracts/ingest exist; runtime production completion waits on existing scheduled semantic runtime.
- Russian language availability as ranking factor remains planned.
- YouTube Russian-language game review selection remains deferred/planned.
- Modern Windows compatibility evidence source remains deferred.
- SteamDB tail: only `App_901735` unresolved/retryable; low priority/external.
- Detailed score UI implementation/fixes are deployed; no new implementation without fresh user evidence.
- Twitch/IGDB route remains externally blocked/waiting.

## Next decision

Continue existing Chat 1 with the very-high-priority Taste gap recon and existing Chat 2 with DLC/personalized-bundle economics recon. Read both exact reports before selecting any implementation.
