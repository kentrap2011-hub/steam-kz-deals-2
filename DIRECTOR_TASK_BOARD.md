# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины. Эта board хранит только директорские метаданные: worker-slot, задача, report path, статус, приоритет и пользовательские проверки.

## Правила работы

1. Одновременно по умолчанию работают не больше двух implementation worker-чатов.
2. Нормальная пара: одна главная задача + одна независимая небольшая задача.
3. Перед запуском проверять пересечение областей и canonical ownership.
4. Неясная проблема сначала идёт в bounded `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
5. Bounded sample разрешён только для диагностики/validation. Interactive worker не должен вручную обрабатывать production-каталог item-by-item.
6. Полный production scope, queue, ordering, retries, persistence, completeness и downstream rebuild принадлежат GitHub/GitHub Actions по `config/execution_ownership_contract.json`.
7. Если GitHub не может получить внешний/semantic факт сам, scheduled ChatGPT получает only GitHub-prepared exact scope и возвращает результат через canonical interface; interactive worker не создаёт собственную production-очередь.
8. UI-задачи с real-device judgment закрывать только после пользовательской проверки.
9. Worker-чат удалять только после сохранённого report, решения директора и всех ближайших проверок.
10. Для активных задач хранить ожидаемый report path.
11. Task-file не считается запущенной, пока пользователь реально не отправил команду worker-чату.
12. Живые implementation worker-чаты имеют пользовательские слоты `ЧАТ 1`, `ЧАТ 2`.
13. Before semantic translation, first check approved ready-Russian sources. Translation is fallback, not default.
14. Current project commercial status: personal/non-commercial; commercial use requires `COMMERCIALIZATION_GUARD.md` review.
15. Task-memory invariant: future user work must have a durable destination; backlog removal requires destination/completion/cancellation evidence.
16. Worker efficiency is important, but prepared work is not automatically next.
17. **Priority discipline:** `prepared` does not mean `next`. When a worker finishes, first read its report, then choose direct continuation vs explicit user priority vs dependencies vs backlog.
18. **Review checkpoint invariant:** before assigning a new ordinary backlog task whenever a worker slot becomes free, read `DIRECTOR_REVIEW_CHECKPOINTS.md`. If a mandatory review is due, it takes priority unless the user explicitly gives a more urgent time-sensitive task.
19. `TASTE REVIEWER` is a separate advisory chat. It does not implement production changes and therefore does not consume one of the two implementation worker slots while used only in the boundaries of `TASTE_REVIEWER_ROLE.md`.
20. `SYSTEM AUDITOR` is an independent periodic review role governed by `SYSTEM_AUDITOR_ROLE.md`; it must not be forgotten or replaced by ordinary acceptance tests.

## Активно сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Срочно: контент страницы пропадает | Localize mobile lifecycle/data-render bug where shell+controls work but feed cards are absent after load/refresh and appear after app resume | `WORKER_TASK_MOBILE_PAGE_INTERACTION_FREEZE_RECON_01.md` | `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md` | `ready_to_start_new_chat` |
| `ЧАТ 2` | Свежесть публикации | Final acceptance passed; branch ready for merge/release but production release intentionally deferred until urgent missing-content incident is localized | `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_ACCEPTANCE_02.md` | `reviews/worker_reports/visual-freshness-chain-acceptance-02.md` | `complete_release_deferred_chat_can_delete` |

## Urgent user-visible incident — mobile feed content missing

- User clarified with real-device screenshot on 2026-09-03: controls/tabs are clickable; the defect is not interaction freeze.
- After normal load/refresh, page shell/navigation/swipe hint render but game content/cards are absent.
- Switching to another app and returning causes content to appear temporarily; another refresh returns to empty-content state.
- Corrected task keeps the same durable task/report path but now focuses on data fetch/render lifecycle, visibility/pageshow resume re-render, service-worker/cache mismatch, runtime initialization error, and whether canonical current payload is actually non-empty.
- Classification: urgent user-visible UI/data-render incident; pre-empts System Audit and ITAD until localized/stabilized.
- No implementation until recon localizes the earliest failing step.
- Real-device user verification mandatory after fix.

## Semantic runtime completion — accepted

- Follow-up acceptance report: `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`, blob `5b4a25c89845ab258651a30608658e90d7d1840d`.
- Runtime observability: pass.
- Feed semantic completeness visibility: pass.
- No duplicate scheduler/runtime/queue.
- Director decision: closed; old Chat 1 can be deleted/replaced by the new urgent incident chat.

## Visual freshness — accepted, release deferred

- Implementation report: `reviews/worker_reports/visual-freshness-chain-fix-01.md`, blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`.
- Final acceptance report: `reviews/worker_reports/visual-freshness-chain-acceptance-02.md`, blob `6a691fb29d88b1785accf717752149e027265a2c`.
- Status: `complete`.
- All acceptance controls pass:
  - `Fresh-cycle build proof`: pass;
  - `Deploy-to-built-cycle binding`: pass;
  - `Stale-success visibility`: pass;
  - `Ownership/regression preserved`: pass.
- Accepted branch: `worker/visual-freshness-chain-fix-01`, acceptance head `4080030e686d6b04fcc666069819aa46df18da7a`.
- Acceptance concludes the branch is ready for production merge/release and no scoped blocker remains.
- No production merge/regeneration/Pages deployment was performed by acceptance.
- Director decision: do **not** merge/release while the urgent mobile missing-content incident is being localized, because an unrelated deploy/payload-cycle change would complicate incident attribution. Preserve the accepted branch/report and release after the incident is localized/stabilized and overlap risk is reassessed.
- No immediate continuation belongs in the same worker chat; Chat 2 can be deleted.

## System Auditor checkpoint

- Last report: `reviews/system_audits/baseline-01.md`.
- `system_audit_due: true` after accepted semantic-runtime control/stabilized incident.
- New missing-content incident is explicit urgent user priority and may pre-empt audit.
- After incident stabilizes, run due System Audit before ITAD/ordinary implementation work. Accepted visual freshness release remains a direct production continuation, not ordinary backlog work, but should be reconsidered against the incident findings before deployment.

## Taste Reviewer — baseline complete

- Dedicated reviewer established.
- Report: `reviews/taste_reviews/baseline-01.md`, blob `f243047d9bbb3d8515e7929e2962da66688243c4`.
- Advisory only; no automatic Taste/ranking changes.

## Giveaway identity — ITAD permission confirmed, provider switch prepared

- ITAD permission confirmed.
- Prepared task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Architecture: one provider-neutral identity interface, active `itad`, reserved future `igdb`, no automatic fallback.
- Status: `prepared_not_started` and explicitly lower priority than urgent missing-content incident and due audit.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Twitch/IGDB: waiting for Twitch Support; potential later provider adapter/switch target.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

1. Start/continue NEW Chat 1 with corrected `WORKER_TASK_MOBILE_PAGE_INTERACTION_FREEZE_RECON_01.md` immediately.
2. Do not release the accepted visual-freshness branch until the urgent missing-content incident is localized/stabilized and overlap risk is reassessed.
3. When urgent recon finishes, read its exact report first and assign bounded fix if localized.
4. Real-device user verification mandatory after fix.
5. After incident stabilization, run due System Audit before ITAD/ordinary backlog implementation; then schedule the accepted visual-freshness release at the safest bounded point.