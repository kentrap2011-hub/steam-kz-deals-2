# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины. Эта board хранит только директорские метаданные.

## Ключевые правила

1. По умолчанию не больше двух implementation worker-чатов.
2. Неясная проблема сначала `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
3. Interactive worker не владеет production queue/retry/completeness; это GitHub/GitHub Actions по `config/execution_ownership_contract.json`.
4. UI-инциденты закрывать только после real-device проверки.
5. Worker-чат удалять только после сохранённого report и решения директора.
6. `prepared` не значит `next`.
7. Перед обычным backlog читать `DIRECTOR_REVIEW_CHECKPOINTS.md`; mandatory review имеет приоритет, кроме более срочного конкретного production-дефекта.
8. `TASTE REVIEWER` и `SYSTEM AUDITOR` — отдельные роли; не заменять их обычной acceptance-проверкой.

## Активно сейчас

| Чат | Задача | Task file | Report | Статус |
|---|---|---|---|---|
| `ЧАТ 1` | Нормализовать closeout релиза visual freshness (`STOP` -> разрешённый статус) без нового исследования | `WORKER_TASK_VISUAL_FRESHNESS_RELEASE_01.md` | `reviews/worker_reports/visual-freshness-release-01.md` | `needs_report_status_closeout_existing_chat` |
| `ЧАТ 2` | Короткий независимый пост-аудит уже исправленного Epic-инцидента | `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md` | `reviews/system_audits/epic-post-incident-audit-01.md` | `ready_to_start_new_chat` |

## Epic giveaway source incident — PRODUCTION RECOVERED

- Recon: `reviews/worker_reports/epic-giveaway-schema-recon-01.md`, blob `32d487e13a916424693bd05d0d0ced41cf688bc2`.
- Fix report: `reviews/worker_reports/epic-giveaway-schema-fix-01.md`, blob `4e79874e4d4d0b4ed9d101ec7dba8791686dd69b`.
- Parser fix commit: `aa7cea8d06d4d71a5ff6fe4c23a71c2cbda28783`.
- Regression commit: `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`.
- Exact production code-run `33790369125` completed `success`.
- Follow-up test-run `33790442843` was still in progress at Director check; do not claim its final conclusion until complete.
- Current canonical `data/production/giveaways/v1/current.json` now proves:
  - `snapshot_status=complete`;
  - Epic `status=ok`, `complete=true`;
  - Epic candidate_count `1`, accepted_count `1`;
  - no Epic error;
  - active accepted giveaway: `Alone With You`, 100% discount, KZ available.
- Therefore the original user-visible `SOURCE_SCHEMA_FAILURE` is operationally recovered in production.
- Existing Chat 2 implementation worker has no further direct fix work and can be deleted.
- Because this was a user-visible giveaway incident, `system_audit_due=true` now; prepared task: `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md`, creation commit `8b055a223cc07a4ba3eba0ddce28b06d57cfb650`.

## Visual freshness — protection landed, full successful-chain proof pending upstream readiness

- Release report: `reviews/worker_reports/visual-freshness-release-01.md`, blob `68bdf93bb9ee3a9c2782faaa1715571f38ec9c5e`.
- Accepted fix landed unchanged on `main` via PR #13 at `ddbf25d855f3ed7b86aca5ecbebb834e87178012`.
- Production build run `33788418064` failed upstream on `ChatGPT production payload is not complete`.
- Freshness control itself worked: receipt tests passed, artifact uploaded, truthful `fresh_build=false / degraded/no_fresh_build` emitted.
- Resulting workflow-run deploy `33788465486` was correctly skipped.
- Exact triggering-run binding is installed on `main` but has not yet been dynamically exercised in a successful build->deploy chain.
- Existing Chat 1 must only normalize report status to an allowed exact value; no new work.
- Separate recon already prepared for persistent upstream blocker: `WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md`, commit `ac2111029b01a813655be6e12c6b3e4043c9e583`.

## Mobile feed incident — accepted

- Production release `f745dac844213880cd7eb984573877f58803a3f0`; Pages run `33779042331` success.
- User real-device acceptance: works.
- Post-incident audit: `reviews/system_audits/mobile-post-incident-audit-01.md`, blob `db07eb4f7848d18e3a8cc62d5cb754e245695db4`.
- Remaining bounded gap only: existing `tests/feed-bootstrap.test.js` is not in canonical Pages deploy gate.
- Prepared follow-up: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`, commit `ad279b127ee87d8b1f15313f4d62a565c376b040`.

## Review checkpoint

- `system_audit_due: true` because the user-visible Epic giveaway incident has now been stabilized.
- Prepared audit: `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md`.
- Do not start ordinary backlog/ITAD before this short audit unless a more urgent concrete production defect is explicitly prioritized.

## Operational health watch

- Automation `Steam KZ Health Watch` runs hourly and alerts only on new/materially worsened problems not already tracked here.

## Other prepared / parked work

- Visual-build input incompleteness recon: `WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md` — concrete production blocker, prepared.
- Mobile deploy regression gate: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md` — prepared.
- ITAD provider-neutral identity implementation: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` — prepared, lower priority until current review/production blockers clear.
- Twitch/IGDB: waiting for Twitch Support.
- Semantic runtime observability: accepted/closed; UI still does not visibly surface degraded semantic completeness.
- Legacy Taste writer ambiguity remains a later bounded cleanup risk.

## Следующий порядок

1. Existing Chat 1 finishes status-only closeout, then can be deleted.
2. Delete finished Epic implementation Chat 2.
3. Start NEW Chat 2 with `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md`.
4. After that audit, use next free slot for `WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md` unless its blocker has naturally cleared by then.
5. Then wire mobile regression gate; only after current blockers/review permit it move to ITAD/ordinary backlog.