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
| `ЧАТ 1` | Visual freshness release closeout | `WORKER_TASK_VISUAL_FRESHNESS_RELEASE_01.md` | `reviews/worker_reports/visual-freshness-release-01.md` | `blocked_saved_chat_can_delete` |
| `ЧАТ 2` | Найти, почему canonical раздача есть, а на сайте не видна | `WORKER_TASK.md` (`giveaway-publication-gap-recon-01`) | `reviews/worker_reports/giveaway-publication-gap-recon-01.md` | `prepared_direct_continuation_not_started_keep_chat` |

## Giveaway visibility incident — current urgent user-visible defect

- User reports that free giveaways are still not visible on the published site.
- Current canonical `data/production/giveaways/v1/current.json` on `main` is `complete` and contains one active KZ Epic giveaway: `Alone With You`, 100%, through `2026-09-10T15:00:00Z`.
- Therefore the Epic source/parser incident is closed, but a later publication/browser/view boundary is still defective or stale.
- Prepared bounded recon in root `WORKER_TASK.md`:
  - Task ID: `giveaway-publication-gap-recon-01`;
  - mode: `READ-ONLY / RECON`;
  - report: `reviews/worker_reports/giveaway-publication-gap-recon-01.md`.
- Use existing Chat 2 because it is a direct continuation of the giveaway incident and its context is still useful.
- Do not start a fix until this recon proves the exact failing layer.

## Epic giveaway source incident — closed

- Final report: `reviews/worker_reports/epic-giveaway-schema-fix-01.md`.
- Status: `complete`.
- Parser fix commit: `aa7cea8d06d4d71a5ff6fe4c23a71c2cbda28783`.
- Regression commit: `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`.
- Final run `33790442843` proved 23 giveaway tests pass, canonical giveaway build succeeds, contract validation succeeds, fresh snapshot is complete, Epic is `ok/complete`, accepted_count `1`.
- Overall run failure occurred only at the final generated-file commit/rebase step after task-relevant validation and does not reopen the Epic parser incident.

## Visual freshness

- Accepted fix landed on `main` via PR #13 at `ddbf25d855f3ed7b86aca5ecbebb834e87178012`.
- Final release report is valid `blocked`: `reviews/worker_reports/visual-freshness-release-01.md`.
- Production run `33788418064` truthfully emitted `fresh_build=false / degraded/no_fresh_build`; receipt artifact uploaded.
- Full successful build->exact-run deploy proof remains pending because upstream failed on `ChatGPT production payload is not complete`.
- Do not redesign freshness fix.
- Prepared exact upstream recon remains: `WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md`.
- Chat 1 has no immediate continuation and can be deleted.

## Mobile feed incident

- User/device accepted as working.
- Post-incident audit complete.
- Remaining bounded gap: `tests/feed-bootstrap.test.js` not yet in canonical Pages deploy gate.
- Prepared: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.

## Review checkpoint

- `system_audit_due: true` due to stabilized Epic user-visible incident.
- Prepared post-audit: `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md`, report `reviews/system_audits/epic-post-incident-audit-01.md`.
- The currently visible giveaway-publication defect is a more urgent concrete production issue and may pre-empt the audit until localized/stabilized.
- Do not start ordinary backlog/ITAD before the required audit completes.

## Other prepared / parked work

- Visual-build input incompleteness recon: `WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md`.
- Mobile deploy regression gate: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- ITAD provider-neutral identity implementation: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Twitch/IGDB: waiting for Twitch Support.
- Semantic runtime observability: accepted/closed; degraded semantic completeness still not visibly surfaced in UI.
- Legacy Taste writer ambiguity: later bounded cleanup.

## Следующий порядок

1. Delete finished Chat 1.
2. Existing Chat 2 runs `giveaway-publication-gap-recon-01` from root `WORKER_TASK.md`.
3. If recon proves a concrete defect, issue one bounded IMPLEMENT and require real-site verification after deploy.
4. Once the giveaway visibility incident is stabilized, run `WORKER_TASK_EPIC_POST_INCIDENT_AUDIT_01.md` in a fresh worker chat.
5. Then return to visual-build input recon, mobile regression gate, and only after review checkpoints permit it ITAD/ordinary backlog.