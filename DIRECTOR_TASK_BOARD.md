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

## Активная пара

### ЧАТ 1 — Wishlist + хорошая скидка против слабого Taste

Task:
`WORKER_TASK_WISHLIST_GOOD_DEAL_OVERRIDE_RECON_01.md`

Task ID:
`wishlist-good-deal-override-recon-01`

Mode: `READ-ONLY / RECON`
Expected report:
`reviews/worker_reports/wishlist-good-deal-override-recon-01.md`

Status: `user_approved_running_recon`.

### ЧАТ 2 — Epic RU giveaway availability

Task:
`WORKER_TASK_EPIC_RU_GIVEAWAY_AVAILABILITY_RECON_01.md`

Task ID:
`epic-ru-giveaway-availability-recon-01`

Mode: `READ-ONLY / RECON`
Expected report:
`reviews/worker_reports/epic-ru-giveaway-availability-recon-01.md`

Status: `user_approved_running_recon`.

These two tasks are safely parallel: Chat 1 is paid-feed ranking/Taste policy recon; Chat 2 is Epic giveaway source/region recon.

## VERY HIGH PRIORITY NEXT — implement Taste Reviewer recommendations

User explicitly asked that implementation of the prior Taste Reviewer recommendations be treated as **very high priority**.

Authoritative reviewer handoff:
`reviews/taste_reviews/DIRECTOR_IMPLEMENTATION_HANDOFF_01.md`
Status there: `READY_FOR_IMPLEMENTATION`.

The handoff explicitly says the next step is implementation/regression testing rather than more broad taste questioning.

Because repository logic evolved after that handoff, a precise implementation-gap recon is prepared first:
`WORKER_TASK_TASTE_REVIEW_RECOMMENDATIONS_GAP_RECON_01.md`

Task ID:
`taste-review-recommendations-gap-recon-01`
Mode: `READ-ONLY / RECON`
Expected report:
`reviews/worker_reports/taste-review-recommendations-gap-recon-01.md`
Priority: `VERY_HIGH_USER_PRIORITY_NEXT_TASTE_SLOT`.

Goal:
- map each reviewer recommendation to already satisfied / partial / missing in current code;
- avoid reimplementing later accepted work;
- produce the smallest implementation sequence for genuinely missing recommendations;
- retain the review controls around unknown-vs-negative, old shallow abandonment, role/queue priority, discount-vs-fit, giveaways, bundle value and franchise priors.

Scheduling constraint:
- current Chat 1 wishlist task is only RECON and may finish normally;
- do **not** run a Taste-recommendations IMPLEMENT and wishlist/Taste IMPLEMENT in parallel because both can touch ranking/Taste semantics;
- after current reports, reconcile wishlist findings with this very-high-priority reviewer handoff before choosing implementation order;
- ordinary UI/technical-debt tasks should not jump ahead of this user-promoted Taste work absent a blocker.

## NEW queued future request — DLC + personalized bundle economics

Prepared task:
`WORKER_TASK_DLC_PERSONALIZED_BUNDLE_ECONOMICS_RECON_01.md`

Task ID:
`dlc-personalized-bundle-economics-recon-01`
Mode: `READ-ONLY / RECON`
Expected report:
`reviews/worker_reports/dlc-personalized-bundle-economics-recon-01.md`
Status: `queued_user_requested_not_started`.

User requirements:
1. If the base game is confirmed owned, relevant DLC/expansions can be considered as paid deal candidates under explicit ownership/value rules.
2. For a target game, inspect not only standalone discount but also package/bundle acquisition routes.
3. If the storefront offers a personalized bundle where already-owned items reduce the **actual payable price**, that real payable price must be considered when deciding whether the target can be acquired materially cheaper.
4. Do not fake ownership savings for ordinary fixed packages where duplicates do not reduce payable price.
5. A target may become commercially interesting through a bundle even when standalone has no/weak discount.

Known current gap:
`reviews/worker_reports/compact-purchase-options-01.md` confirms fixed-package purchase routes already exist, but dynamic/personalized Complete-the-Set is explicitly excluded today. Package economics remain producer-owned.

This new task must first prove authoritative personalized-price/ownership semantics and may split implementation into DLC eligibility and personalized-bundle economics if their source/ownership boundaries differ.

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

Let the current two READ-ONLY recons finish. Then read their exact reports.
The next safe Taste/ranking slot should prioritize `taste-review-recommendations-gap-recon-01` before ordinary UI/technical debt, while avoiding a conflicting parallel wishlist/Taste IMPLEMENT.
The DLC/personalized-bundle recon is durably queued and can be selected as an independent future slot.
