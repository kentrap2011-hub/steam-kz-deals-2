# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины. Эта board хранит только директорские метаданные.

## Ключевые правила

1. По умолчанию не больше двух implementation worker-чатов.
2. Неясная проблема сначала `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
3. Production queue/retry/completeness принадлежат GitHub/GitHub Actions по `config/execution_ownership_contract.json`.
4. UI-инциденты закрывать только после real-device проверки.
5. Worker-чат удалять только после сохранённого report, решения директора и ближайших проверок.
6. `prepared` не значит `next`.
7. Перед обычным backlog читать `DIRECTOR_REVIEW_CHECKPOINTS.md`.
8. `TASTE REVIEWER` и `SYSTEM AUDITOR` — отдельные независимые роли.

## Активно сейчас

| Чат | Задача | Task file | Report | Статус |
|---|---|---|---|---|
| `ЧАТ 1` | Нормализовать closeout visual freshness (`STOP` -> разрешённый статус) без нового исследования | `WORKER_TASK_VISUAL_FRESHNESS_RELEASE_01.md` | `reviews/worker_reports/visual-freshness-release-01.md` | `needs_report_status_closeout_existing_chat` |
| `ЧАТ 2` | Epic fix уже восстановил production; дождаться финала regression-run `33790442843` и обновить closeout | `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_FIX_01.md` | `reviews/worker_reports/epic-giveaway-schema-fix-01.md` | `needs_final_ci_closeout_keep_chat` |

## Epic giveaway source incident — production recovered, final test closeout pending

- Recon report: `reviews/worker_reports/epic-giveaway-schema-recon-01.md`, blob `32d487e13a916424693bd05d0d0ced41cf688bc2`.
- Fix report: `reviews/worker_reports/epic-giveaway-schema-fix-01.md`, blob `4e79874e4d4d0b4ed9d101ec7dba8791686dd69b`.
- Parser fix commit: `aa7cea8d06d4d71a5ff6fe4c23a71c2cbda28783`.
- Regression commit: `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`.
- Canonical code-run `33790369125` completed `success`.
- Current canonical giveaway snapshot is `complete`; Epic is `ok/complete`, candidate_count `1`, accepted_count `1`, no error.
- Active accepted Epic giveaway: `Alone With You`, 100% discount, KZ available.
- Operationally the original `SOURCE_SCHEMA_FAILURE` is recovered.
- Final regression run `33790442843` was still `in_progress` at Director check. Do not delete Chat 2 until this finishes and the report is updated to the final allowed status.
- Because this was a user-visible giveaway incident, `system_audit_due=true`; post-incident audit is prepared but must start only after final fix closeout.
- Prepared post-audit: `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md`, report `reviews/system_audits/epic-post-incident-audit-01.md`.

## Visual freshness

- Accepted fix landed on `main` via PR #13 at `ddbf25d855f3ed7b86aca5ecbebb834e87178012`.
- Production run `33788418064` truthfully emitted `fresh_build=false / degraded/no_fresh_build`; receipt artifact uploaded.
- Full successful build->exact-run deploy proof remains pending because upstream failed on `ChatGPT production payload is not complete`.
- Do not redesign freshness fix.
- Prepared exact upstream recon: `WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md`.

## Mobile feed incident

- User/device accepted as working.
- Post-incident audit complete.
- Remaining bounded gap: `tests/feed-bootstrap.test.js` not yet in canonical Pages deploy gate.
- Prepared: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.

## Review checkpoint

- `system_audit_due: true` due to stabilized Epic user-visible incident.
- Do not start ordinary backlog/ITAD before `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md` completes, unless a more urgent concrete production defect is explicitly prioritized.

## Other prepared / parked work

- Visual-build input incompleteness recon: `WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md`.
- Mobile deploy regression gate: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- ITAD provider-neutral identity implementation: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Twitch/IGDB: waiting for Twitch Support.
- Semantic runtime observability: accepted/closed; degraded semantic completeness still not visibly surfaced in UI.
- Legacy Taste writer ambiguity: later bounded cleanup.

## Следующий порядок

1. Existing Chat 1 finishes status-only closeout, then can be deleted.
2. Existing Chat 2 waits only for run `33790442843`, then updates `reviews/worker_reports/epic-giveaway-schema-fix-01.md`; no new implementation.
3. After Chat 2 final closeout, delete it and start NEW Chat 2 with `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md`.
4. After audit, use next free slot for `WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md` unless that blocker has naturally cleared.
5. Then mobile regression gate; only after current blockers/review permit it move to ITAD/ordinary backlog.