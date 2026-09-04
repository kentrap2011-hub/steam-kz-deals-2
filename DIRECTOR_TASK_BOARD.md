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
9. В каждой копируемой worker-команде первая строка должна явно начинаться с `=== ЧАТ N ===`, чтобы пользователь не путал назначения.

## Активно сейчас

| Чат | Задача | Task file | Report | Статус |
|---|---|---|---|---|
| `ЧАТ 1` | Проверить здоровье существующей semantic scheduled-задачи для текущих 701 unresolved rows | `WORKER_TASK_SEMANTIC_RUNTIME_TASK_HEALTH_RECON_01.md` | `reviews/worker_reports/semantic-runtime-task-health-recon-01.md` | `prepared_send_to_existing_chat` |
| `ЧАТ 2` | Найти live-site divergence после технически успешного giveaway deploy | `WORKER_TASK_GIVEAWAY_LIVE_SITE_MISMATCH_RECON_01.md` | `reviews/worker_reports/giveaway-live-site-mismatch-recon-01.md` | `prepared_send_to_existing_chat` |

## Giveaway visibility incident — still open after user verification

Previous bounded implementation report:
`reviews/worker_reports/giveaway-publication-gap-fix-01.md`
Status: technically `complete`.

That implementation proved:
- canonical giveaway -> visual refresh routing was repaired;
- refreshed visual payload contains `Alone With You`;
- exact deployed Pages artifact from run `33832350887` contains `Alone With You`.

New decisive user evidence:
- user checked the real mobile site after that deploy;
- giveaways still do not appear.

Therefore the user-visible incident is **not closed**. The new investigation must start downstream of the proven deployed artifact and trace:
`deployed Pages artifact -> live HTTP-served files -> browser-loaded data -> giveaway render/view`.

Prepared:
- `WORKER_TASK_GIVEAWAY_LIVE_SITE_MISMATCH_RECON_01.md`
- Task ID `giveaway-live-site-mismatch-recon-01`
- mode `READ-ONLY / RECON`
- report `reviews/worker_reports/giveaway-live-site-mismatch-recon-01.md`
- use existing Chat 2.

Do not reopen Epic parser or canonical giveaway rules without new evidence.

## Visual freshness / semantic production blocker

Recon report:
`reviews/worker_reports/visual-build-input-incomplete-recon-01.md`
Status: `needs_user_evidence`.

Proven primary blocker:
- canonical ChatGPT/semantic payload is truthfully `degraded`;
- `701` unresolved semantic rows remain;
- `sufficiently_complete_for_publication=false`;
- normal fresh visual build must remain fail-closed.

Secondary separate defect:
- visual readiness checks top-level `status != complete` before its later queued/degraded handling, making that degraded branch unreachable; this is not a safe shortcut around semantic incompleteness.

Only missing fact from prior recon: exact health/state of the **existing scheduled ChatGPT semantic production task** for the current 701-row scope.

Prepared:
- `WORKER_TASK_SEMANTIC_RUNTIME_TASK_HEALTH_RECON_01.md`
- Task ID `semantic-runtime-task-health-recon-01`
- mode `READ-ONLY / RECON`
- report `reviews/worker_reports/semantic-runtime-task-health-recon-01.md`
- use existing Chat 1.

## Queued user UI request — top summary filters

Prepared task:
`WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`

Task ID: `top-summary-filter-buttons-01`.
Status: `queued_user_requested_ui_not_started`.

User request:
- make top cards `Новые`, `Не смотрел`, `Интересно`, `Видел` clickable using existing filter state;
- after top `Интересно` fully replaces the existing function, remove the lower duplicate `Интересно` button/tab;
- keep current meanings and counters;
- require real-device mobile verification after deploy.

## Review checkpoint

- `system_audit_due: true` from stabilized Epic source incident.
- Prepared: `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md`.
- Current still-open giveaway live-site defect remains more urgent.
- Ordinary backlog/ITAD stays blocked until required audit completes, unless user explicitly reprioritizes another concrete production defect.

## Other prepared / parked work

- Mobile deploy regression gate: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- ITAD provider-neutral identity implementation: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Twitch/IGDB: waiting for Twitch Support.
- Legacy Taste writer ambiguity: later bounded cleanup.

## Следующий порядок

1. Chat 2 runs `giveaway-live-site-mismatch-recon-01` immediately because user verification failed.
2. Chat 1 runs `semantic-runtime-task-health-recon-01` in parallel.
3. Read exact reports when each worker finishes; do not infer completion from chat prose.
4. If Chat 2 proves one exact defect, issue one bounded IMPLEMENT in the same chat when continuity remains useful.
5. Giveaway incident closes only after technical fix + new real-site user verification succeeds.
6. Once giveaway visibility stabilizes, run mandatory Epic post-incident audit in next free slot.
7. Then queued UI/mobile tasks may proceed according to review checkpoints and user priority.
