# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины. Эта board хранит только директорские метаданные.

## Ключевые правила

1. По умолчанию держать два worker-чата занятыми параллельно, если задачи независимы и не конфликтуют.
2. Неясная проблема сначала `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`; отдельная задача не обязательно требует нового чата.
3. Production queue/retry/completeness принадлежат GitHub/GitHub Actions по `config/execution_ownership_contract.json`.
4. UI-инциденты закрывать только после real-device/site проверки пользователя.
5. Worker-чат удалять только после сохранённого report, решения директора и ближайших проверок.
6. `prepared` не значит `next`.
7. Перед обычным backlog читать `DIRECTOR_REVIEW_CHECKPOINTS.md`.
8. `TASTE REVIEWER` и `SYSTEM AUDITOR` — отдельные независимые роли.

## Активно сейчас

| Чат | Задача | Task file | Report | Статус |
|---|---|---|---|---|
| `ЧАТ 1` | Разобрать `ChatGPT production payload is not complete` | `WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md` | `reviews/worker_reports/visual-build-input-incomplete-recon-01.md` | `assigned_waiting_report` |
| `ЧАТ 2` | Исправить stale canonical -> visual giveaway publication gap | `WORKER_TASK.md` (`giveaway-publication-gap-fix-01`) | `reviews/worker_reports/giveaway-publication-gap-fix-01.md` | `prepared_send_to_existing_chat` |

## Giveaway visibility incident — current urgent user-visible defect

Recon complete:
`reviews/worker_reports/giveaway-publication-gap-recon-01.md`
Status: `needs_fix`.

Proven first loss boundary:
`data/production/giveaways/v1/current.json` -> stale giveaway sibling in `data/production/visual/current.json`.

Canonical giveaway is healthy and contains active KZ Epic giveaway `Alone With You`, but current visual payload still references the older incomplete giveaway snapshot and has `giveaways.games=[]`.

Concrete routing gap: the existing giveaway-only visual refresh classifier does not include committed changes to `data/production/giveaways/v1/current.json`, so a healthy canonical giveaway update can fail to refresh the visual derivative.

Prepared bounded fix in root `WORKER_TASK.md`:
- Task ID: `giveaway-publication-gap-fix-01`;
- mode: `IMPLEMENT`;
- report: `reviews/worker_reports/giveaway-publication-gap-fix-01.md`.

Use existing Chat 2 as direct continuation. After deploy, require actual user site verification before closing the user-visible incident.

## Epic giveaway source incident — closed

- Final report: `reviews/worker_reports/epic-giveaway-schema-fix-01.md`.
- Status: `complete`.
- Parser fix commit: `aa7cea8d06d4d71a5ff6fe4c23a71c2cbda28783`.
- Regression commit: `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`.
- Do not reopen parser work without new evidence.

## Visual freshness / visual-build blocker

- Accepted freshness fix landed on `main` via PR #13 at `ddbf25d855f3ed7b86aca5ecbebb834e87178012`.
- Release report: `reviews/worker_reports/visual-freshness-release-01.md`, status `blocked` only because upstream visual build failed on `ChatGPT production payload is not complete`.
- Freshness protection itself truthfully emitted `degraded/no_fresh_build` and is not to be redesigned.
- Current Chat 1 task: `WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md`.

## Queued user UI request — top summary filters

Prepared task:
`WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`

Task ID: `top-summary-filter-buttons-01`.
Status: `queued_user_requested_ui_not_started`.

User request from current mobile UI:
- make all four top summary cards clickable using the existing filter state: `Новые`, `Не смотрел`, `Интересно`, `Видел`;
- after the top `Интересно` card fully performs the existing interesting-filter function, remove the separate lower `Интересно` button/tab as a duplicate;
- keep existing meanings and live counters unchanged;
- require mobile real-device verification after deploy.

Do not interrupt the current giveaway production incident or mandatory audit for this queued UX improvement unless the user explicitly reprioritizes it.

## Mobile feed incident

- User/device accepted as working.
- Post-incident audit complete.
- Remaining bounded gap: `tests/feed-bootstrap.test.js` not yet in canonical Pages deploy gate.
- Prepared: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.

## Review checkpoint

- `system_audit_due: true` due to stabilized Epic user-visible source incident.
- Prepared: `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md`.
- Current still-visible giveaway publication defect is more urgent and may finish first.
- Do not start ordinary backlog/ITAD before required audit completes.

## Other prepared / parked work

- Mobile deploy regression gate: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- ITAD provider-neutral identity implementation: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Twitch/IGDB: waiting for Twitch Support.
- Semantic runtime observability: accepted/closed; degraded semantic completeness still not visibly surfaced in UI.
- Legacy Taste writer ambiguity: later bounded cleanup.

## Следующий порядок

1. Existing Chat 2 implements `giveaway-publication-gap-fix-01` from root `WORKER_TASK.md`.
2. Chat 1 continues/finishes `visual-build-input-incomplete-recon-01` in parallel.
3. After Chat 2 technical deploy proof, user verifies the real site; only then close giveaway visibility incident.
4. Once giveaway visibility incident is stabilized, run `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md` in the next free worker slot.
5. Then use remaining free slot for the next bounded step from Chat 1 recon, mobile regression gate, or queued `top-summary-filter-buttons-01`, respecting review checkpoints and user priority.
6. ITAD/ordinary backlog only after mandatory audit permits it.
