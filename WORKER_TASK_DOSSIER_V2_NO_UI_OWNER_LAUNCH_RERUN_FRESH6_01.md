# ЧАТ 2 — Dossier V2: повтор шести игр без ручного GitHub UI

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: dossier-v2-no-ui-owner-launch-rerun-fresh6-01
Assigned: НОВЫЙ физический ЧАТ 2
Mode: BOUNDED IMPLEMENT + CI, one source PR

## Goal and authority
Пользователь одобрил повтор настоящего Research после упрощения механизма и **не будет самостоятельно открывать GitHub Actions, вводить SHA и запускать workflow**. Точный PR #450 уже принят в main (squash c3574cf0d43b72597be1dda7d9ea21c3184fd828), 4/4 CI PASS. Аутентифицированный ChatGPT GitHub connector пользователя `kentrap2011-hub` (numeric 315790060) умеет GitHub file/blob/tree/commit/branch/PR/merge и GET Actions, но не поддерживает workflow_dispatch. GitHub push после owner merge действительно исполняет GitHub Actions с actor_id 315790060. Учитывай эту реальную возможность, не притворяйся, что GET запускает workflow.

Сначала прочитай CHAT_PROTOCOL.md, выполни START, затем текущие Dossier V2 owner/batch/Research/receipt/strict-writer contracts. Это DEVELOPER task; не исследуй игры, не запускай Assembly, не создавай Scheduled Task.

## Exact new cohort and isolation
Зарегистрируй и подготовь `config/dossier_notes_v2_batches/dossier-notes-v2-fresh6-20261114-rerun1.json` для той же исторически закреплённой шестерки, сохраняя настоящие pinned provenance snapshot 2026-11-11 (не выдавая за свежую дату):
1000010 Crown Trick; 102600 Orcs Must Die!; 1029690 Sniper Elite 5; 49520 Borderlands 2; 499180 Braid, Anniversary Edition; 501590 Bulletstorm: Full Clip Edition.
Новый trial_id = `dossier-notes-v2-fresh6-20261114-rerun1`; ветка = `sandbox/dossier-notes-v2-fresh6-20261114-rerun1`. Пересчёт assignment делается existing deterministic frozen assignment, не вручную.
Прежняя шестерка `dossier-notes-v2-fresh6-20261111-first` уже имеет 6/6 immutable Research candidates + 6/6 receipts, HEAD `164f70870e00d1adc124c769a68f4d5c0ac752b4`. Нельзя ни повторить запись в эти же пути, ни переиспользовать старые grant/marker/authorization, ни изменять старую ветку.

## Implement minimal no-UI GitHub-owned authority
1. Сейчас `issue-dossier-notes-v2-batch.yml`, `authorize-dossier-notes-v2-batch.yml`, `ingest-dossier-notes-v2-research.yml` принимают **только owner workflow_dispatch first attempt**, который ChatGPT GitHub connector не умеет вызывать. Доработай owner authorization так, чтобы явно разрешённый пользователем **owner-merged new cohort source PR / owner-authenticated GitHub push on main** инициировал одноразовый GitHub-owned Freeze→Authorize без ручного Actions UI. Предусмотри точный repo/actor_id=315790060/ref/event/first attempt, proof actual origin GitHub push and exact new source path + immutable source/ancestry/one-use binding, checked source main SHA, prohibit PR CI or arbitrary sandbox push as authority. Два шага grant/manifest/unique marker/authorization остаются отдельно в Git commit chain, а GitHub реально выпускает и проверяет owner run evidence. Старые manual-only workflows можно сохранить как legacy; новая отдельная auth alternative должна иметь равноценные подтверждения в Python/JS/Actions.
2. Новые 6 Research кандидатов должны записываться semantic chat посредством ровно **одного `mcp__GitHub__create_file` на игру** по уже принятому launcher из PR #450. После этого GitHub автоматически (owner-verified push event) валидирует путь, неизменяемую ветку, Git parent, assignment, schema, bytes, затем добавляет **typed Research receipt** без второго owner workflow_dispatch. Должна быть serial/idempotent single receipt per valid candidate; отказы отдельных игр не блокируют других; отсутствие/source-invalid = truthful incomplete, не fake success. Сохраняй старый manual ingest fallback, если нужен, без изменения original18.
3. Применяй safe GitHub CAS/non-force, exact branch readback, no overwrite, no unverified actor/marker, no blind retries. Не делай новое permission широким для чужих веток. Проверки должны действительно разрешать последующий `Assembly` на новом trial и не расшатывать strict final writer/production/V1/Deep. Candidate receipt = техподтверждение, не финальная оценка.
4. Проверить поддержку ChatGPT connector реально: `create_file`/owner merge делает `push` with github.actor_id owner (подтверждено для main), но для sandbox Action push permissions проверить на disposable tests/PR, без настоящей semantic записи. Если не удаётся без ослабления доказательства владельца — fail closed и report `BLOCKED_INTERFACE`; не выдавать пустую новую ветку за авторизованную и не начинать Research.
5. Минимизируй сложность: никаких 14+11 Code Mode вызовов, human-pasted SHA, tokens, новых reviews/audits перед Research, смены production architecture. Synthetic regression invalid actor/branch, repeated owner consent, stale ref, wrong edition, original18, old 6 unchanged, six exact new items, receipt strict first-parent, concurrency, failed candidate. Run existing test and 4 PR workflows on exact HEAD. Итог — один source PR и краткий worker-report `reviews/worker_reports/dossier-v2-no-ui-owner-launch-rerun-fresh6-01.md`. После принятия source PR директор через подключённый GitHub выполняет разрешённый запуск без посещения GitHub UI; семантический worker — отдельный чат, не developer.

## STOP
Do not fabricate Actions owner run, falsely mark trial authorized, relax existing issuer proofs, change old sandbox or any production/canonical state, or silently auto-run semantic Research. No manual owner dispatch required or demanded from user. Follow explicit owner approval and genuine GitHub event identity only.
